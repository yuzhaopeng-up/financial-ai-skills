---
name: research_rag
description: "Financial AI Skill - 研报RAG检索引擎。BM25+TF-IDF双路检索+RRF融合+多轮对话上下文+引用标注，支持自然语言查询行业/公司研报知识库，零外部依赖。"
version: 1.0.0
author: ArkClaw (Financial AI Community)
license: MIT
metadata:
  hermes:
    tags: [rag, retrieval, bm25, tfidf, research, knowledge-base, ftir]
    related_skills: [research-report, financial-intelligence]
    coverage:
      industries: [新能源, 金融, 半导体, 医药, 消费, 汽车, 通用]
      companies: [宁德时代, 比亚迪, 招商银行, 贵州茅台, 宝钢股份]
prerequisites:
  commands: [python3]
---

# 研报RAG检索引擎 v1.0

> 输入研究问题 → 秒级输出带引用的答案
>
> ⚡ BM25 + TF-IDF 双路检索 | 🎯 RRF 融合 | 💬 多轮对话 | 📎 引用标注

## 一、核心能力

| 能力 | 说明 |
|------|------|
| **BM25 + TF-IDF 双路检索** | 两路独立索引，RRF 融合提升召回 |
| **多轮对话上下文** | 自动注入最近 3 轮对话内容 |
| **引用来源标注** | 返回 source_type / source_name / section / snippet |
| **规则答案生成** | 无需外部 LLM，基于模板规则生成结构化答案 |
| **PDF 研报扩展** | 支持加载额外 PDF 文件到知识库 |
| **4 种输出格式** | text / json / markdown / citations |

## 二、核心概念

- **Chunk**: 知识库最小检索单元（行业/公司/章节）
- **BM25**: 经典稀疏检索，适合关键词精确匹配
- **TF-IDF**: 词频-逆文档频率，捕捉语义关联
- **RRF (Reciprocal Rank Fusion)**: 双路结果融合排序
- **Citation**: 引用标注，含来源类型/名称/章节/摘要

## 三、快速开始

```bash
cd /tmp/financial-ai-skills/skills/research_rag

# CLI 查询（单轮）
python3 scripts/rag_cli.py query "研报RAG 宁德时代 储能业务竞争力分析"
python3 scripts/rag_cli.py query "招商银行净息差走势" --format json

# 多轮对话（交互式）
python3 scripts/rag_cli.py chat

# 查看知识库
python3 scripts/rag_cli.py stats

# 仅检索
python3 scripts/rag_cli.py search "新能源储能"
```

## 四、知识库来源

复用 `research-report` skill 的行业公司数据：

- **行业维度**：新能源 / 金融 / 半导体 / 医药 / 消费 / 汽车 / 通用
- **公司维度**：宁德时代 / 比亚迪 / 招商银行 / 贵州茅台 / 宝钢股份
- **章节维度**：行业趋势 / 增长驱动 / 龙头公司 / 关键指标 / 风险提示 / 护城河 / 公司亮点 / 公司风险

## 五、检索流程

```
用户查询
   ↓
Query Expansion（注入对话历史）
   ↓
BM25 检索（top_k） + TF-IDF 检索（top_k）
   ↓
RRF 融合（k=60）
   ↓
返回 Top-K 结果 + Citation 标注
   ↓
规则答案生成（模板引擎）
   ↓
RAGAnswer（含 citations / sources / conversation_turns）
```

## 六、API 用法

```python
from research_rag import ResearchRAGEngine, query

# 单次查询
answer = query("宁德时代储能业务竞争力分析")
print(answer.answer)
for c in answer.citations:
    print(f"[{c.source_type}] {c.source_name} · {c.section}")

# 多轮对话
eng = ResearchRAGEngine(max_turns=3)
ans1 = eng.query("宁德时代储能业务如何？")
ans2 = eng.query("那和比亚迪比呢？")   # 自动带入历史上下文
```

## 七、输出格式

```
🏢 **宁德时代** 关键信息：
  • 护城河：全球动力电池龙头(37%全球市占率)...
  • 主营业务：动力电池|储能电池|电池材料
  • 近期亮点：储能业务高速增长|海外建厂...
  ⚠️ 关注风险：国内竞争加剧(比亚迪/中创新航)...
```
