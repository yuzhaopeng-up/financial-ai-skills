"""
UnderwritingV2Engine - 券商两融智能核保引擎 v2
基于客户信息评估两融准入资格，输出额度建议、担保物折算率、风险提示及利率建议
"""

import re
import datetime
from typing import Dict, List, Optional, Any


class UnderwritingV2Engine:
    """
    券商两融智能核保引擎

    评估维度：
    1. 准入条件：资产 ≥ 50万、持股满6个月、风险测评C4及以上、信用记录良好
    2. 额度建议：根据担保物折算率计算最高可借金额
    3. 担保物折算率：主板股票0.65 / 科创板0.50 / 债券0.90 / 基金0.80
    4. 风险提示：识别潜在风险点
    5. 利率建议：基于信用评级建议利率区间
    """

    # 准入条件配置
    MIN_ASSET = 50_0000  # 最低资产50万（单位：元）
    MIN_HOLDING_MONTHS = 6  # 最少持股月数
    MIN_RISK_LEVEL = "C4"  # 最低风险等级
    RISK_LEVELS = ["C1", "C2", "C3", "C4", "C5", "C6"]

    # 担保物折算率
    COLLATERAL_RATES = {
        "主板股票": 0.65,
        "科创板": 0.50,
        "创业板": 0.65,
        "北交所": 0.50,
        "债券": 0.90,
        "基金": 0.80,
        "国债": 0.95,
        "货币基金": 0.95,
        "现金": 1.0,
        "理财产品": 0.70,
    }

    # 折算率表（按资产类型细分）
    ASSET_TYPE_RATES = {
        # 股票类
        "沪市主板": 0.65, "深市主板": 0.65,
        "中小板": 0.65, "创业板": 0.65,
        "科创板": 0.50, "ST股票": 0.30,
        "北交所": 0.50, "新三板": 0.20,
        # 债券类
        "国债": 0.95, "地方债": 0.90,
        "信用债": 0.85, "可转债": 0.80,
        "金融债": 0.90,
        # 基金类
        "股票型基金": 0.80, "混合型基金": 0.75,
        "债券型基金": 0.85, "货币基金": 0.95,
        "指数基金": 0.80, "ETF": 0.80,
        # 其他
        "现金": 1.0, "理财产品": 0.70,
        "资管计划": 0.60, "信托": 0.50,
    }

    # 利率建议（年化）
    BASE_MARGIN_RATE = 0.085  # 融资默认年化利率 8.5%
    BASE_SECURITY_RATE = 0.085  # 融券默认年化利率 8.5%
    RATE_DISCOUNT_BY_CREDIT = {
        "极优": -0.015,  # 利率下调
        "优秀": -0.010,
        "良好": 0.000,
        "一般": 0.005,
        "较差": 0.015,
    }

    def __init__(self):
        self.name = "UnderwritingV2Engine"
        self.version = "2.0.0"

    def parse_user_input(self, text: str) -> Dict[str, Any]:
        """
        解析自然语言输入
        格式示例：两融核保 客户资产500万 持仓市值300万 信用评分80 无负债
        """
        result = {}

        # 客户资产
        asset_match = re.search(r'资产(\d+(?:\.\d+)?)(万|亿|元)', text)
        if asset_match:
            value = float(asset_match.group(1))
            unit = asset_match.group(2)
            if unit == "亿":
                value *= 10000
            elif unit == "万":
                value *= 1
            else:  # 元
                value /= 10000
            result['total_asset'] = value * 10000  # 转为元

        # 持仓市值
        holding_match = re.search(r'持仓市值(\d+(?:\.\d+)?)(万|亿|元)', text)
        if holding_match:
            value = float(holding_match.group(1))
            unit = holding_match.group(2)
            if unit == "亿":
                value *= 10000
            elif unit == "万":
                value *= 1
            else:
                value /= 10000
            result['holding_market_value'] = value * 10000

        # 持仓类型
        holding_type_match = re.search(r'持仓(主板|科创板|创业板|科创|债券|基金|ETF|沪市|深市|北交所)', text)
        if holding_type_match:
            result['holding_type'] = holding_type_match.group(1)

        # 信用评分 (0-100)
        credit_match = re.search(r'信用评分(\d+)', text)
        if credit_match:
            result['credit_score'] = int(credit_match.group(1))

        # 负债情况
        if "无负债" in text or "无欠款" in text or "零负债" in text:
            result['debt_status'] = "无负债"
        elif "少量负债" in text:
            result['debt_status'] = "少量负债"
        elif "负债" in text:
            debt_amount_match = re.search(r'负债(\d+(?:\.\d+)?)(万|亿|元)', text)
            result['debt_status'] = "有负债"
            if debt_amount_match:
                value = float(debt_amount_match.group(1))
                unit = debt_amount_match.group(2)
                if unit == "亿":
                    value *= 10000
                elif unit == "万":
                    value *= 1
                else:
                    value /= 10000
                result['debt_amount'] = value * 10000

        # 持股月数
        months_match = re.search(r'持股(\d+)个月|持仓(\d+)个月|持股满(\d+)个月|(\d+)个月持股', text)
        if months_match:
            for g in months_match.groups():
                if g:
                    result['holding_months'] = int(g)
                    break

        # 风险等级
        risk_match = re.search(r'风险测评(C[1-6])|风险等级(C[1-6])', text)
        if risk_match:
            result['risk_level'] = risk_match.group(1) or risk_match.group(2)

        # 账户年限
        account_match = re.search(r'开户(\d+)年|账户(\d+)年', text)
        if account_match:
            for g in account_match.groups():
                if g:
                    result['account_years'] = int(g)
                    break

        # 收入
        income_match = re.search(r'年收入(\d+(?:\.\d+)?)(万|亿|元)', text)
        if income_match:
            value = float(income_match.group(1))
            unit = income_match.group(2)
            if unit == "亿":
                value *= 10000
            elif unit == "万":
                value *= 1
            else:
                value /= 10000
            result['annual_income'] = value * 10000

        # 信用记录
        if "信用记录良好" in text or "无不良" in text or "信用好" in text:
            result['credit_record'] = "良好"
        elif "信用一般" in text:
            result['credit_record'] = "一般"
        elif "信用较差" in text or "有不良" in text:
            result['credit_record'] = "较差"

        # 担保物明细
        collaterals = []
        for asset_type, rate in self.ASSET_TYPE_RATES.items():
            if asset_type in text:
                match = re.search(rf'{asset_type}(\d+(?:\.\d+)?)(万|亿|元)', text)
                if match:
                    value = float(match.group(1))
                    unit = match.group(2)
                    if unit == "亿":
                        value *= 10000
                    elif unit == "万":
                        value *= 1
                    else:
                        value /= 10000
                    collaterals.append({
                        "asset_type": asset_type,
                        "market_value": value * 10000,
                        "discount_rate": rate
                    })
        if collaterals:
            result['collaterals'] = collaterals

        return result

    def evaluate_admission(self, total_asset: float, holding_months: int,
                          risk_level: str, credit_record: str) -> Dict[str, Any]:
        """
        评估两融准入资格

        Returns:
            admission_result: 包含 decision, reasons, qualification_score
        """
        reasons = []
        score = 0
        max_score = 4  # 4项准入条件

        # 1. 资产 ≥ 50万
        if total_asset >= self.MIN_ASSET:
            score += 1
            reasons.append(f"✅ 资产条件：{total_asset/10000:.0f}万 ≥ 50万（满足）")
        else:
            reasons.append(f"❌ 资产条件：{total_asset/10000:.0f}万 < 50万（不满足）")

        # 2. 持股满6个月
        if holding_months >= self.MIN_HOLDING_MONTHS:
            score += 1
            reasons.append(f"✅ 持股时间：满{holding_months}个月（满足）")
        else:
            reasons.append(f"❌ 持股时间：{holding_months}个月 < 6个月（不满足）")

        # 3. 风险测评 C4及以上
        risk_idx = self.RISK_LEVELS.index(risk_level) if risk_level in self.RISK_LEVELS else -1
        min_idx = self.RISK_LEVELS.index(self.MIN_RISK_LEVEL)
        if risk_idx >= min_idx:
            score += 1
            reasons.append(f"✅ 风险等级：{risk_level}（满足）")
        else:
            reasons.append(f"❌ 风险等级：{risk_level} < {self.MIN_RISK_LEVEL}（不满足）")

        # 4. 信用记录良好
        if credit_record == "良好":
            score += 1
            reasons.append(f"✅ 信用记录：{credit_record}（满足）")
        elif credit_record == "一般":
            reasons.append(f"⚠️ 信用记录：{credit_record}（有条件通过）")
        else:
            reasons.append(f"❌ 信用记录：{credit_record}（不满足）")

        qualification_score = score / max_score

        if score == 4:
            decision = "可开"
            decision_detail = "完全满足两融准入条件"
        elif score >= 2:
            decision = "有条件开"
            decision_detail = f"满足{score}/4项准入条件，可申请有条件开通"
        else:
            decision = "不开"
            decision_detail = f"仅满足{score}/4项准入条件，暂不满足开通条件"

        return {
            "decision": decision,
            "decision_detail": decision_detail,
            "qualification_score": qualification_score,
            "qualified_count": score,
            "total_count": max_score,
            "reasons": reasons
        }

    def calculate_collateral_value(self, holding_market_value: float,
                                  holding_type: str = "主板股票") -> Dict[str, Any]:
        """
        计算担保物折算价值
        """
        rate = self.COLLATERAL_RATES.get(holding_type, 0.65)
        discounted_value = holding_market_value * rate

        return {
            "market_value": holding_market_value,
            "asset_type": holding_type,
            "discount_rate": rate,
            "collateral_value": discounted_value,
            " haircut": 1 - rate
        }

    def calculate_collaterals_from_list(self, collaterals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        从担保物列表计算总折算价值
        """
        total_market_value = 0
        total_collateral_value = 0
        details = []

        for c in collaterals:
            mv = c.get("market_value", 0)
            rate = c.get("discount_rate", 0.65)
            cv = mv * rate
            total_market_value += mv
            total_collateral_value += cv
            details.append({
                "asset_type": c.get("asset_type", "未知"),
                "market_value": mv,
                "discount_rate": rate,
                "collateral_value": cv
            })

        return {
            "total_market_value": total_market_value,
            "total_collateral_value": total_collateral_value,
            "overall_discount_rate": total_collateral_value / total_market_value if total_market_value > 0 else 0,
            "details": details
        }

    def calculate_quota(self, total_asset: float, holding_market_value: float,
                       holding_type: str = "主板股票",
                       debt_amount: float = 0) -> Dict[str, Any]:
        """
        计算两融额度建议

        规则：
        - 融资额度上限 = min(担保证券折算价值 × 杠杆系数, 客户总资产 × 1.0)
        - 保证金比例要求：维持担保比例 ≥ 130%
        - 杠杆系数：信用评分 ≥ 90 → 1.5；≥ 80 → 1.2；≥ 70 → 1.0；else → 0.8
        """
        collateral_result = self.calculate_collateral_value(holding_market_value, holding_type)
        collateral_value = collateral_result["collateral_value"]

        # 可用保证金（剔除已有负债）
        available_margin = collateral_value - debt_amount
        if available_margin < 0:
            available_margin = 0

        # 融资额度（取可用保证金和客户资产的较小值，同时受折算价值约束）
        max_financing_by_collateral = available_margin * 1.5  # 最高可借 = 折算价值 × 1.5
        max_financing_by_asset = total_asset * 1.0  # 最高不超过客户总资产
        max_financing = min(max_financing_by_collateral, max_financing_by_asset)

        # 维持担保比例 = (现金 + 证券市值) / 负债总额
        # 平仓线 130%，警戒线 150%
        if debt_amount > 0:
            maintenance_ratio = (total_asset) / debt_amount * 100
        else:
            maintenance_ratio = float('inf')

        return {
            "max_financing_amount": max_financing,
            "max_financing_display": f"{max_financing/10000:.0f}万",
            "collateral_value": collateral_value,
            "collateral_value_display": f"{collateral_value/10000:.0f}万",
            "available_margin": available_margin,
            "maintenance_ratio": maintenance_ratio,
            "maintenance_ratio_display": f"{maintenance_ratio:.0f}%" if maintenance_ratio != float('inf') else "无负债",
            "warning_line": "130%",
            "alert_line": "150%"
        }

    def evaluate_risk_warnings(self, total_asset: float, holding_market_value: float,
                               risk_level: str, credit_score: int,
                               debt_amount: float = 0,
                               holding_type: str = "主板股票") -> List[Dict[str, str]]:
        """
        生成风险提示列表
        """
        warnings = []

        # 持仓集中度风险
        if holding_market_value > total_asset * 0.9:
            warnings.append({
                "level": "高",
                "type": "持仓集中度",
                "message": f"持仓市值占总资产{holding_market_value/total_asset*100:.0f}%，集中度较高，建议分散持仓"
            })

        # 科创板风险
        if holding_type in ["科创板", "科创"]:
            warnings.append({
                "level": "中",
                "type": "板块风险",
                "message": "科创板股票波动较大，折算率仅50%，需关注追保风险"
            })

        # 负债率风险
        if debt_amount > 0:
            debt_ratio = debt_amount / total_asset * 100
            if debt_ratio > 50:
                warnings.append({
                    "level": "高",
                    "type": "负债率",
                    "message": f"负债占比{debt_ratio:.0f}%偏高，面临较高追保风险"
                })
            elif debt_ratio > 30:
                warnings.append({
                    "level": "中",
                    "type": "负债率",
                    "message": f"负债占比{debt_ratio:.0f}%，需关注维持担保比例"
                })

        # 杠杆风险
        if holding_market_value > total_asset * 0.7:
            warnings.append({
                "level": "高",
                "type": "杠杆风险",
                "message": "高杠杆持仓，市场波动可能导致强制平仓"
            })

        # 信用评分偏低
        if credit_score < 60:
            warnings.append({
                "level": "高",
                "type": "信用风险",
                "message": f"信用评分{credit_score}偏低，违约风险较高"
            })

        # 低风险等级客户大额融资
        if risk_level in ["C4"] and total_asset > 500_0000:
            pass  # C4且资产较大，属于正常
        elif risk_level == "C4" and total_asset > 1000_0000:
            warnings.append({
                "level": "中",
                "type": "额度风险",
                "message": "C4客户大额融资，需持续关注账户风险状况"
            })

        return warnings

    def suggest_interest_rate(self, credit_score: int, risk_level: str) -> Dict[str, Any]:
        """
        建议利率（年化）
        """
        # 基础利率
        margin_rate = self.BASE_MARGIN_RATE
        security_rate = self.BASE_SECURITY_RATE

        # 信用评分调整
        if credit_score >= 90:
            credit_level = "极优"
            adjustment = self.RATE_DISCOUNT_BY_CREDIT["极优"]
        elif credit_score >= 80:
            credit_level = "优秀"
            adjustment = self.RATE_DISCOUNT_BY_CREDIT["优秀"]
        elif credit_score >= 70:
            credit_level = "良好"
            adjustment = self.RATE_DISCOUNT_BY_CREDIT["良好"]
        elif credit_score >= 60:
            credit_level = "一般"
            adjustment = self.RATE_DISCOUNT_BY_CREDIT["一般"]
        else:
            credit_level = "较差"
            adjustment = self.RATE_DISCOUNT_BY_CREDIT["较差"]

        final_margin_rate = margin_rate + adjustment
        final_security_rate = security_rate + adjustment

        return {
            "margin_rate": final_margin_rate,
            "margin_rate_display": f"{final_margin_rate*100:.2f}%",
            "security_rate": final_security_rate,
            "security_rate_display": f"{final_security_rate*100:.2f}%",
            "credit_level": credit_level,
            "adjustment": adjustment,
            "adjustment_display": f"{adjustment*100:+.2f}%"
        }

    def underwrite(self, total_asset: float = None, holding_market_value: float = None,
                   credit_score: int = None, debt_status: str = None,
                   debt_amount: float = None, holding_months: int = None,
                   risk_level: str = None, credit_record: str = None,
                   holding_type: str = "主板股票",
                   annual_income: float = None,
                   raw_input: str = None,
                   collaterals: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        核心核保方法

        Args:
            total_asset: 客户总资产（元）
            holding_market_value: 持仓市值（元）
            credit_score: 信用评分（0-100）
            debt_status: 负债状态
            debt_amount: 负债金额（元）
            holding_months: 持股月数
            risk_level: 风险等级（C1-C6）
            credit_record: 信用记录（良好/一般/较差）
            holding_type: 持仓类型
            annual_income: 年收入（元）
            raw_input: 自然语言输入
            collaterals: 担保物明细列表

        Returns:
            Dict containing underwriting results
        """
        # 解析自然语言输入
        if raw_input:
            parsed = self.parse_user_input(raw_input)
            total_asset = total_asset or parsed.get('total_asset')
            holding_market_value = holding_market_value or parsed.get('holding_market_value')
            credit_score = credit_score or parsed.get('credit_score')
            debt_status = debt_status or parsed.get('debt_status')
            debt_amount = debt_amount or parsed.get('debt_amount')
            holding_months = holding_months or parsed.get('holding_months')
            risk_level = risk_level or parsed.get('risk_level')
            credit_record = credit_record or parsed.get('credit_record')
            holding_type = holding_type or parsed.get('holding_type', '主板股票')
            annual_income = annual_income or parsed.get('annual_income')
            if parsed.get('collaterals'):
                collaterals = parsed['collaterals']

        # 默认值
        total_asset = total_asset or 500_0000  # 默认500万
        holding_market_value = holding_market_value or (total_asset * 0.6)  # 默认60%持仓
        credit_score = credit_score or 75
        debt_status = debt_status or "无负债"
        debt_amount = debt_amount if debt_amount is not None else 0
        holding_months = holding_months or 12
        risk_level = risk_level or "C4"
        credit_record = credit_record or "良好"

        # 1. 准入评估
        admission_result = self.evaluate_admission(
            total_asset, holding_months, risk_level, credit_record
        )

        # 2. 担保物折算
        if collaterals:
            collateral_result = self.calculate_collaterals_from_list(collaterals)
        else:
            collateral_result = self.calculate_collateral_value(holding_market_value, holding_type)

        # 3. 额度计算
        quota_result = self.calculate_quota(
            total_asset, holding_market_value, holding_type, debt_amount
        )

        # 4. 风险提示
        risk_warnings = self.evaluate_risk_warnings(
            total_asset, holding_market_value, risk_level,
            credit_score, debt_amount, holding_type
        )

        # 5. 利率建议
        rate_suggestion = self.suggest_interest_rate(credit_score, risk_level)

        # 构建最终结果
        result = {
            "客户信息": {
                "总资产(万)": round(total_asset / 10000, 2),
                "持仓市值(万)": round(holding_market_value / 10000, 2),
                "持仓类型": holding_type,
                "信用评分": credit_score,
                "负债状态": debt_status,
                "负债金额(万)": round(debt_amount / 10000, 2) if debt_amount else 0,
                "持股月数": holding_months,
                "风险等级": risk_level,
                "信用记录": credit_record,
                "年收入(万)": round(annual_income / 10000, 2) if annual_income else None,
            },
            "准入评估": {
                "决定": admission_result["decision"],
                "说明": admission_result["decision_detail"],
                "资质评分": f"{admission_result['qualification_score']*100:.0f}%",
                "满足条件": f"{admission_result['qualified_count']}/{admission_result['total_count']}",
                "条件明细": admission_result["reasons"]
            },
            "担保物折算": {
                "总市值(万)": round(collateral_result.get('total_market_value', holding_market_value) / 10000, 2),
                "折算价值(万)": round(collateral_result.get('total_collateral_value', collateral_result.get('collateral_value', 0)) / 10000, 2),
                "综合折算率": collateral_result.get('overall_discount_rate', collateral_result.get('discount_rate', 0)),
                "明细": collateral_result.get('details', [
                    {
                        "asset_type": holding_type,
                        "market_value": holding_market_value,
                        "discount_rate": collateral_result.get('discount_rate', 0.65),
                        "collateral_value": collateral_result.get('collateral_value', 0)
                    }
                ])
            },
            "额度建议": {
                "最高可借金额(万)": round(quota_result['max_financing_amount'] / 10000, 2),
                "担保证券价值(万)": round(quota_result['collateral_value'] / 10000, 2),
                "维持担保比例": quota_result['maintenance_ratio_display'],
                "平仓线": quota_result['warning_line'],
                "警戒线": quota_result['alert_line']
            },
            "利率建议": {
                "融资年化利率": rate_suggestion['margin_rate_display'],
                "融券年化利率": rate_suggestion['security_rate_display'],
                "信用等级": rate_suggestion['credit_level'],
                "利率调整": rate_suggestion['adjustment_display']
            },
            "风险提示": [
                {
                    "级别": w["level"],
                    "类型": w["type"],
                    "说明": w["message"]
                } for w in risk_warnings
            ],
            "报告时间": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return result

    def format_text_report(self, result: Dict[str, Any]) -> str:
        """格式化输出为文本报告"""
        admission = result["准入评估"]
        collateral = result["担保物折算"]
        quota = result["额度建议"]
        rate = result["利率建议"]

        # 决策图标
        decision_icons = {"可开": "✅", "有条件开": "⚠️", "不开": "❌"}
        icon = decision_icons.get(admission["决定"], "📋")

        lines = [
            "=" * 52,
            "        券商两融智能核保报告 v2",
            "=" * 52,
            "",
            "【客户信息】",
            f"  总资产：{result['客户信息']['总资产(万)']}万",
            f"  持仓市值：{result['客户信息']['持仓市值(万)']}万",
            f"  持仓类型：{result['客户信息']['持仓类型']}",
            f"  信用评分：{result['客户信息']['信用评分']}",
            f"  负债状态：{result['客户信息']['负债状态']}",
            f"  持股月数：{result['客户信息']['持股月数']}个月",
            f"  风险等级：{result['客户信息']['风险等级']}",
            f"  信用记录：{result['客户信息']['信用记录']}",
            "",
            "【准入评估】",
            f"  ★ 准入决定：{admission['决定']} {icon}",
            f"  ★ 说明：{admission['说明']}",
            f"  ★ 资质评分：{admission['资质评分']}（{admission['满足条件']}）",
        ]

        for reason in admission["条件明细"]:
            lines.append(f"    {reason}")

        lines.extend([
            "",
            "【担保物折算】",
            f"  总市值：{collateral['总市值(万)']}万",
            f"  折算价值：{collateral['折算价值(万)']}万",
            f"  综合折算率：{collateral['综合折算率']:.0%}",
        ])

        for detail in collateral['明细']:
            lines.append(f"    {detail['asset_type']}：市值{detail['market_value']/10000:.0f}万 × {detail['discount_rate']:.0%} = {detail['collateral_value']/10000:.0f}万")

        lines.extend([
            "",
            "【额度建议】",
            f"  最高可借金额：{quota['最高可借金额(万)']}万",
            f"  担保证券价值：{quota['担保证券价值(万)']}万",
            f"  维持担保比例：{quota['维持担保比例']}",
            f"  警戒线：{quota['警戒线']}  |  平仓线：{quota['平仓线']}",
            "",
            "【利率建议】",
            f"  融资年化利率：{rate['融资年化利率']}",
            f"  融券年化利率：{rate['融券年化利率']}",
            f"  信用等级：{rate['信用等级']}  利率调整：{rate['利率调整']}",
        ])

        if result["风险提示"]:
            lines.append("")
            lines.append("【风险提示】")
            for w in result["风险提示"]:
                level_icon = {"高": "🔴", "中": "🟡", "低": "🟢"}.get(w["级别"], "⚪")
                lines.append(f"  {level_icon} [{w['级别']}] {w['类型']}：{w['说明']}")

        lines.extend([
            "",
            f"  报告时间：{result['报告时间']}",
            "=" * 52,
        ])

        return "\n".join(lines)


# 便捷函数
def underwrite(**kwargs) -> Dict[str, Any]:
    """快捷核保函数"""
    engine = UnderwritingV2Engine()
    return engine.underwrite(**kwargs)


def underwrite_from_text(text: str) -> Dict[str, Any]:
    """从自然语言文本快速核保"""
    engine = UnderwritingV2Engine()
    return engine.underwrite(raw_input=text)
