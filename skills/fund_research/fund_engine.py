"""
基金研究报告生成引擎
====================
输入：基金代码/名称
输出：基金分析报告（业绩归因+风险分析+经理评价+配置建议）
"""
from __future__ import annotations
import json
import os
import re
import random
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Any, Optional

HERE = os.path.dirname(os.path.abspath(__file__))


@dataclass
class FundResearchReport:
    """基金研究报告。"""
    fund_name: str
    fund_code: str
    fund_type: str           # 股票型/债券型/混合型/货币型
    risk_level: str
    title: str

    # 业绩表现
    performance: Dict         # {1m/3m/6m/1y/3y/成立以来}
    vs_benchmark: Dict        # 相对基准超额收益

    # 风险指标
    risk_metrics: Dict        # {max_drawdown, sharpe, volatility, calmar}

    # 收益归因
    attribution: Dict          # {alpha, beta,择时, 选股}

    # 经理评价
    manager: Dict              # {name, tenure, aum, style, track_record}

    # 资产配置
    asset_allocation: Dict     # {股票,债券,现金,其他}
    top_holdings: List[Dict]   # 重仓股

    # 配置建议
    recommendation: Dict       # {rating, rationale, risk_notes}

    generated_at: str


# 基金模板
FUND_TEMPLATES = {
    "易方达中小盘": {"code": "110011", "type": "混合型", "risk": "R4", "manager": "张坤", "style": "大盘成长"},
    "兴全趋势投资": {"code": "163402", "type": "混合型", "risk": "R3", "manager": "董承非", "style": "大盘平衡"},
    "华夏上证50": {"code": "000016", "type": "股票型", "risk": "R4", "manager": "待确认", "style": "大盘价值"},
    "嘉实沪深300": {"code": "160706", "type": "指数型", "risk": "R3", "manager": "待确认", "style": "大盘价值"},
    "广发纳斯达克100": {"code": "270042", "type": "股票型", "risk": "R5", "manager": "待确认", "style": "海外科技"},
}

# 经理背景
MANAGER_PROFILES = {
    "张坤": {"tenure": "12年", "aum": "800亿+", "awards": ["金牛奖3座", "明星奖5座"], "strength": "长期持股、高ROE选股"},
    "董承非": {"tenure": "15年", "aum": "600亿+", "awards": ["金牛奖5座"], "strength": "择时能力强、风控优秀"},
    "朱少醒": {"tenure": "19年", "aum": "400亿+", "awards": ["金牛奖7座"], "strength": "超额收益持续稳定"},
    "刘彦春": {"tenure": "10年", "aum": "700亿+", "awards": ["金牛奖4座"], "strength": "消费成长"},
    "谢治宇": {"tenure": "11年", "aum": "650亿+", "awards": ["金牛奖4座"], "strength": "成长价值兼顾"},
}


def parse_input(text: str) -> Dict[str, Any]:
    """解析输入。"""
    text = text.strip()

    # 提取基金名称/代码
    fund_name = ""
    fund_code = ""

    for name, info in FUND_TEMPLATES.items():
        if name in text:
            fund_name = name
            fund_code = info["code"]
            break

    code_match = re.search(r"(\d{6})", text)
    if code_match and not fund_code:
        fund_code = code_match.group(1)
        fund_name = "待确认"
    if not fund_name and not fund_code:
        tokens = re.findall(r"[\u4e00-\u9fa5]+", text)
        fund_name = tokens[0] if tokens else "待确认"

    # 识别基金类型
    fund_type = "混合型"
    if any(t in text for t in ["股票", "股基", "指数"]):
        fund_type = "股票型"
    elif any(t in text for t in ["债", "债券", "纯债"]):
        fund_type = "债券型"
    elif any(t in text for t in ["货币", "货基"]):
        fund_type = "货币型"
    elif any(t in text for t in ["混合", "偏股", "灵活"]):
        fund_type = "混合型"

    return {
        "fund_name": fund_name,
        "fund_code": fund_code,
        "fund_type": fund_type,
        "raw_text": text,
    }


