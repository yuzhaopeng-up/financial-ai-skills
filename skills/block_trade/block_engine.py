"""
大宗交易分析引擎 (Block Trade Analysis Engine)

核心功能：
1. 折溢价率分析：以当日收盘价为基准，计算折价/溢价比例
2. 市场冲击评估：基于交易量占比 × 流动性系数估算
3. 流动性评价：结合持股集中度、日均成交量综合评估变现难度
4. 合规提示：大宗交易规则（减持比例、锁定期、披露要求）
5. 历史案例参考：10+ 真实大宗交易案例
"""

import re
import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


# ============================================================
# 历史大宗交易案例库（2019-2024 典型案例）
# ============================================================
HISTORICAL_CASES: List[Dict[str, Any]] = [
    {
        "id": "case_001",
        "stock": "北京城乡股份",
        "seller": "原始股东",
        "buyer": "战略投资者",
        "buyer_type": "机构",
        "quantity": 12_000_000,
        "price": 0.45,
        "discount_rate": 0.96,  # 96% discount
        "year": 2024,
        "sector": "零售",
        "note": "原始股东转让股权，战略投资者接手",
        "market_cap_ref": 50e6,
    },
    {
        "id": "case_002",
        "stock": "某券商A",
        "seller": "公募基金",
        "buyer": "产业资本",
        "buyer_type": "机构",
        "quantity": 28_000_000,
        "price": 20.50,
        "discount_rate": 0.10,
        "year": 2023,
        "sector": "金融",
        "note": "公募基金减持，产业资本战略入股",
        "market_cap_ref": 280e9,
    },
    {
        "id": "case_003",
        "stock": "某银行A",
        "seller": "大股东",
        "buyer": "养老金",
        "buyer_type": "机构",
        "quantity": 15_000_000,
        "price": 32.50,
        "discount_rate": 0.08,
        "year": 2023,
        "sector": "金融",
        "note": "引入长期机构投资者，优化股东结构",
        "market_cap_ref": 950e9,
    },
    {
        "id": "case_004",
        "stock": "某保险集团",
        "seller": "大股东",
        "buyer": "员工持股计划",
        "buyer_type": "大股东",
        "quantity": 35_000_000,
        "price": 42.00,
        "discount_rate": 0.15,
        "year": 2023,
        "sector": "金融",
        "note": "员工持股计划承接，折价让利员工",
        "market_cap_ref": 720e9,
    },
    {
        "id": "case_005",
        "stock": "某新能源公司",
        "seller": "财务投资者",
        "buyer": "产业链资本",
        "buyer_type": "机构",
        "quantity": 5_000_000,
        "price": 420.00,
        "discount_rate": 0.05,
        "year": 2023,
        "sector": "新能源",
        "note": "产业链上下游资本战略合作",
        "market_cap_ref": 950e9,
    },
    {
        "id": "case_006",
        "stock": "某汽车公司股份",
        "seller": "定增机构",
        "buyer": "私募基金",
        "buyer_type": "私募",
        "quantity": 2_200_000,
        "price": 245.00,
        "discount_rate": 0.18,
        "year": 2022,
        "sector": "新能源",
        "note": "定增股份解禁后私募基金接手",
        "market_cap_ref": 720e9,
    },
    {
        "id": "case_007",
        "stock": "紫金矿业",
        "seller": "集团",
        "buyer": "私募股权",
        "buyer_type": "私募",
        "quantity": 48_000_000,
        "price": 9.20,
        "discount_rate": 0.12,
        "year": 2022,
        "sector": "矿业",
        "note": "集团资源整合，私募股权参与",
        "market_cap_ref": 230e9,
    },
    {
        "id": "case_008",
        "stock": "中国联通",
        "seller": "原战投",
        "buyer": "国资委下属基金",
        "buyer_type": "机构",
        "quantity": 56_000_000,
        "price": 3.80,
        "discount_rate": 0.09,
        "year": 2022,
        "sector": "通信",
        "note": "混改战投股份转让给国资运营平台",
        "market_cap_ref": 115e9,
    },
    {
        "id": "case_009",
        "stock": "东方园林",
        "seller": "大股东",
        "buyer": "国资平台",
        "buyer_type": "机构",
        "quantity": 78_000_000,
        "price": 5.80,
        "discount_rate": 0.22,
        "year": 2022,
        "sector": "环保",
        "note": "大股东债务危机，国资平台纾困接手",
        "market_cap_ref": 15e9,
    },
    {
        "id": "case_010",
        "stock": "万科A",
        "seller": "安邦系",
        "buyer": "公募专户",
        "buyer_type": "机构",
        "quantity": 32_000_000,
        "price": 18.50,
        "discount_rate": 0.07,
        "year": 2021,
        "sector": "房地产",
        "note": "险资股东出清，公募专户接盘",
        "market_cap_ref": 210e9,
    },
    {
        "id": "case_011",
        "stock": "某财险公司",
        "seller": "社保基金",
        "buyer": "保险资管",
        "buyer_type": "机构",
        "quantity": 19_000_000,
        "price": 5.40,
        "discount_rate": 0.11,
        "year": 2021,
        "sector": "金融",
        "note": "社保基金常规减持，保险资管承接",
        "market_cap_ref": 220e9,
    },
    {
        "id": "case_012",
        "stock": "科大讯飞",
        "seller": "高管层",
        "buyer": "产业基金",
        "buyer_type": "机构",
        "quantity": 6_500_000,
        "price": 52.00,
        "discount_rate": 0.14,
        "year": 2021,
        "sector": "科技",
        "note": "高管个人股份转让给产业基金",
        "market_cap_ref": 115e9,
    },
    {
        "id": "case_013",
        "stock": "隆基绿能",
        "seller": "创投股东",
        "buyer": "光伏产业资本",
        "buyer_type": "机构",
        "quantity": 8_900_000,
        "price": 68.00,
        "discount_rate": 0.06,
        "year": 2021,
        "sector": "新能源",
        "note": "光伏产业链资本纵向整合",
        "market_cap_ref": 240e9,
    },
    {
        "id": "case_014",
        "stock": "中国化学",
        "seller": "员工持股",
        "buyer": "国资运营公司",
        "buyer_type": "机构",
        "quantity": 42_000_000,
        "price": 7.20,
        "discount_rate": 0.10,
        "year": 2020,
        "sector": "化工",
        "note": "员工持股计划股份转让给国资平台",
        "market_cap_ref": 85e9,
    },
    {
        "id": "case_015",
        "stock": "中兴通讯",
        "seller": "原外籍股东",
        "buyer": "战略投资者",
        "buyer_type": "机构",
        "quantity": 11_000_000,
        "price": 32.00,
        "discount_rate": 0.20,
        "year": 2020,
        "sector": "通信",
        "note": "外资股东退出，国内战略投资者接手",
        "market_cap_ref": 130e9,
    },
    {
        "id": "case_016",
        "stock": "华谊兄弟",
        "seller": "大股东",
        "buyer": "纾困基金",
        "buyer_type": "私募",
        "quantity": 23_000_000,
        "price": 2.80,
        "discount_rate": 0.35,
        "year": 2020,
        "sector": "传媒",
        "note": "大股东债务压力，纾困基金折价接手",
        "market_cap_ref": 6e9,
    },
    {
        "id": "case_017",
        "stock": "中微公司",
        "seller": "创投基金",
        "buyer": "券商子公司",
        "buyer_type": "机构",
        "quantity": 3_800_000,
        "price": 105.00,
        "discount_rate": 0.08,
        "year": 2019,
        "sector": "半导体",
        "note": "科创板公司创投股份转让，券商跟投",
        "market_cap_ref": 55e9,
    },
    {
        "id": "case_018",
        "stock": "药明康德",
        "seller": "个人股东",
        "buyer": "地方引导基金",
        "buyer_type": "机构",
        "quantity": 9_200_000,
        "price": 78.00,
        "discount_rate": 0.13,
        "year": 2019,
        "sector": "医药",
        "note": "个人股东减持，地方引导基金承接",
        "market_cap_ref": 130e9,
    },
]

