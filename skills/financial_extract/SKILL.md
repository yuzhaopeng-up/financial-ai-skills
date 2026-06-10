# financial_extract — 财报智能提取

## 定位

输入财务报表原始数据（营收、利润、资产、负债），输出结构化财务指标、同业对比、杜邦分析、异常预警。

## 输入

| 字段 | 类型 | 说明 |
|------|------|------|
| company | string | 公司名称（脱敏为"某公司"） |
| revenue | float | 营业收入（万元） |
| net_profit | float | 净利润（万元） |
| total_assets | float | 总资产（万元） |
| total_liabilities | float | 总负债（万元） |
| operating_cost | float | 营业成本（万元），可选 |
| interest_expense | float | 利息支出（万元），可选 |
| equity | float | 股东权益（万元），可选，由 total_assets - total_liabilities 计算 |

## 输出

### 财务指标

| 指标 | 计算公式 | 说明 |
|------|----------|------|
| 毛利率 | (营收 - 营业成本) / 营收 × 100% | 盈利能力 |
| 净利率 | 净利润 / 营收 × 100% | 净利润率 |
| ROE | 净利润 / 股东权益 × 100% | 净资产收益率 |
| 资产负债率 | 总负债 / 总资产 × 100% | 杠杆水平 |
| 营收增长率 | 需历史数据 | 成长性 |

### 杜邦分析

- 净利率 = 净利润 / 营收
- 总资产周转率 = 营收 / 总资产
- 权益乘数 = 总资产 / 股东权益
- ROE = 净利率 × 总资产周转率 × 权益乘数

### 同业对比

| 指标 | 某公司 | 行业均值 | 参考值 |
|------|--------|----------|--------|
| 毛利率 | 自动计算 | 40% | 行业标杆 |
| 净利率 | 自动计算 | 15% | 行业标杆 |
| ROE | 自动计算 | 12% | 行业标杆 |
| 资产负债率 | 自动计算 | 60% | 行业标杆 |

### 异常预警

| 预警等级 | 条件 | 说明 |
|----------|------|------|
| 🔴 高 | 资产负债率 > 80% | 杠杆过高 |
| 🟡 中 | 资产负债率 > 70% | 偏高 |
| 🟡 中 | 净利率 < 5% | 盈利能力弱 |
| 🟢 低 | 其他 | 正常范围 |

## 使用方式

### CLI

```bash
python3 scripts/extract_cli.py generate "财报提取 某公司 营收1000万 净利润80万 资产2000万 负债1200万"
```

### Python API

```python
from financial_extract import FinancialExtractEngine

engine = FinancialExtractEngine()
result = engine.extract(
    company="某公司",
    revenue=1000,
    net_profit=80,
    total_assets=2000,
    total_liabilities=1200
)
print(result)
```

## 文件结构

```
financial_extract/
├── SKILL.md
├── extract_engine.py     # 核心引擎
├── __init__.py
├── scripts/
│   └── extract_cli.py     # CLI入口
└── wecom_integration.py  # 企微卡片
```

## 依赖

- Python 3.8+
- 无外部依赖（纯计算引擎）

## 版本

- v1.0.0 (2026-06-10) 初始版本
