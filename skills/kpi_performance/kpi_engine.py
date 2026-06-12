"""
KPI 绩效考核引擎
Bank Performance Evaluation Engine

支持岗位：客户经理（大堂/对公/零售/理财）、柜员、风控经理、产品经理、网点负责人
KPI维度：存款类、贷款类、中间业务收入、客户类、风险合规类
"""

from dataclasses import dataclass, field
from typing import Any
import json


@dataclass
class KPIIndicator:
    """单个KPI指标"""
    name: str                          # 指标名称
    weight: float                      # 权重（%）
    target: str                        # 目标值
    threshold: str                     # 及格线
    scoring_method: str                # 评分方法
    data_required: list[str] = field(default_factory=list)  # 所需数据


@dataclass
class KPICategory:
    """KPI分类"""
    dimension: str                     # 维度名称
    indicators: list[KPIIndicator]    # 指标列表
    category_weight: float = 0.0      # 维度权重


@dataclass
class KPIResult:
    """完整KPI考核方案"""
    position: str                      # 岗位
    sub_type: str                      # 子类型
    period: str                        # 考核周期
    categories: list[KPICategory]      # KPI分类列表
    total_weight: float = 100.0       # 总权重
    assessment_rules: str = ""         # 考核规则说明
    data_requirements: list[str] = field(default_factory=list)  # 数据要求
    improvement_suggestions: list[str] = field(default_factory=list)  # 改进建议

    def to_dict(self) -> dict:
        return {
            "position": self.position,
            "sub_type": self.sub_type,
            "period": self.period,
            "total_weight": self.total_weight,
            "assessment_rules": self.assessment_rules,
            "categories": [
                {
                    "dimension": cat.dimension,
                    "category_weight": cat.category_weight,
                    "indicators": [
                        {
                            "name": ind.name,
                            "weight": ind.weight,
                            "target": ind.target,
                            "threshold": ind.threshold,
                            "scoring_method": ind.scoring_method,
                            "data_required": ind.data_required,
                        }
                        for ind in cat.indicators
                    ]
                }
                for cat in self.categories
            ],
            "data_requirements": self.data_requirements,
            "improvement_suggestions": self.improvement_suggestions,
        }


