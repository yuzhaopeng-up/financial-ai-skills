"""
顶层 API：MaterialChecker —— 进件材料完整性 + 合规性核对引擎。
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from .checker_engine import (
        MaterialDoc, CheckIssue, CheckReport,
        FIELD_RULES, SCENARIO_RULES,
    )
    from .rule_runner import RuleRunner
except ImportError:
    from checker_engine import (
        MaterialDoc, CheckIssue, CheckReport,
        FIELD_RULES, SCENARIO_RULES,
    )
    from rule_runner import RuleRunner


class MaterialChecker:
    """
    使用示例:
        checker = MaterialChecker()
        report = checker.check("sme_loan", docs=[...])
        print(MaterialReportFormatter.to_text(report))
    """

    def __init__(self, rules: Optional[Dict[str, Any]] = None):
        self.rules = rules or SCENARIO_RULES

    def list_scenarios(self) -> List[Dict[str, Any]]:
        return [
            {"key": k, "name": v["name"], "required_count": len(v["required_docs"])}
            for k, v in self.rules.items()
        ]

    def get_required_docs(self, scenario_key: str) -> List[str]:
        s = self.rules.get(scenario_key)
        return s["required_docs"] if s else []

    def check(
        self,
        scenario_key: str,
        docs: List[MaterialDoc],
        today: Optional[datetime] = None,
    ) -> CheckReport:
        scenario = self.rules.get(scenario_key)
        if not scenario:
            raise ValueError(f"未知场景: {scenario_key}")
        today = today or datetime.now()
        docs_by_type: Dict[str, MaterialDoc] = {d.doc_type: d for d in docs}

        # 1) 完整性检查 —— 必需文档
        submitted = sorted(docs_by_type.keys())
        required = scenario["required_docs"]
        missing = [d for d in required if d not in docs_by_type]

        issues: List[CheckIssue] = []
        for m in missing:
            issues.append(CheckIssue(
                severity="missing",
                doc_type=m,
                message=f"必备材料缺失: {m}",
                suggestion=f"请上传 {m}",
                rule_id=f"MISSING-{m}",
            ))

        # 2) 字段级校验
        runner = RuleRunner(docs_by_type, today=today)
        issues.extend(runner.check_field_formats(scenario.get("doc_field_requirements", {})))

        # 3) 业务规则
        issues.extend(runner.run_extra_rules(scenario.get("extra_rules", [])))

        # 4) 评分与结论
        score, passed, summary = self._score(scenario, required, missing, issues)

        return CheckReport(
            scenario=scenario["name"],
            submitted=submitted,
            required=required,
            missing=missing,
            issues=issues,
            score=score,
            pass_=passed,
            summary=summary,
            generated_at=today.strftime("%Y-%m-%d %H:%M:%S"),
        )

    @staticmethod
    def _score(scenario, required, missing, issues):
        sev_weight = {
            "missing": 15.0,
            "expired": 12.0,
            "invalid": 8.0,
            "mismatch": 10.0,
            "warning": 3.0,
        }
        penalty = sum(sev_weight.get(i.severity, 5.0) for i in issues)
        score = max(0.0, 100.0 - penalty)
        # 通过条件：无缺失、无 expired、无 mismatch、无 invalid
        critical = [i for i in issues if i.severity in ("missing", "expired", "mismatch", "invalid")]
        passed = len(critical) == 0
        if passed:
            summary = (
                f"✅ 进件材料齐全合规，可进入下一审批环节。"
                f"共提交 {len(scenario['required_docs'])} 类必备材料、"
                f"{len(issues)} 项提示/建议（非阻断）。"
            )
        else:
            summary = (
                f"❌ 进件材料存在 {len(critical)} 项阻断问题，需补充/修正后重新提交。"
                f"其中缺失材料 {len(missing)} 类，字段类问题 "
                f"{len(critical) - len(missing)} 项。"
            )
        return round(score, 1), passed, summary


# ============================================================
# 报告渲染
# ============================================================


class MaterialReportFormatter:
    """文本 / JSON / 企微卡片 三种输出格式。"""

    SEV_ICONS = {
        "missing": "❌",
        "expired": "⏰",
        "invalid": "⚠️",
        "mismatch": "🔁",
        "warning": "ℹ️",
    }

    SEV_NAME = {
        "missing": "缺失",
        "expired": "过期",
        "invalid": "无效",
        "mismatch": "不一致",
        "warning": "提示",
    }

    @classmethod
    def to_text(cls, report: CheckReport) -> str:
        lines = []
        lines.append("=" * 56)
        lines.append(f"📋 进件材料核对报告 - {report.scenario}")
        lines.append(f"📅 生成时间: {report.generated_at}")
        lines.append("=" * 56)
        lines.append("")
        lines.append(f"🏁 结论: {report.summary}")
        lines.append(f"📊 评分: {report.score} / 100  | 状态: {'通过 ✅' if report.pass_ else '不通过 ❌'}")
        lines.append("")
        lines.append(f"📁 已提交 ({len(report.submitted)}/{len(report.required)}):")
        for d in report.submitted:
            lines.append(f"    ✓ {d}")
        if report.missing:
            lines.append("")
            lines.append(f"📂 缺失材料 ({len(report.missing)}):")
            for d in report.missing:
                lines.append(f"    ✗ {d}  ← 请补充")
        if report.issues:
            lines.append("")
            lines.append("🔍 详细问题清单:")
            # 按严重度分组
            grouped: Dict[str, List[CheckIssue]] = {}
            for it in report.issues:
                grouped.setdefault(it.severity, []).append(it)
            for sev in ["missing", "expired", "mismatch", "invalid", "warning"]:
                if sev not in grouped:
                    continue
                icon = cls.SEV_ICONS.get(sev, "•")
                name = cls.SEV_NAME.get(sev, sev)
                lines.append(f"")
                lines.append(f"  {icon} [{name}] ({len(grouped[sev])} 项)")
                for it in grouped[sev]:
                    lines.append(f"     - [{it.rule_id}] {it.message}")
                    if it.suggestion:
                        lines.append(f"       💡 建议: {it.suggestion}")
        lines.append("")
        lines.append("=" * 56)
        return "\n".join(lines)

    @classmethod
    def to_json(cls, report: CheckReport) -> str:
        return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def to_markdown(cls, report: CheckReport) -> str:
        md = []
        md.append(f"# 进件材料核对报告 — {report.scenario}\n")
        md.append(f"- **生成时间**: {report.generated_at}")
        md.append(f"- **评分**: {report.score} / 100")
        md.append(f"- **结论**: {'通过 ✅' if report.pass_ else '不通过 ❌'}")
        md.append(f"- **说明**: {report.summary}\n")
        md.append("## 一、提交概况\n")
        md.append("| 状态 | 材料类型 |")
        md.append("|------|---------|")
        for d in report.required:
            mark = "✅ 已提交" if d in report.submitted else "❌ 缺失"
            md.append(f"| {mark} | `{d}` |")
        if report.issues:
            md.append("\n## 二、问题清单\n")
            md.append("| 序号 | 严重度 | 规则ID | 问题 | 整改建议 |")
            md.append("|------|--------|--------|------|---------|")
            for i, it in enumerate(report.issues, 1):
                name = cls.SEV_NAME.get(it.severity, it.severity)
                md.append(f"| {i} | {name} | `{it.rule_id}` | {it.message} | {it.suggestion or '-'} |")
        return "\n".join(md)

    @classmethod
    def to_wecom_card(cls, report: CheckReport) -> Dict[str, Any]:
        # 高亮缺失项
        miss_text = "、".join(report.missing) if report.missing else "（无）"
        top_issues = report.issues[:3]
        issue_text = "\n".join(
            f"{cls.SEV_ICONS.get(it.severity, '•')} {it.message}"
            for it in top_issues
        ) or "无阻断性问题"
        return {
            "card_type": "text_notice",
            "main_title": {
                "title": f"📋 {report.scenario} - 核对结果",
                "desc": f"{report.score}/100  · {'通过' if report.pass_ else '不通过'}",
            },
            "emphasis_content": {
                "title": f"{len(report.submitted)}/{len(report.required)} 类材料",
                "desc": f"问题 {len(report.issues)} 项",
            },
            "horizontal_content_list": [
                {"keyname": "缺失材料", "value": miss_text},
                {"keyname": "评分", "value": f"{report.score} / 100"},
                {"keyname": "结论", "value": "✅ 通过" if report.pass_ else "❌ 需补充"},
            ],
            "quote_area": {"title": "Top 问题", "quote_text": issue_text},
            "button_list": [
                {"text": "📄 查看完整报告", "action_url": "/checker/report"},
                {"text": "📤 补传材料", "action_url": "/checker/upload"},
                {"text": "💬 联系审批员", "action_url": "/checker/contact"},
            ],
        }
