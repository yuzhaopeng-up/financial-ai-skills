#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Stars/Forks 自动追踪脚本

功能:
1. 每日抓取 GitHub 仓库 Stars、Forks、Watchers 数据
2. 存储到 SQLite 数据库
3. 生成趋势图表（HTML）
4. 里程碑庆祝通知

用法:
    python github_metrics_tracker.py --init          # 初始化数据库
    python github_metrics_tracker.py --daily         # 每日更新
    python github_metrics_tracker.py --report        # 生成周报
    python github_metrics_tracker.py --chart         # 生成图表

定时任务（crontab）:
    0 9 * * * cd /path/to/repo && python scripts/github_metrics_tracker.py --daily
"""

import os
import sys
import sqlite3
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path

# 配置
REPO_OWNER = "yuzhaopeng-up"
REPO_NAME = "financial-ai-skills"
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "github_metrics.db")
CHART_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "stars_chart.html")

# 里程碑
MILESTONES = [10, 50, 100, 500, 1000, 5000]


class GitHubMetricsTracker:
    """GitHub指标追踪器"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self._ensure_db()
    
    def _ensure_db(self):
        """确保数据库和表存在"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                stars INTEGER DEFAULT 0,
                forks INTEGER DEFAULT 0,
                watchers INTEGER DEFAULT 0,
                open_issues INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                milestone INTEGER NOT NULL,
                reached_date TEXT,
                notified INTEGER DEFAULT 0
            )
        ''')
        
        # 初始化里程碑
        for m in MILESTONES:
            cursor.execute('''
                INSERT OR IGNORE INTO milestones (milestone) VALUES (?)
            ''', (m,))
        
        conn.commit()
        conn.close()
    
    def fetch_metrics(self) -> Dict[str, Any]:
        """
        从GitHub API获取仓库指标
        
        注意: 不需要Token即可获取公开仓库的基本信息
        """
        import urllib.request
        
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
        
        try:
            req = urllib.request.Request(url)
            req.add_header('Accept', 'application/vnd.github.v3+json')
            req.add_header('User-Agent', 'Financial-AI-Skills-Tracker')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                return {
                    'stars': data.get('stargazers_count', 0),
                    'forks': data.get('forks_count', 0),
                    'watchers': data.get('watchers_count', 0),
                    'open_issues': data.get('open_issues_count', 0),
                    'success': True
                }
        except Exception as e:
            print(f"❌ 获取GitHub数据失败: {e}")
            return {
                'stars': 0, 'forks': 0, 'watchers': 0, 'open_issues': 0,
                'success': False, 'error': str(e)
            }
    
    def save_metrics(self, metrics: Dict[str, Any]) -> bool:
        """保存指标到数据库"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO metrics 
            (date, stars, forks, watchers, open_issues)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            today,
            metrics.get('stars', 0),
            metrics.get('forks', 0),
            metrics.get('watchers', 0),
            metrics.get('open_issues', 0)
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ 已保存 {today} 数据: ⭐{metrics['stars']} | 🍴{metrics['forks']} | 👁️{metrics['watchers']}")
        return True
    
    def check_milestones(self) -> list:
        """检查是否达到里程碑"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取最新数据
        cursor.execute('SELECT stars FROM metrics ORDER BY date DESC LIMIT 1')
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return []
        
        current_stars = row[0]
        
        # 检查未通知的里程碑
        cursor.execute('''
            SELECT milestone FROM milestones 
            WHERE reached_date IS NULL AND milestone <= ?
            ORDER BY milestone ASC
        ''', (current_stars,))
        
        reached = cursor.fetchall()
        
        # 更新已达到的里程碑
        today = datetime.now().strftime('%Y-%m-%d')
        for (milestone,) in reached:
            cursor.execute('''
                UPDATE milestones 
                SET reached_date = ?, notified = 1 
                WHERE milestone = ?
            ''', (today, milestone))
            print(f"🎉 里程碑达成: {milestone} Stars!")
        
        conn.commit()
        conn.close()
        
        return [m[0] for m in reached]
    
    def generate_report(self, days: int = 7) -> str:
        """生成周报"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT date, stars, forks, watchers, open_issues
            FROM metrics
            WHERE date >= ?
            ORDER BY date ASC
        ''', (since,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < 2:
            return "数据不足，无法生成报告"
        
        first = rows[0]
        last = rows[-1]
        
        stars_diff = last[1] - first[1]
        forks_diff = last[2] - first[2]
        
        report = f"""
📊 GitHub 周报 ({first[0]} ~ {last[0]})

⭐ Stars: {last[1]} ({'+' if stars_diff >= 0 else ''}{stars_diff})
🍴 Forks: {last[2]} ({'+' if forks_diff >= 0 else ''}{forks_diff})
👁️ Watchers: {last[3]}
🐛 Open Issues: {last[4]}

📈 日均增长: {stars_diff / max(len(rows)-1, 1):.1f} Stars/天
"""
        return report
    
    def generate_chart(self) -> str:
        """生成趋势图表HTML"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, stars, forks
            FROM metrics
            ORDER BY date ASC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return "暂无数据"
        
        dates = [r[0] for r in rows]
        stars = [r[1] for r in rows]
        forks = [r[2] for r in rows]
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Financial AI Skills - Stars趋势</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ color: #333; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat {{ background: #f5f5f5; padding: 15px; border-radius: 8px; flex: 1; text-align: center; }}
        .stat-value {{ font-size: 2em; font-weight: bold; color: #5865F2; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🦞 Financial AI Skills - GitHub趋势</h1>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{stars[-1]}</div>
                <div class="stat-label">⭐ Stars</div>
            </div>
            <div class="stat">
                <div class="stat-value">{forks[-1]}</div>
                <div class="stat-label">🍴 Forks</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(rows)}</div>
                <div class="stat-label">📅 记录天数</div>
            </div>
        </div>
        <canvas id="chart" width="800" height="400"></canvas>
    </div>
    <script>
        const ctx = document.getElementById('chart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(dates)},
                datasets: [
                    {{
                        label: '⭐ Stars',
                        data: {json.dumps(stars)},
                        borderColor: '#5865F2',
                        backgroundColor: 'rgba(88, 101, 242, 0.1)',
                        tension: 0.3
                    }},
                    {{
                        label: '🍴 Forks',
                        data: {json.dumps(forks)},
                        borderColor: '#3BA55C',
                        backgroundColor: 'rgba(59, 165, 92, 0.1)',
                        tension: 0.3
                    }}
                ]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Stars & Forks 趋势'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>'''
        
        os.makedirs(os.path.dirname(CHART_PATH), exist_ok=True)
        with open(CHART_PATH, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ 图表已生成: {CHART_PATH}")
        return CHART_PATH


def main():
    parser = argparse.ArgumentParser(description='GitHub Metrics Tracker')
    parser.add_argument('--init', action='store_true', help='初始化数据库')
    parser.add_argument('--daily', action='store_true', help='每日更新')
    parser.add_argument('--report', action='store_true', help='生成周报')
    parser.add_argument('--chart', action='store_true', help='生成图表')
    
    args = parser.parse_args()
    
    tracker = GitHubMetricsTracker()
    
    if args.init:
        print("✅ 数据库初始化完成")
        return
    
    if args.daily:
        print("🔄 获取GitHub数据...")
        metrics = tracker.fetch_metrics()
        
        if metrics['success']:
            tracker.save_metrics(metrics)
            tracker.check_milestones()
        else:
            print("❌ 数据获取失败，跳过保存")
        return
    
    if args.report:
        report = tracker.generate_report()
        print(report)
        return
    
    if args.chart:
        tracker.generate_chart()
        return
    
    # 默认: 显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()
