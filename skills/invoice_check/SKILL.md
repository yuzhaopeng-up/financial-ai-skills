---
name: invoice_check
description: "发票查验技能用于对企业取得的增值税发票进行真伪鉴别、风险识别和税务合规性分析。支持查验发票类型包括：增值税专用发票、增值税普通发票（含卷式）、机动车销售统一发票、二手车销售统一发票。"
version: 1.0.0
author: ArkClaw
license: MIT
layer: L2
capability_domain: [C03, C04, C10]
industry: financial
metadata:
  raw_title: "invoice_check — 发票查验技能"
  auto_generated: true
  auto_generated_at: "2026-06-20"
---

# invoice_check — 发票查验技能

## 概述

发票查验技能用于对企业取得的增值税发票进行真伪鉴别、风险识别和税务合规性分析。支持查验发票类型包括：增值税专用发票、增值税普通发票（含卷式）、机动车销售统一发票、二手车销售统一发票。

## 查验规则

### 发票状态判定
| 状态 | 说明 |
|------|------|
| 真票 | 发票代码、号码匹配国家税务局增值税发票查验平台数据，且票面信息一致 |
| 假票 | 发票代码/号码在税务局系统无法查到 |
| 失控发票 | 发票已报税但未按时申报，或被主管税务机关列为失控 |
| 作废发票 | 开票方在系统内作废该发票 |
| 红字发票 | 发票为冲红发票，需核实原票信息 |
| 超过认证期限 | 增值税专用发票超过360天（2020年后）/ 90天（2020年前）认证期限 |

### 异常检测规则
- **金额不符**：票面金额与系统记录不一致
- **税率异常**：适用税率与业务类型不匹配（如一般纳税人开具13%以下税率需核实）
- **敏感交易对手**：与客户单位存在以下关联：法人相同 / 注册地址相近 / 短期内大量交易
- **重复报销**：同一发票代码+号码在历史记录中已出现
- **品名异常**：货物或服务品名与业务实质不符

## 核心功能

### 1. InvoiceCheckEngine
**类**：`InvoiceCheckEngine`

**输入参数**：
```python
{
    "invoice_code": "发票代码（144031900360）",
    "invoice_number": "发票号码（44450123）",
    "billing_date": "开票日期（YYYY-MM-DD）",
    "amount": "金额（含税，单位元或万元）",
    "buyer_name": "购买方名称",
    "seller_name": "销售方名称",
    "buyer_tax_id": "购买方税号",
    "seller_tax_id": "销售方税号"
}
```

**输出结果**：
```python
{
    "invoice_code": str,           # 发票代码
    "invoice_number": str,          # 发票号码
    "status": str,                 # 真票/假票/失控发票/作废发票/红字发票/超过认证期限
    "confidence": float,           # 可信度 0.0~1.0
    "anomalies": [                 # 异常提示列表
        {
            "type": str,           # 异常类型
            "severity": str,      # high/medium/low
            "description": str,   # 描述
            "suggestion": str     # 建议
        }
    ],
    "vat_deduction": {             # 增值税抵扣建议
        "can_deduct": bool,        # 是否可抵扣
        "deduction_type": str,    # 进项抵扣类型
        "reason": str             # 原因
    },
    "tax_risk_points": [           # 税务风险点
        {
            "point": str,
            "risk_level": str     # high/medium/low
        }
    ],
    "reference_records": [          # 备查记录
        {
            "record_type": str,
            "content": str,
            "timestamp": str
        }
    ]
}
```

### 2. CLI 入口
```bash
python3 scripts/invoice_cli.py "发票查验 发票代码144031900360 号码44450123 开票日期2024-03-01 金额10万"
python3 scripts/invoice_cli.py generate "发票查验 发票代码144031900360 号码44450123 开票日期2024-03-01 金额10万"
```

### 3. 企微卡片集成
通过 `wecom_integration.py` 生成企业微信卡片消息格式，支持直接推送至企微群或企微机器人。

## 技术架构

```
invoice_check/
├── SKILL.md                  # 本文档
├── invoice_engine.py         # 核心引擎 InvoiceCheckEngine
├── __init__.py               # 导出
├── scripts/
│   └── invoice_cli.py        # CLI 入口
└── wecom_integration.py      # 企微卡片集成
```

## 使用场景

- 财务报销审核
- 供应商准入尽调
- 税务自查
- 审计抽查

## 注意事项

- 本技能为辅助工具，查验结果仅供参照，最终以主管税务机关认定为准
- 敏感交易对手分析需结合工商数据综合判断
- 本地查验规则库需定期更新以反映最新政策
