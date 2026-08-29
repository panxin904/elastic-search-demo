---
title: Job / CronJob
date: 2026-08-15  # date-auto-injected
---

# Job / CronJob - 一次性 / 定时任务

> Deployment 管"常驻服务"，Job 管"跑完就结束"的任务。

## 🤔 典型场景

```
✅ 数据批处理（每天跑 ETL）
✅ 邮件发送
✅ 备份脚本
✅ 报告生成
✅ 定期清理

Job     = 跑一次到成功
CronJob = 按 cron 周期跑
```

## 📜 Job manifest

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: data-migration
spec:
  completions: 1                # 期望完成 1 次
  parallelism: 1                # 并行度（同时跑几个 Pod）
  backoffLimit: 3               # 失败重试次数
  activeDeadlineSeconds: 600    # 超时（10 分钟）
  template:
    spec:
      restartPolicy: OnFailure  # Job 必须是 OnFailure / Never
      containers:
      - name: migrate
        image: migrate:1.0
        env:
        - name: DB_URL
          value: postgres://...
```

`completions: 1` 跑一次就完。

### 并行 Job

```yaml
spec:
  completions: 100              # 100 个任务
  parallelism: 5                # 同时最多 5 个 Pod
  completionMode: Indexed       # 每个 Pod 拿 0..99 的索引
  template:
    spec:
      containers:
      - name: worker
        image: worker:1.0
        command: ["./worker.sh"]
        env:
        - name: INDEX
          valueFrom:
            fieldRef: { fieldPath: metadata.labels['batch.kubernetes.io/job-completion-index'] }
```

## 📜 CronJob manifest

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-daily
spec:
  schedule: "0 2 * * *"          # 每天 02:00（5 字段：分 时 日 月 周）
  timezone: "Asia/Shanghai"      # 必加，否则是 UTC
  startingDeadlineSeconds: 100  # 错过时间后 100s 内还跑
  successfulJobsHistoryLimit: 3  # 保留几次成功历史
  failedJobsHistoryLimit: 3      # 保留几次失败历史
  concurrencyPolicy: Forbid     # Allow / Forbid / Replace
  jobTemplate:
    spec:
      backoffLimit: 2
      activeDeadlineSeconds: 3600
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: backup
            image: backup:1.0
            args: ["./run.sh"]
            env:
            - name: BUCKET
              value: s3://my-backup/
```

## ⏰ cron 表达式

```
分 时 日 月 周
*  *  *  *  *

特殊字符：
*  任意
,  列表（1,3,5）
-  范围（1-5）
/  步长（*/5）

示例：
*/5 * * * *       每 5 分钟
0 2 * * *        每天 02:00
0 0 * * 0        每周日 0 点
0 9 * * 1-5      工作日 09:00
*/15 9-17 * * *   工作时间每 15 分钟
```

## 🔧 重要字段

| 字段 | 作用 |
|------|------|
| `completions` | 完成次数 |
| `parallelism` | 并行 Pod 数 |
| `backoffLimit` | 重试次数 |
| `activeDeadlineSeconds` | 超时 |
| `ttlSecondsAfterFinished` | 完成 N 秒后自动删 Job + Pod |
| `concurrencyPolicy` | Allow / Forbid / Replace |

```yaml
spec:
  ttlSecondsAfterFinished: 86400  # 完成 24h 后自动清理
```

## 🛠 实战

### 跑一次

```bash
# 创建
kubectl apply -f job.yaml

# 看
kubectl get jobs
kubectl get pods -l job-name=data-migration

# 看日志
kubectl logs -f job/data-migration

# 看状态
kubectl describe job data-migration
```

### 手动触发 CronJob

```bash
# 创建 Job 立刻跑（不等下次 schedule）
kubectl create job manual-run --from=cronjob/backup-daily

# 删历史
kubectl delete job backup-daily-1234567
```

### 看 CronJob 历史

```bash
kubectl get cronjob
kubectl get jobs -l cronjob=backup-daily
# 看每次跑出来的 Job
```

## 🩹 故障

```bash
# Job 一直 Pending
kubectl describe job <name>
kubectl get events --field-selector involvedObject.name=<pod>

# Job 失败
kubectl logs job/<name>
# 看 BackoffLimitExceeded → 失败次数超了

# CronJob 没跑
kubectl get cronjob
kubectl get events --field-selector involvedObject.name=<cronjob>
# 看是不是 schedule 写错
# 测 cron：
kubectl run test --image=busybox --schedule="*/1 * * * *" --dry-run=client -o yaml | grep schedule
```

## 🆚 vs 传统 cron

| | k8s CronJob | Linux cron |
|--|------------|------------|
| 集群 | 多 Node 抢着跑 | 单机 |
| 失败告警 | 集成 Prometheus | 自己接 |
| 跳过补跑 | `startingDeadlineSeconds` | ❌ |
| 历史 | 自动保留 N 个 | ❌ |
| 跨时区 | 需显式 timezone | 默认本机 |

## 🔗 下一步

- [Pod 最小单元](/03-k8s-workload/pod)
- [Deployment](/03-k8s-workload/deployment)
- [DaemonSet](/03-k8s-workload/daemonset)