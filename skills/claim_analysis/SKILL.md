---
name: claim_analysis
description: "理赔分析引擎 — 输入理赔案件信息，自动输出："
version: 1.0.0
author: ArkClaw
license: MIT
layer: L3
capability_domain: [C03, C04, C08]
industry: financial
metadata:
  raw_title: "理赔分析技能 (Claim Analysis Skill)"
  auto_generated: true
  auto_generated_at: "2026-06-20"
---

# 理赔分析技能 (Claim Analysis Skill)

## 功能概述

**理赔分析引擎** — 输入理赔案件信息，自动输出：
- 责任认定（属于保险责任 / 不属于 / 部分属于）
- 反欺诈检查（20+条规则）
- 理赔金额计算（扣除免赔额/比例赔付/医保已报）
- 审核要点提示
- 处理时效预估

## 适用场景

- 医疗险理赔审核
- 意外险理赔审核
- 重疾险理赔核查
- 理赔初审/复核流程
- 反欺诈风险筛查

## 输入参数

| 字段 | 类型 | 说明 |
|------|------|------|
| insurance_type | string | 险种类型：医疗险/意外险/重疾险/寿险 |
| accident_type | string | 出险类型：疾病/意外/手术等 |
| accident_reason | string | 出险原因 |
| hospital_level | string | 就诊医院等级：三甲医院/三乙医院/二甲医院/其他 |
| total_expense | float | 住院总花费（元） |
| insurance_paid | float | 医保已报销金额（元） |
| policy_terms | dict | 保单条款（含免赔额/赔付比例/保障范围等） |
| patient_history | dict | 既往病史（用于既往症核查） |
| invoice_list | list | 发票清单（用于虚假发票核查） |
| admission_date | string | 入院日期 |
| discharge_date | string | 出院日期 |

## 输出结构

```json
{
  "claim_id": "CLM-20250610-001",
  "timestamp": "2026-06-10T13:00:00+08:00",
  "liability_assessment": {
    "decision": "属于保险责任",
    "coverage_details": [...],
    "exclusions": [...]
  },
  "fraud_check": {
    "score": 15,
    "risk_level": "低风险",
    "flags": [...],
    "details": [...]
  },
  "claim_calculation": {
    "total_expense": 80000.0,
    "insurance_paid": 30000.0,
    "deductible": 10000.0,
    "co_insurance_rate": 0.2,
    "final_reimbursement": 40000.0,
    "breakdown": [...]
  },
  "audit_points": [...],
  "processing_time": {
    "category": "普通件",
    "days": 7,
    "deadline": "2026-06-17"
  },
  "next_steps": [...]
}
```

## 反欺诈规则库（20+条）

### 一、虚假凭证类
1. **虚假发票** — 发票号重复、金额异常、医院不存在
2. **发票篡改** — 金额/日期/项目被修改
3. **伪造病历** — 病历签字造假、无挂号记录

### 二、医疗行为异常类
4. **过度医疗** — 套餐式检查、无关用药、超长住院
5. **挂名住院** — 实际未住院但产生床位费
6. **分解住院** — 同一病种短期内反复入院
7. **冒名就医** — 盗用他人医保卡就诊
8. **不合理治疗** — 诊断与治疗方案不符

### 三、既往症相关
9. **既往症未告知** — 投保前已患疾病未如实告知
10. **带病投保** — 等待期内确诊重疾
11. **症状倒签** — 出险日期早于实际就诊日期

### 四、保单异常类
12. **保险期间外** — 出险时间不在保单有效期内
13. **免赔额不达标** — 费用未超过免赔额
14. **保障范围外** — 就诊项目不在保障范围内
15. **未指定医院** — 就诊医院不符合条款要求

### 五、保额异常类
16. **高额理赔异常** — 理赔金额显著高于同类案件
17. **多家重复索赔** — 同时向多家保险公司索赔
18. **刚过等待期索赔** — 等待期刚过即大额索赔

### 六、行为异常类
19. **短期内频繁索赔** — 同一被保人多次理赔
20. **非本人领取** — 理赔款由非受益人领取
21. **理赔后退保** — 大额理赔后退保
22. **受益人异常变更** — 理赔前频繁变更受益人

## 责任认定逻辑

### 属于保险责任
- 出险在保险期间内
- 就诊医院符合条款
- 疾病/意外在保障范围内
- 无既往症/未告知情形
- 无责任免除事项

### 不属于保险责任
- 等待期内出险
- 既往症属于责任免除
- 就诊项目为免责条款（如美容整形）
- 保险期间外出险
- 故意行为/违法

### 部分属于
- 存在部分保障责任，但有除外项
- 比例赔付（仅按比例报销部分费用）
- 存在免赔额，需扣除后计算

## 理赔金额计算公式

```
应报销 = (总费用 - 医保已报销 - 免赔额) × 赔付比例
final = max(0, (total_expense - insurance_paid - deductible) × co_insurance_rate)
```

## 处理时效

| 类型 | 时效 | 说明 |
|------|------|------|
| 普通件 | 7个工作日 | 事实清晰、材料齐全 |
| 复杂件 | 30个工作日 | 需调查/协查/第三方核实 |
| 紧急件 | 3个工作日 | 涉及重大疾病/高额医疗 |

## 使用方式

### CLI
```bash
python3 scripts/claim_cli.py generate "理赔分析 医疗险 住院花费8万 就诊三甲医院 医保报销3万"
```

### Python API
```python
from claim_analysis import ClaimAnalysisEngine

engine = ClaimAnalysisEngine()
result = engine.analyze(
    insurance_type="医疗险",
    total_expense=80000,
    hospital_level="三甲医院",
    insurance_paid=30000
)
print(result)
```

### 企业微信集成
```python
from claim_analysis.wecom_integration import build_claim_card
card = build_claim_card(result)
# 发送至企业微信群
```

## 文件结构

```
claim_analysis/
├── SKILL.md
├── claim_engine.py      # 核心引擎
├── __init__.py
├── scripts/
│   └── claim_cli.py     # CLI入口
└── wecom_integration.py # 企微卡片
```

## 注意事项

1. 本引擎输出为**辅助参考**，最终理赔决定需人工审核确认
2. 反欺诈评分为统计模型，仅供参考，需结合实际调查
3. 涉及高额/复杂案件建议转交专业核保人员
4. 保持规则库更新，定期审计反欺诈规则有效性
