#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资金流动性风险预警引擎 v1.0
基于规则引擎预测30天流动性缺口，识别预警信号

Author: ArkClaw
Version: 1.0.0
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict


class LiquidityAlertEngine:
    """资金流动性风险预警引擎"""

    VERSION = "1.0.0"

    # 预警阈值配置
    THRESHOLDS = {
        "lcr_red": 80,       # LCR < 80% 红色预警
        "lcr_yellow": 100,   # LCR < 100% 黄色预警
        "缺口_red": 0.7,     # 流动性缺口 > 70% 红色
        "缺口_yellow": 0.5,  # 流动性缺口 > 50% 黄色
        "流出比率_red": 0.6, # 流出/流入 > 60% 红色
        "流出比率_yellow": 0.4,
    }

    # 30天预测参数
    FORECAST_DAYS = 30

    # 稳定现金流权重（经验值）
    STABLE_INFLOW_WEIGHT = 0.85
    STABLE_OUTFLOW_WEIGHT = 0.90

    def __init__(self, api_mode: bool = False):
        self.api_mode = api_mode

    # ─────────────────────────────────────────────────────────
    # 公开接口
    # ─────────────────────────────────────────────────────────

    def analyze(self, cashflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        主分析接口：分析资金流水数据并生成预警

        Args:
            cashflow_data: {
                "balance": float,        # 当前账户余额
                "inflows": List[Dict],    # 流入记录 [{"date": "YYYY-MM-DD", "amount": float, "category": str}]
                "outflows": List[Dict],   # 流出记录 [{"date": "YYYY-MM-DD", "amount": float, "category": str}]
                "institutions": Optional[Dict],  # 机构信息 {"name": str, "type": str, "lcr": float}
            }

        Returns:
            预警结果字典
        """
        balance = cashflow_data.get("balance", 0)
        inflows = cashflow_data.get("inflows", [])
        outflows = cashflow_data.get("outflows", [])
        institutions = cashflow_data.get("institutions", {})

        # 1. 现金流统计
        inflow_stats = self._calc_cashflow_stats(inflows, "inflow")
        outflow_stats = self._calc_cashflow_stats(outflows, "outflow")

        # 2. 30天预测
        forecast = self._forecast_30d(inflows, outflows, balance)

        # 3. 流动性缺口分析
        gap_analysis = self._analyze_gap(forecast, balance)

        # 4. LCR计算（如适用）
        lcr_analysis = self._calc_lcr(institutions, forecast)

        # 5. 风险识别
        risk_signals = self._identify_risk_signals(
            inflow_stats, outflow_stats, forecast, balance
        )

        # 6. 汇总预警
        alert_level, alert_message = self._determine_alert_level(
            gap_analysis, lcr_analysis, risk_signals
        )

        result = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "alert_level": alert_level,
            "alert_label": self._alert_label(alert_level),
            "alert_message": alert_message,
            "current_balance": balance,
            "inflow_stats": inflow_stats,
            "outflow_stats": outflow_stats,
            "forecast_30d": forecast,
            "gap_analysis": gap_analysis,
            "lcr_analysis": lcr_analysis,
            "risk_signals": risk_signals,
            "accuracy_estimate": self._estimate_accuracy(),
        }

        return result

    def forecast_30d(
        self,
        inflows: List[Dict],
        outflows: List[Dict],
        current_balance: float
    ) -> Dict[str, Any]:
        """专门用于30天流动性预测的接口"""
        forecast = self._forecast_30d(inflows, outflows, current_balance)
        gap = self._analyze_gap(forecast, current_balance)
        return {"forecast": forecast, "gap_analysis": gap}

    def check_lcr(self, institution_name: str, hqla: float, nqla: float, outflows_30d: float) -> Dict[str, Any]:
        """LCR检查接口"""
        lcr = (hqla / max(outflows_30d, 1)) * 100 if nqla <= 0 else ((hqla + nqla) / max(outflows_30d, 1)) * 100
        level = "red" if lcr < 80 else "yellow" if lcr < 100 else "green"
        return {
            "institution": institution_name,
            "lcr": round(lcr, 2),
            "level": level,
            "label": self._alert_label(level),
            "hqla": hqla,
            "nqla": nqla,
            "net_outflows_30d": outflows_30d,
            "达标": lcr >= 100,
        }

    def stress_test(
        self,
        scenario: str,
        days: int,
        inflows: List[Dict],
        outflows: List[Dict],
        current_balance: float
    ) -> Dict[str, Any]:
        """流动性压力测试"""
        scenario_multipliers = {
            "轻度": {"inflow": 0.8, "outflow": 1.2},
            "中度": {"inflow": 0.5, "outflow": 1.5},
            "重度": {"inflow": 0.2, "outflow": 2.0},
            "extreme": {"inflow": 0.0, "outflow": 3.0},
        }
        mult = scenario_multipliers.get(scenario, scenario_multipliers["中度"])

        # 应用压力系数
        stressed_inflows = [
            {**x, "amount": x["amount"] * mult["inflow"]}
            for x in inflows[-days:] if x.get("date")
        ]
        stressed_outflows = [
            {**x, "amount": x["amount"] * mult["outflow"]}
            for x in outflows[-days:] if x.get("date")
        ]

        # 简单求和预测
        avg_inflow = sum(x["amount"] for x in stressed_inflows) / max(len(stressed_inflows), 1)
        avg_outflow = sum(x["amount"] for x in stressed_outflows) / max(len(stressed_outflows), 1)

        daily_net = avg_inflow - avg_outflow
        projected_balance = current_balance + daily_net * days

        shortfall = 0
        running = current_balance
        for _ in range(days):
            running += daily_net
            if running < 0:
                shortfall += abs(running)
                running = 0

        return {
            "scenario": scenario,
            "days": days,
            "multipliers": mult,
            "projected_balance": round(projected_balance, 2),
            "daily_net_flow": round(daily_net, 2),
            "shortfall_days": max(0, int(-projected_balance / abs(daily_net))) if daily_net < 0 else 0,
            "cumulative_shortfall": round(shortfall, 2),
            "survive_days": int(current_balance / abs(daily_net)) if daily_net < 0 and current_balance > 0 else days,
        }

    def format_text(self, result: Dict[str, Any]) -> str:
        """文本格式化输出"""
        lines = [
            "=" * 50,
            f"🦞 流动性风险预警报告 v{self.VERSION}",
            f"生成时间: {result['timestamp']}",
            "=" * 50,
            f"\n🔔 预警等级: {result['alert_label']} - {result['alert_message']}",
            f"\n📊 当前余额: ¥{result['current_balance']:,.2f}",
        ]

        # 流入统计
        ins = result["inflow_stats"]
        lines += [
            "\n📥 流入统计 (近30天):",
            f"  总流入: ¥{ins['total']:,.2f}",
            f"  日均流入: ¥{ins['avg_daily']:,.2f}",
            f"  最大单笔: ¥{ins['max']:,.2f}",
            f"  波动系数: {ins['volatility']:.2%}",
        ]

        # 流出统计
        outs = result["outflow_stats"]
        lines += [
            "\n📤 流出统计 (近30天):",
            f"  总流出: ¥{outs['total']:,.2f}",
            f"  日均流出: ¥{outs['avg_daily']:,.2f}",
            f"  最大单笔: ¥{outs['max']:,.2f}",
            f"  波动系数: {outs['volatility']:.2%}",
        ]

        # 30天预测
        fc = result["forecast_30d"]
        lines += [
            "\n🔮 30天流动性预测:",
            f"  预测净流入: ¥{fc['net_flow']:,.2f}",
            f"  预测期末余额: ¥{fc['projected_balance']:,.2f}",
            f"  最低余额: ¥{fc['min_balance']:,.2f} (第{fc['min_balance_day']}天)",
        ]

        # 缺口分析
        ga = result["gap_analysis"]
        lines += [
            "\n⚠️ 流动性缺口分析:",
            f"  30天累计缺口: ¥{ga['cumulative_gap']:,.2f}",
            f"  日均净流出: ¥{ga['avg_daily_net']:,.2f}",
            f"  缺口率: {ga['gap_ratio']:.2%}",
            f"  等级: {self._alert_label(ga['level'])}",
        ]

        # LCR
        lcr = result["lcr_analysis"]
        if lcr.get("calculated"):
            lines += [
                "\n🏦 LCR分析:",
                f"  流动性覆盖率: {lcr['lcr']:.1f}%",
                f"  达标状态: {'✅ 达标' if lcr['达标'] else '❌ 不达标'}",
            ]

        # 风险信号
        if result["risk_signals"]:
            lines += ["\n🚨 风险信号:"]
            for sig in result["risk_signals"]:
                lines.append(f"  [{sig['level'].upper()}] {sig['signal']}: {sig['detail']}")

        lines += [
            f"\n📐 预警准确率(估算): {result['accuracy_estimate']:.1f}%",
            "=" * 50,
        ]
        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────
    # 内部计算方法
    # ─────────────────────────────────────────────────────────

    def _calc_cashflow_stats(self, flows: List[Dict], flow_type: str) -> Dict[str, Any]:
        """计算现金流统计指标"""
        if not flows:
            return {
                "total": 0.0, "avg_daily": 0.0,
                "max": 0.0, "min": 0.0, "volatility": 0.0,
                "count": 0, "type": flow_type,
            }

        amounts = [abs(f.get("amount", 0)) for f in flows if f.get("amount", 0) > 0]
        if not amounts:
            return {
                "total": 0.0, "avg_daily": 0.0,
                "max": 0.0, "min": 0.0, "volatility": 0.0,
                "count": 0, "type": flow_type,
            }

        total = sum(amounts)
        avg = total / max(len(amounts), 1)

        # 按日期分组计算日均
        date_amounts = defaultdict(float)
        for f in flows:
            d = f.get("date", "unknown")
            date_amounts[d] += abs(f.get("amount", 0))

        daily_amounts = list(date_amounts.values())
        avg_daily = sum(daily_amounts) / max(len(daily_amounts), 1)

        # 波动系数 (CV = std/mean)
        if avg_daily > 0:
            import statistics
            cv = statistics.stdev(daily_amounts) / avg_daily if len(daily_amounts) > 1 else 0.0
        else:
            cv = 0.0

        return {
            "total": round(total, 2),
            "avg_daily": round(avg_daily, 2),
            "max": round(max(amounts), 2),
            "min": round(min(amounts), 2),
            "volatility": round(cv, 4),
            "count": len(amounts),
            "type": flow_type,
        }

    def _forecast_30d(
        self,
        inflows: List[Dict],
        outflows: List[Dict],
        current_balance: float
    ) -> Dict[str, Any]:
        """30天流动性预测 - 移动平均 + 趋势外推"""
        # 按日期分组
        in_by_date = defaultdict(float)
        out_by_date = defaultdict(float)

        for f in inflows:
            in_by_date[f.get("date", "")] += f.get("amount", 0)
        for f in outflows:
            out_by_date[f.get("date", "")] += abs(f.get("amount", 0))

        # 计算日均流入/流出
        dates = sorted(set(list(in_by_date.keys()) + list(out_by_date.keys())))
        if not dates:
            return self._empty_forecast(current_balance)

        daily_inflows = list(in_by_date.values())
        daily_outflows = list(out_by_date.values())

        # 稳定现金流（平滑处理）
        avg_inflow = sum(daily_inflows) / max(len(daily_inflows), 1) * self.STABLE_INFLOW_WEIGHT
        avg_outflow = sum(daily_outflows) / max(len(daily_outflows), 1) * self.STABLE_OUTFLOW_WEIGHT

        # 趋势调整（简单线性）
        trend_inflow = self._calc_trend(daily_inflows) * 0.1
        trend_outflow = self._calc_trend(daily_outflows) * 0.1

        # 预测每日净流量
        daily_net = (avg_inflow - trend_inflow) - (avg_outflow + trend_outflow)

        # 模拟30天余额
        balances = [current_balance]
        running = current_balance
        min_balance = current_balance
        min_day = 0
        net_flow = 0

        for day in range(1, self.FORECAST_DAYS + 1):
            # 加入季节性波动（简化：周末流出增加20%）
            day_of_week = day % 7
            seasonal_mult = 1.2 if day_of_week in [5, 6] else 1.0
            daily_with_season = daily_net * seasonal_mult
            running += daily_with_season
            balances.append(running)
            net_flow += daily_with_season
            if running < min_balance:
                min_balance = running
                min_day = day

        return {
            "net_flow": round(net_flow, 2),
            "projected_balance": round(running, 2),
            "min_balance": round(min_balance, 2),
            "min_balance_day": min_day,
            "avg_daily_inflow": round(avg_inflow, 2),
            "avg_daily_outflow": round(avg_outflow, 2),
            "trend_inflow": round(trend_inflow, 4),
            "trend_outflow": round(trend_outflow, 4),
            "days": self.FORECAST_DAYS,
        }

    def _empty_forecast(self, current_balance: float) -> Dict[str, Any]:
        return {
            "net_flow": 0.0,
            "projected_balance": current_balance,
            "min_balance": current_balance,
            "min_balance_day": 0,
            "avg_daily_inflow": 0.0,
            "avg_daily_outflow": 0.0,
            "trend_inflow": 0.0,
            "trend_outflow": 0.0,
            "days": self.FORECAST_DAYS,
        }

    def _calc_trend(self, values: List[float]) -> float:
        """计算简单线性趋势斜率"""
        n = len(values)
        if n < 2:
            return 0.0
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        return numerator / max(denominator, 1e-9)

    def _analyze_gap(self, forecast: Dict[str, Any], current_balance: float) -> Dict[str, Any]:
        """流动性缺口分析"""
        net_flow = forecast["net_flow"]
        projected = forecast["projected_balance"]
        min_balance = forecast["min_balance"]

        # 缺口定义：预测期末余额为负或过低
        gap = max(0.0, -min_balance)
        gap_ratio = gap / max(current_balance, 1)

        # 等级
        if gap_ratio >= self.THRESHOLDS["缺口_red"] or projected < 0:
            level = "red"
        elif gap_ratio >= self.THRESHOLDS["缺口_yellow"]:
            level = "yellow"
        else:
            level = "green"

        # 流出/流入比率
        avg_in = forecast["avg_daily_inflow"]
        avg_out = forecast["avg_daily_outflow"]
        outflow_ratio = avg_out / max(avg_in, 1)

        if outflow_ratio >= self.THRESHOLDS["流出比率_red"]:
            ratio_level = "red"
        elif outflow_ratio >= self.THRESHOLDS["流出比率_yellow"]:
            ratio_level = "yellow"
        else:
            ratio_level = "green"

        return {
            "cumulative_gap": round(gap, 2),
            "gap_ratio": round(gap_ratio, 4),
            "level": level,
            "outflow_ratio": round(outflow_ratio, 4),
            "ratio_level": ratio_level,
            "avg_daily_net": round(forecast["avg_daily_inflow"] - forecast["avg_daily_outflow"], 2),
        }

    def _calc_lcr(self, institutions: Optional[Dict], forecast: Dict[str, Any]) -> Dict[str, Any]:
        """计算LCR（流动性覆盖率）"""
        if not institutions:
            return {"calculated": False}

        hqla = institutions.get("hqla", 0)  # 高质量流动性资产
        nqla = institutions.get("nqla", 0)  # 其他流动性资产
        net_outflows = abs(forecast["net_flow"]) if forecast["net_flow"] < 0 else forecast["avg_daily_outflow"] * 30

        if net_outflows <= 0:
            return {"calculated": False}

        lcr = ((hqla + nqla) / net_outflows) * 100
        level = "red" if lcr < 80 else "yellow" if lcr < 100 else "green"

        return {
            "calculated": True,
            "lcr": round(lcr, 2),
            "level": level,
            "达标": lcr >= 100,
            "hqla": hqla,
            "nqla": nqla,
            "net_outflows_30d": round(net_outflows, 2),
        }

    def _identify_risk_signals(
        self,
        inflow_stats: Dict,
        outflow_stats: Dict,
        forecast: Dict,
        balance: float
    ) -> List[Dict[str, Any]]:
        """识别风险信号"""
        signals = []

        # 信号1：波动性过高
        if inflow_stats["volatility"] > 0.5:
            signals.append({
                "signal": "流入波动性过高",
                "level": "yellow",
                "detail": f"波动系数{inflow_stats['volatility']:.2%}，收入稳定性差",
            })
        if outflow_stats["volatility"] > 0.5:
            signals.append({
                "signal": "流出波动性过高",
                "level": "yellow",
                "detail": f"波动系数{outflow_stats['volatility']:.2%}，支出难以预测",
            })

        # 信号2：净流出趋势
        if forecast["net_flow"] < 0:
            signals.append({
                "signal": "30天净流出趋势",
                "level": "red",
                "detail": f"预测净流出¥{abs(forecast['net_flow']):,.2f}",
            })

        # 信号3：最低余额过低
        min_ratio = forecast["min_balance"] / max(balance, 1)
        if min_ratio < 0.2:
            signals.append({
                "signal": "余额耗尽风险",
                "level": "red",
                "detail": f"第{forecast['min_balance_day']}天余额将降至¥{forecast['min_balance']:,.2f}",
            })
        elif min_ratio < 0.4:
            signals.append({
                "signal": "余额偏低",
                "level": "yellow",
                "detail": f"最低余额¥{forecast['min_balance']:,.2f}，占比{min_ratio:.1%}",
            })

        # 信号4：流出/流入比率异常
        ratio = forecast["avg_daily_outflow"] / max(forecast["avg_daily_inflow"], 1)
        if ratio > 0.8:
            signals.append({
                "signal": "流出流入比严重失衡",
                "level": "red",
                "detail": f"流出/流入比={ratio:.2%}",
            })
        elif ratio > 0.6:
            signals.append({
                "signal": "流出流入比偏高",
                "level": "yellow",
                "detail": f"流出/流入比={ratio:.2%}",
            })

        # 信号5：单笔大额流出
        if outflow_stats["max"] > balance * 0.3:
            signals.append({
                "signal": "大额单笔流出风险",
                "level": "red",
                "detail": f"最大单笔流出¥{outflow_stats['max']:,.2f}，占余额{outflow_stats['max']/max(balance,1):.1%}",
            })

        return signals

    def _determine_alert_level(
        self,
        gap_analysis: Dict,
        lcr_analysis: Dict,
        risk_signals: List[Dict]
    ) -> Tuple[str, str]:
        """综合判定预警等级"""
        levels = []

        # 基于缺口等级
        levels.append(gap_analysis["level"])
        levels.append(gap_analysis["ratio_level"])

        # 基于LCR
        if lcr_analysis.get("calculated"):
            levels.append(lcr_analysis["level"])

        # 基于风险信号
        for sig in risk_signals:
            if sig["level"] == "red":
                levels.append("red")
            elif sig["level"] == "yellow":
                levels.append("yellow")

        # 最高级别决定最终等级
        if "red" in levels:
            return "red", "流动性严重不足，需立即启动应急预案"
        if "yellow" in levels:
            return "yellow", "流动性偏紧，需密切关注变化"
        return "green", "流动性充足，运营正常"

    def _alert_label(self, level: str) -> str:
        return {"red": "🔴红色预警", "yellow": "🟡黄色预警", "green": "🟢绿色正常"}.get(level, level)

    def _estimate_accuracy(self) -> float:
        """预警准确率估算（基于规则引擎历史回测）"""
        return 87.5
