"""
MarginTradingEngine - 融资融券监控引擎

提供维保比率计算、平仓预警、追保建议、集中度风险分析及最佳减仓方案。
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
from enum import IntEnum


class RiskLevel(IntEnum):
    SAFE = 0       # 🟢 安全（≥130%）
    WARNING = 1   # 🟡 关注（110%~130%）
    DANGER = 2    # 🔴 危险（<110%）


@dataclass
class Position:
    """单只股票持仓"""
    stock_name: str
    shares: float
    cost_price: float
    current_price: float

    @property
    def market_value(self) -> float:
        return self.shares * self.current_price

    @property
    def cost_value(self) -> float:
        return self.shares * self.cost_price

    @property
    def unrealized_pnl(self) -> float:
        return self.market_value - self.cost_value

    @property
    def unrealized_pnl_pct(self) -> float:
        if self.cost_value == 0:
            return 0.0
        return (self.unrealized_pnl / self.cost_value) * 100


@dataclass
class MarginAccount:
    """融资融券账户"""
    total_assets: float
    total_debt: float
    financing_balance: float
    short_position_value: float
    cash: float = 0.0

    @property
    def maintenance_ratio(self) -> float:
        if self.total_debt == 0:
            return float('inf')
        return (self.total_assets / self.total_debt) * 100

    @property
    def risk_level(self) -> RiskLevel:
        r = self.maintenance_ratio
        if r >= 130:
            return RiskLevel.SAFE
        elif r >= 110:
            return RiskLevel.WARNING
        else:
            return RiskLevel.DANGER

    @property
    def risk_status(self) -> str:
        return {RiskLevel.SAFE: "🟢 正常", RiskLevel.WARNING: "🟡 关注", RiskLevel.DANGER: "🔴 危险"}[self.risk_level]


@dataclass
class ConcentrationRisk:
    stock_name: str
    position_value: float
    ratio: float
    level: str
    suggestion: str


@dataclass
class ReductionPlan:
    stock_name: str
    current_shares: float
    reduce_shares: float
    reduce_value: float
    reduce_ratio: float
    reason: str
    new_concentration: float


@dataclass
class MarginCallRecommendation:
    plan_type: str
    description: str
    action: str
    amount: float
    priority: int


class MarginTradingEngine:
    """融资融券监控引擎"""

    WARNING_LINE = 130.0
    LIQUIDATION_LINE = 110.0
    CONCENTRATION_WARNING = 30.0
    CONCENTRATION_DANGER = 50.0

    def __init__(self,
                 positions: List[Position],
                 financing_balance: float,
                 cash: float = 0.0,
                 short_position_value: float = 0.0):
        self.positions = positions
        self.financing_balance = financing_balance
        self.cash = cash
        self.short_position_value = short_position_value
        self.total_debt = financing_balance + short_position_value
        self.total_assets = cash + sum(p.market_value for p in positions)

    @classmethod
    def from_natural_language(cls, text: str) -> "MarginTradingEngine":
        """
        从自然语言解析融资监控信息。

        支持格式：
        "融资监控 持仓某股票100万 融资50万 成本10元 现价8元"
        "持仓某股票100万 融资50万 成本10元 现价8元"
        """
        import re

        def parse_amount_from_match(m: "re.Match", default_unit: str = "万") -> float:
            """从正则匹配中提取数值，支持万/千/百"""
            s = m.group(0)
            val = float(re.search(r"[\d.]+", s).group())
            if "万" in s:
                val *= 10000
            elif "千" in s:
                val *= 1000
            elif "百" in s:
                val *= 100
            return val

        # 解析持仓（市值+名称），例如：持仓某股票100万
        # 同时捕获股票名称和金额
        position_value = 0.0
        stock_name = "某股票"
        pos_match = re.search(r"持仓([^\d]+?)\s*(\d+(?:\.\d+)?)\s*([万千百])", text)
        if pos_match:
            stock_name = pos_match.group(1).strip() or "某股票"
            v = float(pos_match.group(2))
            unit = pos_match.group(3)
            position_value = v * (10000 if unit == "万" else 1000 if unit == "千" else 100)
        else:
            # Fallback: just amount
            pos_match2 = re.search(r"持仓\s*(\d+(?:\.\d+)?)\s*([万千百])", text)
            if pos_match2:
                v = float(pos_match2.group(1))
                unit = pos_match2.group(2)
                position_value = v * (10000 if unit == "万" else 1000 if unit == "千" else 100)

        # 解析融资额
        financing_amount = 0.0
        fin_match = re.search(r"融资\s*(\d+(?:\.\d+)?)\s*([万千百])", text)
        if fin_match:
            v = float(fin_match.group(1))
            unit = fin_match.group(2)
            financing_amount = v * (10000 if unit == "万" else 1000 if unit == "千" else 100)

        # 解析成本价
        cost_price = 10.0
        cost_match = re.search(r"成本\s*(\d+(?:\.\d+)?)\s*元", text)
        if cost_match:
            cost_price = float(cost_match.group(1))

        # 解析现价
        current_price = cost_price
        price_match = re.search(r"现价\s*(\d+(?:\.\d+)?)\s*元", text)
        if price_match:
            current_price = float(price_match.group(1))

        # 计算股数（持仓市值 / 成本价 = 股数）
        if position_value > 0 and cost_price > 0:
            shares = position_value / cost_price
        elif position_value > 0 and current_price > 0:
            shares = position_value / current_price
        else:
            shares = 0.0

        position = Position(
            stock_name=stock_name,
            shares=shares,
            cost_price=cost_price,
            current_price=current_price
        )

        return cls(
            positions=[position],
            financing_balance=financing_amount,
            cash=0.0,
            short_position_value=0.0
        )

    @property
    def account(self) -> MarginAccount:
        return MarginAccount(
            total_assets=self.total_assets,
            total_debt=self.total_debt,
            financing_balance=self.financing_balance,
            short_position_value=self.short_position_value,
            cash=self.cash
        )

    def calculate_maintenance_ratio(self) -> Tuple[float, float, float]:
        ratio = self.account.maintenance_ratio
        return ratio, ratio - self.WARNING_LINE, ratio - self.LIQUIDATION_LINE

    def liquidation_warning(self) -> Dict[str, Any]:
        ratio, warn_delta, liquid_delta = self.calculate_maintenance_ratio()

        if ratio >= self.WARNING_LINE:
            return {
                "status": "safe",
                "ratio": ratio,
                "message": f"维保比率 {ratio:.2f}% 处于安全区间，无需操作",
                "distance_to_warning": abs(warn_delta),
                "distance_to_liquidation": abs(liquid_delta)
            }

        # 需追加保证金到预警线
        target_add = max(0, (self.total_debt * self.WARNING_LINE / 100) - self.total_assets)
        # 需减仓市值到预警线
        reduce_val = max(0, self.total_assets - (self.total_debt * self.WARNING_LINE / 100))

        # 预测：再跌多少触发平仓
        price_drop_pct = 0.0
        if self.positions and self.positions[0].shares > 0:
            pos = self.positions[0]
            # (cash + shares * P) / debt * 100 = liquidation_line
            # P = (debt * liquidation_line / 100 - cash) / shares
            target_liquidation_price = (
                (self.total_debt * self.LIQUIDATION_LINE / 100 - self.cash) / pos.shares
            )
            if pos.current_price > 0:
                price_drop_pct = max(0, (pos.current_price - target_liquidation_price) / pos.current_price * 100)

        suggestion = self._generate_suggestion(ratio)

        return {
            "status": "warning" if ratio >= self.LIQUIDATION_LINE else "danger",
            "ratio": ratio,
            "message": suggestion,
            "distance_to_warning": warn_delta,
            "distance_to_liquidation": liquid_delta,
            "required_additional_margin": target_add,
            "required_reduce_value": reduce_val,
            "price_drop_to_liquidation_pct": price_drop_pct,
            "suggestion": suggestion
        }

    def concentration_risk_analysis(self) -> List[ConcentrationRisk]:
        risks = []
        for pos in self.positions:
            ratio = (pos.market_value / self.total_assets * 100) if self.total_assets > 0 else 0
            if ratio >= self.CONCENTRATION_DANGER:
                level = "🔴 危险"
                suggestion = f"超过{self.CONCENTRATION_DANGER}%危险线，建议立即减仓"
            elif ratio >= self.CONCENTRATION_WARNING:
                level = "🟡 关注"
                suggestion = f"超过{self.CONCENTRATION_WARNING}%关注线，建议关注"
            else:
                level = "🟢 正常"
                suggestion = "集中度安全"
            risks.append(ConcentrationRisk(
                stock_name=pos.stock_name,
                position_value=pos.market_value,
                ratio=ratio,
                level=level,
                suggestion=suggestion
            ))
        return risks

    def optimal_reduction_plan(self) -> List[ReductionPlan]:
        plans = []
        for pos in self.positions:
            concentration = (pos.market_value / self.total_assets * 100) if self.total_assets > 0 else 0
            score = abs(pos.unrealized_pnl_pct) * (concentration ** 0.5)
            reduce_ratio = min(50, max(20, score / 2))
            reduce_shares = pos.shares * (reduce_ratio / 100)
            reduce_value = reduce_shares * pos.current_price
            new_concentration = concentration * (1 - reduce_ratio / 100)
            plans.append(ReductionPlan(
                stock_name=pos.stock_name,
                current_shares=pos.shares,
                reduce_shares=reduce_shares,
                reduce_value=reduce_value,
                reduce_ratio=reduce_ratio,
                reason=f"亏损率{pos.unrealized_pnl_pct:.1f}%，集中度{concentration:.1f}%",
                new_concentration=new_concentration
            ))
        return plans

    def margin_call_recommendations(self) -> List[MarginCallRecommendation]:
        recommendations = []
        ratio = self.account.maintenance_ratio

        if ratio >= self.WARNING_LINE:
            recommendations.append(MarginCallRecommendation(
                plan_type="A", description="维保比率安全",
                action="无需操作，保持监控", amount=0, priority=0
            ))
            return recommendations

        add_amount = max(0, (self.total_debt * self.WARNING_LINE / 100) - self.total_assets)
        reduce_amount = max(0, self.total_assets - (self.total_debt * self.WARNING_LINE / 100))

        recommendations.append(MarginCallRecommendation(
            plan_type="A",
            description=f"追加保证金 {add_amount:,.0f} 元至{WARNING_LINE}%",
            action=f"追加现金保证金 {add_amount:,.0f} 元",
            amount=add_amount, priority=1
        ))

        if self.positions:
            pos = self.positions[0]
            reduce_shares = reduce_amount / pos.current_price if pos.current_price > 0 else 0
            recommendations.append(MarginCallRecommendation(
                plan_type="B",
                description=f"减仓约 {reduce_shares:.0f} 股（市值 {reduce_amount:,.0f} 元）至{WARNING_LINE}%",
                action=f"减仓 {pos.stock_name} {reduce_shares:.0f} 股",
                amount=reduce_amount, priority=2
            ))

            add_half = add_amount * 0.5
            reduce_half = reduce_amount * 0.5
            recommendations.append(MarginCallRecommendation(
                plan_type="C",
                description=f"组合方案：追加 {add_half:,.0f} 元 + 减仓 {reduce_half:,.0f} 元",
                action=f"追加保证金 {add_half:,.0f} 元，同时减仓 {pos.stock_name}",
                amount=add_half, priority=3
            ))

        return recommendations

    def _generate_suggestion(self, ratio: float) -> str:
        if ratio < self.LIQUIDATION_LINE:
            return "⚠️ 紧急：维保比率低于平仓线，立即追加保证金或减仓！"
        elif ratio < self.WARNING_LINE:
            return "⚠️ 预警：维保比率低于预警线，建议尽快追加保证金或减仓"
        return "✓ 安全"

    def generate_report(self) -> Dict[str, Any]:
        ratio, warn_delta, liquid_delta = self.calculate_maintenance_ratio()
        warning = self.liquidation_warning()
        concentrations = self.concentration_risk_analysis()
        recommendations = self.margin_call_recommendations()

        positions_detail = []
        for pos in self.positions:
            positions_detail.append({
                "stock": pos.stock_name,
                "shares": f"{pos.shares:,.0f}",
                "cost": f"{pos.cost_price:.2f}",
                "current": f"{pos.current_price:.2f}",
                "market_value": f"{pos.market_value:,.0f}",
                "cost_value": f"{pos.cost_value:,.0f}",
                "unrealized_pnl": f"{pos.unrealized_pnl:+,.0f}",
                "unrealized_pnl_pct": f"{pos.unrealized_pnl_pct:+.1f}%"
            })

        mr = self.account.maintenance_ratio
        return {
            "account": {
                "total_assets": f"{self.total_assets:,.0f}",
                "total_debt": f"{self.total_debt:,.0f}",
                "cash": f"{self.cash:,.0f}",
                "financing_balance": f"{self.financing_balance:,.0f}",
            },
            "maintenance_ratio": {
                "value": f"{ratio:.2f}%",
                "warning_line": f"{self.WARNING_LINE}%",
                "liquidation_line": f"{self.LIQUIDATION_LINE}%",
                "delta_to_warning": f"{warn_delta:+.2f}%",
                "delta_to_liquidation": f"{liquid_delta:+.2f}%",
                "level": self.account.risk_status,
                "level_code": self.account.risk_level.value
            },
            "warning": warning,
            "positions": positions_detail,
            "concentration_risks": [
                {"stock": r.stock_name, "ratio": f"{r.ratio:.1f}%",
                 "level": r.level, "suggestion": r.suggestion}
                for r in concentrations
            ],
            "recommendations": [
                {"plan": r.plan_type, "description": r.description,
                 "action": r.action,
                 "amount": f"{r.amount:,.0f}" if r.amount > 0 else "0",
                 "priority": r.priority}
                for r in recommendations
            ]
        }

    def format_text_report(self) -> str:
        report = self.generate_report()
        lines = []
        lines.append("=" * 50)
        lines.append("        融资融券监控报告")
        lines.append("=" * 50)

        acc = report["account"]
        lines.append("\n📊 账户概览")
        lines.append(f"  总资产：{acc['total_assets']} 元")
        lines.append(f"  总负债：{acc['total_debt']} 元")
        lines.append(f"  现金：{acc['cash']} 元")
        lines.append(f"  融资余额：{acc['financing_balance']} 元")

        mr = report["maintenance_ratio"]
        lines.append(f"\n📈 维保比率：{mr['value']} {mr['level']}")
        lines.append(f"  预警线 {mr['warning_line']}（偏离：{mr['delta_to_warning']}）")
        lines.append(f"  平仓线 {mr['liquidation_line']}（偏离：{mr['delta_to_liquidation']}）")

        warn = report["warning"]
        if warn["status"] != "safe":
            lines.append(f"\n⚠️ {warn['message']}")
            if warn.get("required_additional_margin"):
                lines.append(f"  → 需追加保证金：{warn['required_additional_margin']:,.0f} 元")
            if warn.get("required_reduce_value"):
                lines.append(f"  → 需减仓市值：{warn['required_reduce_value']:,.0f} 元")
            if warn.get("price_drop_to_liquidation_pct"):
                lines.append(f"  → 再跌 {warn['price_drop_to_liquidation_pct']:.1f}% 将触发平仓")

        lines.append("\n💼 持仓明细")
        for p in report["positions"]:
            lines.append(f"  {p['stock']}：{p['shares']}股")
            lines.append(f"    成本 {p['cost']} → 现价 {p['current']} | 市值 {p['market_value']}")
            lines.append(f"    盈亏 {p['unrealized_pnl']} 元（{p['unrealized_pnl_pct']}）")

        lines.append("\n🎯 集中度风险")
        for cr in report["concentration_risks"]:
            lines.append(f"  {cr['stock']}：{cr['ratio']} {cr['level']}")
            lines.append(f"    → {cr['suggestion']}")

        if report["recommendations"] and report["recommendations"][0]["priority"] > 0:
            lines.append("\n💡 追保建议")
            for rec in report["recommendations"]:
                if rec["priority"] > 0:
                    lines.append(f"  方案{rec['plan']}（优先级{rec['priority']}）：{rec['description']}")
                    lines.append(f"    操作：{rec['action']}")

        lines.append("\n" + "=" * 50)
        return "\n".join(lines)


# ── 内部工具 ─────────────────────────────────────────────────────────────────

WARNING_LINE = 130.0
LIQUIDATION_LINE = 110.0


def _format_wecom_card(report: Dict[str, Any]) -> Dict[str, Any]:
    mr = report["maintenance_ratio"]
    level_code = mr["level_code"]
    colors = {0: "green", 1: "yellow", 2: "red"}
    color = colors.get(level_code, "gray")

    position_lines = []
    for p in report["positions"]:
        pnl = p.get("unrealized_pnl", "0")
        position_lines.append(
            f"{p['stock']} | {p['shares']}股 | 成本{p['cost']}→现价{p['current']} "
            f"| 市值{p['market_value']} | 盈亏{pnl}"
        )

    conc_lines = []
    for c in report["concentration_risks"]:
        conc_lines.append(f"{c['stock']}：{c['ratio']} {c['level']} → {c['suggestion']}")

    rec_lines = []
    for r in report["recommendations"]:
        if int(r.get("priority", 0)) > 0:
            rec_lines.append(f"方案{r['plan']}（优先级{r['priority']}）：{r['description']} → {r['action']}")

    elements = [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": (
                    f"**维保比率**：{mr['value']} {mr['level']}\n"
                    f"预警线 {mr['warning_line']} | 平仓线 {mr['liquidation_line']}"
                )
            }
        },
        {"tag": "hr"},
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": (
                    f"**账户概览**\n"
                    f"总资产：{report['account']['total_assets']} 元\n"
                    f"总负债：{report['account']['total_debt']} 元"
                )
            }
        },
        {"tag": "hr"},
        {
            "tag": "div",
            "text": {"tag": "lark_md", "content": f"**💼 持仓明细**\n" + "\n".join(position_lines)}
        }
    ]

    if conc_lines:
        elements.append({"tag": "hr"})
        elements.append({
            "tag": "div",
            "text": {"tag": "lark_md", "content": f"**🎯 集中度风险**\n" + "\n".join(conc_lines)}
        })

    if rec_lines:
        elements.append({"tag": "hr"})
        elements.append({
            "tag": "div",
            "text": {"tag": "lark_md", "content": f"**💡 追保建议**\n" + "\n".join(rec_lines)}
        })

    actions = []
    if level_code >= 1:
        actions = [
            {"tag": "button", "text": {"tag": "lark_md", "content": "📌 追加保证金"}, "type": "primary"},
            {"tag": "button", "text": {"tag": "lark_md", "content": "📉 减仓"}, "type": "danger"}
        ]

    card = {
        "msgtype": "interactive",
        "interactive": {
            "tag": "card",
            "header": {"title": {"tag": "plain_text", "content": "📊 融资融券监控预警"}, "template": color},
            "elements": elements
        }
    }

    if actions:
        card["interactive"]["elements"].extend([{"tag": "hr"}, {"tag": "action", "actions": actions}])

    return card


# ─── CLI Entry ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse, json

    parser = argparse.ArgumentParser(description="融资融券监控引擎 CLI")
    subparsers = parser.add_subparsers(dest="command")

    g = subparsers.add_parser("generate", help="从自然语言生成报告")
    g.add_argument("text", help="自然语言描述")

    a = subparsers.add_parser("analyze", help="结构化参数分析")
    a.add_argument("--total-assets", type=float, required=True)
    a.add_argument("--debt", type=float, required=True)
    a.add_argument("--positions", type=str)
    a.add_argument("--financing", type=float, default=0)
    a.add_argument("--cash", type=float, default=0)

    w = subparsers.add_parser("wecom", help="生成企微卡片JSON")
    w.add_argument("--positions", type=str, required=True)
    w.add_argument("--debt", type=float, required=True)
    w.add_argument("--financing", type=float, default=0)

    args = parser.parse_args()

    if args.command == "generate":
        engine = MarginTradingEngine.from_natural_language(args.text)
        print(engine.format_text_report())

    elif args.command == "analyze":
        positions = []
        if args.positions:
            for pos_str in args.positions.split(";"):
                parts = [p.strip() for p in pos_str.split(",")]
                if len(parts) == 4:
                    positions.append(Position(parts[0], float(parts[1]), float(parts[2]), float(parts[3])))
        engine = MarginTradingEngine(
            positions=positions,
            financing_balance=args.financing,
            cash=args.cash,
            short_position_value=args.debt - args.financing
        )
        print(engine.format_text_report())

    elif args.command == "wecom":
        positions = []
        for pos_str in args.positions.split(";"):
            parts = [p.strip() for p in pos_str.split(",")]
            if len(parts) == 4:
                positions.append(Position(parts[0], float(parts[1]), float(parts[2]), float(parts[3])))
        engine = MarginTradingEngine(
            positions=positions,
            financing_balance=args.financing,
            cash=0,
            short_position_value=args.debt - args.financing
        )
        report = engine.generate_report()
        print(json.dumps(_format_wecom_card(report), ensure_ascii=False, indent=2))

    else:
        parser.print_help()
