"""
合规培训引擎 (Compliance Training Engine)

根据岗位类型/部门/培训主题/时长要求，生成完整的合规培训方案。
"""

import json
import random
from dataclasses import dataclass, field
from typing import Any


# ===== 培训主题库 =====
TRAINING_TOPICS = {
    "销售合规": {
        "name": "销售合规",
        "regulations": [
            "《证券期货投资者适当性管理办法》",
            "《证券公司经纪业务规范》",
            "《商业银行理财产品销售管理办法》",
            "《证券投资基金销售管理办法》",
        ],
        "key_points": [
            "投资者适当性管理：了解你的客户（KYC），风险等级匹配",
            "产品销售合规：三适当原则（适当的产品卖给适当的投资者）",
            "信息披露义务：真实、准确、完整、及时",
            "禁止虚假宣传和误导销售",
            "客户资料保密与信息安全管理",
        ],
        "violation_consequences": [
            "警告、罚款（最高5000万元）",
            "暂停业务资格",
            "吊销业务牌照",
            "市场禁入",
            "刑事责任（欺诈发行、非法集资等）",
        ],
    },
    "反洗钱": {
        "name": "反洗钱",
        "regulations": [
            "《中华人民共和国反洗钱法》",
            "《金融机构反洗钱规定》",
            "《金融机构大额交易和可疑交易报告管理办法》",
            "《证券期货业反洗钱工作实施办法》",
        ],
        "key_points": [
            "客户身份识别（KYC）：核实客户身份，了解资金来源",
            "大额交易报告：单笔50万元以上即时报告",
            "可疑交易识别：15类可疑交易特征",
            "名单监控：制裁名单、高风险名单实时筛查",
            "跨境资金流动监控",
        ],
        "violation_consequences": [
            "反洗钱行政处罚（最高5000万元）",
            "中国人民银行/银保监会监管谈话",
            "暂停新业务",
            "高级管理人员问责",
            "涉及洗钱罪的刑事责任（最高死刑）",
        ],
    },
    "信息安全": {
        "name": "信息安全",
        "regulations": [
            "《中华人民共和国网络安全法》",
            "《证券期货业信息系统信息安全保护管理办法》",
            "《金融机构信息科技风险管理指引》",
            "《个人信息保护法》",
        ],
        "key_points": [
            "客户信息保护：非必要不收集、不泄露、不滥用",
            "网络安全防护：边界安全、入侵检测、漏洞管理",
            "数据分类分级：敏感数据加密存储",
            "访问控制：最小权限原则",
            "应急响应：制定并演练信息安全事件应急预案",
        ],
        "violation_consequences": [
            "网络安全等级保护处罚",
            "个人信息泄露民事赔偿（最高5000万元）",
            "停业整顿",
            "相关责任人员行政处罚",
            "泄露商业秘密的刑事责任",
        ],
    },
    "消费者权益保护": {
        "name": "消费者权益保护",
        "regulations": [
            "《中华人民共和国消费者权益保护法》",
            "《银行业消费者权益保护办法》",
            "《证券期货投资者保护基金管理办法》",
            "《金融消费者权益保护实施办法》",
        ],
        "key_points": [
            "知情权保障：充分揭示产品风险",
            "自主选择权：不得强制搭售",
            "公平交易权：禁止歧视性定价",
            "财产安全权：客户资金隔离存放",
            "投诉处理：建立投诉响应机制，限时处理",
        ],
        "violation_consequences": [
            "监管机构行政处罚",
            "消费者投诉激增",
            "民事赔偿责任",
            "声誉风险",
            "业务受限",
        ],
    },
    "关联交易": {
        "name": "关联交易",
        "regulations": [
            "《上市公司信息披露管理办法》",
            "《上市公司关联交易实施指引》",
            "《商业银行与内部人和股东关联交易管理办法》",
            "《公司法》关联交易相关条款",
        ],
        "key_points": [
            "关联交易定义与类型识别",
            "关联关系披露：关联方识别与登记",
            "关联交易审议程序：关联董事/股东回避表决",
            "定价公允性：关联交易价格须公允",
            "信息披露要求：及时、完整、准确披露",
        ],
        "violation_consequences": [
            "行政处罚（警告、罚款）",
            "关联交易无效",
            "损害赔偿",
            "退市风险警示",
            "实际控制人、董事/高管问责",
        ],
    },
    "内幕交易": {
        "name": "内幕交易",
        "regulations": [
            "《中华人民共和国证券法》内幕交易条款",
            "《上市公司信息披露管理办法》",
            "《内幕交易防控办法》",
            "《老鼠仓相关司法解释》",
        ],
        "key_points": [
            "内幕信息界定：重大未公开信息",
            "内幕信息知情人：董监高、投行人员、监管人员等",
            "禁止行为：内幕交易、泄露内幕信息、建议他人买卖",
            "窗口期交易限制：定期报告、业绩预告等敏感期",
            "员工持股与股票交易申报",
        ],
        "violation_consequences": [
            "行政处罚：没收违法所得，罚款（最高10倍违法所得）",
            "市场禁入（最长终身）",
            "刑事责任：内幕交易罪（最高10年有期徒刑）",
            "民事赔偿责任",
            "公司声誉严重受损",
        ],
    },
}

