"""
厅堂智能分流引擎
Lobby Routing Engine - 银行网点智能客户分流系统
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class CustomerProfile:
    """客户画像"""
    age: int
    business_type: str
    wait_time: int  # 已等候分钟数
    vip: bool
    is_first_visit: bool = False
    has_disability: bool = False

    def __post_init__(self):
        if self.business_type:
            self.business_type = self.business_type.strip()


@dataclass
class RoutingResult:
    """分流结果"""
    recommended_counter: str
    counter_description: str
    estimated_wait_minutes: int
    wait_queue_count: int
    recommended_products: List[str]
    service_priority: int  # 1=最高, 5=最低
    congestion_level: str  # green/yellow/orange/red
    congestion_advice: str
    movement_suggestion: str
    alternative_routes: List[Dict[str, str]]
    reasoning: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recommended_counter": self.recommended_counter,
            "counter_description": self.counter_description,
            "estimated_wait_minutes": self.estimated_wait_minutes,
            "wait_queue_count": self.wait_queue_count,
            "recommended_products": self.recommended_products,
            "service_priority": self.service_priority,
            "congestion_level": self.congestion_level,
            "congestion_advice": self.congestion_advice,
            "movement_suggestion": self.movement_suggestion,
            "alternative_routes": self.alternative_routes,
            "reasoning": self.reasoning,
        }

    def __str__(self) -> str:
        level_emoji = {"green": "🟢", "yellow": "🟡", "orange": "🟠", "red": "🔴"}
        priority_label = {1: "最高", 2: "高", 3: "中", 4: "较低", 5: "普通"}
        emoji = level_emoji.get(self.congestion_level, "⚪")

        lines = [
            f"📋 【智能分流方案】",
            f"",
            f"🏧 推荐窗口：{self.recommended_counter}",
            f"   {self.counter_description}",
            f"",
            f"⏱️  预计等候：约 {self.estimated_wait_minutes} 分钟（当前排队 {self.wait_queue_count} 人）",
            f"🎯 服务优先级：{priority_label.get(self.service_priority, '普通')}",
            f"",
            f"{emoji} 拥堵等级：{self.congestion_advice}",
            f"",
            f"🚶 动线建议：{self.movement_suggestion}",
            f"",
            f"💡 推荐产品：{', '.join(self.recommended_products) if self.recommended_products else '暂无'}",
            f"",
        ]
        if self.alternative_routes:
            lines.append("🔄 备选方案：")
            for alt in self.alternative_routes:
                lines.append(f"   • {alt['counter']}：{alt['reason']}")
        lines.append(f"\n📝 决策依据：{self.reasoning}")
        return "\n".join(lines)


class LobbyRoutingEngine:
    """厅堂智能分流引擎"""

    # 业务类型关键词映射
    BUSINESS_KEYWORDS = {
        "存款": ["存款", "存钱", "存折", "储蓄"],
        "取款": ["取款", "取钱", "提现"],
        "转账": ["转账", "汇款", "汇款", "跨行转账"],
        "理财": ["理财", "基金", "投资", "理财产品", "购买理财"],
        "信用卡": ["信用卡", "还卡", "卡还款", "信用卡业务"],
        "开户": ["开户", "新开户", "办卡", "开账户"],
        "查询": ["查询", "查余额", "查流水", "打印", "明细"],
        "挂失": ["挂失", "补卡", "密码重置"],
        "缴费": ["缴费", "水电费", "话费充值", "生活缴费"],
        "外汇": ["外汇", "购汇", "结汇", "美元", "港币"],
        "贷款": ["贷款", "借款", "信贷", "房贷"],
    }

    # 各类柜口配置
    COUNTER_CONFIG = {
        "现金柜口": {
            "keywords": ["现金", "存款", "取款", "存折", "挂失", "密码", "开户"],
            "avg_duration": 5,  # 平均办理时长（分钟）
            "suitable_for": ["老年人", "现金业务", "复杂业务"],
            "vip_suitable": False,
        },
        "非现金柜口": {
            "keywords": ["转账", "汇款", "信用卡", "电子银行", "查询", "打印", "缴费"],
            "avg_duration": 3,
            "suitable_for": ["中年人", "转账业务", "常规业务"],
            "vip_suitable": False,
        },
        "自助设备": {
            "keywords": ["查询", "转账", "缴费", "打印", "简单"],
            "avg_duration": 2,
            "suitable_for": ["年轻人", "简单业务", "快速业务"],
            "vip_suitable": False,
        },
        "理财室": {
            "keywords": ["理财", "基金", "投资", "大额", "资产配置"],
            "avg_duration": 15,
            "suitable_for": ["有理财需求客户", "高净值客户"],
            "vip_suitable": True,
        },
        "贵宾室": {
            "keywords": ["贵宾", "VIP", "私密", "大额存款", "私人银行业务"],
            "avg_duration": 10,
            "suitable_for": ["VIP客户", "私密业务需求"],
            "vip_suitable": True,
        },
        "手机银行指导台": {
            "keywords": ["手机银行", "APP", "网上银行", "不会用", "指导", "开通"],
            "avg_duration": 5,
            "suitable_for": ["需要指导的客户", "手机银行业务"],
            "vip_suitable": False,
        },
    }

    # 等待时间与拥堵等级映射（每窗口排队人数）
    CONGESTION_THRESHOLDS = {
        "green": {"max": 5, "advice": "畅通，无需等待太久"},
        "yellow": {"max": 10, "advice": "繁忙，建议耐心等候或尝试自助设备"},
        "orange": {"max": 15, "advice": "拥挤，建议引导至人少的窗口或启用弹性窗口"},
        "red": {"max": float("inf"), "advice": "严重拥堵，建议全员上岗并引导客户使用自助/手机银行"},
    }

    # 优先级基准（数值越小优先级越高）
    PRIORITY_RULES = [
        ("vip", True, -2),           # VIP提升2级
        ("age >= 70", None, -1),     # 70岁以上老人提升1级
        ("age >= 60", None, -1),     # 60岁以上提升1级
        ("wait_time >= 30", None, -2),  # 等候超过30分钟提升2级
        ("wait_time >= 15", None, -1),  # 等候超过15分钟提升1级
        ("has_disability", True, -2),   # 残障人士提升2级
    ]

    def __init__(self, queue_snapshots: Optional[Dict[str, int]] = None):
        """
        初始化分流引擎
        
        Args:
            queue_snapshots: 实时队列快照 {"现金柜口": 3, "非现金柜口": 5, ...}
        """
        self.queue_snapshots = queue_snapshots or self._default_queues()

    def _default_queues(self) -> Dict[str, int]:
        """默认队列状态（模拟数据）"""
        return {
            "现金柜口": 4,
            "非现金柜口": 6,
            "自助设备": 2,
            "理财室": 1,
            "贵宾室": 0,
            "手机银行指导台": 1,
        }

    def _classify_business(self, business_text: str) -> str:
        """根据文本分类业务类型"""
        business_text = business_text.lower()
        for biz_type, keywords in self.BUSINESS_KEYWORDS.items():
            for kw in keywords:
                if kw in business_text:
                    return biz_type
        return "其他"

    def _match_counter(self, customer: CustomerProfile) -> List[tuple]:
        """匹配最适合的柜口，返回[(柜口, 匹配度, 原因), ...]"""
        matches = []
        biz = customer.business_type

        for counter, config in self.COUNTER_CONFIG.items():
            score = 0
            reasons = []

            # 业务类型匹配
            for kw in config["keywords"]:
                if kw in biz:
                    score += 3
                    reasons.append(f"业务匹配：{kw}")

            # 年龄适配
            if customer.age >= 60:
                if counter == "现金柜口":
                    score += 2
                    reasons.append("老年人适合人工柜口")
                elif counter in ["自助设备", "手机银行指导台"]:
                    score -= 1
                    reasons.append("老年客户对自助设备不熟悉")

            # VIP适配
            if customer.vip:
                if counter in ["贵宾室", "理财室"]:
                    score += 5
                    reasons.append("VIP专属窗口")
                elif counter in ["现金柜口", "非现金柜口"]:
                    score -= 2
                    reasons.append("VIP可优先选择专属窗口")

            # 等候时间触发快速通道
            if customer.wait_time >= 20 and counter not in ["贵宾室", "理财室"]:
                # 长时间等候客户优先推荐人少的窗口
                queue_count = self.queue_snapshots.get(counter, 0)
                if queue_count <= 2:
                    score += 3
                    reasons.append("快速通道：排队人少")

            if score > 0:
                matches.append((counter, score, "; ".join(reasons)))

        # 按匹配度排序
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

    def _calculate_priority(self, customer: CustomerProfile, base: int = 3) -> int:
        """计算服务优先级（1=最高, 5=最低）"""
        priority = base
        for rule, condition, delta in self.PRIORITY_RULES:
            if rule == "vip" and condition == customer.vip:
                priority += delta
            elif rule == "age >= 70" and customer.age >= 70:
                priority += delta
            elif rule == "age >= 60" and customer.age >= 60:
                priority += delta
            elif rule == "wait_time >= 30" and customer.wait_time >= 30:
                priority += delta
            elif rule == "wait_time >= 15" and customer.wait_time >= 15:
                priority += delta
            elif rule == "has_disability" and condition == customer.has_disability:
                priority += delta
        return max(1, min(5, priority))

    def _estimate_wait(self, counter: str, avg_duration: Optional[int] = None) -> tuple:
        """估算等待时间和队列人数"""
        queue_count = self.queue_snapshots.get(counter, 0)
        duration = avg_duration or self.COUNTER_CONFIG.get(counter, {}).get("avg_duration", 5)
        wait_minutes = queue_count * duration
        return wait_minutes, queue_count

    def _get_congestion_level(self, queue_count: int) -> tuple:
        """获取拥堵等级"""
        if queue_count <= 5:
            return "green", self.CONGESTION_THRESHOLDS["green"]["advice"]
        elif queue_count <= 10:
            return "yellow", self.CONGESTION_THRESHOLDS["yellow"]["advice"]
        elif queue_count <= 15:
            return "orange", self.CONGESTION_THRESHOLDS["orange"]["advice"]
        else:
            return "red", self.CONGESTION_THRESHOLDS["red"]["advice"]

    def _generate_movement_suggestion(self, counter: str, customer: CustomerProfile) -> str:
        """生成动线建议"""
        suggestions = {
            "现金柜口": "进门左转→3号现金柜口区域→老年人优先窗口",
            "非现金柜口": "进门右转→非现金业务区→叫号机取号（优先B开头）",
            "自助设备": "进门直走→左侧自助服务区→大堂经理可协助操作",
            "理财室": "请到大堂经理处登记→等候理财经理接待→贵宾客户可直接进入",
            "贵宾室": "请前往1号贵宾室→无需排队→专属客户经理服务",
            "手机银行指导台": "进门右转→手机银行体验区→有专人指导操作",
        }
        base = suggestions.get(counter, "请联系大堂经理指引")

        # 针对老年人的额外建议
        if customer.age >= 65:
            base += "，行动不便可要求上门服务"
        if customer.wait_time >= 15:
            base += "，等候时间较长可先在休息区等候"
        return base

    def _generate_alternatives(self, customer: CustomerProfile, primary: str) -> List[Dict[str, str]]:
        """生成备选分流方案"""
        alternatives = []
        for counter, config in self.COUNTER_CONFIG.items():
            if counter == primary:
                continue
            if counter == "贵宾室" and not customer.vip:
                continue
            if counter == "理财室" and not customer.vip and customer.business_type not in ["理财", "基金", "投资"]:
                continue

            queue_count = self.queue_snapshots.get(counter, 0)
            wait, _ = self._estimate_wait(counter)
            alternatives.append({
                "counter": counter,
                "queue": f"排队{queue_count}人",
                "wait": f"约{wait}分钟",
                "reason": config["suitable_for"][0] if config["suitable_for"] else "",
            })

        # 按等候时间排序，返回最短的两个
        alternatives.sort(key=lambda x: int(x["wait"].replace("约", "").replace("分钟", "")) if x["wait"].replace("约", "").replace("分钟", "").isdigit() else 999)
        return alternatives[:2]

    def _recommend_products(self, customer: CustomerProfile, counter: str) -> List[str]:
        """根据客户画像推荐产品"""
        products = []
        if customer.business_type in ["存款", "理财"] and customer.age < 60:
            products.append("定期存款（利率上浮）")
            products.append("稳健型理财产品")
        if customer.business_type == "信用卡":
            products.append("信用卡分期")
        if counter == "手机银行指导台":
            products.append("手机银行新客礼")
        if customer.vip:
            products.extend(["私人银行理财", "尊享信用卡", "跨境金融服务"])
        elif customer.age >= 50:
            products.append("大额存单")
        return products

    def route(self, age: int, business_type: str, wait_time: int, vip: bool = False,
              has_disability: bool = False, is_first_visit: bool = False) -> RoutingResult:
        """
        执行智能分流

        Args:
            age: 年龄
            business_type: 办理业务类型（支持中文描述）
            wait_time: 已等候时间（分钟）
            vip: 是否VIP客户
            has_disability: 是否有残疾
            is_first_visit: 是否首次到访

        Returns:
            RoutingResult 分流结果
        """
        # 构建客户画像
        customer = CustomerProfile(
            age=age,
            business_type=business_type,
            wait_time=wait_time,
            vip=vip,
            has_disability=has_disability,
            is_first_visit=is_first_visit,
        )

        # 分类业务类型
        classified_biz = self._classify_business(business_type)

        # 匹配柜口
        matches = self._match_counter(customer)

        if not matches:
            # 默认非现金柜口
            primary_counter = "非现金柜口"
            primary_reason = "未匹配到明确业务类型，默认推荐"
        else:
            primary_counter, match_score, match_reason = matches[0]

        config = self.COUNTER_CONFIG[primary_counter]

        # 计算优先级
        priority = self._calculate_priority(customer)

        # 估算等待
        wait_minutes, queue_count = self._estimate_wait(primary_counter, config["avg_duration"])

        # 拥堵等级
        congestion_level, congestion_advice = self._get_congestion_level(queue_count)

        # 动线建议
        movement = self._generate_movement_suggestion(primary_counter, customer)

        # 备选方案
        alternatives = self._generate_alternatives(customer, primary_counter)

        # 推荐产品
        products = self._recommend_products(customer, primary_counter)

        # 生成综合推理
        reasoning_parts = [
            f"客户{age}岁，办理{classified_biz}业务",
            f"等候时间{wait_time}分钟",
            f"匹配度最高方案：{primary_counter}（得分{matches[0][1] if matches else 0}）",
            f"匹配原因：{match_reason if matches else '默认推荐'}",
        ]
        if vip:
            reasoning_parts.append("VIP客户优先")
        if customer.age >= 60:
            reasoning_parts.append("老年人适当照顾")
        reasoning = "；".join(reasoning_parts)

        return RoutingResult(
            recommended_counter=primary_counter,
            counter_description=config.get("suitable_for", ["标准柜口"])[0],
            estimated_wait_minutes=wait_minutes,
            wait_queue_count=queue_count,
            recommended_products=products,
            service_priority=priority,
            congestion_level=congestion_level,
            congestion_advice=congestion_advice,
            movement_suggestion=movement,
            alternative_routes=alternatives,
            reasoning=reasoning,
        )

    def route_from_text(self, text: str) -> RoutingResult:
        """
        从自然语言文本解析客户信息并分流

        支持格式示例：
        - "智能分流 60岁老人 办理存款 等候20分钟 普通客户"
        - "分流 35岁 转账 等待10分钟 VIP"
        - "客户80岁 挂失 等了30分钟"
        """
        text = text.strip()

        # 提取年龄
        age_match = re.search(r"(\d{1,3})\s*[岁周]|[岁周](\d{1,3})", text)
        age = int(age_match.group(1) or age_match.group(2)) if age_match else 40

        # 提取等候时间
        wait_match = re.search(r"等[待候]?(\d+)\s*分|(\d+)\s*分钟", text)
        wait_time = int(wait_match.group(1) or wait_match.group(2)) if wait_match else 0

        # 提取VIP标识
        vip = any(kw in text for kw in ["VIP", "贵宾", "钻石", "金卡", "私人银行"])

        # 提取残障标识
        disability = any(kw in text for kw in ["残疾", "轮椅", "盲人"])

        # 提取业务类型
        business_type = ""
        for biz in self.BUSINESS_KEYWORDS.keys():
            if biz in text:
                business_type = biz
                break
        if not business_type:
            # 尝试用关键词匹配
            for biz_type, keywords in self.BUSINESS_KEYWORDS.items():
                for kw in keywords:
                    if kw in text:
                        business_type = biz_type
                        break
                if business_type:
                    break
        business_type = business_type or "其他业务"

        return self.route(
            age=age,
            business_type=business_type,
            wait_time=wait_time,
            vip=vip,
            has_disability=disability,
        )


def main():
    """测试入口"""
    engine = LobbyRoutingEngine()

    test_cases = [
        "智能分流 60岁老人 办理存款 等候20分钟 普通客户",
        "分流 35岁 转账 等待10分钟 VIP",
        "客户80岁 挂失 等了30分钟",
        "55岁中年人 理财业务 等候5分钟",
    ]

    for text in test_cases:
        print("=" * 60)
        print(f"输入：{text}")
        result = engine.route_from_text(text)
        print(result)
        print()


if __name__ == "__main__":
    main()
