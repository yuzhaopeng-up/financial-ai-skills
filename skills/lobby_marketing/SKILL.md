# Lobby Marketing Skill（厅堂精准营销）

## 1. 技能概述

**技能名称**：厅堂精准营销（Lobby Marketing）  
**技能路径**：`skills/lobby_marketing/`  
**核心功能**：基于客户画像（年龄/职业/资产级别/历史产品/等候时间），实时生成厅堂营销话术推荐、产品匹配、促成时机判断及异议处理预案。  
**目标用户**：银行网点柜员、客户经理、大堂经理  
**渠道集成**：企微消息卡片（wecom_integration.py）、CLI脚本（scripts/lobby_mkt_cli.py）

---

## 2. 核心能力

### 2.1 客户画像解析
输入字段：
- `年龄`（整数）
- `职业`（企业主/上班族/退休/自由职业等）
- `资产级别`（20万以下/20-100万/100-500万/500万以上）
- `历史产品`（定期/理财/基金/保险/活期/无）
- `等候时间`（分钟）
- `风险偏好`（保守型/稳健型/积极型，可由系统根据历史产品推断）

### 2.2 产品匹配规则

| 维度 | 规则 |
|------|------|
| 年龄 | ≤30岁：推荐灵活储蓄+基金定投；31-50岁：综合理财+保险；≥51岁：定期+保险+稳健理财 |
| 资产级别 | <20万：储蓄型；20-100万：稳健理财+保险；100-500万：综合配置；>500万：私行级定制 |
| 风险偏好 | 保守型：大额存单/定期/保险；稳健型：固收理财+基金；积极型：混合基金+权益类 |
| 历史产品 | 已持定期→推荐理财/保险；已持理财→推荐基金/定期；无产品→推荐储蓄+简易理财 |

### 2.3 话术模板结构

```
[阶段1：开场白] → 寒暄+认同+切入
[阶段2：需求挖掘] → SPIN四问（现状/问题/影响/解决）
[阶段3：产品呈现] → FAB法则（特征/优势/利益）
[阶段4：异议处理] → 5类常见异议应对
[阶段5：促成信号] → 促成时机判断+闭口话术
```

### 2.4 促成时机判断

触发条件（满足任一）：
- 等候时间 ≥ 10 分钟
- 客户主动询问产品
- 客户表现出兴趣（点头/停留/记录）
- 资产级别 ≥ 100万

---

## 3. 输出格式

### JSON输出
```json
{
  "customer_profile": {...},
  "recommended_products": [
    {"product": "xxx", "type": "存款/理财/保险/基金", "match_score": 0.85, "reason": "..."}
  ],
  "script": {
    "opening": "...",
    "need_discovery": "...",
    "product_presentation": "...",
    "objection_handling": [...],
    "closing": "..."
  },
  "timing_signal": {"ready": true, "confidence": 0.8, "reasons": [...]},
  "wecom_card": {...}
}
```

---

## 4. 文件结构

```
skills/lobby_marketing/
├── SKILL.md                          # 本文档
├── lobby_mkt_engine.py               # 核心引擎 LobbyMarketingEngine
├── __init__.py                       # 导出 LobbyMarketingEngine
├── scripts/
│   └── lobby_mkt_cli.py              # CLI入口
└── wecom_integration.py              # 企微卡片集成
```

---

## 5. 使用方式

### CLI
```bash
python3 scripts/lobby_mkt_cli.py generate "厅堂营销 40岁企业主 等候15分钟 资产200万 持有定期"
python3 scripts/lobby_mkt_cli.py generate "厅堂营销 55岁退休 等候5分钟 资产50万 持有定期"
```

### Python API
```python
from lobby_marketing import LobbyMarketingEngine

engine = LobbyMarketingEngine()
result = engine.generate(
    age=40,
    occupation="企业主",
    waiting_minutes=15,
    asset_level="100-500万",
    history_products=["定期"],
)
print(result["script"]["opening"])
```

---

## 6. 测试用例

| 场景 | 预期产品 | 预期话术方向 |
|------|----------|-------------|
| 40岁企业主/200万/等15分钟/持定期 | 理财+保险+基金 | 资产保值+传承+流动性 |
| 55岁退休/50万/等5分钟/持定期 | 大额存单+保险 | 安全性+利息+传承 |
| 28岁上班族/30万/等20分钟/无产品 | 基金定投+灵活储蓄 | 强制储蓄+长期收益 |
| 50岁高管/800万/等5分钟/持理财 | 私募/保险+综合配置 | 资产隔离+传承+节税 |

---

## 7. 版本历史

- v1.0.0（2026-06-10）：初版发布，支持基础画像+产品匹配+话术生成+异议处理+企微卡片
