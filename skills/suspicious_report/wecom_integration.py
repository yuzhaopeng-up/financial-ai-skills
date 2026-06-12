"""
企微集成模块
用于将可疑交易报告发送到企业微信
"""

import json
import os
from typing import Dict, Any, Optional

# 尝试导入企微 MCP 工具（如果可用）
try:
    from wecom_mcp import wecom_mcp
    WECOM_MCP_AVAILABLE = True
except ImportError:
    WECOM_MCP_AVAILABLE = False


class WecomIntegration:
    """企微消息卡片集成"""

    def __init__(self):
        self.mcp_available = WECOM_MCP_AVAILABLE

    def send_card(
        self,
        analysis_result: Dict[str, Any],
        chat_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        发送可疑交易报告卡片到企微

        Args:
            analysis_result: SuspiciousReportEngine.analyze() 的返回结果
            chat_id: 企微群ID（可选）
            agent_id: 应用Agent ID（可选）

        Returns:
            发送结果
        """
        from suspicious_engine import SuspiciousReportEngine
        engine = SuspiciousReportEngine()
        card = engine.to_wecom_card(analysis_result)

        # 构建消息内容
        features_str = "、".join(analysis_result["suspicious_features"]) if analysis_result["suspicious_features"] else "无"
        amount = analysis_result["parsed_info"].get("total_amount", 0)
        if amount >= 10000:
            amount_str = f"{amount/10000:.1f} 万元"
        else:
            amount_str = f"{amount:.0f} 元"

        # 企微文本消息（作为备选）
        text_content = f"""🚨 可疑交易报告
━━━━━━━━━━━━━━━
客户：{analysis_result['parsed_info'].get('customer_name', '某客户')}
金额：{amount_str}
特征：{features_str}
置信度：{analysis_result['confidence']*100:.0f}%

建议行动：
{chr(10).join(f'{i+1}. {a}' for i, a in enumerate(analysis_result['recommended_actions'][:3]))}

报告编号：STR-{analysis_result['analyzed_at'].replace('-', '').replace(':', '').replace(' ', '')}"""

        if self.mcp_available and chat_id:
            try:
                # 使用 MCP 发送消息
                result = wecom_mcp.call(
                    category="message",
                    method="send_msg",
                    args=json.dumps({
                        "chat_id": chat_id,
                        "msg_type": "text",
                        "content": text_content,
                    }),
                )
                return {
                    "success": True,
                    "method": "mcp",
                    "result": result,
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "fallback_content": text_content,
                }
        else:
            # 返回卡片JSON供手动发送
            return {
                "success": True,
                "method": "manual",
                "card": card,
                "text_fallback": text_content,
            }

    def generate_card_json(self, analysis_result: Dict[str, Any]) -> str:
        """生成企微卡片JSON（用于在企微后台创建消息）"""
        from suspicious_engine import SuspiciousReportEngine
        engine = SuspiciousReportEngine()
        card = engine.to_wecom_card(analysis_result)
        return json.dumps(card, ensure_ascii=False, indent=2)


def send_suspicious_report(
    text: str,
    chat_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    便捷函数：分析文本并发送报告到企微

    Args:
        text: 交易描述文本
        chat_id: 企微群ID（可选）

    Returns:
        发送结果
    """
    from suspicious_engine import SuspiciousReportEngine
    engine = SuspiciousReportEngine()
    result = engine.analyze(text)

    integrator = WecomIntegration()
    return integrator.send_card(result, chat_id=chat_id)


if __name__ == "__main__":
    # 测试
    from suspicious_engine import SuspiciousReportEngine
    engine = SuspiciousReportEngine()
    result = engine.analyze("某客户 累计500万 分散20个账户 快进快出")

    integrator = WecomIntegration()
    card_json = integrator.generate_card_json(result)
    print("企微卡片JSON:")
    print(card_json)
