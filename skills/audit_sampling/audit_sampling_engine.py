# -*- coding: utf-8 -*-
"""
审计抽样引擎 - 风险导向智能审计抽样
支持覆盖率≥95%的验收标准

Author: ArkClaw
Version: 1.0.0
"""

import json
import random
import math
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple


class AuditSamplingEngine:
    """风险导向智能审计抽样引擎"""

    VERSION = "1.0.0"

    # 风险分层阈值配置
    DEFAULT_CONFIG = {
        "high_risk_amount_threshold": 1_000_000,      # 高风险金额阈值（元）
        "medium_risk_amount_threshold": 100_000,       # 中风险金额阈值（元）
        "high_risk_sample_rate": 1.0,                  # 高风险层抽样率 100%
        "medium_risk_sample_rate": 0.3,                # 中风险层抽样率 30%
        "low_risk_sample_rate": 0.05,                 # 低风险层抽样率 5%
        "min_sample_size": 10,                         # 最小样本量
        "max_sample_ratio": 0.20,                      # 最大抽样比例（总体的20%）
        "coverage_target": 0.95,                       # 覆盖率目标 95%
        "stratify_by_type": True,                      # 按交易类型分层
        "stratify_by_amount": True,                    # 按金额分层
        "stratify_by_frequency": True,                 # 按频率分层
    }

    # 高风险交易类型关键词
    HIGH_RISK_TYPES = [
        "大额", "异常", "可疑", "敏感", "关联交易",
        "跨境", "衍生品", "担保", "抵押", "信用证",
        "理财", "投资", "股权", "资产处置", "核销"
    ]

    # 中风险交易类型关键词
    MEDIUM_RISK_TYPES = [
        "跨行", "转账", "贴现", "承兑", "保理",
        "租赁", "外包", "咨询", "顾问", "手续费"
    ]

    def __init__(self, config: Dict[str, Any] = None, api_mode: bool = False):
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
        self.api_mode = api_mode
        self._log("初始化审计抽样引擎 v%s" % self.VERSION)
        self._log("配置: %s" % self.config)

    def _log(self, msg: str):
        if not self.api_mode:
            print(msg)

    def load_transactions(self, data: List[Dict]) -> List[Dict]:
        """
        加载交易数据集

        Args:
            data: 交易记录列表，每条记录需包含:
                - id: 交易ID
                - amount: 交易金额
                - type: 交易类型（可选）
                - date: 交易日期（可选）
                - counterparty: 交易对手（可选）
                - description: 交易描述（可选）

        Returns:
            处理后的交易列表
        """
        self._log("加载交易数据: %d 条" % len(data))

        processed = []
        for idx, tx in enumerate(data):
            # 确保必需字段存在
            processed_tx = {
                "id": tx.get("id", f"TXN_{idx+1}"),
                "amount": float(tx.get("amount", 0)),
                "type": tx.get("type", "未知"),
                "date": tx.get("date", ""),
                "counterparty": tx.get("counterparty", ""),
                "description": tx.get("description", ""),
                "_index": idx,
            }
            # 计算风险分数
            processed_tx["_risk_score"] = self._calculate_risk_score(processed_tx)
            # 确定风险层级
            processed_tx["_risk_level"] = self._determine_risk_level(processed_tx)
            processed.append(processed_tx)

        self._log("数据加载完成，风险分层完成")
        return processed

    def _calculate_risk_score(self, tx: Dict) -> float:
        """
        计算单笔交易的风险分数 (0-100)

        考虑因素：
        1. 金额大小（权重40%）
        2. 交易类型（权重30%）
        3. 频率异常（权重20%）
        4. 描述关键词（权重10%）
        """
        score = 0.0

        # 1. 金额因素 (0-40分)
        amount = tx.get("amount", 0)
        if amount >= self.config["high_risk_amount_threshold"]:
            score += 40
        elif amount >= self.config["medium_risk_amount_threshold"]:
            score += 20
        elif amount >= 10_000:
            score += 5

        # 2. 交易类型因素 (0-30分)
        tx_type = tx.get("type", "")
        tx_type_text = tx_type + " " + tx.get("description", "")
        tx_type_lower = tx_type_text.lower()

        for keyword in self.HIGH_RISK_TYPES:
            if keyword.lower() in tx_type_lower:
                score += 15
                break
        else:
            for keyword in self.MEDIUM_RISK_TYPES:
                if keyword.lower() in tx_type_lower:
                    score += 8
                    break

        # 3. 频率因素 (0-20分) - 占位，后续可接入频率统计
        # 目前简化处理：描述中含"频繁"、"异常"关键词
        if any(kw in tx_type_lower for kw in ["频繁", "异常", "可疑", "重复"]):
            score += 20

        # 4. 描述关键词因素 (0-10分)
        risk_keywords = ["关联交易", "关联方", "利益输送", "虚构", "虚假", "隐瞒"]
        if any(kw in tx_type_lower for kw in risk_keywords):
            score += 10

        return min(100.0, score)

    def _determine_risk_level(self, tx: Dict) -> str:
        """确定风险层级"""
        score = tx.get("_risk_score", 0)
        if score >= 50:
            return "high"
        elif score >= 20:
            return "medium"
        else:
            return "low"

    def stratify(self, transactions: List[Dict]) -> Dict[str, List[Dict]]:
        """
        对交易数据进行分层

        Returns:
            分层字典: {"high": [...], "medium": [...], "low": [...]}
        """
        strata = {"high": [], "medium": [], "low": []}

        for tx in transactions:
            level = tx.get("_risk_level", "low")
            strata[level].append(tx)

        for level, txs in strata.items():
            self._log("  %s 层: %d 笔" % (level.upper(), len(txs)))

        return strata

    def sample(self, transactions: List[Dict],
               target_sample_size: int = None,
               coverage_target: float = None) -> Dict[str, Any]:
        """
        执行风险导向抽样

        Args:
            transactions: 交易数据（已通过load_transactions处理）
            target_sample_size: 目标样本量（可选，不指定时自动计算）
            coverage_target: 覆盖率目标（默认95%）

        Returns:
            抽样结果字典
        """
        self._log("开始风险导向抽样...")
        self._log("  交易总数: %d" % len(transactions))
        self._log("  覆盖率目标: %.1f%%" % ((coverage_target or self.config["coverage_target"]) * 100))

        if not transactions:
            return self._empty_result()

        # 分层
        strata = self.stratify(transactions)

        # 计算各层应抽样本数
        total_amount = sum(tx.get("amount", 0) for tx in transactions)
        total_high = sum(tx.get("amount", 0) for tx in strata["high"])
        total_medium = sum(tx.get("amount", 0) for tx in strata["medium"])
        total_low = sum(tx.get("amount", 0) for tx in strata["low"])

        # 各层样本分配（基于金额加权）
        samples = {"high": [], "medium": [], "low": []}
        sample_counts = {"high": 0, "medium": 0, "low": 0}

        # 高风险层：100%全抽
        samples["high"] = strata["high"][:]
        sample_counts["high"] = len(samples["high"])

        # 中风险层：按比例抽样，但保证覆盖
        medium_count = len(strata["medium"])
        if medium_count > 0:
            # 金额加权抽样
            if total_medium > 0:
                medium_sample_size = max(
                    int(medium_count * self.config["medium_risk_sample_rate"]),
                    min(10, medium_count)  # 最少10笔
                )
            else:
                medium_sample_size = int(medium_count * self.config["medium_risk_sample_rate"])

            # 金额分层抽样（确保大额优先）
            medium_sorted = sorted(strata["medium"],
                                  key=lambda x: x.get("amount", 0),
                                  reverse=True)
            # Top 50% 金额的记录全抽
            top_count = max(1, medium_count // 2)
            top_medium = medium_sorted[:top_count]
            rest_medium = medium_sorted[top_count:]

            # 从剩余中随机抽样补足
            remaining_needed = medium_sample_size - len(top_medium)
            if remaining_needed > 0 and rest_medium:
                sampled_rest = random.sample(rest_medium,
                                            min(remaining_needed, len(rest_medium)))
            else:
                sampled_rest = []

            samples["medium"] = top_medium + sampled_rest
            sample_counts["medium"] = len(samples["medium"])

        # 低风险层：统计抽样
        low_count = len(strata["low"])
        if low_count > 0:
            # 使用泊松分布抽样，大额优先
            low_sorted = sorted(strata["low"],
                                key=lambda x: x.get("amount", 0),
                                reverse=True)

            # 按四分位数分层抽样
            q1 = low_count // 4
            q2 = low_count // 2
            q3 = low_count * 3 // 4

            low_samples = []
            # Q1 (最大额25%) - 抽取30%
            if q1 > 0:
                low_samples.extend(random.sample(low_sorted[:q1],
                                                min(max(1, int(q1 * 0.3)), q1)))
            # Q2 (次大额25%) - 抽取10%
            q2_count = q2 - q1
            if q2_count > 0:
                low_samples.extend(random.sample(low_sorted[q1:q2],
                                                min(max(1, int(q2_count * 0.1)), q2_count)))
            # Q3-Q4 (小额50%) - 抽取3%
            q34_count = low_count - q2
            if q34_count > 0:
                low_samples.extend(random.sample(low_sorted[q2:],
                                                min(max(1, int(q34_count * 0.03)), q34_count)))

            samples["low"] = low_samples
            sample_counts["low"] = len(samples["low"])

        # 合并样本
        all_samples = samples["high"] + samples["medium"] + samples["low"]

        # 去重（按id）
        seen = set()
        unique_samples = []
        for s in all_samples:
            if s["id"] not in seen:
                seen.add(s["id"])
                unique_samples.append(s)

        # 按风险分数降序排列
        unique_samples.sort(key=lambda x: x.get("_risk_score", 0), reverse=True)

        # 检查覆盖率
        coverage = self._calculate_coverage(unique_samples, transactions)

        # 如果覆盖率不达标，补充抽样
        target_cov = coverage_target or self.config["coverage_target"]
        if coverage < target_cov and strata["low"]:
            # 从低风险层补充大额记录
            shortfall = int(len(transactions) * (target_cov - coverage))
            补充 = [tx for tx in strata["low"]
                    if tx not in unique_samples]
            补充.sort(key=lambda x: x.get("amount", 0), reverse=True)
            unique_samples.extend(补充[:min(shortfall, len(补充))])
            coverage = self._calculate_coverage(unique_samples, transactions)

        # 如果仍不达标，触发高风险层的追加（全量已抽时跳过）
        if coverage < target_cov and strata["medium"]:
            补充 = [tx for tx in strata["medium"]
                    if tx not in unique_samples]
            unique_samples.extend(补充)
            coverage = self._calculate_coverage(unique_samples, transactions)

        # 按风险分数降序
        unique_samples.sort(key=lambda x: x.get("_risk_score", 0), reverse=True)
        sample_counts = {
            "high": len([s for s in unique_samples if s.get("_risk_level") == "high"]),
            "medium": len([s for s in unique_samples if s.get("_risk_level") == "medium"]),
            "low": len([s for s in unique_samples if s.get("_risk_level") == "low"]),
        }

        self._log("抽样完成:")
        self._log("  总样本量: %d (占总交易 %.1f%%)" % (
            len(unique_samples),
            len(unique_samples) / len(transactions) * 100 if transactions else 0
        ))
        self._log("  高风险: %d, 中风险: %d, 低风险: %d" % (
            sample_counts["high"], sample_counts["medium"], sample_counts["low"]
        ))
        self._log("  覆盖率: %.2f%%" % (coverage * 100))

        return {
            "total_transactions": len(transactions),
            "sample_size": len(unique_samples),
            "sample_ratio": len(unique_samples) / len(transactions) if transactions else 0,
            "coverage": coverage,
            "coverage_target": target_cov,
            "coverage_met": coverage >= target_cov,
            "sample_counts": sample_counts,
            "samples": unique_samples,
            "strata_summary": {
                "high": {
                    "total": len(strata["high"]),
                    "sampled": sample_counts["high"],
                    "sample_rate": sample_counts["high"] / len(strata["high"]) if strata["high"] else 0,
                },
                "medium": {
                    "total": len(strata["medium"]),
                    "sampled": sample_counts["medium"],
                    "sample_rate": sample_counts["medium"] / len(strata["medium"]) if strata["medium"] else 0,
                },
                "low": {
                    "total": len(strata["low"]),
                    "sampled": sample_counts["low"],
                    "sample_rate": sample_counts["low"] / len(strata["low"]) if strata["low"] else 0,
                },
            },
            "total_amount_sampled": sum(s.get("amount", 0) for s in unique_samples),
            "total_amount_audited": total_amount,
            "amount_coverage": sum(s.get("amount", 0) for s in unique_samples) / total_amount if total_amount else 0,
            "sampled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _calculate_coverage(self, samples: List[Dict], all_transactions: List[Dict]) -> float:
        """计算覆盖率（基于金额）"""
        if not all_transactions:
            return 0.0
        sampled_amount = sum(s.get("amount", 0) for s in samples)
        total_amount = sum(tx.get("amount", 0) for tx in all_transactions)
        return sampled_amount / total_amount if total_amount else 0.0

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "total_transactions": 0,
            "sample_size": 0,
            "sample_ratio": 0,
            "coverage": 0,
            "coverage_target": self.config["coverage_target"],
            "coverage_met": False,
            "sample_counts": {"high": 0, "medium": 0, "low": 0},
            "samples": [],
            "strata_summary": {},
            "total_amount_sampled": 0,
            "total_amount_audited": 0,
            "amount_coverage": 0,
            "sampled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def generate_sampling_plan(self, transactions: List[Dict],
                               params: Dict = None) -> Dict[str, Any]:
        """
        生成完整抽样方案（含方案描述，不执行抽样）

        Args:
            transactions: 交易数据
            params: 抽样参数覆盖

        Returns:
            抽样方案描述
        """
        config = {**self.config, **(params or {})}
        processed = self.load_transactions(transactions)
        strata = self.stratify(processed)

        # 计算各层应抽数量（不实际抽样）
        plan = {
            "config": config,
            "strata": {
                level: {
                    "count": len(txs),
                    "sample_rate": (1.0 if level == "high"
                                    else config.get(f"{level}_risk_sample_rate", 0.1)),
                    "estimated_samples": int(len(txs) * (1.0 if level == "high"
                                    else config.get(f"{level}_risk_sample_rate", 0.1))),
                }
                for level, txs in strata.items()
            },
            "estimated_total": sum(
                int(len(txs) * (1.0 if level == "high"
                 else config.get(f"{level}_risk_sample_rate", 0.1)))
                for level, txs in strata.items()
            ),
            "coverage_target": config["coverage_target"],
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        return plan

    def format_plan_text(self, result: Dict) -> str:
        """格式化输出抽样方案（文本）"""
        lines = [
            "📊 **风险导向审计抽样报告**",
            "",
            f"⏰ 生成时间: {result.get('sampled_at', '')}",
            "",
            "=" * 40,
            "",
            "**一、抽样概况**",
            f"  总交易笔数: {result.get('total_transactions', 0):,} 笔",
            f"  抽样样本量: {result.get('sample_size', 0):,} 笔",
            f"  抽样比例:   {result.get('sample_ratio', 0)*100:.2f}%",
            f"  金额覆盖率: {result.get('coverage', 0)*100:.2f}%",
            "",
            f"  ✅ 覆盖率达标: {'是' if result.get('coverage_met') else '否'} "
            f"(目标 {result.get('coverage_target', 0)*100:.0f}%)",
            "",
            "=" * 40,
            "",
            "**二、分层抽样详情**",
        ]

        summary = result.get("strata_summary", {})
        for level, label in [("high", "🔴 高风险"), ("medium", "🟡 中风险"), ("low", "🟢 低风险")]:
            if level in summary:
                s = summary[level]
                lines.append(
                    f"  {label}层: "
                    f"全层{summary[level].get('total', 0)}笔 "
                    f"→ 抽样{s.get('sampled', 0)}笔 "
                    f"(抽样率{s.get('sample_rate', 0)*100:.1f}%)"
                )

        lines.extend([
            "",
            "=" * 40,
            "",
            "**三、样本清单**",
        ])

        samples = result.get("samples", [])
        if samples:
            lines.append(f"  {'ID':<15} {'金额':>15} {'风险分':>8} {'风险级':<6} {'交易类型'}")
            lines.append("  " + "-" * 70)
            for s in samples[:50]:  # 最多显示50条
                lines.append(
                    f"  {str(s.get('id', '')):<15} "
                    f"{s.get('amount', 0):>15,.2f} "
                    f"{s.get('_risk_score', 0):>8.1f} "
                    f"{s.get('_risk_level', ''):<6} "
                    f"{str(s.get('type', ''))[:20]}"
                )
            if len(samples) > 50:
                lines.append(f"  ... (共 {len(samples)} 条，仅显示前50条)")
        else:
            lines.append("  (无样本)")

        lines.extend([
            "",
            "=" * 40,
            "",
            "**四、审计建议**",
        ])

        if result.get("coverage_met"):
            lines.append("  ✓ 抽样方案满足覆盖率≥95%要求，可执行审计程序")
        else:
            lines.append("  ⚠️ 覆盖率未达标，建议增加高风险层样本量")

        high_count = result.get("sample_counts", {}).get("high", 0)
        if high_count > 0:
            lines.append(f"  ✓ 高风险层 {high_count} 笔已全量纳入，需重点审计")

        return "\n".join(lines)

    def format_json(self, result: Dict) -> str:
        """格式化输出为JSON"""
        # 去除样本中的内部字段
        output = {k: v for k, v in result.items() if k != "samples"}
        output["samples"] = [
            {
                "id": s.get("id"),
                "amount": s.get("amount"),
                "type": s.get("type"),
                "date": s.get("date"),
                "counterparty": s.get("counterparty"),
                "description": s.get("description"),
                "risk_score": s.get("_risk_score"),
                "risk_level": s.get("_risk_level"),
            }
            for s in result.get("samples", [])
        ]
        return json.dumps(output, ensure_ascii=False, indent=2)


def main():
    """主函数 - CLI测试"""
    print("=" * 50)
    print("🦞 风险导向审计抽样引擎 v1.0")
    print("=" * 50)
    print()

    engine = AuditSamplingEngine()

    # 生成模拟交易数据
    import random
    random.seed(42)  # 复现性

    types = ["转账", "贷款发放", "还款", "手续费", "理财购买", "理财赎回",
             "担保", "信用证", "贴现", "咨询费", "资产处置"]

    transactions = []
    for i in range(500):
        amount = random.uniform(100, 5_000_000)
        # 10%大额
        if i < 50:
            amount = random.uniform(1_000_000, 5_000_000)
        # 20%中等
        elif i < 150:
            amount = random.uniform(100_000, 1_000_000)

        transactions.append({
            "id": f"TXN_{i+1:06d}",
            "amount": round(amount, 2),
            "type": random.choice(types),
            "date": f"2024-{(i%12)+1:02d}-{(i%28)+1:02d}",
            "counterparty": f"对手方{random.randint(1, 50)}",
            "description": random.choice(["正常", "大额", "异常", "关联交易"])
        })

    print(f"加载测试数据: {len(transactions)} 笔交易")
    print()

    # 加载并分层
    processed = engine.load_transactions(transactions)

    # 执行抽样
    result = engine.sample(processed, coverage_target=0.95)

    print()
    print(engine.format_plan_text(result))


if __name__ == "__main__":
    main()
