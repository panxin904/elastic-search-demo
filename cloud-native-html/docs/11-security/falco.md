---
title: Falco 运行时检测
---

# Falco - 运行时安全

> Falco = CNCF 毕业项目，**容器运行时异常检测**。内核层监听 syscalls，发现可疑行为立刻告警。

## 🤔 为什么需要

```
PodSecurity / NetworkPolicy 只能在**启动时** / **进入时**限制
运行时：
  ❌ 容器跑起来后反 shell？
  ❌ 进程改 /etc/passwd？
  ❌ 进程监听新端口？
  ❌ 进程读 SSH 私钥？
  ❌ k8s API 异常调用？

Falco：内核层 eBPF / syscalls 监听 → 规则匹配 → 告警
```

## 🏗️ 架构

```
[Pod]   [Pod]   [Pod]
   ↓       ↓       ↓
[syscall stream (host)]
   ↓
[userspace Falco]   ← 解析 + 规则匹配
   ↓ alert
[output]   → stdout / syslog / Falcosidekick
                              ↓
                         [Slack / Elasticsearch / Lambda / S3]
```

| 组件 | 作用 |
|------|------|
| **Falco** | 引擎，监听 syscalls |
| **Falcosidekick** | 事件分发（推到多种后端） |
| **Rules** | YAML 规则（开源 + 自定义） |
| **Drivers** | `kmod`（默认）/ `bpf`（推荐）/ `modern-bpf` |

## 🚀 部署

### Helm（生产推荐）

```bash
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo update

# 装（用 eBPF probe）
helm install falco falcosecurity/falco \
  --namespace falco --create-namespace \
  --set driver.kind=modern-bpf \
  --set tty=true

# DaemonSet 会在每个 Node 跑一个 Falco
```

### 配置文件

```yaml
# /etc/falco/falco.yaml
- rule: Terminal shell in container
  desc: A shell was spawned in a container
  condition: >
    spawned_process and container and
    proc.name in (bash, sh, zsh, fish)
  output: >
    Shell spawned in container
    (user=%user.name container=%container.name
    image=%container.image.repository shell=%proc.name)
  priority: WARNING
  tags: [process, container]

- rule: Sensitive file read
  condition: >
    open_read and container and
    fd.name startswith /etc/shadow
  output: Sensitive file read by container
  priority: CRITICAL
  tags: [file, container]
```

## 📜 关键规则（默认就有）

| 规则 | 触发 |
|------|------|
| Terminal shell in container | 容器内启动 shell |
| Sensitive file read | 读 /etc/shadow / /proc/kcore |
| Crypto miner detection | 检测挖矿行为 |
| Outbound connection to C2 | 连可疑 IP |
| Container drift detected | 装新二进制 |
| Kubernetes API suspicious access | 可疑 API 调用 |

## 🔧 实战

### 检测反 shell

```yaml
# falco_rules.local.yaml
- rule: Reverse shell
  condition: >
    spawned_process and container and
    proc.cmdline contains "/dev/tcp" or
    proc.cmdline contains "bash -i" or
    proc.cmdline contains "nc -e"
  output: "Reverse shell detected: %proc.cmdline"
  priority: CRITICAL
  tags: [process, security]
```

```bash
# 应用
kubectl -n falco create configmap falco-rules \
  --from-file=falco_rules.local.yaml

# 改 falco daemonset 挂载
helm upgrade falco ... \
  --set customRules.customRules={falco_rules.local.yaml}
```

### 输出到 Slack

```yaml
# falcosidekick
config:
  webhook:
    address: "https://hooks.slack.com/services/xxx"
```

```bash
helm install sidekick falcosecurity/falcosidekick -n falco
```

## 🪜 进阶

### 自定义规则

```yaml
- rule: My App Config Changed
  condition: >
    open_write and container and
    fd.name startswith /etc/myapp/ and
    not proc.name in (myapp, myapp-migrator)
  output: Config file modified
  priority: WARNING
  tags: [config]
```

### 异常行为画像

```yaml
- rule: Container started with unexpected shell
  condition: >
    container_started and container and
    proc.name in (bash, sh, zsh) and
    not container.image.repository in (allowed_images)
  output: Unexpected shell
  priority: WARNING
```

## 📊 告警分发架构

```
[Falco] → [Falcosidekick] → 各种后端
              ├─ Slack
              ├─ Elasticsearch
              ├─ Loki
              ├─ S3 / GCS
              ├─ Lambda / Cloud Function
              ├─ Kafka
              └─ Opsgenie / PagerDuty
```

## 🛠 实战

```bash
# 1. 装
helm install falco falcosecurity/falco -n falco --create-namespace \
  --set driver.kind=modern-bpf

# 2. 看 Falco 日志
kubectl -n falco logs -l app.kubernetes.io/name=falco -f

# 3. 装 sidekick 推到 Slack
helm install sidekick falcosecurity/falcosidekick -n falco \
  --set config.webhook.address=https://hooks.slack.com/xxx

# 4. 写自定义规则
# 写 falco_rules.local.yaml
# 挂到 configmap
# 重启 Falco

# 5. 测试
# Pod 里跑
kubectl exec -it <pod> -- bash
# 看 Falco 告警
```

## 🩹 故障

```bash
# Falco pod 启动失败
kubectl -n falco logs -l app.kubernetes.io/name=falco
# 通常：内核不支持 eBPF / 缺特权

# 告警太多（告警疲劳）
# 解决：精简规则 + 提高 priority 阈值 + 用 Falcosidekick 路由

# 性能开销
# eBPF 几乎无开销，kmod 略大
```

## 🆚 vs 其他

| | Falco | Tracee | Tetragon |
|--|-------|--------|----------|
| 出品 | Sysdig | Aqua | Cilium |
| 引擎 | eBPF / kmod | eBPF | eBPF |
| 规则 | YAML | Rego / eBPF | YAML |
| 集成 | 广 | 较强 | Cilium 一体化 |

## 🔗 下一步

- [RBAC](/11-security/rbac)
- [NetworkPolicy + PodSecurity](/11-security/policy)
- [Secret 管理](/11-security/secret)