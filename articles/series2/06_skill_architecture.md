# 银行智能体架构：7个Skill如何协同工作

> 实战代码：基于 `financial-ai-skills` 项目 | 架构设计 | Skill协同 | 数据流

## 单体架构 vs 微服务架构

银行系统常见的两种架构：

```
单体架构:                    微服务架构:
┌─────────────┐            ┌─────┐ ┌─────┐ ┌─────┐
│  核心系统    │            │信贷 │ │风控 │ │营销 │
│  ├─信贷     │            │服务 │ │服务 │ │服务 │
│  ├─风控     │            └─────┘ └─────┘ └─────┘
│  ├─营销     │               ↑       ↑       ↑
│  └─运营     │            ┌─────────────────────┐
└─────────────┘            │      API网关         │
                           └─────────────────────┘
```

**问题**：单体太臃肿，微服务太复杂。

## 方案：Skill化架构

我设计的架构：

```
┌─────────────────────────────────────────┐
│           应用层 (业务系统)               │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │ 信贷系统 │ │ 风控系统 │ │ 营销系统 │  │
│  └────┬────┘ └────┬────┘ └────┬────┘  │
└───────┼───────────┼───────────┼────────┘
        │           │           │
        └───────────┼───────────┘
                    ↓
┌─────────────────────────────────────────┐
│           Skill层 (7个核心模块)           │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐      │
│  │财务 │ │风控 │ │尽调 │ │营销 │      │
│  │智能 │ │合规 │ │    │ │    │      │
│  └─────┘ └─────┘ └─────┘ └─────┘      │
│  ┌─────┐ ┌─────┐ ┌─────┐              │
│  │信贷 │ │运营 │ │财富 │              │
│  │审批 │ │自动化│ │管理 │              │
│  └─────┘ └─────┘ └─────┘              │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
┌───────────┐ ┌───────────┐ ┌───────────┐
│  数据层    │ │  规则引擎  │ │  LLM层    │
│  CSV/SQL  │ │  评分卡   │ │ (可选)    │
└───────────┘ └───────────┘ └───────────┘
```

## Skill协同示例

```python
from financial_intelligence import CashflowForecaster
from risk_compliance import FraudDetector
from credit_approval import CreditScorer

# 场景：企业申请贷款
# 需要多个Skill协同

class LoanApprovalWorkflow:
    def __init__(self):
        self.cashflow = CashflowForecaster()
        self.fraud = FraudDetector()
        self.credit = CreditScorer()
    
    def process(self, application: dict) -> dict:
        """处理贷款申请"""
        results = {}
        
        # Step 1: 财务分析
        print("🔍 Step 1: 财务分析")
        cashflow_result = self.cashflow.forecast(
            application["financial_data"]
        )
        results["cashflow"] = cashflow_result
        
        # Step 2: 反欺诈检测
        print("🔍 Step 2: 反欺诈检测")
        fraud_result = self.fraud.check(
            application["transaction_history"]
        )
        results["fraud"] = fraud_result
        
        # Step 3: 信用评分
        print("🔍 Step 3: 信用评分")
        credit_result = self.credit.score(
            application["credit_data"]
        )
        results["credit"] = credit_result
        
        # Step 4: 综合决策
        print("🔍 Step 4: 综合决策")
        decision = self.make_decision(results)
        
        return {
            "application_id": application["id"],
            "results": results,
            "decision": decision,
            "timestamp": datetime.now().isoformat()
        }
    
    def make_decision(self, results: dict) -> dict:
        """综合决策"""
        score = 0
        reasons = []
        
        # 现金流评分 (权重30%)
        cf_score = results["cashflow"]["health_score"]
        score += cf_score * 0.3
        
        # 反欺诈评分 (权重30%)
        fraud_score = 100 - results["fraud"]["risk_score"]
        score += fraud_score * 0.3
        
        # 信用评分 (权重40%)
        credit_score = results["credit"]["score"]
        score += credit_score * 0.4
        
        # 决策
        if score >= 80:
            decision = "APPROVE"
            suggestion = "建议审批"
        elif score >= 60:
            decision = "REVIEW"
            suggestion = "建议人工复核"
        else:
            decision = "REJECT"
            suggestion = "建议拒绝"
        
        return {
            "score": score,
            "decision": decision,
            "suggestion": suggestion,
            "reasons": reasons
        }

# 使用
workflow = LoanApprovalWorkflow()
result = workflow.process({
    "id": "APP001",
    "financial_data": {...},
    "transaction_history": {...},
    "credit_data": {...}
})

print(f"决策: {result['decision']['decision']}")
print(f"评分: {result['decision']['score']}")
print(f"建议: {result['decision']['suggestion']}")
```

## 数据流设计

