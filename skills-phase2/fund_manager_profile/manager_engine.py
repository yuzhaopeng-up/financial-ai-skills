# -*- coding: utf-8 -*-
"""
基金经理画像引擎
Fund Manager Profile Engine

内置20+知名基金经理数据，支持快速查询基金经理画像报告
"""

from typing import Dict, List, Optional, Any
import json
import re


class FundManagerEngine:
    """基金经理画像引擎"""

    # ============================================================
    # 内置基金经理数据库
    # ============================================================
    MANAGERS: Dict[str, Dict[str, Any]] = {

        "张坤": {
            "name": "张坤",
            "fund_company": "某头部基金公司",
            "representative_fund": "某基金公司蓝筹精选混合（XXXXXX）",
            "representative_fund_2": "某基金公司优质精选混合（XXXXXX）",
            "experience_years": 18,
            "career_start": "2006年加入某基金公司",
            "first_fund_year": "2012年",
            "management_scale_bn": 650,  # 亿元
            "investment_style": ["大盘成长", "价值投资", "长期持有"],
            "style_tags": ["逆向投资", "高ROE", "商业模式护城河"],
            "area_expertise": ["消费", "白酒", "医疗器械", "互联网"],
            "holding_preference": {
                "top_holdings": ["某白酒龙头企业", "某白酒企业", "泸州老窖", "某互联网巨头", "美团"],
                "sector_concentration": "高",
                "stock_concentration": "高（前十大持仓占比60%-80%）",
                "holding_period": "长期（平均2-3年）",
            },
            "performance": {
                "cumulative_return_5y": "约180%（截至2024年末）",
                "annual_return_5y": "约20%",
                "max_drawdown": "-45%（2021-2022年回撤）",
                "sharpe_ratio": "约1.2",
            },
            "risk特征": {
                "volatility": "较高",
                "drawdown_control": "中等（2021年回撤较大）",
                "风格稳定性": "稳定",
            },
            "awards": [
                "晨星奖（2020）",
                "金牛奖（2020/2021）",
                "明星基金奖（2020/2021）",
                "金基金奖（2021）",
            ],
            "famous_saying": "好公司比便宜更重要；把鸡蛋放在稳定增长的篮子里",
            "education": "清华大学管理学硕士",
            "personality": "低调务实，专注基本面，偏好商业模式清晰的行业龙头",
        },

        "朱少醒": {
            "name": "朱少醒",
            "fund_company": "某头部基金公司",
            "representative_fund": "某明星基金精选成长混合（XXXXXX）",
            "experience_years": 20,
            "career_start": "2000年加入富国",
            "first_fund_year": "2005年",
            "management_scale_bn": 380,
            "investment_style": ["均衡配置", "成长风格", "长期持有"],
            "style_tags": ["自下而上", "高仓位运作", "低换手率"],
            "area_expertise": ["制造业", "消费", "医药", "金融"],
            "holding_preference": {
                "top_holdings": ["某白酒龙头企业", "某股份制银行", "某大型保险集团", "某乳制品龙头企业", "某城商行"],
                "sector_concentration": "中",
                "stock_concentration": "中等（前十大约50%）",
                "holding_period": "超长期（部分持仓超10年）",
            },
            "performance": {
                "cumulative_return_5y": "约160%（截至2024年末）",
                "annual_return_5y": "约18%",
                "max_drawdown": "-40%（2015年/2018年/2022年）",
                "sharpe_ratio": "约1.1",
            },
            "risk特征": {
                "volatility": "中等",
                "drawdown_control": "中等",
                "风格稳定性": "非常稳定",
            },
            "awards": [
                "金牛奖（2015/2020）",
                "明星基金奖（2015/2020）",
                "金基金奖（2015）",
            ],
            "famous_saying": "在有成长性的行业里持有最优质的公司",
            "education": "上海财经大学管理学硕士",
            "personality": "极度专注，长期主义，业内罕见的'一基到底'基金经理",
        },

        "谢治宇": {
            "name": "谢治宇",
            "fund_company": "兴证全球基金管理有限公司",
            "representative_fund": "兴全合润混合（163406）",
            "representative_fund_2": "兴全合宜混合（163417）",
            "experience_years": 16,
            "career_start": "2007年加入兴全",
            "first_fund_year": "2013年",
            "management_scale_bn": 580,
            "investment_style": ["均衡配置", "成长价值兼顾", "灵活仓位"],
            "style_tags": ["行业分散", "个股集中", "择时灵活"],
            "area_expertise": ["制造业", "消费电子", "医药", "新能源", "金融"],
            "holding_preference": {
                "top_holdings": ["某家电龙头企业", "三安光电", "海康威视", "晶盛机电", "芒果超媒"],
                "sector_concentration": "低-中",
                "stock_concentration": "中等（前十大约45%）",
                "holding_period": "中长期（1-3年）",
            },
            "performance": {
                "cumulative_return_5y": "约150%（截至2024年末）",
                "annual_return_5y": "约17%",
                "max_drawdown": "-38%（2022年）",
                "sharpe_ratio": "约1.1",
            },
            "risk特征": {
                "volatility": "中等",
                "drawdown_control": "较好",
                "风格稳定性": "稳定",
            },
            "awards": [
                "晨星奖（2019）",
                "金牛奖（2019/2020/2022）",
                "明星基金奖（2019/2020）",
            ],
            "famous_saying": "用合理价格买优质公司，而非用便宜价格买一般公司",
            "education": "复旦大学经济学硕士",
            "personality": "稳健平衡，重视风险收益比，攻防兼备",
        },

        "刘彦春": {
            "name": "刘彦春",
            "fund_company": "景顺长城基金管理有限公司",
            "representative_fund": "景顺长城新兴成长混合（260108）",
            "representative_fund_2": "景顺长城内需增长混合（260104）",
            "experience_years": 17,
            "career_start": "2008年加入景顺长城",
            "first_fund_year": "2010年",
            "management_scale_bn": 420,
            "investment_style": ["大盘成长", "消费为主", "高仓位运作"],
            "style_tags": ["大消费", "高ROE", "行业集中"],
            "area_expertise": ["白酒", "免税", "医药", "食品饮料", "消费电子"],
            "holding_preference": {
                "top_holdings": ["某白酒龙头企业", "某白酒企业", "中国中免", "泸州老窖", "迈瑞医疗"],
                "sector_concentration": "高（消费占比60%以上）",
                "stock_concentration": "高（前十大60-70%）",
                "holding_period": "长期（2-4年）",
            },
            "performance": {
                "cumulative_return_5y": "约200%（消费黄金期）",
                "annual_return_5y": "约22%",
                "max_drawdown": "-50%（2021-2022年回撤）",
                "sharpe_ratio": "约1.3",
            },
            "risk特征": {
                "volatility": "较高",
                "drawdown_control": "弱（行业集中风险）",
                "风格稳定性": "稳定",
            },
            "awards": [
                "晨星奖（2020）",
                "金牛奖（2020/2021）",
                "明星基金奖（2020）",
            ],
            "famous_saying": "消费升级是长期主线，竞争格局决定利润分配",
            "education": "中国人民大学经济学硕士",
            "personality": "专注消费赛道，偏好高壁垒龙头，风格鲜明",
        },

        "董承非": {
            "name": "董承非",
            "fund_company": "兴证全球基金管理有限公司",
            "representative_fund": "兴全趋势投资混合（163402）",
            "experience_years": 19,
            "career_start": "2003年加入兴全",
            "first_fund_year": "2007年",
            "management_scale_bn": 250,
            "investment_style": ["均衡配置", "价值风格", "适度择时"],
            "style_tags": ["逆向投资", "低估值", "仓位管理"],
            "area_expertise": ["制造业", "地产链", "金融", "消费", "周期"],
            "holding_preference": {
                "top_holdings": ["紫金矿业", "万科A", "某大型保险集团", "保利发展", "三安光电"],
                "sector_concentration": "低",
                "stock_concentration": "分散（前十大约40%）",
                "holding_period": "中长期（1-3年）",
            },
            "performance": {
                "cumulative_return_5y": "约120%（截至2024年末）",
                "annual_return_5y": "约14%",
                "max_drawdown": "-35%（2015年/2018年）",
                "sharpe_ratio": "约0.9",
            },
            "risk特征": {
                "volatility": "中等偏低",
                "drawdown_control": "较好",
                "风格稳定性": "稳定",
            },
            "awards": [
                "金牛奖（2015/2017/2019）",
                "明星基金奖（2017/2019）",
                "金基金奖（2019）",
            ],
            "famous_saying": "投资要相信均值回归，低迷处播种，高涨时收获",
            "education": "上海交通大学理学硕士",
            "personality": "谨慎稳健，重视风险控制，行业轮动能力强",
        },

        "周蔚文": {
            "name": "周蔚文",
            "fund_company": "中欧基金管理有限公司",
            "representative_fund": "中欧新蓝筹混合（166002）",
            "representative_fund_2": "中欧新趋势混合（166001）",
            "experience_years": 22,
            "career_start": "2002年（从业）",
            "first_fund_year": "2006年",
            "management_scale_bn": 350,
            "investment_style": ["行业轮动", "成长价值均衡", "宏观视角"],
            "style_tags": ["自上而下", "行业景气度", "轮动配置"],
            "area_expertise": ["消费电子", "医药", "新能源", "金融", "制造业"],
            "holding_preference": {
                "top_holdings": ["立讯精密", "恒瑞医药", "某新能源龙头企业", "某互联网券商", "歌尔股份"],
                "sector_concentration": "中",
                "stock_concentration": "中（前十大约50%）",
                "holding_period": "中短期（0.5-2年）",
            },
            "performance": {
                "cumulative_return_5y": "约140%（截至2024年末）",
                "annual_return_5y": "约16%",
                "max_drawdown": "-38%（2022年）",
                "sharpe_ratio": "约1.0",
            },
            "risk特征": {
                "volatility": "中等",
                "drawdown_control": "中等",
                "风格稳定性": "灵活",
            },
            "awards": [
                "金牛奖（2016/2018/2020）",
                "明星基金奖（2016/2018）",
                "金基金奖（2020）",
            ],
            "famous_saying": "跟随时代趋势，在高景气赛道中寻找确定性增长",
            "education": "北京大学管理学硕士",
            "personality": "宏观视野强，行业配置灵活，适应不同市场风格",
        },

        "傅友兴": {
            "name": "傅友兴",
            "fund_company": "广发基金管理有限公司",
            "representative_fund": "广发稳健增长混合（270002）",
            "experience_years": 19,
            "career_start": "2004年加入广发",
            "first_fund_year": "2013年",
            "management_scale_bn": 280,
            "investment_style": ["股债平衡", "稳健配置", "高仓位权益"],
            "style_tags": ["平衡型", "回撤控制", "低估稳健"],
            "area_expertise": ["医药", "消费", "制造业", "金融"],
            "holding_preference": {
                "top_holdings": ["山东药玻", "我武生物", "长春高新", "华域汽车", "某股份制银行"],
                "sector_concentration": "低",
                "stock_concentration": "分散（前十大约35%）",
                "holding_period": "中长期（1-3年）",
            },
            "performance": {
                "cumulative_return_5y": "约110%（截至2024年末）",
                "annual_return_5y": "约13%",
                "max_drawdown": "-25%（2022年）",
                "sharpe_ratio": "约1.0",
            },
            "risk特征": {
                "volatility": "低",
                "drawdown_control": "优秀",
                "风格稳定性": "非常稳定",
            },
            "awards": [
                "金牛奖（2019/2020）",
                "明星基金奖（2019/2020）",
            ],
            "famous_saying": "稳健是长期复利的基石，控制回撤比追求高收益更重要",
            "education": "中国人民大学经济学硕士",
            "personality": "极度稳健，回撤控制能力极强，适合保守型投资者",
        },

        "何帅": {
            "name": "何帅",
            "fund_company": "交银施罗德基金管理有限公司",
            "representative_fund": "交银阿尔法核心混合（519712）",
            "representative_fund_2": "交银优势行业灵活配置混合（519697）",
            "experience_years": 14,
            "career_start": "2010年加入交银施罗德",
            "first_fund_year": "2015年",
            "management_scale_bn": 180,
            "investment_style": ["中小盘成长", "个股挖掘", "高换手"],
            "style_tags": ["成长猎手", "高仓位", "择股能力强"],
            "area_expertise": ["软件信息", "电子", "医药", "化工", "新材料"],
            "holding_preference": {
                "top_holdings": ["恒生电子", "广联达", "某新能源龙头企业", "药明康德", "立讯精密"],
                "sector_concentration": "中",
                "stock_concentration": "中等（前十大约50%）",
                "holding_period": "中短期（0.5-1.5年）",
            },
            "performance": {
                "cumulative_return_5y": "约170%（截至2024年末）",
                "annual_return_5y": "约19%",
                "max_drawdown": "-32%（2022年）",
                "sharpe_ratio": "约1.2",
            },
            "risk特征": {
                "volatility": "较高",
                "drawdown_control": "中等",
                "风格稳定性": "灵活",
            },
            "awards": [
                "金牛奖（2019/2020）",
                "明星基金奖（2019/2020）",
            ],
            "famous_saying": "在变化的产业趋势中寻找高成长标的",
            "education": "上海交通大学管理学硕士",
            "personality": "成长型选手，擅长挖掘中小盘黑马，换手率较高",
        },

        "周应波": {
            "name": "周应波",
            "fund_company": "中欧基金管理有限公司",
            "representative_fund": "中欧时代先锋股票（001938）",
            "experience_years": 14,
            "career_start": "2010年从业",
            "first_fund_year": "2015年",
            "management_scale_bn": 200,
            "investment_style": ["科技成长", "制造业升级", "高仓位运作"],
            "style_tags": ["时代趋势", "制造业", "高增长"],
            "area_expertise": ["新能源汽车", "光伏", "半导体", "消费电子", "制造业升级"],
            "holding_preference": {
                "top_holdings": ["某新能源龙头企业", "某光伏龙头企业", "亿纬锂能", "立讯精密", "三安光电"],
                "sector_concentration": "高（科技制造）",
                "stock_concentration": "高（前十大60-70%）",
                "holding_period": "中长期（1-2年）",
            },
            "performance": {
                "cumulative_return_5y": "约190%（科技红利期）",
                "annual_return_5y": "约21%",
                "max_drawdown": "-42%（2022年）",
                "sharpe_ratio": "约1.2",
            },
            "risk特征": {
                "volatility": "高",
                "drawdown_control": "中等",
                "风格稳定性": "稳定",
            },
            "awards": [
                "金牛奖（2020）",
                "明星基金奖（2020）",
            ],
            "famous_saying": "做科技时代的价值发现者，拥抱制造业升级的历史机遇",
            "education": "北京大学工程学硕士",
            "personality": "专注科技制造，赛道型选手，顺周期进攻性强",
        },

        "赵晓东": {
            "name": "赵晓东",
            "fund_company": "国海富兰克林基金管理有限公司",
            "representative_fund": "国富弹性市值混合（450002）",
            "representative_fund_2": "国富基本面优选混合（457001）",
            "experience_years": 19,
            "career_start": "2005年加入国海富兰克林",
            "first_fund_year": "2009年",
            "management_scale_bn": 150,
            "investment_style": ["价值风格", "低估值", "逆向投资"],
            "style_tags": ["安全边际", "自下而上", "择股不择时"],
            "area_expertise": ["银行", "地产", "制造业", "消费", "保险"],
            "holding_preference": {
                "top_holdings": ["某股份制银行", "某城商行", "某大型保险集团", "万科A", "保利发展"],
                "sector_concentration": "中",
                "stock_concentration": "中等（前十大约50%）",
                "holding_period": "长期（2-5年）",
            },
            "performance": {
                "cumulative_return_5y": "约130%（截至2024年末）",
                "annual_return_5y": "约15%",
                "max_drawdown": "-30%（2018年/2022年）",
                "sharpe_ratio": "约1.0",
            },
            "risk特征": {
                "volatility": "中等偏低",
                "drawdown_control": "较好",
                "风格稳定性": "稳定",
            },
            "awards": [
                "金牛奖（2018/2019）",
                "明星基金奖（2018/2019）",
            ],
            "famous_saying": "安全边际是投资的第一原则，不买贵的，只买对的",
            "education": "复旦大学经济学硕士",
            "personality": "深度价值风格，不追热点，偏好金融地产等传统行业",
        },

        "王宗合": {
            "name": "王宗合",
            "fund_company": "鹏华基金管理有限公司",
            "representative_fund": "鹏华消费优选混合（206007）",
            "experience_years": 17,
            "career_start": "2009年加入鹏华",
            "first_fund_year": "2012年",
            "management_scale_bn": 120,
            "investment_style": ["消费成长", "长期持有", "行业集中"],
            "style_tags": ["大消费", "长期主义", "品牌护城河"],
            "area_expertise": ["白酒", "家电", "食品饮料", "农业", "医疗服务"],
            "holding_preference": {
                "top_holdings": ["某白酒龙头企业", "某白酒企业", "泸州老窖", "洋河股份", "山西汾酒"],
                "sector_concentration": "高（白酒为主）",
                "stock_concentration": "高（前十大60-75%）",
                "holding_period": "超长期（3-5年）",
            },
            "performance": {
                "cumulative_return_5y": "约170%（白酒红利期）",
                "annual_return_5y": "约19%",
                "max_drawdown": "-48%（2021-2022年）",
                "sharpe_ratio": "约1.1",
            },
            "risk特征": {
                "volatility": "较高",
                "drawdown_control": "弱",
                "风格稳定性": "稳定",
            },
            "awards": [
                "金牛奖（2019/2020）",
                "明星基金奖（2019/2020）",
            ],
            "famous_saying": "消费品牌的护城河最深，长期持有优质品牌公司是穿越周期的最佳策略",
            "education": "中国人民大学金融学硕士",
            "personality": "极致消费风格，超配白酒，长期持股不动摇",
        },

        "胡昕炜": {
            "name": "胡昕炜",
            "fund_company": "某头部基金公司管理股份有限公司",
            "representative_fund": "汇添富消费行业混合（000083）",
            "experience_years": 13,
            "career_start": "2011年加入汇添富",
            "first_fund_year": "2016年",
            "management_scale_bn": 380,
            "investment_style": ["消费升级", "大盘成长", "长期持有"],
            "style_tags": ["消费全产业链", "品牌消费", "新兴消费"],
            "area_expertise": ["白酒", "免税", "美妆", "餐饮旅游", "医美"],
            "holding_preference": {
                "top_holdings": ["某白酒龙头企业", "某白酒企业", "中国中免", "泸州老窖", "山西汾酒"],
                "sector_concentration": "高（消费占比70%+）",
                "stock_concentration": "高（前十大65-75%）",
                "holding_period": "长期（2-4年）",
            },
            "performance": {
                "cumulative_return_5y": "约185%（消费黄金期）",
                "annual_return_5y": "约20%",
                "max_drawdown": "-46%（2021-2022年）",
                "sharpe_ratio": "约1.2",
            },
            "risk特征": {
                "volatility": "较高",
                "drawdown_control": "中等",
                "风格稳定性": "稳定",
            },
            "awards": [
                "金牛奖（2020/2021）",
                "明星基金奖（2020/2021）",
            ],
            "famous_saying": "消费升级是贯穿中国经济增长的核心主线",
            "education": "清华大学经济学硕士",
            "personality": "消费赛道全面布局，白酒+新兴消费双轮驱动",
        },

        "杨浩": {
            "name": "杨浩",
            "fund_company": "交银施罗德基金管理有限公司",
            "representative_fund": "交银新生活力灵活配置混合（519772）",
            "experience_years": 12,
            "career_start": "2010年加入交银施罗德",
            "first_fund_year": "2016年",
            "management_scale_bn": 200,
            "investment_style": ["成长风格", "科技创新", "新兴消费"],
            "style_tags": ["TMT", "新兴消费", "高仓位"],
            "area_expertise": ["互联网", "通信", "传媒", "消费电子", "智能制造"],
            "holding_preference": {
                "top_holdings": ["某互联网巨头", "美团", "舜宇光学科技", "海康威视", "芒果超媒"],
                "sector_concentration": "中",
                "stock_concentration": "中等（前十大约50%）",
                "holding_period": "中长期（1-2年）",
            },
            "performance": {
                "cumulative_return_5y": "约160%（互联网红利期）",
                "annual_return_5y": "约18%",
                "max_drawdown": "-40%（2021-2022年）",
                "sharpe_ratio": "约1.1",
            },
            "risk特征": {
                "volatility": "较高",
                "drawdown_control": "中等",
                "风格稳定性": "灵活",
            },
            "awards": [
                "金牛奖（2020）",
                "明星基金奖（2020）",
            ],
            "famous_saying": "科技创新是时代最大红利，顺应产业趋势获取超额收益",
            "education": "复旦大学计算机硕士",
            "personality": "TMT+新兴消费双轮驱动，善于捕捉科技产业变革机会",
        },

        "王培": {
            "name": "王培",
            "fund_company": "中欧基金管理有限公司",
            "representative_fund": "中欧创新成长灵活配置混合（005276）",
            "representative_fund_2": "中欧行业成长混合（166012）",
            "experience_years": 17,
            "career_start": "2007年从业",
            "first_fund_year": "2011年",
            "management_scale_bn": 180,
            "investment_style": ["成长价值均衡", "自下而上", "行业分散"],
            "style_tags": ["质量成长", "全球化视野", "个股精选"],
            "area_expertise": ["化工", "电子", "医药", "新能源", "消费"],
            "holding_preference": {
                "top_holdings": ["万华化学", "某新能源龙头企业", "立讯精密", "华鲁恒升", "中芯国际"],
                "sector_concentration": "低-中",
                "stock_concentration": "中等（前十大约45%）",
                "holding_period": "中长期（1-3年）",
            },
            "performance": {
                "cumulative_return_5y": "约145%（截至2024年末）",
                "annual_return_5y": "约17%",
                "max_drawdown": "-36%（2022年）",
                "sharpe_ratio": "约1.1",
            },
            "risk特征": {
                "volatility": "中等",
                "drawdown_control": "较好",
                "风格稳定性": "稳定",
            },
            "awards": [
                "金牛奖（2019）",
                "明星基金奖（2019）",
            ],
            "famous_saying": "好公司需要好价格，等待是投资最好的朋友",
            "education": "复旦大学化学硕士",
            "personality": "化工+成长双背景，兼顾质量与估值，攻防兼备",
        },

        "刘格菘": {
            "name": "刘格菘",
            "fund_company": "广发基金管理有限公司",
            "representative_fund": "广发双擎升级混合（005911）",
            "representative_fund_2": "广发科技先锋混合（008272）",
            "experience_years": 13,
            "career_start": "2010年从业",
            "first_fund_year": "2017年",
            "management_scale_bn": 520,
            "investment_style": ["科技成长", "高端制造", "高仓位集中"],
            "style_tags": ["半导体", "新能源", "科技追风"],
            "area_expertise": ["半导体", "新能源汽车", "光伏", "医药", "军工"],
            "holding_preference": {
                "top_holdings": ["某新能源龙头企业", "某光伏龙头企业", "亿纬锂能", "圣邦股份", "晶澳科技"],
                "sector_concentration": "高（科技制造）",
                "stock_concentration": "高（前十大65-80%）",
                "holding_period": "中短期（0.5-2年）",
            },
            "performance": {
                "cumulative_return_3y": "约220%（科技牛市）",
                "annual_return_3y": "约48%",
                "max_drawdown": "-55%（2022年）",
                "sharpe_ratio": "约1.4",
            },
            "risk特征": {
                "volatility": "极高",
                "drawdown_control": "弱",
                "风格稳定性": "赛道驱动",
            },
            "awards": [
                "金牛奖（2020）",
                "明星基金奖（2020）",
            ],
            "famous_saying": "顺应时代趋势，在高成长赛道中获取超额收益",
            "education": "中国人民大学经济学博士",
            "personality": "极致科技成长风格，进攻性强，回撤也大，典型的赛道型选手",
        },

        "冯明远": {
            "name": "冯明远",
            "fund_company": "信达澳亚基金管理有限公司",
            "representative_fund": "信达澳银新能源产业股票（001410）",
            "experience_years": 11,
            "career_start": "2010年从业",
            "first_fund_year": "2016年",
            "management_scale_bn": 260,
            "investment_style": ["科技成长", "中小盘", "高换手"],
            "style_tags": ["TMT", "新能源", "产业链研究"],
            "area_expertise": ["半导体", "新能源", "电子", "计算机", "通信"],
            "holding_preference": {
                "top_holdings": ["某新能源龙头企业", "璞泰来", "恩捷股份", "天齐锂业", "赣锋锂业"],
                "sector_concentration": "高（新能源+科技）",
                "stock_concentration": "分散（前十大约40%）",
                "holding_period": "中短期（0.5-1.5年）",
            },
            "performance": {
                "cumulative_return_5y": "约350%（新能源超级红利期）",
                "annual_return_5y": "约32%",
                "max_drawdown": "-50%（2022年）",
                "sharpe_ratio": "约1.5",
            },
            "risk特征": {
                "volatility": "极高",
                "drawdown_control": "弱",
                "风格稳定性": "赛道驱动",
            },
            "awards": [
                "金牛奖（2020/2021）",
                "明星基金奖（2020/2021）",
            ],
            "famous_saying": "新能源是未来十年的核心主线，产业趋势重于估值",
            "education": "浙江大学工学硕士",
            "personality": "专注新能源产业链，善于挖掘中小盘成长股，换手率较高",
        },

        "黄兴亮": {
            "name": "黄兴亮",
            "fund_company": "万家基金管理有限公司",
            "representative_fund": "万家行业优选混合（161903）",
            "experience_years": 13,
            "career_start": "2009年从业",
            "first_fund_year": "2018年",
            "management_scale_bn": 120,
            "investment_style": ["科技成长", "长期持有", "高仓位"],
            "style_tags": ["半导体", "软件", "互联网"],
            "area_expertise": ["半导体", "软件", "互联网", "医疗器械", "CXO"],
            "holding_preference": {
                "top_holdings": ["韦尔股份", "士兰微", "用友网络", "金山办公", "恒生电子"],
                "sector_concentration": "高（科技）",
                "stock_concentration": "高（前十大60-75%）",
                "holding_period": "中长期（1-3年）",
            },
            "performance": {
                "cumulative_return_5y": "约190%（科技成长期）",
                "annual_return_5y": "约21%",
                "max_drawdown": "-48%（2022年）",
                "sharpe_ratio": "约1.2",
            },
            "risk特征": {
                "volatility": "高",
                "drawdown_control": "弱",
                "风格稳定性": "稳定",
            },
            "awards": [
                "金牛奖（2021）",
            ],
            "famous_saying": "科技是强国之本，陪伴优质科技公司共同成长",
            "education": "清华大学工学博士",
            "personality": "硬科技为核心，偏好半导体和软件，长周期持有不动摇",
        },

        "袁芳": {
            "name": "袁芳",
            "fund_company": "工银瑞信基金管理有限公司",
            "representative_fund": "工银文体产业股票（001714）",
            "experience_years": 13,
            "career_start": "2011年从业",
            "first_fund_year": "2015年",
            "management_scale_bn": 200,
            "investment_style": ["消费+科技均衡", "灵活配置", "自下而上"],
            "style_tags": ["均衡配置", "品质成长", "回撤控制"],
            "area_expertise": ["食品饮料", "家电", "医药", "电子", "新能源汽车"],
            "holding_preference": {
                "top_holdings": ["某白酒龙头企业", "某白酒企业", "某新能源龙头企业", "立讯精密", "海康威视"],
                "sector_concentration": "中",
                "stock_concentration": "中等（前十大约50%）",
                "holding_period": "中长期（1-2年）",
            },
            "performance": {
                "cumulative_return_5y": "约175%（截至2024年末）",
                "annual_return_5y": "约19%",
                "max_drawdown": "-35%（2022年）",
                "sharpe_ratio": "约1.2",
            },
            "risk特征": {
                "volatility": "中等",
                "drawdown_control": "较好",
                "风格稳定性": "稳定",
            },
            "awards": [
                "金牛奖（2020/2021）",
                "明星基金奖（2020/2021）",
            ],
            "famous_saying": "在不确定的市场中，寻找最确定的优质资产",
            "education": "北京大学文学+金融复合背景",
            "personality": "女性基金经理代表，均衡配置，回撤控制好，持有人体验佳",
        },

        "归凯": {
            "name": "归凯",
            "fund_company": "某头部基金公司",
            "representative_fund": "嘉实泰和混合（000595）",
            "representative_fund_2": "嘉实增长混合（070002）",
            "experience_years": 14,
            "career_start": "2008年从业",
            "first_fund_year": "2016年",
            "management_scale_bn": 280,
            "investment_style": ["成长风格", "长期持有", "品质投资"],
            "style_tags": ["大消费", "大健康", "科技升级"],
            "area_expertise": ["医药", "消费", "制造升级", "半导体", "云计算"],
            "holding_preference": {
                "top_holdings": ["某白酒龙头企业", "迈瑞医疗", "某新能源龙头企业", "立讯精密", "恒生电子"],
                "sector_concentration": "中",
                "stock_concentration": "中等（前十大约50%）",
                "holding_period": "长期（2-4年）",
            },
            "performance": {
                "cumulative_return_5y": "约165%（截至2024年末）",
                "annual_return_5y": "约18%",
                "max_drawdown": "-40%（2022年）",
                "sharpe_ratio": "约1.1",
            },
            "risk特征": {
                "volatility": "中等",
                "drawdown_control": "中等",
                "风格稳定性": "稳定",
            },
            "awards": [
                "金牛奖（2020）",
                "明星基金奖（2020）",
            ],
            "famous_saying": "买股票就是买公司，关注长期创造价值的优质企业",
            "education": "对外经济贸易大学经济学硕士",
            "personality": "质量成长风格，持仓分散在大消费、大健康和科技三大赛道",
        },

        "陈皓": {
            "name": "陈皓",
            "fund_company": "某头部基金公司",
            "representative_fund": "某基金公司科翔混合（110013）",
            "representative_fund_2": "某基金公司创新成长混合（009293）",
            "experience_years": 14,
            "career_start": "2007年加入某基金公司",
            "first_fund_year": "2014年",
            "management_scale_bn": 320,
            "investment_style": ["成长风格", "制造业升级", "高仓位运作"],
            "style_tags": ["先进制造", "军民融合", "科技成长"],
            "area_expertise": ["军工", "半导体", "新能源汽车", "高端装备", "新能源"],
            "holding_preference": {
                "top_holdings": ["紫光国微", "振华科技", "西部超导", "某新能源龙头企业", "亿纬锂能"],
                "sector_concentration": "高（制造+科技）",
                "stock_concentration": "高（前十大60-70%）",
                "holding_period": "中长期（1-3年）",
            },
            "performance": {
                "cumulative_return_5y": "约190%（制造红利期）",
                "annual_return_5y": "约21%",
                "max_drawdown": "-44%（2022年）",
                "sharpe_ratio": "约1.2",
            },
            "risk特征": {
                "volatility": "较高",
                "drawdown_control": "中等",
                "风格稳定性": "稳定",
            },
            "awards": [
                "金牛奖（2020）",
                "明星基金奖（2020）",
            ],
            "famous_saying": "制造业升级是中国经济的核心主线，先进制造蕴含巨大投资机遇",
            "education": "复旦大学管理学硕士",
            "personality": "制造+军工背景，成长进攻型，擅长军民融合领域",
        },

        "雷鸣": {
            "name": "雷鸣",
            "fund_company": "某头部基金公司管理股份有限公司",
            "representative_fund": "汇添富成长焦点混合（519068）",
            "representative_fund_2": "汇添富外延增长主题股票（000925）",
            "experience_years": 16,
            "career_start": "2006年从业",
            "first_fund_year": "2014年",
            "management_scale_bn": 240,
            "investment_style": ["大盘成长", "消费+医药", "长期持有"],
            "style_tags": ["核心资产", "高ROE", "行业龙头"],
            "area_expertise": ["医药", "白酒", "免税", "食品饮料", "医疗器械"],
            "holding_preference": {
                "top_holdings": ["某白酒龙头企业", "恒瑞医药", "药明康德", "中国中免", "某白酒企业"],
                "sector_concentration": "高（消费+医药）",
                "stock_concentration": "高（前十大65-75%）",
                "holding_period": "长期（2-4年）",
            },
            "performance": {
                "cumulative_return_5y": "约175%（核心资产红利期）",
                "annual_return_5y": "约19%",
                "max_drawdown": "-47%（2021-2022年）",
                "sharpe_ratio": "约1.2",
            },
            "risk特征": {
                "volatility": "较高",
                "drawdown_control": "中等",
                "风格稳定性": "稳定",
            },
            "awards": [
                "金牛奖（2019/2020）",
                "明星基金奖（2019/2020）",
            ],
            "famous_saying": "核心资产是穿越经济周期的最佳配置",
            "education": "上海交通大学管理学硕士",
            "personality": "消费+医药双核心，偏好高ROE龙头，长期持股",
        },

        "李晓星": {
            "name": "李晓星",
            "fund_company": "银华基金管理股份有限公司",
            "representative_fund": "银华中小盘精选混合（180031）",
            "representative_fund_2": "银华盛世精选灵活配置（003940）",
            "experience_years": 12,
            "career_start": "2011年从业",
            "first_fund_year": "2015年",
            "management_scale_bn": 350,
            "investment_style": ["科技+消费均衡", "行业轮动", "高仓位"],
            "style_tags": ["景气度投资", "TMT+消费", "轮动配置"],
            "area_expertise": ["新能源汽车", "半导体", "白酒", "医药", "消费电子"],
            "holding_preference": {
                "top_holdings": ["某新能源龙头企业", "某光伏龙头企业", "某白酒龙头企业", "立讯精密", "药明康德"],
                "sector_concentration": "中",
                "stock_concentration": "中等（前十大约50%）",
                "holding_period": "中短期（0.5-2年）",
            },
            "performance": {
                "cumulative_return_5y": "约180%（截至2024年末）",
                "annual_return_5y": "约20%",
                "max_drawdown": "-42%（2022年）",
                "sharpe_ratio": "约1.2",
            },
            "risk特征": {
                "volatility": "较高",
                "drawdown_control": "中等",
                "风格稳定性": "灵活",
            },
            "awards": [
                "金牛奖（2020/2021）",
                "明星基金奖（2020/2021）",
            ],
            "famous_saying": "用产业趋势的眼光做投资，在景气上行期布局高增长行业",
            "education": "北京大学工商管理硕士",
            "personality": "景气度轮动高手，TMT和消费轮换配置，攻守兼备",
        },
    }

    def __init__(self):
        """初始化基金经理画像引擎"""
        self.managers = self.MANAGERS
        # 构建名称索引（支持模糊匹配）
        self._build_index()

    def _build_index(self):
        """构建基金经理名称索引，支持模糊匹配"""
        self._name_index: Dict[str, List[str]] = {}
        for name in self.managers:
            # 全匹配
            self._name_index[name] = [name]
            # 单字符
            if len(name) >= 2:
                for i in range(len(name)):
                    key = name[i]
                    if key not in self._name_index:
                        self._name_index[key] = []
                    if name not in self._name_index[key]:
                        self._name_index[key].append(name)
            # 拼音首字母（简化版）
            # 留作扩展

    def search_manager(self, name: str) -> Optional[str]:
        """
        搜索基金经理名称，支持模糊匹配
        返回最匹配的管理人名称（若未找到返回None）
        """
        name = name.strip()
        if not name:
            return None

        # 精确匹配
        if name in self.managers:
            return name

        # 包含匹配
        for mgr_name in self.managers:
            if name in mgr_name or mgr_name in name:
                return mgr_name

        # 单字符搜索（取第一个）
        if len(name) == 1 and name in self._name_index:
            candidates = self._name_index[name]
            return candidates[0] if candidates else None

        return None

    def get_profile(self, name: str, format: str = "text") -> str:
        """
        获取基金经理画像

        Args:
            name: 基金经理名称
            format: 输出格式，text/markdown/json

        Returns:
            画像报告文本
        """
        matched_name = self.search_manager(name)
        if not matched_name:
            return f"未找到基金经理「{name}」，请确认姓名是否正确。当前支持查询的基金经理包括：{', '.join(sorted(self.managers.keys()))}"

        data = self.managers[matched_name]

        if format == "json":
            return json.dumps(data, ensure_ascii=False, indent=2)

        # text / markdown
        holding = data["holding_preference"]
        perf = data["performance"]
        risk = data["risk特征"]

        lines = [
            f"# 📊 基金经理画像：{data['name']}",
            "",
            f"**所属公司**：{data['fund_company']}",
            f"**从业年限**：{data['experience_years']}年（{data['career_start']}，首只基金{data['first_fund_year']}）",
            f"**管理规模**：约{data['management_scale_bn']}亿元",
            f"**学历背景**：{data['education']}",
            "",
            "## 🎯 代表基金",
            f"- {data['representative_fund']}",
        ]
        if "representative_fund_2" in data:
            lines.append(f"- {data['representative_fund_2']}")

        lines.extend([
            "",
            "## 📈 投资风格",
            f"**风格标签**：`{' / '.join(data['investment_style'])}`",
            f"**特色标签**：{' '.join(f'`{t}`' for t in data['style_tags'])}",
            f"**能力圈**：{' / '.join(data['area_expertise'])}",
            "",
            "## 💼 持仓偏好",
            f"**前十大重仓**：`{'、'.join(holding['top_holdings'])}`",
            f"**行业集中度**：{holding['sector_concentration']}",
            f"**个股集中度**：{holding['stock_concentration']}",
            f"**平均持仓周期**：{holding['holding_period']}",
            "",
            "## 📊 业绩表现（截至2024年末）",
            f"- 5年年化收益：{perf.get('annual_return_5y', 'N/A')}",
            f"- 5年累计收益：{perf.get('cumulative_return_5y', 'N/A')}",
            f"- 最大回撤：{perf.get('max_drawdown', 'N/A')}",
            f"- 夏普比率：{perf.get('sharpe_ratio', 'N/A')}",
            "",
            "## ⚠️ 风险特征",
            f"- 波动率：{risk['volatility']}",
            f"- 回撤控制：{risk['drawdown_control']}",
            f"- 风格稳定性：{risk['风格稳定性']}",
            "",
            "## 🏆 获奖记录",
        ])
        for award in data["awards"]:
            lines.append(f"- {award}")

        lines.extend([
            "",
            "## 💬 投资理念",
            f"> 「{data['famous_saying']}」",
            "",
            "## 📋 人物点评",
            f"{data['personality']}",
        ])

        return "\n".join(lines)

    def list_managers(self) -> List[str]:
        """返回所有内置基金经理名称列表"""
        return sorted(self.managers.keys())

    def get_summary_table(self) -> str:
        """返回基金经理汇总简表（Markdown格式）"""
        lines = [
            "# 基金经理汇总表",
            "",
            "| 姓名 | 所属公司 | 从业年限 | 管理规模(亿) | 投资风格 | 代表基金 |",
            "|------|----------|---------|------------|---------|---------|",
        ]
        for name, data in sorted(self.managers.items(), key=lambda x: x[1]["experience_years"], reverse=True):
            company_short = data["fund_company"].replace("基金管理有限公司", "").replace("股份有限公司", "")
            style = " / ".join(data["investment_style"][:2])
            rep_fund = data["representative_fund"].split("（")[0]
            lines.append(
                f"| {data['name']} | {company_short} | {data['experience_years']}年 "
                f"| ~{data['management_scale_bn']} | {style} | {rep_fund} |"
            )
        return "\n".join(lines)


# 便捷函数
def get_profile(name: str, format: str = "text") -> str:
    """快捷函数：获取基金经理画像"""
    engine = FundManagerEngine()
    return engine.get_profile(name, format)


def list_managers() -> List[str]:
    """快捷函数：列出所有基金经理"""
    engine = FundManagerEngine()
    return engine.list_managers()


if __name__ == "__main__":
    engine = FundManagerEngine()
    print("内置基金经理：", engine.list_managers())
    print()
    print(engine.get_profile("张坤"))
