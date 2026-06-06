# 掘金自动发布测试报告

## 测试时间
2026-06-06

## 测试账号
- 用户名：13701884857
- 密码：ttt888ttT888

## 测试结果

### ❌ 自动登录失败

**原因分析：**

1. **WAF反爬机制**：掘金首页有WAF（Web Application Firewall）防护，curl直接访问返回JavaScript挑战页面（`waf_jschallenge`），需要执行JavaScript计算才能获取真实页面内容

2. **验证码登录优先**：掘金默认登录方式是手机号+短信验证码，密码登录需要手动切换

3. **登录状态未保持**：即使浏览器中输入账号密码点击登录，页面仍停留在登录页，未成功跳转

4. **iframe验证**：登录过程中出现iframe（可能是reCAPTCHA或行为验证）

### 详细测试步骤

```
1. GET https://juejin.cn (curl)
   → 返回WAF挑战页面（需执行JS计算cookie）
   → 无法直接获取页面内容

2. 浏览器访问 https://juejin.cn/login
   → 默认显示"验证码登录/注册"
   → 需手动切换到"密码登录"

3. 输入账号密码点击登录
   → 按钮显示"登录中..."
   → 出现iframe（可能是验证）
   → 页面未跳转，仍停留在登录页

4. 访问 https://juejin.cn/editor/drafts/new
   → 返回空页面（未登录）
```

### 关键发现

- 掘金使用字节跳动的WAF防护（`lf-waf-js.byted-static.com`）
- Cookie中包含`_waftokenid`（WAF token）
- 登录需要`passport_csrf_token`
- 有iframe验证机制

## 可行性评估

| 方案 | 可行性 | 难度 | 说明 |
|------|--------|------|------|
| 纯curl + cookie | ❌ 低 | 极高 | WAF JS挑战 + iframe验证 |
| Selenium/Playwright | ⚠️ 中 | 高 | 需处理WAF和iframe |
| 掘金API | ❓ 未知 | 未知 | 官方未公开API文档 |
| 已登录Cookie | 🔍 待测试 | 中 | 手动登录后导出cookie |

## 建议

### 方案1：手动登录+Cookie自动化（推荐尝试）
1. 用户手动在浏览器登录掘金
2. 导出cookie（特别是`sessionid`类cookie）
3. 脚本使用导出的cookie访问创作API
4. 定期刷新cookie

### 方案2：放弃掘金，专注已验证平台
- 知乎：✅ 已验证可用
- Dev.to：✅ API可用（英文）
- 微信公众号：⚠️ 待验证

### 方案3：Selenium方案（如必须发掘金）
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get("https://juejin.cn/login")

# 切换到密码登录
driver.find_element(By.XPATH, "//span[contains(text(),'密码登录')]").click()

# 输入账号密码
driver.find_element(By.CSS_SELECTOR, "input[type='text']").send_keys("13701884857")
driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys("ttt888ttT888")

# 点击登录
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

# 等待iframe验证（可能需要人工介入）
# 然后访问编辑页面
```

## 结论

**掘金自动发布不可行（纯API方式）**，原因：
1. WAF JS挑战防护
2. 验证码登录优先
3. iframe验证机制
4. 登录状态难以保持

**建议转向：**
1. 优先知乎（已验证）
2. 测试微信公众号（壹伴API）
3. 英文内容发Dev.to
4. 如需发掘金，使用Selenium+人工辅助

## 修正后的平台矩阵

| 平台 | 自动发布 | 状态 | 优先级 |
|------|---------|------|--------|
| **知乎** | ✅ z_c0 Cookie | **已验证** | P0 |
| **Dev.to** | ✅ API | 英文出海 | P1 |
| **微信公众号** | ⚠️ 需插件 | 待验证 | P2 |
| **掘金** | ❌ WAF+验证 | 不可行 | 放弃/ Selenium |
| **博客园** | ❌ Angular+验证 | 不可行 | 放弃 |
| **CSDN** | ❌ 阿里云签名 | 太复杂 | 放弃 |
