#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALM CLI - 资产负债管理命令行工具

用法：
    python3 alm_cli.py generate "ALM 资产500亿 定期存款60% 活期30%"
    python3 alm_cli.py analyze --data '{"total_assets": 500000000000, ...}'
    python3 alm_cli.py serve --port 8080
    python3 alm_cli.py compare "ALM 资产500亿..." "ALM 资产800亿..."
"""

import argparse
import json
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

import sys
import os
from pathlib import Path

# 添加父目录到路径以支持直接运行
sys.path.insert(0, str(Path(__file__).parent.parent))

from alm_engine import ALMEngine, analyze, summarize


def cmd_generate(args):
    """生成 ALM 分析报告"""
    text = args.text or args.query
    if not text:
        print("错误：必须提供分析文本，例如：ALM 资产500亿 定期存款60% 活期30%", file=sys.stderr)
        sys.exit(1)
    
    if args.format == "json":
        result = analyze(text)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.format == "summary":
        print(summarize(text))
    else:
        # 默认 both
        print(summarize(text))
        if args.verbose:
            print("\n" + "=" * 60)
            print("JSON 原始数据：")
            print(json.dumps(analyze(text), ensure_ascii=False, indent=2))


def cmd_analyze(args):
    """使用 JSON 数据进行分析"""
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError as e:
            print(f"错误：无效的 JSON 格式 - {e}", file=sys.stderr)
            sys.exit(1)
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        print("错误：必须提供 --data 或 --file 参数", file=sys.stderr)
        sys.exit(1)
    
    engine = ALMEngine()
    engine.load(data)
    
    if args.format == "json":
        print(json.dumps(engine.analyze(), ensure_ascii=False, indent=2))
    else:
        print(engine.summary())


def cmd_compare(args):
    """对比分析两个场景"""
    if len(args.scenarios) < 2:
        print("错误：compare 命令需要至少两个场景", file=sys.stderr)
        sys.exit(1)
    
    results = []
    for i, text in enumerate(args.scenarios):
        print(f"\n{'='*60}")
        print(f"场景 {i+1}: {text}")
        print("="*60)
        engine = ALMEngine()
        engine.parse(text)
        result = engine.analyze()
        results.append(result)
        print(engine.summary())
    
    if args.format == "json":
        print("\n" + "="*60)
        print("对比 JSON：")
        print(json.dumps(results, ensure_ascii=False, indent=2))


class ALMHTTPHandler(BaseHTTPRequestHandler):
    """HTTP 服务处理器"""
    
    def do_GET(self):
        """GET 请求：健康检查"""
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("ALM Engine OK".encode("utf-8"))
    
    def do_POST(self):
        """POST 请求：执行分析"""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            
            # 尝试解析 JSON
            try:
                data = json.loads(body)
                engine = ALMEngine()
                engine.load(data)
                result = engine.analyze()
            except json.JSONDecodeError:
                # 尝试作为中文文本处理
                engine = ALMEngine()
                engine.parse(body)
                result = engine.analyze()
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8"))
        
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            error_result = {"error": str(e)}
            self.wfile.write(json.dumps(error_result, ensure_ascii=False).encode("utf-8"))
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        sys.stderr.write(f"[ALM Server] {args[0]}\n")


def cmd_serve(args):
    """启动 HTTP 服务"""
    port = args.port
    server = HTTPServer(("0.0.0.0", port), ALMHTTPHandler)
    print(f"ALM Engine HTTP Server 启动于 http://0.0.0.0:{port}")
    print(f"  POST /  → 执行分析（JSON body 或中文文本）")
    print(f"  GET  /  → 健康检查")
    print("按 Ctrl+C 停止服务器")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        server.shutdown()


def main():
    parser = argparse.ArgumentParser(
        description="ALM 资产负债管理分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python3 alm_cli.py generate "ALM 资产500亿 定期存款60% 活期30%"
  python3 alm_cli.py generate "ALM 资产1000亿 同业负债15%" --format=json
  python3 alm_cli.py analyze --data '{"total_assets": 500000000000}'
  python3 alm_cli.py compare "ALM 资产500亿..." "ALM 资产800亿..."
  python3 alm_cli.py serve --port 8080
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # generate 命令
    gen_parser = subparsers.add_parser("generate", help="从中文文本生成 ALM 分析")
    gen_parser.add_argument("text", nargs="?", help="分析文本，如：ALM 资产500亿 定期存款60% 活期30%")
    gen_parser.add_argument("-q", "--query", dest="query", help="分析文本（另一种写法）")
    gen_parser.add_argument("-f", "--format", choices=["summary", "json", "both"], default="both", help="输出格式")
    gen_parser.add_argument("-v", "--verbose", action="store_true", help="显示详细信息")
    gen_parser.set_defaults(func=cmd_generate)
    
    # analyze 命令
    ana_parser = subparsers.add_parser("analyze", help="使用 JSON 数据执行分析")
    ana_parser.add_argument("-d", "--data", help="JSON 格式数据")
    ana_parser.add_argument("-f", "--file", help="JSON 文件路径")
    ana_parser.add_argument("--format", choices=["summary", "json"], default="summary", help="输出格式")
    ana_parser.set_defaults(func=cmd_analyze)
    
    # compare 命令
    cmp_parser = subparsers.add_parser("compare", help="对比多个场景")
    cmp_parser.add_argument("scenarios", nargs="+", help="多个 ALM 分析文本")
    cmp_parser.add_argument("-f", "--format", choices=["summary", "json"], default="summary", help="输出格式")
    cmp_parser.set_defaults(func=cmd_compare)
    
    # serve 命令
    srv_parser = subparsers.add_parser("serve", help="启动 HTTP 服务")
    srv_parser.add_argument("-p", "--port", type=int, default=8080, help="服务端口")
    srv_parser.set_defaults(func=cmd_serve)
    
    args = parser.parse_args()
    
    if args.command is None:
        # 默认行为：当作 generate 命令处理
        if len(sys.argv) > 1:
            # 把剩余参数当作文本处理
            args.text = " ".join(sys.argv[1:])
            args.format = "both"
            args.verbose = False
            cmd_generate(args)
        else:
            parser.print_help()
            sys.exit(1)
    else:
        args.func(args)


if __name__ == "__main__":
    main()
