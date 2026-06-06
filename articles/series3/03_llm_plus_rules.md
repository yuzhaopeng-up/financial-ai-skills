# 大模型+规则引擎：金融场景的最佳搭档

> 方法论：LLM与规则引擎的协同 | 金融场景适用性 | 架构设计

## 纯LLM的问题

金融场景直接用大模型：

**问题1：幻觉**
```
用户: "我的贷款能批多少？"
LLM: "根据您的情况，可以批500万"
实际: 客户信用评分只有45分，最高只能批10万
```

**问题2：不可解释**
```
用户: "为什么拒贷？"
LLM: "综合评估不通过"
监管: "具体原因？"
LLM: "..."
```

**问题3：成本高**
```
每次调用: $0.02
日均查询: 10万次
月成本: $60,000 ≈ 43万人民币
```

**问题4：延迟高**
```
API调用: 2-5秒
金融场景要求: <500ms
```

## 方案：LLM + 规则引擎

### 架构设计

```
┌─────────────────────────────────────┐
│         用户请求                     │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│         路由层                       │
│  ├─ 规则能处理？ → 规则引擎          │
│  └─ 需要理解？   → LLM              │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│         规则引擎层                   │
│  ├─ 硬规则 (100%确定)               │
│  ├─ 评分卡 (量化评估)               │
│  └─ 决策树 (条件判断)               │
├─────────────────────────────────────┤
│         LLM增强层                    │
│  ├─ 意图理解                        │
│  ├─ 文案生成                        │
│  └─ 复杂推理                        │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│         输出层                       │
│  ├─ 结构化数据 (规则输出)            │
│  └─ 自然语言 (LLM增强)               │
└─────────────────────────────────────┘
```

### 协同流程

```python
class HybridSystem:
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.llm = LLMClient()
    
    def process(self, user_input: str, context: dict) -> dict:
        """
        处理用户请求
        """
        # Step 1: 意图识别 (LLM)
        intent = self.llm.classify_intent(user_input)
        
        # Step 2: 规则处理
        if intent in self.rule_engine.supported_intents:
            # 规则能处理，直接走规则
            result = self.rule_engine.process(intent, context)
            
            # LLM增强输出
            if result["needs_explanation"]:
                explanation = self.llm.generate_explanation(result)
                result["explanation"] = explanation
            
            return result
        else:
            # 规则处理不了，走LLM
            return self.llm.process(user_input, context)
    
    def handle_query(self, query: str) -> str:
        """
        处理查询类请求
        """
        # 先查规则库
        rule_result = self.rule_engine.query(query)
        
        if rule_result["confidence"] > 0.9:
            # 规则置信度高，直接返回
            return self.format_response(rule_result)
        else:
            # 规则置信度低，LLM补充
            llm_result = self.llm.query(query)
            return self.merge_results(rule_result, llm_result)
```

## 场景适用性分析

### 适合规则引擎的场景

| 场景 | 规则处理 | LLM增强 | 原因 |
|------|----------|---------|------|
| 信贷审批 | 90% | 10% | 规则明确，可量化 |
| 反洗钱检测 | 95% | 5% | 规则严格，需可解释 |
| 合规检查 | 100% | 0% | 监管要求，必须规则 |
| 利息计算 | 100% | 0% | 数学公式，精确计算 |
| 额度管理 | 85% | 15% | 规则为主，LLM辅助 |

### 适合LLM的场景

| 场景 | 规则处理 | LLM增强 | 原因 |
|------|----------|---------|------|
| 客户咨询 | 30% | 70% | 问题多样，需理解 |
| 报告生成 | 20% | 80% | 自然语言生成 |
| 舆情分析 | 10% | 90% | 文本理解能力强 |
| 智能客服 | 40% | 60% | 对话理解+规则 |
| 营销文案 | 0% | 100% | 纯文本生成 |

## 成本对比

### 纯LLM方案

```
月调用量: 100万次
每次成本: $0.02
月成本: $20,000 ≈ 14.4万人民币
年成本: $240,000 ≈ 173万人民币
```

### 混合方案

