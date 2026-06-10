#!/usr/bin/env python3
"""
合规培训CLI入口

用法:
    python3 scripts/training_cli.py generate "合规培训 客户经理 销售合规 60分钟"

参数格式:
    合规培训 <岗位类型> <培训主题> [时长]
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from training_engine import ComplianceTrainingEngine


def parse_input(text: str) -> dict:
    """解析输入文本"""
    parts = text.strip().split()

    # Default values
    result = {
        "topic_prefix": "合规培训",
        "job_type": "客户经理",
        "topic": "销售合规",
        "duration": 60,
    }

    # Find topic prefix
    for i, part in enumerate(parts):
        if part == "合规培训":
            result["topic_prefix"] = part
            remaining = parts[i + 1 :]
            break
    else:
        remaining = parts

    # Parse remaining parts
    # Format: <job_type> <topic> [duration]
    if len(remaining) >= 1:
        result["job_type"] = remaining[0]

    if len(remaining) >= 2:
        # Check if second part is a duration or topic
        if remaining[1].endswith("分钟") or remaining[1].endswith("min"):
            result["duration"] = int(remaining[1].rstrip("分钟min"))
        elif remaining[1].isdigit():
            result["duration"] = int(remaining[1])
        else:
            result["topic"] = remaining[1]

    if len(remaining) >= 3:
        if remaining[2].endswith("分钟") or remaining[2].endswith("min"):
            result["duration"] = int(remaining[2].rstrip("分钟min"))
        elif remaining[2].isdigit():
            result["duration"] = int(remaining[2])
        else:
            result["topic"] = remaining[2]

    return result


def format_output(result: dict, format_type: str = "text") -> str:
    """格式化输出"""
    if format_type == "json":
        return json.dumps(result, ensure_ascii=False, indent=2)

    # Text format
    meta = result.get("meta", {})
    outline = result.get("outline", {})
    content = result.get("content", {})
    cases = result.get("cases", [])
    quiz = result.get("quiz", [])
    evaluation = result.get("evaluation", {})
    quick_ref = result.get("quick_ref", {})

    lines = []
    lines.append("=" * 60)
    lines.append(f"📚 合规培训方案")
    lines.append("=" * 60)
    lines.append(f"岗位类型: {meta.get('job_type', 'N/A')}")
    lines.append(f"部门: {meta.get('department', 'N/A')}")
    lines.append(f"培训主题: {meta.get('topic', 'N/A')}")
    lines.append(f"时长要求: {meta.get('duration_minutes', 'N/A')}分钟")
    lines.append("")

    # 课件大纲
    lines.append("-" * 60)
    lines.append("📋 培训课件大纲")
    lines.append("-" * 60)
    lines.append(f"标题: {outline.get('title', 'N/A')}")
    lines.append(f"总时长: {outline.get('total_minutes', 'N/A')}分钟")
    lines.append("")
    for section in outline.get("sections", []):
        lines.append(f"  【{section['name']}】({section['minutes']}分钟)")
        for module in section.get("modules", []):
            lines.append(f"    - {module}")
        lines.append("")

    # 培训内容
    lines.append("-" * 60)
    lines.append("📖 培训内容")
    lines.append("-" * 60)
    lines.append("【适用法规】")
    for reg in content.get("regulations", []):
        lines.append(f"  • {reg}")
    lines.append("")
    lines.append("【核心要点】")
    for i, point in enumerate(content.get("key_points", []), 1):
        lines.append(f"  {i}. {point}")
    lines.append("")
    lines.append("【违规后果】")
    for consequence in content.get("violation_consequences", []):
        lines.append(f"  • {consequence}")
    lines.append("")
    lines.append("【岗位提示】")
    for tip in content.get("job_specific_tips", []):
        lines.append(f"  ✓ {tip}")
    lines.append("")

    # 案例分析
    lines.append("-" * 60)
    lines.append("📁 典型案例（已脱敏）")
    lines.append("-" * 60)
    for case in cases:
        lines.append(f"案例编号: {case.get('case_id', 'N/A')}")
        lines.append(f"案例标题: {case.get('title', 'N/A')}")
        lines.append(f"案情摘要: {case.get('summary', 'N/A')}")
        lines.append(f"违规认定: {case.get('violation', 'N/A')}")
        lines.append(f"处罚结果: {case.get('penalty', 'N/A')}")
        lines.append("")
    lines.append("")

    # 课后测试
    lines.append("-" * 60)
    lines.append("📝 课后测试（10题选择题）")
    lines.append("-" * 60)
    for q in quiz:
        lines.append(f"{q['id']}. {q['question']}")
        for option in q["options"]:
            lines.append(f"   {option}")
        lines.append("")
    lines.append("（答案见JSON输出）")
    lines.append("")

    # 效果评估
    lines.append("-" * 60)
    lines.append("📊 培训效果评估")
    lines.append("-" * 60)
    lines.append(f"及格分数: {evaluation.get('passing_score', 'N/A')}分")
    lines.append("")
    for dim in evaluation.get("dimensions", []):
        lines.append(f"【{dim['dimension']}】权重: {dim['weight']}")
        lines.append(f"  评估方式: {dim['method']}")
        lines.append(f"  指标: {', '.join(dim['indicators'])}")
        lines.append("")
    lines.append("")

    # 速查卡
    lines.append("-" * 60)
    lines.append("⚡ 合规要点速查卡")
    lines.append("-" * 60)
    lines.append(f"主题: {quick_ref.get('title', 'N/A')}")
    lines.append("")
    for rule in quick_ref.get("key_rules", []):
        lines.append(f"【规则】{rule.get('rule', 'N/A')}")
        lines.append(f"  自查: {rule.get('check', 'N/A')}")
        lines.append(f"  违规后果: {rule.get('if_violated', 'N/A')}")
        lines.append("")
    lines.append("")

    lines.append("=" * 60)
    lines.append("✅ 培训方案生成完成")
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="合规培训方案生成CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python3 scripts/training_cli.py generate "合规培训 客户经理 销售合规 60分钟"
    python3 scripts/training_cli.py generate "合规培训 风控专员 反洗钱 90分钟"
    python3 scripts/training_cli.py generate "合规培训 高管 内幕交易 120分钟" --format=json
        """,
    )
    parser.add_argument(
        "command",
        choices=["generate"],
        help="命令: generate - 生成培训方案",
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="合规培训 客户经理 销售合规 60分钟",
        help='输入文本，格式: "合规培训 岗位类型 培训主题 时长"',
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json"],
        default="text",
        help="输出格式 (默认: text)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="输出文件路径 (可选)",
    )

    args = parser.parse_args()

    if args.command == "generate":
        # Parse input
        params = parse_input(args.input)

        # Generate training
        engine = ComplianceTrainingEngine()
        result = engine.generate_training(
            job_type=params["job_type"],
            department="",
            topic=params["topic"],
            duration_minutes=params["duration"],
        )

        # Format output
        output = format_output(result, args.format)

        # Write output
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"✅ 结果已保存到: {args.output}")
        else:
            print(output)


if __name__ == "__main__":
    main()
