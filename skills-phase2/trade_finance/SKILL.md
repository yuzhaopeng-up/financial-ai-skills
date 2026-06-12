# Trade Finance Skill（贸易融资技能）

## 概述

本技能为进出口企业提供全面的贸易融资方案推荐与对比分析，基于企业类型、贸易类型、融资金额、账期等关键参数，智能推荐最适合的融资产品。

## 支持产品

| 产品 | 英文名 | 适用场景 |
|------|--------|----------|
| 信用证 | L/C | 进出口双方不信任，需银行信用介入 |
| 国际保理 | International Factoring | 出口企业赊销，想提前变现应收账款 |
| 福费廷 | Forfaiting | 中长期大额应收账款买断 |
| 出口押汇 | Export Bill Forward | 出口单据未齐，想提前用单据融资 |
| 进口押汇 | Import Bill Forward | 进口企业想延期付款但要赎单 |
| 打包贷款 | Packing Credit | 出口企业采购备货阶段融资 |
| 订单融资 | Order Financing | 拿到订单合同，想提前采购生产 |
| 保单融资 | Insurance Policy Financing | 以出口信用保险保单为担保融资 |

## 核心功能

- **方案推荐**：根据企业类型、贸易类型、金额、账期智能推荐
- **多维度对比**：融资比例、利率参考、办理周期、所需材料、风控要点
- **企微推送**：支持生成企业微信卡片，一键推送客户

## 使用方式

### CLI 方式

```bash
python3 scripts/trade_cli.py generate "贸易融资 出口企业 金额100万美元 账期90天"
python3 scripts/trade_cli.py compare "L/C,国际保理,福费廷"
python3 scripts/trade_cli.py wecom "出口企业 金额50万美元 账期60天"
```

### Python API

```python
from trade_engine import TradeFinanceEngine

engine = TradeFinanceEngine()
result = engine.recommend(
    company_type="出口企业",
    trade_type="一般贸易",
    amount_usd=1_000_000,
    payment_terms_days=90
)
print(result)
```

## 输出字段

每个方案包含：
- **适用场景**：何时选择该产品
- **融资比例**：通常可融金额占应收账款的百分比
- **利率参考**：年化利率参考范围（基于2026年市场水平）
- **办理周期**：从申请到放款的预估时间
- **所需材料**：办理所需核心文件清单
- **风控要点**：银行/金融机构关注的核心风险点
