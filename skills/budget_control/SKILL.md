# Budget Control Skill（预算管控）

## 概述

预算管控技能用于分析企业部门/项目的预算执行情况，提供执行率监控、超支风险预警、剩余期间预测和管控建议。

## 核心能力

- **预算执行分析**：计算执行率，判断执行进度是否正常
- **预警状态评估**：绿灯/黄灯/红灯三级预警
- **超支风险预测**：基于剩余时间和剩余预算计算风险等级
- **管控建议生成**：根据分析结果提供具体的管控措施

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| dept | string | ✓ | 部门名称 |
| category | string | ✓ | 费用科目 |
| budget | float | ✓ | 预算金额（万元） |
| spent | float | ✓ | 已使用金额（万元） |
| remaining_months | float | ✓ | 剩余月份 |

## 预警阈值

| 执行率 | 预警状态 | 说明 |
|--------|----------|------|
| ≤80% | 🟢 绿灯 | 执行进度正常 |
| 80%~95% | 🟡 黄灯 | 需要关注 |
| >95% | 🔴 红灯 | 超支风险高 |

## 输出结构

```json
{
  "dept": "市场部",
  "category": "差旅费",
  "budget": 20.0,
  "spent": 18.0,
  "remaining": 2.0,
  "remaining_months": 2,
  "execution_rate": 90.0,
  "status": "yellow",
  "status_text": "🟡 需要关注",
  "overrun_risk": "medium",
  "overrun_risk_text": "中等风险",
  "monthly_burn_rate": 9.0,
  "projected_spend": 27.0,
  "projected_overrun": 7.0,
  "recommendations": [...]
}
```

## 使用方式

### CLI
```bash
python3 scripts/budget_cli.py generate "预算管控 市场部 差旅费 预算20万 已用18万 剩余2个月"
```

### Python API
```python
from budget_engine import BudgetControlEngine

engine = BudgetControlEngine()
result = engine.analyze(
    dept="市场部",
    category="差旅费",
    budget=20.0,
    spent=18.0,
    remaining_months=2.0
)
print(result)
```

## 文件结构

```
budget_control/
├── SKILL.md              # 本文档
├── budget_engine.py       # 核心分析引擎
├── __init__.py           # 模块导出
├── scripts/
│   └── budget_cli.py      # CLI入口
└── wecom_integration.py  # 企微卡片集成
```
