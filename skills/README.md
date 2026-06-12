# Financial AI Skills

开源金融AI技能库，覆盖银行、证券、基金、保险四大行业。

## 技能列表（17个）

### 报告生成（7个）
| 技能 | 说明 | 状态 |
|------|------|------|
| meeting_minutes | 调研纪要生成 | ✅ |
| market_view | 市场观点输出 | ✅ |
| roadshow_material | 路演材料生成 | ✅ |
| fund_research | 基金研究报告 | ✅ |
| ops_daily_report | 运营日报 | ✅ |
| family_trust | 家族信托方案 | ✅ |
| global_asset_allocation | 全球资产配置 | ✅ |

### 核心业务（10个）
| 技能 | 说明 | 状态 |
|------|------|------|
| financial-intelligence | 财务AI智能体 | ✅ |
| risk-compliance | 风控合规 | ✅ |
| wealth-management | 财富管理 | ✅ |
| customer-persona | 客户画像 | ✅ |
| customer-marketing | 营销话术 | ✅ |
| research-report | 研报生成 | ✅ |
| product-manual-rag | 产品手册问答 | ✅ |
| application-material-checker | 进件材料核对 | ✅ |
| regulatory-policy-rag | 监管政策查询 | ✅ |
| wecom-template-card | 企微卡片模板 | ✅ |

## 使用方式

```python
from meeting_minutes import MeetingMinutesEngine

eng = MeetingMinutesEngine()
result = eng.generate("调研纪要 某新能源公司储能业务")
print(result.to_markdown())
```

## 架构设计

所有技能遵循统一架构：

```
Skill/
├── SKILL.md              # 技能文档
├── __init__.py           # 模块导出
├── *_engine.py           # 核心引擎
├── scripts/              # CLI工具
└── wecom_integration.py  # 企微集成（可选）
```

## 开源协议

MIT License

## 贡献指南

欢迎提交PR，新增金融AI场景。
