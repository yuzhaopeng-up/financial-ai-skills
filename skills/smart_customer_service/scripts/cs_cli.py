#!/usr/bin/env python3
"""
智能客服 CLI 入口
用法:
    python3 cs_cli.py generate "智能客服 我想投诉 银行卡被盗刷了"
    python3 cs_cli.py stats
    python3 cs_cli.py interactive
"""

import argparse
import json
import sys
import os

# 添加父目录到路径以便导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cs_engine import SmartCustomerServiceEngine


def cmd_generate(engine: SmartCustomerServiceEngine, text: str) -> dict:
    """处理用户输入"""
    result = engine.process(text)
    return result


def cmd_stats(engine: SmartCustomerServiceEngine) -> dict:
    """显示统计信息"""
    return engine.get_stats()


def cmd_interactive(engine: SmartCustomerServiceEngine):
    """交互模式"""
    print("=" * 60)
    print("智能客服交互模式 (输入 'quit' 或 'exit' 退出)")
    print("=" * 60)

    session_misjudgment = 0

    while True:
        try:
            user_input = input("\n您: ").strip()
            if user_input.lower() in ["quit", "exit", "q", "退出"]:
                print("再见！祝您生活愉快！")
                break
            if not user_input:
                continue

            result = engine.process(user_input, misjudgment_count=session_misjudgment)

            # 跟踪判断失误
            if result["intent_id"] == 9:
                session_misjudgment += 1

            print(f"\n[意图] {result['intent_name']} (置信度: {result['confidence']:.2f})")

            if result["should_transfer"]:
                print(f"[⚠️ 转人工] {result['transfer_reason']}")

            if result["faq_match"]:
                print(f"[FAQ匹配] {result['faq_match']['question']}")

            print(f"\n[回答] {result['answer']}")

        except KeyboardInterrupt:
            print("\n\n再见！祝您生活愉快！")
            break
        except Exception as e:
            print(f"处理出错: {e}")


def format_output(result: dict, format_type: str = "text") -> str:
    """格式化输出"""
    if format_type == "json":
        return json.dumps(result, ensure_ascii=False, indent=2)
    elif format_type == "compact":
        lines = [
            f"意图: {result['intent_name']}",
            f"置信度: {result['confidence']:.2f}",
            f"转人工: {'是' if result['should_transfer'] else '否'}",
            f"回答: {result['answer']}",
        ]
        if result["faq_match"]:
            lines.append(f"FAQ: {result['faq_match']['question']}")
        return "\n".join(lines)
    else:
        # text
        output = []
        output.append("=" * 60)
        output.append("智能客服处理结果")
        output.append("=" * 60)
        output.append(f"意图分类: {result['intent_name']}")
        output.append(f"意图ID: {result['intent_id']}")
        output.append(f"置信度: {result['confidence']:.2f}")

        if result["faq_match"]:
            output.append(f"\n[FAQ匹配]")
            output.append(f"  问题: {result['faq_match']['question']}")
            output.append(f"  答案: {result['faq_match']['answer']}")

        if result["should_transfer"]:
            output.append(f"\n[⚠️ 建议转人工]")
            output.append(f"  原因: {result['transfer_reason']}")

        output.append(f"\n[自动回答]")
        output.append(f"{result['answer']}")
        output.append("=" * 60)
        return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="智能客服CLI工具")
    parser.add_argument("command", choices=["generate", "stats", "interactive", "serve"],
                        help="命令: generate处理文本, stats显示统计, interactive交互模式")
    parser.add_argument("text", nargs="?", help="要处理的文本（generate命令时使用）")
    parser.add_argument("-f", "--format", choices=["text", "json", "compact"],
                        default="text", help="输出格式")
    parser.add_argument("-m", "--misjudgment", type=int, default=0,
                        help="当前会话判断失误次数")

    args = parser.parse_args()

    # 初始化引擎
    engine = SmartCustomerServiceEngine()

    if args.command == "generate":
        if not args.text:
            print("错误: generate命令需要提供文本")
            sys.exit(1)
        result = cmd_generate(engine, args.text)
        print(format_output(result, args.format))

    elif args.command == "stats":
        stats = cmd_stats(engine)
        print(json.dumps(stats, ensure_ascii=False, indent=2))

    elif args.command == "interactive":
        cmd_interactive(engine)

    elif args.command == "serve":
        print("HTTP服务模式待实现，可使用Flask/FastAPI包装")
        sys.exit(1)


if __name__ == "__main__":
    main()
