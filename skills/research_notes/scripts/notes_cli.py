#!/usr/bin/env python3
"""
调研纪要 CLI
用法：
    python3 notes_cli.py generate "调研纪要 某上市公司 IR调研 纪要包含光伏扩产计划和毛利率下降"
    python3 notes_cli.py generate "..." --format json
    python3 notes_cli.py generate "..." --output result.json
    python3 notes_cli.py generate "..." --format markdown --output result.md
"""

import sys
import os
import json
import argparse
import re

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notes_engine import ResearchNotesEngine


def parse_input(input_str: str) -> dict:
    """
    从用户输入中解析出调研纪要信息

    支持格式：
    - 调研纪要 公司名 调研对象 调研方式 纪要内容...
    - 调研纪要 IR调研 纪要包含xxx
    """
    # 去掉开头的"调研纪要"
    text = re.sub(r'^调研纪要\s*', '', input_str.strip())

    # 提取公司名（假设在"公司"或"某上市公司"后）
    company = "某公司"
    subject = "IR"
    method = "IR调研"

    # 常见调研对象/方式
    method_map = {
        'ir调研': 'IR调研',
        '管理层调研': '管理层现场调研',
        '现场调研': '现场调研',
        '电话调研': '电话调研',
        '策略会': '策略会',
        '分析师会议': '分析师会议',
    }

    for kw, val in method_map.items():
        if kw in text.lower():
            method = val
            break

    # 提取"纪要包含"后的内容作为纪要原文
    raw_notes = ""
    match = re.search(r'纪要[包含含]?(.*)', text)
    if match:
        raw_notes = match.group(1).strip()
    else:
        # 尝试提取双引号内容
        quotes = re.findall(r'["""\'\'\'](.*?)["""\'\'\']', text)
        if quotes:
            raw_notes = quotes[0]
        else:
            raw_notes = text

    # 尝试识别公司名
    company_patterns = [
        r'([\u4e00-\u9fa5]{4,}(?:股份|集团|公司|科技))',
        r'某(上市公司|公司)',
    ]
    for p in company_patterns:
        m = re.search(p, text)
        if m:
            company = m.group(1)
            break

    return {
        "company": company,
        "subject": subject,
        "method": method,
        "raw_notes": raw_notes,
        "date": "",
    }


def generate_handler(args):
    """处理 generate 命令"""
    engine = ResearchNotesEngine()

    # 解析输入
    parsed = parse_input(args.input)

    print(f"[INFO] 正在生成调研纪要...")
    print(f"[INFO] 公司: {parsed['company']} | 方式: {parsed['method']}")
    print(f"[INFO] 纪要长度: {len(parsed['raw_notes'])} 字符\n")

    # 生成纪要
    result = engine.generate(
        company=parsed['company'],
        subject=parsed['subject'],
        method=parsed['method'],
        raw_notes=parsed['raw_notes'],
        date=parsed['date']
    )

    # 输出
    if args.format == 'json':
        output = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        output = engine.to_markdown(result)

    # 写入文件或打印
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"[INFO] 已保存到: {args.output}")
    else:
        print(output)

    # 企微卡片预览
    if args.wecom:
        card = engine.to_wecom_card(result)
        print("\n[INFO] 企微卡片格式：")
        print(json.dumps(card, ensure_ascii=False, indent=2)[:500])


def main():
    parser = argparse.ArgumentParser(description="调研纪要生成工具")
    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # generate 子命令
    gen_parser = subparsers.add_parser('generate', help='生成结构化调研纪要')
    gen_parser.add_argument('input', type=str, help='调研纪要输入（格式：调研纪要 公司 方式 纪要内容...）')
    gen_parser.add_argument('--format', type=str, choices=['json', 'markdown'], default='markdown',
                            help='输出格式（默认 markdown）')
    gen_parser.add_argument('--output', type=str, default='', help='输出文件路径')
    gen_parser.add_argument('--wecom', action='store_true', help='同时输出企微卡片格式')

    args = parser.parse_args()

    if args.command == 'generate':
        generate_handler(args)
    else:
        # 兼容直接传入输入的方式
        if len(sys.argv) > 1:
            parser.parse_args(['generate'] + sys.argv[1:])
        else:
            parser.print_help()


if __name__ == '__main__':
    main()
