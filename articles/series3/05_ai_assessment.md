# 金融AI评估体系：如何判断你的智能体"够聪明"

> 基于《AI赋能银行数字化转型》第9章评估体系。

---

## 一、为什么需要评估体系？

某银行上线了一个"智能客服"，半年后才发现：

- **准确率**：只有60%（宣称90%）
- **用户满意度**：30%（宣称80%）
- **成本**：比人工客服贵2倍

**问题**：没有建立科学的评估体系，被vendor的PPT忽悠了。

---

## 二、评估维度

### 2.1 技术维度

| 指标 | 定义 | 目标值 |
|------|------|--------|
| **准确率** | 正确回答/总回答 | >85% |
| **召回率** | 正确识别/应识别 | >90% |
| **F1分数** | 准确率和召回率的调和平均 | >87% |
| **响应时间** | 从请求到响应的时间 | <2秒 |
| **吞吐量** | 每秒处理请求数 | >100 QPS |

### 2.2 业务维度

| 指标 | 定义 | 目标值 |
|------|------|--------|
| **任务完成率** | 用户问题被解决的比例 | >80% |
| **转人工率** | 需要转人工处理的比例 | <20% |
| **用户满意度** | 用户评分（1-5分） | >4.0 |
| **业务转化率** | 咨询转业务办理的比例 | >10% |

### 2.3 安全维度

| 指标 | 定义 | 目标值 |
|------|------|--------|
| **数据泄露事件** | 敏感数据外泄次数 | 0 |
| **幻觉率** | 生成虚假信息的概率 | <5% |
| **合规通过率** | 监管检查通过率 | 100% |

---

## 三、评估方法

### 3.1 离线评估

```python
# 使用测试集评估
def offline_evaluation(model, test_set):
    correct = 0
    total = len(test_set)
    
    for item in test_set:
        prediction = model.predict(item['input'])
        if prediction == item['label']:
            correct += 1
    
    accuracy = correct / total
    return {'accuracy': accuracy}
```

### 3.2 在线评估

```python
# A/B测试
def ab_test(model_a, model_b, traffic_split=0.5):
    """
    50%流量走模型A，50%走模型B
    对比业务指标
    """
    metrics = {
        'model_a': {'conversion': 0, 'satisfaction': 0},
        'model_b': {'conversion': 0, 'satisfaction': 0}
    }
    
    # 收集数据...
    
    return metrics
```

### 3.3 人工评估

| 评估类型 | 频率 | 样本量 |
|---------|------|--------|
| 专家评估 | 每月 | 100条 |
| 用户反馈 | 实时 | 全量 |
| 第三方审计 | 每季度 | 1000条 |

---

## 四、评估工具

```python
class AIEvaluator:
    """AI评估器"""
    
    def __init__(self):
        self.metrics = {}
    
    def evaluate_accuracy(self, predictions, labels):
        """评估准确率"""
        correct = sum(p == l for p, l in zip(predictions, labels))
        return correct / len(labels)
    
    def evaluate_latency(self, response_times):
        """评估延迟"""
        return {
            'avg': sum(response_times) / len(response_times),
            'p95': sorted(response_times)[int(len(response_times) * 0.95)],
            'p99': sorted(response_times)[int(len(response_times) * 0.99)]
        }
    
    def evaluate_hallucination(self, outputs, ground_truth):
        """评估幻觉率"""
        # 使用事实核查模型
        hallucinated = sum(not self.fact_check(o, g) 
                          for o, g in zip(outputs, ground_truth))
        return hallucinated / len(outputs)
```

---

## 五、评估报告模板

```
📊 AI系统评估报告
═══════════════════════════════════
系统名称：智能客服系统
评估周期：2025年6月
评估人：AI评估小组

一、技术指标
├── 准确率：87% (目标: >85%) ✅
├── 召回率：92% (目标: >90%) ✅
├── F1分数：89% (目标: >87%) ✅
├── 平均响应时间：1.2秒 (目标: <2秒) ✅
└── 吞吐量：150 QPS (目标: >100) ✅

二、业务指标
├── 任务完成率：82% (目标: >80%) ✅
├── 转人工率：18% (目标: <20%) ✅
├── 用户满意度：4.2/5 (目标: >4.0) ✅
└── 业务转化率：12% (目标: >10%) ✅

三、安全指标
├── 数据泄露事件：0 (目标: 0) ✅
├── 幻觉率：3% (目标: <5%) ✅
└── 合规通过率：100% (目标: 100%) ✅

综合评级：🌟🌟🌟🌟🌟 (优秀)
```

---

## 六、持续优化

```
评估 → 发现问题 → 根因分析 → 优化 → 再评估
  ↑                                      ↓
  └──────────────────────────────────────┘
```

---

> **关于作者**：作者，金融科技从业经历，服务超500家金融机构。《AI赋能银行数字化转型》作者。
