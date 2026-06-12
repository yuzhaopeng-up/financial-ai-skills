"""
财报智能提取引擎
FinancialExtractEngine: 输入财务数据，返回财务指标 + 杜邦分析 + 同业对比 + 异常预警
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FinancialIndicators:
    """财务指标"""
    company: str
    revenue: float          # 万元
    net_profit: float       # 万元
    total_assets: float     # 万元
    total_liabilities: float # 万元
    operating_cost: Optional[float] = None  # 万元
    interest_expense: Optional[float] = None # 万元
    equity: Optional[float] = None  # 万元

    # 计算得出
    gross_margin: float = 0.0    # 毛利率 %
    net_margin: float = 0.0     # 净利率 %
    roe: float = 0.0            # 净资产收益率 %
    debt_asset_ratio: float = 0.0 # 资产负债率 %

    def __post_init__(self):
        if self.equity is None:
            self.equity = self.total_assets - self.total_liabilities

        # 计算毛利率
        if self.operating_cost is not None and self.revenue > 0:
            self.gross_margin = (self.revenue - self.operating_cost) / self.revenue * 100
        elif self.operating_cost is None:
            # 无法计算，设为 None 表示不适用
            self.gross_margin = None

        # 计算净利率
        if self.revenue > 0:
            self.net_margin = self.net_profit / self.revenue * 100

        # 计算 ROE
        if self.equity > 0:
            self.roe = self.net_profit / self.equity * 100

        # 计算资产负债率
        if self.total_assets > 0:
            self.debt_asset_ratio = self.total_liabilities / self.total_assets * 100


@dataclass
class DupontAnalysis:
    """杜邦分析"""
    net_margin: float           # 净利率
    asset_turnover: float       # 总资产周转率
    equity_multiplier: float     # 权益乘数
    roe: float                  # ROE

    @classmethod
    def from_indicators(cls, ind: FinancialIndicators) -> "DupontAnalysis":
        revenue = ind.revenue
        assets = ind.total_assets
        equity = ind.equity if ind.equity > 0 else 1  # 防止除零

        net_margin = ind.net_margin / 100  # 转小数
        asset_turnover = revenue / assets if assets > 0 else 0
        equity_multiplier = assets / equity if equity > 0 else 0
        roe = net_margin * asset_turnover * equity_multiplier * 100  # 转百分比

        return cls(
            net_margin=round(net_margin * 100, 2),
            asset_turnover=round(asset_turnover, 4),
            equity_multiplier=round(equity_multiplier, 4),
            roe=round(roe, 2)
        )

    def breakdown(self) -> str:
        return (
            f"净利率 {self.net_margin}% × 总资产周转率 {self.asset_turnover}次 "
            f"× 权益乘数 {self.equity_multiplier} = ROE {self.roe}%"
        )


@dataclass
class IndustryBenchmark:
    """同业对比基准"""
    gross_margin: float = 40.0   # 行业毛利率均值 %
    net_margin: float = 15.0     # 行业净利率均值 %
    roe: float = 12.0            # 行业ROE均值 %
    debt_asset_ratio: float = 60.0  # 行业资产负债率均值 %


@dataclass
class IndustryComparison:
    """同业对比结果"""
    company: str
    indicators: FinancialIndicators
    benchmark: IndustryBenchmark

    def to_dict(self) -> dict:
        rows = []
        # 毛利率
        gm = self.indicators.gross_margin
        rows.append({
            "指标": "毛利率",
            "某公司": f"{gm:.1f}%" if gm is not None else "N/A",
            "行业均值": f"{self.benchmark.gross_margin}%",
            "参考值": "优秀<60%，良好40-60%"
        })
        # 净利率
        rows.append({
            "指标": "净利率",
            "某公司": f"{self.indicators.net_margin:.1f}%",
            "行业均值": f"{self.benchmark.net_margin}%",
            "参考值": "优秀>20%，良好10-20%"
        })
        # ROE
        rows.append({
            "指标": "ROE",
            "某公司": f"{self.indicators.roe:.1f}%",
            "行业均值": f"{self.benchmark.roe}%",
            "参考值": "优秀>15%，良好10-15%"
        })
        # 资产负债率
        rows.append({
            "指标": "资产负债率",
            "某公司": f"{self.indicators.debt_asset_ratio:.1f}%",
            "行业均值": f"{self.benchmark.debt_asset_ratio}%",
            "参考值": "优秀<50%，良好50-70%"
        })
        return {"rows": rows}


@dataclass
class Alert:
    """预警项"""
    level: str      # high / medium / low
    icon: str       # 🔴 / 🟡 / 🟢
    message: str    # 预警说明


@dataclass
class AlertReport:
    """异常预警报告"""
    alerts: list = field(default_factory=list)

    def add(self, level: str, icon: str, message: str):
        self.alerts.append(Alert(level=level, icon=icon, message=message))

    def __str__(self) -> str:
        if not self.alerts:
            return "🟢 无异常预警"
        lines = [a.icon + " " + a.message for a in self.alerts]
        return "\n".join(lines)


class FinancialExtractEngine:
    """财报智能提取引擎"""

    def __init__(self, api_mode: bool = False):
        """
        Args:
            api_mode: True 则减少 stdout 打印，便于程序调用
        """
        self.api_mode = api_mode

    def extract(
        self,
        company: str = "某公司",
        revenue: float = 0,
        net_profit: float = 0,
        total_assets: float = 0,
        total_liabilities: float = 0,
        operating_cost: Optional[float] = None,
        interest_expense: Optional[float] = None,
    ) -> dict:
        """
        提取财务指标 + 杜邦分析 + 同业对比 + 异常预警
        """
        # 构建指标
        ind = FinancialIndicators(
            company=company,
            revenue=revenue,
            net_profit=net_profit,
            total_assets=total_assets,
            total_liabilities=total_liabilities,
            operating_cost=operating_cost,
            interest_expense=interest_expense,
        )

        # 杜邦分析
        dupont = DupontAnalysis.from_indicators(ind)

        # 同业对比
        benchmark = IndustryBenchmark()
        comparison = IndustryComparison(company, ind, benchmark)

        # 异常预警
        alerts = self._generate_alerts(ind)

        return {
            "company": company,
            "indicators": {
                "毛利率": f"{ind.gross_margin:.1f}%" if ind.gross_margin is not None else "N/A",
                "净利率": f"{ind.net_margin:.1f}%",
                "ROE": f"{ind.roe:.1f}%",
                "资产负债率": f"{ind.debt_asset_ratio:.1f}%",
                "股东权益": f"{ind.equity:.0f}万元",
            },
            "dupont": {
                "净利率": f"{dupont.net_margin}%",
                "总资产周转率": f"{dupont.asset_turnover}次",
                "权益乘数": f"{dupont.equity_multiplier}",
                "ROE分解": dupont.breakdown(),
            },
            "industry_comparison": comparison.to_dict()["rows"],
            "alerts": [a.message for a in alerts.alerts],
            "summary": self._summary(ind, dupont, alerts),
        }

    def _generate_alerts(self, ind: FinancialIndicators) -> AlertReport:
        """生成异常预警"""
        report = AlertReport()

        # 资产负债率
        if ind.debt_asset_ratio > 80:
            report.add("high", "🔴", f"资产负债率 {ind.debt_asset_ratio:.1f}% 超过80%，杠杆过高！")
        elif ind.debt_asset_ratio > 70:
            report.add("medium", "🟡", f"资产负债率 {ind.debt_asset_ratio:.1f}% 超过70%，偏高")
        elif ind.debt_asset_ratio > 60:
            report.add("low", "🟢", f"资产负债率 {ind.debt_asset_ratio:.1f}% 在合理范围")

        # 净利率
        if ind.net_margin < 5:
            report.add("medium", "🟡", f"净利率 {ind.net_margin:.1f}% 低于5%，盈利能力偏弱")
        elif ind.net_margin < 10:
            report.add("low", "🟢", f"净利率 {ind.net_margin:.1f}% 低于10%，建议关注")

        # ROE
        if ind.roe < 5:
            report.add("medium", "🟡", f"ROE {ind.roe:.1f}% 低于5%，股东回报不足")
        elif ind.roe < 10:
            report.add("low", "🟢", f"ROE {ind.roe:.1f}% 低于10%，有提升空间")

        # 毛利率
        if ind.gross_margin is not None and ind.gross_margin < 20:
            report.add("low", "🟢", f"毛利率 {ind.gross_margin:.1f}% 低于20%，关注成本控制")
        elif ind.gross_margin is None:
            report.add("low", "🟢", "毛利率数据不足（未提供营业成本），无法评估")

        return report

    def _summary(self, ind: FinancialIndicators, dupont: DupontAnalysis, alerts: AlertReport) -> str:
        """生成摘要文本"""
        gm = f"{ind.gross_margin:.1f}%" if ind.gross_margin is not None else "N/A"
        lines = [
            f"【{ind.company}财报提取报告】",
            f"",
            f"📊 核心指标：",
            f"  毛利率: {gm} | 净利率: {ind.net_margin:.1f}%",
            f"  ROE: {ind.roe:.1f}% | 资产负债率: {ind.debt_asset_ratio:.1f}%",
            f"",
            f"🔬 杜邦分析：",
            f"  {dupont.breakdown()}",
            f"",
            f"⚠️ 异常预警：",
            f"  {str(alerts)}",
        ]
        return "\n".join(lines)

    def extract_from_text(self, text: str) -> dict:
        """
        从自然语言文本解析财务数据并提取指标。
        支持格式示例：
        '财报提取 某公司 营收1000万 净利润80万 资产2000万 负债1200万'
        """
        import re

        # 解析营收
        revenue_m = re.search(r"营收\s*(\d+(?:\.\d+)?)\s*万", text)
        # 解析净利润
        profit_m = re.search(r"净利润\s*(\d+(?:\.\d+)?)\s*万", text)
        # 解析总资产
        assets_m = re.search(r"资产\s*(\d+(?:\.\d+)?)\s*万", text)
        # 解析总负债
        liab_m = re.search(r"负债\s*(\d+(?:\.\d+)?)\s*万", text)
        # 解析营业成本（可选）
        cost_m = re.search(r"成本\s*(\d+(?:\.\d+)?)\s*万", text)
        revenue = float(revenue_m.group(1)) if revenue_m else 0
        net_profit = float(profit_m.group(1)) if profit_m else 0
        total_assets = float(assets_m.group(1)) if assets_m else 0
        total_liabilities = float(liab_m.group(1)) if liab_m else 0
        operating_cost = float(cost_m.group(1)) if cost_m else None
        # 解析公司名：提取"提取"和"营收"之间的词组
        revenue_pos = re.search(r"营收", text)
        end_pos = revenue_pos.start() if revenue_pos else len(text)
        after_cmd = re.sub(r"^财报提取\s*", "", text[:end_pos]).strip()
        company = after_cmd if after_cmd else "某公司"

        return self.extract(
            company=company,
            revenue=revenue,
            net_profit=net_profit,
            total_assets=total_assets,
            total_liabilities=total_liabilities,
            operating_cost=operating_cost,
        )
