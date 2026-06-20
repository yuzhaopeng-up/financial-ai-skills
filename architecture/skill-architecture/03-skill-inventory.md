# 03 Skill 资产清单摘要

本文件按能力域展示代表 Skill。完整机器可读清单见：

- `data/skill-inventory.json`
- `data/skill-inventory.csv`

## C01 信息提取与结构化

| name | level | scope | source | description |
| --- | --- | --- | --- | --- |
| application-material-checker | L2 组合Skill | 行业可迁移 | private_financial | Financial AI Skill - 进件材料自动核对引擎。基于规则引擎对身份证/营业执照/银行流水/合同等单据进行完整性+合规性双维校验，自动识别缺失项、过期证件、名称... |
| enterprise-due-diligence | L1 基础Skill | 行业可迁移 | workspace_installed |  |
| financial_extract | L2 组合Skill | 跨行业通用 | private_financial |  |
| invoice_check | L2 组合Skill | 跨行业通用 | private_financial |  |
| video-to-prompt | L1 基础Skill | 行业可迁移 | workspace_installed | Convert a local desktop recording (MP4 / MKV) into a structured CUA prompt. Use this sk... |
## C02 数据分析与洞察

| name | level | scope | source | description |
| --- | --- | --- | --- | --- |
| actuarial_model | L2 组合Skill | 行业专用：金融 | private_financial |  |
| alm | L2 组合Skill | 行业专用：金融 | private_financial |  |
| branch_analysis | L2 组合Skill | 行业专用：金融 | private_financial |  |
| budget_control | L2 组合Skill | 跨行业通用 | private_financial |  |
| cash_management | L2 组合Skill | 行业专用：金融 | private_financial |  |
| cashflow_forecast | L2 组合Skill | 行业可迁移 | private_financial |  |
| claim_analysis | L2 组合Skill | 行业专用：金融 | private_financial |  |
| code_review_skill | L2 组合Skill | 跨行业通用 | private_financial |  |
| collateral-valuation | L2 组合Skill | 行业专用：金融 | private_financial | 金融AI技能 - 抵押物智能估值引擎。输入抵押物类型、地址/规格、面积，输出估值报告+风险建议。支持房产、设备、车辆、土地、应收账款、股权等抵押物类型，覆盖金融行业常见抵押物... |
| collection-optimize | L2 组合Skill | 行业专用：金融 | private_financial | 金融AI技能 - 智能催收策略优化引擎。输入逾期客户信息及历史催收记录，输出分层催收策略与定制化话术。目标：回收率提升≥10%。 |
| contract-review | L2 组合Skill | 跨行业通用 | private_financial | 金融AI技能 - 合同智能审查引擎。自动审查合同条款，识别风险点，提供修改建议。支持多种合同类型，覆盖金融行业常见合同风险。 |
| corp_account_opening | L2 组合Skill | 行业专用：金融 | private_financial |  |
| credit_approval | L2 组合Skill | 行业专用：金融 | private_financial |  |
| credit_collection | L2 组合Skill | 行业专用：金融 | private_financial |  |
| cross_border_biz | L2 组合Skill | 行业专用：金融 | private_financial |  |
| data-analysis-skill | L0 原子/连接器Skill | 跨行业通用 | workspace_installed | 数据分析技能包 - 自动抓取、清洗、可视化、生成报告。适合数据分析师、运营人员，告别 Excel 手工操作。 |
| dca_calculator | L2 组合Skill | 行业专用：金融 | private_financial |  |
| douyin-creator-cn | L2 组合Skill | 行业可迁移 | workspace_installed | Douyin Creator Assistant - Tag recommendations, best posting times, title optimization,... |
| financial-intelligence | L3 组合的组合Skill | 行业专用：金融 | private_financial | Financial AI Skill - 6大财务场景AI赋能：发票查验、预算管控、财报速读、税务筹划、费用报销、资金预测。基于规则引擎的轻量级财务智能体，零API费用，毫秒... |
| frontend-design | L1 基础Skill | 跨行业通用 | workspace_installed | Create distinctive, production-grade frontend interfaces with high design quality. Use ... |
| ipo_analysis | L2 组合Skill | 行业专用：金融 | private_financial |  |
| kpi_performance | L2 组合Skill | 行业专用：金融 | private_financial |  |
| ma-scheme | L2 组合Skill | 行业专用：金融 | private_financial | 金融AI技能 - 并购方案生成引擎。输入收购方、被收购方、交易目的，输出交易结构设计、估值分析、财务预测及风险提示。支持多种交易结构，覆盖A股上市公司并购重组场景。 |
| model-healthcheck | L0 原子/连接器Skill | 跨行业通用 | workspace_installed | Test all configured models for availability. Activate when user says "test models", "ch... |
| no-code-frontend-builder | L2 组合Skill | 跨行业通用 | workspace_installed | Meta-skill for generating production-ready React UI for non-programmers by orchestratin... |
| performance_attribution | L2 组合Skill | 行业专用：金融 | private_financial |  |
| product-manager-toolkit | L2 组合Skill | 跨行业通用 | workspace_installed | Comprehensive toolkit for product managers including RICE prioritization, customer inte... |
| robo_advisor | L2 组合Skill | 行业专用：金融 | private_financial |  |
| stress_test | L2 组合Skill | 行业专用：金融 | private_financial |  |
| supply_chain | L2 组合Skill | 行业专用：金融 | private_financial |  |
## C03 知识检索与RAG

