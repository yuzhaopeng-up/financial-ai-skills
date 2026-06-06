# 龙马集群知识中枢 - 快速上手指南

## 🎉 已完成！知识中枢已全自动运转

---

## 📊 当前状态

```
✅ 环境变量配置    ✅ Token获取      ✅ 表格访问
✅ 写入权限        ✅ GitHub API     ✅ Actions配置
```

**整体进度: 100% 完成**

---

## 🚀 立即使用

### 1. 验证配置（可选）
```bash
cd /tmp/financial-ai-skills
python3 scripts/verify_setup.py
```

### 2. 手动同步 GitHub Stars
```bash
cd /tmp/financial-ai-skills
python3 scripts/github_stars_sync.py
```

### 3. 记录文章发布
```bash
cd /tmp/financial-ai-skills
python3 scripts/publish_article_with_tracking.py \
  --article articles/series1/01.md \
  --platform 知乎 \
  --url https://zhuanlan.zhihu.com/p/xxxx
```

### 4. 更新节点状态
```python
from feishu_base_writer import record_node_heartbeat
record_node_heartbeat("KimiClaw", tasks=5, token_used=1200)
```

---

## 📅 自动运行的任务

| 任务 | 频率 | 下次运行 |
|------|------|---------|
| GitHub Stars 同步 | 每6小时 | 自动 |
| 每日指标汇总 | 每天00:00 UTC | 自动 |

**无需手动操作，全自动运行！**

---

## 📁 文件索引

| 文件 | 路径 | 用途 |
|------|------|------|
| 验证脚本 | `scripts/verify_setup.py` | 一键验证配置 |
| 写入器 | `scripts/feishu_base_writer.py` | 核心API封装 |
| Stars同步 | `scripts/github_stars_sync.py` | 手动同步Stars |
| 发布记录 | `scripts/publish_article_with_tracking.py` | 记录文章发布 |
| 群聊通知 | `scripts/feishu_notifier.py` | 发送群聊通知 |
| Stars Action | `.github/workflows/sync-stars.yml` | 自动同步Stars |
| 汇总 Action | `.github/workflows/daily-metrics.yml` | 自动汇总指标 |
| 配置教程 | `docs/GITHUB_SECRETS_SETUP.md` | Secrets配置 |
| 检查清单 | `docs/SETUP_CHECKLIST.md` | 完整检查清单 |
| 状态总结 | `docs/STATUS_SUMMARY.md` | 当前进度 |

---

## 🎯 常见使用场景

### 场景1：发布知乎文章后自动记录
```bash
# 发布文章后执行
python3 scripts/publish_article_with_tracking.py \
  --article articles/series1/01_financial_intelligence.md \
  --platform 知乎 \
  --url https://zhuanlan.zhihu.com/p/123456 \
  --author KimiClaw
```

### 场景2：手动同步GitHub数据
```bash
# 查看当前Stars
python3 scripts/github_stars_sync.py --repo yuzhaopeng-up/financial-ai-skills
```

### 场景3：在Python代码中记录数据
```python
from scripts.feishu_base_writer import FeishuBaseWriter

writer = FeishuBaseWriter()

# 添加Skill
writer.add_skill("new-skill", repo_url="https://github.com/...", responsible="KimiClaw")

# 更新节点状态
writer.update_node_status("ArkClaw", "在线", tasks=3)

# 添加任务
writer.add_task("开发新Skill", flywheel="飞轮1", priority="P0", assignee="KimiClaw")
```

---

## 📈 查看数据

### 飞书多维表格
打开飞书 → 多维表格 → 「龙马集群知识中枢」

### 各表用途
| 表名 | 用途 | 查看频率 |
|------|------|---------|
| Skill追踪 | 监控GitHub Stars/Forks | 每周 |
| 文章发布 | 记录文章发布情况 | 每次发布 |
| 节点状态 | 监控节点在线状态 | 每天 |
| 任务看板 | 跟踪任务进度 | 每天 |
| 每日指标 | 汇总每日数据 | 每天 |

---

## 🆘 故障排查

### 问题1：脚本运行失败
```bash
# 检查环境变量
python3 -c "import os; print(os.environ.get('FEISHU_APP_ID', '未设置'))"

# 运行验证脚本
python3 scripts/verify_setup.py
```

### 问题2：GitHub Actions失败
1. 检查 Secrets 是否配置正确
2. 查看 Actions 日志获取详细错误
3. 确认飞书应用权限未过期

### 问题3：数据未同步
1. 检查网络连接
2. 确认多维表格未被删除
3. 检查字段名是否匹配

---

## 📞 获取帮助

1. 查看 `docs/SETUP_CHECKLIST.md` 故障排查章节
2. 运行 `python3 scripts/verify_setup.py` 诊断问题
3. 联系 Hermes 协助排查

---

**🎉 恭喜！龙马集群知识中枢已就绪，开始享受自动化数据同步吧！**

