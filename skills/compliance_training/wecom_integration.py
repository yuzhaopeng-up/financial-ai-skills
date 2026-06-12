"""
企微集成模块 - 合规培训

将合规培训内容通过企微消息卡片发送给相关人员。
"""

import json
from typing import Any, Dict, List, Optional


def build_training_card(
    job_type: str,
    topic: str,
    duration_minutes: int,
    outline: dict,
    content: dict,
    cases: list,
    quiz: list,
    evaluation: dict,
    quick_ref: dict,
) -> dict:
    """
    构建培训内容企微卡片

    Args:
        job_type: 岗位类型
        topic: 培训主题
        duration_minutes: 时长
        outline: 课件大纲
        content: 培训内容
        cases: 案例列表
        quiz: 测试题列表
        evaluation: 效果评估
        quick_ref: 速查卡

    Returns:
        dict: 企微卡片消息体
    """
    # 构建法规要点
    regulations_md = "**适用法规：**\n"
    for reg in content.get("regulations", [])[:3]:
        regulations_md += f"• {reg}\n"

    # 构建核心要点
    key_points_md = "**核心要点：**\n"
    for i, point in enumerate(content.get("key_points", [])[:4], 1):
        key_points_md += f"{i}. {point}\n"

    # 构建违规后果
    consequences_md = "**违规后果：**\n"
    for consequence in content.get("violation_consequences", [])[:3]:
        consequences_md += f"⚠️ {consequence}\n"

    # 构建案例摘要
    cases_md = "**典型案例：**\n"
    for case in cases[:2]:
        cases_md += f"📁 **{case.get('title', 'N/A')}**\n"
        cases_md += f"   违规：{case.get('violation', 'N/A')[:50]}...\n"
        cases_md += f"   处罚：{case.get('penalty', 'N/A')[:50]}...\n\n"

    # 构建测试题预览
    quiz_md = "**课后测试（共10题）：**\n"
    for q in quiz[:3]:
        quiz_md += f"{q['id']}. {q['question'][:40]}...\n"
    quiz_md += f"...\n**及格分数：{evaluation.get('passing_score', 70)}分**\n"

    # 构建速查卡
    quick_ref_md = f"**⚡ {quick_ref.get('title', '合规要点速查卡')}**\n\n"
    for rule in quick_ref.get("key_rules", [])[:3]:
        quick_ref_md += f"📌 {rule.get('rule', 'N/A')[:30]}...\n"
        quick_ref_md += f"   自查：{rule.get('check', 'N/A')}\n\n"

    card = {
        "msgtype": "interactive",
        "agentid": 0,  # 企微agent_id，需配置
        "interactive": {
            "tag": "markdown",
            "custom_size": "lg",
            "content": (
                f"## 📚 合规培训方案\n\n"
                f"**岗位：** {job_type} | **主题：** {topic} | **时长：** {duration_minutes}分钟\n\n"
                f"---\n\n"
                f"{regulations_md}\n\n"
                f"---\n\n"
                f"{key_points_md}\n\n"
                f"---\n\n"
                f"{consequences_md}\n\n"
                f"---\n\n"
                f"{cases_md}\n\n"
                f"---\n\n"
                f"{quiz_md}\n\n"
                f"---\n\n"
                f"{quick_ref_md}\n\n"
                f"---\n\n"
                f"📌 *完整培训方案请查看系统*\n"
            ),
        },
    }

    return card


def build_simple_card(
    title: str,
    content: str,
    action_text: str = "查看详情",
    action_url: str = "",
) -> dict:
    """
    构建简单的企微卡片（用于提醒或通知）

    Args:
        title: 卡片标题
        content: 卡片内容
        action_text: 按钮文本
        action_url: 按钮链接

    Returns:
        dict: 企微卡片消息体
    """
    card = {
        "msgtype": "interactive",
        "agentid": 0,
        "interactive": {
            "tag": "markdown",
            "custom_size": "lg",
            "content": f"## {title}\n\n{content}",
        },
    }

    if action_url:
        card["interactive"]["card"] = {
            "action"] = {
                "text": action_text,
                "url": action_url,
            }
        }

    return card


