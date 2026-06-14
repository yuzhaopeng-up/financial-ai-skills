# 银行信贷审批智能化：信用评分88分自动通过50万

> 开源地址：https://github.com/yuzhaopeng-up/financial-ai-skills
>
> 基于《AI赋能银行数字化转型》第14-15章实战代码。

---

## 一、传统信贷审批的痛点

某银行信贷经理的日常：

- **申请受理**：纸质材料，手工录入，容易出错
- **信用评估**：查征信、算分数，2小时一笔
- **审批决策**：层层上报，3-5个工作日出结果
- **贷后管理**：人工监控，逾期了才发现

**结果**：客户流失到互联网金融平台。

---

## 二、AI信贷审批：4步自动完成

```python
from credit_approval import CreditApprovalEngine

engine = CreditApprovalEngine()

# 完整审批流程
result = engine.full_approval_process(
    application_id="APP20250606001",
    applicant_type="个人",
    name="张三",
    id_number="31010119900101XXXX",
    phone="13800138000",
    loan_amount=500000,
    loan_purpose="住房",
    loan_term_months=240,
    income_monthly=25000,
    documents=["身份证", "收入证明", "银行流水", "购房合同", "首付证明", "征信授权书"],
    age=35,
    education="本科",
    occupation="IT工程师",
    housing_status="租房",
    credit_history_years=10,
    existing_loans=1,
    overdue_count_24m=0,
    max_overdue_days=0,
    credit_utilization=0.3,
    query_count_6m=2,
    payment_regularity="按时",
    existing_debts_monthly=5000,
    collateral_value=800000
)
```

**输出**：
```
🏦 信贷审批报告
├── 申请信息：张三，住房按揭50万，240期
├── 信用评分：88.0 分，AA级（信用优秀）
│   ├── 身份特质：16.0 分
│   ├── 信用历史：25 分（满分）
│   ├── 行为偏好：20 分（满分）
│   ├── 履约能力：22.0 分
│   └── 社交关系：5.0 分
└── 审批决策：🟢 自动通过
    ├── 批准金额：500,000 元
    ├── 批准利率：4.55%（抵押物优惠）
    └── 审批理由：信用评分优秀，抵押物充足
```

---

## 三、8大能力

| 能力 | 描述 | 书中对应 |
|------|------|---------|
| **信贷申请受理** | 申请信息校验、材料完整性检查 | 第14章 14.1 |
| **信用评分模型** | 多维度信用评分、行为评分 | 第14章 14.2 |
| **审批决策引擎** | 规则引擎+模型决策、自动审批 | 第14章 14.3 |
| **额度测算模型** | 收入偿债比、抵押物评估 | 第14章 14.4 |
| **担保评估** | 担保人资质、抵质押物估值 | 第14章 14.5 |
| **合同生成** | 标准化合同条款、风险提示 | 第14章 14.6 |
| **贷后预警** | 还款监控、风险信号识别 | 第15章 15.1 |
| **催收策略** | 分级催收、智能外呼 | 第15章 15.2 |

---

## 四、核心算法

### 4.1 信用评分（五维模型）

```python
def calculate_score(self, age, education, occupation, income_monthly,
                    housing_status, credit_history_years, existing_loans,
                    overdue_count_24m, max_overdue_days, credit_utilization,
                    query_count_6m, payment_regularity):
    
    # 1. 身份特质 (20分)
    identity = self._score_identity(age, education, occupation, housing_status)
    
    # 2. 信用历史 (25分)
    credit_history = self._score_credit_history(
        credit_history_years, overdue_count_24m, max_overdue_days)
    
    # 3. 行为偏好 (20分)
    behavior = self._score_behavior(credit_utilization, query_count_6m, payment_regularity)
    
    # 4. 履约能力 (25分)
    ability = self._score_ability(income_monthly, existing_loans)
    
    # 5. 社交关系 (10分)
    social = self._score_social(occupation)
    
    total = identity + credit_history + behavior + ability + social
    return CreditScore(total, CreditGrade.get_grade(total))
```

### 4.2 审批决策

```python
def make_decision(self, credit_score, loan_amount, income_monthly,
                  existing_debts_monthly, collateral_value):
    
    # 计算债务收入比
    debt_ratio = (existing_debts_monthly + estimate_monthly_payment(loan_amount)) / income_monthly
    
    # 自动通过条件
    if (credit_score >= 80 and debt_ratio <= 0.5 and 
        overdue_count == 0 and income >= 10000):
        return DecisionResult.AUTO_APPROVE
    
    # 人工复核条件
    elif (credit_score >= 60 and debt_ratio <= 0.7 and
          overdue_count <= 2 and income >= 5000):
        return DecisionResult.MANUAL_REVIEW
    
    # 拒绝
    else:
        return DecisionResult.REJECT
```

---

## 五、等额本息算法

```python
def estimate_monthly_payment(loan_amount, annual_rate=0.0435, term_months=240):
    """等额本息公式"""
    monthly_rate = annual_rate / 12
    payment = loan_amount * monthly_rate * (1 + monthly_rate) ** term_months / \
              ((1 + monthly_rate) ** term_months - 1)
    return payment
```

---

## 六、开源

```
https://github.com/yuzhaopeng-up/financial-ai-skills/tree/master/skills/credit-approval
```

---

> **关于作者**：作者，金融科技从业经历，服务超500家金融机构。《AI赋能银行数字化转型》作者。
