# 金融AI评估体系：如何判断你的智能体"够聪明"

> 方法论：AI评估指标体系 | 金融场景特殊性 | 持续优化

## 为什么需要评估体系？

银行上线AI系统后，常见对话：

```
行长: "这个AI系统怎么样？"
科技: "准确率95%"
行长: "那客户满意度呢？"
科技: "...没统计"
行长: "业务效率提升多少？"
科技: "...应该挺多的"
```

**问题**：没有体系化的评估，无法证明价值。

## 评估指标体系

### 三层评估模型

```
┌─────────────────────────────────────┐
│         战略层 (北极星指标)           │
│  ├─ 业务价值                        │
│  ├─ 客户体验                        │
│  └─ 风险控制                        │
├─────────────────────────────────────┤
│         战术层 (过程指标)             │
│  ├─ 系统性能                        │
│  ├─ 模型效果                        │
│  └─ 运营效率                        │
├─────────────────────────────────────┤
│         执行层 (基础指标)             │
│  ├─ 技术指标                        │
│  ├─ 数据质量                        │
│  └─ 资源消耗                        │
└─────────────────────────────────────┘
```

### 金融AI专用指标

#### 1. 准确性指标

| 指标 | 定义 | 目标值 | 适用场景 |
|------|------|--------|----------|
| 准确率 | 正确预测/总预测 | >95% | 分类任务 |
| 精确率 | TP/(TP+FP) | >90% | 欺诈检测 |
| 召回率 | TP/(TP+FN) | >85% | 反洗钱 |
| F1分数 | 2*精确率*召回率/(精确率+召回率) | >90% | 综合评估 |
| AUC-ROC | ROC曲线下面积 | >0.9 | 排序任务 |

```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

class ModelEvaluator:
    def __init__(self):
        self.thresholds = {
            "accuracy": 0.95,
            "precision": 0.90,
            "recall": 0.85,
            "f1": 0.90,
            "auc": 0.90
        }
    
    def evaluate(self, y_true, y_pred, y_prob=None) -> dict:
        """评估模型"""
        results = {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred),
            "recall": recall_score(y_true, y_pred),
            "f1": f1_score(y_true, y_pred)
        }
        
        if y_prob is not None:
            results["auc"] = roc_auc_score(y_true, y_prob)
        
        # 检查是否达标
        results["passed"] = all(
            results.get(k, 0) >= v 
            for k, v in self.thresholds.items()
        )
        
        return results
```

#### 2. 业务价值指标

| 指标 | 定义 | 计算方式 |
|------|------|----------|
| 效率提升 | 节省时间/原时间 | (T_old - T_new) / T_old |
| 成本降低 | 节省成本/原成本 | (C_old - C_new) / C_old |
| 收入增加 | 新增收入/原收入 | (R_new - R_old) / R_old |
| 风险降低 | 减少损失/原损失 | (L_old - L_new) / L_old |

```python
class BusinessEvaluator:
    def calculate_efficiency(self, old_time, new_time):
        """计算效率提升"""
        return (old_time - new_time) / old_time * 100
    
    def calculate_cost_saving(self, old_cost, new_cost):
        """计算成本节省"""
        return (old_cost - new_cost) / old_cost * 100
    
    def calculate_roi(self, investment, return_value):
        """计算ROI"""
        return (return_value - investment) / investment * 100
```

#### 3. 可解释性指标

| 指标 | 定义 | 目标值 |
|------|------|--------|
| 决策透明度 | 可解释决策/总决策 | >90% |
| 特征重要性 | 关键特征可识别 | 是 |
| 反事实解释 | 可提供反事实案例 | 是 |

```python
class ExplainabilityEvaluator:
    def __init__(self, model):
        self.model = model
    
    def get_feature_importance(self) -> dict:
        """获取特征重要性"""
        if hasattr(self.model, 'feature_importances_'):
            return dict(zip(
                self.model.feature_names_, 
                self.model.feature_importances_
            ))
        return {}
    
    def generate_counterfactual(self, instance, desired_outcome):
        """生成反事实解释"""
        # 使用DiCE或其他库
        pass
```

#### 4. 公平性指标

| 指标 | 定义 | 目标值 |
|------|------|--------|
| 人口统计 parity | 不同群体通过率差异 | <5% |
| 机会均等 | 真正例率差异 | <5% |
| 校准性 | 预测概率与实际概率一致性 | >95% |

