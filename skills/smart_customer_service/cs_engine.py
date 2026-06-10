"""
智能客服核心引擎
SmartCustomerServiceEngine: 意图识别 + FAQ匹配 + 自动回答 + 转人工判断
"""

import re
from typing import Dict, List, Optional, Tuple


class SmartCustomerServiceEngine:
    """银行智能客服引擎"""

    # 意图定义
    INTENT_NAMES = {
        1: "开户咨询",
        2: "贷款申请",
        3: "理财产品",
        4: "信用卡",
        5: "保险业务",
        6: "投诉建议",
        7: "信息查询",
        8: "转人工",
        9: "判断失误",
        10: "闲聊",
    }

    # 意图关键词权重
    INTENT_KEYWORDS = {
        1: {  # 开户咨询
            "开户": 1.0, "开设账户": 1.0, "新户": 0.9, "办卡": 0.8,
            "开卡": 0.8, "注册": 0.6, "怎么办卡": 1.0, "如何开户": 1.0,
        },
        2: {  # 贷款申请
            "贷款": 1.0, "借款": 0.9, "信贷": 0.9, "房贷": 1.0,
            "车贷": 1.0, "信用贷": 1.0, "经营贷": 1.0, "贷款申请": 1.0,
            "怎么贷款": 1.0, "贷款条件": 0.9,
        },
        3: {  # 理财产品
            "理财": 1.0, "基金": 0.8, "收益": 0.7, "定期": 0.8,
            "理财产品": 1.0, "购买理财": 1.0, "理财产品的": 1.0,
            "收益怎么样": 0.9, "年化": 0.7, "净值": 0.6,
        },
        4: {  # 信用卡
            "信用卡": 1.0, "卡片": 0.7, "额度": 0.8, "账单": 0.8,
            "还款": 0.8, "分期": 0.7, "年费": 0.7, "积分": 0.6,
            "信用卡申请": 1.0, "怎么还款": 0.9,
        },
        5: {  # 保险业务
            "保险": 1.0, "投保": 0.9, "理赔": 1.0, "险种": 0.8,
            "医疗险": 1.0, "寿险": 1.0, "车险": 1.0, "意外险": 1.0,
        },
        6: {  # 投诉建议
            "投诉": 1.0, "建议": 0.8, "反馈": 0.7, "不满": 0.8,
            "被盗刷": 1.0, "盗刷": 1.0, "欺诈": 0.9, "骗子": 0.8,
            "非常不满": 1.0, "要投诉": 1.0, "差评": 0.9, "投诉你们": 1.0,
        },
        7: {  # 信息查询
            "查询": 1.0, "余额": 0.9, "明细": 0.9, "流水": 0.9,
            "利率": 0.8, "汇率": 0.7, "手续费": 0.8, "怎么查": 0.8,
            "什么时候到账": 0.8,
        },
        8: {  # 转人工
            "转人工": 1.0, "人工服务": 1.0, "人工客服": 1.0,
            "帮我转": 0.9, "要人工": 1.0, "接入人工": 1.0,
        },
        10: {  # 闲聊
            "你好": 0.5, "在吗": 0.5, "嗨": 0.4, "天气": 0.4,
            "吃饭": 0.3, "无聊": 0.3,
        },
    }

    # 隐私关键词（触发转人工）
    PRIVACY_KEYWORDS = [
        "身份证号", "身份证号码", "密码", "验证码", "cvv",
        "安全码", "后三码", "完整卡号",
    ]

    # 情绪激动关键词
    EMOTION_KEYWORDS = [
        "非常不满", "太差了", "垃圾", "废物", "滚", "白痴",
        "投诉你", "曝光", "起诉", "威胁", "要告", "杀人",
    ]

    # 复杂投诉关键词
    COMPLEX_COMPLAINT_KEYWORDS = [
        "之前投诉过", "已经反馈", "好几次", "多次", "一直没有",
        "历史", "上次", "上次说", "已经很久", "都几天了",
    ]

    # 50+条FAQ
    FAQ_DATA: List[Dict] = [
        # 开户咨询 (1)
        {
            "intent": 1, "question": "如何开设银行账户？", "answer": "开设银行账户需要您携带有效身份证件（如居民身份证、护照等）前往就近网点办理。您也可以通过手机银行APP在线申请开户，准备好身份证即可。",
            "similar": ["开户需要什么", "怎么办卡", "新户怎么办理"],
        },
        {
            "intent": 1, "question": "开户需要准备哪些材料？", "answer": "个人开户需要：1.有效身份证件（身份证/护照/港澳通行证）；2.手机号码（用于接收验证码）；3.如为代理开户还需代理人身份证及授权委托书。",
            "similar": ["开户材料", "办卡要什么证件", "开卡资料"],
        },
        {
            "intent": 1, "question": "未成年人可以开户吗？", "answer": "未满16周岁的未成年人需由监护人代理开户，监护人需携带双方身份证及监护关系证明（如户口簿、出生证明等）。16-18周岁可凭身份证自行办理。",
            "similar": ["小孩开户", "儿童开户", "孩子办卡"],
        },
        # 贷款申请 (2)
        {
            "intent": 2, "question": "如何申请贷款？", "answer": "您可以通过以下方式申请贷款：1.手机银行APP→贷款→立即申请；2.网上银行→个人贷款→在线申请；3.前往就近网点咨询办理。申请时需提供身份证明、收入证明、资产证明等材料。",
            "similar": ["怎么贷款", "贷款申请条件", "借款怎么办"],
        },
        {
            "intent": 2, "question": "贷款需要什么条件？", "answer": "贷款基本条件：1.年满18-65周岁具有完全民事行为能力的自然人；2.有稳定收入来源；3.信用记录良好；4.有明确贷款用途；5.提供相应担保或抵押。具体条件因贷款类型而异。",
            "similar": ["贷款要求", "什么条件能贷款", "贷款资质"],
        },
        {
            "intent": 2, "question": "房贷如何申请？", "answer": "申请房贷流程：1.准备身份证、收入证明、购房合同等材料；2.向银行提交贷款申请；3.银行审批（通常3-7个工作日）；4.审批通过后签订合同；5.办理抵押登记；6.放款。",
            "similar": ["房贷申请流程", "买房贷款", "商业贷款"],
        },
        # 理财产品 (3)
        {
            "intent": 3, "question": "理财产品安全吗？", "answer": "我行理财产品分为R1-R5五个风险等级：R1（谨慎型）主要投资货币市场，风险最低；R2（稳健型）以债券为主；R3起包含权益类资产。您可根据自身风险承受能力选择合适产品。",
            "similar": ["理财风险", "保本理财", "理财产品的风险"],
        },
        {
            "intent": 3, "question": "如何购买理财产品？", "answer": "购买渠道：1.手机银行→理财→理财产品；2.网上银行→理财专区；3.网点柜台。首次购买需进行风险评估，完成评估后可线上购买。起购金额通常为1万元。",
            "similar": ["怎么买理财", "理财购买流程", "理财产品怎么买"],
        },
        {
            "intent": 3, "question": "理财产品的收益如何计算？", "answer": "理财产品收益=本金×年化收益率×实际持有天数/365。示例：10万元购买90天、年化4.5%的理财产品，收益=100000×4.5%×90/365≈1109元。（收益仅供参考，实际以到期净值计算）",
            "similar": ["收益怎么算", "理财收益计算", "年化收益"],
        },
        # 信用卡 (4)
        {
            "intent": 4, "question": "如何申请信用卡？", "answer": "信用卡申请渠道：1.手机银行→信用卡→我要办卡；2.官方网站在线申请；3.网点柜台申请；4.合作渠道（支付宝、微信等）。需提供身份证、工作证明、收入证明等材料。",
            "similar": ["怎么办信用卡", "信用卡申请条件", "怎么申请卡"],
        },
        {
            "intent": 4, "question": "信用卡额度是多少？", "answer": "信用卡额度根据申请人资质综合评定：1.初次办卡额度通常在5000-50000元；2.额度过低可在使用6个月后申请调额；3.优质客户最高可达数十万元；4.可在APP查看和申请调额。",
            "similar": ["额度多少", "信用额度", "卡额度"],
        },
        {
            "intent": 4, "question": "信用卡如何还款？", "answer": "还款方式：1.自动还款（绑定借记卡）；2.手机银行转账还款；3.ATM现金还款；4.网点柜台还款；5.支付宝/微信还款。建议设置自动还款避免逾期。",
            "similar": ["怎么还信用卡", "账单怎么还", "还款方式"],
        },
        {
            "intent": 4, "question": "信用卡分期手续费多少？", "answer": "分期手续费因期数和合作活动而异：3期约0.9%-1.0%/期；6期约0.75%-0.85%/期；12期约0.65%-0.75%/期。具体以申请时显示费率为准，可享部分期数0手续费优惠。",
            "similar": ["分期手续费", "账单分期", "信用卡分期"],
        },
        # 保险业务 (5)
        {
            "intent": 5, "question": "银行可以购买保险吗？", "answer": "是的，我行代销多种保险产品，包括：1.意外险（交通意外、综合意外）；2.医疗险（住院医疗、百万医疗）；3.寿险（终身寿险、定期寿险）；4.年金险。可在手机银行→保险频道选购。",
            "similar": ["银行有保险吗", "怎么买保险", "保险产品"],
        },
        {
            "intent": 5, "question": "保险理赔怎么申请？", "answer": "理赔申请流程：1.发生保险事故后及时报案（955XX客服热线或APP）；2.准备理赔材料（保险合同、身份证、事故证明、医疗单据等）；3.提交理赔申请；4.保险公司审核（通常3-7个工作日）；5.理赔款到账。",
            "similar": ["理赔流程", "怎么理赔", "出险怎么赔"],
        },
        # 投诉建议 (6)
        {
            "intent": 6, "question": "银行卡被盗刷怎么办？", "answer": "银行卡被盗刷请立即按以下步骤处理：1.第一时间拨打客服热线冻结账户（955XX）；2.挂失卡片；3.在就近ATM操作留下时间戳证明；4.报警并获取报警回执；5.提交否认交易申请。我行将协助调查处理。",
            "similar": ["卡被盗刷", "银行卡被盗", "被刷卡"],
        },
        {
            "intent": 6, "question": "如何投诉银行服务？", "answer": "投诉渠道：1.客服热线955XX；2.手机银行→投诉建议；3.网上银行在线投诉；4.网点柜台；5.邮件投诉（投诉邮箱）。我行重视每一位客户的反馈，将尽快核实处理。",
            "similar": ["怎么投诉", "投诉电话", "反馈问题"],
        },
        {
            "intent": 6, "question": "网点服务态度差怎么办？", "answer": "对网点服务不满意，我们深表歉意。您可以通过：1.客服热线955XX反映；2.手机银行意见反馈；3.网点意见簿留言进行投诉。我们会及时核查并改进。",
            "similar": ["服务态度差", "柜员态度不好", "网点投诉"],
        },
        # 信息查询 (7)
        {
            "intent": 7, "question": "如何查询账户余额？", "answer": "余额查询渠道：1.手机银行APP首页；2.网上银行；3.电话银行（955XX）；4.ATM机；5.柜台。推荐使用手机银行，随时随地查询便捷安全。",
            "similar": ["余额怎么查", "查余额", "账户有多少钱"],
        },
        {
            "intent": 7, "question": "如何查询交易明细？", "answer": "查询交易明细：1.手机银行→账户→交易明细；2.网上银行→账户明细；3.柜台查询。可按时间范围、交易类型等条件筛选，最长可查询近5年明细。",
            "similar": ["流水怎么查", "明细查询", "消费记录"],
        },
        {
            "intent": 7, "question": "当前存款利率是多少？", "answer": "我行存款利率根据央行基准利率制定，具体利率因存期和地区而异。可通过：1.手机银行→利率查询；2.官网利率公告；3.网点咨询。活期约0.3%，定期一年约1.75%，具体以柜台实际办理为准。",
            "similar": ["利率查询", "存款利率", "利息多少"],
        },
        {
            "intent": 7, "question": "转账多久到账？", "answer": "转账时效：1.行内转账：实时到账；2.跨行转账：工作日16:00前操作当日到账，16:00后或节假日顺延；3.大额转账（超过5万）：人行审批，可能延时。建议大额转账提前操作。",
            "similar": ["转账时间", "什么时候到账", "汇款多久到"],
        },
        {
            "intent": 7, "question": "跨行转账手续费多少？", "answer": "跨行转账手续费：1.手机银行：每月前5笔免费，后续0.2元/笔（封顶5元）；2.网上银行：0.2元/笔（封顶5元）；3.柜台：1元/笔（封顶50元）。VIP客户可享更多免费笔数。",
            "similar": ["转账手续费", "跨行费用", "汇款手续费"],
        },
        # 转人工 (8)
        {
            "intent": 8, "question": "我要转人工服务", "answer": "正在为您转接人工客服，请稍候。为确保服务质量，您的通话可能被录音。感谢您的耐心等待。",
            "similar": ["转人工", "人工客服", "要人工服务"],
        },
        # 闲聊 (10)
        {
            "intent": 10, "question": "你好", "answer": "您好！很高兴为您服务。我是智能客服小e，请问有什么可以帮助您的？",
            "similar": ["您好", "在吗", "嗨"],
        },
        {
            "intent": 10, "question": "你是机器人吗？", "answer": "我是智能客服小e，可以帮您解答银行常见问题。对于复杂问题，我可以为您转接人工客服。",
            "similar": ["你是机器人", "真人吗", "是AI吗"],
        },
        {
            "intent": 10, "question": "谢谢", "answer": "不客气！很高兴能帮到您。如果还有其他问题，随时联系我。祝您生活愉快！",
            "similar": ["感谢", "谢谢啊", "谢了"],
        },
    ]

    def __init__(self):
        self._build_faq_index()

    def _build_faq_index(self):
        """构建FAQ索引"""
        self.faq_by_intent: Dict[int, List[Dict]] = {}
        for faq in self.FAQ_DATA:
            intent = faq["intent"]
            if intent not in self.faq_by_intent:
                self.faq_by_intent[intent] = []
            self.faq_by_intent[intent].append(faq)

    def _preprocess(self, text: str) -> str:
        """预处理文本"""
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        # 去除常见前缀
        prefixes = ["智能客服", "客服", "小e", "小e客服"]
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                break
        return text

    def _calculate_intent_score(self, text: str, intent_id: int) -> float:
        """计算文本与某意图的匹配得分"""
        text_lower = text.lower()
        keywords = self.INTENT_KEYWORDS.get(intent_id, {})
        if not keywords:
            return 0.0

        max_score = 0.0
        for keyword, weight in keywords.items():
            if keyword in text_lower:
                max_score = max(max_score, weight)

        # 检查相似问法
        for keyword in keywords.keys():
            for char in keyword:
                if char in text_lower and weight > 0.5:
                    max_score = max(max_score, weight * 0.3)
                    break

        return max_score

    def _detect_intent(self, text: str) -> Tuple[int, float]:
        """检测意图，返回(意图ID, 置信度)"""
        text_lower = text.lower()

        # 优先检查转人工
        transfer_keywords = self.INTENT_KEYWORDS.get(8, {})
        for kw, weight in transfer_keywords.items():
            if kw in text_lower:
                return (8, weight)

        # 计算各意图得分
        scores = {}
        for intent_id in self.INTENT_KEYWORDS.keys():
            if intent_id == 8:
                continue
            score = self._calculate_intent_score(text, intent_id)
            if score > 0:
                scores[intent_id] = score

        if not scores:
            return (10, 0.5)  # 默认闲聊

        # 取最高分
        best_intent = max(scores, key=scores.get)
        best_score = scores[best_intent]

        # 置信度阈值判断
        if best_score < 0.4:
            return (9, best_score)  # 判断失误

        return (best_intent, best_score)

    def _match_faq(self, text: str, intent_id: int) -> Optional[Dict]:
        """匹配FAQ"""
        text_lower = text.lower()
        if intent_id not in self.faq_by_intent:
            return None

        faqs = self.faq_by_intent[intent_id]
        best_match = None
        best_score = 0

        for faq in faqs:
            # 检查标准问题
            if faq["question"] in text_lower or text_lower in faq["question"]:
                score = 0.8
            else:
                score = 0
                # 检查相似问法
                for sim in faq.get("similar", []):
                    if sim in text_lower or text_lower in sim:
                        score = 0.6
                        break
                    # 部分匹配
                    words = sim.split()
                    matched = sum(1 for w in words if w in text_lower)
                    if matched >= len(words) * 0.5:
                        score = max(score, 0.3 * (matched / len(words)))

            if score > best_score:
                best_score = score
                best_match = faq

        if best_score < 0.2:
            return None
        return best_match

    def _should_transfer_human(self, text: str, intent_id: int,
                               misjudgment_count: int = 0) -> Tuple[bool, str]:
        """判断是否应转人工"""
        text_lower = text.lower()

        # 1. 隐私信息
        for kw in self.PRIVACY_KEYWORDS:
            if kw in text_lower:
                return True, f"涉及隐私信息（{kw}），建议转人工处理以保障账户安全"

        # 2. 情绪激动
        for kw in self.EMOTION_KEYWORDS:
            if kw in text_lower:
                return True, "检测到情绪激动，为保障服务质量，建议转人工服务"

        # 3. 复杂投诉
        if intent_id == 6:  # 投诉类
            complex_count = sum(1 for kw in self.COMPLEX_COMPLAINT_KEYWORDS if kw in text_lower)
            if complex_count > 0:
                return True, "涉及复杂投诉场景，建议转人工专员处理"

        # 4. 多次判断失误
        if misjudgment_count > 2:
            return True, "多次无法准确理解您的问题，为保障服务质量，建议转人工"

        # 5. 转人工意图明确
        if intent_id == 8:
            return True, "用户明确要求转人工服务"

        return False, ""

    def _generate_auto_answer(self, text: str, intent_id: int) -> str:
        """生成自动回答（当无FAQ匹配时）"""
        intent_name = self.INTENT_NAMES.get(intent_id, "未知")
        answers = {
            1: "关于开户问题，您可以通过手机银行APP在线申请开户，或前往就近网点办理。如需更多帮助，请详细描述您的问题。",
            2: "关于贷款问题，建议您通过手机银行-贷款频道了解各类贷款产品详情，或前往网点由客户经理为您详细介绍。",
            3: "关于理财问题，我行提供多种理财产品，您可根据风险偏好选择。如需个性化建议，建议咨询网点理财经理。",
            4: "关于信用卡问题，您可拨打信用卡服务热线或通过手机银行处理。请问具体是什么问题呢？",
            5: "关于保险问题，我行代销多款保险产品，您可通过手机银行保险频道了解详情。",
            6: "非常抱歉给您带来不便，请您详细描述遇到的问题，我们会认真处理并改进。",
            7: "您可以通过手机银行、网上银行、ATM或柜台查询相关信息。请问您想查询什么呢？",
            10: "您好，请问有什么可以帮助您的？您可以告诉我您想咨询的业务类型，如开户、贷款、理财等。",
        }
        return answers.get(intent_id, "请问您能详细描述一下您的问题吗？")

    def process(self, text: str, misjudgment_count: int = 0) -> Dict:
        """
        处理用户输入，返回结构化结果

        Returns:
            {
                "success": bool,
                "intent_id": int,
                "intent_name": str,
                "confidence": float,
                "faq_match": dict | None,
                "answer": str,
                "should_transfer": bool,
                "transfer_reason": str,
            }
        """
        text = self._preprocess(text)

        # 意图识别
        intent_id, confidence = self._detect_intent(text)

        # FAQ匹配
        faq_match = self._match_faq(text, intent_id)

        # 转人工判断
        should_transfer, transfer_reason = self._should_transfer_human(
            text, intent_id, misjudgment_count
        )

        # 生成回答
        if faq_match:
            answer = faq_match["answer"]
        elif should_transfer:
            answer = f"您好，为了更好地为您服务，我将为您转接人工客服。{transfer_reason}"
        else:
            answer = self._generate_auto_answer(text, intent_id)

        return {
            "success": True,
            "intent_id": intent_id,
            "intent_name": self.INTENT_NAMES.get(intent_id, "未知"),
            "confidence": confidence,
            "faq_match": faq_match,
            "answer": answer,
            "should_transfer": should_transfer,
            "transfer_reason": transfer_reason,
        }

    def get_stats(self) -> Dict:
        """获取技能统计信息"""
        return {
            "faq_count": len(self.FAQ_DATA),
            "intent_count": len(self.INTENT_NAMES),
            "intent_list": list(self.INTENT_NAMES.values()),
        }


# 便捷函数
def create_engine() -> SmartCustomerServiceEngine:
    """创建引擎实例"""
    return SmartCustomerServiceEngine()
