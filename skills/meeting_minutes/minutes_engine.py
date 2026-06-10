"""
调研纪要生成引擎
================
输入：调研录音/会议记录文字
输出：结构化纪要（参会人+议题+要点+待办+风险）
"""
from __future__ import annotations
import json
import os
import re
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Dict, List, Optional, Any

HERE = os.path.dirname(os.path.abspath(__file__))


@dataclass
class Attendee:
    name: str
    title: str = ""
    company: str = ""


@dataclass
class MeetingMinutes:
    """调研纪要。"""
    title: str
    meeting_type: str          # 实地调研/电话会议/交流会
    attendees: List[Dict]      # 参会人
    company: str               # 调研公司
    date: str
    core_topics: List[str]     # 核心议题
    key_points: List[Dict]     # 关键要点 {speaker, content, sentiment}
    data_mentioned: List[Dict]  # 提及数据 {value, context, source}
    action_items: List[Dict]   # 待办事项 {item, owner, deadline}
    risks: List[str]           # 风险提示
    summary: str               # 3句话摘要
    generated_at: str


def parse_input(text: str) -> Dict[str, Any]:
    """解析输入文本，提取关键信息。"""
    text = text.strip()

    # 识别会议类型
    meeting_types = ["实地调研", "电话会议", "视频会议", "交流会", "业绩发布会", "投资者交流"]
    meeting_type = "交流会"
    for mt in meeting_types:
        if mt in text:
            meeting_type = mt
            break

    # 提取公司名（已知公司列表）
    known_companies = {
        "宁德时代": "300750.SZ", "比亚迪": "002594.SZ",
        "招商银行": "600036.SH", "贵州茅台": "600519.SH",
        "中国平安": "601318.SH", "工商银行": "601398.SH",
        "建设银行": "601939.SH", "农业银行": "601288.SH",
        "中国银行": "601988.SH", "兴业银行": "601166.SH",
    }
    company = ""
    company_code = ""
    for c, code in known_companies.items():
        if c in text:
            company = c
            company_code = code
            break

    # 提取参会人（简单规则：姓名后跟职位/公司）
    attendee_pattern = re.findall(r"([A-Za-z·]+|[\u4e00-\u9fa5]{2,4})(?:总|总|经理|总|董事|总|总|总)", text)
    attendees = []
    for name in set(attendee_pattern):
        if len(name) >= 2:
            attendees.append({"name": name, "title": "待确认", "company": company})

    # 提取时间
    date_match = re.search(r"(\d{1,2}月\d{1,2}日|\d{4}-\d{2}-\d{2}|今天|昨天|本周)", text)
    date = date_match.group(1) if date_match else "待确认"

    # 提取数字数据
    numbers = re.findall(r"[\d\.]+[%亿万元]", text)

    return {
        "meeting_type": meeting_type,
        "company": company,
        "company_code": company_code,
        "attendees": attendees,
        "date": date,
        "raw_text": text,
        "numbers_mentioned": numbers[:10],
    }


def extract_key_points(text: str, parsed: Dict) -> List[Dict]:
    """从文本中提取关键要点。"""
    points = []
    sentences = re.split(r"[。！？\n]", text)
    for s in sentences:
        s = s.strip()
        if len(s) < 10:
            continue
        # 判断情感
        sentiment = "中性"
        if any(w in s for w in ["乐观", "积极", "超预期", "大幅增长", "突破"]):
            sentiment = "正面"
        elif any(w in s for w in ["担忧", "压力", "下滑", "不及预期", "风险"]):
            sentiment = "负面"
        # 判断是否包含数据
        has_data = bool(re.search(r"\d", s))
        # 判断是否包含承诺
        has_commitment = any(w in s for w in ["将", "计划", "预计", "承诺", "会", "会于"])
        if has_data or sentiment != "中性" or has_commitment:
            points.append({
                "speaker": "管理层/嘉宾" if "公司" in s or "我们" in s else "待确认",
                "content": s[:200],
                "sentiment": sentiment,
                "has_data": has_data,
                "has_commitment": has_commitment,
            })
    return points[:8]  # 最多8条


def extract_action_items(text: str) -> List[Dict]:
    """提取待办事项。"""
    items = []
    # 匹配"待确认"/"后续"/"将提供"等承诺句式
    commitment_patterns = [
        r"(?:我们|公司)将?([^\n。]{5,30})",
        r"待?([^\n。]{5,30})(?:提供|回复|确认|补充)",
        r"后续([^\n。]{5,30})",
        r"请([^\n。]{5,30})(?:确认|核实|提供)",
    ]
    for pat in commitment_patterns:
        matches = re.findall(pat, text)
        for m in matches:
            items.append({
                "item": m.strip(),
                "owner": "待确认",
                "deadline": "待确认",
                "priority": "中",
            })
    # 去重
    seen = set()
    unique = []
    for item in items:
        key = item["item"][:20]
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique[:5]


