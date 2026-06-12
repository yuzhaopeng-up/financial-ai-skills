"""
市场观点输出引擎
================
输入：市场数据/新闻/行情描述
输出：日报/周报（大盘综述+行业+热点+资金+展望）
"""
from __future__ import annotations
import json
import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

HERE = os.path.dirname(os.path.abspath(__file__))


@dataclass
class MarketViewReport:
    """市场观点报告。"""
    report_type: str           # 日报/周报
    title: str
    date_range: str            # 日期范围
    index_performance: List[Dict]  # 指数表现
    sector_performance: List[Dict]  # 行业表现
    hot_themes: List[Dict]     # 热点主题 {theme,龙头,逻辑}
    money_flow: Dict           # 资金流向
    macro_view: str           # 宏观视角
    outlook: Dict              # 展望 {short_term, medium_term, key_notes}
    risks: List[str]           # 风险提示
    generated_at: str


# 指数基准数据
INDEX_DATA = {
    "沪深300": {"code": "000300.SH", "base": 3500, "weight": "大盘蓝筹"},
    "上证指数": {"code": "000001.SH", "base": 3100, "weight": "综合"},
    "创业板指": {"code": "399006.SZ", "base": 1800, "weight": "成长"},
    "科创50": {"code": "000688.SH", "base": 700, "weight": "科技"},
    "恒生指数": {"code": "HSI.HK", "base": 18000, "weight": "港股大盘"},
    "纳斯达克": {"code": "IXIC", "base": 14000, "weight": "美股科技"},
}

# 行业驱动逻辑
SECTOR_DRIVERS = {
    "银行": {"logic": "利率下行压制息差，但资产质量改善", "performance": "分化"},
    "证券": {"logic": "资本市场改革红利，交投活跃度提升", "performance": "跑赢"},
    "白酒": {"logic": "商务消费回暖，龙头量价齐升", "performance": "稳健"},
    "新能源": {"logic": "全球能源转型加速，渗透率持续提升", "performance": "分化"},
    "半导体": {"logic": "国产替代加速，AI驱动算力需求", "performance": "跑赢"},
    "医药": {"logic": "创新药出海，政策边际改善", "performance": "修复"},
    "房地产": {"logic": "销售降幅收窄，政策支持加码", "performance": "筑底"},
    "煤炭": {"logic": "煤价回落，火电盈利改善", "performance": "中性"},
    "钢铁": {"logic": "需求疲软，供给侧改革托底", "performance": "中性"},
    "汽车": {"logic": "价格战延续，出口成为亮点", "performance": "分化"},
    "军工": {"logic": "装备采购加速，国际局势催化", "performance": "超额"},
    "计算机": {"logic": "AI应用落地，信创订单释放", "performance": "超额"},
    "通信": {"logic": "运营商资本开支扩张，AI算力带动", "performance": "超额"},
    "消费": {"logic": "居民消费意愿回升，内需政策加码", "performance": "稳健"},
    "农林牧渔": {"logic": "猪周期筑底，种业振兴政策", "performance": "中性"},
}


def parse_market_input(text: str) -> Dict[str, Any]:
    """解析输入，识别市场类型和时间范围。"""
    text = text.strip()

    # 识别日报/周报
    report_type = "日报"
    if any(w in text for w in ["周报", "本周", "周度", "weekly"]):
        report_type = "周报"

    # 识别市场
    markets = []
    if any(w in text for w in ["A股", "A股", "沪市", "沪深", "上证", "创业板"]):
        markets.extend(["沪深300", "上证指数", "创业板指"])
    if any(w in text for w in ["港股", "恒生", "香港"]):
        markets.append("恒生指数")
    if any(w in text for w in ["美股", "纳斯达克", "标普", "华尔街"]):
        markets.append("纳斯达克")
    if not markets:
        markets = ["沪深300", "上证指数"]

    # 提取日期
    today = datetime.now()
    if "今天" in text or "今日" in text:
        date_range = today.strftime("%Y-%m-%d")
    elif "昨天" in text or "昨日" in text:
        date_range = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    elif "本周" in text:
        weekday = today.weekday()
        start = today - timedelta(days=weekday)
        date_range = f"{start.strftime('%Y-%m-%d')}至{today.strftime('%Y-%m-%d')}"
    elif "上周" in text:
        weekday = today.weekday()
        start = today - timedelta(days=weekday + 7)
        end = start + timedelta(days=6)
        date_range = f"{start.strftime('%Y-%m-%d')}至{end.strftime('%Y-%m-%d')}"
    else:
        date_range = today.strftime("%Y-%m-%d")

    # 提取涨跌信息
    up_pattern = re.findall(r"涨[\d\.]+%?", text)
    down_pattern = re.findall(r"跌[\d\.]+%?", text)

    return {
        "report_type": report_type,
        "markets": markets,
        "date_range": date_range,
        "raw_text": text,
    }