def send_training_notification(
    webhook_url: str,
    job_type: str,
    topic: str,
    duration_minutes: int,
    outline: dict,
    content: dict,
    cases: list,
    quiz: list,
    evaluation: dict,
    quick_ref: dict,
) -> dict:
    """
    通过企微webhook发送培训内容

    Args:
        webhook_url: 企微webhook地址
        其他参数同 build_training_card

    Returns:
        dict: 发送结果
    """
    import urllib.request
    import urllib.error

    card = build_training_card(
        job_type=job_type,
        topic=topic,
        duration_minutes=duration_minutes,
        outline=outline,
        content=content,
        cases=cases,
        quiz=quiz,
        evaluation=evaluation,
        quick_ref=quick_ref,
    )

    data = json.dumps(card).encode("utf-8")
    headers = {"Content-Type": "application/json"}

    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))
            return {"status": "success", "result": result}
    except urllib.error.URLError as e:
        return {"status": "error", "error": str(e)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def generate_training_report(
    job_type: str,
    topic: str,
    duration_minutes: int,
    training_result: dict,
) -> str:
    """
    生成培训报告文本

    Args:
        job_type: 岗位类型
        topic: 培训主题
        duration_minutes: 时长
        training_result: 培训生成结果

    Returns:
        str: 报告文本
    """
    outline = training_result.get("outline", {})
    content = training_result.get("content", {})
    cases = training_result.get("cases", [])
    quiz = training_result.get("quiz", [])
    evaluation = training_result.get("evaluation", {})
    quick_ref = training_result.get("quick_ref", {})

    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("合规培训执行报告")
    report_lines.append("=" * 60)
    report_lines.append("")
    report_lines.append(f"岗位类型: {job_type}")
    report_lines.append(f"培训主题: {topic}")
    report_lines.append(f"培训时长: {duration_minutes}分钟")
    report_lines.append(f"课件章节: {len(outline.get('sections', []))}个")
    report_lines.append(f"案例数量: {len(cases)}个")
    report_lines.append(f"测试题目: {len(quiz)}题")
    report_lines.append(f"评估维度: {len(evaluation.get('dimensions', []))}个")
    report_lines.append("")
    report_lines.append("-" * 60)
    report_lines.append("培训内容摘要")
    report_lines.append("-" * 60)
    report_lines.append("")
    report_lines.append("【法规要点】")
    for reg in content.get("regulations", [])[:2]:
        report_lines.append(f"  • {reg}")
    report_lines.append("")
    report_lines.append("【核心要点】")
    for point in content.get("key_points", [])[:3]:
        report_lines.append(f"  ✓ {point}")
    report_lines.append("")
    report_lines.append("-" * 60)
    report_lines.append("合规要点速查卡")
    report_lines.append("-" * 60)
    report_lines.append(f"标题: {quick_ref.get('title', 'N/A')}")
    report_lines.append(f"版本: {quick_ref.get('version', '1.0')}")
    report_lines.append(f"生效日期: {quick_ref.get('effective_date', 'N/A')}")
    report_lines.append("")
    report_lines.append("=" * 60)
    report_lines.append("报告生成完成")
    report_lines.append("=" * 60)

    return "\n".join(report_lines)


# 测试
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__file__).rsplit("/", 1)[0])

    from training_engine import ComplianceTrainingEngine

    engine = ComplianceTrainingEngine()
    result = engine.generate_training(
        job_type="客户经理",
        department="销售部",
        topic="销售合规",
        duration_minutes=60,
    )

    # 构建卡片
    card = build_training_card(
        job_type=result["meta"]["job_type"],
        topic=result["meta"]["topic"],
        duration_minutes=result["meta"]["duration_minutes"],
        **{
            k: v
            for k, v in result.items()
            if k in ["outline", "content", "cases", "quiz", "evaluation", "quick_ref"]
        },
    )

    print("企微卡片内容预览：")
    print(json.dumps(card, ensure_ascii=False, indent=2))
