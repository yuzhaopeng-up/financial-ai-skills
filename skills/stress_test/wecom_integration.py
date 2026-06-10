"""
企微集成 - 压力测试报告发送
WeCom Integration for Stress Test Report Delivery
"""

import json
import urllib.request
from typing import Dict, Any, Optional


class WeComStressTestCard:
    """企微压力测试卡片构建器"""

    @staticmethod
    def build_card(results: Dict[str, Any], title: str = "银行压力测试报告") -> Dict[str, Any]:
        """
        构建企微消息卡片
        
        Args:
            results: StressTestEngine.run_stress_test() 返回的结果
            title: 卡片标题
        
        Returns:
            企微消息格式的卡片数据
        """
        info = results.get("bank_info", {})
        base = results.get("baseline", {})
        scenarios = results.get("stress_scenarios", {})

        # 构建表格行
        table_rows = []
        for name, r in scenarios.items():
            car_color = "red" if r["car"] < 10.5 else "yellow" if r["car"] < 12 else "green"
            row = {
                "scenario": name,
                "car": f"{r['car']:.2f}%",
                "car_color": car_color,
                "npl": f"{r['npl_ratio']:.2f}%",
                "roe": f"{r['roe']:.2f}%",
                "lcr": f"{r['lcr']:.2f}%",
                "risk_score": f"{r['risk_score']}/10"
            }
            table_rows.append(row)

        card = {
            "msgtype": "interactive",
            "interactive": {
                "card": {
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "text": f"🏦 {title}"
                        },
                        "color": "red"
                    },
                    "elements": [
                        {
                            "tag": "markdown",
                            "content": f"**银行信息** | 总资产: **{info.get('total_assets', 0):.0f}亿** | 资本金: **{info.get('capital', 0):.0f}亿亿** | 当前不良率: **{info.get('npl_ratio', 0):.2f}%**"
                        },
                        {"tag": "hr"},
                        {
                            "tag": "markdown",
                            "content": "**压力测试结果对比**"
                        },
                        {
                            "tag": "table",
                            "columns": [
                                {"tag": "col", "title": "情景", "width": 60},
                                {"tag": "col", "title": "资本充足率", "width": 90},
                                {"tag": "col", "title": "不良率", "width": 70},
                                {"tag": "col", "title": "ROE", "width": 70},
                                {"tag": "col", "title": "LCR", "width": 70},
                                {"tag": "col", "title": "风险评分", "width": 80}
                            ],
                            "elements": [
                                {
                                    "tag": "tr",
                                    "tr": [
                                        {"tag": "td", "colspan": 1, "rowspan": 1, "color": "grey", "content": {"tag": "plain_text", "text": "基准"}},
                                        {"tag": "td", "colspan": 1, "rowspan": 1, "color": "grey", "content": {"tag": "plain_text", "text": f"{base.get('car', 0):.2f}%"}},
                                        {"tag": "td", "colspan": 1, "rowspan": 1, "color": "grey", "content": {"tag": "plain_text", "text": f"{base.get('npl_ratio', 0):.2f}%"}},
                                        {"tag": "td", "colspan": 1, "rowspan": 1, "color": "grey", "content": {"tag": "plain_text", "text": f"{base.get('roe', 0):.2f}%"}},
                                        {"tag": "td", "colspan": 1, "rowspan": 1, "color": "grey", "content": {"tag": "plain_text", "text": f"{base.get('lcr', 0):.0f}%"}},
                                        {"tag": "td", "colspan": 1, "rowspan": 1, "color": "grey", "content": {"tag": "plain_text", "text": "-"}}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        }

        # Add stress scenario rows to table
        for row in table_rows:
            tr = {
                "tag": "tr",
                "tr": [
                    {"tag": "td", "content": {"tag": "plain_text", "text": row["scenario"]}},
                    {"tag": "td", "color": row["car_color"], "content": {"tag": "plain_text", "text": row["car"]}},
                    {"tag": "td", "content": {"tag": "plain_text", "text": row["npl"]}},
                    {"tag": "td", "content": {"tag": "plain_text", "text": row["roe"]}},
                    {"tag": "td", "content": {"tag": "plain_text", "text": row["lcr"]}},
                    {"tag": "td", "content": {"tag": "plain_text", "text": row["risk_score"]}}
                ]
            }
            card["interactive"]["card"]["elements"][3]["elements"].append(tr)

        # Add risk channels
        if scenarios:
            first_scenario = list(scenarios.values())[0]
            if first_scenario.get("risk_channels"):
                channel_content = "**风险传导路径:**\n"
                for ch in first_scenario["risk_channels"][:3]:
                    channel_content += f"• {ch}\n"
                card["interactive"]["card"]["elements"].append({"tag": "hr"})
                card["interactive"]["card"]["elements"].append({
                    "tag": "markdown",
                    "content": channel_content
                })

        return card

    @staticmethod
    def send_card(card: Dict[str, Any], webhook_url: str) -> Dict[str, Any]:
        """
        发送企微卡片消息
        
        Args:
            card: build_card() 构建的卡片数据
            webhook_url: 企业微信机器人的 webhook URL
        
        Returns:
            发送结果
        """
        try:
            data = json.dumps(card, ensure_ascii=False).encode("utf-8")
            req = urllib.request.Request(
                webhook_url,
                data=data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                if result.get("errcode") == 0:
                    return {"success": True, "errmsg": result.get("errmsg")}
                else:
                    return {"success": False, "errmsg": result.get("errmsg")}
        except Exception as e:
            return {"success": False, "error": str(e)}


def send_stress_test_card(results: Dict[str, Any], webhook_url: str, 
                          title: str = "银行压力测试报告") -> Dict[str, Any]:
    """
    便捷函数：直接发送压力测试报告到企微
    
    Args:
        results: StressTestEngine.run_stress_test() 返回的结果
        webhook_url: 企业微信机器人的 webhook URL
        title: 卡片标题
    
    Returns:
        发送结果
    """
    card = WeComStressTestCard.build_card(results, title)
    return WeComStressTestCard.send_card(card, webhook_url)


# 简单文本消息格式（备用）
def send_simple_text(results: Dict[str, Any], webhook_url: str) -> Dict[str, Any]:
    """发送简单文本格式的压力测试摘要"""
    info = results.get("bank_info", {})
    base = results.get("baseline", {})
    scenarios = results.get("stress_scenarios", {})

    content = f"""🏦 **银行压力测试报告**

**基本信息**: 总资产 {info.get('total_assets', 0):.0f}亿 | 资本金 {info.get('capital', 0):.0f}亿 | 不良率 {info.get('npl_ratio', 0):.2f}%

**基准**: CAR {base.get('car', 0):.2f}% | NPL {base.get('npl_ratio', 0):.2f}% | ROE {base.get('roe', 0):.2f}%

**压力测试结果:**
"""

    for name, r in scenarios.items():
        content += f"\n• **{name}**: CAR {r['car']:.1f}% | NPL {r['npl_ratio']:.1f}% | ROE {r['roe']:.1f}% | LCR {r['lcr']:.0f}% | 风险 {r['risk_score']}/10"

    msg = {"msgtype": "markdown", "markdown": {"content": content}}

    try:
        data = json.dumps(msg, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(webhook_url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return {"success": result.get("errcode") == 0, "errmsg": result.get("errmsg")}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Test
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from stress_engine import StressTestEngine
    
    engine = StressTestEngine()
    results = engine.run_stress_test(1000, 80, 1.5)
    
    card = WeComStressTestCard.build_card(results)
    print(json.dumps(card, ensure_ascii=False, indent=2))
