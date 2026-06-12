"""
反欺诈检测引擎
FraudDetectionEngine - 交易风险评分 + 30+规则检测 + 建议行动
"""

import re
import math
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TriggeredRule:
    """触发的规则"""
    id: str
    name: str
    confidence: float
    category: str
    detail: str = ""

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "confidence": self.confidence,
            "category": self.category,
            "detail": self.detail
        }


@dataclass
class FraudDetectionResult:
    """检测结果"""
    score: int  # 0-100
    level: str  # 低/中/高/极高
    rules: list[TriggeredRule]
    actions: list[str]
    summary: str

    def to_dict(self):
        return {
            "score": self.score,
            "level": self.level,
            "rules": [r.to_dict() for r in self.rules],
            "actions": self.actions,
            "summary": self.summary
        }


class FraudDetectionEngine:
    """
    反欺诈检测引擎
    支持30+条规则，覆盖金额/时间/频率/对手方/路径/账户六维度
    """

    def __init__(self):
        # 风险等级阈值
        self.THRESHOLDS = {
            "low": 25,
            "medium": 50,
            "high": 75,
        }

        # 规则配置表
        self.RULES = self._init_rules()

    def _init_rules(self):
        """初始化所有规则"""
        return [
            # ========== 金额异常类 ==========
            {"id": "R001", "name": "大额交易超阈值", "category": "amount",
             "confidence": 0.85, "threshold": 500000,
             "check": lambda ctx: ctx["amount"] > 500000,
             "detail": lambda ctx: ("单笔交易" + str(int(ctx["amount"]/10000)) + "万超过50万阈值")
            },
            {"id": "R002", "name": "整数偏好异常", "category": "amount",
             "confidence": 0.70,
             "check": lambda ctx: self._is_round_amount(ctx["amount"]),
             "detail": lambda ctx: ("金额" + str(ctx["amount"]) + "元为万元整数倍，存在拆分嫌疑")
            },
            {
                "id": "R003", "name": "金额突增", "category": "amount",
                "confidence": 0.80,
                "check": lambda ctx: self._is_amount_surge(ctx),
                "detail": lambda ctx: f"较历史均值增长{self._get_surge_ratio(ctx)*100:.0f}%，存在异常"
            },
            {
                "id": "R004", "name": "分散小额试探", "category": "amount",
                "confidence": 0.75,
                "check": lambda ctx: self._is_small_frequent(ctx),
                "detail": lambda ctx: f"同一对手方多笔小额交易{ctx.get('small_tx_count',0)}笔，疑似试探"
            },
            {
                "id": "R005", "name": "接近上限阈值", "category": "amount",
                "confidence": 0.65, "threshold": 450000,
                "check": lambda ctx: 450000 <= ctx["amount"] <= 500000,
                "detail": lambda ctx: f"金额在45-50万区间，接近单笔限额"
            },

            # ========== 时间异常类 ==========
            {
                "id": "T001", "name": "凌晨交易", "category": "time",
                "confidence": 0.90,
                "check": lambda ctx: ctx["hour"] in (2, 3, 4, 5) if "hour" in ctx else self._is_late_night(ctx),
                "detail": lambda ctx: f"交易发生在凌晨{int(ctx.get('hour', self._extract_hour(ctx.get('transaction_time', ''))))}点，风险较高"
            },
            {
                "id": "T002", "name": "节假日交易", "category": "time",
                "confidence": 0.75,
                "check": lambda ctx: self._is_holiday(ctx),
                "detail": lambda ctx: f"节假日期间进行大额交易，需要关注"
            },
            {
                "id": "T003", "name": "短时高频", "category": "time",
                "confidence": 0.85,
                "check": lambda ctx: ctx.get("hourly_count", 0) > 5,
                "detail": lambda ctx: f"1小时内交易{int(ctx.get('hourly_count',0))}次，频率异常"
            },
            {
                "id": "T004", "name": "非常规时段", "category": "time",
                "confidence": 0.70,
                "check": lambda ctx: self._is_unusual_hour(ctx),
                "detail": lambda ctx: f"在{int(ctx.get('hour',0))}点非工作时间交易"
            },
            {
                "id": "T005", "name": "月末密集交易", "category": "time",
                "confidence": 0.60,
                "check": lambda ctx: self._is_month_end(ctx),
                "detail": lambda ctx: f"月末{int(ctx.get('day',1))}日交易频繁，可能涉及税务或合规目的"
            },

            # ========== 频率异常类 ==========
            {
                "id": "F001", "name": "短时高频交易", "category": "frequency",
                "confidence": 0.80,
                "check": lambda ctx: ctx.get("hourly_count", 0) > 3,
                "detail": lambda ctx: f"1小时内{int(ctx.get('hourly_count',0))}笔交易，频率偏高"
            },
            {
                "id": "F002", "name": "交易频率突增", "category": "frequency",
                "confidence": 0.85,
                "check": lambda ctx: self._is_freq_surge(ctx),
                "detail": lambda ctx: f"交易频率较日均增长{self._get_freq_ratio(ctx)*100:.0f}%"
            },
            {
                "id": "F003", "name": "账户静默后激活", "category": "frequency",
                "confidence": 0.75,
                "check": lambda ctx: ctx.get("silent_days", 0) > 30,
                "detail": lambda ctx: f"账户{int(ctx.get('silent_days',0))}天未交易后突然激活"
            },
            {
                "id": "F004", "name": "对手方首次交易", "category": "frequency",
                "confidence": 0.70,
                "check": lambda ctx: ctx.get("counterparty_first", False),
                "detail": lambda ctx: f"与对手方[{ctx.get('counterparty','未知')}]为首笔交易"
            },
            {
                "id": "F005", "name": "交易时段过于规律", "category": "frequency",
                "confidence": 0.60,
                "check": lambda ctx: self._is_regular_interval(ctx),
                "detail": lambda ctx: f"交易间隔时间过于规律，可能为机器操作"
            },

            # ========== 对方异常类 ==========
            {"id": "C001", "name": "高风险地区对手方", "category": "counterparty",
             "confidence": 0.95,
             "check": lambda ctx: self._is_high_risk_region(ctx),
             "detail": lambda ctx: ("对手方所在地区[" + str(ctx.get('region', '未知')) + "]为高风险地区")
            },
            {"id": "C002", "name": "新客户首笔大额", "category": "counterparty",
             "confidence": 0.85,
             "check": lambda ctx: self._is_new_customer_large(ctx),
             "detail": lambda ctx: ("新客户注册" + str(int(ctx.get('customer_days', 0))) + "天，首笔交易" + str(int(ctx['amount']/10000)) + "万")
            },
            {
                "id": "C003", "name": "敏感行业对手方", "category": "counterparty",
                "confidence": 0.80,
                "check": lambda ctx: self._is_sensitive_industry(ctx),
                "detail": lambda ctx: f"对手方行业[{ctx.get('industry','未知')}]为敏感行业"
            },
            {
                "id": "C004", "name": "壳公司特征", "category": "counterparty",
                "confidence": 0.75,
                "check": lambda ctx: ctx.get("is_shell_company", False),
                "detail": lambda ctx: f"对手方[{ctx.get('counterparty','未知')}]具有空壳公司特征"
            },
            {
                "id": "C005", "name": "对手方信用评级低", "category": "counterparty",
                "confidence": 0.80,
                "check": lambda ctx: self._is_low_credit_rating(ctx),
                "detail": lambda ctx: f"对手方信用评级为{ctx.get('credit_rating','未知')}"
            },

            # ========== 路径异常类 ==========
            {
                "id": "P001", "name": "大额分散转入后集中转出", "category": "path",
                "confidence": 0.90,
                "check": lambda ctx: ctx.get("分散转入", False) and ctx.get("集中转出", False),
                "detail": lambda ctx: "资金呈现[分散转入→集中转出]模式，为典型洗钱特征"
            },
            {"id": "P002", "name": "资金快进快出", "category": "path",
             "confidence": 0.85,
             "check": lambda ctx: ctx.get("fund_hours", 999) < 24,
             "detail": lambda ctx: ("资金入账到转出仅" + str(int(ctx.get('fund_hours', 0))) + "小时")
            },
            {
                "id": "P003", "name": "交易链路闭环", "category": "path",
                "confidence": 0.90,
                "check": lambda ctx: ctx.get("loop_detected", False),
                "detail": lambda ctx: "检测到资金在关联账户间形成闭环"
            },
            {
                "id": "P004", "name": "跨境资金中转", "category": "path",
                "confidence": 0.85,
                "check": lambda ctx: ctx.get("cross_border_hops", 0) >= 3,
                "detail": lambda ctx: f"资金经过{int(ctx.get('cross_border_hops',0))}个国家/地区中转"
            },
            {
                "id": "P005", "name": "地下钱庄特征", "category": "path",
                "confidence": 0.95,
                "check": lambda ctx: ctx.get("underground_features", 0) >= 2,
                "detail": lambda ctx: f"具备{int(ctx.get('underground_features',0))}项地下钱庄特征"
            },

            # ========== 账户异常类 ==========
            {
                "id": "A001", "name": "账户信息变更后交易", "category": "account",
                "confidence": 0.80,
                "check": lambda ctx: ctx.get("info_changed_hours", 999) < 24,
                "detail": lambda ctx: f"账户信息变更后仅{int(ctx.get('info_changed_hours',0))}小时即进行交易"
            },
            {
                "id": "A002", "name": "登录IP突变", "category": "account",
                "confidence": 0.75,
                "check": lambda ctx: ctx.get("ip_changed", False),
                "detail": lambda ctx: f"登录IP从{ctx.get('usual_ip','未知')}切换到{ctx.get('current_ip','未知')}"
            },
            {
                "id": "A003", "name": "多账户关联异常", "category": "account",
                "confidence": 0.70,
                "check": lambda ctx: ctx.get("linked_accounts", 0) > 3,
                "detail": lambda ctx: f"该账户与{int(ctx.get('linked_accounts',0))}个账户存在关联"
            },
            {
                "id": "A004", "name": "账户长期闲置后启用", "category": "account",
                "confidence": 0.65,
                "check": lambda ctx: ctx.get("idle_days", 0) > 90,
                "detail": lambda ctx: f"账户闲置{int(ctx.get('idle_days',0))}天后重新启用"
            },
            {"id": "A005", "name": "账户持有人风险名单", "category": "account",
             "confidence": 1.00,
             "check": lambda ctx: ctx.get("on_risk_list", False),
             "detail": lambda ctx: ("账户持有人命中风险名单[涉赌/涉诈/制裁]")
            },
        ]

    # -------------------- 辅助检测方法 --------------------

    def _is_round_amount(self, amount):
        """R002: 整数偏好（万元整数倍）"""
        return amount > 0 and amount % 10000 == 0

    def _is_amount_surge(self, ctx):
        """R003: 金额突增（较历史均值>300%）"""
        avg = ctx.get("avg_amount", 0)
        if avg <= 0:
            return False
        return (ctx["amount"] / avg) > 3.0

    def _get_surge_ratio(self, ctx):
        """获取金额增长比例"""
        avg = ctx.get("avg_amount", ctx["amount"])
        return (ctx["amount"] / max(avg, 1)) - 1

    def _is_small_frequent(self, ctx):
        """R004: 分散小额试探"""
        return ctx.get("small_tx_count", 0) >= 3 and ctx["amount"] < 10000

    def _is_late_night(self, ctx):
        """T001: 凌晨交易"""
        return ctx.get("hour", -1) in (2, 3, 4, 5)

    def _extract_hour(self, time_str):
        """从时间字符串提取小时"""
        if not time_str:
            return -1
        # 匹配 "凌晨2点" / "早上6点" / "下午3点" 等
        m = re.search(r'(\d{1,2})[点时]', time_str)
        if m:
            h = int(m.group(1))
            if "凌晨" in time_str or "深夜" in time_str:
                return h if h >= 0 else -1
            return h
        return -1

    def _is_holiday(self, ctx):
        """T002: 节假日检测（简化版：中国法定节假日）"""
        holidays = {1, 2, 3,  # 元旦
                    5,  # 五一
                    10,  # 国庆
                    4, 5, 6, 7, 8, 9}  # 春节(简化)
        return ctx.get("month", 0) in holidays

    def _is_unusual_hour(self, ctx):
        """T004: 非工作时间"""
        h = ctx.get("hour", -1)
        return h >= 22 or h < 8

    def _is_month_end(self, ctx):
        """T005: 月末密集"""
        return ctx.get("day", 0) >= 28

    def _is_freq_surge(self, ctx):
        """F002: 频率突增>500%"""
        ratio = self._get_freq_ratio(ctx)
        return ratio > 5.0

    def _get_freq_ratio(self, ctx):
        """获取频率增长比例"""
        avg = ctx.get("avg_daily_freq", 1)
        current = ctx.get("daily_freq", 0)
        return current / max(avg, 1)

    def _is_regular_interval(self, ctx):
        """F005: 规律间隔"""
        return ctx.get("interval_std", 999) < 60  # 标准差<60秒

    def _is_high_risk_region(self, ctx):
        """C001: 高风险地区"""
        high_risk = {"缅甸", "老挝", "柬埔寨", "菲律宾", "迪拜", "土耳其",
                     "巴拿马", "开曼", "泽西", "塞舌尔", "马绍尔"}
        region = ctx.get("region", "")
        return region in high_risk

    def _is_new_customer_large(self, ctx):
        """C002: 新客户首笔大额"""
        days = ctx.get("customer_days", 999)
        amount = ctx["amount"]
        return days < 30 and amount > 100000

    def _is_sensitive_industry(self, ctx):
        """C003: 敏感行业"""
        sensitive = {"房地产", "博彩", "虚拟货币", "外汇", "贵金属", "典当"}
        industry = ctx.get("industry", "")
        return industry in sensitive

    def _is_low_credit_rating(self, ctx):
        """C005: 低信用评级"""
        rating = ctx.get("credit_rating", "")
        return rating in {"B", "C", "D", "CCC", "CC", "C"}

    # -------------------- 核心检测方法 --------------------

    def _parse_transaction_time(self, time_str: str) -> dict:
        """解析时间描述，返回 hour/day/month 等"""
        result = {"hour": -1, "day": -1, "month": -1}
        if not time_str:
            return result

        # 提取小时
        h = self._extract_hour(time_str)
        if h >= 0:
            result["hour"] = h

        # 节假日
        if any(k in time_str for k in ["元旦", "春节", "五一", "国庆", "清明", "端午", "中秋"]):
            result["is_holiday"] = True

        # 简单月份提取
        months = {"1月": 1, "2月": 2, "3月": 3, "4月": 4, "5月": 5, "6月": 6,
                  "7月": 7, "8月": 8, "9月": 9, "10月": 10, "11月": 11, "12月": 12}
        for k, v in months.items():
            if k in time_str:
                result["month"] = v
                break

        # 日
        d = re.search(r'(\d{1,2})日', time_str)
        if d:
            result["day"] = int(d.group(1))

        return result

    def _parse_amount(self, amount_str: str) -> float:
        """解析金额字符串"""
        if isinstance(amount_str, (int, float)):
            return float(amount_str)
        if not amount_str:
            return 0.0

        # 匹配 "50万" / "100万" / "500万" / "50万" 等
        m = re.search(r'(\d+(?:\.\d+)?)\s*万', amount_str)
        if m:
            return float(m.group(1)) * 10000

        # 匹配纯数字
        m = re.search(r'(\d+(?:\.\d+)?)', amount_str)
        if m:
            return float(m.group(1))

        return 0.0

    def _build_context(self, amount=None, transaction_type=None, counterparty=None,
                       transaction_time=None, account_history=None) -> dict:
        """构建检测上下文"""
        ctx = {
            "amount": self._parse_amount(str(amount)) if amount else 0.0,
            "transaction_type": transaction_type or "",
            "counterparty": counterparty or "",
            "transaction_time": transaction_time or "",
            # 从 account_history 提取
            "hourly_count": 0,
            "daily_freq": 0,
            "avg_daily_freq": 0,
            "avg_amount": 0,
            "silent_days": 0,
            "hourly_count": 0,
            "small_tx_count": 0,
            "customer_days": 9999,
            "counterparty_first": False,
            "region": "",
            "industry": "",
            "is_shell_company": False,
            "credit_rating": "",
            "分散转入": False,
            "集中转出": False,
            "fund_hours": 999,
            "loop_detected": False,
            "cross_border_hops": 0,
            "underground_features": 0,
            "info_changed_hours": 999,
            "ip_changed": False,
            "linked_accounts": 0,
            "idle_days": 0,
            "on_risk_list": False,
        }

        # 解析时间
        if transaction_time:
            time_info = self._parse_transaction_time(transaction_time)
            ctx.update(time_info)

        # 从 account_history 合并
        if account_history and isinstance(account_history, dict):
            ctx.update(account_history)

        # 推断counterparty特征
        cp = counterparty or ""
        if "新客户" in cp or "新" in cp:
            ctx["customer_days"] = 1  # 首笔
            ctx["counterparty_first"] = True

        # 推断敏感行业
        sensitive_industries = {"房地产", "博彩", "虚拟货币", "房地产", "赌场", "加密货币"}
        for ind in sensitive_industries:
            if ind in cp:
                ctx["industry"] = ind
                break

        # 高风险地区
        high_risk_regions = {"缅甸", "老挝", "柬埔寨", "菲律宾", "迪拜", "土耳其",
                             "巴拿马", "开曼", "泽西", "塞舌尔"}
        for reg in high_risk_regions:
            if reg in cp:
                ctx["region"] = reg
                ctx["on_risk_list"] = True  # 高风险地区直接标记
                break

        return ctx

    def _compute_score(self, triggered: list[TriggeredRule]) -> int:
        """计算风险评分：加权置信度 × 规则数量加成，上限100"""
        if not triggered:
            return 0

        # 加权求和
        weighted = sum(r.confidence for r in triggered)

        # 规则数量加成（3条以上开始有明显加成）
        count = len(triggered)
        count_bonus = max(0, (count - 2) * 3)

        score = weighted * 100 + count_bonus
        return min(100, int(score))

    def _get_level(self, score: int) -> str:
        """根据评分确定等级"""
        if score <= self.THRESHOLDS["low"]:
            return "低"
        elif score <= self.THRESHOLDS["medium"]:
            return "中"
        elif score <= self.THRESHOLDS["high"]:
            return "高"
        else:
            return "极高"

    def _get_actions(self, score: int, rules: list[TriggeredRule]) -> list[str]:
        """根据评分和规则生成建议行动"""
        actions = []
        categories = {r.category for r in rules}

        if score >= 76:
            actions.extend([
                "立即拦截该笔交易",
                "通知风控专员人工复核",
                "暂时冻结账户并展开调查"
            ])
        elif score >= 51:
            actions.extend([
                "标记为高风险交易",
                "进行人工复核后再放行",
                "通知风控团队监控账户"
            ])
        elif score >= 26:
            actions.extend([
                "加强交易监控",
                "纳入关注名单",
                "可选择电话核实"
            ])
        else:
            actions.append("正常通过，建议保持监控")

        # 按类别补充特定建议
        if "path" in categories:
            actions.append("调取完整交易链路记录备查")
        if "counterparty" in categories:
            actions.append("核查对手方背景及资质")
        if "account" in categories:
            actions.append("核查账户持有人身份及授权情况")

        return list(dict.fromkeys(actions))  # 去重保持顺序

    # -------------------- 公开接口 --------------------

    def detect(self, amount=None, transaction_type=None, counterparty=None,
               transaction_time=None, account_history=None) -> FraudDetectionResult:
        """
        执行欺诈检测

        Args:
            amount: 交易金额 (数字或字符串如"50万")
            transaction_type: 交易类型 (转账/支付/提现等)
            counterparty: 对手方描述
            transaction_time: 交易时间描述 (如"凌晨2点")
            account_history: 账户历史数据字典

        Returns:
            FraudDetectionResult: 检测结果
        """
        # 构建上下文
        ctx = self._build_context(amount, transaction_type, counterparty,
                                  transaction_time, account_history)

        # 执行所有规则检测
        triggered = []
        for rule in self.RULES:
            try:
                if rule["check"](ctx):
                    triggered.append(TriggeredRule(
                        id=rule["id"],
                        name=rule["name"],
                        confidence=rule["confidence"],
                        category=rule["category"],
                        detail=rule["detail"](ctx)
                    ))
            except Exception:
                pass

        # 计算评分和等级
        score = self._compute_score(triggered)
        level = self._get_level(score)
        actions = self._get_actions(score, triggered)

        # 生成摘要
        if not triggered:
            summary = "未检测到明显异常规则，交易通过"
        else:
            high_conf = [r for r in triggered if r.confidence >= 0.85]
            summary = f"检测到{len(triggered)}条规则触发"
            if high_conf:
                names = "、".join(r.name for r in high_conf[:3])
                summary += f"，其中{names}置信度较高，建议重点关注"

        return FraudDetectionResult(
            score=score,
            level=level,
            rules=triggered,
            actions=actions,
            summary=summary
        )

    def detect_from_nl(self, nl_text: str) -> FraudDetectionResult:
        """
        从自然语言描述执行检测
        示例: "反欺诈 交易金额50万 时间凌晨2点 对方是新客户"
        """
        # 解析金额
        amount = self._parse_amount(nl_text)

        # 解析时间
        time_kw = ["凌晨", "早上", "下午", "晚上", "中午", "深夜",
                   "节假日", "周末", "月末"]
        transaction_time = None
        for kw in time_kw:
            if kw in nl_text:
                transaction_time = nl_text[nl_text.find(kw):]
                break

        # 解析对手方
        counterparty = None
        cp_kw = ["对方", "对手方", "收款方", "付款方", "客户"]
        for kw in cp_kw:
            if kw in nl_text:
                idx = nl_text.find(kw) + len(kw)
                counterparty = nl_text[idx:].split()[0] if idx < len(nl_text) else ""

        # 解析交易类型
        type_kw = ["转账", "支付", "提现", "汇款", "充值", "消费"]
        transaction_type = "转账"
        for kw in type_kw:
            if kw in nl_text:
                transaction_type = kw
                break

        return self.detect(
            amount=amount,
            transaction_type=transaction_type,
            counterparty=counterparty,
            transaction_time=transaction_time,
            account_history=None
        )
