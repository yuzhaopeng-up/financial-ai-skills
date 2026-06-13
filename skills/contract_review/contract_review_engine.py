#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合同智能审查引擎 v1.0
自动审查合同条款，识别风险点，提供修改建议

Author: ArkClaw
Version: 1.0.0
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple


class ContractReviewEngine:
    """合同智能审查引擎"""
    
    VERSION = "1.0.0"
    
    # 风险规则库
    RISK_RULES = {
        # 高风险规则
        "high": [
            {
                "id": "R001",
                "name": "利率条款不明确",
                "pattern": r"利率.{0,5}(不确定|另行|待定)",
                "description": "利率条款约定不明确，可能导致争议",
                "suggestion": "明确约定利率的具体数值或计算方式",
                "law_reference": "《民法典》第670条"
            },
            {
                "id": "R002",
                "name": "担保范围过宽",
                "pattern": r"担保.{0,20}(一切|所有|全部|无限)",
                "description": "担保范围约定过于宽泛",
                "suggestion": "限定担保的具体范围和最高限额",
                "law_reference": "《民法典》第681条"
            },
            {
                "id": "R003",
                "name": "违约金过高",
                "pattern": r"违约金.{0,10}(30%|30％|三成)",
                "description": "违约金比例超过法定上限",
                "suggestion": "违约金不超过实际损失的30%",
                "law_reference": "《民法典》第585条"
            },
            {
                "id": "R004",
                "name": "管辖权约定不明",
                "pattern": r"管辖.{0,10}(待定|另行|不确定)",
                "description": "管辖法院约定不明确",
                "suggestion": "明确约定管辖法院",
                "law_reference": "《民事诉讼法》第34条"
            },
            {
                "id": "R005",
                "name": "保密条款缺失",
                "pattern": r"(保密|机密|泄露).{0,20}?(无|不|未|缺失|未约定)",
                "description": "重要合同缺少保密条款",
                "suggestion": "添加保密条款，明确保密范围和期限",
                "law_reference": "《民法典》第501条"
            },
        ],
        # 中风险规则
        "medium": [
            {
                "id": "R006",
                "name": "还款期限模糊",
                "pattern": r"还款.{0,10}(尽快|尽快|适时|及时)",
                "description": "还款期限约定不够明确",
                "suggestion": "明确具体的还款日期或计算方式",
                "law_reference": "《民法典》第675条"
            },
            {
                "id": "R007",
                "name": "提前还款限制",
                "pattern": r"提前还款.{0,10}(不允许|禁止|违约金)",
                "description": "对提前还款设置不合理限制",
                "suggestion": "允许提前还款并明确计算方式",
                "law_reference": "《民法典》第672条"
            },
            {
                "id": "R008",
                "name": "争议解决方式不明确",
                "pattern": r"(仲裁|诉讼|协商).{0,10}?(未约定|无)",
                "description": "争议解决方式未明确约定",
                "suggestion": "明确约定仲裁或诉讼方式",
                "law_reference": "《民事诉讼法》第34条"
            },
            {
                "id": "R009",
                "name": "通知条款不完整",
                "pattern": r"通知.{0,10}(方式|地址|联系人)",
                "description": "通知条款缺少必要要素",
                "suggestion": "明确通知方式、地址和联系人",
                "law_reference": "《民法典》第490条"
            },
            {
                "id": "R010",
                "name": "不可抗力条款缺失",
                "pattern": r"(不可抗力|地震|疫情).{0,10}?(无|不|未|缺失)",
                "description": "缺少不可抗力条款",
                "suggestion": "添加不可抗力条款及处理方式",
                "law_reference": "《民法典》第590条"
            },
        ],
        # 低风险规则
        "low": [
            {
                "id": "R011",
                "name": "合同份数未明确",
                "pattern": r"(合同份数|各持|各执).{0,10}?(未|无|未写)",
                "description": "合同份数约定不明确",
                "suggestion": "明确合同份数及各执份数",
                "law_reference": "《民法典》第469条"
            },
            {
                "id": "R012",
                "name": "签署日期缺失",
                "pattern": r"(签署|签订|签字).{0,10}?(日期|时间|年月日)",
                "description": "合同签署日期约定不明确",
                "suggestion": "明确签署的具体日期",
                "law_reference": "《民法典》第490条"
            },
            {
                "id": "R013",
                "name": "附件引用不规范",
                "pattern": r"附件.{0,10}(无编号|未注明)",
                "description": "附件引用不够规范",
                "suggestion": "附件应编号并在正文中明确引用",
                "law_reference": "《民法典》第470条"
            },
        ]
    }
    
    # 合同类型关键词
    CONTRACT_TYPES = {
        "贷款合同": ["贷款", "借款", " Lending", "loan"],
        "担保合同": ["担保", "抵押", "质押", "保证", "guarantee"],
        "理财合同": ["理财", "投资", "资产管理"],
        "保险合同": ["保险", "投保", "理赔"],
        "投资协议": ["投资", "入股", "增资", "股权转让"],
        "保密协议": ["保密", "机密", "NDA"],
        "服务合同": ["服务", "咨询", "外包"]
    }
    
    def __init__(self, api_mode: bool = False):
        self.api_mode = api_mode
        self._log("初始化合同智能审查引擎 v%s" % self.VERSION)
    
    def _log(self, msg: str):
        if not self.api_mode:
            print(msg)
    
    def detect_contract_type(self, text: str) -> str:
        """识别合同类型"""
        text_lower = text.lower()
        scores = {}
        
        for contract_type, keywords in self.CONTRACT_TYPES.items():
            score = sum(1 for kw in keywords if kw.lower() in text_lower)
            if score > 0:
                scores[contract_type] = score
        
        if scores:
            return max(scores, key=scores.get)
        return "未知类型"
    
    def review_contract(self, text: str, contract_type: str = None) -> Dict[str, Any]:
        """
        审查合同
        
        Args:
            text: 合同文本
            contract_type: 合同类型（可选，自动识别）
        
        Returns:
            审查结果
        """
        if not contract_type:
            contract_type = self.detect_contract_type(text)
        
        # 执行规则检查
        all_risks = []
        for level in ["high", "medium", "low"]:
            risks = self._check_rules(text, self.RISK_RULES[level], level)
            all_risks.extend(risks)
        
        # 按风险等级和分数排序
        all_risks.sort(key=lambda x: (x["risk_level"], x["confidence"]), reverse=True)
        
        # 统计
        risk_stats = {
            "high": len([r for r in all_risks if r["risk_level"] == "high"]),
            "medium": len([r for r in all_risks if r["risk_level"] == "medium"]),
            "low": len([r for r in all_risks if r["risk_level"] == "low"])
        }
        
        # 风险评分
        risk_score = self._calculate_risk_score(risk_stats)
        
        # 合规评分 (100 - risk_score)
        compliance_score = 100 - risk_score
        
        # 风险等级
        if risk_score >= 60:
            risk_level = "high"
            risk_label = "🔴 高风险"
        elif risk_score >= 30:
            risk_level = "medium"
            risk_label = "🟡 中风险"
        else:
            risk_level = "low"
            risk_label = "🟢 低风险"
        
        return {
            "contract_type": contract_type,
            "risk_score": risk_score,
            "compliance_score": compliance_score,
            "risk_level": risk_level,
            "risk_label": risk_label,
            "risk_stats": risk_stats,
            "risks": all_risks,
            "summary": self._generate_summary(risk_stats, contract_type),
            "reviewed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _check_rules(self, text: str, rules: List[Dict], level: str) -> List[Dict]:
        """检查规则"""
        found_risks = []
        text_lower = text.lower()
        
        for rule in rules:
            if re.search(rule["pattern"], text_lower):
                # 找到匹配的条款
                match = re.search(rule["pattern"], text_lower)
                context_start = max(0, match.start() - 20)
                context_end = min(len(text), match.end() + 50)
                context = text[context_start:context_end]
                
                found_risks.append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "description": rule["description"],
                    "suggestion": rule["suggestion"],
                    "law_reference": rule["law_reference"],
                    "risk_level": level,
                    "confidence": 0.9,  # 简化处理
                    "matched_text": context,
                    "position": match.start()
                })
        
        return found_risks
    
    def _calculate_risk_score(self, risk_stats: Dict) -> float:
        """计算风险评分"""
        score = 0
        score += risk_stats["high"] * 25
        score += risk_stats["medium"] * 10
        score += risk_stats["low"] * 3
        return min(100, score)
    
    def _generate_summary(self, risk_stats: Dict, contract_type: str) -> str:
        """生成审查摘要"""
        total = sum(risk_stats.values())
        
        if risk_stats["high"] > 0:
            return f"发现{risk_stats['high']}个高风险条款、{risk_stats['medium']}个中风险条款、{risk_stats['low']}个低风险条款，需要重点关注"
        elif risk_stats["medium"] > 0:
            return f"发现{risk_stats['medium']}个中风险条款、{risk_stats['low']}个低风险条款，建议修改"
        elif risk_stats["low"] > 0:
            return f"发现{risk_stats['low']}个低风险条款，整体风险可控"
        else:
            return "未发现明显风险条款，合同整体规范"
    
    def format_text(self, result: Dict) -> str:
        """格式化输出为文本"""
        lines = [
            f"📋 **合同智能审查报告**",
            f"",
            f"📄 合同类型: {result['contract_type']}",
            f"⏰ 审查时间: {result['reviewed_at']}",
            f"",
            f"{'='*30}",
            f"",
            f"📊 **风险评估**",
            f"",
            f"风险评分: {result['risk_score']:.1f}/100",
            f"合规评分: {result['compliance_score']:.1f}/100",
            f"风险等级: {result['risk_label']}",
            f"",
            f"🔢 **风险统计**",
            f"   🔴 高风险: {result['risk_stats']['high']}个",
            f"   🟡 中风险: {result['risk_stats']['medium']}个",
            f"   🟢 低风险: {result['risk_stats']['low']}个",
            f"",
            f"{'='*30}",
            f"",
            f"📝 **审查摘要**",
            f"",
            f"{result['summary']}",
        ]
        
        if result["risks"]:
            lines.extend([
                f"",
                f"{'='*30}",
                f"",
                f"⚠️ **风险条款详情**",
            ])
            
            level_labels = {"high": "🔴 高风险", "medium": "🟡 中风险", "low": "🟢 低风险"}
            
            current_level = None
            for risk in result["risks"][:10]:  # 最多显示10条
                if risk["risk_level"] != current_level:
                    current_level = risk["risk_level"]
                    lines.append(f"\n{level_labels.get(current_level, '')}")
                
                lines.extend([
                    f"",
                    f"**{risk['name']}**",
                    f"  📌 风险: {risk['description']}",
                    f"  💡 建议: {risk['suggestion']}",
                    f"  ⚖️ 法条: {risk['law_reference']}",
                    f"  📄 匹配: ...{risk['matched_text']}...",
                ])
        
        return '\n'.join(lines)
    
    def format_json(self, result: Dict) -> str:
        """格式化输出为JSON"""
        return json.dumps(result, ensure_ascii=False, indent=2)


