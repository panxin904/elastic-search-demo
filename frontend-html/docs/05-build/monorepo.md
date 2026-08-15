---
title: Monorepo (Turbo/Nx)
---

# Monorepo — Turbo / Nx

## 🎯 为什么用 Monorepo

```
polyrepo 痛点：
  ❌ 共享 utils 抽 git submodule / npm 包 → 版本 + 发布流程繁琐
  ❌ 跨项目重构一次要改 10 个仓库
  ❌ CI 配置分散

monorepo：
  ✅ 共享代码直接 import，refactor 一处生效
  ✅ 统一 lint / format / TS config
  ✅ 一次安装所有依赖
```

## 📁 标准布局

```
my-org/
├── apps/
│   ├── web/           # Next.js
│   ├── admin/         # Vue 后台
│   └── docs/          # VitePress
├── packages/
│   ├── ui/            # 共享组件
│   ├── utils/         # 工具函数
│   ├── tsconfig/      # 共享 TS 配置
│   └── eslint-config/ # 共享 ESLint
├── pnpm-workspace.yaml
├── turbo.json
└── package.json
```

## ⚡ Turborepo（推荐）

```jsonc
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": { "dependsOn": ["^build"], "outputs": ["dist/**"] },
    "test":   { "dependsOn": ["build"] },
    "lint":   {},
    "dev":    { "cache": false, "persistent": true }
  }
}
```

```bash
turbo run build          # 并行 + 缓存
turbo run build --force  # 强制忽略缓存
turbo run dev            # 并发执行所有 dev 任务
turbo run build --filter=web  # 只构建 web 及其依赖
```

- **增量缓存**（基于文件 hash 的内容缓存）
- **任务编排**（`dependsOn: ["^build"]` 先构建依赖）
- **远程缓存**（自建或 Vercel）

## 🔧 Nx（Nrwl）

适合**大型 monorepo**，自带：
- 代码生成器（`nx generate @nx/react:app`）
- 依赖图可视化（`nx graph`）
- 严格的工作区约定
- 受影响的项目分析（`nx affected`）

```bash
nx build web
nx test web --watch
nx run-many -t build      # 多个项目并行
nx affected -t test       # 只测试被改动影响的
```

## 📦 包管理选型

| 工具 | 推荐 |
|------|------|
| npm workspaces | 简单项目 |
| yarn workspaces v4 | 已有 yarn 的项目 |
| **pnpm workspaces** | ✅ 推荐——快、严格 |

```yaml
# pnpm-workspace.yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

```bash
pnpm -r run build         # 所有包
pnpm --filter @org/ui run build  # 指定包及其依赖
```

## 🏗 共享 TS 配置

```jsonc
// packages/tsconfig/base.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "esModuleInterop": true
  }
}
```

```jsonc
// packages/ui/tsconfig.json
{
  "extends": "@org/tsconfig/base.json"
}
```

## 🎨 共享 ESLint

```js
// packages/eslint-config/index.js
module.exports = {
  extends: ['eslint:recommended', 'plugin:@typescript-eslint/recommended'],
  parser: '@typescript-eslint/parser'
}
```

```jsonc
// apps/web/.eslintrc
{
  "extends": "@org/eslint-config"
}
```

## 🔄 共享组件包

```ts
// packages/ui/src/Button.tsx
export function Button(props) { /* ... */ }

// apps/web/app.tsx
import { Button } from '@org/ui'   // 直接用，无需发布
```

## ⚠️ 注意事项

- **依赖引用方式**：共享包使用 `workspace:*`（pnpm）
- **CI 缓存**：`turbo` 自带 hash 缓存
- **构建产物**：每个包自己 `dist/`，在 `turbo.json` 中声明 `outputs`
- **测试隔离**：用 vitest workspaces / jest projects

## 🔗 下一步

- [包管理器](/05-build/package-manager)
- [CI/CD](/14-tools/cicd)
- [微前端](/14-tools/micro-frontend)
