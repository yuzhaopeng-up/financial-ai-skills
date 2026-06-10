"""
SecuritiesResearchEngine — 投研报告生成引擎

输入公司名称/行业/研究类型，返回研究报告大纲、核心观点、数据支撑及投资建议。
所有输出使用"某公司"替代真实公司名，实现数据脱敏。
"""

from __future__ import annotations

import re
import random
from dataclasses import dataclass, field
from typing import Any


# ──────────────────────────────────────────────
# 行业研究框架定义
# ──────────────────────────────────────────────

INDUSTRY_FRAMEWORKS = {
    "银行": {
        "name": "银行",
        "key_metrics": ["净息差(NIM)", "不良贷款率", "拨备覆盖率", "资本充足率", "贷存比", "流动性覆盖率(LCR)", "净稳定资金比率(NSFR)"],
        "financial_indicators": {
            "盈利能力": ["净利息收入", "非利息收入", "成本收入比", "ROE", "ROA"],
            "资产质量": ["不良贷款余额", "不良率", "关注类贷款", "逾期贷款"],
            "资本充足": ["核心一级资本", "一级资本", "资本充足率", "杠杆率"],
        },
        "core_view_template": [
            "某银行资产规模稳步增长，截至最新报告期，总资产约{total_asset}亿元，",
            "净息差为{nim}%，较上年同期{Direction}{bps}bps，",
            "主要受{Direction}因素影响：{factor}。",
            "资产质量方面，不良贷款率为{npl}%，整体{quality_assessment}。",
            "公司积极推进{Direction}转型，{business_highlight}业务表现亮眼。",
        ],
        "investment_rating": {
            "strong_buy": ["净息差企稳回升", "资产质量改善", "数字化转型领先"],
            "hold": ["净息差承压", "资产质量平稳", "业务转型中"],
            "sell": ["资产质量恶化", "资本充足率下滑", "监管处罚"],
        },
    },
    "证券": {
        "name": "证券",
        "key_metrics": ["经纪业务市占率", "投行承销规模", "资管AUM", "自营投资收益率", "两融余额"],
        "financial_indicators": {
            "经纪业务": ["股基交易额", "佣金率", "市占率"],
            "投行业务": ["IPO承销规模", "再融资规模", "债券承销规模", "并购顾问收入"],
            "资管业务": ["集合资管规模", "定向资管规模", "专项资管规模", "资管收入"],
            "自营业务": ["投资收益", "公允价值变动", "固收投资收益率", "权益投资收益率"],
        },
        "core_view_template": [
            "某证券公司为{Direction}特色券商，业务布局覆盖经纪/投行/资管/自营四大板块。",
            "经纪业务方面，受市场交易量{Direction}影响，",
            "最新报告期股基交易额为{turnover}亿元，{Direction}。",
            "投行业务方面，IPO承销规模为{ipo_scale}亿元，排名行业第{rank}位。",
            "自营业务方面，{direction}收益率表现为{return_rate}%。",
        ],
        "investment_rating": {
            "strong_buy": ["投行业务爆发", "资管收入高增长", "权益投资超预期"],
            "hold": ["经纪业务承压", "自营收益平稳", "业务结构优化中"],
            "sell": ["自营大幅亏损", "投行收入骤降", "监管处罚"],
        },
    },
    "保险": {
        "name": "保险",
        "key_metrics": ["寿险EV增速", "NBV增速", "产险综合成本率", "险资投资收益率", "偿付能力充足率"],
        "financial_indicators": {
            "寿险": ["原保险保费收入", "新业务价值(NBV)", "内含价值(EV)", "退保率", "续期保费"],
            "产险": ["原保险保费收入", "综合成本率", "赔付率", "费用率"],
            "险资运用": ["总投资收益率", "净投资收益率", "大类资产配置"],
        },
        "core_view_template": [
            "某保险公司寿险业务表现{performance}，",
            "NBV增速为{nbv_growth}%，EV增速为{ev_growth}%。",
            "产险综合成本率为{cost_rate}%，{assessment}。",
            "险资总投资收益率为{inv_return}%，{direction}。",
        ],
        "investment_rating": {
            "strong_buy": ["NBV超预期增长", "综合成本率改善", "投资端表现优异"],
            "hold": ["NBV增速放缓", "综合成本率平稳", "投资收益率承压"],
            "sell": ["综合成本率大幅恶化", "偿付能力不足", "重大赔付事件"],
        },
    },
    "房地产": {
        "name": "房地产",
        "key_metrics": ["合同销售金额", "合同销售面积", "土地储备", "拿地成本", "融资成本", "经营性现金流"],
        "financial_indicators": {
            "开发业务": ["合同销售", "结算收入", "毛利率", "归母净利润"],
            "土地储备": ["总土储面积", "土储成本", "楼面价", "土储年限"],
            "财务结构": ["资产负债率", "净负债率", "现金短债比", "融资成本"],
        },
        "core_view_template": [
            "某房地产公司销售表现{performance}，",
            "最新报告期合同销售金额为{sales_amount}亿元，{direction}。",
            "土地储备约{land_reserve}万平方米，楼面价约{floor_price}元/㎡，成本可控。",
            "公司积极推进{strategy}战略，{business_highlight}。",
            "财务结构方面，净负债率为{debt_ratio}%，{assessment}。",
        ],
        "investment_rating": {
            "strong_buy": ["销售超预期", "融资成本下降", "政策放松受益"],
            "hold": ["销售平稳", "土地储备合理", "融资渠道通畅"],
            "sell": ["销售大幅下滑", "资金链紧张", "项目去化困难"],
        },
    },
    "医药": {
        "name": "医药",
        "key_metrics": ["研发费用率", "研发管线数量", "创新药收入占比", "学术推广费用", "招标价格"],
        "financial_indicators": {
            "化学制药": ["制剂收入", "原料药收入", "出口收入", "毛利率"],
            "生物制药": ["疫苗收入", "抗体药物收入", "细胞治疗收入"],
            "医疗器械": ["设备收入", "耗材收入", "IVD收入"],
            "商业流通": ["医药商业收入", "零售药房收入"],
        },
        "core_view_template": [
            "某医药公司深耕{therapeutic_area}领域，",
            "研发费用为{rnd_expense}亿元，占营收比重为{rnd_ratio}%。",
            "公司在研管线{count}个，其中{highlight}已进入{stage}阶段。",
            "公司产品线覆盖{coverage}，{assessment}竞争格局。",
        ],
        "investment_rating": {
            "strong_buy": ["创新药获批", "管线超预期", "政策免疫"],
            "hold": ["存量品种稳定", "研发稳步推进", "带量采购影响可控"],
            "sell": ["主力品种丢标", "研发失败", "重大安全事件"],
        },
    },
    "科技": {
        "name": "科技/半导体",
        "key_metrics": ["研发费用率", "专利数量", "量产良率", "产能利用率", "国产化率"],
        "financial_indicators": {
            "设计": ["芯片出货量", "ASP", "毛利率", "市场份额"],
            "制造": ["先进制程产能", "产能利用率", "工艺良率", "资本开支"],
            "封装测试": ["封装收入", "测试收入", "先进封装收入占比"],
            "设备材料": ["设备收入", "材料收入", "国产化率"],
        },
        "core_view_template": [
            "某科技公司为{segment}领域{Direction}企业，",
            "最新报告期营收为{revenue}亿元，{direction}。",
            "研发费用为{rnd_expense}亿元，研发费用率{rnd_ratio}%，{assessment}。",
            "公司{Direction}进展显著：{progress}。",
            "受益于{upstream}需求回暖，{assessment2}。",
        ],
        "investment_rating": {
            "strong_buy": ["技术突破", "订单超预期", "国产替代加速"],
            "hold": ["技术稳步推进", "订单平稳", "行业景气度适中"],
            "sell": ["技术落后", "订单丢失", "行业景气下行"],
        },
    },
    "消费": {
        "name": "消费",
        "key_metrics": ["收入增速", "毛利率", "净利率", "存货周转", "渠道库存"],
        "financial_indicators": {
            "品牌力": ["品牌收入占比", "品牌溢价率", "品牌知名度"],
            "渠道力": ["电商收入占比", "线下门店数", "经销商数量"],
            "产品力": ["新品收入占比", "SKU数量", "爆款占比"],
            "供应链": ["存货周转天数", "应付账款周转", "现金循环周期"],
        },
        "core_view_template": [
            "某消费品公司主攻{market_segment}市场，",
            "最新报告期营收为{revenue}亿元，{direction}增速{growth_rate}%。",
            "毛利率为{gp_margin}%，{gp_assessment}。",
            "渠道结构持续优化，{channel_highlight}。",
            "品牌建设成效显著，{brand_highlight}。",
        ],
        "investment_rating": {
            "strong_buy": ["收入超预期", "毛利率改善", "渠道扩张超预期"],
            "hold": ["收入平稳增长", "毛利率稳定", "渠道优化中"],
            "sell": ["收入下滑", "毛利率大幅下降", "库存积压"],
        },
    },
    "新能源": {
        "name": "新能源",
        "key_metrics": ["装机容量", "发电量", "利用小时数", "弃风弃光率", "上网电价", "成本曲线"],
        "financial_indicators": {
            "光伏": ["组件出货量", "电池片产能", "毛利率", "中标价格"],
            "风电": ["风机出货量", "在手订单", "装机容量", "风电利用小时"],
            "储能": ["储能出货量", "PACK能量密度", "毛利率", "在手订单"],
            "电网": ["中标金额", "特高压订单", "海外订单"],
        },
        "core_view_template": [
            "某新能源公司为{segment}领域{Direction}企业，",
            "最新报告期{metric}为{value}，{direction}。",
            "公司{segment}产能约{capacity}，{capacity_assessment}。",
            "公司积极推进{strategy}，{business_highlight}。",
            "受益于{policy}，{assessment}。",
        ],
        "investment_rating": {
            "strong_buy": ["装机超预期", "成本优势显著", "政策大力支持"],
            "hold": ["装机平稳", "成本优势稳固", "政策平稳"],
            "sell": ["装机下滑", "成本优势收窄", "政策收紧"],
        },
    },
    "能源": {
        "name": "能源/煤炭",
        "key_metrics": ["原煤产量", "商品煤销量", "煤炭价格", "长协比例", "运输成本"],
        "financial_indicators": {
            "生产": ["原煤产量", "商品煤产量", "掘进进尺", "回采率"],
            "销售": ["商品煤销量", "长协销量", "现货销量", "平均售价"],
            "财务": ["吨煤成本", "毛利率", "净利率", "EBITDA"],
        },
        "core_view_template": [
            "某煤炭公司为{Direction}大型煤企，",
            "最新报告期原煤产量为{coal_output}万吨，{direction}。",
            "商品煤售价约{price}元/吨，{price_assessment}。",
            "公司长协比例约{long_contract_ratio}%，{assessment}。",
            "财务方面，吨煤成本约{cost}元/吨，{cost_assessment}。",
        ],
        "investment_rating": {
            "strong_buy": ["煤价超预期上涨", "产量增长", "成本管控优秀"],
            "hold": ["煤价平稳", "产量平稳", "成本稳定"],
            "sell": ["煤价大幅下跌", "安全停产", "重大事故"],
        },
    },
    "钢铁": {
        "name": "钢铁/建材",
        "key_metrics": ["粗钢产量", "钢材销量", "吨钢毛利", "产能利用率", "铁矿石成本"],
        "financial_indicators": {
            "钢铁": ["粗钢产量", "钢材销量", "吨钢毛利", "产能利用率", "市场占有率"],
            "建材": ["水泥销量", "熟料产能", "水泥价格", "错峰生产"],
        },
        "core_view_template": [
            "某{Direction}公司最新报告期{metric}为{value}，{direction}。",
            "行业层面，{industry_trend}。",
            "公司成本优势{assessment}，{cost_highlight}。",
        ],
        "investment_rating": {
            "strong_buy": ["吨钢毛利改善", "产能置换完成", "需求超预期"],
            "hold": ["吨钢毛利平稳", "产能利用率适中", "需求平稳"],
            "sell": ["吨钢毛利大幅恶化", "产能过剩", "需求下滑"],
        },
    },
    "交通运输": {
        "name": "交通运输",
        "key_metrics": ["客货运量", "周转量", "港口吞吐", "航空客座率", "铁路货运量"],
        "financial_indicators": {
            "航运": ["货运量", "运价指数", "船舶租金", "期租率"],
            "港口": ["货物吞吐量", "集装箱吞吐量", "平均单吨装卸费"],
            "航空": ["旅客运输量", "客座率", "RPK", "ASK", "单位成本"],
            "铁路": ["货运量", "旅客运输量", "平均运价"],
        },
        "core_view_template": [
            "某交通运输公司最新报告期{metric}为{value}，{direction}。",
            "{Direction}运价为{rate}，{assessment}。",
            "公司积极拓展{new_business}，{business_highlight}。",
        ],
        "investment_rating": {
            "strong_buy": ["运量超预期", "运价大幅上涨", "新业务突破"],
            "hold": ["运量平稳", "运价稳定", "业务结构优化"],
            "sell": ["运量大幅下滑", "运价持续低迷", "安全事故"],
        },
    },
}


