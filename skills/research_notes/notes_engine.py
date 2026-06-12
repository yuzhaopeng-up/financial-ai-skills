"""
调研纪要生成引擎 - ResearchNotesEngine
"""

import re
import json
import time
from typing import Dict, List, Any, Optional


class ResearchNotesEngine:
    """
    券商调研纪要结构化处理引擎

    输入：调研原始信息（公司/调研对象/方式/纪要原文）
    输出：结构化纪要 + 情感分析 + 可信度评分
    """

    def __init__(self, model_client=None):
        """
        Args:
            model_client: LLM 模型客户端，默认使用 arkcloudsdk
        """
        self.model_client = model_client

    def generate(self, company: str, subject: str, method: str,
                 raw_notes: str, date: str = "") -> Dict[str, Any]:
        """
        生成结构化调研纪要

        Args:
            company: 公司名称
            subject: 调研对象（IR/管理层/分析师等）
            method: 调研方式（现场调研/电话调研/策略会等）
            raw_notes: 纪要原文
            date: 调研日期（YYYY-MM-DD）

        Returns:
            结构化纪要字典
        """
        # 脱敏：公司名替换为"某公司"
        masked_company = self._mask_company(company, raw_notes)
        raw_notes_masked = self._apply_mask(company, "某公司", raw_notes)

        # 提取各维度信息
        attendees = self._extract_attendees(raw_notes_masked)
        core_discussions = self._extract_core_discussions(raw_notes_masked)
        key_data = self._extract_key_data(raw_notes_masked)
        commitments = self._extract_commitments(raw_notes_masked)
        risk_points = self._extract_risk_points(raw_notes_masked)
        follow_up = self._extract_follow_up(raw_notes_masked)
        suggestion = self._extract_investment_suggestion(raw_notes_masked)

        # 情感分析
        sentiment = self._analyze_sentiment(raw_notes_masked)

        # 可信度评分
        credibility = self._score_credibility(raw_notes_masked, attendees, key_data)

        return {
            "attendees": attendees,
            "core_discussions": core_discussions,
            "key_data": key_data,
            "commitments": commitments,
            "risk_points": risk_points,
            "investment_suggestion": suggestion,
            "follow_up_questions": follow_up,
            "sentiment_analysis": sentiment,
            "credibility_score": credibility,
            "metadata": {
                "company_masked": masked_company,
                "调研日期": date or self._extract_date(raw_notes_masked),
                "调研对象": subject,
                "调研方式": method,
                "生成时间": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        }

    def _mask_company(self, company: str, text: str) -> str:
        """返回脱敏后的公司名称"""
        if not company or company in text:
            # 尝试从文本中识别公司名（通常是最先出现的疑似公司名）
            candidates = re.findall(r'([\u4e00-\u9fa5]{4,}(?:股份|集团|公司|科技|实业)/?[A-Za-z]?)', text)
            if candidates:
                return "某公司"
        return "某公司"

    def _apply_mask(self, real_name: str, mask_name: str, text: str) -> str:
        """将真实公司名替换为脱敏名称"""
        if real_name and real_name in text:
            return text.replace(real_name, mask_name)
        return text

    def _extract_attendees(self, text: str) -> List[str]:
        """提取出席人员"""
        attendees = []

        # 模式1：出席人员/参会人员/参与人员
        patterns = [
            r'出席人员[：:]\s*([^\n。]+)',
            r'参会人员[：:]\s*([^\n。]+)',
            r'参与人员[：:]\s*([^\n。]+)',
            r'出席[：:]\s*([^\n。]+)',
            r'参会嘉宾[：:]\s*([^\n。]+)',
        ]
        for p in patterns:
            m = re.search(p, text)
            if m:
                names = re.split(r'[,，、/]', m.group(1))
                attendees.extend([n.strip() for n in names if n.strip()])
                break

        # 去重
        seen = set()
        result = []
        for a in attendees:
            key = a.strip()
            if key and key not in seen:
                seen.add(key)
                result.append(key)

        return result if result else ["某公司IR/管理层"]

    def _extract_core_discussions(self, text: str) -> List[str]:
        """提取核心交流内容"""
        discussions = []

        # 提取Q&A段落
        qa_sections = re.findall(r'Q[：:](.*?)(?:A[：:](.*?))?(?=\nQ[：:]|纪要结束|\Z)',
                                  text, re.DOTALL)
        for q, a in qa_sections:
            q = q.strip()
            a = (a or "").strip()
            if q:
                discussion = f"Q: {q}" + (f" A: {a}" if a else "")
                if len(discussion) > 10:
                    discussions.append(discussion[:200])

        # 提取关键话题
        topics = re.findall(r'关于(.+?)[，,]', text)
        for t in topics[:5]:
            if t and len(t) > 2:
                discussions.append(f"讨论：{t.strip()}")

        # 提取光标色关键词段落（按行业关键词）
        keywords = ['扩产', '毛利率', '产能', '订单', '出货', '竞争', '技术', '市场', '价格', '成本']
        for kw in keywords:
            if kw in text:
                # 找包含该关键词的句子
                sentences = re.findall(rf'[^。]*[{kw}][^。]*。', text)
                for s in sentences[:2]:
                    s = s.strip()
                    if s and s not in discussions and len(s) > 5:
                        discussions.append(s[:200])

        # 去重
        seen = set()
        result = []
        for d in discussions:
            if d[:50] not in seen:
                seen.add(d[:50])
                result.append(d)
        return result[:10]

    def _extract_key_data(self, text: str) -> List[Dict[str, str]]:
        """提取关键数据"""
        data = []

        # 提取百分比数据
        pct_matches = re.findall(r'([\u4e00-\u9fa5a-zA-Z]{2,20}?)[\s:：]*(\d+(?:\.\d+)?)\s*%',
                                  text)
        for label, val in pct_matches[:5]:
            data.append({
                "指标": label.strip(),
                "数值": f"{val}%",
                "说明": "数据来源于调研纪要"
            })

        # 提取金额数据
        amount_patterns = [
            r'(\d+(?:\.\d+)?)\s*(亿|万|千)\s*元',
            r'(营收|收入|利润|市值|估值|规模)[\s:：]*(\d+(?:\.\d+)?)\s*(亿|万)?',
            r'(产能|产量|出货量)[\s:：]*(\d+(?:\.\d+)?)\s*(GW|万|MW|万吨|件)?',
        ]
        for p in amount_patterns:
            matches = re.findall(p, text)
            for m in matches[:3]:
                if len(m) >= 2:
                    data.append({
                        "指标": m[0] if isinstance(m[0], str) else str(m[0]),
                        "数值": "".join(str(x) for x in m[1:]),
                        "说明": "数据来源于调研纪要"
                    })

        # 特定行业关键词
        industry_keywords = {
            '光伏': ['装机', '组件', '电池片', '硅片', '毛利', '扩产', '产能'],
            '锂电': ['锂价', '碳酸锂', '产能', '装机', '毛利'],
            '半导体': ['先进制程', '成熟制程', '稼动率', '毛利', '订单'],
            '消费': ['毛利率', '净利率', '营收增长', '市占率'],
        }

        for industry, keywords in industry_keywords.items():
            for kw in keywords:
                if kw in text:
                    sentences = re.findall(rf'[^。]*[{kw}][^。]*', text)
                    for s in sentences[:2]:
                        s = s.strip()
                        if s and len(s) > 5:
                            # 提取其中的数字
                            nums = re.findall(r'\d+(?:\.\d+)?', s)
                            if nums:
                                data.append({
                                    "指标": kw,
                                    "数值": nums[0],
                                    "说明": s[:80]
                                })
                                break

        # 去重
        seen = set()
        result = []
        for d in data:
            key = d["指标"] + d["数值"]
            if key not in seen:
                seen.add(key)
                result.append(d)
        return result[:8]

    def _extract_commitments(self, text: str) -> List[Dict[str, str]]:
        """提取承诺事项"""
        commitments = []

        patterns = [
            r'承诺[：:]\s*([^\n。]+)',
            r'将[在会]*(.{0,20}?)[，,]预计(\d+[年月日])',
            r'计划(.{0,15}?)[，,]预计(\d+[年月日])',
            r'将于(.+?)[。\n]',
            r'预计(.+?\d+年\d+月.+)',
        ]

        for p in patterns:
            matches = re.findall(p, text)
            for m in matches[:3]:
                if isinstance(m, tuple) and len(m) >= 2:
                    commitments.append({
                        "事项": m[0].strip(),
                        "承诺时间": m[1].strip() if len(m) > 1 else "待确认",
                        "状态": "承诺中"
                    })
                elif isinstance(m, str):
                    commitments.append({
                        "事项": m.strip()[:100],
                        "承诺时间": "待确认",
                        "状态": "承诺中"
                    })

        return commitments[:5]

    def _extract_risk_points(self, text: str) -> List[str]:
        """提取风险点"""
        risks = []

        risk_keywords = ['风险', '挑战', '压力', '竞争加剧', '价格下跌', '毛利率下降',
                         '需求不及预期', '产能过剩', '政策风险', '技术迭代', '供应链']

        for kw in risk_keywords:
            if kw in text:
                sentences = re.findall(rf'[^。\n]*[{kw}][^。\n]*。', text)
                for s in sentences[:2]:
                    s = s.strip()
                    if s and len(s) > 5:
                        risks.append(s[:150])

        return list(dict.fromkeys(risks))[:5]

    def _extract_follow_up(self, text: str) -> List[str]:
        """提取待跟进问题"""
        questions = []

        patterns = [
            r'待跟进[：:]\s*([^\n。]+)',
            r'待确认[：:]\s*([^\n。]+)',
            r'后续需(.+?)[。\n]',
            r'请(.+?)[。\n]',
            r'需要(.+?核实|确认|跟进)',
        ]

        for p in patterns:
            matches = re.findall(p, text)
            for m in matches[:3]:
                if isinstance(m, str):
                    questions.append(m.strip()[:100])

        return list(dict.fromkeys(questions))[:5]

    def _extract_investment_suggestion(self, text: str) -> str:
        """提取投资建议"""
        suggestions = []

        patterns = [
            r'投资建议[：:]\s*([^\n。]+)',
            r'建议[：:]\s*([^\n。]+)',
            r'维持[买入增持持有评级]',
            r'(买入|增持|持有|中性|减持|卖出)',
        ]

        for p in patterns:
            matches = re.findall(p, text)
            for m in matches[:2]:
                s = m.strip() if isinstance(m, str) else str(m)
                if len(s) > 3:
                    suggestions.append(s)

        if suggestions:
            return " | ".join(suggestions[:3])
        return "维持关注，建议持续跟踪行业动态"

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """情感分析：管理层信心指数"""
        positive_words = ['乐观', '信心', '增长', '扩张', '订单充足', '需求旺盛',
                          '超预期', '好于预期', '提升', '扩大', '加速', '强劲']
        negative_words = ['压力', '下降', '谨慎', '不及预期', '竞争加剧', '挑战',
                          '困难', '下滑', '过剩', '风险', '收缩', '放缓']
        neutral_words = ['平稳', '稳定', '维持', '持平', '保持', '符合预期']

        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)
        neu_count = sum(1 for w in neutral_words if w in text)

        # 基础分数 5 分
        score = 5.0 + (pos_count - neg_count) * 0.5
        score = max(1.0, min(10.0, score))

        if score >= 7:
            label = "乐观"
        elif score >= 4:
            label = "中性"
        else:
            label = "谨慎"

        return {
            "confidence_index": round(score, 1),
            "sentiment_label": label,
        }

    def _score_credibility(self, text: str, attendees: List[str],
                           key_data: List[Dict]) -> float:
        """信息可信度评分"""
        score = 5.0

        # 出席人员明确 +1
        if len(attendees) > 0 and attendees[0] != "某公司IR/管理层":
            score += 1

        # 有具体数据 +1
        if len(key_data) >= 3:
            score += 1
        elif len(key_data) >= 1:
            score += 0.5

        # 有Q&A交流内容 +0.5
        if 'Q:' in text or '问:' in text:
            score += 0.5

        # 文本长度适中（太短可能信息不足）
        if len(text) < 100:
            score -= 1
        elif len(text) > 500:
            score += 0.5

        return round(max(1.0, min(10.0, score)), 1)

    def _extract_date(self, text: str) -> str:
        """从文本中提取日期"""
        patterns = [
            r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)',
            r'(\d{4}年\d{1,2}月\d{1,2}日)',
            r'(\d{4}-\d{2}-\d{2})',
        ]
        for p in patterns:
            m = re.search(p, text)
            if m:
                return m.group(1)
        return time.strftime("%Y-%m-%d")

    def to_markdown(self, result: Dict[str, Any]) -> str:
        """将结构化结果转换为 Markdown 格式"""
        md = []
        md.append(f"# 调研纪要\n")
        md.append(f"**公司：** {result['metadata']['company_masked']}\n")
        md.append(f"**调研日期：** {result['metadata'].get('调研日期', 'N/A')}\n")
        md.append(f"**调研对象：** {result['metadata'].get('调研对象', 'N/A')}\n")
        md.append(f"**调研方式：** {result['metadata'].get('调研方式', 'N/A')}\n")
        md.append(f"**生成时间：** {result['metadata'].get('生成时间', 'N/A')}\n")
        md.append(f"\n---\n")

        md.append(f"## 出席人员\n")
        for a in result['attendees']:
            md.append(f"- {a}\n")
        md.append(f"\n")

        md.append(f"## 核心交流\n")
        for i, d in enumerate(result['core_discussions'], 1):
            md.append(f"{i}. {d}\n")
        md.append(f"\n")

        md.append(f"## 关键数据\n")
        for d in result['key_data']:
            md.append(f"- **{d['指标']}**：{d['数值']}\n")
            if d.get('说明') and d['说明'] != '数据来源于调研纪要':
                md.append(f"  - 说明：{d['说明']}\n")
        md.append(f"\n")

        md.append(f"## 承诺事项\n")
        for c in result['commitments']:
            md.append(f"- {c['事项']}（{c.get('承诺时间','待确认')}，{c.get('状态','承诺中')}）\n")
        md.append(f"\n")

        md.append(f"## 风险点\n")
        for r in result['risk_points']:
            md.append(f"- {r}\n")
        md.append(f"\n")

        md.append(f"## 投资建议\n")
        md.append(f"{result['investment_suggestion']}\n\n")

        md.append(f"## 待跟进问题\n")
        for q in result['follow_up_questions']:
            md.append(f"- {q}\n")
        md.append(f"\n")

        sentiment = result['sentiment_analysis']
        md.append(f"## 情感分析\n")
        md.append(f"- 管理层信心指数：**{sentiment['confidence_index']}/10**（{sentiment['sentiment_label']}）\n")
        md.append(f"- 信息可信度评分：**{result['credibility_score']}/10**\n")

        return "".join(md)

    def to_wecom_card(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """转换为企微消息卡片格式"""
        sentiment = result['sentiment_analysis']
        return {
            "msgtype": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "text": f"📋 调研纪要 | {result['metadata']['company_masked']}"
                    },
                    "subtitle": {
                        "tag": "plain_text",
                        "text": f"{result['metadata'].get('调研方式', 'N/A')} | {result['metadata'].get('调研日期', 'N/A')}"
                    }
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": f"**出席人员**：{', '.join(result['attendees'][:3])}{'等' if len(result['attendees']) > 3 else ''}"
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "markdown",
                        "content": self._build_discussions_md(result['core_discussions'][:3])
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "markdown",
                        "content": self._build_key_data_md(result['key_data'][:3])
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "markdown",
                        "content": f"**🚨 风险点**\n" + "\n".join([f"- {r[:60]}" for r in result['risk_points'][:2]]) if result['risk_points'] else "- 无明显风险点"
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "markdown",
                        "content": (
                            f"**📊 情感分析**\n"
                            f"- 信心指数：{sentiment['confidence_index']}/10（{sentiment['sentiment_label']}）\n"
                            f"- 可信度评分：{result['credibility_score']}/10\n\n"
                            f"**💡 投资建议**：{result['investment_suggestion'][:50]}"
                        )
                    }
                ]
            }
        }

    def _build_discussions_md(self, discussions: List[str]) -> str:
        if not discussions:
            return "**核心交流**：暂无"
        content = "**💬 核心交流**\n"
        for d in discussions:
            content += f"- {d[:80]}{'...' if len(d) > 80 else ''}\n"
        return content

    def _build_key_data_md(self, key_data: List[Dict]) -> str:
        if not key_data:
            return "**📈 关键数据**：暂无"
        content = "**📈 关键数据**\n"
        for d in key_data:
            content += f"- **{d['指标']}**：{d['数值']}\n"
        return content