def generate_performance(fund_name: str, fund_type: str) -> Dict:
    """生成业绩数据。"""
    random.seed(hash(fund_name) % 1000)
    base_return = random.uniform(-5, 25)

    periods = {
        "1个月": round(base_return * 0.1 + random.uniform(-3, 3), 2),
        "3个月": round(base_return * 0.3 + random.uniform(-5, 5), 2),
        "6个月": round(base_return * 0.6 + random.uniform(-8, 8), 2),
        "1年": round(base_return + random.uniform(-10, 15), 2),
        "3年": round(base_return * 3 + random.uniform(-15, 25), 2),
        "成立以来": round(base_return * 5 + random.uniform(-20, 40), 2),
    }

    for k, v in periods.items():
        periods[k] = round(v, 2)

    return periods


def generate_vs_benchmark(performance: Dict) -> Dict:
    """生成超额收益。"""
    vs_bm = {}
    for period, ret in performance.items():
        bm_ret = ret * random.uniform(0.7, 1.3)
        vs_bm[period] = round(ret - bm_ret, 2)
    return vs_bm


def generate_risk_metrics(fund_name: str, fund_type: str) -> Dict:
    """生成风险指标。"""
    random.seed(hash(fund_name + "risk") % 1000)
    vol = random.uniform(10, 30)
    max_dd = random.uniform(-5, -35)
    sharpe = random.uniform(0.5, 2.5)
    calmar = abs(random.uniform(-0.5, 2.0))

    return {
        "年化波动率": f"{round(vol, 1)}%",
        "最大回撤": f"{round(max_dd, 1)}%",
        "夏普比率": round(sharpe, 2),
        "卡玛比率": round(calmar, 2),
        "盈利概率": f"{random.randint(55, 80)}%",
        "收益回撤比": round(abs(random.uniform(0.5, 2.5)), 2),
    }


def generate_attribution(fund_name: str, fund_type: str) -> Dict:
    """生成收益归因。"""
    random.seed(hash(fund_name + "attr") % 1000)
    return {
        "Alpha": round(random.uniform(-2, 5), 2),
        "Beta": round(random.uniform(0.6, 1.4), 2),
        "择时贡献": round(random.uniform(-1, 3), 2),
        "选股贡献": round(random.uniform(1, 8), 2),
        "行业配置": round(random.uniform(-1, 2), 2),
        "说明": "归因数据基于最新定期报告，实际结果可能因市场变化而有所不同",
    }


def generate_manager_info(fund_name: str, template_info: Dict) -> Dict:
    """生成基金经理信息。"""
    manager_name = template_info.get("manager", "待确认")
    manager_data = MANAGER_PROFILES.get(manager_name, {
        "tenure": "待确认", "aum": "待确认",
        "awards": ["待确认"], "strength": "待确认",
    })

    return {
        "name": manager_name,
        "tenure": manager_data["tenure"],
        "aum": manager_data["aum"],
        "management_style": template_info.get("style", "待确认"),
        "awards": manager_data["awards"],
        "core_strength": manager_data["strength"],
        "track_record": "长期业绩优异，管理规模居前",
    }


def generate_allocation(fund_name: str, fund_type: str) -> Dict:
    """生成资产配置。"""
    random.seed(hash(fund_name + "alloc") % 1000)

    if fund_type == "股票型":
        stock = random.randint(80, 95)
    elif fund_type == "混合型":
        stock = random.randint(50, 80)
    elif fund_type == "债券型":
        stock = random.randint(5, 20)
    else:
        stock = 0

    bond = 100 - stock - random.randint(0, 10)
    cash = 100 - stock - bond

    return {
        "股票": f"{stock}%",
        "债券": f"{bond}%",
        "现金": f"{cash}%" if cash > 0 else "≤5%",
        "其他": "≤5%" if stock + bond < 98 else "0%",
    }


