#!/usr/bin/env python3
"""
龙马集群知识中枢 - 飞书多维表格自动写入器
app_token: G1kgbpDYlaFO8DsoTE2c3vBonBh

使用 Hermes 飞书应用凭证（已开通 bitable 权限）
"""
import os
import requests
from datetime import datetime
from typing import Dict, List, Optional

# 飞书应用凭证（从环境变量读取）
FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
BASE_TOKEN = "G1kgbpDYlaFO8DsoTE2c3vBonBh"

# 表ID映射（ArkClaw已创建）
TABLE_IDS = {
    "skill_tracking": "tblqnknKfbFfLBzn",      # Skill追踪
    "article_publish": "tblRU0knKUahGzm5",      # 文章发布
    "node_status": "tblY6mT9YCnwrmo0",          # 节点状态
    "task_board": "tblAhofAW6ehXqKJ",           # 任务看板
    "daily_metrics": "tblFFP8qTWOn0SAN",        # 每日指标
}


class FeishuBaseWriter:
    """飞书多维表格写入器"""
    
    def __init__(self):
        self.app_token = BASE_TOKEN
        self.tenant_access_token = self._get_tenant_access_token()
    
    def _get_tenant_access_token(self) -> str:
        """获取租户访问令牌"""
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        resp = requests.post(url, json={
            "app_id": FEISHU_APP_ID,
            "app_secret": FEISHU_APP_SECRET
        }, timeout=10)
        data = resp.json()
        if data.get("code") != 0:
            raise Exception(f"获取token失败: {data}")
        return data["tenant_access_token"]
    
    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """统一请求封装"""
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.app_token}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json"
        }
        resp = requests.request(method, url, headers=headers, timeout=15, **kwargs)
        return resp.json()
    
    # ==================== Skill追踪表 ====================
    
    def add_skill(self, name: str, repo_url: str = "", stars: int = 0, 
                  forks: int = 0, pv: int = 0, responsible: str = "",
                  status: str = "开发中", note: str = "") -> dict:
        """添加Skill记录"""
        table_id = TABLE_IDS["skill_tracking"]
        
        fields = {
            "Skill名称": name,
            "GitHub Stars": stars,
            "Forks": forks,
            "PV": pv,
            "负责节点": responsible,
            "状态": status,
            "备注": note
        }
        
        # 链接字段特殊格式
        if repo_url:
            fields["仓库URL"] = {"text": repo_url, "link": repo_url}
        
        return self._request("POST", f"/{table_id}/records", json={"fields": fields})
    
    def update_skill_stars(self, record_id: str, stars: int, forks: int) -> dict:
        """更新Skill Stars（Cron任务用）"""
        table_id = TABLE_IDS["skill_tracking"]
        return self._request("PUT", f"/{table_id}/records/{record_id}", json={
            "fields": {
                "GitHub Stars": stars,
                "Forks": forks
            }
        })
    
    # ==================== 文章发布表 ====================
    
    def add_article(self, title: str, platform: str, url: str = "",
                    author: str = "Hermes", status: str = "已发布") -> dict:
        """添加文章发布记录"""
        table_id = TABLE_IDS["article_publish"]
        
        fields = {
            "标题": title,
            "平台": platform,
            "阅读量": 0,
            "点赞": 0,
            "收藏": 0,
            "作者节点": author,
            "状态": status
        }
        
        # 链接字段特殊格式
        if url:
            fields["链接"] = {"text": url, "link": url}
        
        return self._request("POST", f"/{table_id}/records", json={"fields": fields})
    
    def update_article_metrics(self, record_id: str, 
                                views: int, likes: int, bookmarks: int) -> dict:
        """更新文章数据指标"""
        table_id = TABLE_IDS["article_publish"]
        return self._request("PUT", f"/{table_id}/records/{record_id}", json={
            "fields": {
                "阅读量": views,
                "点赞": likes,
                "收藏": bookmarks
            }
        })
    
    # ==================== 节点状态表 ====================
    
    def update_node_status(self, node_name: str, status: str = "在线",
                           last_seen: str = "", tasks: int = 0,
                           token_used: int = 0, note: str = "") -> dict:
        """更新节点状态"""
        table_id = TABLE_IDS["node_status"]
        
        # 先查询是否已有记录
        search_result = self._request("POST", f"/{table_id}/records/search", json={
            "filter": {
                "conjunction": "and",
                "conditions": [
                    {"field_name": "节点", "operator": "is", "value": node_name}
                ]
            }
        })
        
        fields = {
            "节点": node_name,
            "在线状态": status,
            "今日任务数": tasks,
            "本周任务数": 0,  # 简化处理
            "主机/IP": "",
            "备注": note
        }
        
        items = search_result.get("data", {}).get("items", [])
        if items:
            # 更新现有记录
            record_id = items[0]["record_id"]
            return self._request("PUT", f"/{table_id}/records/{record_id}", json={"fields": fields})
        else:
            # 新建记录
            return self._request("POST", f"/{table_id}/records", json={"fields": fields})
    
    # ==================== 任务看板表 ====================
    
    def add_task(self, task_name: str, flywheel: str = "飞轮1",
                 priority: str = "P1", assignee: str = "",
                 deadline: str = "", status: str = "待开始") -> dict:
        """添加任务"""
        table_id = TABLE_IDS["task_board"]
        return self._request("POST", f"/{table_id}/records", json={
            "fields": {
                "任务名称": task_name,
                "所属飞轮": flywheel,
                "优先级": priority,
                "负责人": assignee,
                "截止日期": deadline,
                "状态": status
            }
        })
    
    def update_task_status(self, record_id: str, status: str) -> dict:
        """更新任务状态"""
        table_id = TABLE_IDS["task_board"]
        return self._request("PUT", f"/{table_id}/records/{record_id}", json={
            "fields": {"状态": status}
        })
    
    # ==================== 每日指标表 ====================
    
    def add_daily_metrics(self, date: str, skill_pushes: int = 0,
                          articles: int = 0, active_nodes: int = 0,
                          github_stars: int = 0, wecom_users: int = 0,
                          zhihu_views: int = 0, note: str = "") -> dict:
        """添加每日指标"""
        table_id = TABLE_IDS["daily_metrics"]
        return self._request("POST", f"/{table_id}/records", json={
            "fields": {
                "日期": date,
                "Skill提交数": skill_pushes,
                "文章发布数": articles,
                "活跃节点数": active_nodes,
                "GitHub新增Stars": github_stars,
                "企微端用户数": wecom_users,
                "知乎阅读量": zhihu_views,
                "备注": note
            }
        })


