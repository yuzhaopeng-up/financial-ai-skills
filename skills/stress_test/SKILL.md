---
name: stress_test
description: "本技能用于商业银行压力测试场景，基于银行资产负债数据（资产规模、负债结构、资本金），模拟不同宏观经济压力情景下的风险传导，输出各情景下的资本充足率、不良率、ROE、流动性缺口等关键指标。"
version: 1.0.0
author: ArkClaw
license: MIT
layer: L3
capability_domain: [C02, C03, C09]
industry: financial
metadata:
  raw_title: "银行压力测试技能 (Stress Test Skill)"
  auto_generated: true
  auto_generated_at: "2026-06-20"
---

# 银行压力测试技能 (Stress Test Skill)

## 概述

本技能用于商业银行压力测试场景，基于银行资产负债数据（资产规模、负债结构、资本金），模拟不同宏观经济压力情景下的风险传导，输出各情景下的资本充足率、不良率、ROE、流动性缺口等关键指标。

## 核心功能

### StressTestEngine 类

```python
from stress_engine import StressTestEngine

engine = StressTestEngine()
result = engine.run_stress_test(
    total_assets=1000_亿,      # 总资产规模
    capital=80_亿,              # 资本金
    npl_ratio=1.5,             # 不良率(%)
    liability_structure={...}   # 负债结构(可选)
)
```

## 压力情景定义

| 情景 | GDP增速变化 | 房地产价格变化 | 利率变化 | 股市变化 | 外部冲击 |
|------|------------|---------------|---------|---------|---------|
| 轻压 | -1% | -10% | +50bp | - | - |
| 中压 | -3% | -20% | +100bp | - | - |
| 重压 | -5% | -30% | +150bp | -20% | - |
| 极重压 | <-5% | <-30% | +200bp+ | -30%+ | 疫情/制裁 |

## 输出指标

### 1. 资本充足率 (CAR)
- 核心一级资本充足率
- 一级资本充足率
- 资本充足率

### 2. 不良率 (NPL Ratio)
- 压力情景下不良率预测
- 不良贷款额变化

### 3. 盈利能力
- ROE (净资产收益率)
- 净利润变化

### 4. 流动性缺口
- LCR (流动性覆盖率)
- NSFR (净稳定资金比例)
- 30天流动性缺口

## 风险传导路径

```
宏观经济冲击(GDP↓/房地产↓/利率↑)
    ↓
借款人偿债能力下降
    ↓
贷款违约率上升 → 不良率↑
    ↓
拨备覆盖率↓ → 净利润↓
    ↓
资本金被侵蚀 → 资本充足率↓
    ↓
流动性紧张 → 流动性缺口扩大
```

## 使用场景

- 监管报送（银保监会压力测试报告）
- 内部风险管理（季度/年度压力测试）
- 应急预案制定
- 资本规划与补充计划

## CLI 使用

```bash
python3 scripts/stress_cli.py generate "压力测试 资产1000亿 资本金80亿 不良率1.5%"
python3 scripts/stress_cli.py report --scenario=重压 --format=json
python3 scripts/stress_cli.py compare --baseline --stress
```

## 企微集成

支持通过企微机器人发送压力测试报告卡片：
```python
from wecom_integration import send_stress_test_card
send_stress_test_card(result, webhook_url)
```

## 依赖模型

-Ark API (doubao-seed-2.0-pro) 用于生成分析报告

## 版本

v1.0.0 (2026-06-10)