class KPIPerformanceEngine:
    """
    银行绩效考核引擎
    根据岗位类型和考核周期，自动生成KPI考核方案
    """

    # ============================================================
    # 岗位配置
    # ============================================================

    POSITION_CONFIGS = {
        "客户经理": {
            "sub_types": ["大堂客户经理", "对公客户经理", "零售客户经理", "理财客户经理"],
            "default_sub": "零售客户经理",
        },
        "柜员": {
            "sub_types": ["综合柜员", "现金柜员"],
            "default_sub": "综合柜员",
        },
        "风控经理": {
            "sub_types": ["信贷风控经理", "柜面风控经理"],
            "default_sub": "信贷风控经理",
        },
        "产品经理": {
            "sub_types": ["存款产品经理", "贷款产品经理", "中间业务产品经理"],
            "default_sub": "存款产品经理",
        },
        "网点负责人": {
            "sub_types": ["支行行长", "网点主任"],
            "default_sub": "支行行长",
        },
    }

    PERIOD_CONFIGS = {
        "季度": {
            "description": "季度绩效考核（Q1/Q2/Q3/Q4）",
            "scoring_season": "季度评分",
        },
        "月度": {
            "description": "月度绩效考核",
            "scoring_season": "月度评分",
        },
    }

    # ============================================================
    # 客户经理（大堂/对公/零售/理财）KPI 配置
    # ============================================================

    KMI_HALL_KPI = KPICategory(
        dimension="大堂客户经理",
        category_weight=100.0,
        indicators=[
            KPIIndicator(
                name="日均存款增量",
                weight=25.0,
                target="季度日均新增≥3000万元",
                threshold="季度日均新增≥1500万元",
                scoring_method="完成率法：实际增量/目标增量×25分，上限25分",
                data_required=["每日存款余额台账", "季末存款余额报表"],
            ),
            KPIIndicator(
                name="新开客户数（有效户）",
                weight=20.0,
                target="季度新增有效客户≥150户",
                threshold="季度新增有效客户≥80户",
                scoring_method="完成率法：实际数/目标数×20分，上限20分",
                data_required=["新开客户清单", "客户信息表", "有效户认定标准"],
            ),
            KPIIndicator(
                name="客户满意度",
                weight=15.0,
                target="满意度评分≥95分",
                threshold="满意度评分≥88分",
                scoring_method="满意度调查评分直接折算",
                data_required=["客户满意度调查问卷数据"],
            ),
            KPIIndicator(
                name="产品渗透率（理财/基金）",
                weight=15.0,
                target="客户产品持有率≥60%",
                threshold="客户产品持有率≥40%",
                scoring_method="实际渗透率/目标渗透率×15分",
                data_required=["客户资产配置表", "产品持有统计"],
            ),
            KPIIndicator(
                name="合规操作评分",
                weight=15.0,
                target="合规评分≥98分",
                threshold="合规评分≥92分",
                scoring_method="合规检查评分直接折算",
                data_required=["内控合规检查记录", "神秘人检查报告"],
            ),
            KPIIndicator(
                name="中间业务收入贡献",
                weight=10.0,
                target="季度中收≥50万元",
                threshold="季度中收≥25万元",
                scoring_method="完成率法：实际/目标×10分",
                data_required=["中间业务收入台账", "手续费收入报表"],
            ),
        ],
    )

    KMI_CORPORATE_KPI = KPICategory(
        dimension="对公客户经理",
        category_weight=100.0,
        indicators=[
            KPIIndicator(
                name="对公存款日均余额",
                weight=25.0,
                target="季度日均对公存款新增≥1亿元",
                threshold="季度日均对公存款新增≥5000万元",
                scoring_method="完成率法：实际/目标×25分，上限25分",
                data_required=["对公存款明细账", "日均存款计算表"],
            ),
            KPIIndicator(
                name="对公贷款投放量",
                weight=20.0,
                target="季度新增对公贷款≥2亿元",
                threshold="季度新增对公贷款≥1亿元",
                scoring_method="完成率法：实际/目标×20分，上限20分",
                data_required=["贷款台账", "贷款发放明细"],
            ),
            KPIIndicator(
                name="有效企业客户新增",
                weight=15.0,
                target="季度新增有效企业客户≥20户",
                threshold="季度新增有效企业客户≥10户",
                scoring_method="完成率法：实际/目标×15分",
                data_required=["企业客户清单", "开户资料"],
            ),
            KPIIndicator(
                name="客户经理管户数",
                weight=10.0,
                target="管户企业≥80户",
                threshold="管户企业≥50户",
                scoring_method="达标即得满分10分，未达标按比例扣分",
                data_required=["管户客户清单"],
            ),
            KPIIndicator(
                name="不良贷款率控制",
                weight=15.0,
                target="不良率≤1.0%",
                threshold="不良率≤2.0%",
                scoring_method="达标得15分，超标按超标幅度扣分",
                data_required=["不良贷款台账", "五级分类报表"],
            ),
            KPIIndicator(
                name="合规与风险合规评分",
                weight=15.0,
                target="合规评分≥97分",
                threshold="合规评分≥90分",
                scoring_method="合规检查评分直接折算",
                data_required=["内控检查记录", "风险排查报告"],
            ),
        ],
    )

    KMI_RETAIL_KPI = KPICategory(
        dimension="零售客户经理",
        category_weight=100.0,
        indicators=[
            KPIIndicator(
                name="储蓄存款日均增量",
                weight=25.0,
                target="季度日均新增≥5000万元",
                threshold="季度日均新增≥2500万元",
                scoring_method="完成率法：实际/目标×25分，上限25分",
                data_required=["个人存款台账", "日均存款报表"],
            ),
            KPIIndicator(
                name="个人贷款投放量",
                weight=20.0,
                target="季度新增个人贷款≥8000万元",
                threshold="季度新增个人贷款≥4000万元",
                scoring_method="完成率法：实际/目标×20分，上限20分",
                data_required=["个人贷款台账", "贷款发放明细"],
            ),
            KPIIndicator(
                name="新增个人有效客户",
                weight=15.0,
                target="季度新增有效个人客户≥200户",
                threshold="季度新增有效个人客户≥100户",
                scoring_method="完成率法：实际/目标×15分",
                data_required=["新开个人账户清单", "客户信息表"],
            ),
            KPIIndicator(
                name="理财/基金销售收入",
                weight=15.0,
                target="季度销售额≥3000万元",
                threshold="季度销售额≥1500万元",
                scoring_method="完成率法：实际/目标×15分",
                data_required=["理财销售台账", "基金销售报表"],
            ),
            KPIIndicator(
                name="客户资产留存率",
                weight=15.0,
                target="资产留存率≥95%",
                threshold="资产留存率≥88%",
                scoring_method="达标得15分，每降1%扣2分",
                data_required=["客户AUM变动表", "资产流失分析"],
            ),
            KPIIndicator(
                name="合规操作与反洗钱",
                weight=10.0,
                target="合规评分≥97分",
                threshold="合规评分≥90分",
                scoring_method="合规评分直接折算",
                data_required=["合规检查记录", "反洗钱系统数据"],
            ),
        ],
    )

    KMI_WEALTH_KPI = KPICategory(
        dimension="理财客户经理",
        category_weight=100.0,
        indicators=[
            KPIIndicator(
                name="管理客户资产总量（AUM）",
                weight=25.0,
                target="季度AUM新增≥1亿元",
                threshold="季度AUM新增≥5000万元",
                scoring_method="完成率法：实际/目标×25分，上限25分",
                data_required=["客户资产配置表", "AUM统计报表"],
            ),
            KPIIndicator(
                name="理财产品销售额",
                weight=20.0,
                target="季度销售额≥5000万元",
                threshold="季度销售额≥2500万元",
                scoring_method="完成率法：实际/目标×20分，上限20分",
                data_required=["理财销售系统数据", "销售明细台账"],
            ),
            KPIIndicator(
                name="基金/保险销售收入",
                weight=15.0,
                target="季度销售收入≥1500万元",
                threshold="季度销售收入≥800万元",
                scoring_method="完成率法：实际/目标×15分",
                data_required=["基金销售报表", "保险代理收入台账"],
            ),
            KPIIndicator(
                name="VIP客户新增",
                weight=15.0,
                target="季度新增VIP客户≥30户",
                threshold="季度新增VIP客户≥15户",
                scoring_method="完成率法：实际/目标×15分",
                data_required=["VIP客户名单", "客户等级变动记录"],
            ),
            KPIIndicator(
                name="客户持有产品种类数（交叉销售）",
                weight=15.0,
                target="户均持有产品≥3种",
                threshold="户均持有产品≥2种",
                scoring_method="达标得15分，每降0.5种扣3分",
                data_required=["客户产品持有统计表"],
            ),
            KPIIndicator(
                name="合规与适当性管理",
                weight=10.0,
                target="合规评分≥98分 | 适当性评估覆盖率100%",
                threshold="合规评分≥93分 | 适当性评估覆盖率≥95%",
                scoring_method="适当性合规评分直接折算",
                data_required=["适当性评估记录", "合规检查报告"],
            ),
        ],
    )

    # ============================================================
    # 柜员 KPI 配置
    # ============================================================

    TELLER_KPI = KPICategory(
        dimension="柜员",
        category_weight=100.0,
        indicators=[
            KPIIndicator(
                name="业务量（笔数）",
                weight=25.0,
                target="月均业务量≥1500笔",
                threshold="月均业务量≥1000笔",
                scoring_method="完成率法：实际/目标×25分，上限25分",
                data_required=["柜面业务交易日志", "业务量统计表"],
            ),
            KPIIndicator(
                name="业务差错率",
                weight=20.0,
                target="差错率≤0.3%",
                threshold="差错率≤0.8%",
                scoring_method="达标得20分，超标按超标幅度扣分，每超0.1%扣2分",
                data_required=["差错处理台账", "稽核差错报告"],
            ),
            KPIIndicator(
                name="客户满意度",
                weight=20.0,
                target="满意度评分≥96分",
                threshold="满意度评分≥90分",
                scoring_method="满意度调查评分直接折算",
                data_required=["柜面满意度调查", "955xx投诉记录"],
            ),
            KPIIndicator(
                name="服务效率（平均办理时长）",
                weight=15.0,
                target="平均办理时长≤6分钟/笔",
                threshold="平均办理时长≤8分钟/笔",
                scoring_method="达标得15分，每超1分钟扣3分",
                data_required=["业务耗时统计表"],
            ),
            KPIIndicator(
                name="中间业务营销（信用卡/理财）",
                weight=10.0,
                target="季度营销业绩前30%",
                threshold="季度营销业绩前60%",
                scoring_method="排名百分位法折算",
                data_required=["营销业绩统计表"],
            ),
            KPIIndicator(
                name="合规操作评分",
                weight=10.0,
                target="合规评分≥98分",
                threshold="合规评分≥93分",
                scoring_method="合规评分直接折算",
                data_required=["内控合规检查记录", "神秘人检查报告"],
            ),
        ],
    )

    # ============================================================
    # 风控经理 KPI 配置
    # ============================================================

    RISK_CORPORATE_KPI = KPICategory(
        dimension="信贷风控经理",
        category_weight=100.0,
        indicators=[
            KPIIndicator(
                name="贷款审查通过率",
                weight=20.0,
                target="审查通过率75%-85%",
                threshold="审查通过率65%-90%",
                scoring_method="区间达标准得满分20分，区间外按偏离幅度扣分",
                data_required=["贷款审查记录", "审查通过率统计"],
            ),
            KPIIndicator(
                name="不良贷款率",
                weight=25.0,
                target="管户不良率≤1.5%",
                threshold="管户不良率≤2.5%",
                scoring_method="达标得25分，超标按超标幅度扣分",
                data_required=["不良贷款台账", "五级分类报表"],
            ),
            KPIIndicator(
                name="风险预警准确率",
                weight=20.0,
                target="预警准确率≥85%",
                threshold="预警准确率≥70%",
                scoring_method="准确率直接折算",
                data_required=["风险预警系统记录", "预警核查报告"],
            ),
            KPIIndicator(
                name="信贷检查覆盖率",
                weight=15.0,
                target="季度检查覆盖管户100%",
                threshold="季度检查覆盖率≥80%",
                scoring_method="覆盖率直接折算",
                data_required=["信贷检查计划", "检查执行记录"],
            ),
            KPIIndicator(
                name="合规与制度完善",
                weight=10.0,
                target="合规评分≥97分 | 完善制度≥2项/季度",
                threshold="合规评分≥90分",
                scoring_method="合规评分直接折算",
                data_required=["合规检查记录", "制度修订文件"],
            ),
            KPIIndicator(
                name="风险培训与宣讲",
                weight=10.0,
                target="组织培训≥4次/季度",
                threshold="组织培训≥2次/季度",
                scoring_method="完成率折算",
                data_required=["培训记录", "培训签到表"],
            ),
        ],
    )

    RISK_TELLER_KPI = KPICategory(
        dimension="柜面风控经理",
        category_weight=100.0,
        indicators=[
            KPIIndicator(
                name="柜面风险事件发生数",
                weight=25.0,
                target="季度风险事件≤1起",
                threshold="季度风险事件≤3起",
                scoring_method="达标得25分，每多1起扣5分",
                data_required=["风险事件报告", "差错处理台账"],
            ),
            KPIIndicator(
                name="合规检查覆盖率",
                weight=20.0,
                target="检查覆盖网点100%",
                threshold="检查覆盖率≥85%",
                scoring_method="覆盖率直接折算",
                data_required=["检查计划", "检查记录"],
            ),
            KPIIndicator(
                name="反洗钱识别准确率",
                weight=20.0,
                target="识别准确率≥90%",
                threshold="识别准确率≥75%",
                scoring_method="准确率直接折算",
                data_required=["反洗钱系统数据", "可疑交易报告"],
            ),
            KPIIndicator(
                name="柜员合规培训通过率",
                weight=15.0,
                target="培训通过率100%",
                threshold="培训通过率≥95%",
                scoring_method="通过率直接折算",
                data_required=["培训记录", "考试通过率统计"],
            ),
            KPIIndicator(
                name="整改落实率",
                weight=10.0,
                target="整改完成率100%",
                threshold="整改完成率≥90%",
                scoring_method="整改率直接折算",
                data_required=["整改台账", "整改验收报告"],
            ),
            KPIIndicator(
                name="内控评价评分",
                weight=10.0,
                target="评分≥97分",
                threshold="评分≥92分",
                scoring_method="评分直接折算",
                data_required=["内控评价报告"],
            ),
        ],
    )

    # ============================================================
    # 产品经理 KPI 配置
    # ============================================================

    PRODUCT_DEPOSIT_KPI = KPICategory(
        dimension="存款产品经理",
        category_weight=100.0,
        indicators=[
            KPIIndicator(
                name="存款产品创新数量",
                weight=25.0,
                target="季度创新产品≥2个",
                threshold="季度创新产品≥1个",
                scoring_method="达标得25分，每少1个扣12分",
                data_required=["产品创新立项书", "产品上线报告"],
            ),
            KPIIndicator(
                name="存款规模增长贡献",
                weight=25.0,
                target="存款增长率≥15%",
                threshold="存款增长率≥8%",
                scoring_method="增长率直接折算",
                data_required=["存款规模统计报表"],
            ),
            KPIIndicator(
                name="产品上线及时率",
                weight=15.0,
                target="项目按时上线率≥90%",
                threshold="项目按时上线率≥75%",
                scoring_method="及时率直接折算",
                data_required=["项目管理台账", "上线里程碑记录"],
            ),
            KPIIndicator(
                name="客户产品满意度",
                weight=15.0,
                target="满意度≥92分",
                threshold="满意度≥85分",
                scoring_method="满意度评分直接折算",
                data_required=["产品满意度调研报告"],
            ),
            KPIIndicator(
                name="竞品分析与定价建议",
                weight=10.0,
                target="提供定价建议≥4次/年",
                threshold="提供定价建议≥2次/年",
                scoring_method="完成率折算",
                data_required=["竞品分析报告", "定价建议文档"],
            ),
            KPIIndicator(
                name="合规与风险评估",
                weight=10.0,
                target="合规评分≥97分",
                threshold="合规评分≥90分",
                scoring_method="合规评分直接折算",
                data_required=["合规审查记录"],
            ),
        ],
    )

    PRODUCT_LOAN_KPI = KPICategory(
        dimension="贷款产品经理",
        category_weight=100.0,
        indicators=[
            KPIIndicator(
                name="贷款产品创新数量",
                weight=20.0,
                target="季度创新产品≥2个",
                threshold="季度创新产品≥1个",
                scoring_method="达标得20分，每少1个扣10分",
                data_required=["产品创新立项书", "产品上线报告"],
            ),
            KPIIndicator(
                name="贷款投放规模贡献",
                weight=25.0,
                target="贷款增长率≥20%",
                threshold="贷款增长率≥10%",
                scoring_method="增长率直接折算",
                data_required=["贷款投放统计报表"],
            ),
            KPIIndicator(
                name="不良率控制贡献",
                weight=20.0,
                target="不良率≤1.2%",
                threshold="不良率≤2.0%",
                scoring_method="达标得20分，超标按超标幅度扣分",
                data_required=["不良贷款统计报表"],
            ),
            KPIIndicator(
                name="产品上线及时率",
                weight=15.0,
                target="项目按时上线率≥90%",
                threshold="项目按时上线率≥75%",
                scoring_method="及时率直接折算",
                data_required=["项目管理台账"],
            ),
            KPIIndicator(
                name="定价与收益管理",
                weight=10.0,
                target="净息差改善≥5bp",
                threshold="净息差保持稳定",
                scoring_method="达标得10分，下降扣分",
                data_required=["FTP利差分析报告"],
            ),
            KPIIndicator(
                name="合规与风险评估",
                weight=10.0,
                target="合规评分≥97分",
                threshold="合规评分≥90分",
                scoring_method="合规评分直接折算",
                data_required=["合规审查记录"],
            ),
        ],
    )

    PRODUCT_INTERMEDIATE_KPI = KPICategory(
        dimension="中间业务产品经理",
        category_weight=100.0,
        indicators=[
            KPIIndicator(
                name="中间业务收入增长率",
                weight=30.0,
                target="中收增长率≥25%",
                threshold="中收增长率≥12%",
                scoring_method="增长率直接折算",
                data_required=["中间业务收入统计报表"],
            ),
            KPIIndicator(
                name="新产品上线数量",
                weight=20.0,
                target="季度上线≥3个产品",
                threshold="季度上线≥1个产品",
                scoring_method="达标得20分，少1个扣7分",
                data_required=["产品上线记录"],
            ),
            KPIIndicator(
                name="重点产品渗透率",
                weight=20.0,
                target="目标客群渗透率≥40%",
                threshold="目标客群渗透率≥25%",
                scoring_method="渗透率直接折算",
                data_required=["产品渗透率统计表"],
            ),
            KPIIndicator(
                name="渠道建设贡献",
                weight=15.0,
                target="新渠道上线≥2个/季度",
                threshold="新渠道上线≥1个/季度",
                scoring_method="完成率折算",
                data_required=["渠道上线记录"],
            ),
            KPIIndicator(
                name="客户满意度（产品侧）",
                weight=15.0,
                target="满意度≥93分",
                threshold="满意度≥86分",
                scoring_method="满意度直接折算",
                data_required=["产品满意度调研报告"],
            ),
        ],
    )

    # ============================================================
    # 网点负责人 KPI 配置
    # ============================================================

    BRANCH_MANAGER_KPI = KPICategory(
        dimension="支行行长/网点主任",
        category_weight=100.0,
        indicators=[
            KPIIndicator(
                name="存款规模（网点日均AUM）",
                weight=25.0,
                target="网点日均AUM增长率≥12%",
                threshold="网点日均AUM增长率≥6%",
                scoring_method="增长率直接折算",
                data_required=["网点日均存款报表", "AUM统计"],
            ),
            KPIIndicator(
                name="净利润贡献",
                weight=25.0,
                target="净利润计划完成率≥105%",
                threshold="净利润计划完成率≥95%",
                scoring_method="完成率直接折算，超目标加奖励分",
                data_required=["利润报表", "财务收支统计"],
            ),
            KPIIndicator(
                name="不良贷款率控制",
                weight=15.0,
                target="不良率≤1.2%",
                threshold="不良率≤2.0%",
                scoring_method="达标得15分，超标扣分",
                data_required=["不良贷款台账", "五级分类报表"],
            ),
            KPIIndicator(
                name="客户满意度（网点）",
                weight=10.0,
                target="网点满意度≥95分",
                threshold="网点满意度≥90分",
                scoring_method="满意度直接折算",
                data_required=["网点满意度调查汇总"],
            ),
            KPIIndicator(
                name="员工队伍建设",
                weight=10.0,
                target="员工培训覆盖率100% | 人才晋升≥1人/年",
                threshold="培训覆盖率≥90%",
                scoring_method="综合评分折算",
                data_required=["培训记录", "人员晋升档案"],
            ),
            KPIIndicator(
                name="合规内控评价",
                weight=10.0,
                target="内控评价≥A级",
                threshold="内控评价≥B级",
                scoring_method="等级直接折算",
                data_required=["内控评价报告"],
            ),
            KPIIndicator(
                name="风险案件防控",
                weight=5.0,
                target="零案件、零重大风险事件",
                threshold="无案件、有1起一般风险事件",
                scoring_method="达标得5分，出案件全扣",
                data_required=["案件防控报告"],
            ),
        ],
    )

    # ============================================================
    # 子类型 → KPI分类 映射
    # ============================================================

    SUB_TYPE_KPI_MAP = {
        "大堂客户经理": KMI_HALL_KPI,
        "对公客户经理": KMI_CORPORATE_KPI,
        "零售客户经理": KMI_RETAIL_KPI,
        "理财客户经理": KMI_WEALTH_KPI,
        "综合柜员": TELLER_KPI,
        "现金柜员": TELLER_KPI,
        "信贷风控经理": RISK_CORPORATE_KPI,
        "柜面风控经理": RISK_TELLER_KPI,
        "存款产品经理": PRODUCT_DEPOSIT_KPI,
        "贷款产品经理": PRODUCT_LOAN_KPI,
        "中间业务产品经理": PRODUCT_INTERMEDIATE_KPI,
        "支行行长": BRANCH_MANAGER_KPI,
        "网点主任": BRANCH_MANAGER_KPI,
    }

    # ============================================================
    # 通用改进建议模板
    # ============================================================

    IMPROVEMENT_SUGGESTIONS = {
        "大堂客户经理": [
            "加强厅堂联动营销，提升存款自然增长",
            "深化客户分层管理，重点维护中高端客户",
            "优化产品组合，提高客户产品持有种类",
            "强化合规意识，降低操作差错率",
        ],
        "对公客户经理": [
            "深耕存量客户，提高客户黏性和资金沉淀",
            "加强企业关联营销，拓展上下游客户链",
            "关注贷后管理，控制不良贷款率",
            "提升对公产品渗透（现金管理、供应链金融）",
        ],
        "零售客户经理": [
            "做大储蓄存款基数，优化存款结构",
            "加强个人贷款营销（消费贷、信用贷）",
            "深耕客户资产配置，提升AUM留存率",
            "强化交叉销售，提高客户持有产品种类",
        ],
        "理财客户经理": [
            "加强客户画像，精准匹配产品",
            "做大AUM基数，提升客户资产总量",
            "优化产品配置，均衡发展理财/基金/保险",
            "加强VIP客户维护，提升客户忠诚度",
        ],
        "柜员": [
            "提升业务处理效率，缩短单笔办理时长",
            "加强业务学习，减少差错率",
            "主动营销推荐，提升中收贡献",
            "强化合规操作意识，杜绝违规行为",
        ],
        "风控经理": [
            "加强贷前调查质量，从源头控制风险",
            "完善风险预警机制，提高预警准确率",
            "加强合规培训，提升全员合规意识",
            "定期梳理信贷政策，及时修订完善",
        ],
        "产品经理": [
            "加强市场调研，深入了解客户需求",
            "加快产品创新迭代，提升市场竞争力",
            "优化产品定价，提高收益水平",
            "加强跨部门协作，推动产品快速上线",
        ],
        "网点负责人": [
            "加强团队建设，提升员工专业能力",
            "优化绩效考核，充分调动员工积极性",
            "强化内控管理，坚守合规底线",
            "深耕本地市场，提升网点市场份额",
        ],
    }

    # ============================================================
    # 核心方法
    # ============================================================

    def __init__(self):
        self.supported_positions = list(self.POSITION_CONFIGS.keys())
        self.supported_periods = list(self.PERIOD_CONFIGS.keys())

    def generate(
        self,
        position: str,
        sub_type: str = None,
        period: str = "季度",
        format: str = "text",
    ) -> str | dict:
        """
        生成绩效考核方案

        Args:
            position: 岗位类型（客户经理/柜员/风控经理/产品经理/网点负责人）
            sub_type: 子类型（如零售客户经理、综合柜员等）
            period: 考核周期（季度/月度）
            format: 输出格式（text/json）

        Returns:
            str 或 dict: 考核方案
        """
        # 参数校验与标准化
        position = position.strip()
        period = period.strip()

        # 岗位校验
        if position not in self.POSITION_CONFIGS:
            return self._error_response(
                f"不支持的岗位类型：{position}。"
                f"支持的岗位：{', '.join(self.supported_positions)}"
            )

        # 子类型标准化
        if sub_type is None:
            sub_type = self.POSITION_CONFIGS[position]["default_sub"]
        sub_type = sub_type.strip()

        # 子类型校验
        valid_subs = self.POSITION_CONFIGS[position]["sub_types"]
        if sub_type not in valid_subs:
            return self._error_response(
                f"不支持的子类型：{sub_type}。"
                f"{position}支持的子类型：{', '.join(valid_subs)}"
            )

        # 周期校验
        if period not in self.PERIOD_CONFIGS:
            return self._error_response(
                f"不支持的考核周期：{period}。"
                f"支持的周期：{', '.join(self.supported_periods)}"
            )

        # 获取KPI配置
        kpi_category = self.SUB_TYPE_KPI_MAP.get(sub_type)
        if kpi_category is None:
            return self._error_response(f"未找到子类型 {sub_type} 对应的KPI配置")

        # 收集数据要求
        data_reqs = set()
        for ind in kpi_category.indicators:
            data_reqs.update(ind.data_required)

        # 获取改进建议
        # 匹配建议：优先精确匹配子类型，其次匹配岗位
        suggestions = self.IMPROVEMENT_SUGGESTIONS.get(
            sub_type,
            self.IMPROVEMENT_SUGGESTIONS.get(position, [])
        )

        # 构建结果
        result = KPIResult(
            position=position,
            sub_type=sub_type,
            period=period,
            categories=[kpi_category],
            assessment_rules=self._build_assessment_rules(period),
            data_requirements=sorted(list(data_reqs)),
            improvement_suggestions=suggestions,
        )

        if format == "json":
            return result.to_dict()
        else:
            return self._format_text(result)

    def _build_assessment_rules(self, period: str) -> str:
        """构建考核规则说明"""
        rules = (
            f"【{period}考核规则】\n"
            "1. KPI总分 = Σ（各指标得分），满分100分\n"
            "2. 各指标得分 = min(权重×完成率, 权重)，封顶权重分\n"
            "3. 完成率 = 实际值 / 目标值，上限为150%\n"
            "4. 90分及以上：优秀（A）| 80-89分：良好（B）| "
            "70-79分：合格（C）| 70分以下：不合格（D）\n"
            "5. 数据来源以考核期内各业务系统报表为准\n"
            "6. 考核结果与绩效奖金、职级晋升挂钩"
        )
        return rules

    def _format_text(self, result: KPIResult) -> str:
        """格式化输出纯文本"""
        lines = []
        lines.append("=" * 60)
        lines.append(f"  银行{result.sub_type} {result.period}绩效考核方案")
        lines.append("=" * 60)
        lines.append(f"岗位类型：{result.position} | 子类型：{result.sub_type} | "
                     f"考核周期：{result.period}")
        lines.append(f"总权重：{result.total_weight}%")
        lines.append("")

        for cat in result.categories:
            lines.append(f"【{cat.dimension}】（维度权重：{cat.category_weight}%）")
            lines.append("-" * 60)
            lines.append(f"{'指标名称':<20} {'权重':>6} {'目标值':<20} {'评分方法'}")
            lines.append("-" * 60)

            for ind in cat.indicators:
                lines.append(f"{ind.name:<20} {ind.weight:>5.1f}% {ind.target:<20} {ind.scoring_method}")
            lines.append("")

        lines.append("【考核规则】")
        lines.append(result.assessment_rules)
        lines.append("")

        lines.append("【数据要求】")
        for req in result.data_requirements:
            lines.append(f"  · {req}")
        lines.append("")

        lines.append("【改进建议】")
        for i, sug in enumerate(result.improvement_suggestions, 1):
            lines.append(f"  {i}. {sug}")
        lines.append("")
        lines.append("=" * 60)
        lines.append("  本方案由 KPI 绩效考核引擎 v1.0 自动生成")
        lines.append("=" * 60)

        return "\n".join(lines)

    def _error_response(self, message: str) -> dict:
        """错误响应"""
        return {"error": True, "message": message}

    def list_positions(self) -> dict:
        """列出所有支持的岗位"""
        return {
            "supported_positions": self.supported_positions,
            "position_configs": {
                pos: cfg["sub_types"]
                for pos, cfg in self.POSITION_CONFIGS.items()
            },
        }


# ============================================================
# 便捷函数（CLI使用）
# ============================================================

def generate_kpi(position: str, period: str = "季度", sub_type: str = None, format: str = "text"):
    """便捷生成函数"""
    engine = KPIPerformanceEngine()
    return engine.generate(
        position=position,
        sub_type=sub_type,
        period=period,
        format=format,
    )