| name | level | scope | source | description |
| --- | --- | --- | --- | --- |
| esg_research | L2 组合Skill | 行业专用：金融 | private_financial |  |
| find-skills | L1 基础Skill | 跨行业通用 | workspace_installed | Search and discover OpenClaw skills from various sources. Use when: user wants to find ... |
| multi-search-engine | L0 原子/连接器Skill | 跨行业通用 | workspace_installed | Multi search engine integration with 17 engines (8 CN + 9 Global). Supports advanced se... |
| policy_management | L2 组合Skill | 行业专用：金融 | private_financial |  |
| product-manual-rag | L2 组合Skill | 行业专用：金融 | private_financial | Financial AI Skill - 产品手册智能对话引擎。基于 BM25 + TF-IDF 双路检索 + RRF 融合的轻量级 RAG，零外部依赖、毫秒级响应、自动出处... |
| regulatory-policy-rag | L2 组合Skill | 跨行业通用 | private_financial | Financial AI Skill - 监管政策智能解读引擎。基于 BM25 + TF-IDF 双路检索 + RRF 融合，对银保监/央行/证监会等监管文件进行智能问答，自... |
| research_rag | L2 组合Skill | 跨行业通用 | private_financial | Financial AI Skill - 研报RAG检索引擎。BM25+TF-IDF双路检索+RRF融合+多轮对话上下文+引用标注，支持自然语言查询行业/公司研报知识库，零外... |
| securities_research | L2 组合Skill | 行业专用：金融 | private_financial |  |
| tavily-search | L0 原子/连接器Skill | 跨行业通用 | workspace_installed | Use Tavily API for real-time web search and content extraction. Use when: user needs re... |
## C04 报告/文档生成

| name | level | scope | source | description |
| --- | --- | --- | --- | --- |
| byted-seedance-video-generate | L1 基础Skill | 行业可迁移 | workspace_installed | Generate videos using Seedance models. Invoke when user wants to create videos from tex... |
| byted-teamproject-video-generate | L1 基础Skill | 行业可迁移 | workspace_installed | Generate videos using Seedance models. Invoke when user wants to create videos from tex... |
| Grammar | L0 原子/连接器Skill | 跨行业通用 | workspace_installed | Correct grammar and spelling without changing meaning or style. |
| humanizer | L0 原子/连接器Skill | 跨行业通用 | workspace_installed | Humanize text: strip AI-isms and add real voice. |
| humanizer-academic-zh | L1 基础Skill | 跨行业通用 | workspace_installed | Humanizer 中文学术版——当用户要求润色论文、去除AI味、降低AIGC检测率，或说"帮我改改这段""这段读起来像AI写的"时触发。 |
| market-view | L2 组合Skill | 行业专用：金融 | private_financial | Financial AI Skill - 市场观点输出引擎。输入市场数据/新闻/行情，自动生成日报/周报观点输出（大盘综述+行业表现+热点主题+资金流向+下周展望）。覆盖A股... |
| meeting-minutes | L1 基础Skill | 跨行业通用 | private_financial | Financial AI Skill - 调研纪要生成器 v2.0。输入调研录音文字/会议记录/音频文件路径，自动输出结构化纪要（参会人+核心议题+关键要点+待办事项+风险提... |
| ops-daily-report | L1 基础Skill | 跨行业通用 | private_financial | Financial AI Skill - 运营日报生成器。输入运营数据指标，自动生成格式化运营日报（业务概况+重点指标+同比环比+异常预警+明日计划）。覆盖银行/证券/基金运... |
| py-test-creator | L0 原子/连接器Skill | 跨行业通用 | workspace_installed | Automatically generates pytest-compatible unit test templates from Python function sign... |
| research-report | L3 组合的组合Skill | 行业专用：金融 | private_financial | Financial AI Skill - 投研报告自动生成器。输入行业/公司/年度自然语言请求，自动输出完整投研报告（摘要+行业趋势+公司基本面+财务估值+风险提示+投资建议... |
| research_notes | L2 组合Skill | 行业专用：金融 | private_financial |  |
| roadshow-material | L2 组合Skill | 行业专用：金融 | private_financial | Financial AI Skill - 路演材料生成器。输入产品信息/目标客户/演讲时长，自动生成路演PPT大纲+讲稿（开场白+产品亮点+对比优势+风险揭示+结语）。覆盖银... |
## C05 风险/合规/安全

