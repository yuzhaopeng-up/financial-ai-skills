#!/usr/bin/env python3
"""
IPO Analysis CLI
用法: python3 ipo_cli.py generate "IPO分析 某科技公司 科创板 募资10亿"
"""

import re
import sys
import json
from pathlib import Path

# Add parent dir to path for import
sys.path.insert(0, str(Path(__file__).parent.parent))

from ipo_engine import IPOAnalysisEngine


def parse_command(command: str) -> dict:
    """解析CLI命令，提取公司名/行业/板块/募资额"""
    command = command.strip()

    # 匹配格式: "IPO分析 公司名 板块 募资X亿"
    patterns = [
        r"IPO[分分]析\s+(.+?)\s+(科创板|创业板|主板|北交所)\s+募资(\d+\.?\d*)(亿|千万|万)",
        r"IPO[分分]析\s+(.+?)\s+(科创板|创业板|主板|北交所)\s+(\d+\.?\d*)(亿|千万|万)",
        r"(.+?)\s+(科创板|创业板|主板|北交所)\s+募资(\d+\.?\d*)(亿|千万|万)",
        r"(.+?)\s+(科创板|创业板|主板|北交所)\s+(\d+\.?\d*)(亿|千万|万)",
    ]

    multiplier_map = {"亿": 1e8, "千万": 1e7, "万": 1e4}

    for pattern in patterns:
        m = re.search(pattern, command)
        if m:
            groups = m.groups()
            if len(groups) == 4:
                company, board, amount_str, unit = groups
            else:
                company, board, amount_str, unit = groups
            amount = float(amount_str) * multiplier_map.get(unit, 1e8)
            return {
                "company": company.strip(),
                "board": board.strip(),
                "amount": amount,
                "raw_amount_str": f"{amount_str}{unit}",
            }

    # 默认值
    return {
        "company": "某科技公司",
        "board": "科创板",
        "amount": 10_000_000_000,
        "raw_amount_str": "10亿",
    }


def detect_industry(company_name: str, board: str) -> str:
    """根据公司名和板块推断行业"""
    name = company_name.lower()
    if any(k in name for k in ["芯片", "半导", "IC"]):
        return "半导体"
    elif any(k in name for k in ["药", "医", "生物", "健康"]):
        return "生物医药"
    elif any(k in name for k in ["云", "AI", "智能", "软件"]):
        return "人工智能"
    elif any(k in name for k in ["光", "新能", "光伏", "锂"]):
        return "光伏新能源"
    elif any(k in name for k in ["通信", "5G", "网络"]):
        return "通信设备"
    elif any(k in name for k in ["消费", "电子", "手机"]):
        return "消费电子"
    elif any(k in name for k in ["银行", "金融", "保险"]):
        return "金融服务"
    else:
        # 根据板块推断
        if board == "科创板":
            return "半导体"
        elif board == "创业板":
            return "医疗器械"
        else:
            return "互联网服务"


def main():
    args = sys.argv[1:]

    if not args:
        print("用法: python3 ipo_cli.py generate \"IPO分析 某科技公司 科创板 募资10亿\"")
        print("或:   python3 ipo_cli.py generate \"某公司 科创板 10亿\"")
        print("参数: python3 ipo_cli.py generate <命令> [--json]")
        sys.exit(1)

    command = " ".join(args)
    json_output = "--json" in command
    command = command.replace("--json", "").strip()

    if args[0] == "generate" and len(args) > 1:
        command = " ".join(args[1:]).replace("--json", "").strip()

    parsed = parse_command(command)
    company = parsed["company"]
    board = parsed["board"]
    amount = parsed["amount"]
    industry = detect_industry(company, board)

    engine = IPOAnalysisEngine()
    result = engine.analyze(
        company_name=company,
        industry=industry,
        board=board,
        fundraising_amount=amount,
    )

    if json_output:
        # JSON格式输出
        output = {
            "company": result.company_name,
            "industry": result.industry,
            "board": result.board,
            "fundraising_billion": result.fundraising_amount / 1e8,
            "price_range": {"low": result.price_range[0], "high": result.price_range[1]},
            "mid_price": result.mid_price,
            "pe_valuation": {
                "low": result.pe_valuation["low_price"],
                "mid": result.pe_valuation["mid_price"],
                "high": result.pe_valuation["high_price"],
                "industry_avg_pe": result.pe_valuation["industry_avg_pe"],
            },
            "pb_valuation": {
                "low": result.pb_valuation["low_price"],
                "mid": result.pb_valuation["mid_price"],
                "high": result.pb_valuation["high_price"],
                "industry_avg_pb": result.pb_valuation["industry_avg_pb"],
            },
            "ps_valuation": {
                "low": result.ps_valuation["low_price"],
                "mid": result.ps_valuation["mid_price"],
                "high": result.ps_valuation["high_price"],
                "industry_avg_ps": result.ps_valuation["industry_avg_ps"],
            },
            "peers": result.peers,
            "winning_rate_percent": result.winning_rate,
            "winning_rate_note": result.winning_rate_note,
            "first_day_prediction": result.first_day_prediction,
            "long_term_outlook": result.long_term_outlook,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        # 文本格式输出
        report = engine.format_report(result)
        print(report)


if __name__ == "__main__":
    main()
