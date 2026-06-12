# 智能客服技能 (Smart Customer Service)

## 概述

智能客服技能基于规则+关键词匹配的混合引擎，实现银行场景下的意图识别、FAQ匹配、自动回答和转人工判断。

## 10类意图分类

| 意图ID | 意图名称 | 关键词示例 |
|--------|----------|------------|
| 1 | 开户咨询 | 开户、开设账户、怎么办卡、新户 |
| 2 | 贷款申请 | 贷款、借款、信贷、房贷、车贷 |
| 3 | 理财产品 | 理财、基金、收益、定期、理财产品的 |
| 4 | 信用卡 | 信用卡、卡片、额度、账单、还款 |
| 5 | 保险业务 | 保险、投保、理赔、险种 |
| 6 | 投诉建议 | 投诉、建议、反馈、不满、被盗刷 |
| 7 | 信息查询 | 查询、余额、明细、流水、利率 |
| 8 | 转人工 | 转人工、人工服务、人工客服 |
| 9 | 判断失误 | (由置信度<0.4触发) |
| 10 | 闲聊 | 你好、天气、吃饭、闲聊 |

## 核心能力

### 意图识别
- 基于关键词权重 + 模式匹配的混合识别
- 返回意图分类 + 置信度(0.0~1.0)
- 置信度<0.4时标记为「判断失误」

### FAQ匹配
- 内置50+条银行核心业务FAQ
- 支持相似问法扩展
- 返回匹配FAQ及答案

### 自动回答
- 直接给出标准答案
- 多轮对话上下文支持

### 转人工判断
满足以下任一条件时建议转人工：
- 涉及隐私信息（身份证号、银行卡密码、验证码）
- 复杂投诉（多次申诉、历史投诉、涉及金额较大）
- 情绪激动（强烈不满、威胁、辱骂）
- 多次判断失误（同一会话内>2次）

## 文件结构

```
smart_customer_service/
├── SKILL.md
├── __init__.py
├── cs_engine.py        # 核心引擎
├── scripts/
│   └── cs_cli.py       # CLI入口
└── wecom_integration.py # 企微卡片
```

## 使用方式

### Python API
```python
from smart_customer_service import SmartCustomerServiceEngine

engine = SmartCustomerServiceEngine()
result = engine.process("我想投诉 银行卡被盗刷了")
print(result)
```

### CLI
```bash
python3 scripts/cs_cli.py generate "智能客服 我想投诉 银行卡被盗刷了"
```

### 企微集成
```python
from smart_customer_service.wecom_integration import build_cs_card
card = build_cs_card(result)
```
