#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户健康度热力图 - 企微集成
"""

import json
from customer_health_engine import CustomerHealthEngine


class CustomerHealthWecom:
    """客户健康度企微集成处理器"""

    def __init__(self):
        self.engine = CustomerHealthEngine(api_mode=True)

    def handle_message(self, text: str, user_id: str = None, customer_data: list = None) -> dict:
        """
        处理企微消息

        Args:
            text: 用户输入文本
            user_id: 用户ID
            customer_data: 可选的客户数据列表

        Returns:
            企微消息格式的响应
        """
        text = text.strip()

        # 解析命令
        if text.startswith("客户健康度") or text.startswith("健康度热力图"):
            # 提取客户群ID或使用默认数据
            group_id = text.replace("客户健康度", "").replace("健康度热力图", "").strip()
            return self._handle_health_check(group_id, customer_data)

        elif text.startswith("客户预警") or text.startswith("预警"):
            group_id = text.replace("客户预警", "").replace("预警", "").strip()
            return self._handle_warning_list(group_id, customer_data)

        elif text in ["健康度帮助", "帮助"]:
            return self._build_help()

        return self._build_help()

    def _handle_health_check(self, group_id: str, customer_data: list = None) -> dict:
        """处理健康度查询"""
        if not customer_data:
            # 生成模拟数据
            import random
            customers = self._generate_mock_customers(20)
        else:
            customers = customer_data

        group_name = f"客户群 {group_id}" if group_id else "默认客户群"
        result = self.engine.analyze_group(customers, group_name=group_name)
        return self.engine.format_wecom_card(result)

    def _handle_warning_list(self, group_id: str, customer_data: list = None) -> dict:
        """处理预警名单查询"""
        if not customer_data:
            customers = self._generate_mock_customers(20)
        else:
            customers = customer_data

        group_name = f"客户群 {group_id}" if group_id else "默认客户群"
        result = self.engine.analyze_group(customers, group_name=group_name)

        # 构建预警列表卡片
        warning_list = result["warning_list"]
        warning_items = []

        for w in warning_list[:10]:
            reasons = " | ".join(w["risk_reasons"]) if w["risk_reasons"] else "综合指标异常"
            warning_items.append({
                "tag": "div",
                "text": {"tag": "lark_md", "content": f"{w['health_emoji']} **{w['customer_name']}**\n得分:{w['total_score']:.0f} | {reasons}"}
            })

        if not warning_items:
            warning_items.append({
                "tag": "div",
                "text": {"tag": "lark_md", "content": "✅ 暂无预警客户，健康状况良好"}
            })

        return {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"🚨 {group_name} 预警名单",
                    "template": "red"
                },
                "elements": [
                    {"tag": "div", "text": {"tag": "lark_md", "content": f"**预警客户数**: {len(warning_list)}人\n**高风险**: {len([w for w in warning_list if w['health_level'] == '高风险'])}人\n**低健康**: {len([w for w in warning_list if w['health_level'] == '低健康'])}人"}},
                    {"tag": "hr"},
                    *warning_items,
                    {"tag": "hr"},
                    {"tag": "note", "elements": [{"tag": "plain_text", "content": "💡 建议优先联系高风险客户，了解实际情况"}]}
                ]
            }
        }

    def _generate_mock_customers(self, count: int) -> list:
        """生成模拟客户数据"""
        import random
        customers = []
        segments = ["VIP客户", "普通客户", "潜力客户"]
        names = ["张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十",
                 "郑十一", "王十二", "冯十三", "陈十四", "楚十五", "卫十六", "蒋十七",
                 "沈十八", "韩十九", "杨二十", "朱二十一", "秦二十二"]

        used_names = set()
        for i in range(count):
            # 确保名字不重复
            while True:
                name = random.choice(names)
                if name not in used_names:
                    used_names.add(name)
                    break

            seg = segments[i % len(segments)]
            customer = {
                "customer_id": f"C{i+1:04d}",
                "customer_name": f"{name}({seg})",
                "login_frequency": random.randint(0, 10),
                "transaction_frequency": random.randint(0, 15),
                "last_active_days": random.randint(0, 90),
                "service_interaction_count": random.randint(0, 10),
                "satisfaction_score": round(random.uniform(2.5, 5.0), 1),
                "response_rate": random.randint(50, 100),
                "overdue_days": random.randint(0, 30) if random.random() > 0.7 else 0,
                "overdue_count": random.randint(0, 5) if random.random() > 0.8 else 0,
                "credit_utilization": random.randint(10, 95),
                "complaint_count": random.randint(0, 5) if random.random() > 0.7 else 0,
                "unresolved_days": random.randint(0, 20) if random.random() > 0.8 else 0,
                "service_satisfaction": round(random.uniform(3.0, 5.0), 1),
                "tenure_months": random.randint(1, 48),
                "retention_rate": random.randint(50, 100),
                "product_count": random.randint(1, 6),
                "aum_change_pct": random.randint(-30, 30),
                "new_product_count": random.randint(0, 4),
                "asset_growth_pct": random.randint(-20, 25)
            }
            customers.append(customer)

        return customers

    def _build_help(self) -> dict:
        """构建帮助信息"""
        return {
            "type": "text",
            "content": """🦞 **客户健康度热力图引擎**

📊 功能：多维度健康度评分 + 热力图 + 预警名单

📝 命令：
`客户健康度 [客户群ID]` - 查看健康度热力图
`客户预警 [客户群ID]` - 查看预警名单
`帮助` - 显示此帮助

📈 评分维度：活动度 | 互动度 | 付款度 | 服务度 | 稳定度 | 增长度

🏆 健康等级：🟢高健康(80+) 🟡中健康(60-79) 🟠低健康(40-59) 🔴高风险(0-39)

⚠️ 示例：
`客户健康度 GROUP001`
`客户预警`"""
        }


def handle(text: str, user_id: str = None, customer_data: list = None) -> dict:
    """
    企微消息处理入口函数

    Args:
        text: 用户输入文本
        user_id: 用户ID (可选)
        customer_data: 客户数据列表 (可选)

    Returns:
        企微消息格式的响应
    """
    return CustomerHealthWecom().handle_message(text, user_id, customer_data)


if __name__ == "__main__":
    # 测试
    result = handle("客户健康度 TEST_GROUP")
    print("热力图卡片:")
    print(json.dumps(result, ensure_ascii=False, indent=2)[:1000])

    print("\n" + "=" * 50)

    result2 = handle("客户预警")
    print("预警名单卡片:")
    print(json.dumps(result2, ensure_ascii=False, indent=2)[:1000])
