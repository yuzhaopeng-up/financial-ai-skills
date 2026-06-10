#!/usr/bin/env python3
"""
FOF Portfolio WeChat Enterprise Integration - 企微卡片消息集成
用于将FOF组合方案以企微消息卡片形式发送
"""

import json
from typing import Dict, Any, Optional, List


class WecomCardBuilder:
    """企微消息卡片构建器"""

    def __init__(self, agent_id: str = "", corp_id: str = ""):
        self.agent_id = agent_id
        self.corp_id = corp_id

    def build_portfolio_card(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """构建FOF组合方案企微卡片"""

        # 提取关键数据
        params = result.get('input_params', {})
        saa = result.get('strategic_asset_allocation', {})
        taa = result.get('tactical_adjustments', [])
        weights = result.get('weight_optimization', [])

        # 构建资产配置描述
        alloc_text = []
        for asset_type, pct in saa.get('allocations', {}).items():
            if pct > 0:
                alloc_text.append(f"{asset_type}{pct}%")

        # 构建基金列表描述
        fund_list = []
        for w in weights[:5]:  # 最多显示5只
            fund_list.append({
                "tag": "text",
                "text": f"• {w['fund_name']} {w['weight']}"
            })

        # 构建TAA调整描述
        taa_text = []
        for adj in taa[:3]:
            taa_text.append({
                "tag": "text",
                "text": f"▶ {adj['asset_type']}: {adj['adjustment']} ({adj['reason'][:20]}...)"
            })

        # 构建卡片内容
        card_content = {
            "msgtype": "interactive",
            "agentid": self.agent_id,
            "interactive": {
                "card": {
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "text": f"📊 FOF组合方案 | {params.get('risk_preference', '平衡型')}"
                        },
                        "description": {
                            "tag": "plain_text",
                            "text": f"规模:{params.get('portfolio_size', '-')} | 目标:{params.get('investment_goal', '-')} | 期限:{params.get('holding_period', '-')}"
                        },
                        "color": "blue"
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "fields": [
                                {
                                    "is_short": True,
                                    "text": {
                                        "tag": "lark_md",
                                        "content": "**目标收益**\n" + saa.get('target_annual_return', '-')
                                    }
                                },
                                {
                                    "is_short": True,
                                    "text": {
                                        "tag": "lark_md",
                                        "content": "**预期波动**\n" + saa.get('expected_volatility', '-')
                                    }
                                }
                            ]
                        },
                        {"tag": "hr"},
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": "**📌 战略配置 (SAA)**\n" + " | ".join(alloc_text)
                            }
                        },
                        {"tag": "hr"},
                        {
                            "tag": "div",
                            "fields": fund_list[:3]
                        },
                        {"tag": "hr"},
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": "**🔄 战术调整 (TAA)**"
                            }
                        },
                        *taa_text[:2],
                        {"tag": "hr"},
                        {
                            "tag": "note",
                            "elements": [
                                {
                                    "tag": "plain_text",
                                    "text": "⚠️ 基金过往业绩不代表未来表现，本方案仅供参考，不构成投资建议。"
                                }
                            ]
                        }
                    ],
                    "footer": {
                        "style": {
                            "align": "center"
                        },
                        "fields": [
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": f"**组合ID**\n{result.get('portfolio_id', '-')}"
                                }
                            },
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": f"**生成时间**\n{result.get('generated_at', '-')}"
                                }
                            }
                        ]
                    }
                }
            }
        }

        return card_content

    def build_screening_card(self, screened: List[Dict[str, Any]],
                           risk_pref: str, goal: str, period: str) -> Dict[str, Any]:
        """构建基金筛选结果卡片"""

        # 基金列表
        fund_fields = []
        for i, s in enumerate(screened[:6], 1):
            metrics = s.get('key_metrics', {})
            fund_fields.append({
                "is_short": i % 2 == 1,
                "text": {
                    "tag": "lark_md",
                    "content": f"**{i}. {s['fund_name']}**\n码:{s['fund_code']} | 类型:{s['fund_type']}\n1年收益:{metrics.get('annual_return_1y', '-')} | 夏普:{metrics.get('sharpe_ratio', '-')}"
                }
            })

        card_content = {
            "msgtype": "interactive",
            "agentid": self.agent_id,
            "interactive": {
                "card": {
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "text": f"🎯 基金筛选 | {risk_pref}"
                        },
                        "description": {
                            "tag": "plain_text",
                            "text": f"目标:{goal} | 期限:{period}"
                        },
                        "color": "green"
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "fields": fund_fields
                        },
                        {"tag": "hr"},
                        {
                            "tag": "note",
                            "elements": [
                                {
                                    "tag": "plain_text",
                                    "text": f"共筛选出 {len(screened)} 只基金，按综合评分排序。"
                                }
                            ]
                        }
                    ]
                }
            }
        }

        return card_content

    def build_allocation_card(self, saa: Dict[str, Any],
                             taa: List[Dict[str, Any]]) -> Dict[str, Any]:
        """构建资产配置卡片"""

        # SAA配置
        saa_fields = []
        for asset, pct in saa.get('allocations', {}).items():
            if pct > 0:
                saa_fields.append({
                    "is_short": True,
                    "text": {
                        "tag": "lark_md",
                        "content": f"**{asset}**\n{pct}%"
                    }
                })

        # TAA调整
        taa_elements = []
        for adj in taa:
            adjustment_icon = "📈" if "+" in adj.get('adjustment', '') else "📉" if "-" in adj.get('adjustment', '') and adj.get('adjustment', '') != "0%" else "➡️"
            taa_elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"{adjustment_icon} **{adj.get('asset_type', '-')}** {adj.get('current_weight', '-')} → {adj.get('recommended_weight', '-')} ({adj.get('adjustment', '-')})\n{adj.get('reason', '')}"
                }
            })

        card_content = {
            "msgtype": "interactive",
            "agentid": self.agent_id,
            "interactive": {
                "card": {
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "text": "⚙️ 资产配置方案"
                        },
                        "color": "purple"
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "fields": saa_fields
                        },
                        {"tag": "hr"},
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": "**📊 关键指标**\n目标收益:{saa.get('target_annual_return', '-')} | 预期波动:{saa.get('expected_volatility', '-')} | 最大回撤:{saa.get('max_drawdown_limit', '-')}"
                            }
                        },
                        {"tag": "hr"},
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": "**🔄 战术调整 (TAA)**"
                            }
                        },
                        *taa_elements[:3],
                        {"tag": "hr"},
                        {
                            "tag": "note",
                            "elements": [
                                {
                                    "tag": "plain_text",
                                    "text": "⚠️ TAA为基于当前宏观环境的短期调整建议，请结合自身情况判断。"
                                }
                            ]
                        }
                    ]
                }
            }
        }

        return card_content

    def build_due_diligence_card(self, dd_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """构建基金尽调卡片"""

        # 每只基金的尽调摘要
        dd_elements = []
        for dd in dd_points[:4]:  # 最多4只
            strengths = dd.get('strength_points', [])
            concerns = dd.get('concern_points', [])

            strength_text = "\n".join([f"✅ {s}" for s in strengths[:2]]) if strengths else ""
            concern_text = "\n".join([f"⚠️ {c}" for c in concerns[:1]]) if concerns else ""

            dd_elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**{dd['fund_name']}**\n{strength_text}\n{concern_text}"
                }
            })

        card_content = {
            "msgtype": "interactive",
            "agentid": self.agent_id,
            "interactive": {
                "card": {
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "text": "🔍 基金尽调要点"
                        },
                        "color": "orange"
                    },
                    "elements": [
                        *dd_elements,
                        {"tag": "hr"},
                        {
                            "tag": "note",
                            "elements": [
                                {
                                    "tag": "plain_text",
                                    "text": "📊 完整尽调报告请查看FOF方案详情。监控指标包括: 季度超额收益、规模变化、持仓集中度等。"
                                }
                            ]
                        }
                    ]
                }
            }
        }

        return card_content


def send_wecom_message(card_data: Dict[str, Any],
                       webhook_url: str = "") -> Dict[str, Any]:
    """
    发送企微消息卡片

    Args:
        card_data: 卡片数据（由WecomCardBuilder构建）
        webhook_url: 企微webhook地址

    Returns:
        发送结果
    """
    import urllib.request
    import urllib.error

    if not webhook_url:
        return {"errcode": 0, "errmsg": "webhook not configured, returning mock success"}

    try:
        data = json.dumps(card_data, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except urllib.error.URLError as e:
        return {"errcode": -1, "errmsg": str(e)}
    except Exception as e:
        return {"errcode": -2, "errmsg": str(e)}


# 示例用法
if __name__ == "__main__":
    # 导入fof_engine进行测试
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from fof_engine import FOFEngine

    # 生成测试组合
    engine = FOFEngine()
    result = engine.generate_portfolio(
        risk_preference="平衡型",
        portfolio_size="1亿",
        investment_goal="养老规划",
        holding_period="5年"
    )

    # 构建企微卡片
    builder = WecomCardBuilder()
    card = builder.build_portfolio_card(result)

    print("企微卡片JSON (预览):")
    print(json.dumps(card, ensure_ascii=False, indent=2))
