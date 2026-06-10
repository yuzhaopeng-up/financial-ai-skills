"""
跨境业务综合解决方案引擎
Cross-Border Business Engine
"""

from typing import Optional


class CrossBorderEngine:
    """跨境业务引擎"""

    def __init__(self):
        self.currency_map = {
            "USD": "美元",
            "EUR": "欧元",
            "GBP": "英镑",
            "JPY": "日元",
            "CNY": "人民币",
            "HKD": "港币",
        }
        # 欧盟成员国
        self.eu_countries = [
            "德国", "法国", "意大利", "西班牙", "荷兰", "比利时",
            "奥地利", "瑞士", "波兰", "瑞典", "丹麦", "芬兰", "挪威",
        ]
        # 一带一路国家
        self.belt_road_countries = [
            "越南", "马来西亚", "泰国", "印度尼西亚", "新加坡",
            "俄罗斯", "哈萨克斯坦", "巴基斯坦", "老挝", "缅甸",
        ]
        # 高风险国家/地区
        self.high_risk_countries = [
            "伊朗", "朝鲜", "叙利亚", "古巴", "苏丹",
        ]

    def generate(
        self,
        business_type: str,
        amount: float,
        currency: str,
        destination_country: str,
    ) -> dict:
        """
        生成跨境业务方案

        Args:
            business_type: 企业类型（出口/进口/跨境投融资）
            amount: 交易金额
            currency: 币种
            destination_country: 目的国/地区

        Returns:
            跨境业务综合方案
        """
        currency_name = self.currency_map.get(currency, currency)
        amount_str = self._format_amount(amount, currency)

        # 标准化业务类型
        biz_type = business_type.replace("企业", "").strip()

        result = {
            "business_type": biz_type,
            "amount": amount_str,
            "currency": currency,
            "destination_country": destination_country,
            "recommended_settlement": self._get_settlement_recommendation(
                biz_type, amount, currency, destination_country
            ),
            "fx_hedging": self._get_fx_hedging(
                biz_type, amount, currency, destination_country
            ),
            "compliance": self._get_compliance(
                biz_type, amount, currency, destination_country
            ),
            "crossborder_rmb": self._get_crossborder_rmb(
                biz_type, amount, currency, destination_country
            ),
            "special_trade_zone": self._get_special_trade_zone_policy(destination_country),
        }

        return result

    def _format_amount(self, amount: float, currency: str) -> str:
        """格式化金额显示"""
        currency_symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥",
            "CNY": "¥",
            "HKD": "HK$",
        }
        symbol = currency_symbols.get(currency, currency)
        if amount >= 10000:
            unit = amount / 10000
            return f"{symbol}{unit:.1f}万"
        return f"{symbol}{amount:,.0f}"

    def _get_settlement_recommendation(
        self, business_type: str, amount: float, currency: str, destination_country: str
    ) -> dict:
        """获取结算方式推荐"""
        is_high_risk = destination_country in self.high_risk_countries
        is_eu = any(c in destination_country for c in self.eu_countries)

        # 基于金额和业务类型推荐结算方式
        if amount >= 500000:
            if business_type == "出口":
                method = "LC信用证"
                bank_rec = "建议采用不可撤销跟单信用证(USANCE LC)，通过中资银行海外分行或外资银行开证"
                flow = ["出口商发货→提交全套单据(发票/装箱单/提单/原产地证)→通知行审单→开证行付款→进口商赎单提货"]
            elif business_type == "进口":
                method = "TT电汇(预付+尾款)"
                bank_rec = "建议30%预付，70%尾款见单据付款，控制发货风险"
                flow = ["签订合同→30%预付→出口商发货→提交单据→支付尾款70%→取得单据提货"]
            else:
                method = "跨境直贷+备用信用证担保"
                bank_rec = "建议采用跨境直贷结构，备用信用证(Standby LC)作为担保"
                flow = ["签署投资协议→开具备用信用证→资金跨境→到期还本付息"]
        elif amount >= 100000:
            if business_type == "出口":
                method = "DP付款交单"
                bank_rec = "建议采用即期DP，通过出口信用保险覆盖商业风险"
                flow = ["出口商发货→提交单据到银行→银行向进口商提示付款→进口商付款→取得单据提货"]
            else:
                method = "TT电汇"
                bank_rec = "建议采用TT结算，简便快捷"
                flow = ["签订合同→出口商发货→进口商付款→取得单据提货"]
        else:
            if business_type == "出口":
                method = "TT电汇"
                bank_rec = "小额交易建议TT结算，节省银行费用"
                flow = ["签订合同→出口商发货→进口商电汇付款→收款入账"]
            else:
                method = "OA赊账"
                bank_rec = "小额进口可采用OA，配合中信保保单"
                flow = ["签订合同→出口商发货→进口商收到货后付款→到期支付"]

        # 高风险国家特殊处理
        if is_high_risk:
            method = "预付货款+LC"
            bank_rec = "高风险国家建议100%预付或通过主权银行保兑的LC"
            flow = ["高风险地区建议采用预付货款或主权银行保兑信用证"]

        return {
            "method": method,
            "bank_recommendation": bank_rec,
            "flow": flow,
            "estimated_fees": self._estimate_settlement_fees(method, amount, currency),
        }

    def _estimate_settlement_fees(
        self, method: str, amount: float, currency: str
    ) -> dict:
        """估算结算费用"""
        fees = {}
        if method == "LC信用证":
            fees["opening_commission"] = f"{amount * 0.0015:.2f} {currency}"  # 开证费约0.15%
            fees["negotiation_commission"] = f"{amount * 0.001:.2f} {currency}"  # 议付费约0.1%
            fees["total_estimate"] = f"约{amount * 0.0025:.2f} {currency}"
        elif method == "DP付款交单":
            fees["handling_commission"] = f"{amount * 0.001:.2f} {currency}"
            fees["total_estimate"] = f"约{amount * 0.001:.2f} {currency}"
        elif method == "TT电汇":
            fees["cable_charge"] = f"{amount * 0.0005:.2f} {currency}"
            fees["total_estimate"] = f"约{amount * 0.0005:.2f} {currency}"
        else:
            fees["total_estimate"] = f"约{amount * 0.001:.2f} {currency}"
        return fees

    def _get_fx_hedging(
        self, business_type: str, amount: float, currency: str, destination_country: str
    ) -> dict:
        """获取外汇避险方案"""
        currency_name = self.currency_map.get(currency, currency)

        # 高波动货币
        high_volatility = ["EUR", "GBP", "JPY"]

        if currency in high_volatility or amount >= 500000:
            if currency == "EUR":
                hedge_type = "远期外汇合约(Forward)"
                structure = f"锁6个月远期EUR/USD，锁定汇率1.08附近，规避欧元贬值风险"
                cost = "无期权费，锁定即期汇率+50-100pips"
                example = f"100万EUR远期锁汇，假设当前EUR/USD=1.08，6个月远期约1.075，可节省约5000USD潜在损失"
            elif currency == "GBP":
                hedge_type = "外汇期权(Option)"
                structure = f"买入GBP看跌期权，执行价1.27，期限6个月"
                cost = "期权费约1%-1.5%，即10000-15000USD"
                example = "保留英镑上涨收益，同时锁定下跌风险"
            elif currency == "JPY":
                hedge_type = "外汇掉期(Swap)"
                structure = f"3个月USD/JPY掉期，锁定汇率148附近"
                cost = "掉期点约50-80pips/年化"
                example = "适合有日元收付需求的进出口商"
            else:
                hedge_type = "远期外汇合约"
                structure = f"锁定{currency_name}远期汇率，期限3-6个月"
                cost = "约0.3%-0.8%"
                example = f"{amount}万{currency_name}远期锁汇示例"
        else:
            hedge_type = "自然对冲+动态监测"
            structure = "建议通过时间分散、保留部分敞口"
            cost = "无额外成本，但需关注汇率波动"
            example = "建议配合外汇监测工具，每周评估一次敞口"

        return {
            "recommended": hedge_type,
            "structure": structure,
            "estimated_cost": cost,
            "example": example,
            "risk_level": "高" if amount >= 500000 else "中",
        }

    def _get_compliance(
        self, business_type: str, amount: float, currency: str, destination_country: str
    ) -> dict:
        """获取合规要点"""
        is_eu = any(c in destination_country for c in self.eu_countries)
        is_belt_road = destination_country in self.belt_road_countries

        # 基础合规要求
        registrations = ["货物贸易外汇管理登记"]
        licenses = []
        tax_benefits = []

        if business_type == "出口":
            registrations.append("出口退税备案")
            registrations.append("电子口岸系统登记")

            if is_eu:
                registrations.append("欧盟CE标志认证(如适用)")
                tax_benefits.append("出口欧盟可享受增值税退税")

            if amount >= 500000:
                licenses.append("若涉及出口管制商品需申请《出口许可证》")
                licenses.append("两用物项出口需申请《两用物项和技术出口许可证》")
                tax_benefits.append("符合条件的出口企业可申请增值税出口退税")

            if is_belt_road:
                registrations.append("一带一路重点市场备案")
                tax_benefits.append("一带一路沿线国家出口可享受增值税退税")

        elif business_type == "进口":
            registrations.append("进口货物报关")
            registrations.append("海关检验检疫申请")

            if is_eu:
                registrations.append("原产地证明(CO FORM A或RCEP优惠产地证)")
                tax_benefits.append("进口增值税可抵扣")

            if amount >= 500000:
                licenses.append("自动进口许可证(如涉及许可管理商品)")

        else:  # 跨境投融资
            registrations.append("ODI境外直接投资备案")
            registrations.append("外汇登记(37号文/7号文)")
            licenses.append("境外投资证书(商务部)")
            licenses.append("境外投资外汇登记(外汇局)")

            if is_belt_road:
                registrations.append("一带一路投资备案")
                tax_benefits.append("境外企业所得税抵免")

        # 反洗钱要求
        compliance_notes = [
            "保存交易相关发票、合同、运输单据至少5年",
            "大额交易(≥50万USD)需主动向外汇局报告",
            "确保交易背景真实完整",
        ]

        return {
            "required_registrations": list(set(registrations)),
            "restricted_licenses": licenses,
            "tax_benefits": tax_benefits,
            "compliance_notes": compliance_notes,
        }

    def _get_crossborder_rmb(
        self, business_type: str, amount: float, currency: str, destination_country: str
    ) -> dict:
        """获取跨境人民币政策"""
        is_eu = any(c in destination_country for c in self.eu_countries)

        result = {
            "eligibility": "符合跨境人民币结算条件",
            "benefits": [
                "降低汇兑成本，规避汇率波动",
                "提升资金结算效率",
                "可享受跨境人民币政策红利",
            ],
            "applicable_scenarios": [],
        }

        # 适用场景
        if business_type == "出口":
            result["applicable_scenarios"].append("跨境贸易人民币结算")
            result["applicable_scenarios"].append("境外直接投资人民币结算")
        elif business_type == "进口":
            result["applicable_scenarios"].append("跨境贸易人民币结算")
            result["applicable_scenarios"].append("跨境人民币资金池")
        else:
            result["applicable_scenarios"].append("境外直接投资人民币结算")
            result["applicable_scenarios"].append("跨境人民币贷款")

        # 特定国家/地区优惠
        if is_eu:
            result["eu_priority"] = "欧盟企业人民币使用活跃，建议优先推荐"
            result["banks_available"] = ["中行柏林分行", "工行法兰克福分行", "建行伦敦分行"]

        # 限制条件
        result["restrictions"] = [
            "需满足展业三原则(了解客户、了解业务、尽职审查)",
            "单笔交易需提供真实贸易背景证明",
            "人民币资金流动需符合人民银行相关规定",
        ]

        return result

    def _get_special_trade_zone_policy(self, destination_country: str) -> dict:
        """获取特殊贸易区政策"""
        zones = []

        # 海南自贸港
        zones.append({
            "zone": "海南自由贸易港",
            "benefits": [
                "零关税：部分商品免征进口关税",
                "低税率：企业所得税15%，个人所得税最高15%",
                "贸易自由便利：货物进出港自由",
                "跨境资金流动自由便利化",
            ],
            "applicable": "进口加工、跨境电商、国际航运",
        })

        # 横琴粤澳合作区
        zones.append({
            "zone": "横琴粤澳深度合作区",
            "benefits": [
                "对澳资企业优惠：企业所得税减按15%",
                "跨境人民币贷款试点",
                "澳门居民个人所得税优惠",
            ],
            "applicable": "粤港澳大湾区合作、澳门企业内地布局",
        })

        # 前海深港合作区
        zones.append({
            "zone": "前海深港现代服务业合作区",
            "benefits": [
                "港资企业企业所得税减按15%",
                "跨境人民币创新业务试点",
                "法律服务扩大开放",
            ],
            "applicable": "港资企业、金融创新、专业服务",
        })

        # 综合保税区
        zones.append({
            "zone": "综合保税区",
            "benefits": [
                "进口保税",
                "出口退税",
                "区内加工货物不征增值税",
            ],
            "applicable": "加工贸易、保税仓储、跨境电商",
        })

        return {
            "available_zones": zones,
            "recommendation": "建议结合企业业务布局，选择合适特殊区域享受政策红利",
        }

    def format_output(self, result: dict) -> str:
        """格式化输出为可读文本"""
        lines = [
            "=" * 60,
            "📋 跨境业务方案建议",
            "=" * 60,
            f"业务类型: {result['business_type']}",
            f"交易金额: {result['amount']} ({result['currency']})",
            f"目的国/地区: {result['destination_country']}",
            "",
            "【一、推荐结算方式】",
            f"  ✦ 结算方法: {result['recommended_settlement']['method']}",
            f"  ✦ 银行建议: {result['recommended_settlement']['bank_recommendation']}",
            f"  ✦ 结算流程:",
        ]

        for step in result['recommended_settlement']['flow']:
            lines.append(f"    {step}")

        lines.extend([
            "  ✦ 费用估算:",
        ])
        fees = result['recommended_settlement'].get('estimated_fees', {})
        for fee_type, fee_amount in fees.items():
            lines.append(f"    - {fee_type}: {fee_amount}")

        lines.extend([
            "",
            "【二、外汇避险方案】",
            f"  ✦ 推荐工具: {result['fx_hedging']['recommended']}",
            f"  ✦ 方案结构: {result['fx_hedging']['structure']}",
            f"  ✦ 预计成本: {result['fx_hedging']['estimated_cost']}",
            f"  ✦ 操作示例: {result['fx_hedging']['example']}",
            "",
            "【三、合规要点】",
            f"  ✦ 所需备案/登记:",
        ])

        for reg in result['compliance']['required_registrations']:
            lines.append(f"    · {reg}")

        if result['compliance']['restricted_licenses']:
            lines.append(f"  ✦ 许可证件:")
            for lic in result['compliance']['restricted_licenses']:
                lines.append(f"    · {lic}")

        if result['compliance']['tax_benefits']:
            lines.append(f"  ✦ 税收优惠:")
            for benefit in result['compliance']['tax_benefits']:
                lines.append(f"    · {benefit}")

        lines.extend([
            "",
            "【四、跨境人民币】",
            f"  ✦ 适用性: {result['crossborder_rmb']['eligibility']}",
        ])

        lines.append(f"  ✦ 适用场景:")
        for scenario in result['crossborder_rmb']['applicable_scenarios']:
            lines.append(f"    · {scenario}")

        lines.extend([
            f"  ✦ 核心优势:",
        ])
        for benefit in result['crossborder_rmb']['benefits']:
            lines.append(f"    · {benefit}")

        lines.extend([
            "",
            "【五、特殊贸易区政策】",
        ])
        for zone in result['special_trade_zone']['available_zones']:
            lines.append(f"  ✦ {zone['zone']}:")
            for benefit in zone['benefits']:
                lines.append(f"    · {benefit}")
            lines.append(f"    适用: {zone['applicable']}")

        lines.append("")
        lines.append(f"  💡 {result['special_trade_zone']['recommendation']}")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)
