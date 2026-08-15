---
title: mTLS 双向认证
---

# mTLS 双向认证

## 一句话总结

> **mTLS = TLS + 客户端也要证书**。**3 大场景：服务网格 / API 网关 / 零信任**。**优势：双向身份 + 防中间人 + 强认证**。**实施：SPIFFE / SPIRE / Istio / Consul**。

---

## 单向 TLS vs mTLS

```
┌────────────────────────────────────────┐
│  单向 TLS（默认，所有 HTTPS）           │
│  客户端验证服务端证书                     │
│  服务端不验证客户端                       │
│  服务端不知道谁连它                       │
├────────────────────────────────────────┤
│  mTLS（双向）                            │
│  客户端验证服务端证书                     │
│  服务端验证客户端证书                     │
│  双方互相知道身份                         │
│  服务网格 / 零信任标配                    │
└────────────────────────────────────────┘
```

## mTLS 流程

```
Client                                              Server
   │                                                  │
   │  ClientHello + 客户端证书                        │
   │ ─────────────────────────────────────────────→ │
   │                                                  │
   │  ServerHello + 服务端证书 + CertificateRequest  │
   │ ←───────────────────────────────────────────── │
   │                                                  │
   │  CertificateVerify（客户端私钥签名）              │
   │  Finished                                       │
   │ ─────────────────────────────────────────────→ │
   │                                                  │
   │  双向验证完成，应用数据加密传输                    │
   │ ←═════════════════════════════════════════════ │
```

## 实战：Nginx mTLS

```nginx
server {
    listen 443 ssl;
    server_name api.example.com;

    ssl_certificate /etc/ssl/server.crt;
    ssl_certificate_key /etc/ssl/server.key;

    # 客户端证书验证
    ssl_client_certificate /etc/ssl/ca.crt;  # CA bundle
    ssl_verify_client on;                       # 强制 mTLS
    ssl_verify_depth 2;

    # 提取客户端信息
    location / {
        proxy_pass http://upstream;
        proxy_set_header X-Client-DN $ssl_client_s_dn;
        proxy_set_header X-Client-CN $ssl_client_s_dn_cn;
    }
}
```

## 实战：Go mTLS Server

```go
import (
    "crypto/tls"
    "crypto/x509"
    "io/ioutil"
    "log"
    "net/http"
)

func main() {
    // 加载 CA
    caCert, _ := ioutil.ReadFile("ca.crt")
    caCertPool := x509.NewCertPool()
    caCertPool.AppendCertsFromPEM(caCert)

    // TLS 配置
    tlsConfig := &tls.Config{
        ClientAuth: tls.RequireAndVerifyClientCert,
        ClientCAs:  caCertPool,
        MinVersion: tls.VersionTLS12,
    }

    server := &http.Server{
        Addr:      ":443",
        TLSConfig: tlsConfig,
    }
    log.Fatal(server.ListenAndServeTLS("server.crt", "server.key"))
}
```

## 实战：Istio 服务网格 mTLS

```yaml
# 强制命名空间内 mTLS
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: prod
spec:
  mtls:
    mode: STRICT
---
# 允许前端调用订单服务
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: order-service
  namespace: prod
spec:
  selector:
    matchLabels:
      app: order-service
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/prod/sa/frontend"]
```

## 实战：OpenSSL 生成测试证书

```bash
# 1. CA 私钥 + 证书
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -days 3650 -out ca.crt     -subj "/CN=MyCA"

# 2. 服务端证书
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr     -subj "/CN=api.example.com"
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial     -out server.crt -days 365

# 3. 客户端证书
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr     -subj "/CN=client-app"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial     -out client.crt -days 365
```

## 实战：Java mTLS Client

```java
KeyStore clientStore = KeyStore.getInstance("PKCS12");
try (InputStream is = new FileInputStream("client.p12")) {
    clientStore.load(is, "password".toCharArray());
}

KeyManagerFactory kmf = KeyManagerFactory.getInstance("SunX509");
kmf.init(clientStore, "password".toCharArray());

SSLContext sslContext = SSLContext.getInstance("TLSv1.3");
sslContext.init(kmf.getKeyManagers(), null, null);

HttpClient client = HttpClient.newBuilder()
    .sslContext(sslContext)
    .build();

HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com"))
    .build();

client.send(request, BodyHandlers.ofString());
```

## mTLS 在零信任的角色

```
┌────────────────────────────────────────┐
│  零信任 = 三件套                        │
│  ├── SPIFFE / SPIRE：身份               │
│  │   spiffe://trust-domain/workload-id  │
│  ├── mTLS：加密 + 双向认证             │
│  │   自动签发 / 短期 / 轮换             │
│  └── OPA / Cedar：策略                  │
│      "service A 可调用 service B"       │
└────────────────────────────────────────┘
```

## 实战：SPIRE 自动发证书

```bash
# 1. 启动 SPIRE Server
spire-server run -config conf/server.conf

# 2. 启动 SPIRE Agent（每个节点）
spire-agent run -config conf/agent.conf -joinToken <token>

# 3. 注册 Workload
spire-server api fetch x509svid -spiffeID spiffe://example.com/ns/prod/sa/order

# 4. 应用获取 SVID
java -jar app.jar -spiffeSocket /run/spire/sockets/agent.sock
```

## 关联章节

- **04-network/tls-pki**：TLS 证书体系
- **06-zero-trust/overview**：零信任架构
- **06-zero-trust/spiffe**：SPIFFE Workload Identity
- **cloud-native**：Istio 服务网格

## 一句话总结

> **mTLS = 双向证书认证**。**服务网格标配（Istio STRICT）**。**零信任三件套之一。自动化生命周期用 SPIRE**。
