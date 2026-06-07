# Financial AI Skills 🤖💰

> **6大财务场景 + 8大财富场景 + 9大风控场景 AI 智能体，纯 Python 实现，零 API 费用，毫秒级响应**
>
> 发票查验 · 预算管控 · 财报速读 · 税务筹划 · 费用报销 · 资金预测 · 资产配置 · 风险评估

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/yuzhaopeng-up/financial-ai-skills?style=social)](https://github.com/yuzhaopeng-up/financial-ai-skills/stargazers)

---

## 🎬 效果预览

### 发票查验 — 3 秒识别真伪
```bash
$ python financial_cli.py invoice 011001900111 12345678
```

```markdown
## 🧾 发票查验结果

✅ **查验结果: 真票**

| 项目 | 内容 |
|------|------|
| 发票代码 | 011001900111 |
| 发票号码 | 12345678 |
| 开票单位 | 北京 XX 科技有限公司 |
| 金额 | ¥12,580.00 |
| 价税合计 | **¥13,335.66** |

🟢 **合规状态**: 合规 (评分: 100/100)
```

### 预算管控 — 超支预警一目了然
```bash
$ python financial_cli.py budget 市场部
```

| 科目 | 预算 | 已用 | 预计 | 状态 |
|------|------|------|------|------|
| 差旅费 | ¥150,000 | ¥168,000 | ¥185,000 | 🔴 超支预警 |
| 广告费 | ¥200,000 | ¥145,000 | ¥195,000 | 🟡 接近上限 |

### 财报速读 — 关键指标秒提取
```bash
$ python financial_cli.py report 美的集团 2025
```

> **速读结论: 稳健增长，盈利能力强，需关注海外营收占比下降**

| 指标 | 数值 | 同比 |
|------|------|------|
| 营业收入 | ¥3,847 亿 | +8.2% |
| 净利润 | ¥337 亿 | +12.5% |
| ROE | 22.1% | - |

### 资产配置 — 个性化投资方案
```python
from wealth_engine import WealthEngine, WealthFormatter

engine = WealthEngine()
formatter = WealthFormatter()
result = engine.get_allocation("张伟")
print(formatter.format_allocation(result))
```

| 资产类型 | 比例 | 金额 (万) | 推荐产品 |
|------|------|------|------|
| 股票基金 | 40% | 208 | 蓝筹精选、成长混合 |
| 债券基金 | 25% | 130 | 产业债 A、信用债 |
| 货币基金 | 15% | 78 | 余额宝、现金增利 |

### 企业风险评估 — 多维度风险扫描
```python
from risk_engine import RiskEngine, RiskFormatter

engine = RiskEngine()
formatter = RiskFormatter()
result = engine.get_enterprise_risk("比亚迪")
print(formatter.format_enterprise_risk(result))
```

| 风险类型 | 等级 | 说明 |
|------|------|------|
| 市场风险 | 🟡 中 | 新能源汽车市场竞争加剧 |
| 供应链风险 | 🟡 中 | 电池原材料价格波动 |
| 财务风险 | 🟢 低 | 现金流充裕，负债率合理 |

---

## 📦 已发布 Skill

| Skill | 场景数 | 核心能力 | 状态 |
|------|--------|---------|------|
| [financial-intelligence](skills/financial-intelligence/) | 6 | 发票查验、预算管控、财报速读、税务筹划、费用报销、资金预测 | ✅ 已发布 |
| [wealth-management](skills/wealth-management/) | 8 | 资产配置、财务健康、退休规划、保险规划、税务优化、教育金、房产规划、智能投顾 | ✅ 已发布 |
| [risk-compliance](skills/risk-compliance/) | 9 | 企业风险评估、信用评级、反欺诈、合规检查、财务诊断、监管政策、贷后监控、产业链风险、市场情绪 | ✅ 已发布 |
| [wecom-template-card](skills/wecom-template-card/) | 5 | 尽调摘要卡、行情快讯卡、风险预警卡、图文报告卡、交互确认卡 | ✅ 已发布 |
| [customer-marketing](skills/customer-marketing/) | 18 | 客户经理营销话术生成、异议处理、多风格适配、方言话术 | ✅ 已发布 |
| [product-manual-rag](skills/product-manual-rag/) ⭐ | 3+ | 产品手册智能问答（BM25+TF-IDF 双路 RAG）、出处标注、产品自动识别、Hit@1=100% | ✅ P0-2 新发布 |
| [application-material-checker](skills/application-material-checker/) ⭐ | 3 | 进件材料自动核对、完整性+合规性检查、18 条业务规则、4 种报告格式 | ✅ P0-3 新发布 |

---

## 🚀 快速开始

### 安装（30 秒）

```bash
# 克隆仓库
git clone https://github.com/yuzhaopeng-up/financial-ai-skills.git
cd financial-ai-skills

# 复制到 Hermes Agent 目录（可选）
cp -r skills/financial-intelligence ~/.hermes/skills/
cp -r skills/wealth-management ~/.hermes/skills/
cp -r skills/risk-compliance ~/.hermes/skills/
```

> 无需 pip 安装依赖！纯 Python 标准库实现，开箱即用。

### 命令行使用

```bash
cd skills/financial-intelligence/scripts

# 发票查验
python3 financial_cli.py invoice 011001900111 12345678

# 预算管控
python3 financial_cli.py budget 市场部

# 财报速读
python3 financial_cli.py report 美的集团 2025

# 税务筹划
python3 financial_cli.py tax 演示企业

# 费用报销审核
python3 financial_cli.py expense "北京出差机票" 1580

# 资金预测
python3 financial_cli.py cashflow 30
```

### Python API 调用

```python
import sys
sys.path.insert(0, "skills/financial-intelligence")

from engines import InvoiceEngine, BudgetEngine, ReportEngine
from formatters import FinancialFormatter

# 发票查验
engine = InvoiceEngine()
result = engine.verify("011001900111", "12345678")
print(FinancialFormatter.format_invoice(result))

# 预算分析
engine = BudgetEngine()
result = engine.analyze(dept="市场部")
print(FinancialFormatter.format_budget(result))
```

### 财富管理 API

```python
import sys
sys.path.insert(0, "skills/wealth-management")

from wealth_engine import WealthEngine, WealthFormatter

engine = WealthEngine()
formatter = WealthFormatter()

# 资产配置
result = engine.get_allocation("张伟")
print(formatter.format_allocation(result))

# 财务健康诊断
result = engine.get_health("李娜")
print(formatter.format_health(result))

# 退休规划
result = engine.get_retirement("王芳")
print(formatter.format_retirement(result))
```

### 风控合规 API

```python
import sys
sys.path.insert(0, "skills/risk-compliance")

from risk_engine import RiskEngine, RiskFormatter

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

---

## 🏗️ 项目结构

```
financial-ai-skills/
├── skills/
│   ├── financial-intelligence/     # 财务智能体（6 大引擎）
│   │   ├── engines/
│   │   ├── formatters/
│   │   ├── scripts/
│   │   └── SKILL.md
│   ├── wealth-management/          # 财富管理（8 大能力）
│   │   ├── wealth_engine.py
│   │   └── SKILL.md
│   └── risk-compliance/            # 风控合规（9 大能力）
│       ├── risk_engine.py
│       └── SKILL.md
├── scripts/                        # 知识中枢自动化脚本
│   ├── feishu_base_writer.py      # 飞书多维表格写入器
│   ├── github_stars_sync.py       # GitHub Stars同步
│   ├── daily_metrics_cron.py      # 每日指标汇总
│   └── verify_setup.py            # 一键验证配置
├── .github/workflows/              # GitHub Actions
│   ├── sync-stars.yml             # 自动同步Stars
│   └── daily-metrics.yml          # 自动汇总指标
├── docs/                           # 文档
│   ├── QUICK_START.md             # 快速上手指南
│   └── SETUP_CHECKLIST.md         # 配置检查清单
├── LICENSE
└── README.md
```

---

## ✨ 核心能力矩阵

### 财务智能体（financial-intelligence）

| 智能体 | 触发关键词 | 核心能力 | 响应速度 |
|--------|----------|----------|----------|
| 🧾 **发票查验** | 发票、查验、OCR | 信息提取、真伪校验、合规审查 | < 100ms |
| 📊 **预算管控** | 预算、超支、预警 | 执行跟踪、偏差分析、超支预警 | < 50ms |
| 📈 **财报速读** | 财报、年报、速读 | 关键指标提取、趋势分析、风险扫描 | < 50ms |
| 🏛️ **税务筹划** | 税务、节税、合规 | 税负分析、优惠匹配、节税建议 | < 100ms |
| 📝 **费用报销** | 报销、费用、审批 | 智能分类、合规检查、审批建议 | < 50ms |
| 💰 **资金预测** | 现金流、预测、资金 | 现金流建模、缺口预警、调度建议 | < 100ms |

### 财富管理（wealth-management）

| 能力 | 触发关键词 | 核心功能 |
|------|-----------|---------|
| 📈 **资产配置** | 资产配置、投资组合 | 根据风险偏好生成配置方案 |
| 🏥 **财务健康** | 财务健康、体检 | 储蓄率、负债率、流动性诊断 |
| 🏖️ **退休规划** | 退休、养老 | 养老金缺口测算与储蓄计划 |
| 🛡️ **保险规划** | 保险、保障 | 险种推荐与保额测算 |
| 💰 **税务优化** | 个税、节税 | 专项扣除与节税策略 |
| 📚 **教育金** | 教育金、学费 | 教育费用测算与储蓄方案 |
| 🏠 **房产规划** | 购房、房贷 | 购房能力评估与贷款方案 |
| 🤖 **智能投顾** | 智能投顾、AI 理财 | 基于 AI 的资产配置建议 |

### 风控合规（risk-compliance）

| 能力 | 触发关键词 | 核心功能 |
|------|-----------|---------|
| 🏢 **企业风险评估** | 企业风险、评估 | 多维度风险评分与预警 |
| 📊 **信用评级** | 信用评级、征信 | 企业信用等级评定 |
| 🛡️ **反欺诈检测** | 反欺诈、交易异常 | 交易风险识别与处置建议 |
| ✅ **合规检查** | 合规、检查 | 制度执行与整改建议 |
| 🔍 **财务诊断** | 财务诊断、体检 | 财务指标分析与预警 |
| 📋 **监管政策** | 政策、监管 | 最新政策查询与解读 |
| 📈 **贷后监控** | 贷后、监控 | 授信客户动态监控 |
| ⛓️ **产业链风险** | 产业链、供应链 | 上下游风险传导分析 |
| 📉 **市场情绪** | 市场情绪、舆情 | 市场情绪监测与预警 |

---

## 🎯 技术特点

- **⚡ 零 API 费用**：纯规则引擎，无外部 API 调用，适合高频场景
- **🚀 毫秒级响应**：本地计算，平均响应 < 100ms
- **📱 IM 友好输出**：原生 Markdown 表格，完美适配企业微信、飞书、钉钉
- **🔧 模块化设计**：各引擎独立，可单独使用或组合
- **🧪 内置演示数据**：Mock 数据支持，无需配置即可体验全部功能
- **📦 零依赖**：仅使用 Python 标准库，无需 pip install
- **🔄 知识中枢集成**：自动同步 GitHub Stars、文章发布、节点状态到飞书多维表格

---

## 🏗️ 架构设计

```
用户输入 → 关键词匹配 → 引擎计算 → 格式化输出
                ↓
        ┌───────┴───────┐
        ↓               ↓
   规则引擎          Mock 数据
   (确定性)          (演示用)
        ↓               ↓
        └───────┬───────┘
                ↓
        Markdown 格式化
                ↓
        企业微信 / 飞书 / 钉钉
                ↓
        飞书多维表格（知识中枢）
```

---

## 📝 使用示例

### 场景 1：财务培训演示

```python
from engines import InvoiceEngine, FinancialFormatter

# 讲师现场演示发票查验
engine = InvoiceEngine()
result = engine.verify("011001900111", "12345678")
print(FinancialFormatter.format_invoice(result))

# 学员可立即复现，结果 100% 一致
```

### 场景 2：企业微信机器人集成

```python
# 在 Hermes Agent 中配置触发词
# 用户发送："查验发票 xxx"
# Agent 自动调用 InvoiceEngine → 返回 Markdown
```

### 场景 3：批量发票处理

```python
from engines import InvoiceEngine

engine = InvoiceEngine()
invoices = [
    {"code": "011001900111", "no": "12345678"},
    {"code": "011001900111", "no": "87654321"},
]
result = engine.batch_verify(invoices)
print(f"有效: {result['valid_count']}, 异常: {result['invalid_count']}")
```

### 场景 4：客户资产配置咨询

```python
from wealth_engine import WealthEngine, WealthFormatter

engine = WealthEngine()
formatter = WealthFormatter()

# 客户经理快速生成配置方案
result = engine.get_allocation("张伟")
print(formatter.format_allocation(result))
```

### 场景 5：企业风控尽调

```python
from risk_engine import RiskEngine, RiskFormatter

engine = RiskEngine()
formatter = RiskFormatter()

# 贷前风险评估
result = engine.get_enterprise_risk("比亚迪")
print(formatter.format_enterprise_risk(result))
```

---

## 🤝 贡献指南

欢迎提交 PR！请确保：

1. 代码已脱敏，无公司内部信息
2. 新增引擎需附带 `format_xxx` 格式化方法
3. 提交前运行 `python -m py_compile` 检查语法
4. 更新 SKILL.md 文档

### 如何写一个 Hermes Skill？

参考我的技术博客：
- 知乎：[《如何写一个 Hermes Skill：从零到一完整指南》](https://zhuanlan.zhihu.com/p/2046524748184675279)

---

## 📄 许可证

[MIT License](LICENSE) — 自由使用、修改、分发，保留署名。

---

## 🌟 Star History

如果这个项目对你有帮助，请点个 ⭐ Star，让更多人发现它！

[![Star History Chart](https://api.star-history.com/svg?repos=yuzhaopeng-up/financial-ai-skills&type=Date)](https://star-history.com/#yuzhaopeng-up/financial-ai-skills&Date)

---

> **Financial AI Community** | 以真实用户反馈为唯一北极星指标
>
> 💬 有问题？欢迎提 [Issue](https://github.com/yuzhaopeng-up/financial-ai-skills/issues)