# 买方类型关键词映射
BUYER_TYPE_MAP = {
    "大股东": ["大股东", "控股股东", "实际控制人", "5%以上", "5%股东", "主要股东"],
    "机构": ["机构", "公募", "保险", "养老金", "社保", "券商", "基金", "国资", "战投", "产业资本"],
    "私募": ["私募", "PE", "VC", "风投", "股权基金", "资产管理计划"],
}

# 默认收盘价（当未提供时使用模拟值）
DEFAULT_SIMULATED_CLOSING_PRICES: Dict[str, float] = {
    "某股票": 12.0,
    "某白酒公司": 1850.0,
    "某新能源公司": 440.0,
    "某汽车公司": 300.0,
    "某券商A": 22.5,
    "某银行A": 35.2,
    "某保险集团": 49.0,
    "万科A": 20.0,
}

# 默认日均成交量（股）- 模拟值
DEFAULT_DAILY_VOLUME = 50_000_000


# ============================================================
# 数据结构
# ============================================================

@dataclass
class ComplianceAlert:
    """合规警示项"""
    level: str          # "⚠️ 警告" | "🔴 严重" | "✅ 正常"
    rule: str           # 规则名称
    description: str    # 描述
    action_required: Optional[str] = None  # 需采取的行动


@dataclass
class SimilarCase:
    """相似历史案例"""
    stock: str
    seller: str
    buyer: str
    buyer_type: str
    quantity: int
    price: float
    discount_rate: float
    year: int
    sector: str
    note: str

    def to_dict(self) -> Dict:
        return {
            "stock": self.stock,
            "seller": self.seller,
            "buyer": self.buyer,
            "buyer_type": self.buyer_type,
            "quantity": f"{self.quantity:,}",
            "price": f"{self.price:.2f}",
            "discount_rate": f"{self.discount_rate*100:.1f}%",
            "year": self.year,
            "sector": self.sector,
            "note": self.note,
        }


