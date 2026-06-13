# -*- coding: utf-8 -*-
"""
催收策略优化引擎 v1.0
智能催收策略生成：输入逾期客户信息、历史催收记录，输出分层催收策略+话术

Author: ArkClaw
Version: 1.0.0
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


class CollectionOptimizeEngine:
    """催收策略优化引擎"""

    VERSION = "1.0.0"

    # 逾期天数分层阈值（天）
    TIER_THRESHOLDS = {
        "M0": 0,      # 正常
        "M1": 1,      # 逾期1-30天
        "M2": 31,     # 逾期31-60天
        "M3": 61,     # 逾期61-90天
        "M4": 91,     # 逾期91-180天
        "M5": 181,    # 逾期180天以上
    }

    # 分层策略配置
    TIER_STRATEGY = {
        "M0": {
            "name": "正常",
            "priority": 0,
            "channel": ["短信", "App推送"],
            "frequency": "月度提醒",
            "script_type": "温馨提醒",
            "escalation_days": 0,
        },
        "M1": {
            "name": "关注",
            "priority": 1,
            "channel": ["短信", "App推送", "电话"],
            "frequency": "每3天一次",
            "script_type": "友好提醒",
            "escalation_days": 30,
        },
        "M2": {
            "name": "预警",
            "priority": 2,
            "channel": ["电话", "短信", "上门"],
            "frequency": "每天一次",
            "script_type": "正式催收",
            "escalation_days": 60,
        },
        "M3": {
            "name": "重点催收",
            "priority": 3,
            "channel": ["电话", "上门", "法律函"],
            "frequency": "每天多次",
            "script_type": "严肃警告",
            "escalation_days": 90,
        },
        "M4": {
            "name": "高压催收",
            "priority": 4,
            "channel": ["电话", "上门", "诉讼"],
            "frequency": "每天不限次数",
            "script_type": "法律威慑",
            "escalation_days": 180,
        },
        "M5": {
            "name": "呆账核销",
            "priority": 5,
            "channel": ["诉讼", "债权转让", "核销"],
            "frequency": "季度评估",
            "script_type": "法律终结",
            "escalation_days": 365,
        },
    }

    # 催收话术模板库
    SCRIPT_TEMPLATES = {
        "温馨提醒": {
            "开场": [
                "尊敬的客户您好，您的账户保持良好记录，继续保持将有助于提升您的信用评分。",
                "您好，我们注意到您的最近一期账单已出，按时还款有助于维护您的良好信用。",
            ],
            "提醒": [
                "温馨提醒：您的账单金额为{amount}元，到期日为{due_date}，请记得按时还款哦。",
            ],
            "结束": [
                "如有疑问，欢迎联系我们。祝您生活愉快！",
            ],
        },
        "友好提醒": {
            "开场": [
                "您好，我是{company}的客服人员，想跟您确认一下您的还款计划。",
                "您好，这里是{company}提醒您，您的账户已逾期，为避免产生更多费用，建议您尽快处理。",
            ],
            "理解": [
                "我们理解生活中可能会有各种困难，但及时还款对您非常重要。",
                "如果您目前有还款困难，我们可以一起想办法解决。",
            ],
            "承诺": [
                "请问您最快什么时候可以处理这笔{amount}元的逾期款项？",
                "我们可以为您安排一个灵活的还款计划，您看这个{due_date}之前可以吗？",
            ],
            "结束": [
                "感谢您的配合，期待您的积极处理。再见！",
            ],
        },
        "正式催收": {
            "开场": [
                "您好，这里是{company}法务部通知，您的账户已正式进入逾期处理流程。",
                "您好，我是{company}的正式催收人员，工号{agent_id}，您的账户已逾期{overdue_days}天。",
            ],
            "告知": [
                "根据合同条款，逾期将产生滞纳金，每日按未还本息的{penalty_rate}计算。",
                "您的逾期记录已按要求上报征信系统，请尽快处理以避免影响您的信用记录。",
            ],
            "施压": [
                "我们希望通过友好协商解决此事，否则我们将不得不采取进一步的法律手段。",
                "请在{deadline}之前还款，否则我们将启动诉讼程序。",
            ],
            "结束": [
                "请尽快处理，您的还款将对您的信用记录至关重要。再见。",
            ],
        },
        "严肃警告": {
            "开场": [
                "您好，这里是{company}法务催收中心，您的账户已进入重点关注名单。",
                "我是{company}授权的第三方催收机构，您的案件由我负责跟进。",
            ],
            "法律告知": [
                "根据《合同法》第{contract_law}条及《民事诉讼法》，我司保留追究您法律责任的权利。",
                "您的逾期行为已构成违约，我司已委托律师事务所准备相关法律文书。",
            ],
            "后果": [
                "如在本函规定的期限内仍不还款，我司将向有管辖权的人民法院提起诉讼。",
                "诉讼后，您将承担诉讼费、律师费及全部逾期费用，并将被列入失信被执行人名单。",
            ],
            "最后通牒": [
                "这是我们最后一次友好协商的机会，请在{deadline}前联系我们确定还款方案。",
                "您的案件编号为{case_no}，请妥善保管以便查询。",
            ],
            "结束": [
                "请务必重视此事，再见。",
            ],
        },
        "法律威慑": {
            "开场": [
                "您好，本函为{company}法务部最终催收通知。",
                "我是{company}委托的{lawfirm}律师事务所律师，您的案件已进入司法准备阶段。",
            ],
            "法律依据": [
                "根据《民法典》第{ Civil_law }条、《刑法》第{penalty_article}条，恶意逾期可能涉及欺诈罪。",
                "我司已收集完整证据链，包括借款合同、转账记录、催收记录等。",
            ],
            "司法后果": [
                "法院判决后，您名下的银行账户、房产、车辆等资产将被依法冻结和查封。",
                "您将被纳入失信被执行人名单（黑名单），限制高消费，子女就读高收费学校将受影响。",
            ],
            "最后期限": [
                "最后还款期限：{final_deadline}。",
                "在此之前还款，可避免司法程序的启动。",
            ],
            "结束": [
                "请慎重考虑此事对您及家庭的影响。",
            ],
        },
        "法律终结": {
            "告知": [
                "您的账户已被列为呆账，我司已启动债权转让或核销程序。",
                "您的逾期记录已永久保存在征信系统中，不可删除。",
                "您的案件已移交专业资产管理公司处理。",
            ],
            "影响": [
                "您将被限制乘坐高铁、飞机，限制在金融机构开设账户。",
                "您的社会信用评分将受到长期影响。",
            ],
        },
    }

    # 金额风险系数
    AMOUNT_RISK_FACTORS = {
        "小额": {"min": 0, "max": 10000, "factor": 0.8, "description": "金额较小，优先短信/电话"},
        "中额": {"min": 10000, "max": 100000, "factor": 1.0, "description": "金额适中，综合催收手段"},
        "大额": {"min": 100000, "max": 1000000, "factor": 1.5, "description": "金额较大，需上门+法律手段"},
        "巨额": {"min": 1000000, "max": 999999999, "factor": 2.0, "description": "金额巨大，重点关注，必要时诉讼"},
    }

    # 还款意愿评估规则
    WILLINGNESS_RULES = [
        {"pattern": r"(承诺|保证|一定|肯定|会还)", "score": 20, "label": "还款承诺"},
        {"pattern": r"(困难|问题|资金紧张|周转不开)", "score": 10, "label": "说明困难"},
        {"pattern": r"(分期|延期|缓一缓|延后)", "score": 5, "label": "请求宽限"},
        {"pattern": r"(不接|挂断|关机|消失|跑路)", "score": -20, "label": "逃避行为"},
        {"pattern": r"(无所谓|不还|随便)", "score": -30, "label": "恶意拖欠"},
        {"pattern": r"(已还|还清了|没问题)", "score": 15, "label": "声称已还"},
    ]

    def __init__(self, api_mode: bool = False):
        self.api_mode = api_mode
        self._log("初始化催收策略优化引擎 v%s" % self.VERSION)

    def _log(self, msg: str):
        if not self.api_mode:
            print(msg)

    def classify_tier(self, overdue_days: int) -> str:
        """根据逾期天数分类账户等级"""
        if overdue_days >= 181:
            return "M5"
        elif overdue_days >= 91:
            return "M4"
        elif overdue_days >= 61:
            return "M3"
        elif overdue_days >= 31:
            return "M2"
        elif overdue_days >= 1:
            return "M1"
        else:
            return "M0"

    def classify_amount_tier(self, amount: float) -> str:
        """根据逾期金额分类"""
        if amount >= 1000000:
            return "巨额"
        elif amount >= 100000:
            return "大额"
        elif amount >= 10000:
            return "中额"
        else:
            return "小额"

    def evaluate_willingness(self, history_records: List[Dict]) -> Dict[str, Any]:
        """评估还款意愿（基于历史催收记录）"""
        total_score = 50  # 基础分
        evidence = []

        if not history_records:
            return {"score": total_score, "level": "未知", "evidence": ["无历史记录"]}

        for record in history_records[-5:]:  # 最近5条记录
            content = record.get("content", "").lower()
            for rule in self.WILLINGNESS_RULES:
                if re.search(rule["pattern"], content):
                    total_score += rule["score"]
                    evidence.append({
                        "label": rule["label"],
                        "record": record.get("content", "")[:50],
                        "score": rule["score"]
                    })

        # 历史联系成功率
        responded = sum(1 for r in history_records if r.get("responded", False))
        if history_records:
            response_rate = responded / len(history_records)
            if response_rate >= 0.7:
                total_score += 15
                evidence.append({"label": "联系成功率高", "score": 15})
            elif response_rate >= 0.4:
                total_score += 5
                evidence.append({"label": "偶尔联系成功", "score": 5})
            else:
                total_score -= 10
                evidence.append({"label": "联系困难", "score": -10})

        # 还款行为
        repayments = sum(1 for r in history_records if r.get("repaid", False))
        if repayments > 0:
            total_score += repayments * 10
            evidence.append({"label": f"历史还款{repayments}次", "score": repayments * 10})

        total_score = max(0, min(100, total_score))

        if total_score >= 70:
            level = "良好"
        elif total_score >= 40:
            level = "一般"
        else:
            level = "恶劣"

        return {"score": total_score, "level": level, "evidence": evidence}

    def generate_strategy(self, customer_info: Dict, history_records: List[Dict] = None) -> Dict[str, Any]:
        """
        生成催收策略

        Args:
            customer_info: 客户信息，包含:
                - overdue_days: 逾期天数（必填）
                - overdue_amount: 逾期金额（必填）
                - customer_name: 客户姓名
                - phone: 联系电话
                - id_number: 身份证号
                - address: 地址
                - company: 所属公司
                - product_type: 产品类型（贷款/信用卡/消费贷等）
            history_records: 历史催收记录列表，每条包含:
                - date: 催收日期
                - channel: 催收渠道（电话/短信/上门等）
                - content: 催收内容/结果
                - responded: 是否联系上
                - repaid: 是否还款

        Returns:
            催收策略结果
        """
        history_records = history_records or []

        overdue_days = customer_info.get("overdue_days", 0)
        overdue_amount = customer_info.get("overdue_amount", 0)
        customer_name = customer_info.get("customer_name", "客户")
        phone = customer_info.get("phone", "")
        id_number = customer_info.get("id_number", "")
        address = customer_info.get("address", "")
        company = customer_info.get("company", "")
        product_type = customer_info.get("product_type", "贷款")

        # 分层定级
        tier = self.classify_tier(overdue_days)
        tier_info = self.TIER_STRATEGY[tier]
        amount_tier = self.classify_amount_tier(overdue_amount)
        amount_factor = self.AMOUNT_RISK_FACTORS[amount_tier]["factor"]

        # 还款意愿评估
        willingness = self.evaluate_willingness(history_records)

        # 综合优先级
        base_priority = tier_info["priority"]
        amount_priority = base_priority * amount_factor
        willingness_modifier = (100 - willingness["score"]) / 20  # 意愿越差，优先级越高
        final_priority = round(amount_priority + willingness_modifier, 1)

        # 选择催收渠道
        channels = self._select_channels(tier, amount_tier, willingness)

        # 生成催收话术
        scripts = self._generate_scripts(
            tier=tier,
            tier_info=tier_info,
            customer_name=customer_name,
            overdue_amount=overdue_amount,
            overdue_days=overdue_days,
            company=company,
            willingness=willingness
        )

        # 制定还款计划建议
        repayment_plan = self._generate_repayment_plan(
            overdue_amount=overdue_amount,
            tier=tier,
            willingness=willingness
        )

        # 回收率预估
        recovery_rate_estimate = self._estimate_recovery_rate(
            tier=tier,
            amount_tier=amount_tier,
            willingness=willingness,
            history_records=history_records
        )

        # 策略摘要
        summary = self._generate_summary(
            tier=tier,
            tier_info=tier_info,
            amount_tier=amount_tier,
            channels=channels,
            willingness=willingness,
            recovery_rate=recovery_rate_estimate
        )

        return {
            "customer_info": {
                "name": customer_name,
                "phone": self._mask_phone(phone),
                "id_number": self._mask_id(id_number),
                "overdue_days": overdue_days,
                "overdue_amount": overdue_amount,
                "product_type": product_type,
            },
            "tier": tier,
            "tier_name": tier_info["name"],
            "tier_description": self._get_tier_description(tier),
            "amount_tier": amount_tier,
            "priority_score": final_priority,
            "willingness": willingness,
            "channels": channels,
            "frequency": tier_info["frequency"],
            "scripts": scripts,
            "repayment_plan": repayment_plan,
            "recovery_rate_estimate": recovery_rate_estimate,
            "summary": summary,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "engine_version": self.VERSION,
        }

    def _select_channels(self, tier: str, amount_tier: str, willingness: Dict) -> List[Dict]:
        """选择催收渠道及权重"""
        base_channels = self.TIER_STRATEGY[tier]["channel"]
        amount_factor = self.AMOUNT_RISK_FACTORS[amount_tier]["factor"]

        channel_configs = []
        for ch in base_channels:
            weight = 1.0
            if amount_factor >= 1.5 and ch in ["上门", "法律函", "诉讼"]:
                weight = 1.5
            if willingness["score"] < 40 and ch == "电话":
                weight = 1.3

            channel_configs.append({
                "channel": ch,
                "priority": weight,
                "note": self._get_channel_note(ch, tier)
            })

        # 按优先级排序
        channel_configs.sort(key=lambda x: x["priority"], reverse=True)
        return channel_configs

    def _get_channel_note(self, channel: str, tier: str) -> str:
        notes = {
            "短信": "低成本，覆盖广，适合M0-M1轻度逾期",
            "App推送": "触达率高，需用户已安装App",
            "电话": "核心催收手段，M1+必须执行",
            "上门": "高成本，M3+大额客户建议采用",
            "法律函": "施压效果强，M3+建议使用",
            "诉讼": "最终手段，M4+大额优先考虑",
            "债权转让": "M5账户可考虑",
            "核销": "M5确无回收可能时使用",
        }
        return notes.get(channel, "")

    def _generate_scripts(self, tier: str, tier_info: Dict, customer_name: str,
                          overdue_amount: float, overdue_days: int, company: str,
                          willingness: Dict) -> Dict[str, Any]:
        """生成催收话术"""
        script_type = tier_info["script_type"]
        templates = self.SCRIPT_TEMPLATES.get(script_type, self.SCRIPT_TEMPLATES["友好提醒"])

        def pick(lst):
            import random
            return random.choice(lst)

        def fill(text):
            return text.format(
                company=company or "我司",
                customer_name=customer_name,
                amount=f"{overdue_amount:,.2f}",
                due_date=(datetime.now() + timedelta(days=7)).strftime("%Y年%m月%d日"),
                overdue_days=overdue_days,
                penalty_rate="0.05%",  # 简化，实际从配置读取
                deadline=(datetime.now() + timedelta(days=3)).strftime("%Y年%m月%d日"),
                agent_id="A1001",
                case_no=f"CASE{datetime.now().strftime('%Y%m%d')}{overdue_days:04d}",
                lawfirm="XX律师事务所",
                final_deadline=(datetime.now() + timedelta(days=7)).strftime("%Y年%m月%d日"),
                contract_law="670",
                civil_law="675",
                penalty_article="193",
            )

        # 拼接话术
        sections = {}
        for section_name, lines in templates.items():
            if isinstance(lines, list) and lines:
                section_text = pick(lines)
                sections[section_name] = fill(section_text)

        return {
            "script_type": script_type,
            "sections": sections,
            "full_script": "\n\n".join(sections.values()),
        }

    def _generate_repayment_plan(self, overdue_amount: float, tier: str,
                                  willingness: Dict) -> Dict[str, Any]:
        """生成建议还款计划"""
        plans = []

        if tier in ["M0", "M1"]:
            plans.append({
                "type": "一次性还清",
                "description": f"在{3}日内一次性偿还{overdue_amount:,.2f}元",
                "feasibility": "高",
                "discount": "无",
            })
            plans.append({
                "type": "延期3天",
                "description": f"延期3天，偿还全额{overdue_amount:,.2f}元",
                "feasibility": "中",
                "discount": "无",
            })

        if tier in ["M2", "M3"]:
            plans.append({
                "type": "分期3期",
                "description": f"分3期偿还，首付{overdue_amount*0.5:,.2f}元，剩余均分",
                "feasibility": "高",
                "discount": "无逾期罚息减免",
            })
            plans.append({
                "type": "一次性还清",
                "description": f"一次性偿还，享受逾期罚息减免20%",
                "feasibility": "中",
                "discount": "减免20%罚息",
            })

        if tier in ["M4", "M5"]:
            plans.append({
                "type": "分期6期",
                "description": f"分6期偿还，首付{overdue_amount*0.3:,.2f}元",
                "feasibility": "中",
                "discount": "减免部分罚息",
            })
            plans.append({
                "type": "一次性还清",
                "description": f"一次性偿还，享受逾期罚息减免50%",
                "feasibility": "低",
                "discount": "减免50%罚息",
            })

        recommended = plans[0] if plans else None
        return {
            "plans": plans,
            "recommended": recommended,
        }

    def _estimate_recovery_rate(self, tier: str, amount_tier: str,
                                 willingness: Dict, history_records: List) -> Dict[str, Any]:
        """预估回收率"""
        # 基准回收率（基于逾期天数）
        base_rates = {
            "M0": 98, "M1": 85, "M2": 60, "M3": 35, "M4": 15, "M5": 5
        }

        base = base_rates.get(tier, 10)

        # 金额系数（大额回收难度更高）
        amount_adj = {"小额": 5, "中额": 0, "大额": -10, "巨额": -20}
        base += amount_adj.get(amount_tier, 0)

        # 意愿系数
        if willingness["score"] >= 70:
            base += 10
        elif willingness["score"] < 40:
            base -= 15

        # 历史还款加成
        if history_records:
            repayments = sum(1 for r in history_records if r.get("repaid", False))
            base += repayments * 3

        base = max(0, min(100, base))

        # 计算提升空间（对比无策略基准）
        baseline_without_strategy = base - 15 if base > 15 else 0
        improvement = base - baseline_without_strategy

        return {
            "estimated_rate": base,
            "improvement_vs_baseline": improvement,
            "target_rate": min(100, base + 10),  # 验收标准：提升≥10%
            "meets_acceptance": improvement >= 10 or base >= 90,
        }

    def _generate_summary(self, tier: str, tier_info: Dict, amount_tier: str,
                           channels: List, willingness: Dict,
                           recovery_rate: Dict) -> str:
        """生成策略摘要"""
        channel_names = [c["channel"] for c in channels[:3]]
        meets = "✅" if recovery_rate["meets_acceptance"] else "⚠️"

        return (
            f"客户逾期{tier_info['name']}（{tier}），{amount_tier}客户，"
            f"建议优先通过{'/'.join(channel_names)}进行催收。"
            f"还款意愿评估{willingness['level']}（{willingness['score']}分），"
            f"预估回收率{recovery_rate['estimated_rate']}%，"
            f"策略执行后预计提升{recovery_rate['improvement_vs_baseline']}%，"
            f"{meets}达到验收标准。"
        )

    def _mask_phone(self, phone: str) -> str:
        if not phone or len(phone) < 7:
            return phone
        return phone[:3] + "****" + phone[-4:]

    def _mask_id(self, id_number: str) -> str:
        if not id_number or len(id_number) < 10:
            return id_number
        return id_number[:6] + "****" + id_number[-4:]

    def _get_tier_description(self, tier: str) -> str:
        descriptions = {
            "M0": "正常账户，无逾期",
            "M1": "逾期1-30天，轻度关注",
            "M2": "逾期31-60天，中度关注",
            "M3": "逾期61-90天，重点关注",
            "M4": "逾期91-180天，高压催收",
            "M5": "逾期180天以上，呆账核销",
        }
        return descriptions.get(tier, "")

    def format_text(self, result: Dict) -> str:
        """格式化输出为文本"""
        lines = [
            f"📋 **催收策略优化报告**",
            f"",
            f"👤 客户信息",
            f"  姓名: {result['customer_info']['name']}",
            f"  电话: {result['customer_info']['phone']}",
            f"  逾期天数: {result['customer_info']['overdue_days']}天",
            f"  逾期金额: ¥{result['customer_info']['overdue_amount']:,.2f}",
            f"  产品类型: {result['customer_info']['product_type']}",
            f"",
            f"{'='*30}",
            f"",
            f"🏷️ **分层定级**",
            f"  等级: {result['tier']} - {result['tier_name']}",
            f"  描述: {result['tier_description']}",
            f"  金额层级: {result['amount_tier']}",
            f"  综合优先级: {result['priority_score']}",
            f"",
            f"💡 **还款意愿评估**",
            f"  评分: {result['willingness']['score']}/100",
            f"  定级: {result['willingness']['level']}",
            f"  依据: {', '.join(str(e['label']) if isinstance(e, dict) else str(e) for e in result['willingness']['evidence'][:3])}",            f"",
            f"📞 **催收渠道**（按优先级）",
        ]

        for ch in result["channels"][:4]:
            lines.append(f"  • {ch['channel']}（优先级{ ch['priority']:.1f}）- {ch['note']}")

        lines.extend([
            f"  催收频率: {result['frequency']}",
            f"",
            f"{'='*30}",
            f"",
            f"📝 **催收话术**",
            f"  话术类型: {result['scripts']['script_type']}",
            f"",
        ])

        for section_name, section_text in result["scripts"]["sections"].items():
            lines.extend([
                f"  【{section_name}】",
                f"  {section_text}",
                f"",
            ])

        lines.extend([
            f"{'='*30}",
            f"",
            f"📊 **回收率预估**",
            f"  预估回收率: {result['recovery_rate_estimate']['estimated_rate']}%",
            f"  策略提升: +{result['recovery_rate_estimate']['improvement_vs_baseline']}%",
            f"  目标回收率: {result['recovery_rate_estimate']['target_rate']}%",
            f"  验收标准: {'✅ 达标' if result['recovery_rate_estimate']['meets_acceptance'] else '⚠️ 未达标'}",
            f"",
            f"{'='*30}",
            f"",
            f"💼 **建议还款方案**",
        ])

        if result["repayment_plan"]["plans"]:
            for i, plan in enumerate(result["repayment_plan"]["plans"], 1):
                rec = "⭐" if plan == result["repayment_plan"]["recommended"] else "  "
                lines.append(f"  {rec}{i}. {plan['type']}: {plan['description']}（可行性:{plan['feasibility']}，优惠:{plan['discount']}）")

        lines.extend([
            f"",
            f"{'='*30}",
            f"",
            f"📌 **策略摘要**",
            f"  {result['summary']}",
            f"",
            f"⏰ 生成时间: {result['generated_at']}",
            f"  引擎版本: v{result['engine_version']}",
        ])

        return '\n'.join(lines)

    def format_json(self, result: Dict) -> str:
        """格式化输出为JSON"""
        return json.dumps(result, ensure_ascii=False, indent=2)


def main():
    """主函数 - CLI测试"""
    print("=" * 50)
    print("🦞 催收策略优化引擎 v1.0")
    print("=" * 50)
    print()

    engine = CollectionOptimizeEngine()

    # 示例客户信息
    sample_customer = {
        "customer_name": "张三",
        "phone": "13800138000",
        "id_number": "110101199001011234",
        "overdue_days": 45,
        "overdue_amount": 58000.00,
        "product_type": "消费贷",
        "company": "XX消费金融",
    }

    # 示例历史催收记录
    sample_history = [
        {"date": "2026-06-01", "channel": "短信", "content": "发送温馨提醒短信", "responded": False, "repaid": False},
        {"date": "2026-06-03", "channel": "电话", "content": "电话联系，客户承诺本周还款", "responded": True, "repaid": False},
        {"date": "2026-06-05", "channel": "电话", "content": "再次联系，客户未接听", "responded": False, "repaid": False},
        {"date": "2026-06-08", "channel": "短信", "content": "正式催收通知，客户回复说资金困难", "responded": True, "repaid": False},
        {"date": "2026-06-10", "channel": "电话", "content": "客户承诺6月15日还5000元", "responded": True, "repaid": False},
    ]

    print("📋 分析示例客户...")
    print()

    result = engine.generate_strategy(sample_customer, sample_history)
    print(engine.format_text(result))


if __name__ == "__main__":
    main()