# ==================== 快捷函数（供其他脚本调用） ====================

def record_skill_push(name: str, repo_url: str = "", responsible: str = "") -> dict:
    """记录Skill提交（供GitHub Action调用）"""
    writer = FeishuBaseWriter()
    return writer.add_skill(name, repo_url=repo_url, responsible=responsible)


def record_article_publish(title: str, platform: str, url: str = "", author: str = "") -> dict:
    """记录文章发布（供发布脚本调用）"""
    writer = FeishuBaseWriter()
    return writer.add_article(title, platform, url, author)


def record_node_heartbeat(node_name: str, tasks: int = 0, token_used: int = 0) -> dict:
    """记录节点心跳（供ClawLink调用）"""
    writer = FeishuBaseWriter()
    return writer.update_node_status(node_name, "在线", 
                                      datetime.now().strftime("%Y-%m-%d %H:%M"),
                                      tasks, token_used)


def record_daily_summary() -> dict:
    """记录每日汇总（供Cron调用）"""
    writer = FeishuBaseWriter()
    today = datetime.now().strftime("%Y-%m-%d")
    # TODO: 从各表统计实际数据
    return writer.add_daily_metrics(today)


if __name__ == "__main__":
    # 测试写入
    print("=== 飞书多维表格写入器测试 ===")
    print(f"App ID: {FEISHU_APP_ID}")
    print(f"Base Token: {BASE_TOKEN}")
    print()
    
    try:
        writer = FeishuBaseWriter()
        print("✅ 连接成功")
        
        # 测试写入节点状态
        result = writer.update_node_status("Hermes_Brain", "在线", tasks=3, note="自动测试")
        if result.get("code") == 0:
            print("✅ 节点状态写入成功")
        else:
            print(f"❌ 节点状态写入失败: {result.get('msg', '未知错误')}")
        
        # 测试写入文章发布
        result = writer.add_article("测试文章", "知乎", "https://zhuanlan.zhihu.com/p/test", "Hermes")
        if result.get("code") == 0:
            print("✅ 文章发布写入成功")
        else:
            print(f"❌ 文章发布写入失败: {result.get('msg', '未知错误')}")
        
        # 测试写入Skill
        result = writer.add_skill("test-skill", "https://github.com/test", responsible="KimiClaw")
        if result.get("code") == 0:
            print("✅ Skill追踪写入成功")
        else:
            print(f"❌ Skill追踪写入失败: {result.get('msg', '未知错误')}")
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
