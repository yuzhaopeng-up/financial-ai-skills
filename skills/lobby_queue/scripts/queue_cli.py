#!/usr/bin/env python3
"""
Lobby Queue CLI — 排队预警命令行工具

用法：
    python queue_cli.py generate "排队预警 非现金区3人等候 等待最长达25分钟"
    python queue_cli.py analyze <json_data>
    python queue_cli.py server

示例：
    python queue_cli.py generate "排队预警 现金区5人等候 30分钟"
    python queue_cli.py generate "排队预警 贵宾区2人等候"
"""

import argparse
import json
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from queue_engine import LobbyQueueEngine, analyze_queue


def cmd_generate(args):
    """生成排队预警分析报告"""
    text = args.text or args.query
    if not text:
        print("错误：请提供输入文本", file=sys.stderr)
        sys.exit(1)

    result = analyze_queue(text)
    if not result:
        print("错误：无法解析输入，请检查格式", file=sys.stderr)
        print("支持格式：排队预警 [区域]人数等候 等待最长达[分钟]分钟", file=sys.stderr)
        print("区域可选：现金区/非现金区/贵宾区/综合区", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        engine = LobbyQueueEngine()
        analysis = engine.analyze(text)
        print(engine.format_report(analysis))


def cmd_analyze(args):
    """分析JSON格式的排队数据"""
    try:
        data = json.loads(args.json_data)
    except json.JSONDecodeError:
        print("错误：无效的JSON格式", file=sys.stderr)
        sys.exit(1)

    engine = LobbyQueueEngine()
    analysis = engine.analyze_from_dict(data)

    if args.format == "json":
        print(json.dumps(analysis.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(engine.format_report(analysis))


def cmd_server(args):
    """启动简单的HTTP服务器（用于调试）"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import urllib.parse

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = urllib.parse.parse_qs(post_data.decode('utf-8'))

            text = params.get('text', [''])[0]
            result = analyze_queue(text)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result or {}, ensure_ascii=False).encode())

        def log_message(self, format, *args):
            pass  # 静默日志

    server = HTTPServer(('0.0.0.0', args.port), Handler)
    print(f"🚀 排队预警服务已启动：http://0.0.0.0:{args.port}")
    print("按 Ctrl+C 停止服务")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
        server.shutdown()


def main():
    parser = argparse.ArgumentParser(
        description="🏧 Lobby Queue CLI — 排队预警命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python queue_cli.py generate "排队预警 非现金区3人等候 等待最长达25分钟"
  python queue_cli.py generate "排队预警 现金区5人等候 30分钟" --format json
  python queue_cli.py analyze '{"region":"非现金区","waiting_count":3,"max_wait":25}'
  python queue_cli.py server --port 8080

支持格式：
  排队预警 [区域][人数]人等候 [等待最长达][分钟]分钟
  区域：现金区/非现金区/贵宾区/综合区（默认非现金区）
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # generate 命令
    gen_parser = subparsers.add_parser("generate", help="生成排队预警分析报告")
    gen_parser.add_argument("text", nargs="?", help="输入文本")
    gen_parser.add_argument("-q", "--query", dest="query", help="输入文本（别名）")
    gen_parser.add_argument("-f", "--format", choices=["text", "json"], default="text",
                           help="输出格式（默认text）")
    gen_parser.set_defaults(func=cmd_generate)

    # analyze 命令
    anal_parser = subparsers.add_parser("analyze", help="分析JSON格式的排队数据")
    anal_parser.add_argument("json_data", help="JSON格式的排队数据")
    anal_parser.add_argument("-f", "--format", choices=["text", "json"], default="text",
                            help="输出格式（默认text）")
    anal_parser.set_defaults(func=cmd_analyze)

    # server 命令
    serv_parser = subparsers.add_parser("server", help="启动HTTP服务")
    serv_parser.add_argument("-p", "--port", type=int, default=8080, help="服务端口（默认8080）")
    serv_parser.set_defaults(func=cmd_server)

    args = parser.parse_args()

    if args.command is None:
        # 默认执行generate，尝试读取剩余参数
        if len(sys.argv) > 1:
            args.text = sys.argv[1]
            args.format = "text"
            cmd_generate(args)
        else:
            parser.print_help()
            sys.exit(1)
    else:
        args.func(args)


if __name__ == "__main__":
    main()
