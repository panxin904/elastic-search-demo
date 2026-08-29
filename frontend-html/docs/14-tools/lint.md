---
title: Lint / Format
date: 2026-08-15  # date-auto-injected
---

# 代码规范 — Lint / Format

## 🧰 ESLint

```bash
npm i -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
```

```js
// eslint.config.js（v9 flat config）
import tseslint from '@typescript-eslint/eslint-plugin'
import tsParser from '@typescript-eslint/parser'

export default [
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      parser: tsParser
    },
    plugins: { '@typescript-eslint': tseslint },
    rules: {
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      'no-console': 'warn',
      'eqeqeq': ['error', 'always']
    }
  }
]
```

常用 preset：
- `eslint-config-airbnb`（严格）
- `eslint-config-standard`（折中）
- `eslint-config-prettier`（与 Prettier 配合）
- `eslint-plugin-react` / `eslint-plugin-react-hooks`
- `eslint-plugin-jsx-a11y`

## 🎨 Prettier

```bash
npm i -D prettier
```

```jsonc
// .prettierrc.json
{
  "semi": false,
  "singleQuote": true,
  "trailingComma": "all",
  "printWidth": 100,
  "tabWidth": 2
}
```

```bash
npx prettier --write .
npx prettier --check .
```

## 🤝 ESLint + Prettier 集成

顺序：**Prettier 负责格式化，ESLint 负责代码质量**。

```bash
npm i -D eslint-config-prettier
```

```js
// eslint.config.js 最后覆盖样式类规则
export default [
  ...,
  { rules: {
    'prettier/prettier': 'error'
  }}
]
```

Lint-staged / husky 在 commit 前自动修：

```bash
npm i -D husky lint-staged
npx husky init
```

```jsonc
// package.json
{
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{css,md}": ["prettier --write"]
  }
}
```

## 🌐 其他项目类型

| 项目 | 主要工具 |
|------|---------|
| Vue | ESLint + `eslint-plugin-vue` + Prettier |
| React | ESLint + `eslint-plugin-react` / `react-hooks` |
| TS | `@typescript-eslint` |
| MD/Vue SFC | `eslint-plugin-markdown` / `eslint-plugin-vue` |

## 🪛 IDE 集成

VSCode `.vscode/settings.json`：

```jsonc
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit"
  }
}
```

## 📦 共享配置 (monorepo)

```js
// packages/eslint-config/index.js
module.exports = require('./node.js')  // 拆 server / browser
```

```jsonc
// apps/web/package.json
{ "eslintConfig": { "extends": "@org/eslint-config/browser" } }
```

## 🎯 团队规范落地的关键

1. **CI 验证**：PR 必须 lint pass
2. **自动修复**：lint-staged + husky
3. **文档化**：README / CONTRIBUTING.md
4. **不严格规则**：先开启 warning，一段时间转 error

## 🔗 下一步

- [CI/CD](/14-tools/cicd)
- [微前端](/14-tools/micro-frontend)
