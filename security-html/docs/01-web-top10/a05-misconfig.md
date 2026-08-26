---
title: A05 安全配置错误
---

# A05 · Security Misconfiguration（安全配置错误）

## 一句话总结

> **A05 = 默认 / 调试 / 错误配置**。**典型：默认密码 admin/admin / .git 暴露 / 堆栈信息泄漏 / debug 模式 / 卸载的组件残留**。**防御：硬化清单 + 持续审计 + IaC**。

---

## 常见配置错误

| 错误 | 危害 |
|------|------|
| 默认密码 admin/admin | 攻击者常用字典直接打 |
| 暴露 `.git` / `.env` | 源码 + 密钥泄漏 |
| Spring Boot Actuator 全开 | /env /heapdump 拉密钥 |
| PHP `display_errors=on` | 堆栈信息暴露文件路径 |
| Docker 监听 0.0.0.0:2375 | 远程 Docker 完全控制 |
| K8s Dashboard 公网 | 集群一键接管 |
| 卸载残留的 demo / test 路由 | 攻击者未授权访问 |
| CORS `*` + 凭证 | 跨域带 cookie |
| 目录列举 | 文件结构暴露 |

## 实战：Spring Boot Actuator 暴露

```yaml
# ❌ 不安全：暴露所有 endpoint
management:
  endpoints:
    web:
      exposure:
        include: "*"

# ✅ 安全：只暴露 health + prometheus
management:
  endpoints:
    web:
      exposure:
        include: "health,prometheus"
  endpoint:
    health:
      show-details: when-authorized
```

```bash
# 攻击路径
$ curl https://target.com/actuator/env
# 拿到所有环境变量，包括 AWS_ACCESS_KEY / 数据库密码
```

## 实战：Nginx 配置错误

```nginx
# ❌ 错误：目录列举
server {
    location / {
        root /var/www/app;
        autoindex on;  # 危险！
    }
}

# ✅ 正确：禁止
server {
    location / {
        root /var/www/app;
        autoindex off;
    }
}
```

## 实战：Kubernetes Dashboard

```yaml
# ❌ 默认配置（公开暴露）
apiVersion: v1
kind: Service
metadata:
  name: kubernetes-dashboard
spec:
  type: LoadBalancer  # 公网可访问！
  ports:
    - port: 443
      targetPort: 8443
```

## 实战：Docker 远程 API

```bash
# 默认 /etc/docker/daemon.json
{
  "hosts": ["tcp://0.0.0.0:2375", "unix:///var/run/docker.sock"]
}
# 攻击者直接 docker -H tcp://target:2375 run -it alpine sh
```

## 防御清单

| 措施 | 落地 |
|------|------|
| **硬化基线** | CIS Benchmark（OS / K8s / DB） |
| **IaC 扫描** | tfsec / checkov / Snyk IaC |
| **持续审计** | Trivy / ScoutSuite / Prowler |
| **环境隔离** | dev/staging/prod 严格隔 |
| **默认 deny** | 防火墙 + NetworkPolicy |
| **环境变量管理** | Vault / Sealed Secrets |
| **错误处理** | 生产关闭 debug 模式 |

## 自动化扫描

```bash
# CIS benchmark
docker run --net host --pid host --userns host --cap-add audit_control     -e DOCKER_CONTENT_TRUST=$DOCKER_CONTENT_TRUST     --label docker_bench_security     docker/docker-bench-security

# 配置扫描
prowler aws --severity critical
```

## 关联章节

- **01-web-top10/a01-broken-access**：A01 默认允许
- **04-network/hsts-csp**：HTTP 安全头
- **05-container/overview**：容器配置安全

## 一句话总结

> **A05 配置错误 = 默认不安全**。**核心：硬化基线 + 自动审计 + 生产最小开放**。**Debug / 默认密码 / 暴露接口 = 前 3 大常见**。


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
