#!/usr/bin/env python3
"""
营销话术生成 CLI 工具
用法：
  python3 marketing_cli.py generate --name "张总" --industry "制造业" --goal "推荐供应链金融"
  python3 marketing_cli.py train --goal "推荐信用卡" --difficulty medium
"""
import argparse
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from marketing_engine import MarketingEngine, MarketingFormatter


def main():
    parser = argparse.ArgumentParser(description="客户经理营销话术生成工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # generate 子命令
    gen_parser = subparsers.add_parser("generate", help="生成营销话术")
    gen_parser.add_argument("--name", "-n", required=True, help="客户姓名/称呼")
    gen_parser.add_argument("--industry", "-i", required=True, help="客户行业")
    gen_parser.add_argument("--scale", "-s", default="", help="企业规模（如'年营收5000万'）")
    gen_parser.add_argument("--news", default="", help="客户近期动态")
    gen_parser.add_argument("--goal", "-g", required=True, help="营销目标")
    gen_parser.add_argument("--channel", "-c", default="face-to-face",
                           choices=["phone", "wechat", "face-to-face", "sms"],
                           help="沟通渠道")
    gen_parser.add_argument("--style", default="professional",
                           choices=["formal", "friendly", "professional", "concise"],
                           help="话术风格")
    gen_parser.add_argument("--bank", default="我行", help="银行名称")
    gen_parser.add_argument("--manager", default="", help="客户经理姓名")
    gen_parser.add_argument("--output", "-o", help="输出文件路径")

    # train 子命令
    train_parser = subparsers.add_parser("train", help="生成异议处理训练")
    train_parser.add_argument("--goal", "-g", required=True, help="营销目标")
    train_parser.add_argument("--industry", "-i", default="", help="客户行业")
    train_parser.add_argument("--difficulty", "-d", default="medium",
                             choices=["easy", "medium", "hard"],
                             help="训练难度")
    train_parser.add_argument("--output", "-o", help="输出文件路径")

    args = parser.parse_args()

    engine = MarketingEngine()
    formatter = MarketingFormatter()

    if args.command == "generate":
        result = engine.generate_script(
            customer_name=args.name,
            industry=args.industry,
            company_scale=args.scale,
            recent_news=args.news,
            marketing_goal=args.goal,
            channel=args.channel,
            style=args.style,
            bank_name=args.bank,
            manager_name=args.manager,
        )
        output = formatter.format_script(result)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"✅ 话术已保存到: {args.output}")
        else:
            print(output)

    elif args.command == "train":
        result = engine.generate_objections_training(
            marketing_goal=args.goal,
            industry=args.industry,
            difficulty=args.difficulty,
        )
        output = formatter.format_objections(result)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"✅ 训练材料已保存到: {args.output}")
        else:
            print(output)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
