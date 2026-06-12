"""
实时欺诈预警引擎
FraudAlertEngine - 毫秒级实时交易预警 + 红色/橙色/黄色分级 + 紧急处置建议
"""

import re
import math
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AlertRule:
    """预警规则"""
    id: str
    name: str
    severity: str  # A(红)/B(橙)/C(黄)
    confidence: float
    category: str
    detail: str = ""

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "severity": self.severity,
            "confidence": self.confidence,
            "category": self.category,
            "detail": self.detail
        }


@dataclass
class FraudAlertResult:
    """预警结果"""
    level: str           # 红色/橙色/黄色/正常
    score: int           # 0-100
    rules: list[AlertRule]
    actions: list[str]
    review_required: bool
    review_urgency: str  # 高/中/低
    summary: str

    def to_dict(self):
        return {
            "level": self.level,
            "score": self.score,
            "rules": [r.to_dict() for r in self.rules],
            "actions": self.actions,
            "review_required": self.review_required,
            "review_urgency": self.review_urgency,
            "summary": self.summary
        }


class FraudAlertEngine:
    """
    实时欺诈预警引擎
    专注毫秒级实时交易预警，20+规则，覆盖异地/大额/夜间/设备/频率等维度
    """

    def __init__(self):
        self.THRESHOLDS = {
            "yellow": 25,
            "orange": 50,
            "red": 75,
        }
        self.SEVERITY_COLOR = {
            "A": "🔴",
            "B": "🟠",
            "C": "🟡",
        }
        self.RULES = self._init_rules()

    def _init_rules(self):
        """初始化20+预警规则"""
        return [
            # ========== 🔴 A类高危规则 ==========
            {
                "id": "A001", "name": "异地登录+大额交易", "severity": "A",
                "category": "location",
                "confidence": 0.95,
                "check": lambda ctx: (
                    ctx.get("location_changed", False) and
                    ctx["amount"] >= 50000
                ),
                "detail": lambda ctx: (
                    f"登录地{ctx.get('login_location','未知')}，交易地点{ctx.get('location','未知')}，"
                    f"金额{int(ctx['amount']/10000)}万元"
                )
            },
            {
                "id": "A002", "name": "设备指纹突变", "severity": "A",
                "category": "device",
                "confidence": 0.90,
                "check": lambda ctx: (
                    ctx.get("device_change", False) and ctx["amount"] >= 10000
                ),
                "detail": lambda ctx: (
                    f"设备{ctx.get('device_id','异常设备')}发生变更，"
                    f"交易金额{int(ctx['amount']/10000)}万元"
                )
            },
            {
                "id": "A003", "name": "大额快进快出", "severity": "A",
                "category": "velocity",
                "confidence": 0.92,
                "check": lambda ctx: (
                    ctx["amount"] >= 100000 and
                    ctx.get("fund_out_hours", 999) < 24
                ),
                "detail": lambda ctx: (
                    f"单笔{int(ctx['amount']/10000)}万元，资金入账后"
                    f"{int(ctx.get('fund_out_hours',0))}小时内转出超过80" + "%"
                )
            },
            {
                "id": "A004", "name": "风险名单命中", "severity": "A",
                "category": "blacklist",
                "confidence": 1.00,
                "check": lambda ctx: ctx.get("on_risk_list", False),
                "detail": lambda ctx: (
                    f"账户/对手方命中风险名单[{ctx.get('risk_list_type','涉赌/涉诈/制裁')}]"
                )
            },
            {
                "id": "A005", "name": "非常规时段+大额", "severity": "A",
                "category": "time",
                "confidence": 0.88,
                "check": lambda ctx: (
                    ctx.get("is_night", False) and ctx["amount"] >= 50000
                ),
                "detail": lambda ctx: (
                    f"交易时间{ctx.get('transaction_time','未知')}，属于夜间非工作时段，"
                    f"金额{int(ctx['amount']/10000)}万元"
                )
            },
            {
                "id": "A006", "name": "大额分散转入后集中转出", "severity": "A",
                "category": "velocity",
                "confidence": 0.93,
                "check": lambda ctx: (
                    ctx.get("multi_in", False) and ctx.get("single_out", False) and
                    ctx["amount"] >= 50000
                ),
                "detail": lambda ctx: "资金呈现[多笔分散转入→集中转出]模式，典型洗钱特征"
            },
            {
                "id": "A007", "name": "新账户首笔大额+夜间", "severity": "A",
                "category": "account",
                "confidence": 0.91,
                "check": lambda ctx: (
                    ctx.get("account_days", 999) < 7 and
                    ctx["amount"] >= 50000 and
                    ctx.get("is_night", False)
                ),
                "detail": lambda ctx: (
                    f"账户开户仅{ctx.get('account_days',0)}天，首笔{int(ctx['amount']/10000)}万元，"
                    f"发生在夜间"
                )
            },
            {
                "id": "A008", "name": "IP突变+频繁交易", "severity": "A",
                "category": "device",
                "confidence": 0.89,
                "check": lambda ctx: (
                    ctx.get("ip_changed", False) and
                    ctx.get("hourly_count", 0) >= 3
                ),
                "detail": lambda ctx: (
                    f"IP发生变更，1小时内交易{int(ctx.get('hourly_count',0))}次，"
                    f"可能存在账户被盗用"
                )
            },

            # ========== 🟠 B类中危规则 ==========
            {
                "id": "B001", "name": "频繁小额测试", "severity": "B",
                "category": "frequency",
                "confidence": 0.85,
                "check": lambda ctx: (
                    ctx.get("hourly_count", 0) >= 5 and
                    ctx["amount"] < 1000
                ),
                "detail": lambda ctx: (
                    f"1小时内{int(ctx.get('hourly_count',0))}笔小额(<1000元)交易，"
                    f"疑似洗钱试探"
                )
            },
            {
                "id": "B002", "name": "夜间交易", "severity": "B",
                "category": "time",
                "confidence": 0.80,
                "check": lambda ctx: ctx.get("is_night", False),
                "detail": lambda ctx: f"交易时间{ctx.get('transaction_time','未知')}，属于夜间时段"
            },
            {
                "id": "B003", "name": "整数大额", "severity": "B",
                "category": "amount",
                "confidence": 0.75,
                "check": lambda ctx: (
                    self._is_round_amount(ctx["amount"]) and
                    ctx["amount"] >= 50000
                ),
                "detail": lambda ctx: f"金额{int(ctx['amount']/10000)}万元为万元整数倍，存在拆分嫌疑"
            },
            {
                "id": "B004", "name": "新设备首笔", "severity": "B",
                "category": "device",
                "confidence": 0.78,
                "check": lambda ctx: (
                    ctx.get("device_first", False) and ctx["amount"] >= 5000
                ),
                "detail": lambda ctx: (
                    f"首次使用新设备[{ctx.get('device_id','未知设备')}]，"
                    f"交易金额{int(ctx['amount']/10000)}万元"
                )
            },
            {
                "id": "B005", "name": "短时累计超额", "severity": "B",
                "category": "frequency",
                "confidence": 0.82,
                "check": lambda ctx: (
                    ctx.get("hourly_total", 0) > ctx.get("daily_limit", 100000) * 0.5
                ),
                "detail": lambda ctx: (
                    f"1小时内累计{int(ctx.get('hourly_total',0)/10000)}万元，"
                    f"超过日限额50%"
                )
            },
            {
                "id": "B006", "name": "敏感地区收款", "severity": "B",
                "category": "counterparty",
                "confidence": 0.88,
                "check": lambda ctx: ctx.get("counterparty_high_risk", False),
                "detail": lambda ctx: (
                    f"收款方所在地区[{ctx.get('counterparty_region','高风险地区')}]"
                    f"为洗钱高发区"
                )
            },
            {
                "id": "B007", "name": "可疑对手方行业", "severity": "B",
                "category": "counterparty",
                "confidence": 0.80,
                "check": lambda ctx: ctx.get("counterparty_sensitive", False),
                "detail": lambda ctx: (
                    f"对手方行业[{ctx.get('counterparty_industry','未知')}]"
                    f"为房地产/博彩/虚拟货币等敏感行业"
                )
            },
            {
                "id": "B008", "name": "境外网络+大额", "severity": "B",
                "category": "location",
                "confidence": 0.83,
                "check": lambda ctx: (
                    ctx.get("is_overseas", False) and ctx["amount"] >= 30000
                ),
                "detail": lambda ctx: (
                    f"使用境外网络环境，大额交易{int(ctx['amount']/10000)}万元"
                )
            },

            # ========== 🟡 C类低危规则 ==========
            {
                "id": "C001", "name": "非工作日交易", "severity": "C",
                "category": "time",
                "confidence": 0.60,
                "check": lambda ctx: ctx.get("is_weekend", False) or ctx.get("is_holiday", False),
                "detail": lambda ctx: (
                    f"交易发生在{'周末' if ctx.get('is_weekend') else '节假日'}，"
                    f"非工作日交易需关注"
                )
            },
            {
                "id": "C002", "name": "夜间小额试探", "severity": "C",
                "category": "time",
                "confidence": 0.65,
                "check": lambda ctx: (
                    ctx.get("is_night", False) and ctx["amount"] < 5000
                ),
                "detail": lambda ctx: (
                    f"夜间时段进行{int(ctx['amount'])}元小额交易，可能为试探性操作"
                )
            },
            {
                "id": "C003", "name": "交易金额异常波动", "severity": "C",
                "category": "amount",
                "confidence": 0.70,
                "check": lambda ctx: self._is_amount_anomaly(ctx),
                "detail": lambda ctx: (
                    f"交易金额较历史均值波动{int(self._get_amount_ratio(ctx)*100)}%，"
                    f"存在异常"
                )
            },
            {
                "id": "C004", "name": "首次交易对手方", "severity": "C",
                "category": "counterparty",
                "confidence": 0.55,
                "check": lambda ctx: ctx.get("counterparty_first", False),
                "detail": lambda ctx: (
                    f"与对手方[{ctx.get('counterparty','未知')}]为首次交易，"
                    f"建议关注后续行为"
                )
            },
            {
                "id": "C005", "name": "账户静默后激活", "severity": "C",
                "category": "account",
                "confidence": 0.68,
                "check": lambda ctx: ctx.get("silent_days", 0) >= 30,
                "detail": lambda ctx: (
                    f"账户{int(ctx.get('silent_days',0))}天未交易后突然激活"
                )
            },
            {
                "id": "C006", "name": "单笔接近限额", "severity": "C",
                "category": "amount",
                "confidence": 0.60,
                "check": lambda ctx: (
                    ctx.get("daily_limit", 0) > 0 and
                    ctx["amount"] >= ctx.get("daily_limit", 1) * 0.9
                ),
                "detail": lambda ctx: (
                    f"交易金额达到单笔限额的"
                    f"{int(ctx['amount']/max(ctx.get('daily_limit',1),1)*100)}" + "%"
                )
            },
            {
                "id": "C007", "name": "IP/设备频繁变更", "severity": "C",
                "category": "device",
                "confidence": 0.72,
                "check": lambda ctx: ctx.get("device_change_count", 0) >= 3,
                "detail": lambda ctx: (
                    f"24小时内设备/IP变更{int(ctx.get('device_change_count',0))}次，"
                    f"存在账户共享或被盗风险"
                )
            },
            {
                "id": "C008", "name": "短时交易频率异常", "severity": "C",
                "category": "frequency",
                "confidence": 0.70,
                "check": lambda ctx: (
                    ctx.get("hourly_count", 0) >= 5 and
                    ctx.get("hourly_count", 0) < 10
                ),
                "detail": lambda ctx: (
                    f"1小时内{int(ctx.get('hourly_count',0))}笔交易，频率偏高"
                )
            },
            {
                "id": "C009", "name": "大额充值后立即转账", "severity": "C",
                "category": "velocity",
                "confidence": 0.68,
                "check": lambda ctx: (
                    ctx.get("deposit_then_transfer", False) and ctx["amount"] >= 10000
                ),
                "detail": lambda ctx: (
                    f"充值后立即转账{int(ctx['amount']/10000)}万元，"
                    f"资金快进快出特征"
                )
            },
        ]

    # -------------------- 辅助方法 --------------------

    def _is_round_amount(self, amount: float) -> bool:
        """金额为万元整数倍"""
        return amount > 0 and amount % 10000 == 0

    def _is_amount_anomaly(self, ctx: dict) -> bool:
        """金额较历史均值波动>200%"""
        ratio = self._get_amount_ratio(ctx)
        return ratio > 2.0

    def _get_amount_ratio(self, ctx: dict) -> float:
        """获取金额波动比例"""
        avg = ctx.get("avg_amount", 0)
        if avg <= 0:
            return 0.0
        return ctx["amount"] / avg

    def _parse_time(self, time_str) -> dict:
        """解析时间描述，返回 hour / is_night / is_weekend / is_holiday"""
        result = {"hour": -1, "is_night": False, "is_weekend": False, "is_holiday": False}
        if not time_str:
            return result

        # HH:MM 格式
        m = re.search(r'(\d{1,2}):(\d{2})', str(time_str))
        if m:
            h = int(m.group(1))
            result["hour"] = h
            result["is_night"] = (h >= 22 or h < 5)
            return result

        # 中文时间描述
        night_kw = ["凌晨", "深夜", "夜间", "晚上", "夜里", "22点", "23点", "00点", "01点", "02点", "03点", "04点"]
        if any(kw in time_str for kw in night_kw):
            result["is_night"] = True
            # 尝试提取数字
            hm = re.search(r'(\d{1,2})[点时]', time_str)
            if hm:
                result["hour"] = int(hm.group(1))

        weekend_kw = ["周末", "周六", "周日", "星期天", "星期六"]
        if any(kw in time_str for kw in weekend_kw):
            result["is_weekend"] = True

        holiday_kw = ["元旦", "春节", "五一", "国庆", "清明", "端午", "中秋", "节假日"]
        if any(kw in time_str for kw in holiday_kw):
            result["is_holiday"] = True

        return result

    def _parse_amount(self, amount) -> float:
        """解析金额字符串"""
        if isinstance(amount, (int, float)):
            return float(amount)
        if not amount:
            return 0.0
        s = str(amount)
        m = re.search(r'(\d+(?:\.\d+)?)\s*万', s)
        if m:
            return float(m.group(1)) * 10000
        m = re.search(r'(\d+(?:\.\d+)?)', s)
        if m:
            return float(m.group(1))
        return 0.0

    def _build_context(self, amount=None, transaction_type=None,
                       transaction_time=None, location=None, device_change=False,
                       device_id=None, account_id=None, counterparty=None,
                       location_changed=False, history=None) -> dict:
        """构建预警检测上下文"""
        ctx = {
            "amount": self._parse_amount(amount),
            "transaction_type": transaction_type or "",
            "transaction_time": transaction_time or "",
            "location": location or "",
            "device_change": device_change,
            "device_id": device_id or "",
            "account_id": account_id or "",
            "counterparty": counterparty or "",
            "location_changed": location_changed,
            # 历史行为
            "hourly_count": 0,
            "hourly_total": 0,
            "daily_limit": 500000,
            "avg_amount": 0,
            "silent_days": 0,
            "account_days": 9999,
            "counterparty_first": False,
            "counterparty_high_risk": False,
            "counterparty_sensitive": False,
            "counterparty_region": "",
            "counterparty_industry": "",
            "is_night": False,
            "is_weekend": False,
            "is_holiday": False,
            "is_overseas": False,
            "fund_out_hours": 999,
            "multi_in": False,
            "single_out": False,
            "deposit_then_transfer": False,
            "ip_changed": False,
            "device_first": False,
            "device_change_count": 0,
            "on_risk_list": False,
            "risk_list_type": "",
        }

        # 解析时间
        if transaction_time:
            ctx.update(self._parse_time(transaction_time))

        # 从 history 合并
        if history and isinstance(history, dict):
            ctx.update(history)

        # 推断 location_changed
        if location:
            loc_lower = location.lower()
            异地_kw = ["异地", "外省", "外地", "其他省份", "不同城市"]
            for kw in 异地_kw:
                if kw in loc_lower:
                    ctx["location_changed"] = True
                    break
            if any(kw in loc_lower for kw in ["境外", "国外", "海外", "香港", "澳门", "台湾"]):
                ctx["is_overseas"] = True

        # 推断对手方敏感行业/地区
        cp = counterparty or ""
        sensitive_ind = {"房地产", "博彩", "虚拟货币", "外汇", "贵金属", "赌场", "加密货币"}
        for ind in sensitive_ind:
            if ind in cp:
                ctx["counterparty_sensitive"] = True
                ctx["counterparty_industry"] = ind
                break
        high_risk_regions = {"缅甸", "老挝", "柬埔寨", "菲律宾", "迪拜", "土耳其", "巴拿马", "开曼"}
        for reg in high_risk_regions:
            if reg in cp:
                ctx["counterparty_high_risk"] = True
                ctx["counterparty_region"] = reg
                break

        # 新对手方
        if "新客户" in cp or "新" in cp:
            ctx["counterparty_first"] = True

        # 风险名单
        risk_kw = ["制裁", "涉诈", "涉赌", "黑名单", "惩戒"]
        for kw in risk_kw:
            if kw in cp:
                ctx["on_risk_list"] = True
                ctx["risk_list_type"] = kw
                break

        return ctx

    def _compute_score(self, triggered: list[AlertRule]) -> int:
        """计算风险评分"""
        if not triggered:
            return 0
        weighted = sum(r.confidence for r in triggered)
        count = len(triggered)
        count_bonus = max(0, (count - 1) * 4)
        score = weighted * 100 + count_bonus
        return min(100, int(score))

    def _get_level(self, triggered: list[AlertRule], score: int) -> str:
        """根据触发规则等级和评分确定预警等级"""
        has_A = any(r.severity == "A" for r in triggered)
        has_B = any(r.severity == "B" for r in triggered)

        if has_A or score >= self.THRESHOLDS["red"]:
            return "红色"
        elif has_B or score >= self.THRESHOLDS["orange"]:
            return "橙色"
        elif score >= self.THRESHOLDS["yellow"]:
            return "黄色"
        return "正常"

    def _get_review_urgency(self, level: str) -> str:
        return {"红色": "高", "橙色": "中", "黄色": "低", "正常": "无"}.get(level, "无")

    def _get_actions(self, level: str, rules: list[AlertRule]) -> list[str]:
        """根据预警等级生成紧急处置建议"""
        actions = []
        severities = {r.severity for r in rules}

        if level == "红色":
            actions.extend([
                "🚨 立即拦截该笔交易",
                "📞 电话联系客户核实身份及交易目的",
                "🔒 临时冻结账户12-24小时",
                "👤 通知风控专员立即人工复核",
                "📋 记录交易详情及处置过程"
            ])
        elif level == "橙色":
            actions.extend([
                "⏸️ 延迟放行该笔交易",
                "📋 提交人工复核工单",
                "🔍 核查设备/IP/位置异常",
                "📞 可选择电话回访客户确认"
            ])
        elif level == "黄色":
            actions.extend([
                "👀 标记为关注交易",
                "📊 纳入风控监控清单",
                "📝 记录异常特征备查"
            ])
        else:
            actions.append("✅ 正常通过，保持常规监控")

        # 按类别补充
        categories = {r.category for r in rules}
        if "location" in categories:
            actions.append("🔎 核查登录地与交易地差异")
        if "device" in categories:
            actions.append("📱 核实设备变更是否客户本人操作")
        if "velocity" in categories:
            actions.append("💰 调取账户资金流水追查资金去向")

        return list(dict.fromkeys(actions))  # 去重保持顺序

    # -------------------- 公开接口 --------------------

    def alert(self, amount=None, transaction_type=None, transaction_time=None,
              location=None, device_change=False, device_id=None, account_id=None,
              counterparty=None, location_changed=None, history=None) -> FraudAlertResult:
        """
        执行实时欺诈预警

        Args:
            amount: 交易金额 (数字或字符串如"5万")
            transaction_type: 交易类型 (转账/支付/提现/消费)
            transaction_time: 交易时间 (HH:MM格式或中文描述)
            location: 地点描述 (异地/同城/境外等)
            device_change: 设备是否更换/异常
            device_id: 设备指纹ID
            account_id: 账户ID
            counterparty: 对手方描述
            location_changed: 登录地与交易地是否不同
            history: 历史行为数据字典

        Returns:
            FraudAlertResult: 预警结果
        """
        # 合并 location_changed
        if location_changed is None and location:
            loc_lower = location.lower()
            异地_kw = ["异地", "外省", "外地", "其他省份", "不同城市"]
            location_changed = any(kw in loc_lower for kw in 异地_kw)

        ctx = self._build_context(
            amount=amount,
            transaction_type=transaction_type,
            transaction_time=transaction_time,
            location=location,
            device_change=device_change,
            device_id=device_id,
            account_id=account_id,
            counterparty=counterparty,
            location_changed=bool(location_changed),
            history=history
        )

        # 执行所有规则检测
        triggered = []
        for rule in self.RULES:
            try:
                if rule["check"](ctx):
                    triggered.append(AlertRule(
                        id=rule["id"],
                        name=rule["name"],
                        severity=rule["severity"],
                        confidence=rule["confidence"],
                        category=rule["category"],
                        detail=rule["detail"](ctx)
                    ))
            except Exception:
                pass

        score = self._compute_score(triggered)
        level = self._get_level(triggered, score)
        actions = self._get_actions(level, triggered)
        review_required = level in ("红色", "橙色")
        urgency = self._get_review_urgency(level)

        # 生成摘要
        if not triggered:
            summary = "未检测到异常规则，交易正常，建议正常放行"
        else:
            severity_groups = {"A": [], "B": [], "C": []}
            for r in triggered:
                severity_groups[r.severity].append(r.name)
            
            parts = []
            if severity_groups["A"]:
                parts.append(f"高危规则[{','.join(severity_groups['A'][:2])}]")
            if severity_groups["B"]:
                parts.append(f"中危规则[{','.join(severity_groups['B'][:2])}]")
            if severity_groups["C"]:
                parts.append(f"低危规则{len(severity_groups['C'])}条")
            
            summary = f"{level}预警：{', '.join(parts)}，共{len(triggered)}条规则触发"
            if level != "正常":
                if level == "红色":
                    summary += "，建议立即拦截并人工复核"
                elif level == "橙色":
                    summary += "，建议延迟放行并复核"

        return FraudAlertResult(
            level=level,
            score=score,
            rules=triggered,
            actions=actions,
            review_required=review_required,
            review_urgency=urgency,
            summary=summary
        )

    def alert_from_nl(self, nl_text: str) -> FraudAlertResult:
        """
        从自然语言描述执行预警
        示例: "fraud_alert 交易金额5万 时间22:00 地点异地 设备更换"
        """
        amount = self._parse_amount(nl_text)

        # 解析时间
        time_m = re.search(r'(\d{1,2}):(\d{2})', nl_text)
        time_str = None
        if time_m:
            time_str = f"{time_m.group(1)}:{time_m.group(2)}"
        else:
            night_kw = ["凌晨", "深夜", "夜间", "晚上", "22点", "23点", "00点", "01点", "02点"]
            for kw in night_kw:
                if kw in nl_text:
                    hm = re.search(r'(\d{1,2})[点时]', nl_text)
                    time_str = f"{hm.group(1)}:00" if hm else "22:00"
                    break

        # 解析地点
        location = None
        loc_kw = ["异地", "同城", "境外", "外地", "外省", "国外", "海外"]
        for kw in loc_kw:
            if kw in nl_text:
                location = kw
                break

        # 解析设备更换
        device_change = any(kw in nl_text for kw in ["设备更换", "新设备", "设备异常", "换设备"])

        # 解析交易类型
        type_kw = ["转账", "支付", "提现", "汇款", "充值", "消费"]
        transaction_type = "转账"
        for kw in type_kw:
            if kw in nl_text:
                transaction_type = kw
                break

        return self.alert(
            amount=amount,
            transaction_type=transaction_type,
            transaction_time=time_str,
            location=location,
            device_change=device_change,
        )
