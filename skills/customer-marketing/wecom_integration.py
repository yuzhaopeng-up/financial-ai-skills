#!/usr/bin/env python3
"""
企微端集成模块 - 营销话术生成器
提供适配企业微信的接口和数据格式
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from marketing_engine import MarketingEngine, MarketingFormatter


class WeComMarketingIntegration:
    """企微端营销话术集成"""

    # 岗位-场景映射（用于企微端菜单）
    POSITION_SCENES = {
        "retail": {
            "name": "零售客户经理",
            "icon": "👔",
            "scenes": [
                {"id": "r1", "name": "信用卡开卡", "goal": "推荐信用卡"},
                {"id": "r2", "name": "理财推荐", "goal": "推荐理财产品"},
                {"id": "r3", "name": "存款升级", "goal": "推荐大额存单"},
                {"id": "r4", "name": "贷款营销", "goal": "推荐消费贷"},
            ],
        },
        "corporate": {
            "name": "对公客户经理",
            "icon": "🏢",
            "scenes": [
                {"id": "c1", "name": "开户营销", "goal": "开立对公账户"},
                {"id": "c2", "name": "贷款推荐", "goal": "推荐经营贷"},
                {"id": "c3", "name": "供应链金融", "goal": "推荐供应链金融"},
                {"id": "c4", "name": "票据业务", "goal": "推荐票据贴现"},
            ],
        },
        "wealth": {
            "name": "理财经理",
            "icon": "💰",
            "scenes": [
                {"id": "w1", "name": "资产配置", "goal": "推荐资产配置方案"},
                {"id": "w2", "name": "基金定投", "goal": "推荐基金定投"},
                {"id": "w3", "name": "保险规划", "goal": "推荐保险方案"},
                {"id": "w4", "name": "退休规划", "goal": "推荐养老理财"},
            ],
        },
        "private_bank": {
            "name": "私行客户经理",
            "icon": "🏛️",
            "scenes": [
                {"id": "p1", "name": "家族信托", "goal": "推荐家族信托"},
                {"id": "p2", "name": "税务筹划", "goal": "推荐税务优化方案"},
                {"id": "p3", "name": "全球配置", "goal": "推荐海外资产配置"},
            ],
        },
        "credit_card": {
            "name": "信用卡专员",
            "icon": "💳",
            "scenes": [
                {"id": "k1", "name": "新客开卡", "goal": "推荐信用卡"},
                {"id": "k2", "name": "分期营销", "goal": "推荐账单分期"},
                {"id": "k3", "name": "权益激活", "goal": "激活信用卡权益"},
            ],
        },
    }

    # 示例客户数据（用于企微端演示）
    DEMO_CUSTOMERS = {
        "r1": {"name": "小李", "industry": "科技", "scale": "月收入1.5万", "news": "经常出差"},
        "r2": {"name": "王阿姨", "industry": "教育", "scale": "退休教师，存款50万", "news": ""},
        "c1": {"name": "张总", "industry": "制造业", "scale": "年营收5000万", "news": "刚获得大额订单"},
        "c3": {"name": "刘总", "industry": "物流", "scale": "年营收3000万", "news": "旺季来临，需扩大车队"},
        "w1": {"name": "陈先生", "industry": "医疗", "scale": "可投资资产300万", "news": "刚升职为科室主任"},
        "k1": {"name": "小张", "industry": "零售", "scale": "大学生", "news": "即将毕业实习"},
    }

    def __init__(self):
        self.engine = MarketingEngine()
        self.formatter = MarketingFormatter()

    def get_positions_menu(self) -> dict:
        """获取岗位菜单（企微端首页）"""
        return {
            "type": "template_card",
            "card_type": "text_notice",
            "source": {
                "desc": "金融AI智能助手",
                "desc_color": 0,
            },
            "main_title": {
                "title": "🏦 选择您的岗位",
                "desc": "AI生成专业营销话术，像招行/平安一样高效",
            },
            "jump_list": [
                {
                    "type": 1,
                    "url": f"wecom://position/{key}",
                    "title": f"{cfg['icon']} {cfg['name']}",
                    "desc": f"{len(cfg['scenes'])}个场景",
                }
                for key, cfg in self.POSITION_SCENES.items()
            ],
            "card_image": {
                "url": "https://example.com/banner.jpg",
                "aspect_ratio": 2.25,
            },
        }

    def get_scenes_menu(self, position_key: str) -> dict:
        """获取场景菜单（岗位详情页）"""
        position = self.POSITION_SCENES.get(position_key)
        if not position:
            return {"error": "岗位不存在"}

        return {
            "type": "template_card",
            "card_type": "text_notice",
            "source": {
                "desc": f"{position['icon']} {position['name']}",
                "desc_color": 0,
            },
            "main_title": {
                "title": f"{position['name']} AI赋能场景",
                "desc": "选择场景，AI生成专业话术",
            },
            "emphasis_content": {
                "title": str(len(position["scenes"])),
                "desc": "个场景",
            },
            "jump_list": [
                {
                    "type": 1,
                    "url": f"wecom://scene/{scene['id']}",
                    "title": scene["name"],
                    "desc": f"目标：{scene['goal']}",
                }
                for scene in position["scenes"]
            ],
        }

    def generate_for_scene(self, scene_id: str, style: str = "professional",
                          channel: str = "face-to-face") -> dict:
        """为指定场景生成话术（企微端调用）"""
        # 查找场景配置
        scene_config = None
        position_key = None
        for pk, pc in self.POSITION_SCENES.items():
            for s in pc["scenes"]:
                if s["id"] == scene_id:
                    scene_config = s
                    position_key = pk
                    break
            if scene_config:
                break

        if not scene_config:
            return {"error": "场景不存在"}

        # 获取示例客户数据
        demo = self.DEMO_CUSTOMERS.get(scene_id, {
            "name": "客户",
            "industry": "未知",
            "scale": "",
            "news": "",
        })

        # 生成话术
        result = self.engine.generate_script(
            customer_name=demo["name"],
            industry=demo["industry"],
            company_scale=demo["scale"],
            recent_news=demo["news"],
            marketing_goal=scene_config["goal"],
            channel=channel,
            style=style,
        )

        # 格式化输出（适配企微卡片）
        return {
            "type": "template_card",
            "card_type": "text_notice",
            "source": {
                "desc": f"{self.POSITION_SCENES[position_key]['icon']} {self.POSITION_SCENES[position_key]['name']}",
                "desc_color": 0,
            },
            "main_title": {
                "title": f"🎯 {scene_config['name']}话术",
                "desc": f"客户：{demo['name']} | 行业：{demo['industry']}",
            },
            "emphasis_content": {
                "title": result["recommended_product"],
                "desc": "推荐产品",
            },
            "sub_title_text": "话术内容",
            "jump_list": [
                {
                    "type": 1,
                    "url": "wecom://copy",
                    "title": "📋 复制话术",
                },
                {
                    "type": 1,
                    "url": "wecom://regenerate",
                    "title": "🔄 重新生成",
                },
                {
                    "type": 1,
                    "url": "wecom://objections",
                    "title": "🛡️ 异议处理",
                },
            ],
            "card_content": {
                "text": f"💬 开场白：\n{result['opening'][:100]}...\n\n📦 产品介绍：\n{result['product_intro'][:100]}...",
            },
            "full_script": self.formatter.format_script(result),
        }

    def get_peer_case(self, scene_id: str) -> dict:
        """获取同业案例（"照抄作业"功能）"""
        cases = {
            "r1": {
                "bank": "某股份制银行A",
                "product": "AI信用卡推荐",
                "effect": "开卡转化率提升35%",
                "detail": "通过客户画像分析，精准识别有出差需求的客户，推荐航空联名卡。",
            },
            "c3": {
                "bank": "某股份制银行D",
                "product": "AI信贷工厂",
                "effect": "审批时效从3天缩短至10分钟",
                "detail": "小微企业贷款全线上审批，AI自动评估企业信用风险。",
            },
            "w1": {
                "bank": "某股份制银行A",
                "product": "AI理财顾问",
                "effect": "服务效率提升3倍，AUM提升25%",
                "detail": "根据客户画像自动生成资产配置方案，客户经理只需讲解确认。",
            },
            "k1": {
                "bank": "建设银行",
                "product": "智能信用卡营销",
                "effect": "激活率提升20%",
                "detail": "AI分析客户消费行为，推荐最适合的信用卡类型。",
            },
        }

        return cases.get(scene_id, {
            "bank": "行业领先银行",
            "product": "AI营销助手",
            "effect": "营销效率显著提升",
            "detail": "利用AI技术辅助客户经理生成个性化营销话术。",
        })


def main():
    """测试企微端集成"""
    integration = WeComMarketingIntegration()

    print("=" * 60)
    print("企微端岗位菜单")
    print("=" * 60)
    menu = integration.get_positions_menu()
    print(json.dumps(menu, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)
    print("企微端场景菜单（对公客户经理）")
    print("=" * 60)
    scenes = integration.get_scenes_menu("corporate")
    print(json.dumps(scenes, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)
    print("企微端话术生成（供应链金融场景）")
    print("=" * 60)
    script = integration.generate_for_scene("c3", style="professional", channel="face-to-face")
    print(json.dumps(script, ensure_ascii=False, indent=2)[:2000])

    print("\n" + "=" * 60)
    print("同业案例（照抄作业）")
    print("=" * 60)
    case = integration.get_peer_case("c3")
    print(json.dumps(case, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
