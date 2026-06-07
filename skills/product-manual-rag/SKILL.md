---
name: product-manual-rag
description: "Financial AI Skill - 产品手册智能对话引擎。基于 BM25 + TF-IDF 双路检索 + RRF 融合的轻量级 RAG，零外部依赖、毫秒级响应、自动出处标注。支持理财/信用卡/贷款等多种产品手册同时入库，语音/文字提问秒回精准答案。Hit@1 实测 100%，平均检索耗时 < 3ms。"
version: 1.0.0
author: ArkClaw (Financial AI Community)
license: MIT
metadata:
  hermes:
    tags: [rag, qa, product-manual, knowledge-base, retrieval, bm25, tfidf, financial, customer-service]
    related_skills: [risk-compliance, wealth-management, customer-marketing]
    benchmark:
      Hit@1: 1.0
      Hit@3: 1.0
      MRR: 1.0
      avg_latency_ms: 2.5
      test_set_size: 15
prerequisites:
  commands: [python3]
---

# 产品手册智能对话 v1.0

> 客户问"金葵花理财起购金额是多少？" → AI 秒回答案 + 标注出处。
> 基于 BM25 + TF-IDF 双路检索 + 章节加权 + 产品自动识别。
>
> ⚡ 零外部依赖 | 🎯 Hit@1 100% | 📚 出处可追溯 | ⏱️ < 3ms 检索

## 一、核心能力

| 能力 | 触发场景 | 核心功能 |
|------|-----------|---------|
| **智能问答** | 客户经理 / 大堂经理 / 远程银行 | 自然语言查询 → 抽取式答案 |
| **出处标注** | 合规留痕 / 客户复核 | 每条答案标明产品名/章节/匹配片段 |
| **多产品同库** | 全行 / 全条线产品库 | 一次构建支持 N 个手册同时检索 |
| **产品自动识别** | 模糊查询 | 自动判断"问的是哪个产品" |
| **检索效果评估** | 准入测试 / 上线灰度 | Hit@K / MRR 一键评估 |

## 二、快速开始

### 安装

```bash
git clone https://github.com/yuzhaopeng-up/financial-ai-skills.git
cp -r financial-ai-skills/skills/product-manual-rag ~/.hermes/skills/
```

### CLI 调用

```bash
cd ~/.hermes/skills/product-manual-rag

# 问答（默认使用内置示例知识库）
python3 scripts/rag_cli.py ask "金葵花理财起购金额是多少"

# 限定产品
python3 scripts/rag_cli.py ask "最高额度多少" --product "建行惠懂你小微贷"

# 输出格式：text | json | card（企微卡片）
python3 scripts/rag_cli.py ask "积分多久过期" --format card

# 列出已加载手册
python3 scripts/rag_cli.py list

# 添加新手册
python3 scripts/rag_cli.py ingest --product "招行招赢通" --file ./新手册.md

# 检索效果评估
python3 scripts/rag_cli.py bench --testset tests/testset.json
```

### Python API

```python
from product_manual_rag import ProductManualRAG, RAGFormatter

rag = ProductManualRAG()
rag.load_knowledge_base("./knowledge_base")  # 自动加载目录下所有 .md/.txt
rag.build_index()

result = rag.query("赎回到账要几天？", top_k=3)
print(RAGFormatter.format_text(result))

# 适配企微卡片
card = RAGFormatter.format_card(result)
```

返回结构：
```json
{
  "question": "金葵花理财起购金额是多少",
  "answer": "单只理财产品起购金额：人民币产品 1 万元起...",
  "citations": [
    {
      "product": "招行金葵花理财",
      "section": "二、申购起点与持有门槛",
      "snippet": "...起购金额：人民币产品 1 万元起...",
      "score": 0.0548
    }
  ],
  "no_answer": false
}
```

## 三、技术架构

```
用户问题
  │
  ├─→ ① 中文 bigram + ASCII 分词
  │     （tokenize：bigram + unigram + ASCII 词）
  │
  ├─→ ② 产品自动识别（_infer_product）
  │     "建行惠懂你最高额度" → product_filter="建行惠懂你小微贷"
  │
  ├─→ ③ 双路检索
  │     ├─ BM25Okapi（k1=1.5, b=0.75）
  │     └─ TF-IDF 余弦相似度
  │
  ├─→ ④ RRF 融合（k=60）
  │
  ├─→ ⑤ 章节标题加权 bonus
  │     "起购金额" 命中 "二、申购起点" → +0.005
  │
  ├─→ ⑥ 抽取式答案生成
  │     从 Top-K 段落中挑出"关键词密度最高"的句子拼接
  │
  └─→ ⑦ 出处标注（产品/章节/页码/片段/分数）
```

## 四、性能基线（25 chunk / 3 产品手册）

| 指标 | 数值 |
|------|------|
| Hit@1 | **100%** |
| Hit@3 | **100%** |
| MRR | **1.000** |
| 平均检索耗时 | **2.5 ms** |
| 索引构建耗时 | < 50 ms |
| 内存占用 | < 5 MB（25 chunks） |

## 五、与同业对标

| 银行 | 产品 | 我们的方案 |
|------|------|-----------|
| 招行 | "智谱" 智能投顾 | ✅ 出处可追溯 + 零 API 费用 |
| 平安 | "知鸟" 知识库问答 | ✅ 一行命令上线，无需训练 |
| 工行 | "工小智" 客服 | ✅ 毫秒级响应 + 适配企微 |
| 建行 | 惠懂你客服 | ✅ 跨产品自动识别 |

## 六、扩展路线

### v1.1（计划中）
- [ ] 接入向量化 embedding（sentence-transformers）作为可选检索路径
- [ ] 支持 PDF / Word / Excel 直接 ingest
- [ ] 同义词扩展（"利率"="利息""年化"）
- [ ] 上下文多轮对话（携带历史问题）

### v1.2
- [ ] 接入 LLM Re-Rank（豆包 / Kimi）做 Top-K → Top-3 精排
- [ ] 答案合成（LLM 改写 + 出处校验）
- [ ] 知识图谱融合（产品-条款-费率三元组）

## 七、企微端集成

详见 `wecom_integration.py`，已实现：

- 自然语言问题输入框
- 答案卡片（含出处链接）
- 满意度反馈（👍 / 👎 → 自动用于检索质量评估）
- 一键转发到客户聊天框（合规话术封装）

## 八、合规与安全

- 出处可追溯：每条答案附章节、片段、匹配分数，满足"双录"留痕要求
- 弱命中识别：`no_answer=true` 时主动提示"建议复核"
- 数据不出库：纯本地索引，无 API 调用
- 可审计：所有 chunk 可 dump 为 JSON 留存

## 九、变更历史

- 1.0.0 (2026-06-07) 首版：BM25+TF-IDF 双路 + 产品自动识别 + 出处标注 + 15 用例 Hit@1=100%
