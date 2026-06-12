"""
企微机器人卡片集成 (wecom_integration)

将费用报销审计结果以企微消息卡片格式输出

使用方式：
    from wecom_integration import ExpenseAuditCard
    card = ExpenseAuditCard()
    card_data = card.build_card(audit_result)
"""

import json
from typing import Optional


class ExpenseAuditCard:
    """费用报销审计企微卡片构建器"""

    # 状态颜色映射
    STATUS_COLOR = {
        "通过": "#00B42A",    # 绿色
        "驳回": "#F53F3F",    # 红色
        "需补充": "#FF7D00",  # 橙色
    }

    # 风险等级颜色
    RISK_COLOR = {
        "高": "#F53F3F",
        "中": "#FF7D00",
        "低": "#00B42A",
    }

    def __init__(self):
        self.template = "news"

    def _build_header(self, status: str, risk_level: str) -> dict:
        """构建卡片头部"""
        status_color = self.STATUS_COLOR.get(status, "#165DFF")
        risk_color = self.RISK_COLOR.get(risk_level, "#165DFF")

        return {
            "tag": "div",
            "text": {
                "content": f"💰 **费用报销审计报告**",
                "tag": "lark_md"
            }
        }

    def _build_field(self, label: str, value: str) -> dict:
        """构建字段"""
        return {
            "tag": "column_set",
            "flex_mode": "gold",
            "background_style": "grey",
            "fields": [
                {
                    "tag": "column",
                    "text": {
                        "content": f"**{label}**",
                        "tag": "lark_md"
                    },
                    "width": "weighted",
                    "weight": "1"
                },
                {
                    "tag": "column",
                    "text": {
                        "content": value,
                        "tag": "lark_md"
                    },
                    "width": "weighted",
                    "weight": "2"
                }
            ]
        }

    def _build_divider(self) -> dict:
        return {"tag": "hr"}

    def _build_status_block(self, status: str, risk_level: str) -> dict:
        """构建状态块"""
        color = self.STATUS_COLOR.get(status, "#165DFF")
        return {
            "tag": "div",
            "text": {
                "content": f"**审计结果：** {"✅ " + status if status == "通过" else "❌ " + status if status == "驳回" else "⚠️ " + status}　　**风险等级：** {risk_level}",
                "tag": "lark_md"
            }
        }

    def _build_violations(self, violations: list) -> Optional[dict]:
        """构建违规列表"""
        if not violations:
            return None

        violation_names = [
            "V001:招待费超收入千分之五上限",
            "V002:招待费事前未审批",
            "V003:缺少正规发票",
            "V004:发票日期晚于报销日期",
            "V005:单笔金额超限未额外审批",
            "V006:费用类型与部门不匹配",
            "V007:同员工同类型费用本月累计异常",
        ]

        items = []
        for v in violations:
            name = violation_names[int(v.replace("V", "")) - 1] if v.startswith("V") and v[1:].isdigit() else v
            items.append(f"• {name}")

        return {
            "tag": "div",
            "text": {
                "content": f"**违规类型：**\n{chr(10).join(items)}",
                "tag": "lark_md"
            }
        }

    def _build_suggestions(self, suggestions: list) -> Optional[dict]:
        """构建合规建议"""
        if not suggestions:
            return None

        items = [f"• {s}" for s in suggestions]
        return {
            "tag": "div",
            "text": {
                "content": f"**合规建议：**\n{chr(10).join(items)}",
                "tag": "lark_md"
            }
        }

    def _build_details(self, details: str) -> dict:
        """构建详细说明"""
        return {
            "tag": "div",
            "text": {
                "content": f"**说明：** {details}",
                "tag": "lark_md"
            }
        }

    def build_card(self, audit_result: dict) -> dict:
        """
        构建企微消息卡片

        Args:
            audit_result: ExpenseAuditEngine.audit() 返回的结果

        Returns:
            dict: 企微卡片元素数组
        """
        elements = []

        # 头部
        elements.append(self._build_header(audit_result["status"], audit_result["risk_level"]))
        elements.append(self._build_divider())

        # 基本信息
        # 注意：audit_result 中没有 employee/department/expense_type/amount 字段
        # 这些信息需要从 remarks 或其他地方获取
        # 这里用简化版本
        elements.append(self._build_status_block(audit_result["status"], audit_result["risk_level"]))
        elements.append(self._build_divider())

        # 违规类型
        if audit_result["violations"]:
            elements.append(self._build_violations(audit_result["violations"]))
            elements.append(self._build_divider())

        # 合规建议
        if audit_result["suggestions"]:
            elements.append(self._build_suggestions(audit_result["suggestions"]))
            elements.append(self._build_divider())

        # 详细说明
        elements.append(self._build_details(audit_result["details"]))

        # 构建完整卡片
        card = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "content": "💰 费用报销审计报告",
                        "tag": "plain_text"
                    },
                    "template": self.STATUS_COLOR.get(audit_result["status"], "#165DFF")
                },
                "elements": elements
            }
        }

        return card

    def build_simple_card(self, status: str, risk_level: str, violations: list, suggestions: list, details: str) -> dict:
        """构建简化版卡片（用于直接传入参数）"""
        return self.build_card({
            "status": status,
            "risk_level": risk_level,
            "violations": violations,
            "suggestions": suggestions,
            "details": details,
        })

    @staticmethod
    def to_json(card: dict) -> str:
        """转换为JSON字符串"""
        return json.dumps(card, ensure_ascii=False)


def send_wecom_card(card_data: dict, webhook_url: str = None) -> dict:
    """
    发送企微卡片消息（需要webhook_url）

    Args:
        card_data: 卡片数据
        webhook_url: 企微机器人webhook地址

    Returns:
        dict: 发送结果
    """
    if not webhook_url:
        return {"errcode": 1, "errmsg": "webhook_url is required"}

    import urllib.request
    import urllib.error

    try:
        data = json.dumps(card_data).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result
    except urllib.error.URLError as e:
        return {"errcode": 2, "errmsg": str(e)}
    except Exception as e:
        return {"errcode": 3, "errmsg": str(e)}


if __name__ == "__main__":
    # 测试卡片构建
    card_builder = ExpenseAuditCard()

    # 模拟审计结果
    test_result = {
        "status": "需补充",
        "violations": ["V001", "V002"],
        "risk_level": "高",
        "suggestions": [
            "招待费上限为收入×0.5‰=5000元，当前报销8000元，超出3000元",
            "招待费单笔超过1000元必须事前审批，请补充事前申请流程"
        ],
        "details": "【需补充】员工张三报销招待费8000元，需补充相关材料后提交。"
    }

    card = card_builder.build_card(test_result)
    print("企微卡片内容：")
    print(json.dumps(card, ensure_ascii=False, indent=2))