```python
class FairnessEvaluator:
    def demographic_parity(self, y_pred, sensitive_attr):
        """人口统计parity"""
        groups = {}
        for group in sensitive_attr.unique():
            mask = sensitive_attr == group
            groups[group] = y_pred[mask].mean()
        
        return max(groups.values()) - min(groups.values())
    
    def equal_opportunity(self, y_true, y_pred, sensitive_attr):
        """机会均等"""
        groups = {}
        for group in sensitive_attr.unique():
            mask = (sensitive_attr == group) & (y_true == 1)
            groups[group] = y_pred[mask].mean()
        
        return max(groups.values()) - min(groups.values())
```

### 评估仪表盘

```python
class EvaluationDashboard:
    def __init__(self):
        self.metrics = {}
    
    def add_metric(self, name: str, value: float, threshold: float):
        """添加指标"""
        self.metrics[name] = {
            "value": value,
            "threshold": threshold,
            "status": "pass" if value >= threshold else "fail"
        }
    
    def generate_report(self) -> str:
        """生成报告"""
        report = "# AI系统评估报告\n\n"
        
        for name, metric in self.metrics.items():
            status = "✅" if metric["status"] == "pass" else "❌"
            report += f"{status} {name}: {metric['value']:.2%} (目标: {metric['threshold']:.2%})\n"
        
        return report
    
    def visualize(self):
        """可视化"""
        import matplotlib.pyplot as plt
        
        names = list(self.metrics.keys())
        values = [m["value"] for m in self.metrics.values()]
        thresholds = [m["threshold"] for m in self.metrics.values()]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        x = range(len(names))
        
        ax.bar(x, values, label="实际值", alpha=0.7)
        ax.plot(x, thresholds, 'r--', label="目标值", linewidth=2)
        
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha="right")
        ax.set_ylabel("数值")
        ax.set_title("AI系统评估指标")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig("evaluation_dashboard.png")
```

## 持续评估机制

### 监控频率

| 指标类型 | 监控频率 | 告警阈值 |
|----------|----------|----------|
| 技术指标 | 实时 | 下降5% |
| 业务指标 | 每日 | 下降10% |
| 风险指标 | 实时 | 任何异常 |
| 公平性指标 | 每周 | 差异>5% |

### 自动告警

```python
class AlertSystem:
    def __init__(self):
        self.rules = []
    
    def add_rule(self, metric: str, condition: str, threshold: float, action: str):
        """添加告警规则"""
        self.rules.append({
            "metric": metric,
            "condition": condition,
            "threshold": threshold,
            "action": action
        })
    
    def check(self, metrics: dict):
        """检查告警"""
        alerts = []
        
        for rule in self.rules:
            value = metrics.get(rule["metric"])
            if value is None:
                continue
            
            triggered = False
            if rule["condition"] == "<" and value < rule["threshold"]:
                triggered = True
            elif rule["condition"] == ">" and value > rule["threshold"]:
                triggered = True
            
            if triggered:
                alerts.append({
                    "metric": rule["metric"],
                    "value": value,
                    "threshold": rule["threshold"],
                    "action": rule["action"]
                })
        
        return alerts
```

## 评估案例

### 信贷审批AI评估

```python
# 初始化评估器
evaluator = ModelEvaluator()
business = BusinessEvaluator()
dashboard = EvaluationDashboard()

# 模型效果
model_results = evaluator.evaluate(y_true, y_pred, y_prob)
dashboard.add_metric("准确率", model_results["accuracy"], 0.95)
dashboard.add_metric("精确率", model_results["precision"], 0.90)
dashboard.add_metric("召回率", model_results["recall"], 0.85)
dashboard.add_metric("F1分数", model_results["f1"], 0.90)

# 业务价值
efficiency = business.calculate_efficiency(72, 2)  # 小时
cost_saving = business.calculate_cost_saving(500000, 20000)  # 元/月
dashboard.add_metric("效率提升", efficiency / 100, 0.80)
dashboard.add_metric("成本节省", cost_saving / 100, 0.70)

# 生成报告
print(dashboard.generate_report())
dashboard.visualize()
```

**输出**：
```
# AI系统评估报告

✅ 准确率: 96.50% (目标: 95.00%)
✅ 精确率: 92.30% (目标: 90.00%)
✅ 召回率: 88.70% (目标: 85.00%)
✅ F1分数: 90.40% (目标: 90.00%)
✅ 效率提升: 97.20% (目标: 80.00%)
✅ 成本节省: 96.00% (目标: 70.00%)
```

---

**#AI评估 #指标体系 #金融AI #模型监控 #持续优化**
