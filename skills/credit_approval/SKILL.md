# credit_approval - 信用审批技能

## 描述

信用审批技能通过多维度财务分析对企业及个人进行信用评估，输出信用评分（0-100）、杜邦分析、Altman Z-score财务预警、贷款额度建议、利率建议及最终审批结论。

## 输入

- **企业名称**：待评估企业名称（字符串）
- **年营收/销售额**：主营业务收入（万元，数值）
- **负债率**：总负债/总资产（%，数值，0-100）
- **利润率**：净利润/营业收入（%，数值）
- **经营年限**：企业存续年限（年，数值）
- **行业类型**：制造业/服务业/零售业/科技业/建筑业等（字符串，可选）
- **流动比率**：流动资产/流动负债（可选，若不提供则用经验值1.5估算）
- **资产总额**：企业总资产（万元，可选）

## 输出

```json
{
  "credit_score": 0-100,
  "grade": "AAA/AA/A/BBB/BB/B/CCC/CC/C/D",
  "approval_conclusion": "通过/有条件通过/拒绝",
  "dupont_analysis": {
    "ROE": 0.0,
    "net_margin": 0.0,
    "asset_turnover": 0.0,
    "equity_multiplier": 0.0,
    "breakdown": "ROE = 净利率 × 资产周转率 × 权益乘数"
  },
  "z_score": {
    "value": 0.0,
    "zone": "灰色区/破产区/安全区",
    "warning": "预警描述"
  },
  "loan_suggestion": {
    "max_amount": 0.0,
    "currency": "CNY",
    "unit": "万元",
    "tenor": "12/24/36个月"
  },
  "interest_rate_suggestion": {
    "base_rate": 0.0,
    "spread": 0.0,
    "final_rate": 0.0,
    "description": "利率描述"
  },
  "scoring_details": {
    "debt_ratio_score": 0-20,
    "current_ratio_score": 0-20,
    "profit_margin_score": 0-20,
    "operating_years_score": 0-20,
    "industry_risk_score": 0-20
  }
}
```

## 杜邦分析（DuPont Analysis）

**核心公式**：
```
ROE = 净利率 × 资产周转率 × 权益乘数
ROE = (净利润/营业收入) × (营业收入/总资产) × (总资产/净资产)
```

### ROE 三因素拆解

| 因素 | 计算公式 | 含义 |
|------|---------|------|
| 净利率 (Net Margin) | 净利润 / 营业收入 | 盈利能力 |
| 资产周转率 (Asset Turnover) | 营业收入 / 总资产 | 运营效率 |
| 权益乘数 (Equity Multiplier) | 总资产 / 净资产 | 财务杠杆 |

### ROE 分级标准

- ROE > 20%：优秀
- ROE 15-20%：良好
- ROE 10-15%：中等
- ROE < 10%：较差

## Altman Z-score 模型

**公式**（适用于私营企业）：
```
Z = 1.2X1 + 1.4X2 + 3.3X3 + 0.6X4 + 1.0X5
```

| 变量 | 计算公式 | 含义 |
|------|---------|------|
| X1 | 营运资本 / 总资产 | 流动性 |
| X2 | 留存收益 / 总资产 | 盈利能力 |
| X3 | EBIT / 总资产 | 资产收益率 |
| X4 | 股东权益 / 总负债 | 偿债能力 |
| X5 | 营业收入 / 总资产 | 资产周转率 |

### Z-score 区间

| Z值 | 区间 | 预警 |
|-----|------|------|
| Z > 2.99 | 安全区 | 低风险 |
| 1.81 < Z < 2.99 | 灰色区 | 中等风险，需关注 |
| Z < 1.81 | 破产区 | 高风险，财务危机 |

## 信用评分维度

| 维度 | 权重 | 评分标准 |
|------|------|---------|
| 资产负债率 | 20分 | ≤40%满分，每超5%扣2分 |
| 流动比率 | 20分 | ≥2满分，1.5-2扣5分，<1.5扣10分 |
| 利润率 | 20分 | ≥15%满分，每降2%扣1分 |
| 经营年限 | 20分 | ≥10年满分，每少1年扣2分 |
| 行业风险 | 20分 | 制造业10分/服务业12分/零售业8分/科技业15分/建筑业6分 |

## 贷款额度建议模型

基于信用评分和年营收计算：

```
max_loan = min(年营收 × 信用系数, 净资产 × 抵押折扣)
```

| 信用等级 | 信用系数 | 抵押折扣 |
|---------|---------|---------|
| AAA | 0.5 | 0.8 |
| AA | 0.4 | 0.7 |
| A | 0.3 | 0.6 |
| BBB | 0.2 | 0.5 |
| BB | 0.15 | 0.4 |
| B | 0.1 | 0.3 |
| CCC | 0.05 | 0.2 |
| CC-C | 0 | 0 |

## 利率建议模型

```
最终利率 = 基准利率 + 风险溢价 + 期限溢价
```

- 基准利率：4.35%（1年期LPR）
- 风险溢价：根据信用等级，AAA=+0.5%，AA=+0.8%，A=+1.2%，BBB=+1.8%，BB=+2.5%，B=+3.5%，CCC=+5%，CC-C=拒绝
- 期限溢价：1年期+0%，2年期+0.2%，3年期+0.4%

## 使用方式

### Python 调用

```python
from credit_approval import CreditApprovalEngine

engine = CreditApprovalEngine()
result = engine.evaluate(
    company_name="某制造企业",
    annual_revenue=5000,      # 万元
    debt_ratio=60,           # %
    profit_margin=8,          # %
    operating_years=5,        # 年
    industry="制造业",
    current_ratio=1.8,        # 可选
    total_assets=8000         # 万元，可选
)

print(result)
```

### CLI 调用

```bash
python3 scripts/credit_cli.py generate "信用审批 某制造企业 年营收5000万 负债率60% 利润率8%"
python3 scripts/credit_cli.py evaluate --revenue 5000 --debt 60 --profit 8 --years 5 --industry 制造业
```

### 企业微信集成

```python
from credit_approval.wecom_integration import build_credit_card

card = build_credit_card(result)
# 发送至企业微信群或个人
```

## 适用场景

- 企业贷款审批
- 供应商信用评估
- 客户信用分级
- 保理业务准入
- 项目融资尽调

## 注意事项

1. 本模型输出仅供参考，实际审批需结合人工复核
2. 流动比率若未提供，默认使用1.5估算
3. 资产总额若未提供，按年营收/0.5估算总资产
4. 净资产按总资产×(1-负债率/100)估算
5. EBIT按净利润×1.3估算（适用于一般企业）
