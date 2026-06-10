"""
LobbyEmotionEngine - 客户情绪识别引擎

基于客户行为特征（语气/表情/肢体语言/等待时长/投诉历史）
识别情绪状态、情绪强度，并给出服务策略建议与舆情风险预警。
"""

from typing import Literal, Optional
from dataclasses import dataclass


# 情绪状态枚举
EmotionState = Literal["非常满意", "满意", "中性", "不满", "愤怒"]

# 敏感词列表（触发立即升级）
SENSITIVE_KEYWORDS = [
    "投诉", "媒体", "曝光", "微博", "抖音", "记者",
    "上访", "举报", "维权", "律师", "央视", "热搜",
    "发帖", "朋友圈", "抖音", "小红书"
]

# 安抚话术库
SCRIPT_TEMPLATES = {
    "非常满意": "感谢您的认可，我们会继续努力为您提供优质服务。",
    "满意": "很高兴能帮到您，请问还有其他需要协助的吗？",
    "中性": "您好，请问有什么可以帮到您的？",
    "不满": "非常抱歉让您久等了，我理解您的时间非常宝贵。让我来看看能否为您提供优先服务...",
    "愤怒": "我深感抱歉让您遇到了这样的体验，请先稍作休息，我马上请我们的负责人来为您处理。"
}

# 升级原因话术
ESCALATION_SCRIPTS = {
    "intensity_high": "客户情绪强度较高（{level}级），需要管理人员介入协助处理。",
    "sensitive_keyword": "客户提及敏感词「{keyword}」，存在舆情风险，需升级处理。",
    "complaint_history": "该客户有历史投诉记录，请重点关注。",
    "long_wait": "客户等待时间较长（{minutes}分钟），建议优先处理。"
}


@dataclass
class EmotionResult:
    """情绪识别结果"""
    emotion: EmotionState
    emotion_level: int  # 1=非常满意 ... 5=愤怒
    intensity_score: int  # 原始强度分 1-5
    service_strategy: dict
    public_sentiment_risk: dict
    management_intervention: dict


