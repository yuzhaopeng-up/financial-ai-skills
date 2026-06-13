#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
业务流程合规性自动检查引擎 v1.0
自动检查业务流程合规性，输出合规报告和整改建议

Author: ArkClaw
Version: 1.0.0
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple


class ComplianceAutoEngine:
    """业务流程合规性自动检查引擎"""

    VERSION = "1.0.0"

    # 合规规则库 - 14条规则
    COMPLIANCE_RULES = {
        # 反洗钱类
        "C001": {
            "name": "客户身份核验",
            "category": "反洗钱",
            "description": "客户身份核验是否完整（姓名+证件+手机号+人脸识别）",
            "severity": "high",
            "patterns": [
                r"未核验|未认证|未验证",
                r"身份信息不完整",
                r"证件过期",
                r"人脸识别未通过",
            ],
            "suggestion": "完成客户身份核验，包含姓名、证件号码、手机号及人脸识别",
            "regulation": "《金融机构客户身份识别和客户身份资料及交易记录保存管理办法》"
        },
        "C002": {
            "name": "大额交易报告",
            "category": "反洗钱",
            "description": "单笔或累计交易超过5万元需报告可疑交易",
            "severity": "high",
            "patterns": [
                r"交易金额.{0,5}(超过|大于|多于).{0,5}(5万|50000|五十万|五万)",
                r"大额交易.{0,10}(未报|未报告|未申报)",
                r"拆分.{0,5}(规避|逃避).{0,5}(报告|大额)",
            ],
            "suggestion": "对超过5万元的交易进行可疑交易报告",
            "regulation": "《金融机构大额交易和可疑交易报告管理办法》"
        },
        "C003": {
            "name": "可疑交易识别",
            "category": "反洗钱",
            "description": "识别可疑交易行为（分散转账、频繁交易、夜间交易等）",
            "severity": "high",
            "patterns": [
                r"分散转账",
                r"频繁.{0,5}(转账|交易|汇款)",
                r"夜间.{0,5}(转账|交易|汇款)",
                r"快进快出",
                r"账户.{0,5}(过渡|借用|出租)",
            ],
            "suggestion": "对可疑交易进行人工审核，必要时上报反洗钱监测中心",
            "regulation": "《金融机构大额交易和可疑交易报告管理办法》"
        },
        # 适当性管理类
        "C004": {
            "name": "风险测评有效期",
            "category": "适当性管理",
            "description": "客户风险测评报告有效期为1年，过期需重新测评",
            "severity": "medium",
            "patterns": [
                r"风险测评.{0,5}(过期|超期|失效)",
                r"风险测评.{0,5}(超过|大于|多于).{0,5}1年|一年",
                r"风险评估.{0,5}(未做|缺失|过期)",
                r"超过.{0,5}12.{0,5}个月",
            ],
            "suggestion": "要求客户重新完成风险测评，确保在有效期内",
            "regulation": "《证券期货投资者适当性管理办法》"
        },
        "C005": {
            "name": "产品风险匹配",
            "category": "适当性管理",
            "description": "产品风险等级需与客户风险承受能力匹配",
            "severity": "high",
            "patterns": [
                r"风险等级不匹配",
                r"风险等级.{0,5}(高于|超过|大于).{0,5}(客户|投资者)",
                r"高风险产品.{0,5}(未确认|未告知|未揭示)",
                r"客户.{0,5}(保守型|谨慎型).{0,5}(购买|认购|申购).{0,5}(高风险|权益类|股票型)",
            ],
            "suggestion": "核对客户风险等级与产品风险等级，不匹配需签署《不适当购买确认书》",
            "regulation": "《证券期货投资者适当性管理办法》"
        },
        # 信息披露类
        "C006": {
            "name": "信息披露完整性",
            "category": "信息披露",
            "description": "产品销售需完整披露风险、费用、收益特征等信息",
            "severity": "high",
            "patterns": [
                r"未披露|披露不完整",
                r"风险揭示.{0,5}(缺失|不完整|未做)",
                r"产品说明书.{0,5}(未提供|未签署)",
                r"费率.{0,5}(未说明|未告知)",
            ],
            "suggestion": "补充完整的产品信息披露，确保客户签署风险揭示书",
            "regulation": "《商业银行理财产品销售管理办法》"
        },
        # 开户业务类
        "C007": {
            "name": "合同签署合规",
            "category": "开户业务",
            "description": "各类合同协议需由客户本人签署完整",
            "severity": "medium",
            "patterns": [
                r"代签|代签字|代盖章",
                r"签名.{0,5}(缺失|不全|遗漏)",
                r"日期.{0,5}(缺失|未填|空白)",
                r"合同.{0,5}(未签署|未签字|未盖章)",
            ],
            "suggestion": "确保合同由客户本人签署完整，包含签名、日期等要素",
            "regulation": "《民法典》第490条"
        },
        # 双录类
        "C008": {
            "name": "双录合规检查",
            "category": "双录",
            "description": "高风险产品销售需进行录音录像",
            "severity": "high",
            "patterns": [
                r"双录.{0,5}(缺失|未做|未完成)",
                r"录音录像.{0,5}(缺失|未做|未完成)",
                r"录像.{0,5}(中断|不完整|模糊)",
                r"高风险产品.{0,5}(未双录|无录音录像)",
            ],
            "suggestion": "对高风险产品销售进行完整的录音录像，保存至少5年",
            "regulation": "《银行业金融机构销售专区录音录像管理暂行规定》"
        },
        # 贷款业务类
        "C009": {
            "name": "利率上限控制",
            "category": "贷款业务",
            "description": "贷款年化利率不超过LPR4倍（目前约15.4%）",
            "severity": "high",
            "patterns": [
                r"年化利率.{0,5}(超过|高于|大于).{0,5}(15\.?%|16\.?%|17\.?%|18\.?%|20\.?%|24\.?%|36\.?%)",
                r"利率.{0,5}(超过|高于).{0,5}LPR.{0,5}(4倍|四倍)",
                r"综合成本.{0,5}(超过|高于).{0,5}(24|36)%",
                r"砍头息|预扣利息",
            ],
            "suggestion": "调整贷款利率至合规区间，禁止收取砍头息",
            "regulation": "《关于进一步加强金融消费者权益保护工作的指导意见》"
        },
        "C010": {
            "name": "贷款用途合规",
            "category": "贷款业务",
            "description": "贷款资金用途需符合规定，不得流入股市、楼市等",
            "severity": "high",
            "patterns": [
                r"贷款用途.{0,5}(流入|进入).{0,5}(股市|证券市场|房地产|楼市)",
                r"资金.{0,5}(流入|进入).{0,5}(股市|证券市场|房地产|楼市)",
                r"流入股市|流入楼市|流入房地产",
                r"贷款.{0,5}(炒股|购房|买房)",
                r"挪用.{0,5}(贷款|借款|资金)",
            ],
            "suggestion": "核实贷款用途，确保资金流向合规领域，保存用途证明材料",
            "regulation": "《商业银行贷款管理暂行办法》"
        },
        # 理财销售类
        "C011": {
            "name": "理财冷静期",
            "category": "理财销售",
            "description": "银行理财需提供不少于24小时的冷静期",
            "severity": "medium",
            "patterns": [
                r"冷静期.{0,5}(未设|缺失|不足)",
                r"购买后.{0,5}(无法|不能).{0,5}(撤销|撤回|取消)",
                r"募集期.{0,5}(未告知|未说明).{0,5}(冷静期|撤退)",
            ],
            "suggestion": "在销售时明确告知客户冷静期权利，确保可撤销",
            "regulation": "《商业银行理财产品销售管理办法》"
        },
        # 跨境业务类
        "C012": {
            "name": "跨境汇款申报",
            "category": "跨境业务",
            "description": "跨境汇款超过限额需进行国际收支申报",
            "severity": "high",
            "patterns": [
                r"跨境汇款.{0,5}(未申报|未报送)",
                r"国际收支.{0,5}(未申报|缺失)",
                r"外汇.{0,5}(申报.{0,5})?(缺失|未做)",
                r"跨境.{0,5}(超过|大于).{0,5}(5万|50000)",
            ],
            "suggestion": "对跨境汇款进行国际收支申报，保存申报证明",
            "regulation": "《国际收支统计申报办法》"
        },
        # 信用卡类
        "C013": {
            "name": "信用卡额度管理",
            "category": "信用卡",
            "description": "信用卡额度调整需有完整审批记录",
            "severity": "medium",
            "patterns": [
                r"额度.{0,5}(调整.{0,5})?(无|缺失|未).{0,5}(审批|记录)",
                r"额度.{0,5}(超额|超限).{0,5}(未告知|未审批)",
                r"降额.{0,5}(未通知|未告知)",
                r"临时额度.{0,5}(超期|超时)",
            ],
            "suggestion": "额度调整需经过完整审批流程，并通知客户",
            "regulation": "《商业银行信用卡业务监督管理办法》"
        },
        # 信息安全类
        "C014": {
            "name": "客户信息保密",
            "category": "信息安全",
            "description": "客户信息收集使用需获得授权，不得泄露",
            "severity": "high",
            "patterns": [
                r"信息.{0,5}(泄露|外泄|丢失)",
                r"客户信息.{0,5}(未授权|未同意).{0,5}(使用|收集|提供)",
                r"数据.{0,5}(泄露|外泄)",
                r"隐私.{0,5}(泄露|侵犯)",
            ],
            "suggestion": "立即通知受影响的客户，采取补救措施，并向监管部门报告",
            "regulation": "《个人信息保护法》《银行业消费者权益保护工作指引》"
        },
    }

    # 业务类型关键词
    BUSINESS_TYPES = {
        "贷款业务": ["贷款", "借款", "个人贷款", "企业贷款", "信用贷款", "抵押贷款"],
        "存款业务": ["存款", "储蓄", "定期", "活期", "大额存单"],
        "理财销售": ["理财", "基金", "净值", "收益", "申购", "认购", "购买"],
        "保险销售": ["保险", "投保", "理赔", "寿险", "财险", "健康险"],
        "信用卡业务": ["信用卡", "额度", "账单", "分期", "还款", "透支"],
        "跨境汇款": ["跨境", "外汇", "国际汇款", "购汇", "结汇", "跨境转账"],
        "开户业务": ["开户", "签约", "开户行", "新户", "首开"],
        "反洗钱检查": ["反洗钱", "可疑交易", "大额交易", "客户身份", "身份识别"],
        "信息披露": ["披露", "风险揭示", "产品说明书", "告知", "揭示"],
        "客户适当性管理": ["适当性", "风险测评", "风险评估", "投资者", "合格投资者"],
    }

    def __init__(self, api_mode: bool = False):
        self.api_mode = api_mode
        self._log("初始化业务流程合规性自动检查引擎 v%s" % self.VERSION)

    def _log(self, msg: str):
        if not self.api_mode:
            print(msg)

    def detect_business_type(self, text: str) -> str:
        """识别业务类型"""
        text_lower = text.lower()
        scores = {}

        for biz_type, keywords in self.BUSINESS_TYPES.items():
            score = sum(1 for kw in keywords if kw.lower() in text_lower)
            if score > 0:
                scores[biz_type] = score

        if scores:
            return max(scores, key=scores.get)
        return "未知业务"

    def check_compliance(
        self,
        text: str,
        business_type: str = None,
        specific_rules: List[str] = None
    ) -> Dict[str, Any]:
        """
        检查合规性

        Args:
            text: 操作记录文本
            business_type: 业务类型（可选，自动识别）
            specific_rules: 指定检查的规则ID列表（可选）

        Returns:
            合规检查结果
        """
        if not business_type:
            business_type = self.detect_business_type(text)

        # 获取规则列表
        if specific_rules:
            rules_to_check = {
                rid: rule for rid, rule in self.COMPLIANCE_RULES.items()
                if rid in specific_rules
            }
        else:
            rules_to_check = self.COMPLIANCE_RULES

        # 执行规则检查
        violations = []
        for rule_id, rule in rules_to_check.items():
            found = self._check_rule(text, rule)
            if found:
                violations.append({
                    "rule_id": rule_id,
                    **found
                })

        # 按严重程度排序
        severity_order = {"high": 0, "medium": 1, "low": 2}
        violations.sort(key=lambda x: severity_order.get(x["severity"], 3))

        # 统计
        stats = {
            "total": len(violations),
            "high": len([v for v in violations if v["severity"] == "high"]),
            "medium": len([v for v in violations if v["severity"] == "medium"]),
            "low": len([v for v in violations if v["severity"] == "low"]),
            "by_category": self._count_by_category(violations)
        }

        # 计算合规评分
        compliance_score = self._calculate_compliance_score(stats)

        # 风险等级
        if stats["high"] > 0:
            risk_level = "high"
            risk_label = "🔴 高风险"
        elif stats["medium"] > 0:
            risk_level = "medium"
            risk_label = "🟡 中风险"
        elif stats["low"] > 0:
            risk_level = "low"
            risk_label = "🟢 低风险"
        else:
            risk_level = "pass"
            risk_label = "✅ 合规"

        return {
            "business_type": business_type,
            "compliance_score": compliance_score,
            "risk_level": risk_level,
            "risk_label": risk_label,
            "stats": stats,
            "violations": violations,
            "summary": self._generate_summary(stats, business_type),
            "rectification": self._generate_rectification(violations),
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "rules_count": len(rules_to_check)
        }

    def _check_rule(self, text: str, rule: Dict) -> Optional[Dict]:
        """检查单条规则"""
        text_lower = text.lower()

        for pattern in rule["patterns"]:
            match = re.search(pattern, text_lower)
            if match:
                context_start = max(0, match.start() - 20)
                context_end = min(len(text), match.end() + 50)
                context = text[context_start:context_end]

                return {
                    "name": rule["name"],
                    "category": rule["category"],
                    "description": rule["description"],
                    "severity": rule["severity"],
                    "suggestion": rule["suggestion"],
                    "regulation": rule["regulation"],
                    "matched_pattern": pattern,
                    "matched_text": context,
                    "confidence": 0.9
                }
        return None

    def _count_by_category(self, violations: List[Dict]) -> Dict[str, int]:
        """按类别统计违规"""
        categories = {}
        for v in violations:
            cat = v["category"]
            categories[cat] = categories.get(cat, 0) + 1
        return categories

    def _calculate_compliance_score(self, stats: Dict) -> float:
        """计算合规评分"""
        # 基础分100分，每高风险-20，中风险-10，低风险-3
        score = 100.0
        score -= stats["high"] * 20
        score -= stats["medium"] * 10
        score -= stats["low"] * 3
        return max(0, min(100, score))

    def _generate_summary(self, stats: Dict, business_type: str) -> str:
        """生成检查摘要"""
        if stats["total"] == 0:
            return f"未发现违规事项，业务类型「{business_type}」合规检查通过"

        high = stats["high"]
        medium = stats["medium"]
        low = stats["low"]

        parts = []
        if high > 0:
            parts.append(f"{high}个高风险违规")
        if medium > 0:
            parts.append(f"{medium}个中风险违规")
        if low > 0:
            parts.append(f"{low}个低风险违规")

        return f"发现「{business_type}」相关{'、'.join(parts)}，需立即整改"

    def _generate_rectification(self, violations: List[Dict]) -> List[Dict]:
        """生成整改建议"""
        rectifications = []
        for v in violations:
            rectifications.append({
                "rule_id": v["rule_id"],
                "name": v["name"],
                "priority": v["severity"],
                "action": v["suggestion"],
                "deadline": self._get_deadline(v["severity"])
            })

        # 按优先级排序
        priority_order = {"high": 0, "medium": 1, "low": 2}
        rectifications.sort(key=lambda x: priority_order.get(x["priority"], 3))
        return rectifications

    def _get_deadline(self, severity: str) -> str:
        """获取整改期限"""
        deadlines = {
            "high": "立即整改（24小时内）",
            "medium": "3个工作日内",
            "low": "5个工作日内"
        }
        return deadlines.get(severity, "5个工作日内")

    def format_text(self, result: Dict) -> str:
        """格式化输出为文本"""
        lines = [
            f"📋 **业务流程合规性检查报告**",
            f"",
            f"🏢 业务类型: {result['business_type']}",
            f"⏰ 检查时间: {result['checked_at']}",
            f"📐 检查规则: {result['rules_count']}条",
            f"",
            f"{'='*36}",
            f"",
            f"📊 **合规评估**",
            f"",
            f"合规评分: {result['compliance_score']:.1f}/100",
            f"风险等级: {result['risk_label']}",
            f"",
            f"📈 **违规统计**",
            f"   🔴 高风险: {result['stats']['high']}个",
            f"   🟡 中风险: {result['stats']['medium']}个",
            f"   🟢 低风险: {result['stats']['low']}个",
        ]

        if result["stats"]["by_category"]:
            lines.append(f"")
            lines.append(f"📂 **按类别分布**")
            for cat, count in result["stats"]["by_category"].items():
                lines.append(f"   {cat}: {count}个")

        lines.extend([
            f"",
            f"{'='*36}",
            f"",
            f"📝 **检查摘要**",
            f"",
            f"{result['summary']}",
        ])

        if result["violations"]:
            lines.extend([
                f"",
                f"{'='*36}",
                f"",
                f"⚠️ **违规详情**",
            ])

            for v in result["violations"]:
                severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(v["severity"], "⚪")
                lines.extend([
                    f"",
                    f"{severity_icon} **{v['name']}** [{v['rule_id']}]",
                    f"   类别: {v['category']}",
                    f"   描述: {v['description']}",
                    f"   建议: {v['suggestion']}",
                    f"   法规: {v['regulation']}",
                    f"   匹配: ...{v['matched_text']}...",
                ])

        if result["rectification"]:
            lines.extend([
                f"",
                f"{'='*36}",
                f"",
                f"🔧 **整改建议**",
            ])
            for i, r in enumerate(result["rectification"], 1):
                priority_label = {"high": "🔴紧急", "medium": "🟡一般", "low": "🟢缓办"}.get(r["priority"], "")
                lines.extend([
                    f"",
                    f"{i}. **{r['name']}** {priority_label}",
                    f"   操作: {r['action']}",
                    f"   期限: {r['deadline']}",
                ])

        lines.append(f""
            f"{'='*36}"
            f""
            f"_报告生成时间: {result['checked_at']}_"
        )

        return '\n'.join(lines)

    def format_json(self, result: Dict) -> str:
        """格式化输出为JSON"""
        return json.dumps(result, ensure_ascii=False, indent=2)

    def format_wecom_card(self, result: Dict) -> Dict:
        """格式化输出为企微卡片"""
        template_map = {
            "high": "red",
            "medium": "orange",
            "low": "green",
            "pass": "blue"
        }

        card = {
            "type": "interactive",
            "card": {
                "header": {
                    "title": f"📋 合规检查 - {result['risk_label']}",
                    "template": template_map.get(result["risk_level"], "gray")
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**业务类型**: {result['business_type']}"
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**合规评分**: {result['compliance_score']:.1f}/100\n**风险等级**: {result['risk_label']}"
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**违规统计**: 🔴{result['stats']['high']} 🟡{result['stats']['medium']} 🟢{result['stats']['low']}"
                        }
                    },
                    {"tag": "hr"},
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**摘要**: {result['summary']}"
                        }
                    },
                ]
            }
        }

        # 添加违规详情
        if result["violations"]:
            elements = card["card"]["elements"]
            elements.append({"tag": "hr"})
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**违规详情** ({len(result['violations'])}项)"
                }
            })

            for v in result["violations"][:5]:  # 最多显示5条
                severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(v["severity"], "⚪")
                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"{severity_icon} {v['name']}: {v['suggestion']}"
                    }
                })

            if len(result["violations"]) > 5:
                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"_...还有{len(result['violations']) - 5}项违规_"
                    }
                })

        # 添加整改建议
        if result["rectification"]:
            elements = card["card"]["elements"]
            elements.append({"tag": "hr"})
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**整改建议** ({len(result['rectification'])}项)"
                }
            })

            for r in result["rectification"][:3]:  # 最多显示3条
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(r["priority"], "⚪")
                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"{priority_icon} {r['name']} - {r['deadline']}"
                    }
                })

        return card


