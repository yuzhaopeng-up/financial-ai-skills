#!/usr/bin/env python3
"""
operational_risk CLI - 操作风险管理命令行工具

用法：
    python3 scripts/oprisk_cli.py generate "操作风险 内部欺诈 损失200万 未遂"
    python3 scripts/oprisk_cli.py generate "操作风险 系统故障 损失500万 偶尔" --format=json
    python3 scripts/oprisk_cli.py batch data.csv
    python3 scripts/oprisk_cli.py interactive
"""

import argparse
import csv
import json
import sys
import os
from pathlib import Path

# 将 skills 目录加入路径，以便直接导入引擎
SCRIPT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

# 动态构建 operational_risk 路径
OPERATIONAL_RISK_PATH = SCRIPT_DIR / "operational_risk"
sys.path.insert(0, str(OPERATIONAL_RISK_PATH))

from op_risk_engine import OperationalRiskEngine


def cmd_generate(args) -> int:
    """生成操作风险评估"""
    engine = OperationalRiskEngine()

    # 解析输入
    parsed = engine.parse_cli_input(args.input)

    # 执行分析
    result = engine.analyze(
        scenario=parsed["scenario"],
        loss_amount=parsed["loss_amount"],
        frequency=parsed["frequency"],
        operator=parsed["operator"],
        category_override=parsed["category_override"],
    )

    # 输出
    if args.format == "json":
        output = {
            "category": result.category,
            "category_code": result.category_code,
            "risk_matrix": {
                "possibility": result.risk_matrix.possibility,
                "impact": result.risk_matrix.impact,
                "score": result.risk_matrix.score,
                "level": result.risk_matrix.level,
            },
            "loss_estimate": {
                "direct": result.loss_estimate.direct,
                "indirect": result.loss_estimate.indirect,
                "regulatory_fine": result.loss_estimate.regulatory_fine,
                "total": result.loss_estimate.total,
            },
            "controls": {
                "preventive": result.controls.preventive,
                "detective": result.controls.detective,
                "corrective": result.controls.corrective,
            },
            "risk_level": result.risk_level,
            "next_action": result.next_action,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(result.summary())

    return 0


def cmd_batch(args) -> int:
    """批量分析 CSV 文件"""
    engine = OperationalRiskEngine()

    if not os.path.exists(args.csv_file):
        print(f"错误：文件不存在 → {args.csv_file}", file=sys.stderr)
        return 1

    results = []
    with open(args.csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed = engine.parse_cli_input(row.get("scenario", ""))
            result = engine.analyze(
                scenario=parsed["scenario"],
                loss_amount=parsed["loss_amount"],
                frequency=parsed["frequency"],
                operator=parsed["operator"],
                category_override=parsed["category_override"],
            )
            results.append(result)

    # 输出汇总
    print(f"\n{'='*60}")
    print(f"批量分析完成：共 {len(results)} 条记录")
    print(f"{'='*60}\n")

    for i, r in enumerate(results, 1):
        print(f"[{i}] {r.category}（{r.category_code}）| "
              f"风险{r.risk_level} | 评分{r.risk_matrix.score} | "
              f"损失估算{r.loss_estimate.total:.1f}万元")
        print(f"     处置：{r.next_action}")
        print()

    # 可选：保存 JSON 结果
    if args.output:
        out_data = [
            {
                "category": r.category,
                "category_code": r.category_code,
                "risk_level": r.risk_level,
                "score": r.risk_matrix.score,
                "loss_total": r.loss_estimate.total,
                "next_action": r.next_action,
            }
            for r in results
        ]
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(out_data, f, ensure_ascii=False, indent=2)
        print(f"结果已保存至：{args.output}")

    return 0


def cmd_interactive(args) -> int:
    """交互式分析模式"""
    engine = OperationalRiskEngine()
    print("=" * 60)
    print("操作风险管理 - 交互式分析")
    print("输入业务场景描述，按回车分析，输入 'quit' 退出")
    print("=" * 60)
    print()

    while True:
        try:
            line = input("场景描述> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n退出。")
            break

        if line.lower() in ["quit", "q", "exit"]:
            print("退出。")
            break

        if not line:
            continue

        parsed = engine.parse_cli_input(line)
        result = engine.analyze(
            scenario=parsed["scenario"],
            loss_amount=parsed["loss_amount"],
            frequency=parsed["frequency"],
            operator=parsed["operator"],
            category_override=parsed["category_override"],
        )
        print()
        print(result.summary())
        print()


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="oprisk_cli.py",
        description="操作风险管理（Operational Risk）命令行工具",
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # generate 子命令
    gen_parser = subparsers.add_parser(
        "generate", help="生成单条操作风险评估"
    )
    gen_parser.add_argument(
        "input",
        help="业务场景描述，支持格式：'操作风险 内部欺诈 损失200万 未遂'",
    )
    gen_parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json"],
        default="text",
        help="输出格式（默认 text）",
    )
    gen_parser.set_defaults(func=cmd_generate)

    # batch 子命令
    batch_parser = subparsers.add_parser(
        "batch", help="批量分析 CSV 文件"
    )
    batch_parser.add_argument("csv_file", help="CSV 文件路径，需含 scenario 列")
    batch_parser.add_argument(
        "--output", "-o", help="输出 JSON 文件路径（可选）"
    )
    batch_parser.set_defaults(func=cmd_batch)

    # interactive 子命令
    inter_parser = subparsers.add_parser(
        "interactive", help="交互式分析模式"
    )
    inter_parser.set_defaults(func=cmd_interactive)

    args = parser.parse_args()

    if args.command is None:
        # 默认行为：当作 generate 处理
        if len(sys.argv) > 1:
            # 把剩余参数拼回传给 generate
            args2 = argparse.Namespace(
                command="generate",
                input=" ".join(sys.argv[1:]),
                format="text",
            )
            return cmd_generate(args2)
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
