---
name: customer-marketing
description: "Financial AI Skill - 客户经理营销话术实时生成器。输入客户画像和营销目标，AI自动生成电话/微信/拜访话术，支持异议处理预演、方言适配、多风格切换。覆盖零售/对公/理财/私行/信用卡全营销岗位。"
version: 1.1.0
author: Financial AI Community
license: MIT
metadata:
  hermes:
    tags: [marketing, sales,话术,客户经理,营销,对公,零售,理财,私行,信用卡]
    related_skills: [wealth-management, risk-compliance, wecom-template-card]
prerequisites:
  commands: [python3]
---

# 客户经理营销话术实时生成器 v1.0

> 输入客户画像，秒级生成专业营销话术。
> 覆盖电话/微信/拜访全渠道，支持异议处理预演。
>
> ⚡ 零API费用 | 🎯 多风格适配 | 📦 开箱即用

## 一、核心能力

| 能力 | 触发关键词 | 核心功能 |
|------|-----------|---------|
| **话术生成** | 话术、营销、拜访 | 根据客户画像生成电话/微信/面对面话术 |
| **异议处理** | 异议、拒绝、反驳 | 预置常见客户异议及应答话术 |
| **风格切换** | 风格、语气、正式 | 支持正式/亲和/专业/简洁多种风格 |
| **方言适配** | 方言、本地化 | 支持粤语/闽南语/四川话等方言话术（文本版） |
| **场景模板** | 场景、模板 | 开户/贷款/理财/信用卡等预置场景模板 |
| **扩展模板库 (v1.1)** | - | templates/ 目录提供 10 个开场白 + 10 个产品话术 + 10 个异议 + 5 同业案例可直接调用 |

## 二、快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yuzhaopeng-up/financial-ai-skills.git

# 复制Skill到Hermes目录
cp -r financial-ai-skills/skills/customer-marketing ~/.hermes/skills/
```

### CLI工具调用

```bash
cd ~/.hermes/skills/customer-marketing/scripts

# 基础话术生成
python3 marketing_cli.py generate \
  --name "张总" \
  --industry "制造业" \
  --scale "年营收5000万" \
  --goal "推荐供应链金融产品" \
  --channel "face-to-face"

# 带异议处理的话术
python3 marketing_cli.py generate \
  --profile "profiles/enterprise_a.json" \
  --goal "开立对公账户" \
  --style "professional" \
  --with-objections

# 方言版话术
python3 marketing_cli.py generate \
  --name "李姐" \
  --industry "零售" \
  --goal "推荐信用卡" \
  --dialect "cantonese"
```

### Python API调用

```python
import sys
sys.path.insert(0, "~/.hermes/skills/customer-marketing")

from marketing_engine import MarketingEngine, MarketingFormatter

# 初始化
engine = MarketingEngine()
formatter = MarketingFormatter()

# 生成话术
result = engine.generate_script(
    customer_name="张总",
    industry="制造业",
    company_scale="年营收5000万",
    recent_news="刚获得大额订单",
    marketing_goal="推荐供应链金融产品",
    channel="face-to-face",
    style="professional"
)
print(formatter.format_script(result))

# 生成异议处理
objections = engine.generate_objections(
    goal="推荐供应链金融产品",
    industry="制造业"
)
print(formatter.format_objections(objections))
```

## 三、场景模板库

### 3.1 零售客户经理场景

| 编号 | 场景 | 输入示例 | 输出示例 |
|------|------|---------|---------|
| R1 | 信用卡开卡 | 年轻白领，月收入1.5万，经常出差 | 出差权益介绍话术 |
| R2 | 理财推荐 | 退休教师，风险偏好保守，有50万存款 | 稳健型理财推荐话术 |
| R3 | 存款升级 | 活期存款20万，未购买任何理财 | 大额存单升级话术 |

### 3.2 对公客户经理场景

| 编号 | 场景 | 输入示例 | 输出示例 |
|------|------|---------|---------|
| C1 | 开户营销 | 新注册科技公司，注册资本100万 | 对公账户+结算套餐话术 |
| C2 | 贷款推荐 | 制造业企业，年营收5000万，有扩产计划 | 经营贷/设备贷话术 |
| C3 | 供应链金融 | 核心企业供应商，账期3个月 | 应收账款融资话术 |

### 3.3 理财经理场景

| 编号 | 场景 | 输入示例 | 输出示例 |
|------|------|---------|---------|
| W1 | 资产配置 | 高净值客户，可投资资产300万 | 股债配置方案话术 |
| W2 | 基金定投 | 年轻父母，为孩子储备教育金 | 教育金定投话术 |
| W3 | 保险规划 | 家庭支柱，有房贷，无商业保险 | 定期寿险+重疾险话术 |

### 3.4 私行客户经理场景

| 编号 | 场景 | 输入示例 | 输出示例 |
|------|------|---------|---------|
| P1 | 家族信托 | 企业主，资产过亿，有子女教育规划 | 家族信托架构话术 |
| P2 | 税务筹划 | 高管，年收入200万，税负较重 | 个税优化方案话术 |
| P3 | 全球配置 | 有海外资产，需分散风险 | QDII+海外保险话术 |

### 3.5 信用卡专员场景

| 编号 | 场景 | 输入示例 | 输出示例 |
|------|------|---------|---------|
| K1 | 新客开卡 | 大学生，首次申请信用卡 | 学生卡权益介绍话术 |
| K2 | 分期营销 | 大额消费后，账单压力较大 | 账单分期话术 |
| K3 | 权益激活 | 白金卡客户，未使用机场贵宾厅 | 权益提醒+激活话术 |

## 四、话术风格说明

| 风格 | 适用场景 | 特点 |
|------|---------|------|
| **正式** | 对公大客户、首次拜访 | 措辞严谨、专业术语、结构清晰 |
| **亲和** | 零售老客户、熟人推荐 | 语气亲切、拉近距离、自然流畅 |
| **专业** | 理财/私行客户 | 数据支撑、逻辑严密、方案完整 |
| **简洁** | 微信/短信触达 | 要点突出、简短有力、便于阅读 |

## 五、企微端体验

### 5.1 使用流程

```
[企微打开] → [选择岗位：零售/对公/理财/私行/信用卡]
         → [选择场景：开户/贷款/理财/信用卡...]
         → [填写客户信息] → [选择风格/渠道]
         → [AI生成话术] → [复制/发送到企微/保存]
