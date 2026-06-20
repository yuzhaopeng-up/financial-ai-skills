---
name: regulatory_reporting
description: "报送清单生成：输入报送类型+期间，输出完整报表清单及截止日期 - 指标口径说明：关键指标的定义、计算公式、填报说明 - 数据来源系统：各报表对应的源系统及取数逻辑 - 常见错误提示：历史高频错误及核查要点"
version: 1.0.0
author: ArkClaw
license: MIT
layer: L2
capability_domain: [C02, C03, C09]
industry: financial
metadata:
  raw_title: "监管报送技能 (Regulatory Reporting Skill)"
  auto_generated: true
  auto_generated_at: "2026-06-20"
---

# 监管报送技能 (Regulatory Reporting Skill)

金融监管报送全栈支持引擎，覆盖银保监、人民银行、金融稳定、EAST4.0等主流报送类型，输出报表清单、口径说明、数据来源及常见错误提示。

## 支持的报送类型

| 代码 | 报送类型 | 监管机构 |
|------|----------|----------|
| 1104 | 1104非现场监管统计报表 | 银保监会 |
| RPBC | 人民银行金融统计报送 | 人民银行 |
| GRS / GR-S | 金融稳定报表 | 人民银行/金融稳定局 |
| EAST | EAST4.0监管数据标准化报送 | 银保监会 |
| SPECIAL | 特殊监管报送（现场检查、临时统计等） | 银保监/人民银行 |
| WM | 理财登记系统报送（银行理财信息登记） | 银保监会 |

## 核心能力

- **报送清单生成**：输入报送类型+期间，输出完整报表清单及截止日期
- **指标口径说明**：关键指标的定义、计算公式、填报说明
- **数据来源系统**：各报表对应的源系统及取数逻辑
- **常见错误提示**：历史高频错误及核查要点

## 使用方式

### CLI
```bash
python3 scripts/regreport_cli.py generate "监管报送 1104 2024年Q1"
python3 scripts/regreport_cli.py generate "报送 GL18 2024年6月"
python3 scripts/regreport_cli.py list-types
```

### Python API
```python
from regulatory_reporting.reg_report_engine import RegReportingEngine

engine = RegReportingEngine()
result = engine.generate("1104", "2024Q1")
print(result)
```

### 企业微信
```python
from regulatory_reporting.wecom_integration import build_regreport_card

card = build_regreport_card(report_type="1104", period="2024Q1")
# 发送至企业微信
```

## 输出格式

```json
{
  "report_type": "1104",
  "period": "2024Q1",
  "deadline": "2024-04-30",
  "reports": [...],
  "key_indicators": [...],
  "data_sources": [...],
  "common_errors": [...]
}
```

## 文件结构

```
regulatory_reporting/
├── SKILL.md
├── reg_report_engine.py   # 核心引擎
├── __init__.py
├── scripts/
│   └── regreport_cli.py    # CLI入口
└── wecom_integration.py   # 企微卡片
```
