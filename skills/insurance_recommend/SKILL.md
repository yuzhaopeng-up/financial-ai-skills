# Insurance Recommend Skill - 保险产品智能推荐

## 1. 技能概述

**技能名称**: insurance_recommend  
**功能定位**: 根据客户画像（年龄/家庭结构/收入/已有保单/保障缺口/预算），输出保险产品推荐方案  
**核心能力**: 险种组合建议 / 保额精确计算 / 保费预算规划 / 产品匹配 / 推荐理由说明 / 家庭保障全景

---

## 2. 核心原则

1. **先保障后理财** - 优先配置保障型保险，再考虑理财型
2. **先大人后小孩** - 家庭经济支柱优先保障
3. **先家庭经济支柱** - 家庭收入最高者保障最全面

---

## 3. 保额计算规则

| 险种 | 计算公式 | 说明 |
|------|---------|------|
| 定期寿险 | 年收入 × 10 + 负债 | 覆盖家庭责任期 |
| 终身寿险 | 年收入 × 10~15 | 资产传承 |
| 意外险 | 年收入 × 10 | 身价保障 |
| 医疗险 | 300万+ | 大病医疗覆盖 |
| 重疾险 | 年收入 × 3~5 | 康复期收入补偿 |
| 年金险 | 量力而行 | 养老规划 |

---

## 4. 输入参数

```python
{
    "age": 30,                    # 年龄
    "gender": "male",             # 性别 male/female
    "family": {                   # 家庭结构
        "married": True,
        "children": [{"age": 1}], # 孩子列表
        "dependents": 0           # 赡养父母数量
    },
    "annual_income": 300000,      # 年收入（元）
    "existing_policies": [        # 已有保单
        {"type": "医保", "coverage": 100000}
    ],
    "liabilities": {              # 负债
        "mortgage": 2000000,      # 房贷
        "car_loan": 0,
        "other_debt": 0
    },
    "budget_percent": 0.1,        # 保费占年收入比例（默认10%）
    "health_status": "good"       # 健康状况 good/average/poor
}
```

---

## 5. 输出结构

```python
{
    "customer_profile": {...},    # 客户画像摘要
    "protection_gap": {           # 保障缺口分析
        "life_insurance_gap": 2800000,
        "critical_illness_gap": 1200000,
        "medical_gap": 2000000,
        "accident_gap": 3000000
    },
    "recommendations": [          # 推荐方案（按优先级排序）
        {
            "priority": 1,
            "insurance_type": "定期寿险",
            "product_matching": "华贵大麦2024定期寿险",
            "coverage": 3000000,
            "annual_premium": 3000,
            "policy_term": "30年",
            "reason": "家庭经济支柱必备，防止身故导致家庭经济崩溃",
            "key_benefits": ["身故/全残保障", "健康告知宽松", "性价比高"]
        },
        ...
    ],
    "family_protection_overview": {  # 家庭保障全景
        "total_coverage_needed": 9200000,
        "current_coverage": 100000,
        "gap": 9100000,
        "priority_order": ["定期寿险", "意外险", "医疗险", "重疾险", "年金险"]
    },
    "premium_budget": {           # 保费预算
        "total_annual": 30000,
        "by_type": {
            "保障型": 20000,
            "理财型": 10000
        }
    }
}
```

---

## 6. 险种优先级矩阵

| 家庭角色 | 第一优先 | 第二优先 | 第三优先 | 第四优先 |
|---------|---------|---------|---------|---------|
| 未婚青年 | 意外险 | 医疗险 | 重疾险 | 定寿 |
| 已婚无孩 | 寿险 | 意外险 | 医疗险 | 重疾险 |
| 已婚有孩 | 寿险 | 意外险 | 医疗险 | 重疾险 |
| 中年家庭支柱 | 寿险 | 意外险 | 重疾险 | 医疗险 |
| 老年人 | 医疗险 | 意外险 | 防癌险 | - |

---

## 7. 适用场景

- 客户咨询保险配置
- 家庭保障缺口分析
- 保险产品对比推荐
- 保费预算规划

---

## 8. 使用方式

```bash
# CLI方式
python3 scripts/ins_rec_cli.py generate "保险推荐 30岁男性 已婚 孩子1岁 年收入30万 已有医保"

# Python模块方式
from insurance_recommend import InsuranceRecommendEngine
engine = InsuranceRecommendEngine()
result = engine.generate_recommendation(age=30, gender="male", ...)
```

---

## 9. 产品知识库（示例）

| 险种 | 推荐产品示例 | 年保费参考 | 特点 |
|------|------------|----------|------|
| 定期寿险 | 华贵大麦2024 | 3000元/300万 | 健康告知宽松 |
| 终身寿险 | 同方全球传世荣耀 | 15000元/100万 | 现金价值增长 |
| 意外险 | 平安小顽童5号 | 200元/50万 | 少儿专属 |
| 医疗险 | 太平洋蓝医保 | 300元/400万 | 20年保证续保 |
| 重疾险 | 国联人寿明爱易心 | 5000元/50万 | 重疾额外赔 |
| 年金险 | 太平岁岁金生 | 20000元 | 养老社区对接 |
