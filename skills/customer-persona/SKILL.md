---
name: customer-persona
description: "Financial AI Skill - 360 度客户画像生成器。输入客户基本信息（自然语言或结构化），输出 RFM 标签、生命周期阶段、推荐产品清单（25 个银行产品）、触达渠道建议、营销话术钩子和下一步最佳动作。覆盖零售/财富/信贷/保险全产品线，零外部依赖。"
version: 1.0.0
author: ArkClaw (Financial AI Community)
license: MIT
metadata:
  hermes:
    tags: [customer-360, rfm, lifecycle, recommendation, marketing, persona, segmentation]
    related_skills: [customer-marketing, wealth-management, financial-intelligence]
    coverage:
      products: 25
      lifecycle_stages: 5
      rfm_segments: 8
      channels: 5
prerequisites:
  commands: [python3]
---

# 客户画像生成器 v1.0

> 输入自然语言客户描述 → 秒级输出 360° 画像 + 营销策略 + 话术钩子
>
> ⚡ 零外部依赖 | 🎯 25 个产品匹配 | 📊 8 类 RFM 分层 | 💬 12 套话术模板

## 一、核心能力

| 能力 | 说明 |
|------|------|
| **自然语言解析** | 从 `客户画像 张伟 35岁 月收入2万 已婚 有房贷 风险偏好稳健` 抽取 14 个字段 |
| **RFM 客户分层** | 8 类（重要价值/重要发展/重要保持/重要挽留/一般价值/一般发展/一般保持/流失） |
| **生命周期识别** | 5 阶段（潜在/新客户/成长/成熟/流失） |
| **产品推荐引擎** | 25 个产品（理财/基金/保险/信贷/财富）多维评分 |
| **触达渠道建议** | 5 类渠道（电话/微信/短信/APP推送/线下面访）按年龄+客群优先级排序 |
| **营销话术钩子** | 12 套模板按生命周期+产品类型匹配 |
| **风险提示** | 自动识别风险偏好与推荐产品的错配 |
| **下一步动作** | NBA（Next Best Action）智能建议 |

## 二、快速开始

### 安装

```bash
git clone https://github.com/yuzhaopeng-up/financial-ai-skills.git
cp -r financial-ai-skills/skills/customer-persona ~/.hermes/skills/
```

### CLI 调用

```bash
cd ~/.hermes/skills/customer-persona

# 1. 自然语言生成（最常用）
python3 scripts/persona_cli.py generate "客户画像 张伟 35岁 月收入2万 已婚 有房贷 风险偏好稳健"

# 2. 多种输出格式
python3 scripts/persona_cli.py generate "张伟 35岁 月收入2万 已婚 风险偏好稳健" --format md
python3 scripts/persona_cli.py generate "张伟 35岁 月收入2万 已婚 风险偏好稳健" --format card
python3 scripts/persona_cli.py generate "张伟 35岁 月收入2万 已婚 风险偏好稳健" --format json

# 3. 仅解析字段（调试）
python3 scripts/persona_cli.py parse "李华 女 42岁 月收入5万 已婚 2个孩子 高净值 风险偏好平衡"

# 4. 批量画像
python3 scripts/persona_cli.py batch customers.json
```

### Python API

```python
from customer_persona import PersonaEngine, PersonaFormatter

eng = PersonaEngine()

# 自然语言输入
p = eng.generate("客户画像 张伟 35岁 月收入2万 已婚 有房贷 风险偏好稳健")

# 结构化输入
p = eng.generate({
    "name": "李华",
    "age": 42,
    "monthly_income": 50000,
    "marital_status": "married",
    "has_children": True,
    "children_count": 2,
    "aum": 6_000_000,
    "risk_preference": "balanced",
    "products_held": ["大额存单"],
})

print(p.rfm_segment)        # "重要价值客户"
print(p.life_cycle_stage)   # "成长客户"
for product in p.recommended_products:
    print(f"{product['name']}  匹配度 {product['score']}")

print(PersonaFormatter.to_text(p))  # 完整 360 画像报告
```

## 三、输入支持的字段

### 自然语言示例（推荐）

```
张伟 35岁 月收入2万 已婚 有房贷 风险偏好稳健
李华 女 42岁 月收入5万 已婚 2个孩子 高净值 风险偏好平衡 北京
王小明 28岁 月收入1.5万 单身 风险偏好进取
陈大爷 65岁 退休 月收入8000 丧偶 风险偏好保守
```

