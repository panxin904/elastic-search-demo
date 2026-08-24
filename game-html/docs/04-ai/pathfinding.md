---
title: 寻路
---

# 寻路

> 寻路算法：A* / Dijkstra / NavMesh / Flow Field / D* Lite，NPC 移动核心。

## 🎯 核心要点

- A*：启发式搜索，最常用
- Dijkstra：无启发式，最短路径
- NavMesh：导航网格，预烘焙
- Flow Field：RTS 大规模寻路
- D* Lite：动态障碍物寻路

## 🛠️ 实战示例

```text
// A* 简化实现（伪代码）
function AStar(start, goal):
  open = PriorityQueue([(0, start)])
  cameFrom = {}
  while open not empty:
    current = open.pop()
    if current == goal: return reconstruct(cameFrom)
    for neighbor in neighbors(current):
      tentative = gScore[current] + dist(current, neighbor)
      if tentative < gScore[neighbor]:
        cameFrom[neighbor] = current
        gScore[neighbor] = tentative
        fScore = tentative + heuristic(neighbor, goal)
        open.push((fScore, neighbor))
```

## 🔗 相关链接

- [决策系统](./decision)
- [碰撞检测](../03-physics/collision)
- [← 返回 AI 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[决策系统](./decision)

## 🛠️ 实战提示

A* 是必学，NavMesh 是引擎标配。

## 🔗 延伸阅读

- [GameDev.net](https://www.gamedev.net/)
- [GDC Vault](https://www.gdcvault.com/)
- [Unity Manual](https://docs.unity3d.com/Manual/index.html)
- [Unreal Engine Docs](https://docs.unrealengine.com/)