# ===== 案例库 =====
CASE_LIBRARY = {
    "销售合规": [
        {
            "case_id": "CASE-2021-001",
            "title": "某券商客户经理诱导老年投资者购买高风险基金案",
            "summary": "某券商客户经理在销售基金产品时，未对老年投资者进行适当性评估，诱导其将养老储蓄全部购买股票型基金，该基金随后发生大幅亏损。",
            "violation": "违反投资者适当性管理规定，向风险承受能力不匹配的客户销售高风险产品。",
            "penalty": "对该客户经理给予警告，并处罚款3万元；对该券商采取监管警示措施，责令整改。",
        },
        {
            "case_id": "CASE-2020-015",
            "title": "某银行虚假宣传理财产品预期收益案",
            "summary": "某银行在理财产品销售过程中，通过海报、宣传折页口头宣称'保本保息'、'年化收益12%'，实际产品为非保本浮动收益型。",
            "violation": "虚假宣传、误导销售，未向投资者充分揭示产品风险。",
            "penalty": "银保监局对该银行罚款50万元，对直接责任人警告并罚款5万元。",
        },
        {
            "case_id": "CASE-2019-008",
            "title": "某基金销售公司代客操作账户案",
            "summary": "某基金销售公司员工接受客户委托，在客户账户中代为买卖基金，并约定分享收益。",
            "violation": "代客理财，违反销售从业人员行为规范。",
            "penalty": "对该公司采取暂停新业务3个月措施，对责任人解除劳动合同并报行业协会记入黑名单。",
        },
    ],
    "反洗钱": [
        {
            "case_id": "AML-2022-003",
            "title": "某农商行对公账户涉嫌分拆交易规避大额报告案",
            "summary": "某企业对公账户在短期内发生数十笔49万元交易，合计金额超过5000万元，交易时间分散在多个工作日，明显存在分拆交易特征。",
            "violation": "未按规定识别和报告可疑交易，故意规避大额交易报告义务。",
            "penalty": "人民银行对该银行罚款200万元，对相关责任人员罚款5万元，暂停该行业务准入6个月。",
        },
        {
            "case_id": "AML-2021-007",
            "title": "某券商客户身份识别不到位导致账户被用于洗钱案",
            "summary": "某券商在开户过程中未有效核实客户身份信息，客户利用他人身份证件开户并从事洗钱活动。",
            "violation": "客户身份识别制度执行不到位，违反反洗钱客户尽职调查要求。",
            "penalty": "证监会对该券商罚款100万元，责令其对全部客户重新进行身份核实，暂停新开户业务1个月。",
        },
    ],
    "信息安全": [
        {
            "case_id": "INFO-2023-001",
            "title": "某保险公司客户信息泄露案",
            "summary": "某保险公司因内部员工非法出售客户信息，导致数万条客户个人信息泄露，在暗网流通。",
            "violation": "未有效履行客户信息保护义务，内部人员违规泄露个人信息。",
            "penalty": "银保监局对该公司罚款500万元，责令整改并对相关责任人员给予纪律处分，泄露信息员工被追究刑事责任。",
        },
        {
            "case_id": "INFO-2022-005",
            "title": "某券商交易系统被黑客入侵案",
            "summary": "某券商因网络安全防护不到位，交易系统被黑客入侵，部分客户交易数据被篡改，造成客户经济损失。",
            "violation": "信息系统安全保护措施不力，未能有效防范网络攻击。",
            "penalty": "证监会对该券商罚款300万元，责令加强网络安全建设，对直接责任人严肃追责。",
        },
    ],
    "消费者权益保护": [
        {
            "case_id": "CON-2022-008",
            "title": "某银行捆绑销售贷款产品案",
            "summary": "某银行在发放个人贷款时，要求客户必须购买其代销的保险产品，否则不予贷款或提高贷款利率。",
            "violation": "强制捆绑销售，侵犯消费者自主选择权。",
            "penalty": "银保监局对该银行罚款100万元，责令退还违规收费，对相关责任人给予纪律处分。",
        },
    ],
    "关联交易": [
        {
            "case_id": "REL-2021-012",
            "title": "某上市公司关联交易未披露案",
            "summary": "某上市公司与其实际控制人控制的企业发生关联交易，金额占净资产的15%，但未履行关联交易审议程序和披露义务。",
            "violation": "关联交易未履行审议程序和信息披露义务，违反上市公司治理要求。",
            "penalty": "证监会对该公司采取出具警示函措施，对实际控制人、董事长予以通报批评，责令整改。",
        },
    ],
    "内幕交易": [
        {
            "case_id": "INS-2022-001",
            "title": "某上市公司董事长内幕交易案",
            "summary": "某上市公司董事长在公司重大资产重组停牌前，利用其内幕信息账户买入该公司股票，获利约800万元。",
            "violation": "内幕交易，违反证券法禁止内幕交易规定。",
            "penalty": "证监会没收违法所得800万元，并处以4000万元罚款，对该董事长采取10年市场禁入措施，移送司法机关追究刑事责任。",
        },
        {
            "case_id": "INS-2020-003",
            "title": "某券商保荐代表人泄露内幕信息案",
            "summary": "某券商保荐代表人在企业IPO辅导过程中知悉重大未披露信息后，向其朋友泄露，导致他人交易该公司股票。",
            "violation": "泄露内幕信息，违反证券法。",
            "penalty": "证监会对该保代人罚款200万元，取消其保荐代表人资格，10年不得从事证券业务，移送公安机关。",
        },
    ],
}

