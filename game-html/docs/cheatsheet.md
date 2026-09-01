---
title: 游戏开发速查表
date: 2026-08-22  # date-auto-injected
---

# 🧾 游戏开发速查表

> 引擎版本 / 数学公式 / 寻路算法 / 物理参数 / Shader 关键字 一页速查。

## 主流引擎版本

| 引擎 | 当前稳定版 | LTS | 语言 | 包大小 |
|---|---|---|---|---|
| Unity | 6000.x (Unity 6) | 2022 LTS | C# | ~250MB |
| Unreal Engine | 5.4 / 5.5 | 5.3 | C++ / Blueprint | ~150MB |
| Godot | 4.3 / 4.4 | — | GDScript / C# | ~30MB |

## 关键数学公式

### 向量运算

```text
点积（Dot）：a · b = |a| × |b| × cos(θ)
  用于：判断朝向 / 光照衰减 / 投影长度

叉积（Cross）：a × b = |a| × |b| × sin(θ)
  用于：法线计算 / 左右判断 / 三角形面积

反射：R = D - 2(D · N)N
  用于：镜面反射 / 弹球
```

### 矩阵变换

```text
世界变换 = Scale × Rotation × Translation (TRS)
视图变换 = View Matrix（摄像机位置 / 朝向）
投影变换 = Projection Matrix（透视 / 正交）

MVP = Projection × View × World
```

### 坐标系

- **左手系**：Unity / Unreal / Godot 默认（Y 向上，Z 向前）
- **右手系**：DirectX / OpenGL 默认（Y 向上，-Z 向前）
- **屏幕坐标**：左下角 (0, 0)，右上角 (W, H)

## Shader 关键字速查

### HLSL / GLSL 共通

```glsl
// 顶点着色器输入
struct VS_INPUT {
    float3 pos : POSITION;
    float3 normal : NORMAL;
    float2 uv : TEXCOORD0;
};

// 像素着色器输出
struct PS_OUTPUT {
    float4 color : SV_Target;
};

// 常用语义（HLSL）
POSITION     // 顶点位置
NORMAL       // 法线
TEXCOORD0    // UV / 顶点数据
SV_Target    // 像素输出
SV_VertexID  // 顶点索引
```

### Unity URP / Shader Graph 关键字

```text
_ MainTex          主纹理
_ NormalMap        法线贴图
_ BaseColor        基础颜色（URP）
_ Metallic        金属度
_ Smoothness      光滑度
_ EmissionColor   自发光
```

## 寻路算法复杂度

| 算法 | 时间复杂度 | 空间复杂度 | 适合 |
|---|---|---|---|
| BFS | O(V + E) | O(V) | 无权图 |
| Dijkstra | O((V+E) log V) | O(V) | 正权图 |
| A* | O((V+E) log V) | O(V) | 有启发式的最优 |
| NavMesh | O(P log P)，P=多边形 | O(P) | 开放世界 |
| Flow Field | O(V) 一次 | O(V) | 大量单位同目标 |
| D* Lite | O(E log V) | O(V) | 动态障碍 |

## 物理参数表

### 刚体参数

```text
质量 Mass：单位 kg
重力 Gravity：默认 (0, -9.81, 0) m/s²
阻力 Drag：0 = 无阻力，1 = 立即停止
角阻力 Angular Drag：旋转阻力
```

### 常用物理材质（Unity Physic Material）

```text
Dynamic Friction：动态摩擦（运动时）
Static Friction：静态摩擦（启动时）
Bounciness：弹性（0-1）
Friction Combine：Average / Min / Max / Multiply
Bounce Combine：同上
```

### 触发器条件

| 组合 | 行为 |
|---|---|
| 两个 Collider 都非 Is Trigger | 物理碰撞 |
| 任一 Is Trigger | 触发事件，无物理推力 |
| 两个 Rigidbody | 完整物理响应 |
| 一个 Kinematic | 不受力，但可推动非 Kinematic |

## 网络协议对比

| 协议 | 可靠 | 速度 | 适合 |
|---|---|---|---|
| TCP | ✓ | 慢 | 登录 / 支付 |
| UDP | ✗ | 快 | 实时游戏 |
| KCP | ✓ | 较快 | 自研可靠 UDP |
| ENet | ✓ | 中 | Unity / Godot 内置 |
| WebSocket | ✓ | 中 | Web 游戏 |
| WebRTC | ✓ | 低延迟 | Web P2P |

## 关键性能指标

```text
帧率 FPS：30 / 60 / 120 / 144
帧时间：33ms / 16ms / 8ms / 7ms
Draw Call 预算：PC ≤ 3000 / 移动 ≤ 200
三角形预算：PC ≤ 100 万 / 移动 ≤ 30 万
纹理内存：移动 ≤ 50MB / PC ≤ 500MB
GC 时间：单帧 ≤ 2ms（Unity C#）
网络抖动：≤ 100ms 可玩 / ≤ 50ms 流畅
```

## 常用命令（Unity 编辑器）

```bash
# 命令行批处理构建
Unity -batchmode -projectPath . -buildTarget Android -executeMethod BuildScript.BuildAndroid -quit

# 清空 Library 缓存（解决诡异编译错误）
rm -rf Library/ScriptAssemblies/ Temp/

# 强制重导入资源
touch Assets && find Assets -name "*.meta" -exec touch {} \;
```

## 调试快捷键

| 引擎 | 快捷键 | 功能 |
|---|---|---|
| Unity | F | 聚焦选中物体 |
| Unity | Shift+F | 锁定跟随相机 |
| Unity | Ctrl+Shift+C | 显示 / 隐藏 Collider |
| Unity | Ctrl+Alt+F | 帧率限制 60/30 |
| Unreal | F8 | Eject（脱离玩家控制） |
| Unreal | F11 | Simulate 模拟模式 |
| Godot | F1 | 帮助 / F5 运行场景 |

## 资产导入设置速查

### 纹理（Texture）

```
纹理类型：Default / Normal map / Sprite
压缩格式：移动 ASTC / PC DXT5 / iOS ASTC
Mip Maps：开启（3D）/ 关闭（UI）
sRGB：颜色纹理开 / 法线贴图关
过滤：Trilinear（3D）/ Bilinear（UI）
各向异性：8-16（地面）
```

### 模型（Model）

```
Scale Factor：1
Import Normals：Calculate / Import
Import Tangents：Calculate MikkTSpace（推荐）
Rig：Generic / Humanoid
Optimize Mesh：开启
Read/Write Enabled：按需（开启可运行时访问顶点）
```


## 📱 手机扫码继续阅读

<ClientOnly>
  <QrShare />
</ClientOnly>
