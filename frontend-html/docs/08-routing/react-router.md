---
title: React Router v6/v7
---

# React Router v6/v7

## 🌐 路由发展史

| 版本 | 特点 |
|------|------|
| v3 / v4 | 静态路由配置、`<Route>` 内联 |
| v5 | Hooks API（useHistory → useNavigate） |
| **v6** | `<Routes>`、嵌套路由、`loader` data API |
| **v7** | 与 Remix 统一（Remix 模式） |

## 🚀 v6 基础 API

### 声明式

```tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="about" element={<About />} />
        <Route path="users/:id" element={<UserDetail />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  )
}
```

### 数据式（router v6.4+，承袭 Remix）

```tsx
import { createBrowserRouter, RouterProvider } from 'react-router-dom'

const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    children: [
      { index: true, element: <Home /> },
      { path: 'about', element: <About /> },
      {
        path: 'users/:id',
        element: <UserDetail />,
        loader: ({ params }) => fetch(`/api/users/${params.id}`)
      }
    ]
  }
])

<RouterProvider router={router} />
```

## 🧩 嵌套路由 + Outlet

```tsx
function Root() {
  return (
    <div>
      <Nav />
      <Outlet />   {/* 子路由渲染在这里 */}
    </div>
  )
}
```

## 🚦 导航与状态

```tsx
import { useNavigate, useLocation, useParams } from 'react-router-dom'

function Profile() {
  const navigate = useNavigate()
  const { id } = useParams()
  const location = useLocation()

  return (
    <button onClick={() => navigate(-1)}>Back</button>
  )
}
```

## 🛡️ 守卫 / 重定向

```tsx
function Protected() {
  const auth = useAuth()
  if (!auth.user) return <Navigate to="/login" replace />
  return <Dashboard />
}
```

或者用 v6.4 的 `loader` + `redirect()`：

```tsx
{
  path: 'admin',
  loader: () => {
    if (!isLogin) throw redirect('/login')
    return null
  },
  element: <Admin />
}
```

## 📊 v7 与 Remix 统一

v7 把 Remix 的 **loader / action / Form / revalidate** 集成进来：

```tsx
import { redirect } from 'react-router'

export async function loader({ params }) {
  const data = await fetch(`/api/posts/${params.id}`)
  if (!data.ok) throw redirect('/404')
  return data.json()
}

export default function Post() {
  const post = useLoaderData<typeof loader>()
  return <article>{post.title}</article>
}
```

## 🔗 与 TanStack Router 比较

| | React Router | TanStack Router |
|--|---------------|-----------------|
| API 心智 | 传统 React | 类型安全 first |
| 类型化参数 | 需手写 | 自动推断 |
| Search params 类型 | ❌ | ✅ |
| 缓存 | ❌ | 内置 |

如果项目重类型安全，**TanStack Router 值得一试**。

## 🔗 下一步

- [Vue Router 4](/08-routing/vue-router)
- [TanStack Router](/08-routing/tanstack-router)
- [File-system Routing](/08-routing/file-routing)
