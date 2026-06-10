#!/usr/bin/env python3
"""
厅堂智能分流 CLI
Usage: python3 routing_cli.py generate "智能分流 60岁老人 办理存款 等候20分钟 普通客户"
"""

import sys
import os

# Resolve paths properly: script is in skills/lobby_routing/scripts/
# We need to add skills/ to path so lobby_routing can be imported
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# _SCRIPT_DIR = .../skills/lobby_routing/scripts
_LOBBY_ROUTING_DIR = os.path.dirname(_SCRIPT_DIR)  # .../skills/lobby_routing
_SKILLS_DIR = os.path.dirname(_LOBBY_ROUTING_DIR)   # .../skills
sys.path.insert(0, _SKILLS_DIR)

from lobby_routing import LobbyRoutingEngine


def generate(query: str) -> str:
    """执行分流并返回结果"""
    engine = LobbyRoutingEngine()
    result = engine.route_from_text(query)
    return str(result)


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 routing_cli.py generate \"智能分流 60岁老人 办理存款 等候20分钟 普通客户\"")
        sys.exit(1)

    command = sys.argv[1]
    query = sys.argv[2]

    if command == "generate":
        result = generate(query)
        print(result)
    else:
        print(f"Unknown command: {command}")
        print("Available commands: generate")
        sys.exit(1)


if __name__ == "__main__":
    main()
