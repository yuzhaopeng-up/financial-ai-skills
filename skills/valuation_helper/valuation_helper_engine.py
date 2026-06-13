#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
估值核算辅助引擎 v1.0
基金/理财持仓估值与异常预警

Author: ArkClaw
Version: 1.0.0
"""

import json
import re
from datetime import datetime, date
from typing import Dict, Any, List, Optional


class ValuationHelperEngine:
    """估值核算辅助引擎"""

    VERSION = "1.0.0"

    # 资产类型配置
    ASSET_TYPES = {
        "stock": {"name": "股票", "vol_unit": "股", "price_precision": 2},
        "fund": {"name": "基金", "vol_unit": "份", "price_precision": 3},
        "bond": {"name": "债券", "vol_unit": "张", "price_precision": 4},
        "futures": {"name": "期货", "vol_unit": "手", "price_precision": 2},
        "deposit": {"name": "银行存款", "vol_unit": "元", "price_precision": 2},
        "cash": {"name": "现金", "vol_unit": "元", "price_precision": 2},
        "other": {"name": "其他", "vol_unit": "元", "price_precision": 2},
    }

    # 预警阈值配置
    ALERT_THRESHOLDS = {
        "severe_volatility": 0.20,      # 20%以上波动 → 严重
        "warning_volatility": 0.10,     # 10%以上波动 → 警告
        "notice_volatility": 0.05,      # 5%以上波动 → 注意
        "liquidity_ratio": 0.02,        # 流动性资产低于2%
        "single_position_limit": 0.30,  # 单只股票超30% → 超限
        "concentration_limit": 0.60,    # 前十大持仓超60% → 集中度警告
    }

    # 资产类型关键词映射
    ASSET_KEYWORDS = {
        "stock": ["股票", "A股", "港股", "美股", "SH", "SZ"],
        "fund": ["基金", "ETF", "LOF", "公募", "私募"],
        "bond": ["债券", "国债", "企业债", "可转债", "CB"],
        "futures": ["期货", "IF", "IC", "IH", "T", "CU"],
        "deposit": ["存款", "定期", "活期"],
        "cash": ["现金", "余额"],
    }

    def __init__(self, api_mode: bool = False):
        self.api_mode = api_mode
        self._log("初始化估值核算辅助引擎 v%s" % self.VERSION)

    def _log(self, msg: str):
        if not self.api_mode:
            print(msg)

    def detect_asset_type(self, name: str = "", code: str = "") -> str:
        """检测资产类型"""
        text = (name + " " + code).upper()
        for asset_type, keywords in self.ASSET_KEYWORDS.items():
            for kw in keywords:
                if kw.upper() in text:
                    return asset_type
        return "other"

    def parse_positions(self, input_data: Any) -> List[Dict]:
        """
        解析持仓数据
        支持格式:
        1. 字符串格式: "股票A 1000股@10.5元, 基金B 5000份@2.3元"
        2. JSON格式: {"positions": [...]}
        3. 列表格式: [...]
        """
        if isinstance(input_data, str):
            return self._parse_string(input_data)
        elif isinstance(input_data, dict):
            if "positions" in input_data:
                return input_data["positions"]
            return [input_data]
        elif isinstance(input_data, list):
            return input_data
        return []

    def _parse_string(self, text: str) -> List[Dict]:
        """解析字符串格式持仓"""
        positions = []
        # 支持的分隔符: 逗号、顿号、换行
        items = re.split(r'[，,\n]+', text.strip())
        
        for item in items:
            item = item.strip()
            if not item:
                continue
            
            # 尝试匹配格式: "名称 数量[股/份/元]@价格"
            patterns = [
                r'(.+?)\s*(\d+(?:\.\d+)?)\s*(股|份|张|手|元)\s*@\s*(\d+(?:\.\d+)?)\s*元',
                r'(.+?)\s*(\d+(?:\.\d+)?)\s*(股|份|张|手|元)\s*@\s*(\d+(?:\.\d+)?)',
                r'(.+?)\s*(\d+(?:\.\d+)?)\s*(股|份|张|手|元)\s*成本\s*(\d+(?:\.\d+)?)',
            ]
            
            matched = False
            for pattern in patterns:
                m = re.search(pattern, item)
                if m:
                    name = m.group(1).strip()
                    volume = float(m.group(2))
                    vol_unit = m.group(3)
                    price = float(m.group(4))
                    
                    asset_type = self._infer_type_from_unit(vol_unit)
                    
                    positions.append({
                        "name": name,
                        "volume": volume,
                        "vol_unit": vol_unit,
                        "cost": price,
                        "current_price": price,
                        "asset_type": asset_type,
                        "cost_value": volume * price,
                        "current_value": volume * price,
                    })
                    matched = True
                    break
            
            if not matched:
                # 尝试更简单的解析
                m2 = re.search(r'(.+?)\s*(\d+(?:\.\d+)?)\s*@\s*(\d+(?:\.\d+)?)', item)
                if m2:
                    positions.append({
                        "name": m2.group(1).strip(),
                        "volume": float(m2.group(2)),
                        "cost": float(m2.group(3)),
                        "current_price": float(m2.group(3)),
                        "asset_type": "other",
                        "cost_value": float(m2.group(2)) * float(m2.group(3)),
                        "current_value": float(m2.group(2)) * float(m2.group(3)),
                    })
        
        return positions

    def _infer_type_from_unit(self, unit: str) -> str:
        """根据单位推断资产类型"""
        unit_map = {
            "股": "stock",
            "份": "fund",
            "张": "bond",
            "手": "futures",
            "元": "cash",
        }
        return unit_map.get(unit, "other")

    def update_prices(self, positions: List[Dict], price_map: Dict[str, float]) -> List[Dict]:
        """
        更新持仓价格
        price_map: {"股票A": 11.2, "600036.SH": 35.6, ...}
        """
        for pos in positions:
            name = pos.get("name", "")
            code = pos.get("code", "")
            
            # 优先按代码匹配
            if code and code in price_map:
                new_price = price_map[code]
            elif name in price_map:
                new_price = price_map[name]
            else:
                continue
            
            pos["current_price"] = new_price
            pos["current_value"] = pos["volume"] * new_price
            pos["price_change"] = (new_price - pos["cost"]) / pos["cost"] if pos["cost"] > 0 else 0
            pos["unrealized_gain"] = pos["current_value"] - pos["cost_value"]
            pos["unrealized_gain_pct"] = pos["price_change"] * 100
        
        return positions

    def calculate_valuation(self, positions: List[Dict], nav_date: str = None) -> Dict[str, Any]:
        """
        计算估值
        
        Args:
            positions: 持仓列表
            nav_date: 净值日期
        
        Returns:
            估值结果
        """
        if not nav_date:
            nav_date = date.today().strftime("%Y-%m-%d")
        
        # 分类汇总
        type_summary = {}
        for pos in positions:
            at = pos.get("asset_type", "other")
            if at not in type_summary:
                type_summary[at] = {
                    "asset_type": at,
                    "asset_type_name": self.ASSET_TYPES.get(at, {}).get("name", "其他"),
                    "total_cost": 0.0,
                    "total_current": 0.0,
                    "total_gain": 0.0,
                    "count": 0,
                }
            
            cost_val = pos.get("cost_value", pos.get("volume", 0) * pos.get("cost", 0))
            curr_val = pos.get("current_value", pos.get("volume", 0) * pos.get("current_price", pos.get("cost", 0)))
            
            type_summary[at]["total_cost"] += cost_val
            type_summary[at]["total_current"] += curr_val
            type_summary[at]["total_gain"] += (curr_val - cost_val)
            type_summary[at]["count"] += 1
        
        # 计算各类资产收益率
        for at, summary in type_summary.items():
            if summary["total_cost"] > 0:
                summary["gain_pct"] = (summary["total_gain"] / summary["total_cost"]) * 100
            else:
                summary["gain_pct"] = 0.0
        
        # 总览
        total_cost = sum(s["total_cost"] for s in type_summary.values())
        total_current = sum(s["total_current"] for s in type_summary.values())
        total_gain = total_current - total_cost
        total_gain_pct = (total_gain / total_cost * 100) if total_cost > 0 else 0
        
        # 持仓明细
        position_details = []
        for pos in positions:
            position_details.append({
                "name": pos.get("name", ""),
                "code": pos.get("code", ""),
                "asset_type": pos.get("asset_type", "other"),
                "asset_type_name": self.ASSET_TYPES.get(pos.get("asset_type", "other"), {}).get("name", "其他"),
                "volume": pos.get("volume", 0),
                "vol_unit": pos.get("vol_unit", "元"),
                "cost": pos.get("cost", 0),
                "current_price": pos.get("current_price", pos.get("cost", 0)),
                "cost_value": pos.get("cost_value", 0),
                "current_value": pos.get("current_value", 0),
                "price_change": pos.get("price_change", 0),
                "unrealized_gain": pos.get("unrealized_gain", 0),
                "unrealized_gain_pct": pos.get("unrealized_gain_pct", 0),
            })
        
        # 排序: 按当前价值降序
        position_details.sort(key=lambda x: x["current_value"], reverse=True)
        
        # 计算权重
        for pos in position_details:
            if total_current > 0:
                pos["weight"] = pos["current_value"] / total_current * 100
            else:
                pos["weight"] = 0
        
        # 异常检测
        alerts = self._detect_anomalies(position_details, type_summary, total_current)
        
        return {
            "nav_date": nav_date,
            "valuation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_cost": total_cost,
            "total_current": total_current,
            "total_gain": total_gain,
            "total_gain_pct": total_gain_pct,
            "type_summary": list(type_summary.values()),
            "position_details": position_details,
            "alerts": alerts,
            "alert_count": len(alerts),
            "alert_stats": {
                "severe": len([a for a in alerts if a["level"] == "severe"]),
                "warning": len([a for a in alerts if a["level"] == "warning"]),
                "notice": len([a for a in alerts if a["level"] == "notice"]),
                "info": len([a for a in alerts if a["level"] == "info"]),
            },
            "position_count": len(positions),
        }

    def _detect_anomalies(self, positions: List[Dict], type_summary: Dict, total_value: float) -> List[Dict]:
        """检测异常"""
        alerts = []
        thresholds = self.ALERT_THRESHOLDS
        
        for pos in positions:
            pc = pos.get("price_change", 0)
            
            # 波动异常
            if abs(pc) >= thresholds["severe_volatility"]:
                alerts.append({
                    "level": "severe",
                    "level_label": "🔴 严重",
                    "type": "volatility",
                    "title": "价格剧烈波动",
                    "message": f"{pos['name']} 今日波动 {pc*100:+.2f}%，超过20%阈值",
                    "position": pos["name"],
                    "value": pc * 100,
                })
            elif abs(pc) >= thresholds["warning_volatility"]:
                alerts.append({
                    "level": "warning",
                    "level_label": "🟠 警告",
                    "type": "volatility",
                    "title": "价格波动较大",
                    "message": f"{pos['name']} 今日波动 {pc*100:+.2f}%，超过10%阈值",
                    "position": pos["name"],
                    "value": pc * 100,
                })
            elif abs(pc) >= thresholds["notice_volatility"]:
                alerts.append({
                    "level": "notice",
                    "level_label": "🟡 注意",
                    "type": "volatility",
                    "title": "价格波动",
                    "message": f"{pos['name']} 今日波动 {pc*100:+.2f}%，超过5%阈值",
                    "position": pos["name"],
                    "value": pc * 100,
                })
            
            # 集中度超限
            weight = pos.get("weight", 0)
            if pos.get("asset_type") == "stock" and weight >= thresholds["single_position_limit"] * 100:
                alerts.append({
                    "level": "warning",
                    "level_label": "🟠 警告",
                    "type": "concentration",
                    "title": "单一股票超限",
                    "message": f"{pos['name']} 权重 {weight:.2f}%，超过30%集中度上限",
                    "position": pos["name"],
                    "value": weight,
                })
        
        # 流动性检查
        cash_type = type_summary.get("cash", {})
        if total_value > 0:
            cash_ratio = cash_type.get("total_current", 0) / total_value
            if cash_ratio < thresholds["liquidity_ratio"]:
                alerts.append({
                    "level": "notice",
                    "level_label": "🟡 注意",
                    "type": "liquidity",
                    "title": "流动性不足",
                    "message": f"现金及等价物比例 {cash_ratio*100:.2f}%，低于2%最低要求",
                    "position": "现金",
                    "value": cash_ratio * 100,
                })
        
        # 按level排序
        level_order = {"severe": 0, "warning": 1, "notice": 2, "info": 3}
        alerts.sort(key=lambda x: (level_order.get(x["level"], 9), -abs(x.get("value", 0))))
        
        return alerts

    def format_text(self, result: Dict) -> str:
        """格式化输出为文本"""
        lines = [
            f"📊 **估值核算报告**",
            f"",
            f"📅 净值日期: {result['nav_date']}",
            f"⏰ 计算时间: {result['valuation_date']}",
            f"",
            f"{'='*36}",
            f"",
            f"💰 **资产总览**",
            f"",
            f"总成本:   ¥{result['total_cost']:,.2f}",
            f"当前市值: ¥{result['total_current']:,.2f}",
            f"累计收益: ¥{result['total_gain']:+,.2f}",
            f"收益率:   {result['total_gain_pct']:+.2f}%",
            f"",
            f"{'='*36}",
            f"",
            f"📂 **分类汇总**",
        ]
        
        for summary in result.get("type_summary", []):
            lines.append(
                f"  [{summary['asset_type_name']}] "
                f"成本 {summary['total_cost']:,.2f} | "
                f"市值 {summary['total_current']:,.2f} | "
                f"收益 {summary['total_gain']:+,.2f} ({summary['gain_pct']:+.2f}%)"
            )
        
        lines.extend([
            f"",
            f"{'='*36}",
            f"",
            f"📋 **持仓明细**",
            f"",
        ])
        
        # 表头
        lines.append(f"  {'名称':<12} {'类型':<6} {'数量':>10} {'成本':>10} {'现价':>10} {'市值':>12} {'收益':>10} {'权重':>6}")
        lines.append(f"  {'-'*12} {'-'*6} {'-'*10} {'-'*10} {'-'*10} {'-'*12} {'-'*10} {'-'*6}")
        
        for pos in result.get("position_details", []):
            name = pos["name"][:12]
            at_name = pos.get("asset_type_name", "")[:6]
            lines.append(
                f"  {name:<12} {at_name:<6} "
                f"{pos['volume']:>10.2f} "
                f"{pos['cost']:>10.4f} "
                f"{pos['current_price']:>10.4f} "
                f"{pos['current_value']:>12,.2f} "
                f"{pos['unrealized_gain']:>+10,.2f} "
                f"{pos.get('weight', 0):>5.2f}%"
            )
        
        # 预警
        if result.get("alerts"):
            lines.extend([
                f"",
                f"{'='*36}",
                f"",
                f"🚨 **异常预警** ({result['alert_count']}条)",
                f"",
            ])
            for alert in result["alerts"]:
                lines.append(f"  {alert['level_label']} {alert['title']}: {alert['message']}")
        else:
            lines.extend([
                f"",
                f"{'='*36}",
                f"",
                f"✅ **无异常预警**",
            ])
        
        lines.append(f"")
        
        return '\n'.join(lines)

    def format_json(self, result: Dict) -> str:
        """格式化输出为JSON"""
        return json.dumps(result, ensure_ascii=False, indent=2)

    def format_wecom_card(self, result: Dict) -> dict:
        """格式化输出为企微卡片"""
        # 选择告警级别颜色
        stats = result.get("alert_stats", {})
        if stats.get("severe", 0) > 0:
            template = "red"
        elif stats.get("warning", 0) > 0:
            template = "orange"
        elif stats.get("notice", 0) > 0:
            template = "yellow"
        else:
            template = "green"
        
        # 汇总摘要
        summary_parts = []
        for s in result.get("type_summary", []):
            summary_parts.append(
                f"{s['asset_type_name']}: ¥{s['total_current']:,.0f}({s['gain_pct']:+.1f}%)"
            )
        
        # 告警摘要
        alert_parts = []
        for alert in result.get("alerts", [])[:5]:
            alert_parts.append(f"{alert['level_label']} {alert['message']}")
        
        elements = [
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**净值日期**: {result['nav_date']}"}},
            {"tag": "hr"},
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**总成本**: ¥{result['total_cost']:,.2f}\n**当前市值**: ¥{result['total_current']:,.2f}\n**累计收益**: ¥{result['total_gain']:+,.2f} ({result['total_gain_pct']:+.2f}%)"}},
            {"tag": "hr"},
        ]
        
        if summary_parts:
            elements.append({"tag": "div", "text": {"tag": "lark_md", "content": "**分类汇总**: " + " | ".join(summary_parts)}})
            elements.append({"tag": "hr"})
        
        if alert_parts:
            elements.append({"tag": "div", "text": {"tag": "lark_md", "content": "**异常预警**:\n" + "\n".join(alert_parts)}})
        else:
            elements.append({"tag": "div", "text": {"tag": "lark_md", "content": "✅ 无异常预警"}})
        
        return {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"📊 估值核算 - 收益{result['total_gain_pct']:+.2f}%",
                    "template": template
                },
                "elements": elements
            }
        }


def main():
    """主函数 - CLI测试"""
    print("=" * 50)
    print("🦞 估值核算辅助引擎 v1.0")
    print("=" * 50)
    print()
    
    engine = ValuationHelperEngine()
    
    # 示例持仓
    sample_text = "招商银行 1000股@35.5元, 贵州茅台 200股@1680元, 沪深300ETF 5000份@3.85元, 现金 50000元"
    
    print("📋 示例持仓:", sample_text)
    print()
    
    positions = engine.parse_positions(sample_text)
    
    # 模拟更新价格
    price_map = {
        "招商银行": 36.8,
        "贵州茅台": 1650.0,
        "沪深300ETF": 3.92,
    }
    positions = engine.update_prices(positions, price_map)
    
    # 计算估值
    result = engine.calculate_valuation(positions, nav_date="2024-01-15")
    print(engine.format_text(result))
    print()
    
    # JSON输出
    print("--- JSON输出样例 ---")
    print(engine.format_json(result)[:500], "...")


if __name__ == "__main__":
    main()
