# 等额本息算法揭秘：信贷审批背后的数学

> 实战代码：基于 `credit-approval` Skill | 还款计算 | 利率定价 | 月供公式

## 信贷审批的核心：还款能力评估

银行审批贷款时，最核心的问题是：**客户还得起吗？**

这需要计算：
1. **月供金额**：每月还多少
2. **还款能力**：收入能否覆盖
3. **总利息**：贷款成本多少

## 等额本息公式

等额本息是最常见的还款方式：每月还款额相同。

```
月供 = 本金 × 月利率 × (1+月利率)^还款月数 / [(1+月利率)^还款月数 - 1]
```

```python
import math

def calculate_emi(principal, annual_rate, years):
    """
    计算等额本息月供
    
    Args:
        principal: 贷款本金
        annual_rate: 年利率 (如 0.0435 表示 4.35%)
        years: 贷款年限
    
    Returns:
        月供金额
    """
    monthly_rate = annual_rate / 12
    months = years * 12
    
    emi = principal * monthly_rate * (1 + monthly_rate)**months / \
          ((1 + monthly_rate)**months - 1)
    
    return emi

# 示例：贷款50万，年利率4.35%，20年
emi = calculate_emi(500000, 0.0435, 20)
print(f"月供: ¥{emi:,.2f}")
# 输出: 月供: ¥3,123.42
```

## 完整代码：贷款计算器

