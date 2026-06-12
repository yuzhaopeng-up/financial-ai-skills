"""
定投计算引擎 (DCA Calculator Engine)

核心算法：
1. 定期定额投资模拟：每月投入固定金额，按月结算
2. 收益计算：(期末净值 - 期初净值) * 持有份额
3. 年化收益率：IRR (内部收益率) 算法
"""

import re
import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


# 内置指数基金数据
BUILTIN_FUNDS: Dict[str, Dict[str, Any]] = {
    "沪深300": {"code": "000300.SH", "name": "沪深300", "type": "A股宽基"},
    "中证500": {"code": "000905.SH", "name": "中证500", "type": "A股宽基"},
    "创业板指": {"code": "399006.SZ", "name": "创业板指", "type": "A股宽基"},
    "科创50": {"code": "000922.CSI", "name": "科创50", "type": "科创板"},
    "深证100": {"code": "139930.SZ", "name": "深证100", "type": "A股宽基"},
    "上证指数": {"code": "XXXXXX.SH", "name": "上证指数", "type": "A股宽基"},
    "纳斯达克100": {"code": "NDX.O", "name": "纳斯达克100", "type": "美股"},
    "标普500": {"code": "SPX.GI", "name": "标普500", "type": "美股"},
    "德国DAX": {"code": "GDAXI.GI", "name": "德国DAX", "type": "欧股"},
    "日经225": {"code": "N225.GI", "name": "日经225", "type": "亚太"},
    "中证红利": {"code": "CSI930850.SH", "name": "中证红利", "type": "A股策略"},
    "消费红利": {"code": "CSI701010.SH", "name": "消费红利", "type": "A股策略"},
    "中证500低波动": {"code": "000922.CSI", "name": "中证500低波动", "type": "A股SmartBeta"},
    "中证1000": {"code": "CSI000852.SH", "name": "中证1000", "type": "A股宽基"},
    "上证50": {"code": "000016.SH", "name": "上证50", "type": "A股宽基"},
}

# 频率映射
FREQ_MAP = {
    "每月": 12,
    "每周": 52,
    "每两周": 26,
    "每季": 4,
    "每年": 1,
}

# 收益率情景
SCENARIOS = {
    "optimistic": {"label": "乐观", "annual_return": 0.15, "desc": "年化15%"},
    "neutral": {"label": "中性", "annual_return": 0.08, "desc": "年化8%"},
    "pessimistic": {"label": "悲观", "annual_return": -0.05, "desc": "年化-5%"},
}


@dataclass
class MonthlyRecord:
    """月度定投记录"""
    month: int       # 第几月
    invested: float  # 本月投入
    nav: float       # 净值（假设）
    shares: float    # 新购份额
    total_shares: float  # 累计份额
    cumulative_invested: float  # 累计投入
    account_value: float      # 账户价值


@dataclass
class DCAResult:
    """定投计算结果"""
    fund_name: str
    fund_code: str
    fund_type: str
    amount: float
    frequency: str
    frequency_times: int  # 每年多少次
    years: int
    total_months: int

    # 核心指标
    total_invested: float = 0.0
    final_value: float = 0.0
    total_return: float = 0.0
    total_return_rate: float = 0.0
    annualized_return: float = 0.0

    # 情景分析
    scenario_analysis: Dict[str, Dict] = field(default_factory=dict)

    # 月度记录
    monthly_records: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "fund_name": self.fund_name,
            "fund_code": self.fund_code,
            "fund_type": self.fund_type,
            "amount": self.amount,
            "frequency": self.frequency,
            "frequency_times": self.frequency_times,
            "years": self.years,
            "total_months": self.total_months,
            "total_invested": round(self.total_invested, 2),
            "final_value": round(self.final_value, 2),
            "total_return": round(self.total_return, 2),
            "total_return_rate": round(self.total_return_rate, 4),
            "annualized_return": round(self.annualized_return, 4),
            "scenario_analysis": self.scenario_analysis,
            "monthly_records": self.monthly_records,
        }

    def summary(self) -> str:
        """生成摘要文本"""
        lines = [
            f"📊 定投计算报告：{self.fund_name}",
            f"{'─'*40}",
            f"基金代码：{self.fund_code} | 类型：{self.fund_type}",
            f"定投方案：{self.frequency} {self.amount}元",
            f"定投期限：{self.years}年（共{self.total_months}期）",
            f"",
            f"【核心指标】",
            f"累计投入：{self.total_invested:,.2f} 元",
            f"期末总资产：{self.final_value:,.2f} 元",
            f"累计收益：{self.total_return:,.2f} 元",
            f"累计收益率：{self.total_return_rate*100:.2f}%",
            f"年化收益率：{self.annualized_return*100:.2f}%",
        ]
        return "\n".join(lines)

    def scenario_summary(self) -> str:
        """生成情景分析文本"""
        lines = [f"{'─'*40}", f"【收益率情景分析】"]
        for key, s in self.scenario_analysis.items():
            lines.append(
                f"• {s['label']}（{s['desc']}）："
                f"期末资产 {s['final_value']:,.2f} 元，"
                f"累计收益 {s['total_return']:,.2f} 元，"
                f"收益率 {s['return_rate']*100:.2f}%，"
                f"年化 {s['annualized_return']*100:.2f}%"
            )
        return "\n".join(lines)


