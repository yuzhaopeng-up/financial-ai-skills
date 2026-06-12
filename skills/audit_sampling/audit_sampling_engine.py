"""
审计智能抽样引擎 (Audit Sampling Engine)

基于统计学原理和审计准则（CAS/ISA），提供科学的样本量计算、
抽样方法选择及误差推断能力。
"""

import random
import math
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum


class SamplingMethod(Enum):
    RANDOM = "随机抽样"
    STRATIFIED = "分层抽样"
    CLUSTER = "整群抽样"
    PPS = "PPS抽样"


class RiskLevel(Enum):
    HIGH = "高风险"
    MEDIUM = "中风险"
    LOW = "低风险"


@dataclass
class SampledItem:
    """抽样项目"""
    item_id: str
    stratum: str
    amount: float
    is_flagged: bool = False
    finding_type: Optional[str] = None
    finding_amount: float = 0.0


@dataclass
class SamplingPlan:
    """抽样方案"""
    method: str
    method_rationale: str
    sample_size: int
    confidence_level: float
    tolerable_error_rate: float
    expected_error_rate: float
    stratification_key: Optional[str] = None
    allocation_strategy: Optional[str] = None


@dataclass
class SamplingResult:
    """抽样结果"""
    sampled_items: List[Dict[str, Any]]
    findings_count: int
    findings_amount: float
    findings_rate: float
    high_value_items_sampled: int = 0


@dataclass
class AuditFindings:
    """审计发现推断"""
    estimated_error_rate: float
    projected_total_errors: int
    projected_total_amount: float
    error_rate_lower: float
    error_rate_upper: float


@dataclass
class PopulationConclusion:
    """总体结论"""
    error_rate_range: str
    confidence_interval: str
    opinion_impact: str
    recommendation: str
    needs_expansion: bool


