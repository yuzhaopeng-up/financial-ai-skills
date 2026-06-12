# 企业对公开户技能（corp_account_opening）

## 技能定位

为企业客户提供对公开户全流程智能指引，输入企业基本信息，返回开户所需材料清单、办理流程、注意事项及常见问题。

## 核心能力

- **企业类型识别**：支持有限责任公司、股份有限公司、合伙企业、外资企业、个体工商户
- **材料清单生成**：根据企业类型、注册资本、经营范围定制所需材料
- **基本户/一般户区分**：明确两类账户的区别及选择建议
- **流程步骤说明**：开户全流程7步指引
- **时长/费用说明**：办理时长、收费标准、后续注意事项
- **常见问题解答**：FAQ 覆盖90%常见疑问

## 输出格式

技能输出结构化 JSON，包含以下字段：

```json
{
  "enterprise_type": "有限责任公司",
  "account_type": "基本户",
  "materials": [...],
  "process": [...],
  "duration": "...",
  "fees": "...",
  "notes": [...],
  "faq": [...]
}
```

## 支持的查询方式

- CLI：`python3 scripts/account_cli.py generate "对公开户 科技公司 注册资本500万"`
- 模块调用：`from corp_account_opening import CorpAccountEngine; engine = CorpAccountEngine()`
- 企微卡片：调用 `wecom_integration.py` 生成卡片消息

## 企业类型支持

| 类型 | 代码 | 特点 |
|------|------|------|
| 有限责任公司 | LTD | 最常见，股东以出资额为限 |
| 股份有限公司 | CORP | 股份可转让，股东以股份为限 |
| 合伙企业 | PARTNERSHIP | 含普通/有限合伙，税收透明 |
| 外资企业 | FOREIGN | 需商务部门审批，材料最多 |
| 个体工商户 | SOLE_PROP | 流程简化，材料最少 |

## 基本户 vs 一般户

| 项目 | 基本存款账户 | 一般存款账户 |
|------|------------|------------|
| 数量 | 每个企业只能开1个 | 可开多个 |
| 功能 | 日常转账结算、工资发放 | 借款、资金归集 |
| 开户要求 | 须先开基本户 | 须已有基本户 |
| 人行备案 | 需要 | 需要 |

## 文件结构

```
corp_account_opening/
├── SKILL.md
├── account_engine.py   # 核心引擎 CorpAccountEngine
├── __init__.py
├── scripts/
│   └── account_cli.py  # CLI 入口
└── wecom_integration.py # 企微卡片
```

## 版本

- v1.0.0（2026-06-10）：初始版本
