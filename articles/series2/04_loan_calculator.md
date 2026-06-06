# 等额本息算法揭秘：信贷审批背后的数学

> 开源代码：https://github.com/yuzhaopeng-up/financial-ai-skills
>
> 从数学原理到Python实现，完整解析信贷审批核心算法。

---

## 一、什么是等额本息？

等额本息是银行贷款最常见的还款方式：

- **每月还款额固定**：便于借款人规划
- **前期利息多本金少**：银行风险可控
- **后期本金多利息少**：借款人负担减轻

**公式**：

```
月供 = 贷款本金 × 月利率 × (1+月利率)^还款月数 / ((1+月利率)^还款月数 - 1)
```

---

## 二、完整Python实现

```python
# 保存为 loan_calculator.py，直接运行

import math
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class LoanResult:
    """贷款计算结果"""
    monthly_payment: float      # 月供
    total_payment: float        # 总还款
    total_interest: float       # 总利息
    payment_schedule: List[Dict] # 还款计划表

class LoanCalculator:
    """贷款计算器"""
    
    def calculate_equal_installment(self, principal, annual_rate, term_months):
        """
        等额本息计算
        
        参数:
            principal: 贷款本金（元）
            annual_rate: 年利率（如0.0435表示4.35%）
            term_months: 还款月数
        """
        monthly_rate = annual_rate / 12
        
        # 月供公式
        if monthly_rate == 0:
            monthly_payment = principal / term_months
        else:
            monthly_payment = principal * monthly_rate * \
                (1 + monthly_rate) ** term_months / \
                ((1 + monthly_rate) ** term_months - 1)
        
        # 生成还款计划表
        schedule = []
        remaining = principal
        total_interest = 0
        
        for month in range(1, term_months + 1):
            interest = remaining * monthly_rate
            principal_paid = monthly_payment - interest
            remaining -= principal_paid
            total_interest += interest
            
            schedule.append({
                'month': month,
                'payment': round(monthly_payment, 2),
                'principal': round(principal_paid, 2),
                'interest': round(interest, 2),
                'remaining': round(max(0, remaining), 2)
            })
        
        return LoanResult(
            monthly_payment=round(monthly_payment, 2),
            total_payment=round(monthly_payment * term_months, 2),
            total_interest=round(total_interest, 2),
            payment_schedule=schedule
        )
    
    def calculate_equal_principal(self, principal, annual_rate, term_months):
        """等额本金计算（对比）"""
        monthly_rate = annual_rate / 12
        monthly_principal = principal / term_months
        
        schedule = []
        total_interest = 0
        remaining = principal
        
        for month in range(1, term_months + 1):
            interest = remaining * monthly_rate
            payment = monthly_principal + interest
            remaining -= monthly_principal
            total_interest += interest
            
            schedule.append({
                'month': month,
                'payment': round(payment, 2),
                'principal': round(monthly_principal, 2),
                'interest': round(interest, 2),
                'remaining': round(max(0, remaining), 2)
            })
        
        first_payment = schedule[0]['payment']
        total_payment = sum(p['payment'] for p in schedule)
        
        return LoanResult(
            monthly_payment=round(first_payment, 2),
            total_payment=round(total_payment, 2),
            total_interest=round(total_interest, 2),
            payment_schedule=schedule
        )


# ====== 实战演示 ======
if __name__ == "__main__":
    calc = LoanCalculator()
    
    # 案例：50万房贷，年利率4.35%，20年
    principal = 500000
    annual_rate = 0.0435
    term_months = 240
    
    print("=" * 70)
    print("🏦 贷款计算器演示")
    print("=" * 70)
    print(f"\n贷款金额: ¥{principal:,.0f}")
    print(f"年利率: {annual_rate * 100:.2f}%")
    print(f"期限: {term_months}个月 ({term_months // 12}年)")
    
    # 等额本息
    result1 = calc.calculate_equal_installment(principal, annual_rate, term_months)
    print(f"\n📊 等额本息:")
    print(f"   月供: ¥{result1.monthly_payment:,.2f}")
    print(f"   总还款: ¥{result1.total_payment:,.2f}")
    print(f"   总利息: ¥{result1.total_interest:,.2f}")
    print(f"   利息占比: {result1.total_interest / result1.total_payment * 100:.1f}%")
    
    # 等额本金
    result2 = calc.calculate_equal_principal(principal, annual_rate, term_months)
    print(f"\n📊 等额本金:")
    print(f"   首月月供: ¥{result2.monthly_payment:,.2f}")
    print(f"   总还款: ¥{result2.total_payment:,.2f}")
    print(f"   总利息: ¥{result2.total_interest:,.2f}")
    print(f"   利息占比: {result2.total_interest / result2.total_payment * 100:.1f}%")
    
    # 对比
    print(f"\n📈 对比:")
    print(f"   等额本息比等额本金多还利息: ¥{result1.total_interest - result2.total_interest:,.2f}")
    print(f"   等额本息首月压力小: ¥{result2.monthly_payment - result1.monthly_payment:,.2f}")
    
    # 打印前6个月还款计划
    print(f"\n📋 等额本息前6个月还款计划:")
    print("-" * 70)
    print(f"{'月份':<6} {'月供':<12} {'本金':<12} {'利息':<12} {'剩余本金':<12}")
    print("-" * 70)
    for p in result1.payment_schedule[:6]:
        print(f"{p['month']:<6} ¥{p['payment']:<10.2f} ¥{p['principal']:<10.2f} ¥{p['interest']:<10.2f} ¥{p['remaining']:<10.2f}")
    
    print("\n" + "=" * 70)
```

