---
title: CoAP
---

# CoAP

> 受限应用协议，基于 UDP 的 RESTful 架构。低功耗设备首选，比 HTTP 协议头更小。

## 🎯 核心要点

- 协议基于 UDP，默认端口 5683 / DTLS 5684
- 方法同 HTTP（GET/POST/PUT/DELETE）
- 资源发现（`.well-known/core`）
- 观察模式（订阅资源变化，类似 WebSocket）
- 适用场景：电池供电设备 / 网络不稳定 / 资源受限

## 🛠️ 实战示例

```javascript
# Node.js coap 客户端
const coap = require("coap");
const req = coap.request("coap://californium.eclipseprojects.io:5683/.well-known/core");
req.on("response", (res) => {
  console.log(res.payload.toString());
});
req.end();
```

## 🔗 相关链接

- [MQTT](./mqtt)
- [Modbus](./modbus)
- [← 返回 通信协议 目录](./)
- [← 返回 iot 首页](../)
## 🎯 CoAP 实战建议

- **资源 URI 设计**：分层结构 `/device/{id}/sensor/{type}`
- **CoAP over DTLS**：用 PSK（预共享密钥）或证书认证
- **观察模式**：适合周期性上报（类似 WebSocket）
- **调试工具**：libcoap / copper (Firefox 插件，已废弃) / Wireshark
