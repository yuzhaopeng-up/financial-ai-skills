---
name: renewal_alert
description: "renewal_alert 技能用于分析客户保单的续保情况，提供续保建议、客户挽留策略及话术支持。"
version: 1.0.0
author: ArkClaw
license: MIT
layer: L2
capability_domain: [C02, C03, C05]
industry: financial
metadata:
  raw_title: "续保提醒技能 (Renewal Alert)"
  auto_generated: true
  auto_generated_at: "2026-06-20"
---

# 续保提醒技能 (Renewal Alert)

## 概述
`renewal_alert` 技能用于分析客户保单的续保情况，提供续保建议、客户挽留策略及话术支持。

## 核心判断规则

### 续保判断规则
| 条件 | 建议 |
|------|------|
| 已缴年限 ≥ 保障期限 × 50% | **建议续保**（已有较高累计价值） |
| 现金价值 > 已缴保费 × 80% | **建议升级**（退保需谨慎） |
| 其他情况 | **建议退保** |

### 挽留优先级（从高到低）
1. 年金险（养老/教育金）
2. 终身寿险
3. 定期寿险
4. 医疗险
5. 意外险

## 引擎输入参数

```python
{
    "customer_name": str,      # 客户姓名
    "product_type": str,       # 险种：终身寿险/年金险/定期寿险/医疗险/意外险
    "annual_premium": float,   # 年缴保费（元）
    "paid_years": int,         # 已缴年限
    "coverage_years": int,     # 保障期限（年，0表示终身）
    "renewal_premium": float,  # 续期保费（元）
    "cash_value": float = None # 现金价值（可选）
}
```

## 引擎输出参数

```python
{
    "customer_name": str,           # 客户姓名
    "product_type": str,            # 险种
    "recommendation": str,           # 建议：建议续保 / 建议升级 / 建议退保
    "priority": str,                # 优先级：紧急 / 重要 / 一般
    "alternative": str = None,      # 替代方案（退保时提供）
    "retention_strategy": str,       # 客户挽留策略
    "renewal_script": str,          # 续保话术
    "analysis": {                    # 分析依据
        "paid_ratio": float,         # 已缴/保障期限比例
        "cash_value_ratio": float,   # 现金价值/已缴保费比例
        "risk_level": str            # 风险等级
    }
}
```

## 目录结构

```
renewal_alert/
├── SKILL.md
├── renewal_engine.py      # RenewalAlertEngine 核心类
├── __init__.py
├── scripts/
│   └── renewal_cli.py     # CLI 入口
└── wecom_integration.py   # 企微卡片推送
```

## CLI 用法

```bash
# 生成续保提醒
python3 scripts/renewal_cli.py generate "续保提醒 客户张总 终身寿险 年缴2万 已缴10年 续期将至"

# 企微推送
python3 scripts/renewal_cli.py wecom "客户张总 终身寿险 紧急"

# 帮助
python3 scripts/renewal_cli.py --help
```

## 依赖

- Python 3.8+
- 无外部依赖（纯计算引擎）