# ===== 测试题库 =====
QUESTION_BANK = {
    "销售合规": [
        {
            "id": 1,
            "question": "根据《证券期货投资者适当性管理办法》，经营机构向投资者销售产品或提供服务时，应当做到（）",
            "options": [
                "A. 适当的产品卖给适当的投资者",
                "B. 越高收益的产品越好",
                "C. 客户要求什么就卖什么",
                "D. 完成任务最重要"
            ],
            "answer": "A",
            "explanation": "适当性管理的核心原则是将适当的产品销售给适当的投资者，实现风险匹配。"
        },
        {
            "id": 2,
            "question": "以下哪种行为违反了销售合规要求？",
            "options": [
                "A. 对客户进行风险评估",
                "B. 推荐与客户风险等级匹配的产品",
                "C. 向老年投资者夸大产品收益，隐瞒风险",
                "D. 告知客户产品的主要风险"
            ],
            "answer": "C",
            "explanation": "向投资者夸大收益、隐瞒风险属于虚假宣传和误导销售，严重违反销售合规要求。"
        },
        {
            "id": 3,
            "question": "投资者适当性管理中，'KYC'是指？",
            "options": [
                "A. 了解你的客户（Know Your Customer）",
                "B. 了解你的产品（Know Your Product）",
                "C. 了解市场（Know the Market）",
                "D. 知识储备（Knowledge储备）"
            ],
            "answer": "A",
            "explanation": "KYC是'了解你的客户'（Know Your Customer）的缩写，是投资者适当性管理的基础环节。"
        },
        {
            "id": 4,
            "question": "以下哪项是理财产品销售必须告知投资者的内容？",
            "options": [
                "A. 产品的历史最高收益",
                "B. 产品的风险等级和最坏情形",
                "C. 银行员工的个人业绩",
                "D. 其他客户的收益情况"
            ],
            "answer": "B",
            "explanation": "销售理财产品时，必须向投资者充分揭示产品风险，包括风险等级和最坏情形下的损失。"
        },
        {
            "id": 5,
            "question": "客户风险等级为C3（稳健型），以下哪类产品适合推荐？",
            "options": [
                "A. 高风险股票型基金",
                "B. 中等风险混合型产品",
                "C. 保本型固定收益产品",
                "D. 所有产品都可以推荐"
            ],
            "answer": "B",
            "explanation": "C3（稳健型）投资者适合购买中等风险产品，不应推荐高风险或超出其风险承受能力的产品。"
        },
        {
            "id": 6,
            "question": "代客理财的禁止性规定主要依据是？",
            "options": [
                "A. 《证券法》",
                "B. 《证券公司经纪业务规范》",
                "C. 《刑法》",
                "D. 以上全部"
            ],
            "answer": "D",
            "explanation": "代客理财涉及多项法律法规，包括《证券法》禁止性规定、《经纪业务规范》以及《刑法》相关条款。"
        },
        {
            "id": 7,
            "question": "以下哪种情况需要客户重新进行风险评估？",
            "options": [
                "A. 客户联系方式变更",
                "B. 客户超过一年未购买产品",
                "C. 客户年龄超过70岁",
                "D. 客户居住地址变更"
            ],
            "answer": "B",
            "explanation": "根据适当性管理要求，投资者情况变化或长期未交易后重新购买产品时，需重新评估风险承受能力。"
        },
        {
            "id": 8,
            "question": "基金销售机构在销售货币基金时，以下做法正确的是？",
            "options": [
                "A. 承诺保本，承诺收益",
                "B. 宣传货币基金历史上从未亏损",
                "C. 告知客户货币基金风险较低但仍存在亏损可能",
                "D. 强调货币基金可以替代银行存款"
            ],
            "answer": "C",
            "explanation": "任何理财产品都存在风险，销售时应客观介绍，货币基金虽风险较低但也存在亏损可能。"
        },
        {
            "id": 9,
            "question": "向个人投资者销售集合资产管理计划时，正确的做法是？",
            "options": [
                "A. 仅向合规投资者销售",
                "B. 向所有投资者销售",
                "C. 向资产超过一定金额的投资者销售",
                "D. 向有专业背景的投资者销售"
            ],
            "answer": "A",
            "explanation": "集合资产管理计划属于私募产品，只能向合规投资者销售。"
        },
        {
            "id": 10,
            "question": "销售人员在完成产品销售后，发现适当性管理存在瑕疵，正确的处理方式是？",
            "options": [
                "A. 隐瞒问题，继续持有",
                "B. 主动向公司报告并及时纠正",
                "C. 等客户投诉再处理",
                "D. 转移客户资料"
            ],
            "answer": "B",
            "explanation": "发现合规问题应主动报告并纠正，这是从业人员的合规义务，也是保护自身和公司利益的重要措施。"
        },
    ],
    "反洗钱": [
        {
            "id": 1,
            "question": "大额交易报告的标准是：单笔交易金额达到多少以上？",
            "options": [
                "A. 10万元人民币",
                "B. 20万元人民币",
                "C. 50万元人民币",
                "D. 100万元人民币"
            ],
            "answer": "C",
            "explanation": "根据规定，单笔50万元以上的现金交易和20万元以上的跨境交易需要报告。"
        },
        {
            "id": 2,
            "question": "客户身份识别的'了解你的客户'原则，英文缩写是？",
            "options": [
                "A. KYP",
                "B. KYC",
                "C. KYB",
                "D. KYT"
            ],
            "answer": "B",
            "explanation": "KYC是'了解你的客户'（Know Your Customer）的缩写，是反洗钱的基础工作。"
        },
        {
            "id": 3,
            "question": "以下哪项不属于可疑交易特征？",
            "options": [
                "A. 资金分散转入、集中转出",
                "B. 正常的企业经营收支",
                "C. 频繁开户销户",
                "D. 短期内的巨额资金流动"
            ],
            "answer": "B",
            "explanation": "正常的企业经营收支是合法交易，不是可疑交易特征。可疑交易通常具有异常性和刻意规避监管的特征。"
        },
        {
            "id": 4,
            "question": "反洗钱工作中，'名单监控'主要监控哪些名单？",
            "options": [
                "A. 所有客户名单",
                "B. 制裁名单、高风险名单",
                "C. 普通客户名单",
                "D. 潜在客户名单"
            ],
            "answer": "B",
            "explanation": "名单监控主要针对制裁名单（如联合国、OFAC等）和高风险名单进行实时筛查。"
        },
        {
            "id": 5,
            "question": "客户无法提供身份证明文件时，金融机构应如何处理？",
            "options": [
                "A. 先办理业务，后续补交",
                "B. 拒绝建立业务关系",
                "C. 可以办理低风险业务",
                "D. 由客户口头承诺即可"
            ],
            "answer": "B",
            "explanation": "客户身份识别是法定义务，无法提供有效身份证明的，应拒绝建立业务关系。"
        },
        {
            "id": 6,
            "question": "以下哪种行为可能涉嫌洗钱？",
            "options": [
                "A. 朋友之间转账",
                "B. 将大额现金分散存入多个账户",
                "C. 正常工资发放",
                "D. 银行转账支付货款"
            ],
            "answer": "B",
            "explanation": "将大额现金分散存入多个账户（化整为零）是典型的疑似洗钱行为，涉嫌规避大额交易报告。"
        },
        {
            "id": 7,
            "question": "反洗钱可疑交易报告的提交对象是？",
            "options": [
                "A. 公安机关",
                "B. 人民银行反洗钱监测分析中心",
                "C. 银保监会",
                "D. 人民法院"
            ],
            "answer": "B",
            "explanation": "金融机构应向中国人民银行反洗钱监测分析中心提交可疑交易报告。"
        },
        {
            "id": 8,
            "question": "客户身份资料和交易记录的保存期限是？",
            "options": [
                "A. 1年",
                "B. 3年",
                "C. 5年",
                "D. 长期保存"
            ],
            "answer": "C",
            "explanation": "根据规定，客户身份资料和交易记录应保存不少于5年。"
        },
        {
            "id": 9,
            "question": "信托公司反洗钱工作的直接监管机构是？",
            "options": [
                "A. 人民银行",
                "B. 银保监会",
                "C. 证监会",
                "D. 外汇管理局"
            ],
            "answer": "A",
            "explanation": "人民银行是反洗钱工作的行政主管部门，对金融机构反洗钱工作实施监管。"
        },
        {
            "id": 10,
            "question": "员工发现客户可能涉及洗钱活动时，正确的做法是？",
            "options": [
                "A. 立即报警",
                "B. 在内部报告后，配合反洗钱部门调查",
                "C. 通知客户",
                "D. 假装不知道"
            ],
            "answer": "B",
            "explanation": "发现可疑交易应首先内部报告，由反洗钱部门评估后决定是否提交可疑交易报告，不应擅自行动。"
        },
    ],
    "信息安全": [
        {
            "id": 1,
            "question": "根据《个人信息保护法》，个人信息的处理原则不包括哪项？",
            "options": [
                "A. 合法性",
                "B. 正当性",
                "C. 必要性",
                "D. 盈利性"
            ],
            "answer": "D",
            "explanation": "《个人信息保护法》规定处理个人信息应遵循合法、正当、必要和诚信原则，不得通过误导、欺诈等方式处理。"
        },
        {
            "id": 2,
            "question": "网络安全等级保护2.0中，第三级系统每年至少进行几次测评？",
            "options": [
                "A. 每年一次",
                "B. 每半年一次",
                "C. 每两年一次",
                "D. 不需要测评"
            ],
            "answer": "A",
            "explanation": "第三级信息系统每年至少进行一次等级测评。"
        },
        {
            "id": 3,
            "question": "以下哪项不是数据分类分级的正确原则？",
            "options": [
                "A. 敏感数据优先保护",
                "B. 所有数据采用相同保护措施",
                "C. 根据泄露影响确定级别",
                "D. 动态调整分类分级"
            ],
            "answer": "B",
            "explanation": "数据分类分级应依据数据的重要性和敏感程度采取差异化保护措施，不应一刀切。"
        },
        {
            "id": 4,
            "question": "访问控制应遵循什么原则？",
            "options": [
                "A. 最大化授权原则",
                "B. 最小权限原则",
                "C. 按需接近原则",
                "D. 便利性原则"
            ],
            "answer": "B",
            "explanation": "最小权限原则是信息安全基本原则，指用户只能获得完成工作所需的最少访问权限。"
        },
        {
            "id": 5,
            "question": "发现信息系统被入侵后，第一步应该做什么？",
            "options": [
                "A. 立即通知黑客",
                "B. 启动应急响应预案",
                "C. 继续观察",
                "D. 关闭所有系统"
            ],
            "answer": "B",
            "explanation": "发现安全事件后应立即启动应急响应预案，按照预定流程进行处置和报告。"
        },
        {
            "id": 6,
            "question": "客户信息泄露后，金融机构的主要义务不包括？",
            "options": [
                "A. 通知受影响客户",
                "B. 立即删除所有数据",
                "C. 采取补救措施",
                "D. 向监管部门报告"
            ],
            "answer": "B",
            "explanation": "发生信息泄露时，应通知客户、采取补救措施并报告监管机构，而不是立即删除所有数据（需保留证据）。"
        },
        {
            "id": 7,
            "question": "密码设置的最佳实践是？",
            "options": [
                "A. 使用简单易记的密码",
                "B. 多个系统使用相同密码",
                "C. 定期更换密码，使用强密码",
                "D. 将密码写在纸上"
            ],
            "answer": "C",
            "explanation": "强密码应包含大小写字母、数字和特殊字符，且应定期更换，避免在多个系统使用相同密码。"
        },
        {
            "id": 8,
            "question": "社会工程学攻击主要利用的是什么？",
            "options": [
                "A. 系统漏洞",
                "B. 人的心理弱点",
                "C. 网络协议缺陷",
                "D. 加密算法弱点"
            ],
            "answer": "B",
            "explanation": "社会工程学攻击主要利用人性的弱点，如信任、好奇、恐惧等，通过人际互动获取信息或权限。"
        },
        {
            "id": 9,
            "question": "移动存储介质（如U盘）使用规范正确的是？",
            "options": [
                "A. 在任何电脑上随意使用",
                "B. 只在内部授权设备间使用，定期杀毒",
                "C. 交叉使用以提高效率",
                "D. 无需管理"
            ],
            "answer": "B",
            "explanation": "移动存储介质应在授权设备间使用，定期进行病毒查杀，避免交叉使用带来的安全风险。"
        },
        {
            "id": 10,
            "question": "信息安全事件应急预案不包括以下哪个阶段？",
            "options": [
                "A. 预防阶段",
                "B. 处置阶段",
                "C. 善后阶段",
                "D. 创收阶段"
            ],
            "answer": "D",
            "explanation": "应急预案应包括预防、监测、处置和善后等阶段，不包括创收阶段。"
        },
    ],
    "消费者权益保护": [
        {
            "id": 1,
            "question": "金融消费者的'知情权'是指？",
            "options": [
                "A. 金融机构知情权",
                "B. 消费者有权了解产品或服务的真实情况",
                "C. 消费者无需了解产品信息",
                "D. 金融机构可以保留信息"
            ],
            "answer": "B",
            "explanation": "知情权是金融消费者的基本权利，指消费者有权知悉其购买、使用的产品或服务的真实情况。"
        },
        {
            "id": 2,
            "question": "以下哪种行为侵犯了消费者的自主选择权？",
            "options": [
                "A. 提供多种产品供选择",
                "B. 强制搭售保险产品",
                "C. 说明产品特点",
                "D. 告知风险"
            ],
            "answer": "B",
            "explanation": "强制搭售产品侵犯了消费者的自主选择权，消费者有权自主选择金融机构和产品。"
        },
        {
            "id": 3,
            "question": "金融机构处理消费者投诉的时限要求是？",
            "options": [
                "A. 无时间限制",
                "B. 尽快处理即可",
                "C. 一般不超过15个工作日",
                "D. 30分钟内"
            ],
            "answer": "C",
            "explanation": "根据规定，金融机构应建立投诉处理制度，一般投诉应在15个工作日内处理完毕。"
        },
        {
            "id": 4,
            "question": "以下哪项不是消费者的基本权利？",
            "options": [
                "A. 知情权",
                "B. 选择权",
                "C. 强制交易权",
                "D. 安全权"
            ],
            "answer": "C",
            "explanation": "消费者权益保护法保护知情权、选择权、安全权、公平交易权等，强制交易权不是消费者权利而是侵权行为。"
        },
        {
            "id": 5,
            "question": "客户投诉处理流程中，首先应该做什么？",
            "options": [
                "A. 推卸责任",
                "B. 记录投诉内容，安抚客户情绪",
                "C. 拒绝受理",
                "D. 置之不理"
            ],
            "answer": "B",
            "explanation": "处理投诉首先应认真记录投诉内容，耐心倾听并安抚客户情绪，然后按流程处理。"
        },
        {
            "id": 6,
            "question": "'适当性原则'在消费者权益保护中的含义是？",
            "options": [
                "A. 消费者应该适应金融机构",
                "B. 金融机构应将适当的产品和服务销售给适当的消费者",
                "C. 消费者必须购买所有产品",
                "D. 金融机构可以任意选择客户"
            ],
            "answer": "B",
            "explanation": "适当性原则要求金融机构了解消费者，评估其风险承受能力，推荐与其相匹配的产品和服务。"
        },
        {
            "id": 7,
            "question": "金融机构应当在哪里公示服务价格信息？",
            "options": [
                "A. 仅内部保存",
                "B. 营业场所醒目位置和官方网站",
                "C. 仅在合同中约定",
                "D. 无需公示"
            ],
            "answer": "B",
            "explanation": "金融机构应在营业场所醒目位置和官方网站公示收费项目和标准，保障消费者知情权。"
        },
        {
            "id": 8,
            "question": "消费者因金融机构误导销售受损，能否要求赔偿？",
            "options": [
                "A. 不能",
                "B. 可以",
                "C. 只有老年人可以",
                "D. 仅限VIP客户"
            ],
            "answer": "B",
            "explanation": "消费者因误导销售等侵权行为受损，有权要求金融机构依法承担赔偿责任。"
        },
        {
            "id": 9,
            "question": "以下哪种宣传行为是违规的？",
            "options": [
                "A. 客观介绍产品特点和风险",
                "B. 承诺保本保收益",
                "C. 列举历史业绩",
                "D. 说明产品起购金额"
            ],
            "answer": "B",
            "explanation": "理财产品不得宣传或承诺保本保收益，这是违规行为，会误导消费者。"
        },
        {
            "id": 10,
            "question": "金融机构在代理销售产品时，正确的做法是？",
            "options": [
                "A. 不需要告知是代理销售",
                "B. 不需要对产品进行尽职调查",
                "C. 应明确告知是代理销售，并进行必要的尽职调查",
                "D. 可以夸大产品收益"
            ],
            "answer": "C",
            "explanation": "代理销售时，金融机构应明确告知消费者产品来源和自身责任，对产品进行必要的尽职调查。"
        },
    ],
    "关联交易": [
        {
            "id": 1,
            "question": "关联交易的定义中，以下哪项不属于关联方？",
            "options": [
                "A. 控股股东",
                "B. 董监高",
                "C. 陌生人",
                "D. 控股股东控制的企业"
            ],
            "answer": "C",
            "explanation": "关联方包括控股股东、董监高及其控制或施加重大影响的企业等，陌生人不是关联方。"
        },
        {
            "id": 2,
            "question": "上市公司关联交易必须履行的程序是？",
            "options": [
                "A. 无需特别程序",
                "B. 关联董事回避表决，独立董事认可",
                "C. 仅需董事长批准",
                "D. 只需董事会秘书知道即可"
            ],
            "answer": "B",
            "explanation": "关联交易需经关联董事回避表决，独立董事事前认可并发表独立意见。"
        },
        {
            "id": 3,
            "question": "关联交易定价应遵循什么原则？",
            "options": [
                "A. 成本最低原则",
                "B. 公允原则",
                "C. 一方决定原则",
                "D. 越低越好原则"
            ],
            "answer": "B",
            "explanation": "关联交易定价应当公允，参考市场价格或独立第三方价格，不得偏离正常范围。"
        },
        {
            "id": 4,
            "question": "未按规定披露关联交易会受到什么处罚？",
            "options": [
                "A. 没有处罚",
                "B. 警告、罚款、责令改正",
                "C. 仅需道歉",
                "D. 仅需补披露"
            ],
            "answer": "B",
            "explanation": "未按规定披露关联交易违反了信息披露规定，监管机构可对公司及责任人采取警告、罚款等措施。"
        },
        {
            "id": 5,
            "question": "商业银行与关联方之间的单笔交易金额超过多少需要按照关联交易程序审批？",
            "options": [
                "A. 10万元",
                "B. 一级资本净额0.5%以上或500万元",
                "C. 1亿元",
                "D. 由行长决定"
            ],
            "answer": "B",
            "explanation": "商业银行关联交易管理办法规定，达到一定比例或金额的交易需按关联交易程序审批。"
        },
        {
            "id": 6,
            "question": "以下哪种情况可以不认定为关联交易？",
            "options": [
                "A. 与控股股东的交易",
                "B. 与独立董事的交易",
                "C. 独立董事不知情的交易",
                "D. 与非关联方开展的正常业务"
            ],
            "answer": "D",
            "explanation": "与非关联方开展的正常业务不构成关联交易，关联交易需发生在关联方之间。"
        },
        {
            "id": 7,
            "question": "关联方的识别责任在谁？",
            "options": [
                "A. 仅在发生时识别",
                "B. 金融机构和上市公司应持续识别",
                "C. 仅上市公司需识别",
                "D. 不需要识别"
            ],
            "answer": "B",
            "explanation": "金融机构和上市公司应建立关联方名单，持续识别和更新，不是在发生时才识别。"
        },
        {
            "id": 8,
            "question": "关联交易信息披露的责任主体是？",
            "options": [
                "A. 仅控股股东",
                "B. 仅上市公司",
                "C. 上市公司及其董事、监事、高级管理人员",
                "D. 仅董事会秘书"
            ],
            "answer": "C",
            "explanation": "信息披露是上市公司的法定义务，上市公司及其董监高都对信息披露的真实性、准确性、完整性负责。"
        },
        {
            "id": 9,
            "question": "某上市公司计划向控股股东销售货物，正确的做法是？",
            "options": [
                "A. 直接签订合同",
                "B. 按关联交易程序审批，披露后实施",
                "C. 先实施再披露",
                "D. 不需要任何程序"
            ],
            "answer": "B",
            "explanation": "关联交易应按程序审批并及时披露，不可事后补办，更不可不披露。"
        },
        {
            "id": 10,
            "question": "下列属于关联交易类型的是？",
            "options": [
                "A. 上市公司向关联方销售产品",
                "B. 上市公司从非关联方采购原材料",
                "C. 上市公司向员工支付工资",
                "D. 上市公司向国家纳税"
            ],
            "answer": "A",
            "explanation": "向关联方销售产品属于关联交易类型，其他选项属于正常业务往来。"
        },
    ],
    "内幕交易": [
        {
            "id": 1,
            "question": "以下哪项属于'内幕信息'？",
            "options": [
                "A. 已经在媒体上公开报道的信息",
                "B. 对公司股价有重大影响但尚未公开的信息",
                "C. 公司早餐菜单",
                "D. 公开的年报信息"
            ],
            "answer": "B",
            "explanation": "内幕信息是指尚未公开的、对公司证券或衍生品价格有重大影响的信息。"
        },
        {
            "id": 2,
            "question": "内幕信息知情人包括以下哪类人员？",
            "options": [
                "A. 公司独立董事",
                "B. 公司食堂厨师",
                "C. 公司普通保洁员",
                "D. 公司茶水间阿姨"
            ],
            "answer": "A",
            "explanation": "内幕信息知情人包括公司董监高、持股5%以上股东及其董事、高管，以及因业务往来知悉内幕信息的人员。"
        },
        {
            "id": 3,
            "question": "内幕交易行为不包括以下哪项？",
            "options": [
                "A. 利用内幕信息买卖证券",
                "B. 泄露内幕信息给他人",
                "C. 根据公开信息进行交易",
                "D. 建议他人买卖证券"
            ],
            "answer": "C",
            "explanation": "根据公开信息进行交易是合法行为，不构成内幕交易。"
        },
        {
            "id": 4,
            "question": "禁止内幕交易的法规主要是？",
            "options": [
                "A. 《合同法》",
                "B. 《证券法》",
                "C. 《商标法》",
                "D. 《票据法》"
            ],
            "answer": "B",
            "explanation": "《证券法》明确规定禁止内幕交易，并对相关行为规定了严厉的处罚措施。"
        },
        {
            "id": 5,
            "question": "某上市公司董事长在业绩预告披露前买入自家公司股票，正确的说法是？",
            "options": [
                "A. 这是正常投资行为",
                "B. 这属于违规交易",
                "C. 只要获利就不是违规",
                "D. 只要不亏就不是违规"
            ],
            "answer": "B",
            "explanation": "在敏感期（业绩预告披露前）买卖本公司股票构成内幕交易，无论盈亏。"
        },
        {
            "id": 6,
            "question": "员工进行证券交易申报制度的目的是？",
            "options": [
                "A. 增加公司收入",
                "B. 监控员工证券交易，防范内幕交易",
                "C. 控制员工投资自由",
                "D. 增加交易量"
            ],
            "answer": "B",
            "explanation": "员工证券交易申报制度旨在监控员工交易行为，防范内幕交易和利益冲突。"
        },
        {
            "id": 7,
            "question": "内幕交易行政处罚中，没收违法所得后，还可以处以多少倍罚款？",
            "options": [
                "A. 1倍以下",
                "B. 最高10倍",
                "C. 随意罚款",
                "D. 不罚款"
            ],
            "answer": "B",
            "explanation": "《证券法》规定，内幕交易可处以最高10倍违法所得的罚款。"
        },
        {
            "id": 8,
            "question": "老鼠仓行为是指？",
            "options": [
                "A. 养老基金投资",
                "B. 金融机构从业人员先建仓后用公有资金拉升股价从中获利",
                "C. 购买稳健理财产品",
                "D. 长期持有蓝筹股"
            ],
            "answer": "B",
            "explanation": "老鼠仓是指金融机构从业人员利用公有资金拉升股价前，先用个人账户建仓获利的违法行为。"
        },
        {
            "id": 9,
            "question": "以下哪项措施可以有效防范内幕交易？",
            "options": [
                "A. 随意谈论未公开信息",
                "B. 建立信息隔离墙制度",
                "C. 不需要任何措施",
                "D. 鼓励员工买卖公司股票"
            ],
            "answer": "B",
            "explanation": "信息隔离墙（Chinese Wall）是防范内幕交易的的重要制度措施，用于隔离敏感信息。"
        },
        {
            "id": 10,
            "question": "发现可能存在内幕交易时，正确的做法是？",
            "options": [
                "A. 不管不问",
                "B. 向公司合规部门或监察稽核部门报告",
                "C. 参与其中",
                "D. 泄露给媒体"
            ],
            "answer": "B",
            "explanation": "发现疑似内幕交易应向合规部门或稽核部门报告，由公司启动内部调查并决定是否向监管机构报告。"
        },
    ],
}

