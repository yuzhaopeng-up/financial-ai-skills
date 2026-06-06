---
name: wealth-management
description: "Financial AI Skill - 财富管理智能体。提供资产配置、财务健康诊断、退休规划、保险规划、税务优化、教育金规划、房产规划、智能投顾等8大能力。基于规则引擎的轻量级财富管理系统，零API费用。"
version: 1.0.0
author: Financial AI Community
license: MIT
metadata:
  hermes:
    tags: [wealth, finance, investment, allocation, retirement, insurance, tax, estate]
    related_skills: [financial-intelligence, risk-compliance]
prerequisites:
  commands: [python3]
---

# 财富管理智能体 v1.0

> 基于规则引擎的轻量级财富管理系统，8大场景全覆盖。
>
> ⚡ 零API费用 | 🚀 毫秒级响应 | 📦 开箱即用

## 一、8大财富管理能力

| 能力 | 触发关键词 | 核心功能 |
|------|-----------|---------|
| **资产配置** | 资产配置、投资组合 | 根据风险偏好生成配置方案 |
| **财务健康** | 财务健康、体检 | 储蓄率、负债率、流动性诊断 |
| **退休规划** | 退休、养老 | 养老金缺口测算与储蓄计划 |
| **保险规划** | 保险、保障 | 险种推荐与保额测算 |
| **税务优化** | 个税、节税 | 专项扣除与节税策略 |
| **教育金** | 教育金、学费 | 教育费用测算与储蓄方案 |
| **房产规划** | 购房、房贷 | 购房能力评估与贷款方案 |
| **智能投顾** | 智能投顾、AI理财 | 基于AI的资产配置建议 |

## 二、快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yuzhaopeng-up/financial-ai-skills.git

# 复制Skill到Hermes目录
cp -r financial-ai-skills/skills/wealth-management ~/.hermes/skills/
```

### Python API 调用

```python
import sys
sys.path.insert(0, "~/.hermes/skills/wealth-management")

from wealth_engine import WealthEngine, WealthFormatter

# 初始化
engine = WealthEngine()
formatter = WealthFormatter()

# 查看客户列表
result = engine.list_customers()
print(formatter.format_customer_list(result))

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

## 三、演示数据

内置5个典型客户画像：

| 客户 | 年龄 | 职业 | 资产(万) | 风险偏好 |
|------|------|------|---------|----------|
| 张伟 | 38 | 企业高管 | 520 | 激进型 |
| 李娜 | 32 | 医生 | 180 | 稳健型 |
| 王芳 | 45 | 私营业主 | 850 | 平衡型 |
| 刘洋 | 28 | 程序员 | 35 | 激进型 |
| 陈明 | 52 | 企业主 | 1200 | 保守型 |

## 四、项目结构

```
wealth-management/
├── wealth_engine.py      # 核心引擎 + 格式化器
└── SKILL.md              # 本文件
```

## 五、技术特点

- **纯Python实现**：无外部API依赖，零调用成本
- **规则引擎**：100%可复现结果，适合合规场景
- **Markdown输出**：适配IM平台（企业微信、飞书、钉钉等）
- **可扩展**：基于类结构，易于添加新客户和新功能

## 六、版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-06-06 | 初始发布，8大财富管理能力完整实现 |

## 许可证

[MIT License](../../LICENSE)

---

*Financial AI Community | 以真实用户反馈为唯一北极星指标*