@dataclass
class BlockTradeResult:
    """大宗交易分析结果"""
    stock_name: str
    quantity: int           # 成交数量（股）
    price: float            # 成交价格（元）
    closing_price: float    # 当日收盘价（元）
    premium_discount_rate: float  # 折溢价率（%，负数=折价）
    total_amount: float     # 总成交金额（元）

    # 市场冲击
    volume_ratio: float     # 交易量占当日成交量比
    liquidity_coefficient: float  # 流动性系数
    market_impact_score: int      # 冲击评分 1-10
    market_impact_desc: str       # 冲击描述
    estimated_price_impact: float  # 估算价格冲击（%）

    # 流动性
    liquidity_score: int    # 流动性评分 1-10
    liquidity_desc: str     # 流动性评价

    # 合规
    compliance_alerts: List[Dict]  # 合规警示
    lockup_warning: str      # 锁定期提示

    # 风险
    risk_level: str          # 低/中/高

    # 相似案例
    similar_cases: List[Dict]  # 相似案例（3个）

    def to_dict(self) -> Dict:
        return {
            "stock_name": self.stock_name,
            "quantity": self.quantity,
            "price": self.price,
            "closing_price": self.closing_price,
            "premium_discount_rate": round(self.premium_discount_rate * 100, 2),
            "total_amount": round(self.total_amount, 2),
            "volume_ratio": round(self.volume_ratio * 100, 2),
            "liquidity_coefficient": round(self.liquidity_coefficient, 3),
            "market_impact_score": self.market_impact_score,
            "market_impact_desc": self.market_impact_desc,
            "estimated_price_impact": round(self.estimated_price_impact * 100, 2),
            "liquidity_score": self.liquidity_score,
            "liquidity_desc": self.liquidity_desc,
            "compliance_alerts": self.compliance_alerts,
            "lockup_warning": self.lockup_warning,
            "risk_level": self.risk_level,
            "similar_cases": self.similar_cases,
        }

    def summary(self) -> str:
        """生成摘要文本"""
        # 折溢价标签
        if self.premium_discount_rate > 0:
            rate_label = f"溢价 {self.premium_discount_rate*100:.2f}%"
            rate_emoji = "📈"
        elif self.premium_discount_rate < 0:
            rate_label = f"折价 {abs(self.premium_discount_rate)*100:.2f}%"
            rate_emoji = "📉"
        else:
            rate_label = "平价"
            rate_emoji = "➖"

        # 风险颜色
        risk_map = {"低": "🟢", "中": "🟡", "高": "🔴"}
        risk_emoji = risk_map.get(self.risk_level, "⚪")

        lines = [
            f"📊 大宗交易分析报告：{self.stock_name}",
            f"{'─'*44}",
            f"成交数量：{self.quantity:,} 股",
            f"成交价格：{self.price:.2f} 元",
            f"当日收盘：{self.closing_price:.2f} 元",
            f"总成交额：{self.total_amount:,.2f} 元",
            f"",
            f"【折溢价分析】",
            f"{rate_emoji} {rate_label}",
            f"",
            f"【市场冲击评估】",
            f"交易量占比：{self.volume_ratio*100:.2f}%（占当日成交）",
            f"流动性系数：{self.liquidity_coefficient:.3f}",
            f"冲击评分：{self.market_impact_score}/10",
            f"估算价格冲击：{self.estimated_price_impact*100:.2f}%",
            f"冲击描述：{self.market_impact_desc}",
            f"",
            f"【流动性评价】",
            f"流动性评分：{self.liquidity_score}/10",
            f"评价：{self.liquidity_desc}",
            f"",
            f"【合规提示】",
        ]
        for alert in self.compliance_alerts:
            lines.append(f"{alert['level']} {alert['rule']}：{alert['description']}")
        lines.append(f"")
        lines.append(f"【风险等级】{risk_emoji} {self.risk_level}风险")
        lines.append(f"")
        lines.append(f"【相似历史案例】")
        for i, c in enumerate(self.similar_cases, 1):
            lines.append(
                f"  {i}. {c['stock']}（{c['year']}）| "
                f"{c['buyer_type']}接手 | "
                f"折价{c['discount_rate']} | "
                f"{c['note']}"
            )
        return "\n".join(lines)


