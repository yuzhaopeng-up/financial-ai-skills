"""
研报生成引擎
============

输入：行业/公司/年度 任意组合
输出：完整投研报告（摘要+行业+公司+财务+风险+建议）

支持自然语言：
  研报生成 新能源 宁德时代 2025
  研报 招商银行 2025
  研报生成 半导体行业 2025
  研报 比亚迪
"""
from __future__ import annotations
import json
import os
import re
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_PATH = os.path.join(HERE, "report_templates.json")


def _load_templates() -> Dict[str, Any]:
    with open(TEMPLATES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@dataclass
class ReportRequest:
    """报告请求参数。"""
    industry: str = ""    # 新能源/金融/半导体/...
    company: str = ""     # 宁德时代/招商银行/...
    year: int = 0         # 报告年度，0=当年
    raw_text: str = ""


@dataclass
class ResearchReport:
    """生成的研报。"""
    request: ReportRequest
    title: str
    summary: str
    industry_section: Dict[str, Any]   # {趋势/驱动/风险/龙头/指标}
    company_section: Dict[str, Any]    # {基本面/亮点/护城河/风险}
    financial_section: Dict[str, Any]  # {估值参考/关键指标/财务画像}
    risks: List[str]                   # 风险提示清单
    investment_view: Dict[str, Any]    # {评级/理由/目标价区间/逻辑}
    generated_at: str
    confidence: float                  # 0-1，模板覆盖率（覆盖知名公司=1.0，纯通用模板=0.5）

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ========== 自然语言解析 ==========

CURRENT_YEAR = datetime.now().year

def parse_request(text: str) -> ReportRequest:
    """从自然语言提取行业/公司/年度。"""
    text = text.strip()
    text = re.sub(r"^研报生成\s*", "", text)
    text = re.sub(r"^研报\s*", "", text)
    text = re.sub(r"^生成研报\s*", "", text)

    req = ReportRequest(raw_text=text)
    templates = _load_templates()

    # 年度
    m = re.search(r"(20\d{2})", text)
    if m:
        req.year = int(m.group(1))
    else:
        req.year = CURRENT_YEAR

    # 公司（已知列表优先匹配）
    for company in templates["companies"]:
        if company in text:
            req.company = company
            req.industry = templates["companies"][company]["industry"]
            return req

    # 行业（已知列表）
    for industry in templates["industries"]:
        if industry == "通用": continue
        if industry in text:
            req.industry = industry
            break

    # 提取剩余 token 作为未知公司
    tokens = re.findall(r"[\u4e00-\u9fa5]+", text)
    for t in tokens:
        if t in templates["industries"] or t == "通用": continue
        if t in ("行业", "公司", "研报", "生成", "投研", "报告"): continue
        if len(t) >= 2 and not req.company:
            req.company = t
            break

    if not req.industry:
        req.industry = "通用"

    return req


# ========== 报告生成 ==========

class ReportEngine:
    """研报生成引擎。"""

    def __init__(self):
        self.templates = _load_templates()

    def generate(self, source) -> ResearchReport:
        """生成报告。

        Args:
            source: ReportRequest 实例 / 自然语言字符串 / dict
        """
        if isinstance(source, str):
            req = parse_request(source)
        elif isinstance(source, dict):
            req = ReportRequest(**{k: v for k, v in source.items()
                                   if k in ReportRequest.__dataclass_fields__})
            if not req.year: req.year = CURRENT_YEAR
        elif isinstance(source, ReportRequest):
            req = source
        else:
            raise TypeError(f"unsupported input type: {type(source)}")

        # 行业模板
        industry_data = self.templates["industries"].get(req.industry,
                                                          self.templates["industries"]["通用"])
        # 公司模板
        company_data = self.templates["companies"].get(req.company, None)

        # 标题
        if req.company and req.industry != "通用":
            title = f"【{req.year}】{req.company}（{req.industry}）投研报告"
        elif req.company:
            title = f"【{req.year}】{req.company} 投研报告"
        elif req.industry != "通用":
            title = f"【{req.year}】{req.industry} 行业研究报告"
        else:
            title = f"【{req.year}】综合投研报告"

        # 摘要
        summary = self._build_summary(req, industry_data, company_data)

        # 行业部分
        industry_section = {
            "core_trends": industry_data["trend_keywords"],
            "growth_drivers": industry_data["drivers"],
            "industry_risks": industry_data["risks"],
            "key_companies": industry_data["leaders"],
            "key_metrics": industry_data["key_metrics"],
        }

        # 公司部分
        if company_data:
            company_section = {
                "code": company_data.get("code", "-"),
                "business_segments": company_data["business_segments"],
                "moat": company_data["moat"],
                "highlights": company_data["highlights"],
                "specific_risks": company_data["risks"],
            }
        else:
            company_section = {
                "code": "-",
                "business_segments": ["待补充：建议查询年报/招股书"],
                "moat": ["待研究：建议从市占率/技术/品牌/规模四维分析"],
                "highlights": ["待补充：建议结合最新季度业绩"],
                "specific_risks": ["待补充：建议关注同业可比"],
            }

        # 财务部分
        financial_section = self._build_financial(req, industry_data, company_data)

        # 风险汇总
        risks = self._build_risks(industry_data, company_data, req)

        # 投资建议
        view = self._build_investment_view(req, industry_data, company_data)

        # 置信度
        confidence = 1.0 if company_data else (0.7 if req.industry != "通用" else 0.5)

        return ResearchReport(
            request=req,
            title=title,
            summary=summary,
            industry_section=industry_section,
            company_section=company_section,
            financial_section=financial_section,
            risks=risks,
            investment_view=view,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            confidence=confidence,
        )

    def _build_summary(self, req, industry_data, company_data):
        parts = []
        if company_data:
            moat0 = company_data["moat"][0] if company_data["moat"] else ""
            parts.append(f"{req.company}（{company_data.get('code', '')}）作为 {req.industry} 行业代表公司，{moat0}。")
            if company_data.get("highlights"):
                parts.append(f"近期亮点包括：{company_data['highlights'][0]}。")
        else:
            parts.append(f"{req.year} 年 {req.industry} 行业整体处于结构性机会期。")

        if industry_data["drivers"]:
            parts.append(f"行业核心驱动：{industry_data['drivers'][0]}。")
        if industry_data["risks"]:
            parts.append(f"关注风险：{industry_data['risks'][0]}。")
        return " ".join(parts)

    def _build_financial(self, req, industry_data, company_data):
        return {
            "valuation_reference": {
                "PE": "建议对比同业平均PE，结合PEG判断",
                "PB": "结合 ROE 拆解，关注估值与盈利匹配度",
                "DCF": "适用于现金流稳定的成熟期公司",
            },
            "core_metrics": industry_data["key_metrics"],
            "data_sources": [
                "公司定期报告（年报/季报）",
                "Wind/同花顺 iFinD",
                "公司公告及投资者关系活动",
                "行业协会数据",
                "Bloomberg/Refinitiv 国际比较",
            ],
            "comparable_companies": industry_data.get("leaders", [])[:5],
        }

    def _build_risks(self, industry_data, company_data, req):
        risks = []
        # 行业风险
        for r in industry_data["risks"]:
            risks.append(f"【行业】{r}")
        # 公司风险
        if company_data:
            for r in company_data["risks"]:
                risks.append(f"【公司】{r}")
        # 通用风险
        risks.append("【系统性】宏观经济波动、利率/汇率/政策变化等系统性风险")
        risks.append("【合规】部分前瞻性陈述可能存在与实际情况偏差，本报告不构成投资建议")
        return risks

    def _build_investment_view(self, req, industry_data, company_data):
        # 简单规则：明星行业+龙头公司 → 增持；普通组合 → 中性
        star_industries = {"新能源", "半导体", "医药", "金融"}
        if company_data and req.industry in star_industries:
            rating = "买入"
            reason = f"行业景气度高，公司具备 {company_data['moat'][0] if company_data['moat'] else '核心竞争力'}，业绩可持续性强"
        elif company_data:
            rating = "增持"
            reason = "公司基本面稳健，估值具备一定安全边际"
        elif req.industry in star_industries:
            rating = "增持"
            reason = f"{req.industry} 行业整体景气度向好，可重点关注龙头标的"
        else:
            rating = "中性"
            reason = "建议结合具体公司基本面进一步研究"

        return {
            "rating": rating,
            "rating_explanation": self.templates["templates"]["rating_system"][rating],
            "core_logic": reason,
            "target_price_note": "目标价测算需结合公司公告/最新季报，建议研究员人工复核",
            "timeframe": "未来 6-12 个月",
            "key_catalysts": (
                company_data["highlights"][:3] if company_data
                else industry_data["drivers"][:3]
            ),
        }


if __name__ == "__main__":
    eng = ReportEngine()
    r = eng.generate("研报生成 新能源 宁德时代 2025")
    print(json.dumps(r.to_dict(), ensure_ascii=False, indent=2))
