"""
Lobby Queue Engine — 排队预警核心引擎

基于等候人数×平均办理时长/服务窗口数计算排队指数（0-100），
输出预警等级（红/黄/绿）+ 开台建议 + 客户等候预估 + 历史对比分析。
"""

import re
import json
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class QueueData:
    """排队基础数据"""
    region: str                    # 业务区域（现金区/非现金区/贵宾区/综合区）
    waiting_count: int             # 当前等候人数
    max_wait: int                 # 最长等候时间（分钟）
    avg_service_time: float       # 平均办理时长（分钟）
    service_windows: int          # 当前开放窗口数
    vip_count: int = 0            # 贵宾等候人数
    history_data: Optional[dict] = None  # 历史数据（可选）


@dataclass
class QueueAnalysis:
    """排队分析结果"""
    queue_index: int              # 排队指数（0-100）
    alert_level: str              # 预警等级：green/yellow/red
    alert_color: str              # 颜色标签：正常/注意/告急
    suggestion: str                # 开台建议
    wait_estimate: str            # 客户等候预估
    history_compare: str            # 历史对比分析
    queue_data: QueueData          # 原始排队数据

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


class LobbyQueueEngine:
    """
    排队预警核心引擎

    计算公式：
        基础排队指数 = (等候人数 × 平均办理时长) / 服务窗口数 × 10
        最终指数 = min(100, 基础指数 × 区域系数 × 贵宾系数)

    预警阈值：
        绿色（0-40）：正常，无需干预
        黄色（41-70）：注意，建议增开窗口
        红色（71-100）：告急，紧急增开窗口
    """

    # 区域系数（区域繁忙程度权重）
    REGION_WEIGHTS = {
        "现金区": 1.2,     # 现金区业务复杂，权重较高
        "非现金区": 1.0,   # 标准权重
        "贵宾区": 0.8,     # 贵宾区客流量相对稳定
        "综合区": 1.1,     # 综合区情况复杂
        "默认": 1.0,
    }

    # 预警阈值
    ALERT_THRESHOLDS = {
        "green": (0, 40),
        "yellow": (41, 70),
        "red": (71, 100),
    }

    # 窗口类型推荐
    WINDOW_SUGGESTIONS = {
        "现金区": "建议增开现金窗口或引导客户使用自助设备",
        "非现金区": "建议增开非现金服务窗口或开设弹性窗口",
        "贵宾区": "建议启动贵宾专属服务或临时开放快速通道",
        "综合区": "建议启动多窗口联动机制，分流客户",
        "默认": "建议增开服务窗口或优化客户分流",
    }

    def __init__(self):
        self.history = []  # 历史记录（内存）

    def parse_input(self, text: str) -> Optional[QueueData]:
        """
        解析自然语言输入

        支持格式：
        - "排队预警 非现金区3人等候 等待最长达25分钟"
        - "排队预警 现金区5人等候 30分钟"
        - "排队预警 贵宾区2人等候"
        """
        # 区域关键词
        region_pattern = "(现金区|非现金区|贵宾区|综合区)"
        # 人数
        count_pattern = "(\\d+)人"
        # 等待时间
        wait_pattern = "等待最长达(\\d+)分钟|(\\d+)分钟"

        region_match = re.search(region_pattern, text)
        count_match = re.search(count_pattern, text)
        wait_match = re.search(wait_pattern, text)

        if not region_match or not count_match:
            return None

        region = region_match.group(1)
        waiting_count = int(count_match.group(1))

        # 等待时间（分钟）
        if wait_match:
            max_wait = int(wait_match.group(1) or wait_match.group(2))
        else:
            # 默认：等候人数 × 5分钟
            max_wait = waiting_count * 5

        # 估算平均办理时长（基于等候时间反推）
        avg_service_time = max(3.0, max_wait / max(waiting_count, 1) * 0.6)

        # 默认窗口数（根据区域设定）
        default_windows = {
            "现金区": 3,
            "非现金区": 4,
            "贵宾区": 2,
            "综合区": 5,
        }
        service_windows = default_windows.get(region, 3)

        return QueueData(
            region=region,
            waiting_count=waiting_count,
            max_wait=max_wait,
            avg_service_time=round(avg_service_time, 1),
            service_windows=service_windows,
        )

    def calculate_queue_index(self, data: QueueData) -> int:
        """
        计算排队指数（0-100）

        公式：
            基础指数 = (等候人数 × 平均办理时长) / 服务窗口数 × 10
        """
        if data.service_windows <= 0:
            return 0

        base_index = (data.waiting_count * data.avg_service_time) / data.service_windows * 10

        # 区域系数
        region_weight = self.REGION_WEIGHTS.get(data.region, 1.0)

        # 贵宾系数（贵宾客户占用更多资源）
        vip_factor = 1.0 + (data.vip_count * 0.1)

        # 最终指数
        final_index = base_index * region_weight * vip_factor

        return min(100, max(0, int(final_index)))

    def get_alert_level(self, queue_index: int) -> tuple:
        """根据排队指数获取预警等级"""
        if queue_index <= 40:
            return "green", "正常"
        elif queue_index <= 70:
            return "yellow", "注意"
        else:
            return "red", "告急"

    def generate_suggestion(self, data: QueueData, alert_level: str) -> str:
        """生成开台建议"""
        base_suggestion = self.WINDOW_SUGGESTIONS.get(data.region, self.WINDOW_SUGGESTIONS["默认"])

        if alert_level == "red":
            return f"🚨【紧急】{base_suggestion}，当前窗口严重不足，建议立即调配支援！"
        elif alert_level == "yellow":
            return f"⚠️【建议】{base_suggestion}，可提前做好窗口调配准备。"
        else:
            return f"✅ 当前排队情况正常，{base_suggestion}。"

    def estimate_wait_time(self, data: QueueData) -> str:
        """估算等候时间"""
        avg_wait = data.max_wait * 0.6 if data.waiting_count > 1 else data.max_wait

        if data.vip_count > 0:
            vip_note = f"（另有{data.vip_count}位贵宾等候）"
        else:
            vip_note = ""

        return (
            f"当前等候人数：{data.waiting_count}人\n"
            f"平均等候时长：约{int(avg_wait)}分钟\n"
            f"最长等候时长：{data.max_wait}分钟{vip_note}"
        )

    def compare_history(self, data: QueueData) -> str:
        """历史对比分析"""
        # 模拟历史数据对比
        if not self.history:
            compare_note = "首次记录，无历史数据对比"
        else:
            last = self.history[-1]
            diff = data.waiting_count - last.waiting_count
            if diff > 0:
                compare_note = f"较上次记录增加{diff}人，排队压力上升"
            elif diff < 0:
                compare_note = f"较上次记录减少{abs(diff)}人，排队压力缓解"
            else:
                compare_note = "与上次记录持平"

        # 记录当前数据
        self.history.append(data)
        # 只保留最近10条记录
        if len(self.history) > 10:
            self.history = self.history[-10:]

        return compare_note

    def analyze(self, text: str) -> Optional[QueueAnalysis]:
        """
        核心分析入口

        Args:
            text: 自然语言输入，如"排队预警 非现金区3人等候 等待最长达25分钟"

        Returns:
            QueueAnalysis: 分析结果，包含排队指数、预警等级、开台建议等
        """
        data = self.parse_input(text)
        if not data:
            return None

        queue_index = self.calculate_queue_index(data)
        alert_level, alert_color = self.get_alert_level(queue_index)
        suggestion = self.generate_suggestion(data, alert_level)
        wait_estimate = self.estimate_wait_time(data)
        history_compare = self.compare_history(data)

        return QueueAnalysis(
            queue_index=queue_index,
            alert_level=alert_level,
            alert_color=alert_color,
            suggestion=suggestion,
            wait_estimate=wait_estimate,
            history_compare=history_compare,
            queue_data=data,
        )

    def format_report(self, analysis: QueueAnalysis) -> str:
        """格式化输出报告"""
        data = analysis.queue_data
        level_emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}
        emoji = level_emoji.get(analysis.alert_level, "⚪")

        return f"""
╔══════════════════════════════════════════════════════╗
║           🏧 大堂排队预警分析报告                    ║
╠══════════════════════════════════════════════════════╣
║  📍 区域：{data.region:<36}  ║
║  👥 等候人数：{data.waiting_count}人                              ║
║  ⏱️ 最长等候：{data.max_wait}分钟                            ║
║  🏧 服务窗口：{data.service_windows}个                              ║
╠══════════════════════════════════════════════════════╣
║  📊 排队指数：{analysis.queue_index}  {emoji} {analysis.alert_color:<6}              ║
╠══════════════════════════════════════════════════════╣
║  💡 开台建议                                      ║
║  {analysis.suggestion:<46}  ║
╠══════════════════════════════════════════════════════╣
║  ⏰ 等候预估                                      ║
║  {analysis.wait_estimate:<46}  ║
╠══════════════════════════════════════════════════════╣
║  📈 历史对比                                      ║
║  {analysis.history_compare:<46}  ║
╚══════════════════════════════════════════════════════╝
"""


# 快捷函数
def analyze_queue(text: str) -> Optional[dict]:
    """快速分析排队情况"""
    engine = LobbyQueueEngine()
    result = engine.analyze(text)
    if result:
        return result.to_dict()
    return None


if __name__ == "__main__":
    # 测试
    test_input = "排队预警 非现金区3人等候 等待最长达25分钟"
    engine = LobbyQueueEngine()
    result = engine.analyze(test_input)
    if result:
        print(engine.format_report(result))
    else:
        print("解析失败，请检查输入格式")