# ===== 评估维度 =====
EVALUATION_DIMENSIONS = [
    {
        "dimension": "培训满意度",
        "weight": "20%",
        "indicators": ["课程内容实用性", "讲师授课水平", "教学方式互动性", "案例分析贴合度"],
        "method": "问卷调查（5分制）"
    },
    {
        "dimension": "知识掌握度",
        "weight": "40%",
        "indicators": ["法规要点理解", "场景识别能力", "风险判断能力", "应对措施掌握"],
        "method": "课后测试（10题选择题，满分100分）"
    },
    {
        "dimension": "行为改变度",
        "weight": "30%",
        "indicators": ["合规意识提升", "操作规范执行", "风险识别主动性", "问题报告及时性"],
        "method": "培训后30/60/90天行为观察"
    },
    {
        "dimension": "业务合规率",
        "weight": "10%",
        "indicators": ["合规检查通过率", "投诉率变化", "违规事件发生率"],
        "method": "培训后业务数据对比分析"
    },
]


@dataclass
class TrainingPlan:
    """培训方案数据类"""
    topic: str
    job_type: str
    duration_minutes: int
    outline: dict = field(default_factory=dict)
    content: dict = field(default_factory=dict)
    quiz: list = field(default_factory=list)
    evaluation: dict = field(default_factory=dict)
    quick_ref: dict = field(default_factory=dict)
    cases: list = field(default_factory=list)


