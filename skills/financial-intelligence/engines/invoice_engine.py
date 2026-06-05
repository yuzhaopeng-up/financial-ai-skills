# -*- coding: utf-8 -*-
"""
发票查验引擎 v1.0

核心能力:
- 发票信息OCR识别
- 发票真伪查验
- 合规性审查
- 重复报销检测

协同: KimiClaw (OCR+代码实现) / ArkClaw (合规分析)
"""

import re
import json
from typing import Dict, Any, Optional, List
from datetime import datetime


class InvoiceEngine:
    """发票查验引擎"""
    
    # 发票类型映射
    INVOICE_TYPES = {
        "01": "增值税专用发票",
        "04": "增值税普通发票",
        "10": "增值税电子普通发票",
        "11": "增值税电子专用发票",
        "14": "增值税普通发票(卷式)",
        "15": "二手车销售统一发票",
        "20": "机动车销售统一发票",
    }
    
    # 模拟查验数据库（演示用）
    MOCK_DB = {
        "011001900111-12345678": {
            "status": "valid",
            "invoice_type": "04",
            "seller_name": "北京XX科技有限公司",
            "seller_tax_no": "91110108MA00XXXXXXXX",
            "buyer_name": "XX股份有限公司",
            "buyer_tax_no": "91310000XXXXXXXXXX",
            "amount": 12580.00,
            "tax_amount": 755.66,
            "total_amount": 13335.66,
            "date": "2026-04-15",
            "items": [
                {"name": "技术服务费", "amount": 8000.00, "tax": 480.00},
                {"name": "咨询服务费", "amount": 4580.00, "tax": 275.66},
            ],
            "verify_source": "国家税务总局全国增值税发票查验平台",
        },
        "011001900111-87654321": {
            "status": "invalid",
            "reason": "发票号码不存在",
            "verify_source": "国家税务总局全国增值税发票查验平台",
        }
    }
    
    def __init__(self):
        self.engine_name = "InvoiceEngine"
        self.version = "1.0.0"
    
    def verify(
        self,
        invoice_code: Optional[str] = None,
        invoice_no: Optional[str] = None,
        invoice_text: Optional[str] = None,
        image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        发票查验主入口
        
        Args:
            invoice_code: 发票代码
            invoice_no: 发票号码
            invoice_text: 发票文本内容（OCR结果）
            image_url: 发票图片URL
            
        Returns:
            查验结果字典
        """
        start_time = datetime.now()
        
        # 1. 参数提取
        if not invoice_code or not invoice_no:
            extracted = self._extract_from_text(invoice_text or "")
            invoice_code = invoice_code or extracted.get("code")
            invoice_no = invoice_no or extracted.get("no")
        
        if not invoice_code or not invoice_no:
            return self._error_result("请提供发票代码和号码，或上传发票图片")
        
        # 2. 格式校验
        validation = self._validate_format(invoice_code, invoice_no)
        if not validation["valid"]:
            return self._error_result(validation["message"])
        
        # 3. 模拟查验（实际场景调用国家税务总局API）
        key = f"{invoice_code}-{invoice_no}"
        mock_result = self.MOCK_DB.get(key)
        
        if mock_result:
            result = self._build_result(invoice_code, invoice_no, mock_result)
        else:
            # 生成随机演示结果
            result = self._build_demo_result(invoice_code, invoice_no)
        
        # 4. 合规检查
        compliance = self._check_compliance(result)
        result["compliance"] = compliance
        
        # 5. 计算耗时
        result["latency_ms"] = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return result
    
    def batch_verify(self, invoices: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        批量发票查验
        
        Args:
            invoices: 发票列表 [{"code": "...", "no": "..."}, ...]
            
        Returns:
            批量查验结果
        """
        results = []
        valid_count = 0
        invalid_count = 0
        total_amount = 0.0
        
        for inv in invoices:
            result = self.verify(
                invoice_code=inv.get("code"),
                invoice_no=inv.get("no")
            )
            results.append(result)
            
            if result.get("status") == "valid":
                valid_count += 1
                total_amount += result.get("total_amount", 0)
            else:
                invalid_count += 1
        
        return {
            "success": True,
            "scenario": "invoice_batch",
            "summary": f"查验完成: {valid_count}张有效, {invalid_count}张异常",
            "total_count": len(invoices),
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "total_amount": total_amount,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _extract_from_text(self, text: str) -> Dict[str, str]:
        """从文本中提取发票代码和号码"""
        result = {"code": "", "no": ""}
        
        # 发票代码: 10或12位数字
        code_match = re.search(r'发票代码[：:]\s*(\d{10,12})', text)
        if code_match:
            result["code"] = code_match.group(1)
        
        # 发票号码: 8位数字
        no_match = re.search(r'发票号码[：:]\s*(\d{8,20})', text)
        if no_match:
            result["no"] = no_match.group(1)
        
        return result
    
    def _validate_format(self, code: str, no: str) -> Dict[str, Any]:
        """校验发票格式"""
        if not re.match(r'^\d{10,12}$', code):
            return {"valid": False, "message": f"发票代码格式错误: {code} (应为10-12位数字)"}
        
        if not re.match(r'^\d{8,20}$', no):
            return {"valid": False, "message": f"发票号码格式错误: {no} (应为8-20位数字)"}
        
        return {"valid": True, "message": ""}
    
    def _check_compliance(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """合规性检查"""
        flags = []
        score = 100
        
        if result.get("status") != "valid":
            flags.append({"level": "error", "msg": "发票查验未通过"})
            score = 0
            return {"score": score, "flags": flags, "status": "不合规"}
        
        # 检查金额合理性
        amount = result.get("total_amount", 0)
        if amount > 100000:
            flags.append({"level": "warning", "msg": "单张发票金额超过10万元，需额外审批"})
            score -= 10
        
        # 检查开票日期
        inv_date = result.get("date", "")
        if inv_date:
            try:
                inv_dt = datetime.strptime(inv_date, "%Y-%m-%d")
                days_ago = (datetime.now() - inv_dt).days
                if days_ago > 365:
                    flags.append({"level": "warning", "msg": f"发票开具已超1年（{days_ago}天前）"})
                    score -= 15
                elif days_ago > 180:
                    flags.append({"level": "info", "msg": f"发票开具已超半年（{days_ago}天前）"})
                    score -= 5
            except:
                pass
        
        # 检查重复（模拟）
        if result.get("invoice_no", "").endswith("88"):
            flags.append({"level": "warning", "msg": "疑似重复报销，请核对"})
            score -= 20
        
        status = "合规" if score >= 90 else "需关注" if score >= 70 else "不合规"
        
        return {"score": score, "flags": flags, "status": status}
    
    def _build_result(self, code: str, no: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """构建查验结果"""
        inv_type = self.INVOICE_TYPES.get(data.get("invoice_type", ""), "未知类型")
        
        return {
            "success": True,
            "scenario": "invoice",
            "status": data.get("status"),
            "invoice_code": code,
            "invoice_no": no,
            "invoice_type": inv_type,
            "seller_name": data.get("seller_name", ""),
            "seller_tax_no": data.get("seller_tax_no", ""),
            "buyer_name": data.get("buyer_name", ""),
            "buyer_tax_no": data.get("buyer_tax_no", ""),
            "amount": data.get("amount", 0),
            "tax_amount": data.get("tax_amount", 0),
            "total_amount": data.get("total_amount", 0),
            "date": data.get("date", ""),
            "items": data.get("items", []),
            "verify_source": data.get("verify_source", ""),
            "timestamp": datetime.now().isoformat()
        }
    
    def _build_demo_result(self, code: str, no: str) -> Dict[str, Any]:
        """生成演示用查验结果"""
        # 根据号码最后一位决定结果
        last_digit = int(no[-1]) if no[-1].isdigit() else 0
        
        if last_digit in [0, 2, 4, 6, 8]:
            # 偶数位 = 有效发票
            amount = 5000 + (last_digit * 1234)
            tax = round(amount * 0.06, 2)
            total = amount + tax
            
            return {
                "success": True,
                "scenario": "invoice",
                "status": "valid",
                "invoice_code": code,
                "invoice_no": no,
                "invoice_type": "增值税普通发票",
                "seller_name": f"演示供应商{last_digit}有限公司",
                "seller_tax_no": f"91110108MA00{code[-6:]}XX",
                "buyer_name": "XX股份有限公司",
                "buyer_tax_no": "91310000XXXXXXXXXX",
                "amount": amount,
                "tax_amount": tax,
                "total_amount": total,
                "date": "2026-04-15",
                "items": [
                    {"name": "技术服务费", "amount": amount * 0.6, "tax": round(amount * 0.6 * 0.06, 2)},
                    {"name": "咨询服务费", "amount": amount * 0.4, "tax": round(amount * 0.4 * 0.06, 2)},
                ],
                "verify_source": "国家税务总局全国增值税发票查验平台（演示数据）",
                "timestamp": datetime.now().isoformat()
            }
        else:
            # 奇数位 = 异常发票
            reasons = [
                "发票号码不存在",
                "发票代码与号码不匹配",
                "发票已作废",
                "查询次数超限，请明日再试",
                "开票日期超过5年，无法查验"
            ]
            return {
                "success": True,
                "scenario": "invoice",
                "status": "invalid",
                "invoice_code": code,
                "invoice_no": no,
                "reason": reasons[last_digit % len(reasons)],
                "verify_source": "国家税务总局全国增值税发票查验平台（演示数据）",
                "timestamp": datetime.now().isoformat()
            }
    
    def _error_result(self, message: str) -> Dict[str, Any]:
        """构建错误结果"""
        return {
            "success": False,
            "scenario": "invoice",
            "status": "error",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
