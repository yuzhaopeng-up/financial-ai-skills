"""
quant_fund - 量化基金分析引擎
基于 Fama-French 五因子 + Carhart 四因子模型
"""

import json
import random
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta


@dataclass
class FactorExposure:
    """因子暴露"""
    alpha: float       # 超额收益
    beta: float        # 市场敏感度
    smb: float         # 市值因子 (小盘股)
    hml: float         # 价值因子
    rmw: float         # 盈利因子
    cma: float         # 投资因子
    mom: float         # 动量因子


@dataclass
class StyleDrift:
    """风格漂移"""
    current_style: Dict[str, float]   # 当前实现风格
    contract_style: Dict[str, float] # 契约约定风格
    drift_score: float                # 漂移得分 (0-1)
    alert: str                        # 预警级别 LOW/MEDIUM/HIGH


@dataclass
class BrinsonAttribution:
    """Brinson归因"""
    selection_effect: float    # 选股效应
    allocation_effect: float   # 行业配置效应
    interaction_effect: float  # 交互效应
    total_attribution: float   # 总归因


@dataclass
class PerformanceAttribution:
    """业绩归因"""
    benchmark_return: float
    factor_contribution: float
    selection_contribution: float
    allocation_contribution: float
    timing_contribution: float
    net_return: float


@dataclass
class QuantFundAnalysis:
    """完整分析结果"""
    fund_code: str
    fund_name: str
    analysis_date: str
    factor_exposure: FactorExposure
    style_drift: StyleDrift
    brinson_attribution: BrinsonAttribution
    performance_attribution: PerformanceAttribution

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "fund_code": self.fund_code,
            "fund_name": self.fund_name,
            "analysis_date": self.analysis_date,
            "factor_exposure": asdict(self.factor_exposure),
            "style_drift": {
                "current_style": self.style_drift.current_style,
                "contract_style": self.style_drift.contract_style,
                "drift_score": self.style_drift.drift_score,
                "alert": self.style_drift.alert
            },
            "brinson_attribution": asdict(self.brinson_attribution),
            "performance_attribution": asdict(self.performance_attribution)
        }
        return result

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def summary(self) -> str:
        """生成摘要文本"""
        lines = [
            f"=== 量化基金分析报告 ===",
            f"基金代码: {self.fund_code}",
            f"基金名称: {self.fund_name}",
            f"分析日期: {self.analysis_date}",
            "",
            "【因子暴露】",
            f"  Alpha (超额收益): {self.factor_exposure.alpha:+.2%}",
            f"  Beta (市场敏感度): {self.factor_exposure.beta:.2f}",
            f"  SMB (市值因子): {self.factor_exposure.smb:+.2f}",
            f"  HML (价值因子): {self.factor_exposure.hml:+.2f}",
            f"  RMW (盈利因子): {self.factor_exposure.rmw:+.2f}",
            f"  CMA (投资因子): {self.factor_exposure.cma:+.2f}",
            f"  MOM (动量因子): {self.factor_exposure.mom:+.2f}",
            "",
            "【风格漂移检测】",
            f"  当前风格: 规模{self.style_drift.current_style.get('size',0):.0%} "
            f"价值{self.style_drift.current_style.get('value',0):.0%} "
            f"成长{self.style_drift.current_style.get('growth',0):.0%}",
            f"  契约风格: 规模{self.style_drift.contract_style.get('size',0):.0%} "
            f"价值{self.style_drift.contract_style.get('value',0):.0%} "
            f"成长{self.style_drift.contract_style.get('growth',0):.0%}",
            f"  漂移得分: {self.style_drift.drift_score:.2f} ({self.style_drift.alert})",
            "",
            "【Brinson归因】",
            f"  选股效应: {self.brinson_attribution.selection_effect:+.2%}",
            f"  行业配置效应: {self.brinson_attribution.allocation_effect:+.2%}",
            f"  交互效应: {self.brinson_attribution.interaction_effect:+.2%}",
            f"  总归因贡献: {self.brinson_attribution.total_attribution:+.2%}",
            "",
            "【业绩归因】",
            f"  基准收益: {self.performance_attribution.benchmark_return:+.2%}",
            f"  因子贡献: {self.performance_attribution.factor_contribution:+.2%}",
            f"  选股贡献: {self.performance_attribution.selection_contribution:+.2%}",
            f"  行业配置贡献: {self.performance_attribution.allocation_contribution:+.2%}",
            f"  择时贡献: {self.performance_attribution.timing_contribution:+.2%}",
            f"  基金净收益: {self.performance_attribution.net_return:+.2%}",
        ]
        return "\n".join(lines)