```python
# Skill间的数据流
class DataFlow:
    """数据流管理器"""
    
    def __init__(self):
        self.pipeline = []
    
    def add_step(self, skill, input_mapping, output_mapping):
        """添加处理步骤"""
        self.pipeline.append({
            "skill": skill,
            "input_mapping": input_mapping,
            "output_mapping": output_mapping
        })
    
    def execute(self, initial_data: dict) -> dict:
        """执行数据流"""
        data = initial_data.copy()
        
        for step in self.pipeline:
            skill = step["skill"]
            
            # 映射输入
            inputs = {}
            for key, path in step["input_mapping"].items():
                inputs[key] = self._get_value(data, path)
            
            # 执行Skill
            result = skill.process(**inputs)
            
            # 映射输出
            for key, path in step["output_mapping"].items():
                self._set_value(data, path, result[key])
        
        return data
    
    def _get_value(self, data: dict, path: str):
        """获取嵌套值"""
        keys = path.split(".")
        value = data
        for key in keys:
            value = value.get(key, {})
        return value
    
    def _set_value(self, data: dict, path: str, value):
        """设置嵌套值"""
        keys = path.split(".")
        target = data
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        target[keys[-1]] = value

# 定义贷款审批数据流
flow = DataFlow()

# Step 1: 财务分析
flow.add_step(
    skill=CashflowForecaster(),
    input_mapping={"data": "application.financial_data"},
    output_mapping={"health_score": "results.cashflow.health_score"}
)

# Step 2: 反欺诈
flow.add_step(
    skill=FraudDetector(),
    input_mapping={"transactions": "application.transaction_history"},
    output_mapping={"risk_score": "results.fraud.risk_score"}
)

# Step 3: 信用评分
flow.add_step(
    skill=CreditScorer(),
    input_mapping={"credit_data": "application.credit_data"},
    output_mapping={"score": "results.credit.score"}
)

# 执行
result = flow.execute({
    "application": {...}
})
```

## 配置化Skill加载

```python
# skill_config.yaml
skills:
  financial-intelligence:
    enabled: true
    version: "1.0"
    config:
      forecast_horizon: 30
      
  risk-compliance:
    enabled: true
    version: "1.1"
    config:
      min_transaction_amount: 100000
      
  credit-approval:
    enabled: true
    version: "1.0"
    config:
      min_score: 75
      max_auto_amount: 500000

# 加载配置
import yaml

class SkillManager:
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        self.skills = {}
    
    def load_skills(self):
        """加载所有Skill"""
        for name, cfg in self.config["skills"].items():
            if cfg["enabled"]:
                self.skills[name] = self._load_skill(name, cfg)
    
    def _load_skill(self, name: str, cfg: dict):
        """加载单个Skill"""
        module = __import__(f"skills.{name.replace('-', '_')}")
        skill_class = getattr(module, name.replace("-", " ").title().replace(" ", ""))
        return skill_class(**cfg.get("config", {}))
    
    def get_skill(self, name: str):
        """获取Skill"""
        return self.skills.get(name)

# 使用
manager = SkillManager("skill_config.yaml")
manager.load_skills()

credit_skill = manager.get_skill("credit-approval")
result = credit_skill.score(application_data)
```

## 监控与日志

```python
class SkillMonitor:
    """Skill监控器"""
    
    def __init__(self):
        self.metrics = {}
    
    def record(self, skill_name: str, operation: str, duration: float, success: bool):
        """记录指标"""
        key = f"{skill_name}.{operation}"
        
        if key not in self.metrics:
            self.metrics[key] = {
                "count": 0,
                "total_duration": 0,
                "success_count": 0,
                "fail_count": 0
            }
        
        self.metrics[key]["count"] += 1
        self.metrics[key]["total_duration"] += duration
        
        if success:
            self.metrics[key]["success_count"] += 1
        else:
            self.metrics[key]["fail_count"] += 1
    
    def get_report(self) -> dict:
        """生成监控报告"""
        report = {}
        
        for key, metrics in self.metrics.items():
            report[key] = {
                "total_calls": metrics["count"],
                "avg_duration": metrics["total_duration"] / metrics["count"],
                "success_rate": metrics["success_count"] / metrics["count"] * 100,
                "error_rate": metrics["fail_count"] / metrics["count"] * 100
            }
        
        return report

# 装饰器自动记录
import time
import functools

def monitored(skill_name: str, operation: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                monitor.record(skill_name, operation, time.time() - start, True)
                return result
            except Exception as e:
                monitor.record(skill_name, operation, time.time() - start, False)
                raise
        return wrapper
    return decorator

# 使用
class CreditScorer:
    @monitored("credit-approval", "score")
    def score(self, data: dict) -> dict:
        # 评分逻辑
        pass
```

---

**完整代码**：https://github.com/yuzhaopeng-up/financial-ai-skills

**#架构设计 #Skill协同 #数据流 #银行系统 #微服务**