| name | level | scope | source | description |
| --- | --- | --- | --- | --- |
| aml_rating | L2 组合Skill | 行业专用：金融 | private_financial |  |
| claim_review_v2 | L2 组合Skill | 行业专用：金融 | private_financial |  |
| compliance-auto | L2 组合Skill | 行业专用：金融 | private_financial | 金融AI技能 - 业务流程合规性自动检查引擎。输入业务类型和操作记录，自动检查合规性，输出合规报告和整改建议。支持10+种合规规则，覆盖金融行业主要业务流程合规检查场景。 |
| compliance_training | L2 组合Skill | 行业专用：金融 | private_financial |  |
| cyber-owasp-review | L1 基础Skill | 跨行业通用 | workspace_installed | Map application security findings to OWASP Top 10 categories and generate remediation c... |
| expense_audit | L2 组合Skill | 跨行业通用 | private_financial |  |
| fraud_alert | L2 组合Skill | 行业专用：金融 | private_financial |  |
| fraud_detection | L2 组合Skill | 行业专用：金融 | private_financial |  |
| liquidity-alert | L2 组合Skill | 行业专用：金融 | private_financial | 金融AI技能 - 资金流动性风险预警引擎。基于规则引擎预测30天流动性缺口，识别预警信号，支持LCR/净流动性缺口监控。适用于银行、证券、基金、保险等金融机构资金管理场景。 |
| operational_risk | L2 组合Skill | 行业专用：金融 | private_financial |  |
| review-evo | L1 基础Skill | 跨行业通用 | workspace_installed | Self-improving code reviewer that learns your codebase over time. Analyzes git history,... |
| risk-compliance | L2 组合Skill | 行业专用：金融 | private_financial | Financial AI Skill - 风控合规智能体。提供企业风险评估、信用评级、反欺诈检测、合规检查、财务诊断、监管政策查询、贷后监控、产业链风险追踪、市场情绪监测、关... |
| smart_underwriting | L2 组合Skill | 行业专用：金融 | private_financial |  |
| suspicious_report | L2 组合Skill | 行业专用：金融 | private_financial |  |
| underwriting_v2 | L2 组合Skill | 行业专用：金融 | private_financial |  |
| wecom-template-card | L2 组合Skill | 行业专用：金融 | private_financial | Enterprise WeChat template_card builder and sender. Provides reusable card templates fo... |
## C06 流程编排与路由

| name | level | scope | source | description |
| --- | --- | --- | --- | --- |
| arkclaw-team-project-builder | L3 组合的组合Skill | 行业可迁移 | workspace_installed | 项目经理负责项目规划、团队组建与项目调整。涵盖：意图识别 → 澄清沟通 → 规划方案 → 创建团队，以及项目运行中的成员增删改、项目信息修改。通过 openclaw gate... |
| byted-web-search | L0 原子/连接器Skill | 跨行业通用 | workspace_agent_installed | 火山引擎联网搜索 API，返回网页/图片结果。联网搜索场景优先使用本 skill。触发词包括：查/搜/找、真的吗/靠谱吗/确认/核实、最近/今天/最新/近期、出处/来源/链接... |
| lobby_routing | L2 组合Skill | 行业专用：金融 | private_financial |  |
| opencli | L1 基础Skill | 行业可迁移 | agent_installed |  |
| skill-creator | L0 原子/连接器Skill | 行业可迁移 | workspace_installed | Guide for creating effective skills. This skill should be used when users want to creat... |
| Story Writer — Bilingual Enhanced Edition | L2 组合Skill | 跨行业通用 | workspace_installed | 小说创作、角色设计、情节设计(三幕式)、对话生成、世界观构建、续写。Story writing with character design, three-act plot s... |
| summarize | L1 基础Skill | 跨行业通用 | agent_installed | Summarize URLs or files with the summarize CLI (web, PDFs, images, audio, YouTube). |
## C07 客户/营销/服务

