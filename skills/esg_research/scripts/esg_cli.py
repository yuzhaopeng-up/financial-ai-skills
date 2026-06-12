#!/usr/bin/env python3
"""
ESG CLI - ESG研究命令行工具
用法：
  python3 scripts/esg_cli.py generate "ESG研究 某新能源龙头企业"
  python3 scripts/esg_cli.py generate "ESG分析 某股份制银行" --format=markdown
  python3 scripts/esg_cli.py list
  python3 scripts/esg_cli.py search "白酒"
"""

import sys
import os
import argparse
import json

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from esg_engine import ESGEngine


def cmd_generate(engine: ESGEngine, args):
    """生成ESG报告"""
    # 解析命令格式："ESG研究 XXX" 或 "ESG分析 XXX"
    query = args.query
    for prefix in ["ESG研究", "ESG分析", "ESG查询", "esg研究", "esg分析"]:
        if query.startswith(prefix):
            company = query[len(prefix):].strip()
            break
    else:
        company = query.strip()

    if not company:
        print("错误：请提供公司名称，如：ESG研究 某新能源龙头企业")
        sys.exit(1)

    fmt = args.format or "text"
    output_file = args.output

    result = engine.generate_report(company)

    if "error" in result and "available_companies" in result:
        print(f"❌ {result['error']}")
        print("\n当前内置公司列表（前30家）：")
        for i, c in enumerate(result["available_companies"][:30], 1):
            print(f"  {i:>2}. {c}")
        sys.exit(1)

    content = engine.format_report(result, format=fmt)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ 报告已保存至：{output_file}")
    else:
        print(content)

    # 同时输出JSON结构（便于后续程序解析）
    if not args.no_json:
        scores = result.get("scores", {})
        print(f"\n--- JSON SCORES ---")
        print(json.dumps(scores, ensure_ascii=False))


def cmd_list(engine: ESGEngine, args):
    """列出所有公司"""
    if args.industry:
        companies = [c for c in engine.list_companies()
                   if engine.data[c].get("industry") == args.industry]
        print(f"行业「{args.industry}」下公司（共{len(companies)}家）：")
    else:
        companies = engine.list_companies()
        print(f"ESG内置数据库（共{len(companies)}家公司）：")

    for c in companies:
        if args.industry:
            data = engine.data[c]
            print(f"  • {c} | {data.get('rating', 'N/A')} | 综合{data['overall']} | "
                  f"E:{data['e']['score']} S:{data['s']['score']} G:{data['g']['score']}")
        else:
            print(f"  • {c}")


def cmd_search(engine: ESGEngine, args):
    """搜索公司"""
    keyword = args.keyword
    results = []
    for name, data in engine.data.items():
        if keyword in name or keyword in data.get("industry", ""):
            results.append((name, data))
    if results:
        print(f"找到 {len(results)} 个匹配「{keyword}」的结果：")
        for name, data in results:
            print(f"  • {name} | {data.get('rating', 'N/A')} | 综合{data['overall']} | "
                  f"E:{data['e']['score']} S:{data['s']['score']} G:{data['g']['score']}")
    else:
        print(f"未找到包含「{keyword}」的公司")


def cmd_industries(engine: ESGEngine, args):
    """列出所有行业"""
    industries = engine.list_industries()
    print(f"ESG数据库涵盖 {len(industries)} 个行业：")
    for ind in industries:
        count = sum(1 for d in engine.data.values() if d.get("industry") == ind)
        avg_score = sum(engine.data[n]["overall"] for n in engine.data
                       if engine.data[n].get("industry") == ind) / max(count, 1)
        print(f"  • {ind}（{count}家，平均ESG {avg_score:.0f}分）")


def main():
    parser = argparse.ArgumentParser(
        description="ESG研究工具 - 中国上市公司ESG评分分析",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # generate
    p_gen = subparsers.add_parser("generate", help="生成ESG报告")
    p_gen.add_argument("query", help="查询内容，如：ESG研究 某新能源龙头企业")
    p_gen.add_argument("--format", "-f", choices=["text", "json", "markdown"],
                       default="text", help="输出格式")
    p_gen.add_argument("--output", "-o", help="输出文件路径")
    p_gen.add_argument("--no-json", action="store_true", help="不输出JSON分数")

    # list
    p_list = subparsers.add_parser("list", help="列出所有公司")
    p_list.add_argument("--industry", "-i", help="按行业筛选")

    # search
    p_search = subparsers.add_parser("search", help="搜索公司")
    p_search.add_argument("keyword", help="搜索关键词（公司名或行业）")

    # industries
    p_ind = subparsers.add_parser("industries", help="列出所有行业")

    args = parser.parse_args()
    engine = ESGEngine()

    if args.command == "generate":
        cmd_generate(engine, args)
    elif args.command == "list":
        cmd_list(engine, args)
    elif args.command == "search":
        cmd_search(engine, args)
    elif args.command == "industries":
        cmd_industries(engine, args)
    else:
        # 默认：generate（兼容直接传入公司名）
        if len(sys.argv) > 1:
            args2 = argparse.Namespace(
                query=sys.argv[1],
                format="text",
                output=None,
                no_json=False
            )
            cmd_generate(engine, args2)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