# ──────────────────────────────────────────────
# 数据类
# ──────────────────────────────────────────────

@dataclass
class ResearchReport:
    """投研报告结果"""
    report_type: str
    company: str
    industry: str
    rating: str
    rating_basis: str
    outline: list[str]
    core_views: list[str]
    financial_data: dict[str, Any]
    industry_data: dict[str, Any]
    competitive_data: dict[str, Any]
    investment_advice: str
    risk_factors: list[str]
    target_price: str | None = None
    upside: str | None = None


# ──────────────────────────────────────────────
# 核心引擎
# ──────────────────────────────────────────────

class SecuritiesResearchEngine:
    """
    投研报告生成引擎

    用法:
        engine = SecuritiesResearchEngine()
        report = engine.generate(
            company="某新能源公司",
            industry="新能源",
            report_type="深度报告"
        )
    """

    DIRECTIONS = ["上行", "稳健", "承压", "改善", "增长", "收缩", "疲软"]
    RATINGS = ["强烈推荐", "推荐", "中性", "谨慎", "回避"]
    RISK_LEVELS = ["低风险", "中风险", "中高风险", "高风险"]

    def __init__(self, seed: int = 42):
        random.seed(seed)

    # ── 公开API ──────────────────────────────

    def generate(
        self,
        company: str,
        industry: str | None = None,
        report_type: str = "深度报告",
    ) -> ResearchReport:
        """
        生成投研报告

        Args:
            company: 公司名称（建议传入"某XX公司"格式以满足脱敏要求）
            industry: 行业（可选，从公司名推断）
            report_type: 报告类型（深度报告/行业跟踪/宏观策略/晨会点评）

        Returns:
            ResearchReport 对象
        """
        # 推断行业
        if industry is None:
            industry = self._infer_industry(company)

        report_type = self._normalize_report_type(report_type)

        if report_type == "宏观策略":
            return self._generate_macro(company, report_type)
        else:
            return self._generate_company_report(company, industry, report_type)

    # ── 报告类型解析 ─────────────────────────

    def parse_command(self, command: str) -> dict[str, str]:
        """
        解析自然语言命令，提取公司/行业/报告类型

        Examples:
            "投研报告 某新能源公司 深度报告"
            -> {"company": "某新能源公司", "industry": "新能源", "report_type": "深度报告"}
        """
        command = command.strip()

        # 去掉"投研报告"前缀
        command = re.sub(r"^投研报告\s*", "", command)

        # 推断报告类型
        report_type = "深度报告"
        if "行业跟踪" in command:
            report_type = "行业跟踪"
            command = command.replace("行业跟踪", "").strip()
        elif "宏观策略" in command:
            report_type = "宏观策略"
            command = command.replace("宏观策略", "").strip()
        elif "晨会点评" in command or "每日" in command:
            report_type = "晨会点评"
            command = command.replace("晨会点评", "").replace("每日", "").strip()
        elif "深度报告" in command:
            report_type = "深度报告"
            command = command.replace("深度报告", "").strip()

        # 推断行业
        industry_keywords = {
            "新能源": ["新能源", "光伏", "风电", "储能", "锂电", "电动车", "电动汽车"],
            "银行": ["银行", "国有大行", "股份制", "城商行", "农商行"],
            "证券": ["证券", "券商", "投行"],
            "保险": ["保险", "寿险", "产险", "险企"],
            "房地产": ["房地产", "房企", "地产", "万科", "保利", "龙湖"],
            "医药": ["医药", "制药", "生物药", "医疗器械", "中药", "化药"],
            "科技": ["科技", "半导体", "芯片", "集成电路", "AI", "软件"],
            "消费": ["消费", "食品", "饮料", "家电", "纺织", "服装", "零售"],
            "能源": ["煤炭", "煤企", "石油", "燃气", "能源"],
            "钢铁": ["钢铁", "建材", "水泥", "钢材"],
            "交通运输": ["航空", "航运", "港口", "铁路", "物流", "运输"],
        }

        industry = None
        for ind, keywords in industry_keywords.items():
            for kw in keywords:
                if kw in command:
                    industry = ind
                    break
            if industry:
                break

        # 提取公司名称
        company = command.strip()
        if not company:
            company = "某公司"

        return {
            "company": company,
            "industry": industry or "综合",
            "report_type": report_type,
        }

    # ── 内部生成逻辑 ─────────────────────────

    def _generate_company_report(
        self,
        company: str,
        industry: str,
        report_type: str,
    ) -> ResearchReport:
        """生成公司/行业研究报告"""
        framework = INDUSTRY_FRAMEWORKS.get(
            industry, INDUSTRY_FRAMEWORKS["消费"]
        )

        rating, rating_basis = self._determine_rating(framework, industry)
        outline = self._build_outline(company, industry, report_type)
        core_views = self._build_core_views(company, industry, framework, report_type)
        financial_data = self._generate_financial_data(company, industry)
        industry_data = self._generate_industry_data(industry)
        competitive_data = self._generate_competitive_data(company, industry)
        investment_advice = self._build_investment_advice(company, rating, rating_basis)
        risk_factors = self._build_risk_factors(industry)

        return ResearchReport(
            report_type=report_type,
            company=company,
            industry=industry,
            rating=rating,
            rating_basis=rating_basis,
            outline=outline,
            core_views=core_views,
            financial_data=financial_data,
            industry_data=industry_data,
            competitive_data=competitive_data,
            investment_advice=investment_advice,
            risk_factors=risk_factors,
        )

    def _generate_macro(
        self,
        company: str,
        report_type: str,
    ) -> ResearchReport:
        """生成宏观策略报告"""
        outline = [
            "一、宏观经济运行情况",
            "  1.1 GDP与经济增长",
            "  1.2 通货膨胀与货币政策",
            "  1.3 财政政策与基建投资",
            "  1.4 进出口与外贸形势",
            "二、大类资产配置建议",
            "  2.1 权益市场展望",
            "  2.2 固定收益市场",
            "  2.3 商品与外汇",
            "  2.4 另类资产配置",
            "三、行业配置建议",
            "  3.1 景气度上行行业",
            "  3.2 景气度下行行业",
            "  3.3 政策受益行业",
            "四、风险提示",
            "  4.1 宏观风险",
            "  4.2 政策风险",
            "  4.3 海外风险",
        ]
        core_views = [
            f"当前宏观经济整体呈现{self._random_pick(['温和复苏', '结构性分化', '筑底回升', '承压运行'])}态势，",
            "货币政策保持稳健略偏宽松，财政政策积极发力。",
            f"权益市场方面，{self._random_pick(['低估值的顺周期板块', '科技成长板块', '消费复苏主线', '高股息防御板块'])}值得关注。",
            "债券市场预计维持震荡格局，利率债配置价值凸显。",
            f"行业配置建议超配{self._random_pick(['银行/非银金融', '医药/消费', '科技/新能源', '军工/能源'])}，",
            f"低配{self._random_pick(['房地产链条', '出口导向型行业', '传统周期品'])}。",
        ]
        return ResearchReport(
            report_type=report_type,
            company="宏观经济",
            industry="宏观策略",
            rating="中性",
            rating_basis="宏观基本面与资产配置框架综合判断",
            outline=outline,
            core_views=core_views,
            financial_data={"GDP增速": "5.0%左右", "CPI": "2.0%左右", "社融增量": "约35万亿元"},
            industry_data={"A股整体PE": "13-15x", "十年期国债收益率": "2.5-2.8%", "人民币汇率": "6.8-7.2"},
            competitive_data={"北向资金": "净流入约2000亿元", "公募基金发行": "同比回暖"},
            investment_advice="建议股债均衡配置，权益资产聚焦政策受益和景气拐点方向。",
            risk_factors=["全球衰退风险", "地缘政治冲突升级", "国内通缩风险", "房地产风险传导"],
        )

    # ── 报告结构 ────────────────────────────

    def _build_outline(
        self,
        company: str,
        industry: str,
        report_type: str,
    ) -> list[str]:
        if report_type == "深度报告":
            return [
                f"一、公司概况与业务结构",
                "  1.1 公司历史沿革与股权结构",
                "  1.2 主营业务构成与收入占比",
                "  1.3 战略定位与核心竞争力",
                f"二、{industry}行业分析",
                "  2.1 行业规模与增长空间",
                "  2.2 竞争格局与主要参与者",
                "  2.3 政策环境与监管趋势",
                "  2.4 产业链分析",
                "三、公司财务分析",
                "  3.1 盈利能力分析",
                "  3.2 资产质量分析",
                "  3.3 现金流量分析",
                "  3.4 关键财务比率对比",
                "四、竞争优势与成长性",
                "  4.1 护城河分析",
                "  4.2 产能布局与扩张计划",
                "  4.3 研发创新与第二曲线",
                "五、公司治理与股权激励",
                "六、盈利预测与估值",
                "  6.1 核心假设",
                "  6.2 盈利预测",
                "  6.3 估值分析（PE/PB/DCF）",
                "七、投资建议与风险提示",
                "  7.1 投资建议",
                "  7.2 风险提示",
            ]
        elif report_type == "行业跟踪":
            return [
                f"一、{industry}行业近期动态",
                "  1.1 行业政策要闻",
                "  1.2 行业价格/产量数据",
                "  1.3 重大事项跟踪",
                f"二、{company}近期经营情况",
                "  2.1 近期经营数据",
                "  2.2 重大合同/中标情况",
                "  2.3 投资者交流要点",
                "三、数据跟踪与更新",
                "四、盈利预测调整",
                "五、风险提示",
            ]
        elif report_type == "晨会点评":
            return [
                "一、今日市场概况",
                "  1.1 主要指数表现",
                "  1.2 成交情况",
                "  1.3 北向资金动向",
                "二、行业与板块热点",
                "三、{company}相关事项",
                "四、投研观点更新",
                "五、风险提示",
            ]
        else:
            return self._build_outline(company, industry, "深度报告")

    def _build_core_views(
        self,
        company: str,
        industry: str,
        framework: dict,
        report_type: str,
    ) -> list[str]:
        direction = self._random_pick(self.DIRECTIONS)
        dir_char = "增" if direction in ["上行", "增长", "改善"] else "降"
        views = []
        if report_type == "深度报告":
            views = [
                f"{company}为{industry}领域{self._random_pick(['龙头企业', '头部公司', '二线领军企业', '快速成长型企业'])}，",
                f"核心业务覆盖{self._random_pick(['研发/生产/销售一体化', '制造+服务双轮驱动', '产业链垂直整合', '产能规模优势显著'])}。",
                f"我们判断，公司中长期成长逻辑清晰，{self._random_pick(['市场份额有望持续提升', '技术迭代推动盈利中枢上移', '规模效应带动成本下行', '新产能陆续释放'])}。",
                f"短期来看，公司经营{self._random_pick(['保持稳健', '环比改善', '符合预期', '有所承压'])}，",
                f"{self._random_pick(['净利率', '毛利率', 'ROE', '营收增速'])}{direction}，{self._random_pick(['看好', '建议关注', '需观察', '持谨慎态度'])}后续变化。",
                f"综合来看，我们认为公司当前估值{self._random_pick(['具备吸引力', '处于历史中枢', '溢价合理', '偏高'])}，",
                f"首次覆盖给予" + self._random_pick(["强烈推荐", "推荐", "中性"]) + "评级。",
            ]
        elif report_type == "行业跟踪":
            views = [
                f"{industry}行业近期{self._random_pick(['景气度边际改善', '整体平稳运行', '面临一定压力', '政策暖风频吹'])}，",
                f"{self._random_pick(['供给端', '需求端', '价格端', '政策端'])}出现{self._random_pick(['积极变化', '新情况', '需关注的变化', '超预期因素'])}。",
                f"{company}近期经营{self._random_pick(['保持稳健', '环比改善', '有所波动', '符合预期'])}，",
                f"{self._random_pick(['维持', '调整'])}盈利预测，维持" + self._random_pick(["强烈推荐", "推荐", "中性"]) + "评级。",
            ]
        else:
            views = [
                f"{company}今日{self._random_pick(['发布', '公告', '召开', '披露'])}{self._random_pick(['季报', '经营数据', '重大事项', '公告'])}，",
                f"{self._random_pick(['整体符合预期', '略超预期', '低于预期', '超预期显著'])}。",
                f"{self._random_pick(['维持', "上调", "下调"])}评级至" + self._random_pick(["强烈推荐", "推荐", "中性", "谨慎"]) + "。",
            ]
        return views

    def _generate_financial_data(self, company: str, industry: str) -> dict:
        """生成模拟财务数据（脱敏）"""
        year = 2024
        return {
            f"营业收入（亿元）": {
                f"{year-2}A": round(random.uniform(50, 500), 1),
                f"{year-1}A": round(random.uniform(55, 550), 1),
                f"{year}E": round(random.uniform(60, 600), 1),
                f"{year+1}E": round(random.uniform(65, 650), 1),
            },
            f"归母净利润（亿元）": {
                f"{year-2}A": round(random.uniform(5, 80), 1),
                f"{year-1}A": round(random.uniform(6, 90), 1),
                f"{year}E": round(random.uniform(7, 100), 1),
                f"{year+1}E": round(random.uniform(8, 110), 1),
            },
            f"毛利率（%）": {
                f"{year-2}A": round(random.uniform(15, 45), 1),
                f"{year-1}A": round(random.uniform(15, 45), 1),
                f"{year}E": round(random.uniform(15, 45), 1),
            },
            f"净利率（%）": {
                f"{year-2}A": round(random.uniform(5, 25), 1),
                f"{year-1}A": round(random.uniform(5, 25), 1),
                f"{year}E": round(random.uniform(5, 25), 1),
            },
            f"ROE（%）": {
                f"{year-2}A": round(random.uniform(8, 25), 1),
                f"{year-1}A": round(random.uniform(8, 25), 1),
                f"{year}E": round(random.uniform(8, 25), 1),
            },
            f"EPS（元）": {
                f"{year-1}A": round(random.uniform(0.5, 5), 2),
                f"{year}E": round(random.uniform(0.6, 5.5), 2),
                f"{year+1}E": round(random.uniform(0.7, 6), 2),
            },
            f"PE（倍）": {
                f"{year-1}A": round(random.uniform(8, 40), 1),
                f"{year}E": round(random.uniform(8, 40), 1),
                f"{year+1}E": round(random.uniform(7, 35), 1),
            },
        }

    def _generate_industry_data(self, industry: str) -> dict:
        """生成模拟行业数据"""
        return {
            "行业规模（亿元）": round(random.uniform(1000, 50000), 0),
            "行业增速（%）": round(random.uniform(-5, 20), 1),
            "集中度CR3（%）": round(random.uniform(10, 60), 1),
            "产能利用率（%）": round(random.uniform(60, 95), 1),
            "进口依存度（%）": round(random.uniform(0, 50), 1),
            "政策环境": self._random_pick(["支持", "中性", "规范", "收紧"]),
            "技术迭代周期": self._random_pick(["导入期", "成长期", "成熟期", "衰退期"]),
            "下游需求": self._random_pick(["旺盛", "平稳", "分化", "疲软"]),
        }

    def _generate_competitive_data(self, company: str, industry: str) -> dict:
        """生成模拟竞争格局数据"""
        return {
            f"{company}市占率（%）": round(random.uniform(3, 30), 1),
            "行业第1名市占率（%）": round(random.uniform(10, 40), 1),
            "行业第2名市占率（%）": round(random.uniform(5, 25), 1),
            "行业第3名市占率（%）": round(random.uniform(3, 20), 1),
            "公司产能排名": f"行业第{random.randint(1, 10)}位",
            "公司研发投入排名": f"行业第{random.randint(1, 10)}位",
            "核心竞争要素": self._random_pick([
                "技术壁垒/品牌/规模效应/渠道/成本",
                "技术+品牌双壁垒",
                "全产业链布局",
                "研发创新驱动",
            ]),
        }

    def _build_investment_advice(
        self,
        company: str,
        rating: str,
        rating_basis: str,
    ) -> str:
        return (
            f"投资建议：{rating}。 "
            f"理由：{rating_basis}。 "
            f"建议关注公司核心业务边际变化、产能投放节奏及行业竞争格局演变，"
            f"适时择机布局。风险偏好型投资者可重点关注。"
        )

    def _build_risk_factors(self, industry: str) -> list[str]:
        base_risks = [
            f"{self._random_pick(['下游需求', '行业政策', '原材料价格', '汇率波动', '行业竞争'])}超预期{self._random_pick(['上行', '下行', '变化'])}风险",
            f"{self._random_pick(['技术迭代', '产品升级', '产能投放'])}不及预期风险",
            f"{self._random_pick(['融资环境', '信用风险', '资金链', '应收账款'])}恶化风险",
            f"{self._random_pick(['国际局势', '地缘政治', '贸易摩擦', '海外监管'])}导致出口受阻风险",
        ]
        industry_specific = {
            "银行": ["资产质量恶化超预期", "净息差大幅收窄", "资本充足率压力"],
            "证券": ["市场交易量大幅萎缩", "自营业务亏损", "监管政策收紧"],
            "保险": ["利率持续下行影响投资收益", "重疾率假设偏差", "退保率大幅上升"],
            "房地产": ["销售持续下滑", "融资渠道受阻", "项目去化困难导致计提减值"],
            "医药": ["带量采购降价超预期", "创新药审评审批不及预期", "医保控费压力"],
            "科技": ["半导体设备禁运升级", "技术路线变化", "国产替代进度低于预期"],
            "消费": ["消费复苏不及预期", "原材料价格波动", "渠道库存积压"],
            "新能源": ["政策补贴退坡", "行业竞争加剧", "技术路线变化导致资产减值"],
            "能源": ["煤炭价格大幅下跌", "安全生产事故", "进口煤冲击"],
        }
        return base_risks + industry_specific.get(industry, [])

    # ── 辅助方法 ────────────────────────────

    def _determine_rating(
        self,
        framework: dict,
        industry: str,
    ) -> tuple[str, str]:
        rand = random.random()
        if rand >= 0.6:
            rating = "强烈推荐"
        elif rand >= 0.35:
            rating = "推荐"
        elif rand >= 0.15:
            rating = "中性"
        elif rand >= 0.05:
            rating = "谨慎"
        else:
            rating = "回避"

        basis_map = {
            "强烈推荐": f"{industry}行业景气度上行，公司竞争优势突出，业绩增长确定性高，估值具备提升空间",
            "推荐": f"{industry}行业基本面稳健，公司主业稳健成长，估值处于合理区间",
            "中性": f"{industry}行业整体平稳，公司业务结构优化中，短期估值弹性有限",
            "谨慎": f"{industry}行业面临一定压力，公司短期经营承压，估值存在调整风险",
            "回避": f"{industry}行业景气度下行，公司基本面出现明显恶化，估值偏高",
        }
        return rating, basis_map[rating]

    def _normalize_report_type(self, report_type: str) -> str:
        type_map = {
            "深度报告": "深度报告",
            "deep": "深度报告",
            "行业跟踪": "行业跟踪",
            "industry": "行业跟踪",
            "行业": "行业跟踪",
            "宏观策略": "宏观策略",
            "macro": "宏观策略",
            "晨会点评": "晨会点评",
            "daily": "晨会点评",
            "每日": "晨会点评",
        }
        for key, val in type_map.items():
            if key in report_type:
                return val
        return "深度报告"

    def _infer_industry(self, company: str) -> str:
        for ind, keywords in {
            "新能源": ["新能源", "光伏", "风电", "储能", "锂电", "电动", "汽车"],
            "银行": ["银行"],
            "证券": ["证券", "券商"],
            "保险": ["保险"],
            "房地产": ["房地产", "地产"],
            "医药": ["医药", "制药", "医疗"],
            "科技": ["科技", "半导体", "芯片", "电子"],
            "消费": ["消费", "食品", "饮料", "家电", "零售"],
            "能源": ["煤炭", "石油", "能源"],
            "钢铁": ["钢铁", "建材", "水泥"],
            "交通运输": ["航空", "航运", "港口", "铁路", "物流"],
        }.items():
            if any(kw in company for kw in keywords):
                return ind
        return "综合"

    def _random_pick(self, options: list[str]) -> str:
        return random.choice(options)

    # ── 格式化输出 ───────────────────────────

    def format_markdown(self, report: ResearchReport) -> str:
        """输出 Markdown 格式"""
        lines = [
            f"# {report.company} — {report.report_type}",
            "",
            f"**行业：** {report.industry}  |  **评级：** {report.rating}  |  **评级依据：** {report.rating_basis}",
            "",
            "---",
            "",
            "## 一、研究报告大纲",
        ]
        for item in report.outline:
            lines.append(f"  {item}")

        lines += ["", "## 二、核心观点", ""]
        for view in report.core_views:
            lines.append(f"- {view}")

        lines += ["", "## 三、财务数据（脱敏模拟）", ""]
        for metric, data in report.financial_data.items():
            lines.append(f"**{metric}**")
            for period, val in data.items():
                lines.append(f"  - {period}: {val}")
            lines.append("")

        lines += ["", "## 四、行业数据（脱敏模拟）", ""]
        for k, v in report.industry_data.items():
            lines.append(f"- {k}: {v}")

        lines += ["", "## 五、竞争格局（脱敏模拟）", ""]
        for k, v in report.competitive_data.items():
            lines.append(f"- {k}: {v}")

        lines += [
            "",
            "## 六、投资建议",
            f"{report.investment_advice}",
            "",
            "## 七、风险提示",
        ]
        for i, risk in enumerate(report.risk_factors, 1):
            lines.append(f"{i}. {risk}")

        lines += [
            "",
            "---",
            f"> 本报告数据为脱敏模拟数据，仅供内部研究参考，不构成投资建议。",
        ]
        return "\n".join(lines)

    def format_json(self, report: ResearchReport) -> dict:
        """输出 JSON 格式（dict）"""
        import dataclasses

        return dataclasses.asdict(report)
