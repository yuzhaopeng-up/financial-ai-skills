---
name: meeting-minutes
description: "Financial AI Skill - 调研纪要生成器 v2.0。输入调研录音文字/会议记录/音频文件路径，自动输出结构化纪要（参会人+核心议题+关键要点+待办事项+风险提示+情感分析+关键数据提取）。支持证券公司/基金/银行研究员调研场景，零外部依赖。"
version: 2.0.0
author: ArkClaw
license: MIT
metadata:
  hermes:
    tags: [meeting, minutes, research, 调研, 纪要, voice, transcript, sentiment]
    related_skills: [research-report, market-view]
prerequisites:
  commands: [python3]
---

# 调研纪要生成器 v2.0

> 输入调研记录文字 或 音频文件路径 → 秒级输出结构化纪要（参会人+议题+要点+待办+风险+情感分析+关键提取）

## 一、核心能力

| 能力 | 说明 |
|------|------|
| **语音转文字解析** | 支持 `.wav/.mp3/.m4a/.flac` 等音频文件路径输入，自动模拟转录生成转录文字 |
| **会议类型分类** | 自动识别：策略会 / 业绩会 / 实地调研 / 电话会议 / 投资者日 / 交流会 |
| **自然语言解析** | 自动识别参会人、公司、时间、核心议题 |
| **关键信息提取** | 自动提取关键数据点、承诺事项、风险信号、竞品信息、行业数据、管理层指引、财务指标 |
| **情感分析** | 正面/负面/中性词汇计数，输出整体情感倾向和词汇列表 |
| **结构化提取 | 嘉宾观点/数据/承诺/争议自动归类 |
| **要点提炼** | 核心结论3条内，关键数据标注来源 |
| **待办跟踪** | 纪要中隐含的承诺/跟进事项自动提取 |
| **风险提示** | 夸大陈述/数据不一致/合规风险自动识别 |

## 二、输入格式

### 文字输入
```
纪要生成 今天上午调研宁德时代关于储能业务的情况
纪要 招商银行零售业务交流会 老张/老李参会
```

### 音频文件路径输入（模拟语音转文字）
```
python3 scripts/minutes_cli.py generate "语音转文字 会议录音.wav"
python3 scripts/minutes_cli.py generate "实地调研_宁德时代_20240601.mp3"
python3 scripts/minutes_cli.py generate "策略会演讲记录.m4a"
```

## 三、输出格式

### text / json / markdown / wecom_card

## 四、输出字段说明

```json
{
  "title": "日期 公司 会议类型纪要",
  "meeting_type": "实地调研",          // 原始会议类型
  "meeting_category": "实地调研",       // 标准分类：策略会/业绩会/实地调研/电话会议/投资者日/交流会
  "company": "宁德时代",
  "date": "2024年6月1日",
  "core_topics": ["储能业务", "海外业务", "竞争格局"],
  "sentiment_analysis": {              // 情感分析结果
    "positive_count": 5,
    "negative_count": 2,
    "neutral_count": 45,
    "overall_sentiment": "正面",
    "positive_words": ["增长", "超预期", ...],
    "negative_words": ["压力", "竞争加剧", ...],
    "sentiment_ratio": 2.5
  },
  "key_data_points": [                 // 关键数据点
    {"value": "200%", "type": "增长率", "context": "...", "source": "公司披露"}
  ],
  "commitments": [                     // 承诺事项
    {"content": "明年海外收入占比提升至40%", "priority": "高", "deadline": "2025年"}
  ],
  "risk_signals": [                    // 风险信号
    {"signal": "...", "type": "竞争风险", "severity": "中"}
  ],
  "competitor_info": [                 // 竞品信息
    {"company": "比亚迪", "ticker": "BYD", "context_sentiment": "中性"}
  ],
  "industry_data": [                   // 行业数据
    {"data": "行业规模约2000亿元", "type": "市场规模", "context": "..."}
  ],
  "guidance": {                        // 管理层指引
    "revenue_guidance": "预计全年收入约500亿",
    "profit_guidance": null,
    "margin_guidance": "毛利率约35%"
  },
  "financial_metrics": {},             // 财务指标 PE/PB/ROE等
  "key_points": [...],
  "action_items": [...],
  "risks": [...],
  "summary": "...",
  "voice_transcript": "...",           // 原始转录文字（语音输入时）
  "generated_at": "2024-06-01 15:30:00"
}
```

## 五、类说明

### VoiceTranscriptParser
语音转文字解析器。输入音频文件路径，输出模拟转录文字和元数据。
- `parse(audio_path, meeting_type_hint)` → `VoiceTranscriptResult`

### KeyExtractor
关键信息提取器。输入转录文字，提取结构化信息。
- `extract(text, meeting_type)` → `Dict` (key_data_points / commitments / risk_signals / competitor_info / industry_data / guidance / financial_metrics)

### SentimentAnalyzer
情感分析器。统计正负面词汇出现次数。
- `count(text)` → `Dict` (positive_count / negative_count / overall_sentiment / positive_words / negative_words / sentiment_ratio)

### MeetingMinutesEngine
主引擎。同时支持文字输入和音频文件路径输入。
- `generate(source)` → `MeetingMinutes`
- `generate_from_audio(audio_path)` → `MeetingMinutes`
- `generate_from_text(text)` → `MeetingMinutes`

## 六、依赖

无外部依赖，纯 Python 标准库实现。
