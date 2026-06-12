"""
调研纪要生成引擎
================
输入：调研录音/会议记录文字
输出：结构化纪要（参会人+议题+要点+待办+风险）
增强版本：语音转文字模拟 + 关键信息提取 + 情感分析 + 会议分类
"""
from __future__ import annotations
import json
import os
import re
import random
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

HERE = os.path.dirname(os.path.abspath(__file__))


# ============ 会议类型枚举 ============
class MeetingType(Enum):
    STRATEGY = "策略会"           # 券商/基金年度策略会
    EARNINGS = "业绩会"           # 季度/年度业绩发布会
    SITE_VISIT = "实地调研"       # 机构投资者实地调研
    PHONE_CALL = "电话会议"       # 电话沟通/电话调研
    INVESTOR_DAY = "投资者日"     # 上市公司投资者日活动
    CONFERENCE = "交流会"         # 行业交流会/论坛
    UNKNOWN = "交流会"            # 默认类型


# ============ 情感分析 ============
class SentimentAnalyzer:
    """情感分析器 - 统计正面/负面/中性词汇出现次数。"""

    POSITIVE_WORDS = [
        "增长", "盈利", "超预期", "突破", "创新", "领先", "稳健", "优化",
        "提升", "扩张", "高增长", "强劲", "显著", "大幅", "创历史", "首",
        "唯一", "Top", "最优", "最佳", "积极", "乐观", "向好", "好转",
        "超额完成", "如期", "达标", "符合预期", "领跑", "跑赢", "优于",
        "市场份额提升", "毛利率改善", "订单充足", "产能利用率", "满产",
        "供不应求", "量价齐升", "量利双增", "现金流改善", "负债率下降",
    ]

    NEGATIVE_WORDS = [
        "下滑", "下降", "压力", "风险", "担忧", "不及预期", "低于预期",
        "亏损", "恶化", "竞争加剧", "市场萎缩", "政策风险", "技术迭代",
        "产能过剩", "应收账款", "存货", "商誉", "减持", "诉讼", "处罚",
        "监管", "整改", "内控", "合规", "流动性", "偿债", "债务", "违约",
        "汇率", "波动", "不确定性", "困难", "挑战", "瓶颈", "放缓", "减速",
        "毛利率下降", "收入下滑", "利润减少", "库存积压", "订单不足", "停工",
    ]

    def __init__(self):
        self.positive_words = set(self.POSITIVE_WORDS)
        self.negative_words = set(self.NEGATIVE_WORDS)

    def count(self, text: str) -> Dict[str, int]:
        """统计文本中正负面词汇出现次数。"""
        pos_count = 0
        neg_count = 0
        found_positive = []
        found_negative = []

        for word in self.positive_words:
            if word in text:
                pos_count += text.count(word)
                found_positive.append(word)

        for word in self.negative_words:
            if word in text:
                neg_count += text.count(word)
                found_negative.append(word)

        total = pos_count + neg_count
        if total == 0:
            overall = "中性"
        elif pos_count > neg_count * 1.5:
            overall = "正面"
        elif neg_count > pos_count * 1.5:
            overall = "负面"
        else:
            overall = "中性"

        return {
            "positive_count": pos_count,
            "negative_count": neg_count,
            "neutral_count": len(re.findall(r"[\u4e00-\u9fa5]{2,}", text)) - pos_count - neg_count,
            "overall_sentiment": overall,
            "positive_words": found_positive[:10],
            "negative_words": found_negative[:10],
            "sentiment_ratio": round(pos_count / max(neg_count, 1), 2),
        }