```

### 5.2 示例界面

```
🎯 营销话术实时生成

客户信息：
┌─────────────────────────────────────┐
│ 姓名：张总                            │
│ 行业：制造业                          │
│ 规模：年营收5000万                     │
│ 动态：刚获得大额订单                    │
│ 目标：推荐供应链金融产品                │
│ 渠道：面对面拜访                       │
│ 风格：专业正式                         │
└─────────────────────────────────────┘

💬 AI生成话术：

【开场白】
"张总您好！听说贵公司最近拿下了一笔大额订单，
恭喜啊！这种时候资金周转是不是有点紧张？
我们正好有一款供应链金融产品..."

【产品介绍】
"这款产品专门针对像您这样的制造业企业..."

【异议处理】
如果客户说"利率太高" → "张总，您看这样..."
如果客户说"已有合作银行" → "理解理解，不过..."

[📋 复制话术] [📤 发送到企微] [🔄 重新生成]
```

## 六、技术架构

```
customer-marketing/
├── SKILL.md                          # 本文件
├── marketing_engine.py               # 核心引擎
├── marketing_formatter.py            # 格式化输出
├── templates/
│   ├── opening_templates.json        # 开场白模板
│   ├── product_templates.json        # 产品介绍模板
│   ├── objection_templates.json      # 异议处理模板
│   └── closing_templates.json        # 促成签约模板
└── scripts/
    └── marketing_cli.py              # CLI工具
```

## 七、更新日志

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v1.0.0 | 2026-06-07 | 初始版本，覆盖5大岗位15个场景 |

## 八、贡献指南

欢迎提交PR扩展更多场景模板！

1. Fork 本仓库
2. 在 `templates/` 目录添加新场景模板
3. 更新 `SKILL.md` 场景列表
4. 提交PR

---

*金融AI技能库 | MIT License | 由龙马集群六节点协同开发*

---

## 十、v1.1 扩展模板库（2026-06-07 新增）

`templates/` 目录新增四份开箱即用的话术资产：

### `templates/opening_templates.json` — 10 个场景开场白
| ID | 场景 | 渠道 |
|----|------|------|
| OPEN-001 | 新客户首次电话 | phone |
| OPEN-002 | 存量客户回访 | phone |
| OPEN-003 | 微信首次触达 | wechat |
| OPEN-004 | 节假日问候 | wechat |
| OPEN-005 | 高净值面访 | face-to-face |
| OPEN-006 | 潜在客户陌拜 | phone |
| OPEN-007 | 客户流失预警 | phone |
| OPEN-008 | 小微企业主电话 | phone |
| OPEN-009 | 理财到期续作 | wechat |
| OPEN-010 | 新产品上线推介 | sms |

### `templates/product_templates.json` — 10 个产品介绍话术
覆盖：大额存单、基金定投、信用卡白金卡、小微企业贷、家族信托、重疾险、教育金保险、私行理财、QDII海外基金、黄金积存。每条包含核心价值、目标客户、适配场景、异议预案、Closing hook。

### `templates/objection_templates.json` — 10 个异议应答
| ID | 异议类型 |
|----|---------|
| OBJ-001 | 收益太低/对比同业 |
| OBJ-002 | 我再考虑考虑 |
| OBJ-003 | 资金紧张 |
| OBJ-004 | 怕亏钱/担心风险 |
| OBJ-005 | 我自己投资就好 |
| OBJ-006 | 费用太贵 |
| OBJ-007 | 对你们行不了解 |
| OBJ-008 | 等卖了房子再说 |
| OBJ-009 | 需要家人同意 |
| OBJ-010 | 不要再联系我了 |

### `templates/peer_cases.json` — 5 个同业最佳实践案例
- **招商银行** — 私行 + 智谱AI投顾（NPS+18 points）
- **平安银行** — 知鸟 AI 信贷工厂（审批 3 天 → 10 分钟）
- **工商银行** — 工银智涌反欺诈大模型（日拦截 50 万笔）
- **建设银行** — 惠懂你 310 模式（累计放款 2 万亿）
- **网商银行** — 310模式AI小微贷（5300 万户、不良率 1.5%）

附 cross_cases_insights：4 项共性成功因素 + 4 项常见陷阱。

### Python 调用示例

```python
import json, os
path = os.path.expanduser("~/.hermes/skills/customer-marketing/templates")
opens = json.load(open(f"{path}/opening_templates.json"))
products = json.load(open(f"{path}/product_templates.json"))
objections = json.load(open(f"{path}/objection_templates.json"))
cases = json.load(open(f"{path}/peer_cases.json"))

# 找到匹配的开场白
for s in opens["scenarios"]:
    if "高净值" in str(s.get("best_for")):
        print(s["templates"][0])
        break
```

