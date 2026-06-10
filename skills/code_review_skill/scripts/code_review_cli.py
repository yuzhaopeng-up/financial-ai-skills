#!/usr/bin/env python3
"""
Code Review CLI - 代码审查命令行工具

用法:
    python3 scripts/code_review_cli.py generate "代码审查 Python 用户输入SQL拼接查询 未使用参数化"
    python3 scripts/code_review_cli.py review <language> <code_file>
    python3 scripts/code_review_cli.py interactive
"""

import sys
import json
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code_review_engine import CodeReviewEngine


def format_report(report):
    """格式化输出审查报告"""
    summary = report["summary"]
    issues = report["issues"]

    # ANSI 颜色码
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    output = []
    output.append(f"\n{BOLD}{'='*60}{RESET}")
    output.append(f"{BOLD}  🔍  代码安全审查报告  🔍{RESET}")
    output.append(f"{'='*60}")

    # 概览
    score = summary["quality_score"]
    if score >= 8:
        score_color = GREEN
    elif score >= 6:
        score_color = YELLOW
    else:
        score_color = RED

    output.append(f"\n{BOLD}📊 审查概览{RESET}")
    output.append(f"  语言:       {summary['language']}")
    output.append(f"  问题总数:   {summary['total_issues']}")
    output.append(f"  {RED}HIGH: {summary['high']}{RESET}  |  {YELLOW}MEDIUM: {summary['medium']}{RESET}  |  {BLUE}LOW: {summary['low']}{RESET}")
    output.append(f"  质量评分:   {score_color}{score}/10{RESET}")

    # 问题列表
    if issues:
        output.append(f"\n{BOLD}🐛 发现的问题 ({len(issues)}){RESET}")
        for issue in issues:
            sev = issue["severity"]
            if sev == "HIGH":
                sev_color = RED
                sev_icon = "🔴"
            elif sev == "MEDIUM":
                sev_color = YELLOW
                sev_icon = "🟡"
            else:
                sev_color = BLUE
                sev_icon = "🔵"

            output.append(f"\n  {sev_icon} [{sev}] #{issue['id']} {sev_color}{issue['title']}{RESET}")
            output.append(f"     📍 位置: {issue['location']}")
            output.append(f"     📂 分类: {issue['category']}")
            output.append(f"     📝 描述: {issue['description']}")
            if issue.get("code_snippet"):
                output.append(f"     💻 代码:")
                for line in issue["code_snippet"].split('\n'):
                    output.append(f"        {line}")
            output.append(f"     ✅ 修复: {issue['fix_suggestion'][:100]}...")
    else:
        output.append(f"\n{GREEN}✅ 未发现问题，代码看起来很安全！{RESET}")

    output.append(f"\n{'='*60}\n")
    return '\n'.join(output)


def cmd_generate(args):
    """根据自然语言描述生成审查"""
    engine = CodeReviewEngine()
    description = ' '.join(args)

    # 解析请求
    parsed = engine.parse_natural_language(description)
    language = parsed["language"]
    standards = parsed["standards"]

    # 构建示例代码
    sample_code = engine.build_sample_code(description)

    print(f"\n🔍 检测到审查请求:")
    print(f"   语言: {language}")
    print(f"   标准: {standards}")
    print(f"\n📝 审查代码片段:")
    print(sample_code)

    # 执行审查
    report = engine.review(sample_code, language=language, standards=standards)
    result = report.to_dict()

    # 输出
    print(format_report(result))
    return result


def cmd_review(args):
    """审查指定文件或代码"""
    if len(args) < 1:
        print("用法: review <language> [code]")
        return

    engine = CodeReviewEngine()
    language = args[0]

    if len(args) > 1 and os.path.isfile(args[1]):
        with open(args[1], 'r') as f:
            code = f.read()
    else:
        code = ' '.join(args[1:]) if len(args) > 1 else sys.stdin.read()

    report = engine.review(code, language=language)
    result = report.to_dict()
    print(format_report(result))
    return result


def cmd_json(args):
    """输出 JSON 格式"""
    engine = CodeReviewEngine()
    description = ' '.join(args)

    parsed = engine.parse_natural_language(description)
    sample_code = engine.build_sample_code(description)
    report = engine.review(sample_code, language=parsed["language"], standards=parsed["standards"])

    print(report.to_json())
    return report.to_dict()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "generate":
        cmd_generate(args)
    elif cmd == "review":
        cmd_review(args)
    elif cmd == "json":
        cmd_json(args)
    else:
        print(f"未知命令: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
