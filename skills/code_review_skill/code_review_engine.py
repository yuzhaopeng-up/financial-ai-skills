"""
Code Review Engine - 代码安全审查核心引擎
识别 SQL 注入、XSS、敏感信息泄露等安全漏洞，提供修复建议与质量评分
"""

import re
import json
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from enum import Enum


class Severity(Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class IssueCategory(Enum):
    SQL_INJECTION = "SQL_INJECTION"
    XSS = "XSS"
    SENSITIVE_INFO_LEAK = "SENSITIVE_INFO_LEAK"
    HARDCODED_SECRET = "HARDCODED_SECRET"
    COMMAND_INJECTION = "COMMAND_INJECTION"
    PATH_TRAVERSAL = "PATH_TRAVERSAL"
    INSECURE_DESERIALIZATION = "INSECURE_DESERIALIZATION"
    MISSING_INPUT_VALIDATION = "MISSING_INPUT_VALIDATION"
    DANGEROUS_FILE_PERMISSION = "DANGEROUS_FILE_PERMISSION"
    LOG_SENSITIVE_INFO = "LOG_SENSITIVE_INFO"
    INSECURE_RANDOM = "INSECURE_RANDOM"
    MISSING_HTTPS = "MISSING_HTTPS"
    CODE_QUALITY = "CODE_QUALITY"
    MAGIC_NUMBER = "MAGIC_NUMBER"
    POOR_NAMING = "POOR_NAMING"
    MISSING_COMMENT = "MISSING_COMMENT"


@dataclass
class CodeIssue:
    id: int
    severity: str
    category: str
    title: str
    location: str
    description: str
    code_snippet: str
    fix_suggestion: str


@dataclass
class ReviewSummary:
    language: str
    total_issues: int
    high: int
    medium: int
    low: int
    quality_score: float


@dataclass
class CodeReviewReport:
    summary: ReviewSummary
    issues: List[CodeIssue]
    raw_code: str = ""

    def to_dict(self) -> dict:
        return {
            "summary": asdict(self.summary),
            "issues": [asdict(i) for i in self.issues]
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


class CodeReviewEngine:
    """
    代码审查引擎
    输入：代码片段 / 语言 / 审查标准
    输出：代码审查报告（问题列表 + 严重程度）+ 安全漏洞识别 + 修复建议 + 代码质量评分
    """

    # SQL 注入检测模式
    SQL_INJECTION_PATTERNS = [
        (re.compile(r'(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\s+.*?["\'].*?["\'].*?[\+\{]', re.IGNORECASE), "字符串拼接 SQL"),
        (re.compile(r'["\'].*?%\s*\(.*?[\+\.]', re.IGNORECASE), "格式化字符串拼接 SQL"),
        (re.compile(r'["\'].*?\$\{.*?\}', re.IGNORECASE), "模板字符串拼接 SQL"),
        (re.compile(r'cursor\.execute\s*\(\s*["\'].*?%.*?["\'].*?%.*?\)', re.IGNORECASE), "SQL 占位符拼接"),
        (re.compile(r'query\s*\+.*?(?:username|user|name|password|pass|email|id)'), re.IGNORECASE),
        (re.compile(r'f[\'"].*?(?:SELECT|INSERT|UPDATE|DELETE).*?\{.*?\}', re.IGNORECASE), "f-string 拼接 SQL"),
        (re.compile(r'execute\s*\(\s*f[\'"]', re.IGNORECASE), "f-string 执行 SQL"),
    ]

    # 敏感信息检测模式
    SENSITIVE_PATTERNS = [
        (re.compile(r'password\s*=\s*["\'][^"\']{3,}["\']', re.IGNORECASE), "硬编码密码", Severity.HIGH),
        (re.compile(r'api[_\-]?key\s*=\s*["\'][a-zA-Z0-9_\-]{16,}["\']', re.IGNORECASE), "硬编码 API Key", Severity.HIGH),
        (re.compile(r'secret[_\-]?key\s*=\s*["\'][^"\']{8,}["\']', re.IGNORECASE), "硬编码 Secret Key", Severity.HIGH),
        (re.compile(r'private[_\-]?key\s*=\s*["\'][^"\']{20,}["\']', re.IGNORECASE), "硬编码私钥", Severity.HIGH),
        (re.compile(r'token\s*=\s*["\'][a-zA-Z0-9_\-\.]{16,}["\']', re.IGNORECASE), "硬编码 Token", Severity.HIGH),
        (re.compile(r'aws[_\-]?access[_\-]?key', re.IGNORECASE), "AWS 访问密钥", Severity.HIGH),
        (re.compile(r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----', re.IGNORECASE), "私钥文件", Severity.HIGH),
        (re.compile(r'["\']sk[-_][a-zA-Z0-9]{16,}["\']', re.IGNORECASE), "可能的服务密钥", Severity.HIGH),
        (re.compile(r'credit_card|creditcard|card_number|card_no', re.IGNORECASE), "信用卡信息", Severity.HIGH),
        (re.compile(r'ssn|social[_\-]?security', re.IGNORECASE), "身份证/社保号", Severity.HIGH),
        (re.compile(r'connection\s*\.\s*(username|password|user|pass)\s*=', re.IGNORECASE), "数据库连接硬编码凭证", Severity.HIGH),
        (re.compile(r'mysql\s*\.\s*connect\s*\(\s*user\s*=\s*["\']', re.IGNORECASE), "MySQL 连接硬编码用户", Severity.MEDIUM),
        (re.compile(r'mongo\s*://.*?:.*?@', re.IGNORECASE), "MongoDB URI 含凭证", Severity.MEDIUM),
        (re.compile(r'redis\s*://.*?:.*?@', re.IGNORECASE), "Redis URI 含凭证", Severity.MEDIUM),
    ]

    # 命令注入检测
    COMMAND_INJECTION_PATTERNS = [
        (re.compile(r'\beval\s*\(', re.IGNORECASE), "使用 eval", Severity.HIGH),
        (re.compile(r'\bexec\s*\(', re.IGNORECASE), "使用 exec", Severity.HIGH),
        (re.compile(r'os\.system\s*\(', re.IGNORECASE), "使用 os.system", Severity.HIGH),
        (re.compile(r'subprocess\.call\s*\(.*?shell\s*=\s*True', re.IGNORECASE), "subprocess shell=True", Severity.HIGH),
        (re.compile(r'subprocess\.Popen\s*\(.*?shell\s*=\s*True', re.IGNORECASE), "subprocess shell=True", Severity.HIGH),
        (re.compile(r'\bos\.popen\s*\(', re.IGNORECASE), "使用 os.popen", Severity.HIGH),
        (re.compile(r'\b__import__\s*\(', re.IGNORECASE), "动态导入", Severity.MEDIUM),
    ]

    # XSS 检测
    XSS_PATTERNS = [
        (re.compile(r'render_template_string|render_template.*?\(.*?\+', re.IGNORECASE), "模板字符串拼接", Severity.MEDIUM),
        (re.compile(r'document\.write\s*\(', re.IGNORECASE), "document.write XSS", Severity.HIGH),
        (re.compile(r'innerHTML\s*=\s*.*?\+', re.IGNORECASE), "innerHTML 拼接", Severity.MEDIUM),
        (re.compile(r'\.html\s*\(\s*.*?\+', re.IGNORECASE), "jQuery .html() 拼接", Severity.MEDIUM),
        (re.compile(r'Response\.write\s*\(.*?\+', re.IGNORECASE), "ASP Response 拼接", Severity.MEDIUM),
    ]

    # 路径遍历
    PATH_TRAVERSAL_PATTERNS = [
        (re.compile(r'open\s*\(\s*.*?\+.*?(?:path|file|filename|fn)', re.IGNORECASE), "动态路径拼接 open()", Severity.HIGH),
        (re.compile(r'\.\./', re.IGNORECASE), "目录遍历符 ../", Severity.MEDIUM),
        (re.compile(r'\.\.\\', re.IGNORECASE), "目录遍历符 ..\\", Severity.MEDIUM),
    ]

    # 输入验证缺失
    INPUT_VALIDATION_PATTERNS = [
        (re.compile(r'input\s*\(', re.IGNORECASE), "使用 input() 未做消毒处理", Severity.MEDIUM),
        (re.compile(r'request\.(args|form|values|get)\s*\[', re.IGNORECASE), "直接访问请求参数", Severity.MEDIUM),
    ]

    # 不安全反序列化
    DESERIALIZATION_PATTERNS = [
        (re.compile(r'pickle\.loads?\s*\(', re.IGNORECASE), "使用 pickle 反序列化", Severity.HIGH),
        (re.compile(r'yaml\.load\s*\(', re.IGNORECASE), "使用 yaml.load（不安全）", Severity.HIGH),
        (re.compile(r'marshal\.loads?\s*\(', re.IGNORECASE), "使用 marshal 反序列化", Severity.MEDIUM),
        (re.compile(r'shelve\s*\.open', re.IGNORECASE), "使用 shelve（不安全）", Severity.MEDIUM),
    ]

    # 日志敏感信息
    LOG_PATTERNS = [
        (re.compile(r'log\.(info|debug|warning|error)\s*\(.*?(?:password|passwd|pwd|secret|token|key)', re.IGNORECASE), "日志记录敏感信息", Severity.MEDIUM),
        (re.compile(r'print\s*\(.*?(?:password|passwd|pwd|secret|token|key)', re.IGNORECASE), "print 输出敏感信息", Severity.MEDIUM),
        (re.compile(r'logging\.(info|debug|warning|error)\s*\(.*?%.*?(?:password|passwd|pwd|secret|token)', re.IGNORECASE), "日志格式化敏感信息", Severity.MEDIUM),
    ]

    # 不安全随机数
    RANDOM_PATTERNS = [
        (re.compile(r'random\.(random|randint|choice)\s*\(', re.IGNORECASE), "使用 random 生成安全敏感数据", Severity.MEDIUM),
    ]

    # 代码质量
    CODE_QUALITY_PATTERNS = [
        (re.compile(r'#.*?TODO|#.*?FIXME|#.*?XXX', re.IGNORECASE), "未完成标记 TODO/FIXME", Severity.LOW),
        (re.compile(r'\b\d{4,}\b'), "魔法数字", Severity.LOW),
    ]

    def __init__(self):
        self.issue_counter = 0

    def review(
        self,
        code: str,
        language: str = "Python",
        standards: Optional[List[str]] = None
    ) -> CodeReviewReport:
        """
        审查代码并生成报告

        :param code: 代码片段
        :param language: 编程语言
        :param standards: 审查标准列表（默认全部启用）
        :return: CodeReviewReport
        """
        self.issue_counter = 0
        lines = code.split('\n')

        all_issues: List[CodeIssue] = []

        # SQL 注入检测
        if standards is None or "sql_injection" in standards or "all" in standards:
            all_issues.extend(self._check_sql_injection(code, lines))

        # 敏感信息泄露检测
        if standards is None or "hardcoded_secret" in standards or "all" in standards:
            all_issues.extend(self._check_sensitive_info(code, lines))

        # 命令注入检测
        if standards is None or "command_injection" in standards or "all" in standards:
            all_issues.extend(self._check_command_injection(code, lines))

        # XSS 检测
        if standards is None or "xss" in standards or "all" in standards:
            all_issues.extend(self._check_xss(code, lines))

        # 路径遍历
        if standards is None or "path_traversal" in standards or "all" in standards:
            all_issues.extend(self._check_path_traversal(code, lines))

        # 反序列化
        if standards is None or "deserialization" in standards or "all" in standards:
            all_issues.extend(self._check_deserialization(code, lines))

        # 输入验证
        if standards is None or "input_validation" in standards or "all" in standards:
            all_issues.extend(self._check_input_validation(code, lines))

        # 日志敏感信息
        if standards is None or "log_leak" in standards or "all" in standards:
            all_issues.extend(self._check_log_sensitive(code, lines))

        # 不安全随机数
        if standards is None or "insecure_random" in standards or "all" in standards:
            all_issues.extend(self._check_insecure_random(code, lines))

        # 代码质量
        if standards is None or "code_quality" in standards or "all" in standards:
            all_issues.extend(self._check_code_quality(code, lines))

        # 按 ID 排序
        all_issues.sort(key=lambda x: x.id)

        # 统计
        high = sum(1 for i in all_issues if i.severity == Severity.HIGH.value)
        medium = sum(1 for i in all_issues if i.severity == Severity.MEDIUM.value)
        low = sum(1 for i in all_issues if i.severity == Severity.LOW.value)

        # 质量评分
        score = self._calculate_quality_score(code, high, medium, low)

        summary = ReviewSummary(
            language=language,
            total_issues=len(all_issues),
            high=high,
            medium=medium,
            low=low,
            quality_score=score
        )

        return CodeReviewReport(
            summary=summary,
            issues=all_issues,
            raw_code=code
        )

    def _make_issue(
        self,
        severity: Severity,
        category: IssueCategory,
        title: str,
        location: str,
        description: str,
        code_snippet: str,
        fix_suggestion: str
    ) -> CodeIssue:
        self.issue_counter += 1
        return CodeIssue(
            id=self.issue_counter,
            severity=severity.value,
            category=category.value,
            title=title,
            location=location,
            description=description,
            code_snippet=code_snippet.strip(),
            fix_suggestion=fix_suggestion
        )

    def _find_line(self, code: str, pattern_text: str) -> str:
        """找到匹配行号"""
        for i, line in enumerate(code.split('\n'), 1):
            if re.search(pattern_text, line, re.IGNORECASE):
                return f"line {i}"
        return "unknown"

    def _get_snippet(self, code: str, pattern_text: str, context: int = 1) -> str:
        """获取匹配行及其上下文"""
        result_lines = []
        for i, line in enumerate(code.split('\n')):
            if re.search(pattern_text, line, re.IGNORECASE):
                result_lines.append(line.strip())
        return '\n'.join(result_lines[:3])

    def _check_sql_injection(self, code: str, lines: List[str]) -> List[CodeIssue]:
        issues = []
        seen_lines = set()
        for pattern, desc in self.SQL_INJECTION_PATTERNS:
            for match in pattern.finditer(code):
                matched_text = match.group()
                line_no = None
                snippet_lines = []
                for i, line in enumerate(code.split('\n'), 1):
                    if matched_text in line and i not in seen_lines:
                        line_no = i
                        seen_lines.add(i)
                        snippet_lines.append(line.strip())
                        break
                if line_no is None:
                    line_no = 1
                issues.append(self._make_issue(
                    severity=Severity.HIGH,
                    category=IssueCategory.SQL_INJECTION,
                    title=f"SQL 拼接查询 - {desc}",
                    location=f"line {line_no}",
                    description="用户输入直接拼接到 SQL 语句中，攻击者可通过构造特殊输入执行任意 SQL 命令",
                    code_snippet='\n'.join(snippet_lines),
                    fix_suggestion="使用参数化查询（Prepared Statement）：\n"
                                   "cursor.execute('SELECT * FROM users WHERE name = %s', (username,))\n"
                                   "或使用 ORM（如 SQLAlchemy）"
                ))
        return issues

    def _check_sensitive_info(self, code: str, lines: List[str]) -> List[CodeIssue]:
        issues = []
        seen_lines = set()
        for pattern, desc, severity in self.SENSITIVE_PATTERNS:
            for match in pattern.finditer(code):
                line_text = match.group()
                # 找行号
                for i, line in enumerate(code.split('\n'), 1):
                    if line_text in line and i not in seen_lines:
                        seen_lines.add(i)
                        issues.append(self._make_issue(
                            severity=severity,
                            category=IssueCategory.HARDCODED_SECRET if severity == Severity.HIGH else IssueCategory.SENSITIVE_INFO_LEAK,
                            title=f"敏感信息泄露 - {desc}",
                            location=f"line {i}",
                            description=f"代码中发现 {desc}，硬编码在源码中存在极高泄露风险",
                            code_snippet=line.strip()[:200],
                            fix_suggestion=f"将 {desc} 移至环境变量或安全配置中心：\n"
                                           f"import os\n"
                                           f"{desc.split()[0].lower()} = os.environ.get('{desc.split()[0].upper()}_KEY')"
                        ))
                        break
        return issues

    def _check_command_injection(self, code: str, lines: List[str]) -> List[CodeIssue]:
        issues = []
        for pattern, desc in self.COMMAND_INJECTION_PATTERNS:
            if pattern.search(code):
                loc = self._find_line(code, desc)
                snippet = self._get_snippet(code, desc)
                issues.append(self._make_issue(
                    severity=Severity.HIGH,
                    category=IssueCategory.COMMAND_INJECTION,
                    title=f"命令注入风险 - {desc}",
                    location=loc,
                    description="动态执行命令，攻击者可注入恶意命令执行任意操作",
                    code_snippet=snippet,
                    fix_suggestion="避免动态执行，使用子进程参数列表传递命令：\n"
                                   "subprocess.run(['ls', '-la'], shell=False)"
                ))
        return issues

    def _check_xss(self, code: str, lines: List[str]) -> List[CodeIssue]:
        issues = []
        for pattern, desc in self.XSS_PATTERNS:
            if pattern.search(code):
                loc = self._find_line(code, desc)
                snippet = self._get_snippet(code, desc)
                issues.append(self._make_issue(
                    severity=Severity.MEDIUM,
                    category=IssueCategory.XSS,
                    title=f"XSS 风险 - {desc}",
                    location=loc,
                    description="未经过滤的用户输入直接输出到页面，可导致跨站脚本攻击",
                    code_snippet=snippet,
                    fix_suggestion="对用户输入进行 HTML 转义，使用模板引擎的自动转义功能"
                ))
        return issues

    def _check_path_traversal(self, code: str, lines: List[str]) -> List[CodeIssue]:
        issues = []
        for pattern, desc in self.PATH_TRAVERSAL_PATTERNS:
            if pattern.search(code):
                loc = self._find_line(code, desc)
                snippet = self._get_snippet(code, desc)
                issues.append(self._make_issue(
                    severity=Severity.HIGH if "open" in desc else Severity.MEDIUM,
                    category=IssueCategory.PATH_TRAVERSAL,
                    title=f"路径遍历风险 - {desc}",
                    location=loc,
                    description="动态拼接文件路径，攻击者可利用 ../ 访问任意文件",
                    code_snippet=snippet,
                    fix_suggestion="使用 os.path.realpath() 验证路径，或使用 pathlib 安全方法"
                ))
        return issues

    def _check_deserialization(self, code: str, lines: List[str]) -> List[CodeIssue]:
        issues = []
        for pattern, desc in self.DESERIALIZATION_PATTERNS:
            if pattern.search(code):
                loc = self._find_line(code, desc)
                snippet = self._get_snippet(code, desc)
                issues.append(self._make_issue(
                    severity=Severity.HIGH,
                    category=IssueCategory.INSECURE_DESERIALIZATION,
                    title=f"不安全反序列化 - {desc}",
                    location=loc,
                    description="不安全的反序列化可导致远程代码执行",
                    code_snippet=snippet,
                    fix_suggestion="使用 json.loads() 代替 pickle/yaml，或使用安全配置 yaml.safe_load()"
                ))
        return issues

    def _check_input_validation(self, code: str, lines: List[str]) -> List[CodeIssue]:
        issues = []
        for pattern, desc in self.INPUT_VALIDATION_PATTERNS:
            if pattern.search(code):
                loc = self._find_line(code, desc)
                snippet = self._get_snippet(code, desc)
                issues.append(self._make_issue(
                    severity=Severity.MEDIUM,
                    category=IssueCategory.MISSING_INPUT_VALIDATION,
                    title=f"输入验证缺失 - {desc}",
                    location=loc,
                    description="用户输入未做充分验证和消毒处理",
                    code_snippet=snippet,
                    fix_suggestion="添加输入验证：类型检查、长度限制、白名单验证"
                ))
        return issues

    def _check_log_sensitive(self, code: str, lines: List[str]) -> List[CodeIssue]:
        issues = []
        for pattern, desc in self.LOG_PATTERNS:
            if pattern.search(code):
                loc = self._find_line(code, desc)
                snippet = self._get_snippet(code, desc)
                issues.append(self._make_issue(
                    severity=Severity.MEDIUM,
                    category=IssueCategory.LOG_SENSITIVE_INFO,
                    title=f"日志敏感信息 - {desc}",
                    location=loc,
                    description="敏感信息记录到日志，存在信息泄露风险",
                    code_snippet=snippet,
                    fix_suggestion="日志中脱敏处理：password=os.environ.get('PWD') if logger.isEnabledFor(logging.DEBUG) else '***'"
                ))
        return issues

    def _check_insecure_random(self, code: str, lines: List[str]) -> List[CodeIssue]:
        issues = []
        for pattern, desc in self.RANDOM_PATTERNS:
            if pattern.search(code):
                loc = self._find_line(code, desc)
                snippet = self._get_snippet(code, desc)
                issues.append(self._make_issue(
                    severity=Severity.MEDIUM,
                    category=IssueCategory.INSECURE_RANDOM,
                    title=f"不安全随机数 - {desc}",
                    location=loc,
                    description="random 模块不适合生成安全敏感数据（如密码 Token、加密密钥）",
                    code_snippet=snippet,
                    fix_suggestion="使用 secrets 模块或 os.urandom():\n"
                                   "import secrets\n"
                                   "token = secrets.token_hex(16)"
                ))
        return issues

    def _check_code_quality(self, code: str, lines: List[str]) -> List[CodeIssue]:
        issues = []
        for pattern, desc in self.CODE_QUALITY_PATTERNS:
            if pattern.search(code):
                loc = self._find_line(code, desc)
                snippet = self._get_snippet(code, desc)
                issues.append(self._make_issue(
                    severity=Severity.LOW,
                    category=IssueCategory.CODE_QUALITY,
                    title=f"代码质量 - {desc}",
                    location=loc,
                    description="代码可维护性问题",
                    code_snippet=snippet,
                    fix_suggestion="定义常量替代魔法数字，添加 TODO 注释跟踪未完成项"
                ))
        return issues

    def _calculate_quality_score(self, code: str, high: int, medium: int, low: int) -> float:
        """计算代码质量评分（10分制）"""
        base_score = 10.0
        # 扣分规则
        deductions = {
            Severity.HIGH.value: 2.5,
            Severity.MEDIUM.value: 1.0,
            Severity.LOW.value: 0.3,
        }
        total_deduction = high * deductions[Severity.HIGH.value] + \
                          medium * deductions[Severity.MEDIUM.value] + \
                          low * deductions[Severity.LOW.value]
        score = max(0.0, base_score - total_deduction)
        return round(score, 1)

    def parse_natural_language(self, description: str) -> dict:
        """
        解析自然语言描述为审查请求
        例如: "代码审查 Python 用户输入SQL拼接查询 未使用参数化"
        """
        language = "Python"
        standards = ["all"]

        desc_lower = description.lower()

        # 识别语言
        lang_map = {
            "python": "Python", "java": "Java", "javascript": "JavaScript",
            "js": "JavaScript", "sql": "SQL", "go": "Go", "c++": "C++",
            "php": "PHP", "ruby": "Ruby", "rust": "Rust"
        }
        for key, val in lang_map.items():
            if key in desc_lower:
                language = val
                break

        # 识别审查标准
        if "sql" in desc_lower or "注入" in desc_lower:
            standards = ["sql_injection"]
        elif "xss" in desc_lower or "脚本" in desc_lower:
            standards = ["xss"]
        elif "敏感" in desc_lower or "secret" in desc_lower or "密钥" in desc_lower:
            standards = ["hardcoded_secret"]
        elif "命令" in desc_lower or "command" in desc_lower:
            standards = ["command_injection"]
        elif "反序列化" in desc_lower:
            standards = ["deserialization"]
        else:
            standards = ["all"]

        return {"language": language, "standards": standards}

    def build_sample_code(self, description: str) -> str:
        """
        根据自然语言描述构建示例代码
        """
        desc_lower = description.lower()

        if "sql" in desc_lower and "拼接" in desc_lower:
            return '''# 不安全的 SQL 拼接查询
username = input("请输入用户名: ")
query = "SELECT * FROM users WHERE name = '" + username + "'"
cursor.execute(query)'''

        if "xss" in desc_lower:
            return '''# 不安全的 XSS 代码
user_input = request.args.get('name', '')
html = "<h1>Hello " + user_input + "</h1>"
return html'''

        if "hardcoded" in desc_lower or "密钥" in desc_lower:
            return '''# 硬编码密钥
api_key = "sk_test_1234567890abcdef"
password = "admin123"
db_pass = "MySecretPassword2024!"'''

        if "command" in desc_lower or "eval" in desc_lower:
            return '''# 命令注入风险
import os
cmd = input("请输入命令: ")
os.system(cmd)
eval(input("Enter Python expression: "))'''

        # 默认返回 SQL 注入示例
        return '''# SQL 注入示例 - 用户输入未使用参数化查询
user_input = input("Enter username: ")
sql = "SELECT * FROM users WHERE name = '" + user_input + "'"
cursor.execute(sql)'''
