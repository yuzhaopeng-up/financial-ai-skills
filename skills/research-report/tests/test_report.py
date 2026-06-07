"""research-report Skill 单元测试。"""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, SKILL)

from report_engine import ReportEngine, parse_request, ReportRequest
from report_formatter import ReportFormatter


def test_parse_industry_company_year():
    r = parse_request("研报生成 新能源 宁德时代 2025")
    assert r.industry == "新能源"
    assert r.company == "宁德时代"
    assert r.year == 2025


def test_parse_with_prefix_variant():
    r = parse_request("研报 招商银行 2025")
    assert r.company == "招商银行"
    assert r.industry == "金融"
    assert r.year == 2025


def test_parse_company_only_infers_industry():
    r = parse_request("比亚迪")
    assert r.company == "比亚迪"
    assert r.industry == "汽车"


def test_parse_industry_only():
    r = parse_request("研报 半导体 2025")
    assert r.industry == "半导体"


def test_parse_unknown_company_falls_back_general():
    r = parse_request("某公司 2025")
    assert r.industry == "通用"
    assert r.company == "某公司"


def test_generate_known_company():
    e = ReportEngine()
    r = e.generate("研报生成 新能源 宁德时代 2025")
    assert "宁德时代" in r.title
    assert "新能源" in r.title
    assert r.confidence == 1.0
    assert len(r.industry_section["core_trends"]) > 0
    assert len(r.company_section["moat"]) > 0
    assert r.investment_view["rating"] in ("买入", "增持", "中性", "减持")


def test_generate_industry_only():
    e = ReportEngine()
    r = e.generate("研报生成 半导体 2025")
    assert "半导体" in r.title
    assert r.confidence < 1.0
    assert r.investment_view["rating"]


def test_generate_unknown_falls_back_general_templates():
    e = ReportEngine()
    r = e.generate("研报 某未知公司 2025")
    assert r.request.industry == "通用"
    assert r.confidence == 0.5


def test_summary_contains_company_when_known():
    e = ReportEngine()
    r = e.generate("研报 招商银行 2025")
    assert "招商银行" in r.summary


def test_summary_does_not_crash_for_unknown():
    e = ReportEngine()
    r = e.generate("研报 某未知公司 2025")
    assert r.summary  # 不空


def test_rating_for_star_industry_leader():
    e = ReportEngine()
    r = e.generate("研报 新能源 宁德时代 2025")
    assert r.investment_view["rating"] == "买入"


def test_rating_for_unknown_industry():
    e = ReportEngine()
    r = e.generate("研报 通用 2025")
    # 通用行业 + 无公司 → 中性
    assert r.investment_view["rating"] == "中性"


def test_dict_input():
    e = ReportEngine()
    r = e.generate({"industry": "金融", "company": "招商银行", "year": 2025})
    assert "招商银行" in r.title


def test_request_object_input():
    e = ReportEngine()
    req = ReportRequest(industry="新能源", company="宁德时代", year=2025)
    r = e.generate(req)
    assert "宁德时代" in r.title


def test_formatter_text():
    e = ReportEngine()
    r = e.generate("研报 新能源 宁德时代 2025")
    t = ReportFormatter.to_text(r)
    assert "投研报告" in t
    assert "评级" in t
    assert "风险提示" in t


def test_formatter_markdown():
    e = ReportEngine()
    r = e.generate("研报 新能源 宁德时代 2025")
    md = ReportFormatter.to_markdown(r)
    assert "# 📈" in md
    assert "## 一、报告摘要" in md
    assert "## 六、投资建议" in md


def test_formatter_json_roundtrip():
    e = ReportEngine()
    r = e.generate("研报 新能源 宁德时代 2025")
    j = json.loads(ReportFormatter.to_json(r))
    assert j["title"]
    assert "request" in j
    assert "investment_view" in j


def test_formatter_wecom_card():
    e = ReportEngine()
    r = e.generate("研报 新能源 宁德时代 2025")
    card = ReportFormatter.to_wecom_card(r)
    assert card["card_type"] == "text_notice"
    assert len(card["button_list"]) == 4
    assert "emphasis_content" in card


def run_all():
    funcs = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    failures = 0
    for fn in funcs:
        try:
            fn()
            print(f"  ✅ {fn.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"  ❌ {fn.__name__}: {e}")
        except Exception as e:
            failures += 1
            print(f"  💥 {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{'='*40}\n{len(funcs)-failures}/{len(funcs)} passed.")
    return failures


if __name__ == "__main__":
    raise SystemExit(run_all())
