---
name: research-report
description: "Financial AI Skill - 投研报告自动生成器。输入行业/公司/年度自然语言请求，自动输出完整投研报告（摘要+行业趋势+公司基本面+财务估值+风险提示+投资建议）。覆盖 6 大行业（新能源/金融/半导体/医药/消费/汽车）和 5 家龙头公司模板，零外部依赖。"
version: 1.0.0
author: ArkClaw (Financial AI Community)
license: MIT
metadata:
  hermes:
    tags: [research, report, equity, industry, investment, analysis]
    related_skills: [financial-intelligence, wealth-management, risk-compliance]
    coverage:
      industries: 6+1 (通用)
      companies: 5
      templates: 6 sections
prerequisites:
  commands: [python3]
---

# 研报生成器 v1.0

> 输入 `研报生成 新能源 宁德时代 2025` → 秒级输出六大章节完整投研报告
>
> ⚡ 零外部依赖 | 🎯 6 大行业 | 📊 5 家龙头公司

## 一、核心能力

| 能力 | 说明 |
|------|------|
| **自然语言解析** | 从 `研报生成 新能源 宁德时代 2025` 自动提取行业/公司/年度 |
| **行业趋势分析** | 6 大行业（新能源/金融/半导体/医药/消费/汽车）预置趋势、驱动因素、风险、龙头名单 |
| **公司基本面** | 5 家龙头（宁德时代/比亚迪/招商银行/贵州茅台/宝钢股份）预置护城河、亮点、风险 |
| **财务估值参考** | 估值方法说明（PE/PB/DCF）+ 关键指标 + 可比公司 |
| **风险提示** | 行业风险 + 公司风险 + 系统性风险自动汇总 |
| **投资建议** | 规则引擎自动评级（买入/增持/中性/减持） |
| **4 种输出格式** | text / json / markdown / wecom_card |

## 二、快速开始

### CLI 调用

```bash
cd ~/.hermes/skills/research-report

# 查看支持的行业与公司
python3 scripts/report_cli.py list

# 生成知名公司完整报告（置信度 100%）
python3 scripts/report_cli.py generate "研报生成 新能源 宁德时代 2025"
python3 scripts/report_cli.py generate "研报 招商银行 2025"

# 仅行业报告（置信度 70%）
python3 scripts/report_cli.py generate "研报 半导体 2025"

# 未知公司/行业（置信度 50%，通用模板）
python3 scripts/report_cli.py generate "研报 某公司 2025"

# 不同输出格式
python3 scripts/report_cli.py generate "研报 新能源 宁德时代 2025" --format md
python3 scripts/report_cli.py generate "研报 新能源 宁德时代 2025" --format json
python3 scripts/report_cli.py generate "研报 新能源 宁德时代 2025" --format card
```

### Python API

```python
from research_report import ReportEngine, ReportFormatter

eng = ReportEngine()

# 自然语言输入
r = eng.generate("研报生成 新能源 宁德时代 2025")
print(r.title)              # 【2025】宁德时代（新能源）投研报告
print(r.summary)            # 摘要
print(r.investment_view)    # 投资建议

# 结构化输入
r = eng.generate({"industry": "金融", "company": "招商银行", "year": 2025})

# 输出报告
print(ReportFormatter.to_text(r))
print(ReportFormatter.to_markdown(r))
```

## 三、输入格式

### 支持的输入变体

```
研报生成 新能源 宁德时代 2025
研报 招商银行 2025
研报生成 半导体行业 2025  
研报 比亚迪
研报 某公司 2025
```

任意组合均可，引擎自动识别：

- `研报生成` / `研报` / `生成研报` 等前缀均可
- 行业名匹配（6 个大类）
- 公司名匹配（已收录 5 家 + 未收录自动使用通用模板）
- 年度自动提取，不填则使用当年

## 四、支持的行业与公司

### 行业

| 行业 | 趋势数 | 驱动因素 | 风险点 | 龙头数 |
|------|--------|---------|--------|--------|
| 新能源 | 9 | 5 | 5 | 6 |
| 金融 | 8 | 5 | 5 | 5 |
| 半导体 | 6 | 4 | 4 | 6 |
| 医药 | 6 | 4 | 4 | 5 |
| 消费 | 6 | 4 | 4 | 5 |
| 汽车 | 6 | 4 | 4 | 5 |

### 已收录公司

| 公司 | 代码 | 行业 | 护城河数 | 风险数 |
|------|------|------|---------|--------|
| 宁德时代 | 300750.SZ | 新能源 | 3 | 3 |
| 比亚迪 | 002594.SZ | 汽车 | 3 | 3 |
| 招商银行 | 600036.SH | 金融 | 3 | 3 |
| 贵州茅台 | 600519.SH | 消费 | 3 | 3 |
| 宝钢股份 | 600019.SH | 通用 | 3 | 3 |

## 五、报告结构

1. **报告摘要** — 公司/行业定位 + 亮点 + 核心驱动 + 风险
2. **行业趋势分析** — 核心技术趋势 + 增长驱动 + 行业风险 + 龙头公司
3. **公司基本面分析** — 代码 + 业务构成 + 护城河 + 近期亮点
4. **财务亮点与估值** — 关键指标 + 估值方法 + 可比公司
5. **风险提示** — 行业风险 + 公司风险 + 系统性风险
6. **投资建议** — 评级 + 核心理由 + 催化剂 + 时间维度

## 六、扩展指南

### 新增行业

编辑 `report_templates.json::industries`，添加：

```json
"新行业名": {
    "trend_keywords": ["趋势1", "趋势2"],
    "drivers": ["驱动1", "驱动2"],
    "risks": ["风险1", "风险2"],
    "leaders": ["龙头A", "龙头B"],
    "key_metrics": ["指标1", "指标2"]
}
```

### 新增公司

在 `report_templates.json::companies` 添加：

```json
"公司名": {
    "code": "XXXXXX.SZ",
    "industry": "已有行业",
    "business_segments": ["业务1", "业务2"],
    "moat": ["护城河1"],
    "highlights": ["亮点1"],
    "risks": ["风险1"]
}
```

## 七、版本

- **1.0.0** (2026-06-07) 首版：6 行业+5 公司+6 大章节+4 种输出格式，18/18 测试通过