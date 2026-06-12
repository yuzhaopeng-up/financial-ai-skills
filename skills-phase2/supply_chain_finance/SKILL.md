# SKILL.md — 供应链金融技能（Supply Chain Finance）

## 技能概述

**技能名称**：supply_chain_finance
**技能路径**：`/tmp/financial-ai-skills/skills/supply_chain_finance/`
**版本**：v1.0.0
**适用场景**：核心企业供应链金融方案咨询、供应商融资方案推荐

---

## 功能说明

根据核心企业名称、供应商类型、应付账款规模和账期，自动生成五种供应链金融解决方案：

| 序号 | 方案 | 英文名 | 核心特点 |
|------|------|--------|----------|
| 1 | 应收账款质押融资 | Receivables Pledge | 供应商质押应收账款，提前回款 |
| 2 | 订单融资 | Order Financing | 凭采购订单预支生产资金 |
| 3 | 核心企业反向保理 | Reverse Factoring | 核心企业确权，信用直达供应商 |
| 4 | 供应链票据 | Supply Chain Bill | 电子商票多级流转，信用穿透全链 |
| 5 | 仓单融资 | Warehouse Receipt | 仓单质押，实物资产融资 |

---

## 输入参数

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `core_enterprise` | string | ✅ | 核心企业名称 | "某新能源汽车企业"、"汽车整车厂" |
| `supplier_type` | string | ✅ | 供应商类型/行业 | "汽车零部件"、"电子元器件" |
| `accounts_payable` | float | ✅ | 应付账款规模（**万元**） | 100000 (= 10亿元) |
| `payment_term_days` | int | ✅ | 账期（天） | 90 |
| `industry` | string | ❌ | 行业，默认自动推断 | "汽车" |

---

## 输出内容

1. **五大解决方案详情**：额度范围、利率参考、办理周期、所需材料、核心企业配合要点、优势与风险
2. **方案对比表**：额度/利率/周期/配合度/风险/适用规模六维度对比
3. **办理流程**：7步标准流程 + 各方案周期差异说明
4. **综合建议**：推荐方案组合 + 行动建议

---

## 使用方式

### Python API

```python
from supply_chain_finance import SCFEngine, SCFProfile, parse_input

# 方式1：直接构造 Profile
profile = SCFProfile(
    core_enterprise="某新能源汽车企业",
    supplier_type="汽车零部件",
    accounts_payable=100000,      # 10亿元 → 100000万元
    payment_term_days=90,
)
engine = SCFEngine()
result = engine.generate(profile)

# 输出 Markdown
print(engine.format_markdown(result))

# 输出 JSON
print(engine.format_json(result))

# 输出企微卡片
print(engine.format_wecom_card(result))

# 方式2：从自然语言解析
profile = parse_input("供应链金融 汽车整车厂 应付账款10亿 账期90天")
result = SCFEngine().generate(profile)
```

### CLI

```bash
# 自然语言生成（默认 Markdown 输出）
python3 scripts/scf_cli.py generate "供应链金融 汽车整车厂 应付账款10亿"

# JSON 格式输出
python3 scripts/scf_cli.py generate "供应链金融 汽车整车厂 应付账款10亿" --format json

# 帮助
python3 scripts/scf_cli.py --help
```

---

## 文件结构

```
supply_chain_finance/
├── SKILL.md              ← 本文档
├── scf_engine.py         ← 核心引擎（SCFEngine + parse_input）
├── __init__.py           ← 包导出
├── scripts/
│   └── scf_cli.py        ← CLI 入口
└── wecom_integration.py  ← 企微卡片集成
```

---

## 企微集成

```python
from supply_chain_finance import SCFEngine, parse_input

profile = parse_input("供应链金融 汽车整车厂 应付账款10亿")
result = SCFEngine().generate(profile)
card = engine.format_wecom_card(result)
# → 传入企微 webhook 或消息接口
```

---

## 注意事项

- `accounts_payable` 单位为**万元**，注意换算（10亿 = 100000 万元）
- 利率为参考范围，实际利率由金融机构根据核心企业评级定价
- 核心企业反向保理需要核心企业主动确权，配合度是关键因素
- 仓单融资需要有合格仓储资质合作方

---

## 维护记录

- v1.0.0（2026-06-10）：初始版本，支持五种 SCF 模式
