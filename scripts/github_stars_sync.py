#!/usr/bin/env python3
"""
GitHub Stars 自动同步到飞书多维表格
用法: python github_stars_sync.py --repo yuzhaopeng-up/financial-ai-skills
"""
import argparse
import os
import sys
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from feishu_base_writer import FeishuBaseWriter


def get_github_repo_info(owner: str, repo: str) -> dict:
    """获取 GitHub 仓库信息"""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    resp = requests.get(url, timeout=15)
    if resp.status_code != 200:
        raise Exception(f"GitHub API 失败: {resp.status_code}")
    return resp.json()


def sync_stars_to_feishu(repo_full_name: str) -> dict:
    """同步 Stars 到飞书"""
    owner, repo = repo_full_name.split("/")
    
    # 获取 GitHub 数据
    print(f"🔍 获取 GitHub 数据: {repo_full_name}...")
    info = get_github_repo_info(owner, repo)
    stars = info.get("stargazers_count", 0)
    forks = info.get("forks_count", 0)
    
    print(f"   ⭐ Stars: {stars}")
    print(f"   🍴 Forks: {forks}")
    
    # 写入飞书
    print("📝 同步到飞书多维表格...")
    writer = FeishuBaseWriter()
    
    # 先搜索是否已有记录
    table_id = os.environ.get("FEISHU_TABLE_SKILL_TRACKING", "")
    if not table_id:
        print("   ⚠️ FEISHU_TABLE_SKILL_TRACKING 未设置，跳过飞书同步")
        return {"code": 0, "msg": "skipped"}
    search_result = writer._request("POST", f"/{table_id}/records/search", json={
        "filter": {
            "conjunction": "and",
            "conditions": [
                {"field_name": "Skill名称", "operator": "is", "value": repo}
            ]
        }
    })
    
    items = search_result.get("data", {}).get("items", [])
    if items:
        # 更新现有记录
        record_id = items[0]["record_id"]
        result = writer.update_skill_stars(record_id, stars, forks)
        print(f"   ✅ 更新记录: {record_id}")
    else:
        # 新建记录
        result = writer.add_skill(
            name=repo,
            repo_url=f"https://github.com/{repo_full_name}",
            stars=stars,
            forks=forks,
            responsible="KimiClaw"
        )
        print(f"   ✅ 新建记录")
    
    return result


def main():
    parser = argparse.ArgumentParser(description="同步 GitHub Stars 到飞书")
    parser.add_argument("--repo", "-r", default="yuzhaopeng-up/financial-ai-skills",
                       help="GitHub 仓库名 (格式: owner/repo)")
    args = parser.parse_args()
    
    print("=" * 50)
    print("GitHub Stars 同步工具")
    print("=" * 50)
    print()
    
    try:
        result = sync_stars_to_feishu(args.repo)
        if result.get("code") == 0:
            print("\n🎉 同步成功!")
        else:
            print(f"\n❌ 同步失败: {result.get('msg', '未知错误')}")
    except Exception as e:
        print(f"\n❌ 异常: {e}")


if __name__ == "__main__":
    main()
