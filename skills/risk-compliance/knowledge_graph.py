#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关联图谱分析模块 v1.0

核心能力:
- 企业关联关系挖掘（股东/高管/担保/交易）
- 团伙欺诈识别（星型/链型/环型网络）
- 担保链风险传导分析
- 资金异常流动检测
- 隐性关联发现（共同地址/电话/IP）

纯规则引擎，零API费用，毫秒级响应
"""

from typing import Dict, Any, List, Set, Tuple
from collections import defaultdict, deque


class KnowledgeGraphBuilder:
    """知识图谱构建器"""
    
    def __init__(self):
        self.nodes = {}  # 节点: {id: {type, name, attrs}}
        self.edges = []  # 边: [(from, to, relation, weight, attrs)]
        self.adjacency = defaultdict(list)  # 邻接表
    
    def add_node(self, node_id: str, node_type: str, name: str, **attrs):
        """添加节点"""
        self.nodes[node_id] = {
            "id": node_id,
            "type": node_type,
            "name": name,
            **attrs
        }
    
    def add_edge(self, from_id: str, to_id: str, relation: str, 
                 weight: float = 1.0, **attrs):
        """添加边"""
        edge = (from_id, to_id, relation, weight, attrs)
        self.edges.append(edge)
        self.adjacency[from_id].append((to_id, relation, weight))
        # 无向图也添加反向
        if relation in ["担保", "关联", "共同股东", "共同高管"]:
            self.adjacency[to_id].append((from_id, relation, weight))
    def get_neighbors(self, node_id: str, relation: str = None) -> List[Tuple]:
        """获取邻居节点"""
        neighbors = self.adjacency.get(node_id, [])
        if relation:
            return [n for n in neighbors if n[1] == relation]
        return neighbors
    
    def find_path(self, start: str, end: str, max_depth: int = 5) -> List[List[str]]:
        """查找两点间所有路径"""
        paths = []
        visited = set()
        
        def dfs(current, target, path, depth):
            if depth > max_depth:
                return
            if current == target and len(path) > 1:
                paths.append(path[:])
                return
            for neighbor, relation, weight in self.adjacency.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    path.append((neighbor, relation, weight))
                    dfs(neighbor, target, path, depth + 1)
                    path.pop()
                    visited.remove(neighbor)
        
        visited.add(start)
        dfs(start, end, [(start, "起点", 1.0)], 0)
        return paths


class FraudPatternDetector:
    """欺诈模式检测器"""
    
    def __init__(self, graph: KnowledgeGraphBuilder):
        self.graph = graph
    
    def detect_star_pattern(self, center_type: str = "账户", 
                           min_spokes: int = 5,
                           min_amount: float = 1000000) -> List[Dict]:
        """
        检测星型转账模式
        多个账户向同一账户转账（洗钱/非法集资特征）
        """
        patterns = []
        
        # 统计每个节点的入度（被转账次数）
        in_degree = defaultdict(list)
        for from_id, to_id, relation, weight, attrs in self.graph.edges:
            if relation == "转账":
                amount = attrs.get("amount", 0)
                in_degree[to_id].append({
                    "from": from_id,
                    "amount": amount,
                    "time": attrs.get("timestamp", "")
                })
        
        # 检测星型
        for node_id, sources in in_degree.items():
            node = self.graph.nodes.get(node_id)
            if not node:
                continue
            
            total_amount = sum(s["amount"] for s in sources)
            unique_sources = len(set(s["from"] for s in sources))
            
            if unique_sources >= min_spokes and total_amount >= min_amount:
                # 检查时间集中度（24小时内）
                timestamps = [s["time"] for s in sources if s["time"]]
                time_concentrated = self._check_time_concentration(timestamps)
                
                patterns.append({
                    "type": "星型转账",
                    "center": node_id,
                    "center_name": node.get("name", ""),
                    "spoke_count": unique_sources,
                    "total_amount": total_amount,
                    "time_concentrated": time_concentrated,
                    "risk_level": "极高" if time_concentrated else "高",
                    "sources": sources[:10],  # 最多显示10个
                })
        
        return sorted(patterns, key=lambda x: x["total_amount"], reverse=True)
    
    def detect_cycle_pattern(self, max_depth: int = 5,
                            min_amount: float = 100000) -> List[Dict]:
        """
        检测循环转账模式
        A→B→C→A（虚构交易/洗钱特征）
        """
        patterns = []
        visited_cycles = set()
        
        for node_id in self.graph.nodes:
            cycles = self._find_cycles_from(node_id, max_depth, min_amount)
            for cycle in cycles:
                # 去重（同一环的不同起点）
                cycle_key = tuple(sorted([n[0] for n in cycle]))
                if cycle_key not in visited_cycles:
                    visited_cycles.add(cycle_key)
                    
                    total_amount = sum(n[2] for n in cycle if isinstance(n[2], (int, float)))
                    node_names = [self.graph.nodes.get(n[0], {}).get("name", n[0]) 
                                 for n in cycle]
                    
                    patterns.append({
                        "type": "循环转账",
                        "cycle_nodes": node_names,
                        "cycle_length": len(cycle),
                        "total_amount": total_amount,
                        "risk_level": "极高",
                    })
        
        return patterns
    
    def detect_chain_pattern(self, max_depth: int = 5,
                            min_length: int = 4) -> List[Dict]:
        """
        检测链式转账模式
        A→B→C→D→E（多层嵌套/规避监管特征）
        """
        patterns = []
        
        for start_id in self.graph.nodes:
            chains = self._find_chains_from(start_id, max_depth, min_length)
            for chain in chains:
                total_amount = sum(n[2] for n in chain if isinstance(n[2], (int, float)))
                node_names = [self.graph.nodes.get(n[0], {}).get("name", n[0]) 
                             for n in chain]
                
                patterns.append({
                    "type": "链式转账",
                    "chain_nodes": node_names,
                    "chain_length": len(chain),
                    "total_amount": total_amount,
                    "risk_level": "高",
                })
        
        return patterns
    
    def detect_hidden_association(self) -> List[Dict]:
        """
        检测隐性关联
        共同地址/电话/IP/设备等
        """
        patterns = []
        
        # 按属性分组
        attr_groups = defaultdict(list)
        for node_id, node in self.graph.nodes.items():
            for attr_key in ["address", "phone", "ip", "device"]:
                attr_val = node.get(attr_key)
                if attr_val:
                    attr_groups[(attr_key, attr_val)].append(node_id)
        
        # 检测共享属性的节点
        for (attr_key, attr_val), node_ids in attr_groups.items():
            if len(node_ids) >= 2:
                node_names = [self.graph.nodes.get(nid, {}).get("name", nid) 
                             for nid in node_ids]
                
                # 检查是否已有显式关联
                has_explicit = False
                for i, n1 in enumerate(node_ids):
                    for n2 in node_ids[i+1:]:
                        if self._has_direct_edge(n1, n2):
                            has_explicit = True
                            break
                    if has_explicit:
                        break
                
                if not has_explicit:
                    patterns.append({
                        "type": "隐性关联",
                        "attribute": attr_key,
                        "value": attr_val,
                        "nodes": node_names,
                        "node_count": len(node_ids),
                        "risk_level": "高" if len(node_ids) >= 3 else "中",
                    })
        
        return patterns
    
    def detect_guarantee_chain(self, max_depth: int = 5) -> List[Dict]:
        """
        检测担保链风险
        A担保B，B担保C，C担保D...（风险传导）
        """
        patterns = []
        visited = set()
        
        for start_id in self.graph.nodes:
            if start_id in visited:
                continue
            
            chain = self._find_guarantee_chain(start_id, max_depth)
            if len(chain) >= 3:
                visited.update([n[0] for n in chain])
                
                node_names = [self.graph.nodes.get(n[0], {}).get("name", n[0]) 
                             for n in chain]
                total_exposure = sum(n[2] for n in chain if isinstance(n[2], (int, float)))
                
                patterns.append({
                    "type": "担保链",
                    "chain_nodes": node_names,
                    "chain_length": len(chain),
                    "total_exposure": total_exposure,
                    "risk_level": "极高" if len(chain) >= 5 else "高",
                    "suggestion": "建议逐层穿透审查，评估最终担保人偿付能力",
                })
        
        return patterns
    
    def _check_time_concentration(self, timestamps: List[str]) -> bool:
        """检查时间是否集中（24小时内）"""
        if not timestamps or len(timestamps) < 2:
            return False
        # 简化判断：如果有超过50%的时间戳在相同日期
        from collections import Counter
        dates = [ts[:10] if len(ts) >= 10 else ts for ts in timestamps]
        date_counts = Counter(dates)
        most_common = date_counts.most_common(1)
        if most_common:
            return most_common[0][1] / len(dates) >= 0.5
        return False
    
    def _find_cycles_from(self, start: str, max_depth: int, 
                          min_amount: float) -> List[List]:
        """从某节点查找环"""
        cycles = []
        visited = {start}
        
        def dfs(current, path, depth):
            if depth > max_depth:
                return
            for neighbor, relation, weight in self.graph.adjacency.get(current, []):
                if relation != "转账":
                    continue
                if neighbor == start and len(path) >= 2:
                    cycles.append(path[:])
                elif neighbor not in visited:
                    visited.add(neighbor)
                    path.append((neighbor, relation, weight))
                    dfs(neighbor, path, depth + 1)
                    path.pop()
                    visited.remove(neighbor)
        
        dfs(start, [(start, "起点", 0)], 0)
        return cycles
    
    def _find_chains_from(self, start: str, max_depth: int,
                          min_length: int) -> List[List]:
        """从某节点查找链"""
        chains = []
        visited = {start}
        
        def dfs(current, path, depth):
            if depth > max_depth:
                return
            if len(path) >= min_length:
                chains.append(path[:])
            for neighbor, relation, weight in self.graph.adjacency.get(current, []):
                if relation != "转账":
                    continue
                if neighbor not in visited:
                    visited.add(neighbor)
                    path.append((neighbor, relation, weight))
                    dfs(neighbor, path, depth + 1)
                    path.pop()
                    visited.remove(neighbor)
        
        dfs(start, [(start, "起点", 0)], 0)
        return chains
    
    def _has_direct_edge(self, n1: str, n2: str) -> bool:
        """检查两节点是否有直接边"""
        for from_id, to_id, _, _, _ in self.graph.edges:
            if (from_id == n1 and to_id == n2) or (from_id == n2 and to_id == n1):
                return True
        return False
    
    def _find_guarantee_chain(self, start: str, max_depth: int) -> List[List]:
        """查找担保链"""
        chain = []
        visited = {start}
        current = start
        
        while True:
            chain.append((current, "担保", 0))
            found_next = False
            for neighbor, relation, weight in self.graph.adjacency.get(current, []):
                if relation == "担保" and neighbor not in visited:
                    visited.add(neighbor)
                    current = neighbor
                    found_next = True
                    break
            if not found_next or len(chain) >= max_depth:
                break
        
        return chain


class GraphFormatter:
    """图谱格式化器"""
    
    @staticmethod
    def format_star_pattern(patterns: List[Dict]) -> str:
        """格式化星型模式"""
        if not patterns:
            return "✅ 未检测到星型转账模式"
        
        lines = [
            "## 🕸️ 星型转账风险预警",
            "",
            f"**发现 {len(patterns)} 个可疑星型网络**",
            "",
        ]
        
        for i, p in enumerate(patterns[:3], 1):  # 最多显示3个
            level_emoji = "🔴" if p["risk_level"] == "极高" else "🟡"
            lines.extend([
                f"### 网络 {i}: {p['center_name']}",
                "",
                f"- **中心节点**: {p['center_name']}",
                f"- **关联账户数**: {p['spoke_count']} 个",
                f"- **涉及金额**: ¥{p['total_amount']:,.0f}",
                f"- **时间集中度**: {'是' if p['time_concentrated'] else '否'}",
                f"- **风险等级**: {level_emoji} {p['risk_level']}",
                "",
                "**资金来源（前5）**:",
            ])
            
            for s in p["sources"][:5]:
                from_node = s["from"]
                lines.append(f"- {from_node}: ¥{s['amount']:,.0f}")
            
            lines.append("")
        
        lines.extend([
            "### 处置建议",
            "",
            "> 建议立即冻结中心账户，逐笔核实资金来源，排查是否涉及非法集资或洗钱活动。",
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def format_cycle_pattern(patterns: List[Dict]) -> str:
        """格式化循环模式"""
        if not patterns:
            return "✅ 未检测到循环转账模式"
        
        lines = [
            "## 🔄 循环转账风险预警",
            "",
            f"**发现 {len(patterns)} 个可疑资金循环**",
            "",
        ]
        
        for i, p in enumerate(patterns[:3], 1):
            nodes_str = " → ".join(p["cycle_nodes"])
            lines.extend([
                f"### 循环 {i}",
                "",
                f"**路径**: {nodes_str} → {p['cycle_nodes'][0]}",
                f"**涉及节点**: {p['cycle_length']} 个",
                f"**涉及金额**: ¥{p['total_amount']:,.0f}",
                f"**风险等级**: 🔴 {p['risk_level']}",
                "",
            ])
        
        lines.extend([
            "### 处置建议",
            "",
            "> 循环转账是虚构交易或洗钱的典型特征，建议深入核查交易背景真实性。",
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def format_hidden_association(patterns: List[Dict]) -> str:
        """格式化隐性关联"""
        if not patterns:
            return "✅ 未检测到隐性关联"
        
        lines = [
            "## 👥 隐性关联风险预警",
            "",
            f"**发现 {len(patterns)} 组隐性关联**",
            "",
        ]
        
        attr_names = {
            "address": "注册地址",
            "phone": "联系电话",
            "ip": "IP地址",
            "device": "设备指纹",
        }
        
        for i, p in enumerate(patterns[:5], 1):
            level_emoji = "🔴" if p["risk_level"] == "高" else "🟡"
            attr_name = attr_names.get(p["attribute"], p["attribute"])
            
            lines.extend([
                f"### 关联 {i}",
                "",
                f"**关联类型**: {attr_name}",
                f"**关联值**: `{p['value']}`",
                f"**涉及主体**: {p['node_count']} 个",
                f"**风险等级**: {level_emoji} {p['risk_level']}",
                "",
                "**关联主体**:",
            ])
            
            for node in p["nodes"]:
                lines.append(f"- {node}")
            
            lines.append("")
        
        lines.extend([
            "### 处置建议",
            "",
            "> 隐性关联可能是空壳公司集群或团伙作案的信号，建议实地核查经营场所真实性。",
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def format_guarantee_chain(patterns: List[Dict]) -> str:
        """格式化担保链"""
        if not patterns:
            return "✅ 未检测到担保链风险"
        
        lines = [
            "## ⛓️ 担保链风险预警",
            "",
            f"**发现 {len(patterns)} 条担保链**",
            "",
        ]
        
        for i, p in enumerate(patterns[:3], 1):
            nodes_str = " → ".join(p["chain_nodes"])
            level_emoji = "🔴" if p["risk_level"] == "极高" else "🟡"
            
            lines.extend([
                f"### 担保链 {i}",
                "",
                f"**担保路径**: {nodes_str}",
                f"**链长**: {p['chain_length']} 层",
                f"**总敞口**: ¥{p['total_exposure']:,.0f}",
                f"**风险等级**: {level_emoji} {p['risk_level']}",
                "",
                f"**建议**: {p['suggestion']}",
                "",
            ])
        
        lines.extend([
            "### 风险说明",
            "",
            "> 担保链越长，风险传导效应越强。一旦中间环节违约，可能引发连锁反应。",
        ])
        
        return "\n".join(lines)
    
    @staticmethod
    def format_comprehensive_report(all_patterns: Dict[str, List[Dict]]) -> str:
        """格式化综合报告"""
        total_risk = sum(len(v) for v in all_patterns.values())
        
        lines = [
            "## 📊 关联图谱风险分析报告",
            "",
            f"**检测时间**: 2026-06-06",
            f"**检测维度**: 5 项",
            f"**发现风险**: {total_risk} 处",
            "",
            "### 风险汇总",
            "",
            "| 检测项 | 发现数量 | 最高风险 |",
            "|:---|---:|:---|",
        ]
        
        risk_summary = [
            ("星型转账", all_patterns.get("star", [])),
            ("循环转账", all_patterns.get("cycle", [])),
            ("链式转账", all_patterns.get("chain", [])),
            ("隐性关联", all_patterns.get("hidden", [])),
            ("担保链", all_patterns.get("guarantee", [])),
        ]
        
        for name, patterns in risk_summary:
            count = len(patterns)
            max_risk = "🔴 极高"
            for p in patterns:
                if p.get("risk_level") == "极高":
                    max_risk = "🔴 极高"
                    break
                elif p.get("risk_level") == "高":
                    max_risk = "🟡 高"
            if count == 0:
                max_risk = "🟢 无"
            lines.append(f"| {name} | {count} | {max_risk} |")
        
        lines.append("")
        
        # 详细结果
        if all_patterns.get("star"):
            lines.append(GraphFormatter.format_star_pattern(all_patterns["star"]))
            lines.append("")
        if all_patterns.get("cycle"):
            lines.append(GraphFormatter.format_cycle_pattern(all_patterns["cycle"]))
            lines.append("")
        if all_patterns.get("hidden"):
            lines.append(GraphFormatter.format_hidden_association(all_patterns["hidden"]))
            lines.append("")
        if all_patterns.get("guarantee"):
            lines.append(GraphFormatter.format_guarantee_chain(all_patterns["guarantee"]))
            lines.append("")
        
        return "\n".join(lines)


# ============ 演示数据构建 ============

def build_demo_graph() -> KnowledgeGraphBuilder:
    """构建演示知识图谱"""
    graph = KnowledgeGraphBuilder()
    
    # 添加账户节点
    accounts = [
        ("A001", "账户A", "企业", {"address": "北京市海淀区", "phone": "13800138001"}),
        ("A002", "账户B", "企业", {"address": "北京市海淀区", "phone": "13800138002"}),
        ("A003", "账户C", "企业", {"address": "上海市浦东新区", "phone": "13800138003"}),
        ("A004", "账户D", "个人", {"address": "深圳市南山区", "phone": "13800138004"}),
        ("A005", "账户E", "个人", {"address": "深圳市南山区", "phone": "13800138005"}),
        ("A006", "账户F", "企业", {"address": "北京市海淀区", "phone": "13800138001"}),  # 共享电话
        ("A007", "账户G", "个人", {"address": "广州市天河区", "phone": "13800138007"}),
        ("A008", "账户H", "企业", {"address": "杭州市西湖区", "phone": "13800138008"}),
    ]
    
    for acc_id, name, acc_type, attrs in accounts:
        graph.add_node(acc_id, "账户", name, account_type=acc_type, **attrs)
    
    # 添加转账边（星型：多个账户向A001转账）
    transfers = [
        ("A002", "A001", "转账", 500000, {"amount": 500000, "timestamp": "2026-06-01T10:00:00"}),
        ("A003", "A001", "转账", 300000, {"amount": 300000, "timestamp": "2026-06-01T11:00:00"}),
        ("A004", "A001", "转账", 200000, {"amount": 200000, "timestamp": "2026-06-01T12:00:00"}),
        ("A005", "A001", "转账", 150000, {"amount": 150000, "timestamp": "2026-06-01T13:00:00"}),
        ("A006", "A001", "转账", 100000, {"amount": 100000, "timestamp": "2026-06-01T14:00:00"}),
        ("A007", "A001", "转账", 80000, {"amount": 80000, "timestamp": "2026-06-01T15:00:00"}),
        # 循环转账
        ("A001", "A002", "转账", 100000, {"amount": 100000, "timestamp": "2026-06-02T10:00:00"}),
        ("A002", "A003", "转账", 100000, {"amount": 100000, "timestamp": "2026-06-02T11:00:00"}),
        ("A003", "A001", "转账", 100000, {"amount": 100000, "timestamp": "2026-06-02T12:00:00"}),
        # 链式转账
        ("A004", "A005", "转账", 50000, {"amount": 50000, "timestamp": "2026-06-03T10:00:00"}),
        ("A005", "A007", "转账", 50000, {"amount": 50000, "timestamp": "2026-06-03T11:00:00"}),
        ("A007", "A008", "转账", 50000, {"amount": 50000, "timestamp": "2026-06-03T12:00:00"}),
        # 担保链
        ("A001", "A002", "担保", 0, {"amount": 1000000}),
        ("A002", "A003", "担保", 0, {"amount": 800000}),
        ("A003", "A004", "担保", 0, {"amount": 500000}),
    ]
    
    for from_id, to_id, relation, weight, attrs in transfers:
        graph.add_edge(from_id, to_id, relation, weight, **attrs)
    
    return graph


if __name__ == "__main__":
    # 构建演示图谱
    graph = build_demo_graph()
    detector = FraudPatternDetector(graph)
    formatter = GraphFormatter()
    
    # 检测所有模式
    all_patterns = {
        "star": detector.detect_star_pattern(),
        "cycle": detector.detect_cycle_pattern(),
        "chain": detector.detect_chain_pattern(),
        "hidden": detector.detect_hidden_association(),
        "guarantee": detector.detect_guarantee_chain(),
    }
    
    # 输出综合报告
    print(formatter.format_comprehensive_report(all_patterns))
