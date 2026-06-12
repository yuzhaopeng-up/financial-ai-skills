"""
续保提醒引擎 (Renewal Alert Engine)

分析客户保单续保情况，返回续保建议、优先级、替代方案、挽留策略和话术。
"""

from typing import Optional, Dict, Any


class RenewalAlertEngine:
    """
    续保提醒核心引擎

    判断规则：
    - 已缴年限 ≥ 保障期限 × 50%  → 建议保留
    - 现金价值 > 已缴保费 × 80%  → 建议检视（退保需谨慎）

    挽留优先级（从高到低）：
    1. 年金险
    2. 终身寿险
    3. 定期寿险
    4. 医疗险
    5. 意外险
    """

    PRIORITY_MAP = {
        "年金险": "紧急",
        "终身寿险": "重要",
        "定期寿险": "重要",
        "医疗险": "一般",
        "意外险": "一般",
    }

    # 险种标准化映射
    PRODUCT_TYPE_MAP = {
        "终身寿险": "终身寿险",
        "终身寿": "终身寿险",
        "寿险": "终身寿险",
        "年金险": "年金险",
        "年金": "年金险",
        "养老": "年金险",
        "教育金": "年金险",
        "定期寿险": "定期寿险",
        "定寿": "定期寿险",
        "医疗险": "医疗险",
        "医疗": "医疗险",
        "住院险": "医疗险",
        "意外险": "意外险",
        "意外": "意外险",
    }

    ALTERNATIVE_PRODUCTS = {
        "终身寿险": [
            "增额终身寿险（保额递增，现金价值增长更快）",
            "定期寿险+年金险组合（低保费高保障+养老储备）",
            "终身寿险减额方式（缓解缴费压力）"
        ],
        "年金险": [
            "快返型年金险（更早领取）",
            "万能型年金险（灵活附加）",
            "养老年金险（专为养老设计，领取更稳定）"
        ],
        "定期寿险": [
            "定期寿险（消费型，保费更低）",
            "终身寿险（资产传承需求）",
            "定期寿险+储蓄型保险组合"
        ],
        "医疗险": [
            "百万医疗险（保额更高）",
            "中端医疗险（含特需/国际部）",
            "高端医疗险（含海外医疗）"
        ],
        "意外险": [
            "综合意外险（含意外医疗）",
            "特定职业意外险（保费更低）",
            "驾乘意外险（驾乘场景保障）"
        ],
    }

    def __init__(self):
        pass

    def _normalize_product_type(self, product_type: str) -> str:
        """标准化险种名称"""
        for key, value in self.PRODUCT_TYPE_MAP.items():
            if key in product_type:
                return value
        return product_type

    def _get_priority(self, product_type: str) -> str:
        """获取挽留优先级"""
        return self.PRIORITY_MAP.get(product_type, "一般")

    def _get_alternatives(self, product_type: str) -> str:
        """获取替代方案"""
        alternatives = self.ALTERNATIVE_PRODUCTS.get(product_type, [])
        if not alternatives:
            return "无特定替代方案，建议联系代理人详细咨询。"
        return "；".join(alternatives)

    def _build_retention_strategy(
        self,
        product_type: str,
        paid_ratio: float,
        cash_value_ratio: float,
        annual_premium: float
    ) -> str:
        """构建客户挽留策略"""
        strategies = []

        if paid_ratio >= 0.5:
            strategies.append(f"已缴满{paid_ratio*100:.0f}%保障期限，累计价值较高，应强调保单已建立的保障和现金价值。")

        if cash_value_ratio >= 0.8:
            strategies.append(f"现金价值已超{cash_value_ratio*100:.0f}%已缴保费，退保损失较大，应重点说明持续缴费的优势。")

        if annual_premium <= 50000:
            strategies.append("保费压力较小，可提供分期缴费方案缓解客户资金压力。")
        elif annual_premium >= 200000:
            strategies.append("高保费客户，可提供保单贷款或减额缴清方案，增加灵活性。")

        # 按险种追加策略
        if product_type == "年金险":
            strategies.append("年金险客户注重收益，应对比保单预定利率与当前市场利率，突出锁定收益优势。")
        elif product_type == "终身寿险":
            strategies.append("终身寿险客户注重传承，应强调身故保障和资产传承功能。")
        elif product_type == "医疗险":
            strategies.append("医疗险客户注重健康保障，应强调产品升级或核保宽松优势。")

        return " ".join(strategies) if strategies else "建议与客户深入沟通，了解其真实需求后再制定个性化方案。"

    def _build_renewal_script(
        self,
        customer_name: str,
        product_type: str,
        recommendation: str,
        paid_ratio: float,
        annual_premium: float,
        renewal_premium: float
    ) -> str:
        """构建续保话术"""
        scripts = {
            "建议续保": f"""【续保话术 - {customer_name} 客户】

张总/女士您好，我是您的专属保险顾问。您的{product_type}保单续期将至，特此通知您。

【保单价值回顾】
您的保单已缴费{paid_ratio*100:.0f}%，建立了相当可观的保障权益。根据我们目前的评估，您的保单整体保障价值良好，继续持有对您最为有利。

【续期缴费说明】
本期续期保费为{renewal_premium:.0f}元，为确保您的保障权益不受影响，建议您在保费到期日前完成缴费。

【温馨提示】
如您有任何经济上的顾虑，我们可以提供以下支持：
1. 保费分期缴纳
2. 减额缴清方案
3. 保单贷款（现金价值可贷款）

如有任何疑问，欢迎随时联系我，我会全程协助您。""",

            "建议升级": f"""【续保话术 - {customer_name} 客户】

张总/女士您好，我是您的专属保险顾问。您的{product_type}保单续期将至，和您沟通一下保障升级方案。

【现状分析】
您的保单已缴费{paid_ratio*100:.0f}%，保障权益较为完善。结合您目前的家庭情况，我们认为适当升级保障可以让您获得更全面的保护。

【升级方案建议】
我们为您准备了以下升级选项：
1. 保障额度提升
2. 新增附加险（医疗/意外）
3. 转换为更全面的产品计划

【续期安排】
当前续期保费{renewal_premium:.0f}元，建议按原计划缴纳，同时考虑升级方案。

如需了解详情，我可以为您做一份详细的保障升级分析报告。""",

            "建议退保": f"""【续保话术 - {customer_name} 客户】

张总/女士您好，我是您的专属保险顾问。您的{product_type}保单续期将至，和您做一次深度沟通。

【当前情况说明】
经过全面评估，我们认为您的保单可能存在一些优化空间。在做出决定前，希望您了解以下信息：

【继续持有的情况】
- 已建立{paid_ratio*100:.0f}%保障权益
- 现金价值积累情况

【替代方案参考】
如您确实需要调整保障计划，我们为您准备了以下替代方案：
1. 减额缴清（减少保费，维持部分保障）
2. 转换为其他产品
3. 延期缴费（如有此项权益）

【重要提示】
退保可能带来一定损失，建议您充分考虑后再做决定。如您方便，我们可以约个时间详细分析。"""
        }

        return scripts.get(recommendation, scripts["建议续保"])

    def analyze(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析保单续保情况

        Args:
            params: 包含客户保单信息
                - customer_name: 客户姓名
                - product_type: 险种
                - annual_premium: 年缴保费
                - paid_years: 已缴年限
                - coverage_years: 保障期限（0=终身）
                - renewal_premium: 续期保费
                - cash_value: 现金价值（可选）

        Returns:
            续保分析结果
        """
        customer_name = params.get("customer_name", "客户")
        product_type = self._normalize_product_type(params.get("product_type", ""))
        annual_premium = float(params.get("annual_premium", 0))
        paid_years = int(params.get("paid_years", 0))
        coverage_years = int(params.get("coverage_years", 0))
        renewal_premium = float(params.get("renewal_premium", annual_premium))
        cash_value = params.get("cash_value")

        # 计算已缴保费总额
        total_paid = annual_premium * paid_years

        # 计算已缴比例
        if coverage_years > 0:
            paid_ratio = paid_years / coverage_years
        else:
            # 终身产品，已缴超过10年视为高比例
            paid_ratio = min(paid_years / 20.0, 1.0) if paid_years >= 10 else paid_years / 20.0

        # 计算现金价值比例
        if cash_value is not None and total_paid > 0:
            cash_value_ratio = cash_value / total_paid
        else:
            # 估算现金价值比例（根据经验数据）
            if paid_ratio >= 0.5:
                cash_value_ratio = 0.85
            elif paid_ratio >= 0.3:
                cash_value_ratio = 0.70
            elif paid_ratio >= 0.1:
                cash_value_ratio = 0.50
            else:
                cash_value_ratio = 0.30

        # 判断风险等级
        if paid_ratio >= 0.5 and cash_value_ratio >= 0.8:
            risk_level = "低风险（建议保留）"
        elif paid_ratio >= 0.3:
            risk_level = "中风险（建议检视）"
        else:
            risk_level = "高风险（需谨慎评估）"

        # 生成建议（按任务规则）
        # 已缴年限 ≥ 保障期限 × 50% → 建议保留
        # 现金价值 > 已缴保费 × 80% → 建议检视
        # 其他 → 建议退保
        if coverage_years > 0 and paid_years >= coverage_years * 0.5:
            recommendation = "建议续保"
        elif cash_value_ratio >= 0.8:
            recommendation = "建议升级"
        else:
            recommendation = "建议退保"

        priority = self._get_priority(product_type)
        alternative = self._get_alternatives(product_type) if recommendation == "建议退保" else None
        retention_strategy = self._build_retention_strategy(
            product_type, paid_ratio, cash_value_ratio, annual_premium
        )
        renewal_script = self._build_renewal_script(
            customer_name, product_type, recommendation,
            paid_ratio, annual_premium, renewal_premium
        )

        return {
            "customer_name": customer_name,
            "product_type": product_type,
            "recommendation": recommendation,
            "priority": priority,
            "alternative": alternative,
            "retention_strategy": retention_strategy,
            "renewal_script": renewal_script,
            "analysis": {
                "paid_ratio": round(paid_ratio, 4),
                "cash_value_ratio": round(cash_value_ratio, 4),
                "risk_level": risk_level,
                "total_paid": total_paid,
                "annual_premium": annual_premium,
                "paid_years": paid_years,
                "coverage_years": coverage_years,
                "renewal_premium": renewal_premium,
            }
        }

    def parse_cli_input(self, cli_text: str) -> Dict[str, Any]:
        """
        解析CLI输入文本

        支持格式：
        "续保提醒 客户张总 终身寿险 年缴2万 已缴10年 续期将至"
        "续保提醒 客户李女士 年金险 年缴5万 已缴5年 保障期限20年"

        Args:
            cli_text: CLI输入文本

        Returns:
            解析后的参数字典
        """
        import re

        text = cli_text.strip()

        # 提取客户姓名
        customer_match = re.search(r'客户([^\s]{1,5})', text)
        customer_name = customer_match.group(1) if customer_match else "客户"

        # 提取险种
        product_keywords = ["终身寿险", "终身寿", "寿险", "年金险", "年金", "养老", "教育金",
                          "定期寿险", "定寿", "医疗险", "医疗", "住院险", "意外险", "意外"]
        product_type = "终身寿险"
        for kw in product_keywords:
            if kw in text:
                product_type = self._normalize_product_type(kw)
                break

        # 提取年缴保费
        premium_match = re.search(r'年缴?(\d+(?:\.\d+)?)\s*[万wW]?', text)
        if not premium_match:
            premium_match = re.search(r'保费\s*(\d+(?:\.\d+)?)', text)
        annual_premium = 0.0
        if premium_match:
            val = float(premium_match.group(1))
            annual_premium = val * 10000  # 万转为元
        else:
            # 尝试直接匹配数字
            direct_match = re.search(r'(\d+(?:\.\d+)?)', text)
            if direct_match:
                annual_premium = float(direct_match.group(1)) * 10000

        # 提取已缴年限
        paid_match = re.search(r'已缴(\d+)年', text)
        paid_years = int(paid_match.group(1)) if paid_match else 0

        # 提取保障期限
        coverage_match = re.search(r'保障期限(\d+)年', text)
        coverage_years = int(coverage_match.group(1)) if coverage_match else 0

        # 提取续期保费
        renewal_match = re.search(r'续期[保费]?\s*(\d+(?:\.\d+)?)\s*[万wW]?', text)
        renewal_premium = annual_premium
        if renewal_match:
            renewal_val = float(renewal_match.group(1))
            renewal_premium = renewal_val * 10000

        # 估算保障期限（终身寿险默认30年）
        if coverage_years == 0 and product_type == "终身寿险":
            coverage_years = 30

        return {
            "customer_name": customer_name,
            "product_type": product_type,
            "annual_premium": annual_premium,
            "paid_years": paid_years,
            "coverage_years": coverage_years,
            "renewal_premium": renewal_premium,
            "cash_value": None
        }
