#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资金流动性风险预警 - 企微集成
"""

import json
from liquidity_alert_engine import LiquidityAlertEngine


class LiquidityAlertWecom:
    def __init__(self):
        self.engine = LiquidityAlertEngine(api_mode=True)

    def handle_message(self, text: str, user_id: str = None) -> dict:
        text = text.strip()

        if text.startswith("流动性预警") or text.startswith("流动性分析"):
            return self._handle_alert(text)
        elif text.startswith("LCR检查") or text.startswith("lcr"):
            return self._handle_lcr(text)
        elif text.startswith("流动性压力测试") or text.startswith("压力测试"):
            return self._handle_stress(text)
        elif text in ["流动性帮助", "帮助", "help"]:
            return self._build_help()
        return self._build_help()

    def _handle_alert(self, text: str) -> dict:
        parts = text.replace("流动性预警", "").replace("流动性分析", "").strip()
        try:
            nums = [float(x) for x in parts.split() if self._is_number(x)]
            if len(nums) >= 3:
                balance, total_inflow, total_outflow = nums[0], nums[1], nums[2]
            elif len(nums) == 2:
                balance, total_inflow = nums[0], nums[1]
                total_outflow = total_inflow * 0.5
            else:
                return self._build_help()
        except:
            return self._build_help()

        from datetime import datetime, timedelta
        today = datetime.now()
        inflows = [
            {"date": (today - timedelta(days=i)).strftime("%Y-%m-%d"), "amount": total_inflow / 30}
            for i in range(30)
        ]
        outflows = [
            {"date": (today - timedelta(days=i)).strftime("%Y-%m-%d"), "amount": total_outflow / 30}
            for i in range(30)
        ]
        result = self.engine.analyze({
            "balance": balance,
            "inflows": inflows,
            "outflows": outflows,
        })
        return self._build_result_card(result)

    def _handle_lcr(self, text: str) -> dict:
        parts = text.replace("LCR检查", "").replace("lcr", "").strip()
        tokens = parts.split()
        if len(tokens) >= 4:
            name, hqla, nqla, net_out = tokens[0], float(tokens[1]), float(tokens[2]), float(tokens[3])
        else:
            name, hqla, nqla, net_out = "测试机构", 1000000.0, 500000.0, 1200000.0
        result = self.engine.check_lcr(name, hqla, nqla, net_out)
        return self._build_lcr_card(result)

    def _handle_stress(self, text: str) -> dict:
        parts = text.replace("流动性压力测试", "").replace("压力测试", "").strip()
        tokens = parts.split()
        if len(tokens) >= 3:
            scenario, days, balance = tokens[0], int(tokens[1]), float(tokens[2])
        else:
            scenario, days, balance = "中度", 30, 1000000.0
        result = self.engine.stress_test(scenario, days, [], [], balance)
        return self._build_stress_card(result)

    def _build_help(self) -> dict:
        return {
            "type": "text",
            "content": (
                "🦞 **资金流动性风险预警引擎**\n\n"
                "📋 功能：30天流动性预测 + 多级预警\n\n"
                "📝 命令：\n"
                "`流动性预警 [余额] [流入] [流出]`\n"
                "  示例：流动性预警 1000000 600000 400000\n\n"
                "`LCR检查 [机构名] [HQLA] [NQLA] [净流出]`\n"
                "  示例：LCR检查 某银行 1000000 500000 1200000\n\n"
                "`流动性压力测试 [情景] [天数] [余额]`\n"
                "  示例：流动性压力测试 中度 30 1000000\n\n"
                "⚠️ 预警等级：🔴红色 🟡黄色 🟢绿色\n"
                "📐 预警准确率：≥ 85%"
            ),
        }

    def _build_result_card(self, result: dict) -> dict:
        level = result["alert_level"]
        color_map = {"red": "red", "yellow": "orange", "green": "green"}
        fc = result["forecast_30d"]
        ga = result["gap_analysis"]

        risk_lines = []
        for sig in result["risk_signals"][:3]:
            risk_lines.append(f"\n• [{sig['level'].upper()}] {sig['signal']}: {sig['detail']}")
        risk_signals_md = "".join(risk_lines) if risk_lines else "\n• 无"

        return {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"💧 流动性预警 - {result['alert_label']}",
                    "template": color_map.get(level, "gray"),
                },
                "elements": [
                    {"tag": "div", "text": {"tag": "lark_md", "content": f"**当前余额**: ¥{result['current_balance']:,.2f}"}},
                    {"tag": "hr"},
                    {"tag": "div", "text": {"tag": "lark_md", "content": (
                        f"**30天预测**: 净流量 ¥{fc['net_flow']:,.2f}\n"
                        f"**期末余额**: ¥{fc['projected_balance']:,.2f}\n"
                        f"**最低余额**: ¥{fc['min_balance']:,.2f} (第{fc['min_balance_day']}天)"
                    )}},
                    {"tag": "hr"},
                    {"tag": "div", "text": {"tag": "lark_md", "content": f"**流动性缺口**: ¥{ga['cumulative_gap']:,.2f} (缺口率 {ga['gap_ratio']:.2%})"}},
                    {"tag": "hr"},
                    {"tag": "div", "text": {"tag": "lark_md", "content": (
                        f"**流入统计**: 日均 ¥{result['inflow_stats']['avg_daily']:,.2f}\n"
                        f"**流出统计**: 日均 ¥{result['outflow_stats']['avg_daily']:,.2f}"
                    )}},
                    {"tag": "hr"},
                    {"tag": "div", "text": {"tag": "lark_md", "content": "**风险信号**" + risk_signals_md}},
                    {"tag": "hr"},
                    {"tag": "div", "text": {"tag": "lark_md", "content": f"📐 **预警准确率**: {result['accuracy_estimate']:.1f}%\n⏰ {result['timestamp']}"}},
                ],
            },
        }

    def _build_lcr_card(self, result: dict) -> dict:
        color = {"red": "red", "yellow": "orange", "green": "green"}.get(result["level"], "gray")
        return {
            "type": "interactive",
            "card": {
                "header": {"title": f"🏦 LCR检查 - {result['label']}", "template": color},
                "elements": [
                    {"tag": "div", "text": {"tag": "lark_md", "content": f"**机构**: {result['institution']}"}},
                    {"tag": "hr"},
                    {"tag": "div", "text": {"tag": "lark_md", "content": (
                        f"**LCR**: {result['lcr']:.1f}%\n"
                        f"**达标**: {'✅ 达标 (≥100%)' if result['达标'] else '❌ 不达标 (<100%)'}"
                    )}},
                    {"tag": "hr"},
                    {"tag": "div", "text": {"tag": "lark_md", "content": (
                        f"**高质量流动性资产**: ¥{result['hqla']:,.2f}\n"
                        f"**其他流动性资产**: ¥{result['nqla']:,.2f}\n"
                        f"**30天净流出**: ¥{result['net_outflows_30d']:,.2f}"
                    )}},
                ],
            },
        }

    def _build_stress_card(self, result: dict) -> dict:
        color = "red" if result["survive_days"] < result["days"] else "green"
        return {
            "type": "interactive",
            "card": {
                "header": {"title": f"🧪 压力测试 - {result['scenario']}情景", "template": color},
                "elements": [
                    {"tag": "div", "text": {"tag": "lark_md", "content": (
                        f"**情景**: {result['scenario']} | **持续**: {result['days']}天\n"
                        f"**乘数**: 流入×{result['multipliers']['inflow']} 流出×{result['multipliers']['outflow']}"
                    )}},
                    {"tag": "hr"},
                    {"tag": "div", "text": {"tag": "lark_md", "content": (
                        f"**日均净流量**: ¥{result['daily_net_flow']:,.2f}\n"
                        f"**预测期末余额**: ¥{result['projected_balance']:,.2f}"
                    )}},
                    {"tag": "hr"},
                    {"tag": "div", "text": {"tag": "lark_md", "content": (
                        f"**可支撑天数**: {result['survive_days']}天\n"
                        f"**累计缺口**: ¥{result['cumulative_shortfall']:,.2f}"
                    )}},
                ],
            },
        }

    @staticmethod
    def _is_number(s: str) -> bool:
        try:
            float(s)
            return True
        except:
            return False


def handle(text: str, user_id: str = None) -> dict:
    return LiquidityAlertWecom().handle_message(text, user_id)


if __name__ == "__main__":
    r = handle("流动性预警 1000000 600000 400000")
    print(json.dumps(r, ensure_ascii=False, indent=2)[:500])
