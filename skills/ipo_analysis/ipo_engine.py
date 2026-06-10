"""
IPO Analysis Engine
提供PE/PB/PS三种估值方法 + 同业对比 + 定价区间 + 中签率估算 + 上市后表现预测
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class IPOCase:
    """IPO案例数据（已脱敏）"""
    name: str  # 脱敏后的公司名，如"某互联网公司"
    industry: str
    board: str  # 主板/创业板/科创板/北交所
    ipo_price: float  # 发行价
    pe_ratio: float  # 发行PE
    pb_ratio: float  # 发行PB
    ps_ratio: float  # 发行PS
    first_day_change: float  # 首日涨跌幅%
    fundraising_billion: float  # 募资额（亿元）
    market_cap_ipo: float  # 上市首日市值（亿元）
    eps: float  # 每股收益
    nav_per_share: float  # 每股净资产
    revenue_per_share: float  # 每股营收


@dataclass
class IndustryBenchmark:
    """行业基准数据"""
    industry: str
    avg_pe: float
    avg_pb: float
    avg_ps: float
    median_pe: float
    median_pb: float


@dataclass
class IPOAnalysisResult:
    """IPO分析结果"""
    company_name: str
    industry: str
    board: str
    fundraising_amount: float  # 元

    # 三种估值结果
    pe_valuation: Dict
    pb_valuation: Dict
    ps_valuation: Dict

    # 综合定价区间
    price_range: Tuple[float, float]
    mid_price: float

    # 同业对比
    peers: List[Dict]

    # 中签率
    winning_rate: float
    winning_rate_note: str

    # 上市后表现预测
    first_day_prediction: Dict
    long_term_outlook: Dict


# ============================================================
# 内置IPO案例数据（已脱敏）
# ============================================================

IPO_CASES: List[IPOCase] = [
    # 互联网/科技
    IPOCase(name="某大型互联网公司A", industry="互联网服务", board="主板",
            ipo_price=68.0, pe_ratio=50.2, pb_ratio=9.8, ps_ratio=12.5,
            first_day_change=44.0, fundraising_billion=320.0, market_cap_ipo=2800.0,
            eps=1.35, nav_per_share=6.9, revenue_per_share=5.4),
    IPOCase(name="某电商平台公司B", industry="电子商务", board="主板",
            ipo_price=68.8, pe_ratio=52.1, pb_ratio=12.3, ps_ratio=9.8,
            first_day_change=38.0, fundraising_billion=380.0, market_cap_ipo=3200.0,
            eps=1.32, nav_per_share=5.6, revenue_per_share=7.0),
    IPOCase(name="某云计算公司C", industry="云计算", board="科创板",
            ipo_price=45.0, pe_ratio=68.5, pb_ratio=7.2, ps_ratio=15.3,
            first_day_change=85.0, fundraising_billion=45.0, market_cap_ipo=220.0,
            eps=0.66, nav_per_share=6.3, revenue_per_share=2.9),
    IPOCase(name="某AI软件公司D", industry="人工智能", board="创业板",
            ipo_price=32.5, pe_ratio=72.0, pb_ratio=6.8, ps_ratio=18.2,
            first_day_change=62.0, fundraising_billion=28.0, market_cap_ipo=145.0,
            eps=0.45, nav_per_share=4.8, revenue_per_share=1.8),
    IPOCase(name="某社交媒体公司E", industry="社交网络", board="主板",
            ipo_price=82.0, pe_ratio=45.5, pb_ratio=8.5, ps_ratio=11.2,
            first_day_change=36.0, fundraising_billion=520.0, market_cap_ipo=4800.0,
            eps=1.80, nav_per_share=9.6, revenue_per_share=7.3),

    # 半导体/硬件
    IPOCase(name="某芯片设计公司F", industry="半导体设计", board="科创板",
            ipo_price=62.0, pe_ratio=75.0, pb_ratio=9.5, ps_ratio=22.0,
            first_day_change=128.0, fundraising_billion=55.0, market_cap_ipo=380.0,
            eps=0.83, nav_per_share=6.5, revenue_per_share=2.8),
    IPOCase(name="某半导体设备公司G", industry="半导体设备", board="科创板",
            ipo_price=73.0, pe_ratio=82.0, pb_ratio=11.2, ps_ratio=18.5,
            first_day_change=95.0, fundraising_billion=85.0, market_cap_ipo=620.0,
            eps=0.89, nav_per_share=6.5, revenue_per_share=3.9),
    IPOCase(name="某消费电子公司H", industry="消费电子", board="主板",
            ipo_price=28.5, pe_ratio=38.0, pb_ratio=5.2, ps_ratio=3.8,
            first_day_change=22.0, fundraising_billion=65.0, market_cap_ipo=480.0,
            eps=0.75, nav_per_share=5.5, revenue_per_share=7.5),
    IPOCase(name="某通信设备公司I", industry="通信设备", board="主板",
            ipo_price=38.0, pe_ratio=42.0, pb_ratio=5.8, ps_ratio=4.5,
            first_day_change=28.0, fundraising_billion=75.0, market_cap_ipo=560.0,
            eps=0.90, nav_per_share=6.6, revenue_per_share=8.4),
    IPOCase(name="某光伏公司J", industry="光伏新能源", board="主板",
            ipo_price=22.5, pe_ratio=35.0, pb_ratio=4.2, ps_ratio=5.5,
            first_day_change=55.0, fundraising_billion=95.0, market_cap_ipo=680.0,
            eps=0.64, nav_per_share=5.4, revenue_per_share=4.1),

    # 医疗健康
    IPOCase(name="某创新药公司K", industry="生物医药", board="科创板",
            ipo_price=52.0, pe_ratio=92.0, pb_ratio=8.5, ps_ratio=25.0,
            first_day_change=68.0, fundraising_billion=22.0, market_cap_ipo=115.0,
            eps=0.57, nav_per_share=6.1, revenue_per_share=2.1),
    IPOCase(name="某医疗器械公司L", industry="医疗器械", board="创业板",
            ipo_price=36.0, pe_ratio=48.0, pb_ratio=7.2, ps_ratio=12.0,
            first_day_change=45.0, fundraising_billion=18.0, market_cap_ipo=85.0,
            eps=0.75, nav_per_share=5.0, revenue_per_share=3.0),
    IPOCase(name="某医疗服务公司M", industry="医疗服务", board="主板",
            ipo_price=48.0, pe_ratio=55.0, pb_ratio=6.8, ps_ratio=8.5,
            first_day_change=32.0, fundraising_billion=35.0, market_cap_ipo=220.0,
            eps=0.87, nav_per_share=7.1, revenue_per_share=5.6),
]

# 行业基准（PE/PB/PS参考值）
INDUSTRY_BENCHMARKS: Dict[str, IndustryBenchmark] = {
    "半导体": IndustryBenchmark("半导体", avg_pe=65.0, avg_pb=8.5, avg_ps=18.0, median_pe=60.0, median_pb=7.5),
    "半导体设计": IndustryBenchmark("半导体设计", avg_pe=70.0, avg_pb=9.0, avg_ps=20.0, median_pe=68.0, median_pb=8.0),
    "半导体设备": IndustryBenchmark("半导体设备", avg_pe=75.0, avg_pb=10.0, avg_ps=17.0, median_pe=72.0, median_pb=9.5),
    "互联网服务": IndustryBenchmark("互联网服务", avg_pe=45.0, avg_pb=8.5, avg_ps=11.0, median_pe=42.0, median_pb=7.8),
    "云计算": IndustryBenchmark("云计算", avg_pe=65.0, avg_pb=7.0, avg_ps=15.0, median_pe=60.0, median_pb=6.5),
    "人工智能": IndustryBenchmark("人工智能", avg_pe=70.0, avg_pb=7.5, avg_ps=18.0, median_pe=65.0, median_pb=7.0),
    "电子商务": IndustryBenchmark("电子商务", avg_pe=48.0, avg_pb=10.0, avg_ps=9.0, median_pe=45.0, median_pb=9.0),
    "通信设备": IndustryBenchmark("通信设备", avg_pe=40.0, avg_pb=5.5, avg_ps=4.2, median_pe=38.0, median_pb=5.2),
    "消费电子": IndustryBenchmark("消费电子", avg_pe=35.0, avg_pb=5.0, avg_ps=3.5, median_pe=33.0, median_pb=4.8),
    "光伏新能源": IndustryBenchmark("光伏新能源", avg_pe=32.0, avg_pb=4.0, avg_ps=5.0, median_pe=30.0, median_pb=3.8),
    "生物医药": IndustryBenchmark("生物医药", avg_pe=85.0, avg_pb=8.0, avg_ps=22.0, median_pe=80.0, median_pb=7.5),
    "医疗器械": IndustryBenchmark("医疗器械", avg_pe=45.0, avg_pb=6.5, avg_ps=11.0, median_pe=42.0, median_pb=6.0),
    "医疗服务": IndustryBenchmark("医疗服务", avg_pe=50.0, avg_pb=6.0, avg_ps=8.0, median_pe=48.0, median_pb=5.5),
    "default": IndustryBenchmark("default", avg_pe=40.0, avg_pb=5.0, avg_ps=8.0, median_pe=35.0, median_pb=4.5),
}

# 板块情绪系数（影响中签率和首日表现）
BOARD_SENTIMENT: Dict[str, Dict] = {
    "科创板": {"emotion": 1.3, "base_winning_rate": 0.05, "description": "科创板市场情绪高"},
    "创业板": {"emotion": 1.15, "base_winning_rate": 0.08, "description": "创业板情绪较高"},
    "主板": {"emotion": 0.95, "base_winning_rate": 0.12, "description": "主板情绪平稳"},
    "北交所": {"emotion": 1.1, "base_winning_rate": 0.15, "description": "北交所情绪较活跃"},
}


def _parse_amount(amount_str: str) -> float:
    """解析募资金额字符串，返回元"""
    amount_str = amount_str.strip()
    # 匹配 "10亿", "5千万", "100万" 等
    patterns = [
        (r"(\d+\.?\d*)\s*亿", 1e8),
        (r"(\d+\.?\d*)\s*千万", 1e7),
        (r"(\d+\.?\d*)\s*百万", 1e6),
        (r"(\d+\.?\d*)\s*万", 1e4),
        (r"(\d+\.?\d*)", 1),
    ]
    for pattern, multiplier in patterns:
        m = re.search(pattern, amount_str)
        if m:
            return float(m.group(1)) * multiplier
    return 0.0


class IPOAnalysisEngine:
    """IPO分析引擎"""

    def __init__(self):
        self.cases = IPO_CASES
        self.benchmarks = INDUSTRY_BENCHMARKS
        self.board_sentiment = BOARD_SENTIMENT

    def _find_similar_cases(self, industry: str, board: str, limit: int = 5) -> List[IPOCase]:
        """查找同业可比公司"""
        # 先按行业匹配
        same_industry = [c for c in self.cases if c.industry == industry]
        if len(same_industry) >= limit:
            return same_industry[:limit]

        # 按board放宽匹配
        same_board = [c for c in self.cases if c.board == board and c not in same_industry]
        combined = same_industry + same_board
        return combined[:limit]

    def _estimate_financials(self, company_name: str, industry: str, board: str,
                              fundraising_amount: float) -> Dict:
        """
        基于募资额和行业估算财务数据
        发行股数 = 募资额 / 发行价(假设10-15元)
        """
        # 假设发行价在10-20元之间（不同板块有差异）
        if board == "科创板":
            assumed_price = 45.0
        elif board == "创业板":
            assumed_price = 28.0
        elif board == "主板":
            assumed_price = 22.0
        else:
            assumed_price = 15.0

        # 估算发行股数（万股）
        shares = fundraising_amount / assumed_price / 10000  # 万股

        # 基于行业估算EPS
        bench = self.benchmarks.get(industry, self.benchmarks["default"])
        avg_pe = bench.avg_pe

        # 从可比案例推断 eps
        sample_case = next((c for c in self.cases if c.industry == industry), self.cases[0])
        # 等比例调整
        ratio = (fundraising_amount / 1e8) / max(sample_case.fundraising_billion, 1)
        eps = sample_case.eps * max(0.3, min(ratio, 3.0))

        nav = sample_case.nav_per_share * max(0.5, min(ratio, 2.0))
        rev_per_share = sample_case.revenue_per_share * max(0.5, min(ratio, 2.0))

        return {
            "assumed_issue_price": assumed_price,
            "estimated_shares_million": shares,  # 万股
            "estimated_eps": round(eps, 2),
            "estimated_nav": round(nav, 2),
            "estimated_revenue_per_share": round(rev_per_share, 2),
        }

    def _calc_pe_valuation(self, financials: Dict, industry: str, board: str) -> Dict:
        """PE估值"""
        bench = self.benchmarks.get(industry, self.benchmarks["default"])
        eps = financials["estimated_eps"]

        # 考虑board的情绪加成
        board_adj = self.board_sentiment.get(board, self.board_sentiment["主板"])
        emotion = board_adj["emotion"]

        low_pe = bench.median_pe * 0.85
        mid_pe = bench.avg_pe * emotion
        high_pe = bench.avg_pe * 1.2 * emotion

        return {
            "method": "PE估值（市盈率法）",
            "formula": "发行价 = 行业PE中位数 × 预测EPS",
            "industry_avg_pe": round(bench.avg_pe, 1),
            "median_pe": round(bench.median_pe, 1),
            "emotion_adjust": emotion,
            "estimated_eps": eps,
            "low_price": round(low_pe * eps, 2),
            "mid_price": round(mid_pe * eps, 2),
            "high_price": round(high_pe * eps, 2),
        }

    def _calc_pb_valuation(self, financials: Dict, industry: str, board: str) -> Dict:
        """PB估值"""
        bench = self.benchmarks.get(industry, self.benchmarks["default"])
        nav = financials["estimated_nav"]

        low_pb = bench.median_pb * 0.9
        mid_pb = bench.avg_pb
        high_pb = bench.avg_pb * 1.3

        return {
            "method": "PB估值（市净率法）",
            "formula": "发行价 = 行业PB中位数 × 每股净资产",
            "industry_avg_pb": round(bench.avg_pb, 2),
            "median_pb": round(bench.median_pb, 2),
            "estimated_nav": nav,
            "low_price": round(low_pb * nav, 2),
            "mid_price": round(mid_pb * nav, 2),
            "high_price": round(high_pb * nav, 2),
        }

    def _calc_ps_valuation(self, financials: Dict, industry: str, board: str) -> Dict:
        """PS估值"""
        bench = self.benchmarks.get(industry, self.benchmarks["default"])
        rev = financials["estimated_revenue_per_share"]

        board_adj = self.board_sentiment.get(board, self.board_sentiment["主板"])
        emotion = board_adj["emotion"]

        low_ps = bench.avg_ps * 0.8
        mid_ps = bench.avg_ps * emotion
        high_ps = bench.avg_ps * 1.5 * emotion

        return {
            "method": "PS估值（市销率法）",
            "formula": "发行价 = 行业PS中位数 × 每股营收",
            "industry_avg_ps": round(bench.avg_ps, 2),
            "emotion_adjust": emotion,
            "estimated_revenue_per_share": rev,
            "low_price": round(low_ps * rev, 2),
            "mid_price": round(mid_ps * rev, 2),
            "high_price": round(high_ps * rev, 2),
        }

    def _calc_price_range(self, pe_val: Dict, pb_val: Dict, ps_val: Dict) -> Tuple[float, float]:
        """综合三种估值方法，给出建议定价区间"""
        # 权重：PE 45%, PB 25%, PS 30%
        low_prices = [pe_val["low_price"] * 0.45 + pb_val["low_price"] * 0.25 + ps_val["low_price"] * 0.30,
                      pe_val["low_price"] * 0.40 + pb_val["low_price"] * 0.25 + ps_val["low_price"] * 0.35,
                      pe_val["low_price"] * 0.35 + pb_val["low_price"] * 0.25 + ps_val["low_price"] * 0.40]
        high_prices = [pe_val["high_price"] * 0.45 + pb_val["high_price"] * 0.25 + ps_val["high_price"] * 0.30,
                       pe_val["high_price"] * 0.40 + pb_val["high_price"] * 0.25 + ps_val["high_price"] * 0.35,
                       pe_val["high_price"] * 0.35 + pb_val["high_price"] * 0.25 + ps_val["high_price"] * 0.40]

        # 取三个权重的平均值
        low = round(sum(low_prices) / len(low_prices), 2)
        high = round(sum(high_prices) / len(high_prices), 2)

        # 确保区间合理
        if high < low * 1.15:
            high = round(low * 1.2, 2)

        return (low, high)

    def _calc_winning_rate(self, fundraising_amount: float, board: str) -> Tuple[float, str]:
        """估算中签率"""
        # 募资额分级（亿元）
        amount_billion = fundraising_amount / 1e8

        board_cfg = self.board_sentiment.get(board, self.board_sentiment["主板"])
        emotion = board_cfg["emotion"]
        base_rate = board_cfg["base_winning_rate"]

        # 募资额越大，中签率越低（非线性）
        if amount_billion < 10:
            rate = base_rate * 3.0 * emotion
        elif amount_billion < 30:
            rate = base_rate * 1.5 * emotion
        elif amount_billion < 80:
            rate = base_rate * emotion
        elif amount_billion < 150:
            rate = base_rate * 0.6
        else:
            rate = base_rate * 0.3

        rate = max(0.005, min(rate, 0.5))  # 0.5%~50%

        note = (f"基于【{board}】市场情绪({emotion:.2f})、"
                f"募资规模({amount_billion:.1f}亿元)综合估算。 "
                f"大型IPO(>100亿)需关注战略投资者比例。")

        return round(rate * 100, 2), note

    def _predict_first_day(self, board: str, industry: str, pe_val: Dict,
                            fundraising_amount: float) -> Dict:
        """预测首日表现"""
        board_cfg = self.board_sentiment.get(board, self.board_sentiment["主板"])
        emotion = board_cfg["emotion"]
        amount_billion = fundraising_amount / 1e8

        # 找同行业案例
        same_cases = [c for c in self.cases if c.industry == industry]
        if same_cases:
            avg_first_day = sum(c.first_day_change for c in same_cases) / len(same_cases)
        else:
            avg_first_case = sum(c.first_day_change for c in self.cases) / len(self.cases)
            avg_first_day = avg_first_case

        # 情绪调整
        adjusted = avg_first_day * emotion

        # 募资额对首日涨幅有压制（超大IPO往往涨幅有限）
        if amount_billion > 100:
            dampen = 0.7
        elif amount_billion > 50:
            dampen = 0.85
        else:
            dampen = 1.0

        prediction = adjusted * dampen

        # 设置区间
        low = round(max(prediction * 0.7, 0), 1)
        high = round(prediction * 1.3, 1)
        mid = round(prediction, 1)

        return {
            "predicted_first_day_change_low": low,
            "predicted_first_day_change_mid": mid,
            "predicted_first_day_change_high": high,
            "unit": "%",
            "note": f"参考同业均值({avg_first_day:.1f}%)经板块情绪({emotion:.2f})和募资规模调整",
        }

    def _predict_long_term(self, board: str, industry: str,
                            first_day_pred: Dict) -> Dict:
        """长期表现预测"""
        board_cfg = self.board_sentiment.get(board, self.board_sentiment["主板"])
        emotion = board_cfg["emotion"]
        first_day_mid = first_day_pred["predicted_first_day_change_mid"]

        # 一年后预期（相对首日）
        if first_day_mid > 80:
            # 首日涨幅过大的，长期回调概率高
            long_term_change = first_day_mid * 0.5
        elif first_day_mid > 30:
            long_term_change = first_day_mid * 0.8
        else:
            long_term_change = first_day_mid * 1.1

        return {
            "one_year_outlook": f"预计一年后相对发行价涨幅 {long_term_change:.0f}~{long_term_change*1.5:.0f}%",
            "key_factors": [
                "关注募投项目产能释放节奏",
                "关注行业周期与竞争格局变化",
                "关注核心客户依赖与毛利率趋势",
            ],
            "risk_factors": [
                "市场情绪波动风险",
                "技术迭代风险",
                "政策监管风险",
            ]
        }

    def analyze(self, company_name: str, industry: str, board: str,
                fundraising_amount: float = None,
                fundraising_str: str = None) -> IPOAnalysisResult:
        """
        执行IPO分析

        Args:
            company_name: 公司名称（会脱敏显示为"某公司"）
            industry: 行业
            board: 上市板块（科创板/创业板/主板/北交所）
            fundraising_amount: 募资额（元），可选
            fundraising_str: 募资额字符串，如"10亿"，可选
        """
        # 解析募资额
        if fundraising_amount is None and fundraising_str:
            fundraising_amount = _parse_amount(fundraising_str)
        elif fundraising_amount is None:
            fundraising_amount = 10_000_000_000  # 默认100亿

        # 行业标准化
        industry = industry.strip()
        board = board.strip()

        # 估算财务数据
        financials = self._estimate_financials(company_name, industry, board, fundraising_amount)

        # 三种估值
        pe_val = self._calc_pe_valuation(financials, industry, board)
        pb_val = self._calc_pb_valuation(financials, industry, board)
        ps_val = self._calc_ps_valuation(financials, industry, board)

        # 综合定价区间
        price_low, price_high = self._calc_price_range(pe_val, pb_val, ps_val)
        mid_price = round((price_low + price_high) / 2, 2)

        # 同业对比
        peers = []
        similar_cases = self._find_similar_cases(industry, board, limit=5)
        for c in similar_cases:
            peers.append({
                "name": c.name,
                "industry": c.industry,
                "board": c.board,
                "issue_price": c.ipo_price,
                "pe": c.pe_ratio,
                "pb": c.pb_ratio,
                "ps": c.ps_ratio,
                "first_day_change": c.first_day_change,
                "fundraising_billion": c.fundraising_billion,
            })

        # 中签率
        winning_rate, winning_note = self._calc_winning_rate(fundraising_amount, board)

        # 首日预测
        first_day_pred = self._predict_first_day(board, industry, pe_val, fundraising_amount)

        # 长期预测
        long_term = self._predict_long_term(board, industry, first_day_pred)

        return IPOAnalysisResult(
            company_name=f"某公司（{company_name}）",  # 脱敏
            industry=industry,
            board=board,
            fundraising_amount=fundraising_amount,
            pe_valuation=pe_val,
            pb_valuation=pb_val,
            ps_valuation=ps_val,
            price_range=(price_low, price_high),
            mid_price=mid_price,
            peers=peers,
            winning_rate=winning_rate,
            winning_rate_note=winning_note,
            first_day_prediction=first_day_pred,
            long_term_outlook=long_term,
        )

    def format_report(self, result: IPOAnalysisResult) -> str:
        """格式化输出分析报告"""
        amount_billion = result.fundraising_amount / 1e8

        lines = [
            "=" * 60,
            f"📋 IPO分析报告",
            "=" * 60,
            f"",
            f"【公司信息】",
            f"  公司名称：{result.company_name}",
            f"  所属行业：{result.industry}",
            f"  上市板块：{result.board}",
            f"  预计募资：{amount_billion:.1f}亿元",
            f"",
            f"{'=' * 60}",
            f"【三种估值分析】",
            f"",
            f"1️⃣ PE估值（市盈率法）",
            f"   行业平均PE：{result.pe_valuation['industry_avg_pe']}",
            f"   预测EPS：{result.pe_valuation['estimated_eps']}元",
            f"   情绪调整系数：{result.pe_valuation['emotion_adjust']:.2f}",
            f"   ▶ 估值区间：{result.pe_valuation['low_price']} ~ {result.pe_valuation['high_price']} 元",
            f"   ▶ 中位估值：{result.pe_valuation['mid_price']} 元",
            f"",
            f"2️⃣ PB估值（市净率法）",
            f"   行业平均PB：{result.pb_valuation['industry_avg_pb']}",
            f"   每股净资产：{result.pb_valuation['estimated_nav']}元",
            f"   ▶ 估值区间：{result.pb_valuation['low_price']} ~ {result.pb_valuation['high_price']} 元",
            f"   ▶ 中位估值：{result.pb_valuation['mid_price']} 元",
            f"",
            f"3️⃣ PS估值（市销率法）",
            f"   行业平均PS：{result.ps_valuation['industry_avg_ps']}",
            f"   每股营收：{result.ps_valuation['estimated_revenue_per_share']}元",
            f"   情绪调整系数：{result.ps_valuation['emotion_adjust']:.2f}",
            f"   ▶ 估值区间：{result.ps_valuation['low_price']} ~ {result.ps_valuation['high_price']} 元",
            f"   ▶ 中位估值：{result.ps_valuation['mid_price']} 元",
            f"",
            f"{'=' * 60}",
            f"【综合定价建议】",
            f"   ★ 建议发行价区间：{result.price_range[0]} ~ {result.price_range[1]} 元",
            f"   ★ 中位建议价格：{result.mid_price} 元",
            f"",
            f"{'=' * 60}",
            f"【同业可比公司对比】",
            f"",
        ]

        for i, p in enumerate(result.peers, 1):
            lines.append(
                f"   {i}. {p['name']} | PE={p['pe']} PB={p['pb']} PS={p['ps']} "
                f"| 首日涨幅={p['first_day_change']}% | 募资{p['fundraising_billion']}亿"
            )

        lines.extend([
            f"",
            f"{'=' * 60}",
            f"【中签率估算】",
            f"   🎯 估算中签率：{result.winning_rate}%",
            f"   📝 {result.winning_rate_note}",
            f"",
            f"{'=' * 60}",
            f"【上市后表现预测】",
            f"",
            f"   📈 首日涨幅预测",
            f"   ▶ 预测区间：{result.first_day_prediction['predicted_first_day_change_low']}% ~ "
            f"{result.first_day_prediction['predicted_first_day_change_high']}%",
            f"   ▶ 中位预测：{result.first_day_prediction['predicted_first_day_change_mid']}%",
            f"   📝 {result.first_day_prediction['note']}",
            f"",
            f"   📊 一年期展望",
            f"   ▶ {result.long_term_outlook['one_year_outlook']}",
            f"",
        ])

        lines.append("   ⚠️ 关键风险因素：")
        for r in result.long_term_outlook['risk_factors']:
            lines.append(f"      - {r}")

        lines.extend([
            f"",
            "=" * 60,
            f"【免责声明】本报告仅供参考，不构成投资建议。",
            "=" * 60,
        ])

        return "\n".join(lines)
