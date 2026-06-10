# 寿险理赔审核技能 (Claim Review V2)

## 功能概述

**寿险理赔审核引擎 V2** — 专注寿险理赔场景，输入理赔案件信息，自动输出：
- 理赔审核结果（正常赔付 / 比例赔付 / 拒赔 / 需补充材料）
- 审核要点（病史关联性 / 免赔条款 / 保单有效性）
- 理赔金额计算
- 反欺诈检查

## 适用场景

- 终身寿险理赔审核
- 定期寿险理赔审核
- 两全险理赔审核
- 重疾险理赔核查
- 医疗险理赔审核
- 意外险理赔审核
- 理赔初审 / 复核流程
- 反欺诈风险筛查

## 险种类型

| 险种 | 代码 | 说明 |
|------|------|------|
| 终身寿险 | whole_life | 保障终身，被保险人身故/全残赔付 |
| 定期寿险 | term_life | 保障期限固定（10/20/30年等） |
| 两全险 | endowment | 生存保险金+身故保险金 |
| 重疾险 | critical_illness | 约定重疾确诊即赔 |
| 医疗险 | medical | 医疗费用报销 |
| 意外险 | accident | 意外伤害/医疗/身故 |

## 审核规则

### 一、等待期规则
| 出险类型 | 等待期 | 说明 |
|----------|--------|------|
| 普通疾病 | 180天 | 续保时不再重新计算 |
| 意外事故 | 3天 | 从保单生效日起算 |
| 重疾 | 90天/180天 | 以合同约定为准 |

### 二、既往症规则
- **既往症不赔**：既往症属于责任免除，投保前已患疾病不在保障范围
- **带病投保**：等待期内确诊重疾拒赔
- **症状倒签**：出险日期早于实际就诊日期拒赔

### 三、责任免除规则（常见）
- **酒驾 / 无证驾驶**：拒赔
- **无证驾驶机动车**：拒赔
- **自杀 / 故意行为**：身故险拒赔
- **战争 / 暴乱**：拒赔
- **核辐射 / 污染**：拒赔
- **先天性疾病**：拒赔
- **美容整形**：医疗险拒赔

### 四、保单有效性规则
- 保单需在有效期内
- 保费缴纳正常（无欠费）
- 受益人需明确

## 输入参数

| 字段 | 类型 | 说明 |
|------|------|------|
| insurance_type | string | 险种类型（见险种类型表） |
| accident_type | string | 出险类型：疾病/意外/全残/身故 |
| accident_reason | string | 出险原因 |
| hospital_level | string | 就诊医院等级：三甲医院/三乙医院/二甲医院/其他 |
| total_expense | float | 住院总花费（元） |
| insurance_paid | float | 医保已报销金额（元） |
| policy_terms | dict | 保单条款（含免赔额/赔付比例/保障范围等） |
| patient_history | dict | 既往病史 |
| admission_date | string | 入院日期（YYYY-MM-DD） |
| discharge_date | string | 出院日期（YYYY-MM-DD） |
| policy_start_date | string | 保单生效日期 |
| policy_years | int | 保单生效年限 |
| premium_paid | bool | 保费是否正常缴纳 |
| beneficiary | string | 受益人名称 |
| beneficiary_relation | string | 受益人与被保险人关系 |
| claim_amount | float | 申请理赔金额（元） |
| death_certificate | bool | 是否提供死亡证明 |
| accident_report | bool | 是否提供事故证明 |

## 输出结构

```json
{
  "claim_id": "CLM-V2-20250610-001",
  "timestamp": "2026-06-10T13:00:00+08:00",
  "review_decision": {
    "result": "正常赔付",
    "code": "APPROVED",
    "reason": ""
  },
  "audit_points": {
    "history_relevance": {
      "has_pre_existing": false,
      "related": false,
      "details": []
    },
    "exclusion_clauses": {
      "triggered": [],
      "not_triggered": []
    },
    "policy_validity": {
      "valid": true,
      "issues": []
    }
  },
  "claim_calculation": {
    "claim_amount": 500000.0,
    "approved_amount": 500000.0,
    "deductible": 0.0,
    "co_insurance_rate": 1.0,
    "final_payment": 500000.0,
    "breakdown": []
  },
  "fraud_check": {
    "score": 10,
    "risk_level": "低风险",
    "flags": [],
    "details": []
  },
  "processing_time": {
    "category": "普通件",
    "days": 7,
    "deadline": "2026-06-17"
  },
  "next_steps": []
}
```

