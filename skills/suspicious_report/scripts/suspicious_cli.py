#!/usr/bin/env python3
"""
可疑交易报告 CLI
用法:
    python3 suspicious_cli.py generate "可疑交易 某客户 累计500万 分散20个账户 快进快出"
    python3 suspicious_cli.py generate "大额交易 某客户 单笔300万"
    python3 suspicious_cli.py json "某客户 累计500万 分散20个账户 快进快出"
    python3 suspicious_cli.py wecom "某客户 累计500万 分散20个账户 快进快出"
"""

import sys
import os
import argparse

# 添加父目录到路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from suspicious_engine import SuspiciousReportEngine


def generate_report(text: str, output_format: str = "text"):
    """生成报告"""
    engine = SuspiciousReportEngine()
    result = engine.analyze(text)

    if output_format == "json":
        print(engine.to_json(result))
    elif output_format == "wecom":
        card = engine.to_wecom_card(result)
        import json
        print(json.dumps(card, ensure_ascii=False, indent=2))
    else:
        print(result["report_content"])
        print()
        print("=" * 60)
        print(f"[INFO] 报告类型: {result['report_type']}")
        print(f"[INFO] 可疑特征: {', '.join(result['suspicious_features']) if result['suspicious_features'] else '无'}")
        print(f"[INFO] 置信度: {result['confidence']*100:.0f}%")
        print(f"[INFO] 建议行动: {len(result['recommended_actions'])} 项")


def main():
    parser = argparse.ArgumentParser(
        description="可疑交易报告生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 suspicious_cli.py generate "可疑交易 某客户 累计500万 分散20个账户 快进快出"
  python3 suspicious_cli.py json "某客户 累计500万"
  python3 suspicious_cli.py wecom "某客户 分散归集"
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # generate 命令
    generate_parser = subparsers.add_parser("generate", help="生成报告（文本格式）")
    generate_parser.add_argument("text", type=str, help="交易描述文本")
    generate_parser.add_argument(
        "--format", "-f",
        choices=["text", "json", "wecom"],
        default="text",
        help="输出格式 (默认: text)"
    )

    # json 命令
    json_parser = subparsers.add_parser("json", help="生成报告（JSON格式）")
    json_parser.add_argument("text", type=str, help="交易描述文本")

    # wecom 命令
    wecom_parser = subparsers.add_parser("wecom", help="生成企微卡片格式")
    wecom_parser.add_argument("text", type=str, help="交易描述文本")

    args = parser.parse_args()

    if args.command == "generate":
        generate_report(args.text, args.format)
    elif args.command == "json":
        generate_report(args.text, "json")
    elif args.command == "wecom":
        generate_report(args.text, "wecom")
    else:
        # 默认行为：generate
        if len(sys.argv) > 1:
            generate_report(" ".join(sys.argv[1:]))
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
