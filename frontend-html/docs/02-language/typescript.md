---
title: TypeScript 类型系统
date: 2026-08-15  # date-auto-injected
---

# TypeScript 类型系统

## 🎯 类型基础

```ts
// 基础类型
let a: number = 1
let b: string = 'hi'
let c: boolean = true
let d: number[] = [1, 2, 3]
let e: [string, number] = ['x', 1]  // 元组

// 联合类型
type Result = string | number

// 字面量类型
type Dir = 'up' | 'down' | 'left' | 'right'

// 对象类型
interface User {
  id: string
  name: string
  age?: number                 // 可选
  readonly createdAt: Date     // 只读
}

// type vs interface
type A = { a: number }
type B = A & { b: string }      // 交叉
type C = A | B                  // 联合
```

## 🧬 泛型

```ts
function identity<T>(x: T): T { return x }

interface ApiResponse<T> {
  data: T
  status: number
}

function pick<T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> {
  const out = {} as Pick<T, K>
  keys.forEach(k => (out[k] = obj[k]))
  return out
}

pick(user, ['name', 'age'])     // { name: string, age?: number }
```

## 🏷️ 工具类型

| 工具类型 | 作用 |
|---------|------|
| `Partial<T>` | 全部变可选 |
| `Required<T>` | 全部变必填 |
| `Readonly<T>` | 全部变只读 |
| `Pick<T, K>` | 挑选字段 |
| `Omit<T, K>` | 排除字段 |
| `Record<K, V>` | `K → V` 的对象 |
| `Exclude<T, U>` | 从 T 排除 U |
| `Extract<T, U>` | 从 T 抽取 U |
| `ReturnType<F>` | 函数返回值类型 |
| `Parameters<F>` | 函数参数类型 |
| `NonNullable<T>` | 排除 null/undefined |

## 🔍 类型守卫

```ts
function isUser(x: unknown): x is User {
  return typeof x === 'object' && x !== null && 'id' in x
}

function process(value: string | number) {
  if (typeof value === 'string') {
    return value.toUpperCase()
  }
  return value.toFixed(2)
}
```

## 🎭 类型体操入门

```ts
// 实现一个 Length<T>：返回元组长度
type Length<T extends readonly any[]> = T['length']

type T1 = Length<['a', 'b', 'c']>  // 3

// 实现 First<T>
type First<T extends any[]> = T extends [infer F, ...any[]] ? F : never

type T2 = First<['a', 'b']>  // 'a'

// 实现 TupleToObject
type TupleToObject<T extends readonly (string | number)[]> = {
  [K in T[number]]: K
}

const obj = {} as TupleToObject<['a', 'b']>  // { a: 'a', b: 'b' }
```

## 🔧 配置策略

```jsonc
// tsconfig.json（推荐）
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "noImplicitAny": true,
    "noUncheckedIndexedAccess": true,
    "skipLibCheck": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "verbatimModuleSyntax": true
  }
}
```

`noUncheckedIndexedAccess` 是近年新选项，让 `arr[i]` 返回 `T | undefined`，避免运行时踩坑。

## 🔄 与项目集成

- **Vite**：内置 esbuild，开箱即用
- **Next.js**：内置 SWC
- **Node + ts-node / tsx**：开发 / 生产两套
- **Monorepo**：TS Project References / 共享 `tsconfig.base.json`

## 🧪 运行时校验

TS 只在编译期生效，运行时的数据（如 API 返回）需要额外校验：

- **Zod**（schema = 类型 + 校验）
- **Valibot**（更轻）
- **TypeBox**

```ts
import { z } from 'zod'

const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  age: z.number().optional()
})

type User = z.infer<typeof UserSchema>

const parsed = UserSchema.parse(apiResponse)
```

## 🔗 下一步

- [ESNext 新特性](/02-language/esnext)
- [React 核心与 Hooks](/03-framework/react)