## 审核决策类型

| 决策 | 代码 | 说明 |
|------|------|------|
| 正常赔付 | APPROVED | 材料齐全，符合保险责任，全额赔付 |
| 比例赔付 | PROPORTIONAL | 部分符合，按约定比例赔付 |
| 拒赔 | REJECTED | 不符合保险责任 |
| 需补充材料 | PENDING_MATERIALS | 材料不完整，需补充 |

## 反欺诈规则库（20+条）

### 一、保单异常类
1. **高额理赔异常** — 理赔金额显著高于同类案件
2. **多家重复索赔** — 同时向多家保险公司索赔
3. **刚过等待期索赔** — 等待期刚过即大额索赔
4. **受益人异常变更** — 理赔前频繁变更受益人
5. **退保后索赔** — 退保后提出理赔申请

### 二、虚假凭证类
6. **虚假死亡证明** — 死亡证明伪造/篡改
7. **虚假事故证明** — 事故认定书造假
8. **伪造病历** — 病历签字造假
9. **发票篡改** — 金额/日期被修改

### 三、医疗行为异常类
10. **过度医疗** — 套餐式检查/无关用药
11. **分解住院** — 同一病种短期内反复入院
12. **冒名就医** — 盗用他人身份就诊

### 四、行为异常类
13. **短期内频繁索赔** — 同一被保人多次理赔
14. **非本人领取** — 理赔款由非受益人领取
15. **故意制造事故** — 故意行为导致保险事故

### 五、责任免除类
16. **酒驾拒赔** — 酒后驾驶导致身故/伤残
17. **无证驾驶拒赔** — 无合法驾照驾驶机动车
18. **自杀/故意行为** — 故意自伤/自残
19. **违法犯罪** — 因犯罪行为导致身故

## 理赔金额计算

```
寿险（身故/全残）:
  最终赔付额 = 保额 × 赔付比例
  （一般情况：保额 = 申请理赔金额）

医疗险:
  应报销 = (总费用 - 医保已报销 - 免赔额) × 赔付比例
  final = max(0, (total_expense - insurance_paid - deductible) × co_insurance_rate)

重疾险:
  确诊即赔：一次性给付保险金
  final = 保额（无需计算）
```

## 处理时效

| 类型 | 时效 | 说明 |
|------|------|------|
| 普通件 | 7个工作日 | 材料齐全、事实清晰 |
| 复杂件 | 30个工作日 | 需调查/协查/第三方核实 |
| 紧急件 | 3个工作日 | 涉及高额/重大案件 |

## 使用方式

### CLI
```bash
python3 scripts/claim_review_cli.py generate "理赔审核 寿险 身故理赔 受益人申请 既往无相关病史 保费缴纳正常"
python3 scripts/claim_review_cli.py generate "理赔审核 重疾险 恶性肿瘤 初次确诊"
```

### Python API
```python
from claim_review_v2 import ClaimReviewV2Engine

engine = ClaimReviewV2Engine()
result = engine.review(
    insurance_type="终身寿险",
    accident_type="身故",
    claim_amount=500000,
    policy_years=3,
    premium_paid=True
)
print(result)
```

### 企业微信集成
```python
from claim_review_v2.wecom_integration import build_review_card
card = build_review_card(result)
```

## 文件结构

```
claim_review_v2/
├── SKILL.md
├── claim_review_engine.py  # 核心引擎
├── __init__.py
├── scripts/
│   └── claim_review_cli.py # CLI入口
└── wecom_integration.py    # 企微卡片
```

## 注意事项

1. 本引擎输出为**辅助参考**，最终理赔决定需人工审核确认
2. 反欺诈评分为参考值，需结合实际调查
3. 涉及高额/复杂案件建议转交专业核保人员
4. 保持规则库更新，定期审计反欺诈规则有效性
