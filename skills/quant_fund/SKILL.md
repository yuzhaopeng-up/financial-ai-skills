# quant_fund - 量化基金分析引擎

## 概述

`quant_fund` 是金融场景量化基金深度分析技能，提供因子暴露分析、风格漂移检测、Brinson归因等核心功能。

## 核心能力

### 1. 因子暴露分析

基于 **Fama-French 五因子 + Carhart 四因子扩展** 模型：

| 因子 | 名称 | 说明 |
|------|------|------|
| Alpha | 超额收益 | 不可解释收益 |
| Beta | 市场敏感度 | 相对基准波动 |
| SMB | 市值因子 | 小盘股效应 |
| HML | 价值因子 | 低PB vs 高PB |
| RMW | 盈利因子 | 高盈利 vs 低盈利 |
| CMA | 投资因子 | 低投资 vs 高投资 |
| MOM | 动量因子 | 过去12个月收益 |

### 2. 风格漂移检测

- **方法**：基于滚动收益率的风格回归（60日窗口）
- **对比**：当前实现风格 vs 基金契约约定风格
- **阈值**：偏离度 > 15% 触发预警

### 3. Brinson 归因分析

三层归因拆解：

| 效应 | 含义 |
|------|------|
| 选股效应 (Selection) | 超配好股票带来的收益 |
| 行业配置效应 (Allocation) | 超配好行业带来的收益 |
| 交互效应 (Interaction) | 选股与配置的交叉贡献 |

### 4. 业绩归因

综合考虑：
- 基准收益
- 因子暴露贡献
- 选股贡献
- 行业配置贡献
- 交易成本

## 输入参数

| 参数 | 类型 | 说明 |
|------|------|------|
| fund_code | str | 基金代码（F000001格式） |
| fund_name | str | 基金名称（可选） |
| benchmark | str | 基准指数代码（默认沪深300） |
| period | str | 分析区间（默认近1年） |

## 输出格式

```json
{
  "fund_code": "F000001",
  "fund_name": "某量化基金",
  "factor_exposure": {
    "alpha": 0.023,
    "beta": 1.12,
    "smb": 0.15,
    "hml": -0.08,
    "rmw": 0.21,
    "cma": -0.05,
    "mom": 0.12
  },
  "style_drift": {
    "current_style": {"size": 0.3, "value": 0.2, "growth": 0.5},
    "contract_style": {"size": 0.5, "value": 0.3, "growth": 0.2},
    "drift_score": 0.28,
    "alert": "LOW"
  },
  "brinson_attribution": {
    "selection_effect": 0.034,
    "allocation_effect": 0.021,
    "interaction_effect": 0.008,
    "total_attribution": 0.063
  },
  "performance_attribution": {
    "benchmark_return": 0.081,
    "factor_contribution": 0.052,
    "selection_contribution": 0.034,
    "allocation_contribution": 0.021,
    "timing_contribution": 0.008,
    "net_return": 0.118
  }
}
```

## 使用方式

### CLI 模式

```bash
python3 scripts/quant_cli.py generate "量化基金分析 F000001"
python3 scripts/quant_cli.py factor F000001
python3 scripts/quant_cli.py style F000001
python3 scripts/quant_cli.py brinson F000001
```

### Python API

```python
from quant_engine import QuantFundEngine

engine = QuantFundEngine()
result = engine.analyze(fund_code="F000001", fund_name="某量化基金")
print(result)
```

## 数据脱敏

- 基金代码统一使用 `Fxxxxxx` 格式
- 基金名称使用"某量化基金"占位
- 如需真实数据，请替换为实际基金代码

## 技术栈

- Python 3.8+
- pandas / numpy：数据处理
- scipy.stats：统计分析
- statsmodels：回归分析

## 相关技能

- `fund_compare`：基金多维度对比
- `fund_manager_profile`：基金经理画像
- `dca_calculator`：定投计算器
