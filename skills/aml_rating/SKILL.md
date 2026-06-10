# AML Rating Skill — 反洗钱客户评级

## 概述

**aml_rating** 是金融场景下的反洗钱（Anti-Money Laundering）客户风险评级技能，对客户进行多维度洗钱风险评估，返回风险等级、风险评分及管控措施建议。

## 核心能力

- 多维度风险评分：地域风险 × 行业风险 × 业务风险 × 客户特征
- 风险等级划分：极低 / 低 / 中 / 高 / 极高（对应 0-100 分）
- 完整的风险因素拆解与归因
- 针对性管控措施建议
- 企微卡片输出集成

## 风险维度

| 维度 | 指标 | 最高加分 |
|------|------|----------|
| 地域风险 | 涉制裁/洗钱高发区 | +20 |
| 行业风险 | 高风险行业 | +15 |
| 业务风险 | 跨境交易、大额交易、现金交易 | 各 +10 |
| 客户特征 | 空壳公司、代持结构 | +20 |

## 风险等级

| 评分范围 | 风险等级 | 颜色标识 |
|----------|----------|----------|
| 0–20 | 极低 | 🟢 |
| 21–40 | 低 | 🔵 |
| 41–60 | 中 | 🟡 |
| 61–80 | 高 | 🟠 |
| 81–100 | 极高 | 🔴 |

## 使用方式

### CLI

```bash
python3 scripts/aml_cli.py generate "AML评级 某客户 贸易行业 受益人信息完整"
```

### Python API

```python
from aml_rating import AMLRatingEngine

engine = AMLRatingEngine()
result = engine.rate(
    customer_name="某客户",
    industry="贸易行业",
    region="中国",
    transaction_features=["跨境", "大额"],
    id_validity_days=365,
    has_beneficial_owner=True
)
print(result)
```

## 输入参数

| 参数 | 类型 | 说明 |
|------|------|------|
| customer_name | str | 客户名称 |
| industry | str | 行业类型 |
| region | str | 地区/国家 |
| transaction_features | list[str] | 交易特征（跨境/大额/现金等） |
| id_validity_days | int | 证件有效期（天） |
| has_beneficial_owner | bool | 是否有明确受益人 |

## 输出字段

```json
{
  "customer_name": "某客户",
  "risk_level": "中",
  "risk_score": 45,
  "risk_factors": {
    "地域风险": {"score": 0, "factors": []},
    "行业风险": {"score": 10, "factors": ["一般贸易行业"]},
    "业务风险": {"score": 20, "factors": ["跨境交易"]},
    "客户特征": {"score": 15, "factors": ["受益人信息完整"]}
  },
  "recommendations": ["建议进行定期回顾", "..."]
}
```

## 文件结构

```
aml_rating/
├── SKILL.md
├── aml_engine.py       # 核心引擎 AMLRatingEngine
├── __init__.py
├── scripts/
│   └── aml_cli.py      # CLI 入口
└── wecom_integration.py # 企微卡片集成
```

## 适用场景

- 对公客户开户尽职调查
- 客户定期风险重评
- 可疑交易监控辅助判断
- 监管报送风险筛选
