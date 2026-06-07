"""customer-persona Skill 单元测试。"""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, SKILL)

from persona_engine import (
    PersonaEngine, parse_natural_language, CustomerInput,
    _score_r, _score_f, _score_m, _rfm_segment, _life_cycle,
)
from persona_formatter import PersonaFormatter


def test_parse_basic():
    ci = parse_natural_language("客户画像 张伟 35岁 月收入2万 已婚 有房贷 风险偏好稳健")
    assert ci.name == "张伟"
    assert ci.age == 35
    assert ci.monthly_income == 20000
    assert ci.marital_status == "married"
    assert ci.has_mortgage is True
    assert ci.risk_preference == "steady"


def test_parse_high_net_worth():
    ci = parse_natural_language("李华 女 42岁 月收入5万 已婚 2个孩子 有房贷 风险偏好平衡 高净值")
    assert ci.name == "李华"
    assert ci.gender == "female"
    assert ci.age == 42
    assert ci.monthly_income == 50000
    assert ci.has_children is True
    assert ci.children_count == 2
    assert ci.is_high_net_worth()
    assert ci.risk_preference == "balanced"


def test_parse_aggressive_young():
    ci = parse_natural_language("王小明 28岁 月收入1.5万 单身 风险偏好进取 北京")
    assert ci.age == 28
    assert ci.monthly_income == 15000
    assert ci.marital_status == "single"
    assert ci.risk_preference == "aggressive"
    assert ci.city == "北京"


def test_parse_retired():
    ci = parse_natural_language("陈大爷 65岁 退休 月收入8000 丧偶 风险偏好保守")
    assert ci.age == 65
    assert ci.occupation == "退休"
    assert ci.marital_status == "widowed"
    assert ci.risk_preference == "conservative"


def test_rfm_score_young_high_income():
    ci = CustomerInput(age=30, monthly_income=30000)
    assert _score_r(ci) == 5
    assert _score_m(ci) == 4  # middle_high


def test_rfm_segment_top_tier():
    seg = _rfm_segment(5, 5, 5)
    assert seg == "重要价值客户"


def test_rfm_segment_low():
    seg = _rfm_segment(1, 1, 1)
    assert "流失" in seg or "保持" in seg


def test_lifecycle_new_customer():
    ci = CustomerInput(age=30, monthly_income=20000, products_held=["货币基金"])
    stage = _life_cycle(ci, _score_r(ci))
    assert stage == "新客户"


def test_lifecycle_potential():
    ci = CustomerInput(age=30, monthly_income=20000, products_held=[])
    stage = _life_cycle(ci, _score_r(ci))
    assert stage == "潜在客户"


def test_full_pipeline_basic():
    eng = PersonaEngine()
    p = eng.generate("客户画像 张伟 35岁 月收入2万 已婚 有房贷 风险偏好稳健")
    assert p.customer.name == "张伟"
    assert p.rfm_segment
    assert p.life_cycle_stage
    assert len(p.recommended_products) > 0
    assert len(p.contact_channels) > 0
    assert len(p.marketing_hooks) > 0
    assert p.next_best_action


def test_pipeline_high_net_worth_recommends_wealth():
    eng = PersonaEngine()
    p = eng.generate("李华 42岁 月收入8万 已婚 高净值 风险偏好平衡 资产1000万")
    wealth_products = [x for x in p.recommended_products
                       if x["type"] in ("wealth", "insurance")]
    assert len(wealth_products) >= 1
    assert any("高净值" in t for t in p.value_tags)


def test_pipeline_has_children_recommends_education():
    eng = PersonaEngine()
    p = eng.generate("赵华 35岁 月收入3万 已婚 2个孩子 风险偏好稳健")
    product_names = [x["name"] for x in p.recommended_products]
    family_keywords = ["教育", "重疾", "百万医疗", "终身寿"]
    assert any(any(k in n for k in family_keywords) for n in product_names), product_names


def test_pipeline_input_as_dict():
    eng = PersonaEngine()
    p = eng.generate({
        "name": "刘强",
        "age": 28,
        "monthly_income": 12000,
        "risk_preference": "aggressive",
    })
    assert p.customer.name == "刘强"
    assert p.rfm_segment


def test_formatter_text():
    eng = PersonaEngine()
    p = eng.generate("客户画像 张伟 35岁 月收入2万 已婚 风险偏好稳健")
    txt = PersonaFormatter.to_text(p)
    assert "张伟" in txt
    assert "客户分层" in txt
    assert "推荐产品" in txt


def test_formatter_markdown():
    eng = PersonaEngine()
    p = eng.generate("张伟 35岁 月收入2万 风险偏好稳健")
    md = PersonaFormatter.to_markdown(p)
    assert "# 📊" in md
    assert "| 序号 |" in md


def test_formatter_json():
    eng = PersonaEngine()
    p = eng.generate("张伟 35岁 月收入2万 风险偏好稳健")
    j = json.loads(PersonaFormatter.to_json(p))
    assert "customer" in j
    assert "rfm_segment" in j


def test_formatter_wecom_card():
    eng = PersonaEngine()
    p = eng.generate("张伟 35岁 月收入2万 风险偏好稳健")
    card = PersonaFormatter.to_wecom_card(p)
    assert card["card_type"] == "text_notice"
    assert "main_title" in card
    assert "button_list" in card
    assert len(card["button_list"]) == 4


def test_empty_input():
    eng = PersonaEngine()
    p = eng.generate({})
    assert p.rfm_segment
    assert p.life_cycle_stage


def test_input_with_products_held():
    eng = PersonaEngine()
    p = eng.generate({
        "name": "钱七",
        "age": 40,
        "monthly_income": 25000,
        "products_held": ["大额存单"],
    })
    names = [x["name"] for x in p.recommended_products]
    assert "大额存单" not in names


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
