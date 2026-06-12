#!/usr/bin/env python3
"""
Performance Attribution CLI
用法：
    python3 scripts/perf_attr_cli.py generate "业绩归因 F000001 收益率12% 基准8%"
    python3 scripts/perf_attr_cli.py parse "F000001 12% 8%"
    python3 scripts/perf_attr_cli.py --json F000001 0.12 0.08
"""

import re
import sys
import json
from pathlib import Path

# 将 skill 目录加入 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from perf_attr_engine import PerformanceAttributionEngine


def parse_natural_command(text: str) -> dict:
    """
    解析自然语言命令，如：
    "业绩归因 F000001 收益率12% 基准8%"
    "业绩归因 某基金F000001 收益率12% 基准8%"
    "F000001 12% 8%"
    """
    text = text.strip()

    # 提取基金代码 F + 6位数字
    fund_match = re.search(r'F\d{6}', text)
    fund_code = fund_match.group() if fund_match else "F000001"

    # 提取收益率数字（支持 12% / 0.12 / 12%）
    # 模式：收益率?(\\d+(?:\\.\\d+)?)%?
    pct_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*%')
    pcts = pct_pattern.findall(text)

    if len(pcts) >= 2:
        fund_ret = float(pcts[0]) / 100
        bench_ret = float(pcts[1]) / 100
    elif len(pcts) == 1:
        fund_ret = float(pcts[0]) / 100
        bench_ret = 0.08  # 默认8%
    else:
        # 尝试直接数字（无百分号）
        nums = re.findall(r'(?:^|\s)(\d+(?:\.\d+)?)(?:\s|$)', text)
        if len(nums) >= 2:
            v1, v2 = float(nums[0]), float(nums[1])
            fund_ret = v1 / 100 if v1 < 1 else v1  # 自动判断是0.12还是12
            bench_ret = v2 / 100 if v2 < 1 else v2
        elif len(nums) == 1:
            fund_ret = float(nums[0]) / 100
            bench_ret = 0.08
        else:
            fund_ret = 0.12
            bench_ret = 0.08

    return {"fund_code": fund_code, "fund_return": fund_ret, "benchmark_return": bench_ret}


def cmd_generate(args: list) -> int:
    """generate 子命令：自然语言输入"""
    if not args:
        print("用法: generate \"业绩归因 F000001 收益率12% 基准8%\"", file=sys.stderr)
        return 1

    query = " ".join(args)
    params = parse_natural_command(query)

    engine = PerformanceAttributionEngine()
    result = engine.analyze(**params)
    print(result["summary"])
    return 0


def cmd_parse(args: list) -> int:
    """parse 子命令：结构化输入"""
    if len(args) < 1:
        print("用法: parse F000001 0.12 0.08", file=sys.stderr)
        return 1

    fund_code = args[0]
    fund_return = float(args[1]) if len(args) > 1 else 0.12
    benchmark_return = float(args[2]) if len(args) > 2 else 0.08

    engine = PerformanceAttributionEngine()
    result = engine.analyze(
        fund_code=fund_code,
        fund_return=fund_return,
        benchmark_return=benchmark_return,
    )
    print(result["summary"])
    return 0


def cmd_json(args: list) -> int:
    """直接输出 JSON"""
    if len(args) < 1:
        fund_code = "F000001"
        fund_return = 0.12
        benchmark_return = 0.08
    elif len(args) >= 3:
        fund_code = args[0]
        fund_return = float(args[1])
        benchmark_return = float(args[2])
    else:
        # 尝试解析
        params = parse_natural_command(" ".join(args))
        fund_code = params["fund_code"]
        fund_return = params["fund_return"]
        benchmark_return = params["benchmark_return"]

    engine = PerformanceAttributionEngine()
    result = engine.analyze(
        fund_code=fund_code,
        fund_return=fund_return,
        benchmark_return=benchmark_return,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        # 默认：直接运行示例
        engine = PerformanceAttributionEngine()
        result = engine.analyze(
            fund_code="F000001",
            fund_return=0.12,
            benchmark_return=0.08,
        )
        print(result["summary"])
        return 0

    cmd = sys.argv[1]

    if cmd == "generate":
        return cmd_generate(sys.argv[2:])
    elif cmd == "parse":
        return cmd_parse(sys.argv[2:])
    elif cmd == "--json" or cmd == "-j":
        return cmd_json(sys.argv[2:])
    elif cmd in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    else:
        # 尝试直接解析
        params = parse_natural_command(" ".join(sys.argv[1:]))
        engine = PerformanceAttributionEngine()
        result = engine.analyze(**params)
        print(result["summary"])
        return 0


if __name__ == "__main__":
    sys.exit(main())