class DCACalculatorEngine:
    """定投计算引擎"""

    def __init__(self):
        self.funds = BUILTIN_FUNDS.copy()

    def calculate(
        self,
        fund_name: str,
        amount: float,
        frequency: str = "每月",
        years: int = 3,
        expected_return: float = 0.08,
    ) -> DCAResult:
        """
        计算定投收益

        Args:
            fund_name: 基金名称（支持内置名称模糊匹配）
            amount: 每次定投金额（元）
            frequency: 定投频率（每月/每周/每两周/每季/每年）
            years: 定投年限
            expected_return: 预期年化收益率（默认8%）

        Returns:
            DCAResult 对象
        """
        # 匹配基金
        matched = self._match_fund(fund_name)
        fund = self.funds[matched]

        # 频率
        freq_times = FREQ_MAP.get(frequency, 12)
        periods_per_year = freq_times
        total_periods = periods_per_year * years
        period_return = (1 + expected_return) ** (1 / periods_per_year) - 1

        # 模拟月度（每期）定投
        monthly_records: List[MonthlyRecord] = []
        total_shares = 0.0
        cumulative_invested = 0.0
        current_nav = 1.0  # 假设初始净值1.0

        for period in range(1, total_periods + 1):
            # 本期投入
            invested = amount
            cumulative_invested += invested

            # 假设每期净值按复利增长
            nav = current_nav * (1 + period_return)
            shares_bought = invested / nav
            total_shares += shares_bought
            account_value = total_shares * nav

            record = MonthlyRecord(
                month=period,
                invested=invested,
                nav=nav,
                shares=shares_bought,
                total_shares=total_shares,
                cumulative_invested=cumulative_invested,
                account_value=account_value,
            )
            monthly_records.append(record)
            current_nav = nav

        final_value = total_shares * current_nav
        total_invested = cumulative_invested
        total_return = final_value - total_invested
        total_return_rate = total_return / total_invested if total_invested > 0 else 0

        # 年化收益率（简化版：几何平均）
        annualized_return = (final_value / total_invested) ** (1 / years) - 1

        # 情景分析
        scenario_analysis = self._calc_scenarios(
            amount, periods_per_year, years, total_invested, final_value
        )

        # 月度记录（取关键期次：前12期+后12期+每12期的记录）
        simplified_records = self._simplify_records(monthly_records)

        result = DCAResult(
            fund_name=fund["name"],
            fund_code=fund["code"],
            fund_type=fund["type"],
            amount=amount,
            frequency=frequency,
            frequency_times=periods_per_year,
            years=years,
            total_months=total_periods,
            total_invested=total_invested,
            final_value=final_value,
            total_return=total_return,
            total_return_rate=total_return_rate,
            annualized_return=annualized_return,
            scenario_analysis=scenario_analysis,
            monthly_records=simplified_records,
        )
        return result

    def _match_fund(self, name: str) -> str:
        """模糊匹配基金名称"""
        # 精确匹配
        if name in self.funds:
            return name
        # 模糊匹配
        for key in self.funds:
            if key in name or name in key:
                return key
        # 代码匹配
        for key, fund in self.funds.items():
            if fund["code"] == name:
                return key
        # 默认返回沪深300
        return "沪深300"

    def _calc_scenarios(
        self,
        amount: float,
        periods_per_year: int,
        years: int,
        total_invested: float,
        neutral_final: float,
    ) -> Dict[str, Dict]:
        """计算三种收益率情景"""
        result = {}
        for key, s in SCENARIOS.items():
            annual = s["annual_return"]
            period_ret = (1 + annual) ** (1 / periods_per_year) - 1
            total_periods = periods_per_year * years

            # 模拟
            shares = 0.0
            nav = 1.0
            for _ in range(total_periods):
                shares += amount / nav
                nav *= 1 + period_ret

            fv = shares * nav
            total_ret = fv - total_invested
            ret_rate = total_ret / total_invested if total_invested > 0 else 0
            ann_ret = (fv / total_invested) ** (1 / years) - 1

            result[key] = {
                "label": s["label"],
                "desc": s["desc"],
                "annual_return": annual,
                "final_value": round(fv, 2),
                "total_return": round(total_ret, 2),
                "return_rate": round(ret_rate, 4),
                "annualized_return": round(ann_ret, 4),
            }
        return result

    def _simplify_records(self, records: List[MonthlyRecord]) -> List[Dict]:
        """精简月度记录，保留关键期次"""
        n = len(records)
        if n <= 24:
            indices = list(range(n))
        else:
            indices = list(range(12)) + list(range(12, n - 12, max(1, (n - 24) // 12))) + list(range(n - 12, n))
            indices = sorted(set(indices))

        return [
            {
                "month": r.month,
                "invested": round(r.invested, 2),
                "nav": round(r.nav, 4),
                "shares": round(r.shares, 4),
                "total_shares": round(r.total_shares, 4),
                "cumulative_invested": round(r.cumulative_invested, 2),
                "account_value": round(r.account_value, 2),
            }
            for r in [records[i] for i in indices]
        ]

    @staticmethod
    def parse_command(text: str) -> Dict:
        """
        解析自然语言命令
        格式示例："定投计算 沪深300 每月1000元 3年"
        """
        text = text.strip()

        # 提取基金名（匹配内置基金）
        fund_name = "沪深300"
        for name in sorted(BUILTIN_FUNDS.keys(), key=lambda x: -len(x)):
            if name in text:
                fund_name = name
                break

        # 提取金额（优先匹配"XXXX元"，避免匹配基金代码中的数字）
        amount = 1000
        amount_patterns = [
            (r"(\d+)\s*万\s*元", 10000),
            (r"(\d+)\s*千\s*元", 1000),
            (r"(\d+)\s*元", 1),
            # Fallback: number near frequency word
            (r"(?:每周|每月|每季|每年|每两周)(\d+)", 1),
            (r"(\d+)", 1),
        ]
        for pattern, multiplier in amount_patterns:
            m = re.search(pattern, text)
            if m:
                amount = int(m.group(1)) * multiplier
                break

        # 提取频率
        frequency = "每月"
        if "每周" in text:
            frequency = "每周"
        elif "每两周" in text or "双周" in text:
            frequency = "每两周"
        elif "每季" in text or "季度" in text:
            frequency = "每季"
        elif "每年" in text:
            frequency = "每年"

        # 提取年限
        years = 3
        years_patterns = [
            (r"(\d+)\s*[年]", 1),
            (r"(\d+)\s*个月", 1/12),
        ]
        for pattern, multiplier in years_patterns:
            m = re.search(pattern, text)
            if m:
                years = float(m.group(1)) * multiplier
                years = max(1, int(round(years)))
                break

        return {
            "fund_name": fund_name,
            "amount": amount,
            "frequency": frequency,
            "years": years,
        }


def calculate_dca(
    fund_name: str,
    amount: float,
    frequency: str = "每月",
    years: int = 3,
    expected_return: float = 0.08,
) -> DCAResult:
    """便捷函数"""
    engine = DCACalculatorEngine()
    return engine.calculate(fund_name, amount, frequency, years, expected_return)