### 结构化字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | str | 客户姓名 |
| `age` | int | 年龄 |
| `gender` | str | male/female |
| `monthly_income` | float | 月收入（元） |
| `aum` | float | 资产管理规模（元） |
| `marital_status` | str | single/married/divorced/widowed |
| `has_mortgage` | bool | 有无房贷 |
| `has_car_loan` | bool | 有无车贷 |
| `has_children` | bool | 有无子女 |
| `children_count` | int | 子女数量 |
| `risk_preference` | str | conservative/steady/balanced/aggressive |
| `occupation` | str | 职业 |
| `last_transaction_days` | int | 最近一次交易距今天数 |
| `transaction_frequency_year` | int | 年交易次数 |
| `products_held` | list | 已持有产品名 |
| `city` | str | 所在城市 |

## 四、输出示例

```
============================================================
📊 客户 360° 画像报告 - 张伟
============================================================

👤 基础信息:
   姓名/年龄: 张伟 / 35 岁
   月收入: 20,000 元 (middle_high)
   家庭: 有房贷 无子女
   风险偏好: steady

🎯 客户分层: 重要价值客户
   RFM 评分: R=5/5  F=4/5  M=4/5  (综合 13/15)
   生命周期: 潜在客户

🏷️  价值标签: 中高收入 / 稳健型 / 有房贷 / 已婚 / 千禧一代

💰 推荐产品 (Top 6):
   1. [insurance/conservative] 重疾险  (匹配度 50)
   2. [loan/balanced] 住房按揭贷款  (匹配度 40)
   3. [deposit/conservative] 灵活宝类活期理财  (匹配度 35)
   ...

📞 触达渠道:
   • APP推送  最佳时段: 18:00-20:00
     原因: 有房贷客户，APP推送利率优惠敏感度最高
   • 微信  最佳时段: 10:00-11:30;19:00-21:00
   • 电话  最佳时段: 10:00-11:30;14:00-16:30

💬 营销话术钩子:
   [1] (first_touch)
       "张伟您好，我是您的专属客户经理，我们近期有个非常适合您的金融方案..."

🎬 下一步最佳动作:
   👉 首次触达：介绍万能账户概念，获取客户同意后续联系
============================================================
```

## 五、25 个支持产品

| 类型 | 产品 |
|------|------|
| **存款** | 灵活宝、大额存单、结构性存款 |
| **基金** | 固收+、指数定投、混合偏股、纯债、股票型、货币、海外基金 |
| **保险** | 教育金、养老目标、百万医疗、重疾险、终身寿、年金保险 |
| **信贷** | 信用卡白金卡、消费贷、住房按揭、抵押经营贷、小微企业贷 |
| **财富** | 家族信托、私人银行服务 |
| **其他** | 黄金积存、券商收益凭证 |

## 六、与其他 Skill 协同

```
客户上传基本信息（OCR/CRM）
      │
      ▼
customer-persona  ← 360°画像 + 产品推荐 + 渠道
      │
      ├──▶ customer-marketing  → 生成对应话术
      ├──▶ wealth-management   → 资产配置建议
      ├──▶ product-manual-rag  → 介绍推荐产品详情
      └──▶ application-material-checker → 材料预核（提示需提交材料）
```

## 七、性能与质量

| 指标 | 数值 |
|------|------|
| 单元测试 | 19/19 通过 |
| 单条画像耗时 | < 3 ms |
| 外部依赖 | 零 |
| 产品库 | 25 个 |
| 自然语言字段覆盖 | 14 个 |
| RFM 分层 | 8 类 |
| 生命周期 | 5 阶段 |
| 话术钩子 | 12 模板 × 7 场景 |
| 报告格式 | text / json / markdown / wecom_card |

## 八、扩展指南

### 新增产品

编辑 `persona_engine.py::PRODUCT_CATALOG`，按下面结构添加：

```python
{
    "name": "新产品名",
    "type": "deposit|fund|insurance|loan|credit|wealth|investment",
    "risk": "conservative|steady|balanced|aggressive",
    "min_age": 18, "max_age": 999,
    "tags": ["safe", "long_term", "has_children"],
}
```

### 新增话术钩子场景

在 `HOOK_TEMPLATES` 字典中追加 `"your_scenario": [...]`，并在 `_generate_hooks` 中关联触发条件。

### 新增字段抽取

修改 `parse_natural_language` 添加正则匹配规则。

## 九、版本

- **1.0.0** (2026-06-07) 首版：14 个解析字段、25 个产品、8 类 RFM、5 阶段生命周期、12 套话术、19/19 测试通过
