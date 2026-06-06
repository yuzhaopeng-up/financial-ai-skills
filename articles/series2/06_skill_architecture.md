# 银行智能体架构：7个Skill如何协同工作

> 开源地址：https://github.com/yuzhaopeng-up/financial-ai-skills
> 
> 系统架构设计，展示7个Skill的协同关系。

---

## 一、为什么需要多Skill协同？

单个AI模型无法覆盖银行所有业务场景：

- **财务场景**：发票、现金流、税务
- **风控场景**：反洗钱、信用评估
- **营销场景**：客户分层、产品推荐
- **运营场景**：工单、流程、监控

**解决方案**：模块化Skill，按需组合。

---

## 二、整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户交互层                             │
│         (企微Bot / 飞书Bot / Web界面 / API)              │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                    智能体编排层                           │
│              (任务分发 / Skill调度 / 上下文管理)           │
└─────────────────────────────────────────────────────────┘
                           ↓
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│ financial│  risk    │   due    │  retail  │  credit  │
│intelligence│compliance│diligence │ marketing│ approval │
│  财务智能  │  风控合规  │  对公尽调  │  零售营销  │  信贷审批  │
├──────────┼──────────┼──────────┼──────────┼──────────┤
│ wealth   │operations│          │          │          │
│management│automation│          │          │          │
│  财富管理  │  运营自动化 │          │          │          │
└──────────┴──────────┴──────────┴──────────┴──────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                    数据层                                │
│         (企业信息 / 交易数据 / 客户画像 / 知识库)          │
└─────────────────────────────────────────────────────────┘
```

---

## 三、Skill之间的调用关系

### 3.1 对公开户流程

```
用户: "我要开对公账户"
    ↓
[retail-marketing] 识别客户意图
    ↓
[due-diligence] 执行尽职调查
    ├── [company_collector] 采集企业信息
    ├── [industry_research] 行业研究
    ├── [financial_scorer] 财务评分
    └── [risk_assessor] 风险评估 (复用risk-compliance)
    ↓
[credit-approval] 授信审批 (如需)
    ├── [credit_scorer] 信用评分
    └── [decision_engine] 审批决策
    ↓
[operations-automation] 开户流程编排
    └── [workflow_engine] 自动开户
    ↓
用户: "开户完成，账户已激活"
```

### 3.2 零售客户营销

```
[retail-marketing] 客户画像构建
    ├── [customer_profiler] 标签体系
    ├── [customer_segment] RFM分层
    └── [product_matcher] 产品匹配
    ↓
[wealth-management] 资产配置建议
    ├── 资产全景视图
    ├── 退休规划
    └── 税务优化
    ↓
[operations-automation] 营销执行
    ├── [ticket_processor] 创建营销任务
    └── [campaign_evaluator] 效果追踪
```

---

## 四、数据流转

### 4.1 客户数据流

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  客户基本信息  │────→│  客户画像    │────→│  分层标签    │
│  (CRM系统)   │     │  (Profiler) │     │  (Segment)  │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                                ↓
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  营销效果    │←────│  推荐产品    │←────│  匹配引擎    │
│  (Evaluator)│     │  (Matcher)  │     │  (Matcher)  │
└─────────────┘     └─────────────┘     └─────────────┘
```

### 4.2 风险数据流

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  交易数据    │────→│  关联图谱    │────→│  风险检测    │
│  (核心系统)  │     │  (Graph)    │     │  (Detector) │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                                ↓
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  预警通知    │←────│  评分模型    │←────│  风险聚合    │
│  (Alert)    │     │  (Scorer)   │     │  (Assessor) │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## 五、技术选型

| 层级 | 技术 | 说明 |
|------|------|------|
| 交互层 | 企微Bot / 飞书Bot | 用户入口 |
| 编排层 | Python + 规则引擎 | 任务调度 |
| Skill层 | 纯Python标准库 | 零依赖 |
| 数据层 | SQLite / MySQL | 轻量级存储 |
| 部署 | Docker / 裸机 | 灵活部署 |

---

## 六、扩展性设计

### 6.1 新增Skill

```python
# 新增一个Skill只需3步

# 1. 创建目录
mkdir skills/new-skill

# 2. 实现核心逻辑
# skills/new-skill/new_skill.py
class NewSkill:
    def process(self, input_data):
        # 业务逻辑
        return result

# 3. 注册到主引擎
# main.py
from new_skill import NewSkill
engine.register_skill("new-skill", NewSkill())
```

### 6.2 Skill复用

```python
# due-diligence 复用 risk-compliance 的评分能力
from risk_assessor import RiskAssessor

class DueDiligenceEngine:
    def __init__(self):
        self.risk_assessor = RiskAssessor()  # 复用
    
    def assess_risk(self, company_data):
        # 调用risk-compliance的能力
        return self.risk_assessor.comprehensive_assessment(...)
```

---

## 七、开源

完整代码：
```
https://github.com/yuzhaopeng-up/financial-ai-skills
```

---

> **关于作者**：于兆鹏，银联工作，服务超500家金融机构。《AI赋能银行数字化转型》作者。
