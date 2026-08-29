---
title: 反外挂
date: 2026-08-27  # date-auto-injected
---

# 反外挂

> 反外挂三支柱：服务器权威 / 加密协议 / 行为检测。

## 🎯 核心要点

- 服务器权威：关键逻辑放服务器，客户端只渲染
- 加密协议：防协议分析 / 中间人
- 行为检测：机器学习分析异常操作
- 商用：EAC（Easy Anti-Cheat）/ BattlEye / VAC

## 🛠️ 实战示例

```text
# 关键逻辑放服务器（伪代码）
# 错误：客户端计算伤害
if hit_check() and damage > 0:
  apply_damage(target)
# 正确：服务器验证
def on_damage_request(attacker, target, amount):
  if not server_hit_check(attacker, target):
    return  # 作弊拦截
  target.hp -= amount
```

## 🔗 相关链接

- [一致性](./consistency)
- [联机架构](./arch)
- [← 返回 网络 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[同步模型](./sync) / [架构](./arch)

## 🛠️ 实战提示

关键逻辑放服务器是反外挂的根本。

## 🔗 延伸阅读

- [GameDev.net](https://www.gamedev.net/)
- [GDC Vault](https://www.gdcvault.com/)
- [Unity Manual](https://docs.unity3d.com/Manual/index.html)
- [Unreal Engine Docs](https://docs.unrealengine.com/)


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
