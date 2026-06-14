# GitHub 仓库导入指南

## 由于网络限制，请使用以下方式导入代码

### 方法1: 使用 Git Bundle（推荐）

1. 下载 `financial-ai-skills.bundle` 文件
2. 在本地执行：
```bash
# 从bundle创建仓库
git clone financial-ai-skills.bundle financial-ai-skills
cd financial-ai-skills

# 添加GitHub远程仓库
git remote add origin https://github.com/yuzhaopeng-up/financial-ai-skills.git

# 推送
 git push -u origin master
```

### 方法2: 手动上传

1. 在GitHub创建空仓库 `financial-ai-skills`
2. 下载本目录所有文件
3. 上传到GitHub仓库

### 方法3: 使用GitHub CLI

```bash
gh repo create yuzhaopeng-up/financial-ai-skills --public
gh repo clone yuzhaopeng-up/financial-ai-skills
cd financial-ai-skills
# 复制本目录文件到此
git add -A
git commit -m "Initial release v1.0.0"
git push
```

---

## 仓库内容清单

```
financial-ai-skills/
├── README.md              # 中英文双语README
├── LICENSE                # MIT协议
├── requirements.txt       # Python依赖
├── setup.py              # 安装配置
├── .gitignore
├── IMPORT_INSTRUCTIONS.md # 本文件
├── examples/
│   └── invoice_example.py # 使用示例
├── scripts/
│   └── github_metrics_tracker.py  # Stars追踪
└── skills/
    └── financial-intelligence/
        ├── engines/        # 8大引擎
        │   ├── __init__.py
        │   ├── invoice_engine.py
        │   ├── budget_engine.py
        │   ├── report_engine.py
        │   ├── tax_engine.py
        │   ├── expense_engine.py
        │   └── cashflow_engine.py
        ├── formatters/     # 格式化器
        │   ├── __init__.py
        │   ├── base_formatter.py
        │   └── financial_formatter.py
        └── scripts/
            └── financial_cli.py
```

---

## 发布后的配置

### 启用Stars追踪

```bash
# 初始化数据库
python scripts/github_metrics_tracker.py --init

# 每日定时运行（crontab）
0 9 * * * cd /path/to/repo && python scripts/github_metrics_tracker.py --daily
```

### 生成趋势图表

```bash
python scripts/github_metrics_tracker.py --chart
# 输出: docs/stars_chart.html
```

---

*龙马集群出品 | Financial AI Contributors*
