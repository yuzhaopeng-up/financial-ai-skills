"""
Budget Control Engine - 预算执行管控引擎

输入：部门/科目/预算金额/已使用/剩余月份
输出：执行率/预警状态/超支风险/管控建议
"""

import re
from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class BudgetAnalysisResult:
    """预算分析结果"""
    dept: str
    category: str
    budget: float          # 预算金额（万元）
    spent: float           # 已使用金额（万元）
    remaining: float       # 剩余金额（万元）
    remaining_months: float
    execution_rate: float  # 执行率%
    status: str            # green/yellow/red
    status_text: str
    overrun_risk: str      # low/medium/high/critical
    overrun_risk_text: str
    monthly_burn_rate: float   # 月均消耗
    projected_spend: float    # 预测总支出
    projected_overrun: float  # 预测超支
    recommendations: List[str]
    
    def to_dict(self) -> dict:
        return asdict(self)


class BudgetControlEngine:
    """预算管控引擎"""
    
    # 预警阈值
    YELLOW_THRESHOLD = 80.0   # 执行率>80%黄灯
    RED_THRESHOLD = 95.0      # 执行率>95%红灯
    
    def __init__(self):
        self.name = "BudgetControlEngine"
        self.version = "1.0.0"
    
    def analyze(
        self,
        dept: str,
        category: str,
        budget: float,
        spent: float,
        remaining_months: float
    ) -> BudgetAnalysisResult:
        """
        分析预算执行情况
        
        Args:
            dept: 部门名称
            category: 费用科目
            budget: 预算金额（万元）
            spent: 已使用金额（万元）
            remaining_months: 剩余月份
        
        Returns:
            BudgetAnalysisResult: 分析结果
        """
        # 计算剩余金额
        remaining = budget - spent
        
        # 计算执行率
        execution_rate = (spent / budget * 100) if budget > 0 else 0
        
        # 确定预警状态
        status, status_text = self._get_status(execution_rate)
        
        # 计算月均消耗率
        elapsed_months = max(0.1, 12 - remaining_months)  # 假设全年12个月
        monthly_burn_rate = spent / elapsed_months if elapsed_months > 0 else spent
        
        # 预测总支出
        projected_spend = monthly_burn_rate * 12
        
        # 预测超支
        projected_overrun = max(0, projected_spend - budget)
        
        # 超支风险评估
        overrun_risk, overrun_risk_text = self._get_overrun_risk(
            execution_rate, remaining_months, remaining, budget
        )
        
        # 生成管控建议
        recommendations = self._generate_recommendations(
            dept, category, budget, spent, remaining, 
            execution_rate, remaining_months, status, projected_overrun
        )
        
        return BudgetAnalysisResult(
            dept=dept,
            category=category,
            budget=budget,
            spent=spent,
            remaining=remaining,
            remaining_months=remaining_months,
            execution_rate=round(execution_rate, 2),
            status=status,
            status_text=status_text,
            overrun_risk=overrun_risk,
            overrun_risk_text=overrun_risk_text,
            monthly_burn_rate=round(monthly_burn_rate, 2),
            projected_spend=round(projected_spend, 2),
            projected_overrun=round(projected_overrun, 2),
            recommendations=recommendations
        )
    
    def _get_status(self, execution_rate: float) -> tuple:
        """根据执行率确定预警状态"""
        if execution_rate <= self.YELLOW_THRESHOLD:
            return "green", "🟢 执行正常"
        elif execution_rate <= self.RED_THRESHOLD:
            return "yellow", "🟡 需要关注"
        else:
            return "red", "🔴 超支预警"
    
    def _get_overrun_risk(
        self, 
        execution_rate: float, 
        remaining_months: float,
        remaining: float,
        budget: float
    ) -> tuple:
        """评估超支风险"""
        # 如果执行率已超预算
        if execution_rate > 100:
            return "critical", "⚠️ 已超支"
        
        # 计算每月可消耗预算
        if remaining_months > 0:
            monthly_budget = remaining / remaining_months
        else:
            monthly_budget = 0
        
        # 风险判断
        if execution_rate > self.RED_THRESHOLD:
            return "high", "🔴 高风险"
        elif execution_rate > self.YELLOW_THRESHOLD:
            if remaining_months <= 1:
                return "high", "🔴 高风险"
            elif remaining < (budget * 0.1):
                return "medium", "🟡 中等风险"
            else:
                return "low", "🟢 低风险"
        else:
            return "low", "🟢 低风险"
    
    def _generate_recommendations(
        self,
        dept: str,
        category: str,
        budget: float,
        spent: float,
        remaining: float,
        execution_rate: float,
        remaining_months: float,
        status: str,
        projected_overrun: float
    ) -> List[str]:
        """生成管控建议"""
        recommendations = []
        
        if status == "red":
            recommendations.append(f"🚨 【紧急】{dept}{category}已超预算执行，立即暂停非必要支出")
            recommendations.append(f"📊 预测超支 {projected_overrun:.1f} 万元，需提交预算调整申请")
            recommendations.append(f"💰 建议立即召开预算评审会，重新评估后续支出")
        elif status == "yellow":
            if remaining_months > 0:
                monthly_allowance = remaining / remaining_months
                recommendations.append(f"⚠️ {dept}{category}执行率达 {execution_rate:.1f}%，月均额度控制在 {monthly_allowance:.2f} 万元以内")
            recommendations.append(f"📋 严格审批后续报销，优先处理必要支出")
            recommendations.append(f"📈 每周跟踪执行进度，提前预警超支风险")
        else:
            recommendations.append(f"✅ {dept}{category}执行进度正常，继续保持")
            recommendations.append(f"📊 月度复盘预算执行情况，确保年底不超支")
        
        # 通用建议
        if projected_overrun > 0:
            recommendations.append(f"🔄 考虑跨部门调拨预算或调整支出计划")
        
        return recommendations
    
    def format_report(self, result: BudgetAnalysisResult) -> str:
        """格式化输出报告"""
        lines = [
            f"========== 预算执行分析报告 ==========",
            f"",
            f"📋 基本信息",
            f"   部门：{result.dept}",
            f"   科目：{result.category}",
            f"",
            f"💰 预算执行",
            f"   预算金额：{result.budget:.1f} 万元",
            f"   已使用：  {result.spent:.1f} 万元",
            f"   剩余：    {result.remaining:.1f} 万元",
            f"   剩余月份：{result.remaining_months} 个月",
            f"",
            f"📊 执行分析",
            f"   执行率：  {result.execution_rate}%  {result.status_text}",
            f"   月均消耗：{result.monthly_burn_rate:.2f} 万元/月",
            f"   预测总支出：{result.projected_spend:.1f} 万元",
            f"   预测超支：  {result.projected_overrun:.1f} 万元",
            f"",
            f"⚠️ 风险评估：{result.overrun_risk_text}",
            f"",
            f"💡 管控建议：",
        ]
        
        for rec in result.recommendations:
            lines.append(f"   {rec}")
        
        lines.append("")
        lines.append("=" * 40)
        
        return "\n".join(lines)


