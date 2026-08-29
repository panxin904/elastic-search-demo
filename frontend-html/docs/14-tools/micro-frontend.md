---
title: 微前端
---

# 微前端 (Micro Frontends)

## 🎯 为什么需要微前端

```
单体应用 / 大仓 monorepo 在 50+ 人 / 100+ 团队时：
  ❌ 一次发布全量风险
  ❌ 编译 / 启动变慢
  ❌ 跨团队改动互相阻塞

微前端：
  ✅ 团队自治（独立开发 / 部署）
  ✅ 技术栈可异构（主应用 React，子应用 Vue / Solid）
  ✅ 独立运行时（一个子应用挂掉不影响其他）
```

## 🧱 主流方案对比

| | qiankun | micro-app | Module Federation | Single-SPA | wujie |
|--|---------|-----------|-------------------|------------|-------|
| 出身 | 阿里 | 京东 | Webpack 5 | 历史悠久 | 腾讯 |
| 隔离 | Proxy 沙箱 | Proxy + WebComponent | 真 ESM 模块 | iframe | iframe |
| 性能 | 中 | 良 | 优 | 中 | 优 |
| 多技术栈 | ✅ | ✅ | 受限 | ✅ | ✅ |
| 学习曲线 | 中 | 平 | 中 | 陡 | 中 |
| 生态 | 大 | 中 | 中 | 大 | 中 |

## 🔌 Webpack 5 Module Federation

**原生 + 最先进**的方案。让一个应用加载另一个应用导出的"远程模块"。

```js
// 远程应用（被消费方）webpack.config.js
new ModuleFederationPlugin({
  name: 'host',
  filename: 'remoteEntry.js',
  exposes: {
    './Button': './src/Button'
  },
  shared: ['react', 'react-dom']
})

// 主应用 webpack.config.js
new ModuleFederationPlugin({
  name: 'guest',
  remotes: {
    host: 'host@http://localhost:3001/remoteEntry.js'
  },
  shared: ['react', 'react-dom']
})

// 主应用代码
const Button = lazy(() => import('host/Button'))
```

Vite 也支持（`@originjs/vite-plugin-federation`）。

## 🪟 qiankun（阿里）

基于 **single-spa + Proxy 沙箱**，最常用。

```ts
// 主应用
import { registerMicroApps, start } from 'qiankun'

registerMicroApps([
  {
    name: 'react-app',
    entry: '//localhost:7101',
    container: '#subapp',
    activeRule: '/react',
    props: { token: getToken() }
  },
  {
    name: 'vue-app',
    entry: '//localhost:7102',
    container: '#subapp',
    activeRule: '/vue'
  }
])

start({ prefetch: 'all' })
```

```js
// 子应用 main.js
export async function bootstrap() { /* ... */ }
export async function mount(props) {
  render(props)
}
export async function unmount() {
  instance.unmount()
}
```

## 🧸 micro-app（京东）

基于 **WebComponents**，更轻量。

```html
<!-- 主应用 -->
<micro-app name="react-app" url="http://localhost:7101/" baseroute="/react/" />
```

```js
// 子应用入口改造
import microApp from '@micro-zoe/micro-app'

microApp.start({
  plugins: {
    modules: {
      'react-app': {
        async loadCode(url) {
          // 可以加 cache / 重试
          return await fetch(url).then(r => r.text())
        }
      }
    }
  }
})
```

## 🌐 wujie（腾讯）

基于 **iframe 隔离**，共享 DOM 通讯，性能优。

```js
// 主应用
new WujieVue({ name: 'app1', url: 'http://localhost:7101/', el: '#subapp' })
```

## ⚖️ 选型

| 场景 | 推荐 |
|------|------|
| 老项目接入 / 兼容旧浏览 | qiankun |
| 想要简单 / WebComponent | micro-app |
| 内部团队 / 新项目 / 想最优性能 | Module Federation |
| 严格沙箱 / 旧 iframe 应用 | wujie |

## 🛡️ 关键问题

### 1. 路由联动

```ts
// 主应用监听 hashchange / popstate
// 通知子应用跳转
window.history.pushState = patch(window.history, 'pushState', (original) =>
  function (...args) {
    original.apply(this, args)
    emit('route-change')
  })
```

### 2. 样式隔离

- CSS-in-JS：天然 scope
- CSS Module / BEM 命名
- 子应用被 mount 时清空旧的样式（qiankun 默认）
- Shadow DOM（micro-app 提供）

### 3. 通信

- **Props**：qiankun 通过 `props` 传递
- **事件总线**：自定义 EventBus
- **全局 Store**：Pinia / Zustand 跨应用共享（要 register / unregister lifecycle）

### 4. 共享依赖

```js
// Module Federation
shared: { react: { singleton: true }, 'react-dom': { singleton: true } }
```

## 🆚 微前端 vs Monorepo

| | 微前端 | Monorepo |
|--|--------|----------|
| 团队 | 跨团队、强自治 | 同团队、共享代码 |
| 部署 | 独立部署 | 一起部署 |
| 包大小 | 子应用按需 | 通常 1 个 bundle |
| 隔离 | 运行时隔离 | 同一运行时 |
| 类型复用 | 跨项目共享 types | 直接 import |

两者**不冲突**，常见组合：Monorepo (共享类型) + 微前端 (运行时隔离)。

## 🔗 下一步

- [Monorepo](/05-build/monorepo)
- [Vite 原理](/05-build/vite)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [java](https://java-px.bot.cd/java-web-manual/):Java 后端 API
- [android](https://java-px.bot.cd/android/):Android 移动
- [java-language](https://java-px.bot.cd/java-language/):Java 基础
