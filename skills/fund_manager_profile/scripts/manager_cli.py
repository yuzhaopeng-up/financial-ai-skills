#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基金经理画像 CLI
Usage:
    python3 scripts/manager_cli.py generate "基金经理画像 张坤"
    python3 scripts/manager_cli.py generate "经理分析 朱少醒"
    python3 scripts/manager_cli.py list
    python3 scripts/manager_cli.py summary
    python3 scripts/manager_cli.py search "张坤"
"""

import sys
import os
import re
import argparse

# 确保可导入上级目录的 manager_engine
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from manager_engine import FundManagerEngine


def extract_name_from_query(query: str) -> str:
    """
    从自然语言查询中提取基金经理姓名
    支持格式：
    - 基金经理画像 张坤
    - 经理分析 朱少醒
    - 查询 张坤
    - 张坤的画像
    - 基金经理 张坤
    """
    query = query.strip()

    # 去除常见前缀
    prefixes = [
        "基金经理画像", "经理分析", "查询", "查一下", "看看",
        "基金经理", "经理画像", "查询基金经理", "查基金经理",
        "给我查一下", "生成", "分析",
    ]
    for prefix in prefixes:
        if query.startswith(prefix):
            query = query[len(prefix):].strip()

    # 去除"的画像"、"的简介"等后缀
    suffixes = ["的画像", "的简介", "的情况", "的资料", "的信息"]
    for suffix in suffixes:
        if query.endswith(suffix):
            query = query[:-len(suffix)].strip()

    return query.strip()


def cmd_generate(engine: FundManagerEngine, query: str) -> str:
    """生成基金经理画像"""
    name = extract_name_from_query(query)
    if not name:
        return "❌ 无法从查询中识别基金经理姓名，请明确说明要查询的基金经理，如：基金经理画像 张坤"
    return engine.get_profile(name)


def cmd_list(engine: FundManagerEngine) -> str:
    """列出所有基金经理"""
    managers = engine.list_managers()
    lines = ["📋 当前支持的基金经理列表（共{}位）：".format(len(managers)), ""]
    for i, name in enumerate(managers, 1):
        data = engine.managers[name]
        company = data["fund_company"].replace("基金管理有限公司", "").replace("股份有限公司", "").replace("有限公司", "")
        scale = data["management_scale_bn"]
        style = " / ".join(data["investment_style"][:2])
        lines.append(f"  {i:2d}. {name}（{company}，~{scale}亿，{style}）")
    lines.append("")
    lines.append(f"使用 `python3 scripts/manager_cli.py generate \"基金经理画像 张坤\"` 查询具体画像")
    return "\n".join(lines)


def cmd_summary(engine: FundManagerEngine) -> str:
    """输出基金经理汇总对比表"""
    return engine.get_summary_table()


def cmd_search(engine: FundManagerEngine, name: str) -> str:
    """搜索基金经理"""
    matched = engine.search_manager(name)
    if matched:
        data = engine.managers[matched]
        return (
            f"✅ 找到基金经理：{data['name']}\n"
            f"   公司：{data['fund_company']}\n"
            f"   从业：{data['experience_years']}年\n"
            f"   规模：~{data['management_scale_bn']}亿元\n"
            f"   风格：{' / '.join(data['investment_style'])}\n"
            f"   代表：{data['representative_fund']}\n\n"
            f"完整画像：python3 scripts/manager_cli.py generate \"基金经理画像 {data['name']}\""
        )
    else:
        return f"❌ 未找到基金经理「{name}」，请检查姓名是否正确。"


def main():
    parser = argparse.ArgumentParser(
        description="基金经理画像查询工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python3 scripts/manager_cli.py generate "基金经理画像 张坤"
  python3 scripts/manager_cli.py generate "经理分析 朱少醒"
  python3 scripts/manager_cli.py list
  python3 scripts/manager_cli.py summary
  python3 scripts/manager_cli.py search "张坤"
        """
    )
    parser.add_argument("command", nargs="?", default="generate",
                        help="子命令：generate/list/summary/search")
    parser.add_argument("query", nargs="?", default="", help="查询内容或基金经理姓名")
    parser.add_argument("--format", "-f", choices=["text", "markdown", "json"],
                        default="markdown", help="输出格式（仅generate有效）")

    args = parser.parse_args()
    engine = FundManagerEngine()

    # 兼容：没有子命令时，默认当作 generate
    command = args.command
    query = args.query

    if command == "list":
        print(cmd_list(engine))
    elif command == "summary":
        print(cmd_summary(engine))
    elif command == "search":
        if not query:
            print("❌ search 命令需要提供基金经理姓名，如：search 张坤")
            sys.exit(1)
        print(cmd_search(engine, query))
    elif command == "generate":
        if not query:
            print("❌ generate 命令需要提供查询内容，如：generate \"基金经理画像 张坤\"")
            sys.exit(1)
        profile = cmd_generate(engine, query)
        # 检测是否是"未找到"错误信息
        if profile.startswith("❌"):
            print(profile)
            sys.exit(1)
        print(profile)
    else:
        # 兼容：直接传入基金经理姓名（无子命令）
        if command not in ("generate", "list", "summary", "search"):
            # 可能是直接传了查询内容
            profile = cmd_generate(engine, command)
            print(profile)
            if profile.startswith("❌"):
                sys.exit(1)


if __name__ == "__main__":
    main()
