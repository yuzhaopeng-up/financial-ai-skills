"""
供应链金融（Supply Chain Finance, SCF）引擎
输入：核心企业名称 / 供应商类型 / 应付账款规模 / 账期
输出：供应链金融解决方案（对应收账款融资/订单融资/库存融资/核心企业确权）、
     各方案对比、办理流程、额度范围、利率参考、办理周期、所需材料、核心企业配合要点
"""

from dataclasses import dataclass, field
from typing import Optional
import re


@dataclass
class SCFProfile:
    core_enterprise: str          # 核心企业名称
    supplier_type: str           # 供应商类型
    accounts_payable: float      # 应付账款规模（万元）
    payment_term_days: int       # 账期（天）
    industry: Optional[str] = None  # 行业


@dataclass
class SCFSolution:
    name: str                    # 方案名称
    mode: str                    # 模式
    description: str            # 方案描述
    quota_range: str             # 额度范围
    interest_rate: str           # 利率参考
    cycle: str                   # 办理周期
    materials: list             # 所需材料
    core_cooperation: list      # 核心企业配合要点
    advantages: list            # 优势
    risks: list                 # 风险提示
    suitability: str            # 适用场景


class SCFEngine:
    """
    供应链金融解决方案引擎
    支持五种模式：应收账款质押融资、订单融资、核心企业反向保理、供应链票据、仓单融资
    """

    def __init__(self, api_mode: bool = False):
        self.api_mode = api_mode
        self._industry_keywords = {
            "汽车": ["汽车", "整车", "车企", "车厂", "汽配", "零部件"],
            "电子": ["电子", "半导体", "芯片", "面板", "消费电子", "手机"],
            "医药": ["医药", "制药", "医疗", "器械", "药店", "医院"],
            "家电": ["家电", "电器", "空调", "冰箱", "洗衣机", "彩电"],
            "食品": ["食品", "饮料", "乳业", "酒类", "餐饮", "调味品"],
            "纺织": ["纺织", "服装", "面料", "印染", "制衣"],
            "建材": ["建材", "水泥", "钢材", "木材", "家居"],
            "能源": ["能源", "电力", "光伏", "风电", "电池", "储能"],
        }

    def _detect_industry(self, core_enterprise: str, supplier_type: str) -> str:
        """根据核心企业/供应商类型推断行业"""
        text = core_enterprise + supplier_type
        for industry, keywords in self._industry_keywords.items():
            for kw in keywords:
                if kw in text:
                    return industry
        return "通用制造"

    def _scale_factor(self, ap: float) -> float:
        """根据应付账款规模确定规模系数"""
        if ap >= 100000:   # 100亿+
            return 1.5
        elif ap >= 10000:  # 10亿+
            return 1.2
        elif ap >= 1000:   # 1亿+
            return 1.0
        elif ap >= 100:    # 1000万+
            return 0.8
        else:
            return 0.6

    def generate(self, profile: SCFProfile) -> dict:
        """
        生成供应链金融解决方案
        返回包含：solutions（方案列表）、comparison（方案对比）、process（办理流程）
        """
        industry = profile.industry or self._detect_industry(
            profile.core_enterprise, profile.supplier_type
        )
        scale = self._scale_factor(profile.accounts_payable)

        solutions = self._build_solutions(profile, industry, scale)
        comparison = self._build_comparison(solutions)
        process = self._build_process(solutions)
        summary = self._build_summary(profile, industry, solutions)

        return {
            "profile": {
                "core_enterprise": profile.core_enterprise,
                "supplier_type": profile.supplier_type,
                "accounts_payable_yi": profile.accounts_payable / 10000,
                "accounts_payable_wan": profile.accounts_payable,
                "payment_term_days": profile.payment_term_days,
                "detected_industry": industry,
                "scale_factor": scale,
            },
            "solutions": solutions,
            "comparison": comparison,
            "process": process,
            "summary": summary,
        }

    def _build_solutions(self, profile: SCFProfile, industry: str, scale: float) -> list:
        """构建五种解决方案"""
        ap = profile.accounts_payable
        term = profile.payment_term_days

        # 基础额度参数
        base_quota = min(ap * 0.8, 100000) * scale  # 万元

        s1 = SCFSolution(
            name="应收账款质押融资",
            mode="应收账款质押（Inventory Finance / Receivables Pledge）",
            description="供应商将已确认的应收账款质押给金融机构，提前获取货款，核心企业到期付款至指定账户。",
            quota_range=f"{min(ap * 0.7, 80000) * scale:.0f}～{min(ap * 0.9, 120000) * scale:.0f} 万元",
            interest_rate=f"年化 {3.8 + (8 - scale) * 0.3:.1f}%～{5.5 + (8 - scale) * 0.3:.1f}%（银行自主定价）",
            cycle="3～7 个工作日",
            materials=[
                "供应商营业执照、开户许可证",
                "与核心企业的贸易合同、订单、发票",
                "应收账款确认函或对账函",
                "核心企业付款承诺函",
                "最近 12 个月银行流水",
                "上一年度财务报表",
            ],
            core_cooperation=[
                "出具《应收账款确认函》或对账盖章",
                "承诺付款至监管账户",
                "配合质押登记（如需）",
            ],
            advantages=[
                "不占用核心企业银行授信额度",
                "供应商提前回款，改善经营性现金流",
                "核心企业延长账期，不增加财务成本",
            ],
            risks=[
                "应收账款真实性核实依赖核心企业配合",
                "核心企业信用风险会传导至融资金额",
            ],
            suitability="核心企业信用优质（AAA/AA+）、供应商分散且账期标准化",
        )

        s2 = SCFSolution(
            name="订单融资",
            mode="订单融资（Order Financing / Purchase Order Financing）",
            description="供应商凭借核心企业下达的采购订单，向金融机构申请预支采购/生产资金，锁定未来应收账款。",
            quota_range=f"{min(ap * 0.5, 50000) * scale:.0f}～{min(ap * 0.7, 80000) * scale:.0f} 万元",
            interest_rate=f"年化 {4.5 + (8 - scale) * 0.3:.1f}%～{6.5 + (8 - scale) * 0.3:.1f}%",
            cycle="5～10 个工作日",
            materials=[
                "核心企业下达的正式采购订单/合同",
                "供应商营业执照、生产资质证明",
                "核心企业授信额度证明（如有）",
                "供应商历史履约记录",
                "采购方与供应商的以往交易数据",
            ],
            core_cooperation=[
                "出具真实有效的采购订单",
                "提供供应商评级或履约评价",
                "到期按时付款至监管账户",
            ],
            advantages=[
                "供应商在生产阶段即获融资支持",
                "有助于核心企业锁定优质供应商资源",
                "订单锁定，风险更可控",
            ],
            risks=[
                "订单变更或撤销导致融资用途落空",
                "供应商交付能力存在不确定性",
            ],
            suitability="核心企业采购量大、供应商处于扩产期、资金周转压力大的制造类供应商",
        )

        s3 = SCFSolution(
            name="核心企业反向保理",
            mode="反向保理（Reverse Factoring / Confirmed Supply Chain Finance）",
            description="核心企业主动确权，将自己对供应商的应付账款转让/确认给金融机构，由核心企业承担最终付款责任，金融机构提前向供应商付款。",
            quota_range=f"{min(ap * 0.8, 150000) * scale:.0f}～{min(ap * 1.0, 200000) * scale:.0f} 万元",
            interest_rate=f"年化 {3.2 + (8 - scale) * 0.2:.1f}%～{4.8 + (8 - scale) * 0.2:.1f}%（优质核心可更低）",
            cycle="7～15 个工作日（首次开立）",
            materials=[
                "核心企业营业执照、近3年审计报告",
                "核心企业评级报告（AA及以上）",
                "与供应商的历史贸易数据（ERP对接或对账文件）",
                "保理预付款确认函",
                "供应商营业执照、核心企业供应商准入名单",
            ],
            core_cooperation=[
                "在供应链金融平台注册并完成确权认证",
                "向金融机构确认应付账款真实性与账期",
                "承诺到期刚性兑付（或提供银票/信单链）",
                "开放 ERP/财务系统数据接口（推荐）",
            ],
            advantages=[
                "核心企业信用直接穿透，降低融资成本",
                "利率显著低于传统贷款，供应商受益",
                "全流程线上化，操作便捷高效",
                "核心企业可优化财务报表（降低应付账款）",
            ],
            risks=[
                "核心企业需承担确权责任，法律关系需清晰",
                "平台系统对接有一定 IT 投入",
            ],
            suitability="核心企业信用等级高（AA+以上）、供应商数量多（>50家）、交易数据标准化",
        )

        s4 = SCFSolution(
            name="供应链票据",
            mode="供应链票据（Supply Chain Bill / Electronic Commercial Draft）",
            description="依托上海票交所供应链票据平台或企业自主开立的电子商票，将核心企业信用传导至多级供应商，实现票据的多级流转与融资。",
            quota_range=f"{min(ap * 0.6, 100000) * scale:.0f}～{min(ap * 0.85, 180000) * scale:.0f} 万元",
            interest_rate=f"年化 {3.5 + (8 - scale) * 0.2:.1f}%～{5.2 + (8 - scale) * 0.2:.1f}%（商票直贴）",
            cycle="1～3 个工作日（平台流转）",
            materials=[
                "核心企业在票交所完成企业信息登记",
                "供应链票据平台账户开通",
                "真实贸易背景合同、发票",
                "核心企业评级资料",
                "供应商营业执照、票交所会员资格",
            ],
            core_cooperation=[
                "在票交所开立供应链票据",
                "配合核心企业信用的跨级传导",
                "承诺到期兑付",
            ],
            advantages=[
                "信用多级穿透，一级供应商可继续流转至 N 级供应商",
                "标准化票据，法律保障完善",
                "可对接央行货币政策工具（再贴现）",
                "全线上操作，效率极高",
            ],
            risks=[
                "票交所准入资质要求",
                "票据到期刚性兑付，不可撤销",
            ],
            suitability="核心企业信用强、供应商链条长（多级传导）、希望标准化结算的企业",
        )

        s5 = SCFSolution(
            name="仓单融资",
            mode="仓单融资（Warehouse Receipt Financing）",
            description="供应商将存放在指定仓库的存货（原材料/产成品）的仓单作为质押物，向金融机构申请贷款，适用于有实物资产但应收账款尚未形成的阶段。",
            quota_range=f"{min(ap * 0.4, 30000) * scale:.0f}～{min(ap * 0.6, 50000) * scale:.0f} 万元",
            interest_rate=f"年化 {5.0 + (8 - scale) * 0.3:.1f}%～{8.0 + (8 - scale) * 0.3:.1f}%",
            cycle="3～5 个工作日（标准品）",
            materials=[
                "指定仓库开具的标准仓单（须经仓储企业签章）",
                "库存商品的权属证明（购销合同、发票、出库单）",
                "商品价格波动盯市机制（保险或对冲协议）",
                "仓储监管协议（银行与仓库签署）",
                "企业营业执照、最近一期财务报表",
            ],
            core_cooperation=[
                "认可指定交割仓库资质",
                "采购时提供货权清晰的单据",
                "如涉及核心企业回购，配合签订回购协议",
            ],
            advantages=[
                "有实物资产作为抵押，风险更可控",
                "适用于原材料价格波动较大时期",
                "不依赖核心企业信用",
            ],
            risks=[
                "商品价格波动需盯市盯控",
                "仓储监管成本较高",
                "仓单伪造或重复质押风险",
            ],
            suitability="拥有大宗商品、原材料库存较高的供应商（汽车零部件、电子原材料、粮食等）",
        )

        return [s1, s2, s3, s4, s5]

    def _build_comparison(self, solutions: list) -> dict:
        """构建方案对比表"""
        comparison_rows = []
        for s in solutions:
            comparison_rows.append({
                "方案": s.name,
                "额度范围": s.quota_range,
                "利率参考": s.interest_rate,
                "办理周期": s.cycle,
                "核心企业配合度要求": (
                    "★★☆" if "反向保理" in s.name else
                    "★☆☆" if "仓单" in s.name else
                    "★★★"
                ),
                "供应商自主性": (
                    "★★☆" if "仓单" in s.name else
                    "★★★" if "应收" in s.name or "订单" in s.name else
                    "★★★"
                ),
                "风险等级": (
                    "低" if "反向保理" in s.name or "票据" in s.name else
                    "中" if "应收" in s.name or "订单" in s.name else
                    "中高"
                ),
                "适用规模": "最适合大额（亿级）" if "反向" in s.name or "票据" in s.name else "适中规模",
            })
        return {"headers": list(comparison_rows[0].keys()), "rows": comparison_rows}

    def _build_process(self, solutions: list) -> dict:
        """构建通用办理流程"""
        steps = [
            {"step": 1, "phase": "需求调研", "action": "供应商/核心企业提交融资需求，评估应付账款规模与账期结构", "duration": "1～2天"},
            {"step": 2, "phase": "方案选型", "action": "根据行业特点、核心企业信用等级、供应商数量，选择最适合的SCF模式", "duration": "1天"},
            {"step": 3, "phase": "资质审核", "action": "核心企业确权 + 供应商资质审核 + 贸易真实性核实", "duration": "3～7天"},
            {"step": 4, "phase": "合同签署", "action": "核心企业、供应商、金融机构三方签署 SCF 协议/保理合同/票据开立协议", "duration": "1～3天"},
            {"step": 5, "phase": "额度启用", "action": "金融机构为供应商开通融资额度，供应商提交应收账款/订单/仓单发起融资", "duration": "1～2天"},
            {"step": 6, "phase": "放款", "action": "金融机构审核后放款至供应商账户（T+0～T+3）", "duration": "T+0～3"},
            {"step": 7, "phase": "到期回收", "action": "核心企业到期付款至监管账户，金融机构扣款结清，尾款付至供应商", "duration": "账期届满"},
        ]
        return {"phases": steps, "note": "反向保理和供应链票据可全线上化，周期缩短 30%～50%"}

    def _build_summary(self, profile: SCFProfile, industry: str, solutions: list) -> dict:
        """构建综合建议"""
        ap = profile.accounts_payable
        term = profile.payment_term_days

        recommended = []
        if ap >= 50000:  # 5亿以上
            recommended = ["反向保理", "供应链票据"]
        elif ap >= 10000:  # 1亿以上
            recommended = ["反向保理", "应收账款质押融资", "供应链票据"]
        else:
            recommended = ["应收账款质押融资", "订单融资", "仓单融资"]

        rec_names = [s for s in solutions if any(r in s.name for r in recommended)]

        summary_text = (
            f"【{profile.core_enterprise}】供应链金融方案建议\n\n"
            f"核心企业：{profile.core_enterprise}\n"
            f"应付账款规模：{profile.accounts_payable/10000:.1f}亿元（{profile.accounts_payable:.0f}万元）\n"
            f"账期：{term}天 | 行业：{industry}\n\n"
            f"推荐方案：\n"
        )
        for s in rec_names:
            summary_text += f"  ✅ {s.name}：{s.suitability}\n"

        summary_text += (
            f"\n行动建议：\n"
            f"  1. 优先推荐【反向保理】或【供应链票据】，利率最低（年化 3.2%～5.2%），\n"
            f"     核心企业信用直达供应商，适合{profile.supplier_type}等标准化供应商群体\n"
            f"  2. 若核心企业确权配合度有限，选择【应收账款质押融资】，核心企业仅需出具确认函\n"
            f"  3. 若供应商处于扩产期备货阶段，叠加【订单融资】+【仓单融资】组合\n"
            f"  4. 对接建议：首选银行系 SCF 平台（如中企云链、联易融、京东供应链金融），\n"
            f"     次选保理公司+核心企业确权模式\n"
        )
        return {"text": summary_text, "recommended_names": recommended}

    def format_markdown(self, result: dict) -> str:
        """输出 Markdown 格式报告"""
        p = result["profile"]
        sol = result["solutions"]
        comp = result["comparison"]
        proc = result["process"]
        summ = result["summary"]

        md = f"# 供应链金融解决方案报告\n\n"
        md += f"**核心企业**：{p['core_enterprise']}  \n"
        md += f"**供应商类型**：{p['supplier_type']}  \n"
        md += f"**应付账款**：{p['accounts_payable_yi']:.1f} 亿元（{p['accounts_payable_wan']:.0f} 万元）  \n"
        md += f"**账期**：{p['payment_term_days']} 天  \n"
        md += f"**推断行业**：{p['detected_industry']}  \n\n"

        md += "## 一、五种解决方案\n\n"
        for i, s in enumerate(sol, 1):
            md += f"### {i}. {s.name}（{s.mode}）\n\n"
            md += f"**适用场景**：{s.suitability}\n\n"
            md += f"{s.description}\n\n"
            md += f"| 项目 | 参考值 |\n|------|--------|\n"
            md += f"| 额度范围 | {s.quota_range} |\n"
            md += f"| 利率参考 | {s.interest_rate} |\n"
            md += f"| 办理周期 | {s.cycle} |\n\n"

            md += f"**所需材料**：\n"
            for m in s.materials:
                md += f"- {m}\n"
            md += "\n"

            md += f"**核心企业配合要点**：\n"
            for c in s.core_cooperation:
                md += f"- {c}\n"
            md += "\n"

            md += f"**优势**：{' | '.join(s.advantages)}  \n"
            md += f"**风险**：{' | '.join(s.risks)}  \n\n"
            md += "---\n\n"

        md += "## 二、方案对比\n\n"
        md += "| " + " | ".join(comp["headers"]) + " |\n"
        md += "| " + " | ".join(["---"] * len(comp["headers"])) + " |\n"
        for row in comp["rows"]:
            md += "| " + " | ".join(str(row[h]) for h in comp["headers"]) + " |\n"
        md += "\n"

        md += "## 三、办理流程\n\n"
        md += "| 步骤 | 阶段 | 动作 | 时长 |\n|------|------|------|------|\n"
        for step in proc["phases"]:
            md += f"| {step['step']} | {step['phase']} | {step['action']} | {step['duration']} |\n"
        md += f"\n*备注：{proc['note']}*\n\n"

        md += "## 四、综合建议\n\n"
        md += summ["text"].replace("【", "**【").replace("】", "】**")

        return md

    def format_json(self, result: dict) -> dict:
        """输出 JSON 格式"""
        import copy
        r = copy.deepcopy(result)
        # 将 SCFSolution dataclass 转换为 dict
        r["solutions"] = [
            {
                "name": s.name,
                "mode": s.mode,
                "description": s.description,
                "quota_range": s.quota_range,
                "interest_rate": s.interest_rate,
                "cycle": s.cycle,
                "materials": s.materials,
                "core_cooperation": s.core_cooperation,
                "advantages": s.advantages,
                "risks": s.risks,
                "suitability": s.suitability,
            }
            for s in r["solutions"]
        ]
        return r

    def format_wecom_card(self, result: dict) -> dict:
        """输出企微卡片格式（用于 wecom_integration）"""
        p = result["profile"]
        summ = result["summary"]

        card = {
            "msgtype": "markdown",
            "markdown": {
                "content": (
                    f"### 🏦 供应链金融方案报告\n\n"
                    f"**核心企业**：{p['core_enterprise']}\n"
                    f"**应付账款**：{p['accounts_payable_yi']:.1f}亿 | **账期**：{p['payment_term_days']}天\n"
                    f"**行业**：{p['detected_industry']} | **供应商**：{p['supplier_type']}\n\n"
                    f"### ✅ 推荐方案\n\n"
                    + "\n".join(f"- **{r}**" for r in summ['recommended_names'])
                    + f"\n\n"
                    f"> 💡 回复【详细】获取完整方案对比及办理流程"
                )
            }
        }
        return card


