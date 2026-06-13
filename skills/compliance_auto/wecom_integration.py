#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
业务流程合规性自动检查 - 企微集成
"""

import json
from compliance_auto_engine import ComplianceAutoEngine


class ComplianceAutoWecom:
    """企微集成"""

    def __init__(self):
        self.engine = ComplianceAutoEngine(api_mode=True)

    def handle_message(self, text: str, user_id: str = None) -> dict:
        text = text.strip()

        # 合规检查命令
        if text.startswith("合规检查") or text.startswith("合规"):
            content = text.replace("合规检查", "").replace("合规", "").strip()
            if content:
                # 尝试解析业务类型
                parts = content.split(" ", 1)
                if len(parts) == 2 and parts[0] in [
                    "贷款业务", "存款业务", "理财销售", "保险销售",
                    "信用卡业务", "跨境汇款", "开户业务", "反洗钱检查",
                    "信息披露", "客户适当性管理"
                ]:
                    business_type = parts[0]
                    record_text = parts[1]
                else:
                    business_type = None
                    record_text = content

                result = self.engine.check_compliance(record_text, business_type)
                return self._build_result_card(result)

            return {
                "type": "text",
                "content": "请输入合规检查内容，例如：`合规检查 贷款业务 年化利率18%`"
            }

        # 规则列表
        elif text in ["合规规则", "规则列表", "合规帮助", "帮助"]:
            return self._build_help()

        # 状态查询
        elif text.startswith("合规状态"):
            return {
                "type": "text",
                "content": "✅ 合规检查引擎运行正常\n\n可用命令：\n• 合规检查 [业务类型] [操作记录]\n• 合规规则 - 查看规则列表"
            }

        return self._build_help()

    def _build_help(self) -> dict:
        return {
            "type": "text",
            "content": """🦞 **业务流程合规性自动检查引擎**

📋 功能：自动检查业务流程合规性，输出合规报告和整改建议

📝 命令：`合规检查 [业务类型] [操作记录]`

🏢 支持业务类型：
• 贷款业务、存款业务、理财销售
• 保险销售、信用卡业务、跨境汇款
• 开户业务、反洗钱检查
• 信息披露、客户适当性管理

⚠️ 风险等级：🔴高 🟡中 🟢低

示例：
`合规检查 贷款业务 年化利率18% 资金流入股市`

其他命令：
• `合规规则` - 查看合规规则列表
• `合规状态` - 查看引擎状态"""
        }

    def _build_result_card(self, result: dict) -> dict:
        """构建结果卡片"""
        template_map = {
            "high": "red",
            "medium": "orange",
            "low": "green",
            "pass": "blue"
        }

        card = {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"📋 合规检查 - {result['risk_label']}",
                    "template": template_map.get(result["risk_level"], "gray")
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**业务类型**: {result['business_type']}"
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**合规评分**: {result['compliance_score']:.1f}/100\n**风险等级**: {result['risk_label']}"
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**违规统计**: 🔴{result['stats']['high']} 🟡{result['stats']['medium']} 🟢{result['stats']['low']}"
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**摘要**: {result['summary']}"
                        }
                    },
                ]
            }
        }

        # 添加违规详情（最多5条）
        if result["violations"]:
            elements = card["card"]["elements"]
            elements.append({"tag": "hr"})
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**违规详情** ({len(result['violations'])}项)"
                }
            })

            for v in result["violations"][:5]:
                severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(v["severity"], "⚪")
                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"{severity_icon} {v['name']}: {v['suggestion']}"
                    }
                })

            if len(result["violations"]) > 5:
                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"_...还有{len(result['violations']) - 5}项违规_"
                    }
                })

        # 添加整改建议（最多3条）
        if result["rectification"]:
            elements = card["card"]["elements"]
            elements.append({"tag": "hr"})
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**整改建议** ({len(result['rectification'])}项)"
                }
            })

            for r in result["rectification"][:3]:
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(r["priority"], "⚪")
                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"{priority_icon} {r['name']} - {r['deadline']}"
                    }
                })

        # 页脚
        elements = card["card"]["elements"]
        elements.append({"tag": "hr"})
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"_检查时间: {result['checked_at']}_"
            }
        })

        return card


def handle(text: str, user_id: str = None) -> dict:
    """入口函数"""
    return ComplianceAutoWecom().handle_message(text, user_id)


if __name__ == "__main__":
    # 测试
    test_texts = [
        "合规检查 贷款业务 年化利率18% 资金流入股市 未做双录",
        "合规规则",
        "帮助",
    ]

    for text in test_texts:
        print(f"\n{'='*50}")
        print(f"输入: {text}")
        print(f"{'='*50}")
        result = handle(text)
        if result["type"] == "text":
            print(result["content"])
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2)[:500])
