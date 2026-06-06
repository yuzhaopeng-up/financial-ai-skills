---
name: risk-compliance
description: "Financial AI Skill - 风控合规智能体。提供企业风险评估、信用评级、反欺诈检测、合规检查、财务诊断、监管政策查询、贷后监控、产业链风险追踪、市场情绪监测、关联图谱分析等10大能力。基于规则引擎的轻量级风控系统，零API费用。"
version: 1.1.0
author: Financial AI Community
license: MIT
metadata:
  hermes:
    tags: [risk, compliance, fraud, credit, enterprise, audit, policy, monitoring, knowledge-graph, anti-money-laundering]
    related_skills: [financial-intelligence, wealth-management]
prerequisites:
  commands: [python3]
---

# 风控合规智能体 v1.1
> 基于规则引擎的轻量级风控系统，10大场景全覆盖。
>
> ⚡ 零API费用 | 🚀 毫秒级响应 | 📦 开箱即用

## 一、10大风控合规能力

| 能力 | 触发关键词 | 核心功能 |
|------|-----------|---------|
| **企业风险评估** | 企业风险、评估 | 多维度风险评分与预警 |
| **信用评级** | 信用评级、征信 | 企业信用等级评定 |
| **反欺诈检测** | 反欺诈、交易异常 | 交易风险识别与处置建议 |
| **合规检查** | 合规、检查 | 制度执行与整改建议 |
| **财务诊断** | 财务诊断、体检 | 财务指标分析与预警 |
| **监管政策** | 政策、监管 | 最新政策查询与解读 |
| **贷后监控** | 贷后、监控 | 授信客户动态监控 |
| **产业链风险** | 产业链、供应链 | 上下游风险传导分析 |
| **市场情绪** | 市场情绪、舆情 | 市场情绪监测与预警 |
| **关联图谱分析** ⭐新增 | 关联图谱、团伙、洗钱 | 星型/循环/链式转账检测、担保链、隐性关联 |

## 二、快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yuzhaopeng-up/financial-ai-skills.git

# 复制Skill到Hermes目录
cp -r financial-ai-skills/skills/risk-compliance ~/.hermes/skills/
```

### Python API 调用

```python
import sys
sys.path.insert(0, "~/.hermes/skills/risk-compliance")

from risk_engine import RiskEngine, RiskFormatter

# 初始化
engine = RiskEngine()
formatter = RiskFormatter()

# 企业风险评估
result = engine.get_enterprise_risk("比亚迪")
print(formatter.format_enterprise_risk(result))

# 反欺诈检测
result = engine.get_anti_fraud("TX2026001")
print(formatter.format_anti_fraud(result))

# 合规检查
result = engine.get_compliance()
print(formatter.format_compliance(result))
```

## 三、演示数据

### 企业风险数据

| 企业 | 股票代码 | 行业 | 风险评分 | 信用等级 |
|------|----------|------|---------|----------|
| 比亚迪 | 002594 | 汽车制造 | 72 | AA |
| 宁德时代 | 300750 | 电池制造 | 68 | AA- |
| 某科技公司 | 未上市 | 软件开发 | 55 | BBB |

### 反欺诈案例

| 交易编号 | 金额 | 风险评分 | 风险等级 |
|----------|------|---------|----------|
| TX2026001 | ¥500,000 | 85 | 高风险 |
| TX2026002 | ¥5,000 | 25 | 低风险 |

## 四、项目结构

```
risk-compliance/
├── risk_engine.py          # 核心引擎 + 格式化器
├── knowledge_graph.py      # ⭐新增：关联图谱分析模块
└── SKILL.md                # 本文件
```

## 五、关联图谱分析（⭐v1.1新增）

### 核心能力

| 检测模式 | 风险场景 | 输出 |
|---------|---------|------|
| **星型转账** | 非法集资、洗钱 | 中心账户、关联账户数、涉及金额 |
| **循环转账** | 虚构交易、洗钱 | 循环路径、涉及节点、金额 |
| **链式转账** | 多层嵌套、规避监管 | 链长、总金额、风险等级 |
| **隐性关联** | 空壳公司集群 | 共同地址/电话/IP、关联主体 |
| **担保链** | 风险传导、连环违约 | 担保路径、链长、总敞口 |

### 快速使用

```python
from knowledge_graph import KnowledgeGraphBuilder, FraudPatternDetector, GraphFormatter

# 构建图谱（从交易数据）
graph = KnowledgeGraphBuilder()
graph.add_node("A001", "账户", "企业A")
graph.add_node("A002", "账户", "企业B")
graph.add_edge("A002", "A001", "转账", 500000, amount=500000)

# 检测欺诈模式
detector = FraudPatternDetector(graph)
patterns = {
    "star": detector.detect_star_pattern(),
    "cycle": detector.detect_cycle_pattern(),
    "hidden": detector.detect_hidden_association(),
    "guarantee": detector.detect_guarantee_chain(),
}

# 格式化输出
formatter = GraphFormatter()
print(formatter.format_comprehensive_report(patterns))
```

## 六、技术特点

- **纯Python实现**：无外部API依赖，零调用成本
- **规则引擎**：100%可复现结果，适合合规审计场景
- **Markdown输出**：适配IM平台（企业微信、飞书、钉钉等）
- **可扩展**：基于类结构，易于添加新企业和新规则

## 七、版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.1 | 2026-06-06 | 新增关联图谱分析模块（knowledge_graph.py），支持星型/循环/链式转账检测、隐性关联发现、担保链分析 |
| v1.0 | 2026-06-06 | 初始发布，9大风控合规能力完整实现 |

## 许可证

[MIT License](../../LICENSE)

---

*Financial AI Community | 以真实用户反馈为唯一北极星指标*