class LobbyEmotionEngine:
    """
    客户情绪识别引擎

    输入客户行为描述，返回情绪识别结果及服务策略建议。
    """

    def __init__(self):
        self.name = "LobbyEmotionEngine"
        self.version = "1.0.0"

    def analyze(
        self,
        tone: str = "平和",
        expression: str = "无表情",
        body_language: str = "正常",
        wait_minutes: int = 0,
        has_complaint_history: bool = False,
        keywords: Optional[list[str]] = None
    ) -> EmotionResult:
        """
        分析客户情绪

        Args:
            tone: 语气特征（急促/平和/低沉/平和/愤怒）
            expression: 表情特征（微笑/皱眉/面无表情/等）
            body_language: 肢体语言（正常/叉腰/拍桌/挥手/抓头发）
            wait_minutes: 等待时长（分钟）
            has_complaint_history: 是否有投诉历史
            keywords: 客户说出的敏感词列表

        Returns:
            EmotionResult: 情绪识别结果
        """
        tone = tone.strip()
        expression = expression.strip()
        body_language = body_language.strip()
        keywords = keywords or []

        # Step 1: 计算基础情绪强度分
        base_score = self._calc_base_score(
            tone, expression, body_language, wait_minutes, has_complaint_history
        )

        # Step 2: 检查敏感词（触发立即升级）
        has_sensitive = self._check_sensitive_keywords(keywords)

        # Step 3: 应用投诉历史加成
        complaint_boost = 1.5 if has_complaint_history else 0.0

        # Step 4: 计算最终强度分
        raw_score = base_score + complaint_boost
        # 敏感词直接拉满
        if has_sensitive:
            raw_score = max(raw_score, 4.5)
        intensity_score = min(5, max(1, round(raw_score)))

        # Step 5: 映射情绪状态
        emotion, emotion_level = self._map_emotion(intensity_score)

        # Step 6: 判断是否升级
        escalation = emotion_level >= 4 or has_sensitive
        escalation_reasons = []
        if emotion_level >= 4:
            escalation_reasons.append(f"情绪强度{emotion_level}级≥4，需立即升级")
        if has_sensitive:
            escalation_reasons.append(f"提及敏感词：{'/'.join(keywords)}")
        if has_complaint_history and emotion_level >= 3:
            escalation_reasons.append("有投诉历史+当前不满，双重风险")

        # Step 7: 生成服务策略
        service_strategy = self._build_service_strategy(
            emotion, emotion_level, escalation, escalation_reasons, wait_minutes
        )

        # Step 8: 舆情风险预警
        public_sentiment_risk = self._build_sentiment_risk(
            emotion_level, has_sensitive, has_complaint_history, keywords
        )

        # Step 9: 管理人员介入
        management_intervention = self._build_management_intervention(
            emotion_level, has_sensitive, has_complaint_history, escalation_reasons
        )

        return EmotionResult(
            emotion=emotion,
            emotion_level=emotion_level,
            intensity_score=intensity_score,
            service_strategy=service_strategy,
            public_sentiment_risk=public_sentiment_risk,
            management_intervention=management_intervention
        )

    def _calc_base_score(
        self,
        tone: str,
        expression: str,
        body_language: str,
        wait_minutes: int,
        has_complaint_history: bool
    ) -> float:
        """计算基础情绪强度分（满分5分）"""
        score = 0.0

        # 语气贡献
        tone_scores = {
            "急促": 2.0,
            "平和": 0.0,
            "低沉": 0.5,  # 隐忍型
            "愤怒": 3.0,
            "大声": 2.5,
            "颤抖": 1.5,
        }
        score += tone_scores.get(tone, 0.0)

        # 表情贡献
        expr_scores = {
            "皱眉": 1.0,
            "微笑": -0.5,
            "面无表情": 0.5,  # 冷漠
            "紧绷": 1.0,
            "哭泣": 2.0,
            "白眼": 1.5,
            "等": 0.5,
        }
        score += expr_scores.get(expression, 0.0)

        # 肢体语言贡献
        body_scores = {
            "叉腰": 1.0,
            "拍桌": 2.5,
            "挥手": 1.0,
            "抓头发": 2.0,
            "扔东西": 3.0,
            "推搡": 3.0,
            "双手下垂": 0.0,
            "抱臂": 0.5,
            "正常": 0.0,
            "静止": 0.0,
        }
        score += body_scores.get(body_language, 0.0)

        # 等待时间贡献（超过30分钟不满概率+50%）
        if wait_minutes > 60:
            score += 2.0
        elif wait_minutes > 30:
            score += 1.0  # 不满概率+50%
        elif wait_minutes > 10:
            score += 0.5

        return max(0.0, score)

    def _check_sensitive_keywords(self, keywords: list[str]) -> bool:
        """检查是否提及敏感词"""
        if not keywords:
            return False
        for kw in keywords:
            for sensitive in SENSITIVE_KEYWORDS:
                if sensitive in kw:
                    return True
        return False

    def _map_emotion(self, intensity_score: int) -> tuple[EmotionState, int]:
        """将强度分映射为情绪状态"""
        if intensity_score <= 1:
            return "非常满意", 1
        elif intensity_score == 2:
            return "满意", 2
        elif intensity_score == 3:
            return "中性", 3
        elif intensity_score == 4:
            return "不满", 4
        else:
            return "愤怒", 5

    def _build_service_strategy(
        self,
        emotion: EmotionState,
        emotion_level: int,
        escalation: bool,
        escalation_reasons: list[str],
        wait_minutes: int
    ) -> dict:
        """构建服务策略"""
        script = SCRIPT_TEMPLATES.get(emotion, SCRIPT_TEMPLATES["中性"])

        action = ""
        if emotion_level == 1:
            action = "保持微笑服务，感谢客户反馈，适时推荐产品"
        elif emotion_level == 2:
            action = "正常服务，耐心解答疑问"
        elif emotion_level == 3:
            action = "主动询问是否需要帮助，留意情绪变化"
        elif emotion_level == 4:
            if wait_minutes > 30:
                action = "主动提供茶水、优先办理通道，申请权限内补偿（如小礼品）"
            else:
                action = "立即道歉，主动提供服务方案，请客户稍等片刻"
        else:  # 5
            action = "立即呼叫管理人员，暂停手头工作，优先处理，必要时报警"

        return {
            "script": script,
            "action": action,
            "escalation": escalation,
            "escalation_reasons": escalation_reasons
        }

    def _build_sentiment_risk(
        self,
        emotion_level: int,
        has_sensitive: bool,
        has_complaint_history: bool,
        keywords: list[str]
    ) -> dict:
        """构建舆情风险预警"""
        if emotion_level >= 5 or has_sensitive:
            level = "高"
            warning = f"舆情风险高：客户情绪强度{emotion_level}级" + \
                      ("，提及敏感词" + "/".join(keywords) if keywords else "") + \
                      "，建议立即上报并启动舆情预案"
        elif emotion_level == 4 or has_complaint_history:
            level = "中"
            warning = f"舆情风险中：客户情绪强度{emotion_level}级" + \
                      ("，有投诉历史" if has_complaint_history else "") + \
                      "，请做好舆情监控，必要时提前介入"
        elif emotion_level == 3:
            level = "低"
            warning = "舆情风险低：当前情绪中性，建议持续关注"
        else:
            level = "无"
            warning = "舆情风险可控，无异常信号"

        return {
            "level": level,
            "warning": warning
        }

    def _build_management_intervention(
        self,
        emotion_level: int,
        has_sensitive: bool,
        has_complaint_history: bool,
        escalation_reasons: list[str]
    ) -> dict:
        """构建管理人员介入建议"""
        required = emotion_level >= 4 or has_sensitive

        if emotion_level >= 5:
            suggested_person = "网点负责人 + 客服总监"
            reason = "情绪强度5级（愤怒），需高级管理人员立即介入"
        elif emotion_level == 4:
            suggested_person = "网点负责人或值班经理"
            reason = f"情绪强度4级（不满），升级原因：{'；'.join(escalation_reasons)}"
        else:
            suggested_person = "暂无"
            reason = "暂不需要管理人员介入"

        return {
            "required": required,
            "suggested_person": suggested_person,
            "reason": reason
        }

    def analyze_from_text(self, text: str) -> EmotionResult:
        """
        从自然语言描述中解析行为特征并分析情绪

        支持格式如：
        "情绪识别 客户语速急促 皱眉 等待40分钟 有投诉历史"
        "客户语速急促，皱眉，等待40分钟，有投诉历史"
        """
        text_lower = text.lower()
        text_full = text

        # 解析语气
        tone = "平和"
        if any(kw in text_full for kw in ["急促", "快", "大声", "提高音量"]):
            tone = "急促"
        elif any(kw in text_full for kw in ["低沉", "压低", "慢"]):
            tone = "低沉"
        elif any(kw in text_full for kw in ["愤怒", "吼", "叫"]):
            tone = "愤怒"

        # 解析表情
        expression = "无表情"
        if any(kw in text_full for kw in ["皱眉", "不悦"]):
            expression = "皱眉"
        elif any(kw in text_full for kw in ["微笑", "高兴", "满意"]):
            expression = "微笑"
        elif any(kw in text_full for kw in ["面无表情", "冷漠", "无表情"]):
            expression = "面无表情"

        # 解析肢体语言
        body_language = "正常"
        if any(kw in text_full for kw in ["叉腰"]):
            body_language = "叉腰"
        elif any(kw in text_full for kw in ["拍桌"]):
            body_language = "拍桌"
        elif any(kw in text_full for kw in ["挥手", "摆手"]):
            body_language = "挥手"
        elif any(kw in text_full for kw in ["抓头发"]):
            body_language = "抓头发"

        # 解析等待时间
        import re
        wait_match = re.search(r"等待(\d+)", text_full)
        wait_minutes = int(wait_match.group(1)) if wait_match else 0

        # 解析投诉历史
        has_complaint_history = any(
            kw in text_full for kw in ["投诉历史", "有投诉", "历史投诉", "曾投诉"]
        )

        # 解析敏感词
        found_keywords = [kw for kw in SENSITIVE_KEYWORDS if kw in text_full]

        return self.analyze(
            tone=tone,
            expression=expression,
            body_language=body_language,
            wait_minutes=wait_minutes,
            has_complaint_history=has_complaint_history,
            keywords=found_keywords
        )

    def to_dict(self, result: EmotionResult) -> dict:
        """将结果序列化为字典"""
        return {
            "emotion": result.emotion,
            "emotion_level": result.emotion_level,
            "intensity_score": result.intensity_score,
            "service_strategy": result.service_strategy,
            "public_sentiment_risk": result.public_sentiment_risk,
            "management_intervention": result.management_intervention
        }