class QuantFundEngine:
    """
    量化基金分析引擎
    
    提供因子暴露分析、风格漂移检测、Brinson归因等功能
    基于 Fama-French 五因子 + Carhart 四因子模型
    """

    def __init__(self, seed: Optional[int] = None):
        """
        初始化引擎
        
        Args:
            seed: 随机种子，用于模拟数据（测试用）
        """
        self.seed = seed
        if seed is not None:
            random.seed(seed)

    def _generate_simulated_factor_exposure(self, fund_code: str) -> FactorExposure:
        """
        生成模拟因子暴露数据
        
        实际应用中应从数据库或API获取真实数据
        """
        # 基于基金代码生成稳定的伪随机数
        code_hash = hash(fund_code) % 1000
        random.seed(self.seed or code_hash)
        
        return FactorExposure(
            alpha=random.uniform(-0.05, 0.08),     # Alpha: -5% to +8%
            beta=random.uniform(0.6, 1.4),          # Beta: 0.6 to 1.4
            smb=random.uniform(-0.5, 0.5),         # SMB: -0.5 to +0.5
            hml=random.uniform(-0.4, 0.4),         # HML: -0.4 to +0.4
            rmw=random.uniform(-0.3, 0.5),         # RMW: -0.3 to +0.5
            cma=random.uniform(-0.3, 0.3),         # CMA: -0.3 to +0.3
            mom=random.uniform(-0.3, 0.4)          # MOM: -0.3 to +0.4
        )

    def _generate_simulated_style(self, fund_code: str) -> tuple:
        """
        生成模拟风格数据
        返回: (current_style, contract_style, drift_score)
        """
        code_hash = hash(fund_code) % 1000
        random.seed(self.seed or code_hash)
        
        # 当前实现风格（模拟近期持仓）
        current_style = {
            "size": random.uniform(0.1, 0.9),      # 规模偏好
            "value": random.uniform(0.1, 0.7),     # 价值偏好
            "growth": random.uniform(0.1, 0.7),    # 成长偏好
        }
        
        # 契约约定风格（模拟基金合同）
        contract_style = {
            "size": random.uniform(0.3, 0.8),
            "value": random.uniform(0.2, 0.6),
            "growth": random.uniform(0.2, 0.5),
        }
        
        # 归一化
        total_c = sum(current_style.values())
        total_k = sum(contract_style.values())
        for k in current_style:
            current_style[k] /= total_c
        for k in contract_style:
            contract_style[k] /= total_k
        
        # 计算漂移得分（欧氏距离）
        drift_score = sum(
            (current_style[k] - contract_style[k]) ** 2 
            for k in current_style
        ) ** 0.5 / (2 ** 0.5)  # 归一化到 0-1
        
        # 预警级别
        if drift_score < 0.10:
            alert = "LOW"
        elif drift_score < 0.20:
            alert = "MEDIUM"
        else:
            alert = "HIGH"
        
        return current_style, contract_style, drift_score, alert

    def _generate_simulated_brinson(self, fund_code: str) -> BrinsonAttribution:
        """生成模拟Brinson归因数据"""
        code_hash = hash(fund_code) % 1000
        random.seed(self.seed or code_hash)
        
        selection_effect = random.uniform(-0.02, 0.06)
        allocation_effect = random.uniform(-0.01, 0.04)
        interaction_effect = random.uniform(-0.01, 0.02)
        
        return BrinsonAttribution(
            selection_effect=selection_effect,
            allocation_effect=allocation_effect,
            interaction_effect=interaction_effect,
            total_attribution=selection_effect + allocation_effect + interaction_effect
        )

    def _generate_simulated_performance(self, fund_code: str) -> PerformanceAttribution:
        """生成模拟业绩归因数据"""
        code_hash = hash(fund_code) % 1000
        random.seed(self.seed or code_hash)
        
        benchmark_return = random.uniform(-0.10, 0.20)
        factor_contribution = random.uniform(-0.05, 0.15)
        selection_contribution = random.uniform(-0.02, 0.08)
        allocation_contribution = random.uniform(-0.01, 0.05)
        timing_contribution = random.uniform(-0.02, 0.03)
        
        # 确保净值收益与分解项大致匹配
        net_return = (
            benchmark_return + 
            factor_contribution + 
            selection_contribution + 
            allocation_contribution + 
            timing_contribution +
            random.uniform(-0.01, 0.01)  # 残差
        )
        
        return PerformanceAttribution(
            benchmark_return=benchmark_return,
            factor_contribution=factor_contribution,
            selection_contribution=selection_contribution,
            allocation_contribution=allocation_contribution,
            timing_contribution=timing_contribution,
            net_return=net_return
        )

    def analyze(
        self,
        fund_code: str,
        fund_name: Optional[str] = None,
        benchmark: str = "000300.SH",  # 沪深300
        period: str = "1Y"
    ) -> QuantFundAnalysis:
        """
        完整分析量化基金
        
        Args:
            fund_code: 基金代码（F000001格式）
            fund_name: 基金名称（可选）
            benchmark: 基准指数代码（默认沪深300）
            period: 分析区间（默认近1年）
            
        Returns:
            QuantFundAnalysis: 完整分析结果
        """
        # 数据脱敏：统一格式
        if not fund_code.startswith("F"):
            fund_code = f"F{int(fund_code):06d}"
        
        if fund_name is None:
            fund_name = "某量化基金"
        
        # 生成各维度分析
        factor_exposure = self._generate_simulated_factor_exposure(fund_code)
        current_style, contract_style, drift_score, alert = \
            self._generate_simulated_style(fund_code)
        brinson = self._generate_simulated_brinson(fund_code)
        performance = self._generate_simulated_performance(fund_code)
        
        return QuantFundAnalysis(
            fund_code=fund_code,
            fund_name=fund_name,
            analysis_date=datetime.now().strftime("%Y-%m-%d"),
            factor_exposure=factor_exposure,
            style_drift=StyleDrift(
                current_style=current_style,
                contract_style=contract_style,
                drift_score=drift_score,
                alert=alert
            ),
            brinson_attribution=brinson,
            performance_attribution=performance
        )

    def factor_exposure(
        self, 
        fund_code: str, 
        fund_name: Optional[str] = None
    ) -> FactorExposure:
        """仅返回因子暴露分析"""
        result = self.analyze(fund_code, fund_name)
        return result.factor_exposure

    def style_drift(
        self, 
        fund_code: str, 
        fund_name: Optional[str] = None
    ) -> StyleDrift:
        """仅返回风格漂移分析"""
        result = self.analyze(fund_code, fund_name)
        return result.style_drift

    def brinson(
        self, 
        fund_code: str, 
        fund_name: Optional[str] = None
    ) -> BrinsonAttribution:
        """仅返回Brinson归因"""
        result = self.analyze(fund_code, fund_name)
        return result.brinson_attribution


# 导出
__all__ = [
    "QuantFundEngine",
    "QuantFundAnalysis",
    "FactorExposure",
    "StyleDrift",
    "BrinsonAttribution",
    "PerformanceAttribution",
]