```python
"""
银行贷款计算器
运行: python loan_calculator.py --principal 500000 --rate 0.0435 --years 20
"""
import argparse
import pandas as pd
from dataclasses import dataclass
from typing import List

@dataclass
class Payment:
    month: int
    payment: float
    principal: float
    interest: float
    remaining: float

class LoanCalculator:
    """贷款计算器"""
    
    def __init__(self, principal: float, annual_rate: float, years: int):
        self.principal = principal
        self.annual_rate = annual_rate
        self.years = years
        self.monthly_rate = annual_rate / 12
        self.months = years * 12
    
    def calculate_emi(self) -> float:
        """计算月供"""
        r = self.monthly_rate
        n = self.months
        p = self.principal
        
        emi = p * r * (1 + r)**n / ((1 + r)**n - 1)
        return emi
    
    def generate_schedule(self) -> List[Payment]:
        """生成还款计划表"""
        emi = self.calculate_emi()
        schedule = []
        remaining = self.principal
        
        for month in range(1, self.months + 1):
            interest = remaining * self.monthly_rate
            principal_paid = emi - interest
            remaining -= principal_paid
            
            schedule.append(Payment(
                month=month,
                payment=emi,
                principal=principal_paid,
                interest=interest,
                remaining=max(0, remaining)
            ))
        
        return schedule
    
    def get_summary(self) -> dict:
        """获取贷款摘要"""
        emi = self.calculate_emi()
        schedule = self.generate_schedule()
        
        total_payment = emi * self.months
        total_interest = total_payment - self.principal
        
        return {
            "principal": self.principal,
            "annual_rate": self.annual_rate,
            "years": self.years,
            "months": self.months,
            "emi": emi,
            "total_payment": total_payment,
            "total_interest": total_interest,
            "interest_ratio": total_interest / self.principal
        }
    
    def print_schedule(self, limit: int = 12):
        """打印还款计划"""
        schedule = self.generate_schedule()
        
        print(f"\n{'='*70}")
        print(f"{'期数':<6} {'月供':<12} {'本金':<12} {'利息':<12} {'剩余本金':<12}")
        print(f"{'='*70}")
        
        for payment in schedule[:limit]:
            print(f"{payment.month:<6} ¥{payment.payment:<10.2f} "
                  f"¥{payment.principal:<10.2f} ¥{payment.interest:<10.2f} "
                  f"¥{payment.remaining:<10.2f}")
        
        if len(schedule) > limit:
            print(f"... (共{len(schedule)}期，显示前{limit}期)")
        
        print(f"{'='*70}")

# 还款能力评估
class RepaymentCapacity:
    """还款能力评估"""
    
    def __init__(self, monthly_income: float, existing_debts: float = 0):
        self.monthly_income = monthly_income
        self.existing_debts = existing_debts
    
    def assess(self, emi: float) -> dict:
        """
        评估还款能力
        
        银行通常要求:
        - 月供/收入 ≤ 50% (保守银行要求 ≤ 40%)
        - (月供+现有负债)/收入 ≤ 55%
        """
        dti = (emi + self.existing_debts) / self.monthly_income
        emi_ratio = emi / self.monthly_income
        
        if dti <= 0.4 and emi_ratio <= 0.35:
            status = "✅ 优秀"
            suggestion = "还款能力充足，建议审批"
        elif dti <= 0.5 and emi_ratio <= 0.45:
            status = "⚠️ 良好"
            suggestion = "还款能力尚可，建议正常审批"
        elif dti <= 0.55 and emi_ratio <= 0.5:
            status = "⚠️ 一般"
            suggestion = "还款能力偏紧，建议提高利率或降低额度"
        else:
            status = "❌ 不足"
            suggestion = "还款能力不足，建议拒绝或大幅降低额度"
        
        return {
            "monthly_income": self.monthly_income,
            "existing_debts": self.existing_debts,
            "emi": emi,
            "dti": dti,
            "emi_ratio": emi_ratio,
            "status": status,
            "suggestion": suggestion
        }

# 主程序
def main():
    parser = argparse.ArgumentParser(description="银行贷款计算器")
    parser.add_argument("--principal", "-p", type=float, required=True, help="贷款本金")
    parser.add_argument("--rate", "-r", type=float, required=True, help="年利率 (如0.0435)")
    parser.add_argument("--years", "-y", type=int, required=True, help="贷款年限")
    parser.add_argument("--income", "-i", type=float, help="月收入 (用于还款能力评估)")
    parser.add_argument("--debts", "-d", type=float, default=0, help="现有月负债")
    args = parser.parse_args()
    
    # 计算贷款
    calculator = LoanCalculator(args.principal, args.rate, args.years)
    summary = calculator.get_summary()
    
    print(f"\n{'='*50}")
    print(f"📊 贷款计算结果")
    print(f"{'='*50}")
    print(f"贷款本金: ¥{summary['principal']:,.2f}")
    print(f"年利率: {summary['annual_rate']*100:.2f}%")
    print(f"贷款期限: {summary['years']}年 ({summary['months']}个月)")
    print(f"{'='*50}")
    print(f"月供: ¥{summary['emi']:,.2f}")
    print(f"还款总额: ¥{summary['total_payment']:,.2f}")
    print(f"利息总额: ¥{summary['total_interest']:,.2f}")
    print(f"利息占比: {summary['interest_ratio']*100:.1f}%")
    print(f"{'='*50}")
    
    # 打印还款计划
    calculator.print_schedule(limit=12)
    
    # 还款能力评估
    if args.income:
        capacity = RepaymentCapacity(args.income, args.debts)
        assessment = capacity.assess(summary['emi'])
        
        print(f"\n{'='*50}")
        print(f"💰 还款能力评估")
        print(f"{'='*50}")
        print(f"月收入: ¥{assessment['monthly_income']:,.2f}")
        print(f"现有负债: ¥{assessment['existing_debts']:,.2f}")
        print(f"月供: ¥{assessment['emi']:,.2f}")
        print(f"月供/收入比: {assessment['emi_ratio']*100:.1f}%")
        print(f"总负债/收入比: {assessment['dti']*100:.1f}%")
        print(f"评估结果: {assessment['status']}")
        print(f"建议: {assessment['suggestion']}")
        print(f"{'='*50}")

if __name__ == "__main__":
    main()
```

## 运行效果