def main():
    """主函数 - CLI测试"""
    print("=" * 50)
    print("🦞 合同智能审查引擎 v1.0")
    print("=" * 50)
    print()
    
    engine = ContractReviewEngine()
    
    # 测试合同文本
    sample_contract = """
    贷款合同
    
    甲方（贷款方）：XXX银行
    乙方（借款方）：YYY公司
    
    第一条 贷款金额
    乙方向甲方借款人民币1000万元整。
    
    第二条 贷款利率
    贷款利率按另行约定的方式执行。
    
    第三条 贷款期限
    贷款期限为1年，乙方应尽快归还贷款。
    
    第四条 担保条款
    乙方以其全部资产为本合同项下的贷款提供担保，包括但不限于一切债务。
    
    第五条 违约责任
    如乙方未按期还款，应向甲方支付相当于本金30%的违约金。
    
    第六条 争议解决
    本合同争议的管辖法院另行约定。
    
    第七条 保密条款
    本合同内容双方均应予以保密。
    
    本合同一式两份，甲乙双方各执一份。
    """
    
    print("📄 审查示例合同...")
    print()
    
    result = engine.review_contract(sample_contract)
    print(engine.format_text(result))
    print()
    
    # 尝试识别合同类型
    contract_type = engine.detect_contract_type(sample_contract)
    print(f"识别合同类型: {contract_type}")


if __name__ == "__main__":
    main()
