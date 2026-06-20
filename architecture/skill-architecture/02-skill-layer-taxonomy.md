# 02 Skill 分层分类：基础、组合、组合的组合

## 分层定义

| 层级 | 定义 | 类比电信课程 | 复用策略 |
|---|---|---|---|
| L0 原子/连接器Skill | 工具、连接器、平台操作、搜索、文档、测试等技术服务 | TeleAgent/飞书/企微/搜索/文件工具 | 优先复用，不重复开发 |
| L1 基础Skill | 单点业务能力，输入输出清晰，通常只做一件事 | Info-Extractor、Data-Analyst、Knowledge-RAG、Report-Generator、Security-Guard、Archive-Manager | 作为所有行业的基础积木 |
| L2 组合Skill | 串联 2-4 个基础能力，完成一个业务流程 | 材料审核、产品手册RAG、日报生成+异常提示 | 抽取公共子能力，保留行业规则配置 |
| L3 组合的组合Skill | 面向端到端场景，包含多个流程/角色/系统 | 智能客服、厅堂运营、财富管理、智能数据面板 | 作为行业解决方案沉淀，避免复制粘贴式开发 |

## 代表清单

## L0 原子/连接器Skill

| name | source | scope | capability_domain | building_block_type |
| --- | --- | --- | --- | --- |
| api-test-automation | workspace_installed | 跨行业通用 | C07 客户/营销/服务 | SBB: 技术/平台服务构建块 |
| browser | agent_installed | 跨行业通用 | C09 集成连接器 | SBB: 技术/平台服务构建块 |
| byted-text-to-speech | workspace_installed | 跨行业通用 | C09 集成连接器 | SBB: 技术/平台服务构建块 |
| byted-web-search | workspace_agent_installed | 跨行业通用 | C06 流程编排与路由 | SBB: 技术/平台服务构建块 |
| clean-pytest | workspace_installed | 跨行业通用 | C09 集成连接器 | SBB: 技术/平台服务构建块 |
| computer-use | agent_installed | 跨行业通用 | C09 集成连接器 | SBB: 技术/平台服务构建块 |
| data-analysis-skill | workspace_installed | 跨行业通用 | C02 数据分析与洞察 | SBB: 技术/平台服务构建块 |
| edge-tts | workspace_installed | 跨行业通用 | C09 集成连接器 | SBB: 技术/平台服务构建块 |
| Feishu Cloud Drive | workspace_installed | 跨行业通用 | C09 集成连接器 | SBB: 技术/平台服务构建块 |
| feishu-doc-manager | agent_installed | 跨行业通用 | C09 集成连接器 | SBB: 技术/平台服务构建块 |
| feishu-wiki | agent_installed | 跨行业通用 | C09 集成连接器 | SBB: 技术/平台服务构建块 |
| github | workspace_installed | 跨行业通用 | C09 集成连接器 | SBB: 技术/平台服务构建块 |
| Grammar | workspace_installed | 跨行业通用 | C04 报告/文档生成 | SBB: 技术/平台服务构建块 |
| humanizer | workspace_installed | 跨行业通用 | C04 报告/文档生成 | SBB: 技术/平台服务构建块 |
| model-healthcheck | workspace_installed | 跨行业通用 | C02 数据分析与洞察 | SBB: 技术/平台服务构建块 |
| multi-search-engine | workspace_installed | 跨行业通用 | C03 知识检索与RAG | SBB: 技术/平台服务构建块 |
| nano-pdf | workspace_installed | 跨行业通用 | C09 集成连接器 | SBB: 技术/平台服务构建块 |
| newman | workspace_installed | 跨行业通用 | C09 集成连接器 | SBB: 技术/平台服务构建块 |
| ontology | workspace_installed | 跨行业通用 | C10 沉淀归档与治理 | SBB: 技术/平台服务构建块 |
| py-test-creator | workspace_installed | 跨行业通用 | C04 报告/文档生成 | SBB: 技术/平台服务构建块 |
| skill-creator | workspace_installed | 行业可迁移 | C06 流程编排与路由 | SBB: 技术/平台服务构建块 |
| tavily-search | workspace_installed | 跨行业通用 | C03 知识检索与RAG | SBB: 技术/平台服务构建块 |
| weather | workspace_installed | 跨行业通用 | C02 数据分析与洞察 | SBB: 技术/平台服务构建块 |
## L1 基础Skill

