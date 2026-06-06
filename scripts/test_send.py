#!/usr/bin/env python3
"""
企微消息发送测试脚本
从环境变量读取敏感信息，避免硬编码
"""
import os
import sys
import requests

# 从环境变量读取凭证（避免硬编码）
CORP_ID = os.environ.get("WECOM_CORP_ID", "wwbdae461005eaad63")
AGENT_ID = int(os.environ.get("WECOM_AGENT_ID", "1000005"))
SECRET = os.environ.get("WECOM_SECRET", "")
USER_ID = os.environ.get("WECOM_USER_ID", "YuZhaoPeng")

if not SECRET:
    print("❌ 错误: 请设置环境变量 WECOM_SECRET")
    print("   例如: export WECOM_SECRET='your-secret-here'")
    sys.exit(1)


def get_access_token(corp_id: str, secret: str) -> str:
    """获取企微 access_token"""
    url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    params = {
        "corpid": corp_id,
        "corpsecret": secret,
    }
    resp = requests.get(url, params=params, timeout=15)
    data = resp.json()

    if data.get("errcode") != 0:
        raise Exception(f"获取token失败: {data}")

    return data["access_token"]


def send_text_message(token: str, user_id: str, content: str) -> dict:
    """发送文本消息"""
    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"
    payload = {
        "touser": user_id,
        "msgtype": "text",
        "agentid": AGENT_ID,
        "text": {
            "content": content
        },
        "safe": 0,
    }
    resp = requests.post(url, json=payload, timeout=15)
    return resp.json()


def main():
    print("=" * 50)
    print("企微消息发送测试")
    print("=" * 50)
    print(f"企业ID: {CORP_ID}")
    print(f"应用ID: {AGENT_ID}")
    print(f"接收人: {USER_ID}")
    print()

    # 获取 token
    print("1. 获取 access_token...")
    try:
        token = get_access_token(CORP_ID, SECRET)
        print(f"   ✅ 成功: {token[:20]}...")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        sys.exit(1)

    # 准备消息内容
    print("2. 准备消息内容...")
    from wecom_formatter import format_dd_report, TEST_RESULT
    message = format_dd_report(TEST_RESULT)
    print(f"   ✅ 消息长度: {len(message)} 字符")

    # 发送消息
    print("3. 发送消息...")
    try:
        result = send_text_message(token, USER_ID, message)
        if result.get("errcode") == 0:
            print(f"   ✅ 发送成功!")
            print(f"      msgid: {result.get('msgid', 'N/A')}")
        else:
            print(f"   ❌ 发送失败: {result}")
    except Exception as e:
        print(f"   ❌ 异常: {e}")

    print()
    print("=" * 50)
    print("测试完成")
    print("=" * 50)


if __name__ == "__main__":
    main()