def parse_input(text: str) -> SCFProfile:
    """
    从自然语言解析 SCFProfile
    支持格式示例：
    "供应链金融 汽车整车厂 应付账款10亿"
    "汽车整车厂 供应商类型 电子 应付账款5亿 账期90天"
    """
    # 提取核心企业名称（取第一个词组）
    enterprise_match = re.search(r'供应链金融\s*(.+?)(?:\s+供应商|\s+应付)', text)
    if not enterprise_match:
        # 尝试取前两个词
        words = text.split()
        enterprise = words[0] if words else "未知核心企业"

    # 提取应付账款规模
    ap = 0.0
    ap_match = re.search(r'应付账款\s*([\d.]+)\s*(亿|万|元)', text)
    if ap_match:
        val = float(ap_match.group(1))
        unit = ap_match.group(2)
        if unit == '亿':
            ap = val * 10000  # 万元
        elif unit == '万':
            ap = val
        else:
            ap = val / 10000
    else:
        # 尝试数字+亿格式
        num_match = re.search(r'([\d.]+)\s*亿', text)
        if num_match:
            ap = float(num_match.group(1)) * 10000

    # 提取账期
    term = 90  # 默认90天
    term_match = re.search(r'账期\s*(\d+)\s*天', text)
    if term_match:
        term = int(term_match.group(1))

    # 提取供应商类型
    supplier_match = re.search(r'供应商类型?\s*[:：]?\s*(\S+)', text)
    supplier = supplier_match.group(1) if supplier_match else "一般供应商"

    # 如果没找到供应商，从文本前部提取
    if supplier == "一般供应商":
        # 去掉"供应链金融"前缀后取第一个词
        clean = re.sub(r'^供应链金融\s*', '', text)
        parts = clean.split()
        if len(parts) >= 1:
            supplier = parts[0]
            if ap > 0 and supplier in ["亿", "万", "元", "账期"]:
                supplier = "一般供应商"
        else:
            supplier = "一般供应商"

    # 提取核心企业
    core_match = re.search(r'核心企业\s*[:：]?\s*(\S+)', text)
    if core_match:
        enterprise = core_match.group(1)
    elif '汽车' in text:
        enterprise = "汽车整车厂"
    elif '电子' in text:
        enterprise = "电子核心企业"
    else:
        words = text.replace('供应链金融', '').strip().split()
        enterprise = words[0] if words else "未知核心企业"

    return SCFProfile(
        core_enterprise=enterprise,
        supplier_type=supplier,
        accounts_payable=ap if ap > 0 else 10000.0,
        payment_term_days=term,
    )


# ============ CLI entry ============
if __name__ == "__main__":
    import sys, json

    if len(sys.argv) < 2:
        print("Usage: python scf_engine.py generate \"供应链金融 汽车整车厂 应付账款10亿\"")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "generate":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        profile = parse_input(text)
        engine = SCFEngine(api_mode=True)
        result = engine.generate(profile)

        fmt = "markdown"
        if "--format=json" in text:
            fmt = "json"
            text = text.replace("--format=json", "").strip()

        if fmt == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(engine.format_markdown(result))
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