| name | source | scope | capability_domain | building_block_type |
| --- | --- | --- | --- | --- |
| agent-browser | workspace_installed | 跨行业通用 | C09 集成连接器 | SBB: 集成服务构建块 |
| agile-product-owner | workspace_installed | 跨行业通用 | C09 集成连接器 | SBB: 集成服务构建块 |
| ai-contract-review-cn | workspace_installed | 跨行业通用 | C09 集成连接器 | SBB: 集成服务构建块 |
| byted-seedance-video-generate | workspace_installed | 行业可迁移 | C04 报告/文档生成 | ABB: 业务能力构建块 |
| byted-seedream-image-generate | workspace_installed | 跨行业通用 | C09 集成连接器 | SBB: 集成服务构建块 |
| byted-teamproject-image-generate | workspace_installed | 跨行业通用 | C09 集成连接器 | SBB: 集成服务构建块 |
| byted-teamproject-video-generate | workspace_installed | 行业可迁移 | C04 报告/文档生成 | ABB: 业务能力构建块 |
| content-creator-cn | workspace_installed | 跨行业通用 | C09 集成连接器 | SBB: 集成服务构建块 |
| copywriter | workspace_installed | 跨行业通用 | C09 集成连接器 | SBB: 集成服务构建块 |
| cyber-owasp-review | workspace_installed | 跨行业通用 | C05 风险/合规/安全 | ABB: 业务能力构建块 |
| enterprise-due-diligence | workspace_installed | 行业可迁移 | C01 信息提取与结构化 | ABB: 业务能力构建块 |
| find-skills | workspace_installed | 跨行业通用 | C03 知识检索与RAG | ABB: 知识服务构建块 |
| frontend-design | workspace_installed | 跨行业通用 | C02 数据分析与洞察 | ABB: 业务能力构建块 |
| getdesign-md | workspace_installed | 行业可迁移 | C09 集成连接器 | SBB: 集成服务构建块 |
| go-concurrency | workspace_installed | 跨行业通用 | C09 集成连接器 | SBB: 集成服务构建块 |
| humanizer-academic-zh | workspace_installed | 跨行业通用 | C04 报告/文档生成 | ABB: 业务能力构建块 |
| lobby_emotion | private_financial | 行业专用：金融 | C07 客户/营销/服务 | ABB: 业务能力构建块 |
| lobby_queue | private_financial | 行业专用：金融 | C07 客户/营销/服务 | ABB: 业务能力构建块 |
| meeting-minutes | private_financial | 跨行业通用 | C04 报告/文档生成 | ABB: 业务能力构建块 |
| mlops-automation-cn | workspace_installed | 跨行业通用 | C09 集成连接器 | SBB: 集成服务构建块 |
| nodejs-backend-patterns | workspace_installed | 跨行业通用 | C07 客户/营销/服务 | ABB: 业务能力构建块 |
| openclaw-docker | workspace_installed | 跨行业通用 | C09 集成连接器 | SBB: 集成服务构建块 |
| openclaw-feishu-docs-perm-auto | workspace_installed | 跨行业通用 | C09 集成连接器 | SBB: 集成服务构建块 |
| opencli | agent_installed | 行业可迁移 | C06 流程编排与路由 | ABB: 业务能力构建块 |
| ops-daily-report | private_financial | 跨行业通用 | C04 报告/文档生成 | ABB: 业务能力构建块 |
| prd-developer | workspace_installed | 行业可迁移 | C09 集成连接器 | SBB: 集成服务构建块 |
| review-evo | workspace_installed | 跨行业通用 | C05 风险/合规/安全 | ABB: 业务能力构建块 |
| self-improvement | workspace_installed | 跨行业通用 | C09 集成连接器 | SBB: 集成服务构建块 |
| senior-devops | workspace_installed | 跨行业通用 | C09 集成连接器 | SBB: 集成服务构建块 |
| story-cog | workspace_installed | 行业可迁移 | C09 集成连接器 | SBB: 集成服务构建块 |
| summarize | agent_installed | 跨行业通用 | C06 流程编排与路由 | ABB: 业务能力构建块 |
| video-editor | workspace_installed | 行业可迁移 | C09 集成连接器 | SBB: 集成服务构建块 |
| video-to-prompt | workspace_installed | 行业可迁移 | C01 信息提取与结构化 | ABB: 业务能力构建块 |
| vite-react-tailwind | workspace_installed | 行业可迁移 | C09 集成连接器 | SBB: 集成服务构建块 |
| workspace-netdrive | agent_installed | 行业可迁移 | C09 集成连接器 | SBB: 集成服务构建块 |
| XUA-auto | workspace_installed | 跨行业通用 | C09 集成连接器 | SBB: 集成服务构建块 |
## L2 组合Skill

