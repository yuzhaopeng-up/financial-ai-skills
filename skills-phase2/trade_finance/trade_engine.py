"""
Trade Finance Engine - 贸易融资核心引擎

根据企业类型、贸易类型、融资金额、账期等参数，
推荐最适合的贸易融资方案并提供多维度对比分析。
"""

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TradeFinancingProduct:
    """贸易融资产品数据模型"""
    name_cn: str
    name_en: str
    applicable_scenarios: list[str]
    financing_ratio: str  # 占应收账款/订单金额的比例
    interest_rate_ref: str  # 年化利率参考
    processing_cycle: str  # 办理周期
    required_materials: list[str]
    risk_points: list[str]
    suitable_company_types: list[str]  # 出口企业/进口企业/外贸企业
    min_amount_usd: float  # 最小金额（美元）
    max_amount_usd: float  # 最大金额（美元）
    min_terms_days: int  # 最短账期（天）
    max_terms_days: int  # 最长账期（天）
    tags: list[str] = field(default_factory=list)


class TradeFinanceEngine:
    """贸易融资推荐引擎"""

    # 所有支持的产品定义
    PRODUCTS = {
        "LC": TradeFinancingProduct(
            name_cn="信用证",
            name_en="Letter of Credit (L/C)",
            applicable_scenarios=[
                "进出口双方互不信任，缺乏信任基础",
                "买卖双方位于不同国家，信息不对称严重",
                "交易金额较大，需要银行信用背书",
                "买方坚持使用银行信用作为付款保障",
            ],
            financing_ratio="80%~90%（视信用证开证行资信）",
            interest_rate_ref="4%~7%（美元），6%~10%（人民币）",
            processing_cycle="3~7个工作日（开证）；1~3个工作日（押汇）",
            required_materials=[
                "贸易合同（CONTRACT）",
                "商业发票（INVOICE）",
                "装箱单（PACKING LIST）",
                "提单（B/L）或海运单（SWB）",
                "原产地证书（CO/Certificate of Origin）",
                "信用证正本（L/C Original）",
                "出口企业资质证明文件",
            ],
            risk_points=[
                "开证行信用风险（优先选择资信良好的银行）",
                "单据不符风险（单证不符、单单不符将导致拒付）",
                "商品价格波动风险（大宗商品需做好套保）",
                "政治/汇率风险（关注开证行所在国风险）",
                "软条款风险（警惕信用证中隐藏的不合理条款）",
            ],
            suitable_company_types=["出口企业", "进口企业", "外贸企业"],
            min_amount_usd=10_000,
            max_amount_usd=50_000_000,
            min_terms_days=30,
            max_terms_days=180,
            tags=["银行信用", "有追索权", "标准流程"],
        ),
        "FACTORING": TradeFinancingProduct(
            name_cn="国际保理",
            name_en="International Factoring",
            applicable_scenarios=[
                "出口企业采用赊销（O/A）方式，想提前变现应收账款",
                "买方资信良好，但账期较长（90天以上）",
                "出口企业想降低坏账风险，转移信用风险",
                "出口企业缺乏担保物，但有稳定应收账款",
            ],
            financing_ratio="70%~85%（无追索权保理通常较低）",
            interest_rate_ref="5%~9%（含保理费，年化）",
            processing_cycle="3~5个工作日（双保理模式）",
            required_materials=[
                "贸易合同（明确应收账款转让条款）",
                "商业发票（INVOICE）",
                "装箱单/运输单据",
                "出口企业近2年财务报表",
                "买方（债务人）基本信息",
                "出口信用保险保单（如有）",
                "企业营业执照及进出口资质",
            ],
            risk_points=[
                "买方信用风险（保理商核准额度内可转移）",
                "应收账款质量风险（虚假贸易/关联交易所致）",
                "纠纷风险（贸易争议导致反转让）",
                "汇率风险（美元计价需关注汇兑损益）",
                "出口企业回购风险（无追索权保理也有条件）",
            ],
            suitable_company_types=["出口企业"],
            min_amount_usd=5_000,
            max_amount_usd=10_000_000,
            min_terms_days=30,
            max_terms_days=120,
            tags=["无追索权", "应收账款", "赊销"],
        ),
        "FORFAITING": TradeFinancingProduct(
            name_cn="福费廷",
            name_en="Forfaiting",
            applicable_scenarios=[
                "中长期大额应收账款（账期通常1~5年）",
                "出口企业想一次性转嫁所有风险（信用、政治、汇率）",
                "买方资信一般，但想让出口商规避所有风险",
                "出口商想优化财务报表（应收账款项下表）",
            ],
            financing_ratio="75%~90%（扣除贴现息后的净款）",
            interest_rate_ref="6%~12%（按无追索买断，远高于一般贷款）",
            processing_cycle="5~10个工作日",
            required_materials=[
                "贸易合同（明确债权可转让）",
                "商业发票（已承兑/已承诺付款的汇票或发票）",
                "银行保函/备用信用证（担保文件）",
                "提单/运输单据",
                "原产地证书",
                "福费廷协议（与包买银行签署）",
                "出口企业全套资质文件",
            ],
            risk_points=[
                "无追索权，但需担保银行资信良好",
                "包买银行对担保行资信要求极高",
                "担保行所在国政治/经济风险",
                "票据/债权真实性（需严格尽调）",
                "贴现率固定，无法随市场利率下调",
            ],
            suitable_company_types=["出口企业"],
            min_amount_usd=100_000,
            max_amount_usd=100_000_000,
            min_terms_days=180,
            max_terms_days=1825,
            tags=["无追索权", "中长期", "买断型"],
        ),
        "EXPORT_BILL": TradeFinancingProduct(
            name_cn="出口押汇",
            name_en="Export Bill Forward / Export Bill Discounting",
            applicable_scenarios=[
                "出口企业已发货，单据不齐全或不符，无法立即结汇",
                "出口企业急需周转资金，等不及买方付款",
                "采用托收方式（DP/DA），想提前用单据融资",
                "信用证项下单据存在轻微不符点，但开证行已承付",
            ],
            financing_ratio="70%~85%（信用证项下可达90%）",
            interest_rate_ref="4%~8%（美元），5%~10%（人民币）",
            processing_cycle="1~3个工作日",
            required_materials=[
                "商业发票（INVOICE）",
                "全套运输单据（提单/空运单/海运单）",
                "信用证正本（如为L/C项下押汇）",
                "出口报关单（出口押汇必须）",
                "装箱单",
                "出口合同（如有）",
            ],
            risk_points=[
                "单据真实性风险（虚假贸易背景）",
                "货物风险（货物在途，物权凭证需妥善管理）",
                "开证行/付款行信用风险",
                "单证不符风险（押汇银行可追索）",
                "汇率风险（押汇通常为外币）",
            ],
            suitable_company_types=["出口企业"],
            min_amount_usd=5_000,
            max_amount_usd=5_000_000,
            min_terms_days=1,
            max_terms_days=90,
            tags=["有追索权", "单据融资", "短期"],
        ),
        "IMPORT_BILL": TradeFinancingProduct(
            name_cn="进口押汇",
            name_en="Import Bill Forward",
            applicable_scenarios=[
                "进口企业申请开证/托收，想延期付款赎单",
                "进口企业账期较短但资金周转需要时间",
                "想利用银行授信替代自有资金支付货款",
                "大宗商品进口，利用押汇做资金杠杆",
            ],
            financing_ratio="80%~95%（高比例，可达100%开证）",
            interest_rate_ref="3.5%~6%（美元），4.5%~8%（人民币）",
            processing_cycle="1~2个工作日（已有授信前提下）",
            required_materials=[
                "进口合同",
                "商业发票",
                "信用证项下全套单据（如为L/C）",
                "进口许可证（如需要）",
                "报关单（进口后补）",
                "企业近2年财务报表",
            ],
            risk_points=[
                "进口企业信用风险（还款来源）",
                "商品价格下跌风险（大宗商品需做套保）",
                "货物灭失/货损风险",
                "汇率风险（美元计价商品）",
                "担保/抵押物风险（通常需要担保）",
            ],
            suitable_company_types=["进口企业"],
            min_amount_usd=10_000,
            max_amount_usd=20_000_000,
            min_terms_days=1,
            max_terms_days=180,
            tags=["有追索权", "延期付款", "赎单"],
        ),
        "PACKING_CREDIT": TradeFinancingProduct(
            name_cn="打包贷款",
            name_en="Packing Credit / Pre-shipment Finance",
            applicable_scenarios=[
                "出口企业接到订单，需要采购原材料/生产备货",
                "企业流动资金不足，账期尚未到期",
                "想扩大生产规模但缺乏担保物",
                "订单金额较大，需要分阶段备货资金",
            ],
            financing_ratio="30%~70%（占订单金额，通常不超过70%）",
            interest_rate_ref="5%~9%（年化，通常上浮比例较高）",
            processing_cycle="3~5个工作日（有授信）",
            required_materials=[
                "出口订单/销售确认书（Sales Confirmation）",
                "信用证正本（如为L/C项下打包贷款）",
                "出口企业营业执照及进出口资质",
                "最近1年财务报表",
                "采购合同（如需证明资金用途）",
                "担保/抵押文件（如有）",
            ],
            risk_points=[
                "订单履约风险（无法交货将触发还款）",
                "买方毁单风险（订单取消导致资金链断裂）",
                "汇率风险（收款币种与贷款币种不一致）",
                "担保物价值波动风险",
                "出口退税款延迟风险",
            ],
            suitable_company_types=["出口企业"],
            min_amount_usd=10_000,
            max_amount_usd=2_000_000,
            min_terms_days=1,
            max_terms_days=120,
            tags=["有追索权", "备货融资", "订单驱动"],
        ),
        "ORDER_FINANCING": TradeFinancingProduct(
            name_cn="订单融资",
            name_en="Order Financing / Sales Contract Financing",
            applicable_scenarios=[
                "出口企业拿到销售确认书/合同，想提前采购生产",
                "买方为大型优质企业，订单稳定",
                "企业缺乏固定资产抵押，但有稳定订单流",
                "跨境电商等新业态，有平台订单即可融资",
            ],
            financing_ratio="40%~80%（占订单金额，视订单资质）",
            interest_rate_ref="6%~12%（年化，无抵押利率较高）",
            processing_cycle="5~10个工作日（视风控尽调深度）",
            required_materials=[
                "销售合同/订单（Sales Contract / Purchase Order）",
                "买方资信证明（大型企业订单加分）",
                "出口企业近2年财务报表",
                "出口企业历史订单记录（如有）",
                "上游采购合同（证明资金用于采购原料）",
                "担保/抵押/保证文件",
            ],
            risk_points=[
                "订单真实性风险（虚假订单骗贷）",
                "订单执行风险（无法按质按量交货）",
                "买方违约风险（拒收/拒付）",
                "资金被挪用风险（需监控资金用途）",
                "关联交易风险（关联企业虚假贸易）",
            ],
            suitable_company_types=["出口企业"],
            min_amount_usd=20_000,
            max_amount_usd=5_000_000,
            min_terms_days=1,
            max_terms_days=180,
            tags=["有追索权", "订单驱动", "轻资产"],
        ),
        "INSURANCE_POLICY": TradeFinancingProduct(
            name_cn="保单融资",
            name_en="Insurance Policy Financing",
            applicable_scenarios=[
                "出口企业已投保中信保/其他出口信用保险",
                "持有银行非转让性应收账款，想以保单质押融资",
                "企业有一定订单规模，但缺乏其他担保",
                "想借助保险增信降低融资成本",
            ],
            financing_ratio="50%~80%（占保单赔付额度，非应收账款全额）",
            interest_rate_ref="5%~9%（年化，含保险增信成本）",
            processing_cycle="5~10个工作日",
            required_materials=[
                "出口信用保险保单（中文出口信用保险/中信保）",
                "贸易合同及发票",
                "买方信息及额度申请表",
                "出口企业营业执照及财务资料",
                "银行要求的其他担保文件",
                "保单赔款权益转让协议（银行需受让保险权益）",
            ],
            risk_points=[
                "保险赔付条件限制（需满足保险条款约定）",
                "银行对保单条款的合规性要求严格",
                "出口企业需持续缴纳保费维持保单有效",
                "汇率/政治风险需在保险覆盖范围内",
                "保单质押登记合规性（需在中国人行征信中心登记）",
            ],
            suitable_company_types=["出口企业"],
            min_amount_usd=50_000,
            max_amount_usd=5_000_000,
            min_terms_days=30,
            max_terms_days=365,
            tags=["保险增信", "有追索权", "保单质押"],
        ),
    }

    def __init__(self):
        self._score_weights = {
            "amount": 0.25,
            "terms": 0.25,
            "company_type": 0.30,
            "scenario": 0.20,
        }

    def recommend(
        self,
        company_type: str,
        trade_type: str = "一般贸易",
        amount_usd: float = 100_000,
        payment_terms_days: int = 90,
        scenarios: list[str] | None = None,
        top_k: int = 3,
    ) -> dict[str, Any]:
        """
        根据输入参数推荐贸易融资方案

        Args:
            company_type: 企业类型（出口企业/进口企业/外贸企业）
            trade_type: 贸易类型（一般贸易/加工贸易/跨境电商等）
            amount_usd: 融资金额（美元）
            payment_terms_days: 账期（天）
            scenarios: 附加场景描述列表（可选）
            top_k: 返回前k个推荐方案

        Returns:
            包含推荐方案、对比表、决策建议的字典
        """
        company_type_clean = self._normalize_company_type(company_type)

        # 计算每个产品的匹配分数
        scored_products = []
        for product_key, product in self.PRODUCTS.items():
            score = self._calculate_match_score(
                product=product,
                company_type=company_type_clean,
                amount_usd=amount_usd,
                payment_terms_days=payment_terms_days,
                scenarios=scenarios or [],
            )
            scored_products.append((product_key, product, score))

        # 按分数降序排列
        scored_products.sort(key=lambda x: x[2], reverse=True)

        # 取前top_k
        top_products = scored_products[:top_k]

        # 构建推荐结果
        recommendations = []
        for rank, (product_key, product, score) in enumerate(top_products, 1):
            recommendations.append({
                "rank": rank,
                "product_key": product_key,
                "name_cn": product.name_cn,
                "name_en": product.name_en,
                "match_score": round(score, 2),
                "match_reason": self._generate_match_reason(product, company_type_clean, amount_usd, payment_terms_days),
            })

        # 生成对比表
        comparison = self._generate_comparison_table([p[1] for p in top_products])

        # 决策建议
        decision = self._generate_decision_advice(
            top_products[0] if top_products else None,
            company_type_clean,
            amount_usd,
            payment_terms_days,
        )

        return {
            "input": {
                "company_type": company_type,
                "trade_type": trade_type,
                "amount_usd": amount_usd,
                "payment_terms_days": payment_terms_days,
            },
            "recommendations": recommendations,
            "comparison_table": comparison,
            "decision_advice": decision,
            "all_products_summary": self._generate_all_products_summary(),
        }

    def _normalize_company_type(self, company_type: str) -> str:
        """规范化企业类型"""
        ct = company_type.strip()
        if "出口" in ct:
            return "出口企业"
        elif "进口" in ct:
            return "进口企业"
        elif "外贸" in ct or "贸易" in ct:
            return "外贸企业"
        return ct

    def _calculate_match_score(
        self,
        product: TradeFinancingProduct,
        company_type: str,
        amount_usd: float,
        payment_terms_days: int,
        scenarios: list[str],
    ) -> float:
        """计算产品匹配分数"""
        score = 0.0
        max_score = sum(self._score_weights.values())

        # 企业类型匹配
        if company_type in product.suitable_company_types:
            type_score = self._score_weights["company_type"]
            score += type_score

        # 金额区间匹配
        if product.min_amount_usd <= amount_usd <= product.max_amount_usd:
            score += self._score_weights["amount"] * 1.0
        elif amount_usd < product.min_amount_usd:
            score += self._score_weights["amount"] * 0.3
        else:  # 超过最大值
            score += self._score_weights["amount"] * 0.5

        # 账期区间匹配
        if product.min_terms_days <= payment_terms_days <= product.max_terms_days:
            score += self._score_weights["terms"] * 1.0
        elif payment_terms_days < product.min_terms_days:
            score += self._score_weights["terms"] * 0.3
        else:
            score += self._score_weights["terms"] * 0.5

        # 场景关键词匹配加分
        scenario_text = " ".join(scenarios).lower()
        scenario_keywords = {
            "赊销": ["赊销", "O/A", "open account"],
            "订单": ["订单", "order", "purchase"],
            "信用证": ["信用证", "L/C", "letter of credit"],
            "大额": ["大额", "大单", "large"],
            "短期": ["短期", "急需", "紧急"],
            "保单": ["保单", "保险", "insurance"],
        }
        for product_tag in product.tags:
            for keyword_name, keywords in scenario_keywords.items():
                if any(kw in scenario_text for kw in keywords):
                    if keyword_name.lower() in [t.lower() for t in product.tags]:
                        score += 0.05

        # 归一化
        return (score / max_score) * 100

    def _generate_match_reason(
        self,
        product: TradeFinancingProduct,
        company_type: str,
        amount_usd: float,
        payment_terms_days: int,
    ) -> str:
        """生成匹配原因说明"""
        reasons = []

        if company_type in product.suitable_company_types:
            reasons.append(f"{company_type}适用")

        if product.min_amount_usd <= amount_usd <= product.max_amount_usd:
            reasons.append(f"金额{amount_usd:,.0f}美元在适配区间内")
        elif amount_usd < product.min_amount_usd:
            reasons.append(f"金额偏小，建议考虑{product.name_cn}（最低{min_amount_usd:,.0f}美元起）")

        if product.min_terms_days <= payment_terms_days <= product.max_terms_days:
            reasons.append(f"账期{payment_terms_days}天在适配范围内")

        return "；".join(reasons) if reasons else "综合评估为较优匹配"

    def _generate_comparison_table(self, products: list[TradeFinancingProduct]) -> list[dict[str, str]]:
        """生成方案对比表"""
        rows = []
        for p in products:
            rows.append({
                "产品": p.name_cn,
                "融资比例": p.financing_ratio,
                "利率参考": p.interest_rate_ref,
                "办理周期": p.processing_cycle,
                "主要特点": "、".join(p.tags),
                "适用账期": f"{p.min_terms_days}~{p.max_terms_days}天",
            })
        return rows

    def _generate_decision_advice(
        self,
        top_product: tuple[str, TradeFinancingProduct, float] | None,
        company_type: str,
        amount_usd: float,
        payment_terms_days: int,
    ) -> str:
        """生成决策建议"""
        if not top_product:
            return "未找到合适的方案，建议咨询银行客户经理进行个性化评估。"

        product_key, product, score = top_product

        advices = {
            "LC": f"推荐信用证（L/C）方案。{company_type}交易金额达{amount_usd:,.0f}美元，账期{payment_terms_days}天，信用证可通过银行信用解决买卖双方信任问题。建议优先选择工、农、中、建等大型银行开证以提升卖方接受度。",
            "FACTORING": f"推荐国际保理方案。赊销账期{payment_terms_days}天，保理可实现无追索权应收账款变现，改善企业现金流。建议同时投保出口信用保险以提升保理商核准额度。",
            "FORFAITING": f"推荐福费廷方案。交易金额较大（{amount_usd:,.0f}美元），账期较长（{payment_terms_days}天），福费廷可一次性买断应收账款，实现无追索权转嫁所有风险，优化财务报表。",
            "EXPORT_BILL": f"推荐出口押汇方案。单据已备齐但资金周转需要时间，出口押汇1~3个工作日即可放款，效率最高。建议确保单证相符以避免银行追索。",
            "IMPORT_BILL": f"推荐进口押汇方案。{company_type}可利用银行授信延期付款赎单，融资比例高达80%~95%，有效缓解短期资金压力。",
            "PACKING_CREDIT": f"推荐打包贷款方案。{company_type}已有订单，打包贷款可快速补充备货资金，融资比例30%~70%，3~5个工作日放款。建议同步联系下游确认订单执行细节。",
            "ORDER_FINANCING": f"推荐订单融资方案。{company_type}持有优质订单，订单融资可基于订单合同提前获取采购资金，融资比例40%~80%。需提供真实上下游合同佐证资金用途。",
            "INSURANCE_POLICY": f"推荐保单融资方案。已投保出口信用保险，通过保单质押可获取50%~80%的融资额度，保险增信可有效降低融资成本。建议提前与银行沟通保单质押登记流程。",
        }

        base_advice = advices.get(product_key, f"推荐{product.name_cn}方案。")
        return base_advice

    def _generate_all_products_summary(self) -> list[dict[str, str]]:
        """生成全产品一览表"""
        summary = []
        for p in self.PRODUCTS.values():
            summary.append({
                "产品": p.name_cn,
                "英文": p.name_en,
                "适用企业": "、".join(p.suitable_company_types),
                "融资比例": p.financing_ratio,
                "账期范围": f"{p.min_terms_days}~{p.max_terms_days}天",
                "利率参考": p.interest_rate_ref,
            })
        return summary

    def compare_products(self, product_keys: list[str]) -> dict[str, Any]:
        """
        对比指定产品的详细信息

        Args:
            product_keys: 产品key列表，如 ["LC", "FACTORING", "FORFAITING"]

        Returns:
            包含详细对比数据的字典
        """
        selected = []
        for key in product_keys:
            if key.upper() in self.PRODUCTS:
                selected.append(self.PRODUCTS[key.upper()])

        if not selected:
            return {"error": "未找到指定产品，请检查产品key（如：LC, FACTORING, FORFAITING）"}

        return {
            "products": [
                {
                    "name_cn": p.name_cn,
                    "name_en": p.name_en,
                    "applicable_scenarios": p.applicable_scenarios,
                    "financing_ratio": p.financing_ratio,
                    "interest_rate_ref": p.interest_rate_ref,
                    "processing_cycle": p.processing_cycle,
                    "required_materials": p.required_materials,
                    "risk_points": p.risk_points,
                    "suitable_company_types": p.suitable_company_types,
                    "amount_range": f"{p.min_amount_usd:,.0f}~{p.max_amount_usd:,.0f} USD",
                    "terms_range": f"{p.min_terms_days}~{p.max_terms_days} 天",
                    "tags": p.tags,
                }
                for p in selected
            ],
            "quick_compare": self._generate_comparison_table(selected),
        }


