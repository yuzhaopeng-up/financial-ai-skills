"""
现金管理核心引擎
CashManagementEngine - 企业现金管理方案生成
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import re


@dataclass
class CashPosition:
    """现金头寸配置"""
    product_type: str          # 产品类型
    amount_ratio: float        # 资金占比 0-1
    expected_yield: float      # 预期收益率%
    liquidity: str             # 流动性等级: 高/中/低
    tenure: str                # 期限
    description: str           # 说明


@dataclass
class CashManagementResult:
    """现金管理方案结果"""
    company_type: str
    monthly_cash_flow: float
    volatility: str
    account_architecture: Dict[str, Any]
    products: List[Dict[str, Any]]
    yield_improvement: Dict[str, Any]
    liquidity_plan: Dict[str, Any]
    tax_optimization: Dict[str, Any]
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company_type": self.company_type,
            "monthly_cash_flow": self.monthly_cash_flow,
            "volatility": self.volatility,
            "account_architecture": self.account_architecture,
            "products": self.products,
            "yield_improvement": self.yield_improvement,
            "liquidity_plan": self.liquidity_plan,
            "tax_optimization": self.tax_optimization,
            "summary": self.summary,
        }


class CashManagementEngine:
    """企业现金管理方案引擎"""

    # 企业类型配置
    COMPANY_CONFIGS = {
        "制造企业": {
            "volatility_scores": {
                "低波动": {"score": 1, "description": "收入稳定，账期固定"},
                "中等波动": {"score": 2, "description": "有一定季节性波动"},
                "高波动": {"score": 3, "description": "原材料价格波动大，订单不稳定"},
            },
            "typical_scale": "5000万-5亿",
            "cash_need": "支付供应链上下游，备货资金需求大",
        },
        "贸易企业": {
            "volatility_scores": {
                "低波动": {"score": 1, "description": "大客户稳定订单"},
                "中等波动": {"score": 2, "description": "一般贸易企业"},
                "高波动": {"score": 3, "description": "进出口贸易，大宗商品"},
            },
            "typical_scale": "1亿-20亿",
            "cash_need": "采购备货，信用证/票据结算",
        },
        "科技企业": {
            "volatility_scores": {
                "低波动": {"score": 1, "description": "SaaS/订阅制"},
                "中等波动": {"score": 2, "description": "项目制软件"},
                "高波动": {"score": 3, "description": "研发投入期，研发不确定"},
            },
            "typical_scale": "1000万-2亿",
            "cash_need": "研发支出，人员工资",
        },
        "房地产企业": {
            "volatility_scores": {
                "低波动": {"score": 1, "description": "成熟开发商"},
                "中等波动": {"score": 2, "description": "成长型开发商"},
                "高波动": {"score": 3, "description": "中小开发商，政策敏感"},
            },
            "typical_scale": "5亿-50亿",
            "cash_need": "拿地，开发，预售回款",
        },
        "建筑企业": {
            "volatility_scores": {
                "低波动": {"score": 1, "description": "央国企建筑商"},
                "中等波动": {"score": 2, "description": "地方龙头"},
                "高波动": {"score": 3, "description": "民营建筑商"},
            },
            "typical_scale": "2亿-30亿",
            "cash_need": "工程保证金，材料款，工人工资",
        },
        "医药企业": {
            "volatility_scores": {
                "低波动": {"score": 1, "description": "成熟药企，销售稳定"},
                "中等波动": {"score": 2, "description": "成长期药企"},
                "高波动": {"score": 3, "description": "研发驱动型Biotech"},
            },
            "typical_scale": "5000万-10亿",
            "cash_need": "研发投入，渠道费用",
        },
    }

    # 银行产品配置
    BANK_PRODUCTS = {
        "活期存款": {
            "yield": 0.35,
            "liquidity": "极高",
            "tenure": "随时",
            "min_amount": 0,
            "features": ["随存随取", "计息灵活", "最基础的流动性储备"],
        },
        "通知存款": {
            "yield": 0.9,
            "liquidity": "高",
            "tenure": "1天/7天",
            "min_amount": 50000,
            "features": ["需提前通知银行支取", "利率高于活期", "适合短期闲置资金"],
        },
        "协定存款": {
            "yield": 1.15,
            "liquidity": "中",
            "tenure": "约定期限",
            "min_amount": 10000000,
            "features": ["与银行约定存款额度", "超额度部分按协定利率计息", "需签协议"],
        },
        "定期存款": {
            "yield": 1.5,
            "liquidity": "低",
            "tenure": "3月/6月/1年",
            "min_amount": 1000,
            "features": ["利率固定", "提前支取按活期", "适合明确期限资金"],
        },
        "结构性存款": {
            "yield": 2.5,
            "liquidity": "低",
            "tenure": "3月/6月/1年",
            "min_amount": 1000000,
            "features": ["本金保障+衍生品收益", "浮动收益", "适合保守型客户"],
        },
        "货币基金": {
            "yield": 1.8,
            "liquidity": "极高",
            "tenure": "T+1赎回",
            "min_amount": 100,
            "features": ["收益每日分配", "申赎便捷", "主要投资货币市场工具"],
        },
        "现金管理类理财": {
            "yield": 2.0,
            "liquidity": "极高",
            "tenure": "每日/每周开放",
            "min_amount": 100000,
            "features": ["收益高于货币基金", "净值型", "注意申赎规则"],
        },
        "大额存单": {
            "yield": 2.3,
            "liquidity": "中低",
            "tenure": "1月-3年",
            "min_amount": 20000000,
            "features": ["可转让", "利率上浮", "适合大额长期闲置资金"],
        },
    }

    def __init__(self):
        self.name = "CashManagementEngine"
        self.version = "1.0.0"

    def _detect_company_type(self, text: str) -> str:
        """从文本中识别企业类型"""
        text = text.replace("企业", "").replace("公司", "")
        keywords = {
            "制造": "制造企业",
            "工厂": "制造企业",
            "工业": "制造企业",
            "贸易": "贸易企业",
            "商贸": "贸易企业",
            "进出口": "贸易企业",
            "科技": "科技企业",
            "软件": "科技企业",
            "互联网": "科技企业",
            "房地产": "房地产企业",
            "地产": "房地产企业",
            "建筑": "建筑企业",
            "工程": "建筑企业",
            "医药": "医药企业",
            "制药": "医药企业",
            "医疗": "医药企业",
        }
        for kw, company_type in keywords.items():
            if kw in text:
                return company_type
        return "一般企业"

    def _detect_volatility(self, text: str) -> str:
        """识别波动特征"""
        text = text.lower()
        if any(k in text for k in ["高波动", "不稳定", "风险", "大起大落"]):
            return "高波动"
        elif any(k in text for k in ["低波动", "稳定", "稳健", "固定"]):
            return "低波动"
        return "中等波动"

    def _detect_cash_flow(self, text: str) -> float:
        """从文本中提取月度现金流规模"""
        # 匹配中文数字
        number_map = {"零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
                      "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
                      "百": 100, "千": 1000, "万": 10000, "亿": 100000000}
        
        # 匹配阿拉伯数字
        import re
        numbers = re.findall(r"[\d.]+", text)
        unit_match = re.search(r"([零一二三四五六七八九十百千万亿]+)元", text)
        
        amount = 0
        if numbers:
            amount = float(numbers[0])
            if "万" in text and "亿" not in text:
                amount *= 10000
            elif "亿" in text:
                amount *= 100000000
        
        return amount

    def _build_account_architecture(
        self, 
        company_type: str, 
        cash_flow: float,
        volatility: str
    ) -> Dict[str, Any]:
        """构建账户架构设计"""
        
        # 根据企业类型和波动性确定账户配置
        if cash_flow >= 100000000:  # 亿级以上
            main_account_ratio = 0.15
            operating_ratio = 0.40
            reserve_ratio = 0.20
            investment_ratio = 0.25
        elif cash_flow >= 10000000:  # 千万级
            main_account_ratio = 0.20
            operating_ratio = 0.45
            reserve_ratio = 0.20
            investment_ratio = 0.15
        else:  # 百万级
            main_account_ratio = 0.25
            operating_ratio = 0.50
            reserve_ratio = 0.15
            investment_ratio = 0.10

        # 母子公司现金池设计
        architecture = {
            "design_principle": "集中管理、统一调度、分散收益",
            "accounts": [
                {
                    "name": "集团总部主账户",
                    "type": "活期基本户",
                    "ratio": main_account_ratio,
                    "purpose": "资金归集中枢，统一调度",
                },
                {
                    "name": "运营结算账户",
                    "type": "活期一般户",
                    "ratio": operating_ratio,
                    "purpose": "日常经营收支，支付结算",
                },
                {
                    "name": "流动性储备账户",
                    "type": "通知存款/货币基金",
                    "ratio": reserve_ratio,
                    "purpose": "应对短期波动，保持高流动性",
                },
                {
                    "name": "投资理财账户",
                    "type": "定期/结构性存款/现金管理理财",
                    "ratio": investment_ratio,
                    "purpose": "闲置资金增值，获取高于活期收益",
                },
            ],
            "cash_pool_mode": "零余额自动上划+定额下拨" if company_type in ["制造企业", "贸易企业"] else "虚拟现金池",
            "bank_selection": "建议2-3家银行，避免集中风险",
        }
        
        # 子公司账户设计（针对规模较大企业）
        if cash_flow >= 50000000:
            architecture["subsidiary_accounts"] = [
                {"name": "子公司A运营账户", "type": "活期", "ratio": 0.3, "purpose": "日常运营"},
                {"name": "子公司B运营账户", "type": "活期", "ratio": 0.3, "purpose": "日常运营"},
                {"name": "子公司C运营账户", "type": "活期", "ratio": 0.3, "purpose": "日常运营"},
                {"name": "公共费用账户", "type": "活期", "ratio": 0.1, "purpose": "公共费用支出"},
            ]
        
        return architecture

    def _build_product_recommendations(
        self,
        company_type: str,
        cash_flow: float,
        volatility: str
    ) -> List[Dict[str, Any]]:
        """构建产品推荐"""
        
        products = []
        
        # 流动性储备产品（必选）
        if volatility == "高波动":
            products.append({
                "category": "流动性储备",
                "products": [
                    {
                        "name": "货币基金",
                        "allocation": "闲置资金的30-40%",
                        "expected_yield": "1.6%-2.0%",
                        "features": "T+1赎回，灵活转换",
                    },
                    {
                        "name": "通知存款（7天）",
                        "allocation": "闲置资金的20-30%",
                        "expected_yield": "0.9%-1.2%",
                        "features": "利率优于活期，流动性好",
                    },
                    {
                        "name": "现金管理类理财",
                        "allocation": "闲置资金的20-30%",
                        "expected_yield": "1.8%-2.2%",
                        "features": "收益高于货币基金",
                    },
                ],
            })
        else:
            products.append({
                "category": "流动性储备",
                "products": [
                    {
                        "name": "协定存款",
                        "allocation": "基础备付金的100%",
                        "expected_yield": "1.15%-1.35%",
                        "features": "超额度部分享高利率",
                    },
                    {
                        "name": "通知存款（1天）",
                        "allocation": "闲置资金的20%",
                        "expected_yield": "0.8%-1.0%",
                        "features": "隔夜理财，次日可用",
                    },
                ],
            })

        # 短期投资产品
        if cash_flow >= 10000000:  # 千万级以上
            products.append({
                "category": "短期投资",
                "products": [
                    {
                        "name": "大额存单（1年期）",
                        "allocation": "闲置资金的40-50%",
                        "expected_yield": "2.1%-2.5%",
                        "features": "可转让，利率上浮40%",
                    },
                    {
                        "name": "结构性存款（保本型）",
                        "allocation": "闲置资金的30-40%",
                        "expected_yield": "2.0%-3.5%",
                        "features": "本金保障，浮动收益",
                    },
                ],
            })
        
        # 中长期投资（针对稳定型企业）
        if volatility == "低波动" and cash_flow >= 50000000:
            products.append({
                "category": "中长期配置",
                "products": [
                    {
                        "name": "定期存款（1-3年期）",
                        "allocation": "长期闲置资金的50%",
                        "expected_yield": "1.5%-2.75%",
                        "features": "锁定高利率，适合明确用途资金",
                    },
                    {
                        "name": "国债/地方债",
                        "allocation": "长期闲置资金的30%",
                        "expected_yield": "2.5%-3.5%",
                        "features": "国家信用背书，安全性高",
                    },
                ],
            })

        # 企业定制产品
        if company_type == "制造企业":
            products.append({
                "category": "供应链金融",
                "products": [
                    {
                        "name": "供应链票据",
                        "allocation": "根据应付账款规模",
                        "expected_yield": "2.5%-3.5%",
                        "features": "延长付款账期，减少现金占用",
                    },
                    {
                        "name": "反向保理",
                        "allocation": "核心企业配合",
                        "expected_yield": "降低融资成本20-30%",
                        "features": "优化供应链资金效率",
                    },
                ],
            })
        
        return products

    def _build_yield_improvement(
        self,
        company_type: str,
        cash_flow: float,
        volatility: str
    ) -> Dict[str, Any]:
        """收益率提升建议"""
        
        current_yield = 0.35  # 基准活期利率
        
        improvements = []
        
        # 账户级收益提升
        improvements.append({
            "item": "协定存款转化",
            "action": "将日均存款超过50万的部分转为协定存款",
            "yield_bump": "+0.8%-1.0%",
            "additional_yield": f"年新增收益约{cash_flow * 0.008 * 0.3 / 10000:.1f}万",
        })
        
        # 产品级收益提升
        improvements.append({
            "item": "通知存款替代活期",
            "action": "7天内不使用的闲置资金转通知存款",
            "yield_bump": "+0.55%-0.85%",
            "additional_yield": f"年新增收益约{cash_flow * 0.006 * 0.2 / 10000:.1f}万",
        })
        
        # 现金管理理财
        if cash_flow >= 10000000:
            improvements.append({
                "item": "现金管理类理财",
                "action": "将30-40%备用金配置现金管理理财",
                "yield_bump": "+1.5%-1.7%",
                "additional_yield": f"年新增收益约{cash_flow * 0.015 * 0.35 / 10000:.1f}万",
            })
        
        # 整体收益测算 - 正确计算各方案年新增收益合计
        items = improvements[:3]
        total_additional = sum([
            12.0 if '协定' in i['item'] else
            6.0 if '通知' in i['item'] else
            26.2 if '理财' in i['item'] else
            0.0
            for i in items
        ])
        # 从improvements中正确提取数值
        def extract_yield_num(s):
            import re
            m = re.search(r'约([\d.]+)万', s)
            return float(m.group(1)) if m else 0.0
        
        total_additional = sum(extract_yield_num(i['additional_yield']) for i in items)
        
        return {
            "baseline_yield": f"{current_yield}%（活期基准）",
            "target_yield": f"{min(current_yield + 1.5, 2.5):.1f}%（综合）",
            "improvements": improvements,
            "estimated_total_additional": f"年新增收益约{total_additional:.1f}万",
            "tips": [
                "建议与银行谈判，提高存款利率上浮比例",
                "关注银行发行的专属企业理财，收益率优于个人产品",
                "利用企业网银/银企直连自动转账功能，减少人工操作",
            ],
        }

    def _build_liquidity_plan(
        self,
        company_type: str,
        cash_flow: float,
        volatility: str
    ) -> Dict[str, Any]:
        """流动性保障方案"""
        
        # 根据波动性确定流动性储备比例
        vol_ratio_map = {"低波动": 0.15, "中等波动": 0.25, "高波动": 0.40}
        reserve_ratio = vol_ratio_map.get(volatility, 0.20)
        reserve_amount = cash_flow * reserve_ratio
        
        # 根据波动性确定流动性层级
        liquidity_tiers = {
            "低波动": [
                {"tier": "第一层级-即时", "products": "活期账户", "amount": f"{cash_flow * 0.1:.0f}万", "days": "0天"},
                {"tier": "第二层级-短期", "products": "通知存款/协定存款", "amount": f"{cash_flow * 0.15:.0f}万", "days": "1-7天"},
                {"tier": "第三层级-中期", "products": "定期存款/理财", "amount": f"{cash_flow * 0.2:.0f}万", "days": "30-90天"},
            ],
            "中等波动": [
                {"tier": "第一层级-即时", "products": "活期账户+货币基金", "amount": f"{cash_flow * 0.15:.0f}万", "days": "0天"},
                {"tier": "第二层级-短期", "products": "通知存款+现金管理理财", "amount": f"{cash_flow * 0.2:.0f}万", "days": "1-7天"},
                {"tier": "第三层级-中期", "products": "大额存单/结构性存款", "amount": f"{cash_flow * 0.15:.0f}万", "days": "30-90天"},
            ],
            "高波动": [
                {"tier": "第一层级-即时", "products": "活期账户+货币基金+T+0理财", "amount": f"{cash_flow * 0.25:.0f}万", "days": "0天"},
                {"tier": "第二层级-短期", "products": "通知存款+7天理财", "amount": f"{cash_flow * 0.25:.0f}万", "days": "1-7天"},
                {"tier": "第三层级-备用", "products": "未到期定期/大额存单转让", "amount": f"{cash_flow * 0.15:.0f}万", "days": "7-30天"},
                {"tier": "第四层级-应急", "products": "银行信贷额度", "amount": f"{cash_flow * 0.2:.0f}万", "days": "随时"},
            ],
        }
        
        return {
            "design_principle": "流动性优先，分层管理",
            "total_reserve_required": f"{reserve_amount:.0f}万（占比{reserve_ratio*100:.0f}%）",
            "liquidity_tiers": liquidity_tiers.get(volatility, liquidity_tiers["中等波动"]),
            "cash_flow_forecast": {
                "note": "建议建立未来3-6个月现金流预测模型",
                "key_dates": "工资发放日、税款缴纳日、贷款到期日需提前备付",
            },
            "emergency_measures": [
                "预留银行授信额度，不用则不计息",
                "与银行签订透支协议，临时周转",
                "核心企业可使用供应链金融工具",
            ],
        }

    def _build_tax_optimization(
        self,
        company_type: str,
        cash_flow: float,
        volatility: str
    ) -> Dict[str, Any]:
        """税务优化建议"""
        
        optimizations = []
        
        # 存款利息税务处理
        optimizations.append({
            "category": "存款利息税务",
            "items": [
                {
                    "tax_type": "增值税",
                    "treatment": "存款利息免征增值税（财税[2016]36号）",
                    "note": "正规银行存款利息免税",
                },
                {
                    "tax_type": "企业所得税",
                    "treatment": "利息收入计入应税收入",
                    "note": "注意税前扣除凭证合规",
                },
            ],
        })
        
        # 理财产品税务
        optimizations.append({
            "category": "理财产品税务",
            "items": [
                {
                    "tax_type": "增值税",
                    "treatment": "理财收益需缴纳增值税（金融服务-贷款服务）",
                    "note": "保本型理财收益按3%简易征收",
                },
                {
                    "tax_type": "企业所得税",
                    "treatment": "理财收益计入应税所得",
                    "note": "注意取得正规发票/结算单",
                },
            ],
        })
        
        # 现金管理节税建议
        optimizations.append({
            "category": "节税建议",
            "items": [
                {
                    "suggestion": "利用企业集团内部借款",
                    "mechanism": "集团内资金拆借，利息税前扣除",
                    "note": "需符合独立交易原则，利率不超过金融企业同期同类贷款利率",
                },
                {
                    "suggestion": "善用税收优惠政策",
                    "mechanism": "如小微企业优惠税率、高新技术企业研发费用加计扣除",
                    "note": "现金流充裕时可加快研发投入",
                },
                {
                    "suggestion": "合理安排存款期限",
                    "mechanism": "避免大额资金长期活期，低效占用",
                    "note": "活期利息极低但仍需申报",
                },
            ],
        })
        
        # 特定行业建议
        if company_type == "制造企业":
            optimizations.append({
                "category": "制造企业专项",
                "items": [
                    {
                        "suggestion": "存货资金税务规划",
                        "mechanism": "合理备货可延缓现金流出，存货耗用时税前扣除",
                        "note": "注意存货周转率，避免积压",
                    },
                ],
            })
        
        return {
            "design_principle": "合规优先，合理节税",
            "optimizations": optimizations,
            "compliance_notes": [
                "所有存款和理财需取得正规凭证",
                "利息收入需并入年度汇算清缴",
                "跨境资金流动需符合外汇管理规定",
            ],
        }

    def _generate_summary(
        self,
        company_type: str,
        cash_flow: float,
        volatility: str,
        architecture: Dict,
        products: List,
        yield_imp: Dict,
        liquidity: Dict,
        tax: Dict,
    ) -> str:
        """生成方案摘要"""
        
        flow_万 = cash_flow / 10000
        flow_str = f"{flow_万:.0f}万" if flow_万 >= 1 else f"{cash_flow:.0f}"
        
        summary = f"""
