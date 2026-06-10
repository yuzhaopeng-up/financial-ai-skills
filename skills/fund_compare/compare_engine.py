"""
基金对比引擎 (FundCompareEngine)
支持 2-4 只基金的多维度对比分析
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Optional


# =============================================================================
# 数据模型
# =============================================================================

@dataclass
class ReturnData:
    m1: float = 0.0   # 近1月
    m3: float = 0.0   # 近3月
    m6: float = 0.0   # 近6月
    y1: float = 0.0   # 近1年
    y3: float = 0.0   # 近3年


@dataclass
class RiskData:
    sharpe: float = 0.0      # 夏普比率
    max_drawdown: float = 0.0  # 最大回撤 (正数)
    volatility: float = 0.0   # 波动率
    calmar: float = 0.0      # 卡玛比率


@dataclass
class FundInfo:
    code: str = ""
    name: str = ""
    fund_type: str = ""       # 基金类型
    scale: float = 0.0        # 规模（亿元）
    establish_date: str = ""  # 成立日期
    management_fee: float = 0.0  # 管理费率
    manager: str = ""          # 基金经理
    manager_tenure: str = ""  # 任职时间
    manager_exp: int = 0       # 从业年限


@dataclass
class AssetAllocation:
    stock_pct: float = 0.0   # 股票仓位 %
    bond_pct: float = 0.0   # 债券仓位 %
    cash_pct: float = 0.0   # 现金仓位 %
    top_holdings: list = field(default_factory=list)  # 前十大持仓


@dataclass
class FundProfile:
    """单只基金完整档案"""
    code: str
    name: str
    returns: ReturnData = field(default_factory=ReturnData)
    risk: RiskData = field(default_factory=RiskData)
    info: FundInfo = field(default_factory=FundInfo)
    allocation: AssetAllocation = field(default_factory=AssetAllocation)
    score: float = 0.0  # 综合评分


# =============================================================================
# 内置基金数据库（演示数据）
# =============================================================================

BUILTIN_FUNDS: dict[str, FundProfile] = {}


def _init_builtin():
    global BUILTIN_FUNDS

    data = {
        # ---- 明星股票/混合型 ----
        "XXXXXX": FundProfile(
            code="XXXXXX", name="某基金公司中小盘混合",
            returns=ReturnData(m1=3.2, m3=8.5, m6=15.3, y1=28.6, y3=89.2),
            risk=RiskData(sharpe=1.85, max_drawdown=23.5, volatility=18.2, calmar=1.22),
            info=FundInfo(
                code="XXXXXX", name="某基金公司中小盘混合",
                fund_type="混合型", scale=189.5, establish_date="2008-06-19",
                management_fee=0.015, manager="张坤", manager_tenure="6年2个月", manager_exp=12
            ),
            allocation=AssetAllocation(
                stock_pct=80.5, bond_pct=0.0, cash_pct=19.5,
                top_holdings=["某白酒龙头企业", "某白酒企业", "泸州老窖", "海康威视", "上海机场"]
            ),
        ),
        "163402": FundProfile(
            code="163402", name="兴全趋势投资混合",
            returns=ReturnData(m1=2.1, m3=6.8, m6=12.1, y1=22.3, y3=76.8),
            risk=RiskData(sharpe=1.62, max_drawdown=19.8, volatility=15.6, calmar=1.13),
            info=FundInfo(
                code="163402", name="兴全趋势投资混合",
                fund_type="混合型", scale=234.1, establish_date="2005-11-03",
                management_fee=0.015, manager="董承非", manager_tenure="8年3个月", manager_exp=15
            ),
            allocation=AssetAllocation(
                stock_pct=72.3, bond_pct=10.2, cash_pct=17.5,
                top_holdings=["某大型保险集团", "万科A", "某股份制银行", "三一重工", "紫金矿业"]
            ),
        ),
        "260101": FundProfile(
            code="260101", name="景顺长城新兴成长混合",
            returns=ReturnData(m1=4.1, m3=9.2, m6=16.8, y1=31.5, y3=95.3),
            risk=RiskData(sharpe=1.95, max_drawdown=25.6, volatility=19.8, calmar=1.23),
            info=FundInfo(
                code="260101", name="景顺长城新兴成长混合",
                fund_type="混合型", scale=142.3, establish_date="2006-06-28",
                management_fee=0.015, manager="刘彦春", manager_tenure="5年8个月", manager_exp=14
            ),
            allocation=AssetAllocation(
                stock_pct=85.2, bond_pct=0.0, cash_pct=14.8,
                top_holdings=["某白酒企业", "泸州老窖", "某白酒龙头企业", "中国中免", "迈瑞医疗"]
            ),
        ),
        "519068": FundProfile(
            code="519068", name="汇添富价值精选混合",
            returns=ReturnData(m1=2.5, m3=7.1, m6=13.5, y1=24.8, y3=82.1),
            risk=RiskData(sharpe=1.72, max_drawdown=21.3, volatility=16.5, calmar=1.16),
            info=FundInfo(
                code="519068", name="汇添富价值精选混合",
                fund_type="混合型", scale=198.7, establish_date="2009-01-23",
                management_fee=0.015, manager="劳杰男", manager_tenure="7年1个月", manager_exp=10
            ),
            allocation=AssetAllocation(
                stock_pct=78.6, bond_pct=5.3, cash_pct=16.1,
                top_holdings=["某股份制银行", "某大型保险集团", "某城商行", "某家电龙头企业", "海螺水泥"]
            ),
        ),
        "000831": FundProfile(
            code="000831", name="工银医疗保健股票",
            returns=ReturnData(m1=5.8, m3=12.3, m6=18.9, y1=38.2, y3=102.5),
            risk=RiskData(sharpe=2.05, max_drawdown=28.9, volatility=22.1, calmar=1.32),
            info=FundInfo(
                code="000831", name="工银医疗保健股票",
                fund_type="股票型", scale=86.4, establish_date="2014-11-18",
                management_fee=0.015, manager="赵蓓", manager_tenure="6年5个月", manager_exp=8
            ),
            allocation=AssetAllocation(
                stock_pct=92.1, bond_pct=0.0, cash_pct=7.9,
                top_holdings=["药明康德", "爱尔眼科", "泰格医药", "凯莱英", "迈瑞医疗"]
            ),
        ),
        # ---- 指数型 ----
        "510300": FundProfile(
            code="510300", name="华泰柏瑞沪深300ETF",
            returns=ReturnData(m1=1.8, m3=5.2, m6=9.8, y1=18.5, y3=58.3),
            risk=RiskData(sharpe=1.28, max_drawdown=32.1, volatility=17.2, calmar=0.58),
            info=FundInfo(
                code="510300", name="华泰柏瑞沪深300ETF",
                fund_type="指数型", scale=456.2, establish_date="2012-05-04",
                management_fee=0.005, manager="柳军", manager_tenure="9年2个月", manager_exp=12
            ),
            allocation=AssetAllocation(
                stock_pct=99.2, bond_pct=0.0, cash_pct=0.8,
                top_holdings=["某白酒龙头企业", "某股份制银行", "某大型保险集团", "某光伏龙头企业", "某白酒企业"]
            ),
        ),
        "159915": FundProfile(
            code="159915", name="某基金公司创业板ETF",
            returns=ReturnData(m1=4.5, m3=10.8, m6=19.2, y1=35.8, y3=108.6),
            risk=RiskData(sharpe=1.92, max_drawdown=38.5, volatility=24.3, calmar=0.93),
            info=FundInfo(
                code="159915", name="某基金公司创业板ETF",
                fund_type="指数型", scale=182.3, establish_date="2011-09-20",
                management_fee=0.005, manager="刘树荣", manager_tenure="8年6个月", manager_exp=9
            ),
            allocation=AssetAllocation(
                stock_pct=99.5, bond_pct=0.0, cash_pct=0.5,
                top_holdings=["某新能源龙头企业", "某互联网券商", "迈瑞医疗", "爱尔眼科", "智飞生物"]
            ),
        ),
        # ---- 债券型 ----
        "000171": FundProfile(
            code="000171", name="某基金公司高等级信用债",
            returns=ReturnData(m1=0.8, m3=2.1, m6=3.9, y1=6.2, y3=18.5),
            risk=RiskData(sharpe=1.85, max_drawdown=3.2, volatility=3.8, calmar=1.94),
            info=FundInfo(
                code="000171", name="某基金公司高等级信用债",
                fund_type="债券型", scale=52.3, establish_date="2013-09-10",
                management_fee=0.006, manager="胡剑", manager_tenure="5年11个月", manager_exp=9
            ),
            allocation=AssetAllocation(
                stock_pct=0.0, bond_pct=92.5, cash_pct=7.5,
                top_holdings=["国家债券", "政策性金融债", "AAA企业债"]
            ),
        ),
        "217022": FundProfile(
            code="217022", name="招商产业债券",
            returns=ReturnData(m1=0.6, m3=1.8, m6=3.5, y1=5.8, y3=17.2),
            risk=RiskData(sharpe=1.72, max_drawdown=2.8, volatility=3.2, calmar=2.07),
            info=FundInfo(
                code="217022", name="招商产业债券",
                fund_type="债券型", scale=68.9, establish_date="2012-03-21",
                management_fee=0.006, manager="马龙", manager_tenure="6年3个月", manager_exp=7
            ),
            allocation=AssetAllocation(
                stock_pct=0.0, bond_pct=94.2, cash_pct=5.8,
                top_holdings=["国家债券", "政策性金融债", "高等级信用债"]
            ),
        ),
        # ---- 知名基金名称映射 ----
        "某基金公司中小盘": "XXXXXX",
        "兴全趋势": "163402",
        "景顺新兴成长": "260101",
        "汇添富价值精选": "519068",
        "工银医疗保健": "000831",
        "沪深300ETF": "510300",
        "创业板ETF": "159915",
        "某基金公司高等级信用债": "000171",
        "招商产业债券": "217022",
    }

    # 构建 code -> FundProfile 映射（补充 name 别名）
    for key, fund in data.items():
        if key in BUILTIN_FUNDS:
            continue
        if isinstance(fund, FundProfile):
            BUILTIN_FUNDS[key] = fund

_init_builtin()


# =============================================================================
# 核心引擎
# =============================================================================

class FundCompareEngine:
    """
    基金对比引擎
    输入 2-4 个基金代码或名称，返回对比分析结果
    """

    def __init__(self):
        self.funds_db = BUILTIN_FUNDS

    # ---- 解析 ----

    def resolve(self, query: str) -> list[str]:
        """将用户输入解析为标准化基金代码列表"""
        # 清理输入
        query = re.sub(r"(基金对比|比较|对比)\s*", "", query.strip())
        parts = re.split(r"[,\s]+", query)
        codes = []
        for p in parts:
            p = p.strip()
            if not p:
                continue
            # 如果直接是代码（6位数字）
            if re.match(r"^\d{6}$", p):
                codes.append(p)
            else:
                # 尝试名称映射
                mapped = self.funds_db.get(p)
                if mapped:
                    codes.append(mapped.code)
                else:
                    # 模糊匹配
                    found = self._fuzzy_match(p)
                    if found:
                        codes.append(found)
        return list(dict.fromkeys(codes))  # 去重保序

    def _fuzzy_match(self, name: str) -> Optional[str]:
        """模糊匹配基金名称"""
        name_lower = name.lower()
        for key, fund in self.funds_db.items():
            if name_lower in key.lower() or name_lower in fund.name.lower():
                return fund.code
        return None

    # ---- 评分 ----

    def _score_fund(self, fp: FundProfile) -> float:
        """计算综合评分（0-100）"""
        s = 0.0
        # 收益评分（30分）：近1年 + 近3年
        ret_score = (fp.returns.y1 * 0.4 + fp.returns.y3 * 0.6 / 3)
        s += min(ret_score / 1.5, 30)
        # 风险评分（30分）：夏普比率
        s += min(fp.risk.sharpe * 10, 30)
        # 风险控制（20分）：最大回撤
        dd_score = max(0, 20 - fp.risk.max_drawdown * 0.5)
        s += dd_score
        # 稳定性（20分）：卡玛比率
        s += min(fp.risk.calmar * 5, 20)
        return round(min(s, 100), 1)

    # ---- 主流程 ----

    def compare(self, inputs: list[str]) -> dict:
        """
        核心对比方法
        inputs: 基金代码或名称列表（2-4个）
        返回: {
            profiles: [FundProfile, ...],
            comparison_table: dict,
            recommendation: str,
            analysis: str,
            scores: dict
        }
        """
        # 解析
        codes = []
        for inp in inputs:
            resolved = self.resolve(inp)
            codes.extend(resolved)

        codes = list(dict.fromkeys(codes))[:4]  # 最多4个
        if len(codes) < 2:
            raise ValueError("至少需要2只基金进行对比")

        # 获取基金档案
        profiles = []
        for code in codes:
            fund = self.funds_db.get(code)
            if not fund:
                raise ValueError(f"未找到基金: {code}")
            fp = FundProfile(
                code=fund.code,
                name=fund.name,
                returns=fund.returns,
                risk=fund.risk,
                info=fund.info,
                allocation=fund.allocation,
            )
            fp.score = self._score_fund(fp)
            profiles.append(fp)

        # 构建对比表
        comp = self._build_comparison(profiles)

        # 综合推荐
        recommendation = self._build_recommendation(profiles)

        # 差异分析
        analysis = self._build_analysis(profiles)

        scores = {fp.code: fp.score for fp in profiles}

        return {
            "profiles": profiles,
            "comparison_table": comp,
            "recommendation": recommendation,
            "analysis": analysis,
            "scores": scores,
        }

    # ---- 表格构建 ----

    def _build_comparison(self, profiles: list[FundProfile]) -> dict:
        """构建多维度对比表"""

        def fmt_pct(v: float) -> str:
            return f"{v:.2f}%" if v != 0 else "-"

        def fmt_years(y: float) -> str:
            return f"{y:.1f}年"

        rows = {
            "收益": {
                "近1月": [fmt_pct(p.returns.m1) for p in profiles],
                "近3月": [fmt_pct(p.returns.m3) for p in profiles],
                "近6月": [fmt_pct(p.returns.m6) for p in profiles],
                "近1年": [fmt_pct(p.returns.y1) for p in profiles],
                "近3年": [fmt_pct(p.returns.y3) for p in profiles],
            },
            "风险": {
                "夏普比率": [f"{p.risk.sharpe:.2f}" for p in profiles],
                "最大回撤": [fmt_pct(p.risk.max_drawdown) for p in profiles],
                "波动率": [fmt_pct(p.risk.volatility) for p in profiles],
                "卡玛比率": [f"{p.risk.calmar:.2f}" for p in profiles],
            },
            "基本信息": {
                "基金类型": [p.info.fund_type for p in profiles],
                "规模(亿元)": [f"{p.info.scale:.1f}" for p in profiles],
                "成立日期": [p.info.establish_date for p in profiles],
                "管理费率": [f"{p.info.management_fee:.2%}" for p in profiles],
            },
            "基金经理": {
                "基金经理": [p.info.manager for p in profiles],
                "任职时间": [p.info.manager_tenure for p in profiles],
                "从业年限": [f"{p.info.manager_exp}年" for p in profiles],
            },
            "资产配置": {
                "股票仓位": [fmt_pct(p.allocation.stock_pct) for p in profiles],
                "债券仓位": [fmt_pct(p.allocation.bond_pct) for p in profiles],
                "现金仓位": [fmt_pct(p.allocation.cash_pct) for p in profiles],
            },
        }

        return {
            "headers": [f"{p.name}\n({p.code})" for p in profiles],
            "rows": rows,
        }

    # ---- 推荐 ----

    def _build_recommendation(self, profiles: list[FundProfile]) -> str:
        """生成综合推荐"""
        sorted_by_score = sorted(profiles, key=lambda x: x.score, reverse=True)
        winner = sorted_by_score[0]

        lines = [
            f"🏆 综合推荐：**{winner.name}**（{winner.code}）",
            f"   综合评分 {winner.score}/100（基于收益、风险、稳定性多维度）",
        ]

        if len(profiles) > 1:
            runner = sorted_by_score[1]
            lines.append(
                f"📌 次优选择：**{runner.name}**（{runner.code}）评分 {runner.score}/100"
            )

        return "\n".join(lines)

    # ---- 差异分析 ----

    def _build_analysis(self, profiles: list[FundProfile]) -> str:
        """生成差异分析"""
        lines = ["📊 差异分析："]

        # 收益维度
        best_y1 = max(profiles, key=lambda x: x.returns.y1)
        worst_y1 = min(profiles, key=lambda x: x.returns.y1)
        diff_y1 = best_y1.returns.y1 - worst_y1.returns.y1
        lines.append(
            f"- 收益：近1年最高 {best_y1.name}(+{best_y1.returns.y1:.1f}%)，"
            f"最低 {worst_y1.name}(+{worst_y1.returns.y1:.1f}%)，差距 {diff_y1:.1f}个百分点"
        )

        # 风险维度
        safest = min(profiles, key=lambda x: x.risk.max_drawdown)
        riskiest = max(profiles, key=lambda x: x.risk.max_drawdown)
        lines.append(
            f"- 风险：最大回撤最小 {safest.name}(-{safest.risk.max_drawdown:.1f}%)，"
            f"最大 {riskiest.name}(-{riskiest.risk.max_drawdown:.1f}%)"
        )

        # 夏普
        best_sharpe = max(profiles, key=lambda x: x.risk.sharpe)
        lines.append(
            f"- 性价比：夏普比率最高 {best_sharpe.name}({best_sharpe.risk.sharpe:.2f})，"
            f"风险调整后收益最优"
        )

        # 风格
        types = set(p.info.fund_type for p in profiles)
        if len(types) > 1:
            lines.append(f"- 风格：混合了 {'/'.join(types)} 不同类型基金，适合不同风险偏好")
        else:
            lines.append(f"- 风格：均为 {types.pop()}，风格一致，可直接对比收益风险")

        return "\n".join(lines)

    # ---- 输出渲染 ----

    def render_markdown(self, result: dict) -> str:
        """渲染为 Markdown 格式"""
        profiles = result["profiles"]
        comp = result["comparison_table"]
        headers = comp["headers"]
        rows = comp["rows"]

        # 表头
        header_line = "| 维度 | 子维度 | " + " | ".join(headers) + " |"
        sep_line = "|---|---|" + "|---" * len(headers) + "|"

        lines = ["# 基金对比报告\n"]
        lines.append(f"**对比基金**：{' vs '.join([p.name for p in profiles])}")
        lines.append(f"**生成时间**：近期\n")

        for section, sub_rows in rows.items():
            lines.append(f"\n## {section}\n")
            for sub_key, values in sub_rows.items():
                row = f"| {section} | {sub_key} | " + " | ".join(values) + " |"
                lines.append(header_line if sub_key == list(sub_rows.keys())[0] else "")
                lines.append(row)
                lines.append(sep_line)

        lines.append("\n## 综合评分\n")
        for code, score in result["scores"].items():
            fund = next(p for p in profiles if p.code == code)
            lines.append(f"- **{fund.name}**（{code}）：{score}/100")

        lines.append("\n## 推荐\n")
        lines.append(result["recommendation"])
        lines.append("\n## 差异分析\n")
        lines.append(result["analysis"])

        return "\n".join(lines)

    def render_wecom_card(self, result: dict) -> dict:
        """渲染为企微卡片格式"""
        profiles = result["profiles"]
        scores = result["scores"]

        # 构建对比字段
        fields = []
        comp = result["comparison_table"]
        rows = comp["rows"]

        # 关键指标对比（每个基金一行）
        for i, p in enumerate(profiles):
            name = p.name
            y1 = p.returns.y1
            dd = p.risk.max_drawdown
            sharpe = p.risk.sharpe
            score = scores[p.code]
            fields.append({
                "name": name,
                "value": f"评分:{score}分 | 近1年:+{y1:.1f}% | 最大回撤:{dd:.1f}% | 夏普:{sharpe:.2f}"
            })

        # 找到最佳
        best_code = max(scores, key=scores.get)
        best = next(p for p in profiles if p.code == best_code)

        card = {
            "type": "template",
            "data": {
                "template_id": "fund_compare_card",
                "theme_color": "#165DFF",
                "elements": [
                    {
                        "tag": "title",
                        "text": f"🏆 基金对比报告 | 推荐 {best.name}"
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "div",
                        "text": f"综合评分：{best.name}（{best.code}）以 **{scores[best.code]}分** 位居首位"
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "columns",
                        "fields": fields
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "note",
                        "elements": [
                            {"tag": "text", "text": result["recommendation"]}
                        ]
                    }
                ]
            }
        }

        return card
