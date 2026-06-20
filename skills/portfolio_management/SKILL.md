---
name: portfolio_management
description: "本技能基于经典投资组合理论（Modern Portfolio Theory / MPT），为客户提供三种量化策略生成的资产配置方案。支持输入客户风险偏好、资产规模、投资期限和目标收益，返回马科维茨有效前沿推荐组合、风险平价组合和最大多样化组合，并附带持仓明细、预期收益、年化波动率和夏普比率。"
version: 1.0.0
author: ArkClaw
license: MIT
layer: L3
capability_domain: [C02, C03, C05]
industry: financial
metadata:
  raw_title: "Portfolio Management Skill（投资组合管理技能）"
  auto_generated: true
  auto_generated_at: "2026-06-20"
---

# Portfolio Management Skill（投资组合管理技能）

## 概述

本技能基于经典投资组合理论（Modern Portfolio Theory / MPT），为客户提供三种量化策略生成的资产配置方案。支持输入客户风险偏好、资产规模、投资期限和目标收益，返回马科维茨有效前沿推荐组合、风险平价组合和最大多样化组合，并附带持仓明细、预期收益、年化波动率和夏普比率。

## 核心策略

### 1. 马科维茨均值方差（Markowitz MVO）
- **原理**：「不要把鸡蛋放在同一个篮子里」——通过优化资产间的相关性，在给定风险下最大化收益
- **输出**：有效前沿曲线 + 最优夏普比率组合 + 最小方差组合
- **适用场景**：客户有明确收益目标，或希望获得理论最优风险收益交换

### 2. 风险平价（Risk Parity / Equal Risk Contribution）
- **原理**：每个资产对组合总风险的贡献相等
- **优势**：不依赖收益预测天然平衡波动，避免单一资产主导组合风险
- **适用场景**：市场不确定性高、追求稳健收益的客户

### 3. 最大多样化（Maximum Diversification）
- **原理**：最大化组合波动率与加权平均波动率之比（diversification ratio）
- **优势**：最大化分散化效益，降低组合特异性风险
- **适用场景**：希望最大化分散化、降低尾部风险的客户

## 内置资产库（20+可配置）

| 类别 | 资产 | 预期年化收益 | 年化波动率 |
|------|------|-------------|-----------|
| A股 | 沪深300ETF、中证500ETF、创业板ETF、消费ETF、医药ETF、红利低波ETF、家电ETF、新能源ETF、半导体ETF | 9%~14% | 18%~34% |
| 港股 | 恒生ETF、港股科技ETF | 9%~15% | 25%~35% |
| 美股 | 标普500ETF、纳斯达克ETF、中概互联ETF | 10%~14% | 18%~32% |
| 债券 | 国债ETF、企业债ETF、政金债ETF | 3.5%~5% | 4%~6% |
| 黄金/大宗 | 黄金ETF、豆粕ETF | 5%~6% | 15%~20% |
| REITs | 公募REITs | 7% | 12% |
| 现金 | 货币基金 | 1.8% | 0.3% |

## 输入参数

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| risk_preference | str | 风险偏好：保守型/稳健型/平衡型/进取型/激进型 | 平衡型 |
| asset_size | float | 资产规模（万元） | 500 |
| investment_horizon | int | 投资期限（年） | 3 |
| target_return | float, optional | 目标年化收益（%），如 8.0 | 8.0 |

## 输出结构

```json
{
  "metadata": {
    "risk_preference": "平衡型",
    "asset_size": 500,
    "investment_horizon_years": 3,
    "target_return_pct": 8.0,
    "assets_used": [...]
  },
  "markowitz_efficient": {
    "strategy": "马科维茨有效前沿（最优夏普）",
    "expected_return_annual": 9.8,
    "volatility_annual": 14.5,
    "sharpe_ratio": 0.676,
    "max_drawdown_estimate": -21.75,
    "holdings": [
      {
        "asset": "沪深300ETF",
        "weight": 25.0,
        "allocation": 125.0,
        "asset_type": "股票",
        "region": "A股"
      }
    ]
  },
  "markowitz_min_variance": {...},
  "risk_parity": {...},
  "max_diversification": {...},
  "summary": {
    "highest_sharpe": "markowitz_efficient",
    "lowest_volatility": "risk_parity",
    "highest_return": "max_diversification"
  }
}
```

## CLI 使用方式

```bash
# 标准用法
python3 scripts/portfolio_cli.py generate "组合管理 平衡型 资产500万 期限3年 目标收益8%"

# 仅生成组合
python3 scripts/portfolio_cli.py generate "平衡型 500 3 8"

# JSON 输出
python3 scripts/portfolio_cli.py generate "组合管理 平衡型 资产500万 期限3年 目标收益8%" --format=json
```

## 自然语言解析规则

输入格式灵活，支持以下任意组合：
- `组合管理 [风险偏好] 资产[规模] 期限[年限] 目标收益[百分比]`
- `[风险偏好] [规模]万 [年限]年 [目标]%`
- `balance [size] [horizon] [target]`

解析优先级：
1. 风险偏好：匹配 保守/稳健/平衡/进取/激进
2. 规模：数字 + 万/百万/元，缺省默认500万
3. 期限：数字 + 年，缺省默认3年
4. 目标收益：数字 + %，缺省自动计算

## 企微卡片集成

使用 `wecom_integration.py` 生成飞书/企微消息卡片格式，适配 `feishu_im_user_message` 或 `wecom_mcp` 工具发送。

## 注意事项

1. 本技能使用简化的预期收益和相关性估算，实际使用时建议结合宏观经济研究和市场环境调整
2. 最小再平衡阈值建议 5%，超过后触发再平衡操作
3. 最大单一资产权重限制 30%，防止过度集中
4. 过去业绩不代表未来表现，请结合客户风险承受能力综合判断
