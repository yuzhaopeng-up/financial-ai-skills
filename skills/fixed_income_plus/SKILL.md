---
name: fixed_income_plus
description: "固收+策略技能，专注于债券组合的收益分解、久期管理、信用风险管理、类属配置优化，以及与纯债组合的对比分析。"
version: 1.0.0
author: ArkClaw
license: MIT
layer: L3
capability_domain: [C02, C03, C05]
industry: financial
metadata:
  raw_title: "Fixed Income Plus (固收+) Skill"
  auto_generated: true
  auto_generated_at: "2026-06-20"
---

# Fixed Income Plus (固收+) Skill

## 概述

固收+策略技能，专注于债券组合的收益分解、久期管理、信用风险管理、类属配置优化，以及与纯债组合的对比分析。

## 核心功能

### 1. 收益分解（Return Decomposition）

| 收益来源 | 说明 |
|---------|------|
| 票息收入 (Carry) | 债券利息收入，按日计提 |
| 资本利得 (Capital Gain) | 债券价格波动产生的收益/损失 |
| 可转债期权价值 | 嵌入式期权的隐含价值 |
| ABS分层收益 | 优先档/劣后档的收益分配差异 |

### 2. 久期管理策略（Duration Management）

| 策略 | 特点 | 适用场景 |
|-----|------|---------|
| 子弹策略 (Bullet) | 集中配置于某一期限 | 预期利率下行 |
| 阶梯策略 (Ladder) | 均匀分布于各期限 | 稳健收益 |
| 哑铃策略 (Dumbbell) | 两端期限配置 | 兼顾收益与流动性 |

### 3. 信用风险管理（Credit Risk）

- **久期×信用利差敏感性**：DVCS = Duration × Credit Spread Change
- **违约概率估算**：基于评级转移矩阵和历史违约率
- **信用利差阈值监控**：预警利差急剧扩大

### 4. 类属配置优化（Asset Allocation）

```
最优配置比例 = f(目标收益, 风险预算, 流动性要求)
```

类属资产：
- 利率债（国债、政策性金融债）
- 信用债（高等级/中等级/低等级）
- 可转债
- ABS（优先级/劣后级）
- 二级资本债

### 5. VS纯债对比分析

| 对比维度 | 固收+ | 纯债 |
|---------|------|------|
| 收益目标 | 4%-6% | 2%-4% |
| 回撤控制 | <3% | <1% |
| 波动率 | 中等 | 低 |
| 信用下沉 | 适度 | 严控 |

## 使用方式

```bash
# CLI 入口
python3 scripts/fi_plus_cli.py generate "固收加分析 债券组合1亿 久期3.5 信用AA 目标收益4.5%"
```

## 输出格式

- 文本报告
- JSON 数据
- 企微卡片（wecom_integration.py）

## 技术栈

- Python 3.8+
- pandas / numpy
- scipy (优化)
