---
title: 一致性
---

# 一致性

> 网络一致性三大难题：客户端预测 / 服务器仲裁 / 回放录像。

## 🎯 核心要点

- 客户端预测：本地先响应 + 服务器确认后校正
- 服务器仲裁：服务器是唯一真相源
- 回放录像：记录输入流，任意时刻回放
- 锁步：所有客户端严格按帧同步（确定性）

## 🛠️ 实战示例

```text
// 客户端预测 + 服务器校正（伪代码）
void onLocalInput(input) {
  applyLocally(input);  // 本地立即响应
  sendToServer(input);
}
void onServerState(state) {
  if (state.sequence > lastAppliedSequence) {
    correctToState(state);  // 服务器校正
  }
}
```

## 🔗 相关链接

- [同步模型](./sync)
- [反外挂](./anticheat)
- [← 返回 网络 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[同步模型](./sync) / [反外挂](./anticheat)

## 🛠️ 实战提示

客户端预测 + 服务器仲裁是主流方案。

## 🔗 延伸阅读

- [GameDev.net](https://www.gamedev.net/)
- [GDC Vault](https://www.gdcvault.com/)
- [Unity Manual](https://docs.unity3d.com/Manual/index.html)
- [Unreal Engine Docs](https://docs.unrealengine.com/)
