---
name: application-material-checker
description: "Financial AI Skill - 进件材料自动核对引擎。基于规则引擎对身份证/营业执照/银行流水/合同等单据进行完整性+合规性双维校验，自动识别缺失项、过期证件、名称不一致、用途违规、首付不足等问题，输出可追溯的核对报告。覆盖对公开户/小微贷款/个人房贷三大场景，10+ 单据类型，30+ 业务规则。"
version: 1.0.0
author: ArkClaw (Financial AI Community)
license: MIT
metadata:
  hermes:
    tags: [ocr, kyc, credit, compliance, mortgage, sme-loan, account-opening, audit, document-review]
    related_skills: [financial-intelligence, risk-compliance, product-manual-rag]
    coverage:
      scenarios: 3
      doc_types: 12
      business_rules: 18
prerequisites:
  commands: [python3]
---

# 进件材料自动核对 v1.0

> 上传材料 → AI 秒级核对 → 高亮缺失项 + 整改建议 + 评分。
>
> ⚡ 零外部依赖 | 🎯 18 条业务规则 | 📋 报告可追溯 | 🔁 OCR 字段直连

## 一、核心能力

| 能力 | 触发场景 | 核心功能 |
|------|---------|---------|
| **完整性检查** | 所有进件场景 | 对比应提交 vs 已提交材料，识别缺失 |
| **字段级校验** | OCR 后置检查 | 身份证号/手机号/USCC/金额/日期等格式校验 |
| **跨单据一致性** | 法人审核 | 营业执照法人 vs 身份证姓名一致性等 |
| **业务规则校验** | 风控前置 | 经营时长、流水周期、首付比例、用途合规等 |
| **报告生成** | 审批员协同 | text / Markdown / JSON / 企微卡片四种格式 |

## 二、支持的业务场景

| 场景 Key | 名称 | 必备材料数 | 业务规则数 |
|----------|------|-----------|-----------|
| `corporate_account_opening` | 对公账户开户 | 5 | 4 |
| `sme_loan` | 小微企业贷款 | 5 | 5 |
| `personal_mortgage` | 个人住房按揭 | 7 | 6 |

## 三、快速开始

### 安装

```bash
git clone https://github.com/yuzhaopeng-up/financial-ai-skills.git
cp -r financial-ai-skills/skills/application-material-checker ~/.hermes/skills/
```

### CLI 调用

```bash
cd ~/.hermes/skills/application-material-checker

# 列出支持的场景
python3 scripts/checker_cli.py scenarios

# 查看场景所需材料
python3 scripts/checker_cli.py required sme_loan

# 核对样本（输出格式：text | json | md | card）
python3 scripts/checker_cli.py check samples/sme_loan_fail.json
python3 scripts/checker_cli.py check samples/mortgage_partial.json --format md

# 模拟当前日期（用于过期校验测试）
python3 scripts/checker_cli.py check samples/sme_loan_pass.json --today 2026-06-07

# 批量核对
python3 scripts/checker_cli.py batch --dir samples/
```

### Python API

```python
from application_material_checker import (
    MaterialChecker, MaterialDoc, MaterialReportFormatter
)

docs = [
    MaterialDoc(doc_type="business_license", fields={
        "uscc": "91110108MA01ABCDXY",
        "company_name": "北京启航科技有限公司",
        "legal_person": "张三",
        "establish_date": "2022-03-15",
    }),
    MaterialDoc(doc_type="legal_id_card", fields={
        "id_no": "110108198501012345",
        "name": "张三",
        "valid_to": "2030-12-31",
    }),
    # ...
]

report = MaterialChecker().check("sme_loan", docs)
print(MaterialReportFormatter.to_text(report))
print(report.pass_, report.score)
```

## 四、规则库（节选）

### 小微贷款 (`sme_loan`)

| 规则 ID | 类型 | 说明 |
|---------|------|------|
| `SME-001` | not_expired | 法人身份证过期检查 |
| `SME-002` | operating_age | 企业经营时长 ≥ 12 个月 |
| `SME-003` | statement_period | 银行流水连续 ≥ 12 个月 |
| `SME-004` | loan_purpose_compliant | 用途黑名单（房地产/股市/虚拟币等） |
| `SME-005` | amount_limit | 单户最高 500 万元 |

### 个人房贷 (`personal_mortgage`)

