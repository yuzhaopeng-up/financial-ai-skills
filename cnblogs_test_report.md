# 博客园自动发布测试报告

## 测试时间
2026-06-06

## 测试账号
- 用户名：13701884857
- 密码：ttt888ttT888

## 测试结果

### ❌ 自动登录失败

**原因分析：**

1. **Angular SPA架构**：博客园登录页是Angular单页应用，页面内容由JavaScript动态渲染，curl无法获取隐藏的`__RequestVerificationToken`

2. **XSRF-TOKEN机制**：虽然能获取到`XSRF-TOKEN` cookie，但登录API `/api/signin` 需要额外的请求头验证

3. **安全验证弹窗**：登录过程中出现"请完成安全验证"提示（可能是行为验证或滑块验证）

4. **Cookie未持久化**：即使手动输入账号密码点击登录，cookie也未正确设置到`i.cnblogs.com`域名下

### 详细测试步骤

```
1. GET https://account.cnblogs.com/signin
   → 获取XSRF-TOKEN cookie
   → 页面为Angular SPA，无隐藏token input

2. POST https://account.cnblogs.com/api/signin
   → 返回HTML而非JSON（可能是验证失败）
   → 需要额外的请求头或行为验证

3. 手动浏览器登录
   → 出现"请完成安全验证"提示
   → 关闭验证后重新登录
   → 仍跳转回登录页（未成功）

4. 访问 https://i.cnblogs.com/posts/edit
   → 重定向到登录页（未认证）
```

### 关键发现

- 博客园使用`_c_WBKFRo` cookie作为设备/会话标识
- `XSRF-TOKEN`每次请求都会更新
- 登录API可能需要`RequestVerificationToken`（不在cookie中，在Angular应用内部）

## 可行性评估

| 方案 | 可行性 | 难度 | 说明 |
|------|--------|------|------|
| 纯curl + cookie | ❌ 低 | 高 | Angular SPA + 安全验证 |
| Selenium/Playwright | ✅ 中 | 中 | 可模拟完整浏览器行为 |
| 浏览器扩展 | ✅ 中 | 中 | 登录后扩展操作 |
| 博客园API | ❓ 未知 | 未知 | 官方未公开API文档 |

## 建议

### 方案1：Selenium自动化（推荐）
```python
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://account.cnblogs.com/signin")
driver.find_element(By.CSS_SELECTOR, "input[type='text']").send_keys("13701884857")
driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys("ttt888ttT888")
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
# 处理可能的安全验证
# 然后访问编辑页面发布文章
```

### 方案2：先手动登录，再Cookie自动化
1. 用户手动在浏览器登录博客园
2. 导出cookie（Chrome插件：EditThisCookie）
3. 脚本使用导出的cookie访问编辑API
4. 定期刷新cookie

### 方案3：放弃博客园，优先其他平台
- 知乎：✅ 已验证可用
- 掘金：🔍 待测试（可能比博客园简单）
- Dev.to：✅ API可用（英文）

## 结论

**博客园自动发布不可行（纯API方式）**，原因：
1. Angular SPA + 安全验证
2. 无公开API文档
3. 登录流程复杂，需要浏览器环境

**建议转向：**
1. 优先掘金（测试sessionid方式）
2. 使用Selenium方案（如必须发博客园）
3. 英文内容发Dev.to/Medium
