---
name: operational_risk
description: "操作风险管理（Operational Risk Management）技能，通过自然语言描述业务场景，自动完成： - 风险分类：内部欺诈 / 外部欺诈 / 就业政策和工作场所安全 / 客户产品及业务操作 / 执行交割及流程管理 / 系统和技术故障 - 风险矩阵评分：可能性（1-5）× 影响程度（1-5）→ 高/中/低风险 - 损失估算：直接损失 + 间接损失…"
version: 1.0.0
author: ArkClaw
license: MIT
layer: L3
capability_domain: [C01, C02, C03]
industry: financial
metadata:
  raw_title: "Operational Risk Skill（操作风险管理技能）"
  auto_generated: true
  auto_generated_at: "2026-06-20"
---

# Operational Risk Skill（操作风险管理技能）

## 概述

操作风险管理（Operational Risk Management）技能，通过自然语言描述业务场景，自动完成：
- **风险分类**：内部欺诈 / 外部欺诈 / 就业政策和工作场所安全 / 客户产品及业务操作 / 执行交割及流程管理 / 系统和技术故障
- **风险矩阵评分**：可能性（1-5）× 影响程度（1-5）→ 高/中/低风险
- **损失估算**：直接损失 + 间接损失 + 监管罚款
- **管控建议**：预防措施 + 检测措施 + 响应措施

## 7大操作风险类别

| 类别编号 | 风险类别（中文） | 风险类别（英文） | 典型场景 |
|---------|---------------|----------------|---------|
| OR-01 | 内部欺诈 | Internal Fraud | 员工盗用客户资金、伪造文件、违规操作 |
| OR-02 | 外部欺诈 | External Fraud | 电信诈骗、盗刷、假冒客户 |
| OR-03 | 就业政策和工作场所安全 | Employment Practices & Workplace Safety | 劳动纠纷、职场暴力、职业病 |
| OR-04 | 客户产品及业务操作 | Clients Products & Business Practices | 产品设计缺陷、销售误导、信息披露违规 |
| OR-05 | 执行交割及流程管理 | Execution Delivery & Process Management | 交易错误、清算失误、流程违规 |
| OR-06 | 系统和技术故障 | Systems & Technology Failure | 系统宕机、数据丢失、网络攻击 |
| OR-07 | 实体资产损坏 | Damage to Physical Assets | 火灾、盗窃、自然灾害 |

## 风险矩阵（5×5）

|  | 影响1 | 影响2 | 影响3 | 影响4 | 影响5 |
|--|------|------|------|------|------|
| **可能性1** | 低 | 低 | 低 | 中 | 中 |
| **可能性2** | 低 | 低 | 中 | 中 | 高 |
| **可能性3** | 低 | 中 | 中 | 高 | 高 |
| **可能性4** | 中 | 中 | 高 | 高 | 极高 |
| **可能性5** | 中 | 高 | 高 | 极高 | 极高 |

**极高（20-25）**：立即处置，董事会报告
**高（12-19）**：优先处置，3日内上报
**中（6-11）**：常规处置，部门跟踪
**低（1-5）**：持续监测

## 输入参数

- `scenario`：业务场景描述（必填）
- `loss_amount`：损失金额（万元），默认0
- `frequency`：发生频率（未遂/偶尔/经常/持续）
- `operator`：相关操作员（内部/外部/客户）
- `category_override`：手动指定风险类别（可选）

## 输出格式

```json
{
  "category": "内部欺诈",
  "category_code": "OR-01",
  "risk_matrix": {
    "possibility": 4,
    "impact": 4,
    "score": 16,
    "level": "高"
  },
  "loss_estimate": {
    "direct": 200,
    "indirect": 50,
    "regulatory_fine": 100,
    "total": 350
  },
  "controls": {
    "preventive": ["加强员工背景审查", "实施双人复核机制"],
    "detective": ["部署交易监控系统", "定期内部审计"],
    "corrective": ["制定应急响应预案", "建立客户补偿机制"]
  },
  "risk_level": "高",
  "next_action": "优先处置，3日内上报风险管理部"
}
```

## CLI 使用方式

```bash
# 生成操作风险评估
python3 scripts/oprisk_cli.py generate "操作风险 内部欺诈 损失200万 未遂"

# 以 JSON 格式输出
python3 scripts/oprisk_cli.py generate "操作风险 系统故障 损失500万 偶尔" --format=json

# 批量分析
python3 scripts/oprisk_cli.py batch data.csv
```

## 引擎类接口

```python
from operational_risk import OperationalRiskEngine

engine = OperationalRiskEngine()
result = engine.analyze(
    scenario="员工伪造理财产品合同，涉嫌诈骗客户资金",
    loss_amount=200,
    frequency="未遂",
    operator="内部"
)
```

## 企微集成

支持通过 `wecom_integration.py` 生成企微消息卡片，推送给相关人员。

---
*版本：v1.0.0 | 更新：2026-06-10*