class ComplianceTrainingEngine:
    """合规培训引擎"""

    def __init__(self):
        self.topics = TRAINING_TOPICS
        self.cases = CASE_LIBRARY
        self.questions = QUESTION_BANK
        self.evaluation_dims = EVALUATION_DIMENSIONS

    def generate_training(
        self,
        job_type: str,
        department: str = "",
        topic: str = "销售合规",
        duration_minutes: int = 60
    ) -> dict:
        """
        生成合规培训方案

        Args:
            job_type: 岗位类型（如：客户经理、柜员、风控专员等）
            department: 部门（可选）
            topic: 培训主题
            duration_minutes: 时长要求（30/45/60/90/120分钟）

        Returns:
            dict: 包含培训方案（课件大纲/案例/测试题）+ 培训内容（法规要点/案例分析/违规后果）
                  + 课后测试题（10题选择）+ 培训效果评估 + 合规要点速查卡
        """
        topic_info = self.topics.get(topic, self.topics["销售合规"])

        # 生成课件大纲
        outline = self._generate_outline(topic, job_type, duration_minutes)

        # 生成培训内容
        content = self._generate_content(topic_info, job_type, duration_minutes)

        # 选择案例
        cases = self._select_cases(topic)

        # 生成测试题
        quiz = self._generate_quiz(topic)

        # 生成效果评估
        evaluation = self._generate_evaluation(topic, job_type)

        # 生成速查卡
        quick_ref = self._generate_quick_ref(topic, topic_info)

        result = {
            "status": "success",
            "meta": {
                "job_type": job_type,
                "department": department,
                "topic": topic,
                "duration_minutes": duration_minutes,
            },
            "outline": outline,
            "content": content,
            "cases": cases,
            "quiz": quiz,
            "evaluation": evaluation,
            "quick_ref": quick_ref,
        }
        return result

    def _generate_outline(self, topic: str, job_type: str, duration: int) -> dict:
        """生成课件大纲"""
        base_hours = duration / 60

        # 时长分配比例
        sections = []
        if base_hours <= 0.5:
            sections = [
                {"name": "法规要点", "minutes": 15, "modules": ["核心法规解读"]},
                {"name": "案例分析", "minutes": 10, "modules": ["典型案例讨论"]},
                {"name": "要点总结", "minutes": 5, "modules": ["速查卡发放"]},
            ]
        elif base_hours <= 1:
            sections = [
                {"name": "导入与概述", "minutes": int(duration * 0.1), "modules": ["培训背景", "合规重要性"]},
                {"name": "法规要点", "minutes": int(duration * 0.35), "modules": list(self.topics.get(topic, self.topics["销售合规"])["key_points"][:3])},
                {"name": "案例分析", "minutes": int(duration * 0.35), "modules": ["典型违规案例", "处罚结果分析", "启示与教训"]},
                {"name": "要点总结", "minutes": int(duration * 0.1), "modules": ["合规要点速查", "行动承诺"]},
                {"name": "课后测试", "minutes": int(duration * 0.1), "modules": ["10题选择题"]},
            ]
        elif base_hours <= 1.5:
            sections = [
                {"name": "导入与概述", "minutes": int(duration * 0.08), "modules": ["培训背景", "监管形势", "合规重要性"]},
                {"name": "法规要点（上）", "minutes": int(duration * 0.2), "modules": self.topics.get(topic, self.topics["销售合规"])["key_points"][:2]},
                {"name": "法规要点（下）", "minutes": int(duration * 0.17), "modules": self.topics.get(topic, self.topics["销售合规"])["key_points"][2:4]},
                {"name": "案例分析", "minutes": int(duration * 0.3), "modules": ["典型违规案例一", "典型违规案例二", "处罚结果分析", "启示与教训"]},
                {"name": "互动讨论", "minutes": int(duration * 0.1), "modules": ["情景模拟", "角色扮演"]},
                {"name": "要点总结", "minutes": int(duration * 0.08), "modules": ["合规要点速查", "行动承诺"]},
                {"name": "课后测试", "minutes": int(duration * 0.07), "modules": ["10题选择题"]},
            ]
        else:
            sections = [
                {"name": "第一天上午", "minutes": 180, "modules": ["培训导入", "监管框架", "核心法规详解"]},
                {"name": "第一天下午", "minutes": 180, "modules": ["典型案例分析", "分组讨论", "情景演练"]},
                {"name": "第二天上午", "minutes": 180, "modules": ["行业专题", "合规流程", "风险识别"]},
                {"name": "第二天下午", "minutes": 180, "modules": ["合规测试", "案例答辩", "行动承诺"]},
            ]

        return {
            "title": f"{job_type}合规培训 - {topic}",
            "total_minutes": duration,
            "sections": sections,
        }

    def _generate_content(self, topic_info: dict, job_type: str, duration: int) -> dict:
        """生成培训内容"""
        return {
            "regulations": topic_info["regulations"],
            "key_points": topic_info["key_points"],
            "violation_consequences": topic_info["violation_consequences"],
            "job_specific_tips": self._get_job_specific_tips(job_type, topic_info["name"]),
        }

    def _get_job_specific_tips(self, job_type: str, topic: str) -> list:
        """获取岗位特定的合规提示"""
        tips_map = {
            "客户经理": [
                "销售产品前务必完成风险评估问卷",
                "严禁承诺保本保收益",
                "客户资料保密，不向第三方透露",
                "可疑交易及时报告",
            ],
            "柜员": [
                "严格执行客户身份识别",
                "大额现金交易按规定报告",
                "客户签名确保真实意愿",
                "离柜必须签退系统",
            ],
            "风控专员": [
                "定期审查可疑交易报告",
                "监控名单实时更新筛查",
                "风险预警及时响应",
                "合规检查配合到位",
            ],
            "稽核审计": [
                "独立、客观开展审计",
                "发现问题如实报告",
                "审计建议具有可操作性",
                "保密义务严格遵守",
            ],
            "中层管理": [
                "合规管理纳入绩效考核",
                "员工合规培训组织到位",
                "违规行为及时处置",
                "向上级报告合规风险",
            ],
            "高管": [
                "合规文化建设第一责任人",
                "关联交易审批合规把关",
                "信息披露真实准确完整",
                "配合监管检查诚实守信",
            ],
        }
        return tips_map.get(job_type, tips_map["客户经理"])

    def _select_cases(self, topic: str) -> list:
        """选择案例"""
        topic_cases = self.cases.get(topic, self.cases["销售合规"])
        # 随机选择2个案例
        selected = random.sample(topic_cases, min(2, len(topic_cases)))
        return selected

    def _generate_quiz(self, topic: str) -> list:
        """生成课后测试题"""
        topic_questions = self.questions.get(topic, self.questions["销售合规"])
        # 随机选择10题
        selected = random.sample(topic_questions, min(10, len(topic_questions)))
        return [
            {
                "id": i + 1,
                "question": q["question"],
                "options": q["options"],
                "answer": q["answer"],
                "explanation": q["explanation"],
            }
            for i, q in enumerate(selected)
        ]

    def _generate_evaluation(self, topic: str, job_type: str) -> dict:
        """生成效果评估方案"""
        return {
            "dimensions": self.evaluation_dims,
            "passing_score": 70,
            "topic": topic,
            "job_type": job_type,
            "follow_up_schedule": [
                {"time": "培训后7天", "action": "知识回访", "method": "抽查3题核心要点"},
                {"time": "培训后30天", "action": "行为观察", "method": "主管评估合规行为改变"},
                {"time": "培训后90天", "action": "合规检查", "method": "合规抽查通过率对比"},
            ],
        }

    def _generate_quick_ref(self, topic: str, topic_info: dict) -> dict:
        """生成合规要点速查卡"""
        return {
            "title": f"{topic}合规要点速查卡",
            "topic": topic,
            "regulations_count": len(topic_info["regulations"]),
            "key_rules": [
                {
                    "rule": point,
                    "check": "是否落实？",
                    "if_violated": topic_info["violation_consequences"][0] if topic_info["violation_consequences"] else "行政处罚",
                }
                for point in topic_info["key_points"]
            ],
            "emergency_contact": [
                {"role": "合规部门", "responsibility": "合规咨询与违规举报"},
                {"role": "稽核部门", "responsibility": "违规行为调查"},
                {"role": "监管机构", "responsibility": "重大违规报告"},
            ],
            "version": "1.0",
            "effective_date": "培训当天",
        }


def main():
    """测试函数"""
    engine = ComplianceTrainingEngine()
    result = engine.generate_training(
        job_type="客户经理",
        department="销售部",
        topic="销售合规",
        duration_minutes=60
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