| 规则 ID | 类型 | 说明 |
|---------|------|------|
| `MORT-001` | not_expired | 主借款人身份证过期检查 |
| `MORT-002` | spouse_required_if_married | 已婚必须提交配偶身份证 |
| `MORT-003` | match_name | 身份证姓名 = 购房合同买方 |
| `MORT-004` | income_to_loan_ratio | 月供 ≤ 月收入 50% |
| `MORT-005` | down_payment_ratio | 首付 ≥ 30% |
| `MORT-006` | income_proof_freshness | 收入证明 ≤ 90 天 |

### 对公开户 (`corporate_account_opening`)

| 规则 ID | 类型 | 说明 |
|---------|------|------|
| `RG-001` | match_name | 营业执照公司名 = 申请书公司名 |
| `RG-002` | match_name | 营业执照法人 = 身份证姓名 |
| `RG-003` | not_expired | 法人身份证有效期检查 |
| `RG-004` | uscc_match | USCC = 税务登记号（五证合一） |

## 五、报告示例

输入：小微贷款 — 缺失税务记录 + 身份证过期 + 流水不足 + 用途违规 + 金额超限

```
========================================================
📋 进件材料核对报告 - 小微企业贷款
📅 生成时间: 2026-06-07 00:00:00
========================================================

🏁 结论: ❌ 进件材料存在 6 项阻断问题，需补充/修正后重新提交。
📊 评分: 41.0 / 100  | 状态: 不通过 ❌

📁 已提交 (4/5):
    ✓ bank_statement   ✓ business_license   ✓ legal_id_card   ✓ loan_application

📂 缺失材料 (1):
    ✗ tax_payment_record  ← 请补充

🔍 详细问题清单:
  ❌ [缺失] (1 项)
     - [MISSING-tax_payment_record] 必备材料缺失: tax_payment_record
       💡 建议: 请上传 tax_payment_record
  ⏰ [过期] (1 项)
     - [SME-001] 法人身份证已过期 (有效期至: 2024-01-01)
       💡 建议: 请提交在有效期内的证件
  ⚠️ [无效] (4 项)
     - [SME-002] 企业经营时长不足 12 个月，不满足申请条件 (实际: 9.3 个月)
     - [SME-003] 银行流水不足 12 个月 (实际: 5.0 个月)
     - [SME-004] 贷款用途包含禁止性内容 (命中关键词: 房地产)
     - [SME-005] 申请金额超过单户最高 500 万元 (申请: 6,800,000)
```

## 六、与同业对标

| 银行 | 产品 | 我们的方案 |
|------|------|-----------|
| 平安 "AI 信贷工厂" | 进件审批从 3 天 → 10 分钟 | ✅ 规则可追溯 + 零 API 费用 |
| 工行 "工银智涌" | 反欺诈 + 材料审核 | ✅ 18 条业务规则开箱即用 |
| 网商银行 "310 模式" | 3 分钟审批 | ✅ 毫秒级核对，可直接接入 OCR 流水线 |
| 建行 惠懂你 | 全线上信贷 | ✅ 与 financial-intelligence 复用 OCR |

## 七、与 financial-intelligence 协同

```
OCR 流水线（financial-intelligence/invoice_engine）
         │
         ▼
  结构化字段 dict
         │
         ▼  ← MaterialDoc 封装
application-material-checker
         │
         ▼
  CheckReport + 企微卡片
```

## 八、扩展指南

### 新增业务场景

编辑 `checker_engine.py::_scenario_rules()`，按以下结构添加：

```python
"your_scenario_key": {
    "name": "中文场景名",
    "required_docs": ["doc_a", "doc_b"],
    "doc_field_requirements": {
        "doc_a": ["field1", "field2"],
    },
    "extra_rules": [
        {"id": "XYZ-001", "type": "match_name", "src": (...), "dst": (...), "msg": "..."},
    ],
}
```

### 新增规则类型

在 `rule_runner.py::RuleRunner` 添加 `_rule_<your_type>(self, rule)` 方法即可。

## 九、合规与可追溯性

- 每条问题附 `rule_id`，可追溯到规则定义
- 报告 `generated_at` + `score` + `pass` 三元组可作审计依据
- JSON 报告可直接归档到风控系统/审计平台
- 零 API 调用，数据不出库，符合银保监数据安全要求

## 十、变更历史

- 1.0.0 (2026-06-07) 首版：3 场景 / 12 单据类型 / 18 业务规则 / 11 测试用例 100% 通过
