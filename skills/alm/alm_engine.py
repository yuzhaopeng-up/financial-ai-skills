# -*- coding: utf-8 -*-
"""
ALM Engine - 资产负债管理核心引擎
Bank Asset-Liability Management Core Engine

功能：
- 期限缺口分析（1个月/3个月/6个月/1年/3年/5年）
- LCR（流动性覆盖率）计算
- NSFR（净稳定资金比率）计算
- 久期缺口分析
- 风险预警
- 优化建议生成
"""

import re
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class RiskStatus(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


# ─────────────────────────────────────────────
# 数据模型
# ─────────────────────────────────────────────

@dataclass
class GapItem:
    asset: float       # 资产到期量（元）
    liability: float   # 负债到期量（元）
    gap: float         # 缺口（资产-负债）
    gap_ratio: float   # 缺口率 = gap / asset

    @property
    def status(self) -> str:
        ratio = abs(self.gap_ratio)
        if ratio <= 0.20:
            return RiskStatus.GREEN.value
        elif ratio <= 0.30:
            return RiskStatus.YELLOW.value
        else:
            return RiskStatus.RED.value


@dataclass
class LCRResult:
    hqla_level1: float      # 一级HQLA
    hqla_level2: float     # 二级HQLA
    hqla_total: float      # 总HQLA
    net_cash_outflow: float  # 净现金流出
    lcr_ratio: float       # LCR = HQLA / 净流出
    status: str            # green/yellow/red


@dataclass
class NSFRResult:
    available_stable_funding: float   # 可用稳定资金 ASF
    required_stable_funding: float   # 所需稳定资金 RSF
    nsfr_ratio: float                # NSFR = ASF / RSF
    status: str


@dataclass
class DurationGapResult:
    asset_duration: float      # 资产久期
    liability_duration: float   # 负债久期
    duration_gap: float         # 久期缺口
    asset_liability_ratio: float  # 资产/负债比率
    duration_gap_adjusted: float   # 调整后久期缺口
    status: str


@dataclass
class Warning:
    level: str      # yellow / red
    indicator: str  # LCR / NSFR / 期限缺口 / 久期缺口
    message: str
    suggestion: str


# ─────────────────────────────────────────────
# 解析工具函数
# ─────────────────────────────────────────────

def parse_chinese_input(text: str) -> Dict[str, Any]:
    """
    从中文自然语言输入中解析资产负债数据。
    
    支持格式示例：
    "ALM 资产500亿 定期存款60% 活期30%"
    "ALM 资产1000亿 同业负债15% 债券发行10%"
    """
    text = text.strip()
    
    # 提取资产规模
    asset_match = re.search(r'资产\s*(\d+(?:\.\d+)?)\s*亿', text)
    if not asset_match:
        raise ValueError(f"无法从输入中解析资产规模：{text}")
    total_assets = float(asset_match.group(1)) * 1e8  # 亿 → 元
    
    # 初始化负债结构
    liability_structure = {
        "demand_deposits": 0.0,
        "time_deposits": 0.0,
        "interbank": 0.0,
        "bond_issuance": 0.0,
        "other": 0.0,
    }
    
    # 解析各类负债占比
    patterns = [
        (r'定期(?:存款)?\s*(\d+(?:\.\d+)?)\s*%?', 'time_deposits'),
        (r'活期(?:存款)?\s*(\d+(?:\.\d+)?)\s*%?', 'demand_deposits'),
        (r'同业(?:负债|拆借)?\s*(\d+(?:\.\d+)?)\s*%?', 'interbank'),
        (r'债券(?:发行)?\s*(\d+(?:\.\d+)?)\s*%?', 'bond_issuance'),
        (r'其他(?:负债)?\s*(\d+(?:\.\d+)?)\s*%?', 'other'),
    ]
    
    parsed_total = 0.0
    for pattern, key in patterns:
        m = re.search(pattern, text)
        if m:
            liability_structure[key] = float(m.group(1)) / 100.0
            parsed_total += liability_structure[key]
    
    # 如果没有解析到任何负债，使用默认值推算
    if parsed_total == 0:
        # 假设默认结构：定期50% + 活期30% + 同业10% + 其他10%
        liability_structure = {
            "demand_deposits": 0.30,
            "time_deposits": 0.50,
            "interbank": 0.10,
            "bond_issuance": 0.05,
            "other": 0.05,
        }
    else:
        # 归一化
        if parsed_total < 1.0:
            factor = 1.0 / parsed_total
            for k in liability_structure:
                liability_structure[k] *= factor
    
    # 生成标准资产期限分布
    asset_maturity_profile = {
        "1m": 0.10,
        "3m": 0.12,
        "6m": 0.15,
        "1y": 0.20,
        "3y": 0.25,
        "5y": 0.18,
    }
    
    # 生成标准负债期限分布
    liability_maturity_profile = {
        "1m": 0.25,
        "3m": 0.20,
        "6m": 0.18,
        "1y": 0.22,
        "3y": 0.10,
        "5y": 0.05,
    }
    
    # 生成HQLA结构（基于负债结构估算）
    hqla_ratio = 0.15  # HQLA/总资产 基准15%
    hqla_composition = {
        "level1": 0.70,
        "level2": 0.30,
    }
    
    # 默认久期（根据负债结构估算）
    avg_liability_duration = (
        liability_structure["demand_deposits"] * 0.1 +
        liability_structure["time_deposits"] * 1.5 +
        liability_structure["interbank"] * 0.3 +
        liability_structure["bond_issuance"] * 3.0 +
        liability_structure["other"] * 0.5
    )
    
    asset_duration = 2.5  # 默认资产久期
    
    return {
        "total_assets": total_assets,
        "liability_structure": liability_structure,
        "asset_maturity_profile": asset_maturity_profile,
        "liability_maturity_profile": liability_maturity_profile,
        "hqla_composition": hqla_composition,
        "asset_duration": asset_duration,
        "liability_duration": avg_liability_duration,
    }


# ─────────────────────────────────────────────
# 核心引擎
# ─────────────────────────────────────────────

class ALMEngine:
    """
    资产负债管理引擎
    
    输入：银行资产负债数据（总资产规模、负债结构、期限分布、久期等）
    输出：缺口分析、LCR指标、NSFR指标、久期缺口、风险预警、优化建议
    """
    
    # LCR 系数定义
    LCR_OUTFLOW_RATES = {
        "demand_deposits": 0.10,   # 活期存款流出系数 10%
        "time_deposits": 0.05,     # 定期存款流出系数 5%（剩余期限30天内）
        "interbank": 0.25,        # 同业负债流出系数 25%
        "bond_issuance": 0.10,    # 债券发行流出系数 10%
        "other": 0.10,            # 其他负债流出系数 10%
    }
    
    # NSFR ASF 系数（可用稳定资金系数，按负债类型×期限）
    NSFR_ASF_RATES = {
        # (负债类型, 期限档位) -> ASF系数
        "demand_deposits": 0.50,   # 活期存款 ASF系数
        "time_deposits_1y": 0.80,  # 1年内定期
        "time_deposits_1y+": 0.95, # 1年以上定期
        "interbank_1y": 0.50,      # 1年内同业
        "interbank_1y+": 0.95,     # 1年以上同业
        "bond_issuance": 1.00,     # 债券发行 ASF系数 100%
        "other": 0.50,             # 其他
    }
    
    # NSFR RSF 系数（所需稳定资金系数，按资产类型×期限）
    NSFR_RSF_RATES = {
        # 资产类型 -> RSF系数
        "cash": 0.00,
        "hqla_level1": 0.05,       # 一级HQLA 5%
        "hqla_level2": 0.15,       # 二级HQLA 15%
        "interbank_1y": 0.10,      # 1年内同业资产
        "interbank_1y+": 0.40,     # 1年以上同业资产
        "loan_1y": 0.30,           # 1年内贷款
        "loan_1y+": 0.85,          # 1年以上贷款
        "bond": 0.25,              # 债券
        "other_assets": 1.00,      # 其他资产 100%
    }
    
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """
        初始化 ALM 引擎。
        
        Args:
            data: 资产负债数据字典，如果为 None 则需要后续调用 load() 或 parse()
        """
        self._data = data or {}
        self._gap_analysis: Optional[Dict[str, GapItem]] = None
        self._lcr_result: Optional[LCRResult] = None
        self._nsfr_result: Optional[NSFRResult] = None
        self._duration_gap: Optional[DurationGapResult] = None
        self._warnings: Optional[List[Warning]] = None
        self._optimization: Optional[Dict[str, List[str]]] = None
    
    def load(self, data: Dict[str, Any]) -> "ALMEngine":
        """加载数据并清空缓存"""
        self._data = data
        self._invalidate_cache()
        return self
    
    def parse(self, text: str) -> "ALMEngine":
        """从中文自然语言解析数据"""
        self._data = parse_chinese_input(text)
        self._invalidate_cache()
        return self
    
    def _invalidate_cache(self):
        """清空所有缓存，强制重新计算"""
        self._gap_analysis = None
        self._lcr_result = None
        self._nsfr_result = None
        self._duration_gap = None
        self._warnings = None
        self._optimization = None
    
    @property
    def total_assets(self) -> float:
        return self._data.get("total_assets", 0.0)
    
    @property
    def total_liabilities(self) -> float:
        """总负债 = 总资产 × 负债系数（假设85%负债率）"""
        return self.total_assets * 0.85
    
    @property
    def liability_structure(self) -> Dict[str, float]:
        return self._data.get("liability_structure", {
            "demand_deposits": 0.0,
            "time_deposits": 0.0,
            "interbank": 0.0,
            "bond_issuance": 0.0,
            "other": 0.0,
        })
    
    # ─── 期限缺口分析 ───────────────────────────
    
    def calculate_gap_analysis(self) -> Dict[str, GapItem]:
        """
        计算6个期限档位的资产-负债缺口。
        
        期限档位：1m / 3m / 6m / 1y / 3y / 5y
        累计计算：每个档位包含该档位及之前所有档位（累计到期量）
        """
        if self._gap_analysis is not None:
            return self._gap_analysis
        
        asset_profile = self._data.get("asset_maturity_profile", {})
        liability_profile = self._data.get("liability_maturity_profile", {})
        ta = self.total_assets
        tl = self.total_liabilities
        
        # 各档位权重
        buckets = ["1m", "3m", "6m", "1y", "3y", "5y"]
        
        # 转为绝对金额
        asset_amounts = {b: asset_profile.get(b, 0.0) * ta for b in buckets}
        liability_amounts = {b: liability_profile.get(b, 0.0) * tl for b in buckets}
        
        # 累计计算（每个档位累计到期）
        cumulative_asset = 0.0
        cumulative_liability = 0.0
        
        self._gap_analysis = {}
        prev_bucket = None
        bucket_mapping = {
            "1m": ("1m", "1m"),
            "3m": ("1m", "3m"),
            "6m": ("1m", "6m"),
            "1y": ("1m", "1y"),
            "3y": ("1m", "3y"),
            "5y": ("1m", "5y"),
        }
        
        for bucket in buckets:
            low, high = bucket_mapping[bucket]
            if low == high:
                # 独立档位
                cumulative_asset = asset_amounts[bucket]
                cumulative_liability = liability_amounts[bucket]
            else:
                # 累计档位：加上当前档位
                cumulative_asset += asset_amounts[bucket]
                cumulative_liability += liability_amounts[bucket]
            
            gap = cumulative_asset - cumulative_liability
            gap_ratio = gap / cumulative_asset if cumulative_asset > 0 else 0.0
            
            self._gap_analysis[bucket] = GapItem(
                asset=cumulative_asset,
                liability=cumulative_liability,
                gap=gap,
                gap_ratio=gap_ratio,
            )
        
        return self._gap_analysis
    
    # ─── LCR 计算 ──────────────────────────────
    
    def calculate_lcr(self) -> LCRResult:
        """
        计算 LCR（流动性覆盖率）。
        
        LCR = 优质流动性资产 (HQLA) / 未来30天净现金流出
        监管要求：LCR ≥ 100%
        
        HQLA 分级：
        - 一级资产（Level 1）：国债、央行存款，折算率 100%
        - 二级资产（Level 2）：AA- 以上信用债，折算率 85%
        
        现金流出计算：
        - 未来30天内各类负债 × 流出系数
        - 假设各类负债均匀分布在30天内
        """
        if self._lcr_result is not None:
            return self._lcr_result
        
        ta = self.total_assets
        ls = self.liability_structure
        hqla_comp = self._data.get("hqla_composition", {"level1": 0.70, "level2": 0.30})
        
        # HQLA 规模估算：总资产 × 15% × 各类占比
        total_hqla = ta * 0.15
        hqla_level1 = total_hqla * hqla_comp.get("level1", 0.70)
        hqla_level2 = total_hqla * hqla_comp.get("level2", 0.30)
        # 二级资产有85%折算率
        hqla_level2_adjusted = hqla_level2 * 0.85
        hqla_total = hqla_level1 + hqla_level2_adjusted
        
        # 现金流出估算（30天内）
        # 假设：活期存款30%在30天内流出，定期存款5%在30天内流出
        # 同业负债25%在30天内流出
        outflow = (
            ls["demand_deposits"] * ta * 0.30 * self.LCR_OUTFLOW_RATES["demand_deposits"] +
            ls["time_deposits"] * ta * 0.05 * self.LCR_OUTFLOW_RATES["time_deposits"] +
            ls["interbank"] * ta * 0.25 * self.LCR_OUTFLOW_RATES["interbank"] +
            ls["bond_issuance"] * ta * 0.05 * self.LCR_OUTFLOW_RATES["bond_issuance"] +
            ls["other"] * ta * 0.05 * self.LCR_OUTFLOW_RATES["other"]
        )
        
        lcr_ratio = (hqla_total / outflow) if outflow > 0 else 999.0
        
        if lcr_ratio >= 1.0:
            status = RiskStatus.GREEN.value
        elif lcr_ratio >= 0.8:
            status = RiskStatus.YELLOW.value
        else:
            status = RiskStatus.RED.value
        
        self._lcr_result = LCRResult(
            hqla_level1=hqla_level1,
            hqla_level2=hqla_level2,
            hqla_total=hqla_total,
            net_cash_outflow=outflow,
            lcr_ratio=lcr_ratio,
            status=status,
        )
        return self._lcr_result
    
    # ─── NSFR 计算 ──────────────────────────────
    
    def calculate_nsfr(self) -> NSFRResult:
        """
        计算 NSFR（净稳定资金比率）。
        
        NSFR = 可用稳定资金 (ASF) / 所需稳定资金 (RSF)
        监管要求：NSFR ≥ 100%
        
        ASF（可用稳定资金）：
        - 各类负债 × ASF系数（期限越长系数越高）
        
        RSF（所需稳定资金）：
        - 各类资产 × RSF系数（期限越长/流动性越低系数越高）
        """
        if self._nsfr_result is not None:
            return self._nsfr_result
        
        ta = self.total_assets
        tl = self.total_liabilities
        ls = self.liability_structure
        asset_profile = self._data.get("asset_maturity_profile", {})
        
        # ASF 计算
        asf = (
            ls["demand_deposits"] * tl * self.NSFR_ASF_RATES["demand_deposits"] +
            ls["time_deposits"] * tl * self.NSFR_ASF_RATES["time_deposits_1y"] * 0.6 +
            ls["time_deposits"] * tl * self.NSFR_ASF_RATES["time_deposits_1y+"] * 0.4 +
            ls["interbank"] * tl * self.NSFR_ASF_RATES["interbank_1y"] * 0.7 +
            ls["interbank"] * tl * self.NSFR_ASF_RATES["interbank_1y+"] * 0.3 +
            ls["bond_issuance"] * tl * self.NSFR_ASF_RATES["bond_issuance"] +
            ls["other"] * tl * self.NSFR_ASF_RATES["other"]
        )
        
        # RSF 计算
        # 基于资产期限分布估算RSF
        short_term_weight = asset_profile.get("1m", 0) + asset_profile.get("3m", 0) + asset_profile.get("6m", 0)
        medium_term_weight = asset_profile.get("1y", 0) + asset_profile.get("3y", 0)
        long_term_weight = asset_profile.get("5y", 0)
        
        # 假设：HQLA 15%，短期贷款 35%，中期贷款 30%，长期贷款 20%
        rsf = (
            ta * 0.15 * self.NSFR_RSF_RATES["hqla_level1"] +
            ta * 0.35 * self.NSFR_RSF_RATES["loan_1y"] * short_term_weight / max(short_term_weight + medium_term_weight + long_term_weight, 1) +
            ta * 0.30 * self.NSFR_RSF_RATES["loan_1y+"] * medium_term_weight / max(short_term_weight + medium_term_weight + long_term_weight, 1) +
            ta * 0.20 * self.NSFR_RSF_RATES["loan_1y+"] * long_term_weight / max(short_term_weight + medium_term_weight + long_term_weight, 1) +
            ta * 0.15 * self.NSFR_RSF_RATES["bond"] +
            ta * 0.05 * self.NSFR_RSF_RATES["other_assets"]
        )
        
        nsfr_ratio = (asf / rsf) if rsf > 0 else 999.0
        
        if nsfr_ratio >= 1.0:
            status = RiskStatus.GREEN.value
        elif nsfr_ratio >= 0.8:
            status = RiskStatus.YELLOW.value
        else:
            status = RiskStatus.RED.value
        
        self._nsfr_result = NSFRResult(
            available_stable_funding=asf,
            required_stable_funding=rsf,
            nsfr_ratio=nsfr_ratio,
            status=status,
        )
        return self._nsfr_result
    
    # ─── 久期缺口分析 ───────────────────────────
    
    def calculate_duration_gap(self) -> DurationGapResult:
        """
        计算久期缺口。
        
        久期缺口 = 资产久期 - 负债久期 × (负债/资产)
        调整后久期缺口 = 久期缺口 × 资产/负债比率
        
        久期缺口为正：利率上升时，资产价值下降幅度 > 负债价值下降幅度，净资产减少
        """
        if self._duration_gap is not None:
            return self._duration_gap
        
        asset_dur = self._data.get("asset_duration", 2.5)
        liability_dur = self._data.get("liability_duration", 1.5)
        al_ratio = self.total_liabilities / self.total_assets if self.total_assets > 0 else 0.85
        
        # 久期缺口
        duration_gap = asset_dur - liability_dur * al_ratio
        
        # 调整后久期缺口
        duration_gap_adjusted = duration_gap * al_ratio
        
        # 状态判断（调整后久期缺口 > 1年为高风险）
        if abs(duration_gap_adjusted) <= 0.5:
            status = RiskStatus.GREEN.value
        elif abs(duration_gap_adjusted) <= 1.0:
            status = RiskStatus.YELLOW.value
        else:
            status = RiskStatus.RED.value
        
        self._duration_gap = DurationGapResult(
            asset_duration=asset_dur,
            liability_duration=liability_dur,
            duration_gap=duration_gap,
            asset_liability_ratio=1.0 / al_ratio if al_ratio > 0 else 0,
            duration_gap_adjusted=duration_gap_adjusted,
            status=status,
        )
        return self._duration_gap
    
    # ─── 风险预警 ──────────────────────────────
    
    def generate_warnings(self) -> List[Warning]:
        """生成风险预警列表"""
        if self._warnings is not None:
            return self._warnings
        
        self._warnings = []
        
        # LCR 检查
        lcr = self.calculate_lcr()
        if lcr.lcr_ratio < 0.80:
            self._warnings.append(Warning(
                level="red",
                indicator="LCR",
                message=f"LCR={lcr.lcr_ratio:.1%} < 80%，严重低于监管要求（≥100%）",
                suggestion="立即增加优质流动性资产（HQLA），减少30天内到期的高成本负债"
            ))
        elif lcr.lcr_ratio < 1.0:
            self._warnings.append(Warning(
                level="yellow",
                indicator="LCR",
                message=f"LCR={lcr.lcr_ratio:.1%} 低于监管要求（≥100%）",
                suggestion="逐步增持一级HQLA，压降同业短期负债，引入中长期稳定资金"
            ))
        
        # NSFR 检查
        nsfr = self.calculate_nsfr()
        if nsfr.nsfr_ratio < 0.80:
            self._warnings.append(Warning(
                level="red",
                indicator="NSFR",
                message=f"NSFR={nsfr.nsfr_ratio:.1%} < 80%，严重低于监管要求（≥100%）",
                suggestion="发行中长期债券，增加稳定存款来源，压缩长期限贷款投放"
            ))
        elif nsfr.nsfr_ratio < 1.0:
            self._warnings.append(Warning(
                level="yellow",
                indicator="NSFR",
                message=f"NSFR={nsfr.nsfr_ratio:.1%} 低于监管要求（≥100%）",
                suggestion="延长负债期限结构，增加1年以上定期存款，减少短期同业负债"
            ))
        
        # 期限缺口检查
        gaps = self.calculate_gap_analysis()
        for bucket, gap_item in gaps.items():
            if gap_item.status == RiskStatus.RED.value:
                direction = "正缺口" if gap_item.gap > 0 else "负缺口"
                self._warnings.append(Warning(
                    level="red",
                    indicator=f"期限缺口({bucket})",
                    message=f"{bucket}期限 {direction}={abs(gap_item.gap_ratio):.1%}，超过±30%阈值",
                    suggestion="调整资产负债期限配置，使各档位缺口率控制在±20%以内"
                ))
            elif gap_item.status == RiskStatus.YELLOW.value:
                direction = "正缺口" if gap_item.gap > 0 else "负缺口"
                self._warnings.append(Warning(
                    level="yellow",
                    indicator=f"期限缺口({bucket})",
                    message=f"{bucket}期限 {direction}={abs(gap_item.gap_ratio):.1%}，处于±20%~±30%预警区间",
                    suggestion="关注期限错配风险，适时调整资产或负债结构"
                ))
        
        # 久期缺口检查
        dg = self.calculate_duration_gap()
        if dg.status == RiskStatus.RED.value:
            self._warnings.append(Warning(
                level="red",
                indicator="久期缺口",
                message=f"调整久期缺口={dg.duration_gap_adjusted:.2f}年，超过±1年阈值",
                suggestion="利用利率掉期（IRS）对冲长期利率风险，增加短期资产或延长负债久期"
            ))
        elif dg.status == RiskStatus.YELLOW.value:
            self._warnings.append(Warning(
                level="yellow",
                indicator="久期缺口",
                message=f"调整久期缺口={dg.duration_gap_adjusted:.2f}年，处于±0.5~±1年预警区间",
                suggestion="加强利率敏感性管理，择机开展久期缺口调整"
            ))
        
        return self._warnings
    
    # ─── 优化建议 ──────────────────────────────
    
    def generate_optimization(self) -> Dict[str, List[str]]:
        """生成优化建议"""
        if self._optimization is not None:
            return self._optimization
        
        lcr = self.calculate_lcr()
        nsfr = self.calculate_nsfr()
        gaps = self.calculate_gap_analysis()
        dg = self.calculate_duration_gap()
        
        self._optimization = {
            "liability_adjustment": [],
            "asset_optimization": [],
            "derivatives_hedge": [],
        }
        
        # 负债结构调整建议
        ls = self.liability_structure
        if ls["interbank"] > 0.15:
            self._optimization["liability_adjustment"].append(
                f"同业负债占比{ls['interbank']:.1%}偏高，建议压缩至15%以内，替换为稳定性更强的存款"
            )
        if ls["demand_deposits"] < 0.25:
            self._optimization["liability_adjustment"].append(
                f"活期存款占比{ls['demand_deposits']:.1%}偏低，建议加强活期存款营销，提升负债稳定性"
            )
        if ls["time_deposits"] > 0.65:
            self._optimization["liability_adjustment"].append(
                f"定期存款占比{ls['time_deposits']:.1%}偏高，建议适度发行中长期债券，优化负债成本"
            )
        
        # 检查NSFR
        if nsfr.nsfr_ratio < 1.0:
            self._optimization["liability_adjustment"].append(
                f"NSFR={nsfr.nsfr_ratio:.1%}<100%，建议增加1年以上稳定资金来源（定期存款/债券）"
            )
        
        # 资产配置优化建议
        if lcr.lcr_ratio < 1.0:
            hqla_needed = lcr.net_cash_outflow - lcr.hqla_total
            if hqla_needed > 0:
                self._optimization["asset_optimization"].append(
                    f"建议增持{self._format_yuan(hqla_needed)}一级HQLA（国债/央行存款），提升LCR至100%"
                )
        
        # 期限缺口优化
        for bucket, gap_item in gaps.items():
            if abs(gap_item.gap_ratio) > 0.25:
                direction = "资产" if gap_item.gap > 0 else "负债"
                self._optimization["asset_optimization"].append(
                    f"{bucket}期限档位存在较大{direction}缺口（{gap_item.gap_ratio:.1%}），"
                    f"建议通过同业存单、大额存单等工具进行期限匹配"
                )
        
        # 衍生品对冲建议
        if dg.duration_gap_adjusted > 0.5:
            self._optimization["derivatives_hedge"].append(
                f"久期缺口为正（{dg.duration_gap_adjusted:.2f}年），建议通过利率掉期（IRS）"
                f"锁定长期利率风险，将部分固定利率资产转为浮动利率"
            )
        if dg.duration_gap_adjusted < -0.5:
            self._optimization["derivatives_hedge"].append(
                f"久期缺口为负（{dg.duration_gap_adjusted:.2f}年），建议通过利率掉期（IRS）"
                f"锁定短期利率风险，将浮动利率负债固定化"
            )
        
        if lcr.lcr_ratio < 1.0:
            self._optimization["derivatives_hedge"].append(
                "建议配置流动性较好的国债期货作为流动性管理工具，提升HQLA周转效率"
            )
        
        # 如果没有具体建议，添加通用建议
        if not self._optimization["liability_adjustment"]:
            self._optimization["liability_adjustment"].append("当前负债结构总体稳健，建议持续监控各期限档位匹配情况")
        if not self._optimization["asset_optimization"]:
            self._optimization["asset_optimization"].append("当前资产配置总体合理，建议定期检视资产久期结构")
        if not self._optimization["derivatives_hedge"]:
            self._optimization["derivatives_hedge"].append("当前风险敞口可控，可关注利率市场择机开展对冲操作")
        
        return self._optimization
    
    # ─── 综合分析 ──────────────────────────────
    
    def analyze(self) -> Dict[str, Any]:
        """
        执行完整 ALM 分析，返回所有结果。
        """
        gaps = self.calculate_gap_analysis()
        lcr = self.calculate_lcr()
        nsfr = self.calculate_nsfr()
        dg = self.calculate_duration_gap()
        warnings = self.generate_warnings()
        optimization = self.generate_optimization()
        
        return {
            "gap_analysis": {
                bucket: {
                    "asset": item.asset,
                    "liability": item.liability,
                    "gap": item.gap,
                    "gap_ratio": item.gap_ratio,
                    "status": item.status,
                }
                for bucket, item in gaps.items()
            },
            "lcr": {
                "hqla": {
                    "level1": lcr.hqla_level1,
                    "level2": lcr.hqla_level2,
                    "total": lcr.hqla_total,
                },
                "net_cash_outflow": lcr.net_cash_outflow,
                "lcr_ratio": lcr.lcr_ratio,
                "status": lcr.status,
            },
            "nsfr": {
                "available_stable_funding": nsfr.available_stable_funding,
                "required_stable_funding": nsfr.required_stable_funding,
                "nsfr_ratio": nsfr.nsfr_ratio,
                "status": nsfr.status,
            },
            "duration_gap": {
                "asset_duration": dg.asset_duration,
                "liability_duration": dg.liability_duration,
                "duration_gap": dg.duration_gap,
                "duration_gap_adjusted": dg.duration_gap_adjusted,
                "status": dg.status,
            },
            "warnings": [
                {
                    "level": w.level,
                    "indicator": w.indicator,
                    "message": w.message,
                    "suggestion": w.suggestion,
                }
                for w in warnings
            ],
            "optimization": optimization,
        }
    
    def summary(self) -> str:
        """生成人类可读的文本摘要"""
        ta = self.total_assets
        lcr = self.calculate_lcr()
        nsfr = self.calculate_nsfr()
        dg = self.calculate_duration_gap()
        warnings = self.generate_warnings()
        optimization = self.generate_optimization()
        
        ta_str = self._format_yuan(ta)
        
        lines = [
            f"╔════════════════════════════════════════════════════════╗",
            f"║            ALM 资产负债管理分析报告                    ║",
            f"╠════════════════════════════════════════════════════════╣",
            f"║  总资产：{ta_str:<41}║",
            f"╠════════════════════════════════════════════════════════╣",
            f"║  【LCR 流动性覆盖率】                                  ║",
            f"║    HQLA：{self._format_yuan(lcr.hqla_total):<35}║",
            f"║    净流出：{self._format_yuan(lcr.net_cash_outflow):<35}║",
            f"║    LCR：{lcr.lcr_ratio:>7.1%}   状态：{self._status_emoji(lcr.status):<6}                   ║",
            f"╠════════════════════════════════════════════════════════╣",
            f"║  【NSFR 净稳定资金比率】                               ║",
            f"║    ASF：{self._format_yuan(nsfr.available_stable_funding):<35}║",
            f"║    RSF：{self._format_yuan(nsfr.required_stable_funding):<35}║",
            f"║    NSFR：{nsfr.nsfr_ratio:>6.1%}   状态：{self._status_emoji(nsfr.status):<6}                   ║",
            f"╠════════════════════════════════════════════════════════╣",
            f"║  【久期缺口分析】                                      ║",
            f"║    资产久期：{dg.asset_duration:.2f}年  负债久期：{dg.liability_duration:.2f}年                   ║",
            f"║    调整久期缺口：{dg.duration_gap_adjusted:>+.2f}年   状态：{self._status_emoji(dg.status):<6}       ║",
            f"╠════════════════════════════════════════════════════════╣",
            f"║  【期限缺口】                                          ║",
        ]
        
        buckets = ["1m", "3m", "6m", "1y", "3y", "5y"]
        gaps = self.calculate_gap_analysis()
        for bucket in buckets:
            g = gaps[bucket]
            emoji = self._status_emoji(g.status)
            lines.append(
                f"║    {bucket}：{g.gap:>+12.0f} 元 ({g.gap_ratio:>+6.1%}) {emoji}"
            )
        
        if warnings:
            lines.append(f"╠════════════════════════════════════════════════════════╣")
            lines.append(f"║  【风险预警】                                          ║")
            for w in warnings[:5]:  # 最多显示5条
                emoji = "🔴" if w.level == "red" else "🟡"
                lines.append(f"║  {emoji} {w.indicator}: {w.message[:40]}  ║")
        
        if optimization:
            lines.append(f"╠════════════════════════════════════════════════════════╣")
            lines.append(f"║  【优化建议】                                          ║")
            for cat, suggestions in optimization.items():
                if suggestions:
                    cat_name = {"liability_adjustment": "负债结构", "asset_optimization": "资产配置", "derivatives_hedge": "衍生品对冲"}.get(cat, cat)
                    for s in suggestions[:2]:  # 每类最多2条
                        lines.append(f"║  · {s[:44]}  ║")
        
        lines.append(f"╚════════════════════════════════════════════════════════╝")
        return "\n".join(lines)
    
    # ─── 辅助方法 ─────────────────────────────
    
    @staticmethod
    def _format_yuan(amount: float) -> str:
        """格式化金额显示"""
        if abs(amount) >= 1e8:
            return f"{amount/1e8:.2f} 亿"
        elif abs(amount) >= 1e4:
            return f"{amount/1e4:.2f} 万"
        else:
            return f"{amount:.2f} 元"
    
    @staticmethod
    def _status_emoji(status: str) -> str:
        return {"green": "✅", "yellow": "🟡", "red": "🔴"}.get(status, "⚪")
    
    def to_dict(self) -> Dict[str, Any]:
        """返回完整分析结果的字典格式"""
        return self.analyze()
    
    def to_json(self, indent: int = 2) -> str:
        """返回完整分析结果的 JSON 格式"""
        return json.dumps(self.analyze(), ensure_ascii=False, indent=indent)


# ─────────────────────────────────────────────
# 入口函数
# ─────────────────────────────────────────────

def analyze(text: str) -> Dict[str, Any]:
    """快捷分析函数"""
    engine = ALMEngine()
    engine.parse(text)
    return engine.analyze()


def summarize(text: str) -> str:
    """快捷摘要函数"""
    engine = ALMEngine()
    engine.parse(text)
    return engine.summary()


if __name__ == "__main__":
    # 测试
    import sys
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = "ALM 资产500亿 定期存款60% 活期30%"
    
    engine = ALMEngine()
    engine.parse(text)
    print(engine.summary())
    print()
    print("JSON Output:")
    print(engine.to_json())