---

## 三、运行结果

```bash
$ python loan_calculator.py
======================================================================
🏦 贷款计算器演示
======================================================================

贷款金额: ¥500,000
年利率: 4.35%
期限: 240个月 (20年)

📊 等额本息:
   月供: ¥3,123.42
   总还款: ¥749,620.80
   总利息: ¥249,620.80
   利息占比: 33.3%

📊 等额本金:
   首月月供: ¥3,895.83
   总还款: ¥718,906.25
   总利息: ¥218,906.25
   利息占比: 30.4%

📈 对比:
   等额本息比等额本金多还利息: ¥30,714.55
   等额本息首月压力小: ¥772.41

📋 等额本息前6个月还款计划:
----------------------------------------------------------------------
月份   月供         本金         利息         剩余本金
----------------------------------------------------------------------
1      ¥3,123.42   ¥1,310.92   ¥1,812.50   ¥498,689.08
2      ¥3,123.42   ¥1,315.67   ¥1,807.75   ¥497,373.41
3      ¥3,123.42   ¥1,320.44   ¥1,802.98   ¥496,052.97
4      ¥3,123.42   ¥1,325.22   ¥1,798.19   ¥494,727.75
5      ¥3,123.42   ¥1,330.03   ¥1,793.39   ¥493,397.72
6      ¥3,123.42   ¥1,334.85   ¥1,788.57   ¥492,062.87

======================================================================
```

---

## 四、在信贷审批中的应用

```python
# 计算债务收入比
def calculate_debt_ratio(loan_amount, existing_debts, income):
    calculator = LoanCalculator()
    monthly_payment = calculator.calculate_equal_installment(
        loan_amount, 0.0435, 240
    ).monthly_payment
    
    debt_ratio = (existing_debts + monthly_payment) / income
    return debt_ratio

# 审批决策
if debt_ratio <= 0.5:
    decision = "自动通过"
elif debt_ratio <= 0.7:
    decision = "人工复核"
else:
    decision = "拒绝"
```

---

## 五、开源

完整代码：
```
https://github.com/yuzhaopeng-up/financial-ai-skills/tree/master/skills/credit-approval
```

---

> **关于作者**：于兆鹏，银联工作，服务超500家金融机构。《AI赋能银行数字化转型》作者。
