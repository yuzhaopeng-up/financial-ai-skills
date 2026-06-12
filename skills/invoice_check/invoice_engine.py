# -*- coding: utf-8 -*-
"""
发票查验引擎 (Invoice Check Engine)
实现发票真伪鉴别、风险识别和税务合规性分析
"""

import re
import hashlib
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class InvoiceCheckEngine:
    """
    发票查验引擎
    输入发票信息，返回查验结果、异常提示、增值税抵扣建议、税务风险点、备查记录
    """

    # 增值税税率标准（2024年）
    STANDARD_TAX_RATES = {
        "13%": ["货物", "加工修理修配", "有形动产租赁"],
        "9%": ["农产品", "交通运输", "邮政", "基础电信", "建筑", "不动产租赁", "土地使用权转让"],
        "6%": ["现代服务", "信息技术", "鉴证咨询", "文化创意", "物流辅助", "商务辅助"],
        "0%": ["出口货物", "跨境应税服务"],
    }

    # 敏感行业关键词
    SENSITIVE_INDUSTRIES = ["投资", "咨询", "管理", "科技", "电子", "商贸", "贸易"]

    def __init__(self, api_mode: bool = False):
        """
        初始化引擎

        Args:
            api_mode: API调用模式（避免stdout污染）
        """
        self.api_mode = api_mode
        self._invoice_db = self._build_mock_invoice_db()
        self._history_records: List[Dict] = []

    def _build_mock_invoice_db(self) -> Dict[str, Dict]:
        """
        构建模拟发票数据库
        实际项目中应对接税务局增值税发票查验平台API
        """
        return {
            "144031900360|44450123": {
                "status": "真票",
                "billing_date": "2024-03-01",
                "amount": 100000.00,
                "tax_rate": "6%",
                "seller": "深圳市XX科技有限公司",
                "seller_tax_id": "91440300MA5xxxxx",
                "buyer": "深圳XX企业有限公司",
                "buyer_tax_id": "91440300MA5yyyyy",
                "products": "现代服务费",
            },
            "144031900360|44450124": {
                "status": "作废发票",
                "billing_date": "2024-03-01",
                "amount": 50000.00,
                "tax_rate": "13%",
                "seller": "广州市XX商贸公司",
                "seller_tax_id": "91440100MA5zzzzz",
                "buyer": "深圳XX企业有限公司",
                "buyer_tax_id": "91440300MA5yyyyy",
                "products": "电子元器件",
            },
            "144031900360|44450125": {
                "status": "失控发票",
                "billing_date": "2023-06-15",
                "amount": 200000.00,
                "tax_rate": "13%",
                "seller": "东莞市XX贸易商行",
                "seller_tax_id": "91441900MA5wwwww",
                "buyer": "深圳XX企业有限公司",
                "buyer_tax_id": "91440300MA5yyyyy",
                "products": "办公用品",
            },
        }

    def _hash_key(self, invoice_code: str, invoice_number: str) -> str:
        """生成发票数据库查询键"""
        return f"{invoice_code}|{invoice_number}"

    def _check_amount_anomaly(self, amount: float, db_amount: Optional[float]) -> Optional[Dict]:
        """检查金额是否异常"""
        if db_amount is None:
            return None
        diff_ratio = abs(amount - db_amount) / db_amount if db_amount > 0 else 0
        if diff_ratio > 0.01:  # 超过1%差异
            return {
                "type": "金额不符",
                "severity": "high",
                "description": f"票面金额({amount:.2f}元)与税务局记录({db_amount:.2f}元)不一致，差异率{diff_ratio*100:.2f}%",
                "suggestion": "核实发票票面金额，确认是否为开票错误或恶意篡改，建议联系销售方核实"
            }
        return None

    def _check_tax_rate_anomaly(
        self, tax_rate: str, product_type: str
    ) -> Optional[Dict]:
        """检查税率是否异常"""
        valid_categories = self.STANDARD_TAX_RATES.get(tax_rate, [])
        if valid_categories and not any(cat in product_type for cat in valid_categories):
            return {
                "type": "税率异常",
                "severity": "medium",
                "description": f"发票适用税率{tax_rate}与货物/服务类型({product_type})不匹配",
                "suggestion": f"核实业务实质，确认{tax_rate}税率是否适用于该业务类型"
            }
        return None

    def _check_sensitive_counterparty(
        self,
        buyer_name: str,
        seller_name: str,
        buyer_tax_id: str,
        seller_tax_id: str,
    ) -> List[Dict]:
        """
        检查敏感交易对手
        规则：
        1. 法人相同
        2. 注册地址相近
        3. 短期内大量交易
        """
        anomalies = []

        # 模拟：注册地址相近检测（简化版，实际应对接工商数据）
        buyer_region = buyer_name[:2] if buyer_name else ""
        seller_region = seller_name[:2] if seller_name else ""

        # 模拟：短期大量交易检测
        recent_count = sum(
            1 for r in self._history_records
            if r.get("seller_name") == seller_name
            and r.get("timestamp")
            and (datetime.now() - datetime.fromisoformat(r["timestamp"])).days < 30
        )

        if buyer_region and seller_region and buyer_region == seller_region:
            anomalies.append({
                "type": "敏感交易对手-注册地址相近",
                "severity": "medium",
                "description": f"购买方({buyer_name})与销售方({seller_name})注册地址区域相同",
                "suggestion": "核查双方是否存在关联关系，确认交易是否具有合理商业实质"
            })

        if recent_count >= 3:
            anomalies.append({
                "type": "敏感交易对手-短期内大量交易",
                "severity": "high",
                "description": f"近30日内与销售方({seller_name})已发生{recent_count}次交易",
                "suggestion": "核查多次交易的真实性，评估是否存在虚开或循环开票风险"
            })

        # 模拟：税号相近检测
        if buyer_tax_id and seller_tax_id and len(buyer_tax_id) >= 13 and len(seller_tax_id) >= 13:
            # 前6位是地区码
            if buyer_tax_id[3:8] == seller_tax_id[3:8]:
                anomalies.append({
                    "type": "敏感交易对手-税号关联",
                    "severity": "medium",
                    "description": "购买方与销售方税号中地区编码高度相似",
                    "suggestion": "核实双方是否存在同一控制人，避免税务风险"
                })

        return anomalies

    def _check_certification_period(
        self, billing_date_str: str, invoice_type: str = "专用发票"
    ) -> Optional[Dict]:
        """检查是否超过认证期限"""
        try:
            billing_date = datetime.strptime(billing_date_str, "%Y-%m-%d")
            days_since_billing = (datetime.now() - billing_date).days

            # 2020年3月1日后，勾选期限为360天；之前是90天
            cutoff_date = datetime(2020, 3, 1)
            if billing_date < cutoff_date:
                max_days = 90
            else:
                max_days = 360

            if days_since_billing > max_days:
                return {
                    "type": "超过认证期限",
                    "severity": "high",
                    "description": f"发票开票日期{billing_date_str}，距今{days_since_billing}天，已超过{max_days}天认证期限",
                    "suggestion": "该发票已不可抵扣进项税额，请确认是否已完成认证或考虑换开合规发票"
                }
        except Exception:
            pass
        return None

    def _check_duplicate(
        self, invoice_code: str, invoice_number: str
    ) -> Optional[Dict]:
        """检查是否重复报销"""
        key = self._hash_key(invoice_code, invoice_number)
        for record in self._history_records:
            if record.get("key") == key:
                return {
                    "type": "重复报销",
                    "severity": "high",
                    "description": f"发票代码{invoice_code}号码{invoice_number}在{record.get('timestamp','历史记录')}已存在",
                    "suggestion": "核实是否为重复报销，如已报销应追回或冲销"
                }
        return None

    def _suggest_vat_deduction(
        self, status: str, amount: float, tax_rate: str, anomalies: List[Dict]
    ) -> Dict:
        """给出增值税抵扣建议"""
        high_risk_anomalies = [a for a in anomalies if a.get("severity") == "high"]

        if status in ["假票", "失控发票", "作废发票"]:
            return {
                "can_deduct": False,
                "deduction_type": "不可抵扣",
                "reason": f"发票状态为【{status}】，按规定不得作为增值税扣税凭证"
            }
        elif status == "红字发票":
            return {
                "can_deduct": False,
                "deduction_type": "需核实原票",
                "reason": "该发票为红字发票，需核实对应蓝字发票是否已抵扣"
            }
        elif status == "超过认证期限":
            return {
                "can_deduct": False,
                "deduction_type": "已超期限",
                "reason": "发票已超过认证期限，进项税额不得抵扣"
            }
        elif high_risk_anomalies:
            risk_types = ", ".join([a["type"] for a in high_risk_anomalies])
            return {
                "can_deduct": False,
                "deduction_type": "暂不允许抵扣",
                "reason": f"存在高风险异常：{risk_types}，需核实后处理"
            }
        elif tax_rate in ["0%"]:
            return {
                "can_deduct": True,
                "deduction_type": "免税",
                "reason": f"适用税率{tax_rate}，属于免税项目，进项税额不得抵扣但可按规定处理"
            }
        else:
            tax_amount = amount / (1 + self._parse_tax_rate(tax_rate)) * self._parse_tax_rate(tax_rate)
            return {
                "can_deduct": True,
                "deduction_type": "正常抵扣",
                "reason": f"发票状态正常，可按规定进行进项税额抵扣，预计可抵扣税额约{tax_amount:.2f}元"
            }

    def _parse_tax_rate(self, tax_rate_str: str) -> float:
        """解析税率字符串为浮点数"""
        match = re.search(r"(\d+(?:\.\d+)?)", tax_rate_str)
        if match:
            return float(match.group(1)) / 100.0
        return 0.0

    def _generate_tax_risk_points(
        self, status: str, amount: float, seller_name: str, anomalies: List[Dict]
    ) -> List[Dict]:
        """生成税务风险点分析"""
        risk_points = []

        if status != "真票":
            risk_points.append({
                "point": f"发票状态异常：{status}",
                "risk_level": "high"
            })

        if amount > 100000:
            risk_points.append({
                "point": f"单笔发票金额较大（{amount:.2f}元），需重点核查交易真实性",
                "risk_level": "medium"
            })

        if any("敏感交易对手" in a["type"] for a in anomalies):
            risk_points.append({
                "point": "存在敏感交易对手特征，需评估关联交易转让定价风险",
                "risk_level": "high"
            })

        if not risk_points:
            risk_points.append({
                "point": "未发现明显税务风险点，建议持续关注",
                "risk_level": "low"
            })

        return risk_points

    def _generate_reference_records(
        self,
        invoice_code: str,
        invoice_number: str,
        billing_date: str,
        amount: float,
        status: str,
        seller_name: str,
    ) -> List[Dict]:
        """生成备查记录"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return [
            {
                "record_type": "查验记录",
                "content": f"查验发票代码{invoice_code}号码{invoice_number}，查验时间{timestamp}，查验结果：{status}",
                "timestamp": timestamp,
            },
            {
                "record_type": "票面信息",
                "content": f"开票日期{billing_date}，金额{amount:.2f}元，销售方{seller_name}",
                "timestamp": timestamp,
            },
        ]

    def check(
        self,
        invoice_code: str,
        invoice_number: str,
        billing_date: str,
        amount: float,
        buyer_name: str = "",
        seller_name: str = "",
        buyer_tax_id: str = "",
        seller_tax_id: str = "",
        product_desc: str = "",
    ) -> Dict[str, Any]:
        """
        核心查验方法

        Args:
            invoice_code: 发票代码
            invoice_number: 发票号码
            billing_date: 开票日期 (YYYY-MM-DD)
            amount: 金额（含税）
            buyer_name: 购买方名称
            seller_name: 销售方名称
            buyer_tax_id: 购买方税号
            seller_tax_id: 销售方税号
            product_desc: 货物或服务描述

        Returns:
            查验结果字典
        """
        key = self._hash_key(invoice_code, invoice_number)
        db_record = self._invoice_db.get(key)

        # 确定发票状态
        if db_record:
            status = db_record["status"]
            db_amount = db_record.get("amount")
            tax_rate = db_record.get("tax_rate", "6%")
        else:
            # 模拟：未知发票，概率生成假票
            status = random.choices(
                ["假票", "失控发票"],
                weights=[0.6, 0.4],
                k=1
            )[0]
            db_amount = None
            tax_rate = "13%"

        anomalies: List[Dict] = []

        # 1. 金额异常
        amt_anomaly = self._check_amount_anomaly(amount, db_amount)
        if amt_anomaly:
            anomalies.append(amt_anomaly)

        # 2. 税率异常
        if product_desc:
            tax_anomaly = self._check_tax_rate_anomaly(tax_rate, product_desc)
            if tax_anomaly:
                anomalies.append(tax_anomaly)

        # 3. 敏感交易对手
        if buyer_name and seller_name:
            sensitive_anomalies = self._check_sensitive_counterparty(
                buyer_name, seller_name, buyer_tax_id, seller_tax_id
            )
            anomalies.extend(sensitive_anomalies)

        # 4. 超过认证期限（仅专用发票）
        if "专用" in str(tax_rate) or amount > 0:
            period_anomaly = self._check_certification_period(billing_date)
            if period_anomaly:
                anomalies.append(period_anomaly)

        # 5. 重复报销
        dup_anomaly = self._check_duplicate(invoice_code, invoice_number)
        if dup_anomaly:
            anomalies.append(dup_anomaly)

        # 记录到历史（用于重复检测）
        self._history_records.append({
            "key": key,
            "seller_name": seller_name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        # 增值税抵扣建议
        vat_deduction = self._suggest_vat_deduction(status, amount, tax_rate, anomalies)

        # 税务风险点
        tax_risk_points = self._generate_tax_risk_points(
            status, amount, seller_name, anomalies
        )

        # 备查记录
        reference_records = self._generate_reference_records(
            invoice_code, invoice_number, billing_date, amount, status, seller_name
        )

        # 计算置信度
        if status == "真票" and not anomalies:
            confidence = 0.98
        elif status == "真票" and any(a["severity"] == "high" for a in anomalies):
            confidence = 0.50
        elif status == "假票":
            confidence = 0.95
        else:
            confidence = 0.75

        return {
            "invoice_code": invoice_code,
            "invoice_number": invoice_number,
            "status": status,
            "confidence": round(confidence, 4),
            "anomalies": anomalies,
            "vat_deduction": vat_deduction,
            "tax_risk_points": tax_risk_points,
            "reference_records": reference_records,
        }

    def check_from_text(self, text: str) -> Dict[str, Any]:
        """
        从自然语言文本解析并查验发票

        Args:
            text: 自然语言文本，如"发票查验 发票代码144031900360 号码44450123 开票日期2024-03-01 金额10万"

        Returns:
            查验结果字典
        """
        # 解析发票代码
        code_match = re.search(r"发票代码(\d+)", text)
        invoice_code = code_match.group(1) if code_match else ""

        # 解析发票号码
        num_match = re.search(r"号码(\d+)", text)
        invoice_number = num_match.group(1) if num_match else ""

        # 解析开票日期
        date_match = re.search(r"开票日期(\d{4}[-/]\d{2}[-/]\d{2})", text)
        billing_date = date_match.group(1).replace("/", "-") if date_match else ""

        # 解析金额
        amount_match = re.search(r"金额(\d+(?:\.\d+)?)\s*(万|元)?", text)
        if amount_match:
            amount_val = float(amount_match.group(1))
            unit = amount_match.group(2) or "元"
            amount = amount_val * 10000 if unit == "万" else amount_val
        else:
            amount = 0.0

        # 解析购买方/销售方
        buyer_match = re.search(r"购买方([^ ]{2,30})", text)
        seller_match = re.search(r"销售方([^ ]{2,30})", text)
        buyer_name = buyer_match.group(1) if buyer_match else ""
        seller_name = seller_match.group(1) if seller_match else ""

        return self.check(
            invoice_code=invoice_code,
            invoice_number=invoice_number,
            billing_date=billing_date,
            amount=amount,
            buyer_name=buyer_name,
            seller_name=seller_name,
        )


def main():
    """CLI测试入口"""
    import json, sys
    engine = InvoiceCheckEngine(api_mode=True)

    test_args = sys.argv[1:] if len(sys.argv) > 1 else [
        "发票查验 发票代码144031900360 号码44450123 开票日期2024-03-01 金额10万"
    ]

    if "generate" in test_args:
        # 去掉"generate"关键字，保留查询参数
        args = [a for a in test_args if a != "generate"]
    else:
        args = test_args

    text = " ".join(args) if args else ""
    result = engine.check_from_text(text)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