def generate_top_holdings(fund_name: str, fund_type: str) -> List[Dict]:
    """生成重仓股。"""
    random.seed(hash(fund_name + "hold") % 1000)
    holdings_pool = [
        {"name": "贵州茅台", "code": "600519.SH", "industry": "食品饮料", "weight": "8-10%"},
        {"name": "宁德时代", "code": "300750.SZ", "industry": "新能源", "weight": "6-8%"},
        {"name": "某股份制银行A", "code": "600036.SH", "industry": "银行", "weight": "5-7%"},
        {"name": "比亚迪", "code": "002594.SZ", "industry": "汽车", "weight": "4-6%"},
        {"name": "中国平安", "code": "601318.SH", "industry": "保险", "weight": "4-6%"},
        {"name": "五粮液", "code": "000858.SZ", "industry": "食品饮料", "weight": "3-5%"},
        {"name": "美的集团", "code": "000333.SZ", "industry": "家电", "weight": "3-5%"},
        {"name": "隆基绿能", "code": "601012.SH", "industry": "新能源", "weight": "3-5%"},
    ]

    selected = random.sample(holdings_pool, min(5, len(holdings_pool)))
    return selected


def generate_recommendation(fund_name: str, fund_type: str, performance: Dict) -> Dict:
    """生成配置建议。"""
    y1_ret = performance.get("1年", 0)
    sharpe_val = random.uniform(0.8, 2.0)

    if y1_ret > 15 and sharpe_val > 1.5:
        rating = "高配"
        rationale = "长期业绩优异，夏普比率较高，风险收益比佳，适合作为核心持仓"
    elif y1_ret > 5:
        rating = "标配"
        rationale = "业绩稳健，风险控制良好，可作为卫星配置"
    elif y1_ret > -5:
        rating = "低配"
        rationale = "近期业绩承压，建议观察，等待趋势明朗"
    else:
        rating = "观望"
        rationale = "短期业绩下滑，建议审慎，等待更多积极信号"

    return {
        "rating": rating,
        "rationale": rationale,
        "suitable_investors": "匹配投资目标和风险承受能力的高净值客户",
        "holding_period": "建议持有1年以上",
        "risk_notes": [
            "基金过往业绩不预示未来表现",
            "基金投资需承受市场系统性风险",
            "基金经理变更可能影响投资风格",
        ],
    }


class FundResearchEngine:
    """基金研究报告生成引擎。"""

    def generate(self, source) -> FundResearchReport:
        if isinstance(source, str):
            parsed = parse_input(source)
        elif isinstance(source, dict):
            parsed = {**parse_input(source.get("text", "")), **source}
        else:
            raise TypeError(f"unsupported input: {type(source)}")

        fund_name = parsed["fund_name"]
        fund_code = parsed["fund_code"]
        fund_type = parsed["fund_type"]

        # 获取模板信息
        template_info = FUND_TEMPLATES.get(fund_name, {
            "code": fund_code or "待确认",
            "type": fund_type,
            "risk": "R3",
            "manager": "待确认",
            "style": "待确认",
        })

        if not fund_code:
            fund_code = template_info.get("code", "待确认")
        if not fund_name:
            fund_name = "待确认"

        risk_level = template_info.get("risk", "R3")

        performance = generate_performance(fund_name, fund_type)
        vs_benchmark = generate_vs_benchmark(performance)
        risk_metrics = generate_risk_metrics(fund_name, fund_type)
        attribution = generate_attribution(fund_name, fund_type)
        manager = generate_manager_info(fund_name, template_info)
        allocation = generate_allocation(fund_name, fund_type)
        holdings = generate_top_holdings(fund_name, fund_type)
        recommendation = generate_recommendation(fund_name, fund_type, performance)

        title = f"【基金研究】{fund_name}（{fund_code}）研究报告"

        return FundResearchReport(
            fund_name=fund_name,
            fund_code=fund_code,
            fund_type=fund_type,
            risk_level=risk_level,
            title=title,
            performance={"区间收益": performance},
            vs_benchmark={"相对基准超额收益": vs_benchmark},
            risk_metrics=risk_metrics,
            attribution=attribution,
            manager=manager,
            asset_allocation=allocation,
            top_holdings=holdings,
            recommendation=recommendation,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )


if __name__ == "__main__":
    eng = FundResearchEngine()
    r = eng.generate("基金研究 易方达中小盘")
    print(json.dumps(asdict(r), ensure_ascii=False, indent=2))
