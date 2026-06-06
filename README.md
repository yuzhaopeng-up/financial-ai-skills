# Financial AI Skills 🤖💰

> **6大财务场景AI智能体，纯Python实现，零API费用，毫秒级响应**
>
> 发票查验 · 预算管控 · 财报速读 · 税务筹划 · 费用报销 · 资金预测

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/yuzhaopeng-up/financial-ai-skills?style=social)](https://github.com/yuzhaopeng-up/financial-ai-skills/stargazers)

---

## 🎬 效果预览

### 发票查验 — 3秒识别真伪
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
| 开票单位 | 北京XX科技有限公司 |
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
| 营业收入 | ¥3,847亿 | +8.2% |
| 净利润 | ¥337亿 | +12.5% |
| ROE | 22.1% | - |

---

## 🚀 快速开始

### 安装（30秒）

```bash
# 克隆仓库
git clone https://github.com/yuzhaopeng-up/financial-ai-skills.git
cd financial-ai-skills

# 复制到 Hermes Agent 目录（可选）
cp -r skills/financial-intelligence ~/.hermes/skills/
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

---

## 📦 项目结构

```
financial-ai-skills/
├── skills/
│   └── financial-intelligence/
│       ├── engines/              # 6大核心引擎
│       │   ├── invoice_engine.py    # 发票查验
│       │   ├── budget_engine.py     # 预算管控
│       │   ├── report_engine.py     # 财报速读
│       │   ├── tax_engine.py        # 税务筹划
│       │   ├── expense_engine.py    # 费用报销
│       │   └── cashflow_engine.py   # 资金预测
│       ├── formatters/
│       │   └── financial_formatter.py  # Markdown 格式化
│       ├── scripts/
│       │   └── financial_cli.py        # CLI 工具
│       └── SKILL.md                 # 详细文档
├── LICENSE
└── README.md
```

---

## ✨ 六大能力详解

| 智能体 | 触发场景 | 核心能力 | 响应速度 |
|--------|----------|----------|----------|
| 🧾 **发票查验** | 收到发票需要验真 | 信息提取、真伪校验、合规审查 | < 100ms |
| 📊 **预算管控** | 季度预算复盘 | 执行跟踪、偏差分析、超支预警 | < 50ms |
| 📈 **财报速读** | 投资前快速了解公司 | 关键指标提取、趋势分析、风险扫描 | < 50ms |
| 🏛️ **税务筹划** | 年度税务优化 | 税负分析、优惠匹配、节税建议 | < 100ms |
| 📝 **费用报销** | 员工提交报销单 | 智能分类、合规检查、审批建议 | < 50ms |
| 💰 **资金预测** | 现金流紧张期 | 现金流建模、缺口预警、调度建议 | < 100ms |

---

## 🎯 技术特点

- **⚡ 零API费用**：纯规则引擎，无外部API调用，适合高频财务场景
- **🚀 毫秒级响应**：本地计算，平均响应 < 100ms
- **📱 IM 友好输出**：原生 Markdown 表格，完美适配企业微信、飞书、钉钉
- **🔧 模块化设计**：6大引擎独立，可单独使用或组合
- **🧪 内置演示数据**：Mock 数据支持，无需配置即可体验全部功能
- **📦 零依赖**：仅使用 Python 标准库，无需 pip install

---

## 🏗️ 架构设计

```
用户输入 → 关键词匹配 → 引擎计算 → 格式化输出
                ↓
        ┌───────┴───────┐
        ↓               ↓
   规则引擎          Mock数据
   (确定性)          (演示用)
        ↓               ↓
        └───────┬───────┘
                ↓
        Markdown 格式化
                ↓
        企业微信/飞书/钉钉
```

---

## 📝 使用示例

### 场景1：财务培训演示

```python
from engines import InvoiceEngine, FinancialFormatter

# 讲师现场演示发票查验
engine = InvoiceEngine()
result = engine.verify("011001900111", "12345678")
print(FinancialFormatter.format_invoice(result))

# 学员可立即复现，结果100%一致
```

### 场景2：企业微信机器人集成

```python
# 在 Hermes Agent 中配置触发词
# 用户发送："查验发票 011001900111 12345678"
# Agent 自动调用 InvoiceEngine → 返回 Markdown
```

### 场景3：批量发票处理

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

---

## 🤝 贡献指南

欢迎提交 PR！请确保：

1. 代码已脱敏，无公司内部信息
2. 新增引擎需附带 `format_xxx` 格式化方法
3. 提交前运行 `python -m py_compile` 检查语法
4. 更新 SKILL.md 文档

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
