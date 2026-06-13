# -*- coding: utf-8 -*-
"""
资产配置再平衡引擎 v1.0
投资组合再平衡建议：当前持仓 + 目标配置 → 调仓方案 + 交易成本估算

支持多资产类型：股票、债券、基金、现金、黄金、外汇、理财等

Author: ArkClaw
Version: 1.0.0
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple


class RebalanceEngine:
    """资产配置再平衡引擎"""
    
    VERSION = "1.0.0"
    
    # 支持的资产类型及默认交易成本
    ASSET_TYPES = {
        "stock": {
            "name": "股票",
            "commission_rate": 0.0003,      # 佣金万三
            "min_commission": 5.0,          # 最低佣金5元
            "stamp_tax_rate": 0.001,        # 印花税千一（卖出时）
            "slippage_rate": 0.001,         # 滑点千一
            "other_fee_rate": 0.00002,      # 过户费万0.2
        },
        "bond": {
            "name": "债券",
            "commission_rate": 0.0002,      # 佣金万二
            "min_commission": 1.0,
            "stamp_tax_rate": 0.0,
            "slippage_rate": 0.0005,        # 债券滑点较低
            "other_fee_rate": 0.0,
        },
        "fund": {
            "name": "基金",
            "commission_rate": 0.001,       # 申购费千一
            "min_commission": 0.0,
            "stamp_tax_rate": 0.0,
            "slippage_rate": 0.0,           # ETF基金无滑点
            "other_fee_rate": 0.0,
        },
        "money_fund": {
            "name": "货币基金",
            "commission_rate": 0.0,
            "min_commission": 0.0,
            "stamp_tax_rate": 0.0,
            "slippage_rate": 0.0,
            "other_fee_rate": 0.0,
        },
        "gold": {
            "name": "黄金",
            "commission_rate": 0.006,        # 黄金交易费约千分之六
            "min_commission": 0.0,
            "stamp_tax_rate": 0.0,
            "slippage_rate": 0.002,          # 买卖双边滑点
            "other_fee_rate": 0.0,
        },
        "fx": {
            "name": "外汇",
            "commission_rate": 0.001,        # 外汇点差/手续费
            "min_commission": 0.0,
            "stamp_tax_rate": 0.0,
            "slippage_rate": 0.001,
            "other_fee_rate": 0.0,
        },
        "financial_product": {
            "name": "银行理财",
            "commission_rate": 0.0,
            "min_commission": 0.0,
            "stamp_tax_rate": 0.0,
            "slippage_rate": 0.0,
            "other_fee_rate": 0.0,
        },
        "cash": {
            "name": "现金/存款",
            "commission_rate": 0.0,
            "min_commission": 0.0,
            "stamp_tax_rate": 0.0,
            "slippage_rate": 0.0,
            "other_fee_rate": 0.0,
        },
    }
    
    # 默认调仓阈值（容忍偏差%）
    DEFAULT_TOLERANCE = 5.0  # 单项资产偏离目标超过5%才触发调仓
    
    # 最小交易金额（低于此值不执行调仓）
    DEFAULT_MIN_TRADE_AMOUNT = 1000.0
    
    def __init__(self, api_mode: bool = False):
        self.api_mode = api_mode
        self._log("初始化资产配置再平衡引擎 v%s" % self.VERSION)
    
    def _log(self, msg: str):
        if not self.api_mode:
            print(msg)
    
    def rebalance(
        self,
        current_holdings: Dict[str, float],
        target_allocation: Dict[str, float],
        total_value: float = None,
        tolerance: float = None,
        min_trade_amount: float = None,
        asset_types: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        """
        计算再平衡方案
        
        Args:
            current_holdings: 当前持仓 {资产名: 金额}
            target_allocation: 目标配置 {资产名: 百分比(0-100)}
            total_value: 总市值（不传则自动从current_holdings求和）
            tolerance: 容忍偏差%（默认5%）
            min_trade_amount: 最小交易金额（默认1000元）
            asset_types: 资产类型映射 {资产名: 类型}，未指定则默认推断
        
        Returns:
            再平衡方案
        """
        if tolerance is None:
            tolerance = self.DEFAULT_TOLERANCE
        if min_trade_amount is None:
            min_trade_amount = self.DEFAULT_MIN_TRADE_AMOUNT
        if total_value is None:
            total_value = sum(current_holdings.values())
        
        if total_value <= 0:
            return {"error": "总市值必须大于0"}
        
        # 推断资产类型（未指定的根据名称关键字推断）
        inferred_types = self._infer_asset_types(asset_types or {})
        
        # 计算当前配置比例
        current_pct = {k: (v / total_value * 100) for k, v in current_holdings.items()}
        
        # 计算偏离度
        deviations = self._calculate_deviations(current_pct, target_allocation)
        
        # 生成调仓指令
        trades = self._generate_trades(
            current_holdings, current_pct, target_allocation,
            deviations, total_value, tolerance, min_trade_amount
        )
        
        # 计算交易成本
        cost_estimate = self._estimate_costs(trades, inferred_types)
        
        # 模拟再平衡后的配置
        final_allocation = self._simulate_final_allocation(
            current_holdings, trades, total_value
        )
        
        # 风险指标
        risk_metrics = self._calculate_risk_metrics(
            current_pct, target_allocation, deviations
        )
        
        # 综合评估
        assessment = self._assess_rebalance_plan(
            trades, cost_estimate, total_value, tolerance
        )
        
        return {
            "total_value": total_value,
            "current_allocation": {k: round(v, 4) for k, v in current_pct.items()},
            "target_allocation": target_allocation,
            "deviations": deviations,
            "tolerance": tolerance,
            "min_trade_amount": min_trade_amount,
            "trades": trades,
            "cost_estimate": cost_estimate,
            "final_allocation": final_allocation,
            "risk_metrics": risk_metrics,
            "assessment": assessment,
            "asset_types": inferred_types,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    
    def _infer_asset_types(self, explicit_types: Dict[str, str]) -> Dict[str, str]:
        """推断资产类型"""
        inferred = {}
        
        all_assets = set(explicit_types.keys())
        # 还需要推断其他资产
        
        for asset_name in all_assets:
            if asset_name in explicit_types:
                inferred[asset_name] = explicit_types[asset_name]
            else:
                inferred[asset_name] = self._guess_asset_type(asset_name)
        
        return inferred
    
    def _guess_asset_type(self, name: str) -> str:
        """根据名称关键字猜测资产类型"""
        name_lower = name.lower()
        
        if any(kw in name_lower for kw in ["货币", "余额宝", "零钱", "现金", "活期", "存款"]):
            return "money_fund"
        if any(kw in name_lower for kw in ["股票", "A股", "港股", "美股", "沪深", "创业板", "科创板"]):
            return "stock"
        if any(kw in name_lower for kw in ["债券", "国债", "企业债", "可转债", "政金债"]):
            return "bond"
        if any(kw in name_lower for kw in ["基金", "ETF", "指数", "LOF", "私募"]):
            return "fund"
        if any(kw in name_lower for kw in ["黄金", "Au", "gjs"]):
            return "gold"
        if any(kw in name_lower for kw in ["外汇", "USD", "EUR", "JPY", "GBP", "FX"]):
            return "fx"
        if any(kw in name_lower for kw in ["理财", "银行理财", "净值"]):
            return "financial_product"
        
        return "stock"  # 默认为股票
    
    def _calculate_deviations(
        self, current_pct: Dict[str, float], target_pct: Dict[str, float]
    ) -> Dict[str, Dict[str, float]]:
        """计算各资产偏离度"""
        deviations = {}
        
        # 所有资产名
        all_assets = set(current_pct.keys()) | set(target_pct.keys())
        
        for asset in all_assets:
            cur = current_pct.get(asset, 0.0)
            tgt = target_pct.get(asset, 0.0)
            dev = cur - tgt
            deviations[asset] = {
                "current_pct": round(cur, 4),
                "target_pct": round(tgt, 4),
                "deviation": round(dev, 4),
                "abs_deviation": round(abs(dev), 4),
                "action": self._determine_action(dev),
            }
        
        return deviations
    
    def _determine_action(self, deviation: float) -> str:
        """根据偏离度决定操作"""
        if abs(deviation) < 0.5:
            return "持有"
        elif deviation > 0:
            return "卖出"
        else:
            return "买入"
    
    def _generate_trades(
        self,
        current_holdings: Dict[str, float],
        current_pct: Dict[str, float],
        target_pct: Dict[str, float],
        deviations: Dict[str, Dict],
        total_value: float,
        tolerance: float,
        min_trade_amount: float,
    ) -> List[Dict]:
        """生成调仓指令"""
        trades = []
        
        # 按偏离度排序，优先处理偏离大的
        sorted_assets = sorted(
            deviations.items(),
            key=lambda x: x[1]["abs_deviation"],
            reverse=True
        )
        
        # 计算需要卖出的总额
        sell_total = 0.0
        for asset, dev_info in sorted_assets:
            if dev_info["action"] == "卖出":
                dev = dev_info["deviation"]
                sell_amount = total_value * dev / 100
                if abs(sell_amount) >= min_trade_amount:
                    sell_total += abs(sell_amount)
        
        # 生成买入指令（先卖后买）
        buy_total = 0.0
        for asset, dev_info in sorted_assets:
            dev = dev_info["deviation"]
            
            if dev_info["action"] == "卖出":
                # 卖出
                sell_amount = total_value * dev / 100
                if abs(sell_amount) >= min_trade_amount:
                    trades.append({
                        "asset": asset,
                        "action": "卖出",
                        "amount": round(abs(sell_amount), 2),
                        "current_pct": dev_info["current_pct"],
                        "target_pct": dev_info["target_pct"],
                        "deviation": dev_info["deviation"],
                        "estimated_price": 1.0,  # 简化：假设价格1
                        "estimated_shares": round(abs(sell_amount), 2),
                    })
            elif dev_info["action"] == "买入":
                # 买入
                buy_amount = abs(total_value * dev / 100)
                # 可买入金额按比例分配
                if sell_total > 0 and buy_total == 0:
                    # 第一轮买入：使用卖出资金
                    pass
                
                if abs(buy_amount) >= min_trade_amount:
                    trades.append({
                        "asset": asset,
                        "action": "买入",
                        "amount": round(buy_amount, 2),
                        "current_pct": dev_info["current_pct"],
                        "target_pct": dev_info["target_pct"],
                        "deviation": dev_info["deviation"],
                        "estimated_price": 1.0,
                        "estimated_shares": round(buy_amount, 2),
                    })
        
        # 优化：平衡买卖总额
        buy_sum = sum(t["amount"] for t in trades if t["action"] == "买入")
        sell_sum = sum(t["amount"] for t in trades if t["action"] == "卖出")
        
        if buy_sum > sell_sum:
            # 调整买入金额
            diff = buy_sum - sell_sum
            for t in trades:
                if t["action"] == "买入" and t["amount"] > min_trade_amount:
                    reduction = min(diff * (t["amount"] / buy_sum), t["amount"] - min_trade_amount)
                    t["amount"] = round(t["amount"] - reduction, 2)
                    break
        
        return trades
    
    def _estimate_costs(
        self, trades: List[Dict], asset_types: Dict[str, str]
    ) -> Dict[str, Any]:
        """估算交易成本"""
        total_cost = 0.0
        cost_details = []
        
        for trade in trades:
            asset = trade["asset"]
            amount = trade["amount"]
            action = trade["action"]
            asset_type = asset_types.get(asset, "stock")
            
            config = self.ASSET_TYPES.get(asset_type, self.ASSET_TYPES["stock"])
            
            # 佣金
            commission = max(amount * config["commission_rate"], config["min_commission"])
            
            # 印花税（仅卖出股票收取）
            stamp_tax = 0.0
            if action == "卖出" and asset_type == "stock":
                stamp_tax = amount * config["stamp_tax_rate"]
            
            # 其他费用
            other_fee = amount * config["other_fee_rate"]
            
            # 滑点
            slippage = amount * config["slippage_rate"]
            
            subtotal = commission + stamp_tax + other_fee + slippage
            
            total_cost += subtotal
            
            cost_details.append({
                "asset": asset,
                "action": action,
                "amount": amount,
                "asset_type": asset_type,
                "commission": round(commission, 2),
                "stamp_tax": round(stamp_tax, 2),
                "other_fee": round(other_fee, 2),
                "slippage": round(slippage, 2),
                "subtotal": round(subtotal, 2),
            })
        
        return {
            "total_cost": round(total_cost, 2),
            "cost_details": cost_details,
            "cost_rate": 0.0,  # 将在format里计算
        }
    
    def _simulate_final_allocation(
        self,
        current_holdings: Dict[str, float],
        trades: List[Dict],
        total_value: float,
    ) -> Dict[str, float]:
        """模拟再平衡后的配置"""
        # 执行交易后的持仓
        holdings = dict(current_holdings)
        
        for trade in trades:
            asset = trade["asset"]
            amount = trade["amount"]
            if trade["action"] == "卖出":
                holdings[asset] = holdings.get(asset, 0) - amount
            else:
                holdings[asset] = holdings.get(asset, 0) + amount
        
        # 转为百分比
        final = {}
        for asset, value in holdings.items():
            if value > 0:
                final[asset] = round(value / total_value * 100, 4)
            else:
                final[asset] = 0.0
        
        return final
    
    def _calculate_risk_metrics(
        self,
        current_pct: Dict[str, float],
        target_pct: Dict[str, float],
        deviations: Dict[str, Dict],
    ) -> Dict[str, Any]:
        """计算风险指标"""
        all_devs = [d["abs_deviation"] for d in deviations.values()]
        
        max_dev = max(all_devs) if all_devs else 0
        avg_dev = sum(all_devs) / len(all_devs) if all_devs else 0
        
        # 计算加权偏离度（按目标权重）
        weighted_dev = 0.0
        for asset, dev_info in deviations.items():
            tgt = target_pct.get(asset, 0)
            weighted_dev += abs(dev_info["deviation"]) * tgt / 100
        
        # 集中度风险（HHI指数）
        hhi_current = sum((p / 100) ** 2 for p in current_pct.values()) * 10000
        hhi_target = sum((p / 100) ** 2 for p in target_pct.values()) * 10000
        
        return {
            "max_deviation": round(max_dev, 4),
            "avg_deviation": round(avg_dev, 4),
            "weighted_deviation": round(weighted_dev, 4),
            "hhi_current": round(hhi_current, 2),
            "hhi_target": round(hhi_target, 2),
            "hhi_change": round(hhi_current - hhi_target, 2),
        }
    
    def _assess_rebalance_plan(
        self,
        trades: List[Dict],
        cost_estimate: Dict[str, Any],
        total_value: float,
        tolerance: float,
    ) -> Dict[str, Any]:
        """评估再平衡方案"""
        trade_count = len(trades)
        buy_count = sum(1 for t in trades if t["action"] == "买入")
        sell_count = sum(1 for t in trades if t["action"] == "卖出")
        total_cost = cost_estimate["total_cost"]
        cost_rate = total_cost / total_value * 100 if total_value > 0 else 0
        
        # 方案质量评分
        score = 100
        
        # 交易次数扣分
        if trade_count > 10:
            score -= min((trade_count - 10) * 2, 20)
        
        # 成本扣分
        if cost_rate > 0.5:
            score -= min((cost_rate - 0.5) * 20, 25)
        
        # 无交易加分
        if trade_count == 0:
            score = 100
            quality = "✅ 无需调仓"
        elif score >= 80:
            quality = "🟢 方案优良"
        elif score >= 60:
            quality = "🟡 方案一般"
        else:
            quality = "🔴 方案欠佳"
        
        return {
            "quality": quality,
            "score": round(max(0, score), 1),
            "trade_count": trade_count,
            "buy_count": buy_count,
            "sell_count": sell_count,
            "cost_rate": round(cost_rate, 4),
            "recommendation": self._generate_recommendation(
                trade_count, cost_rate, tolerance
            ),
        }
    
    def _generate_recommendation(
        self, trade_count: int, cost_rate: float, tolerance: float
    ) -> str:
        """生成建议"""
        if trade_count == 0:
            return "当前配置已接近目标，无需调仓"
        elif cost_rate > 1.0:
            return f"交易成本率({cost_rate:.2f}%)较高，建议适当放宽容忍度({tolerance}%)减少交易频率"
        elif cost_rate > 0.5:
            return f"交易成本率({cost_rate:.2f}%)可接受，建议在市场平稳时执行"
        else:
            return "交易成本率较低，建议按方案执行调仓"
    
    def format_text(self, result: Dict) -> str:
        """格式化输出为文本"""
        if "error" in result:
            return "❌ " + result["error"]
        
        lines = [
            f"📊 **资产配置再平衡报告**",
            f"",
            f"💰 总市值: {result['total_value']:,.2f} 元",
            f"⏰ 生成时间: {result['generated_at']}",
            f"",
            f"{'='*36}",
            f"",
            f"**容忍偏差**: ±{result['tolerance']}%  |  **最小交易额**: {result['min_trade_amount']:,.0f}元",
            f"",
            f"{'='*36}",
            f"",
            f"📋 **偏离度分析**",
        ]
        
        # 偏离度表格
        sorted_devs = sorted(
            result["deviations"].items(),
            key=lambda x: x[1]["abs_deviation"],
            reverse=True
        )
        
        lines.append("")
        lines.append(f"{'资产':<12} {'当前%':>8} {'目标%':>8} {'偏离%':>8} {'操作':<6}")
        lines.append(f"{'-'*48}")
        
        for asset, dev in sorted_devs:
            if dev["abs_deviation"] >= 0.5:  # 只显示有意义的偏离
                action_map = {"买入": "🟢买入", "卖出": "🔴卖出", "持有": "⚪持有"}
                action = action_map.get(dev["action"], dev["action"])
                lines.append(
                    f"{asset:<12} {dev['current_pct']:>7.2f}% {dev['target_pct']:>7.2f}% "
                    f"{dev['deviation']:>+7.2f}% {action}"
                )
        
        # 调仓方案
        lines.extend([
            f"",
            f"{'='*36}",
            f"",
            f"📋 **调仓方案** (共{result['assessment']['trade_count']}笔)",
        ])
        
        if result["trades"]:
            for t in result["trades"]:
                action_icon = "🔴" if t["action"] == "卖出" else "🟢"
                lines.append(
                    f"  {action_icon} {t['action']} {t['asset']}: "
                    f"{t['amount']:>12,.2f} 元 "
                    f"(当前{t['current_pct']:.2f}% → 目标{t['target_pct']:.2f}%)"
                )
        else:
            lines.append("  ✅ 无需调仓")
        
        # 成本估算
        cost = result["cost_estimate"]
        lines.extend([
            f"",
            f"{'='*36}",
            f"",
            f"💸 **交易成本估算**",
            f"",
            f"  总成本: **{cost['total_cost']:,.2f} 元** "
            f"(占市值 {result['assessment']['cost_rate']:.3f}%)",
        ])
        
        if cost["cost_details"]:
            lines.append("")
            for cd in cost["cost_details"]:
                if cd["subtotal"] > 0:
                    lines.append(
                        f"  · {cd['asset']} ({cd['action']}): "
                        f"佣金{cd['commission']:>8.2f} | "
                        f"印花税{cd['stamp_tax']:>7.2f} | "
                        f"滑点{cd['slippage']:>7.2f} | "
                        f"小计{cd['subtotal']:>8.2f}"
                    )
        
        # 再平衡后配置
        lines.extend([
            f"",
            f"{'='*36}",
            f"",
            f"✅ **再平衡后配置**",
        ])
        
        final = result.get("final_allocation", {})
        if final:
            sorted_final = sorted(final.items(), key=lambda x: x[1], reverse=True)
            for asset, pct in sorted_final:
                if pct > 0:
                    lines.append(f"  {asset}: {pct:.2f}%")
        
        # 风险指标
        risk = result["risk_metrics"]
        lines.extend([
            f"",
            f"{'='*36}",
            f"",
            f"📈 **风险指标**",
            f"",
            f"  最大偏离: {risk['max_deviation']:.2f}%",
            f"  平均偏离: {risk['avg_deviation']:.2f}%",
            f"  加权偏离: {risk['weighted_deviation']:.2f}%",
            f"  集中度(HHI): 当前{risk['hhi_current']} → 目标{risk['hhi_target']} "
            f"(变化{risk['hhi_change']:+.0f})",
        ])
        
        # 综合评估
        assess = result["assessment"]
        lines.extend([
            f"",
            f"{'='*36}",
            f"",
            f"🏆 **综合评估**: {assess['quality']} (评分: {assess['score']}/100)",
            f"",
            f"  买入 {assess['buy_count']} 笔 | 卖出 {assess['sell_count']} 笔 | "
            f"成本率 {assess['cost_rate']:.3f}%",
            f"",
            f"💡 {assess['recommendation']}",
        ])
        
        return '\n'.join(lines)
    
    def format_json(self, result: Dict) -> str:
        """格式化输出为JSON"""
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    def format_wecom_card(self, result: Dict) -> Dict:
        """格式化输出为企微卡片"""
        assess = result["assessment"]
        quality_colors = {
            "✅ 无需调仓": "green",
            "🟢 方案优良": "green",
            "🟡 方案一般": "orange",
            "🔴 方案欠佳": "red",
        }
        
        # 风险指标摘要
        risk = result["risk_metrics"]
        trade_lines = []
        if result["trades"]:
            for t in result["trades"][:5]:  # 最多5条
                icon = "🔴" if t["action"] == "卖出" else "🟢"
                trade_lines.append(
                    f"{icon} {t['action']}{t['asset']}: {t['amount']:,.0f}元"
                )
        else:
            trade_lines.append("✅ 无需调仓")
        
        cost = result["cost_estimate"]
        
        return {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"📊 再平衡方案 {assess['quality']}",
                    "template": quality_colors.get(assess["quality"], "gray")
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": (
                                f"**总市值**: {result['total_value']:,.0f} 元\n"
                                f"**调仓**: 买入{assess['buy_count']}笔 / "
                                f"卖出{assess['sell_count']}笔\n"
                                f"**交易成本**: {cost['total_cost']:,.2f}元 "
                                f"({assess['cost_rate']:.3f}%)"
                            )
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": "**📋 调仓明细**\n" + "\n".join(trade_lines)
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": (
                                f"**📈 风险指标**\n"
                                f"最大偏离: {risk['max_deviation']:.2f}% | "
                                f"平均偏离: {risk['avg_deviation']:.2f}%\n"
                                f"集中度(HHI): {risk['hhi_current']} → {risk['hhi_target']}"
                            )
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"💡 {assess['recommendation']}"
                        }
                    },
                ]
            }
        }


def main():
    """主函数 - CLI测试"""
    print("=" * 50)
    print("🦞 资产配置再平衡引擎 v1.0")
    print("=" * 50)
    print()
    
    engine = RebalanceEngine()
    
    # 示例：当前持仓
    current_holdings = {
        "A股股票": 400000,
        "债券基金": 200000,
        "货币基金": 150000,
        "黄金": 100000,
        "银行存款": 150000,
    }
    
    # 目标配置
    target_allocation = {
        "A股股票": 35.0,
        "债券基金": 25.0,
        "货币基金": 20.0,
        "黄金": 10.0,
        "银行存款": 10.0,
    }
    
    total_value = sum(current_holdings.values())
    print(f"💰 总市值: {total_value:,.2f} 元")
    print()
    
    result = engine.rebalance(
        current_holdings=current_holdings,
        target_allocation=target_allocation,
        total_value=total_value,
        tolerance=5.0,
        min_trade_amount=1000.0,
    )
    
    print(engine.format_text(result))


if __name__ == "__main__":
    main()
