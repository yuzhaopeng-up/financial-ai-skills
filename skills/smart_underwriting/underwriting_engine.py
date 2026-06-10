"""
Smart Underwriting Engine - 智能核保引擎
基于投保人信息自动评估风险等级，输出核保决定、分级、保费调整系数及建议
"""

import re
from typing import Dict, List, Optional, Any


class SmartUnderwritingEngine:
    """智能核保引擎核心类"""

    # 职业风险等级映射
    OCCUPATION_RISK_MAP = {
        # 1类：低风险
        "办公室职员": 1.0, "公务员": 1.0, "教师": 1.0, "会计": 1.0, "律师": 1.0,
        "医生": 1.0, "银行职员": 1.0, "设计师": 1.0, "文员": 1.0, "职员": 1.0,
        "管理人员": 1.0, "企业主": 1.0,
        # 2类：较低风险
        "销售": 1.1, "餐饮服务": 1.1, "农林牧渔": 1.1, "服务员": 1.1, "营业员": 1.1,
        "司机": 1.1,
        # 3类：中等风险
        "机械操作工": 1.2, "电工": 1.2, "焊工": 1.2, "车床工": 1.2, "钳工": 1.2,
        "厨师": 1.2, "理发师": 1.2,
        # 4类：较高风险
        "建筑工人": 1.5, "消防员": 1.5, "警察": 1.5, "保安": 1.5, "装修工": 1.5,
        "木工": 1.5, "油漆工": 1.5,
        # 5类：高风险
        "矿工": 2.0, "隧道工": 2.0, "爆破工": 2.0, "采石工": 2.0,
        # 6类：拒保
        "高空作业": "reject", "潜水员": "reject", "特技演员": "reject",
        "蜘蛛人": "reject", "跳伞教练": "reject",
    }

    # 健康状况系数
    HEALTH_STATUS_MAP = {
        "优秀": 0.9,
        "良好": 1.0,
        "一般": 1.2,
        "较差": 1.5,
    }

    # 家族病史系数
    FAMILY_HISTORY_MAP = {
        "无": 1.0,
        "心脑血管疾病": 1.2,
        "糖尿病": 1.2,
        "恶性肿瘤": 1.3,
        "多种": 1.5,
    }

    # 重大既往症列表（绝对拒保）
    SERIOUS_MEDICAL_CONDITIONS = [
        "恶性肿瘤", "癌症", "白血病", "淋巴瘤",
        "心梗", "心肌梗死", "冠心病", "严重心脏病",
        "脑中风", "脑卒中", "脑血管瘤",
        "肝硬化", "肝衰竭", "重型肝炎",
        "肾功能衰竭", "尿毒症", "肾移植",
        "精神病", "精神分裂症", "抑郁症重度",
        "癫痫", "阿尔茨海默病", "帕金森病",
        "红斑狼疮", "类风湿性关节炎", "强直性脊柱炎",
        "器官移植", "器官移植术后",
        "艾滋病", "HIV",
        "慢性阻塞性肺疾病", "肺心病", "呼吸衰竭",
    ]

    def __init__(self):
        self.name = "SmartUnderwritingEngine"
        self.version = "1.0.0"

    def parse_user_input(self, text: str) -> Dict[str, Any]:
        """
        解析自然语言输入
        格式示例：智能核保 年龄45 职业企业主 健康良好 年收入100万 寿险500万 20年
        """
        result = {}

        # 年龄
        age_match = re.search(r'年龄(\d+)', text)
        if age_match:
            result['age'] = int(age_match.group(1))

        # 职业
        occ_match = re.search(r'职业(\S+)', text)
        if occ_match:
            result['occupation'] = occ_match.group(1)

        # 健康状况
        health_match = re.search(r'健康(优秀|良好|一般|较差)', text)
        if health_match:
            result['health_status'] = health_match.group(1)

        # 年收入（支持万/元）
        income_match = re.search(r'年收入(\d+(?:\.\d+)?)(万|元)?', text)
        if income_match:
            value = float(income_match.group(1))
            unit = income_match.group(2) or "万"
            result['annual_income'] = value if unit == "万" else value / 10000

        # 保额
        coverage_match = re.search(r'(寿险|重疾险|医疗险|意外险)(\d+(?:\.\d+)?)(万|元)?', text)
        if coverage_match:
            result['product_type'] = coverage_match.group(1)
            value = float(coverage_match.group(2))
            unit = coverage_match.group(3) or "万"
            result['coverage_amount'] = value if unit == "万" else value / 10000

        # 保障期限
        period_match = re.search(r'(\d+)年', text)
        if period_match:
            result['coverage_period'] = int(period_match.group(1))

        return result

    def evaluate_occupation_risk(self, occupation: str) -> Dict[str, Any]:
        """评估职业风险"""
        # 模糊匹配
        for key, value in self.OCCUPATION_RISK_MAP.items():
            if key in occupation or occupation in key:
                if value == "reject":
                    return {
                        "risk_factor": 3.0,
                        "decision": "拒保",
                        "reason": f"职业【{occupation}】属于高危职业（6类），拒保处理"
                    }
                return {
                    "risk_factor": value,
                    "decision": "通过",
                    "reason": f"职业【{occupation}】属于{list(self.OCCUPATION_RISK_MAP.keys()).index(key) // 8 + 1}类职业"
                }

        # 默认中等风险
        return {
            "risk_factor": 1.2,
            "decision": "通过",
            "reason": f"职业【{occupation}】按默认3类职业评估"
        }

    def evaluate_health_status(self, health_status: str) -> Dict[str, Any]:
        """评估健康状况"""
        factor = self.HEALTH_STATUS_MAP.get(health_status, 1.0)
        return {
            "risk_factor": factor,
            "reason": f"健康状况【{health_status}】对应系数{factor}"
        }

    def evaluate_family_history(self, family_history: str) -> Dict[str, Any]:
        """评估家族病史"""
        factor = self.FAMILY_HISTORY_MAP.get(family_history, 1.0)
        return {
            "risk_factor": factor,
            "reason": f"家族病史【{family_history}】对应系数{factor}"
        }

    def evaluate_age_factor(self, age: int) -> Dict[str, Any]:
        """评估年龄因素"""
        if age < 18:
            return {"risk_factor": 1.5, "decision": "拒保", "reason": "未成年人暂不受理"}
        if age > 65:
            return {"risk_factor": 1.5, "decision": "拒保", "reason": "65岁以上被保险人需特别评估"}
        if age >= 50:
            factor = 1.3
        elif age >= 40:
            factor = 1.2
        elif age >= 30:
            factor = 1.1
        else:
            factor = 1.0
        return {
            "risk_factor": factor,
            "reason": f"年龄{age}岁对应系数{factor}"
        }

    def evaluate_coverage_ratio(self, annual_income: float, coverage_amount: float, product_type: str) -> Dict[str, Any]:
        """评估保额与收入比（财务核保）"""
        ratio = coverage_amount / annual_income if annual_income > 0 else 999

        # 寿险：保额/年收入 <= 20为正常
        if product_type == "寿险":
            if ratio > 30:
                return {
                    "risk_factor": 2.0,
                    "decision": "加费或体检",
                    "reason": f"寿险保额{coverage_amount}万/年收入{annual_income}万={ratio:.1f}倍，超过30倍限额，需体检或财务核保"
                }
            elif ratio > 20:
                return {
                    "risk_factor": 1.3,
                    "decision": "需体检",
                    "reason": f"保额/年收入={ratio:.1f}倍，建议体检"
                }

        # 重疾险：保额/年收入 <= 5为正常
        if product_type == "重疾险":
            if ratio > 10:
                return {
                    "risk_factor": 1.8,
                    "decision": "加费或体检",
                    "reason": f"重疾险保额/年收入={ratio:.1f}倍，逆选择风险较高"
                }
            elif ratio > 5:
                return {
                    "risk_factor": 1.2,
                    "decision": "需体检",
                    "reason": f"保额/年收入={ratio:.1f}倍，建议体检"
                }

        return {
            "risk_factor": 1.0,
            "decision": "通过",
            "reason": f"保额/年收入={ratio:.1f}倍，财务核保通过"
        }

    def evaluate_medical_conditions(self, health_status: str) -> Dict[str, Any]:
        """评估既往症（简化版，实际应从健康告知问卷获取）"""
        # 如果健康状况较差，检查是否有既往症关键词
        if health_status == "较差":
            return {
                "risk_factor": 1.5,
                "decision": "次标体",
                "reason": "健康状况较差，需进一步核保评估"
            }
        return {
            "risk_factor": 1.0,
            "decision": "通过",
            "reason": "无重大既往症"
        }

    def calculate_total_risk_score(self, factors: List[Dict[str, float]]) -> float:
        """计算综合风险系数（乘法模型）"""
        total = 1.0
        for f in factors:
            total *= f['risk_factor']
        return round(total, 2)

    def determine_underwriting_decision(self, total_score: float, rejection_reasons: List[str]) -> Dict[str, Any]:
        """根据综合系数决定核保结论"""
        if rejection_reasons:
            return {
                "decision": "拒保",
                "level": "拒保体",
                "premium_factor": 0,
                "notes": "存在绝对拒保项，无法承保"
            }

        if total_score > 2.0:
            return {
                "decision": "拒保",
                "level": "拒保体",
                "premium_factor": 0,
                "notes": "综合风险系数过高，超出可承保范围"
            }
        elif total_score > 1.3:
            return {
                "decision": "加费",
                "level": "次标体",
                "premium_factor": total_score,
                "notes": f"综合风险系数{total_score}，按次标体加费承保"
            }
        elif total_score > 1.1:
            return {
                "decision": "加费",
                "level": "标准体",
                "premium_factor": 1.0,
                "notes": f"综合风险系数{total_score}，按标准体或轻微加费承保"
            }
        else:
            return {
                "decision": "标准体",
                "level": "优选体",
                "premium_factor": 1.0,
                "notes": f"综合风险系数{total_score}，优选体标准承保"
            }

    def underwrite(self, age: int = None, occupation: str = None,
                   health_status: str = None, family_medical_history: str = None,
                   annual_income: float = None, coverage_amount: float = None,
                   coverage_period: int = None, product_type: str = "寿险",
                   raw_input: str = None) -> Dict[str, Any]:
        """
        核心核保方法

        Args:
            age: 年龄
            occupation: 职业
            health_status: 健康状况（优秀/良好/一般/较差）
            family_medical_history: 家族病史
            annual_income: 年收入（万元）
            coverage_amount: 保额（万元）
            coverage_period: 保障期限（年）
            product_type: 产品类型（寿险/重疾险/医疗险/意外险）
            raw_input: 自然语言输入（可替代上述参数）

        Returns:
            Dict containing underwriting results
        """
        # 解析自然语言输入
        if raw_input:
            parsed = self.parse_user_input(raw_input)
            age = age or parsed.get('age')
            occupation = occupation or parsed.get('occupation')
            health_status = health_status or parsed.get('health_status')
            annual_income = annual_income or parsed.get('annual_income')
            coverage_amount = coverage_amount or parsed.get('coverage_amount')
            coverage_period = coverage_period or parsed.get('coverage_period')
            product_type = product_type or parsed.get('product_type', '寿险')

        # 默认值
        age = age or 30
        occupation = occupation or "企业主"
        health_status = health_status or "良好"
        family_medical_history = family_medical_history or "无"
        annual_income = annual_income or 50
        coverage_amount = coverage_amount or 100
        coverage_period = coverage_period or 20
        product_type = product_type or "寿险"

        # 评估各项风险因素
        rejection_reasons = []
        risk_factors = []

        # 1. 职业风险评估
        occ_result = self.evaluate_occupation_risk(occupation)
        risk_factors.append({"factor": "职业风险", **occ_result})
        if occ_result.get("decision") == "拒保":
            rejection_reasons.append(occ_result["reason"])

        # 2. 年龄因素
        age_result = self.evaluate_age_factor(age)
        risk_factors.append({"factor": "年龄因素", **age_result})
        if age_result.get("decision") == "拒保":
            rejection_reasons.append(age_result["reason"])

        # 3. 健康状况
        health_result = self.evaluate_health_status(health_status)
        risk_factors.append({"factor": "健康状况", **health_result})

        # 4. 家族病史
        family_result = self.evaluate_family_history(family_medical_history)
        risk_factors.append({"factor": "家族病史", **family_result})

        # 5. 财务核保
        financial_result = self.evaluate_coverage_ratio(annual_income, coverage_amount, product_type)
        risk_factors.append({"factor": "财务核保", **financial_result})

        # 6. 既往症评估
        medical_result = self.evaluate_medical_conditions(health_status)
        risk_factors.append({"factor": "既往症评估", **medical_result})

        # 计算综合风险系数
        total_score = self.calculate_total_risk_score([
            {"risk_factor": r["risk_factor"]} for r in risk_factors
        ])

        # 决定核保结论
        decision_result = self.determine_underwriting_decision(total_score, rejection_reasons)

        # 构建详细评估报告
        evaluation_details = []
        for rf in risk_factors:
            evaluation_details.append({
                "评估项目": rf["factor"],
                "风险系数": rf["risk_factor"],
                "说明": rf.get("reason", ""),
                "结论": rf.get("decision", "通过")
            })

        # 构建最终结果
        result = {
            "投保信息": {
                "年龄": age,
                "职业": occupation,
                "健康状况": health_status,
                "家族病史": family_medical_history,
                "年收入(万)": annual_income,
                "保额(万)": coverage_amount,
                "保障期限(年)": coverage_period,
                "产品类型": product_type
            },
            "核保决定": decision_result["decision"],
            "风险分级": decision_result["level"],
            "保费调整系数": decision_result["premium_factor"],
            "综合风险评分": total_score,
            "评估明细": evaluation_details,
            "拒保原因": rejection_reasons,
            "核保建议": decision_result["notes"]
        }

        return result

    def format_text_report(self, result: Dict[str, Any]) -> str:
        """格式化输出为文本报告"""
        lines = [
            "=" * 50,
            "       智能核保报告",
            "=" * 50,
            "",
            "【投保信息】",
            f"  年龄：{result['投保信息']['年龄']}岁",
            f"  职业：{result['投保信息']['职业']}",
            f"  健康状况：{result['投保信息']['健康状况']}",
            f"  家族病史：{result['投保信息']['家族病史']}",
            f"  年收入：{result['投保信息']['年收入(万)']}万元",
            f"  保额需求：{result['投保信息']['保额(万)']}万元",
            f"  保障期限：{result['投保信息']['保障期限(年)']}年",
            f"  产品类型：{result['投保信息']['产品类型']}",
            "",
            "【核保结论】",
            f"  ★ 核保决定：{result['核保决定']}",
            f"  ★ 风险分级：{result['风险分级']}",
            f"  ★ 保费系数：{result['保费调整系数']}",
            f"  ★ 综合评分：{result['综合风险评分']}",
            "",
            "【评估明细】",
        ]

        for detail in result['评估明细']:
            lines.append(f"  [{detail['评估项目']}] 系数:{detail['风险系数']} - {detail['说明']}")

        if result['拒保原因']:
            lines.extend(["", "【拒保原因】"])
            for reason in result['拒保原因']:
                lines.append(f"  ⚠ {reason}")

        lines.extend([
            "",
            "【核保建议】",
            f"  {result['核保建议']}",
            "=" * 50,
        ])

        return "\n".join(lines)


# 便捷函数
def underwrite(**kwargs) -> Dict[str, Any]:
    """快捷核保函数"""
    engine = SmartUnderwritingEngine()
    return engine.underwrite(**kwargs)


def underwrite_from_text(text: str) -> Dict[str, Any]:
    """从自然语言文本快速核保"""
    engine = SmartUnderwritingEngine()
    return engine.underwrite(raw_input=text)