class AuditSamplingEngine:
    """
    审计智能抽样引擎
    
    根据审计场景（总体数量/金额/风险等级）自动计算最优抽样方案，
    支持随机/分层/整群/PPS四种抽样方法，并返回抽样结果及审计发现概率。
    """

    def __init__(self, seed: Optional[int] = None):
        """
        初始化审计抽样引擎
        
        Args:
            seed: 随机种子，用于结果复现
        """
        if seed is not None:
            random.seed(seed)
        self._random_backup = random.Random(seed)

    def calculate_sample_size(
        self,
        population_size: int,
        confidence_level: float = 0.95,
        tolerable_error_rate: float = 0.05,
        expected_error_rate: float = 0.01,
        method: str = "auto"
    ) -> int:
        """
        计算样本量
        
        Args:
            population_size: 总体大小
            confidence_level: 置信水平
            tolerable_error_rate: 可容忍误差率
            expected_error_rate: 预期误差率
            method: 抽样方法
            
        Returns:
            所需样本量
        """
        # 置信水平对应的Z值
        z_scores = {
            0.90: 1.645,
            0.95: 1.96,
            0.99: 2.576
        }
        z = z_scores.get(confidence_level, 1.96)
        
        # 有限总体校正因子
        n0 = (z ** 2 * expected_error_rate * (1 - expected_error_rate)) / (tolerable_error_rate ** 2)
        finite_correction = n0 / (1 + (n0 - 1) / population_size)
        
        sample_size = math.ceil(finite_correction)
        
        # 最低样本量保障
        min_sample = 30 if population_size > 1000 else max(5, population_size // 10)
        return max(sample_size, min_sample)

    def _generate_mock_population(
        self,
        total_count: int,
        total_amount: float,
        risk_level: str
    ) -> List[Dict[str, Any]]:
        """生成模拟总体数据"""
        avg_amount = total_amount / total_count
        population = []
        
        # 金额分布：80%小额，20%大额
        small_threshold = avg_amount * 2
        
        for i in range(total_count):
            # 金额分布：指数分布模拟真实场景
            if random.random() < 0.8:
                amount = random.uniform(avg_amount * 0.1, small_threshold)
            else:
                amount = random.uniform(small_threshold, avg_amount * 50)
            
            # 风险标记：高风险业务金额偏大，更易出错
            if risk_level == "高风险":
                is_high_risk = random.random() < 0.3
            elif risk_level == "中风险":
                is_high_risk = random.random() < 0.15
            else:
                is_high_risk = random.random() < 0.05
            
            population.append({
                "item_id": f"INV-{i+1:06d}",
                "amount": round(amount, 2),
                "date": f"2026-{random.randint(1,6):02d}-{random.randint(1,28):02d}",
                "vendor": f"供应商{random.randint(1, 200)}",
                "department": random.choice(["销售部", "采购部", "行政部", "研发部", "财务部"]),
                "is_high_risk": is_high_risk,
                "invoice_type": random.choice(["增值税专用发票", "增值税普通发票", "收据"])
            })
        
        return population

    def _simulate_audit_results(
        self,
        population: List[Dict[str, Any]],
        sample: List[Dict[str, Any]],
        risk_level: str
    ) -> List[Dict[str, Any]]:
        """模拟审计检查结果"""
        # 基础误差率：基于风险等级
        base_error_rates = {
            "高风险": 0.08,
            "中风险": 0.03,
            "低风险": 0.01
        }
        base_rate = base_error_rates.get(risk_level, 0.03)
        
        sampled_results = []
        for item in sample:
            # 高风险项目误差率更高
            error_rate = base_rate * 2 if item.get("is_high_risk") else base_rate
            
            # 大额项目误差率略高
            avg_amount = sum(p["amount"] for p in population) / len(population)
            if item["amount"] > avg_amount * 10:
                error_rate *= 1.5
            
            has_error = random.random() < error_rate
            
            result = item.copy()
            if has_error:
                # 误差类型分布
                error_types = ["金额错误", "日期错误", "审批缺失", "发票不合规", "重复入账"]
                result["has_error"] = True
                result["finding_type"] = random.choice(error_types)
                result["finding_amount"] = item["amount"] * random.uniform(0.05, 0.30)
                result["finding_amount"] = round(result["finding_amount"], 2)
            else:
                result["has_error"] = False
                result["finding_type"] = None
                result["finding_amount"] = 0.0
            
            sampled_results.append(result)
        
        return sampled_results

    def _select_method(
        self,
        total_count: int,
        total_amount: float,
        risk_level: str
    ) -> str:
        """智能选择抽样方法"""
        avg_amount = total_amount / total_count
        amount_cv = self._calculate_cv(total_count, total_amount)
        
        # 金额变异系数高 → PPS
        if amount_cv > 1.5:
            return "PPS抽样"
        
        # 高风险 → 分层抽样
        if risk_level == "高风险":
            return "分层抽样"
        
        # 中风险 + 中等变异 → 随机抽样
        return "随机抽样"

    def _calculate_cv(self, total_count: int, total_amount: float) -> float:
        """计算金额变异系数（简化估算）"""
        avg_amount = total_amount / total_count
        # 估算标准差：假设金额服从指数分布
        std_amount = avg_amount * 0.8
        return std_amount / avg_amount if avg_amount > 0 else 0

    def _stratify_population(
        self,
        population: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """分层总体"""
        strata = {
            "高金额区(>10万)": [],
            "中金额区(1-10万)": [],
            "低金额区(<1万)": []
        }
        
        for item in population:
            if item["amount"] > 100000:
                strata["高金额区(>10万)"].append(item)
            elif item["amount"] > 10000:
                strata["中金额区(1-10万)"].append(item)
            else:
                strata["低金额区(<1万)"].append(item)
        
        return strata

    def _allocate_sample_proportional(
        self,
        strata: Dict[str, List[Dict[str, Any]]],
        total_sample_size: int
    ) -> Dict[str, int]:
        """比例分配样本量到各层"""
        total_items = sum(len(s) for s in strata.values())
        allocations = {}
        
        for stratum_name, items in strata.items():
            proportion = len(items) / total_items if total_items > 0 else 0
            # 金额加权调整
            avg_amount = sum(i["amount"] for i in items) / len(items) if items else 0
            amount_weight = min(avg_amount / 10000, 3)  # 封顶3倍
            adjusted_proportion = proportion * (1 + amount_weight * 0.3)
            
            allocations[stratum_name] = max(1, int(total_sample_size * adjusted_proportion))
        
        # 调整总和
        current_total = sum(allocations.values())
        if current_total != total_sample_size:
            diff = total_sample_size - current_total
            # 补偿到最大层
            max_stratum = max(allocations, key=allocations.get)
            allocations[max_stratum] += diff
        
        return allocations

    def _perform_stratified_sampling(
        self,
        population: List[Dict[str, Any]],
        sample_size: int,
        risk_level: str
    ) -> List[Dict[str, Any]]:
        """执行分层抽样"""
        strata = self._stratify_population(population)
        allocations = self._allocate_sample_proportional(strata, sample_size)
        
        sample = []
        for stratum_name, items in strata.items():
            n = allocations.get(stratum_name, 0)
            n = min(n, len(items))
            selected = random.sample(items, n) if len(items) >= n else items
            for item in selected:
                item["stratum"] = stratum_name
            sample.extend(selected)
        
        return sample

    def _perform_random_sampling(
        self,
        population: List[Dict[str, Any]],
        sample_size: int
    ) -> List[Dict[str, Any]]:
        """执行随机抽样"""
        sample_size = min(sample_size, len(population))
        sample = random.sample(population, sample_size)
        for item in sample:
            item["stratum"] = "整体"
        return sample

    def _perform_pps_sampling(
        self,
        population: List[Dict[str, Any]],
        sample_size: int
    ) -> List[Dict[str, Any]]:
        """执行PPS抽样（概率比例规模抽样）"""
        total_amount = sum(item["amount"] for item in population)
        
        # 按金额排序
        sorted_pop = sorted(population, key=lambda x: x["amount"], reverse=True)
        
        # 选择大额项目优先入样
        sample = []
        
        # 第一阶段：选取前N个大额项目
        large_items_count = max(3, sample_size // 3)
        for item in sorted_pop[:large_items_count]:
            item_copy = item.copy()
            item_copy["stratum"] = "PPS大额优先"
            item_copy["pps_weight"] = item["amount"] / total_amount
            sample.append(item_copy)
        
        # 第二阶段：剩余样本随机抽取
        remaining = sorted_pop[large_items_count:]
        remaining_size = sample_size - len(sample)
        if remaining_size > 0 and remaining:
            selected = random.sample(remaining, min(remaining_size, len(remaining)))
            for item in selected:
                item_copy = item.copy()
                item_copy["stratum"] = "PPS随机补抽"
                item_copy["pps_weight"] = item["amount"] / total_amount
                sample.append(item_copy)
        
        return sample

    def _perform_cluster_sampling(
        self,
        population: List[Dict[str, Any]],
        sample_size: int
    ) -> List[Dict[str, Any]]:
        """执行整群抽样（按部门聚类）"""
        # 按部门分组
        clusters = {}
        for item in population:
            dept = item.get("department", "未知")
            if dept not in clusters:
                clusters[dept] = []
            clusters[dept].append(item)
        
        # 计算每个部门作为群体的样本量
        cluster_list = list(clusters.items())
        total_clusters = len(cluster_list)
        
        # 计算需要抽取的群体数
        clusters_to_sample = max(1, min(sample_size // 20 + 1, total_clusters))
        
        # 随机选择群体
        selected_clusters = random.sample(cluster_list, clusters_to_sample)
        
        sample = []
        for dept_name, items in selected_clusters:
            for item in items:
                item_copy = item.copy()
                item_copy["stratum"] = f"整群-{dept_name}"
                sample.append(item_copy)
        
        return sample

    def generate(
        self,
        scenario: str = "通用审计",
        total_count: int = 1000,
        total_amount: float = 10000000,
        risk_level: str = "中风险",
        confidence_level: float = 0.95,
        tolerable_error_rate: float = 0.05,
        expected_error_rate: float = 0.01,
        method: str = "auto"
    ) -> Dict[str, Any]:
        """
        生成审计抽样方案和结果
        
        Args:
            scenario: 审计场景描述
            total_count: 总体数量（如发票张数）
            total_amount: 总体金额（元）
            risk_level: 风险等级（高/中/低风险）
            confidence_level: 置信水平
            tolerable_error_rate: 可容忍误差率
            expected_error_rate: 预期误差率
            method: 抽样方法（auto/随机抽样/分层抽样/整群抽样/PPS抽样）
            
        Returns:
            完整的抽样结果，包含方案、结果、发现推断、总体结论
        """
        # 智能选择方法
        if method == "auto":
            method = self._select_method(total_count, total_amount, risk_level)
        
        # 计算样本量
        sample_size = self.calculate_sample_size(
            population_size=total_count,
            confidence_level=confidence_level,
            tolerable_error_rate=tolerable_error_rate,
            expected_error_rate=expected_error_rate,
            method=method
        )
        
        # 生成模拟总体
        population = self._generate_mock_population(total_count, total_amount, risk_level)
        
        # 执行抽样
        if method == "分层抽样":
            sample = self._perform_stratified_sampling(population, sample_size, risk_level)
        elif method == "整群抽样":
            sample = self._perform_cluster_sampling(population, sample_size)
        elif method == "PPS抽样":
            sample = self._perform_pps_sampling(population, sample_size)
        else:
            sample = self._perform_random_sampling(population, sample_size)
        
        # 模拟审计检查
        results = self._simulate_audit_results(population, sample, risk_level)
        
        # 统计结果
        findings_count = sum(1 for r in results if r.get("has_error", False))
        findings_amount = sum(r.get("finding_amount", 0) for r in results)
        findings_rate = findings_count / len(results) if results else 0
        high_value_sampled = sum(1 for r in results if r.get("stratum", "").startswith("高金额"))
        
        # 构建抽样计划
        method_rationales = {
            "随机抽样": "总体内部差异较小，边界清晰，随机抽样可保证代表性。",
            "分层抽样": f"高风险业务总体内部差异较大，按金额分层可提高精度，确保大额项目充分覆盖。",
            "整群抽样": "群体间差异小、群体内差异大，整群抽样效率高。",
            "PPS抽样": f"金额分布不均（变异系数>{1.5:.1f}），少量大额项目主导总体，PPS确保大额项目入选概率与金额成正比。"
        }
        
        sampling_plan = SamplingPlan(
            method=method,
            method_rationale=method_rationales.get(method, "基于审计判断选择。"),
            sample_size=len(sample),
            confidence_level=confidence_level,
            tolerable_error_rate=tolerable_error_rate,
            expected_error_rate=expected_error_rate,
            stratification_key="金额分层" if method == "分层抽样" else None,
            allocation_strategy="比例分配+金额加权" if method == "分层抽样" else None
        )
        
        # 审计发现推断
        # 使用泊松分布推断总体误差
        z = 1.96 if confidence_level == 0.95 else (2.576 if confidence_level == 0.99 else 1.645)
        error_std = math.sqrt(findings_rate * (1 - findings_rate) / len(results)) if len(results) > 0 else 0
        margin = z * error_std
        
        estimated_error_rate = findings_rate
        error_rate_lower = max(0, estimated_error_rate - margin)
        error_rate_upper = min(1, estimated_error_rate + margin)
        
        projected_total_errors = int(estimated_error_rate * total_count)
        projected_total_amount = findings_amount / len(results) * total_count if results else 0
        
        audit_findings = AuditFindings(
            estimated_error_rate=round(estimated_error_rate * 100, 2),
            projected_total_errors=projected_total_errors,
            projected_total_amount=round(projected_total_amount, 2),
            error_rate_lower=round(error_rate_lower * 100, 2),
            error_rate_upper=round(error_rate_upper * 100, 2)
        )
        
        # 总体结论
        if estimated_error_rate <= tolerable_error_rate * 0.5:
            opinion_impact = "无保留意见"
            recommendation = "误差率显著低于可容忍水平，审计范围充分，结论可靠。"
            needs_expansion = False
        elif estimated_error_rate <= tolerable_error_rate:
            opinion_impact = "保留意见或带说明段的无保留意见"
            recommendation = "误差率接近但未超过可容忍水平，建议扩大样本量或执行替代程序。"
            needs_expansion = True
        else:
            opinion_impact = "否定意见或拒绝表示意见"
            recommendation = "误差率超过可容忍水平，需要扩大审计范围或建议管理层调整。"
            needs_expansion = True
        
        population_conclusion = PopulationConclusion(
            error_rate_range=f"{error_rate_lower*100:.1f}% ~ {error_rate_upper*100:.1f}%",
            confidence_interval=f"{confidence_level*100:.0f}%",
            opinion_impact=opinion_impact,
            recommendation=recommendation,
            needs_expansion=needs_expansion
        )
        
        return {
            "scenario": scenario,
            "population_summary": {
                "total_count": total_count,
                "total_amount": total_amount,
                "avg_amount": round(total_amount / total_count, 2) if total_count > 0 else 0,
                "risk_level": risk_level
            },
            "sampling_plan": asdict(sampling_plan),
            "sampling_results": {
                "sample_size": len(sample),
                "sampled_items": [
                    {k: v for k, v in r.items() if k in ["item_id", "stratum", "amount", "date", "vendor", "has_error", "finding_type", "finding_amount"]}
                    for r in results
                ],
                "findings_count": findings_count,
                "findings_amount": round(findings_amount, 2),
                "findings_rate": round(findings_rate * 100, 2),
                "high_value_items_sampled": high_value_sampled
            },
            "audit_findings": asdict(audit_findings),
            "population_conclusion": asdict(population_conclusion)
        }

    def generate_text_report(self, result: Dict[str, Any]) -> str:
        """生成文本格式的审计抽样报告"""
        plan = result["sampling_plan"]
        results = result["sampling_results"]
        findings = result["audit_findings"]
        conclusion = result["population_conclusion"]
        pop_summary = result["population_summary"]
        
        lines = [
            "=" * 60,
            "审计智能抽样报告",
            "=" * 60,
            "",
            f"【审计场景】{result['scenario']}",
            "",
            "【总体概况】",
            f"  总体数量: {pop_summary['total_count']:,} 件",
            f"  总体金额: {pop_summary['total_amount']:,.2f} 元",
            f"  平均金额: {pop_summary['avg_amount']:,.2f} 元/件",
            f"  风险等级: {pop_summary['risk_level']}",
            "",
            "【抽样方案】",
            f"  抽样方法: {plan['method']}",
            f"  方法说明: {plan['method_rationale']}",
            f"  置信水平: {plan['confidence_level']*100:.0f}%",
            f"  可容忍误差率: {plan['tolerable_error_rate']*100:.1f}%",
            f"  预期误差率: {plan['expected_error_rate']*100:.1f}%",
            f"  计算样本量: {plan['sample_size']} 件",
            "",
            "【抽样结果】",
            f"  实际抽样: {results['sample_size']} 件",
            f"  发现问题: {results['findings_count']} 件 ({results['findings_rate']:.2f}%)",
            f"  问题金额: {results['findings_amount']:,.2f} 元",
            f"  大额项目抽样: {results['high_value_items_sampled']} 件",
            "",
            "【误差推断】",
            f"  估计误差率: {findings['estimated_error_rate']:.2f}%",
            f"  误差率区间({findings['projected_total_errors']}项): {findings['error_rate_lower']:.2f}% ~ {findings['error_rate_upper']:.2f}%",
            f"  推断总体误差金额: {findings['projected_total_amount']:,.2f} 元",
            "",
            "【总体结论】",
            f"  {confidence_interval}置信水平下误差率范围: {conclusion['error_rate_range']}",
            f"  对审计意见的影响: {conclusion['opinion_impact']}",
            f"  建议: {conclusion['recommendation']}",
            "",
            "=" * 60
        ]
        
        return "\n".join(lines)


# 兼容性别名
AuditSamplingEngine().generate_text_report = lambda r: AuditSamplingEngine.generate_text_report(None, r)
