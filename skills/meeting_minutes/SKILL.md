---
name: meeting-minutes
description: "Financial AI Skill - 调研纪要生成器。输入调研录音文字/会议记录，自动输出结构化纪要（参会人+核心议题+关键要点+待办事项+风险提示）。支持证券公司/基金/银行研究员调研场景，零外部依赖。"
version: 1.0.0
author: ArkClaw
license: MIT
metadata:
  hermes:
    tags: [meeting, minutes, research,调研,纪要]
    related_skills: [research-report, market-view]
prerequisites:
  commands: [python3]
---

# 调研纪要生成器 v1.0

> 输入调研记录文字 → 秒级输出结构化纪要（参会人+议题+要点+待办+风险）

## 一、核心能力

| 能力 | 说明 |
|------|------|
| 自然语言解析 | 自动识别参会人、公司、时间、核心议题 |
| 结构化提取 | 嘉宾观点/数据/承诺/争议自动归类 |
| 要点提炼 | 核心结论3条内，关键数据标注来源 |
| 待办跟踪 | 纪要中隐含的承诺/跟进事项自动提取 |
| 风险提示 | 夸大陈述/数据不一致/合规风险自动识别 |

## 二、输入格式

```
纪要生成 今天上午调研宁德时代关于储能业务的情况
纪要 招商银行零售业务交流会 老张/老李参会
```

## 三、输出格式

text / json / markdown / wecom_card
