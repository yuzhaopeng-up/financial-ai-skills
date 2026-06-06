# 开源金融AI技能库：56个场景全覆盖

> 开源地址：https://github.com/yuzhaopeng-up/financial-ai-skills
>
> 7个Skill，56个场景，MIT许可证，欢迎Star和贡献。

---

## 一、项目概览

| 指标 | 数据 |
|------|------|
| Skill数量 | 7个 |
| 覆盖场景 | 56个 |
| 代码行数 | 10,000+ |
| 许可证 | MIT |
| 依赖 | 纯Python标准库 |

---

## 二、Skill矩阵

| Skill | 场景数 | 核心能力 | 书中对应 |
|-------|--------|----------|---------|
| **financial-intelligence** | 6 | 发票/现金流/税务/预算/费用/报表 | 基础财务 |
| **wealth-management** | 8 | 资产配置/税务优化/退休规划 | 第12章 |
| **risk-compliance** | 10 | 关联图谱/反洗钱/风险评分 | 第10章 |
| **due-diligence** | 8 | 企业信息采集/行业研究/尽调报告 | 第11章 |
| **retail-marketing** | 8 | 客户画像/分层/推荐/AUM提升 | 第12-13章 |
| **credit-approval** | 8 | 申请受理/信用评分/审批决策 | 第14-15章 |
| **operations-automation** | 8 | 工单/流程/监控/RPA | 第16-17章 |

---

## 三、快速开始

```bash
# 克隆仓库
git clone https://github.com/yuzhaopeng-up/financial-ai-skills.git

# 进入项目
cd financial-ai-skills

# 运行演示
python skills/financial-intelligence/examples/demo.py
python skills/risk-compliance/knowledge_graph.py
python skills/retail-marketing/retail_marketing.py
```

---

## 四、使用示例

### 4.1 财务智能

```python
from skills.financial_intelligence.engines.invoice_engine import InvoiceProcessor

processor = InvoiceProcessor()
result = processor.process_invoice({
    'invoice_code': '3100123456',
    'amount': 50000.00
})
print(result['summary'])
```

### 4.2 风控合规

```python
from skills.risk_compliance.knowledge_graph import KnowledgeGraphBuilder, FraudPatternDetector

graph = KnowledgeGraphBuilder()
graph.add_node("A001", "账户", "企业A")
graph.add_edge("P001", "A001", "转账", 500000)

detector = FraudPatternDetector(graph)
stars = detector.detect_star_pattern()
```

### 4.3 零售营销

```python
from skills.retail_marketing.retail_marketing import RetailMarketingEngine

engine = RetailMarketingEngine()
result = engine.full_marketing_analysis(
    customer_id="C001",
    name="李明",
    age=35,
    aum=500000,
    risk_preference="稳健型"
)
```

---

## 五、项目结构

```
financial-ai-skills/
├── skills/
│   ├── financial-intelligence/    # 财务智能
│   ├── wealth-management/         # 财富管理
│   ├── risk-compliance/           # 风控合规
│   ├── due-diligence/            # 对公尽调
│   ├── retail-marketing/         # 零售营销
│   ├── credit-approval/          # 信贷审批
│   └── operations-automation/    # 运营自动化
├── articles/                      # 技术文章
├── content_strategy.md           # 内容策略
├── README.md                      # 项目说明
└── LICENSE                        # MIT许可证
```

---

## 六、贡献指南

### 6.1 提交新Skill

1. Fork仓库
2. 创建新分支：`git checkout -b feat/new-skill`
3. 在`skills/`目录下新建文件夹
4. 实现核心逻辑 + SKILL.md + 示例
5. 提交PR

### 6.2 提交文章

1. 在`articles/`目录下新建文章
2. 遵循模板格式
3. 提交PR

---

## 七、路线图

| 阶段 | 目标 | 时间 |
|------|------|------|
| Phase 1 | 7个核心Skill | ✅ 已完成 |
| Phase 2 | 监管报送Skill | 2026 Q3 |
| Phase 3 | 数据平台Skill | 2026 Q4 |
| Phase 4 | 多语言支持 | 2027 Q1 |

---

## 八、社区

- GitHub Discussions：技术讨论
- Issues：Bug反馈、功能建议
- Pull Requests：代码贡献

---

## 九、Star历史

[![Star History Chart](https://api.star-history.com/svg?repos=yuzhaopeng-up/financial-ai-skills&type=Date)](https://star-history.com/#yuzhaopeng-up/financial-ai-skills&Date)

---

> **关于作者**：于兆鹏，银联工作，服务超500家金融机构。《AI赋能银行数字化转型》作者。
>
> 如果这个项目对你有帮助，请给个 ⭐ Star！
