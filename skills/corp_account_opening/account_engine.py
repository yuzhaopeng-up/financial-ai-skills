"""
企业对公开户核心引擎
CorpAccountEngine: 输入企业基本信息，返回开户所需材料清单+办理流程+注意事项+常见问题
"""

import re
import json
from typing import Optional


class CorpAccountEngine:
    """企业对公开户智能引擎"""

    # 企业类型映射
    ENTERPRISE_TYPES = {
        "有限责任公司": "LTD",
        "股份公司": "CORP",
        "股份有限公司": "CORP",
        "合伙企业": "PARTNERSHIP",
        "外资企业": "FOREIGN",
        "外商投资企业": "FOREIGN",
        "个体工商户": "SOLE_PROP",
        "个人独资企业": "SOLE_PROP",
    }

    # 通用材料（所有企业类型都需要）
    COMMON_MATERIALS = [
        {"name": "营业执照", "desc": "正副本原件及复印件", "note": "复印件需加盖公章"},
        {"name": "法定代表人身份证", "desc": "原件及正反面复印件", "note": "复印件需加盖公章"},
        {"name": "经办人身份证", "desc": "原件及正反面复印件", "note": "如非法人亲自办理"},
        {"name": "公章", "desc": "企业公章、财务章、法人章", "note": "基本户必须"},
        {"name": "财务章", "desc": "财务专用章", "note": "部分银行需要"},
        {"name": "法人章", "desc": "法定代表人名章", "note": "基本户必须"},
    ]

    # 类型差异化材料
    TYPE_SPECIFIC_MATERIALS = {
        "LTD": [
            {"name": "公司章程", "desc": "最新修订版，加盖公章", "note": "有限责仼公司提供"},
            {"name": "股东会决议", "desc": "关于开立基本存款账户的决议", "note": "全体股东签字"},
            {"name": "注册地址证明", "desc": "租赁合同+房产证复印件", "note": "注册地与经营地一致"},
        ],
        "CORP": [
            {"name": "公司章程", "desc": "最新修订版，股份公司需经股东大会通过", "note": "股份公司提供"},
            {"name": "股东大会决议", "desc": "关于开立基本存款账户的决议", "note": "需董事会及股东大会通过"},
            {"name": "董事会成员名单", "desc": "全体董事会成员身份证复印件", "note": "加盖公章"},
            {"name": "注册地址证明", "desc": "租赁合同+房产证复印件", "note": "注册地与经营地一致"},
        ],
        "PARTNERSHIP": [
            {"name": "合伙协议", "desc": "全体合伙人签署的合伙协议", "note": "普通合伙/有限合伙通用"},
            {"name": "全体合伙人身份证", "desc": "原件及复印件", "note": "包括普通合伙人和有限合伙人"},
            {"name": "执行事务合伙人委派书", "desc": "如执行事务合伙人为法人时", "note": "加盖公章"},
            {"name": "注册地址证明", "desc": "租赁合同+房产证复印件", "note": "注册地与经营地一致"},
        ],
        "FOREIGN": [
            {"name": "外商投资批准证书", "desc": "商务部门颁发的批准文件", "note": "外资企业必须提供"},
            {"name": "公司章程", "desc": "最新版，中英文对照需公证", "note": "外资企业提供"},
            {"name": "外商投资企业批准证书", "desc": "商务部门审批文件", "note": "设立时审批的批文"},
            {"name": "注册地址证明", "desc": "租赁合同+房产证复印件", "note": "注册地与经营地一致"},
            {"name": "外汇登记证", "desc": "外汇管理部门颁发", "note": "涉及外汇业务时提供"},
        ],
        "SOLE_PROP": [
            {"name": "个体工商户营业执照", "desc": "正副本原件及复印件", "note": "经营者姓名需与身份证一致"},
            {"name": "经营者身份证", "desc": "原件及正反面复印件", "note": "个体工商户经营者本人"},
            {"name": "实际经营地址证明", "desc": "租赁合同或房产证明", "note": "部分银行要求"},
        ],
    }

    # 开户流程
    PROCESS_STEPS = [
        {"step": 1, "name": "预约开户", "desc": "通过银行官网、手机银行或电话预约开户时间，填写企业基本信息"},
        {"step": 2, "name": "准备材料", "desc": "对照材料清单准备齐全所有文件，确保复印件加盖公章"},
        {"step": 3, "name": "前往银行柜台", "desc": "携带全部材料到银行对公业务柜台办理，填写开户申请书"},
        {"step": 4, "name": "银行审核", "desc": "银行对材料进行审核，审核时间通常为1-3个工作日"},
        {"step": 5, "name": "人行备案", "desc": "银行向中国人民银行提交开户备案，获取基本存款账户编号"},
        {"step": 6, "name": "领取开户许可证", "desc": "审核通过后，领取开户许可证（基本户）或账户信息"},
        {"step": 7, "name": "启用账户", "desc": "领取网银U盾/企业手机银行，设置账户密码，正式启用"},
    ]

    # 费用说明
    FEES = {
        "LTD": "开户费：200-800元；年费：300-1200元/年；网银U盾：50-200元/个",
        "CORP": "开户费：300-1000元；年费：500-2000元/年；网银U盾：50-200元/个",
        "PARTNERSHIP": "开户费：200-800元；年费：300-1200元/年；网银U盾：50-200元/个",
        "FOREIGN": "开户费：500-2000元；年费：800-3000元/年；网银U盾：50-200元/个",
        "SOLE_PROP": "开户费：0-300元；年费：0-600元/年；网银U盾：50-200元/个",
    }

    # 注意事项
    NOTES = [
        "基本存款账户是企业的唯一主账户，建议先开基本户再开一般户",
        "注册资本较大的企业建议提前与银行客户经理沟通，确认上门核实地址",
        "部分银行对外资企业有特殊要求，建议提前电话咨询",
        "开户许可证遗失需登报挂失，并到人行办理补发手续",
        "企业名称变更后，需在30日内到开户银行办理变更手续",
        "每年需进行账户年检，配合银行提供相关经营证明材料",
    ]

    # 常见问题
    FAQ = [
        {
            "q": "基本户和一般户有什么区别？",
            "a": "基本户是每个企业只能开一个的主账户，用于日常转账结算、工资发放等；一般户是在有基本户的基础上可开多个的辅助账户，主要用于借款、资金归集等业务。"
        },
        {
            "q": "开户需要多长时间？",
            "a": "材料齐全的情况下，银行审核通常需要1-3个工作日，人行备案1-2个工作日，整体约3-5个工作日。外资企业因材料较多可能需要7-10个工作日。"
        },
        {
            "q": "注册资本大小会影响开户吗？",
            "a": "注册资本本身不影响开户资格，但注册资本较大的企业（如500万以上）银行通常会进行上门实地核查经营地址，流程会略有延长。"
        },
        {
            "q": "一个人可以注册几个公司开几个基本户？",
            "a": "一个人可以作为多家公司的法定代表人，但每家公司只能开立一个基本存款账户，且基本户必须为同名账户。"
        },
        {
            "q": "外资企业开户有什么特殊要求？",
            "a": "外资企业需额外提供外商投资批准证书、外商投资企业批准证书等文件，部分银行还会要求提供外汇登记证。流程比内资企业稍复杂。"
        },
        {
            "q": "开户费用是多少？",
            "a": "不同银行收费标准不同，国有大行通常开户费200-800元、年费300-1200元；外资银行收费相对较高。具体以各银行官方公布为准。"
        },
        {
            "q": "个体工商户可以开对公账户吗？",
            "a": "可以。个体工商户可开立基本存款账户，材料要求相对简化，只需提供营业执照和经营者身份证。"
        },
        {
            "q": "异地企业可以在本地开户吗？",
            "a": "可以在注册地以外的城市开户，但需提供实际经营地址证明，且部分银行可能要求上门核实。具体以各银行政策为准。"
        },
    ]

    def parse_input(self, query: str) -> dict:
        """解析用户输入，提取企业信息"""
        result = {
            "enterprise_type": None,
            "registered_capital": None,
            "business_scope": None,
            "raw_query": query,
        }

        # 提取企业类型
        for etype, code in self.ENTERPRISE_TYPES.items():
            if etype in query:
                result["enterprise_type"] = etype
                result["enterprise_code"] = code
                break

        # 如果没找到明确类型，尝试从关键词推断
        if not result["enterprise_type"]:
            if any(kw in query for kw in ["科技", "技术", "软件", "信息"]):
                result["enterprise_type"] = "有限责任公司"
                result["enterprise_code"] = "LTD"
            elif any(kw in query for kw in ["股份", "上市"]):
                result["enterprise_type"] = "股份有限公司"
                result["enterprise_code"] = "CORP"
            elif any(kw in query for kw in ["合伙"]):
                result["enterprise_type"] = "合伙企业"
                result["enterprise_code"] = "PARTNERSHIP"
            elif any(kw in query for kw in ["外资", "外商", "中外合资"]):
                result["enterprise_type"] = "外资企业"
                result["enterprise_code"] = "FOREIGN"
            elif any(kw in query for kw in ["个体", "个人"]):
                result["enterprise_type"] = "个体工商户"
                result["enterprise_code"] = "SOLE_PROP"
            else:
                # 默认推断为有限责任公司
                result["enterprise_type"] = "有限责任公司"
                result["enterprise_code"] = "LTD"

        # 提取注册资本
        capital_pattern = r"注册资本[是为]?\s*([\d,．.]+)\s*(万|亿|元)?"
        match = re.search(capital_pattern, query)
        if match:
            raw_capital = match.group(1).replace(",", "").replace("，", "")
            unit = match.group(2) or "万"
            try:
                value = float(raw_capital)
                if unit == "亿":
                    value *= 10000
                result["registered_capital"] = f"{int(value)}万"
            except ValueError:
                result["registered_capital"] = raw_capital + unit

        # 提取经营范围关键词
        scope_keywords = []
        scope_map = {
            "科技": "技术开发、技术服务、技术咨询",
            "技术": "技术服务、技术开发",
            "软件": "软件开发、软件服务",
            "制造": "生产、制造、加工",
            "贸易": "批发、零售、进出口",
            "咨询": "商务咨询、企业管理咨询",
        }
        for kw, scope in scope_map.items():
            if kw in query:
                scope_keywords.append(scope)
        if scope_keywords:
            result["business_scope"] = "、".join(list(dict.fromkeys(scope_keywords)))

        return result

    def generate_materials(self, enterprise_code: str, registered_capital: Optional[str] = None) -> list:
        """生成材料清单"""
        materials = list(self.COMMON_MATERIALS)

        # 添加类型特定材料
        if enterprise_code in self.TYPE_SPECIFIC_MATERIALS:
            materials.extend(self.TYPE_SPECIFIC_MATERIALS[enterprise_code])

        # 注册资本较大时，额外材料
        if registered_capital:
            try:
                cap_value = int(registered_capital.replace("万", ""))
                if cap_value >= 1000:
                    materials.append({
                        "name": "注册地址实地核查",
                        "desc": "银行可能安排上门核实经营地址",
                        "note": "注册资本1000万以上企业"
                    })
                    materials.append({
                        "name": "董事会关于开户的特别决议",
                        "desc": "大额注册资本企业可能需要",
                        "note": "注册资本1000万以上企业"
                    })
            except (ValueError, AttributeError):
                pass

        # 去重（按name去重）
        seen = set()
        unique_materials = []
        for m in materials:
            if m["name"] not in seen:
                seen.add(m["name"])
                unique_materials.append(m)

        return unique_materials

    def generate(
        self,
        query: str,
        account_type: str = "基本户",
        format: str = "text",
    ) -> dict:
        """
        生成对公开户报告

        Args:
            query: 用户查询，如"对公开户 科技公司 注册资本500万"
            account_type: 账户类型，"基本户"或"一般户"
            format: 输出格式，"text"或"json"

        Returns:
            dict: 包含材料清单、流程、注意事项、FAQ等
        """
        # 解析输入
        parsed = self.parse_input(query)

        # 生成材料清单
        materials = self.generate_materials(
            parsed.get("enterprise_code", "LTD"),
            parsed.get("registered_capital")
        )

        # 构建结果
        result = {
            "enterprise_type": parsed.get("enterprise_type", "有限责任公司"),
            "enterprise_code": parsed.get("enterprise_code", "LTD"),
            "registered_capital": parsed.get("registered_capital"),
            "business_scope": parsed.get("business_scope"),
            "account_type": account_type,
            "account_difference": self._get_account_difference(),
            "materials": materials,
            "process": self.PROCESS_STEPS,
            "duration": self._get_duration(parsed.get("enterprise_code", "LTD")),
            "fees": self.FEES.get(parsed.get("enterprise_code", "LTD"), self.FEES["LTD"]),
            "notes": self.NOTES,
            "faq": self.FAQ,
        }

        if format == "json":
            return result

        # text格式输出
        return self._format_text(result)

    def _get_account_difference(self) -> dict:
        """获取基本户和一般户的区别"""
        return {
            "basic": {
                "name": "基本存款账户",
                "quantity": "每个企业只能开立1个",
                "function": "日常转账结算、工资发放、现金存取",
                "requirement": "需在人行备案，开户许可证",
                "transfer_limit": "无限额",
            },
            "general": {
                "name": "一般存款账户",
                "quantity": "可开立多个",
                "function": "借款、资金归集、临时转账",
                "requirement": "须先开立基本户，再人行备案",
                "transfer_limit": "部分有限额",
            },
        }

    def _get_duration(self, enterprise_code: str) -> dict:
        """获取办理时长"""
        durations = {
            "LTD": {"total": "3-5个工作日", "bank_review": "1-3个工作日", "pbc_filing": "1-2个工作日"},
            "CORP": {"total": "5-7个工作日", "bank_review": "2-4个工作日", "pbc_filing": "2-3个工作日"},
            "PARTNERSHIP": {"total": "3-5个工作日", "bank_review": "1-3个工作日", "pbc_filing": "1-2个工作日"},
            "FOREIGN": {"total": "7-10个工作日", "bank_review": "3-5个工作日", "pbc_filing": "3-4个工作日"},
            "SOLE_PROP": {"total": "1-3个工作日", "bank_review": "0.5-1个工作日", "pbc_filing": "0.5-1个工作日"},
        }
        return durations.get(enterprise_code, durations["LTD"])

    def _format_text(self, result: dict) -> str:
        """格式化输出为文本"""
        lines = []
        lines.append("=" * 60)
        lines.append("           企业对公开户办理指南")
        lines.append("=" * 60)
        lines.append(f"\n【企业信息】")
        lines.append(f"  企业类型：{result['enterprise_type']}")
        if result.get("registered_capital"):
            lines.append(f"  注册资本：{result['registered_capital']}")
        if result.get("business_scope"):
            lines.append(f"  经营范围：{result['business_scope']}")
        lines.append(f"  开户类型：{result['account_type']}")

        # 基本户vs一般户
        diff = result["account_difference"]
        lines.append(f"\n【基本户 vs 一般户】")
        lines.append(f"  基本户：{diff['basic']['name']} | 数量：{diff['basic']['quantity']}")
        lines.append(f"  一般户：{diff['general']['name']} | 数量：{diff['general']['quantity']}")

        # 材料清单
        lines.append(f"\n【所需材料清单】({len(result['materials'])}项)")
        for i, m in enumerate(result["materials"], 1):
            lines.append(f"  {i}. {m['name']}")
            lines.append(f"     说明：{m['desc']}")
            if m.get("note"):
                lines.append(f"     注意：{m['note']}")

        # 开户流程
        lines.append(f"\n【开户流程】({len(result['process'])}步)")
        for step in result["process"]:
            lines.append(f"  第{step['step']}步：{step['name']}")
            lines.append(f"         {step['desc']}")

        # 办理时长
        dur = result["duration"]
        lines.append(f"\n【办理时长】")
        lines.append(f"  预计总时长：{dur['total']}")
        lines.append(f"  银行审核：{dur['bank_review']}")
        lines.append(f"  人行备案：{dur['pbc_filing']}")

        # 费用
        lines.append(f"\n【费用说明】")
        lines.append(f"  {result['fees']}")
        lines.append(f"  注：具体费用以各银行官方公布为准")

        # 注意事项
        lines.append(f"\n【注意事项】")
        for i, note in enumerate(result["notes"], 1):
            lines.append(f"  {i}. {note}")

        # 常见问题
        lines.append(f"\n【常见问题FAQ】")
        for i, qa in enumerate(result["faq"], 1):
            lines.append(f"  Q{i}：{qa['q']}")
            lines.append(f"  A{i}：{qa['a']}")

        lines.append("\n" + "=" * 60)
        lines.append("  提示：本指南仅供参考，具体以当地银行要求为准")
        lines.append("=" * 60)

        return "\n".join(lines)


# 快捷函数
def generate_account_opening_report(query: str, account_type: str = "基本户", format: str = "text") -> dict:
    """快速生成开户报告"""
    engine = CorpAccountEngine()
    return engine.generate(query, account_type, format)


if __name__ == "__main__":
    # 测试
    engine = CorpAccountEngine()
    result = engine.generate("对公开户 科技公司 注册资本500万")
    print(result)
