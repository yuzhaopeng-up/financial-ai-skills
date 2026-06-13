#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户异议训练引擎 CLI

Usage:
    python objection_training_cli.py types
    python objection_training_cli.py scenario [--type TYPE] [--difficulty DIFFICULTY]
    python objection_training_cli.py evaluate "用户回复"
    python objection_training_cli.py practice [--type TYPE]
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from objection_training_engine import ObjectionTrainingEngine


def cmd_types(args):
    """显示所有支持的异议类型"""
    engine = ObjectionTrainingEngine()
    types = engine.get_available_types()
    
    print("📋 支持的异议类型:")
    print()
    for obj in types:
        print(f"  {obj['icon']} **{obj['type']}**")
        print(f"     {obj['description']}")
        print(f"     示例: {obj['examples'][0]}")
        print()


def cmd_scenario(args):
    """生成训练场景"""
    engine = ObjectionTrainingEngine()
    
    scenario = engine.generate_scenario(
        objection_type=args.type if args.type != "random" else None,
        difficulty=args.difficulty
    )
    
    print(engine.format_text(scenario, "scenario"))
    
    # 如果需要评估
    if args.evaluate:
        print()
        print("-" * 40)
        print("📝 请输入您的回复:")
        user_response = input()
        if user_response.strip():
            evaluation = engine.evaluate_response(scenario, user_response)
            print()
            print(engine.format_text(evaluation, "evaluation"))
    
    return 0


def cmd_evaluate(args):
    """评估用户回复"""
    engine = ObjectionTrainingEngine()
    
    # 先生成场景
    scenario = engine.generate_scenario(
        objection_type=args.type if args.type != "random" else None,
        difficulty=args.difficulty
    )
    
    print("🎭 训练场景:")
    print("-" * 40)
    print(f"异议类型: {scenario['objection_name']}")
    print(f"客户说: {scenario['customer_statement']}")
    print()
    
    if not args.response:
        print("📝 请输入您的回复:")
        user_response = input()
    else:
        user_response = args.response
    
    evaluation = engine.evaluate_response(scenario, user_response)
    print(engine.format_text(evaluation, "evaluation"))
    
    return 0


def cmd_practice(args):
    """交互式训练"""
    engine = ObjectionTrainingEngine()
    
    print("=" * 50)
    print("🎭 客户异议实战训练")
    print("=" * 50)
    print()
    
    # 生成场景
    scenario = engine.generate_scenario(
        objection_type=args.type if args.type != "random" else None
    )
    
    print("📌 请根据以下场景回复客户:")
    print()
    print(f"【场景】")
    print(f"异议类型: {scenario['objection_icon']} {scenario['objection_name']}")
    print(f"客户态度: {scenario['customer_mood']}")
    print()
    print(f"💬 客户说:")
    print(f"> {scenario['customer_statement']}")
    print()
    
    print("📝 请输入您的回复:")
    user_response = input()
    print()
    
    # 评估
    evaluation = engine.evaluate_response(scenario, user_response)
    print(engine.format_text(evaluation, "evaluation"))
    print()
    
    # 是否继续
    while True:
        choice = input("是否继续下一轮训练？(y/n): ").strip().lower()
        if choice != 'y':
            break
        
        # 继续下一轮
        scenario = engine.generate_continue_scenario(scenario, user_response)
        print()
        print("📌 客户追问:")
        print(f"> {scenario['customer_counter']}")
        print()
        
        print("📝 请输入您的回复:")
        user_response = input()
        
        evaluation = engine.evaluate_response(scenario, user_response)
        print(engine.format_text(evaluation, "evaluation"))
        print()
    
    print("感谢参与训练！")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="🦞 客户异议训练引擎 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # types 子命令
    types_parser = subparsers.add_parser("types", help="显示所有支持的异议类型")
    types_parser.set_defaults(func=cmd_types)
    
    # scenario 子命令
    scenario_parser = subparsers.add_parser("scenario", help="生成训练场景")
    scenario_parser.add_argument("--type", "-t", default="random", help="异议类型")
    scenario_parser.add_argument("--difficulty", "-d", default="medium", 
                                  choices=["easy", "medium", "hard"], help="难度")
    scenario_parser.add_argument("--evaluate", "-e", action="store_true", help="生成后评估")
    scenario_parser.set_defaults(func=cmd_scenario)
    
    # evaluate 子命令
    eval_parser = subparsers.add_parser("evaluate", help="评估回复")
    eval_parser.add_argument("response", nargs="?", help="用户回复")
    eval_parser.add_argument("--type", "-t", default="random", help="异议类型")
    eval_parser.add_argument("--difficulty", "-d", default="medium", help="难度")
    eval_parser.set_defaults(func=cmd_evaluate)
    
    # practice 子命令
    practice_parser = subparsers.add_parser("practice", help="交互式训练")
    practice_parser.add_argument("--type", "-t", default="random", help="异议类型")
    practice_parser.set_defaults(func=cmd_practice)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
