# 定投计算器 (DCA Calculator)

## 概述
定投计算器是一个金融分析工具，通过模拟定期定额投资策略，帮助用户评估定投指数基金的收益表现。

## 功能特性
- 支持 10+ 主流指数基金内置
- 三种收益率情景分析：乐观(年化15%) / 中性(年化8%) / 悲观(年化-5%)
- 输出完整月度定投模拟记录
- 核心指标：累计投入、期末总资产、累计收益、收益率、年化收益率

## 内置指数基金
| 基金代码 | 基金名称 | 类型 |
|----------|----------|------|
| 000300.SH | 沪深300 | A股宽基 |
| 000905.SH | 中证500 | A股宽基 |
| 399006.SZ | 创业板指 | A股宽基 |
| 000688.SH | 科创50 | A股宽基 |
| 139930.SZ | 深证100 | A股宽基 |
| 000001.SH | 上证指数 | A股宽基 |
| NDX.O | 纳斯达克100 | 美股 |
| SPX.GI | 标普500 | 美股 |
| GDAXI.GI | 德国DAX | 欧股 |
| N225.GI | 日经225 | 亚太 |
| CSI930850.SH | 中证红利 | A股策略 |
| CSI701010.SH | 消费红利 | A股策略 |
| 000922.CSI | 中证500低波动 | A股SmartBeta |
| CSI716567.SH | 科创50 | 科创板 |
| CSI000852.SH | 中证1000 | A股宽基 |

## 使用方式

### CLI
```bash
python3 scripts/dca_cli.py generate "定投计算 沪深300 每月1000元 3年"
```

### Python API
```python
from dca_calculator import DCACalculatorEngine

engine = DCACalculatorEngine()
result = engine.calculate(
    fund_name="沪深300",
    amount=1000,
    frequency="monthly",
    years=3,
    expected_return=0.08
)
```

## 输出字段
- `total_invested`: 累计投入本金
- `final_value`: 期末总资产
- `total_return`: 累计收益（绝对值）
- `total_return_rate`: 累计收益率（%）
- `annualized_return`: 年化收益率（%）
- `scenario_analysis`: 三种情景分析
- `monthly_records`: 月度定投明细

## 集成
- WeCom 企业微信卡片集成 (`wecom_integration.py`)
- 支持直接推送至企业微信群
