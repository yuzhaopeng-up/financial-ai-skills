"""
企微卡片集成 - ESG研究报告企微消息卡片
支持发送ESG评分卡片到企业微信
"""

from typing import Dict, List, Optional
import json


class WecomCard:
    """ESG企微卡片生成器"""

    @staticmethod
    def score_to_color(score: float) -> str:
        """根据评分返回颜色"""
        if score >= 80:
            return "#00C853"   # 绿色 - 优秀
        elif score >= 70:
            return "#64DD17"   # 浅绿 - 良好
        elif score >= 60:
            return "#FFB300"  # 黄色 - 中等
        elif score >= 50:
            return "#FF6D00"  # 橙色 - 偏弱
        return "#D50000"      # 红色 - 较弱

    @staticmethod
    def rating_to_color(rating: str) -> str:
        """根据评级返回颜色"""
        colors = {
            "AAA": "#00C853", "AA": "#00E676", "A": "#76FF03",
            "BBB": "#FFB300", "BB": "#FF6D00", "B": "#FF3D00", "CCC": "#D50000"
        }
        return colors.get(rating, "#9E9E9E")

    @classmethod
    def build_esg_card(cls, data: Dict) -> Dict:
        """
        构建ESG企微消息卡片
        data: generate_report() 返回的字典
        """
        scores = data["scores"]
        vs_ind = data["vs_industry"]
        e_score = scores["E（环境）"]
        s_score = scores["S（社会）"]
        g_score = scores["G（治理）"]
        overall = scores["综合"]
        rating = data["rating"]
        company = data["company"]
        industry = data["industry"]
        highlights = data["highlights"]

        def diff_tag(diff_val: float) -> str:
            if diff_val > 0:
                return f"<font color='green'>+{diff_val:.1f} ↑</font>"
            elif diff_val < 0:
                return f"<font color='red'>{diff_val:.1f} ↓</font>"
            return "0.0"

        # 计算同业排名
        peer_data = data.get("peer_comparison", [])
        peer_rank = None
        for i, peer in enumerate(peer_data, 1):
            if peer["company"] == company:
                peer_rank = i
                break

        rank_text = f"同业第{peer_rank}名（共{len(peer_data)}家）" if peer_rank else ""

        card = {
            "msgtype": "interactive",
            "interactive": {
                "tag": "card",
                "card": {
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "text": f"📊 ESG研究报告 | {company}"
                        },
                        "description": {
                            "tag": "markdown",
                            "content": (
                                f"**行业：** {industry}  |  "
                                f"**ESG评级：** <font color='{cls.rating_to_color(rating)}'>{rating}</font>\n"
                                f"**核心亮点：** {highlights}"
                            )
                        },
                        "color": cls.rating_to_color(rating)
                    },
                    "elements": [
                        # 评分区
                        {
                            "tag": "div",
                            "text": {
                                "tag": "markdown",
                                "content": (
                                    "## 📈 ESG评分\n"
                                    "| 维度 | 评分 | vs行业均值 |"
                                    "|------|------|------------|"
                                    f"| 🌿 E（环境） | **{e_score}** | {diff_tag(vs_ind['E'])} |"
                                    f"| 👥 S（社会） | **{s_score}** | {diff_tag(vs_ind['S'])} |"
                                    f"| ⚖️ G（治理） | **{g_score}** | {diff_tag(vs_ind['G'])} |"
                                    f"| **综合** | **{overall}** | {diff_tag(vs_ind['综合'])} |"
                                )
                            }
                        },
                        {"tag": "hr"},
                        # E维度亮点
                        {
                            "tag": "section",
                            "text": {
                                "tag": "markdown",
                                "content": (
                                    f"**🌿 E（环境）[{e_score}]**\n"
                                    f"• 碳排放：{data['details']['E（环境）'].get('carbon', 'N/A')[:50]}...\n"
                                    f"• 能源：{data['details']['E（环境）'].get('energy', 'N/A')[:50]}...\n"
                                    f"• 优势：{data['details']['E（环境）'].get('strengths', 'N/A')[:30]}"
                                )
                            }
                        },
                        {"tag": "hr"},
                        # S维度亮点
                        {
                            "tag": "section",
                            "text": {
                                "tag": "markdown",
                                "content": (
                                    f"**👥 S（社会）[{s_score}]**\n"
                                    f"• 员工关怀：{data['details']['S（社会）'].get('employee', 'N/A')[:50]}...\n"
                                    f"• 供应链：{data['details']['S（社会）'].get('supply_chain', 'N/A')[:50]}...\n"
                                    f"• 优势：{data['details']['S（社会）'].get('strengths', 'N/A')[:30]}"
                                )
                            }
                        },
                        {"tag": "hr"},
                        # G维度亮点
                        {
                            "tag": "section",
                            "text": {
                                "tag": "markdown",
                                "content": (
                                    f"**⚖️ G（治理）[{g_score}]**\n"
                                    f"• 董事会：{data['details']['G（治理）'].get('board', 'N/A')[:50]}...\n"
                                    f"• 信息披露：{data['details']['G（治理）'].get('disclosure', 'N/A')[:50]}...\n"
                                    f"• 优势：{data['details']['G（治理）'].get('strengths', 'N/A')[:30]}"
                                )
                            }
                        },
                        {"tag": "hr"},
                    ]
                }
            }
        }

        # 添加同业对比区
        if peer_data:
            peer_rows = []
            for peer in peer_data[:5]:
                marker = " ★" if peer["company"] == company else ""
                peer_rows.append(
                    f"| {peer['company']}{marker} | {peer['overall']} | "
                    f"<font color='{cls.rating_to_color(peer['rating'])}'>{peer['rating']}</font> | "
                    f"{peer['e']} | {peer['s']} | {peer['g']} |"
                )
            peer_section = {
                "tag": "section",
                "text": {
                    "tag": "markdown",
                    "content": (
                        "**🏆 同业ESG对比（Top 5）**\n"
                        "| 公司 | 综合 | 评级 | E | S | G |\n"
                        "|------|------|------|---|---|---|\n"
                        + "\n".join(peer_rows)
                    )
                }
            }
            card["interactive"]["card"]["elements"].extend([
                {"tag": "hr"},
                peer_section
            ])

        # 底部数据来源
        card["interactive"]["card"]["elements"].append({
            "tag": "note",
            "elements": [
                {"tag": "plain_text", "text": f"数据来源：ESG内置数据库 | {data['report_date']} | ★ = 目标公司"}
            ]
        })

        return card

    @classmethod
    def build_esg_summary_card(cls, companies: List[Dict]) -> Dict:
        """
        构建ESG摘要对比卡片（多公司对比）
        companies: [{"company": "xxx", "overall": 80, "rating": "AA", ...}]
        """
        rows = []
        for c in companies:
            rows.append(
                f"| {c['company']} | {c['overall']} | "
                f"<font color='{cls.rating_to_color(c['rating'])}'>{c['rating']}</font> | "
                f"{c.get('e_score', '-')} | {c.get('s_score', '-')} | {c.get('g_score', '-')} |"
            )

        card = {
            "msgtype": "interactive",
            "interactive": {
                "tag": "card",
                "card": {
                    "header": {
                        "title": {"tag": "plain_text", "text": "📊 ESG评分对比"},
                        "color": "#2196F3"
                    },
                    "elements": [
                        {
                            "tag": "section",
                            "text": {
                                "tag": "markdown",
                                "content": (
                                    "| 公司 | 综合 | 评级 | E | S | G |\n"
                                    "|------|------|------|---|---|---|\n"
                                    + "\n".join(rows)
                                )
                            }
                        },
                        {
                            "tag": "note",
                            "elements": [
                                {"tag": "plain_text", "text": "数据来源：ESG内置数据库 | 2025年年报"}
                            ]
                        }
                    ]
                }
            }
        }
        return card


def send_wecom_card(card: Dict, webhook_url: str) -> Dict:
    """
    发送企微卡片到webhook
    card: build_esg_card() 返回的卡片
    webhook_url: 企业微信机器人webhook地址
    """
    import urllib.request
    import urllib.error

    data = json.dumps(card).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("errcode") == 0:
                return {"success": True, "errmsg": result.get("errmsg", "ok")}
            return {"success": False, "errcode": result.get("errcode"), "errmsg": result.get("errmsg")}
    except urllib.error.URLError as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # 测试
    from esg_engine import ESGEngine
    engine = ESGEngine()
    result = engine.generate_report("宁德时代", format="json")
    card = WecomCard.build_esg_card(result)
    print(json.dumps(card, ensure_ascii=False, indent=2)[:2000])
