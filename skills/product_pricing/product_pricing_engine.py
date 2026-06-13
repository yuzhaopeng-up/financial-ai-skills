#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品定价引擎 v1.0
支持存贷汇理财四大产品线，提供利率敏感性分析

Author: ArkClaw
Version: 1.0.0
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional


class ProductPricingEngine:
    """产品定价引擎"""

    VERSION = "1.0.0"

    # 产品基准利差（产品类型 → 基准利差%）
    PRODUCT_SPREADS = {
        "存款": {
            "定期一年": 0.30,
            "定期三年": 0.50,
            "定期五年": 0.65,
            "活期": 0.05,
            "结构性存款": 0.45,
        },
        "贷款": {
            "信用贷款": 2.50,
            "抵押贷款": 1.20,
            "经营贷款": 1.80,
            "消费贷款": 2.00,
            "住房贷款": 0.60,
        },
        "汇兑": {
            "结汇": 0.15,
            "售汇": 0.20,
            "外币兑换": 0.25,
            "跨境汇款": 0.35,
        },
        "理财": {
            "固定收益类": 0.80,
            "净值型理财": 1.00,
            "结构性理财": 1.50,
            "权益类理财": 2.20,
        },
    }

    # 客户风险等级加成（%）
    RISK_PREMIUMS = {
        "保守型": 0.00,
        "稳健型": 0.40,
        "进取型": 1.20,
        "谨慎型": 0.20,   # 介于保守和稳健之间
        "积极型": 1.80,   # 介于稳健和进取之间
    }

    # 基准利率（市场参考）
    BENCHMARK_RATES = {
        "存款基准": 1.50,     # 一年期定期基准
        "贷款LPR1Y": 3.60,   # 一年期LPR
        "贷款LPR5Y": 4.00,   # 五年期LPR
        "外汇美元兑": 7.20,  # USD/CNY
        "理财国债1Y": 1.80,  # 一年期国债收益率
    }

    # 利率敏感性步长（bp）
    SENSITIVITY_BPS = [-100, -75, -50, -25, 0, 25, 50, 75, 100]

    def __init__(self, api_mode: bool = False):
        self.api_mode = api_mode
        self._log("初始化产品定价引擎 v%s" % self.VERSION)

    def _log(self, msg: str):
        if not self.api_mode:
            print(msg)

    def parse_input(self, text: str) -> Dict[str, Any]:
        """解析输入文本，提取产品类型、客户风险等级、市场利率"""
        text = text.strip()

        # 提取产品类型
        product_type = None
        for pt in ["存款", "贷款", "汇兑", "理财"]:
            if pt in text:
                product_type = pt
                break

        # 提取风险等级
        risk_level = None
        for rl in ["保守型", "谨慎型", "稳健型", "积极型", "进取型"]:
            if rl in text:
                risk_level = rl
                break

        # 提取利率（支持 % 或 百分号）
        rate_match = re.search(r"(\d+\.?\d*)\s*%", text)
        market_rate = float(rate_match.group(1)) if rate_match else None

        # 提取具体子产品（如"信用贷款"）
        sub_product = None
        if product_type and product_type in self.PRODUCT_SPREADS:
            for sp in self.PRODUCT_SPREADS[product_type]:
                if sp in text:
                    sub_product = sp
                    break

        return {
            "product_type": product_type,
            "sub_product": sub_product,
            "risk_level": risk_level,
            "market_rate": market_rate,
            "raw_input": text,
        }

    def price(
        self,
        product_type: str,
        risk_level: str,
        market_rate: float,
        sub_product: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        计算产品定价

        Args:
            product_type: 产品类型（存款/贷款/汇兑/理财）
            risk_level: 客户风险等级
            market_rate: 市场参考利率（%）
            sub_product: 具体子产品（如"信用贷款"）

        Returns:
            定价结果
        """
        if product_type not in self.PRODUCT_SPREADS:
            return {"error": f"不支持的产品类型：{product_type}"}

        # 选用子产品
        if sub_product and sub_product in self.PRODUCT_SPREADS[product_type]:
            spread = self.PRODUCT_SPREADS[product_type][sub_product]
        else:
            # 取该类型默认子产品（第一个）
            spread = list(self.PRODUCT_SPREADS[product_type].values())[0]
            sub_product = list(self.PRODUCT_SPREADS[product_type].keys())[0]

        # 风险溢价
        risk_premium = self.RISK_PREMIUMS.get(risk_level, 0.0)

        # 定价计算
        if product_type == "存款":
            # 存款：银行支付给客户利率 = 市场利率 + 利差
            offered_rate = market_rate + spread + risk_premium
            customer_rate = offered_rate
            bank_margin = spread
        elif product_type == "贷款":
            # 贷款：银行收取客户利率 = 市场利率 + 利差 + 风险溢价
            offered_rate = market_rate + spread + risk_premium
            customer_rate = offered_rate
            bank_margin = spread + risk_premium
        elif product_type == "汇兑":
            # 汇兑：手续费率
            offered_rate = spread + risk_premium
            customer_rate = offered_rate
            bank_margin = offered_rate
        else:  # 理财
            # 理财：预期收益率
            offered_rate = market_rate + spread + risk_premium
            customer_rate = offered_rate
            bank_margin = spread

        # 竞争力评估
        competitiveness = self._evaluate_competitiveness(
            product_type, customer_rate
        )

        # 敏感性分析
        sensitivity = self._build_sensitivity(
            product_type, market_rate, spread, risk_premium
        )

        # 定价建议
        recommendation = self._generate_recommendation(
            product_type, risk_level, customer_rate, competitiveness
        )

        return {
            "product_type": product_type,
            "sub_product": sub_product,
            "risk_level": risk_level,
            "market_rate": market_rate,
            "offered_rate": round(offered_rate, 4),
            "customer_rate": round(customer_rate, 4),
            "spread": round(spread, 4),
            "risk_premium": round(risk_premium, 4),
            "bank_margin": round(bank_margin, 4),
            "competitiveness": competitiveness,
            "sensitivity": sensitivity,
            "recommendation": recommendation,
            "calculated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _evaluate_competitiveness(
        self, product_type: str, rate: float
    ) -> Dict[str, Any]:
        """评估定价竞争力"""
        benchmarks = {
            "存款": ("存款基准", True),   # 越高越好
            "贷款": ("贷款LPR1Y", False), # 越低越好
            "汇兑": ("外汇美元兑", False), # 参考汇率
            "理财": ("理财国债1Y", True),  # 越高越好
        }

        if product_type not in benchmarks:
            return {"level": "unknown", "vs_benchmark": 0.0, "label": "未知"}

        benchmark_name, higher_is_better = benchmarks[product_type]
        benchmark_val = self.BENCHMARK_RATES.get(benchmark_name, 0.0)

        if higher_is_better:
            diff = rate - benchmark_val
            vs_benchmark_pct = (diff / benchmark_val) * 100 if benchmark_val else 0
        else:
            diff = benchmark_val - rate
            vs_benchmark_pct = (diff / benchmark_val) * 100 if benchmark_val else 0

        if vs_benchmark_pct >= 20:
            level = "excellent"
            label = "⭐ 极优"
        elif vs_benchmark_pct >= 10:
            level = "good"
            label = "✅ 良好"
        elif vs_benchmark_pct >= 0:
            level = "fair"
            label = "🔹 持平"
        else:
            level = "poor"
            label = "⚠️ 偏高"

        return {
            "level": level,
            "vs_benchmark_pct": round(vs_benchmark_pct, 2),
            "benchmark_name": benchmark_name,
            "benchmark_value": benchmark_val,
            "label": label,
        }

    def _build_sensitivity(
        self,
        product_type: str,
        base_rate: float,
        spread: float,
        risk_premium: float,
    ) -> List[Dict[str, Any]]:
        """构建利率敏感性分析表"""
        results = []
        is_deposit = product_type == "存款"

        for bp in self.SENSITIVITY_BPS:
            # 利率变动值（%）
            rate_change = bp / 100.0
            # 变动后的市场利率
            new_market_rate = base_rate + rate_change

            if is_deposit:
                # 存款：客户利率跟随市场
                new_customer_rate = new_market_rate + spread + risk_premium
            else:
                # 贷款/理财：定价跟随市场
                new_customer_rate = new_market_rate + spread + risk_premium

            # 相对基准变动
            base_customer_rate = base_rate + spread + risk_premium
            rate_diff = new_customer_rate - base_customer_rate

            # 银行利差变化
            if is_deposit:
                new_margin = spread
            else:
                new_margin = spread + risk_premium

            results.append({
                "bp": bp,
                "market_rate": round(new_market_rate, 4),
                "customer_rate": round(new_customer_rate, 4),
                "rate_change": round(rate_change, 4),
                "rate_diff": round(rate_diff, 4),
                "bank_margin": round(new_margin, 4),
                "scenario": self._get_scenario_label(bp),
            })

        return results

    def _get_scenario_label(self, bp: int) -> str:
        if bp == 0:
            return "基准"
        elif bp > 0:
            return f"+{bp}bp ↑"
        else:
            return f"{bp}bp ↓"

    def _generate_recommendation(
        self, product_type: str, risk_level: str, rate: float, competitiveness: Dict
    ) -> str:
        """生成定价建议"""
        level = competitiveness.get("level", "unknown")
        vs_pct = competitiveness.get("vs_benchmark_pct", 0)

        if level == "excellent":
            action = "建议立即成交"
        elif level == "good":
            action = "建议积极营销"
        elif level == "fair":
            action = "可适度议价"
        else:
            action = "建议重新评估定价"

        return (
            f"该定价{competitiveness.get('label', '')}，"
            f"较基准{vp_pct_str(vs_pct)}，{action}。"
        )

    def format_text(self, result: Dict) -> str:
        """格式化输出为文本"""
        if "error" in result:
            return f"❌ {result['error']}"

        lines = [
            f"💰 **产品定价方案**",
            f"",
            f"📦 产品类型: {result['product_type']} / {result['sub_product']}",
            f"👤 风险等级: {result['risk_level']}",
            f"📊 市场利率: {result['market_rate']:.2f}%",
            f"",
            f"{'='*32}",
            f"",
            f"💎 **定价结果**",
            f"",
            f"执行利率: **{result['offered_rate']:.2f}%**",
            f"客户利率: {result['customer_rate']:.2f}%",
            f"利差成本: {result['spread']:.2f}%",
            f"风险溢价: {result['risk_premium']:.2f}%",
            f"银行利润: {result['bank_margin']:.2f}%",
            f"",
            f"🏆 竞争力: {result['competitiveness'].get('label', '')} "
            f"(较{result['competitiveness'].get('benchmark_name', '基准')}"
            f"{vp_pct_str(result['competitiveness'].get('vs_benchmark_pct', 0))})",
            f"",
            f"💡 {result['recommendation']}",
            f"",
            f"{'='*32}",
            f"",
            f"📉 **利率敏感性分析**（±bp / 市场利率 / 客户利率 / 变动）",
            f"",
        ]

        # 敏感性表格
        lines.append(f"{'情景':<10} {'市场利率':>10} {'客户利率':>10} {'变动':>8}")
        lines.append("-" * 42)
        for row in result["sensitivity"]:
            scenario = row["scenario"]
            mr = f"{row['market_rate']:.2f}%"
            cr = f"{row['customer_rate']:.2f}%"
            diff = f"{row['rate_diff']:+.2f}%"
            lines.append(f"{scenario:<10} {mr:>10} {cr:>10} {diff:>8}")

        lines.extend([
            f"",
            f"⏰ 计算时间: {result['calculated_at']}",
        ])

        return '\n'.join(lines)

    def format_json(self, result: Dict) -> str:
        """格式化输出为JSON"""
        return json.dumps(result, ensure_ascii=False, indent=2)


def vp_pct_str(pct: float) -> str:
    """格式化百分比差异字符串"""
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.1f}%"


def main():
    """主函数 - CLI测试"""
    print("=" * 50)
    print("💰 产品定价引擎 v1.0")
    print("=" * 50)
    print()

    engine = ProductPricingEngine(api_mode=True)

    # 测试1：贷款定价
    print("📋 场景1：信用贷款 稳健型客户 市场利率3.60%")
    result1 = engine.price("贷款", "稳健型", 3.60, "信用贷款")
    print(engine.format_text(result1))
    print()

    # 测试2：存款定价
    print("📋 场景2：定期一年 保守型客户 市场利率2.00%")
    result2 = engine.price("存款", "保守型", 2.00, "定期一年")
    print(engine.format_text(result2))
    print()

    # 测试3：理财定价
    print("📋 场景3：净值型理财 进取型客户 市场利率2.50%")
    result3 = engine.price("理财", "进取型", 2.50, "净值型理财")
    print(engine.format_text(result3))


if __name__ == "__main__":
    main()
