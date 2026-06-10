"""
企微卡片集成模块
现金管理方案 -> 企微消息卡片
"""

from typing import Dict, Any, Optional
import json


class CashManagementWecomCard:
    """企微消息卡片构建器"""
    
    # 卡片配色方案
    COLORS = {
        "primary": "#1F4E79",      # 深蓝
        "secondary": "#2E75B6",   # 蓝色
        "success": "#548235",     # 绿色
        "warning": "#C55A11",     # 橙色
        "info": "#0070C0",        # 浅蓝
        "text": "#303030",        # 深灰文字
        "light": "#F5F5F5",       # 浅灰背景
    }

    @classmethod
    def build_card(
        cls,
        company_type: str,
        monthly_cash_flow: float,
        volatility: str,
        target_yield: str,
        reserve_ratio: str,
        summary: str,
    ) -> Dict[str, Any]:
        """
        构建企微卡片
        
        Args:
            company_type: 企业类型
            monthly_cash_flow: 月度现金流（元）
            target_yield: 目标收益率
            reserve_ratio: 流动性储备比例
            summary: 方案摘要
        
        Returns:
            企微卡片JSON
        """
        flow_str = f"{monthly_cash_flow/10000:.0f}万"
        
        card = {
            "msgtype": "interactive",
            "interactive": {
                "tag": "card",
                "card": {
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "content": "💰 现金管理方案",
                        },
                        "subtitle": {
                            "tag": "plain_text",
                            "content": f"{company_type} | 月现金流{flow_str} | {volatility}",
                        },
                        "color": cls.COLORS["primary"],
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "tag": "markdown",
                                "content": summary[:500] + "..." if len(summary) > 500 else summary,
                            },
                        },
                        {"tag": "hr"},
                        {
                            "tag": "column_set",
                            "flex_mode": "border_aligned",
                            "elements": [
                                {
                                    "tag": "column",
                                    "width": "auto",
                                    "elements": [
                                        {
                                            "tag": "markdown",
                                            "content": f"**目标收益率**\n{target_yield}",
                                        },
                                    ],
                                },
                                {
                                    "tag": "column",
                                    "width": "auto",
                                    "elements": [
                                        {
                                            "tag": "markdown",
                                            "content": f"**流动性储备**\n{reserve_ratio}",
                                        },
                                    ],
                                },
                            ],
                        },
                        {"tag": "hr"},
                        {
                            "tag": "note",
                            "elements": [
                                {
                                    "tag": "plain_text",
                                    "content": "📋 方案仅供参考，具体请咨询银行客户经理",
                                },
                            ],
                        },
                    ],
                },
            },
        }
        
        return card

    @classmethod
    def build_detail_card(cls, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建详细方案卡片
        
        Args:
            result: CashManagementEngine.generate() 返回的字典
        
        Returns:
            企微卡片JSON
        """
        company_type = result.get("company_type", "一般企业")
        monthly_cash_flow = result.get("monthly_cash_flow", 0)
        volatility = result.get("volatility", "中等波动")
        flow_str = f"{monthly_cash_flow/10000:.0f}万"
        
        yield_imp = result.get("yield_improvement", {})
        liquidity = result.get("liquidity_plan", {})
        target_yield = yield_imp.get("target_yield", "N/A")
        reserve_ratio = liquidity.get("total_reserve_required", "N/A")
        
        # 构建账户架构表格
        arch = result.get("account_architecture", {})
        accounts = arch.get("accounts", [])
        account_md = "**【账户架构】**\n"
        for acc in accounts:
            account_md += f"• {acc.get('name', '')}：{acc.get('type', '')}（占比{acc.get('ratio', 0)*100:.0f}%）\n"
        account_md += f"\n模式：{arch.get('cash_pool_mode', '标准零余额')}"
        
        # 构建产品推荐表格
        products = result.get("products", [])
        product_md = "**【产品推荐】**\n"
        for cat in products[:3]:  # 只取前3类
            product_md += f"\n◆ {cat.get('category', '')}：\n"
            for p in cat.get("products", [])[:2]:  # 每类只取前2个
                product_md += f"  - {p.get('name', '')}（{p.get('expected_yield', '')}）\n"
        
        card = {
            "msgtype": "interactive",
            "interactive": {
                "tag": "card",
                "card": {
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "content": "💰 现金管理方案",
                        },
                        "subtitle": {
                            "tag": "plain_text",
                            "content": f"{company_type} | 月现金流{flow_str} | {volatility}",
                        },
                        "color": cls.COLORS["primary"],
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "tag": "markdown",
                                "content": account_md,
                            },
                        },
                        {"tag": "hr"},
                        {
                            "tag": "div",
                            "text": {
                                "tag": "markdown",
                                "content": product_md,
                            },
                        },
                        {"tag": "hr"},
                        {
                            "tag": "column_set",
                            "flex_mode": "border_aligned",
                            "elements": [
                                {
                                    "tag": "column",
                                    "width": "auto",
                                    "elements": [
                                        {
                                            "tag": "markdown",
                                            "content": f"**目标收益率**\n{target_yield}",
                                        },
                                    ],
                                },
                                {
                                    "tag": "column",
                                    "width": "auto",
                                    "elements": [
                                        {
                                            "tag": "markdown",
                                            "content": f"**流动性储备**\n{reserve_ratio}",
                                        },
                                    ],
                                },
                            ],
                        },
                        {"tag": "hr"},
                        {
                            "tag": "note",
                            "elements": [
                                {
                                    "tag": "plain_text",
                                    "content": "📋 完整方案请查看详细报告或咨询银行客户经理",
                                },
                            ],
                        },
                    ],
                },
            },
        }
        
        return card


def format_for_wecom(result: Dict[str, Any]) -> str:
    """将方案结果格式化为企微卡片JSON字符串"""
    card = CashManagementWecomCard.build_detail_card(result)
    return json.dumps(card, ensure_ascii=False)


if __name__ == "__main__":
    # 测试
    from cash_engine import CashManagementEngine
    engine = CashManagementEngine()
    result = engine.generate(
        text="现金管理 制造企业 月现金流5000万"
    )
    print(format_for_wecom(result.to_dict()))
