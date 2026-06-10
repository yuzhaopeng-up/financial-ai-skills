#!/usr/bin/env python3
"""
审计智能抽样 CLI

用法:
    python3 audit_sampling_cli.py generate "审计抽样 发票总量10000张 总金额5000万 高风险业务"
    python3 audit_sampling_cli.py generate "审计抽样 总量5000 总金额2000万 中风险业务" --method 分层抽样 --confidence 0.99
    python3 audit_sampling_cli.py generate "审计抽样 总量200 总金额100万 低风险业务" --output json
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from audit_sampling_engine import AuditSamplingEngine


def parse_natural_language(s: str) -> dict:
    """解析自然语言描述的审计场景"""
    result = {
        "scenario": "通用审计",
        "total_count": 1000,
        "total_amount": 10000000,
        "risk_level": "中风险",
        "confidence_level": 0.95,
    }
    
    s = s.strip()
    
    # 提取场景
    if "发票" in s:
        result["scenario"] = "发票审计"
    elif "采购" in s:
        result["scenario"] = "采购审计"
    elif "销售" in s:
        result["scenario"] = "销售审计"
    elif "费用" in s:
        result["scenario"] = "费用审计"
    elif "合同" in s:
        result["scenario"] = "合同审计"
    elif "银行" in s or "账户" in s:
        result["scenario"] = "银行账户审计"
    else:
        result["scenario"] = "通用审计"
    
    # 提取总量
    count_patterns = [
        r"总量(\d+(?:\.\d+)?[万千百]?(?:张|笔|件|个|户|份)?)",
        r"总数(\d+(?:\.\d+)?[万千百]?(?:张|笔|件|个|户|份)?)",
        r"(\d+(?:\.\d+)?[万千百]?)张",
        r"(\d+(?:\.\d+)?[万千百]?)笔",
        r"(\d+(?:\.\d+)?[万千百]?)件",
    ]
    
    for pattern in count_patterns:
        match = re.search(pattern, s)
        if match:
            num_str = match.group(1).rstrip("张笔件个户份")
            result["total_count"] = int(float(num_str))
            break
    
    # 如果没找到数量，尝试从"总量XXX"或"总计XXX"提取
    if result["total_count"] == 1000:
        total_pattern = r"(?:总量|总数|总计|合计)[:：]?\s*(\d+)"
        match = re.search(total_pattern, s)
        if match:
            result["total_count"] = int(match.group(1))
    
    # 提取总金额
    amount_patterns = [
        r"总金额(\d+(?:\.\d+)?[万亿千万]?(?:元|万)?)",
        r"(\d+(?:\.\d+)?[万亿千万])元",
        r"(\d+(?:\.\d+)?[万亿千万])万",
    ]
    
    for pattern in amount_patterns:
        match = re.search(pattern, s)
        if match:
            num_str = match.group(1).rstrip("元万亿千万")
            if "亿" in match.group(0):
                result["total_amount"] = float(num_str) * 100000000
            elif "万" in match.group(0):
                result["total_amount"] = float(num_str) * 10000
            elif "千" in match.group(0):
                result["total_amount"] = float(num_str) * 1000
            else:
                result["total_amount"] = float(num_str)
            break
    
    # 如果没找到金额，尝试从独立数字推断
    if result["total_amount"] == 10000000:
        # 查找"5000万"格式
        m2 = re.search(r"(\d+(?:\.\d+)?)\s*万", s)
        if m2:
            result["total_amount"] = float(m2.group(1)) * 10000
    
    # 提取风险等级
    if "高风险" in s:
        result["risk_level"] = "高风险"
    elif "中风险" in s:
        result["risk_level"] = "中风险"
    elif "低风险" in s:
        result["risk_level"] = "低风险"
    
    # 提取置信水平
    conf_pattern = r"置信(\d+)%?"
    match = re.search(conf_pattern, s)
    if match:
        result["confidence_level"] = int(match.group(1)) / 100
    
    return result


def format_report(result: dict) -> str:
    """格式化输出报告"""
    plan = result["sampling_plan"]
    res = result["sampling_results"]
    findings = result["audit_findings"]
    conclusion = result["population_conclusion"]
    pop = result["population_summary"]
    
    # 模拟样本列表（只显示前10条和有问题 的）
    sampled = res["sampled_items"]
    
    lines = []
    lines.append("")
    lines.append("=" * 56)
    lines.append("  📊 审计智能抽样报告")
    lines.append("=" * 56)
    lines.append("")
    lines.append(f"  场景: {result['scenario']}")
    lines.append("")
    lines.append("  【总体概况】")
    lines.append(f"    总体数量  : {pop['total_count']:>12,} 件")
    lines.append(f"    总体金额  : {pop['total_amount']:>12,.0f} 元")
    lines.append(f"    平均金额  : {pop['avg_amount']:>12,.2f} 元/件")
    lines.append(f"    风险等级  : {pop['risk_level']}")
    lines.append("")
    lines.append("  【抽样方案】")
    lines.append(f"    抽样方法  : {plan['method']}")
    lines.append(f"    样本数量  : {plan['sample_size']:>12} 件")
    lines.append(f"    置信水平  : {plan['confidence_level']*100:>11.0f}%")
    lines.append(f"    可容忍误差: {plan['tolerable_error_rate']*100:>11.1f}%")
    lines.append(f"    预期误差  : {plan['expected_error_rate']*100:>11.1f}%")
    lines.append("")
    lines.append(f"  方法说明: {plan['method_rationale']}")
    lines.append("")
    lines.append("  【抽样结果】")
    lines.append(f"    实际抽样  : {res['sample_size']:>12} 件")
    lines.append(f"    发现问题  : {res['findings_count']:>12} 件 ({res['findings_rate']:.2f}%)")
    lines.append(f"    问题金额  : {res['findings_amount']:>12,.2f} 元")
    lines.append("")
    lines.append("  【误差推断】")
    lines.append(f"    估计误差率: {findings['estimated_error_rate']:>11.2f}%")
    lines.append(f"    误差范围  : {findings['error_rate_lower']:.2f}% ~ {findings['error_rate_upper']:.2f}%")
    lines.append(f"    推断总体误差金额: {findings['projected_total_amount']:>12,.2f} 元")
    lines.append("")
    lines.append("  【总体结论】")
    lines.append(f"    审计意见  : {conclusion['opinion_impact']}")
    lines.append(f"    {conclusion['recommendation']}")
    lines.append("")
    lines.append("=" * 56)
    
    # 抽样明细（只显示有问题或高金额的）
    lines.append("")
    lines.append("  【抽样明细】(显示有问题/高风险项目)")
    lines.append("-" * 56)
    
    findings_items = [i for i in sampled if i.get("has_error")] or sampled[:10]
    for item in findings_items[:15]:
        flag = "⚠️" if item.get("has_error") else "  "
        finding = f"[{item.get('finding_type', '')}]" if item.get("has_error") else ""
        lines.append(
            f"  {flag} {item['item_id']} | {item['stratum']:<15} | "
            f"¥{item['amount']:>10,.2f} {finding}"
        )
    
    if len(findings_items) > 15:
        lines.append(f"  ... 还有 {len(findings_items) - 15} 条记录")
    
    lines.append("-" * 56)
    lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="审计智能抽样工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 audit_sampling_cli.py generate "审计抽样 发票总量10000张 总金额5000万 高风险业务"
  python3 audit_sampling_cli.py generate "审计抽样 总量5000 总金额2000万 中风险" --confidence 0.99
  python3 audit_sampling_cli.py generate "审计抽样 总量1000" --output json
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # generate 命令
    gen_parser = subparsers.add_parser("generate", help="生成审计抽样方案")
    gen_parser.add_argument(
        "query",
        nargs="*",
        default=[],
        help="审计场景描述，如：审计抽样 发票总量10000张 总金额5000万 高风险业务"
    )
    gen_parser.add_argument("--method", "-m", default="auto", help="抽样方法")
    gen_parser.add_argument("--confidence", "-c", type=float, default=0.95, help="置信水平")
    gen_parser.add_argument("--tolerable", "-t", type=float, default=0.05, help="可容忍误差率")
    gen_parser.add_argument("--expected", "-e", type=float, default=0.01, help="预期误差率")
    gen_parser.add_argument("--output", "-o", default="text", choices=["text", "json"], help="输出格式")
    gen_parser.add_argument("--seed", "-s", type=int, default=42, help="随机种子(用于复现)")
    
    args = parser.parse_args()
    
    if args.command == "generate":
        # 合并query参数为字符串
        if args.query:
            query_str = " ".join(args.query)
        else:
            # 交互式输入
            query_str = input("请输入审计场景描述: ").strip()
        
        # 解析参数
        params = parse_natural_language(query_str)
        
        # 命令行参数覆盖
        if args.method != "auto":
            params["method"] = args.method
        if args.confidence:
            params["confidence_level"] = args.confidence
        params["tolerable_error_rate"] = args.tolerable
        params["expected_error_rate"] = args.expected
        
        # 执行抽样
        engine = AuditSamplingEngine(seed=args.seed)
        result = engine.generate(**params)
        
        # 输出
        if args.output == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            report = format_report(result)
            print(report)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
