#!/usr/bin/env python3
"""
企微消息格式化器 - 纯文本卡片式布局
适配企业微信的文本消息限制
"""
from typing import Dict, Any
from datetime import datetime


def format_dd_report(result: Dict[str, Any]) -> str:
    """格式化尽调报告为企微文本消息"""
    if not result.get('success'):
        return result.get('message', '⚠️ 报告生成失败')

    company = result['company_name']
    code = result['stock_code']
    market = result.get('market_data', {})
    assessment = result.get('assessment', {})
    sentiment = result.get('sentiment', {})

    lines = [
        f"📊 {company} [{code if code else '未找到'}]",
        f"⏱️ {datetime.now().strftime('%m-%d %H:%M')}",
        "",
    ]

    # 行情数据（不用表格，用文本列表）
    if market and market.get('success'):
        price = market.get('latest_price', '-')
        change = market.get('change_percent', 0)
        change_str = f"+{change:.2f}%" if change > 0 else f"{change:.2f}%"
        change_emoji = "📈" if change > 0 else "📉" if change < 0 else "➖"

        lines.extend([
            f"💹 行情 {change_emoji} {change_str} ¥{price}",
            f"  开盘价: ¥{market.get('open', '-')}",
            f"  最高价: ¥{market.get('high', '-')}",
            f"  最低价: ¥{market.get('low', '-')}",
            f"  成交量: {market.get('volume', '-')}",
            f"  市盈率: {market.get('pe_ratio', '-')}",
            f"  市净率: {market.get('pb_ratio', '-')}",
            f"  总市值: ¥{market.get('market_cap', '-')}亿",
            "",
        ])

    # 舆情
    if sentiment and sentiment.get('level') != '未知':
        level = sentiment.get('level', '未知')
        score = sentiment.get('score', 50)
        emoji = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"
        summary = sentiment.get('summary', '')
        lines.extend([
            f"📰 舆情 {emoji} {level}(评分:{score})",
            f"  {summary}" if summary else "",
            "",
        ])

    # 评估
    if assessment:
        risk_level = assessment.get('risk_level', '未知')
        overall_score = assessment.get('overall_score', 70)
        recommendation = assessment.get('recommendation', '审慎通过')
        risk_emoji = "🟢" if risk_level in ['AAA', 'AA', 'A'] else "🟡" if risk_level in ['BBB', 'BB'] else "🔴"
        lines.extend([
            f"🎯 评估",
            f"  风险等级: {risk_emoji} {risk_level}",
            f"  综合得分: {overall_score}",
            f"  建议: {recommendation}",
            "",
        ])

    # 数据来源
    sources = result.get('data_sources', [])
    if sources:
        lines.extend([
            f"📡 来源: {' · '.join(sources)}",
            "",
        ])

    lines.append("— 🦞 龙马金融AI")
    return '\n'.join(lines)


def format_simple_message(title: str, content: str, footer: str = "龙马金融AI") -> str:
    """格式化简单文本消息"""
    return f"{title}\n\n{content}\n\n— {footer}"


# 测试数据
TEST_RESULT = {
    "success": True,
    "company_name": "美的集团",
    "stock_code": "000333",
    "market_data": {
        "success": True,
        "latest_price": 72.5,
        "change_percent": 1.23,
        "open": 71.8,
        "high": 73.1,
        "low": 71.5,
        "volume": "45.2万手",
        "pe_ratio": 15.3,
        "pb_ratio": 3.2,
        "market_cap": 5080,
    },
    "sentiment": {
        "level": "正面",
        "score": 82,
        "summary": "近期机构研报密集覆盖，智能家居业务增长亮眼",
    },
    "assessment": {
        "risk_level": "AA",
        "overall_score": 88,
        "recommendation": "建议关注",
    },
    "data_sources": ["东方财富", "同花顺", "雪球"],
}


if __name__ == "__main__":
    # 本地测试格式化效果
    print("=" * 50)
    print("企微消息格式化测试")
    print("=" * 50)
    print()
    print(format_dd_report(TEST_RESULT))
    print()
    print("=" * 50)
    print("消息长度:", len(format_dd_report(TEST_RESULT)), "字符")
    print("=" * 50)