def main():
    """主函数 - CLI测试"""
    print("=" * 50)
    print("🦞 业务流程合规性自动检查引擎 v1.0")
    print("=" * 50)
    print()

    engine = ComplianceAutoEngine()

    # 测试用例
    test_cases = [
        {
            "name": "贷款业务合规检查",
            "business_type": "贷款业务",
            "text": """
            客户张三分期购买手机贷款15000元，
            年化利率18%，略超LPR4倍，
            贷款用途为日常消费，核对贷款去向时发现资金流入股市，
            客户风险测评已过期13个月，
            未签署产品风险揭示书
            """
        },
        {
            "name": "反洗钱检查",
            "business_type": "反洗钱检查",
            "text": """
            客户李四账户频繁进行小额转账，单笔约9900元，
            累计超过50万元，单笔最大9.8万元，
            存在分散转账、规避报告的嫌疑，
            客户身份核验已完成，人脸识别通过
            """
        },
        {
            "name": "理财销售合规检查",
            "business_type": "理财销售",
            "text": """
            客户王五为保守型投资者，购买了高风险股票型基金，
            风险等级不匹配，销售人员未进行双录，
            未签署产品风险揭示书和适当性确认书，
            客户购买后想撤销被告知没有冷静期
            """
        }
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"📋 测试用例 {i}: {case['name']}")
        print(f"{'='*50}")
        print()

        result = engine.check_compliance(case["text"], case["business_type"])
        print(engine.format_text(result))
        print()


if __name__ == "__main__":
    main()
