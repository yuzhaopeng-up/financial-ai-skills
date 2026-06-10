"""
可疑交易报告引擎
SuspiciousReportEngine: 识别可疑交易特征并生成符合人民银行格式的报告
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Any


class SuspiciousReportEngine:
    """可疑交易报告生成引擎"""

    # 可疑特征阈值配置
    THRESHOLDS = {
        "fast_flow_minutes": 1440,      # 资金停留超过此分钟数视为非快进快出
        "分散账户数_threshold": 5,        # 分散转入账户数阈值
        "跨境笔数占比_threshold": 0.30,   # 跨境笔数占比阈值
        "单笔大额_threshold": 500000,    # 单笔大额交易阈值（元）
        "累计大额_threshold": 2000000,   # 累计大额交易阈值（元）
    }

    # 可疑特征关键词库
    SUSPICIOUS_PATTERNS = {
        "资金快进快出": [
            "快进快出", "即进即出", "当日转入转出", "T+0", "不留余额",
            "资金停留时间极短", "瞬间转移", "过账", "归集后立即转出"
        ],
        "分散归集": [
            "分散20个账户", "分散多个账户", "分散转入", "集中转出",
            "分散归集", "多处汇集", "资金归集", "账户分散", "多点流入"
        ],
        "虚拟货币关联": [
            "虚拟货币", "加密货币", "比特币", "BTC", "ETH", "USDT",
            "币安", "OKX", "火币", "交易所", "链上转账", "钱包转账"
        ],
        "虚假贸易背景": [
            "虚假贸易", "贸易背景不实", "合同虚假", "发票虚构",
            "贸易真实性存疑", "无实际货物", "虚构交易背景"
        ],
        "跨境资金异常": [
            "跨境资金", "境外汇款", "离岸账户", "跨境转账", "外汇异常",
            "资金跨境", "海外账户", "跨境汇入汇出"
        ],
    }

    def __init__(self, thresholds: Optional[Dict[str, Any]] = None):
        """初始化引擎，可选择性覆盖阈值"""
        if thresholds:
            self.THRESHOLDS.update(thresholds)

    def analyze(self, input_text: str) -> Dict[str, Any]:
        """
        分析输入文本，识别可疑交易特征

        Args:
            input_text: 自然语言描述的交易行为
                       例如："某客户 累计500万 分散20个账户 快进快出"

        Returns:
            包含以下键的字典:
                - report_type: str, 报告类型（大额/可疑）
                - suspicious_features: List[str], 可疑特征列表
                - feature_details: Dict, 各特征详细描述
                - report_content: str, 报告内容草稿
                - recommended_actions: List[str], 建议行动
                - confidence: float, 可信度 0-1
        """
        # 解析输入文本
        parsed = self._parse_input(input_text)

        # 识别可疑特征
        features = self._detect_features(input_text)

        # 判断报告类型
        report_type = self._determine_report_type(parsed, features)

        # 生成特征详情
        feature_details = self._generate_feature_details(parsed, features)

        # 生成报告内容
        report_content = self._generate_report_content(
            parsed, features, report_type, feature_details
        )

        # 生成建议行动
        recommended_actions = self._generate_actions(features, report_type)

        # 计算置信度
        confidence = min(0.5 + 0.1 * len(features), 1.0)

        return {
            "report_type": report_type,
            "suspicious_features": features,
            "feature_details": feature_details,
            "report_content": report_content,
            "recommended_actions": recommended_actions,
            "confidence": round(confidence, 2),
            "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "raw_input": input_text,
            "parsed_info": parsed,
        }

    def _parse_input(self, text: str) -> Dict[str, Any]:
        """解析自然语言输入"""
        result = {
            "customer_name": "某客户",
            "total_amount": 0,
            "account_count": 0,
            "transaction_type": [],
            "time_horizon": None,
            "raw_keywords": [],
        }

        # 提取金额
        amount_patterns = [
            (r"累计(\d+(?:\.\d+)?)\s*(?:万|亿|千)", "万"),
            (r"单笔(\d+(?:\.\d+)?)\s*(?:万|亿|千)", "万"),
            (r"(\d+(?:\.\d+)?)\s*(?:万|亿|千)", "万"),
            (r"(\d+(?:\.\d+)?)\s*元", "元"),
        ]

        for pattern, unit in amount_patterns:
            match = re.search(pattern, text)
            if match:
                amount = float(match.group(1))
                if unit == "万":
                    amount *= 10000
                elif unit == "亿":
                    amount *= 100000000
                elif unit == "千":
                    amount *= 1000
                result["total_amount"] = amount
                break

        # 提取账户数量
        account_patterns = [
            r"(\d+)\s*(?:个|多)?\s*账户",
            r"(\d+)\s*(?:个|多)?\s*账号",
        ]
        for pattern in account_patterns:
            match = re.search(pattern, text)
            if match:
                result["account_count"] = int(match.group(1))
                break

        # 提取交易类型关键词
        for category, keywords in self.SUSPICIOUS_PATTERNS.items():
            for keyword in keywords:
                if keyword in text:
                    if category not in result["transaction_type"]:
                        result["transaction_type"].append(category)
                    if keyword not in result["raw_keywords"]:
                        result["raw_keywords"].append(keyword)

        # 提取时间范围
        time_patterns = [
            (r"(\d+)\s*天内?", "day"),
            (r"(\d+)\s*周内?", "week"),
            (r"(\d+)\s*月内?", "month"),
            (r"近\s*(?:期|时|日)", "recent"),
        ]
        for pattern, unit in time_patterns:
            match = re.search(pattern, text)
            if match:
                result["time_horizon"] = f"{match.group(1)} {unit}"
                break

        return result

    def _detect_features(self, text: str) -> List[str]:
        """检测可疑特征"""
        detected = []

        for category, keywords in self.SUSPICIOUS_PATTERNS.items():
            for keyword in keywords:
                if keyword in text.lower():
                    if category not in detected:
                        detected.append(category)
                    break

        return detected

    def _determine_report_type(
        self, parsed: Dict[str, Any], features: List[str]
    ) -> str:
        """判断报告类型"""
        # 有可疑特征 → 可疑交易报告
        if features:
            return "可疑交易报告"
        # 无可疑特征但金额达标 → 大额交易报告
        if parsed["total_amount"] >= self.THRESHOLDS["累计大额_threshold"]:
            return "大额交易报告"
        if parsed["total_amount"] >= self.THRESHOLDS["单笔大额_threshold"]:
            return "大额交易报告"

        return "可疑交易报告"

    def _generate_feature_details(
        self, parsed: Dict[str, Any], features: List[str]
    ) -> Dict[str, Any]:
        """生成各特征的详细描述"""
        details = {}

        feature_descriptions = {
            "资金快进快出": {
                "description": "客户资金在账户停留时间极短，呈现即进即出特征，资金不留余额或仅保留最小可用余额。",
                "risk_level": "高",
                "typical_pattern": "资金当日转入当日转出，或在账户停留不超过24小时。",
            },
            "分散归集": {
                "description": "资金由多个不同账户分散转入，随后合并至单一账户或少数账户集中转出。",
                "risk_level": "高",
                "typical_pattern": f"资金分散转入{parsed.get('account_count', '多个')}个不同账户后归集转出。",
            },
            "虚拟货币关联": {
                "description": "交易对手或资金流向涉及虚拟货币交易平台、钱包地址或相关服务。",
                "risk_level": "极高",
                "typical_pattern": "资金流向涉及虚拟货币交易所或链上钱包，跨境特征明显。",
            },
            "虚假贸易背景": {
                "description": "交易金额、频率或交易对手与实际贸易主体经营情况明显不符。",
                "risk_level": "高",
                "typical_pattern": "大额资金流动缺乏真实贸易背景支撑，或合同发票等凭证存在异常。",
            },
            "跨境资金异常": {
                "description": "跨境资金流动频繁，且无法提供合理商业目的或外汇管理规定要求的证明材料。",
                "risk_level": "高",
                "typical_pattern": "跨境汇款笔次频繁，金额与客户经营规模明显不匹配。",
            },
        }

        for feature in features:
            if feature in feature_descriptions:
                details[feature] = feature_descriptions[feature]

        # 基于解析结果添加量化信息
        if parsed.get("total_amount"):
            details["金额情况"] = {
                "description": f"累计交易金额约 {parsed['total_amount']/10000:.1f} 万元",
                "risk_level": "极高" if parsed["total_amount"] >= 5000000 else "高",
            }

        if parsed.get("account_count"):
            details["账户情况"] = {
                "description": f"涉及分散账户数约 {parsed['account_count']} 个",
                "risk_level": "高",
            }

        return details

    def _generate_report_content(
        self,
        parsed: Dict[str, Any],
        features: List[str],
        report_type: str,
        feature_details: Dict[str, Any],
    ) -> str:
        """生成符合人民银行格式的报告内容草稿"""

        amount_str = ""
        if parsed.get("total_amount"):
            if parsed["total_amount"] >= 100000000:
                amount_str = f"{parsed['total_amount']/100000000:.2f} 亿元"
            elif parsed["total_amount"] >= 10000:
                amount_str = f"{parsed['total_amount']/10000:.1f} 万元"
            else:
                amount_str = f"{parsed['total_amount']:.0f} 元"

        report_id = f"STR-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        lines = [
            "=" * 60,
            "          可疑交易报告（草稿）",
            "          符合《金融机构大额交易和可疑交易报告管理办法》",
            "=" * 60,
            "",
            f"【报告编号】{report_id}",
            f"【报告类型】{report_type}",
            f"【报告日期】{datetime.now().strftime('%Y-%m-%d')}",
            f"【金融机构】[填写机构名称]",
            "",
            "-" * 60,
            "一、基本信息",
            "-" * 60,
            f"客户名称：{parsed.get('customer_name', '[待补充]')}",
            f"交易金额：{amount_str if amount_str else '[待补充]'}",
            f"涉及账户数：{parsed.get('account_count', '[待补充]')} 个",
            f"时间范围：{parsed.get('time_horizon', '近期')}",
            "",
            "-" * 60,
            "二、可疑交易特征",
            "-" * 60,
        ]

        for i, feature in enumerate(features, 1):
            detail = feature_details.get(feature, {})
            lines.append(f"{i}. 【{feature}】")
            lines.append(f"   风险等级：{detail.get('risk_level', '中')}")
            lines.append(f"   {detail.get('description', '[待补充]')}")
            lines.append(f"   典型特征：{detail.get('typical_pattern', '[待补充]')}")
            lines.append("")

        lines.extend([
            "-" * 60,
            "三、交易概况",
            "-" * 60,
            f"累计交易金额：{amount_str if amount_str else '[待补充]'}",
            f"可疑特征：{'、'.join(features) if features else '无明显可疑特征'}",
            f"涉及账户：{parsed.get('account_count', '[待补充]')} 个",
            "",
            "-" * 60,
            "四、详细描述",
            "-" * 60,
        ])

        if features:
            if "资金快进快出" in features:
                lines.append("客户账户呈现资金快进快出特征，资金在账户停留时间极短，")
                lines.append("呈现即进即出模式，资金不留余额或仅保留最小可用余额，")
                lines.append("资金流动频率与客户正常经营需求明显不符。")
                lines.append("")
            if "分散归集" in features:
                lines.append(f"资金由约 {parsed.get('account_count', '[待补充]')} 个不同账户分散转入，")
                lines.append("随后归集至少数账户集中转出，呈现明显的资金归集特征。")
                lines.append("")
        else:
            lines.append("[待补充详细交易描述]")

        lines.extend([
            "-" * 60,
            "五、建议采取的行动",
            "-" * 60,
        ])

        actions = self._generate_actions(features, report_type)
        for i, action in enumerate(actions, 1):
            lines.append(f"{i}. {action}")

        lines.extend([
            "",
            "-" * 60,
            "六、附件材料清单",
            "-" * 60,
            "□ 客户身份证件复印件",
            "□ 账户交易流水（近12个月）",
            "□ 客户尽职调查表",
            "□ 交易凭证/合同/发票（如有）",
            "□ 其他相关证明材料",
            "",
            "-" * 60,
            f"报告人：________________ 复核人：________________",
            f"日  期：{datetime.now().strftime('%Y-%m-%d')}                      ",
            "=" * 60,
        ])

        return "\n".join(lines)

    def _generate_actions(self, features: List[str], report_type: str) -> List[str]:
        """生成建议行动"""
        actions = []

        # 基础行动（所有报告都需要）
        base_actions = [
            "按照《金融机构大额交易和可疑交易报告管理办法》规定时限向中国反洗钱监测分析中心报送",
            "在业务系统中标注可疑交易标识，持续关注客户交易行为",
            "按照规定保存报告及相关资料至少5年",
        ]

        # 可疑交易额外行动
        if report_type == "可疑交易报告" or features:
            suspicious_actions = [
                "对客户进行加强型尽职调查（EDD），进一步核实交易背景和目的",
                "必要时联系客户获取补充说明材料",
                "如确认涉嫌洗钱或其他犯罪行为，及时向当地公安机关报案",
                "定期回顾客户风险等级，必要时采取限制交易措施",
            ]
            actions.extend(suspicious_actions)

        # 基于特定特征的行动
        if "虚拟货币关联" in features:
            actions.insert(0, "【高优先级】立即排查资金是否涉及虚拟货币交易平台，必要时限制账户非柜面交易")

        if "分散归集" in features:
            actions.insert(0, "【高优先级】核实各分散账户与客户关系，排查是否存在分拆交易行为")

        if "跨境资金异常" in features:
            actions.insert(0, "【高优先级】核查外汇管理规定执行情况，必要时联系外汇管理局")

        # 去重并保持顺序
        seen = set()
        unique_actions = []
        for a in actions:
            if a not in seen:
                seen.add(a)
                unique_actions.append(a)

        return base_actions + unique_actions

    def to_json(self, analysis_result: Dict[str, Any]) -> str:
        """将分析结果转换为JSON格式"""
        return json.dumps(analysis_result, ensure_ascii=False, indent=2)

    def to_wecom_card(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """转换为企微消息卡片格式"""
        result = analysis_result
        features_str = "、".join(result["suspicious_features"]) if result["suspicious_features"] else "无"

        card = {
            "msgtype": "interactive",
            "card": {
                "header": {
                    "title": f"🚨 {result['report_type']} - {result['analyzed_at'][:10]}",
                    "color": "red" if result["report_type"] == "可疑交易报告" else "warning",
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "content": f"**客户**：{result['parsed_info'].get('customer_name', '某客户')}",
                            "tag": "lark_md",
                        },
                    },
                    {
                        "tag": "div",
                        "text": {
                            "content": f"**交易金额**：{result['parsed_info'].get('total_amount', 0)/10000:.1f} 万元",
                            "tag": "lark_md",
                        },
                    },
                    {
                        "tag": "div",
                        "text": {
                            "content": f"**可疑特征**：{features_str}",
                            "tag": "lark_md",
                        },
                    },
                    {
                        "tag": "div",
                        "text": {
                            "content": f"**置信度**：{result['confidence']*100:.0f}%",
                            "tag": "lark_md",
                        },
                    },
                    {
                        "tag": "hr",
                    },
                    {
                        "tag": "div",
                        "text": {
                            "content": "**建议行动**：\n" + "\n".join(
                                f"{i+1}. {a}" for i, a in enumerate(result["recommended_actions"][:3])
                            ),
                            "tag": "lark_md",
                        },
                    },
                    {
                        "tag": "note",
                        "elements": [
                            {"tag": "plain_text", "content": f"报告编号：STR-{result['analyzed_at'].replace('-', '').replace(':', '').replace(' ', '')}"},
                        ],
                    },
                ],
            },
        }
        return card


if __name__ == "__main__":
    # 简单测试
    engine = SuspiciousReportEngine()
    result = engine.analyze("某客户 累计500万 分散20个账户 快进快出")
    print(result["report_content"])