def identify_risks(text: str, points: List[Dict]) -> List[str]:
    """识别风险提示。"""
    risks = []
    # 文本层面的风险词
    risk_keywords = ["压力", "下滑", "竞争加剧", "政策风险", "市场风险",
                     "技术迭代", "产能过剩", "应收账款", "存货", "商誉"]
    sentences = re.split(r"[。！？\n]", text)
    for s in sentences:
        for kw in risk_keywords:
            if kw in s and len(s) < 150:
                risks.append(f"风险提示：{s.strip()[:100]}")
                break
    # 情感负面的要点本身是风险
    for p in points:
        if p["sentiment"] == "负面":
            risks.append(f"关注事项：{p['content'][:80]}")
    return list(set(risks))[:5]


def generate_summary(points: List[Dict], parsed: Dict) -> str:
    """生成3句话摘要。"""
    company = parsed["company"] or "标的公司"
    date = parsed["date"]

    # 找最重要的正面和负面
    positives = [p["content"] for p in points if p["sentiment"] == "正面"]
    negatives = [p["content"] for p in points if p["sentiment"] == "负面"]
    data_points = [p["content"] for p in points if p.get("has_data")]

    summary_parts = [f"{date}对{company}进行了{parsed['meeting_type']}。"]
    if positives:
        summary_parts.append(f"管理层传递积极信号：{positives[0][:50]}。")
    elif negatives:
        summary_parts.append(f"管理层提及需关注：{negatives[0][:50]}。")
    if data_points:
        summary_parts.append(f"会议披露关键数据，相关方需核实。")
    else:
        summary_parts.append("整体交流内容较为广泛，建议跟进具体事项。")

    return " ".join(summary_parts)


class MeetingMinutesEngine:
    """调研纪要生成引擎。"""

    def generate(self, source) -> MeetingMinutes:
        if isinstance(source, str):
            parsed = parse_input(source)
            text = parsed["raw_text"]
        elif isinstance(source, dict):
            text = source.get("text", source.get("content", ""))
            parsed = parse_input(text)
            parsed.update({k: v for k, v in source.items() if k not in parsed})
        else:
            raise TypeError(f"unsupported input: {type(source)}")

        points = extract_key_points(text, parsed)
        actions = extract_action_items(text)
        risks = identify_risks(text, points)
        summary = generate_summary(points, parsed)

        title = f"{parsed['date']} {parsed['company'] or '某公司'} {parsed['meeting_type']}纪要"

        return MeetingMinutes(
            title=title,
            meeting_type=parsed["meeting_type"],
            attendees=parsed["attendees"],
            company=parsed["company"] or "待确认",
            date=parsed["date"],
            core_topics=self._infer_topics(text),
            key_points=points,
            data_mentioned=[{"value": n, "context": "", "source": "待确认"} for n in parsed["numbers_mentioned"]],
            action_items=actions,
            risks=risks,
            summary=summary,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

    def _infer_topics(self, text: str) -> List[str]:
        """推断核心议题。"""
        topic_keywords = {
            "储能业务": ["储能", "电池储能", "储能系统"],
            "零售业务": ["零售", "个人客户", "财富管理", "私行"],
            "资产质量": ["不良", "逾期", "不良率", "拨备"],
            "资本充足": ["资本", "核心一级资本", "资本充足率", "杠杆"],
            "海外业务": ["海外", "国际化", "出海的"],
            "科技投入": ["科技", "数字化", "IT", "系统"],
            "战略规划": ["战略", "五年", "规划", "目标"],
            "竞争格局": ["竞争", "同业", "市场份额", "对手"],
        }
        topics = []
        for topic, kws in topic_keywords.items():
            if any(kw in text for kw in kws):
                topics.append(topic)
        return topics[:5] if topics else ["综合交流"]


if __name__ == "__main__":
    eng = MeetingMinutesEngine()
    test_input = "今天上午实地调研宁德时代关于储能业务的情况，公司储能负责人张总参加。管理层表示上半年储能出货量同比增长200%，下半年订单已经排满，毛利率预计维持35%以上。但也提到原材料成本压力和竞争加剧的问题。公司计划明年海外收入占比提升至40%。"
    result = eng.generate(test_input)
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
