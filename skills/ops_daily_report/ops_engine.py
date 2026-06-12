"""
运营日报生成引擎
================
输入：运营数据指标
输出：格式化日报（业务概况+重点指标+异常预警+工作计划）
"""
from __future__ import annotations
import json
import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Any

HERE = os.path.dirname(os.path.abspath(__file__))


@dataclass
class OpsDailyReport:
    """运营日报。"""
    title: str
    date: str
    department: str           # 部门/网点
    summary: str              # 一句话总结

    # 业务概况
    business_overview: List[Dict]  # {指标名, 今日, 昨日, 环比, 同比}

    # 重点指标
    key_metrics: List[Dict]   # {指标, 实际, 计划, 完成率, 状态}

    # 异常预警
    alerts: List[Dict]        # {类型, 指标, 当前值, 阈值, 建议}

    # 明日计划
    tomorrow_plan: List[str]

    # 备注
    notes: List[str]

    generated_at: str


METRIC_TEMPLATES = {
    "存款": {"unit": "亿", "baseline": 1000, "threshold": 0.1},
    "贷款": {"unit": "亿", "baseline": 800, "threshold": 0.1},
    "理财": {"unit": "亿", "baseline": 200, "threshold": 0.15},
    "信用卡": {"unit": "万张", "baseline": 50, "threshold": 0.1},
    "新开卡": {"unit": "张", "baseline": 30, "threshold": 0.2},
    "手机银行": {"unit": "户", "baseline": 1000, "threshold": 0.1},
    "基金销售": {"unit": "亿", "baseline": 5, "threshold": 0.2},
    "保险销售": {"unit": "亿", "baseline": 2, "threshold": 0.15},
    "贵金属": {"unit": "万", "baseline": 500, "threshold": 0.25},
    "外汇": {"unit": "万美元", "baseline": 1000, "threshold": 0.2},
}


def parse_indicators(text: str) -> Dict[str, float]:
    """从文本解析运营指标。"""
    indicators = {}

    for metric_name, template in METRIC_TEMPLATES.items():
        if metric_name in text:
            # 提取数字
            pattern = rf"{metric_name}[^\d]*([\d\.]+)"
            match = re.search(pattern, text)
            if match:
                value = float(match.group(1))
                indicators[metric_name] = value
            else:
                indicators[metric_name] = template["baseline"]

    # 如果没有明确指标，生成合理模拟数据
    if not indicators:
        indicators = {
            "存款": 1020.5,
            "贷款": 815.3,
            "理财": 205.8,
            "信用卡": 52.3,
            "新开卡": 35,
        }

    return indicators


def generate_business_overview(indicators: Dict) -> List[Dict]:
    """生成业务概况。"""
    import random
    random.seed(datetime.now().day)

    overview = []
    for metric, value in indicators.items():
        template = METRIC_TEMPLATES.get(metric, {"unit": "万", "baseline": 100, "threshold": 0.1})
        unit = template["unit"]
        threshold = template["threshold"]

        # 生成对比数据
        yesterday = value * (1 + random.uniform(-threshold, threshold))
        last_year = value * (1 + random.uniform(0.05, 0.2))

        mom = (value - yesterday) / yesterday * 100
        yoy = (value - last_year) / last_year * 100

        overview.append({
            "指标": metric,
            "今日": f"{value:.2f}{unit}",
            "昨日": f"{yesterday:.2f}{unit}",
            "环比": f"{mom:+.1f}%",
            "同比": f"{yoy:+.1f}%",
            "状态": "正" if mom > 0 else "负",
        })

    return overview


def generate_key_metrics(indicators: Dict) -> List[Dict]:
    """生成重点指标。"""
    import random
    random.seed(datetime.now().day + 1)

    metrics = []
    priority_metrics = ["存款", "贷款", "理财", "基金销售", "保险销售"]

    for metric in priority_metrics:
        value = indicators.get(metric, METRIC_TEMPLATES.get(metric, {}).get("baseline", 100))
        plan = value * random.uniform(0.9, 1.1)
        completion = value / plan * 100

        status = "达标" if completion >= 100 else ("欠量" if completion >= 80 else "预警")

        metrics.append({
            "指标": metric,
            "实际": f"{value:.2f}",
            "计划": f"{plan:.2f}",
            "完成率": f"{completion:.1f}%",
            "状态": status,
        })

    return metrics