| name | level | scope | source | description |
| --- | --- | --- | --- | --- |
| api-test-automation | L0 原子/连接器Skill | 跨行业通用 | workspace_installed | API接口测试自动化工具，支持REST/GraphQL，包含接口测试、性能测试、契约测试、Mock服务等功能 / API Test Automation for REST/G... |
| churn-recall | L2 组合Skill | 行业专用：金融 | private_financial | 金融AI技能 - 流失客户召回引擎。识别潜在流失客户，基于RFM模型和客户行为数据生成个性化召回话术和营销策略。降低客户流失率，提升客户活跃度。 |
| customer-health | L2 组合Skill | 跨行业通用 | private_financial | 金融AI技能 - 客户健康度热力图引擎。可视化展示客户健康度，基于多维度评分规则自动计算健康度得分，输出热力图与预警名单。支持客户群整体健康监测、异常预警、客群分层。 |
| customer-marketing | L2 组合Skill | 跨行业通用 | private_financial | Financial AI Skill - 客户经理营销话术实时生成器。输入客户画像和营销目标，AI自动生成电话/微信/拜访话术，支持异议处理预演、方言适配、多风格切换。覆盖零... |
| customer-persona | L2 组合Skill | 跨行业通用 | private_financial | Financial AI Skill - 360 度客户画像生成器。输入客户基本信息（自然语言或结构化），输出 RFM 标签、生命周期阶段、推荐产品清单（25 个银行产品）、... |
| insurance_recommend | L2 组合Skill | 行业专用：金融 | private_financial |  |
| lobby_emotion | L1 基础Skill | 行业专用：金融 | private_financial |  |
| lobby_marketing | L2 组合Skill | 行业专用：金融 | private_financial |  |
| lobby_queue | L1 基础Skill | 行业专用：金融 | private_financial |  |
| modified-code-review | L2 组合Skill | 跨行业通用 | workspace_installed | Reviews user-modified code (diffs/PRs), provides best-practice recommendations, analyze... |
| nodejs-backend-patterns | L1 基础Skill | 跨行业通用 | workspace_installed | Build production-ready Node.js backend services with Express/Fastify, implementing midd... |
| objection-training | L2 组合Skill | 行业专用：金融 | private_financial | 金融AI技能 - 客户异议训练引擎。模拟客户各种异议场景，为客户经理提供实战训练。包含5种以上异议类型，自动评分和改进建议。 |
| renewal_alert | L2 组合Skill | 行业专用：金融 | private_financial |  |
| senior-backend | L2 组合Skill | 跨行业通用 | workspace_installed | This skill should be used when the user asks to "design REST APIs", "optimize database ... |
| smart_customer_service | L3 组合的组合Skill | 行业专用：金融 | private_financial |  |
| smart_marketing | L2 组合Skill | 行业专用：金融 | private_financial |  |
## C08 投资/组合/定价

