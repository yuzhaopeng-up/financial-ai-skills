# 网点分析技能 (Branch Analysis Skill)

## 概述

网点分析技能是一个基于AI的银行网点竞争力评估与经营规划引擎。该技能综合分析网点的地理位置、竞争格局、客群特征等维度，输出SWOT分析、三年经营预测、重点发展业务方向及投入产出建议。

## 核心功能

- **多维度竞争力分析**：地理位置、竞争格局、客流量、产能潜力、服务半径
- **SWOT分析**：优势、劣势、机会、威胁的全面评估
- **三年经营预测**：基于历史数据和行业基准的财务预测
- **业务方向建议**：重点发展业务和资源配置建议

## 输入参数

| 参数 | 类型 | 说明 |
|------|------|------|
| zone_type | str | 区域类型：商业区/住宅区/工业区/大学区 |
| area | float | 网点面积（平方米） |
| staff_count | int | 员工人数 |
| competitor_count | int | 周边竞争网点数量 |
| local_enterprise_count | int | 本地企业数量 |

## 输出结构

```json
{
  "branch_id": "string",
  "zone_type": "string",
  "swot": {
    "strengths": ["string"],
    "weaknesses": ["string"],
    "opportunities": ["string"],
    "threats": ["string"]
  },
  "customer_profile": {
    "primary": "string",
    "secondary": "string",
    "potential": "string"
  },
  "traffic_estimate": {
    "daily_visitors": int,
    "peak_hours": ["string"],
    "conversion_rate": float
  },
  "business_focus": ["string"],
  "three_year_forecast": {
    "year1": {"revenue": float, "customers": int},
    "year2": {"revenue": float, "customers": int},
    "year3": {"revenue": float, "customers": int}
  },
  "resource_allocation": {
    "staff": {"front_desk": int, "sales": int, "back_office": int},
    "equipment": ["string"],
    "marketing_budget": float
  },
  "input_output_recommendation": {
    "investment": float,
    "expected_roi": float,
    "payback_period": int
  }
}
```

## 分析维度

### 1. 地理位置分析
- 商业区：高客流、高竞争、中高消费
- 住宅区：稳定客流、中等竞争、家庭金融需求
- 工业区：对公业务为主、季节性波动
- 大学区：年轻客群、数字化需求旺盛

### 2. 竞争格局分析
- 竞争网点数量与分布
- 差异化竞争机会
- 市场饱和度评估

### 3. 客流量预估
- 基于区域类型的基准客流
- 高峰时段识别
- 转化率估算

### 4. 产能潜力评估
- 人均产能基准
- 面积产能比
- 竞争位势指数

### 5. 服务半径分析
- 核心覆盖范围
- 辐射范围
- 潜在客户密度

## 使用方式

### CLI
```bash
python3 scripts/branch_cli.py generate "网点分析 商业区 员工10人 周边3个竞争网点"
```

### Python API
```python
from branch_analysis import BranchAnalysisEngine

engine = BranchAnalysisEngine()
result = engine.analyze(
    zone_type="商业区",
    area=300.0,
    staff_count=10,
    competitor_count=3,
    local_enterprise_count=50
)
print(result)
```

### 企微卡片
```python
from branch_analysis.wecom_integration import generate_wecom_card
card = generate_wecom_card(analysis_result)
```

## 技术规格

- Python 3.8+
- 依赖：pandas, numpy, scikit-learn (可选)
- 无外部API依赖，离线可用

## 作者

龙马集群 AI 团队
