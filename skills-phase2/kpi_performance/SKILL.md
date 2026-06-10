# KPI 绩效考核引擎

## 概述

KPI 绩效考核引擎（KPIPerformanceEngine）针对银行一线岗位，自动生成绩效考核方案（KPI 指标设计 / 权重分配 / 评分标准）、考核数据要求 及 改进建议。

## 支持岗位

| 岗位类别 | 子类 |
|---------|------|
| 客户经理 | 大堂客户经理、对公客户经理、零售客户经理、理财客户经理 |
| 柜员 | 综合柜员、现金柜员 |
| 风控经理 | 信贷风控经理、柜面风控经理 |
| 产品经理 | 存款产品经理、贷款产品经理、中间业务产品经理 |
| 网点负责人 | 支行行长、网点主任 |

## 考核周期

- **季度考核**（Q1/Q2/Q3/Q4）
- **月度考核**

## KPI 维度体系

| 维度 | 说明 |
|------|------|
| 存款类指标 | 日均存款余额、存款增长率、存款市场份额 |
| 贷款类指标 | 贷款发放量、贷款不良率、贷款利息回收率 |
| 中间业务收入 | 手续费收入、理财销售收入、银行卡收入 |
| 客户类指标 | 新增客户数、客户维护率、客户满意度 |
| 风险合规类指标 | 合规操作评分、风险事件数、反洗钱合规 |

## 使用方式

### CLI

```bash
python3 scripts/kpi_cli.py generate "绩效考核 客户经理 季度"
python3 scripts/kpi_cli.py generate "绩效考核 柜员 月度"
python3 scripts/kpi_cli.py generate "绩效考核 风控经理 季度"
```

### Python API

```python
from kpi_engine import KPIPerformanceEngine

engine = KPIPerformanceEngine()
result = engine.generate(
    position="客户经理",
    sub_type="零售客户经理",
    period="季度"
)
print(result)
```

## 输出格式

- `text`：纯文本格式
- `json`：JSON 结构化格式
- `wecom_card`：企业微信卡片格式（通过 wecom_integration.py）

## 企微集成

通过 `wecom_integration.py` 可将 KPI 方案以企业微信消息卡片形式发送给指定用户或群。

---

*引擎版本：v1.0.0 | 最后更新：2026-06-10*