| name | level | scope | source | description |
| --- | --- | --- | --- | --- |
| block_trade | L2 组合Skill | 行业专用：金融 | private_financial |  |
| family-trust | L3 组合的组合Skill | 行业专用：金融 | private_financial | Financial AI Skill - 家族信托方案引擎。输入客户画像/资产规模/传承目标，自动生成家族信托设立方案（架构设计+资产配置+税务筹划+受益人安排+风险隔离）。... |
| fixed_income_plus | L2 组合Skill | 行业专用：金融 | private_financial |  |
| fof_portfolio | L2 组合Skill | 行业专用：金融 | private_financial |  |
| fund-research | L2 组合Skill | 行业专用：金融 | private_financial | Financial AI Skill - 基金研究报告生成器。输入基金代码/名称，自动输出基金分析报告（业绩归因+收益分解+风险分析+基金经理评价+投资建议）。覆盖公募/私募... |
| fund_compare | L2 组合Skill | 行业专用：金融 | private_financial |  |
| fund_manager_profile | L2 组合Skill | 行业专用：金融 | private_financial |  |
| global-asset-allocation | L3 组合的组合Skill | 行业专用：金融 | private_financial | Financial AI Skill - 全球资产配置引擎。输入客户风险偏好/资产规模/配置目标，自动生成全球资产配置方案（区域分布+资产类别+货币对冲+再平衡策略）。覆盖银... |
| margin_trading | L2 组合Skill | 行业专用：金融 | private_financial |  |
| options_strategy | L2 组合Skill | 行业专用：金融 | private_financial |  |
| portfolio_management | L3 组合的组合Skill | 行业专用：金融 | private_financial |  |
| portfolio_optimize | L2 组合Skill | 行业专用：金融 | private_financial |  |
| product-pricing | L2 组合Skill | 行业专用：金融 | private_financial | 金融AI技能 - 产品定价引擎。输入产品类型、客户风险等级、市场利率，输出定价方案及利率敏感性分析。支持存款、贷款、汇兑、理财四大产品线。 |
| quant_backtest | L2 组合Skill | 行业专用：金融 | private_financial |  |
| quant_fund | L2 组合Skill | 行业专用：金融 | private_financial |  |
| rebalance | L2 组合Skill | 行业专用：金融 | private_financial | 金融AI技能 - 资产配置再平衡引擎。输入当前持仓+目标配置，输出调仓方案+交易成本估算。支持多资产类型（股票/债券/基金/黄金/外汇/理财等），基于规则引擎，无需LLM。 |
| wealth-management | L3 组合的组合Skill | 行业专用：金融 | private_financial | Financial AI Skill - 财富管理智能体。提供资产配置、财务健康诊断、退休规划、保险规划、税务优化、教育金规划、房产规划、智能投顾等8大能力。基于规则引擎的轻... |
## C09 集成连接器

