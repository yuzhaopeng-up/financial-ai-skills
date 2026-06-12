#!/usr/bin/env python3
"""
KPI 绩效考核 CLI
用法:
    python3 kpi_cli.py generate "绩效考核 客户经理 季度"
    python3 kpi_cli.py generate "绩效考核 柜员 月度"
    python3 kpi_cli.py list
"""

import sys
import os
import re
import json

# 添加父目录到路径，支持模块导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kpi_engine import KPIPerformanceEngine


def parse_command(text: str) -> dict:
    """
    解析自然语言命令
    支持格式：
      "绩效考核 客户经理 季度"
      "绩效考核 客户经理 零售客户经理 季度"
      "绩效考核 柜员 月度"
      "绩效考核 风控经理 季度"
      "list" / "列表"
    """
    text = text.strip()

    # 列表命令
    if text in ["list", "列表", "支持岗位"]:
        return {"action": "list"}

    # 解析 "绩效考核 岗位 [子类型] 周期"
    # 支持前缀：绩效考核、考核、绩效方案
    pattern = r"^(?:绩效考核|考核|绩效方案|kpi)[\s]+(.+?)(?:[\s]+(季度|月度))?$"
    match = re.match(pattern, text)
    if not match:
        return {"action": "error", "message": f"无法解析命令：{text}"}

    rest = match.group(1).strip()
    period = match.group(2) or "季度"

    # 解析岗位和子类型
    # 格式1: "客户经理 零售客户经理" 或 "客户经理-零售" 或 "客户经理零售"
    # 格式2: "客户经理" （自动使用默认子类型）

    # 先尝试提取周期词（季/月度）
    period_pattern = r"(.+?)(季度|月度)$"
    period_match = re.search(period_pattern, rest)
    if period_match:
        rest = period_match.group(1).strip()
        period = period_match.group(2)

    # 岗位关键词
    position_keywords = {
        "客户经理": "客户经理",
        "柜员": "柜员",
        "风控经理": "风控经理",
        "产品经理": "产品经理",
        "网点负责人": "网点负责人",
        "网点主任": "网点负责人",
        "支行行长": "网点负责人",
    }

    # 构建所有可识别的子类型列表（完整名→岗位）
    all_subs_flat = {}
    for pos, cfg in KPIPerformanceEngine.POSITION_CONFIGS.items():
        for sub in cfg["sub_types"]:
            all_subs_flat[sub] = pos

    # 子类型关键词匹配（优先精确匹配子类型，再匹配岗位）
    sub_type = None
    position = None
    remaining = rest

    # 方法1: 精确匹配已知子类型（如 "对公客户经理"）
    for sub, pos in all_subs_flat.items():
        if rest.startswith(sub) or rest == sub:
            sub_type = sub
            position = pos
            remaining = rest[len(sub):].strip()
            break

    # 方法2: 匹配岗位关键词
    if position is None:
        for kw, pos in position_keywords.items():
            if kw in remaining:
                position = pos
                remaining = remaining.replace(kw, "").strip()
                break

    if position is None:
        return {"action": "error", "message": f"未识别岗位关键词：{rest}"}

    # 子类型：优先使用精确匹配的sub_type，否则remaining就是子类型，否则用默认
    if sub_type is None:
        sub_type = remaining if remaining else None

    return {
        "action": "generate",
        "position": position,
        "sub_type": sub_type,
        "period": period,
    }


def cmd_generate(args: dict, engine: KPIPerformanceEngine, output_format: str = "text"):
    """执行生成"""
    result = engine.generate(
        position=args["position"],
        sub_type=args.get("sub_type"),
        period=args["period"],
        format=output_format,
    )

    if isinstance(result, dict) and result.get("error"):
        print(f"❌ 错误：{result['message']}", file=sys.stderr)
        sys.exit(1)

    if output_format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result)


def cmd_list(engine: KPIPerformanceEngine):
    """列出所有支持的岗位"""
    info = engine.list_positions()
    print("支持岗位列表：")
    print("-" * 40)
    for pos, subs in info["position_configs"].items():
        print(f"  {pos}: {', '.join(subs)}")
    print("-" * 40)
    print(f"支持周期: {', '.join(engine.supported_periods)}")


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 kpi_cli.py generate \"绩效考核 客户经理 季度\"")
        print("  python3 kpi_cli.py generate \"绩效考核 柜员 月度\"")
        print("  python3 kpi_cli.py list")
        sys.exit(1)

    action = sys.argv[1]

    if action == "generate" and len(sys.argv) >= 3:
        query = sys.argv[2]
        output_format = "text"
        if len(sys.argv) >= 4 and sys.argv[3] == "--json":
            output_format = "json"

        parsed = parse_command(query)
        if parsed.get("action") == "error":
            print(f"❌ {parsed['message']}", file=sys.stderr)
            sys.exit(1)

        engine = KPIPerformanceEngine()
        cmd_generate(parsed, engine, output_format)

    elif action in ("list", "列表"):
        engine = KPIPerformanceEngine()
        cmd_list(engine)

    else:
        # 尝试直接解析（兼容无generate子命令的用法）
        engine = KPIPerformanceEngine()
        parsed = parse_command(action + " " + " ".join(sys.argv[2:]) if len(sys.argv) > 2 else action)
        if parsed.get("action") == "error":
            print(f"❌ {parsed['message']}", file=sys.stderr)
            sys.exit(1)
        cmd_generate(parsed, engine)


if __name__ == "__main__":
    main()
