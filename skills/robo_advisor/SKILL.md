---
name: robo_advisor
description: "智能投顾增强技能：基于现代投资组合理论（MPT）和 Black-Litterman 模型框架，为用户提供个性化资产配置方案、投资组合建议及再平衡计划。支持风险偏好解析、资产规模评估、投资目标识别，合规提示全链路覆盖。"
version: 1.0.0
author: ArkClaw
license: MIT
layer: L2
capability_domain: [C02, C03, C05]
industry: financial
metadata:
  raw_title: "Robo Advisor Skill - 智能投顾引擎"
  auto_generated: true
  auto_generated_at: "2026-06-20"
---

# Robo Advisor Skill - 智能投顾引擎

## Description

**智能投顾增强技能**：基于现代投资组合理论（MPT）和 Black-Litterman 模型框架，为用户提供个性化资产配置方案、投资组合建议及再平衡计划。支持风险偏好解析、资产规模评估、投资目标识别，合规提示全链路覆盖。

## 核心能力

### 1. 风险测评问卷解析
- 解析自然语言风险偏好（稳健型、平衡型、进取型、保守型）
- 支持多维度风险因子提取（风险承受能力、投资期限、流动性需求）
- 输出结构化风险评分（0-100）

### 2. 资产配置生成
- 基于风险评分的战略资产配置（SAA）
- 资产类别：股票（A股/港股/美股）、债券（利率债/信用债）、另类资产（黄金/原油/REITs）、现金及等价物
- Black-Litterman 模型框架：融合市场均衡收益与投资者观点

### 3. 投资组合优化
- 均值-方差优化（Mean-Variance Optimization）
- 风险平价（Risk Parity）配置
- 最大夏普比率组合构建
- 因子暴露分析

### 4. 再平衡策略
- 阈值触发再平衡（drift > 5%）
- 日历再平衡（季度/半年/年）
- 成本感知再平衡优化

### 5. 合规提示
- 适当性管理提示
- 产品风险等级匹配
- 非保本理财警示
- 法规引用（资管新规、基金投顾指引等）

## 输入输出格式

### CLI 调用
```bash
python3 scripts/robo_advisor_cli.py generate "智能投顾 稳健型 资产100万 养老规划"
python3 scripts/robo_advisor_cli.py questionnaire "年龄30 收入50万 投资经验5年 亏损承受20%"
python3 scripts/robo_advisor_cli.py rebalance "当前配置股票30%债券50%现金20% 市值100万"
```

### 输出 JSON Schema
```json
{
  "session_id": "uuid",
  "timestamp": "ISO8601",
  "risk_profile": {
    "risk_type": "string",
    "risk_score": 0-100,
    "investment_horizon": "string",
    "liquidity_need": "string"
  },
  "asset_allocation": {
    "strategic": {"stocks": "%", "bonds": "%", "alternatives": "%", "cash": "%"},
    "tactical": {"stocks": "%", "bonds": "%", "alternatives": "%", "cash": "%"},
    "region_allocation": {"china": "%", "hk": "%", "us": "%", "other": "%"}
  },
  "portfolio": {
    "positions": [{"asset": "", "target_pct": "", "rationale": ""}],
    "expected_return": "%",
    "expected_volatility": "%",
    "sharpe_ratio": 0.0,
    "var_95": "%",
    "max_drawdown_est": "%"
  },
  "rebalancing": {
    "strategy": "string",
    "threshold": "%",
    "next_rebalance_date": "ISO8601",
    "drift_alerts": [{"asset": "", "current_pct": "", "target_pct": "", "drift": ""}]
  },
  "compliance": {
    "appropriateness": "string",
    "risk_disclosure": ["string"],
    "regulatory_references": ["string"]
  }
}
```

## 架构
- `robo_advisor_engine.py`: 核心引擎，RoboAdvisorEngine 类
- `scripts/robo_advisor_cli.py`: 命令行入口
- `wecom_integration.py`: 企业微信卡片输出
