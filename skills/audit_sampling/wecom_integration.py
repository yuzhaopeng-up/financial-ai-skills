#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
审计抽样 - 企微集成
支持企微消息卡片格式的接入
"""

import json
from audit_sampling_engine import AuditSamplingEngine


class AuditSamplingWecom:
    def __init__(self):
        self.engine = AuditSamplingEngine(api_mode=True)

    def handle_message(self, text: str, user_id: str = None) -> dict:
        text = text.strip()

        # 解析命令
        if text.startswith("审计抽样") or text.startswith("抽样"):
            return self._handle_sampling(text)

        elif text.startswith("抽样方案"):
            return self._handle_plan(text)

        elif text in ["审计帮助", "帮助", "抽样帮助"]:
            return self._build_help()

        # 默认为抽样
        return self._handle_sampling("抽样 " + text)

    def _handle_sampling(self, text: str) -> dict:
        """处理抽样命令"""
        # 提取参数
        params = {}
        content = text.replace("审计抽样", "").replace("抽样", "").strip()

        # 解析 key=value 格式
        for part in content.split():
            if "=" in part:
                key, value = part.split("=", 1)
                key = key.strip()
                try:
                    if "." in value:
                        params[key] = float(value)
                    else:
                        params[key] = int(value)
                except ValueError:
                    params[key] = value

        coverage = params.get("coverage", params.get("覆盖", 0.95))
        high_threshold = params.get("high_threshold", params.get("高风险阈值", 1_000_000))
        medium_threshold = params.get("medium_threshold", params.get("中风险阈值", 100_000))

        # 生成演示数据
        import random
        random.seed(42)
        types = [
            "转账", "贷款发放", "还款", "手续费", "理财购买", "理财赎回",
            "担保", "信用证", "贴现", "咨询费", "资产处置"
        ]
        transactions = []
        for i in range(200):
            amount = random.uniform(100, 5_000_000)
            if i < 20:
                amount = random.uniform(1_000_000, 5_000_000)
            elif i < 60:
                amount = random.uniform(100_000, 1_000_000)
            transactions.append({
                "id": f"TXN_{i+1:06d}",
                "amount": round(amount, 2),
                "type": random.choice(types),
                "date": f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
                "counterparty": f"对手方{random.randint(1, 20)}",
                "description": random.choice(["正常", "大额", "异常", "关联交易"])
            })

        config = {
            "high_risk_amount_threshold": high_threshold,
            "medium_risk_amount_threshold": medium_threshold,
            "coverage_target": coverage,
        }
        engine = AuditSamplingEngine(config=config, api_mode=True)
        processed = engine.load_transactions(transactions)
        result = engine.sample(processed, coverage_target=coverage)

        return self._build_result_card(result)

    def _handle_plan(self, text: str) -> dict:
        """处理抽样方案命令"""
        params = {}
        content = text.replace("抽样方案", "").strip()
        for part in content.split():
            if "=" in part:
                key, value = part.split("=", 1)
                try:
                    params[key.strip()] = float(value) if "." in value else int(value)
                except ValueError:
                    params[key.strip()] = value

        coverage = params.get("coverage", params.get("覆盖", 0.95))

        # 生成演示数据
        import random
        random.seed(42)
        transactions = []
        for i in range(200):
            transactions.append({
                "id": f"TXN_{i+1:06d}",
                "amount": round(random.uniform(100, 5_000_000), 2),
                "type": random.choice(["转账", "贷款", "手续费"]),
            })

        engine = AuditSamplingEngine(api_mode=True)
        processed = engine.load_transactions(transactions)
        plan = engine.generate_sampling_plan(processed, {"coverage_target": coverage})

        return self._build_plan_card(plan)

    def _build_help(self) -> dict:
        return {
            "type": "text",
            "content": """🦞 **风险导向审计抽样引擎**

📋 功能：基于风险模型自动生成审计抽样方案

📝 命令：
  `审计抽样` - 使用默认参数抽样200笔演示数据
  `抽样 覆盖=0.95` - 指定覆盖率目标
  `抽样 高风险阈值=100万 中风险阈值=10万` - 指定金额阈值
  `抽样方案` - 生成抽样方案（不执行抽样）

⚠️ 验收标准：覆盖率≥95%，高风险层100%覆盖