| name | source | scope | capability_domain | building_block_type |
| --- | --- | --- | --- | --- |
| actuarial_model | private_financial | 行业专用：金融 | C02 数据分析与洞察 | ABB组合: 流程/规则构建块 |
| alm | private_financial | 行业专用：金融 | C02 数据分析与洞察 | ABB组合: 流程/规则构建块 |
| aml_rating | private_financial | 行业专用：金融 | C05 风险/合规/安全 | ABB组合: 流程/规则构建块 |
| application-material-checker | private_financial | 行业可迁移 | C01 信息提取与结构化 | ABB组合: 流程/规则构建块 |
| audit-sampling | private_financial | 跨行业通用 | C10 沉淀归档与治理 | ABB组合: 流程/规则构建块 |
| block_trade | private_financial | 行业专用：金融 | C08 投资/组合/定价 | ABB组合: 流程/规则构建块 |
| branch_analysis | private_financial | 行业专用：金融 | C02 数据分析与洞察 | ABB组合: 流程/规则构建块 |
| budget_control | private_financial | 跨行业通用 | C02 数据分析与洞察 | ABB组合: 流程/规则构建块 |
| cash_management | private_financial | 行业专用：金融 | C02 数据分析与洞察 | ABB组合: 流程/规则构建块 |
| cashflow_forecast | private_financial | 行业可迁移 | C02 数据分析与洞察 | ABB组合: 流程/规则构建块 |
| churn-recall | private_financial | 行业专用：金融 | C07 客户/营销/服务 | ABB组合: 流程/规则构建块 |
| claim_analysis | private_financial | 行业专用：金融 | C02 数据分析与洞察 | ABB组合: 流程/规则构建块 |
| claim_review_v2 | private_financial | 行业专用：金融 | C05 风险/合规/安全 | ABB组合: 流程/规则构建块 |
| code_review_skill | private_financial | 跨行业通用 | C02 数据分析与洞察 | ABB组合: 流程/规则构建块 |
| collateral-valuation | private_financial | 行业专用：金融 | C02 数据分析与洞察 | ABB组合: 流程/规则构建块 |
| collection-optimize | private_financial | 行业专用：金融 | C02 数据分析与洞察 | ABB组合: 流程/规则构建块 |
| compliance-auto | private_financial | 行业专用：金融 | C05 风险/合规/安全 | ABB组合: 流程/规则构建块 |
| compliance_training | private_financial | 行业专用：金融 | C05 风险/合规/安全 | ABB组合: 流程/规则构建块 |
| content-strategy | workspace_installed | 跨行业通用 | C09 集成连接器 | SBB: 集成服务构建块 |
| contract-review | private_financial | 跨行业通用 | C02 数据分析与洞察 | ABB组合: 流程/规则构建块 |
| corp_account_opening | private_financial | 行业专用：金融 | C02 数据分析与洞察 | ABB组合: 流程/规则构建块 |
| credit_approval | private_financial | 行业专用：金融 | C02 数据分析与洞察 | ABB组合: 流程/规则构建块 |
| credit_collection | private_financial | 行业专用：金融 | C02 数据分析与洞察 | ABB组合: 流程/规则构建块 |
| cross_border_biz | private_financial | 行业专用：金融 | C02 数据分析与洞察 | ABB组合: 流程/规则构建块 |
| customer-health | private_financial | 跨行业通用 | C07 客户/营销/服务 | ABB组合: 流程/规则构建块 |
| customer-marketing | private_financial | 跨行业通用 | C07 客户/营销/服务 | ABB组合: 流程/规则构建块 |
| customer-persona | private_financial | 跨行业通用 | C07 客户/营销/服务 | ABB组合: 流程/规则构建块 |
| dca_calculator | private_financial | 行业专用：金融 | C02 数据分析与洞察 | ABB组合: 流程/规则构建块 |
| douyin-creator-cn | workspace_installed | 行业可迁移 | C02 数据分析与洞察 | ABB组合: 流程/规则构建块 |
| esg_research | private_financial | 行业专用：金融 | C03 知识检索与RAG | ABB: 知识服务构建块 |
| expense_audit | private_financial | 跨行业通用 | C05 风险/合规/安全 | ABB组合: 流程/规则构建块 |
| financial_extract | private_financial | 跨行业通用 | C01 信息提取与结构化 | ABB组合: 流程/规则构建块 |
| fixed_income_plus | private_financial | 行业专用：金融 | C08 投资/组合/定价 | ABB组合: 流程/规则构建块 |
| fof_portfolio | private_financial | 行业专用：金融 | C08 投资/组合/定价 | ABB组合: 流程/规则构建块 |
| fraud_alert | private_financial | 行业专用：金融 | C05 风险/合规/安全 | ABB组合: 流程/规则构建块 |
| fraud_detection | private_financial | 行业专用：金融 | C05 风险/合规/安全 | ABB组合: 流程/规则构建块 |
| fund-research | private_financial | 行业专用：金融 | C08 投资/组合/定价 | ABB组合: 流程/规则构建块 |
| fund_compare | private_financial | 行业专用：金融 | C08 投资/组合/定价 | ABB组合: 流程/规则构建块 |
| fund_manager_profile | private_financial | 行业专用：金融 | C08 投资/组合/定价 | ABB组合: 流程/规则构建块 |
| insurance_recommend | private_financial | 行业专用：金融 | C07 客户/营销/服务 | ABB组合: 流程/规则构建块 |
## L3 组合的组合Skill

