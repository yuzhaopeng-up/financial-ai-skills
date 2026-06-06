# GitHub Secrets 配置教程

## 为什么需要配置 Secrets？

GitHub Actions 需要访问飞书 API 才能自动同步数据到多维表格。
由于安全原因，凭证不能硬编码在代码中，必须通过 Secrets 注入。

## 配置步骤（2分钟完成）

### Step 1: 打开 Secrets 设置页面

点击以下链接直接打开：

```
https://github.com/yuzhaopeng-up/financial-ai-skills/settings/secrets/actions
```

或手动导航：
1. 打开 GitHub 仓库首页
2. 点击顶部 **「Settings」** 标签
3. 左侧菜单选择 **「Secrets and variables」→「Actions」**

### Step 2: 添加 FEISHU_APP_ID

1. 点击绿色按钮 **「New repository secret」**
2. 填写：
   - **Name**: `FEISHU_APP_ID`
   - **Secret**: `cli_a9792a1a6eb8dbc1`
3. 点击 **「Add secret」**

```
┌─────────────────────────────────────────┐
│  New secret                             │
│                                         │
│  Name *                                 │
│  ┌─────────────────────────────────┐   │
│  │ FEISHU_APP_ID                   │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Secret *                               │
│  ┌─────────────────────────────────┐   │
│  │ cli_a9792a1a6eb8dbc1            │   │
│  └─────────────────────────────────┘   │
│                                         │
│              [ Add secret ]             │
└─────────────────────────────────────────┘
```

### Step 3: 添加 FEISHU_APP_SECRET

1. 再次点击 **「New repository secret」**
2. 填写：
   - **Name**: `FEISHU_APP_SECRET`
   - **Secret**: `FJsPVw6eTP4duaQKiqZt2chlxXZ7o33m`
3. 点击 **「Add secret」**

### Step 4: 验证配置

配置完成后，页面应显示：

```
Repository secrets
├── FEISHU_APP_ID      Updated now
└── FEISHU_APP_SECRET  Updated now
```

### Step 5: 手动触发测试

1. 打开 Actions 页面：
   ```
   https://github.com/yuzhaopeng-up/financial-ai-skills/actions
   ```

2. 选择 **「Sync GitHub Stars to Feishu」** 工作流

3. 点击右侧 **「Run workflow」** 按钮

4. 等待运行完成（约1分钟）

5. 检查飞书多维表格「Skill追踪」表，Stars 应已更新

## 常见问题

### Q1: Secret 添加后为什么不生效？
A: 需要重新触发工作流才会使用新的 Secret。

### Q2: 如何查看 Actions 运行日志？
A: 打开 Actions 页面 → 点击工作流名称 → 点击最新运行记录 → 查看日志。

### Q3: Secret 泄露了怎么办？
A: 
1. 立即在飞书开放平台重置 App Secret
2. 在 GitHub 更新 Secret 值
3. 检查仓库历史记录是否包含敏感信息

### Q4: 可以本地测试吗？
A: 可以，设置环境变量后运行：
```bash
export FEISHU_APP_ID="cli_a9792a1a6eb8dbc1"
export FEISHU_APP_SECRET="FJsPVw6eTP4duaQKiqZt2chlxXZ7o33m"
python scripts/github_stars_sync.py
```

## 安全提醒

⚠️ **永远不要将 Secret 提交到代码仓库！**

如果误提交，请立即：
1. 重置 Secret（飞书开放平台）
2. 从 Git 历史中删除（使用 `git filter-branch` 或 BFG）
3. 更新 GitHub Secrets

## 完成！

配置完成后，以下自动化将生效：

| 工作流 | 频率 | 功能 |
|--------|------|------|
| Sync GitHub Stars | 每6小时 | 自动同步 Stars/Forks 到飞书 |
| Daily Metrics | 每天00:00 | 自动汇总每日指标到飞书 |

