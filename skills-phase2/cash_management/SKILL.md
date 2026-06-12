# 现金管理技能 (Cash Management)

## 概述
针对企业客户的现金管理方案生成引擎，输入企业类型、月度现金流规模、波动特征，输出优化建议。

## 功能
- 账户架构设计（活期/定期/通知存款/协定存款/现金池）
- 短期理财产品推荐（货币基金/通知存款/协定存款/结构性存款）
- 收益率提升建议
- 流动性保障方案
- 税务优化建议

## 使用方式
```bash
# CLI 入口
python3 scripts/cash_cli.py generate "现金管理 制造企业 月现金流5000万"

# Python API
from cash_management import CashManagementEngine
engine = CashManagementEngine()
result = engine.generate("制造企业", 50000000, "中等波动")
```

## 返回字段
| 字段 | 说明 |
|------|------|
| account_architecture | 账户架构设计 |
| products | 推荐产品列表 |
| yield_improvement | 收益率提升建议 |
| liquidity_plan | 流动性保障方案 |
| tax_optimization | 税务优化建议 |
