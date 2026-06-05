# Financial AI Skills

> 龙马集群金融 AI Skill 生态公共仓库
>
> 仅包含**脱敏后**的 Skill 代码，供社区学习、复用与共建。

## 仓库定位

本仓库是 [龙马集群](https://github.com/yuzhaopeng-up/openclaw-workspace) 的**公共技能发布端**，与私有仓库严格分离：

| 维度 | 本仓库（Public） | 私有仓库（Private） |
|------|----------------|-------------------|
| 内容 | 脱敏 Skill 代码、通用模板 | 内部成果、敏感数据、完整文档 |
| 目的 | 社区共建、品牌展示 | 内部协作、资产保护 |
| 访问 | 全网公开 | 仅集群成员 |

## 目录结构

```
├── skills/
│   ├── wealth-management/      # 财富管理 Skill
│   ├── risk-compliance/        # 风控合规 Skill
│   ├── financial-planning/     # 财务规划 Skill
│   └── retail-marketing/       # 零售营销 Skill
├── templates/
│   └── skill-template/         # 新建 Skill 的脚手架模板
├── docs/
│   ├── CONTRIBUTING.md         # 贡献指南
│   └── SKILL_SPEC.md           # Skill 编写规范
├── .github/
│   └── workflows/              # CI / 自动化检查
├── LICENSE
└── README.md
```

## 快速开始

### 使用现有 Skill

每个 Skill 目录包含独立的 `SKILL.md` 和可运行代码，直接复制到 Hermes Agent 的 `~/.hermes/skills/` 目录即可使用。

```bash
# 示例：使用财富管理 Skill
cp -r skills/wealth-management ~/.hermes/skills/
```

### 贡献新 Skill

1. 阅读 [SKILL_SPEC.md](docs/SKILL_SPEC.md) 了解规范
2. 使用 [templates/skill-template](templates/skill-template) 脚手架创建
3. 确保所有数据已脱敏，无内部敏感信息
4. 提交 PR，等待审核

## 核心原则

- **脱敏优先**：绝不包含任何内部敏感数据、客户信息、未公开策略
- **可运行**：每个 Skill 必须提供可验证的最小可用示例
- **文档完整**：必须包含 `SKILL.md`、使用说明、依赖清单
- **版本兼容**：标注测试通过的 Hermes Agent 版本

## 许可证

[MIT License](LICENSE) — 自由使用、修改、分发，保留署名。

---

*由龙马集群维护 | 以真实用户反馈为唯一北极星指标*