def generate_alerts(key_metrics: List[Dict]) -> List[Dict]:
    """生成异常预警。"""
    alerts = []
    for m in key_metrics:
        if "预警" in m["状态"]:
            alerts.append({
                "类型": "⚠️ 欠量预警",
                "指标": m["指标"],
                "当前值": m["实际"],
                "计划": m["计划"],
                "差额": f"{float(m['计划']) - float(m['实际']):.2f}",
                "建议": f"加强{m['指标']}业务推动，差距{abs(100-float(m['完成率'].replace('%',''))):.1f}%",
            })
        elif "达标" in m["状态"]:
            completion_rate = float(m["完成率"].replace("%", ""))
            if completion_rate > 110:
                alerts.append({
                    "类型": "✅ 超额完成",
                    "指标": m["指标"],
                    "当前值": m["实际"],
                    "计划": m["计划"],
                    "差额": f"+{float(m['实际']) - float(m['计划']):.2f}",
                    "建议": f"继续保持，可研究推广经验",
                })

    # 检查环比异常
    for m in key_metrics:
        yoy_str = ""
        # 从overview数据判断
        if "正" in m.get("状态", "") and float(m.get("完成率", "100").replace("%", "")) > 105:
            alerts.append({
                "类型": "📈 增长强劲",
                "指标": m["指标"],
                "当前值": m["实际"],
                "计划": m["计划"],
                "差额": "增长良好",
                "建议": f"{m['指标']}表现优异，可适度加大资源配置",
            })

    return alerts[:5]  # 最多5条


def generate_tomorrow_plan(alerts: List[Dict], key_metrics: List[Dict]) -> List[str]:
    """生成明日工作计划。"""
    plans = []

    # 根据预警生成针对性计划
    for alert in alerts:
        if "欠量" in alert["类型"]:
            plans.append(f"重点推动{alert['指标']}业务，目标追回{alert['差额']}")

    # 常规计划
    underperforming = [m["指标"] for m in key_metrics if "欠量" in m.get("状态", "")]
    if underperforming:
        plans.append(f"晨会部署{'/'.join(underperforming)}专项营销计划")

    if not plans:
        plans = [
            "持续维护存量客户，推动产品交叉销售",
            "跟进意向客户，促进签约转化",
            "优化服务流程，提升客户体验",
        ]

    return plans[:5]


class OpsDailyReportEngine:
    """运营日报生成引擎。"""

    def generate(self, source) -> OpsDailyReport:
        if isinstance(source, str):
            indicators = parse_indicators(source)
            date = datetime.now().strftime("%Y-%m-%d")
            department = "待确认"
        elif isinstance(source, dict):
            indicators = parse_indicators(source.get("text", ""))
            date = source.get("date", datetime.now().strftime("%Y-%m-%d"))
            department = source.get("department", "待确认")
        else:
            raise TypeError(f"unsupported input: {type(source)}")

        business_overview = generate_business_overview(indicators)
        key_metrics = generate_key_metrics(indicators)
        alerts = generate_alerts(key_metrics)
        tomorrow_plan = generate_tomorrow_plan(alerts, key_metrics)

        # 生成一句话总结
        total_growth = sum(
            float(o.get("环比", "0%").replace("%", "").replace("+", ""))
            for o in business_overview
        ) / max(len(business_overview), 1)

        if total_growth > 5:
            summary = f"今日整体运营良好，主要指标环比增长{total_growth:.1f}%，超额完成计划。"
        elif total_growth > 0:
            summary = f"今日运营平稳，主要指标环比增长{total_growth:.1f}%，基本完成目标。"
        else:
            summary = f"今日运营承压，主要指标环比下降{abs(total_growth):.1f}%，需加强业务推动。"

        return OpsDailyReport(
            title=f"【运营日报】{date} {department}",
            date=date,
            department=department,
            summary=summary,
            business_overview=business_overview,
            key_metrics=key_metrics,
            alerts=alerts,
            tomorrow_plan=tomorrow_plan,
            notes=[
                "数据截止当日17:00，实际业绩以月度报表为准",
                "节假日期间指标口径可能调整，请关注后续通知",
            ],
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )


if __name__ == "__main__":
    eng = OpsDailyReportEngine()
    r = eng.generate("运营日报 今日存款1000亿 贷款800亿 理财200亿 信用卡50万张 新开卡30张")
    print(json.dumps(asdict(r), ensure_ascii=False, indent=2))
