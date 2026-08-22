---
title: 游戏开发知识图谱
---

# 🗺️ 游戏开发知识图谱

> 本页用 Mermaid mindmap 展示游戏开发全栈知识结构。

```mermaid
mindmap
  root((游戏开发))
    引擎层
      商业引擎
        Unity
        Unreal Engine
        Godot
      自研引擎
        ECS 架构
        渲染抽象 RHI
        资源管理
      选型决策
        平台目标
        团队规模
        预算 / License
        性能需求
    渲染
      渲染管线
        前向渲染
        延迟渲染
        Clustered / Tiled
        光线追踪
      光照
        PBR / IBL
        阴影算法
        全局光照 GI
      着色器
        HLSL / GLSL
        Shader Graph
        Compute Shader
      后处理
        Bloom / DOF / SSAO
        抗锯齿 TAA / SMAA
        Color Grading
    物理
      碰撞检测
        AABB / OBB
        GJK / SAT
        空间分割
          四叉树
          BVH
          NavMesh
      刚体动力学
        Verlet 积分
        约束求解
        PhysX / Bullet
      柔体
        弹簧质点
        布料模拟
        流体 SPH
    AI
      寻路
        A* / Dijkstra
        NavMesh
        Flow Field
        D* Lite
      决策
        FSM 有限状态机
        行为树 BT
        效用系统
        GOAP 规划
      机器学习
        强化学习
        神经网络 NPC
        群体模拟 Boids
    网络
      同步模型
        状态同步
        帧同步 Lockstep
        快照同步
      一致性
        客户端预测
        服务器仲裁
        回放录像
      反外挂
        服务器权威
        加密协议
        行为检测
      联机架构
        C/S 房间制
        P2P Host 迁移
        Matchmaker
    音频
      空间音频
        HRTF 头相关
        3D 衰减
        声障遮挡
      动态混音
        Snapshot 切换
        实时参数
        音效总线
      音效
        Wwise / FMOD
        事件驱动
        音乐自适应
    工具链
      资产管线
        FBX / glTF
        LOD 生成
        纹理压缩
        Addressable
      版本控制
        Git LFS
        Perforce Helix
        分支策略
      构建发布
        平台构建脚本
        CI/CD
        Steam / 主机 SDK
    性能与上线
      性能
        Draw Call 优化
        GC / 内存池
        帧率稳定
        移动端功耗
      上线
        多平台适配
        主机认证
        反作弊对接
        数据埋点
```

## 阅读建议

- **引擎使用者**：从引擎选型 → 渲染管线 → 着色器 入手，掌握一个 DCC 工作流
- **图形程序员**：渲染管线 → 光照 → 着色器 → GPU 优化，最后补 Compute / 光追
- **AI / 网络程序员**：寻路 → 行为树 → 同步模型，重点掌握一致性和反外挂
- **工具链工程师**：资产管线 → 版本控制 → CI/CD，关注资产膨胀和构建时长

## 在图谱中的位置

游戏开发是 frontend（客户端开发延伸）+ rust（高性能原生）+ ai（NPC / 寻路）+ network（联机同步）的横切栈。客户端开发基础是底盘；想深入图形 / 引擎底层，建议补 rust + 数学（线性代数）；要做联机，必看 network + 反外挂。
