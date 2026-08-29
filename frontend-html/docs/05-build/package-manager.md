---
title: 包管理器 (pnpm/yarn)
date: 2026-08-15  # date-auto-injected
---

# 包管理器 — pnpm / yarn / npm

## 🆚 三者对比

| | npm | yarn (classic) | yarn (v4 berry) | pnpm |
|--|----|----|----|----|
| 安装速度 | 慢 | 中 | 快 | **最快** |
| 磁盘占用 | 大 | 大 | 中 | **最小** |
| 单仓多包 | workspaces | workspaces | workspaces | workspaces (最快) |
| Lock | package-lock.json | yarn.lock | yarn.lock | pnpm-lock.yaml |
| Node 版本 | 内置 | 内置 | 内置 | 内置 |
| 严格性 | 一般 | 一般 | ✅ | ✅ |

## ⭐ pnpm 优势

```bash
npm install        # 拷贝所有依赖到 node_modules
pnpm install       # 软链 + 内容寻址 store（/pnpm-store）
```

**软链布局**：每个包共享一份 disk store，符号链接到 `node_modules`。

```
my-app/
  node_modules/
    .pnpm/
      react@18.2.0/        ← 真实目录
      vue@3.5.0/
    react -> .pnpm/react@18.2.0/node_modules/react   ← 软链
```

优点：
- 几十个包的项目也能快速安装
- 不会因为 hoist 引起依赖幽灵

## 🛠️ 常用命令

```bash
# 安装
pnpm install            # 按 lockfile 安装
pnpm add react          # 添加
pnpm add -D eslint      # 添加 devDependency
pnpm add -g pnpm        # 全局

# 升级
pnpm up                  # 全部升级
pnpm up react            # 单包升级
pnpm up --latest react   # 升级到 latest

# 工作区
pnpm -r run build        # 所有子包执行 build
pnpm --filter @app/web run dev
```

## 🔒 严格性 / 幽灵依赖

```bash
# pnpm 默认阻止幽灵依赖（直接 import 未在 package.json 声明的包）
echo '{ "name": "...", "peerDependencies": { ... } }' > .npmrc

# 单独项目用：
echo 'auto-install-peers=true' >> .npmrc
```

## 📁 Workspaces（Monorepo 一把好手）

```yaml
# pnpm-workspace.yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

```bash
pnpm -F @app/web build
pnpm -r --parallel dev
```

## ⚡ 加速秘籍

- `.npmrc` 设置 `registry=https://registry.npmmirror.com`
- 用 `pnpm fetch` 预下载到离线目录
- CI 中用 `pnpm install --frozen-lockfile`（强制 lockfile 一致）

## 🔒 安全

```bash
pnpm audit           # 同 npm audit
pnpm audit --fix
```

pnpm 8+ 默认不会读取非声明依赖，避免供应链攻击。

## 🔗 下一步

- [Monorepo (Turbo/Nx)](/05-build/monorepo)
- [Vite 原理](/05-build/vite)
