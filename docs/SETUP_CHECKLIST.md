# 龙马集群知识中枢 - 配置检查清单

## ✅ 已完成配置

### 1. 飞书多维表格
- [x] 创建「龙马集群知识中枢」多维表格
- [x] 创建5张表：Skill追踪、文章发布、节点状态、任务看板、每日指标
- [x] 获取 Base Token: `G1kgbpDYlaFO8DsoTE2c3vBonBh`

### 2. 飞书应用权限
- [x] Hermes 应用（cli_a9792a1a6eb8dbc1）开通 bitable 权限
- [x] 验证读取权限（GET /tables、GET /records）
- [x] 验证写入权限（POST /records、PUT /records）

### 3. 代码仓库
- [x] 创建 `feishu_base_writer.py`（多维表格写入器）
- [x] 创建 `github_stars_sync.py`（Stars同步）
- [x] 创建 `daily_metrics_cron.py`（每日汇总）
- [x] 创建 `publish_article_with_tracking.py`（文章发布记录）
- [x] 创建 `feishu_notifier.py`（群聊通知）
- [x] 删除代码中的硬编码凭证（安全修复）

### 4. GitHub Actions
- [x] 创建 `sync-stars.yml`（每6小时同步Stars）
- [x] 创建 `daily-metrics.yml`（每天00:00汇总）

---

## ⏳ 待完成配置

### 1. GitHub Secrets（必须）
在 GitHub 仓库设置中添加：
```
https://github.com/yuzhaopeng-up/financial-ai-skills/settings/secrets/actions
```

- [ ] **FEISHU_APP_ID** = `cli_a9792a1a6eb8dbc1`
- [ ] **FEISHU_APP_SECRET** = `FJsPVw6eTP4duaQKiqZt2chlxXZ7o33m`

### 2. 服务器环境变量（必须）
SSH 登录服务器后执行：
```bash
ssh root@175.24.131.184

# 编辑环境变量
nano ~/.bashrc

# 添加以下行
export FEISHU_APP_ID="cli_a9792a1a6eb8dbc1"
export FEISHU_APP_SECRET="FJsPVw6eTP4duaQKiqZt2chlxXZ7o33m"

# 生效
source ~/.bashrc

# 验证
python3 -c "import os; print('App ID:', os.environ.get('FEISHU_APP_ID', '未设置'))"
```

### 3. 飞书群聊 Webhook（可选）
如需群聊通知，配置 Webhook URL：
```bash
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxx"
```

### 4. 定时任务配置（可选）
如需服务器本地运行 Cron：
```bash
# 编辑 crontab
crontab -e

# 添加以下行
0 0 * * * cd /tmp/financial-ai-skills && python3 scripts/daily_metrics_cron.py
0 */6 * * * cd /tmp/financial-ai-skills && python3 scripts/github_stars_sync.py
```

---

## 🧪 验证测试

配置完成后，运行以下测试：

### 测试1：本地写入测试
```bash
cd /tmp/financial-ai-skills
python3 scripts/feishu_base_writer.py
```
**预期输出**：
```
✅ 连接成功
✅ 节点状态写入成功
✅ 文章发布写入成功
✅ Skill追踪写入成功
```

### 测试2：GitHub Stars 同步
```bash
cd /tmp/financial-ai-skills
python3 scripts/github_stars_sync.py
```
**预期输出**：
```
==================================================
GitHub Stars 同步工具
==================================================
🔍 获取 GitHub 数据: yuzhaopeng-up/financial-ai-skills...
   ⭐ Stars: 1
   🍴 Forks: 0
📝 同步到飞书多维表格...
✅ 更新记录: recvlJh48Jr29c
🎉 同步成功!
```

### 测试3：GitHub Actions 手动触发
1. 打开 https://github.com/yuzhaopeng-up/financial-ai-skills/actions
2. 选择「Sync GitHub Stars to Feishu」
3. 点击「Run workflow」
4. 等待运行完成（约1分钟）
5. 检查飞书多维表格「Skill追踪」表

---

## 📋 文件清单

| 文件 | 路径 | 说明 |
|------|------|------|
| 写入器 | `scripts/feishu_base_writer.py` | 核心API封装 |
| Stars同步 | `scripts/github_stars_sync.py` | GitHub→飞书 |
| 每日汇总 | `scripts/daily_metrics_cron.py` | 定时汇总 |
| 发布记录 | `scripts/publish_article_with_tracking.py` | 文章发布 |
| 群聊通知 | `scripts/feishu_notifier.py` | 消息通知 |
| Stars Action | `.github/workflows/sync-stars.yml` | 每6小时 |
| 汇总 Action | `.github/workflows/daily-metrics.yml` | 每天00:00 |
| 配置教程 | `docs/GITHUB_SECRETS_SETUP.md` | Secrets配置 |
| 检查清单 | `docs/SETUP_CHECKLIST.md` | 本文件 |

---

## 🆘 故障排查

### 问题1：获取token失败
```
获取token失败: {'code': 99991663, 'msg': 'invalid app_id or app_secret'}
```
**解决**：检查环境变量是否正确设置

### 问题2：写入记录403
```
{'code': 91403, 'msg': 'Forbidden'}
```
**解决**：应用未被添加为多维表格协作者，或权限仅为「可查看」

### 问题3：字段名不存在
```
{'code': 1254045, 'msg': 'FieldNameNotFound'}
```
**解决**：检查字段名是否与多维表格中一致（区分大小写）

### 问题4：日期格式错误
```
{'code': 1254064, 'msg': 'DatetimeFieldConvFail'}
```
**解决**：日期字段需要特定格式，建议暂时省略或使用时间戳

---

## 🎉 完成后的自动化流程

```
GitHub Push ──→ Actions ──→ 同步Stars ──→ 飞书Skill追踪表
每天00:00 ──→ Actions ──→ 汇总指标 ──→ 飞书每日指标表
发布文章 ──→ 脚本 ──→ 记录发布 ──→ 飞书文章发布表
节点心跳 ──→ ClawLink ──→ 更新状态 ──→ 飞书节点状态表
```

---

**配置完成后，龙马集群知识中枢将自动运转，无需人工干预！**

