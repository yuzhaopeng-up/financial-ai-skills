"""
AML Rating Engine — 反洗钱客户评级核心引擎
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RiskFactor:
    """单项风险因素"""
    dimension: str          # 维度名称
    score: int              # 加分
    factors: list[str]      # 触发因素列表


@dataclass
class AMLRatingResult:
    """AML评级结果"""
    customer_name: str
    risk_level: str          # 极低/低/中/高/极高
    risk_score: int           # 0-100
    risk_factors: dict        # 各维度风险拆解
    recommendations: list[str] # 管控措施建议

    def to_dict(self) -> dict:
        return {
            "customer_name": self.customer_name,
            "risk_level": self.risk_level,
            "risk_score": self.risk_score,
            "risk_factors": self.risk_factors,
            "recommendations": self.recommendations
        }


class AMLRatingEngine:
    """
    反洗钱客户评级引擎

    风险维度计分规则：
    - 地域风险：涉制裁/洗钱高发区 +20
    - 行业风险：高风险行业 +15
    - 业务风险：跨境+10，大额+10，现金+10
    - 客户特征：空壳公司/代持 +20

    等级划分：
    - 0-20  极低
    - 21-40 低
    - 41-60 中
    - 61-80 高
    - 81-100 极高
    """

    # 高风险地区（涉制裁/洗钱高发区）
    HIGH_RISK_REGIONS = {
        "伊朗", "朝鲜", "叙利亚", "缅甸", "委内瑞拉", "古巴",
        "阿富汗", "也门", "索马里", "厄立特里亚", "苏丹",
        "俄罗斯", "乌克兰", "北朝鲜", "朝鲜民主主义人民共和国",
        "iran", "north korea", "syria", "myanmar", "venezuela",
        "cuba", "afghanistan", "yemen", "somalia", "russia",
        "高风险地区", "制裁地区"
    }

    # 高风险行业
    HIGH_RISK_INDUSTRIES = {
        "虚拟货币", "加密货币", "数字货币", "博彩", "赌场",
        "色情", "武器", "军火", "毒品", "走私", "现金业务",
        "兑换", "换汇", "第三方支付", "汇款", "地下钱庄",
        " cryptocurrency", "gambling", "casino", "arms", "drugs"
    }

    # 高风险业务特征
    HIGH_RISK_TRANSACTIONS = {
        "跨境": 10,
        "大额": 10,
        "现金": 10,
        "分散集中": 5,    # 分散转入集中转出
        "快进快出": 5,
        "频繁": 5,
        "异常": 5,
    }

    # 高风险客户特征
    HIGH_RISK_CUSTOMER_FEATURES = {
        "空壳公司": 20,
        "代持": 20,
        "代持结构": 20,
        "不透明股权": 15,
        "政治敏感人士": 15,
        "PEP": 15,
        "高风险行业": 15,
    }

    # 缓解因素（降低风险）
    MITIGATING_FACTORS = {
        "受益人信息完整": -10,
        "实际控制人明确": -10,
        "证件有效": -5,
        "长期客户": -5,
        "合规记录良好": -10,
        "强KYC": -8,
        "本地企业": -5,
    }

    # 等级颜色映射
    LEVEL_COLORS = {
        "极低": "🟢",
        "低": "🔵",
        "中": "🟡",
        "高": "🟠",
        "极高": "🔴",
    }

    def __init__(self):
        pass

    def _detect_region_risk(self, region: str) -> RiskFactor:
        """分析地域风险"""
        if not region:
            return RiskFactor("地域风险", 0, [])

        region_upper = region.upper()
        factors = []

        for high_risk in self.HIGH_RISK_REGIONS:
            if high_risk.upper() in region_upper or region_upper in high_risk.upper():
                factors.append(f"位于高风险地区：{region}")
                return RiskFactor("地域风险", 20, factors)

        # 检查制裁相关关键词
        sanction_keywords = ["制裁", "禁运", "FATF高风险", "黑名单"]
        for kw in sanction_keywords:
            if kw in region:
                factors.append(f"地区存在制裁/黑名单状态：{region}")
                return RiskFactor("地域风险", 20, factors)

        return RiskFactor("地域风险", 0, [])

    def _detect_industry_risk(self, industry: str) -> RiskFactor:
        """分析行业风险"""
        if not industry:
            return RiskFactor("行业风险", 0, ["行业信息缺失"])

        industry_upper = industry.upper()
        factors = []

        for high_risk in self.HIGH_RISK_INDUSTRIES:
            if high_risk.upper() in industry_upper:
                factors.append(f"高风险行业：{industry}")
                return RiskFactor("行业风险", 15, factors)

        # 中等风险行业
        medium_risk = ["贸易", "进出口", "海外", "国际"]
        for mr in medium_risk:
            if mr in industry:
                factors.append(f"一般贸易行业（中等风险）：{industry}")
                return RiskFactor("行业风险", 10, factors)

        return RiskFactor("行业风险", 0, [f"行业正常：{industry}"])

    def _detect_transaction_risk(self, transaction_features: list) -> RiskFactor:
        """分析业务风险"""
        if not transaction_features:
            return RiskFactor("业务风险", 0, ["无特殊交易特征"])

        total_score = 0
        factors = []

        for feature in transaction_features:
            feature_clean = feature.strip()
            if feature_clean in self.HIGH_RISK_TRANSACTIONS:
                score = self.HIGH_RISK_TRANSACTIONS[feature_clean]
                total_score += score
                factors.append(f"{feature_clean} (+{score})")

        return RiskFactor("业务风险", min(total_score, 30), factors if factors else ["无高风险交易特征"])

    def _detect_customer_risk(self,
                              id_validity_days: Optional[int] = None,
                              has_beneficial_owner: bool = False,
                              customer_features: Optional[list] = None) -> RiskFactor:
        """分析客户特征风险"""
        total_score = 0
        factors = []

        features = customer_features or []

        for feature in features:
            feature_clean = feature.strip()
            if feature_clean in self.HIGH_RISK_CUSTOMER_FEATURES:
                score = self.HIGH_RISK_CUSTOMER_FEATURES[feature_clean]
                total_score += score
                factors.append(f"{feature_clean} (+{score})")

        # 证件过期风险
        if id_validity_days is not None:
            if id_validity_days <= 0:
                total_score += 10
                factors.append("证件已过期 (+10)")
            elif id_validity_days < 90:
                total_score += 5
                factors.append("证件即将过期 (+5)")

        # 受益人信息
        if has_beneficial_owner:
            # 有受益人是正面因素
            pass
        else:
            total_score += 10
            factors.append("缺少受益人信息 (+10)")

        return RiskFactor("客户特征", min(total_score, 30), factors if factors else ["客户特征正常"])

    def _apply_mitigating_factors(self, factors: list[RiskFactor], customer_features: Optional[list] = None) -> list[RiskFactor]:
        """应用缓解因素"""
        features = customer_features or []

        for i, factor in enumerate(factors):
            for feature in features:
                feature_clean = feature.strip()
                if feature_clean in self.MITIGATING_FACTORS:
                    reduction = self.MITIGATING_FACTORS[feature_clean]
                    factor.score = max(0, factor.score + reduction)
                    if reduction < 0:
                        factor.factors.append(f"{feature_clean} ({reduction})")

        return factors

    def _calculate_total_score(self, factors: list[RiskFactor]) -> int:
        """计算总分（各维度加权相加，上限100）"""
        total = sum(f.score for f in factors)
        return min(total, 100)

    def _determine_level(self, score: int) -> str:
        """根据评分确定风险等级"""
        if score <= 20:
            return "极低"
        elif score <= 40:
            return "低"
        elif score <= 60:
            return "中"
        elif score <= 80:
            return "高"
        else:
            return "极高"

    def _generate_recommendations(self, result: AMLRatingResult, factors: list[RiskFactor]) -> list[str]:
        """生成管控措施建议"""
        recommendations = []
        level = result.risk_level

        # 基础建议（按等级）
        if level in ["极低", "低"]:
            recommendations.append("建议进行年度常规回顾")
        elif level == "中":
            recommendations.append("建议加强持续监控，增加交易审核频率")
            recommendations.append("建议每半年进行一次客户信息更新")
        elif level == "高":
            recommendations.append("建议启动强化尽调（Enhanced Due Diligence, EDD）")
            recommendations.append("建议提高交易报告阈值，收紧交易限额")
            recommendations.append("建议由合规部门进行专项审查")
        else:  # 极高
            recommendations.append("建议立即暂停业务关系，启动紧急评估")
            recommendations.append("建议向管理层和合规委员会报告")
            recommendations.append("考虑向相关监管部门进行可疑交易报告（STR/SAR）")

        # 维度针对性建议
        for factor in factors:
            if factor.dimension == "地域风险" and factor.score > 10:
                recommendations.append(f"地域风险较高：建议重新评估与{factor.factors[0] if factor.factors else '该地区'}的业务关系必要性")
            elif factor.dimension == "行业风险" and factor.score > 10:
                recommendations.append("行业风险较高：建议审查行业准入合规性，增加行业专项监控")
            elif factor.dimension == "业务风险" and factor.score > 15:
                recommendations.append("业务风险较高：建议对相关交易类型设置强化审批流程")
            elif factor.dimension == "客户特征" and factor.score > 10:
                recommendations.append("客户特征风险较高：建议获取完整的股权/受益人结构信息")

        return list(dict.fromkeys(recommendations))  # 去重保持顺序

    def rate(self,
             customer_name: str,
             industry: str = "",
             region: str = "",
             transaction_features: Optional[list] = None,
             id_validity_days: Optional[int] = None,
             has_beneficial_owner: bool = False,
             customer_features: Optional[list] = None,
             **kwargs) -> AMLRatingResult:
        """
        执行AML客户评级

        Args:
            customer_name: 客户名称
            industry: 行业类型
            region: 地区/国家
            transaction_features: 交易特征列表 ["跨境", "大额", "现金"]
            id_validity_days: 证件有效期（天）
            has_beneficial_owner: 是否有明确受益人
            customer_features: 额外客户特征列表

        Returns:
            AMLRatingResult: 包含风险等级、评分、因素拆解和建议
        """
        transaction_features = transaction_features or []
        customer_features = customer_features or []

        # 分维度计算
        region_factor = self._detect_region_risk(region)
        industry_factor = self._detect_industry_risk(industry)
        transaction_factor = self._detect_transaction_risk(transaction_features)
        customer_factor = self._detect_customer_risk(
            id_validity_days=id_validity_days,
            has_beneficial_owner=has_beneficial_owner,
            customer_features=customer_features
        )

        # 合并所有因素
        all_factors = [region_factor, industry_factor, transaction_factor, customer_factor]

        # 应用缓解因素
        all_factors = self._apply_mitigating_factors(all_factors, customer_features)

        # 计算总分
        total_score = self._calculate_total_score(all_factors)

        # 确定等级
        risk_level = self._determine_level(total_score)

        # 构建风险因素字典
        risk_factors = {
            "地域风险": {"score": region_factor.score, "factors": region_factor.factors},
            "行业风险": {"score": industry_factor.score, "factors": industry_factor.factors},
            "业务风险": {"score": transaction_factor.score, "factors": transaction_factor.factors},
            "客户特征": {"score": customer_factor.score, "factors": customer_factor.factors},
        }

        # 构建结果
        result = AMLRatingResult(
            customer_name=customer_name,
            risk_level=risk_level,
            risk_score=total_score,
            risk_factors=risk_factors,
            recommendations=[]
        )

        # 生成建议
        result.recommendations = self._generate_recommendations(result, all_factors)

        return result

    def rate_from_text(self, text: str) -> AMLRatingResult:
        """
        从自然语言文本解析客户信息并评级

        支持格式示例：
        "AML评级 某客户 贸易行业 受益人信息完整"
        "客户名称:XXX 行业:贸易 地区:香港 交易特征:跨境,大额"
        """
        import re

        # 默认值
        customer_name = "未知客户"
        industry = ""
        region = ""
        transaction_features = []
        has_beneficial_owner = False
        customer_features = []

        # 尝试提取客户名称（第一个词组）
        text_without_cmd = re.sub(r"^AML评级\s*", "", text.strip())
        parts = text_without_cmd.split()
        if parts:
            customer_name = parts[0]

        # 提取行业
        industry_match = re.search(r"行业[：:]([^,\s]+)", text)
        if industry_match:
            industry = industry_match.group(1)

        # 提取地区
        region_match = re.search(r"地区[：:]([^,\s]+)", text)
        if region_match:
            region = region_match.group(1)

        # 提取交易特征
        txn_match = re.search(r"交易特征[：:]([^,\s]+)", text)
        if txn_match:
            txn_str = txn_match.group(1)
            transaction_features = [t.strip() for t in txn_str.replace(",", " ").split()]

        # 提取受益人信息
        if "受益人信息完整" in text or "受益人明确" in text:
            has_beneficial_owner = True
            customer_features.append("受益人信息完整")

        # 推断行业关键词
        industry_keywords = ["贸易", "金融", "科技", "制造", "地产", "建筑", "能源", "运输", "餐饮", "零售"]
        for kw in industry_keywords:
            if kw in text and not industry:
                industry = kw + "行业"
                break

        # 推断交易特征
        feature_keywords = {
            "跨境": ["跨境", "国际", "海外"],
            "大额": ["大额", "巨额", "高金额"],
            "现金": ["现金", "现钞", "纸币"],
        }
        for feature, keywords in feature_keywords.items():
            for kw in keywords:
                if kw in text and feature not in transaction_features:
                    transaction_features.append(feature)

        return self.rate(
            customer_name=customer_name,
            industry=industry,
            region=region,
            transaction_features=transaction_features,
            has_beneficial_owner=has_beneficial_owner,
            customer_features=customer_features
        )

    def pretty_print(self, result: AMLRatingResult) -> str:
        """格式化输出评级结果"""
        color = self.LEVEL_COLORS.get(result.risk_level, "⚪")
        lines = [
            f"{'='*50}",
            f"  AML 客户风险评级报告",
            f"{'='*50}",
            f"  客户名称: {result.customer_name}",
            f"  风险等级: {color} {result.risk_level}  ({result.risk_score}/100)",
            f"",
            f"  ── 风险因素拆解 ──",
        ]

        for dim, data in result.risk_factors.items():
            score = data["score"]
            factors = data["factors"]
            bar = "█" * (score // 5) + "░" * (20 - score // 5)
            lines.append(f"  {dim}: [{bar}] +{score}分")
            for f in factors:
                lines.append(f"    · {f}")

        lines.append(f"")
        lines.append(f"  ── 管控措施建议 ──")
        for i, rec in enumerate(result.recommendations, 1):
            lines.append(f"  {i}. {rec}")

        lines.append(f"{'='*50}")
        return "\n".join(lines)


# 便捷函数
def rate_customer(**kwargs) -> dict:
    """便捷函数：直接返回字典"""
    engine = AMLRatingEngine()
    result = engine.rate(**kwargs)
    return result.to_dict()
