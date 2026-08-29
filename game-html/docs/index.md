---
layout: home

hero:
  name: "Game"
  text: "游戏开发全栈知识图谱"
  tagline: "Unity · Unreal · Godot · 渲染 · 物理 · AI · 网络"
  image:
    src: /favicon.svg
    alt: Game
  actions:
    - theme: brand
      text: 开始学习
      link: /path
    - theme: alt
      text: 知识图谱
      link: /mindmap

features:
  - title: 🎮 游戏引擎
    details: Unity（C# / DOTS / ECS / Addressables）/ Unreal（C++ / Blueprint / Nanite / Lumen）/ Godot（GDScript / C# / Vulkan）/ 引擎选型决策（团队 / 项目 / 平台）。
    link: /path
    linkText: 引擎入门
  - title: 🎨 渲染管线
    details: OpenGL / Vulkan / Metal / DirectX 12 / WebGPU；渲染管线（前向 / 延迟 / Clustered）；PBR / 光线追踪 / 后处理 / Shader（HLSL / GLSL / MSL）。
    link: /path
    linkText: 渲染原理
  - title: ⚙️ 物理与数学
    details: 碰撞检测（AABB / OBB / GJK / SAT）/ 刚体动力学 / 软体（布料 / 毛发）/ 流体（SPH / PBD）/ 数值稳定性（Verlet / RK4）。
    link: /path
    linkText: 物理仿真
  - title: 🤖 游戏 AI
    details: 有限状态机（FSM）/ 行为树（BT）/ 目标导向行动规划（GOAP）/ 效用系统 / 寻路（A* / NavMesh / Flow Field）/ 强化学习（DQN / PPO）。
    link: /path
    linkText: AI 设计
  - title: 🌐 网络与同步
    details: 状态同步 vs 帧同步 / 客户端预测 / 服务器权威 / 延迟补偿 / 反外挂（服务器校验 / 行为分析）/ WebSocket / UDP（KCP / ENet）。
    link: /path
    linkText: 多人游戏
  - title: 🛠️ 工具链与发布
    details: Git LFS（模型 / 贴图）/ Asset Bundle / Steamworks SDK / Epic Online Services / Asset Pipeline / CI/CD（Unity Cloud Build / Jenkins）/ 自动化测试。
    link: /path
    linkText: 工程实践
---

<script setup>
const painPoints = [
  "引擎选型纠结：Unity / Unreal / Godot 哪个更适合我的项目？",
  "渲染卡顿 / 帧率不稳：Draw Call 爆炸 / Shader 编译 / GPU 带宽瓶颈？",
  "物理穿透 / 抖动 / 速度异常：浮点精度 / 碰撞体配置 / 时间步长？",
  "敌人 AI 太死板：FSM 不够灵活 / 行为树不会调试 / 寻路卡墙？",
  "多人游戏外挂泛滥：客户端能改内存 / 状态不同步 / 怎么服务器校验？",
  "包体过大 / 启动慢：Asset Bundle 怎么分包 / 怎么热更新？",
]
const goals = [
  "三大引擎对比与选型（Unity / Unreal / Godot）",
  "现代渲染管线（PBR / 光追 / 后处理）",
  "物理仿真（碰撞检测 / 刚体 / 流体）",
  "游戏 AI（FSM / 行为树 / 寻路）",
  "网络同步（状态同步 / 帧同步 / 反外挂）",
  "工具链（Git LFS / Asset Bundle / Steamworks）",
]
const relatedSites = [
  { site: "frontend", path: "/path", label: "前端（Web 游戏 / Canvas / WebGL）" },
  { site: "android", path: "/path", label: "Android（手游客户端开发）" },
  { site: "rust", path: "/path", label: "Rust（高性能游戏引擎 / Bevy）" },
  { site: "ai", path: "/path", label: "AI（游戏 AI / NPC 决策）" },
  { site: "network", path: "/path", label: "网络（多人游戏同步）" },
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

## 📚 相关阅读（跨站导航）

<!-- xlink-injected:do-not-edit -->

按主题跨站推荐：

- [frontend](https://java-px.bot.cd/frontend/)：客户端基础
- [rust](https://java-px.bot.cd/rust/)：高性能原生
- [ai](https://java-px.bot.cd/ai/)：NPC AI
- [network](https://java-px.bot.cd/network/)：联机同步
- [linux](https://java-px.bot.cd/linux/)：Linux 平台
- [python](https://java-px.bot.cd/python/)：脚本与工具


<!-- auto-enrich:do-not-edit -->

## 实战示例

```bash
# TODO: 在此补充本页主题的实战命令
echo "hello"
```

```yaml
# TODO: 配置示例
key: value
```

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料
<!-- auto-enrich:do-not-edit -->
