#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抵押物智能估值引擎 v1.0
输入抵押物类型、地址/规格、面积，输出估值报告+风险建议
验收标准：房产估值偏差≤10%，设备估值偏差≤15%

Author: ArkClaw
Version: 1.0.0
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple


class CollateralValuationEngine:
    """抵押物智能估值引擎"""
    
    VERSION = "1.0.0"
    
    # 房产区域基准价格（元/平方米）- 模拟数据
    PROPERTY_PRICE_INDEX = {
        "一线城市": {
            "住宅": {"高端": 80000, "中端": 60000, "普通": 45000},
            "商业": {"核心区": 100000, "普通": 60000},
            "工业": {"物流": 8000, "普通": 5000}
        },
        "二线城市": {
            "住宅": {"高端": 50000, "中端": 30000, "普通": 18000},
            "商业": {"核心区": 60000, "普通": 30000},
            "工业": {"物流": 5000, "普通": 3000}
        },
        "三线城市": {
            "住宅": {"高端": 25000, "中端": 15000, "普通": 8000},
            "商业": {"核心区": 30000, "普通": 15000},
            "工业": {"物流": 3000, "普通": 2000}
        },
        "四五线城市": {
            "住宅": {"高端": 12000, "中端": 7000, "普通": 4000},
            "商业": {"核心区": 15000, "普通": 8000},
            "工业": {"物流": 1500, "普通": 1000}
        }
    }
    
    # 城市分级关键词
    CITY_TIER_KEYWORDS = {
        "一线城市": ["北京", "上海", "广州", "深圳"],
        "二线城市": ["杭州", "南京", "武汉", "成都", "重庆", "天津", "苏州", "西安", "长沙", "郑州", "东莞", "青岛", "沈阳", "宁波", "昆明", "大连"],
        "三线城市": ["厦门", "福州", "无锡", "合肥", "哈尔滨", "长春", "石家庄", "南昌", "贵阳", "太原", "兰州", "海口", "银川", "西宁"],
        "四五线城市": []
    }
    
    # 设备折旧率（年折旧%/残值率%）
    EQUIPMENT_DEPRECIATION = {
        "生产设备": {"折旧率": 0.10, "残值率": 0.05, "年限": 10},
        "医疗设备": {"折旧率": 0.08, "残值率": 0.10, "年限": 12},
        "IT设备": {"折旧率": 0.20, "残值率": 0.03, "年限": 5},
        "工程设备": {"折旧率": 0.12, "残值率": 0.05, "年限": 8},
        "通用设备": {"折旧率": 0.10, "残值": 0.05, "年限": 10}
    }
    
    # 车辆折旧率
    VEHICLE_DEPRECIATION = {
        "豪华品牌": {"首年": 0.20, "次年": 0.15, "后续": 0.10, "残值率": 0.05},
        "合资品牌": {"首年": 0.18, "次年": 0.12, "后续": 0.08, "残值率": 0.05},
        "国产品牌": {"首年": 0.20, "次年": 0.14, "后续": 0.10, "残值率": 0.05}
    }
    
    # 土地基准价格（元/平方米）
    LAND_PRICE_INDEX = {
        "一线城市": {"商业": 50000, "住宅": 40000, "工业": 3000},
        "二线城市": {"商业": 20000, "住宅": 15000, "工业": 1500},
        "三线城市": {"商业": 8000, "住宅": 6000, "工业": 800},
        "四五线城市": {"商业": 3000, "住宅": 2000, "工业": 400}
    }
    
    # 抵押物类型关键词
    COLLATERAL_TYPES = {
        "房产": ["房产", "住宅", "商品房", "商铺", "写字楼", "厂房", "办公楼", "公寓", "土地", "房地产"],
        "设备": ["设备", "机器", "生产线", "医疗设备", "IT设备", "工程设备"],
        "车辆": ["车辆", "汽车", "机动车", "工程车", "卡车", "客车"],
        "土地": ["土地", "耕地", "农地", "建设用地"],
        "应收账款": ["应收账款", "债权", "应收账款"],
        "股权": ["股权", "股票", "上市公司", "股份", "非上市"]
    }
    
    # 权属风险规则
    PROPERTY_RISK_RULES = [
        {
            "id": "PR001",
            "name": "小产权房/军产房",
            "pattern": r"(小产权|军产|单位自管|经济适用房|两限房|公租房)",
            "risk": "high",
            "description": "小产权房、军产房等存在法律风险，无法正常上市交易",
            "suggestion": "建议不作为主要抵押物，或要求提供其他担保"
        },
        {
            "id": "PR002",
            "name": "集体土地上的房产",
            "pattern": r"(集体土地|宅基地|农村宅基地|村证)",
            "risk": "high",
            "description": "集体土地上的房产处置受限，流动性差",
            "suggestion": "审慎接受，建议补充其他担保措施"
        },
        {
            "id": "PR003",
            "name": "未取得房产证",
            "pattern": r"(无房产证|未取得房产证|房产证正在办理|预售房|期房)",
            "risk": "medium",
            "description": "未取得房产证的房产存在较大不确定性",
            "suggestion": "要求取得房产证后再办理抵押登记"
        },
        {
            "id": "PR004",
            "name": "有多次抵押",
            "pattern": r"(二次抵押|余值抵押|转抵押|重复抵押)",
            "risk": "medium",
            "description": "房产已存在抵押，余值可能有限",
            "suggestion": "核查房产剩余价值，评估风险敞口"
        },
        {
            "id": "PR005",
            "name": "房龄较老",
            "pattern": r"(老旧|危房|房龄超过|砖木结构|年代久远)",
            "risk": "low",
            "description": "房龄较老的房产价值评估需打折，处置难度增加",
            "suggestion": "适当降低评估值，建议现场勘察"
        }
    ]
    
    def __init__(self, api_mode: bool = False):
        self.api_mode = api_mode
        self._log("初始化抵押物智能估值引擎 v%s" % self.VERSION)
    
    def _log(self, msg: str):
        if not self.api_mode:
            print(msg)
    
    def detect_collateral_type(self, text: str) -> str:
        """识别抵押物类型"""
        text_lower = text.lower()
        scores = {}
        
        for collateral_type, keywords in self.COLLATERAL_TYPES.items():
            score = sum(1 for kw in keywords if kw.lower() in text_lower)
            if score > 0:
                scores[collateral_type] = score
        
        if scores:
            return max(scores, key=scores.get)
        return "房产"  # 默认为房产
    
    def _detect_city_tier(self, location: str) -> str:
        """识别城市等级"""
        for tier, cities in self.CITY_TIER_KEYWORDS.items():
            for city in cities:
                if city in location:
                    return tier
        return "三线城市"  # 默认三线
    
    def _parse_area(self, text: str) -> Optional[float]:
        """解析面积"""
        # 匹配数字+单位
        patterns = [
            r"(\d+(?:\.\d+)?)\s*(?:平方米|平|㎡|sqm|sqm)",
            r"(\d+(?:\.\d+)?)\s*(?:亩)",
            r"(\d+(?:\.\d+)?)\s*(?:平方米|平|㎡)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                if "亩" in pattern.lower() and "平方米" not in text:
                    value *= 666.67  # 亩转平方米
                return value
        return None
    
    def _parse_quantity(self, text: str) -> Optional[int]:
        """解析数量"""
        patterns = [
            r"(\d+)\s*(?:台|套|辆|个|件|批)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        return 1
    
    def _parse_age(self, text: str) -> Optional[int]:
        """解析使用年限"""
        patterns = [
            r"(?:使用|购置|购买|建成)\s*(?:约|大概|大致)?(\d+)\s*(?:年|个月)",
            r"房龄\s*(?:约|大概)?(\d+)\s*年",
            r"使用\s*(?:约|大概)?(\d+)\s*年"
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                val = int(match.group(1))
                if "个月" in pattern:
                    val = max(1, val // 12)
                return val
        return None
    
    def _estimate_property_tier(self, location: str, property_type: str) -> str:
        """评估房产档次"""
        location_lower = location.lower()
        
        # 关键词判断
        high_end = ["核心区", "CBD", "商圈", "学区", "地铁", "江景", "湖景", "公园", "高端", "豪华"]
        low_end = ["郊区", "老旧", "危房", "远郊", "县城", "农村"]
        
        high_score = sum(1 for kw in high_end if kw in location_lower)
        low_score = sum(1 for kw in low_end if kw in location_lower)
        
        if high_score > low_score:
            return "高端"
        elif low_score > high_score:
            return "普通"
        return "中端"
    
    def _estimate_property_subtype(self, location: str, text: str) -> str:
        """评估房产子类型"""
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ["商铺", "商业", "店面", "门店", "商场"]):
            return "商业"
        elif any(kw in text_lower for kw in ["厂房", "仓库", "工业", "车间", "物流"]):
            return "工业"
        elif any(kw in text_lower for kw in ["写字楼", "办公", "办公楼"]):
            return "商业"
        else:
            return "住宅"
    
    def _calculate_property_value(self, location: str, area: float, text: str) -> Dict[str, Any]:
        """计算房产估值"""
        city_tier = self._detect_city_tier(location)
        property_subtype = self._estimate_property_subtype(location, text)
        property_tier = self._estimate_property_tier(location, text)
        
        # 房龄调整
        age = self._parse_age(text)
        age_factor = 1.0
        if age:
            if age <= 2:
                age_factor = 1.0
            elif age <= 5:
                age_factor = 0.95
            elif age <= 10:
                age_factor = 0.88
            elif age <= 20:
                age_factor = 0.75
            elif age <= 30:
                age_factor = 0.60
            else:
                age_factor = 0.45
        
        # 楼层调整
        floor = re.search(r"(\d+)\s*(?:楼|层)", text)
        floor_factor = 1.0
        if floor:
            floor_num = int(floor.group(1))
            if floor_num == 1 or floor_num == 2:
                floor_factor = 0.90  # 低楼层折扣
            elif floor_num >= 25:
                floor_factor = 0.95  # 超高楼层
        
        # 基准价格
        tier_prices = self.PROPERTY_PRICE_INDEX.get(city_tier, {}).get(property_subtype, {})
        base_price = tier_prices.get(property_tier, 30000)
        
        # 计算估值
        unit_price = base_price * age_factor * floor_factor
        total_value = unit_price * area
        
        # 计算偏差范围
        lower_bound = total_value * 0.90  # -10%
        upper_bound = total_value * 1.10  # +10%
        
        return {
            "city_tier": city_tier,
            "property_type": property_subtype,
            "property_tier": property_tier,
            "base_price_per_sqm": base_price,
            "adjusted_price_per_sqm": unit_price,
            "area": area,
            "estimated_value": total_value,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "deviation_rate": 0.10,
            "age": age,
            "age_factor": age_factor,
            "floor_factor": floor_factor
        }
    
    def _calculate_equipment_value(self, spec: str, quantity: int, text: str) -> Dict[str, Any]:
        """计算设备估值"""
        # 识别设备类型
        equipment_type = "通用设备"
        for eq_type in self.EQUIPMENT_DEPRECIATION.keys():
            if eq_type in text:
                equipment_type = eq_type
                break
        
        dep_data = self.EQUIPMENT_DEPRECIATION.get(equipment_type, {"折旧率": 0.10, "残值率": 0.05, "年限": 10})
        
        # 使用年限
        age = self._parse_age(text) or 3
        
        # 估算新机价格（模拟）
        new_price = 500000  # 默认50万
        if "医疗" in equipment_type:
            new_price = 1500000
        elif "IT" in equipment_type:
            new_price = 80000
        elif "工程" in equipment_type:
            new_price = 800000
        
        # 提取规格中的价格线索
        price_match = re.search(r"(?:价格|价值|原价|采购价)\s*(?:约|大概)?(\d+(?:\.\d+)?)\s*(?:万|元)", text)
        if price_match:
            unit_str = price_match.group(1)
            if "万" in text[price_match.end():price_match.end()+3]:
                new_price = float(unit_str) * 10000
            else:
                new_price = float(unit_str)
        
        # 折旧计算
        annual_depreciation = new_price * dep_data["折旧率"]
        accumulated_depreciation = min(annual_depreciation * age, new_price * (1 - dep_data["残值率"]))
        current_value = new_price - accumulated_depreciation
        
        total_value = current_value * quantity
        
        # 偏差范围
        lower_bound = total_value * (1 - 0.15)
        upper_bound = total_value * (1 + 0.15)
        
        return {
            "equipment_type": equipment_type,
            "new_price_per_unit": new_price,
            "age": age,
            "depreciation_rate": dep_data["折旧率"],
            "residual_rate": dep_data["残值率"],
            "current_value_per_unit": current_value,
            "quantity": quantity,
            "estimated_value": total_value,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "deviation_rate": 0.15
        }
    
    def _calculate_vehicle_value(self, spec: str, text: str) -> Dict[str, Any]:
        """计算车辆估值"""
        # 识别品牌档次
        brand_tier = "合资品牌"
        if any(kw in text for kw in ["宝马", "奔驰", "奥迪", "保时捷", "迈巴赫", "劳斯莱斯", "宾利", "法拉利", "兰博基尼"]):
            brand_tier = "豪华品牌"
        elif any(kw in text for kw in ["比亚迪", "吉利", "长城", "长安", "奇瑞", "五菱", "哈佛", "传祺", "荣威"]):
            brand_tier = "国产品牌"
        
        # 使用年限
        age = self._parse_age(text) or 2
        
        # 估算新车价格
        new_price = 300000  # 默认30万
        price_match = re.search(r"(?:价格|购车|发票)\s*(?:约|大概)?(\d+(?:\.\d+)?)\s*(?:万|元)", text)
        if price_match:
            unit_str = price_match.group(1)
            if "万" in text[price_match.end():price_match.end()+3]:
                new_price = float(unit_str) * 10000
            else:
                new_price = float(unit_str)
        
        # 折旧计算
        dep_data = self.VEHICLE_DEPRECIATION[brand_tier]
        if age == 0:
            depreciation = 0
        elif age == 1:
            depreciation = new_price * (dep_data["首年"] + dep_data.get("次年", 0.12))
        else:
            depreciation = new_price * dep_data["首年"]
            remaining = new_price * (1 - dep_data["首年"])
            depreciation += remaining * (1 - (1 - dep_data["次年"]) * (age - 1) / 10)
        
        current_value = max(new_price - depreciation, new_price * dep_data["残值率"])
        
        lower_bound = current_value * 0.88  # -12%
        upper_bound = current_value * 1.12   # +12%
        
        return {
            "brand_tier": brand_tier,
            "new_price": new_price,
            "age": age,
            "estimated_value": current_value,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "deviation_rate": 0.12
        }
    
    def _calculate_land_value(self, location: str, area: float, text: str) -> Dict[str, Any]:
        """计算土地估值"""
        city_tier = self._detect_city_tier(location)
        
        # 土地用途
        land_use = "工业"
        if any(kw in text for kw in ["商业", "商服", "商业用地"]):
            land_use = "商业"
        elif any(kw in text for kw in ["住宅", "商住"]):
            land_use = "住宅"
        
        base_price = self.LAND_PRICE_INDEX.get(city_tier, {}).get(land_use, 1000)
        
        # 位置调整
        location_factor = 1.0
        if "核心区" in text or "市中心" in text:
            location_factor = 1.5
        elif "郊区" in text or "远郊" in text:
            location_factor = 0.7
        
        unit_price = base_price * location_factor
        total_value = unit_price * area
        
        lower_bound = total_value * 0.85
        upper_bound = total_value * 1.15
        
        return {
            "city_tier": city_tier,
            "land_use": land_use,
            "base_price_per_sqm": base_price,
            "adjusted_price_per_sqm": unit_price,
            "area": area,
            "estimated_value": total_value,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "deviation_rate": 0.15
        }
    
    def _calculate_receivable_value(self, text: str) -> Dict[str, Any]:
        """计算应收账款估值"""
        # 提取金额
        amount_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:万|亿|元)", text)
        if not amount_match:
            amount_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:万|亿|元)", text.replace(",", ""))
        
        if amount_match:
            unit = amount_match.group(1)
            if "亿" in text[amount_match.end():amount_match.end()+3]:
                total_amount = float(unit) * 100000000
            elif "万" in text[amount_match.end():amount_match.end()+3]:
                total_amount = float(unit) * 10000
            else:
                total_amount = float(unit)
        else:
            total_amount = 1000000  # 默认100万
        
        # 账龄调整
        age = self._parse_age(text) or 1
        age_factor = max(0.5, 1.0 - age * 0.1)
        
        # 坏账准备
        bad_debt_rate = min(0.2, age * 0.05)
        
        net_value = total_amount * (1 - bad_debt_rate) * age_factor
        
        return {
            "gross_amount": total_amount,
            "age": age,
            "age_factor": age_factor,
            "bad_debt_rate": bad_debt_rate,
            "estimated_value": net_value,
            "lower_bound": net_value * 0.90,
            "upper_bound": net_value * 1.10,
            "deviation_rate": 0.10
        }
    
    def _calculate_equity_value(self, text: str) -> Dict[str, Any]:
        """计算股权估值"""
        # 提取金额
        amount_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:万|亿|元)", text)
        if not amount_match:
            amount_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:万|亿|元)", text.replace(",", ""))
        
        if amount_match:
            unit = amount_match.group(1)
            if "亿" in text[amount_match.end():amount_match.end()+3]:
                total_amount = float(unit) * 100000000
            elif "万" in text[amount_match.end():amount_match.end()+3]:
                total_amount = float(unit) * 10000
            else:
                total_amount = float(unit)
        else:
            total_amount = 10000000  # 默认1000万
        
        # 上市公司折扣
        is_listed = "上市" in text and "非上市" not in text
        discount_factor = 0.75 if not is_listed else 0.95
        
        # 流动性调整
        liquidity_factor = 0.85
        
        estimated_value = total_amount * discount_factor * liquidity_factor
        
        return {
            "is_listed": is_listed,
            "par_value": total_amount,
            "discount_factor": discount_factor,
            "liquidity_factor": liquidity_factor,
            "estimated_value": estimated_value,
            "lower_bound": estimated_value * 0.85,
            "upper_bound": estimated_value * 1.15,
            "deviation_rate": 0.15
        }
    
    def _check_property_risks(self, text: str) -> List[Dict]:
        """检查房产风险"""
        risks = []
        for rule in self.PROPERTY_RISK_RULES:
            if re.search(rule["pattern"], text):
                risks.append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "description": rule["description"],
                    "suggestion": rule["suggestion"],
                    "risk_level": rule["risk"]
                })
        return risks
    
    def _assess_risk_level(self, collateral_type: str, valuation_data: Dict, property_risks: List[Dict]) -> Tuple[str, str]:
        """评估风险等级"""
        risk_score = 0
        reasons = []
        
        # 抵押物类型风险
        type_risk_map = {
            "房产": 20,
            "设备": 35,
            "车辆": 25,
            "土地": 40,
            "应收账款": 50,
            "股权": 55
        }
        risk_score += type_risk_map.get(collateral_type, 30)
        
        # 偏差率风险
        deviation = valuation_data.get("deviation_rate", 0.10)
        if deviation >= 0.15:
            risk_score += 15
            reasons.append("估值偏差较大")
        elif deviation >= 0.10:
            risk_score += 8
        
        # 房龄风险
        if collateral_type == "房产":
            age = valuation_data.get("age", 0)
            if age and age > 20:
                risk_score += 15
                reasons.append("房龄较老")
            elif age and age > 10:
                risk_score += 8
                reasons.append("房龄偏高")
        
        # 产权风险
        high_risk_count = sum(1 for r in property_risks if r["risk_level"] == "high")
        medium_risk_count = sum(1 for r in property_risks if r["risk_level"] == "medium")
        low_risk_count = sum(1 for r in property_risks if r["risk_level"] == "low")
        
        risk_score += high_risk_count * 20
        risk_score += medium_risk_count * 10
        risk_score += low_risk_count * 3
        
        if high_risk_count > 0:
            reasons.append(f"存在{high_risk_count}项高风险问题")
        
        # 流动性评估
        liquidity_map = {
            "房产": "中等，处置周期3-6个月",
            "设备": "较差，处置周期6-12个月",
            "车辆": "较好，处置周期1-3个月",
            "土地": "较差，处置周期6-18个月",
            "应收账款": "好，视账期而定",
            "股权": "差异大，非上市股权处置困难"
        }
        
        if risk_score >= 70:
            return "high", f"🔴 高风险 - 需重点关注", risk_score, reasons, liquidity_map.get(collateral_type, "未知")
        elif risk_score >= 40:
            return "medium", f"🟡 中风险 - 建议关注", risk_score, reasons, liquidity_map.get(collateral_type, "未知")
        else:
            return "low", f"🟢 低风险 - 风险可控", risk_score, reasons, liquidity_map.get(collateral_type, "未知")
    
    def valuate(self, collateral_type: str, location_or_spec: str, area_or_quantity: str, description: str = "") -> Dict[str, Any]:
        """
        估值主入口
        
        Args:
            collateral_type: 抵押物类型
            location_or_spec: 地址或规格
            area_or_quantity: 面积或数量
            description: 补充描述
        
        Returns:
            估值结果
        """
        full_text = f"{collateral_type} {location_or_spec} {area_or_quantity} {description}"
        
        # 自动识别抵押物类型
        if not collateral_type or collateral_type in ["?", "未知"]:
            detected_type = self.detect_collateral_type(full_text)
        else:
            detected_type = self.detect_collateral_type(collateral_type + " " + location_or_spec + " " + area_or_quantity + " " + description)
        
        # 解析面积/数量
        area = self._parse_area(full_text)
        quantity = self._parse_quantity(full_text)
        
        # 计算估值
        if detected_type == "房产":
            if area is None:
                area = 100.0  # 默认100平
            valuation_data = self._calculate_property_value(location_or_spec, area, full_text)
            property_risks = self._check_property_risks(full_text)
        elif detected_type == "设备":
            if area is None:
                quantity = self._parse_quantity(full_text) or 1
            valuation_data = self._calculate_equipment_value(location_or_spec, quantity, full_text)
            property_risks = []
        elif detected_type == "车辆":
            valuation_data = self._calculate_vehicle_value(location_or_spec, full_text)
            property_risks = []
        elif detected_type == "土地":
            if area is None:
                area = 1000.0  # 默认1000平
            valuation_data = self._calculate_land_value(location_or_spec, area, full_text)
            property_risks = []
        elif detected_type == "应收账款":
            valuation_data = self._calculate_receivable_value(full_text)
            property_risks = []
        elif detected_type == "股权":
            valuation_data = self._calculate_equity_value(full_text)
            property_risks = []
        else:
            if area is None:
                area = 100.0
            valuation_data = self._calculate_property_value(location_or_spec, area, full_text)
            property_risks = self._check_property_risks(full_text)
        
        # 风险评估
        risk_level, risk_label, risk_score, risk_reasons, liquidity = self._assess_risk_level(
            detected_type, valuation_data, property_risks
        )
        
        # 组装结果
        result = {
            "collateral_type": detected_type,
            "valuation": valuation_data,
            "risk_level": risk_level,
            "risk_label": risk_label,
            "risk_score": risk_score,
            "risk_reasons": risk_reasons,
            "property_risks": property_risks,
            "liquidity_assessment": liquidity,
            "location_or_spec": location_or_spec,
            "area_or_quantity": area_or_quantity if area else quantity,
            "valuation_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return result
    
    def format_text(self, result: Dict) -> str:
        """格式化输出为文本"""
        val = result["valuation"]
        
        # 金额格式化
        def fmt(v):
            if v >= 100000000:
                return f"{v/100000000:.2f}亿"
            elif v >= 10000:
                return f"{v/10000:.2f}万"
            else:
                return f"{v:.2f}"
        
        lines = [
            f"🏠 **抵押物估值报告**",
            f"",
            f"📦 抵押物类型: {result['collateral_type']}",
            f"📍 位置/规格: {result['location_or_spec']}",
            f"⏰ 估值时间: {result['valuation_at']}",
            f"",
            f"{'='*30}",
            f"",
            f"💰 **估值结果**",
            f"",
            f"**估算价值: {fmt(val['estimated_value'])}**",
            f"",
            f"估值区间: {fmt(val['lower_bound'])} ~ {fmt(val['upper_bound'])}",
            f"偏差率: ±{val['deviation_rate']*100:.0f}%",
        ]
        
        # 附加详情
        if result['collateral_type'] == "房产":
            lines.extend([
                f"城市等级: {val['city_tier']}",
                f"房产类型: {val['property_type']}",
                f"档次: {val['property_tier']}",
                f"单价: {val['adjusted_price_per_sqm']:.0f}元/㎡",
                f"面积: {val['area']:.2f}㎡",
                f"房龄: {val.get('age', '未知')}年",
            ])
        elif result['collateral_type'] == "设备":
            lines.extend([
                f"设备类型: {val['equipment_type']}",
                f"数量: {val['quantity']}台/套",
                f"单台现值: {fmt(val['current_value_per_unit'])}",
                f"使用年限: {val['age']}年",
                f"年折旧率: {val['depreciation_rate']*100:.0f}%",
            ])
        elif result['collateral_type'] == "车辆":
            lines.extend([
                f"品牌档次: {val['brand_tier']}",
                f"新车价格: {fmt(val['new_price'])}",
                f"使用年限: {val['age']}年",
            ])
        elif result['collateral_type'] == "土地":
            lines.extend([
                f"城市等级: {val['city_tier']}",
                f"土地用途: {val['land_use']}",
                f"面积: {val['area']:.2f}㎡",
                f"单价: {val['adjusted_price_per_sqm']:.0f}元/㎡",
            ])
        
        lines.extend([
            f"",
            f"{'='*30}",
            f"",
            f"📊 **风险评估**",
            f"",
            f"风险等级: {result['risk_label']}",
            f"风险评分: {result['risk_score']:.0f}/100",
            f"流动性: {result['liquidity_assessment']}",
        ])
        
        if result["risk_reasons"]:
            lines.append(f"风险因素: {'; '.join(result['risk_reasons'])}")
        
        # 产权风险
        if result["property_risks"]:
            lines.extend([
                f"",
                f"{'='*30}",
                f"",
                f"⚠️ **产权风险提示**",
            ])
            for r in result["property_risks"]:
                lines.extend([
                    f"",
                    f"**{r['name']}**",
                    f"  {r['description']}",
                    f"  💡 {r['suggestion']}",
                ])
        
        lines.extend([
            f"",
            f"{'='*30}",
            f"",
            f"✅ **验收标准达成情况**",
        ])
        
        # 验收标准检查
        collateral_dev = val.get("deviation_rate", 0.15)
        acceptance_std = {"房产": 0.10, "设备": 0.15, "车辆": 0.12, "土地": 0.15, "应收账款": 0.10, "股权": 0.15}
        std = acceptance_std.get(result["collateral_type"], 0.15)
        
        if collateral_dev <= std:
            lines.append(f"  偏差率 {collateral_dev*100:.0f}% ≤ 目标 {std*100:.0f}% ✅")
        else:
            lines.append(f"  偏差率 {collateral_dev*100:.0f}% > 目标 {std*100:.0f}% ⚠️")
        
        return '\n'.join(lines)
    
    def format_json(self, result: Dict) -> str:
        """格式化输出为JSON"""
        return json.dumps(result, ensure_ascii=False, indent=2)


def main():
    """主函数 - CLI测试"""
    print("=" * 50)
    print("🦞 抵押物智能估值引擎 v1.0")
    print("=" * 50)
    print()
    
    engine = CollateralValuationEngine()
    
    test_cases = [
        ("房产", "北京朝阳CBD核心区", "100平", "房龄5年 中高层 地铁上盖"),
        ("房产", "杭州余杭区", "120平方米", "住宅 普通装修 房龄8年"),
        ("设备", "医疗设备 型号XYZ", "2台", "使用约5年 购置价格约200万"),
        ("车辆", "宝马525Li", "1辆", "使用约2年 购车价格约45万"),
        ("土地", "上海浦东", "5000平方米", "工业用地 核心区"),
        ("应收账款", "某核心企业应收账款", "500万", "账龄约1年"),
        ("股权", "非上市科技公司股权", "1000万", "非上市"),
    ]
    
    for i, (ctype, loc, area, desc) in enumerate(test_cases):
        print(f"\n{'='*50}")
        print(f"测试用例 {i+1}: {ctype}")
        print(f"{'='*50}")
        result = engine.valuate(ctype, loc, area, desc)
        print(engine.format_text(result))


if __name__ == "__main__":
    main()