# ---------- CLI 解析辅助函数 ----------
import re

def parse_cli_input(text: str) -> dict[str, Any]:
    """解析CLI输入文本，返回结构化参数"""
    result = {
        "company_type": None,
        "amount_usd": None,
        "payment_terms_days": None,
        "scenarios": [],
    }

    # 提取企业类型
    for ct in ["出口企业", "进口企业", "外贸企业"]:
        if ct in text:
            result["company_type"] = ct
            break

    # 提取金额
    amount_patterns = [
        r"(\d+(?:\.\d+)?)\s*(?:万|千万|亿)\s*(?:美元|USD)",
        r"(\d+(?:\.\d+)?)\s*(?:美元|USD)",
        r"金额\s*[:：]?\s*(\d+(?:\.\d+)?)\s*(?:万|千万|亿)?",
    ]
    for pattern in amount_patterns:
        m = re.search(pattern, text)
        if m:
            val = float(m.group(1))
            if "亿" in m.group(0):
                val *= 100_000_000
            elif "千万" in m.group(0):
                val *= 10_000_000
            elif "万" in m.group(0):
                val *= 10_000
            result["amount_usd"] = val
            break

    # 提取账期天数
    term_patterns = [
        r"(\d+)\s*(?:天|日)",
        r"账期\s*[:：]?\s*(\d+)",
    ]
    for pattern in term_patterns:
        m = re.search(pattern, text)
        if m:
            result["payment_terms_days"] = int(m.group(1))
            break

    # 提取场景关键词
    scenario_keywords = ["赊销", "O/A", "急需", "大额", "小额", "短期", "长期", "订单"]
    for kw in scenario_keywords:
        if kw in text:
            result["scenarios"].append(kw)

    return result


# ---------- 入口 ----------
if __name__ == "__main__":
    import json, sys

    engine = TradeFinanceEngine()

    if len(sys.argv) > 1 and sys.argv[1] == "compare":
        # compare mode: python trade_engine.py compare LC FACTORING FORFAITING
        keys = sys.argv[2:] if len(sys.argv) > 2 else ["LC", "FACTORING"]
        result = engine.compare_products(keys)
    else:
        # recommend mode
        params = parse_cli_input(" ".join(sys.argv[1:]) if len(sys.argv) > 1 else "")
        result = engine.recommend(
            company_type=params["company_type"] or "出口企业",
            amount_usd=params["amount_usd"] or 100_000,
            payment_terms_days=params["payment_terms_days"] or 90,
            scenarios=params["scenarios"],
        )

    print(json.dumps(result, ensure_ascii=False, indent=2))