| name | source | scope | capability_domain | building_block_type |
| --- | --- | --- | --- | --- |
| arkclaw-team-project-builder | workspace_installed | 行业可迁移 | C06 流程编排与路由 | Solution Building Block: 场景解决方案构建块 |
| family-trust | private_financial | 行业专用：金融 | C08 投资/组合/定价 | Solution Building Block: 场景解决方案构建块 |
| financial-intelligence | private_financial | 行业专用：金融 | C02 数据分析与洞察 | Solution Building Block: 场景解决方案构建块 |
| global-asset-allocation | private_financial | 行业专用：金融 | C08 投资/组合/定价 | Solution Building Block: 场景解决方案构建块 |
| portfolio_management | private_financial | 行业专用：金融 | C08 投资/组合/定价 | Solution Building Block: 场景解决方案构建块 |
| research-report | private_financial | 行业专用：金融 | C04 报告/文档生成 | Solution Building Block: 场景解决方案构建块 |
| smart_customer_service | private_financial | 行业专用：金融 | C07 客户/营销/服务 | Solution Building Block: 场景解决方案构建块 |
| wealth-management | private_financial | 行业专用：金融 | C08 投资/组合/定价 | Solution Building Block: 场景解决方案构建块 |


> 完整清单见 `data/skill-inventory.csv`。
