---
title: Cypress / Playwright
date: 2026-08-15  # date-auto-injected
---

# Cypress / Playwright

## 🆚 二者对比

| | Cypress | Playwright |
|--|---------|------------|
| 厂商 | Cypress.io | Microsoft |
| 浏览器 | Chromium / Firefox / WebKit | Chromium / Firefox / WebKit |
| 语言 | JS / TS | JS / TS / Python / .NET / Java |
| 速度 | 较慢 | 快 2-3x |
| 多 Tab | 受限 | 原生支持 |
| 调试体验 | ✅ 时光机 | ✅ trace viewer |
| 移动 | 模拟 | 设备模拟 |
| 自动等待 | ✅ | ✅ |

## 📦 Cypress 基础

```bash
npm install -D cypress
npx cypress open
```

```ts
// cypress/e2e/login.cy.ts
describe('登录', () => {
  it('应该跳转到首页', () => {
    cy.visit('/login')
    cy.get('[data-test=email]').type('alice@example.com')
    cy.get('[data-test=password]').type('secret123')
    cy.get('button[type=submit]').click()
    cy.url().should('include', '/dashboard')
    cy.contains('欢迎')
  })
})
```

**特点**：
- 内置 Mocha / Chai 风格的 `describe` / `it`
- 自动等待 DOM
- Test Runner 可看到每一步

## 📦 Playwright 基础

```bash
npm install -D @playwright/test
npx playwright init
```

```ts
// tests/login.spec.ts
import { test, expect } from '@playwright/test'

test('登录流程', async ({ page }) => {
  await page.goto('/login')
  await page.getByLabel('邮箱').fill('alice@example.com')
  await page.getByLabel('密码').fill('secret123')
  await page.getByRole('button', { name: '登录' }).click()
  await expect(page).toHaveURL(/dashboard/)
  await expect(page.getByText('欢迎')).toBeVisible()
})
```

**特点**：
- 自动追踪失败重试
- `trace viewer` 截图 / 视频 / 网络
- 多浏览器 project 一次跑
- `getByRole` 内置 i18n 支持

## 🔧 通用模式

### 1. 登录态共享

```ts
// Playwright fixture
function createAuthFixture() {
  return async ({ page }, use) => {
    await page.goto('/login')
    await page.getByLabel('邮箱').fill('admin@test.com')
    await page.getByLabel('密码').fill('xxx')
    await page.getByRole('button', { name: '登录' }).click()
    await use(page)
  }
}
```

### 2. 网络拦截

```ts
await page.route('**/api/users', async route => {
  await route.fulfill({ json: [{ id: 1, name: 'mock' }] })
})
```

### 3. 视觉回归

```ts
await expect(page).toHaveScreenshot('homepage.png', { maxDiffPixels: 100 })
```

## 📁 CI 集成

```yaml
# .github/workflows/e2e.yml
- name: Playwright tests
  run: npx playwright test --reporter=html
- uses: actions/upload-artifact@v4
  if: always()
  with:
    name: playwright-report
    path: playwright-report
```

## 🐞 调试

### Cypress
- Test Runner 时光机
- `cy.pause()` / `cy.debug()`

### Playwright
- `PWDEBUG=1 npx playwright test` step-by-step
- `npx playwright show-trace trace.zip`

## 🎯 我的建议

| 场景 | 推荐 |
|------|------|
| React / Vue + 团队熟悉 Cypress | Cypress |
| 跨浏览器、移动、需要 trace | Playwright |
| 想要快速上手 + 时序观察 | Cypress |
| 跨语言（Python / .NET） | Playwright |

## ⚠️ 常见坑

- **E2E 慢且脆弱**：避免依赖具体文案
- **测试隔离**：每个 test 前清状态 / mock storage
- **不要 E2E 测所有逻辑**：单元测试覆盖率 70%+ 后再做 E2E
- **CI 上慢**：并行 + 仅在 PR 触发

## 🔗 下一步

- [Jest / Vitest](/10-testing/unit)
- [Storybook](/10-testing/storybook)
- [CI/CD](/14-tools/cicd)
