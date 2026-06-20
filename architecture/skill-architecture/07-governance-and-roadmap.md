# 07 Skill 治理机制与复用路线图

## 1. 新增 Skill 立项门禁

新增 Skill 前必须回答：

1. 是否已有相同或相似 Skill？见 `data/skill-inventory.csv`。
2. 它属于 L0/L1/L2/L3 哪一层？
3. 能否通过配置复用已有基础构建块？
4. 输入/输出是否符合统一信息流？
5. 是否涉及敏感数据、外发、写入、删除？
6. 是否需要多智能体，还是普通组合即可？

## 2. 目录治理建议

```text
architecture/skill-architecture/     # Skill架构与资产清单
skills/                              # 可运行Skill代码
patterns/                            # 可复用组合模式（建议新增）
industry-packs/                      # 行业规则包（建议新增）
  financial/
  telecom/
  government/
  manufacturing/
```

> 本次仅新增 `architecture/skill-architecture/`，不移动现有代码，避免破坏历史结构。

## 3. 复用路线图

### Phase 1：资产可见
- 建立 inventory。
- 给每个 Skill 标注层级、行业属性、能力域。
- 找出重复能力和可迁移能力。

### Phase 2：构建块抽取
- 抽取六大基础能力：提取、分析、RAG、报告、安全、归档。
- 把行业差异沉淀为字段字典、规则包、模板包。
- 建立统一输出契约。

### Phase 3：组合模板沉淀
- 材料审核模板。
- 知识库问答模板。
- 经营日报模板。
- 客户服务闭环模板。
- 投研报告工厂模板。

### Phase 4：多智能体治理
- 建立 Agent 职责模板。
- 建立 trace/audit 标准。
- 建立人工确认规范。
- 建立平台落地测试清单。

## 4. 命名规范

建议：

```text
<domain>-<capability>-<level>
```

示例：
- `common-info-extractor-l1`
- `common-report-generator-l1`
- `financial-credit-approval-l2`
- `telecom-complaint-flow-l3`

## 5. 交付标准

每个新 Skill 必须包含：

- `SKILL.md`
- 输入参数定义
- 处理流程
- 标准输出
- demo data
- 测试脚本或最小验证命令
- 安全说明
- 行业属性与复用说明
- 在 inventory 中登记