def generate_index_performance(markets: List[str], report_type: str) -> List[Dict]:
    """生成指数表现数据（模拟）。"""
    import random
    result = []
    for idx_name in markets:
        idx_info = INDEX_DATA.get(idx_name, {"base": 3000, "weight": "综合"})
        change = random.uniform(-2.5, 3.5)
        result.append({
            "index": idx_name,
            "code": idx_info["code"],
            "change_pct": round(change, 2),
            "volume": f"{random.randint(200, 500)}亿",
            "comment": "放量" if abs(change) > 1.5 else "缩量",
            "type": idx_info["weight"],
        })
    return result


def generate_sector_performance(report_type: str) -> List[Dict]:
    """生成行业表现。"""
    sectors = []
    for sector, info in SECTOR_DRIVERS.items():
        import random
        change = random.uniform(-3, 4)
        if info["performance"] == "跑赢":
            change = random.uniform(1, 4)
        elif info["performance"] == "超额":
            change = random.uniform(2, 5)
        elif info["performance"] == "中性":
            change = random.uniform(-1.5, 1.5)
        elif info["performance"] == "分化":
            change = random.uniform(-2, 3)
        sectors.append({
            "sector": sector,
            "change_pct": round(change, 2),
            "driver_logic": info["logic"],
            "outlook": info["performance"],
        })
    sectors.sort(key=lambda x: x["change_pct"], reverse=True)
    return sectors


def generate_hot_themes() -> List[Dict]:
    """生成热点主题。"""
    themes_pool = [
        {"theme": "AI应用", "leaders": ["科大讯飞", "金山办公", "昆仑万维"], "logic": "大模型落地加速，C端付费场景涌现"},
        {"theme": "新质生产力", "leaders": ["工业富联", "中科曙光", "寒武纪"], "logic": "政策加码科技自立自强"},
        {"theme": "出海2.0", "leaders": ["比亚迪", "宁德时代", "TCL"], "logic": "新能源产业链全球扩张"},
        {"theme": "消费复苏", "leaders": ["贵州茅台", "五粮液", "中国中免"], "logic": "居民消费信心边际改善"},
        {"theme": "低空经济", "leaders": ["万丰奥威", "莱斯信息", "小鹏汇天"], "logic": "政策催化+产业资本布局"},
        {"theme": "数据要素", "leaders": ["每日互动", "山大地纬", "久远银海"], "logic": "数据资产入表政策落地"},
    ]
    import random
    selected = random.sample(themes_pool, min(4, len(themes_pool)))
    return selected


def generate_money_flow(report_type: str) -> Dict:
    """生成资金流向。"""
    import random
    directions = ["净流入", "净流出"]
    north = random.choice(directions)
    south = random.choice(directions)
    return {
        "north_bound": {"direction": north, "amount": f"{random.randint(20, 200)}亿", "comment": "北向资金"},
        "south_bound": {"direction": south, "amount": f"{random.randint(10, 100)}亿", "comment": "南向资金"},
        "main_fund": {"direction": random.choice(directions), "amount": f"{random.randint(100, 500)}亿", "comment": "主力资金"},
        "retail": {"direction": random.choice(directions), "amount": f"{random.randint(50, 300)}亿", "comment": "散户资金"},
    }


class MarketViewEngine:
    """市场观点输出引擎。"""

    def generate(self, source) -> MarketViewReport:
        if isinstance(source, str):
            parsed = parse_market_input(source)
        elif isinstance(source, dict):
            parsed = {**parse_market_input(source.get("text", "")), **source}
        else:
            raise TypeError(f"unsupported input: {type(source)}")

        report_type = parsed["report_type"]
        markets = parsed["markets"]
        date_range = parsed["date_range"]

        title = f"{date_range} {report_type}市场观点"
        if "周报" in report_type:
            title = f"【周报】{date_range} 市场综述与观点"

        return MarketViewReport(
            report_type=report_type,
            title=title,
            date_range=date_range,
            index_performance=generate_index_performance(markets, report_type),
            sector_performance=generate_sector_performance(report_type),
            hot_themes=generate_hot_themes(),
            money_flow=generate_money_flow(report_type),
            macro_view=self._build_macro_view(),
            outlook=self._build_outlook(),
            risks=self._build_risks(),
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

    def _build_macro_view(self) -> str:
        return (
            "国内：货币政策维持稳健，财政政策加力提效，制造业PMI企稳回升，消费温和修复。"
            "海外：美联储降息预期反复，美债利率高位震荡；地缘风险扰动全球风险偏好。"
        )

    def _build_outlook(self) -> Dict:
        return {
            "short_term": "市场延续震荡格局，政策预期与基本面修复交织，AI+出海主线清晰",
            "medium_term": "企业中报业绩披露期，关注盈利超预期方向；国内政策红利持续释放",
            "key_notes": [
                "1. 密切跟踪7月重要会议政策信号",
                "2. 关注AI应用端商业化进展",
                "3. 警惕海外流动性预期波动",
            ],
        }

    def _build_risks(self) -> List[str]:
        return [
            "海外美联储鹰派超预期，美债利率再度上行",
            "地缘政治风险扰动全球避险情绪",
            "国内政策出台节奏低于预期",
            "部分行业中报业绩不及预期",
        ]


if __name__ == "__main__":
    eng = MarketViewEngine()
    r = eng.generate("市场日报 今天A股收盘情况")
    print(json.dumps(asdict(r), ensure_ascii=False, indent=2))