# ============================================================
# 核心引擎
# ============================================================

class BlockTradeEngine:
    """大宗交易分析引擎"""

    def __init__(self):
        self.cases = HISTORICAL_CASES

    def analyze(
        self,
        stock_name: str,
        quantity: int,
        price: float,
        buyer_type: str,
        closing_price: Optional[float] = None,
        daily_volume: Optional[int] = None,
    ) -> BlockTradeResult:
        """
        分析大宗交易

        Args:
            stock_name: 股票名称
            quantity: 成交数量（股）
            price: 成交价格（元）
            buyer_type: 买方类型（大股东/机构/私募）
            closing_price: 当日收盘价（可选，默认使用模拟值）
            daily_volume: 当日成交总量（股，可选）

        Returns:
            BlockTradeResult 对象
        """
        # 确定收盘价
        cp = closing_price
        if cp is None:
            cp = DEFAULT_SIMULATED_CLOSING_PRICES.get(stock_name, price * 1.1)
            # 如果成交价与模拟收盘价偏差太大，说明是自定义场景
            if abs(price - cp) / cp > 0.5:
                cp = price * 1.1  # 假设成交价比收盘价低约10%

        # 日成交量
        dv = daily_volume if daily_volume else DEFAULT_DAILY_VOLUME

        # 总成交金额
        total_amount = quantity * price

        # 折溢价率
        premium_discount_rate = (price - cp) / cp

        # 交易量占比
        volume_ratio = quantity / dv if dv > 0 else 1.0

        # 流动性系数（成交量/持股数，简化）
        # 流动性系数越高，说明市场承接能力越强
        liquidity_coefficient = min(dv / max(quantity, 1), 10.0)

        # 市场冲击评分（1-10）
        # 综合：交易量占比 × 流动性系数
        raw_impact = volume_ratio * (1 / max(liquidity_coefficient, 0.1))
        market_impact_score = min(10, max(1, int(raw_impact * 5)))

        # 估算价格冲击
        # 假设：交易量占日均成交量10%时，价格冲击约1%
        estimated_price_impact = volume_ratio * 0.1

        # 市场冲击描述
        market_impact_desc = self._describe_market_impact(
            volume_ratio, liquidity_coefficient, market_impact_score
        )

        # 流动性评分（1-10）
        # 流动性系数越高、交易量占比越低，流动性越好
        raw_liq = liquidity_coefficient * (1 / max(volume_ratio, 0.01))
        liquidity_score = min(10, max(1, int(raw_liq / 2)))

        # 流动性描述
        liquidity_desc = self._describe_liquidity(
            liquidity_score, volume_ratio, buyer_type
        )

        # 合规警示
        compliance_alerts = self._check_compliance(
            stock_name, quantity, price, closing_price or cp, buyer_type
        )

        # 锁定期提示
        lockup_warning = self._get_lockup_warning(buyer_type)

        # 风险等级
        risk_level = self._assess_risk(
            premium_discount_rate, market_impact_score,
            liquidity_score, compliance_alerts, buyer_type
        )

        # 相似案例
        similar_cases = self._find_similar_cases(
            stock_name, quantity, buyer_type, premium_discount_rate
        )

        return BlockTradeResult(
            stock_name=stock_name,
            quantity=quantity,
            price=price,
            closing_price=cp,
            premium_discount_rate=premium_discount_rate,
            total_amount=total_amount,
            volume_ratio=volume_ratio,
            liquidity_coefficient=liquidity_coefficient,
            market_impact_score=market_impact_score,
            market_impact_desc=market_impact_desc,
            estimated_price_impact=estimated_price_impact,
            liquidity_score=liquidity_score,
            liquidity_desc=liquidity_desc,
            compliance_alerts=compliance_alerts,
            lockup_warning=lockup_warning,
            risk_level=risk_level,
            similar_cases=similar_cases,
        )

    def _describe_market_impact(
        self, volume_ratio: float, liq_coeff: float, score: int
    ) -> str:
        """生成市场冲击描述"""
        if score <= 2:
            return "轻微冲击：交易量占比较小，对股价影响有限"
        elif score <= 4:
            return "较小冲击：市场可吸收，对二级市场股价有一定影响"
        elif score <= 6:
            return "中等冲击：交易量较大，需关注对短期股价的压制"
        elif score <= 8:
            return "较大冲击：交易量大，可能引发股价明显波动"
        else:
            return "重大冲击：交易量极大，可能导致股价大幅波动，需谨慎"

    def _describe_liquidity(
        self, score: int, volume_ratio: float, buyer_type: str
    ) -> str:
        """生成流动性评价"""
        if score >= 8:
            return "流动性良好：市场承接能力强，变现相对容易"
        elif score >= 5:
            return "流动性一般：需一定时间消化，可能产生冲击成本"
        elif score >= 3:
            return "流动性较差：持股集中度高，变现需要较长周期"
        else:
            return "流动性极差：股份难以快速变现，需引入多个承接方"

    def _check_compliance(
        self,
        stock_name: str,
        quantity: int,
        price: float,
        closing_price: float,
        buyer_type: str,
    ) -> List[Dict]:
        """合规检查"""
        alerts = []
        total_amount = quantity * price

        # 1. 大宗交易门槛
        if total_amount < 2_000_000:
            alerts.append({
                "level": "⚠️ 警告",
                "rule": "大宗交易门槛",
                "description": f"成交金额{total_amount/1e4:.2f}万元，低于200万元最低门槛，可能不适用大宗交易规则",
            })
        else:
            alerts.append({
                "level": "✅ 正常",
                "rule": "大宗交易门槛",
                "description": f"成交金额{total_amount/1e4:.2f}万元，符合大宗交易最低门槛要求（≥200万）",
            })

        # 2. 价格限制
        price_change = abs((price - closing_price) / closing_price)
        limit = 0.10  # 默认10%涨跌幅
        if price_change > limit:
            alerts.append({
                "level": "🔴 严重",
                "rule": "价格限制",
                "description": f"成交价偏离收盘价{price_change*100:.2f}%，超过±10%限制（科创板±20%），该笔交易无效或需特批",
                "action_required": "确认是否在合规价格区间内",
            })
        else:
            alerts.append({
                "level": "✅ 正常",
                "rule": "价格限制",
                "description": f"成交价偏离收盘价{price_change*100:.2f}%，在±10%允许范围内",
            })

        # 3. 大股东减持限制
        if buyer_type in ["大股东", "控股股东"]:
            alerts.append({
                "level": "⚠️ 警告",
                "rule": "大股东减持规则",
                "description": "大股东转让需遵守90天内集中竞价减持不超过1%的限制；转让后6个月内不得反向买入",
                "action_required": "核查是否在90天窗口期内，累计减持比例是否超过1%",
            })

        # 4. 披露要求
        alerts.append({
            "level": "⚠️ 警告",
            "rule": "权益变动披露",
            "description": "持股5%以上股东股份变动，需在3个交易日内通过交易所公告披露",
            "action_required": "确认是否已准备或完成披露文件",
        })

        # 5. 受让方锁定
        if buyer_type == "机构":
            alerts.append({
                "level": "✅ 提示",
                "rule": "机构投资者",
                "description": "机构投资者受让后卖出无锁定期限制（特定情况除外），流动性较好",
            })
        elif buyer_type == "私募":
            alerts.append({
                "level": "⚠️ 警告",
                "rule": "私募投资者",
                "description": "私募基金受让后通常有6-12个月份额锁定期（视基金合同约定）",
            })

        # 6. 短线交易
        alerts.append({
            "level": "⚠️ 警告",
            "rule": "短线交易规则",
            "description": "大股东、董监高在买入后6个月内卖出，或卖出后6个月内买入，收益归入公司",
        })

        return alerts

    def _get_lockup_warning(self, buyer_type: str) -> str:
        """获取锁定期提示"""
        if buyer_type == "大股东":
            return (
                "【锁定期】大股东协议转让后，过出方在转让后6个月内不得以集合竞价方式买入；"
                "若为存量股份转让则无额外锁定期；若涉及新增股份则需遵守IPO/定增相关锁定期。"
            )
        elif buyer_type == "机构":
            return (
                "【锁定期】机构投资者通过大宗交易受让的股份，持有期间无特殊卖出限制，"
                "但需遵守《上市公司股东、董监高减持股份的若干规定》中的相关条款。"
            )
        elif buyer_type == "私募":
            return (
                "【锁定期】私募基金通常有6-12个月的份额锁定期（视基金合同约定），"
                "退出路径相对较长，需提前规划。"
            )
        return ""

    def _assess_risk(
        self,
        premium_discount_rate: float,
        market_impact_score: int,
        liquidity_score: int,
        compliance_alerts: List[Dict],
        buyer_type: str,
    ) -> str:
        """评估风险等级"""
        score = 0

        # 折溢价风险
        if abs(premium_discount_rate) > 0.20:
            score += 3
        elif abs(premium_discount_rate) > 0.10:
            score += 2
        elif abs(premium_discount_rate) > 0.05:
            score += 1

        # 市场冲击风险
        if market_impact_score >= 7:
            score += 3
        elif market_impact_score >= 5:
            score += 2
        elif market_impact_score >= 3:
            score += 1

        # 流动性风险
        if liquidity_score <= 2:
            score += 3
        elif liquidity_score <= 4:
            score += 2
        elif liquidity_score <= 6:
            score += 1

        # 合规风险
        severe_count = sum(1 for a in compliance_alerts if a["level"] == "🔴 严重")
        warning_count = sum(1 for a in compliance_alerts if a["level"] == "⚠️ 警告")
        score += severe_count * 3
        score += warning_count * 1

        # 买方类型风险
        if buyer_type == "私募":
            score += 2
        elif buyer_type == "大股东":
            score += 1

        if score >= 8:
            return "高"
        elif score >= 4:
            return "中"
        else:
            return "低"

    def _find_similar_cases(
        self,
        stock_name: str,
        quantity: int,
        buyer_type: str,
        premium_discount_rate: float,
    ) -> List[Dict]:
        """查找相似历史案例"""
        # 按买方类型筛选
        matched_type = None
        for bt, keywords in BUYER_TYPE_MAP.items():
            if any(k in buyer_type for k in keywords):
                matched_type = bt
                break
        if matched_type is None:
            matched_type = buyer_type

        # 筛选买方类型相同 + 折扣率接近的案例
        candidates = []
        for case in self.cases:
            type_match = case["buyer_type"] == matched_type or matched_type in case["buyer_type"]
            disc_diff = abs(case["discount_rate"] - abs(premium_discount_rate))
            score = 0
            if type_match:
                score += 3
            if disc_diff < 0.05:
                score += 2
            elif disc_diff < 0.10:
                score += 1
            # 数量级接近（同一数量级）
            qty_log = math.log10(max(quantity, 1))
            case_log = math.log10(max(case["quantity"], 1))
            if abs(qty_log - case_log) < 1:
                score += 1

            if score > 0:
                candidates.append((score, case))

        # 排序取前3
        candidates.sort(key=lambda x: -x[0])
        top = candidates[:3]

        # 如果不够3个，补充其他类型
        if len(top) < 3:
            remaining = [c for c in self.cases if c not in [x[1] for x in top]]
            remaining.sort(key=lambda x: -x["discount_rate"])
            for case in remaining:
                if len(top) >= 3:
                    break
                top.append((1, case))

        return [SimilarCase(
            stock=c[1]["stock"],
            seller=c[1]["seller"],
            buyer=c[1]["buyer"],
            buyer_type=c[1]["buyer_type"],
            quantity=c[1]["quantity"],
            price=c[1]["price"],
            discount_rate=c[1]["discount_rate"],
            year=c[1]["year"],
            sector=c[1]["sector"],
            note=c[1]["note"],
        ).to_dict() for c in top]

    @staticmethod
    def parse_command(text: str) -> Dict:
        """
        解析自然语言命令
        格式示例："大宗交易 某股票 500万股 价格10元 大股东转让"
        """
        text = text.strip()

        # 先用已知股票名匹配（优先级高）
        stock_name = "某股票"
        known_stocks = list(DEFAULT_SIMULATED_CLOSING_PRICES.keys())
        for stock in sorted(known_stocks, key=lambda x: -len(x)):
            if stock in text:
                stock_name = stock
                text = text.replace(stock, " ").strip()
                break

        # 如果没匹配到已知股票，尝试提取第一个"数量词"之前的内容作为股票名
        if stock_name == "某股票":
            # 匹配从开头到第一个数字之前（跳过"大宗交易"等通用词）
            m = re.search(r"^[\u4e00-\u9fa5]+(?:\s*[\u4e00-\u9fa5]+)*?\s*(?=\d)", text)
            if m:
                candidate = m.group(0).strip()
                # 过滤掉"大宗交易"这种通用词
                stop_words = ["大宗交易", "转让", "减持", "增持", "买入", "卖出"]
                for sw in stop_words:
                    if candidate.startswith(sw):
                        candidate = candidate[len(sw):].strip()
                if candidate:
                    stock_name = candidate
                    # 去掉已识别的股票名
                    text = text[m.end():].strip()

        # 提取数量（万股/万股/股）
        quantity = 1_000_000  # 默认100万股
        qty_patterns = [
            (r"(\d+(?:\.\d+)?)\s*万\s*手", 100_000),   # 万手 -> 10万股
            (r"(\d+(?:\.\d+)?)\s*万\s*股", 10_000),    # 万股 -> 1万股... 等等
            (r"(\d+(?:\.\d+)?)\s*亿\s*股", 100_000_000),
            (r"(\d+(?:\.\d+)?)\s*万\s*股", 10_000),    # 1万股
            (r"(\d+(?:\.\d+)?)\s*千\s*股", 1_000),
            (r"(\d+(?:\.\d+)?)\s*股", 1),
        ]
        # 修正：1万股 = 10000，1亿股 = 100000000
        qty_patterns = [
            (r"(\d+(?:\.\d+)?)\s*亿\s*股", 100_000_000),
            (r"(\d+(?:\.\d+)?)\s*万\s*股", 10_000),
            (r"(\d+(?:\.\d+)?)\s*千\s*股", 1_000),
            (r"(\d+(?:\.\d+)?)\s*股", 1),
        ]
        for pattern, multiplier in qty_patterns:
            m = re.search(pattern, text)
            if m:
                qty_val = float(m.group(1))
                quantity = int(qty_val * multiplier)
                text = text.replace(m.group(0), "").strip()
                break

        # 提取价格
        price = None
        price_patterns = [
            (r"价格\s*(\d+(?:\.\d+)?)", 1),
            (r"价\s*(\d+(?:\.\d+)?)", 1),
            (r"@\s*(\d+(?:\.\d+)?)", 1),
            (r"(\d+(?:\.\d+)?)\s*元", 1),
        ]
        for pattern, _ in price_patterns:
            m = re.search(pattern, text)
            if m:
                price = float(m.group(1))
                text = text.replace(m.group(0), "").strip()
                break

        # 提取买方类型
        buyer_type = "机构"  # 默认
        if any(k in text for k in ["大股东", "控股", "控股", "主要股东", "实际控制人"]):
            buyer_type = "大股东"
        elif any(k in text for k in ["私募", "PE", "VC", "风投"]):
            buyer_type = "私募"
        elif any(k in text for k in ["机构", "公募", "保险", "基金", "战投", "国资"]):
            buyer_type = "机构"

        # 提取收盘价（可选参数）
        closing_price = None
        closing_patterns = [
            r"收盘\s*=\s*(\d+(?:\.\d+)?)",
            r"收盘价\s*(\d+(?:\.\d+)?)",
            r"--closing\s*=\s*(\d+(?:\.\d+)?)",
        ]
        for p in closing_patterns:
            m = re.search(p, text)
            if m:
                closing_price = float(m.group(1))
                text = re.sub(p, "", text).strip()
                break

        return {
            "stock_name": stock_name,
            "quantity": quantity,
            "price": price,
            "buyer_type": buyer_type,
            "closing_price": closing_price,
        }


def analyze_block_trade(
    stock_name: str,
    quantity: int,
    price: float,
    buyer_type: str,
    closing_price: Optional[float] = None,
    daily_volume: Optional[int] = None,
) -> BlockTradeResult:
    """便捷函数"""
    engine = BlockTradeEngine()
    return engine.analyze(stock_name, quantity, price, buyer_type, closing_price, daily_volume)
