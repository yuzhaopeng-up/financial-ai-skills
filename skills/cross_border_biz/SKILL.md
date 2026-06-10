# 跨境业务技能 (cross_border_biz)

## 概述

跨境业务综合解决方案引擎，支持进出口结算、外汇避险、跨境人民币、ODI备案及特殊贸易区政策咨询。

## 输入参数

| 参数 | 类型 | 说明 |
|------|------|------|
| business_type | str | 企业类型：出口/进口/跨境投融资 |
| amount | float | 交易金额 |
| currency | str | 币种，如 USD/EUR/CNY |
| destination_country | str | 目的国/地区 |

## 支持场景

### 进出口结算
- **TT电汇** - 适用于常规结算，速度快，费用低
- **LC信用证** - 银行信用介入，适合大额交易，风险可控
- **DP付款交单** - 进口商付款后才能取得单据，安全性高
- **DA承兑交单** - 进口商承兑后取得单据，账期灵活
- **OA赊账** - 适用于长期合作客户，信用管理要求高

### 外汇避险
- **远期外汇合约(Forward)** - 锁定未来汇率，规避波动风险
- **外汇掉期(Swap)** - 锁定近端汇率，适用于资金调拨
- **外汇期权(Option)** - 保留汇率向有利方向变动的收益

### 跨境人民币(Cross-border RMB)
- 跨境人民币结算优势与合规要点
- 境外直接投资人民币结算
- 跨境双向人民币资金池

### ODI备案
- 境外直接投资外汇登记
- 敏感行业/地区投资审批
- 37号文特殊目的公司登记

### 特殊贸易区政策
- 海南自贸港政策红利
- 横琴/前海合作区
- 跨境电商综合试验区
- 综合保税区政策

## 输出结构

```json
{
  "business_type": "出口",
  "amount": "100万美元",
  "currency": "USD",
  "destination_country": "欧盟",
  "recommended_settlement": {
    "method": "LC信用证",
    "bank_recommendation": "建议采用不可撤销跟单信用证",
    "flow": ["出口商发货→提交单据→开证行审单→付款"]
  },
  "fx_hedging": {
    "recommended": "远期外汇合约",
    "structure": "锁6个月远期USD/EUR，规避欧元贬值风险",
    "estimated_cost": "0.5%-1%期权费"
  },
  "compliance": {
    "required_registrations": ["货物贸易外汇管理登记", "出口退税备案"],
    "restricted_licenses": ["若涉及出口管制商品需申请出口许可证"]
  },
  "crossborder_rmb": {
    "eligibility": "符合跨境人民币结算条件",
    "benefits": ["降低汇兑成本","规避汇率风险","提升资金效率"]
  }
}
```

## 使用方式

```bash
# CLI使用
python3 scripts/cb_cli.py generate "跨境业务 出口企业 100万美元 欧盟"

# Python调用
from crossborder_engine import CrossBorderEngine
engine = CrossBorderEngine()
result = engine.generate("出口", 1000000, "USD", "欧盟")
```

## 版本
- v1.0.0 (2026-06-10)