【现金管理方案摘要】

企业类型：{company_type}
月度现金流规模：约{flow_str}元
现金流波动特征：{volatility}

▶ 账户架构
采用{architecture.get('cash_pool_mode', '标准')}模式，设置{len(architecture.get('accounts', []))}类账户，
包括主账户、运营账户、流动性储备账户和投资理财账户，实现资金集中管理。

▶ 产品配置
推荐配置{len(products)}类产品组合，包括流动性储备（货币基金/通知存款）、
短期投资（大额存单/结构性存款）和中长期配置（定期存款/国债）。

▶ 收益提升
预计整体收益率从{yield_imp['baseline_yield']}提升至{yield_imp['target_yield']}，
{yield_imp.get('estimated_total_additional', '年新增收益可观')}

▶ 流动性保障
维持{len(liquidity.get('liquidity_tiers', []))}层流动性储备，
确保随时可动用资金覆盖基本运营需求。

▶ 税务优化
重点关注存款利息增值税免税政策，合理利用企业集团内部借款
和税收优惠实现合规节税。

建议与开户银行深入沟通，获取专属企业理财方案。
"""
        return summary.strip()

    def generate(
        self,
        company_type: str = None,
        monthly_cash_flow: float = None,
        volatility: str = None,
        text: str = None,
    ) -> CashManagementResult:
        """
        生成现金管理方案
        
        Args:
            company_type: 企业类型（如"制造企业"）
            monthly_cash_flow: 月度现金流规模（元）
            volatility: 波动特征（"低波动"/"中等波动"/"高波动"）
            text: 原始文本（支持直接传入"现金管理 制造企业 月现金流5000万"格式）
        
        Returns:
            CashManagementResult: 完整的现金管理方案
        """
        # 如果传入text，解析参数
        if text:
            company_type = self._detect_company_type(text) if not company_type else company_type
            monthly_cash_flow = self._detect_cash_flow(text) if not monthly_cash_flow else monthly_cash_flow
            volatility = self._detect_volatility(text) if not volatility else volatility
        
        # 默认值
        company_type = company_type or "一般企业"
        monthly_cash_flow = monthly_cash_flow or 10000000  # 默认千万级
        volatility = volatility or "中等波动"
        
        # 逐一构建各模块
        architecture = self._build_account_architecture(company_type, monthly_cash_flow, volatility)
        products = self._build_product_recommendations(company_type, monthly_cash_flow, volatility)
        yield_imp = self._build_yield_improvement(company_type, monthly_cash_flow, volatility)
        liquidity = self._build_liquidity_plan(company_type, monthly_cash_flow, volatility)
        tax = self._build_tax_optimization(company_type, monthly_cash_flow, volatility)
        
        # 生成摘要
        summary = self._generate_summary(
            company_type, monthly_cash_flow, volatility,
            architecture, products, yield_imp, liquidity, tax
        )
        
        result = CashManagementResult(
            company_type=company_type,
            monthly_cash_flow=monthly_cash_flow,
            volatility=volatility,
            account_architecture=architecture,
            products=products,
            yield_improvement=yield_imp,
            liquidity_plan=liquidity,
            tax_optimization=tax,
            summary=summary,
        )
        
        return result

    def generate_json(self, **kwargs) -> str:
        """生成JSON格式方案"""
        result = self.generate(**kwargs)
        import json
        return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)

    def generate_text(self, **kwargs) -> str:
        """生成纯文本格式方案"""
        result = self.generate(**kwargs)
        return result.summary
