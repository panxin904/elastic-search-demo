---
title: Vue 3 组合式 API
date: 2026-08-15  # date-auto-injected
---

# Vue 3 组合式 API

## 🧬 心智模型

Vue = **响应式数据 + 模板编译 + 单向数据流**

```vue
<script setup>
import { ref, computed } from 'vue'

const count = ref(0)
const double = computed(() => count.value * 2)

function inc() { count.value++ }
</script>

<template>
  <button @click="inc">{{ count }} × 2 = {{ double }}</button>
</template>
```

## ⚙️ 响应式 API

| API | 作用 |
|-----|------|
| `ref(value)` | 包装任意值，访问用 `.value` |
| `reactive(obj)` | 让对象整体响应式 |
| `computed(() => ...)` | 计算属性，自动缓存 |
| `watch(source, fn, opts)` | 通用监听 |
| `watchEffect(fn)` | 自动收集依赖 |
| `shallowRef` | 仅 `.value` 自身变更触发更新 |
| `triggerRef` | 手动触发 shallowRef |

## 🆚 ref vs reactive

```ts
const a = ref(0)            // 推荐：明确
const b = reactive({ n: 0 }) // 自动深度代理，但解构会丢响应性
```

**推荐 `ref`**，因为：
- `.value` 显式可见
- 解构不丢响应性（通过 `toRefs`）
- 在 TS 中类型更明确

## 🔄 生命周期（`onMounted` 系列）

```ts
import { onMounted, onUnmounted, onUpdated } from 'vue'

onMounted(() => {
  // DOM 已挂载
  fetchData()
})

onUnmounted(() => {
  // 清理
  sub.close()
})
```

Vue 3 钩子必须在 `<script setup>` 顶层同步调用。

## 📦 组件通讯

```ts
// defineProps + defineEmits
const props = defineProps<{ msg: string }>()
const emit = defineEmits<{ (e: 'change', v: string): void }>()

emit('change', 'new value')
```

```vue
<!-- 父组件 -->
<Child :msg="hello" @change="onChange" />
```

## 🎭 Provide / Inject

```ts
// 祖先
provide('theme', 'dark')

// 任何后代
const theme = inject('theme', 'light') // 提供默认值
```

适合"无需 prop drilling"的场景，但不要滥用。

## 🧰 Composables

把可复用逻辑抽成函数：

```ts
// useMouse.ts
import { ref, onMounted, onUnmounted } from 'vue'

export function useMouse() {
  const x = ref(0)
  const y = ref(0)
  const onMove = (e) => {
    x.value = e.clientX
    y.value = e.clientY
  }
  onMounted(() => window.addEventListener('mousemove', onMove))
  onUnmounted(() => window.removeEventListener('mousemove', onMove))
  return { x, y }
}
```

## ⚡ 性能优化

- **`v-memo`**：跳过无需重渲染的子树
- **`shallowRef`**：大对象用 shallowRef
- **`defineAsyncComponent`**：按需加载组件
- **`KeepAlive`**：缓存组件实例

## 🧪 与 TypeScript

```vue
<script setup lang="ts">
import { ref } from 'vue'

interface User { id: string; name: string }
const user = ref<User | null>(null)

const list = ref<User[]>([])
</script>
```

## ⚠️ 常见错误

1. **解构 reactive 丢响应性** → 用 `toRefs(obj)`
2. **shallowRef 误用** → 深修改不触发更新
3. **响应式用在 props 上失败** → props 是只读的，用 computed
4. **template 用了未声明的变量** → 编辑器会红线

## 🔗 下一步

- [Nuxt](/04-meta/nuxt)
- [Pinia](/07-state/pinia)
- [Vue Router](/08-routing/vue-router)
