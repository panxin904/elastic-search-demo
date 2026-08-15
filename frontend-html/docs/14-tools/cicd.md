---
title: CI/CD
---

# CI/CD — Git Hooks / Pipeline

## 🪝 Git Hooks (husky)

```bash
npm i -D husky lint-staged
npx husky init
```

```jsonc
// package.json
{
  "lint-staged": {
    "*.{ts,tsx,js}": ["eslint --fix", "prettier --write"],
    "*.md": "prettier --write"
  }
}
```

`.husky/pre-commit` 自动由 husky 生成：
```bash
npx lint-staged
```

`.husky/commit-msg`：
```bash
# 校验 commit message 格式 (commitlint)
npx --no-install commitlint --edit "$1"
```

## 📋 commitlint

```bash
npm i -D @commitlint/cli @commitlint/config-conventional
```

```js
// commitlint.config.js
export default { extends: ['@commitlint/config-conventional'] }
```

格式：`type(scope?): subject`
- feat: 新功能
- fix: 修复
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 杂项

```
feat(tailwind): add dark mode support
fix(cors): resolve preflight 401 issue
```

## 🚀 GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm typecheck
      - run: pnpm test
      - run: pnpm build

  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: pnpm install --frozen-lockfile
      - run: pnpm playwright install --with-deps
      - run: pnpm e2e
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: playwright-report
```

## 🏗 部署策略

| 策略 | 描述 | 回滚 |
|------|------|------|
| 蓝绿 | 新旧两套，切换流量 | 切回旧 |
| 灰度 | 部分用户访问新版本 | 移除比例 |
| 金丝雀 | 小流量验证 | 移除 |
| Feature Flag | 运行时开关 | 关闭 flag |

Vercel / Cloudflare 自动支持蓝绿；自托管可使用 Argo Rollouts / Spinnaker。

## 🌐 Vercel / Netlify 一键部署

```bash
npm i -g vercel
vercel --prod
```

自动：
- PR 预部署（每个 commit 一个 URL）
- 域名 + 自动 HTTPS
- 全球 CDN
- 边缘函数

## 📊 版本发布 (changesets)

```bash
npx changeset        # 添加变更记录
npx changeset version # 更新版本号
npx changeset publish # 发布到 npm
```

```md
# .changeset/xxx.md
---
'@org/ui': patch
'@org/web': minor
---

修复组件在 Safari 上的闪烁
```

## 🔐 敏感数据

```yaml
# Settings → Secrets
VITE_API_BASE_URL: ${{ secrets.API_BASE_URL }}
NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

本地开发用 `.env.local`，**永远不要 commit**。`.gitignore` 加 `.env*`。

## 🚥 Lighthouse CI

```yaml
- name: Lighthouse
  uses: treosh/lighthouse-ci-action@v10
  with:
    urls: https://staging.example.com
    budgetPath: ./lighthouse-budget.json
    uploadArtifacts: true
```

```jsonc
// lighthouse-budget.json
[{
  "path": "/",
  "resourceSizes": [{ "resourceType": "script", "budget": 200 }],
  "timings": [{ "metric": "largest-contentful-paint", "budget": 2500 }]
}]
```

## 🔁 PR 模板

```md
## 改了什么
<!-- 一句话 -->

## 截图 / 录屏
<!-- UI 变更附图 -->

## 怎么测
<!-- 给 reviewer 复现步骤 -->
```

## 🔗 下一步

- [前端监控](/14-tools/monitor)
- [微前端](/14-tools/micro-frontend)
- [Lint / Format](/14-tools/lint)
