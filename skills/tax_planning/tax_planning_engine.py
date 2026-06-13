#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
税务筹划方案引擎 v1.0
输入收入类型、资产状况、地区，输出税负分析与节税方案

Author: ArkClaw
Version: 1.0.0
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional


class TaxPlanningEngine:
    """税务筹划方案引擎"""

    VERSION = "1.0.0"

    # 个税税率表（工资薪金，2019年后合并计税）
    PERSONAL_TAX_RATES = [
        (36000, 0.03, 0),
        (144000, 0.10, 2520),
        (300000, 0.20, 16920),
        (420000, 0.25, 31920),
        (660000, 0.30, 52920),
        (960000, 0.35, 85920),
        (float('inf'), 0.45, 181920),
    ]

    # 个税税率表（劳务报酬，20%起）
    PERSONAL_LABOR_TAX_RATES = [
        (20000, 0.20, 0),
        (50000, 0.30, 0),
        (float('inf'), 0.40, 0),
    ]

    # 企业所得税率
    ENTERPRISE_TAX_RATES = {
        "一般": 0.25,
        "小微": 0.20,
        "高新": 0.15,
        "重点软件": 0.10,
    }

    # 小微企业所得税优惠（分段）
    SME_ENTERPRISE_BENEFITS = [
        (1000000, 0.125),   # 应纳税所得额≤100万，减按12.5%
        (3000000, 0.25),    # 100万< 应纳税所得额≤300万，减按25%
        (float('inf'), 0.25),  # >300万，全额25%
    ]

    # 增值税税率
    VAT_RATES = {
        "一般纳税人": {
            "销售货物/加工": 0.13,
            "建筑服务": 0.09,
            "交通运输": 0.09,
            "现代服务": 0.06,
            "生活服务": 0.06,
            "销售不动产": 0.09,
            "金融服务": 0.06,
            "电信服务-基础": 0.09,
            "电信服务-增值": 0.06,
        },
        "小规模纳税人": 0.03,
    }

    # 地区税收优惠政策
    REGIONAL_BENEFITS = {
        "北京": {
            "个税附加扣除": 1500,
            "住房租金扣除": 1500,
            "企业所得税减免": 0,
            "增值税返还比例": 0.0,
        },
        "上海": {
            "个税附加扣除": 1500,
            "住房租金扣除": 1500,
            "企业所得税减免": 0,
            "增值税返还比例": 0.0,
        },
        "深圳": {
            "个税附加扣除": 1500,
            "住房租金扣除": 1500,
            "企业所得税减免": 0,
            "增值税返还比例": 0.0,
        },
        "海南": {
            "个税附加扣除": 1500,
            "住房租金扣除": 1500,
            "企业所得税减免": 0.15,  # 海南自贸港企业所得税15%
            "增值税返还比例": 0.0,
        },
        "西部": {
            "个税附加扣除": 0,
            "住房租金扣除": 1100,
            "企业所得税减免": 0.15,  # 西部大开发15%
            "增值税返还比例": 0.0,
        },
        "新疆": {
            "个税附加扣除": 0,
            "住房租金扣除": 1100,
            "企业所得税减免": 0.15,
            "增值税返还比例": 0.0,
        },
        "西藏": {
            "个税附加扣除": 0,
            "住房租金扣除": 800,
            "企业所得税减免": 0.15,
            "增值税返还比例": 0.0,
        },
    }

    # 收入类型 → 税种映射
    INCOME_TAX_TYPES = {
        "工资": ["个人所得税"],
        "薪金": ["个人所得税"],
        "劳务": ["个人所得税"],
        "劳务报酬": ["个人所得税"],
        "股息": ["个人所得税"],
        "红利": ["个人所得税"],
        "股息红利": ["个人所得税"],
        "租金": ["个人所得税", "房产税"],
        "租赁": ["个人所得税", "房产税"],
        "房产出租": ["个人所得税", "房产税"],
        "财产租赁": ["个人所得税", "房产税"],
        "股权转让": ["个人所得税"],
        "个体工商户": ["个人所得税", "增值税", "企业所得税"],
        "个体户": ["个人所得税", "增值税", "企业所得税"],
        "企业": ["企业所得税", "增值税"],
        "公司": ["企业所得税", "增值税"],
        "经营": ["个人所得税", "增值税", "企业所得税"],
        "生产经营": ["个人所得税", "增值税", "企业所得税"],
        "奖金": ["个人所得税"],
        "年终奖": ["个人所得税"],
        "特许权使用费": ["个人所得税"],
    }

    # 消费税税目（部分）
    CONSUMPTION_TAX_ITEMS = {
        "烟": 0.56,
        "高档化妆品": 0.15,
        "珠宝": 0.10,
        "玉石": 0.10,
        "铂金": 0.10,
        "高档手表": 0.20,
        "游艇": 0.10,
        "汽车": 0.05,
        "摩托车": 0.10,
        "酒": 0.20,
        "高档首饰": 0.10,
    }

    # 房产相关税率
    PROPERTY_TAX = {
        "契税（首套90平以下）": 0.01,
        "契税（首套90平以上）": 0.015,
        "契税（二套）": 0.02,
        "契税（三套及以上）": 0.03,
        "房产税（从租）": 0.12,
        "房产税（从价）": 0.0012,
        "印花税": 0.0005,
        "土地增值税": 0.0,  # 需按累进计算
    }

    def __init__(self, api_mode: bool = False):
        self.api_mode = api_mode
        self._log("初始化税务筹划方案引擎 v%s" % self.VERSION)

    def _log(self, msg: str):
        if not self.api_mode:
            print(msg)

    def parse_input(self, text: str) -> Dict[str, Any]:
        """解析输入文本，提取收入类型、金额、地区"""
        text_lower = text.lower()

        # 提取金额
        amount_patterns = [
            r'(\d+(?:\.\d+)?)\s*[万w]',
            r'(\d+(?:\.\d+)?)\s*万元',
            r'收入[=为是]?\s*(\d+(?:\.\d+)?)\s*[万w]?',
            r'年收入\s*[=为是]?\s*(\d+(?:\.\d+)?)\s*[万w]?',
            r'年收入\s*[=为是]?\s*(\d+(?:\.\d+)?)\s*万',
            r'¥\s*(\d+(?:\.\d+)?)',
        ]
        amount = None
        for pattern in amount_patterns:
            m = re.search(pattern, text_lower)
            if m:
                val = float(m.group(1))
                # 统一为元
                if '万' in m.group(0) or 'w' in m.group(0):
                    val *= 10000
                amount = val
                break

        # 提取收入类型
        income_type = None
        for key in self.INCOME_TAX_TYPES:
            if key in text_lower:
                income_type = key
                break

        # 提取地区
        region = None
        known_regions = ["北京", "上海", "深圳", "广州", "杭州", "成都", "重庆",
                         "海南", "西部", "新疆", "西藏", "西安", "苏州", "南京",
                         "天津", "武汉", "长沙", "厦门", "福州", "青岛", "大连"]
        for region_name in known_regions:
            if region_name in text:
                region = region_name
                break

        # 提取资产信息
        assets = []
        if "房产" in text or "房子" in text:
            house_count = re.search(r'(\d+)\s*套?房产', text)
            if house_count:
                assets.append({"type": "房产", "count": int(house_count.group(1))})
            else:
                assets.append({"type": "房产", "count": 1})
        if "车" in text or "汽车" in text:
            assets.append({"type": "车辆", "count": 1})
        if "商铺" in text or "店面" in text:
            assets.append({"type": "商铺", "count": 1})

        return {
            "amount": amount,
            "income_type": income_type,
            "region": region or "全国",
            "assets": assets,
            "raw_text": text,
        }

    def calc_personal_income_tax(self, annual_income: float, income_subtype: str = "工资",
                                 region: str = "全国", additional_deduct: float = 0) -> Dict[str, Any]:
        """计算个人所得税"""
        # 免税额（6万/年）
        tax_base = max(0, annual_income - 60000 - additional_deduct)

        # 社保公积金扣除（估算约15%）
        social_insurance = annual_income * 0.105 if annual_income > 0 else 0
        tax_base = max(0, tax_base - social_insurance)

        # 专项附加扣除
        region_benefit = self.REGIONAL_BENEFITS.get(region, self.REGIONAL_BENEFITS["北京"])
        housing_deduct = region_benefit.get("住房租金扣除", 1500) * 12
        other_deduct = region_benefit.get("个税附加扣除", 1500) * 12
        tax_base = max(0, tax_base - housing_deduct - other_deduct)

        # 计算税额
        if income_subtype in ["工资", "薪金", "奖金", "年终奖"]:
            tax, rate = self._calc_salary_tax(tax_base)
        elif income_subtype in ["劳务", "劳务报酬"]:
            tax, rate = self._calc_labor_tax(annual_income)
        elif income_subtype in ["股息", "红利", "股息红利"]:
            tax, rate = self._calc_dividend_tax(annual_income)
        elif income_subtype in ["租金", "租赁", "房产出租", "财产租赁"]:
            tax, rate = self._calc_rental_tax(annual_income)
        else:
            tax, rate = self._calc_salary_tax(tax_base)

        effective_rate = (tax / annual_income * 100) if annual_income > 0 else 0

        return {
            "tax_name": "个人所得税",
            "taxable_income": annual_income,
            "tax_base": tax_base,
            "tax_amount": tax,
            "effective_rate": effective_rate,
            "actual_rate": rate,
            "deduct_items": {
                "免税额": 60000,
                "社保公积金": social_insurance,
                "住房租金扣除": housing_deduct,
                "专项附加扣除": other_deduct,
                "additional_deduct": additional_deduct,
            }
        }

    def _calc_salary_tax(self, tax_base: float) -> tuple:
        """工资薪金个税计算（累进）"""
        tax = 0
        rate = 0
        prev_threshold = 0

        for threshold, rate, deduction in self.PERSONAL_TAX_RATES:
            if tax_base <= threshold:
                tax = tax_base * rate - deduction
                break
            prev_threshold = threshold

        tax = max(0, tax)
        return tax, rate * 100

    def _calc_labor_tax(self, income: float) -> tuple:
        """劳务报酬个税计算（减除20%费用后计税）"""
        taxable = income * 0.80
        if taxable <= 20000:
            tax = taxable * 0.20
            rate = 20
        elif taxable <= 50000:
            tax = taxable * 0.30 - 2000
            rate = 30
        else:
            tax = taxable * 0.40 - 7000
            rate = 40
        return max(0, tax), rate

    def _calc_dividend_tax(self, income: float) -> tuple:
        """股息红利个税（20%固定税率）"""
        tax = income * 0.20
        return tax, 20.0

    def _calc_rental_tax(self, income: float) -> tuple:
        """财产租赁个税（减除20%费用后20%税率）"""
        taxable = income * 0.80
        tax = taxable * 0.20
        return max(0, tax), 20.0

    def calc_enterprise_income_tax(self, annual_income: float, region: str = "全国",
                                    enterprise_type: str = "一般") -> Dict[str, Any]:
        """计算企业所得税"""
        if annual_income <= 0:
            return {
                "tax_name": "企业所得税",
                "taxable_income": 0,
                "tax_amount": 0,
                "effective_rate": 0,
                "actual_rate": 0,
                "deduct_items": {},
                "note": "亏损不纳税"
            }

        # 小微企业与区域优惠判断
        if annual_income <= 3000000:
            # 小微企业优惠
            if annual_income <= 1000000:
                effective_rate = 0.125
                tax = annual_income * effective_rate
            else:
                # 100-300万部分按25%计，再减半
                tax = annual_income * 0.25 * 0.50
                effective_rate = 0.125
        else:
            # 标准税率或优惠税率
            region_benefit = self.REGIONAL_BENEFITS.get(region, {})
            discounted_rate = region_benefit.get("企业所得税减免", 0)
            if discounted_rate > 0:
                tax = annual_income * discounted_rate
                effective_rate = discounted_rate * 100
            else:
                tax = annual_income * 0.25
                effective_rate = 25.0

        return {
            "tax_name": "企业所得税",
            "taxable_income": annual_income,
            "tax_amount": tax,
            "effective_rate": effective_rate,
            "actual_rate": effective_rate,
            "deduct_items": {"应纳税所得额": annual_income},
            "note": "适用小微优惠" if annual_income <= 3000000 else f"适用{region}区域优惠" if effective_rate < 25 else "标准税率"
        }

    def calc_vat(self, sales_amount: float, business_type: str = "小规模纳税人",
                 category: str = "销售货物/加工") -> Dict[str, Any]:
        """计算增值税"""
        if business_type == "小规模纳税人":
            tax = sales_amount * 0.03
            rate = 3.0
            deductible = 0
        else:
            vat_rate = self.VAT_RATES["一般纳税人"].get(category, 0.06)
            # 销项税 - 进项税（简化，假设进项为销项的50%）
            output_tax = sales_amount * vat_rate
            input_tax = output_tax * 0.50
            tax = output_tax - input_tax
            rate = vat_rate * 100
            deductible = input_tax

        return {
            "tax_name": "增值税",
            "taxable_amount": sales_amount,
            "tax_amount": max(0, tax),
            "effective_rate": (max(0, tax) / sales_amount * 100) if sales_amount > 0 else 0,
            "actual_rate": rate,
            "deductible": deductible,
            "note": f"{business_type}"
        }

    def calc_property_tax(self, property_value: float = 0, rent: float = 0,
                         house_count: int = 1) -> Dict[str, Any]:
        """计算房产相关税费"""
        results = []

        # 契税（按首套估算）
        if property_value > 0:
            if house_count == 1:
                if property_value <= 900000:
                    deed_tax = property_value * 0.01
                else:
                    deed_tax = property_value * 0.015
            elif house_count == 2:
                deed_tax = property_value * 0.02
            else:
                deed_tax = property_value * 0.03

            results.append({
                "tax_name": "契税",
                "taxable_amount": property_value,
                "tax_amount": deed_tax,
                "effective_rate": (deed_tax / property_value * 100) if property_value > 0 else 0,
                "note": f"第{house_count}套"
            })

        # 房产税（从租计征）
        if rent > 0:
            property_tax = rent * 12 * 0.12  # 年租金×12%从租
            results.append({
                "tax_name": "房产税（从租）",
                "taxable_amount": rent * 12,
                "tax_amount": property_tax,
                "effective_rate": 12.0,
                "note": "按年租金12%计征"
            })

        # 印花税
        if property_value > 0:
            stamp_tax = property_value * 0.0005
            results.append({
                "tax_name": "印花税",
                "taxable_amount": property_value,
                "tax_amount": stamp_tax,
                "effective_rate": 0.05,
                "note": "产权转移书据"
            })

        return results

    def generate_tax_plan(self, text: str) -> Dict[str, Any]:
        """
        生成税务筹划方案

        Args:
            text: 输入文本，格式：收入类型=xxx 收入=xxx 地区=xxx

        Returns:
            税务筹划结果
        """
        parsed = self.parse_input(text)

        amount = parsed.get("amount") or 0
        income_type = parsed.get("income_type") or "工资"
        region = parsed.get("region") or "全国"
        assets = parsed.get("assets", [])

        # 税种识别
        tax_types = self.INCOME_TAX_TYPES.get(income_type, ["个人所得税"])

        # 计算各税种
        tax_details = []
        total_tax = 0

        for tax_type in tax_types:
            if tax_type == "个人所得税":
                result = self.calc_personal_income_tax(
                    amount, income_subtype=income_type, region=region
                )
                tax_details.append(result)
                total_tax += result["tax_amount"]

            elif tax_type == "企业所得税":
                result = self.calc_enterprise_income_tax(amount, region=region)
                tax_details.append(result)
                total_tax += result["tax_amount"]

            elif tax_type == "增值税":
                result = self.calc_vat(amount)
                tax_details.append(result)
                total_tax += result["tax_amount"]

        # 房产相关税费
        house_count = 0
        for asset in assets:
            if asset["type"] == "房产":
                house_count = asset.get("count", 1)
        if house_count > 0:
            property_taxes = self.calc_property_tax(
                property_value=amount if "购房" in text else 0,
                rent=amount if "出租" in text else 0,
                house_count=house_count
            )
            for pt in property_taxes:
                tax_details.append(pt)
                total_tax += pt["tax_amount"]

        # 综合税负率
        gross_income = amount
        total_tax_burden_rate = (total_tax / gross_income * 100) if gross_income > 0 else 0
        after_tax_income = gross_income - total_tax

        # 节税方案
        tax_saving_plans = self._generate_saving_plans(
            gross_income, income_type, region, assets
        )

        # 风险提示
        risk_warnings = self._generate_risk_warnings(
            gross_income, income_type, region, total_tax_burden_rate
        )

        return {
            "input": parsed,
            "income_type": income_type,
            "gross_income": gross_income,
            "region": region,
            "tax_types_identified": tax_types,
            "tax_details": tax_details,
            "total_tax": total_tax,
            "total_tax_burden_rate": total_tax_burden_rate,
            "after_tax_income": after_tax_income,
            "tax_saving_plans": tax_saving_plans,
            "risk_warnings": risk_warnings,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _generate_saving_plans(self, income: float, income_type: str,
                               region: str, assets: List) -> List[Dict[str, Any]]:
        """生成节税方案"""
        plans = []

        # 专项附加扣除优化
        if income_type in ["工资", "薪金"]:
            plans.append({
                "id": "S001",
                "title": "用足专项附加扣除",
                "description": "填报子女教育（1000元/月）、继续教育（400元/月）、住房租金/贷款利息、大病医疗等专项附加扣除",
                "estimated_saving": "最高可扣除19.2万/年",
                "risk_level": "low",
            })

            plans.append({
                "id": "S002",
                "title": "年终奖单独计税优惠",
                "description": "将奖金单独计税而非并入工资薪金，可选择单独计税方式，降低边际税率",
                "estimated_saving": "视收入层级，约可节税3%-15%",
                "risk_level": "low",
            })

        # 公积金优化
        if income_type in ["工资", "薪金"]:
            plans.append({
                "id": "S003",
                "title": "提高住房公积金缴存比例",
                "description": "在不超过当地上限范围内提高公积金缴存比例，个人所得税前扣除，同时增加住房积累",
                "estimated_saving": "月收入1万为例，公积金提升10%，每月可节税约300元",
                "risk_level": "low",
            })

        # 企业类型优化
        if income_type in ["个体工商户", "个体户", "经营", "生产经营"]:
            plans.append({
                "id": "S004",
                "title": "小微企业税收优惠",
                "description": "年应纳税所得额≤100万减按12.5%，100-300万减按25%，充分利用小微优惠",
                "estimated_saving": "100万以内实际税负仅12.5%",
                "risk_level": "low",
            })

        # 区域优惠
        if region in ["海南", "西部", "新疆", "西藏"]:
            plans.append({
                "id": "S005",
                "title": "区域税收优惠政策",
                "description": f"{region}地区适用企业所得税15%优惠税率，充分利用区域税收洼地",
                "estimated_saving": "相比25%标准税率，节税40%",
                "risk_level": "medium",
            })

        # 股权投资
        if income_type in ["股息", "红利", "股息红利"]:
            plans.append({
                "id": "S006",
                "title": "利用股权激励递延纳税",
                "description": "符合条件的技术入股、企业股权激励可享受递延纳税优惠",
                "estimated_saving": "递延至转让时纳税，避免累进税率",
                "risk_level": "medium",
            })

        # 房产节税
        if any(a["type"] == "房产" for a in assets):
            plans.append({
                "id": "S007",
                "title": "房产持有方式优化",
                "description": "通过公司持有商业物业可计提折旧抵税，但需权衡转让时的土地增值税和所得税",
                "estimated_saving": "视具体情况，约可降低税负2%-5%",
                "risk_level": "medium",
            })

        # 业务拆分
        if income_type in ["企业", "公司", "经营"]:
            plans.append({
                "id": "S008",
                "title": "业务拆分与小规模纳税人认定",
                "description": "将高毛利业务拆分为多个小规模纳税人，享受3%增值税征收率优惠",
                "estimated_saving": "年销售额500万以内，增值税节省约60%",
                "risk_level": "medium",
            })

        # 捐赠抵税
        plans.append({
            "id": "S009",
            "title": "公益慈善捐赠抵税",
            "description": "通过合规公益组织进行捐赠，在应纳税所得额30%以内可税前扣除",
            "estimated_saving": "捐赠100元，最高可抵税45元",
            "risk_level": "low",
        })

        return plans

    def _generate_risk_warnings(self, income: float, income_type: str,
                                 region: str, burden_rate: float) -> List[Dict[str, str]]:
        """生成风险提示"""
        warnings = []

        if burden_rate > 45:
            warnings.append({
                "id": "W001",
                "level": "high",
                "title": "税负率过高",
                "description": "综合税负率超过45%，建议重新审视收入结构，考虑收入类型转换或区域布局优化",
            })

        if income_type == "股息红利" and income > 5000000:
            warnings.append({
                "id": "W002",
                "level": "medium",
                "title": "大额股息税务规划",
                "description": "大额股息需关注20%个税及未来股权转让时的所得税，可考虑股权架构设计",
            })

        if income_type in ["个体工商户", "个体户", "经营"]:
            if income > 5000000:
                warnings.append({
                    "id": "W003",
                    "level": "medium",
                    "title": "经营所得超额累进",
                    "description": "经营所得最高边际税率35%，收入较高时建议评估企业形式（有限公司 vs 个体户）的税负差异",
                })

        if region == "全国":
            warnings.append({
                "id": "W004",
                "level": "low",
                "title": "地区未明确",
                "description": "未识别到地区信息，无法享受区域性税收优惠，建议补充所在地信息",
            })

        return warnings

    def format_text(self, result: Dict) -> str:
        """格式化输出为文本"""
        lines = [
            f"💰 **税务筹划方案报告**",
            f"",
            f"📊 **基本信息**",
            f"收入类型: {result['income_type']}",
            f"地区: {result['region']}",
            f"总收入: ¥{result['gross_income']:,.0f}",
            f"",
            f"{'='*30}",
            f"",
            f"📋 **税负分析**",
            f"",
        ]

        for detail in result["tax_details"]:
            lines.append(
                f"  {detail['tax_name']}: ¥{detail['tax_amount']:,.0f} "
                f"(实际税率 {detail['effective_rate']:.1f}%)"
            )

        lines.extend([
            f"",
            f"  **总税额: ¥{result['total_tax']:,.0f}**",
            f"  **综合税负率: {result['total_tax_burden_rate']:.1f}%**",
            f"  **税后收入: ¥{result['after_tax_income']:,.0f}**",
            f"",
            f"{'='*30}",
            f"",
            f"💡 **节税方案**",
            f"",
        ])

        for plan in result["tax_saving_plans"][:5]:
            lines.append(
                f"**{plan['id']}. {plan['title']}**\n"
                f"   {plan['description']}\n"
                f"   预计节税: {plan['estimated_saving']} ⚠️风险: {plan['risk_level']}\n"
            )

        if result["risk_warnings"]:
            lines.extend([
                f"",
                f"{'='*30}",
                f"",
                f"⚠️ **风险提示**",
                f"",
            ])
            for w in result["risk_warnings"]:
                level_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(w["level"], "⚪")
                lines.append(f"{level_emoji} **{w['title']}**: {w['description']}")

        lines.extend([
            f"",
            f"{'='*30}",
            f"",
            f"🕐 生成时间: {result['generated_at']}",
        ])

        return '\n'.join(lines)

    def format_json(self, result: Dict) -> str:
        """格式化输出为JSON"""
        return json.dumps(result, ensure_ascii=False, indent=2)


def main():
    """主函数 - CLI测试"""
    print("=" * 50)
    print("💰 税务筹划方案引擎 v1.0")
    print("=" * 50)
    print()

    engine = TaxPlanningEngine()

    test_cases = [
        "收入类型=工资 收入=30万 地区=北京",
        "收入类型=个体工商户 收入=80万 地区=深圳",
        "收入类型=股息红利 收入=100万 地区=上海",
        "收入类型=企业 收入=500万 地区=海南",
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n{'='*40}")
        print(f"测试用例 {i}: {case}")
        print("=" * 40)
        result = engine.generate_tax_plan(case)
        print(engine.format_text(result))


if __name__ == "__main__":
    main()
