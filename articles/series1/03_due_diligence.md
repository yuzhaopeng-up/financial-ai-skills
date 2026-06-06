# 对公客户尽职调查智能化：从7天到7分钟的企业风险扫描

> 开源地址：https://github.com/yuzhaopeng-up/financial-ai-skills
>
> 基于《AI赋能银行数字化转型》第11章实战代码，复用风控评分能力。

---

## 一、传统尽调的痛点

某银行对公客户经理的日常：

- **信息采集**：工商、司法、舆情、财务，4个系统来回切换
- **行业研究**：找报告、查数据、做对比，2天过去
- **风险判断**：凭经验打分，标准不统一
- **报告撰写**：复制粘贴，格式混乱，3小时一篇

**结果**：一笔对公开户尽调，7个工作日才能完成。

---

## 二、AI尽调：7分钟完成全流程

```python
from due_diligence import DueDiligenceEngine

engine = DueDiligenceEngine()

report = engine.conduct_due_diligence(
    company_name="示例科技有限公司",
    credit_code="91310000XXXXXXXXXX",
    industry="软件和信息技术服务业"
)

print(report.to_markdown())
```

**输出**：
```
📋 对公客户尽职调查报告
├── 企业基本信息：成立7年，注册资本5000万
├── 行业分析：软件业，高速增长（15.2%）
├── 财务评分：综合85分 🟢 良好
│   ├── 偿债能力：100分 🟢 优秀
│   ├── 盈利能力：90分 🟢 优秀
│   ├── 运营能力：70分 🟡 一般
│   └── 成长能力：70分 🟡 一般
└── 风险评估：🟡 中风险（79分）
    ├── 财务风险：🟢 低风险
    ├── 司法风险：🟡 中风险（1起诉讼）
    ├── 舆情风险：🟢 低风险
    └── 行业风险：🟡 中风险
```

---

## 三、8大能力

| 能力 | 描述 | 书中对应 |
|------|------|---------|
| **企业信息采集** | 工商、司法、舆情、财务多源采集 | 第11章 11.1 |
| **行业研究分析** | 行业地位、竞争格局、发展趋势 | 第11章 11.2 |
| **关联关系挖掘** | 股权穿透、实际控制人、关联交易 | 第11章 11.3 |
| **财务健康评分** | 偿债/盈利/运营/成长四维评分 | 第11章 11.4 |
| **风险综合评级** | 复用 risk-compliance 评分体系 | 第10章 10.3 |
| **尽调报告生成** | 标准化 Markdown/Word 报告 | 第11章 11.5 |
| **舆情监控预警** | 负面新闻、诉讼、失信实时追踪 | 第11章 11.6 |
| **担保圈识别** | 复用 knowledge_graph 担保链检测 | 第10章 10.2.3 |

---

## 四、核心设计

```
DueDiligenceEngine
├── CompanyDataCollector      # 企业信息采集
│   ├── collect_basic_info()   # 工商信息
│   ├── collect_judicial_info() # 司法信息
│   ├── collect_public_opinion() # 舆情信息
│   └── collect_financial_data() # 财务数据
├── IndustryResearchAnalyzer  # 行业研究
├── FinancialHealthScorer     # 财务评分
├── RiskAssessor             # 风险评级（复用）
└── DueDiligenceReport       # 报告生成
```

---

## 五、财务评分算法

```python
class FinancialHealthScorer:
    def comprehensive_score(self, financial_data):
        solvency = self.calculate_solvency(
            total_assets, total_liabilities,
            current_assets, current_liabilities
        )  # 偿债能力
        
        profitability = self.calculate_profitability(
            revenue, net_profit, total_assets, total_equity
        )  # 盈利能力
        
        operation = self.calculate_operation(
            revenue, accounts_receivable, inventory, current_assets
        )  # 运营能力
        
        growth = self.calculate_growth(
            current_revenue, previous_revenue
        )  # 成长能力
        
        # 加权综合
        overall = (solvency * 0.3 + profitability * 0.3 +
                   operation * 0.2 + growth * 0.2)
        
        return FinancialScores(
            solvency_score=solvency,
            profitability_score=profitability,
            operation_score=operation,
            growth_score=growth,
            overall_score=overall
        )
```

---

## 六、实战演示

```python
# 执行完整尽调
result = engine.conduct_due_diligence(
    company_name="示例科技有限公司",
    credit_code="91310000XXXXXXXXXX",
    industry="软件和信息技术服务业"
)

# 关键指标
assert result['financial_scores']['overall_score'] == 85.0
assert result['risk_assessment']['overall_risk'] == '中风险'
```

---

## 七、开源

```
https://github.com/yuzhaopeng-up/financial-ai-skills/tree/master/skills/due-diligence
```

---

> **关于作者**：于兆鹏，银联工作，服务超500家金融机构。《AI赋能银行数字化转型》作者。