# ============ 语音转文字解析器 ============
class VoiceTranscriptParser:
    """语音转文字解析器 - 模拟从音频文件路径生成转录文字。

    在实际场景中可替换为 Whisper/阿里云 ASR 等真实语音识别接口。
    """

    # 模拟不同会议类型的转录模板
    TRANSCRIPT_TEMPLATES = {
        MeetingType.SITE_VISIT: [
            "问：关于你们最新的业务发展情况，能介绍一下吗？\n答：感谢各位投资者关心。上半年我们整体经营稳健，{业务描述}。具体来看，{数据描述}。",
            "问：储能业务目前的毛利率水平如何？\n答：目前维持在{毛利率}左右，随着规模效应显现，下半年有望进一步改善。",
            "问：竞争加剧的情况下，你们的竞争优势是什么？\n答：主要有三点：一是技术领先，二是成本优势，三是客户结构优异。",
        ],
        MeetingType.EARNINGS: [
            "【业绩发布会】\n财务总监：上半年实现营业收入{收入}亿元，同比增长{增速}。\nCEO：下半年我们将重点推进{战略}，预计全年目标可如期完成。",
            "问：毛利率下滑的原因是什么？\n答：主要是原材料成本上涨所致，但公司已采取一系列降本增效措施，预计Q3起逐步改善。",
        ],
        MeetingType.STRATEGY: [
            "【策略会演讲】\n主讲人：感谢大家参会。今天我主要从三个方面分享我们的观点：\n一、{宏观判断}\n二、{行业观点}\n三、{公司战略}",
            "问：如何看待明年行业的竞争格局？\n答：我们认为行业集中度会进一步提升，龙头企业将获得更多市场份额。",
        ],
        MeetingType.PHONE_CALL: [
            "电话会议纪要：\n参会方：{公司}IR + {机构}分析师\n内容：主要就{议题}进行了交流，公司表示{回应}。",
        ],
        MeetingType.INVESTOR_DAY: [
            "【投资者日】\n公司高管团队集体亮相，围绕{主题}进行了全面分享。\n董事长：未来五年我们的愿景是{愿景}。\nCEO：具体到明年，{明年计划}。",
        ],
        MeetingType.CONFERENCE: [
            "【行业交流会】\n嘉宾：感谢邀请参加本次论坛。关于{话题}，我们认为{观点}。\nPanel讨论：各位嘉宾就{议题}展开了热烈讨论。",
        ],
    }

    PLACEHOLDER_VALUES = {
        "业务描述": ["储能业务表现亮眼，出货量同比增长200%", "海外业务拓展顺利，东南亚市场增速超过150%", "新能源业务占比持续提升，已超过40%", "研发投入持续加大，创新产品陆续落地"],
        "数据描述": ["收入利润双增长，净利润同比增45%", "海外收入占比提升至38%，毛利率维持35%以上", "在手订单超过200亿元，同比增长80%", "产能利用率达到95%，满产满销"],
        "毛利率": ["35%", "32%-33%", "30%以上", "33%-35%"],
        "收入": ["350", "420", "280", "500"],
        "增速": ["25%", "30%", "40%", "15%"],
        "战略": ["储能出海、产能扩张、新产品研发", "数字化转型、渠道下沉、高端产品", "降本增效、产能优化、海外布局", "技术创新、客户结构优化、产业链整合"],
        "宏观判断": ["全球流动性收紧背景下，A股估值有望修复", "新能源汽车渗透率持续提升，景气度延续", "储能行业进入规模化发展期，增速超预期", "银行业息差企稳，资产质量改善"],
        "行业观点": ["行业竞争格局优化，龙头份额提升", "技术迭代加速，落后产能出清", "下游需求旺盛，景气周期延长", "政策支持力度加大，发展空间广阔"],
        "公司战略": ["三年内实现营收翻番，五年进入全球前三", "持续加大研发投入，打造技术壁垒", "深耕细分化市场，建立差异化竞争优势", "通过并购整合加速产业链布局"],
        "公司": ["某新能源公司", "某汽车公司", "某银行A", "某白酒公司"],
        "机构": ["某投行A", "某券商A", "某外资投行A", "某外资投行B"],
        "议题": ["储能业务发展前景", "海外市场拓展计划", "技术创新路线", "竞争策略调整"],
        "回应": ["订单充足，产能利用率饱满", "海外业务进展顺利，预计明年贡献显著", "研发成果陆续落地，新产品将发布", "成本控制效果显现，毛利率逐季改善"],
        "主题": ["新能源技术创新与产业发展", "银行数字化转型之路", "储能全球化布局战略", "消费升级与品牌高端化"],
        "愿景": ["成为全球清洁能源领导者", "打造科技驱动的综合性金融集团", "构建产业生态圈，实现多方共赢", "基业长青，回报社会"],
        "明年计划": ["加速海外产能建设，东南亚项目Q1投产", "推出新一代产品线，覆盖更多应用场景", "深化客户合作，拓展战略客户至200家", "持续降本增效，目标净利率提升2个百分点"],
        "亮点": ["业务持续高增长，新产品陆续落地", "海外布局成效显著，东南亚收入翻番", "研发投入加大，技术壁垒不断加固", "降本增效持续推进，毛利率逐季改善", "客户结构优化，战略客户占比提升"],
        "业务": ["储能业务", "新能源业务", "海外业务", "技术研发", "产能扩张"],
        "pe": ["18", "20", "22", "25", "15", "12"],
        "话题": ["储能行业前景", "银行理财转型", "新能源出口", "产业竞争格局"],
        "观点": ["行业长期向好，短期波动不改趋势", "龙头企业具备长期投资价值", "技术创新是核心竞争力", "出海是中国企业的必由之路"],
        "议题": ["行业趋势展望", "技术路线选择", "出海机遇与挑战", "ESG与可持续发展"],
    }

    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()

    def parse(self, audio_path: str, meeting_type: str = None) -> Dict[str, Any]:
        """从音频文件路径解析/模拟生成转录文字。

        Args:
            audio_path: 音频文件路径（如 "会议录音.wav", "调研录音.mp3"）
            meeting_type: 会议类型 hint，可选

        Returns:
            包含转录文字和元数据的字典
        """
        # 检测文件扩展名
        ext = os.path.splitext(audio_path)[1].lower()
        if ext not in [".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac", ".wma"]:
            ext = ".wav"  # 默认

        # 解析文件名获取线索
        filename = os.path.basename(audio_path)
        file_size = 0
        try:
            if os.path.exists(audio_path):
                file_size = os.path.getsize(audio_path)
        except Exception:
            pass

        # 根据文件名关键词推断会议类型
        inferred_type = self._infer_meeting_type_from_filename(filename)
        if meeting_type:
            inferred_type = self._normalize_meeting_type(meeting_type)

        # 生成模拟转录
        transcript = self._generate_mock_transcript(inferred_type, filename)

        # 计算情感
        sentiment = self.sentiment_analyzer.count(transcript)

        # 检测语言（简单判断是否含大量英文/中文）
        lang_hint = "zh" if sum(1 for c in transcript if '\u4e00' <= c <= '\u9fff') > 20 else "mixed"

        return {
            "audio_path": audio_path,
            "audio_format": ext,
            "file_size_bytes": file_size,
            "duration_estimate_seconds": max(300, file_size // 8000) if file_size > 0 else 1800,
            "transcript": transcript,
            "meeting_type_detected": inferred_type.value,
            "confidence": 0.75 + random.random() * 0.2,  # 0.75-0.95
            "sentiment": sentiment,
            "language": lang_hint,
            "speaker_count_estimate": random.randint(2, 6),
            "parsed_at": datetime.now().isoformat(),
        }

    def _infer_meeting_type_from_filename(self, filename: str) -> MeetingType:
        """从文件名推断会议类型。"""
        fname_lower = filename.lower()
        if "策略" in fname_lower or "strategy" in fname_lower:
            return MeetingType.STRATEGY
        elif "业绩" in fname_lower or "earnings" in fname_lower:
            return MeetingType.EARNINGS
        elif "调研" in fname_lower or "visit" in fname_lower:
            return MeetingType.SITE_VISIT
        elif "电话" in fname_lower or "phone" in fname_lower:
            return MeetingType.PHONE_CALL
        elif "投资者日" in fname_lower or "investor day" in fname_lower:
            return MeetingType.INVESTOR_DAY
        elif "交流" in fname_lower or "会议" in fname_lower or "conf" in fname_lower:
            return MeetingType.CONFERENCE
        return MeetingType.UNKNOWN

    def _normalize_meeting_type(self, meeting_type: str) -> MeetingType:
        """将字符串转换为 MeetingType 枚举。"""
        mapping = {
            "策略会": MeetingType.STRATEGY,
            "业绩会": MeetingType.EARNINGS,
            "实地调研": MeetingType.SITE_VISIT,
            "调研": MeetingType.SITE_VISIT,
            "电话会议": MeetingType.PHONE_CALL,
            "投资者日": MeetingType.INVESTOR_DAY,
            "交流会": MeetingType.CONFERENCE,
            "strategy": MeetingType.STRATEGY,
            "earnings": MeetingType.EARNINGS,
            "site_visit": MeetingType.SITE_VISIT,
            "phone_call": MeetingType.PHONE_CALL,
            "investor_day": MeetingType.INVESTOR_DAY,
            "conference": MeetingType.CONFERENCE,
        }
        for key, val in mapping.items():
            if key in meeting_type:
                return val
        return MeetingType.UNKNOWN

    def _generate_mock_transcript(self, meeting_type: MeetingType, filename: str) -> str:
        """生成模拟转录文字。"""
        templates = self.TRANSCRIPT_TEMPLATES.get(meeting_type, self.TRANSCRIPT_TEMPLATES[MeetingType.CONFERENCE])
        transcript_parts = []

        for template in templates:
            # 随机选择占位符值
            result = template
            for placeholder, values in self.PLACEHOLDER_VALUES.items():
                if placeholder in template:
                    result = result.replace("{" + placeholder + "}", random.choice(values))
            transcript_parts.append(result)

        # 额外添加一些Q&A和总结
        extra_lines = [
            "\n问：关于明年的资本开支计划是怎样的？\n答：明年计划资本开支约30亿元，重点投向{业务}。",
            "\n问：你们如何看待当前的估值水平？\n答：我们认为当前估值具备吸引力，对应明年PE约{pe}倍。",
            "\n总结：今日交流整体正面，管理层传递积极信号。公司{亮点}，建议持续关注。",
        ]
        for line in extra_lines:
            if random.random() > 0.3:  # 80%概率添加
                result = line
                for placeholder, values in self.PLACEHOLDER_VALUES.items():
                    if placeholder in line:
                        result = result.replace("{" + placeholder + "}", random.choice(values))
                transcript_parts.append(result)

        return "\n".join(transcript_parts)


# ============ 关键信息提取器 ============
class KeyExtractor:
    """关键信息提取器 - 从转录中自动提取结构化信息。"""

    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()

    def extract(self, text: str, meeting_type: str = None) -> Dict[str, Any]:
        """从转录文字中提取关键信息。"""
        return {
            "key_data_points": self._extract_data_points(text),
            "commitments": self._extract_commitments(text),
            "risk_signals": self._extract_risk_signals(text),
            "competitor_info": self._extract_competitor_info(text),
            "industry_data": self._extract_industry_data(text),
            "guidance": self._extract_guidance(text),
            "financial_metrics": self._extract_financial_metrics(text),
        }

    def _extract_data_points(self, text: str) -> List[Dict]:
        """提取关键数据点。"""
        data_points = []
        # 匹配各种数据模式
        patterns = [
            (r"([\d\.]+)%", "百分比"),
            (r"([\d\.]+)\s*[亿万吨桶千瓦时]", "数量级数据"),
            (r"(同比|环比)\s*(增长|下降|提升|减少)\s*([\d\.]+)%", "增长率"),
            (r"(收入|营收|利润|净利润|毛利率|净利率)\s*([\d\.]+)\s*%", "财务比率"),
            (r"(产能|产量|出货量|订单量)\s*([\d\.]+)", "运营数据"),
            (r"(市场份额|占比|渗透率)\s*([\d\.]+)%", "占比数据"),
        ]

        for pat, ptype in patterns:
            for m in re.finditer(pat, text):
                val = m.group(0)
                if val not in [dp["value"] for dp in data_points]:
                    # 获取上下文
                    start = max(0, m.start() - 20)
                    end = min(len(text), m.end() + 30)
                    context = text[start:end].strip()

                    data_points.append({
                        "value": val,
                        "type": ptype,
                        "context": context,
                        "source": self._infer_source(context),
                    })

        return data_points[:15]  # 最多15条

    def _extract_commitments(self, text: str) -> List[Dict]:
        """提取承诺事项。"""
        commitments = []
        commitment_patterns = [
            (r"(?:公司|我们|管理层)\s*(?:将|计划|预计|承诺|会|将于)\s*([^\n。；，]{5,50})", "高"),
            (r"(?:将|计划|预计)\s*(?:在|于)\s*(\d{4}年|\d{1,2}月)([^\n。；，]{3,30})", "高"),
            (r"(?:目标|预计|预期)\s*([^\n。；，]{5,40})", "中"),
            (r"(?:预计|预期|指引)\s*[\d\.]+\s*(?:%|亿元|万吨)", "中"),
        ]

        for pat, priority in commitment_patterns:
            for m in re.finditer(pat, text):
                content = m.group(0).strip()
                if len(content) > 5 and content not in [c["content"] for c in commitments]:
                    commitments.append({
                        "content": content,
                        "priority": priority,
                        "deadline": self._extract_deadline(content),
                    })

        return commitments[:10]

    def _extract_risk_signals(self, text: str) -> List[Dict]:
        """提取风险信号。"""
        risks = []
        risk_patterns = {
            "竞争风险": ["竞争加剧", "同业的", "市场份额下滑", "面临挑战", "对手"],
            "政策风险": ["政策风险", "监管", "合规", "整改", "处罚", "限制"],
            "经营风险": ["成本压力", "毛利率下滑", "订单不足", "产能过剩", "库存积压"],
            "财务风险": ["应收账款", "商誉", "负债率", "现金流", "流动性风险"],
            "市场风险": ["需求下滑", "价格下跌", "市场萎缩", "周期性波动"],
            "技术风险": ["技术迭代", "替代技术", "研发失败", "专利风险"],
        }

        sentences = re.split(r"[。！？\n]", text)
        for s in sentences:
            s = s.strip()
            if len(s) < 5:
                continue
            for risk_type, keywords in risk_patterns.items():
                for kw in keywords:
                    if kw in s:
                        severity = "高" if any(w in s for w in ["大幅", "严重", "显著", "重大"]) else "中"
                        risks.append({
                            "signal": s[:150],
                            "type": risk_type,
                            "severity": severity,
                        })
                        break

        # 去重
        seen = set()
        unique = []
        for r in risks:
            key = r["signal"][:30]
            if key not in seen:
                seen.add(key)
                unique.append(r)

        return unique[:8]

    def _extract_competitor_info(self, text: str) -> List[Dict]:
        """提取竞品信息。"""
        competitors = []
        known_competitors = {
            "某新能源公司": "CATL", "某汽车公司": "BYD", "亿纬锂能": "EVE",
            "国轩高科": "Gotion", "中创新航": "CALB", "蜂巢能源": "SVOLT",
            "LG新能源": "LGES", "松下": "Panasonic", "三星SDI": "Samsung SDI",
            "赣锋锂业": "Ganfeng", "天齐锂业": "Tianqi",
            "某银行A": "CMB", "某银行B": "ICBC", "某银行C": "CCB",
            "某银行D": "ABC", "某银行E": "BOC", "某银行F": "CIB",
        }

        sentences = re.split(r"[。！？\n]", text)
        for s in sentences:
            s = s.strip()
            if len(s) < 5:
                continue
            for company, ticker in known_competitors.items():
                if company in s and "本公司" not in s and "我们" not in s:
                    sentiment = "正面" if any(w in s for w in ["领先", "超越", "优于", "超过"]) else \
                                "负面" if any(w in s for w in ["落后", "不如", "低于", "不及"]) else "中性"
                    competitors.append({
                        "company": company,
                        "ticker": ticker,
                        "mentioned_in": s[:100],
                        "context_sentiment": sentiment,
                    })
                    break

        return competitors[:6]

    def _extract_industry_data(self, text: str) -> List[Dict]:
        """提取行业数据。"""
        industry_data = []
        patterns = [
            (r"(?:行业|市场)\s*(?:规模|容量|总量)\s*(?:约)?\s*([\d\.]+)\s*([亿万吨桶千瓦时%])", "市场规模"),
            (r"(?:渗透率|占有率|集中度)\s*(?:约)?\s*([\d\.]+)\s*%", "渗透率/集中度"),
            (r"(?:行业|市场)\s*(?:增速|增长率|复合增长)\s*(?:约)?\s*([\d\.]+)\s*%", "行业增速"),
            (r"(?:预计|预测|预期)\s*\d{4}年.*?([\d\.]+)\s*%", "预测数据"),
        ]

        for pat, dtype in patterns:
            for m in re.finditer(pat, text):
                context_start = max(0, m.start() - 15)
                context_end = min(len(text), m.end() + 30)
                context = text[context_start:context_end].strip()

                industry_data.append({
                    "data": m.group(0),
                    "type": dtype,
                    "context": context,
                    "year_reference": self._extract_year_ref(context),
                })

        return industry_data[:8]

    def _extract_guidance(self, text: str) -> Dict[str, Any]:
        """提取管理层指引（业绩指引、目标等）。"""
        guidance = {
            "revenue_guidance": None,
            "profit_guidance": None,
            "margin_guidance": None,
            "capacity_guidance": None,
            "other_guidance": [],
        }

        # 收入指引
        m = re.search(r"(?:预计|目标|指引).*?收入.*?([\d\.]+)\s*亿", text)
        if m:
            guidance["revenue_guidance"] = m.group(0)

        # 利润指引
        m = re.search(r"(?:预计|目标|指引).*?净利润.*?([\d\.]+)\s*亿", text)
        if m:
            guidance["profit_guidance"] = m.group(0)

        # 毛利率指引
        m = re.search(r"(?:预计|目标|指引).*?毛利率.*?([\d\.]+)\s*%", text)
        if m:
            guidance["margin_guidance"] = m.group(0)

        # 产能指引
        m = re.search(r"(?:预计|目标|计划).*?产能.*?([\d\.]+)\s*(?:亿|万吨|GWh)", text)
        if m:
            guidance["capacity_guidance"] = m.group(0)

        return guidance

    def _extract_financial_metrics(self, text: str) -> Dict[str, Any]:
        """提取财务指标。"""
        metrics = {}
        patterns = {
            "pe": r"PE\s*(?:约)?\s*([\d\.]+)\s*倍|[Ff]\s*(?:约)?\s*([\d\.]+)\s*倍",
            "pb": r"PB\s*(?:约)?\s*([\d\.]+)\s*倍",
            "roe": r"ROE\s*(?:约)?\s*([\d\.]+)\s*%|净资产收益率\s*(?:约)?\s*([\d\.]+)\s*%",
            "dividend": r"(?:分红|股息)\s*([\d\.]+)\s*元|股息率\s*([\d\.]+)\s*%",
        }
        for key, pat in patterns.items():
            m = re.search(pat, text)
            if m:
                val = m.group(1) or m.group(2)
                metrics[key.upper()] = val

        return metrics

    def _infer_source(self, context: str) -> str:
        """推断数据来源。"""
        if any(w in context for w in ["公司", "我们"]):
            return "公司披露"
        elif any(w in context for w in ["行业", "协会", "第三方"]):
            return "第三方机构"
        elif any(w in context for w in ["预计", "预期", "预测"]):
            return "研究员预测"
        return "待确认"

    def _extract_deadline(self, content: str) -> str:
        """从承诺中提取时间节点。"""
        m = re.search(r"(\d{4}年|\d{1,2}月|\d{1,2}日|Q[1-4])", content)
        return m.group(1) if m else "待确认"

    def _extract_year_ref(self, context: str) -> str:
        """提取年份参考。"""
        m = re.search(r"(20\d{2})", context)
        return m.group(1) if m else ""


# ============ 数据类定义 ============
@dataclass
class Attendee:
    name: str
    title: str = ""
    company: str = ""


@dataclass
class SentimentResult:
    """情感分析结果。"""
    positive_count: int = 0
    negative_count: int = 0
    neutral_count: int = 0
    overall: str = "中性"
    positive_words: List[str] = field(default_factory=list)
    negative_words: List[str] = field(default_factory=list)
    ratio: float = 1.0


@dataclass
class VoiceTranscriptResult:
    """语音转文字解析结果。"""
    audio_path: str
    transcript: str
    meeting_type: str
    confidence: float
    sentiment: Dict[str, Any]
    duration_estimate: int = 1800  # 秒
    speaker_count: int = 3
    language: str = "zh"


@dataclass
class MeetingMinutes:
    """调研纪要。"""
    # 先定义所有无默认值的字段（按字段名排序）
    title: str
    company: str
    date: str
    generated_at: str
    summary: str
    # 有默认值/默认工厂的字段
    meeting_type: str = "交流会"
    meeting_category: str = "交流会"
    attendees: List[Dict] = field(default_factory=list)
    core_topics: List[str] = field(default_factory=list)
    key_points: List[Dict] = field(default_factory=list)
    data_mentioned: List[Dict] = field(default_factory=list)
    action_items: List[Dict] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    key_data_points: List[Dict] = field(default_factory=list)
    commitments: List[Dict] = field(default_factory=list)
    risk_signals: List[Dict] = field(default_factory=list)
    competitor_info: List[Dict] = field(default_factory=list)
    industry_data: List[Dict] = field(default_factory=list)
    guidance: Dict[str, Any] = field(default_factory=dict)
    financial_metrics: Dict[str, Any] = field(default_factory=dict)
    sentiment_analysis: Dict[str, Any] = field(default_factory=dict)
    voice_transcript: Optional[str] = None
    generated_at: str


def parse_input(text: str) -> Dict[str, Any]:
    """解析输入文本，提取关键信息。"""
    text = text.strip()

    # 识别会议类型
    meeting_types = ["实地调研", "电话会议", "视频会议", "交流会", "业绩发布会", "投资者交流", "策略会", "投资者日"]
    meeting_type = "交流会"
    for mt in meeting_types:
        if mt in text:
            meeting_type = mt
            break

    # 会议分类
    meeting_category = "交流会"
    category_map = {
        "策略会": "策略会",
        "业绩会": "业绩会",
        "实地调研": "实地调研",
        "电话会议": "电话会议",
        "投资者日": "投资者日",
        "交流会": "交流会",
    }
    for k, v in category_map.items():
        if k in text:
            meeting_category = v
            break

    # 提取公司名（已知公司列表）
    known_companies = {
        "某新能源公司": "300750.SZ", "某汽车公司": "002594.SZ",
        "某银行A": "600001.SH", "某白酒公司": "600002.SH",
        "某保险集团": "600003.SH", "某银行B": "600004.SH",
        "某银行C": "600005.SH", "某银行D": "600006.SH",
        "某银行E": "600007.SH", "某银行F": "600008.SH",
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
        "meeting_category": meeting_category,
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
    """调研纪要生成引擎（增强版）。

    支持两种输入模式：
    1. 直接文字输入：直接解析文字
    2. 音频文件路径输入：自动模拟语音转文字 + 增强提取 + 情感分析
    """

    def __init__(self):
        self.voice_parser = VoiceTranscriptParser()
        self.key_extractor = KeyExtractor()
        self.sentiment_analyzer = SentimentAnalyzer()

    def generate(self, source) -> MeetingMinutes:
        """生成调研纪要。

        Args:
            source: str 或 dict
                - str: 直接文字 或 音频文件路径（带.wav/.mp3等扩展名）
                - dict: 包含 text/transcript 等字段的字典

        Returns:
            MeetingMinutes 结构化纪要
        """
        is_voice_input = False
        voice_transcript = None
        voice_meta = None

        # 判断输入类型
        if isinstance(source, str):
            source_stripped = source.strip()
            # 检查是否是音频文件路径
            is_audio = any(
                source_stripped.lower().endswith(ext)
                for ext in [".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac", ".wma"]
            ) or "录音" in source_stripped or "音频" in source_stripped

            if is_audio:
                is_voice_input = True
                # 模拟语音转文字
                voice_meta = self.voice_parser.parse(source_stripped)
                voice_transcript = voice_meta["transcript"]
                text = voice_transcript
            else:
                text = source_stripped

        elif isinstance(source, dict):
            # 支持带语音元数据的字典
            if "transcript" in source:
                voice_transcript = source["transcript"]
                voice_meta = source.get("voice_meta", None)
                text = voice_transcript
                is_voice_input = True
            elif "audio_path" in source:
                is_voice_input = True
                voice_meta = self.voice_parser.parse(source["audio_path"])
                voice_transcript = voice_meta["transcript"]
                text = voice_transcript
            else:
                text = source.get("text", source.get("content", ""))
        else:
            raise TypeError(f"unsupported input: {type(source)}")

        # 基础解析
        parsed = parse_input(text)
        if is_voice_input and voice_meta:
            # 使用语音解析得到的会议类型
            parsed["meeting_category"] = voice_meta["meeting_type_detected"]
            parsed["meeting_type"] = voice_meta["meeting_type_detected"]
            parsed["sentiment"] = voice_meta["sentiment"]

        # 关键要点
        points = extract_key_points(text, parsed)

        # 增强提取：关键数据点、承诺、风险信号、竞品、行业数据
        if is_voice_input:
            extracted = self.key_extractor.extract(text, parsed.get("meeting_category"))
        else:
            extracted = self.key_extractor.extract(text)

        # 情感分析（如果没有通过语音解析获得）
        sentiment = parsed.get("sentiment", None)
        if sentiment is None:
            sentiment = self.sentiment_analyzer.count(text)

        # 待办事项 & 风险
        actions = extract_action_items(text)
        risks_text = identify_risks(text, points)

        # 生成摘要
        summary = generate_summary(points, parsed)

        # 推断议题
        core_topics = _infer_topics_enhanced(text)

        # 标题
        date_str = parsed["date"]
        company_str = parsed["company"] or "某公司"
        category_str = parsed.get("meeting_category", parsed["meeting_type"])
        title = f"{date_str} {company_str} {category_str}纪要"

        return MeetingMinutes(
            title=title,
            meeting_type=parsed["meeting_type"],
            meeting_category=parsed.get("meeting_category", parsed["meeting_type"]),
            attendees=parsed["attendees"],
            company=parsed["company"] or "待确认",
            date=date_str,
            core_topics=core_topics,
            key_points=points,
            data_mentioned=[{"value": n, "context": "", "source": "待确认"} for n in parsed["numbers_mentioned"]],
            action_items=actions,
            risks=risks_text,
            key_data_points=extracted["key_data_points"],
            commitments=extracted["commitments"],
            risk_signals=extracted["risk_signals"],
            competitor_info=extracted["competitor_info"],
            industry_data=extracted["industry_data"],
            guidance=extracted["guidance"],
            financial_metrics=extracted["financial_metrics"],
            sentiment_analysis=sentiment,
            voice_transcript=voice_transcript,
            summary=summary,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

    def generate_from_audio(self, audio_path: str, meeting_type_hint: str = None) -> MeetingMinutes:
        """从音频文件生成纪要（便捷方法）。

        Args:
            audio_path: 音频文件路径
            meeting_type_hint: 会议类型提示（可选）
        """
        return self.generate(audio_path)

    def generate_from_text(self, text: str) -> MeetingMinutes:
        """从文字生成纪要（便捷方法）。"""
        return self.generate(text)


def _infer_topics_enhanced(text: str) -> List[str]:
    """增强版议题推断。"""
    topic_keywords = {
        "储能业务": ["储能", "电池储能", "储能系统", "储能业务"],
        "零售业务": ["零售", "个人客户", "财富管理", "私行", "个人业务"],
        "资产质量": ["不良", "逾期", "不良率", "拨备", "资产质量"],
        "资本充足": ["资本", "核心一级资本", "资本充足率", "杠杆", "资本金"],
        "海外业务": ["海外", "国际化", "出海", "东南亚", "欧洲", "北美"],
        "科技投入": ["科技", "数字化", "IT", "系统", "研发", "技术"],
        "战略规划": ["战略", "五年", "规划", "目标", "愿景"],
        "竞争格局": ["竞争", "同业", "市场份额", "对手", "同行"],
        "新能源": ["新能源", "电动车", "电动汽车", "锂电", "动力电池"],
        "供应链": ["供应链", "产业链", "上游", "下游", "采购"],
        "产能扩张": ["产能", "扩产", "新建", "投产", "产能建设"],
        "毛利率": ["毛利率", "净利率", "利润率", "成本", "降本"],
        "分红": ["分红", "股息", "分红率", "股东回报"],
        "出海": ["出海", "海外市场", "国际化", "出口", "境外"],
    }
    topics = []
    for topic, kws in topic_keywords.items():
        if any(kw in text for kw in kws):
            topics.append(topic)
    return topics[:6] if topics else ["综合交流"]


# ============ 兼容旧版 ============
def _infer_topics(text: str) -> List[str]:
    return _infer_topics_enhanced(text)


if __name__ == "__main__":
    eng = MeetingMinutesEngine()

    # 测试1：文字输入
    print("=== 测试1: 文字输入 ===")
    test_input = "今天上午实地调研某新能源公司关于储能业务的情况，公司储能负责人张总参加。管理层表示上半年储能出货量同比增长200%，下半年订单已经排满，毛利率预计维持35%以上。但也提到原材料成本压力和竞争加剧的问题。公司计划明年海外收入占比提升至40%。"
    result = eng.generate(test_input)
    print(f"标题: {result.title}")
    print(f"情感: {result.sentiment_analysis}")
    print(f"数据点: {len(result.key_data_points)}条")
    print(f"承诺: {len(result.commitments)}条")

    # 测试2：音频文件输入（模拟）
    print("\n=== 测试2: 音频文件输入 ===")
    audio_result = eng.generate("语音转文字 会议录音.wav")
    print(f"标题: {audio_result.title}")
    print(f"会议分类: {audio_result.meeting_category}")
    print(f"情感: {audio_result.sentiment_analysis.get('overall_sentiment', 'N/A')}")
    print(f"风险信号: {len(audio_result.risk_signals)}条")
    print(f"竞品信息: {len(audio_result.competitor_info)}条")
    print(f"行业数据: {len(audio_result.industry_data)}条")
    print(f"指引: {audio_result.guidance}")