示例：
  `审计抽样`
  `抽样 覆盖=0.95 高风险阈值=500000`"""
        }

    def _build_result_card(self, result: dict) -> dict:
        """构建结果卡片"""
        status_icon = "success" if result.get("coverage_met") else "warning"
        status_text = "✅ 达标" if result.get("coverage_met") else "⚠️ 未达标"

        # 样本分布摘要
        counts = result.get("sample_counts", {})
        strata = result.get("strata_summary", {})

        # 构造 elements
        elements = [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**📊 抽样概况**\n"
                              f"总交易: {result.get('total_transactions', 0):,} 笔\n"
                              f"样本量: {result.get('sample_size', 0):,} 笔 ({result.get('sample_ratio', 0)*100:.1f}%)\n"
                              f"金额覆盖: {result.get('coverage', 0)*100:.2f}%\n"
                              f"目标覆盖: {result.get('coverage_target', 0)*100:.0f}%\n"
                              f"**{status_text}**"
                }
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**🔢 分层抽样**\n"
                              f"🔴 高风险: {counts.get('high', 0)} 笔 "
                              f"(全层{strata.get('high', {}).get('total', 0)}笔，"
                              f"抽样率{strata.get('high', {}).get('sample_rate', 0)*100:.0f}%)\n"
                              f"🟡 中风险: {counts.get('medium', 0)} 笔 "
                              f"(全层{strata.get('medium', {}).get('total', 0)}笔，"
                              f"抽样率{strata.get('medium', {}).get('sample_rate', 0)*100:.0f}%)\n"
                              f"🟢 低风险: {counts.get('low', 0)} 笔 "
                              f"(全层{strata.get('low', {}).get('total', 0)}笔，"
                              f"抽样率{strata.get('low', {}).get('sample_rate', 0)*100:.0f}%)"
                }
            },
        ]

        # 添加样本清单（前5条）
        samples = result.get("samples", [])
        if samples:
            sample_lines = ["**📋 样本清单（Top 5）**\n"]
            sample_lines.append(f"{'ID':<12} {'金额':>12} {'风险级'}")
            sample_lines.append("-" * 40)
            for s in samples[:5]:
                sample_lines.append(
                    f"{str(s.get('id', '')):<12} "
                    f"{s.get('amount', 0):>12,.2f} "
                    f"{s.get('_risk_level', '')}"
                )
            elements.append({
                "tag": "div",
                "text": {"tag": "lark_md", "content": "\n".join(sample_lines)}
            })

        elements.append({"tag": "hr"})
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"⏰ 生成时间: {result.get('sampled_at', '')}"
            }
        })

        header_template = "green" if result.get("coverage_met") else "orange"

        return {
            "type": "interactive",
            "card": {
                "header": {
                    "title": "📊 审计抽样报告",
                    "template": header_template
                },
                "elements": elements
            }
        }

    def _build_plan_card(self, plan: dict) -> dict:
        """构建方案卡片"""
        strata = plan.get("strata", {})
        total_est = plan.get("estimated_total", 0)

        elements = [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**📋 抽样方案预览**\n"
                              f"预估样本量: ~{total_est} 笔\n"
                              f"覆盖率目标: {plan.get('coverage_target', 0)*100:.0f}%\n"
                              f"⏰ 生成时间: {plan.get('generated_at', '')}"
                }
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**📊 分层预估**\n"
                              f"🔴 高风险: {strata.get('high', {}).get('total', 0)}笔 "
                              f"→ 抽样{strata.get('high', {}).get('estimated_samples', 0)}笔 "
                              f"(100%全抽)\n"
                              f"🟡 中风险: {strata.get('medium', {}).get('total', 0)}笔 "
                              f"→ 抽样{strata.get('medium', {}).get('estimated_samples', 0)}笔 "
                              f"({strata.get('medium', {}).get('sample_rate', 0)*100:.0f}%)\n"
                              f"🟢 低风险: {strata.get('low', {}).get('total', 0)}笔 "
                              f"→ 抽样{strata.get('low', {}).get('estimated_samples', 0)}笔 "
                              f"({strata.get('low', {}).get('sample_rate', 0)*100:.0f}%)"
                }
            },
        ]

        return {
            "type": "interactive",
            "card": {
                "header": {
                    "title": "📋 抽样方案",
                    "template": "blue"
                },
                "elements": elements
            }
        }


def handle(text: str, user_id: str = None) -> dict:
    """入口函数"""
    return AuditSamplingWecom().handle_message(text, user_id)


if __name__ == "__main__":
    # 测试
    result = handle("审计抽样")
    print(json.dumps(result, ensure_ascii=False, indent=2)[:1000])
    print()
    result2 = handle("抽样 覆盖=0.95")
    print(json.dumps(result2, ensure_ascii=False, indent=2)[:1000])
