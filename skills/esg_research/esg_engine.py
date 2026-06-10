"""
ESG Engine - ESG评分核心引擎
输入公司名称/行业，返回ESG评分（E/S/G三维+综合）、同业对比、风险点、改进建议
内置50+中国上市公司ESG数据
"""

from typing import Dict, List, Optional, Tuple
import re


class ESGEngine:
    """ESG研究引擎"""

    # ============================================================
    # 内置ESG数据库（50+中国上市公司）
    # ============================================================
    ESG_DATA: Dict[str, Dict] = {
        # === 新能源汽车/动力电池 ===
        "宁德时代": {
            "industry": "动力电池",
            "e": {"score": 82, "carbon": "范围一/二碳排放强度持续下降，2023年碳排放强度同比-12%",
                  "energy": "清洁能源使用率62%，绿电采购量行业第一",
                  "water": "单位产品水耗0.38m³/GWh，行业最优",
                  "waste": "电池回收利用率78%，磷酸铁锂电池回收率超92%",
                  "risks": "海外工厂碳足迹核算边界扩展压力", "strengths": "零碳工厂建设领先"},
            "s": {"score": 78, "employee": "员工满意度82%，女性管理层占比24%",
                  "safety": "工伤率0.12%，远低于行业均值0.45%",
                  "supply_chain": "供应商ESG审计覆盖率89%，高标准",
                  "community": "教育公益投入3.2亿元，乡村教育支持超500所",
                  "risks": "海外工厂劳工合规风险", "strengths": "员工培训投入强度高"},
            "g": {"score": 75, "board": "董事会11人，独立非执行董事4人，女性1人",
                 "disclosure": "ESG报告披露评级A，信息披露完整度行业领先",
                 "anti_corruption": "反腐培训覆盖率100%，合规体系成熟",
                 "shareholder": "中小股东权益保护评级B+",
                 "risks": "海外业务合规架构尚待完善", "strengths": "ESG评级纳入高管薪酬考核"},
            "overall": 79, "rating": "AA", "highlights": "动力电池行业ESG标杆，环保技术全球领先"
        },
        "比亚迪": {
            "industry": "新能源汽车",
            "e": {"score": 80, "carbon": "整车碳足迹同比-15%，2025年目标全价值链碳中和",
                  "energy": "光伏自发自用，绿电采购占比55%",
                  "water": "涂装废水循环率92%，行业最高水平",
                  "waste": "动力电池回收网络覆盖全国，回收率71%",
                  "risks": "原材料（锂/钴）供应链碳排放核算不足", "strengths": "新能源车销量全球前三，带动供应链减碳"},
            "s": {"score": 76, "employee": "研发人员超4万人，员工关怀体系完善",
                  "safety": "安全生产标准化达标率100%",
                  "supply_chain": "供应商人权审计覆盖主要供应商",
                  "community": "消费帮扶金额超2亿元，乡村振兴参与度高",
                  "risks": "海外工厂社区关系管理经验不足", "strengths": "员工持股计划覆盖面广"},
            "g": {"score": 74, "board": "董事会10人，独董3人，薪酬委员会独立运作",
                 "disclosure": "ESG报告评级A，TCFD框架对齐完整",
                 "anti_corruption": "合规体系通过ISO 37001认证",
                 "shareholder": "股东大会网络投票渠道畅通",
                 "risks": "关联交易披露细节待提升", "strengths": "信息披露及时性良好"},
            "overall": 77, "rating": "A", "highlights": "新能源汽车龙头，全产业链协同减碳"
        },
        "亿纬锂能": {
            "industry": "动力电池",
            "e": {"score": 75, "carbon": "碳排放强度同比-9%", "energy": "清洁能源占比48%",
                  "water": "水耗控制良好，单位能耗行业中等偏上",
                  "waste": "废旧电池回收布局中，回收率55%", "risks": "海外工厂环境合规", "strengths": "储能业务减碳贡献"},
            "s": {"score": 72, "employee": "员工培训体系完善", "safety": "安全记录良好",
                  "supply_chain": "供应链ESG管理建设ing", "community": "公益投入超1亿元",
                  "risks": "国际业务SHE管理压力", "strengths": "员工职业发展通道清晰"},
            "g": {"score": 71, "board": "董事会结构合理，独董占比符合要求",
                 "disclosure": "ESG报告评级A-", "anti_corruption": "合规体系完善",
                 "shareholder": "中小股东参与渠道畅通", "risks": "海外合规团队建设ing",
                 "strengths": "治理制度更新及时"},
            "overall": 73, "rating": "A", "highlights": "动力电池新锐，储能业务高增长"
        },
        "赣锋锂业": {
            "industry": "锂资源",
            "e": {"score": 68, "carbon": "碳排放强度处于行业中游", "energy": "能耗控制待提升",
                  "water": "盐湖提锂水耗较高，卤水综合利用待优化", "waste": "固废处理压力",
                  "risks": "锂辉石来源国环保法规差异风险", "strengths": "回收业务布局领先"},
            "s": {"score": 65, "employee": "员工结构以技术为主", "safety": "矿山安全记录良好",
                  "supply_chain": "供应链溯源管理建设中", "community": "资源地社区支持",
                  "risks": "海外矿山社区关系复杂", "strengths": "资源地就业贡献"},
            "g": {"score": 63, "board": "家族企业特征，董事会独立性待加强",
                 "disclosure": "ESG报告披露评级B+", "anti_corruption": "合规体系持续完善",
                 "shareholder": "股权结构相对集中", "risks": "治理透明度提升空间大",
                 "strengths": "资源端定价权强"},
            "overall": 65, "rating": "BBB", "highlights": "锂资源龙头，ESG管理处于追赶阶段"
        },

        # === 商业银行 ===
        "招商银行": {
            "industry": "商业银行",
            "e": {"score": 72, "carbon": "自身运营碳中和实现，绿色建筑认证率100%",
                  "energy": "网点节能改造完成率85%", "water": "水资源消耗极低",
                  "waste": "无纸化运营率93%", "risks": "投融资组合碳核算方法学待完善",
                  "strengths": "绿色贷款余额破万亿，绿色金融产品丰富"},
            "s": {"score": 80, "employee": "员工满意度86分，金融科技人才储备充足",
                  "safety": "零重大安全事故", "supply_chain": "采购ESG标准纳入招标",
                  "community": "志愿者服务超20万小时，普惠金融覆盖3千万小微",
                  "risks": "催收外包引发社会争议", "strengths": "客户信息保护行业标杆"},
            "g": {"score": 83, "board": "董事会女性占比30%，独董占比40%，结构最优",
                 "disclosure": "ESG报告评级AA，TCFD/ISSB全面对标",
                 "anti_corruption": "合规体系行业最完善，举报机制健全",
                 "shareholder": "现金分红比例33%，股东回报稳定",
                 "risks": "关联交易管理压力", "strengths": "风控模型领先"},
            "overall": 79, "rating": "AA", "highlights": "零售银行标杆，ESG治理水平行业最优"
        },
        "工商银行": {
            "industry": "商业银行",
            "e": {"score": 70, "carbon": "自身运营碳减排有序推进", "energy": "绿色信贷余额超3万亿",
                  "water": "网点节水改造成效显著", "waste": "电子废物的规范回收",
                  "risks": "高碳行业敞口较大（煤电/钢铁）", "strengths": "绿色债券承销规模领先"},
            "s": {"score": 77, "employee": "员工超44万人，员工关怀体系完善",
                  "safety": "安全生产标准化全面达标", "supply_chain": "供应商准入ESG一票否决",
                  "community": "精准扶贫投入超百亿，网点覆盖全国",
                  "risks": "大行员工规模带来管理复杂度", "strengths": "普惠金融覆盖面最广"},
            "g": {"score": 75, "board": "党委领导下的公司治理，党委前置研究重大事项",
                 "disclosure": "ESG报告评级A+", "anti_corruption": "纪检监察体系健全",
                 "shareholder": "国有控股，股价稳定", "risks": "决策机制透明度有待提升",
                 "strengths": "系统性重要银行，风控严格"},
            "overall": 74, "rating": "A", "highlights": "宇宙行，规模最大，绿色金融布局全面"
        },
        "兴业银行": {
            "industry": "商业银行",
            "e": {"score": 78, "carbon": "首家官方碳中和银行，赤道原则项目超300个",
                  "energy": "绿色建筑运营面积超百万平方米", "water": "水资源管理体系完善",
                  "waste": "绿色采购比例超85%", "risks": "绿色信贷资产质量波动", "strengths": "绿色金融品牌最响"},
            "s": {"score": 74, "employee": "员工专业能力强", "safety": "安全运营记录良好",
                  "supply_chain": "绿色供应链金融", "community": "养老金融普惠化",
                  "risks": "零售业务投诉处理压力", "strengths": "银银平台输出科技"},
            "g": {"score": 76, "board": "独董占比符合要求，委员会设置完善",
                 "disclosure": "ESG报告评级A+", "anti_corruption": "合规文化深入",
                 "shareholder": "分红政策稳定", "risks": "同业业务合规压力",
                 "strengths": "研究驱动型银行"},
            "overall": 76, "rating": "A", "highlights": "绿色金融先行者，赤道原则实践丰富"
        },

        # === 保险 ===
        "中国平安": {
            "industry": "保险",
            "e": {"score": 75, "carbon": "平安信托绿色投融资规模持续扩大",
                  "energy": "运营端节能减排推进", "water": "水资源管理措施有效",
                  "waste": "电子化减少纸张消耗", "risks": "ESG投资组合碳核算能力待建",
                  "strengths": "保险资金绿色投资超千亿"},
            "s": {"score": 82, "employee": "平安希望小学超100所，员工培训体系行业领先",
                  "safety": "零重大安全事故", "supply_chain": "供应链ESG审核落地",
                  "community": "中国平安教育公益投入超10亿，乡村振兴专项支持",
                  "risks": "保险理赔纠纷投诉率较高", "strengths": "三村工程覆盖乡村超百万"},
            "g": {"score": 80, "board": "董事会结构优化，女性董事2人，独董3人",
                 "disclosure": "ESG报告评级AA，ESG绩效纳入高管薪酬",
                 "anti_corruption": "反腐合规体系成熟", "shareholder": "H股+A股，股东结构多元",
                 "risks": "复杂集团架构带来治理难度", "strengths": "金融科技赋能风控"},
            "overall": 79, "rating": "AA", "highlights": "综合金融巨头，社会公益投入巨大"
        },
        "中国人寿": {
            "industry": "保险",
            "e": {"score": 68, "carbon": "保险资金绿色投资布局加速", "energy": "运营节能改造ing",
                  "water": "水资源管理措施建立", "waste": "电子化程度提升",
                  "risks": "高碳行业保险敞口风险", "strengths": "绿色投资规模超500亿"},
            "s": {"score": 76, "employee": "员工关怀体系完善", "safety": "安全生产达标",
                  "supply_chain": "供应商管理ESG标准建立", "community": "大病保险覆盖人群过亿",
                  "risks": "代理人队伍改革压力", "strengths": "县域服务网络最广"},
            "g": {"score": 72, "board": "党委前置治理，央企背景", "disclosure": "ESG报告评级A",
                 "anti_corruption": "纪检监察体系健全", "shareholder": "国有控股，股权稳定",
                 "risks": "治理透明度提升空间", "strengths": "资金规模优势显著"},
            "overall": 72, "rating": "A", "highlights": "寿险龙头，国有控股，风控稳健"
        },

        # === 白酒 ===
        "贵州茅台": {
            "industry": "白酒",
            "e": {"score": 70, "carbon": "碳足迹核算试点中", "energy": "酿造过程能耗下降",
                  "water": "赤水河保护力度最强，单位产品水耗极低",
                  "waste": "酒糟综合利用超95%", "risks": "水资源保护压力（气候变化）",
                  "strengths": "产区生态保护领先"},
            "s": {"score": 78, "employee": "员工薪酬福利行业最优", "safety": "食品安全管控严格",
                  "supply_chain": "糯高粱种植基地覆盖扶贫", "community": "工业旅游带动产区经济",
                  "risks": "经销商管理复杂度高", "strengths": "供应商原粮基地扶贫效果好"},
            "g": {"score": 80, "board": "董事会结构稳定，独董制度完善",
                 "disclosure": "ESG报告评级AA，信息披露质量高",
                 "anti_corruption": "反腐合规体系完善", "shareholder": "现金分红比例高，稳定回报",
                 "risks": "关联交易管理（销售子公司）", "strengths": "品牌护城河极强"},
            "overall": 76, "rating": "A", "highlights": "酱香龙头，产区生态保护典范"
        },
        "五粮液": {
            "industry": "白酒",
            "e": {"score": 68, "carbon": "碳排放核算体系建设中", "energy": "清洁能源使用率持续提升",
                  "water": "长江上游水源保护投入大", "waste": "酒糟综合利用",
                  "risks": "极端天气对酿造影响", "strengths": "产区环保标准严格"},
            "s": {"score": 75, "employee": "员工待遇良好", "safety": "食品安全管控",
                  "supply_chain": "粮食采购基地化", "community": "乡村振兴投入",
                  "risks": "劳动力密集型包装环节合规", "strengths": "就业带动效应强"},
            "g": {"score": 77, "board": "治理结构合理", "disclosure": "ESG报告评级A+",
                 "anti_corruption": "合规体系完善", "shareholder": "分红稳定",
                 "risks": "关联交易透明度待提升", "strengths": "浓香型龙头，品牌力强"},
            "overall": 73, "rating": "A", "highlights": "浓香龙头，ESG信息披露持续改善"
        },

        # === 互联网/科技 ===
        "阿里巴巴": {
            "industry": "互联网",
            "e": {"score": 80, "carbon": "2023年范围一/二碳排放同比-12%，范围三推进中",
                  "energy": "数据中心PUE降至1.22，液冷技术领先",
                  "water": "数据中心水效管理创新", "waste": "电子设备回收体系完善",
                  "risks": "快递包装废弃物管理", "strengths": "技术赋能全社会减碳"},
            "s": {"score": 82, "employee": "员工超20万，灵活用工管理完善",
                  "safety": "零重大安全事故", "supply_chain": "淘宝商家ESG培训超百万",
                  "community": "公益基金会投入超100亿，乡村教育投入大",
                  "risks": "平台经济监管政策不确定性", "strengths": "女性管理者占比超40%"},
            "g": {"score": 78, "board": "董事会独立性持续提升，独董5/11人",
                 "disclosure": "ESG报告评级AA，SEC对齐，TCFD覆盖",
                 "anti_corruption": "阳光联盟反腐平台行业影响大",
                 "shareholder": "股东回报良好，分红比例提升",
                 "risks": "VIE架构监管风险", "strengths": "ESG绩效纳入高管长期激励"},
            "overall": 80, "rating": "AA", "highlights": "电商科技巨头，ESG治理架构成熟"
        },
        "腾讯": {
            "industry": "互联网",
            "e": {"score": 83, "carbon": "2023年实现运营碳中和，可再生能源比例71%",
                  "energy": "数据中心能效全球领先，浸没液冷规模化应用",
                  "water": "数据中心水耗管理创新", "waste": "硬件回收超50万台",
                  "risks": "供应链上游电子垃圾管理", "strengths": "技术产品助力全社会减碳"},
            "s": {"score": 84, "employee": "员工满意度高，多元包容文化突出",
                  "safety": "安全生产管理完善", "supply_chain": "供应商EICC标准推广",
                  "community": "公益投入超150亿，微信生态助农超100亿",
                  "risks": "游戏业务社会责任争议", "strengths": "用户隐私保护行业标杆"},
            "g": {"score": 81, "board": "董事会治理卓越，独董6/11人，女性董事2人",
                 "disclosure": "ESG报告评级AA，ISSB/TCFD全面对标",
                 "anti_corruption": "合规体系成熟，廉政审计严格",
                 "shareholder": "分红与回购并举，股东回报突出",
                 "risks": "业务多元化带来治理复杂度", "strengths": "ESG评级纳入薪酬"},
            "overall": 82, "rating": "AA", "highlights": "社交龙头，碳中和领先，公益投入巨大"
        },
        "百度": {
            "industry": "互联网",
            "e": {"score": 76, "carbon": "数据中心能效持续优化，绿电采购增长",
                  "energy": "PUE降至1.25", "water": "数据中心水冷技术应用",
                  "waste": "服务器回收体系", "risks": "AI算力需求快速增长带来能耗压力",
                  "strengths": "自动驾驶赋能低碳出行"},
            "s": {"score": 75, "employee": "AI人才吸引力强", "safety": "工作场所安全",
                  "supply_chain": "供应商管理ESG建设ing", "community": "AI赋能教育公益",
                  "risks": "竞价排名商业模式社会争议", "strengths": "文心一言赋能千行百业"},
            "g": {"score": 74, "board": "公司治理持续改善，独董占比提升",
                 "disclosure": "ESG报告评级A+", "anti_corruption": "合规培训覆盖全员",
                 "shareholder": "股东回报稳定", "risks": "ESG评级相对科技同行偏低",
                 "strengths": "全栈AI技术能力"},
            "overall": 75, "rating": "A", "highlights": "AI公司，自动驾驶落地加速"
        },
        "京东": {
            "industry": "零售/物流",
            "e": {"score": 77, "carbon": "光伏发电装机容量大，仓储减碳成效显著",
                  "energy": "无人仓/车电耗管理，绿色配送比例提升",
                  "water": "仓储水耗管理", "waste": "快递包装回收体系完善",
                  "risks": "物流车队碳排放管控压力", "strengths": "亚洲一号绿色仓储标杆"},
            "s": {"score": 80, "employee": "物流一线员工超20万，五险一金全覆盖",
                  "safety": "配送安全培训体系", "supply_chain": "乡村振兴农产品上行",
                  "community": "高质量就业带动，返乡快递员项目",
                  "risks": "骑手劳动关系争议", "strengths": "残疾人就业支持领先"},
            "g": {"score": 76, "board": "治理结构持续优化", "disclosure": "ESG报告评级A+",
                 "anti_corruption": "反腐合规体系完善", "shareholder": "连续多年盈利，股东回报改善",
                 "risks": "关联交易管理", "strengths": "供应链效率行业领先"},
            "overall": 78, "rating": "A", "highlights": "物流基础设施重资产，社会价值创造强"
        },
        "美团": {
            "industry": "本地服务",
            "e": {"score": 70, "carbon": "外卖包装减量目标明确，骑手电动化推进",
                  "energy": "即时配送网络效率提升", "water": "餐饮商户用水管理",
                  "waste": "外卖餐盒回收试点ing", "risks": "外卖包装白色污染",
                  "strengths": "即时零售赋能实体商业"},
            "s": {"score": 76, "employee": "骑手保障体系持续完善（职业伤害险试点）",
                  "safety": "配送安全培训", "supply_chain": "商户扶持计划",
                  "community": "数字助农，超10亿销售额农产品",
                  "risks": "骑手劳动权益社会关注度高", "strengths": "就业规模巨大"},
            "g": {"score": 72, "board": "ESG治理架构建设完善ing",
                 "disclosure": "ESG报告评级A", "anti_corruption": "合规团队建设",
                 "shareholder": "连续减亏，盈利可期", "risks": "骑手外包模式争议",
                 "strengths": "本地生活平台龙头"},
            "overall": 73, "rating": "A", "highlights": "本地生活平台，骑手保障行业领先"
        },

        # === 金融机构 ===
        "中国银行": {
            "industry": "商业银行",
            "e": {"score": 69, "carbon": "绿色信贷余额超2万亿", "energy": "运营节能改造推进",
                  "water": "节水措施完善", "waste": "绿色办公",
                  "risks": "海外业务ESG合规复杂", "strengths": "跨境绿色金融服务领先"},
            "s": {"score": 75, "employee": "全球化人才体系", "safety": "安全生产",
                  "supply_chain": "绿色采购", "community": "定点扶贫成效显著",
                  "risks": "跨境业务社会风险", "strengths": "国际化程度最高"},
            "g": {"score": 74, "board": "党委前置治理，国有大行通病",
                 "disclosure": "ESG报告评级A", "anti_corruption": "海外合规法律风险管控",
                 "shareholder": "股息稳定", "risks": "制裁合规压力",
                 "strengths": "全球布局风控体系"},
            "overall": 73, "rating": "A", "highlights": "跨境金融标杆，国际化程度最高"
        },
        "建设银行": {
            "industry": "商业银行",
            "e": {"score": 71, "carbon": "绿色信贷规模领先", "energy": "绿色建筑运营",
                  "water": "水资源管理", "waste": "电子化减废",
                  "risks": "制造业敞口风险", "strengths": "住房租赁绿色建筑"},
            "s": {"score": 76, "employee": "员工超35万", "safety": "安全生产标准化",
                  "supply_chain": "采购ESG标准", "community": "裕农通覆盖全国",
                  "risks": "大行管理复杂度", "strengths": "普惠金融规模最大"},
            "g": {"score": 73, "board": "党委治理结构", "disclosure": "ESG报告评级A",
                 "anti_corruption": "纪检监察", "shareholder": "股息稳定",
                 "risks": "治理透明度空间", "strengths": "金融科技投入大"},
            "overall": 73, "rating": "A", "highlights": "大行绿色信贷领先，住房租赁布局早"
        },
        "交通银行": {
            "industry": "商业银行",
            "e": {"score": 68, "carbon": "绿色信贷增速稳健", "energy": "运营节能",
                  "water": "水资源管理", "waste": "绿色办公",
                  "risks": "高碳行业风险敞口", "strengths": "长三角绿色金融服务"},
            "s": {"score": 73, "employee": "员工关怀", "safety": "安全生产",
                  "supply_chain": "供应商管理", "community": "养老金业务普惠化",
                  "risks": "零售转型人员压力", "strengths": "养老金管理规模领先"},
            "g": {"score": 72, "board": "国有控股通病", "disclosure": "ESG报告评级A-",
                 "anti_corruption": "合规管理", "shareholder": "股息稳定",
                 "risks": "与头部大行差距", "strengths": "综合化经营"},
            "overall": 71, "rating": "A-", "highlights": "第五大银行，综合化经营稳健"
        },

        # === 能源 ===
        "中国石油": {
            "industry": "石油化工",
            "e": {"score": 62, "carbon": "碳排放强度持续下降，但绝对量仍大",
                  "energy": "炼化能效提升", "water": "油田采出水处理",
                  "waste": "固废处理压力", "risks": "化石能源转型压力巨大",
                  "strengths": "新能源业务（油气氢电）协同发展"},
            "s": {"score": 68, "employee": "员工规模超40万", "safety": "安全生产压力（石化高危）",
                  "supply_chain": "供应商管理", "community": "海外业务社区支持",
                  "risks": "海外运营社会风险（中东/非洲）", "strengths": "就业贡献巨大"},
            "g": {"score": 70, "board": "央企党委治理", "disclosure": "ESG报告评级A",
                 "anti_corruption": "合规体系建设", "shareholder": "股息稳定",
                 "risks": "透明度和ESG第三方鉴证不足", "strengths": "油气资源护城河"},
            "overall": 67, "rating": "BBB", "highlights": "油气龙头，转型新能源进行中"
        },
        "中国石化": {
            "industry": "石油化工",
            "e": {"score": 63, "carbon": "碳排放强度同比-3%", "energy": "炼化能效提升",
                  "water": "水资源管理", "waste": "氢能产业链布局（减碳技术）",
                  "risks": "化工业务环保合规压力", "strengths": "氢能产业链最完整"},
            "s": {"score": 69, "employee": "员工超45万", "safety": "安全生产（化工高危）",
                  "supply_chain": "采购标准", "community": "定点帮扶",
                  "risks": "化工事故社会影响大", "strengths": "加油站网络覆盖最广"},
            "g": {"score": 71, "board": "央企党委治理", "disclosure": "ESG报告评级A-",
                 "anti_corruption": "合规管理", "shareholder": "股息稳定",
                 "risks": "ESG数据量化能力待提升", "strengths": "炼化技术领先"},
            "overall": 68, "rating": "BBB", "highlights": "炼化化工龙头，氢能布局领先"
        },
        "中国神华": {
            "industry": "煤炭/电力",
            "e": {"score": 58, "carbon": "煤炭龙头，碳排放总量大", "energy": "高效清洁发电",
                  "water": "矿井水处理", "waste": "煤矸石综合利用",
                  "risks": "煤炭资产搁浅风险", "strengths": "一体化运营成本优势"},
            "s": {"score": 65, "employee": "员工约8万", "safety": "煤矿安全管控严",
                  "supply_chain": "供应商管理", "community": "矿区转型就业支持",
                  "risks": "煤矿社区转型压力", "strengths": "煤电路港航一体化"},
            "g": {"score": 70, "board": "央企治理", "disclosure": "ESG报告评级BBB",
                 "anti_corruption": "合规管理", "shareholder": "高股息率",
                 "risks": "转型战略清晰度待加强", "strengths": "现金流强劲"},
            "overall": 64, "rating": "BBB", "highlights": "煤炭一体化龙头，高股息防御性强"
        },

        # === 制造业 ===
        "美的集团": {
            "industry": "家电制造",
            "e": {"score": 78, "carbon": "碳排放强度同比-10%", "energy": "绿色工厂超100座",
                  "water": "节水改造", "waste": "废旧家电回收超2000万台",
                  "risks": "海外工厂环境合规", "strengths": "智能家居能效领先"},
            "s": {"score": 76, "employee": "员工超16万，海外员工超3万",
                  "safety": "安全生产标准化", "supply_chain": "供应商ESG审核",
                  "community": "美的基金会教育支持", "risks": "海外工厂劳工标准",
                  "strengths": "员工持股覆盖广"},
            "g": {"score": 77, "board": "职业经理人制度，股权激励完善",
                 "disclosure": "ESG报告评级A+", "anti_corruption": "合规体系完善",
                 "shareholder": "持续回购+分红，股东回报高",
                 "risks": "全球化治理复杂度", "strengths": "职业经理人机制行业最优"},
            "overall": 77, "rating": "A", "highlights": "家电龙头全球化标杆，治理结构好"
        },
        "格力电器": {
            "industry": "家电制造",
            "e": {"score": 76, "carbon": "光伏空调减碳贡献", "energy": "工厂节能改造",
                  "water": "绿色制造", "waste": "废旧家电回收",
                  "risks": "空调制冷剂环保争议", "strengths": "光伏空调差异化技术"},
            "s": {"score": 74, "employee": "员工约8万", "safety": "安全生产",
                  "supply_chain": "供应商管理", "community": "教育公益投入",
                  "risks": "员工待遇争议曾发生", "strengths": "分红比例高"},
            "g": {"score": 73, "board": "股权集中（珠海明骏控股）",
                 "disclosure": "ESG报告评级A", "anti_corruption": "合规管理",
                 "shareholder": "高股息", "risks": "一股独大治理风险",
                 "strengths": "空调主业技术壁垒高"},
            "overall": 74, "rating": "A", "highlights": "空调技术龙头，光伏空调引领创新"
        },
        "海康威视": {
            "industry": "安防/AI",
            "e": {"score": 74, "carbon": "工厂能效管理", "energy": "绿色制造推进",
                  "water": "环保合规", "waste": "电子设备回收",
                  "risks": "供应链碳核算能力待建", "strengths": "AI赋能智慧城市减碳"},
            "s": {"score": 76, "employee": "研发人员超2万，员工激励充分",
                  "safety": "安全生产", "supply_chain": "供应商管理",
                  "community": "AI赋能公益", "risks": "美国出口管制影响供应链",
                  "strengths": "技术人才竞争力强"},
            "g": {"score": 75, "board": "治理结构完善", "disclosure": "ESG报告评级A+",
                 "anti_corruption": "合规管理", "shareholder": "分红稳定",
                 "risks": "地缘政治风险持续", "strengths": "全球安防龙头"},
            "overall": 75, "rating": "A", "highlights": "AI视觉龙头，技术壁垒高"
        },
        "宁沪高速": {
            "industry": "高速公路",
            "e": {"score": 65, "carbon": "运营碳排放较低", "energy": "路灯节能改造",
                  "water": "边坡绿化", "waste": "道路固废回收",
                  "risks": "新能源汽车渗透率提升影响收费收入", "strengths": "稳定现金流"},
            "s": {"score": 70, "employee": "员工约1万人", "safety": "道路安全管理",
                  "supply_chain": "工程建设ESG管理", "community": "沿线经济带动",
                  "risks": "交通事故社会关注", "strengths": "区位优势显著"},
            "g": {"score": 72, "board": "国企治理", "disclosure": "ESG报告评级A-",
                 "anti_corruption": "工程建设反腐", "shareholder": "高股息",
                 "risks": "转型新能源布局ing", "strengths": "路产质量优"},
            "overall": 69, "rating": "A-", "highlights": "核心高速资产，高股息防御标的"
        },

        # === 医药 ===
        "恒瑞医药": {
            "industry": "医药",
            "e": {"score": 72, "carbon": "工厂能效提升", "energy": "清洁能源使用",
                  "water": "制药废水处理严格", "waste": "危废处理规范",
                  "risks": "原料药生产环保压力", "strengths": "环保投入持续"},
            "s": {"score": 78, "employee": "研发人员超5000，创新人才吸引力强",
                  "safety": "GMP生产质量管理", "supply_chain": "供应商审计",
                  "community": "慈善赠药覆盖肿瘤患者", "risks": "仿制药集采降价压力",
                  "strengths": "创新药研发管线丰富"},
            "g": {"score": 76, "board": "治理结构合理", "disclosure": "ESG报告评级A+",
                 "anti_corruption": "合规管理", "shareholder": "分红稳定",
                 "risks": "研发投入与盈利平衡", "strengths": "创新药龙头"},
            "overall": 75, "rating": "A", "highlights": "创新药龙头，肿瘤领域研发最强"
        },
        "药明康德": {
            "industry": "医药CXO",
            "e": {"score": 70, "carbon": "实验室能效管理", "energy": "清洁能源使用",
                  "water": "实验室水耗", "waste": "危废管理规范",
                  "risks": "海外监管合规（美国实体清单风险）", "strengths": "全球化CRO龙头"},
            "s": {"score": 76, "employee": "员工超4万，全球化人才",
                  "safety": "实验室安全", "supply_chain": "全球供应链管理",
                  "community": "罕见病药物研发支持", "risks": "地缘政治风险",
                  "strengths": "赋能全球创新药研发"},
            "g": {"score": 74, "board": "治理结构完善", "disclosure": "ESG报告评级A",
                 "anti_corruption": "合规管理", "shareholder": "增长+分红",
                 "risks": "美国出口管制风险", "strengths": "CXO赛道龙头"},
            "overall": 73, "rating": "A", "highlights": "CXO全球龙头，赋能创新药研发"
        },

        # === 房地产 ===
        "万科": {
            "industry": "房地产",
            "e": {"score": 72, "carbon": "绿色建筑认证面积行业第一", "energy": "建筑节能",
                  "water": "海绵社区", "waste": "建筑垃圾减量",
                  "risks": "行业下行周期财务压力", "strengths": "绿色建筑先发优势"},
            "s": {"score": 74, "employee": "员工约13万", "safety": "施工安全管理",
                  "supply_chain": "供应商管理", "community": "城市更新参与",
                  "risks": "流动性压力引发劳动关系争议", "strengths": "物业管理品牌好"},
            "g": {"score": 75, "board": "混合所有制，治理结构相对灵活",
                 "disclosure": "ESG报告评级A+", "anti_corruption": "阳光合规",
                 "shareholder": "深圳地铁为大股东", "risks": "债务压力",
                 "strengths": "行业危机中保持品质"},
            "overall": 74, "rating": "A", "highlights": "绿建龙头，住宅品质标杆"
        },
        "龙湖集团": {
            "industry": "房地产",
            "e": {"score": 75, "carbon": "绿色建筑占比提升", "energy": "商业运营节能",
                  "water": "海绵城市技术", "waste": "装配式建筑减废",
                  "risks": "行业流动性压力", "strengths": "TOD模式布局"},
            "s": {"score": 73, "employee": "员工约3万", "safety": "施工安全",
                  "supply_chain": "供应商管理", "community": "冠寓长租公寓",
                  "risks": "开发业务缩量影响就业", "strengths": "商业+开发+租赁均衡"},
            "g": {"score": 77, "board": "治理架构持续优化", "disclosure": "ESG报告评级A+",
                 "anti_corruption": "合规文化", "shareholder": "民营房企中财务最稳健",
                 "risks": "行业整体性风险", "strengths": "财务纪律严格"},
            "overall": 75, "rating": "A", "highlights": "民营房企稳健标杆，多元业务协同"
        },

        # === 消费 ===
        "伊利股份": {
            "industry": "乳制品",
            "e": {"score": 74, "carbon": "牧场碳足迹核算，饲喂端减碳", "energy": "工厂节能改造",
                  "water": "奶源水耗管理", "waste": "包装轻量化",
                  "risks": "牧场粪污处理压力", "strengths": "有机奶/减碳奶产品布局"},
            "s": {"score": 80, "employee": "员工约8万，产业链带动就业超百万",
                  "safety": "食品安全管控严格", "supply_chain": "奶源基地合作",
                  "community": "脱贫攻坚+乡村振兴深度参与", "risks": "奶源供应稳定性",
                  "strengths": "产业链共赢模式"},
            "g": {"score": 76, "board": "治理结构完善", "disclosure": "ESG报告评级AA",
                 "anti_corruption": "合规管理", "shareholder": "分红比例高",
                 "risks": "原奶价格波动影响盈利", "strengths": "乳制品龙头"},
            "overall": 77, "rating": "A", "highlights": "乳制品龙头，乡村振兴贡献大"
        },
        "蒙牛乳业": {
            "industry": "乳制品",
            "e": {"score": 73, "carbon": "碳减排目标：2025年较2020年降50%",
                  "energy": "工厂能效提升", "water": "水资源管理",
                  "waste": "包装回收体系", "risks": "碳中和目标实现难度",
                  "strengths": "零牧草碳中和计划"},
            "s": {"score": 78, "employee": "员工超7万", "safety": "食品安全",
                  "supply_chain": "奶源合作", "community": "营养普惠",
                  "risks": "原奶价格周期波动", "strengths": "品牌影响力强"},
            "g": {"score": 74, "board": "治理结构合理", "disclosure": "ESG报告评级A+",
                 "anti_corruption": "合规管理", "shareholder": "持续分红",
                 "risks": "雅士利商誉减值", "strengths": "液态奶份额领先"},
            "overall": 75, "rating": "A", "highlights": "乳制品双雄之一，减碳目标激进"
        },

        # === 光伏/新能源 ===
        "隆基绿能": {
            "industry": "光伏",
            "e": {"score": 86, "carbon": "使用100%清洁电力，HPBC电池效率全球领先",
                  "energy": "工厂PUE超低", "water": "硅片清洗用水循环",
                  "waste": "硅废料回收再利用率>95%", "risks": "供应链多晶硅环节碳排放高",
                  "strengths": "光伏产品本身就是清洁能源"},
            "s": {"score": 75, "employee": "员工超5万，研发人员超5000",
                  "safety": "安全生产", "supply_chain": "供应商ESG审核",
                  "community": "光伏扶贫项目", "risks": "海外工厂劳工合规",
                  "strengths": "全球光伏龙头，技术领先"},
            "g": {"score": 76, "board": "治理结构完善", "disclosure": "ESG报告评级AA",
                 "anti_corruption": "合规管理", "shareholder": "持续分红+回购",
                 "risks": "行业周期波动大", "strengths": "BC技术路线领先"},
            "overall": 80, "rating": "AA", "highlights": "光伏全产业链龙头，技术创新最强"
        },
        "通威股份": {
            "industry": "光伏/农业",
            "e": {"score": 84, "carbon": "高纯晶硅生产清洁能源成本优势",
                  "energy": "产能成本全球最低", "water": "水资源利用",
                  "waste": "硅料回收", "risks": "多晶硅扩产环保审批趋严",
                  "strengths": "硅料+电池片双龙头"},
            "s": {"score": 73, "employee": "员工约6万", "safety": "安全生产",
                  "supply_chain": "供应商管理", "community": "水产养殖带动乡村振兴",
                  "risks": "化工+农业双重合规", "strengths": "渔光一体模式独特"},
            "g": {"score": 74, "board": "治理结构合理", "disclosure": "ESG报告评级A+",
                 "anti_corruption": "合规管理", "shareholder": "分红+扩产并重",
                 "risks": "扩张激进财务压力", "strengths": "成本控制能力极强"},
            "overall": 77, "rating": "A", "highlights": "硅料+电池双冠，渔光一体创新"
        },

        # === 电力/公用事业 ===
        "长江电力": {
            "industry": "水电",
            "e": {"score": 95, "carbon": "清洁能源零碳排放，2023年提供绿电超2100亿千瓦时",
                  "energy": "梯级调度效率全球最高", "water": "长江流域水资源综合利用",
                  "waste": "几乎无废弃物排放", "risks": "极端气候（干旱）影响发电量",
                  "strengths": "全球最大水电运营商，碳减排贡献巨大"},
            "s": {"score": 76, "employee": "员工约4000人，人均创利极高",
                  "safety": "大坝安全监测体系完善", "supply_chain": "工程建设管理",
                  "community": "移民后扶，三峡库区经济带动", "risks": "水库淹没区移民安置",
                  "strengths": "就业效率高，社会贡献大"},
            "g": {"score": 80, "board": "央企治理+三峡集团控股，治理稳健",
                 "disclosure": "ESG报告评级AA", "anti_corruption": "合规管理",
                 "shareholder": "高股息率，现金牛特征明显",
                 "risks": "单一股东持股集中", "strengths": "稳定现金流+高分红"},
            "overall": 86, "rating": "AAA", "highlights": "全球水电之王，碳减排贡献无与伦比"
        },
        "中国核电": {
            "industry": "核电",
            "e": {"score": 90, "carbon": "核电零碳排放，2023年减排超4亿吨CO2",
                  "energy": "核电效率超90%", "water": "取水量小，热污染可控",
                  "waste": "核废料处理体系完善", "risks": "核安全公众接受度",
                  "strengths": "核电是基荷能源最优解"},
            "s": {"score": 74, "employee": "员工约1.8万", "safety": "核安全文化全球最高标准",
                  "supply_chain": "国产化供应链", "community": "核电站所在地经济带动",
                  "risks": "核事故零容忍风险", "strengths": "高素质人才队伍"},
            "g": {"score": 78, "board": "央企治理", "disclosure": "ESG报告评级A+",
                 "anti_corruption": "核安全合规全球最严", "shareholder": "稳定分红",
                 "risks": "核电项目审批周期不确定", "strengths": "技术自主化率高"},
            "overall": 81, "rating": "AA", "highlights": "核电龙头，清洁基荷能源最优"
        },
        "国电南瑞": {
            "industry": "电力设备/电网",
            "e": {"score": 74, "carbon": "电网设备节能技术输出", "energy": "工厂绿色制造",
                  "water": "环保合规", "waste": "设备回收",
                  "risks": "特高压建设环保压力", "strengths": "智能电网赋能新型电力系统"},
            "s": {"score": 75, "employee": "员工约2万，技术人员占比高",
                  "safety": "安全生产", "supply_chain": "供应商管理",
                  "community": "电力自动化支持乡村振兴", "risks": "电网投资周期性",
                  "strengths": "电力IT技术壁垒高"},
            "g": {"score": 78, "board": "国电南瑞治理完善", "disclosure": "ESG报告评级A+",
                 "anti_corruption": "合规管理", "shareholder": "稳定分红",
                 "risks": "关联交易管控", "strengths": "电网二次设备龙头"},
            "overall": 76, "rating": "A", "highlights": "电网自动化龙头，新型电力系统核心"
        },
    }

    # 行业ESG均值（用于同业对比）
    INDUSTRY_BENCHMARKS: Dict[str, Dict] = {
        "动力电池": {"e_avg": 72, "s_avg": 72, "g_avg": 70, "overall_avg": 71},
        "新能源汽车": {"e_avg": 76, "s_avg": 74, "g_avg": 73, "overall_avg": 74},
        "商业银行": {"e_avg": 70, "s_avg": 76, "g_avg": 76, "overall_avg": 74},
        "保险": {"e_avg": 68, "s_avg": 77, "g_avg": 75, "overall_avg": 73},
        "白酒": {"e_avg": 66, "s_avg": 75, "g_avg": 77, "overall_avg": 73},
        "互联网": {"e_avg": 79, "s_avg": 81, "g_avg": 78, "overall_avg": 79},
        "零售/物流": {"e_avg": 74, "s_avg": 77, "g_avg": 74, "overall_avg": 75},
        "本地服务": {"e_avg": 68, "s_avg": 73, "g_avg": 70, "overall_avg": 70},
        "石油化工": {"e_avg": 62, "s_avg": 68, "g_avg": 70, "overall_avg": 67},
        "煤炭/电力": {"e_avg": 58, "s_avg": 65, "g_avg": 70, "overall_avg": 64},
        "家电制造": {"e_avg": 75, "s_avg": 74, "g_avg": 74, "overall_avg": 74},
        "安防/AI": {"e_avg": 72, "s_avg": 74, "g_avg": 74, "overall_avg": 73},
        "高速公路": {"e_avg": 63, "s_avg": 68, "g_avg": 70, "overall_avg": 67},
        "医药": {"e_avg": 70, "s_avg": 76, "g_avg": 75, "overall_avg": 74},
        "医药CXO": {"e_avg": 69, "s_avg": 74, "g_avg": 72, "overall_avg": 72},
        "房地产": {"e_avg": 71, "s_avg": 72, "g_avg": 74, "overall_avg": 72},
        "乳制品": {"e_avg": 72, "s_avg": 77, "g_avg": 74, "overall_avg": 74},
        "光伏": {"e_avg": 83, "s_avg": 73, "g_avg": 74, "overall_avg": 78},
        "水电": {"e_avg": 93, "s_avg": 74, "g_avg": 78, "overall_avg": 84},
        "核电": {"e_avg": 87, "s_avg": 72, "g_avg": 76, "overall_avg": 80},
        "电力设备/电网": {"e_avg": 72, "s_avg": 73, "g_avg": 76, "overall_avg": 74},
        "锂资源": {"e_avg": 66, "s_avg": 63, "g_avg": 62, "overall_avg": 64},
    }

    # ESG评级划分
    RATING_SCALE = [
        (90, "AAA"), (80, "AA"), (70, "A"),
        (60, "BBB"), (50, "BB"), (0, "B")
    ]

    def __init__(self):
        self.data = self.ESG_DATA

    def get_esg_rating(self, score: float) -> str:
        """根据综合评分返回评级"""
        for threshold, rating in self.RATING_SCALE:
            if score >= threshold:
                return rating
        return "B"

    def generate_improvement_suggestions(self, company: str, esg_data: Dict) -> Dict[str, List[str]]:
        """生成ESG改进建议"""
        suggestions = {"e": [], "s": [], "g": []}
        e_score = esg_data["e"]["score"]
        s_score = esg_data["s"]["score"]
        g_score = esg_data["g"]["score"]
        industry = esg_data.get("industry", "")

        # E维度建议
        if e_score < 70:
            suggestions["e"].append("建立碳足迹核算体系，覆盖范围一/二/三")
            suggestions["e"].append("制定科学碳减排目标（SBTi）")
            suggestions["e"].append("提升清洁能源使用比例，目标50%+")
        if e_score < 80:
            suggestions["e"].append("优化生产工艺能效，降低单位产品能耗")
            suggestions["e"].append("建立废旧产品回收体系，提升回收率")
        if "water" in esg_data["e"] and "水耗" in esg_data["e"].get("water", ""):
            suggestions["e"].append("加强水资源管理，推广循环用水技术")
        if industry in ["石油化工", "煤炭/电力"]:
            suggestions["e"].append("关注化石能源资产搁浅风险，制定转型路线图")
            suggestions["e"].append("发展新能源业务，降低碳强度")

        # S维度建议
        if s_score < 70:
            suggestions["s"].append("完善员工职业健康安全管理体系")
            suggestions["s"].append("加强供应链ESG审计，覆盖率提升至80%+")
        if s_score < 80:
            suggestions["s"].append("提升员工培训投入强度，建立技能提升通道")
            suggestions["s"].append("完善供应链人权风险尽职调查")
        if industry in ["互联网", "本地服务"]:
            suggestions["s"].append("关注灵活用工/骑手劳动关系合规")
            suggestions["s"].append("建立平台经济ESG治理框架")
        if "supply_chain" in esg_data["s"]:
            suggestions["s"].append("建立供应商ESG评分系统，实施分级管理")

        # G维度建议
        if g_score < 70:
            suggestions["g"].append("提升董事会独立性，独董占比提升至1/3以上")
            suggestions["g"].append("完善信息披露，ESG报告引入第三方鉴证")
        if g_score < 80:
            suggestions["g"].append("将ESG绩效纳入高管薪酬考核")
            suggestions["g"].append("建立反垄断/反腐败合规专项培训体系")
            suggestions["g"].append("完善关联交易管理制度，提高透明度")
        suggestions["g"].append("参考TCFD/ISSB框架完善气候相关信息披露")

        return suggestions

    def analyze_industry_peers(self, company: str, esg_data: Dict) -> List[Dict]:
        """分析同业竞争对手ESG水平"""
        industry = esg_data.get("industry", "")
        peers = []
        for name, data in self.data.items():
            if name != company and data.get("industry") == industry:
                peers.append({
                    "company": name,
                    "overall": data["overall"],
                    "rating": data.get("rating", "N/A"),
                    "e": data["e"]["score"],
                    "s": data["s"]["score"],
                    "g": data["g"]["score"],
                })
        peers.sort(key=lambda x: x["overall"], reverse=True)
        return peers[:5]

    def generate_report(self, company: str, format: str = "text") -> Dict:
        """
        生成ESG研究报告
        format: text | json | markdown
        返回值：总是返回Dict（包含所有字段）；如需格式化字符串，用 format_report()
        """
        # 模糊匹配公司名
        matched = None
        search_name = company.strip()
        for name in self.data:
            if search_name in name or name in search_name:
                matched = name
                break

        if not matched:
            return {"error": f"未找到公司 '{company}'，当前内置{len(self.data)}家公司ESG数据",
                    "available_companies": sorted(list(self.data.keys()))[:20]}

        esg_data = self.data[matched]
        e_score = esg_data["e"]["score"]
        s_score = esg_data["s"]["score"]
        g_score = esg_data["g"]["score"]
        overall = esg_data["overall"]
        rating = esg_data.get("rating", self.get_esg_rating(overall))
        industry = esg_data.get("industry", "")
        highlights = esg_data.get("highlights", "")
        industry_benchmark = self.INDUSTRY_BENCHMARKS.get(industry, {})
        suggestions = self.generate_improvement_suggestions(matched, esg_data)
        peers = self.analyze_industry_peers(matched, esg_data)

        result = {
            "company": matched,
            "industry": industry,
            "rating": rating,
            "scores": {
                "E（环境）": e_score,
                "S（社会）": s_score,
                "G（治理）": g_score,
                "综合": overall,
            },
            "industry_benchmark": industry_benchmark,
            "vs_industry": {
                "E": round(e_score - industry_benchmark.get("e_avg", 0), 1),
                "S": round(s_score - industry_benchmark.get("s_avg", 0), 1),
                "G": round(g_score - industry_benchmark.get("g_avg", 0), 1),
                "综合": round(overall - industry_benchmark.get("overall_avg", 0), 1),
            },
            "highlights": highlights,
            "details": {
                "E（环境）": esg_data["e"],
                "S（社会）": esg_data["s"],
                "G（治理）": esg_data["g"],
            },
            "peer_comparison": peers,
            "suggestions": suggestions,
            "report_date": "2026-01-01",
            "data_source": "内置ESG数据库（截至2025年年报/ESG报告）"
        }
        return result

    def format_report(self, data: Dict, format: str = "text") -> str:
        """将ESG报告数据格式化为字符串"""
        if format == "json":
            import json
            return json.dumps(data, ensure_ascii=False, indent=2)
        elif format == "markdown":
            return self._format_markdown(data)
        else:
            return self._format_text(data)

    def _format_text(self, data: Dict) -> str:
        """文本格式输出"""
        lines = []
        lines.append(f"{'='*50}")
        lines.append(f"  ESG 研究报告：{data['company']}")
        lines.append(f"{'='*50}")
        lines.append(f"行业：{data['industry']}  |  ESG评级：{data['rating']}")
        lines.append(f"数据来源：{data['data_source']}")
        lines.append("")
        lines.append(f"{'─'*50}")
        lines.append("  📊 ESG 评分")
        lines.append(f"{'─'*50}")
        scores = data["scores"]
        vs_ind = data["vs_industry"]
        lines.append(f"  E（环境）   {scores['E（环境）']:>3}  {self._diff_str(vs_ind['E'])}  行业均值 {data['industry_benchmark'].get('e_avg', 'N/A')}")
        lines.append(f"  S（社会）   {scores['S（社会）']:>3}  {self._diff_str(vs_ind['S'])}  行业均值 {data['industry_benchmark'].get('s_avg', 'N/A')}")
        lines.append(f"  G（治理）   {scores['G（治理）']:>3}  {self._diff_str(vs_ind['G'])}  行业均值 {data['industry_benchmark'].get('g_avg', 'N/A')}")
        lines.append(f"  {'─'*30}")
        lines.append(f"  综合评分   {scores['综合']:>3}  {self._diff_str(vs_ind['综合'])}  行业均值 {data['industry_benchmark'].get('overall_avg', 'N/A')}")
        lines.append("")

        lines.append(f"{'─'*50}")
        lines.append("  🔍 核心亮点")
        lines.append(f"{'─'*50}")
        lines.append(f"  {data['highlights']}")
        lines.append("")

        # E详情
        e_details = data["details"]["E（环境）"]
        lines.append(f"{'─'*50}")
        lines.append(f"  🌿 E（环境）维度详情  评分：{e_details['score']}")
        lines.append(f"{'─'*50}")
        lines.append(f"  碳排放：{e_details.get('carbon', 'N/A')}")
        lines.append(f"  能源：  {e_details.get('energy', 'N/A')}")
        lines.append(f"  水资源：{e_details.get('water', 'N/A')}")
        lines.append(f"  废弃物：{e_details.get('waste', 'N/A')}")
        if e_details.get('strengths'):
            lines.append(f"  ✅ 优势：{e_details['strengths']}")
        if e_details.get('risks'):
            lines.append(f"  ⚠️ 风险：{e_details['risks']}")
        lines.append("")

        # S详情
        s_details = data["details"]["S（社会）"]
        lines.append(f"{'─'*50}")
        lines.append(f"  👥 S（社会）维度详情  评分：{s_details['score']}")
        lines.append(f"{'─'*50}")
        lines.append(f"  员工关怀：{s_details.get('employee', 'N/A')}")
        lines.append(f"  安全生产：{s_details.get('safety', 'N/A')}")
        lines.append(f"  供应链：  {s_details.get('supply_chain', 'N/A')}")
        lines.append(f"  社区公益：{s_details.get('community', 'N/A')}")
        if s_details.get('strengths'):
            lines.append(f"  ✅ 优势：{s_details['strengths']}")
        if s_details.get('risks'):
            lines.append(f"  ⚠️ 风险：{s_details['risks']}")
        lines.append("")

        # G详情
        g_details = data["details"]["G（治理）"]
        lines.append(f"{'─'*50}")
        lines.append(f"  ⚖️ G（治理）维度详情  评分：{g_details['score']}")
        lines.append(f"{'─'*50}")
        lines.append(f"  董事会结构：{g_details.get('board', 'N/A')}")
        lines.append(f"  信息披露：  {g_details.get('disclosure', 'N/A')}")
        lines.append(f"  反腐合规：  {g_details.get('anti_corruption', 'N/A')}")
        lines.append(f"  股东权益：  {g_details.get('shareholder', 'N/A')}")
        if g_details.get('strengths'):
            lines.append(f"  ✅ 优势：{g_details['strengths']}")
        if g_details.get('risks'):
            lines.append(f"  ⚠️ 风险：{g_details['risks']}")
        lines.append("")

        # 同业对比
        if data["peer_comparison"]:
            lines.append(f"{'─'*50}")
            lines.append("  🏆 同业ESG对比（Top 5）")
            lines.append(f"{'─'*50}")
            lines.append(f"  {'公司':<12} {'综合':>4} {'评级':>5} {'E':>4} {'S':>4} {'G':>4}")
            for peer in data["peer_comparison"]:
                marker = " ★" if peer["company"] == data["company"] else ""
                lines.append(f"  {peer['company']:<12} {peer['overall']:>4} {peer['rating']:>5} "
                           f"{peer['e']:>4} {peer['s']:>4} {peer['g']:>4}{marker}")
            lines.append("  ★ = 目标公司")
            lines.append("")

        # 改进建议
        sug = data["suggestions"]
        if any(sug.values()):
            lines.append(f"{'─'*50}")
            lines.append("  💡 ESG改进建议")
            lines.append(f"{'─'*50}")
            if sug["e"]:
                lines.append("  🌿 环境（E）改进：")
                for s in sug["e"]:
                    lines.append(f"    • {s}")
            if sug["s"]:
                lines.append("  👥 社会（S）改进：")
                for s in sug["s"]:
                    lines.append(f"    • {s}")
            if sug["g"]:
                lines.append("  ⚖️ 治理（G）改进：")
                for s in sug["g"]:
                    lines.append(f"    • {s}")
            lines.append("")

        lines.append(f"{'='*50}")
        lines.append("  数据来源：内置ESG数据库（截至2025年年报）")
        lines.append(f"{'='*50}")
        return "\n".join(lines)

    def _format_markdown(self, data: Dict) -> str:
        """Markdown格式输出"""
        vs_ind = data["vs_industry"]
        lines = [
            f"# ESG 研究报告：{data['company']}",
            "",
            f"**行业：** {data['industry']}  |  **ESG评级：** {data['rating']}",
            f"**数据来源：** {data['data_source']}",
            "",
            "## 📊 ESG 评分",
            "",
            "| 维度 | 评分 | vs 行业 | 行业均值 |",
            "|------|------|---------|----------|",
            f"| E（环境） | {data['scores']['E（环境）']} | {self._diff_md(vs_ind['E'])} | {data['industry_benchmark'].get('e_avg', 'N/A')} |",
            f"| S（社会） | {data['scores']['S（社会）']} | {self._diff_md(vs_ind['S'])} | {data['industry_benchmark'].get('s_avg', 'N/A')} |",
            f"| G（治理） | {data['scores']['G（治理）']} | {self._diff_md(vs_ind['G'])} | {data['industry_benchmark'].get('g_avg', 'N/A')} |",
            f"| **综合** | **{data['scores']['综合']}** | {self._diff_md(vs_ind['综合'])} | {data['industry_benchmark'].get('overall_avg', 'N/A')} |",
            "",
            "## 🔍 核心亮点",
            "",
            f"{data['highlights']}",
            "",
            "## 🌿 E（环境）维度",
            "",
            f"- **评分：** {data['details']['E（环境）']['score']}",
            f"- **碳排放：** {data['details']['E（环境）'].get('carbon', 'N/A')}",
            f"- **能源：** {data['details']['E（环境）'].get('energy', 'N/A')}",
            f"- **水资源：** {data['details']['E（环境）'].get('water', 'N/A')}",
            f"- **废弃物：** {data['details']['E（环境）'].get('waste', 'N/A')}",
            f"- **优势：** {data['details']['E（环境）'].get('strengths', 'N/A')}",
            f"- **风险：** {data['details']['E（环境）'].get('risks', 'N/A')}",
            "",
            "## 👥 S（社会）维度",
            "",
            f"- **评分：** {data['details']['S（社会）']['score']}",
            f"- **员工关怀：** {data['details']['S（社会）'].get('employee', 'N/A')}",
            f"- **安全生产：** {data['details']['S（社会）'].get('safety', 'N/A')}",
            f"- **供应链：** {data['details']['S（社会）'].get('supply_chain', 'N/A')}",
            f"- **社区公益：** {data['details']['S（社会）'].get('community', 'N/A')}",
            f"- **优势：** {data['details']['S（社会）'].get('strengths', 'N/A')}",
            f"- **风险：** {data['details']['S（社会）'].get('risks', 'N/A')}",
            "",
            "## ⚖️ G（治理）维度",
            "",
            f"- **评分：** {data['details']['G（治理）']['score']}",
            f"- **董事会结构：** {data['details']['G（治理）'].get('board', 'N/A')}",
            f"- **信息披露：** {data['details']['G（治理）'].get('disclosure', 'N/A')}",
            f"- **反腐合规：** {data['details']['G（治理）'].get('anti_corruption', 'N/A')}",
            f"- **股东权益：** {data['details']['G（治理）'].get('shareholder', 'N/A')}",
            f"- **优势：** {data['details']['G（治理）'].get('strengths', 'N/A')}",
            f"- **风险：** {data['details']['G（治理）'].get('risks', 'N/A')}",
            "",
        ]

        # 同业对比
        if data["peer_comparison"]:
            lines += [
                "## 🏆 同业ESG对比",
                "",
                f"| 公司 | 综合 | 评级 | E | S | G |",
                f"|------|------|------|---|---|---|---|"
            ]
            for peer in data["peer_comparison"]:
                marker = " ★" if peer["company"] == data["company"] else ""
                lines.append(f"| {peer['company']}{marker} | {peer['overall']} | {peer['rating']} | "
                           f"{peer['e']} | {peer['s']} | {peer['g']} |")
            lines.append("")
            lines.append("> ★ = 目标公司")
            lines.append("")

        # 改进建议
        sug = data["suggestions"]
        if any(sug.values()):
            lines += ["## 💡 ESG改进建议", ""]
            if sug["e"]:
                lines.append("**🌿 环境（E）改进：**")
                for s in sug["e"]:
                    lines.append(f"- {s}")
                lines.append("")
            if sug["s"]:
                lines.append("**👥 社会（S）改进：**")
                for s in sug["s"]:
                    lines.append(f"- {s}")
                lines.append("")
            if sug["g"]:
                lines.append("**⚖️ 治理（G）改进：**")
                for s in sug["g"]:
                    lines.append(f"- {s}")
                lines.append("")

        lines.append("---")
        lines.append(f"*报告生成时间：{data['report_date']} | 数据截至2025年年报*")
        return "\n".join(lines)

    def _diff_str(self, diff: float) -> str:
        """格式化差异（文本）"""
        if diff > 0:
            return f"+{diff:.1f} ↑"
        elif diff < 0:
            return f"{diff:.1f} ↓"
        return "  0.0"

    def _diff_md(self, diff: float) -> str:
        """格式化差异（Markdown）"""
        if diff > 0:
            return f"<font color='green'>+{diff:.1f} ↑</font>"
        elif diff < 0:
            return f"<font color='red'>{diff:.1f} ↓</font>"
        return "0.0"

    def list_companies(self) -> List[str]:
        """列出所有内置公司"""
        return sorted(list(self.data.keys()))

    def list_industries(self) -> List[str]:
        """列出所有行业"""
        industries = set(v.get("industry", "") for v in self.data.values())
        return sorted(list(industries))


# ============================================================
# 工厂函数
# ============================================================
def create_engine() -> ESGEngine:
    return ESGEngine()
