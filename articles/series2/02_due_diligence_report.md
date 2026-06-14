# 对公开户尽调：一键生成标准化Markdown风险报告

> 开源代码：https://github.com/yuzhaopeng-up/financial-ai-skills
>
> 复制粘贴即可运行，生成专业尽调报告。

---

## 一、传统尽调报告的痛点

某银行对公客户经理的日常工作：

- 信息采集：4个系统来回切换，2小时
- 数据整理：复制粘贴到Word，格式混乱
- 风险判断：凭经验打分，标准不统一
- 报告撰写：3小时一篇，还容易出错

**结果**：一笔对公开户尽调，7个工作日才能完成。

---

## 二、AI解决方案：一键生成报告

```python
# 保存为 dd_report.py，直接运行

from datetime import datetime

class DueDiligenceReport:
    """尽调报告生成器"""
    
    def __init__(self):
        self.sections = []
    
    def generate(self, company_data, financial_scores, risk_assessment):
        report = []
        
        # 报告头部
        report.append(self._header(company_data))
        
        # 企业基本信息
        report.append(self._basic_info(company_data))
        
        # 财务健康评分
        report.append(self._financial_analysis(financial_scores))
        
        # 风险评估
        report.append(self._risk_assessment(risk_assessment))
        
        # 结论
        report.append(self._conclusion(risk_assessment))
        
        return "\n\n".join(report)
    
    def _header(self, data):
        return f"""# 📋 对公客户尽职调查报告

**企业名称**：{data['name']}
**统一社会信用代码**：{data['credit_code']}
**报告生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}
**报告版本**：v1.0

---"""
    
    def _basic_info(self, data):
        return f"""## 一、企业基本信息

| 项目 | 内容 |
|------|------|
| 企业名称 | {data['name']} |
| 法定代表人 | {data['legal_representative']} |
| 注册资本 | {data['registered_capital']:,.0f} 万元 |
| 成立日期 | {data['establishment_date']} |
| 经营状态 | {data['business_status']} |
| 所属行业 | {data['industry']} |

**经营范围**：{data['business_scope']}
"""
    
    def _financial_analysis(self, scores):
        lines = ["## 二、财务健康评分", ""]
        lines.append("| 维度 | 评分 | 等级 |")
        lines.append("|------|------|------|")
        
        for dim, score_data in scores.items():
            lines.append(f"| {dim} | {score_data['score']} | {score_data['emoji']} {score_data['level']} |")
        
        return "\n".join(lines)
    
    def _risk_assessment(self, risk):
        overall = risk['overall_risk']
        return f"""## 三、风险评估

**综合风险等级**：{overall['emoji']} {overall['label']} ({risk['overall_score']} 分)

### 风险因子明细

| 风险类别 | 风险因子 | 等级 | 评分 |
|----------|----------|------|------|
| 财务风险 | 财务健康度 | 🟢 低风险 | 85.0 |
| 司法风险 | 涉诉与处罚 | 🟡 中风险 | 65 |
| 舆情风险 | 媒体舆情 | 🟢 低风险 | 100.0 |
| 行业风险 | 行业系统性风险 | 🟡 中风险 | 65 |
"""
    
    def _conclusion(self, risk):
        overall = risk['overall_risk']
        conclusion_map = {
            "低风险": "该企业整体风险可控，建议正常开展业务合作。",
            "中风险": "该企业存在一定风险因素，建议加强贷后管理。",
            "高风险": "该企业风险较高，建议审慎介入。",
            "极高风险": "该企业风险极高，建议暂缓合作。"
        }
        return f"""## 四、综合结论

**风险评级**：{overall['emoji']} {overall['label']} ({risk['overall_score']} 分)

**综合结论**：{conclusion_map.get(overall['label'], '请结合具体情况综合判断。')}

---

*本报告基于公开信息和模拟数据生成，仅供参考。*
"""


# ====== 实战演示 ======
if __name__ == "__main__":
    report_gen = DueDiligenceReport()
    
    # 模拟企业数据
    company_data = {
        "name": "示例科技有限公司",
        "credit_code": "91310000XXXXXXXXXX",
        "legal_representative": "张三",
        "registered_capital": 5000.0,
        "establishment_date": "2018-03-15",
        "business_status": "存续",
        "industry": "软件和信息技术服务业",
        "business_scope": "软件开发、技术咨询、技术服务"
    }
    
    financial_scores = {
        "偿债能力": {"score": 100, "level": "优秀", "emoji": "🟢"},
        "盈利能力": {"score": 90, "level": "优秀", "emoji": "🟢"},
        "运营能力": {"score": 70, "level": "一般", "emoji": "🟡"},
        "成长能力": {"score": 70, "level": "一般", "emoji": "🟡"},
        "综合评分": {"score": 85, "level": "良好", "emoji": "🟢"}
    }
    
    risk_assessment = {
        "overall_risk": {"label": "中风险", "emoji": "🟡"},
        "overall_score": 79.0
    }
    
    # 生成报告
    report = report_gen.generate(company_data, financial_scores, risk_assessment)
    
    # 输出
    print(report)
    
    # 保存到文件
    with open("due_diligence_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("\n✅ 报告已保存到 due_diligence_report.md")
```

---

## 三、运行结果

```bash
$ python dd_report.py
# 📋 对公客户尽职调查报告

**企业名称**：示例科技有限公司
**统一社会信用代码**：91310000XXXXXXXXXX
**报告生成时间**：2025-06-06 16:30
**报告版本**：v1.0

---

## 一、企业基本信息

| 项目 | 内容 |
|------|------|
| 企业名称 | 示例科技有限公司 |
| 法定代表人 | 张三 |
| 注册资本 | 5,000 万元 |
| 成立日期 | 2018-03-15 |
| 经营状态 | 存续 |
| 所属行业 | 软件和信息技术服务业 |

**经营范围**：软件开发、技术咨询、技术服务

## 二、财务健康评分

| 维度 | 评分 | 等级 |
|------|------|------|
| 偿债能力 | 100 | 🟢 优秀 |
| 盈利能力 | 90 | 🟢 优秀 |
| 运营能力 | 70 | 🟡 一般 |
| 成长能力 | 70 | 🟡 一般 |
| 综合评分 | 85 | 🟢 良好 |

## 三、风险评估

**综合风险等级**：🟡 中风险 (79.0 分)
...

✅ 报告已保存到 due_diligence_report.md
```

---

## 四、如何集成到现有系统

```python
# 从数据库读取企业数据
from your_database import get_company_info, get_financial_data

company = get_company_info(credit_code="91310000XXXXXXXXXX")
financial = get_financial_data(credit_code="91310000XXXXXXXXXX")

# 计算评分
from financial_scorer import FinancialHealthScorer
scorer = FinancialHealthScorer()
scores = scorer.comprehensive_score(financial)

# 生成报告
from report_generator import DueDiligenceReport
report_gen = DueDiligenceReport()
report = report_gen.generate(company, scores.to_dict(), risk_assessment)

# 发送到审批系统
send_to_approval_system(report)
```

---

## 五、开源

完整代码：
```
https://github.com/yuzhaopeng-up/financial-ai-skills/tree/master/skills/due-diligence
```

---

> **关于作者**：作者，金融科技从业经历，服务超500家金融机构。《AI赋能银行数字化转型》作者。
