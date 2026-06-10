# 精算模型技能 (Actuarial Model Skill)

## 概述

本技能提供保险精算核心功能：**保费定价**、**准备金评估**、**偿付能力评估**，适用于终身寿险、定期寿险、重疾险等主要险种。

## 功能模块

### 1. 保费定价
- 纯保费 = 概率 × 保额 / (1 + 利率)
- 附加费用按比例计入总保费
- 支持三种缴费方式：趸交、5年缴、10年缴、20年缴

### 2. 准备金评估
- 未决赔款准备金（IBNR）评估
- 已赚保费准备金评估
- 未来负债现值计算（现金流折现法）

### 3. 偿付能力评估
- 核心偿付能力充足率 = 实际资本 / 最低资本
- 综合偿付能力充足率计算
- 风险边际考量

## 精算假设

内置**中国人寿保险业经验生命表（CL1/CL2）**：
- CL1：非养老类业务一表
- CL2：非养老类业务二表
- 利率假设：2.5%（可配置）
- 费用率假设：首年25%，续年5%
- 退保率假设：按年限递减

## 支持险种

| 险种类型 | 说明 |
|---------|------|
| 终身寿险 | 终身保障，含身故/全残 |
| 定期寿险 | 固定期限保障 |
| 重疾险 | 重大疾病保障 |

## 输入参数

| 参数 | 说明 | 示例 |
|-----|------|-----|
| product_type | 险种类型 | 终身寿险 |
| age | 投保年龄 | 30 |
| gender | 性别 | 男性 |
| sum_insured | 保额（元） | 1000000 |
| payment_term | 缴费期限（年） | 20 |

## 输出结构

```json
{
  "premium_pricing": {
    "net_premium": "纯保费",
    "expense_load": "附加费用",
    "gross_premium": "总保费",
    "annual_premium": "年缴保费"
  },
  "reserve_evaluation": {
    "unpaid_claim_reserve": "未决赔款准备金",
    "earned_premium_reserve": "已赚保费准备金",
    "total_reserve": "总准备金"
  },
  "solvency_assessment": {
    "actual_capital": "实际资本",
    "minimum_capital": "最低资本",
    "core_solvency_ratio": "核心偿付率",
    "comprehensive_solvency_ratio": "综合偿付率"
  },
  "actuarial_assumptions": {
    "mortality_table": "死亡率表",
    "interest_rate": "利率",
    "expense_rate": "费用率",
    "lapse_rate": "退保率"
  }
}
```

## 使用方式

### CLI
```bash
python3 scripts/actuarial_cli.py generate "精算模型 终身寿险 30岁男性 保额100万 20年缴"
```

### Python API
```python
from actuarial_model import ActuarialModelEngine

engine = ActuarialModelEngine()
result = engine.calculate(
    product_type="终身寿险",
    age=30,
    gender="男性",
    sum_insured=1000000,
    payment_term=20
)
```

## 企微集成

可通过 `wecom_integration.py` 生成企微消息卡片，推送精算报告。