```
规则处理: 80% (80万次) → $0
LLM处理: 20% (20万次) → $4,000
月成本: $4,000 ≈ 2.9万人民币
年成本: $48,000 ≈ 34.6万人民币

节省: 173万 - 34.6万 = 138.4万 (80%)
```

## 延迟对比

| 方案 | 平均延迟 | P99延迟 |
|------|----------|---------|
| 纯LLM | 3秒 | 8秒 |
| 纯规则 | 50ms | 100ms |
| 混合方案 | 200ms | 500ms |

## 实施建议

### 第一步：梳理规则（1个月）

```python
# 规则清单
rules = {
    "信贷审批": {
        "硬规则": [
            "黑名单客户 → 拒绝",
            "征信逾期>3次 → 拒绝",
            "DTI>50% → 拒绝"
        ],
        "评分卡": [
            "收入评分 (0-20)",
            "资产评分 (0-20)",
            "信用评分 (0-30)",
            "行为评分 (0-30)"
        ]
    },
    "反洗钱": {
        "硬规则": [
            "单笔>50万 → 上报",
            "日累计>100万 → 预警",
            "敏感国家 → 拦截"
        ]
    }
}
```

### 第二步：建设规则引擎（1-2个月）

```python
class RuleEngine:
    def __init__(self):
        self.rules = []
        self.scorecards = {}
    
    def add_hard_rule(self, condition: str, action: str):
        """添加硬规则"""
        self.rules.append({
            "type": "hard",
            "condition": condition,
            "action": action
        })
    
    def add_scorecard(self, name: str, items: list):
        """添加评分卡"""
        self.scorecards[name] = items
    
    def evaluate(self, data: dict) -> dict:
        """评估数据"""
        result = {"passed": True, "score": 0, "reasons": []}
        
        # 检查硬规则
        for rule in self.rules:
            if eval(rule["condition"], data):
                result["passed"] = False
                result["reasons"].append(rule["action"])
        
        # 计算评分
        for name, items in self.scorecards.items():
            score = sum(item["weight"] * data.get(item["field"], 0) 
                       for item in items)
            result["score"] += score
        
        return result
```

### 第三步：接入LLM（1个月）

```python
class LLMClient:
    def __init__(self, model: str = "gpt-4"):
        self.model = model
    
    def classify_intent(self, text: str) -> str:
        """意图分类"""
        prompt = f"""
        请将以下用户请求分类为：
        - 查询余额
        - 申请贷款
        - 投诉建议
        - 产品咨询
        - 其他
        
        用户请求: {text}
        分类:
        """
        return self.call_llm(prompt)
    
    def generate_explanation(self, result: dict) -> str:
        """生成解释"""
        prompt = f"""
        请用通俗易懂的语言解释以下审批结果：
        
        评分: {result['score']}
        结果: {'通过' if result['passed'] else '拒绝'}
        原因: {', '.join(result['reasons'])}
        
        解释:
        """
        return self.call_llm(prompt)
```

### 第四步：持续优化（持续）

```python
class Optimizer:
    def __init__(self):
        self.metrics = []
    
    def log(self, query: str, intent: str, 
            rule_result: dict, llm_result: dict,
            final_result: dict):
        """记录处理日志"""
        self.metrics.append({
            "query": query,
            "intent": intent,
            "rule_confidence": rule_result.get("confidence"),
            "llm_used": llm_result is not None,
            "correct": self.evaluate_correctness(final_result)
        })
    
    def optimize(self):
        """优化路由策略"""
        # 分析规则命中率
        rule_hit_rate = sum(1 for m in self.metrics 
                           if not m["llm_used"]) / len(self.metrics)
        
        # 分析准确率
        accuracy = sum(1 for m in self.metrics 
                      if m["correct"]) / len(self.metrics)
        
        print(f"规则命中率: {rule_hit_rate:.1%}")
        print(f"整体准确率: {accuracy:.1%}")
        
        # 建议调整阈值
        if rule_hit_rate < 0.7:
            print("建议: 扩充规则库，降低LLM依赖")
        elif accuracy < 0.95:
            print("建议: 优化规则质量，提高准确率")
```

---

**#大模型 #规则引擎 #金融AI #架构设计 #成本优化**
