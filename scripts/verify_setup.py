#!/usr/bin/env python3
"""
龙马集群知识中枢 - 一键验证脚本
运行: python verify_setup.py
"""
import os
import sys
import requests
from datetime import datetime

# 颜色输出
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def check_env():
    """检查环境变量"""
    print("=" * 60)
    print("🔍 检查环境变量")
    print("=" * 60)
    
    app_id = os.environ.get("FEISHU_APP_ID", "")
    app_secret = os.environ.get("FEISHU_APP_SECRET", "")
    
    if not app_id:
        print(f"{RED}❌ FEISHU_APP_ID 未设置{RESET}")
        return False
    else:
        print(f"{GREEN}✅ FEISHU_APP_ID 已设置 ({app_id[:15]}...){RESET}")
    
    if not app_secret:
        print(f"{RED}❌ FEISHU_APP_SECRET 未设置{RESET}")
        return False
    else:
        print(f"{GREEN}✅ FEISHU_APP_SECRET 已设置 ({app_secret[:5]}...{app_secret[-5:]}){RESET}")
    
    return True

def check_token():
    """检查飞书Token获取"""
    print("\n" + "=" * 60)
    print("🔍 检查飞书Token获取")
    print("=" * 60)
    
    app_id = os.environ.get("FEISHU_APP_ID")
    app_secret = os.environ.get("FEISHU_APP_SECRET")
    
    try:
        resp = requests.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"app_id": app_id, "app_secret": app_secret},
            timeout=10
        )
        data = resp.json()
        
        if data.get("code") == 0:
            print(f"{GREEN}✅ Token获取成功 ({data['tenant_access_token'][:20]}...){RESET}")
            return data["tenant_access_token"]
        else:
            print(f"{RED}❌ Token获取失败: {data.get('msg', '未知错误')}{RESET}")
            return None
    except Exception as e:
        print(f"{RED}❌ 异常: {e}{RESET}")
        return None

def check_tables(token):
    """检查多维表格访问"""
    print("\n" + "=" * 60)
    print("🔍 检查多维表格访问")
    print("=" * 60)
    
    base_token = os.environ.get("FEISHU_BASE_TOKEN", "")
    if not base_token:
        print(f"{RED}❌ FEISHU_BASE_TOKEN 未设置{RESET}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        resp = requests.get(
            f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_token}/tables",
            headers=headers, timeout=10
        )
        data = resp.json()
        
        if data.get("code") == 0:
            items = data.get("data", {}).get("items", [])
            print(f"{GREEN}✅ 成功访问多维表格，发现 {len(items)} 张表:{RESET}")
            for item in items:
                print(f"   - {item.get('name', 'N/A')}")
            return True
        else:
            print(f"{RED}❌ 访问失败: {data.get('msg', '未知错误')}{RESET}")
            return False
    except Exception as e:
        print(f"{RED}❌ 异常: {e}{RESET}")
        return False

def check_write(token):
    """检查写入权限"""
    print("\n" + "=" * 60)
    print("🔍 检查写入权限")
    print("=" * 60)
    
    base_token = os.environ.get("FEISHU_BASE_TOKEN", "")
    table_id = os.environ.get("FEISHU_TABLE_NODE_STATUS", "")
    
    if not base_token:
        print(f"{RED}❌ FEISHU_BASE_TOKEN 未设置{RESET}")
        return False
    if not table_id:
        print(f"{RED}❌ FEISHU_TABLE_NODE_STATUS 未设置{RESET}")
        return False
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        resp = requests.post(
            f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_token}/tables/{table_id}/records",
            headers=headers,
            json={
                "fields": {
                    "节点": "Hermes_Brain",
                    "在线状态": "在线",
                    "今日任务数": 0,
                    "备注": f"验证测试 {datetime.now().strftime('%H:%M')}"
                }
            },
            timeout=10
        )
        data = resp.json()
        
        if data.get("code") == 0:
            print(f"{GREEN}✅ 写入权限正常{RESET}")
            return True
        else:
            print(f"{RED}❌ 写入失败: {data.get('msg', '未知错误')}{RESET}")
            return False
    except Exception as e:
        print(f"{RED}❌ 异常: {e}{RESET}")
        return False

def check_github():
    """检查GitHub API访问"""
    print("\n" + "=" * 60)
    print("🔍 检查GitHub API访问")
    print("=" * 60)
    
    try:
        resp = requests.get(
            "https://api.github.com/repos/yuzhaopeng-up/financial-ai-skills",
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"{GREEN}✅ GitHub API访问正常{RESET}")
            print(f"   Stars: {data.get('stargazers_count', 0)}")
            print(f"   Forks: {data.get('forks_count', 0)}")
            return True
        else:
            print(f"{YELLOW}⚠️ GitHub API返回: {resp.status_code}{RESET}")
            return True  # 不影响核心功能
    except Exception as e:
        print(f"{YELLOW}⚠️ GitHub API异常: {e}{RESET}")
        return True  # 不影响核心功能

def main():
    print("\n" + "=" * 60)
    print("🚀 龙马集群知识中枢 - 一键验证")
    print("=" * 60)
    
    results = []
    
    # 检查环境变量
    results.append(("环境变量", check_env()))
    
    # 获取Token
    token = check_token()
    if not token:
        results.append(("Token获取", False))
        print(f"\n{RED}❌ 验证失败: 无法获取Token，后续检查跳过{RESET}")
    else:
        results.append(("Token获取", True))
        
        # 检查表格访问
        results.append(("表格访问", check_tables(token)))
        
        # 检查写入权限
        results.append(("写入权限", check_write(token)))
    
    # 检查GitHub
    results.append(("GitHub API", check_github()))
    
    # 汇总
    print("\n" + "=" * 60)
    print("📊 验证结果汇总")
    print("=" * 60)
    
    for name, result in results:
        status = f"{GREEN}✅ 通过{RESET}" if result else f"{RED}❌ 失败{RESET}"
        print(f"{name:12s} {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print("\n" + "=" * 60)
    if passed == total:
        print(f"{GREEN}🎉 全部通过！知识中枢已就绪！{RESET}")
    else:
        print(f"{YELLOW}⚠️ {passed}/{total} 项通过，请检查失败项{RESET}")
    print("=" * 60)

if __name__ == "__main__":
    main()
