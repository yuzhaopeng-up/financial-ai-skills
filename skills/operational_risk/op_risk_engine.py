"""
Operational Risk Engine - 操作风险管理引擎

支持7大操作风险类别的分类、风险矩阵评分、损失估算和管控建议。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from typing import Optional


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------

@dataclass
class RiskMatrix:
    """风险矩阵结果"""
    possibility: int      # 可能性 1-5
    impact: int          # 影响程度 1-5
    score: int            # 总分 = possibility × impact
    level: str            # 低/中/高/极高


@dataclass
class LossEstimate:
    """损失估算"""
    direct: float         # 直接损失（万元）
    indirect: float       # 间接损失（万元）
    regulatory_fine: float # 监管罚款（万元）
    total: float          # 总损失


@dataclass
class ControlMeasures:
    """管控措施"""
    preventive: list[str]   # 预防措施
    detective: list[str]    # 检测措施
    corrective: list[str]   # 纠正措施


@dataclass
class OperationalRiskResult:
    """操作风险评估完整结果"""
    category: str
    category_code: str
    risk_matrix: RiskMatrix
    loss_estimate: LossEstimate
    controls: ControlMeasures
    risk_level: str
    next_action: str
    raw_input: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def summary(self) -> str:
        """人类可读的摘要文本"""
        lines = [
            f"【操作风险评估报告】",
            f"",
            f"风险类别：{self.category}（{self.category_code}）",
            f"风险等级：{self.risk_level}（评分 {self.risk_matrix.score}）",
            f"  └ 可能性：{self.risk_matrix.possibility}/5 | 影响程度：{self.risk_matrix.impact}/5",
            f"",
            f"损失估算（万元）：",
            f"  └ 直接损失：{self.loss_estimate.direct:.1f} | 间接损失：{self.loss_estimate.indirect:.1f} | 监管罚款：{self.loss_estimate.regulatory_fine:.1f}",
            f"  └ 总损失估算：{self.loss_estimate.total:.1f}",
            f"",
            f"管控建议：",
            f"  预防：{'、'.join(self.controls.preventive)}",
            f"  检测：{'、'.join(self.controls.detective)}",
            f"  纠正：{'、'.join(self.controls.corrective)}",
            f"",
            f"处置建议：{self.next_action}",
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# 7大操作风险类别定义
RISK_CATEGORIES = {
    "内部欺诈": {
        "code": "OR-01",
        "keywords": ["内部欺诈", "内部欺诈", "员工欺诈", "员工盗用", "伪造", "职务侵占", "挪用资金", "内部舞弊"],
        "default_possibility": 2,
        "default_impact": 4,
    },
    "外部欺诈": {
        "code": "OR-02",
        "keywords": ["外部欺诈", "电信诈骗", "盗刷", "假冒客户", "伪卡", "钓鱼", "欺诈"],
        "default_possibility": 3,
        "default_impact": 3,
    },
    "就业政策和工作场所安全": {
        "code": "OR-03",
        "keywords": ["就业政策", "劳动纠纷", "职场暴力", "职场骚扰", "职业病", "工伤", "解聘", "歧视"],
        "default_possibility": 2,
        "default_impact": 3,
    },
    "客户产品及业务操作": {
        "code": "OR-04",
        "keywords": ["客户产品", "产品设计缺陷", "销售误导", "信息披露违规", "适当性", "违规销售", "误导消费者"],
        "default_possibility": 3,
        "default_impact": 3,
    },
    "执行交割及流程管理": {
        "code": "OR-05",
        "keywords": ["执行交割", "流程管理", "交易错误", "清算失误", "流程违规", "操作失误", "交割失败", "对账差异"],
        "default_possibility": 3,
        "default_impact": 3,
    },
    "系统和技术故障": {
        "code": "OR-06",
        "keywords": ["系统故障", "技术故障", "系统宕机", "数据丢失", "网络攻击", "黑客", "信息泄露", "IT故障", "数据库故障"],
        "default_possibility": 2,
        "default_impact": 5,
    },
    "实体资产损坏": {
        "code": "OR-07",
        "keywords": ["实体资产损坏", "火灾", "自然灾害", "盗窃", "损毁", "资产损失", "物理损坏"],
        "default_possibility": 1,
        "default_impact": 3,
    },
}

# 风险等级阈值
RISK_LEVEL_THRESHOLDS = {
    "极高": (20, 25),
    "高":  (12, 19),
    "中":  (6, 11),
    "低":  (1, 5),
}

# 频率 → 可能性映射（考虑意图强度与完成度）
FREQUENCY_POSSIBILITY_MAP = {
    # 未遂：意图已显现+计划性强 → 较高可能性
    "未遂": 3,
    # 已遂：已造成损失，完成度高
    "已遂": 5,
    # 频率维度
    "罕见": 1,
    "偶尔": 2,
    "有时": 3,
    "经常": 4,
    "持续": 5,
}

# 操作员类型 → 可能性调整
OPERATOR_POSSIBILITY_ADJUST = {
    "内部": +1,
    "外部": 0,
    "客户": 0,
}

# 损失金额（万元）→ 影响程度估算
LOSS_IMPACT_RULES = [
    (5000, 5),   # ≥5000万 → 影响5（灾难性）
    (1000, 4),   # ≥1000万 → 影响4（严重）
    (500, 3),    # ≥500万  → 影响3（较大）
    (100, 2),    # ≥100万  → 影响2（中等）
    (0, 1),      # 其他    → 影响1（轻微）
]

# ---------------------------------------------------------------------------
# 引擎主类
# ---------------------------------------------------------------------------

class OperationalRiskEngine:
    """
    操作风险管理引擎

    用法示例：
        engine = OperationalRiskEngine()
        result = engine.analyze(
            scenario="员工伪造理财产品合同诈骗客户资金",
            loss_amount=200,
            frequency="未遂",
            operator="内部"
        )
        print(result.summary())
    """

    def __init__(self):
        self.categories = RISK_CATEGORIES

    # ------------------------------------------------------------------
    # 公开接口
    # ------------------------------------------------------------------

    def analyze(
        self,
        scenario: str,
        loss_amount: float = 0,
        frequency: str = "偶尔",
        operator: str = "内部",
        category_override: Optional[str] = None,
    ) -> OperationalRiskResult:
        """
        分析业务场景，返回操作风险评估结果。

        Args:
            scenario: 业务场景描述（必填）
            loss_amount: 损失金额（万元），默认0
            frequency: 发生频率（未遂/偶尔/经常/持续），默认"偶尔"
            operator: 相关操作员（内部/外部/客户），默认"内部"
            category_override: 手动指定风险类别（可选）

        Returns:
            OperationalRiskResult 对象
        """
        raw_input = f"{scenario} | 损失:{loss_amount}万 | 频率:{frequency} | 操作员:{operator}"

        # Step 1: 识别风险类别
        category_name, category_code = self._classify(scenario, category_override)

        # Step 2: 计算可能性
        possibility = self._calc_possibility(frequency, operator, category_name)

        # Step 3: 计算影响程度
        impact = self._calc_impact(loss_amount, category_name)

        # Step 4: 风险矩阵评分
        risk_matrix = self._calc_risk_matrix(possibility, impact)

        # Step 5: 损失估算
        loss_estimate = self._calc_loss(loss_amount, category_name, risk_matrix.level)

        # Step 6: 管控建议
        controls = self._generate_controls(category_name, risk_matrix.level)

        # Step 7: 处置建议
        next_action = self._generate_next_action(risk_matrix.level, category_code)

        return OperationalRiskResult(
            category=category_name,
            category_code=category_code,
            risk_matrix=risk_matrix,
            loss_estimate=loss_estimate,
            controls=controls,
            risk_level=risk_matrix.level,
            next_action=next_action,
            raw_input=raw_input,
        )

    def batch_analyze(self, items: list[dict]) -> list[OperationalRiskResult]:
        """
        批量分析多个业务场景。

        Args:
            items: 列表，每项包含 scenario/loss_amount/frequency/operator 字段

        Returns:
            OperationalRiskResult 列表
        """
        results = []
        for item in items:
            result = self.analyze(
                scenario=item.get("scenario", ""),
                loss_amount=item.get("loss_amount", 0),
                frequency=item.get("frequency", "偶尔"),
                operator=item.get("operator", "内部"),
                category_override=item.get("category_override", None),
            )
            results.append(result)
        return results

    def parse_cli_input(self, text: str) -> dict:
        """
        解析 CLI 自然语言输入。
        支持格式："操作风险 内部欺诈 损失200万 未遂"

        Returns:
            dict 包含 scenario/loss_amount/frequency/operator
        """
        text = text.strip()

        # 提取损失金额（支持"200万"、"500万元"、"200万"等）
        loss_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:万|万元|千万|亿)", text)
        loss_amount = float(loss_match.group(1)) if loss_match else 0
        if "亿" in (loss_match.group(0) if loss_match else ""):
            loss_amount *= 10000  # 亿→万

        # 提取频率
        frequency = "偶尔"
        for kw in ["未遂", "已遂", "偶尔", "经常", "持续"]:
            if kw in text:
                frequency = kw
                break

        # 提取操作员
        operator = "内部"
        if "外部" in text or "客户" in text:
            operator = "外部" if "外部" in text else "客户"

        # 提取风险类别（从7大类中匹配）
        category = None
        for cat_name in self.categories:
            if cat_name in text or any(kw in text for kw in self.categories[cat_name]["keywords"]):
                category = cat_name
                break

        # 构造场景描述
        scenario = text

        return {
            "scenario": scenario,
            "loss_amount": loss_amount,
            "frequency": frequency,
            "operator": operator,
            "category_override": category,
        }

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    def _classify(self, scenario: str, override: Optional[str] = None) -> tuple[str, str]:
        """识别风险类别"""
        if override and override in self.categories:
            cat = self.categories[override]
            return override, cat["code"]

        # 关键词匹配
        scenario_lower = scenario.lower()
        for cat_name, cat_info in self.categories.items():
            for kw in cat_info["keywords"]:
                if kw in scenario:
                    return cat_name, cat_info["code"]

        # 默认：执行交割及流程管理
        cat = self.categories["执行交割及流程管理"]
        return "执行交割及流程管理", cat["code"]

    def _calc_possibility(
        self,
        frequency: str,
        operator: str,
        category: str,
    ) -> int:
        """计算可能性得分"""
        # 基础分：频率
        base = FREQUENCY_POSSIBILITY_MAP.get(frequency, 2)

        # 操作员调整
        adj = OPERATOR_POSSIBILITY_ADJUST.get(operator, 0)
        base += adj

        # 类别默认值微调
        cat_default = self.categories[category]["default_possibility"]
        if base < cat_default:
            base = cat_default

        return max(1, min(5, base))

    def _calc_impact(self, loss_amount: float, category: str) -> int:
        """计算影响程度"""
        # 有损失金额时按金额阈值
        if loss_amount > 0:
            for threshold, impact in LOSS_IMPACT_RULES:
                if loss_amount >= threshold:
                    return impact
            return 1

        # 无损失金额时用类别默认值
        return self.categories[category]["default_impact"]

    def _calc_risk_matrix(self, possibility: int, impact: int) -> RiskMatrix:
        """计算风险矩阵"""
        score = possibility * impact

        if score >= 20:
            level = "极高"
        elif score >= 12:
            level = "高"
        elif score >= 6:
            level = "中"
        else:
            level = "低"

        return RiskMatrix(
            possibility=possibility,
            impact=impact,
            score=score,
            level=level,
        )

    def _calc_loss(
        self,
        loss_amount: float,
        category: str,
        risk_level: str,
    ) -> LossEstimate:
        """计算损失估算"""
        if loss_amount > 0:
            direct = loss_amount
            # 间接损失通常为直接的10%-50%
            if risk_level in ["高", "极高"]:
                indirect = loss_amount * 0.5
                regulatory_fine = loss_amount * 0.5
            elif risk_level == "中":
                indirect = loss_amount * 0.25
                regulatory_fine = loss_amount * 0.25
            else:
                indirect = loss_amount * 0.1
                regulatory_fine = loss_amount * 0.1
        else:
            # 无已知损失，估算
            if risk_level in ["极高"]:
                direct, indirect, regulatory_fine = 5000, 2500, 2500
            elif risk_level == "高":
                direct, indirect, regulatory_fine = 1000, 500, 500
            elif risk_level == "中":
                direct, indirect, regulatory_fine = 500, 125, 125
            else:
                direct, indirect, regulatory_fine = 100, 10, 10

        total = direct + indirect + regulatory_fine
        return LossEstimate(
            direct=round(direct, 1),
            indirect=round(indirect, 1),
            regulatory_fine=round(regulatory_fine, 1),
            total=round(total, 1),
        )

    def _generate_controls(self, category: str, risk_level: str) -> ControlMeasures:
        """生成管控建议"""
        # 通用建议库
        controls_db: dict[str, dict[str, list[str]]] = {
            "内部欺诈": {
                "preventive": [
                    "实施员工背景审查与定期复核",
                    "建立双人复核与授权分离机制",
                    "完善绩效考核与激励约束平衡",
                    "加强职业道德与合规文化建设",
                ],
                "detective": [
                    "部署交易监控系统与异常预警",
                    "定期开展内部审计与突击检查",
                    "建立举报机制与保护制度",
                    "实施关键岗位轮岗与强制休假",
                ],
                "corrective": [
                    "制定欺诈事件应急处置预案",
                    "建立客户资金优先补偿机制",
                    "及时向监管机构报告并配合调查",
                    "复盘整改，完善制度漏洞",
                ],
            },
            "外部欺诈": {
                "preventive": [
                    "加强客户身份识别（KYC）",
                    "实施多因素身份验证",
                    "建立欺诈风险预警名单库",
                    "开展客户防欺诈宣传教育",
                ],
                "detective": [
                    "部署实时交易监控系统",
                    "建立异常交易识别模型",
                    "定期分析欺诈手法演变趋势",
                    "与同业共享欺诈情报",
                ],
                "corrective": [
                    "建立快速冻结与止付机制",
                    "配合公安机关调查取证",
                    "完善客户损失补偿流程",
                    "迭代更新风控规则与模型",
                ],
            },
            "就业政策和工作场所安全": {
                "preventive": [
                    "完善人力资源管理制度",
                    "建立职场骚扰零容忍政策",
                    "定期开展职业健康安全培训",
                    "配备必要的劳动保护设施",
                ],
                "detective": [
                    "建立员工投诉与申诉渠道",
                    "定期开展职场环境评估",
                    "监控劳动纠纷苗头事件",
                    "建立离职面谈与风险评估机制",
                ],
                "corrective": [
                    "制定劳动纠纷应对预案",
                    "依法合规处理劳动关系",
                    "提供心理咨询与援助服务",
                    "配合劳动监察部门检查",
                ],
            },
            "客户产品及业务操作": {
                "preventive": [
                    "完善产品设计合规审查流程",
                    "建立产品上市前风险评估制度",
                    "加强销售话术标准化管理",
                    "落实投资者适当性管理要求",
                ],
                "detective": [
                    "定期开展产品合规后评估",
                    "监控销售误导投诉与舆情",
                    "抽查销售过程双录资料",
                    "建立客户回访与满意度调查",
                ],
                "corrective": [
                    "及时停售问题产品",
                    "制定客户投诉处理预案",
                    "向监管机构主动报告",
                    "完善信息披露与补偿机制",
                ],
            },
            "执行交割及流程管理": {
                "preventive": [
                    "建立标准化操作流程（SOP）",
                    "实施关键环节复核机制",
                    "加强员工操作技能培训",
                    "建立流程变更评审制度",
                ],
                "detective": [
                    "部署流程监控与预警系统",
                    "定期开展操作风险自评估",
                    "建立对账与交叉核验机制",
                    "实施差错率等绩效考核",
                ],
                "corrective": [
                    "建立操作差错快速纠错机制",
                    "完善客户告知与补偿流程",
                    "定期复盘操作失误案例",
                    "优化流程设计与系统控制",
                ],
            },
            "系统和技术故障": {
                "preventive": [
                    "建立系统变更管理流程",
                    "实施数据备份与灾难恢复计划",
                    "定期开展渗透测试与漏洞扫描",
                    "建立供应商技术评估机制",
                ],
                "detective": [
                    "部署系统监控与告警平台",
                    "7×24小时运维值守",
                    "定期开展业务连续性演练",
                    "建立网络安全态势感知能力",
                ],
                "corrective": [
                    "制定网络安全事件应急预案",
                    "建立故障快速定位与恢复机制",
                    "及时向监管机构报告数据泄露",
                    "开展事后复盘与系统加固",
                ],
            },
            "实体资产损坏": {
                "preventive": [
                    "配备消防与安防设施",
                    "定期开展安全检查与维护",
                    "建立自然灾害预警响应机制",
                    "购买财产保险覆盖主要风险",
                ],
                "detective": [
                    "部署安防监控系统",
                    "定期开展安全风险评估",
                    "建立资产盘点与巡检制度",
                    "监测周边环境风险因素",
                ],
                "corrective": [
                    "启动应急响应与人员疏散预案",
                    "开展财产损失评估与保险理赔",
                    "配合公安机关调查取证",
                    "修复或重建受损资产设施",
                ],
            },
        }

        default_controls: dict[str, dict[str, list[str]]] = {
            "preventive": ["建立风险识别与评估机制", "完善内部控制制度", "加强员工合规培训"],
            "detective": ["定期开展风险排查", "建立监控预警体系", "实施内部审计监督"],
            "corrective": ["制定应急处置预案", "及时整改缺陷", "总结经验教训"],
        }

        controls = controls_db.get(category, default_controls)

        # 极高风险时增加建议
        if risk_level in ["极高", "高"]:
            extra_prev = ["由高级管理层直接督办", "配置专项风险准备金"]
            extra_det = ["增加检查频次至每周", "引入外部审计机构核查"]
            controls["preventive"] = extra_prev + controls["preventive"]
            controls["detective"] = extra_det + controls["detective"]

        return ControlMeasures(
            preventive=controls["preventive"],
            detective=controls["detective"],
            corrective=controls["corrective"],
        )

    def _generate_next_action(self, risk_level: str, category_code: str) -> str:
        """生成处置建议"""
        if risk_level == "极高":
            return "【紧急】立即处置，由董事会/高级管理层牵头，2小时内上报监管机构"
        elif risk_level == "高":
            return "【优先】优先处置，风险管理部3日内上报，相关部门制定整改计划"
        elif risk_level == "中":
            return "【常规】纳入常规管理，部门负责人跟踪，定期向风控委员会报告"
        else:
            return "【持续】纳入持续监测，定期复盘，更新风险缓释措施"


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    engine = OperationalRiskEngine()

    # 测试用例
    result = engine.analyze(
        scenario="员工伪造理财产品合同，涉嫌诈骗客户资金",
        loss_amount=200,
        frequency="未遂",
        operator="内部",
    )
    print(result.summary())
    print("\n--- JSON ---")
    print(result.to_json())
