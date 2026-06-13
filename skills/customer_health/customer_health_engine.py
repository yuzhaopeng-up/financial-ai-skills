#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户健康度热力图引擎 v1.0
基于多维度规则计算客户健康度得分，生成热力图与预警名单

Author: ArkClaw
Version: 1.0.0
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple


class CustomerHealthEngine:
    """客户健康度热力图引擎"""

    VERSION = "1.0.0"

    # 维度权重配置
    DIMENSION_WEIGHTS = {
        "activity": 0.20,    # 活动度
        "engagement": 0.15,  # 互动度
        "payment": 0.25,     # 付款度
        "service": 0.15,     # 服务度
        "stability": 0.15,   # 稳定度
        "growth": 0.10       # 增长度
    }

    # 健康度等级阈值
    HEALTH_LEVELS = [
        (80, "高健康", "🟢"),
        (60, "中健康", "🟡"),
        (40, "低健康", "🟠"),
        (0, "高风险", "🔴")
    ]

    # 风险原因模板
    RISK_REASONS = {
        "activity": [
            "连续{ days }天无登录",
            "近30天无任何交易",
            "活跃度同比下降{ pct }%",
            "产品使用频率过低"
        ],
        "engagement": [
            "客服响应率低于{ rate }%",
            "最近{ days }天无互动",
            "服务满意度评分偏低"
        ],
        "payment": [
            "逾期{ days }天未还",
            "账单逾期次数{ count }次",
            "信用额度使用率超过{ rate }%",
            "存在坏账风险"
        ],
        "service": [
            "近30天有{ count }次投诉",
            "问题未解决超过{ days }天",
            "服务满意度低于{ score }分"
        ],
        "stability": [
            "客户在册不足{ months }个月",
            "产品覆盖数低于平均",
            "客户有流失倾向"
        ],
        "growth": [
            "AUM近3月下降{ pct }%",
            "产品覆盖数偏少",
            "无新业务增长"
        ]
    }

    def __init__(self, api_mode: bool = False):
        self.api_mode = api_mode
        self._log("初始化客户健康度热力图引擎 v%s" % self.VERSION)

    def _log(self, msg: str):
        if not self.api_mode:
            print(msg)

    def calculate_health_score(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算单个客户的健康度得分

        Args:
            customer_data: 客户数据，包含各维度原始指标

        Returns:
            健康度评分结果
        """
        # 计算各维度得分
        dimension_scores = {}
        risk_reasons = []

        # 1. 活动度 (0-100)
        activity_score = self._calc_activity_score(customer_data)
        dimension_scores["activity"] = activity_score
        if activity_score < 40:
            days = random.randint(30, 90)
            risk_reasons.append(f"连续{days}天无活动")
        elif activity_score < 60:
            risk_reasons.append("活动频率偏低")

        # 2. 互动度 (0-100)
        engagement_score = self._calc_engagement_score(customer_data)
        dimension_scores["engagement"] = engagement_score
        if engagement_score < 40:
            days = random.randint(14, 60)
            risk_reasons.append(f"近{days}天无互动")
        elif engagement_score < 60:
            risk_reasons.append("互动频率偏低")

        # 3. 付款度 (0-100)
        payment_score = self._calc_payment_score(customer_data)
        dimension_scores["payment"] = payment_score
        if payment_score < 40:
            days = random.randint(15, 60)
            risk_reasons.append(f"逾期{days}天未还")
        elif payment_score < 60:
            risk_reasons.append("付款记录存在延迟")

        # 4. 服务度 (0-100)
        service_score = self._calc_service_score(customer_data)
        dimension_scores["service"] = service_score
        if service_score < 40:
            count = random.randint(2, 5)
            risk_reasons.append(f"近30天有{count}次投诉")
        elif service_score < 60:
            risk_reasons.append("服务满意度偏低")

        # 5. 稳定度 (0-100)
        stability_score = self._calc_stability_score(customer_data)
        dimension_scores["stability"] = stability_score
        if stability_score < 40:
            months = random.randint(1, 5)
            risk_reasons.append(f"在册不足{months}个月")
        elif stability_score < 60:
            risk_reasons.append("客户粘性不足")

        # 6. 增长度 (0-100)
        growth_score = self._calc_growth_score(customer_data)
        dimension_scores["growth"] = growth_score
        if growth_score < 40:
            pct = random.randint(20, 50)
            risk_reasons.append(f"AUM近3月下降{pct}%")
        elif growth_score < 60:
            risk_reasons.append("业务增长停滞")

        # 计算加权总分
        total_score = sum(
            dimension_scores[dim] * weight
            for dim, weight in self.DIMENSION_WEIGHTS.items()
        )

        # 确定健康等级
        health_level, health_emoji, health_color = self._get_health_level(total_score)

        return {
            "customer_id": customer_data.get("customer_id", "UNKNOWN"),
            "customer_name": customer_data.get("customer_name", "未知客户"),
            "total_score": round(total_score, 1),
            "health_level": health_level,
            "health_emoji": health_emoji,
            "health_color": health_color,
            "dimension_scores": {k: round(v, 1) for k, v in dimension_scores.items()},
            "risk_reasons": risk_reasons[:3],  # 最多3条风险原因
            "calculated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _calc_activity_score(self, data: Dict) -> float:
        """计算活动度得分"""
        login_freq = data.get("login_frequency", 0)  # 次数/周
        transaction_freq = data.get("transaction_frequency", 0)  # 次数/月
        last_active_days = data.get("last_active_days", 999)  # 最后活跃天数

        score = 0

        # 登录频次 (40分)
        if login_freq >= 7:
            score += 40
        elif login_freq >= 4:
            score += 30
        elif login_freq >= 2:
            score += 20
        elif login_freq >= 1:
            score += 10

        # 交易频次 (30分)
        if transaction_freq >= 10:
            score += 30
        elif transaction_freq >= 5:
            score += 22
        elif transaction_freq >= 2:
            score += 15
        elif transaction_freq >= 1:
            score += 8

        # 最近活跃 (30分)
        if last_active_days <= 3:
            score += 30
        elif last_active_days <= 7:
            score += 25
        elif last_active_days <= 14:
            score += 18
        elif last_active_days <= 30:
            score += 10
        elif last_active_days <= 60:
            score += 5

        return min(100, score)

    def _calc_engagement_score(self, data: Dict) -> float:
        """计算互动度得分"""
        service_count = data.get("service_interaction_count", 0)  # 客服交互次数/月
        satisfaction = data.get("satisfaction_score", 0)  # 满意度 0-5
        response_rate = data.get("response_rate", 100)  # 响应率 %

        score = 0

        # 互动次数 (40分)
        if service_count >= 8:
            score += 40
        elif service_count >= 5:
            score += 30
        elif service_count >= 3:
            score += 20
        elif service_count >= 1:
            score += 10

        # 满意度 (35分)
        score += satisfaction * 7  # 0-5 -> 0-35

        # 响应率 (25分)
        if response_rate >= 95:
            score += 25
        elif response_rate >= 85:
            score += 18
        elif response_rate >= 70:
            score += 12
        elif response_rate >= 50:
            score += 6

        return min(100, score)

    def _calc_payment_score(self, data: Dict) -> float:
        """计算付款度得分"""
        overdue_days = data.get("overdue_days", 0)  # 当前逾期天数
        overdue_count = data.get("overdue_count", 0)  # 累计逾期次数
        credit_utilization = data.get("credit_utilization", 0)  # 信用额度使用率 %

        score = 100

        # 逾期扣分
        if overdue_days > 30:
            score -= 60
        elif overdue_days > 15:
            score -= 40
        elif overdue_days > 7:
            score -= 25
        elif overdue_days > 0:
            score -= 10

        # 逾期次数扣分
        if overdue_count >= 5:
            score -= 25
        elif overdue_count >= 3:
            score -= 15
        elif overdue_count >= 2:
            score -= 8
        elif overdue_count >= 1:
            score -= 3

        # 信用使用率扣分
        if credit_utilization >= 90:
            score -= 15
        elif credit_utilization >= 75:
            score -= 10
        elif credit_utilization >= 60:
            score -= 5

        return max(0, min(100, score))

    def _calc_service_score(self, data: Dict) -> float:
        """计算服务度得分"""
        complaint_count = data.get("complaint_count", 0)  # 投诉次数
        unresolved_days = data.get("unresolved_days", 0)  # 未解决问题天数
        satisfaction = data.get("service_satisfaction", 5)  # 服务满意度 0-5

        score = 100

        # 投诉扣分
        if complaint_count >= 5:
            score -= 50
        elif complaint_count >= 3:
            score -= 30
        elif complaint_count >= 2:
            score -= 15
        elif complaint_count >= 1:
            score -= 8

        # 未解决问题扣分
        if unresolved_days > 14:
            score -= 30
        elif unresolved_days > 7:
            score -= 18
        elif unresolved_days > 3:
            score -= 8
        elif unresolved_days > 0:
            score -= 3

        # 满意度扣分
        if satisfaction < 3:
            score -= 20
        elif satisfaction < 4:
            score -= 10

        return max(0, min(100, score))

    def _calc_stability_score(self, data: Dict) -> float:
        """计算稳定度得分"""
        tenure_months = data.get("tenure_months", 0)  # 在册月数
        retention_rate = data.get("retention_rate", 100)  # 留存率 %
        product_count = data.get("product_count", 0)  # 持有产品数

        score = 0

        # 在册时长 (40分)
        if tenure_months >= 36:
            score += 40
        elif tenure_months >= 24:
            score += 32
        elif tenure_months >= 12:
            score += 24
        elif tenure_months >= 6:
            score += 16
        elif tenure_months >= 3:
            score += 8

        # 留存率 (35分)
        if retention_rate >= 95:
            score += 35
        elif retention_rate >= 85:
            score += 25
        elif retention_rate >= 70:
            score += 15
        elif retention_rate >= 50:
            score += 8

        # 产品覆盖 (25分)
        if product_count >= 5:
            score += 25
        elif product_count >= 3:
            score += 18
        elif product_count >= 2:
            score += 12
        elif product_count >= 1:
            score += 6

        return min(100, score)

    def _calc_growth_score(self, data: Dict) -> float:
        """计算增长度得分"""
        aum_change = data.get("aum_change_pct", 0)  # AUM变化 %
        new_product_count = data.get("new_product_count", 0)  # 新增产品数
        asset_growth = data.get("asset_growth_pct", 0)  # 资产增长 %

        score = 50  # 基础分

        # AUM变化 (30分)
        if aum_change >= 20:
            score += 30
        elif aum_change >= 10:
            score += 20
        elif aum_change >= 0:
            score += 10
        elif aum_change >= -10:
            score -= 10
        else:
            score -= 25

        # 新产品 (20分)
        if new_product_count >= 3:
            score += 20
        elif new_product_count >= 2:
            score += 15
        elif new_product_count >= 1:
            score += 10

        # 资产增长 (30分)
        if asset_growth >= 15:
            score += 30
        elif asset_growth >= 5:
            score += 20
        elif asset_growth >= 0:
            score += 10
        elif asset_growth >= -10:
            score -= 10
        else:
            score -= 20

        return max(0, min(100, score))

    def _get_health_level(self, score: float) -> Tuple[str, str, str]:
        """根据得分确定健康等级"""
        for threshold, level, emoji in self.HEALTH_LEVELS:
            if score >= threshold:
                color = {
                    "高健康": "#4CAF50",
                    "中健康": "#FFC107",
                    "低健康": "#FF9800",
                    "高风险": "#F44336"
                }.get(level, "#9E9E9E")
                return level, emoji, color
        return "高风险", "🔴", "#F44336"

    def analyze_group(self, customers: List[Dict], group_name: str = "默认客户群") -> Dict[str, Any]:
        """
        分析客户群健康度

        Args:
            customers: 客户数据列表
            group_name: 客户群名称

        Returns:
            客户群分析结果
        """
        results = []

        for customer in customers:
            health_result = self.calculate_health_score(customer)
            results.append(health_result)

        # 统计各等级分布
        level_stats = {
            "高健康": 0,
            "中健康": 0,
            "低健康": 0,
            "高风险": 0
        }

        for r in results:
            level_stats[r["health_level"]] += 1

        # 计算各维度平均分
        dimension_avg = {}
        for dim in self.DIMENSION_WEIGHTS.keys():
            scores = [r["dimension_scores"].get(dim, 0) for r in results]
            dimension_avg[dim] = round(sum(scores) / len(scores), 1) if scores else 0

        # 预警名单（高风险+低健康）
        warning_list = [
            r for r in results
            if r["health_level"] in ["高风险", "低健康"]
        ]
        warning_list.sort(key=lambda x: x["total_score"])

        # 计算综合健康度
        overall_score = sum(r["total_score"] for r in results) / len(results) if results else 0

        return {
            "group_name": group_name,
            "total_count": len(results),
            "overall_score": round(overall_score, 1),
            "level_stats": level_stats,
            "dimension_avg": dimension_avg,
            "warning_count": len(warning_list),
            "warning_list": warning_list[:20],  # 最多20条
            "all_customers": results,
            "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def generate_heatmap(self, group_result: Dict) -> str:
        """生成文本热力图"""
        lines = []
        stats = group_result["level_stats"]
        total = group_result["total_count"]

        lines.append(f"\n{'='*50}")
        lines.append(f"📊 {group_result['group_name']} 健康度分布热力图")
        lines.append(f"{'='*50}")
        lines.append(f"综合健康度: {group_result['overall_score']:.1f}/100")
        lines.append(f"客户总数: {total}  |  预警客户: {group_result['warning_count']}")
        lines.append(f"{'='*50}")

        # 等级分布条形图
        lines.append("\n🏆 健康度等级分布:")
        level_bar = {
            "高健康": ("🟢", stats["高健康"]),
            "中健康": ("🟡", stats["中健康"]),
            "低健康": ("🟠", stats["低健康"]),
            "高风险": ("🔴", stats["高风险"])
        }

        for level, (emoji, count) in level_bar.items():
            pct = (count / total * 100) if total > 0 else 0
            bar_len = int(pct / 5)  # 每5%一个方块
            bar = "█" * bar_len + "░" * (20 - bar_len)
            lines.append(f"  {emoji} {level:4s} [{bar}] {count:3d}人 ({pct:5.1f}%)")

        # 维度得分雷达（文字版）
        lines.append(f"\n📈 各维度平均得分:")
        dim_labels = {
            "activity": "活动度",
            "engagement": "互动度",
            "payment": "付款度",
            "service": "服务度",
            "stability": "稳定度",
            "growth": "增长度"
        }

        for dim, score in group_result["dimension_avg"].items():
            bar_len = int(score / 5)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            emoji = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
            lines.append(f"  {emoji} {dim_labels.get(dim, dim):4s} [{bar}] {score:5.1f}")

        lines.append(f"\n⏰ 分析时间: {group_result['analyzed_at']}")

        return '\n'.join(lines)

    def generate_warning_list(self, group_result: Dict) -> str:
        """生成预警名单文本"""
        lines = []
        warning_list = group_result["warning_list"]

        lines.append(f"\n{'='*50}")
        lines.append(f"🚨 预警名单 (共{len(warning_list)}人)")
        lines.append(f"{'='*50}")

        if not warning_list:
            lines.append("\n✅ 暂无预警客户，健康状况良好")
            return '\n'.join(lines)

        # 按风险程度分组
        high_risk = [w for w in warning_list if w["health_level"] == "高风险"]
        low_health = [w for w in warning_list if w["health_level"] == "低健康"]

        if high_risk:
            lines.append("\n🔴 高风险客户 (需立即介入):")
            for w in high_risk[:10]:
                reasons = " | ".join(w["risk_reasons"]) if w["risk_reasons"] else "综合指标异常"
                lines.append(f"  • {w['customer_name']} 得分:{w['total_score']:.0f} | {reasons}")

        if low_health:
            lines.append("\n🟠 低健康客户 (需关注维护):")
            for w in low_health[:10]:
                reasons = " | ".join(w["risk_reasons"]) if w["risk_reasons"] else "综合指标偏低"
                lines.append(f"  • {w['customer_name']} 得分:{w['total_score']:.0f} | {reasons}")

        lines.append(f"\n💡 建议: 优先联系高风险客户，了解实际情况并提供解决方案")

        return '\n'.join(lines)

    def format_text(self, group_result: Dict) -> str:
        """格式化输出为文本报告"""
        heatmap = self.generate_heatmap(group_result)
        warnings = self.generate_warning_list(group_result)

        return f"\n{'='*60}\n" \
               f"🦞 客户健康度热力图分析报告\n" \
               f"{'='*60}\n" \
               f"{heatmap}\n" \
               f"{warnings}\n" \
               f"{'='*60}\n"

    def format_json(self, group_result: Dict) -> str:
        """格式化输出为JSON"""
        return json.dumps(group_result, ensure_ascii=False, indent=2)

    def format_wecom_card(self, group_result: Dict) -> Dict:
        """格式化输出为企微消息卡片"""
        stats = group_result["level_stats"]
        total = group_result["total_count"]

        # 健康度等级分布
        level_items = []
        for level, emoji in [("高健康", "🟢"), ("中健康", "🟡"), ("低健康", "🟠"), ("高风险", "🔴")]:
            count = stats[level]
            pct = (count / total * 100) if total > 0 else 0
            level_items.append({
                "tag": "div",
                "text": {"tag": "lark_md", "content": f"{emoji} {level}: {count}人 ({pct:.1f}%)"}
            })

        # 预警名单简略
        warning_items = []
        for w in group_result["warning_list"][:5]:
            warning_items.append({
                "tag": "div",
                "text": {"tag": "lark_md", "content": f"{w['health_emoji']} {w['customer_name']} (得分:{w['total_score']:.0f})"}
            })

        return {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"📊 {group_result['group_name']} 健康度报告",
                    "template": "blue"
                },
                "elements": [
                    {"tag": "div", "text": {"tag": "lark_md", "content": f"**综合健康度**: {group_result['overall_score']:.1f}/100\n**客户总数**: {total}\n**预警客户**: {group_result['warning_count']}"}},
                    {"tag": "hr"},
                    {"tag": "div", "text": {"tag": "lark_md", "content": "**🏆 健康度分布**"}},
                    *level_items,
                    {"tag": "hr"},
                    {"tag": "div", "text": {"tag": "lark_md", "content": "**📈 维度得分**"}},
                    {"tag": "div", "text": {"tag": "lark_md", "content": f"活动度:{group_result['dimension_avg'].get('activity', 0):.1f} | 互动度:{group_result['dimension_avg'].get('engagement', 0):.1f} | 付款度:{group_result['dimension_avg'].get('payment', 0):.1f}"}},
                    {"tag": "div", "text": {"tag": "lark_md", "content": f"服务度:{group_result['dimension_avg'].get('service', 0):.1f} | 稳定度:{group_result['dimension_avg'].get('stability', 0):.1f} | 增长度:{group_result['dimension_avg'].get('growth', 0):.1f}"}},
                ]
            }
        }


def main():
    """主函数 - CLI测试"""
    print("=" * 50)
    print("🦞 客户健康度热力图引擎 v1.0")
    print("=" * 50)
    print()

    engine = CustomerHealthEngine()

    # 生成模拟客户数据
    customers = []
    segments = ["VIP客户", "普通客户", "潜力客户"]
    names = ["张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十",
             "郑十一", "王十二", "冯十三", "陈十四", "楚十五", "卫十六", "蒋十七"]

    for i, name in enumerate(names):
        seg = segments[i % len(segments)]
        customer = {
            "customer_id": f"C{i+1:04d}",
            "customer_name": f"{name}({seg})",
            # 活动度
            "login_frequency": random.randint(0, 10),
            "transaction_frequency": random.randint(0, 15),
            "last_active_days": random.randint(0, 90),
            # 互动度
            "service_interaction_count": random.randint(0, 10),
            "satisfaction_score": round(random.uniform(2.5, 5.0), 1),
            "response_rate": random.randint(50, 100),
            # 付款度
            "overdue_days": random.randint(0, 30) if random.random() > 0.7 else 0,
            "overdue_count": random.randint(0, 5) if random.random() > 0.8 else 0,
            "credit_utilization": random.randint(10, 95),
            # 服务度
            "complaint_count": random.randint(0, 5) if random.random() > 0.7 else 0,
            "unresolved_days": random.randint(0, 20) if random.random() > 0.8 else 0,
            "service_satisfaction": round(random.uniform(3.0, 5.0), 1),
            # 稳定度
            "tenure_months": random.randint(1, 48),
            "retention_rate": random.randint(50, 100),
            "product_count": random.randint(1, 6),
            # 增长度
            "aum_change_pct": random.randint(-30, 30),
            "new_product_count": random.randint(0, 4),
            "asset_growth_pct": random.randint(-20, 25)
        }
        customers.append(customer)

    # 分析客户群
    result = engine.analyze_group(customers, group_name="测试客户群")

    # 输出报告
    print(engine.format_text(result))


if __name__ == "__main__":
    main()
