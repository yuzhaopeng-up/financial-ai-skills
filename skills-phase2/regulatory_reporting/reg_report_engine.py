"""
监管报送引擎 (Regulatory Reporting Engine)
支持：1104报表（银保监）、人行金融统计、金融稳定报表(GR-S)、
      EAST4.0、特殊监管报送、理财登记
"""

import re
from datetime import date, datetime
from typing import Any


class RegReportingEngine:
    """监管报送要求清单生成引擎"""

    # ─────────────────────────────────────────────
    #  报送类型元数据
    # ─────────────────────────────────────────────
    REPORT_META = {
        "1104": {
            "name": "1104非现场监管统计报表",
            "authority": "银保监会",
            "frequency": "月/季",
            "system": "银保监会1104系统",
        },
        "RPBC": {
            "name": "人民银行金融统计报送",
            "authority": "人民银行",
            "frequency": "月/季",
            "system": "人民银行金融统计监测管理系统",
        },
        "GL18": {
            "name": "人民银行金融统计报送（跨境融资GL18）",
            "authority": "人民银行",
            "frequency": "月/季",
            "system": "人民银行金融统计监测管理系统",
        },
        "GRS": {
            "name": "金融稳定报表(GR-S)",
            "authority": "人民银行金融稳定局",
            "frequency": "季",
            "system": "人民银行金融稳定分析系统",
        },
        "EAST": {
            "name": "EAST4.0监管数据标准化报送",
            "authority": "银保监会",
            "frequency": "月",
            "system": "银保监会EAST系统",
        },
        "SPECIAL": {
            "name": "特殊监管报送",
            "authority": "银保监/人民银行",
            "frequency": "按需",
            "system": "监管机构指定系统",
        },
        "WM": {
            "name": "理财登记系统报送",
            "authority": "银保监会",
            "frequency": "日/周/月",
            "system": "银行业理财信息登记系统",
        },
    }

    # ─────────────────────────────────────────────
    #  1104 报表清单
    # ─────────────────────────────────────────────
    REPORTS_1104 = {
        "2024Q1": {
            "deadline": "2024-04-30",
            "reports": [
                {
                    "code": "G01",
                    "name": "资产负债项目统计表",
                    "period": "季末",
                    "due_days": 30,
                    "data_items": [
                        "资产合计", "负债合计", "所有者权益",
                        "各项贷款余额", "同业往来", "衍生金融工具",
                    ],
                    "caliber": (
                        "按照『金融机构资产负债统计制度』口径填报。"
                        "资产项目以借方余额合计填列，负债项目以贷方余额合计填列。"
                    ),
                },
                {
                    "code": "G04",
                    "name": "利润简表",
                    "period": "季末",
                    "due_days": 30,
                    "data_items": [
                        "营业收入", "利息净收入", "手续费及佣金净收入",
                        "业务及管理费", "资产减值损失", "净利润",
                    ],
                    "caliber": (
                        "净利润=营业收入-营业支出（含税金及附加）。"
                        "营业收入包含利息净收入、手续费及佣金净收入、"
                        "投资收益、公允价值变动收益、其他收入。"
                    ),
                },
                {
                    "code": "G14",
                    "name": "大额风险暴露情况",
                    "period": "季末",
                    "due_days": 30,
                    "data_items": [
                        "最大十家客户贷款合计", "单一客户风险暴露",
                        "关联集团客户风险暴露", "行业集中度",
                    ],
                    "caliber": (
                        "依据『大额风险暴露管理办法』填报。"
                        "对同一交易对手或关联方的所有风险暴露合并计算。"
                    ),
                },
                {
                    "code": "G21",
                    "name": "流动性覆盖率",
                    "period": "季末",
                    "due_days": 30,
                    "data_items": [
                        "优质流动性资产", "未来30天净现金流出",
                        "流动性覆盖率(LCR)",
                    ],
                    "caliber": (
                        "LCR = 优质流动性资产 / 未来30天净现金流出 x 100%。"
                        "优质流动性资产不含信贷资产，限于央行备付金、国债等。"
                    ),
                },
                {
                    "code": "G22",
                    "name": "净稳定资金比例",
                    "period": "季末",
                    "due_days": 30,
                    "data_items": [
                        "可用稳定资金", "所需稳定资金",
                        "净稳定资金比例(NSFR)",
                    ],
                    "caliber": (
                        "NSFR = 可用稳定资金 / 所需稳定资金 x 100%，"
                        "监管要求不低于100%。"
                    ),
                },
            ],
            "key_indicators": [
                {"code": "LCR", "name": "流动性覆盖率", "unit": "%", "threshold": "不低于100"},
                {"code": "NSFR", "name": "净稳定资金比例", "unit": "%", "threshold": "不低于100"},
                {"code": "不良贷款率", "name": "不良贷款率", "unit": "%", "threshold": "不超过5"},
                {"code": "拨备覆盖率", "name": "贷款拨备覆盖率", "unit": "%", "threshold": "不低于150"},
                {"code": "资本充足率", "name": "资本充足率", "unit": "%", "threshold": "不低于10.5"},
            ],
            "data_sources": [
                {"system": "核心系统(ABIS)", "tables": "贷款台账、存款分户账", "description": "取数客户贷款、存款余额"},
                {"system": "会计系统", "tables": "总账科目表", "description": "取数财务收支、资产负债项目"},
                {"system": "信贷管理系统", "tables": "五级分类、风险预警", "description": "取数不良贷款、拨备计提"},
                {"system": "FTP系统", "tables": "内部资金转移价格", "description": "取数利息收支核算"},
            ],
            "common_errors": [
                {
                    "code": "E1104-001",
                    "description": "G01表中同业往来未轧差直接填报",
                    "tip": "同业资产与同业负债应分别填报，不得轧差填净值。",
                },
                {
                    "code": "E1104-002",
                    "description": "G14大额风险暴露未穿透识别最终债务人",
                    "tip": "应穿透识别匿名客户，对最大十家客户逐一填报风险暴露金额。",
                },
                {
                    "code": "E1104-003",
                    "description": "G21流动性覆盖率计算时分母漏计15-30天到期业务",
                    "tip": "未来30天净现金流出包含所有已承诺未使用额度及特定义务。",
                },
                {
                    "code": "E1104-004",
                    "description": "G04净利润与财务报表口径不一致",
                    "tip": "1104净利润不含未分配利润，应与监管报告净利润核对一致。",
                },
                {
                    "code": "E1104-005",
                    "description": "EAST数据与1104同源数据不一致",
                    "tip": "EAST采集的明细数据应与1104汇总数据保持一致，建议取数共用同一数据层。",
                },
            ],
        },
        "2024Q2": {
            "deadline": "2024-07-31",
            "reports": [
                {"code": "G01", "name": "资产负债项目统计表", "period": "季末", "due_days": 30,
                 "data_items": ["资产合计", "负债合计", "所有者权益", "各项贷款余额", "同业往来", "衍生金融工具"],
                 "caliber": "同2024Q1口径。"},
                {"code": "G04", "name": "利润简表", "period": "季末", "due_days": 30,
                 "data_items": ["营业收入", "利息净收入", "手续费及佣金净收入", "业务及管理费", "资产减值损失", "净利润"],
                 "caliber": "同2024Q1口径。"},
                {"code": "G14", "name": "大额风险暴露情况", "period": "季末", "due_days": 30,
                 "data_items": ["最大十家客户贷款合计", "单一客户风险暴露", "关联集团客户风险暴露", "行业集中度"],
                 "caliber": "同2024Q1口径。"},
                {"code": "G21", "name": "流动性覆盖率", "period": "季末", "due_days": 30,
                 "data_items": ["优质流动性资产", "未来30天净现金流出", "流动性覆盖率(LCR)"],
                 "caliber": "同2024Q1口径。"},
                {"code": "G22", "name": "净稳定资金比例", "period": "季末", "due_days": 30,
                 "data_items": ["可用稳定资金", "所需稳定资金", "净稳定资金比例(NSFR)"],
                 "caliber": "同2024Q1口径。"},
                {"code": "S67", "name": "房地产贷款专项统计表", "period": "季末", "due_days": 30,
                 "data_items": ["房地产开发贷款", "购房贷款", "保障性安居工程贷款", "房地产贷款不良率"],
                 "caliber": "按『房地产贷款统计制度』填报，需穿透到项目层级。"},
            ],
            "key_indicators": [
                {"code": "LCR", "name": "流动性覆盖率", "unit": "%", "threshold": "不低于100"},
                {"code": "NSFR", "name": "净稳定资金比例", "unit": "%", "threshold": "不低于100"},
                {"code": "不良贷款率", "name": "不良贷款率", "unit": "%", "threshold": "不超过5"},
                {"code": "拨备覆盖率", "name": "贷款拨备覆盖率", "unit": "%", "threshold": "不低于150"},
                {"code": "资本充足率", "name": "资本充足率", "unit": "%", "threshold": "不低于10.5"},
                {"code": "涉房贷款比例", "name": "房地产贷款占比", "unit": "%", "threshold": "集中度红线"},
            ],
            "data_sources": [
                {"system": "核心系统(ABIS)", "tables": "贷款台账、存款分户账", "description": "取数客户贷款、存款余额"},
                {"system": "会计系统", "tables": "总账科目表", "description": "取数财务收支、资产负债项目"},
                {"system": "信贷管理系统", "tables": "五级分类、风险预警", "description": "取数不良贷款、拨备计提"},
                {"system": "FTP系统", "tables": "内部资金转移价格", "description": "取数利息收支核算"},
                {"system": "房管系统", "tables": "开发贷项目台账", "description": "房地产开发贷款穿透项目"},
            ],
            "common_errors": [
                {"code": "E1104-001", "description": "G01表中同业往来未轧差直接填报",
                 "tip": "同业资产与同业负债应分别填报，不得轧差填净值。"},
                {"code": "E1104-002", "description": "G14大额风险暴露未穿透识别最终债务人",
                 "tip": "应穿透识别匿名客户，对最大十家客户逐一填报风险暴露金额。"},
                {"code": "E1104-006", "description": "S67房地产贷款未按项目逐笔填报",
                 "tip": "房地产开发贷款须对应具体项目，填报项目名称、面积、期限等。"},
            ],
        },
    }

    # ─────────────────────────────────────────────
    #  GR-S 金融稳定报表
    # ─────────────────────────────────────────────
    REPORTS_GRS = {
        "2024Q1": {
            "deadline": "2024-05-15",
            "reports": [
                {"code": "GR-1", "name": "金融机构资产负债表", "period": "季末", "due_days": 45,
                 "data_items": ["资产总额", "负债总额", "所有者权益", "中央银行借款", "同业往来"],
                 "caliber": "依据『金融稳定统计制度』填报，参照IMF金融稳定指标框架(FSIs)。"},
                {"code": "GR-2", "name": "金融机构利润表", "period": "季末", "due_days": 45,
                 "data_items": ["营业收入", "营业支出", "税前利润", "净利润", "ROE", "ROA"],
                 "caliber": "净利润=税前利润-所得税；ROE=净利润/所有者权益平均余额x100%。"},
                {"code": "GR-3", "name": "资本充足率统计表", "period": "季末", "due_days": 45,
                 "data_items": ["核心一级资本", "其他一级资本", "二级资本", "风险加权资产", "资本充足率", "核心一级资本充足率"],
                 "caliber": "资本充足率=(核心一级+其他一级+二级资本)/风险加权资产x100%。"},
                {"code": "GR-4", "name": "流动性风险统计表", "period": "季末", "due_days": 45,
                 "data_items": ["流动性比例", "流动性覆盖率(LCR)", "净稳定资金比例(NSFR)", "流动性缺口"],
                 "caliber": "参照巴塞尔III流动性风险监管指标。"},
                {"code": "GR-5", "name": "不良贷款统计表", "period": "季末", "due_days": 45,
                 "data_items": ["不良贷款余额", "不良贷款率", "关注类贷款", "逾期90天以上贷款", "拨备覆盖率"],
                 "caliber": "不良贷款按五级分类认定，逾期90天以上贷款原则上应划入不良。"},
            ],
            "key_indicators": [
                {"code": "资本充足率", "name": "资本充足率", "unit": "%", "threshold": "不低于10.5"},
                {"code": "核心一级资本充足率", "name": "核心一级资本充足率", "unit": "%", "threshold": "不低于8.5"},
                {"code": "不良贷款率", "name": "不良贷款率", "unit": "%", "threshold": "不超过5"},
                {"code": "拨备覆盖率", "name": "贷款拨备覆盖率", "unit": "%", "threshold": "不低于150"},
                {"code": "LCR", "name": "流动性覆盖率", "unit": "%", "threshold": "不低于100"},
                {"code": "NSFR", "name": "净稳定资金比例", "unit": "%", "threshold": "不低于100"},
            ],
            "data_sources": [
                {"system": "监管取数平台", "tables": "1104全量数据", "description": "GR-S数据从1104系统取数并按金融稳定口径加工"},
                {"system": "资本管理系统", "tables": "资本充足率计算结果", "description": "各级资本及RWA取自资本管理系统"},
            ],
            "common_errors": [
                {"code": "EG001", "description": "GR-3风险加权资产计算范围遗漏表外业务",
                 "tip": "担保承诺类表外业务须按信用转换系数折算后计入RWA。"},
                {"code": "EG002", "description": "GR-5不良贷款未包含应划未划贷款",
                 "tip": "关注类贷款中逾期90天以上须划入不良，不得人为调节分类。"},
            ],
        },
    }

    # ─────────────────────────────────────────────
    #  EAST4.0 报送要求
    # ─────────────────────────────────────────────
    REPORTS_EAST = {
        "2024Q1": {
            "deadline": "2024-04-20",
            "reports": [
                {"code": "EAST-01", "name": "个人贷款分户账", "period": "月末", "due_days": 20,
                 "data_items": ["客户号", "贷款账号", "贷款金额", "贷款余额", "到期日期", "五级分类", "月供金额"],
                 "caliber": "每笔有效个人贷款一条记录，含等额本息、等额本金及按月还息贷款。"},
                {"code": "EAST-02", "name": "对公贷款分户账", "period": "月末", "due_days": 20,
                 "data_items": ["客户号", "客户名称", "贷款账号", "贷款金额", "贷款余额", "到期日期", "行业分类", "担保方式"],
                 "caliber": "每笔有效对公贷款一条记录，需与G01关联指标保持一致。"},
                {"code": "EAST-03", "name": "卡片交易流水", "period": "月度", "due_days": 20,
                 "data_items": ["卡号", "交易日期", "交易金额", "交易类型", "商户类别", "交易对手账户"],
                 "caliber": "含借记卡、贷记卡全部消费、取现、转账交易，按月上送。"},
                {"code": "EAST-04", "name": "柜面业务流水", "period": "月度", "due_days": 20,
                 "data_items": ["交易日期", "交易时间", "柜员号", "交易类型", "交易金额", "账号", "授权柜员"],
                 "caliber": "含本行全部柜面业务，按流水上送不汇总。"},
                {"code": "EAST-05", "name": "客户信息", "period": "月末", "due_days": 20,
                 "data_items": ["客户号", "客户姓名", "证件类型", "证件号码", "性别", "出生日期", "职业", "联系方式"],
                 "caliber": "全部有效客户信息，客户号应与贷款分户账、卡片交易关联一致。"},
            ],
            "key_indicators": [
                {"code": "EAST覆盖率", "name": "EAST数据与1104数据一致率", "unit": "%", "threshold": "100%"},
                {"code": "缺失率", "name": "必填字段缺失率", "unit": "%", "threshold": "不超过0.1%"},
                {"code": "重复率", "name": "记录重复率", "unit": "%", "threshold": "不超过0.1%"},
            ],
            "data_sources": [
                {"system": "核心系统(ABIS)", "tables": "贷款分户账、存款分户账", "description": "EAST01/02主要源系统，需与1104数据一致"},
                {"system": "信用卡系统", "tables": "卡账户表、交易流水表", "description": "EAST03数据源，含本行卡及他行卡在行内交易"},
                {"system": "柜面系统(Teller)", "tables": "交易流水表", "description": "EAST04数据源，含跨系统联动交易"},
                {"system": "ECIF", "tables": "客户信息表", "description": "EAST05数据源，含对公和对私客户主数据"},
            ],
            "common_errors": [
                {"code": "EE001", "description": "EAST02对公贷款行业分类与G01不一致",
                 "tip": "EAST行业分类应与1104G01_D行业分类保持一致，建议系统自动映射。"},
                {"code": "EE002", "description": "EAST03交易流水含内部转账未剔除",
                 "tip": "银行卡交易仅上送对外交易，内部转账(本行卡互转)须剔除。"},
                {"code": "EE003", "description": "EAST05证件号码格式不合规(非18位身份证)",
                 "tip": "个人客户证件类型为身份证时须为18位，外籍人护照须保留原始格式。"},
                {"code": "EE004", "description": "EAST01/02五级分类与信贷系统分类结果不一致",
                 "tip": "EAST分类结果须取自信贷管理系统五级分类结果，不得手工维护。"},
            ],
        },
    }

    # ─────────────────────────────────────────────
    #  人民银行金融统计 (RPBC)
    # ─────────────────────────────────────────────
    REPORTS_RPBC = {
        "2024Q1": {
            "deadline": "2024-04-12",
            "reports": [
                {"code": "人民币信贷收支表", "name": "人民币信贷收支表", "period": "月末", "due_days": 12,
                 "data_items": ["各项存款", "单位存款", "个人存款", "财政存款", "各项贷款", "短期贷款", "中长期贷款"],
                 "caliber": "依据『人民银行金融统计制度』填报，资产负债双方平衡。"},
                {"code": "外币信贷收支表", "name": "外币信贷收支表", "period": "月末", "due_days": 12,
                 "data_items": ["外币存款", "外币贷款", "境外存款", "境外贷款"],
                 "caliber": "按折算人民币填报，汇率使用期末人行中间价。"},
                {"code": "GL18", "name": "跨境融资统计", "period": "月末", "due_days": 12,
                 "data_items": ["跨境融资余额", "短期跨境融资", "中长期跨境融资", "加权平均期限"],
                 "caliber": "依据『跨境融资宏观审慎管理制度』填报，余额不超过机构净资产x跨境融资杠杆率。"},
                {"code": "存款准备金", "name": "存款准备金交存情况", "period": "旬末", "due_days": 5,
                 "data_items": ["一般存款余额", "法定存款准备金", "超额存款准备金", "适用档位"],
                 "caliber": "按旬考核，日终时点余额达标，动账当期实交。"},
            ],
            "key_indicators": [
                {"code": "存款准备金率", "name": "法定存款准备金率", "unit": "%", "threshold": "按档位适用"},
                {"code": "跨境融资杠杆率", "name": "跨境融资杠杆率", "unit": "倍", "threshold": "不超过2"},
                {"code": "MPA", "name": "宏观审慎评估得分", "unit": "分", "threshold": "不低于90"},
            ],
            "data_sources": [
                {"system": "核心系统(ABIS)", "tables": "存款分户账、贷款分户账", "description": "人民币信贷收支表主数据源"},
                {"system": "外汇系统(FT系统)", "tables": "外币账户表", "description": "外币资产负债数据，含NRA账户"},
                {"system": "跨境融资系统", "tables": "跨境融资台账", "description": "GL18数据源，含保函、信贷证明等表外业务"},
                {"system": "央行会计核算系统(ACS)", "tables": "准备金账户", "description": "存款准备金交存数据源"},
            ],
            "common_errors": [
                {"code": "ER001", "description": "GL18跨境融资余额穿透关联企业重复计算",
                 "tip": "同一控制人下的关联企业跨境融资余额应合并填报。"},
                {"code": "ER002", "description": "外币信贷表汇率使用错误(非人行中间价)",
                 "tip": "外币业务统一使用人行公布的外汇中间价，不得使用自行套算汇率。"},
                {"code": "ER003", "description": "存款准备金适用档位填报错误",
                 "tip": "适用档位按上季度末一般存款余额确定，新档位自下季度起生效。"},
            ],
        },
    }

    # ─────────────────────────────────────────────
    #  理财登记 (WM)
    # ─────────────────────────────────────────────
    REPORTS_WM = {
        "2024Q1": {
            "deadline": "2024-04-05",
            "reports": [
                {"code": "WM-01", "name": "理财产品持仓余额", "period": "日末", "due_days": 5,
                 "data_items": ["产品代码", "产品名称", "客户号", "持仓份额", "持仓金额", "净值日期", "单位净值"],
                 "caliber": "每个客户每只持有产品每日一条，含申赎未确认在途资金。"},
                {"code": "WM-02", "name": "理财产品发行信息", "period": "发行后2日内", "due_days": 2,
                 "data_items": ["产品代码", "产品名称", "产品类型", "风险等级", "投资范围", "业绩比较基准", "起售金额"],
                 "caliber": "产品发行前上送登记系统，产品成立后生成登记编码。"},
                {"code": "WM-03", "name": "理财产品投资资产明细", "period": "月末", "due_days": 5,
                 "data_items": ["产品代码", "资产代码", "资产名称", "资产类型", "摊余成本", "市值", "持仓比例"],
                 "caliber": "穿透到实际底层资产，含标准化及非标债权、权益仓位。"},
            ],
            "key_indicators": [
                {"code": "净值披露率", "name": "净值披露及时率", "unit": "%", "threshold": "100%"},
                {"code": "穿透披露", "name": "底层资产穿透披露率", "unit": "%", "threshold": "不低于95%"},
            ],
            "data_sources": [
                {"system": "理财产品系统(TAMS/TA)", "tables": "份额登记、净值管理", "description": "WM-01数据源，含客户持仓、净值信息"},
                {"system": "资产管理系统", "tables": "投资交易台账", "description": "WM-03数据源，含底层资产持仓"},
            ],
            "common_errors": [
                {"code": "EW001", "description": "WM-01净值日期与实际净值日期不符",
                 "tip": "净值日期须填产品净值实际计算日，非系统处理日期。"},
                {"code": "EW002", "description": "WM-03底层资产穿透不完整(嵌套资管产品未继续穿透)",
                 "tip": "含基金、资管计划须继续穿透到底层标准化资产。"},
            ],
        },
    }

    # ─────────────────────────────────────────────
    #  特殊监管报送
    # ─────────────────────────────────────────────
    REPORTS_SPECIAL = {
        "default": {
            "deadline": "以监管通知为准",
            "reports": [
                {"code": "SPEC-01", "name": "现场检查数据", "period": "按通知", "due_days": 0,
                 "data_items": ["待定", "根据现场检查通知书确定"],
                 "caliber": "依据检查组下发数据需求清单填报。"},
            ],
            "key_indicators": [],
            "data_sources": [],
            "common_errors": [],
        },
    }

    # ─────────────────────────────────────────────
    #  主方法：生成报送要求
    # ─────────────────────────────────────────────
    def generate(self, report_type: str, period: str, api_mode: bool = False) -> dict[str, Any]:
        """
        生成指定报送类型的完整要求清单。

        Args:
            report_type: 报送类型代码，如 "1104", "GRS", "EAST", "RPBC", "WM", "SPECIAL"
            period: 报送期间，如 "2024Q1", "2024年6月", "2024年Q2"
            api_mode:  True=纯返回dict不做打印，False=同时打印摘要

        Returns:
            包含报表清单、截止日期、指标、数据源、常见错误的完整字典
        """
        # 规范化输入
        rt = report_type.strip().upper()
        period_normalized = self._normalize_period(period)

        # 获取元数据
        meta = self.REPORT_META.get(rt, {
            "name": report_type,
            "authority": "未知",
            "frequency": "未知",
            "system": "未知",
        })

        # 获取报表数据
        report_data = self._get_reports(rt, period_normalized)

        result = {
            "report_type": rt,
            "period": period_normalized,
            "meta": meta,
            "deadline": report_data.get("deadline", "待定"),
            "reports": report_data.get("reports", []),
            "key_indicators": report_data.get("key_indicators", []),
            "data_sources": report_data.get("data_sources", []),
            "common_errors": report_data.get("common_errors", []),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        if not api_mode:
            self._print_summary(result)

        return result

    # ─────────────────────────────────────────────
    #  列表所有支持类型
    # ─────────────────────────────────────────────
    def list_types(self) -> list[dict[str, str]]:
        """返回所有支持的报送类型列表。"""
        return [
            {"code": code, "name": meta["name"], "authority": meta["authority"]}
            for code, meta in self.REPORT_META.items()
        ]

    # ─────────────────────────────────────────────
    #  内部方法
    # ─────────────────────────────────────────────
    def _normalize_period(self, period: str) -> str:
        """将各种中文期间格式标准化为内部格式。"""
        p = period.strip()

        # "2024年Q1" -> "2024Q1"
        q_match = re.match(r"(\d{4})年Q([1-4])", p)
        if q_match:
            return f"{q_match.group(1)}Q{q_match.group(2)}"

        # "2024年6月" -> "2024年6月"
        m_match = re.match(r"(\d{4})年(\d{1,2})月", p)
        if m_match:
            return f"{m_match.group(1)}年{m_match.group(2)}月"

        # "2024-Q1" -> "2024Q1"
        dash_match = re.match(r"(\d{4})-Q([1-4])", p)
        if dash_match:
            return f"{dash_match.group(1)}Q{dash_match.group(2)}"

        # 已经是 "2024Q1" 格式就直接返回
        if re.match(r"\d{4}Q[1-4]", p):
            return p

        return p

    def _get_reports(self, report_type: str, period: str) -> dict:
        """根据报送类型和期间获取报表清单。"""
        if report_type == "1104":
            year_match = re.match(r"(\d{4})Q[1-4]", period)
            if year_match:
                year = year_match.group(1)
                for q in ["2024Q1", "2024Q2"]:
                    if q.startswith(year):
                        return self.REPORTS_1104.get(q, {})
            return self.REPORTS_1104.get(period, self.REPORTS_1104.get("2024Q1", {}))

        if report_type in ("GRS", "GR-S"):
            return self.REPORTS_GRS.get(period, self.REPORTS_GRS.get("2024Q1", {}))

        if report_type == "EAST":
            return self.REPORTS_EAST.get(period, self.REPORTS_EAST.get("2024Q1", {}))

        if report_type in ("RPBC", "GL"):
            return self.REPORTS_RPBC.get(period, self.REPORTS_RPBC.get("2024Q1", {}))

        if report_type == "WM":
            return self.REPORTS_WM.get(period, self.REPORTS_WM.get("2024Q1", {}))

        if report_type == "SPECIAL":
            return self.REPORTS_SPECIAL.get("default", {})

        return {}

    def _print_summary(self, result: dict) -> None:
        """打印结果摘要到 stdout。"""
        print(f"\n{'='*60}")
        print(f"  监管报送要求清单")
        print(f"{'='*60}")
        print(f"  报送类型: [{result['report_type']}] {result['meta']['name']}")
        print(f"  监管机构: {result['meta']['authority']}")
        print(f"  报送期间: {result['period']}")
        print(f"  截止日期: {result['deadline']}")
        print(f"  数据来源: {result['meta']['system']}")
        print(f"{'='*60}")

        if result["reports"]:
            print(f"\n📋 报表清单 ({len(result['reports'])} 张)")
            print(f"  {'代码':<10} {'报表名称':<30} {'期间':<8} {'截止天数':<8}")
            print(f"  {'-'*10} {'-'*30} {'-'*8} {'-'*8}")
            for r in result["reports"]:
                print(f"  {r['code']:<10} {r['name']:<30} {r['period']:<8} {r['due_days']:<8}")

        if result["key_indicators"]:
            print(f"\n📊 关键监管指标 ({len(result['key_indicators'])} 项)")
            for ind in result["key_indicators"]:
                print(f"  * {ind['name']} ({ind['code']}): {ind['unit']}  监管要求: {ind['threshold']}")

        if result["data_sources"]:
            print(f"\n💾 数据来源系统 ({len(result['data_sources'])} 个)")
            for ds in result["data_sources"]:
                print(f"  * {ds['system']}: {ds['tables']}")
                print(f"    -> {ds['description']}")

        if result["common_errors"]:
            print(f"\n⚠️  常见错误 ({len(result['common_errors'])} 条)")
            for err in result["common_errors"]:
                print(f"  [{err['code']}] {err['description']}")
                print(f"      核查建议: {err['tip']}")

        print(f"\n  生成时间: {result['generated_at']}")
        print(f"{'='*60}\n")