| name | level | scope | source | description |
| --- | --- | --- | --- | --- |
| agent-browser | L1 基础Skill | 跨行业通用 | workspace_installed | Browser automation CLI for AI agents. Use when the user needs to interact with websites... |
| agile-product-owner | L1 基础Skill | 跨行业通用 | workspace_installed | Agile product ownership for backlog management and sprint execution. Covers user story ... |
| ai-contract-review-cn | L1 基础Skill | 跨行业通用 | workspace_installed | AI合同审查助手 - 智能风险提示、条款解读、合同生成、法律咨询 |
| browser | L0 原子/连接器Skill | 跨行业通用 | agent_installed | Browser automation. When you need to visit a webpage, open a website, take a screenshot... |
| byted-seedream-image-generate | L1 基础Skill | 跨行业通用 | workspace_installed | Generate high-quality images from text prompts using Volcano Engine Seedream models. Su... |
| byted-teamproject-image-generate | L1 基础Skill | 跨行业通用 | workspace_installed | Generate high-quality images from text prompts using Volcano Engine Seedream models. Su... |
| byted-text-to-speech | L0 原子/连接器Skill | 跨行业通用 | workspace_installed | 将文本合成为语音（TTS）。使用火山引擎豆包语音合成 API，支持流式合成、多种音色、语速/音调/音量调节、Markdown 过滤和 LaTeX 公式播报。当用户需要把文字转... |
| clean-pytest | L0 原子/连接器Skill | 跨行业通用 | workspace_installed | Write clean, maintainable pytest tests using Fake-based testing, contract testing, and ... |
| computer-use | L0 原子/连接器Skill | 跨行业通用 | agent_installed | CUA (Computer Use Agent) for visual GUI-based computer control + Office document automa... |
| content-creator-cn | L1 基础Skill | 跨行业通用 | workspace_installed | 中文内容创作助手 - 一键生成掘金/知乎/公众号/小红书风格文章。适合：内容创作者、自媒体运营。 |
| content-strategy | L2 组合Skill | 跨行业通用 | workspace_installed | Build and execute a content marketing strategy for a solopreneur business. Use when pla... |
| copywriter | L1 基础Skill | 跨行业通用 | workspace_installed | Write compelling UX copy, marketing content, and product messaging. Use when writing bu... |
| edge-tts | L0 原子/连接器Skill | 跨行业通用 | workspace_installed | / |
| Feishu Cloud Drive | L0 原子/连接器Skill | 跨行业通用 | workspace_installed | 基于飞书官方 API 的云盘管理技能，支持文件列表查询、上传、下载、文件夹创建、权限管理、文件搜索、统计信息、快捷方式、复制移动等完整功能。参考 feishu-drive 技... |
| feishu-doc-manager | L0 原子/连接器Skill | 跨行业通用 | agent_installed | / |
| feishu-wiki | L0 原子/连接器Skill | 跨行业通用 | agent_installed | 飞书知识库 Skill。创建知识空间、创建 Wiki 页面节点。当需要在飞书知识库中组织和沉淀文档时使用此 Skill。 |
| getdesign-md | L1 基础Skill | 行业可迁移 | workspace_installed | 从 getdesign.md 下载知名品牌/网站的设计系统文档（DESIGN.md），为前端开发提供风格参考。当需要为项目选择或应用某个品牌的设计系统风格时使用此技能。 |
| github | L0 原子/连接器Skill | 跨行业通用 | workspace_installed | Interact with GitHub using the `gh` CLI. Use `gh issue`, `gh pr`, `gh run`, and `gh api... |
| go-concurrency | L1 基础Skill | 跨行业通用 | workspace_installed | Production Go concurrency patterns — goroutines, channels, sync primitives, context, wo... |
| mlops-automation-cn | L1 基础Skill | 跨行业通用 | workspace_installed | Task automation, containerization, CI/CD, and experiment tracking |
| nano-pdf | L0 原子/连接器Skill | 跨行业通用 | workspace_installed | Edit PDF text/typos/titles via nano-pdf CLI (NL prompts). |
| newman | L0 原子/连接器Skill | 跨行业通用 | workspace_installed | Automated API testing with Postman collections via Newman CLI. Use when user requests A... |
| openclaw-docker | L1 基础Skill | 跨行业通用 | workspace_installed | Manage Docker containers and Compose projects via OpenClaw tools |
| openclaw-feishu-docs-perm-auto | L1 基础Skill | 跨行业通用 | workspace_installed | 自动为飞书文档添加用户权限。每次创建飞书文档（多维表格/文档/电子表格/文件夹/云空间文件/知识库节点等）后自动添加用户权限，或用户反馈文档无权限时补充添加权限。适用于 Op... |
| prd-developer | L1 基础Skill | 行业可迁移 | workspace_installed | 产品需求文档（PRD）开发技能。帮助产品经理从需求分析到完整PRD文档的撰写，包含用户故事、功能规格、交互设计要求和验收标准。适用于前端网页项目的需求定义和产品规划。 |
| self-improvement | L1 基础Skill | 跨行业通用 | workspace_installed | Captures learnings, errors, and corrections to enable continuous improvement. Use when:... |
| senior-devops | L1 基础Skill | 跨行业通用 | workspace_installed | Comprehensive DevOps skill for CI/CD, infrastructure automation, containerization, and ... |
| story-cog | L1 基础Skill | 行业可迁移 | workspace_installed | AI creative writing and storytelling powered by CellCog. Write novels, short stories, s... |
| video-editor | L1 基础Skill | 行业可迁移 | workspace_installed | 视频编辑器，支持合并多个视频文件、为视频添加音频轨道、合并音频、生成并烧录字幕等。 |
| vite-react-tailwind | L1 基础Skill | 行业可迁移 | workspace_installed | 使用 Vite + React + TailwindCSS v4 + lucide-react 进行前端项目搭建和开发的技能。涵盖项目初始化、组件开发、本地 Mock 数据、... |
## C10 沉淀归档与治理

| name | level | scope | source | description |
| --- | --- | --- | --- | --- |
| audit-sampling | L2 组合Skill | 跨行业通用 | private_financial | 金融AI技能 - 风险导向智能审计抽样引擎。基于监管规则和风险模型，自动生成审计抽样方案，实现抽样覆盖率≥95%的验收标准。适用于银行、证券、保险等金融机构的内部审计场景。 |
| ontology | L0 原子/连接器Skill | 跨行业通用 | workspace_installed | Typed knowledge graph for structured agent memory and composable skills. Use when creat... |
| regulatory_reporting | L2 组合Skill | 行业专用：金融 | private_financial |  |