def parse_input(text: str) -> dict:
    """
    解析自然语言输入
    支持格式：
    - "预算管控 市场部 差旅费 预算20万 已用18万 剩余2个月"
    - "预算管控 市场部 差旅费 预算20 已用18 剩余2"
    """
    text = text.strip()
    
    # 尝试提取关键信息
    patterns = [
        # 匹配 预算X万 已用X万 剩余X个月
        r'预算\s*(\d+\.?\d*)\s*万?\s*已用\s*(\d+\.?\d*)\s*万?\s*剩余\s*(\d+\.?\d*)\s*个?月',
        # 匹配 预算X万 已用X万 剩余X
        r'预算\s*(\d+\.?\d*)\s*万?\s*已用\s*(\d+\.?\d*)\s*万?\s*剩余\s*(\d+\.?\d*)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            budget = float(match.group(1))
            spent = float(match.group(2))
            remaining_months = float(match.group(3))
            
            # 尝试提取部门和科目
            # 去掉已知模式后获取部门科目
            remaining = text
            for p in patterns:
                remaining = re.sub(p, '', remaining)
            
            parts = remaining.split()
            # 过滤掉"预算管控"等词
            parts = [p for p in parts if p not in ['预算管控', '管控', '预算', '分析']]
            
            dept = parts[0] if len(parts) > 0 else "未知部门"
            category = parts[1] if len(parts) > 1 else "未知科目"
            
            return {
                "dept": dept,
                "category": category,
                "budget": budget,
                "spent": spent,
                "remaining_months": remaining_months
            }
    
    raise ValueError(f"无法解析输入: {text}")


if __name__ == "__main__":
    # 测试
    engine = BudgetControlEngine()
    
    test_cases = [
        {
            "text": "预算管控 市场部 差旅费 预算20万 已用18万 剩余2个月",
            "expected": {"dept": "市场部", "category": "差旅费", "budget": 20.0, "spent": 18.0, "remaining_months": 2.0}
        },
        {
            "text": "预算管控 研发部 软件费 预算50万 已用35万 剩余3个月",
            "expected": {"dept": "研发部", "category": "软件费", "budget": 50.0, "spent": 35.0, "remaining_months": 3.0}
        },
        {
            "text": "预算管控 行政部 办公费 预算10万 已用9.5万 剩余1个月",
            "expected": {"dept": "行政部", "category": "办公费", "budget": 10.0, "spent": 9.5, "remaining_months": 1.0}
        }
    ]
    
    print("🧪 预算管控引擎测试")
    print("=" * 50)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {case['text']}")
        try:
            parsed = parse_input(case['text'])
            result = engine.analyze(**parsed)
            print(engine.format_report(result))
        except Exception as e:
            print(f"❌ 错误: {e}")