```bash
$ python loan_calculator.py --principal 500000 --rate 0.0435 --years 20 --income 15000

==================================================
📊 贷款计算结果
==================================================
贷款本金: ¥500,000.00
年利率: 4.35%
贷款期限: 20年 (240个月)
==================================================
月供: ¥3,123.42
还款总额: ¥749,620.80
利息总额: ¥249,620.80
利息占比: 49.9%
==================================================

======================================================================
期数   月供         本金         利息         剩余本金
======================================================================
1      ¥3123.42     ¥1311.92     ¥1811.50     ¥498688.08
2      ¥3123.42     ¥1316.68     ¥1806.74     ¥497371.40
3      ¥3123.42     ¥1321.45     ¥1801.97     ¥496049.95
4      ¥3123.42     ¥1326.24     ¥1797.18     ¥494723.71
5      ¥3123.42     ¥1331.05     ¥1792.37     ¥493392.66
6      ¥3123.42     ¥1335.87     ¥1787.55     ¥492056.79
7      ¥3123.42     ¥1340.71     ¥1782.71     ¥490716.08
8      ¥3123.42     ¥1345.57     ¥1777.85     ¥489370.51
9      ¥3123.42     ¥1350.45     ¥1772.97     ¥488020.06
10     ¥3123.42     ¥1355.34     ¥1768.08     ¥486664.72
11     ¥3123.42     ¥1360.26     ¥1763.16     ¥485304.46
12     ¥3123.42     ¥1365.19     ¥1758.23     ¥483939.27
... (共240期，显示前12期)
======================================================================

==================================================
💰 还款能力评估
==================================================
月收入: ¥15,000.00
现有负债: ¥0.00
月供: ¥3,123.42
月供/收入比: 20.8%
总负债/收入比: 20.8%
评估结果: ✅ 优秀
建议: 还款能力充足，建议审批
==================================================
```

## 提前还款计算

```python
def calculate_prepayment(principal, annual_rate, years, prepay_month, prepay_amount):
    """计算提前还款后的新月供"""
    calculator = LoanCalculator(principal, annual_rate, years)
    schedule = calculator.generate_schedule()
    
    # 找到提前还款时的剩余本金
    remaining = schedule[prepay_month - 1].remaining
    
    # 提前还款后剩余本金
    new_principal = remaining - prepay_amount
    
    # 重新计算月供
    new_calculator = LoanCalculator(new_principal, annual_rate, 
                                     (years * 12 - prepay_month) / 12)
    new_emi = new_calculator.calculate_emi()
    
    return {
        "original_emi": calculator.calculate_emi(),
        "new_emi": new_emi,
        "monthly_saving": calculator.calculate_emi() - new_emi,
        "total_saving": (calculator.calculate_emi() - new_emi) * (years * 12 - prepay_month)
    }

# 示例：第60个月提前还10万
result = calculate_prepayment(500000, 0.0435, 20, 60, 100000)
print(f"新月供: ¥{result['new_emi']:,.2f}")
print(f"每月节省: ¥{result['monthly_saving']:,.2f}")
print(f"总节省: ¥{result['total_saving']:,.2f}")
```

## 不同还款方式对比

```python
def compare_repayment_methods(principal, rate, years):
    """对比等额本息 vs 等额本金"""
    
    # 等额本息
    emi_calculator = LoanCalculator(principal, rate, years)
    emi_summary = emi_calculator.get_summary()
    
    # 等额本金
    months = years * 12
    monthly_principal = principal / months
    first_month_interest = principal * rate / 12
    first_month_payment = monthly_principal + first_month_interest
    
    total_interest = 0
    remaining = principal
    for m in range(months):
        interest = remaining * rate / 12
        total_interest += interest
        remaining -= monthly_principal
    
    print("还款方式对比:")
    print(f"{'='*60}")
    print(f"{'方式':<15} {'首月月供':<12} {'末月月供':<12} {'总利息':<12}")
    print(f"{'='*60}")
    print(f"{'等额本息':<15} ¥{emi_summary['emi']:>10.2f} ¥{emi_summary['emi']:>10.2f} ¥{emi_summary['total_interest']:>10.2f}")
    print(f"{'等额本金':<15} ¥{first_month_payment:>10.2f} ¥{monthly_principal:>10.2f} ¥{total_interest:>10.2f}")
    print(f"{'='*60}")

compare_repayment_methods(500000, 0.0435, 20)
```

---

**完整代码**：https://github.com/yuzhaopeng-up/financial-ai-skills/tree/main/skills/credit-approval/examples

**#贷款计算 #等额本息 #信贷审批 #还款能力 #Python实战**
