"""
资金预测引擎（Cashflow Forecast Engine）

输入企业资金数据，返回未来1/3/6/12个月的资金预测及缺口预警。
缺口预警提前3个月红色标注。
"""

import re
from typing import Dict, Any, Optional


class CashflowForecastEngine:
    """资金预测引擎"""

    def __init__(self):
        self.name = "CashflowForecastEngine"
        self.version = "1.0.0"

    def parse_input(self, text: str) -> Optional[Dict[str, float]]:
        """
        从自然语言解析资金数据。

        支持格式：
        - "资金预测 当前资金200万 应收500万 应付300万 月支出100万"
        - "当前资金 200 应收 500 应付 300 月支出 100"

        Returns:
            dict: {'current_cash': float, 'receivables': float,
                   'payables': float, 'monthly_expense': float}
            单位统一为万元
        """
        text = text.strip()

        # 尝试匹配多种模式
        patterns = [
            # 完整关键词模式
            r'当前资金\s*([\d.]+)\s*(万|万元)?\s*应收\s*([\d.]+)\s*(万|万元)?\s*应付\s*([\d.]+)\s*(万|万元)?\s*月支出\s*([\d.]+)\s*(万|万元)?',
            # 缩写模式
            r'现\s*([\d.]+)\s*(?:万|万元)?\s*应\s*([\d.]+)\s*(?:万|万元)?\s*应\s*([\d.]+)\s*(?:万|万元)?\s*支\s*([\d.]+)\s*(?:万|万元)?',
            # 纯数字空格分隔
            r'([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)',
        ]

        for i, pattern in enumerate(patterns):
            m = re.search(pattern, text)
            if m:
                groups = m.groups()
                if i == 0:
                    return {
                        'current_cash': float(groups[0]),
                        'receivables': float(groups[2]),
                        'payables': float(groups[4]),
                        'monthly_expense': float(groups[6]),
                    }
                elif i == 1:
                    return {
                        'current_cash': float(groups[0]),
                        'receivables': float(groups[1]),
                        'payables': float(groups[2]),
                        'monthly_expense': float(groups[3]),
                    }
                elif i == 2:
                    return {
                        'current_cash': float(groups[0]),
                        'receivables': float(groups[1]),
                        'payables': float(groups[2]),
                        'monthly_expense': float(groups[3]),
                    }

        # 兜底：尝试逐行或逗号分隔
        numbers = re.findall(r'([\d.]+)', text)
        if len(numbers) >= 4:
            return {
                'current_cash': float(numbers[0]),
                'receivables': float(numbers[1]),
                'payables': float(numbers[2]),
                'monthly_expense': float(numbers[3]),
            }

        return None

    def forecast(
        self,
        current_cash: float,
        receivables: float,
        payables: float,
        monthly_expense: float,
    ) -> Dict[str, Any]:
        """
        资金预测主方法。

        Args:
            current_cash: 当前资金（万元）
            receivables: 应收款项（万元）
            payables: 应付款项（万元）
            monthly_expense: 月均支出（万元）

        Returns:
            dict，包含 forecast / gap_warning / solutions
        """
        # 净可用资金 = 当前资金 + 应收 - 应付
        net_cash = current_cash + receivables - payables

        # 安全余额阈值：3个月支出
        safety_threshold = monthly_expense * 3

        # 各月预测
        forecast_result = {}
        gap_warning = {}

        for months, label in [(1, "month_1"), (3, "month_3"), (6, "month_6"), (12, "month_12")]:
            future_cash = net_cash - monthly_expense * months
            if future_cash > safety_threshold:
                status = "normal"
            elif future_cash > 0:
                status = "warning"
            else:
                status = "danger"
            forecast_result[label] = {
                "cash": round(future_cash, 2),
                "status": status,
                "months": months,
            }

        # 缺口预警：提前3个月红色标注
        # 扫描所有月份，任何月份资金 <= 0 时，向前推3个月作为预警触发点
        danger_months = [
            (m, data["months"], data["cash"])
            for m, data in forecast_result.items()
            if data["status"] == "danger"
        ]

        if danger_months:
            # 按时间排序，取最早危险月份
            danger_months.sort(key=lambda x: x[1])
            first_danger_month = danger_months[0][1]  # 3/6/12

            # 预警触发点 = 危险月份 - 3个月，最少提前1个月
            warning_months_ahead = max(1, first_danger_month - 3)

            # 标记所有 >= warning_months_ahead 的danger月份为红色
            for label, data in forecast_result.items():
                if data["status"] == "danger" and data["months"] >= warning_months_ahead:
                    gap_months = data["months"]
                    gap_amount = abs(data["cash"])
                    severity = "red"  # 提前3个月红色标注
                    deadline_map = {
                        1: "1个月后",
                        3: "约3个月后",
                        6: "约6个月后",
                        12: "约12个月后",
                    }
                    gap_warning[label] = {
                        "gap": round(gap_amount, 2),
                        "severity": severity,
                        "deadline": deadline_map.get(gap_months, f"约{gap_months}个月后"),
                        "note": f"提前{warning_months_ahead}个月预警",
                    }

        # 缺口应对方案
        solutions = self._generate_solutions(net_cash, receivables, payables, monthly_expense)

        return {
            "input": {
                "current_cash": current_cash,
                "receivables": receivables,
                "payables": payables,
                "monthly_expense": monthly_expense,
                "net_cash": round(net_cash, 2),
            },
            "forecast": forecast_result,
            "gap_warning": gap_warning,
            "solutions": solutions,
        }

    def _generate_solutions(
        self,
        net_cash: float,
        receivables: float,
        payables: float,
        monthly_expense: float,
    ) -> list:
        """生成缺口应对方案"""
        solutions = []
        safety_threshold = monthly_expense * 3

        # 判断是否有危险月份
        has_danger = any(
            (net_cash - monthly_expense * m) <= 0
            for m in [1, 3, 6, 12]
        )
        has_warning = any(
            0 < (net_cash - monthly_expense * m) <= safety_threshold
            for m in [1, 3, 6, 12]
        )

        if has_danger or has_warning:
            # 资金不足场景
            if receivables > 0:
                solutions.append({
                    "action": "加速应收账款回收",
                    "expected_impact": f"+{round(receivables, 0)}万（全部回收）",
                    "timeline": "1-2个月",
                    "priority": "high",
                })

            if payables > 0:
                solutions.append({
                    "action": "谈判延长应付账期",
                    "expected_impact": f"+{round(min(payables, payables * 0.3), 0)}万（延长30%）",
                    "timeline": "1个月",
                    "priority": "high",
                })

            solutions.append({
                "action": "申请银行短期信贷/授信",
                "expected_impact": f"补充流动资金，覆盖潜在缺口",
                "timeline": "2-4周",
                "priority": "high",
            })

            solutions.append({
                "action": "优化应收账款周期（DSO）",
                "expected_impact": "减少资金占用15-30%",
                "timeline": "持续改善",
                "priority": "medium",
            })

            solutions.append({
                "action": "控制非必要支出，延长付款账期",
                "expected_impact": f"+{round(monthly_expense * 0.2, 0)}万/月",
                "timeline": "立即执行",
                "priority": "medium",
            })
        else:
            solutions.append({
                "action": "当前资金充裕，维持现状",
                "expected_impact": "无需特别操作",
                "timeline": "-",
                "priority": "low",
            })

        return solutions

    def format_text(self, result: Dict[str, Any]) -> str:
        """格式化为可读文本"""
        lines = []
        lines.append("=" * 50)
        lines.append("📊 资金预测报告")
        lines.append("=" * 50)

        inp = result["input"]
        lines.append(f"\n【当前状况】")
        lines.append(f"  当前资金：{inp['current_cash']}万")
        lines.append(f"  应收款项：{inp['receivables']}万")
        lines.append(f"  应付款项：{inp['payables']}万")
        lines.append(f"  月均支出：{inp['monthly_expense']}万")
        lines.append(f"  净可用资金：{inp['net_cash']}万")

        lines.append(f"\n【未来预测】")
        status_emoji = {"normal": "🟢", "warning": "🟡", "danger": "🔴"}
        for label, data in result["forecast"].items():
            emoji = status_emoji.get(data["status"], "⚪")
            lines.append(
                f"  {emoji} {label.replace('month_', '')}个月后："
                f"{data['cash']}万 [{data['status']}]"
            )

        if result["gap_warning"]:
            lines.append(f"\n🚨 缺口预警（提前3个月红色标注）")
            for label, warning in result["gap_warning"].items():
                lines.append(
                    f"  🔴 {label.replace('month_', '')}个月后："
                    f"缺口 {warning['gap']}万 | 预计 {warning['deadline']} | "
                    f"预警提前：{warning.get('note', '3个月')}"
                )

        if result["solutions"]:
            lines.append(f"\n💡 缺口应对方案")
            for i, sol in enumerate(result["solutions"], 1):
                priority_tag = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                    sol.get("priority", "low"), "⚪"
                )
                lines.append(
                    f"  {i}. {priority_tag} {sol['action']}"
                )
                lines.append(f"     预期效果：{sol['expected_impact']} | "
                             f"预计周期：{sol['timeline']}")

        lines.append("\n" + "=" * 50)
        return "\n".join(lines)


def main():
    engine = CashflowForecastEngine()
    # 测试用例
    test_input = "资金预测 当前资金200万 应收500万 应付300万 月支出100万"
    parsed = engine.parse_input(test_input)
    print(f"解析结果: {parsed}")
    result = engine.forecast(**parsed)
    print(engine.format_text(result))


if __name__ == "__main__":
    main()
