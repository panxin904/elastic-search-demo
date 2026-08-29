---
title: Angular 体系
date: 2026-08-15  # date-auto-injected
---

# Angular 体系

## 🎯 Angular 是什么

Google 维护的企业级前端框架：**DI + RxJS + Zone.js + 强类型**。

```
优点：
  ✅ 全家桶（路由 / HTTP / 表单 / 动画 / i18n / a11y）开箱即用
  ✅ 强类型 + DI，代码组织严谨
  ✅ 长生命周期，适合企业大型项目
缺点：
  ❌ 学习曲线陡（DI / RxJS / 装饰器）
  ❌ 包体积大（130KB+）
  ❌ 心智与社区主流（React/Vue）差异大
```

## 🏗️ 核心概念

```
Module (NgModule)       传统组织模块（仍可用）
Component              视图组件
Service                 可注入的单例
Pipe                    模板中的数据转换
Directive               自定义 DOM 行为
Guard                   路由守卫
Interceptor             HTTP 拦截器
RxJS Observable         异步流
Zone.js                 自动变化检测
```

## 🆕 Standalone Components（v14+）

推荐：从 v14 起不再强制 NgModule。

```ts
import { Component, inject } from '@angular/core'

@Component({
  standalone: true,
  selector: 'app-counter',
  template: `<button (click)="inc()">{{ count() }}</button>`
})
export class CounterComponent {
  count = signal(0)
  inc() { this.count.update(n => n + 1) }
}
```

## ⚡ Signals（v16+）

类 Solid 的细粒度响应式：

```ts
import { signal, computed, effect } from '@angular/core'

const count = signal(0)
const double = computed(() => count() * 2)

effect(() => {
  console.log('count changed:', count())  // 自动追踪
})

count.set(1)  // 触发 effect
```

## 📡 RxJS（核心难点）

Angular 大量用 Observable / Subject / Operator。

```ts
import { HttpClient } from '@angular/common/http'

http.get<User>('/api/user/1').subscribe(u => console.log(u))

// 取消 + 防抖 + 切换
searchControl.valueChanges.pipe(
  debounceTime(300),
  distinctUntilChanged(),
  switchMap(q => http.get(`/api/search?q=${q}`))
).subscribe(res => this.results.set(res))
```

## 🛣️ 路由（v17+ 函数式 API）

```ts
import { Routes, provideRouter } from '@angular/router'

const routes: Routes = [
  { path: '', component: HomeComponent },
  {
    path: 'admin',
    canMatch: [authGuard],
    loadComponent: () => import('./admin/admin.component')
  }
]

bootstrapApplication(AppComponent, {
  providers: [provideRouter(routes)]
})
```

## 📋 模板驱动表单 vs 响应式表单

```ts
// 模板驱动
<input [(ngModel)]="name">

// 响应式
form = new FormGroup({
  email: new FormControl('', [Validators.required, Validators.email]),
  password: new FormControl('', Validators.minLength(8))
})
```

响应式表单适合复杂校验（异步、跨字段）。

## 🧩 依赖注入

```ts
// service
@Injectable({ providedIn: 'root' })
class UserService {
  getUser(id: string) { /* ... */ }
}

// component
class UserCardComponent {
  private userService = inject(UserService)
}
```

`providedIn: 'root'` 让 Service 成为单例，自动 tree-shake。

## 🚀 构建

- 默认 `@angular/build`（基于 esbuild，新）
- 旧：`ng build` 用 webpack
- 预渲染 / SSR：`ng add @angular/ssr`（Angular Universal）

## 🤝 与 React/Vue 的取舍

| 场景 | Angular | React/Vue |
|------|---------|-----------|
| 大型企业中后台（表单密集） | ✅ 强项 | 也能做 |
| 创业 / 迭代速度优先 | 偏慢 | ✅ 强项 |
| 团队 TypeScript 重度使用 | ✅ | ✅ |
| 招聘 React/Vue 池 | 偏小 | 大 |

## 🔗 下一步

- [前端框架总览](/03-framework/overview)
- [React Router](/08-routing/react-router)
