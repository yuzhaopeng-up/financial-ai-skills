# -*- coding: utf-8 -*-
"""
企业微信卡片集成 - 信用卡逾期催收

将催收方案以企微消息卡片形式推送给催收人员。
"""

import json
from typing import Optional


class WecomCollectionCard:
    """企微催收消息卡片生成器"""

    # 优先级颜色映射
    PRIORITY_COLOR = {
        "紧急": "red",
        "高": "orange",
        "中": "yellow",
        "低": "green"
    }

    # 阶段颜色映射
    STAGE_COLOR = {
        "M1": "green",
        "M2": "yellow",
        "M3": "orange",
        "M3+": "red"
    }

    def __init__(self):
        self.card_version = "1.0"

    def generate_card(self, collection_result: dict) -> dict:
        """
        将催收方案转换为企微卡片格式

        Args:
            collection_result: CreditCollectionEngine.generate_collection_plan() 返回的结果

        Returns:
            企微消息卡片元素
        """
        stage = collection_result["stage"]
        priority = collection_result["priority"]
        overdue_days = collection_result["overdue_days"]
        amount = collection_result["outstanding_amount"]

        # 构建卡片内容
        elements = []

        # 标题区域
        elements.append({
            "tag": "markdown",
            "content": f"**🏦 信用卡逾期催收通知**\n优先级: {priority} | 阶段: {stage} | 逾期: {overdue_days}天"
        })

        # 基本信息
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**客户信息**\n欠款金额: **{amount:.2f}元**\n客户类型: {collection_result['customer_type']}\n联系方式有效: {'✅ 是' if collection_result['contact_valid'] else '❌ 否'}"
            }
        })

        # 催收策略
        strategies_text = "、".join(collection_result["strategies"])
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**催收策略**\n{strategies_text}"
            }
        })

        # 分期建议
        installment = collection_result["installment_advice"]
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**分期还款建议**\n{installment['recommendation']}\n建议期数: {installment['suggested_plan']}期\n预计月还款: {installment['min_monthly_payment']:.2f}元"
            }
        })

        # 法律后果
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**⚠️ 法律后果提示**\n{collection_result['legal_warning'][:100]}..."
            }
        })

        # 催收话术
        if "current" in collection_result["scripts"]:
            current_script = collection_result["scripts"]["current"]
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**📞 当前话术 [{current_script['channel']}]**\n{current_script['template']}"
                }
            })

        # 合规检测
        compliance = collection_result["compliance_check"]
        if compliance["can_proceed"]:
            status_text = "✅ 合规检测通过"
        else:
            status_text = "⚠️ 合规检测未通过"

        time_check = compliance["time_check"]
        status_text += f"\n时段检测: {'✅ 合规' if time_check['compliant'] else f'❌ 违规 ({time_check[\"current_hour\"]}:00)'}"
        status_text += f"\n允许时段: {time_check['allowed_range']}"

        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": status_text
            }
        })

        # 生成时间
        elements.append({
            "tag": "note",
            "elements": [
                {
                    "tag": "lark_md",
                    "content": f"生成时间: {collection_result['generated_at']}"
                }
            ]
        })

        # 构建完整卡片
        card = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"催收任务 - {priority}优先级"
                    },
                    "template": self.PRIORITY_COLOR.get(priority, "gray")
                },
                "elements": elements
            }
        }

        return card

    def generate_batch_cards(self, collection_results: list) -> list:
        """
        生成批量催收卡片

        Args:
            collection_results: 催收方案列表

        Returns:
            企微消息卡片列表
        """
        return [self.generate_card(r) for r in collection_results]

    def generate_wecom_text(self, collection_result: dict) -> str:
        """
        生成简化的企微文本消息（纯文本版本）

        Args:
            collection_result: 催收方案结果

        Returns:
            文本消息内容
        """
        stage = collection_result["stage"]
        priority = collection_result["priority"]
        overdue_days = collection_result["overdue_days"]
        amount = collection_result["outstanding_amount"]
        strategies = "、".join(collection_result["strategies"])
        installment = collection_result["installment_advice"]

        text = f"""🏦 信用卡逾期催收通知

优先级: {priority} | 阶段: {stage} | 逾期: {overdue_days}天
欠款金额: {amount:.2f}元
催收策略: {strategies}
分期建议: {installment['recommendation']}
建议期数: {installment['suggested_plan']}期
预计月还款: {installment['min_monthly_payment']:.2f}元

⚠️ 法律后果提示:
{collection_result['legal_warning']}

生成时间: {collection_result['generated_at']}"""

        return text


def send_collection_card(collection_result: dict, webhook_url: str) -> dict:
    """
    通过企微webhook发送催收卡片

    Args:
        collection_result: 催收方案结果
        webhook_url: 企业微信群机器人的webhook地址

    Returns:
        发送结果
    """
    try:
        import urllib.request
        import urllib.error

        card_generator = WecomCollectionCard()
        card = card_generator.generate_card(collection_result)

        data = json.dumps(card, ensure_ascii=False).encode("utf-8")

        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))

            if result.get("errcode") == 0:
                return {"success": True, "errmsg": result.get("errmsg", "ok")}
            else:
                return {"success": False, "errmsg": result.get("errmsg", "unknown error")}

    except urllib.error.URLError as e:
        return {"success": False, "errmsg": f"网络错误: {str(e)}"}
    except Exception as e:
        return {"success": False, "errmsg": f"发送失败: {str(e)}"}


def main():
    """测试入口"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent))

    from collection_engine import CreditCollectionEngine

    # 生成测试催收方案
    engine = CreditCollectionEngine()
    result = engine.generate_collection_plan(
        overdue_days=30,
        outstanding_amount=50000,
        customer_type="personal",
        payment_history=["按时", "逾期1次"],
        contact_valid=True
    )

    # 生成企微卡片
    card_generator = WecomCollectionCard()
    card = card_generator.generate_card(result)

    print("=" * 60)
    print("企微催收卡片内容:")
    print("=" * 60)
    print(json.dumps(card, ensure_ascii=False, indent=2))

    # 生成文本版本
    text = card_generator.generate_wecom_text(result)
    print("\n" + "=" * 60)
    print("企微文本消息内容:")
    print("=" * 60)
    print(text)


if __name__ == "__main__":
    from pathlib import Path
    main()
