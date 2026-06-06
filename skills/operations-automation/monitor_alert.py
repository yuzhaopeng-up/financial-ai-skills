#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运营监控告警模块
指标采集、阈值告警、趋势预测
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime
import random


class AlertLevel(Enum):
    """告警级别"""
    CRITICAL = ("紧急", "🔴", 1)
    HIGH = ("高", "🟠", 2)
    MEDIUM = ("中", "🟡", 3)
    LOW = ("低", "🟢", 4)
    INFO = ("信息", "🔵", 5)
    
    def __init__(self, label, emoji, priority):
        self.label = label
        self.emoji = emoji
        self.priority = priority


class AlertStatus(Enum):
    """告警状态"""
    ACTIVE = "活跃"
    ACKNOWLEDGED = "已确认"
    RESOLVED = "已解决"
    SUPPRESSED = "已抑制"


@dataclass
class Metric:
    """监控指标"""
    metric_id: str
    name: str
    metric_type: str  # cpu/memory/transaction/latency/error_rate
    current_value: float
    unit: str
    timestamp: str
    
    # 阈值配置
    warning_threshold: float
    critical_threshold: float
    
    # 趋势
    trend: str = "stable"  # up/down/stable
    history: List[Dict] = field(default_factory=list)


@dataclass
class Alert:
    """告警"""
    alert_id: str
    metric_id: str
    metric_name: str
    alert_level: AlertLevel
    status: AlertStatus
    
    message: str
    current_value: float
    threshold: float
    
    created_time: str
    acknowledged_time: Optional[str] = None
    resolved_time: Optional[str] = None
    
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None


class MonitorAlert:
    """监控告警器"""

    def __init__(self):
        self.metrics = {}
        self.alerts = {}
        self.alert_counter = 0

    def register_metric(self, metric_id: str, name: str,
                        metric_type: str, unit: str,
                        warning_threshold: float,
                        critical_threshold: float) -> Metric:
        """注册监控指标"""
        metric = Metric(
            metric_id=metric_id,
            name=name,
            metric_type=metric_type,
            current_value=0.0,
            unit=unit,
            timestamp=datetime.now().isoformat(),
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold
        )
        self.metrics[metric_id] = metric
        return metric

    def collect_metric(self, metric_id: str, value: float) -> Dict:
        """采集指标值"""
        metric = self.metrics.get(metric_id)
        if not metric:
            return {"success": False, "error": "指标未注册"}
        
        metric.current_value = value
        metric.timestamp = datetime.now().isoformat()
        
        # 记录历史
        metric.history.append({
            "value": value,
            "timestamp": metric.timestamp
        })
        
        # 保留最近100条
        if len(metric.history) > 100:
            metric.history = metric.history[-100:]
        
        # 检测趋势
        metric.trend = self._detect_trend(metric.history)
        
        # 检查阈值
        alert = self._check_threshold(metric)
        
        return {
            "success": True,
            "metric_id": metric_id,
            "value": value,
            "trend": metric.trend,
            "alert_triggered": alert is not None,
            "alert": alert
        }

    def _detect_trend(self, history: List[Dict]) -> str:
        """检测趋势"""
        if len(history) < 3:
            return "stable"
        
        recent = [h["value"] for h in history[-5:]]
        if len(recent) < 3:
            return "stable"
        
        # 简单线性趋势
        first_avg = sum(recent[:2]) / 2
        last_avg = sum(recent[-2:]) / 2
        
        diff_pct = (last_avg - first_avg) / first_avg if first_avg != 0 else 0
        
        if diff_pct > 0.1:
            return "up"
        elif diff_pct < -0.1:
            return "down"
        return "stable"

    def _check_threshold(self, metric: Metric) -> Optional[Dict]:
        """检查阈值"""
        value = metric.current_value
        
        # 确定告警级别
        if value >= metric.critical_threshold:
            level = AlertLevel.CRITICAL
            threshold = metric.critical_threshold
        elif value >= metric.warning_threshold:
            level = AlertLevel.HIGH
            threshold = metric.warning_threshold
        else:
            return None
        
        # 创建告警
        self.alert_counter += 1
        alert_id = f"ALERT{self.alert_counter:06d}"
        
        alert = Alert(
            alert_id=alert_id,
            metric_id=metric.metric_id,
            metric_name=metric.name,
            alert_level=level,
            status=AlertStatus.ACTIVE,
            message=f"{metric.name} 超过阈值: {value}{metric.unit} > {threshold}{metric.unit}",
            current_value=value,
            threshold=threshold,
            created_time=datetime.now().isoformat()
        )
        
        self.alerts[alert_id] = alert
        
        return {
            "alert_id": alert_id,
            "level": level.label,
            "emoji": level.emoji,
            "message": alert.message
        }

    def acknowledge_alert(self, alert_id: str, assigned_to: str) -> Dict:
        """确认告警"""
        alert = self.alerts.get(alert_id)
        if not alert:
            return {"success": False, "error": "告警不存在"}
        
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_time = datetime.now().isoformat()
        alert.assigned_to = assigned_to
        
        return {
            "success": True,
            "alert_id": alert_id,
            "status": "已确认",
            "assigned_to": assigned_to
        }

    def resolve_alert(self, alert_id: str, resolution: str) -> Dict:
        """解决告警"""
        alert = self.alerts.get(alert_id)
        if not alert:
            return {"success": False, "error": "告警不存在"}
        
        alert.status = AlertStatus.RESOLVED
        alert.resolved_time = datetime.now().isoformat()
        alert.resolution = resolution
        
        return {
            "success": True,
            "alert_id": alert_id,
            "status": "已解决",
            "resolution": resolution
        }

    def get_metric_summary(self, metric_id: str) -> Dict:
        """获取指标摘要"""
        metric = self.metrics.get(metric_id)
        if not metric:
            return {}
        
        # 计算统计值
        values = [h["value"] for h in metric.history]
        if values:
            avg = sum(values) / len(values)
            max_val = max(values)
            min_val = min(values)
        else:
            avg = max_val = min_val = 0
        
        return {
            "指标ID": metric.metric_id,
            "名称": metric.name,
            "类型": metric.metric_type,
            "当前值": f"{metric.current_value}{metric.unit}",
            "平均值": f"{avg:.2f}{metric.unit}",
            "最大值": f"{max_val:.2f}{metric.unit}",
            "最小值": f"{min_val:.2f}{metric.unit}",
            "趋势": metric.trend,
            "告警阈值": f"警告:{metric.warning_threshold}{metric.unit} 紧急:{metric.critical_threshold}{metric.unit}",
            "数据点数": len(metric.history)
        }

    def get_alert_summary(self, alert_id: str) -> Dict:
        """获取告警摘要"""
        alert = self.alerts.get(alert_id)
        if not alert:
            return {}
        
        return {
            "告警ID": alert.alert_id,
            "指标": alert.metric_name,
            "级别": f"{alert.alert_level.emoji} {alert.alert_level.label}",
            "状态": alert.status.value,
            "消息": alert.message,
            "当前值": alert.current_value,
            "阈值": alert.threshold,
            "创建时间": alert.created_time,
            "处理人": alert.assigned_to or "未分配",
            "解决方案": alert.resolution or "-"
        }

    def get_all_active_alerts(self) -> List[Dict]:
        """获取所有活跃告警"""
        active = []
        for alert in self.alerts.values():
            if alert.status in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]:
                active.append(self.get_alert_summary(alert.alert_id))
        
        # 按优先级排序
        active.sort(key=lambda x: AlertLevel[x["级别"].split()[-1]].priority if hasattr(AlertLevel, x["级别"].split()[-1]) else 99)
        
        return active
