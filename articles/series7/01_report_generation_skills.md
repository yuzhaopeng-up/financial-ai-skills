---
title: "我用AI写了7个金融报告生成器：从调研纪要到全球资产配置"
description: "分享7个开源金融AI Skill的开发实录——调研纪要、市场观点、路演材料、基金研究、运营日报、家族信托、全球资产配置"
tags: ["金融AI", "开源", "Python", "智能体", "报告生成"]
---

# 我用AI写了7个金融报告生成器：从调研纪要到全球资产配置

> 零API费用，纯Python实现，已开源在 GitHub

## 为什么做这件事？

在银行工作多年，我发现一个痛点：**写报告太耗时了**。

- 研究员每天花2小时写调研纪要
- 运营部每天花1小时整理日报数据
- 理财经理每次见客户前花半天准备资产配置方案
- 投行团队花一周准备路演材料

这些工作有80%是结构化的——有固定模板、固定逻辑、固定输出格式。为什么不能交给AI？

## 7个报告生成器一览

### 1. 调研纪要生成器 (meeting_minutes)

**输入**：调研录音文字稿或要点笔记
**输出**：结构化纪要（参会人+议题+关键要点+待办事项+风险提示）

```python
from meeting_minutes import MeetingMinutesEngine

eng = MeetingMinutesEngine()
result = eng.generate("今天上午调研示例新能源企业储能业务")
```

**核心能力**：
- 自动识别参会人和公司
- 提取核心议题和关键数据
- 生成待办事项（带责任人和截止日期）
- 识别风险提示

### 2. 市场观点输出器 (market_view)

**输入**："市场日报"或"策略周报"
**输出**：完整市场观点（大盘综述+行业表现+热点主题+资金流向+展望）

```python
from market_view import MarketViewEngine

eng = MarketViewEngine()
result = eng.generate("市场日报 今天A股收盘")
```

**核心能力**：
- 模拟主要指数表现（沪深300/上证/创业板）
- 分析行业涨跌和热点主题
- 资金流向分析（北向资金/主力/散户）
- 短期/中期/长期展望

### 3. 路演材料生成器 (roadshow_material)

**输入**：产品类型+目标客户+时长
**输出**：PPT大纲+演讲稿+竞品对比+风险揭示+QA准备

```python
from roadshow_material import RoadshowEngine

eng = RoadshowEngine()
result = eng.generate("路演材料 固收理财 50岁保守型 30分钟")
```

**核心能力**：
- 自动生成15-20页PPT大纲
- 每页配演讲要点和时间分配
- 竞品对比表格
- 常见客户异议和应答话术

### 4. 基金研究报告生成器 (fund_research)

**输入**：基金名称或代码
**输出**：完整基金分析报告（业绩归因+风险指标+经理评价+配置建议）

```python
from fund_research import FundResearchEngine

eng = FundResearchEngine()
result = eng.generate("基金研究 示例基金公司A中小盘")
```

**核心能力**：
- 多区间业绩分析（1月/3月/6月/1年/3年/成立来）
- 风险指标（波动率/最大回撤/夏普比率）
- 基金经理风格画像
- 重仓股分析和行业配置

### 5. 运营日报生成器 (ops_daily_report)

**输入**：业务数据指标
**输出**：结构化运营日报（业务概况+异常预警+同比环比+明日计划）

```python
from ops_daily_report import OpsDailyReportEngine

eng = OpsDailyReportEngine()
result = eng.generate("运营日报 存款1000亿 贷款800亿")
```

**核心能力**：
- 自动计算环比/同比
- 异常指标预警（阈值判断）
- 生成明日工作计划
- 一句话业务总结

### 6. 家族信托方案生成器 (family_trust)

**输入**：客户年龄+资产规模+核心需求
**输出**：完整信托方案（架构设计+资产配置+税务筹划+受益人安排+风险隔离）

```python
from family_trust import FamilyTrustEngine

eng = FamilyTrustEngine()
result = eng.generate("家族信托 客户50岁 资产3亿 传承子女")
```

**核心能力**：
- 信托架构设计（境内/离岸/混合）
- 资产配置建议（保守/稳健/平衡/进取）
- 税务筹划要点
- 受益人分配方案
- 风险隔离措施

### 7. 全球资产配置方案生成器 (global_asset_allocation)

**输入**：客户类型+风险偏好+资产规模
**输出**：全球配置方案（区域分布+资产类别+货币对冲+再平衡策略+合规提示）

```python
from global_asset_allocation import GlobalAssetAllocationEngine

eng = GlobalAssetAllocationEngine()
result = eng.generate("全球配置 高净值 R3 资产1亿")
```

**核心能力**：
- 区域配置（中国/美国/欧洲/亚太/其他）
- 资产类别分配（固收/权益/另类/现金）
- 货币对冲建议
- 再平衡策略
- 合规风险提示

## 技术架构

### 统一设计模式

所有7个Skill遵循相同架构：

```
Skill/
├── SKILL.md              # 技能文档
├── __init__.py           # 模块导出
├── *_engine.py           # 核心引擎
├── scripts/
│   └── *_cli.py          # CLI入口
└── wecom_integration.py  # 企微卡片集成
```

### 引擎基类模式

```python
class ReportEngine:
    def generate(self, source) -> Report:
        """生成报告"""
        pass
    
    def format_markdown(self, report) -> str:
        """格式化为Markdown"""
        pass
```

### 企微集成

每个Skill都包含`wecom_integration.py`，可直接生成企微消息卡片：

```python
from meeting_minutes import MeetingMinutesEngine

def build_card(result) -> dict:
    return {
        "msgtype": "interactive",
        "interactive": {
            "header": {"title": result.title},
            "elements": [...]
        }
    }
```

## 开源与使用

**GitHub仓库**：https://github.com/yuzhaopeng-up/financial-ai-workspace

**使用方式**：

1. **独立使用**：
```bash
cd skills/meeting_minutes
python3 minutes_engine.py
```

2. **CLI调用**：
```bash
python3 scripts/minutes_cli.py generate "调研纪要 示例新能源企业"
```

3. **企微集成**：
```bash
python3 wecom_integration.py "调研纪要 示例新能源企业"
```

## 实际应用场景

| 岗位 | 使用场景 | 节省时间 |
|------|----------|----------|
| 研究员 | 调研纪要+市场观点 | 2小时/天 |
| 投资经理 | 路演材料+基金研究 | 4小时/次 |
| 运营经理 | 运营日报 | 1小时/天 |
| 理财经理 | 家族信托+资产配置 | 3小时/客户 |
| 基金经理 | 业绩归因+组合优化 | 2小时/月 |

## 下一步计划

1. **接入真实数据源**：Wind/同花顺iFinD API
2. **增强LLM能力**：接入DeepSeek/Kimi进行深度分析
3. **扩展场景**：ESG研究、量化回测、监管报送
4. **企业微信上线**：已集成到企微Bot，可直接@使用

## 写在最后

这7个Skill不是替代研究员/分析师，而是**把80%的重复工作自动化**，让人专注于20%的核心判断。

AI不会取代金融从业者，但会用AI的金融从业者会取代不会用的。

---

*本文代码已开源，欢迎Star和PR。如有问题可在评论区交流。*
