---
layout: home

hero:
  name: "Android"
  text: "安卓全栈知识图谱"
  tagline: "Kotlin · Jetpack · Compose · 系统层 · 跨平台 · 性能优化"
  image:
    src: /favicon.svg
    alt: Android
  actions:
    - theme: brand
      text: 开始学习
      link: /path
    - theme: alt
      text: 知识图谱
      link: /mindmap

features:
  - title: 🧱 应用层
    details: Kotlin 协程 / Jetpack ViewModel + Hilt + Room + WorkManager / Flow 响应式数据流 / Compose 声明式 UI。
    link: /01-app/
    linkText: 进入章节
  - title: 🎨 UI 体系
    details: View 体系（Activity / Fragment / RecyclerView）/ Compose 状态管理 + Material 3 / 主题切换 + 屏幕适配。
    link: /02-ui/
    linkText: 进入章节
  - title: ⚙️ 系统层
    details: 启动流程（Boot → Zygote → SystemServer）/ Binder IPC / ART 运行时 / AMS WMS PMS IMS 框架服务。
    link: /03-system/
    linkText: 进入章节
  - title: 🌐 跨平台
    details: Flutter / React Native / Kotlin Multiplatform / Compose Multiplatform / 选型决策（性能 vs 一致性）。
    link: /04-cross/
    linkText: 进入章节
  - title: 🛠️ 工具链
    details: Gradle KTS + AGP + Build Variants / Android Studio Profiler + Layout Inspector / APK Analyzer / App Bundle。
    link: /05-toolchain/
    linkText: 进入章节
  - title: 🚀 性能与安全
    details: 启动优化 + Baseline Profile + Macrobenchmark / 内存泄漏 + OOM / ANR / 包大小 / 权限 + Keystore + 证书钉扎。
    link: /06-perf/
    linkText: 进入章节


---

<script setup>
const painPoints = [
  "Activity / Fragment 生命周期混乱：屏幕旋转后 ViewModel 数据丢失？",
  "协程作用域错位：GlobalScope / viewModelScope / lifecycleScope 该用哪个？",
  "Compose 与 View 混用：状态同步、重组范围、跨进程通信怎么搞？",
  "应用卡顿 / ANR / OOM 频发：怎么定位是主线程、IO 还是渲染？",
  "包大小爆炸：从 30MB 涨到 80MB，R8 / 资源压缩 / ABI 拆分怎么做？",
  "跨平台选型纠结：Flutter / RN / KMP 哪个 ROI 最高？"
]
const goals = [
  "Kotlin 协程 + Flow + ViewModel 全套应用层模式",
  "Jetpack Compose 状态管理 + Material 3",
  "系统层四大金刚（Binder / Handler / AMS / WMS）",
  "跨平台选型决策（Flutter / RN / KMP）",
  "Gradle 构建优化（KTS / 插件 / 加速）",
  "性能基线（启动 / 内存 / 包大小 / ANR）"
]
const relatedSites = [
  { site: "frontend", path: "/path", label: "前端（Android 应用层本质是客户端开发）" },
  { site: "java-language", path: "/path", label: "Java 语言（Android 历史主语言 + JVM 基础）" },
  { site: "java", path: "/path", label: "Java Web（Android 后端联调 / OkHttp）" },
  { site: "iot", path: "/path", label: "物联网（Android Things / Embedded）" },
  { site: "rust", path: "/path", label: "Rust（Android 系统层 NDK / Native）" },
  { site: "linux", path: "/path", label: "Linux（Android 基于 Linux Kernel）" },
  { site: "security", path: "/path", label: "安全（权限模型 / 密钥库 / mTLS）" },
  { site: "observability", path: "/path", label: "可观测性（性能监控 / Crash 上报）" }
]
</script>

<ClientOnly>
  <WhyThisGraph
    :pain-points="painPoints"
    :goals="goals"
    :related-sites="relatedSites"
    title="🎯 为什么写这个图谱？"
  />
</ClientOnly>
