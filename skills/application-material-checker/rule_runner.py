"""
规则执行器 —— 对场景规则与材料逐条比对，输出 CheckIssue 列表。
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

try:
    from .checker_engine import (
        MaterialDoc, CheckIssue, CheckReport,
        FIELD_RULES, SCENARIO_RULES,
    )
except ImportError:
    from checker_engine import (
        MaterialDoc, CheckIssue, CheckReport,
        FIELD_RULES, SCENARIO_RULES,
    )


_DATE_FMT = ["%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%Y%m%d"]


def parse_date(s: Any) -> Optional[datetime]:
    if not s:
        return None
    s = str(s).strip()
    if s in ("长期", "永久", "long-term"):
        return datetime(9999, 12, 31)
    for f in _DATE_FMT:
        try:
            return datetime.strptime(s, f)
        except ValueError:
            continue
    return None


def to_float(s: Any) -> Optional[float]:
    if s is None:
        return None
    try:
        return float(str(s).replace(",", "").replace("元", "").strip())
    except (ValueError, TypeError):
        return None


# ============================================================
# 规则原语
# ============================================================


class RuleRunner:
    """根据规则类型分发执行。"""

    def __init__(self, docs: Dict[str, MaterialDoc], today: Optional[datetime] = None):
        self.docs = docs
        self.today = today or datetime.now()

    def get_field(self, doc_key: str, field: str) -> Any:
        doc = self.docs.get(doc_key)
        return doc.get(field) if doc else None

    # ---------- 字段格式校验 ----------

    def check_field_formats(self, requirements: Dict[str, List[str]]) -> List[CheckIssue]:
        issues: List[CheckIssue] = []
        for doc_type, fields in requirements.items():
            doc = self.docs.get(doc_type)
            if not doc:
                # 缺失文档由上层处理
                continue
            for f in fields:
                v = doc.get(f)
                if v in (None, "", []):
                    issues.append(CheckIssue(
                        severity="missing",
                        doc_type=doc_type,
                        field=f,
                        message=f"必填字段 '{f}' 缺失",
                        suggestion=f"请补充 {doc_type} 的 {f} 信息",
                        rule_id=f"F-{doc_type}-{f}",
                    ))
                    continue
                # 检查格式（如果该字段在 FIELD_RULES 中）
                if f in FIELD_RULES:
                    pattern, hint = FIELD_RULES[f]
                    if not re.match(pattern, str(v)):
                        issues.append(CheckIssue(
                            severity="invalid",
                            doc_type=doc_type, field=f,
                            message=f"字段 '{f}' 格式不正确: {hint}",
                            suggestion=hint,
                            rule_id=f"FMT-{f}",
                        ))
        return issues

    # ---------- 业务规则 ----------

    def run_extra_rules(self, rules: List[Dict[str, Any]]) -> List[CheckIssue]:
        issues: List[CheckIssue] = []
        for rule in rules:
            t = rule["type"]
            handler = getattr(self, f"_rule_{t}", None)
            if handler is None:
                continue
            try:
                issue = handler(rule)
                if issue:
                    issues.append(issue)
            except Exception as e:
                issues.append(CheckIssue(
                    severity="warning",
                    doc_type="-", field="-",
                    message=f"规则 {rule.get('id','?')} 执行异常: {e}",
                    rule_id=rule.get("id", "?"),
                ))
        return issues

    def _rule_match_name(self, rule):
        a = self.get_field(*rule["src"])
        b = self.get_field(*rule["dst"])
        if a and b and str(a).strip() != str(b).strip():
            return CheckIssue(
                severity="mismatch",
                doc_type=rule["src"][0], field=rule["src"][1],
                message=f"{rule['msg']}: '{a}' vs '{b}'",
                suggestion="请核实并修正其中一份材料",
                rule_id=rule["id"],
            )
        return None

    def _rule_uscc_match(self, rule):
        a = self.get_field(*rule["src"])
        b = self.get_field(*rule["dst"])
        if a and b and a != b:
            # 五证合一后税号即统一社会信用代码
            return CheckIssue(
                severity="mismatch",
                doc_type=rule["src"][0], field=rule["src"][1],
                message=f"{rule['msg']}: {a} vs {b}",
                suggestion="如已五证合一，营业执照与税务登记号应一致",
                rule_id=rule["id"],
            )
        return None

    def _rule_not_expired(self, rule):
        v = self.get_field(*rule["src"])
        d = parse_date(v)
        if v and (d is None or d < self.today):
            return CheckIssue(
                severity="expired",
                doc_type=rule["src"][0], field=rule["src"][1],
                message=f"{rule['msg']} (有效期至: {v})",
                suggestion="请提交在有效期内的证件",
                rule_id=rule["id"],
            )
        return None

    def _rule_operating_age(self, rule):
        v = self.get_field(*rule["src"])
        d = parse_date(v)
        if v and d:
            months = (self.today - d).days / 30.0
            min_months = rule.get("min_months", 12)
            if months < min_months:
                return CheckIssue(
                    severity="invalid",
                    doc_type=rule["src"][0], field=rule["src"][1],
                    message=f"{rule['msg']} (实际: {months:.1f} 个月, 最低: {min_months})",
                    suggestion=f"企业经营须满 {min_months} 个月以上",
                    rule_id=rule["id"],
                )
        return None

    def _rule_statement_period(self, rule):
        doc, f_start, f_end = rule["src"]
        d_start = parse_date(self.get_field(doc, f_start))
        d_end = parse_date(self.get_field(doc, f_end))
        if d_start and d_end:
            months = (d_end - d_start).days / 30.0
            min_months = rule.get("min_months", 6)
            if months < min_months:
                return CheckIssue(
                    severity="invalid",
                    doc_type=doc, field=f"{f_start}/{f_end}",
                    message=f"{rule['msg']} (实际: {months:.1f} 个月)",
                    suggestion=f"请提供连续 {min_months} 个月以上的流水",
                    rule_id=rule["id"],
                )
        return None

    def _rule_loan_purpose_compliant(self, rule):
        v = self.get_field(*rule["src"])
        if not v:
            return None
        hit = [w for w in rule.get("blacklist", []) if w in str(v)]
        if hit:
            return CheckIssue(
                severity="invalid",
                doc_type=rule["src"][0], field=rule["src"][1],
                message=f"{rule['msg']} (命中关键词: {','.join(hit)})",
                suggestion="请将贷款用途修改为合规的经营性用途（采购、运营、扩产等）",
                rule_id=rule["id"],
            )
        return None

    def _rule_amount_limit(self, rule):
        v = to_float(self.get_field(*rule["src"]))
        if v is not None:
            mx = rule.get("max")
            if mx is not None and v > mx:
                return CheckIssue(
                    severity="invalid",
                    doc_type=rule["src"][0], field=rule["src"][1],
                    message=f"{rule['msg']} (申请: {v:,.0f}, 上限: {mx:,.0f})",
                    suggestion=f"请将申请金额调整至 {mx:,.0f} 元以内",
                    rule_id=rule["id"],
                )
        return None

    def _rule_spouse_required_if_married(self, rule):
        status = self.get_field(*rule["src"])
        if status == "married":
            if not self.docs.get(rule["required_doc"]):
                return CheckIssue(
                    severity="missing",
                    doc_type=rule["required_doc"], field="-",
                    message=rule["msg"],
                    suggestion="请补充配偶身份证及婚姻证明",
                    rule_id=rule["id"],
                )
        return None

    def _rule_income_to_loan_ratio(self, rule):
        income = to_float(self.get_field(*rule["income_src"]))
        price = to_float(self.get_field(*rule["price_src"]))
        if income and price:
            ratio = income / price
            if ratio < rule.get("min_ratio", 1 / 60):
                return CheckIssue(
                    severity="warning",
                    doc_type=rule["income_src"][0], field="monthly_income",
                    message=f"{rule['msg']} (月收入 {income:,.0f} / 房价 {price:,.0f} = {ratio:.4f})",
                    suggestion="建议补充配偶/共同借款人收入证明或提高首付比例",
                    rule_id=rule["id"],
                )
        return None

    def _rule_down_payment_ratio(self, rule):
        down = to_float(self.get_field(*rule["down_src"]))
        price = to_float(self.get_field(*rule["price_src"]))
        if down and price:
            ratio = down / price
            min_r = rule.get("min_ratio", 0.30)
            if ratio < min_r:
                return CheckIssue(
                    severity="invalid",
                    doc_type=rule["down_src"][0], field="amount",
                    message=f"{rule['msg']} (首付 {down:,.0f} / 房价 {price:,.0f} = {ratio:.2%})",
                    suggestion=f"请补足至最低 {min_r:.0%} 首付比例",
                    rule_id=rule["id"],
                )
        return None

    def _rule_income_proof_freshness(self, rule):
        v = self.get_field(*rule["src"])
        d = parse_date(v)
        if d:
            days = (self.today - d).days
            max_days = rule.get("max_days", 90)
            if days > max_days:
                return CheckIssue(
                    severity="expired",
                    doc_type=rule["src"][0], field=rule["src"][1],
                    message=f"{rule['msg']} (开具于 {days} 天前)",
                    suggestion=f"请提供 {max_days} 天内开具的最新收入证明",
                    rule_id=rule["id"],
                )
        return None
