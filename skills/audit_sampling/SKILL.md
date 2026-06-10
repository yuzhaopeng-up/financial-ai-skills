# 审计智能抽样 (Audit Sampling)

## 概述

审计智能抽样引擎，基于统计学原理和审计准则（CAS/ISA），为审计师提供科学的样本量计算、抽样方法选择及误差推断能力。

## 功能特性

- **四大抽样方法**: 随机抽样、分层抽样、整群抽样、PPS抽样（概率比例规模）
- **智能样本量计算**: 基于置信水平、可容忍误差、预期误差率自动计算
- **风险等级评估**: 高/中/低风险业务自动匹配抽样策略
- **审计发现概率**: 基于抽样结果推断总体误差率及置信区间
- **多场景适配**: 发票审计、账户余额审计、交易审计等

## 核心引擎

`AuditSamplingEngine`

```python
from audit_sampling_engine import AuditSamplingEngine

engine = AuditSamplingEngine()
result = engine.generate(
    scenario="发票审计",
    total_count=10000,
    total_amount=50000000,
    risk_level="高风险",
    confidence_level=0.95
)
```

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| scenario | str | 是 | 审计场景描述 |
| total_count | int | 是 | 总体数量（如发票张数） |
| total_amount | float | 是 | 总体金额（元） |
| risk_level | str | 否 | 高/中/低风险，默认"中风险" |
| confidence_level | float | 否 | 置信水平，默认0.95 |
| tolerable_error_rate | float | 否 | 可容忍误差率，默认0.05 |
| expected_error_rate | float | 否 | 预期误差率，默认0.01 |

## 输出结果

```json
{
  "sampling_plan": {
    "method": "分层抽样",
    "sample_size": 384,
    "method_rationale": "高风险业务采用分层抽样..."
  },
  "sampling_results": {
    "sampled_items": [...],
    "findings_count": 5,
    "findings_amount": 125000
  },
  "audit_findings": {
    "estimated_error_rate": 0.013,
    "projected_total_errors": 130,
    "projected_total_amount": 650000
  },
  "population_conclusion": {
    "error_rate_range": [0.8%, 2.1%],
    "confidence_interval": "95%",
    "opinion_impact": "无保留意见基础受到质疑"
  }
}
```

## CLI 用法

```bash
python3 scripts/audit_sampling_cli.py generate "审计抽样 发票总量10000张 总金额5000万 高风险业务"
```

## 企微集成

支持通过 `wecom_integration.py` 发送格式化卡片到企业微信。

## 抽样方法说明

### 随机抽样 (Simple Random Sampling)
- 每个个体被选中的概率相等
- 适用于总体差异较小、边界清晰的场景

### 分层抽样 (Stratified Sampling)
- 按特征（金额、日期、业务类型）分层
- 每层独立计算样本量
- 适用于总体内部差异较大的场景

### 整群抽样 (Cluster Sampling)
- 以群体为单位抽样，群内全查
- 适用于群体间差异小、群体内差异大的场景

### PPS抽样 (Probability Proportional to Size)
- 金额大的项目被选中的概率更高
- 适用于金额分布不均、少量大额项目主导总体的场景
