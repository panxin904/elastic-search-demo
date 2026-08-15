---
title: Curator
category: ops
graphNodeId: curator
---

<span class="kg-badge kg-badge-ops">运维层</span>

# Curator

## 📌 一句话定义
Curator 是 Elastic 官方的**索引管理 CLI 工具**，用于批量删除、合并、快照索引。

> ⚠️ ES 5.x 之后，**ILM** 替代了部分 Curator 场景。但 Curator 在**跨索引管理**和**精细控制**上仍有优势。

## 📦 安装

```bash
pip install elasticsearch-curator
```

## 🔧 配置文件

`curator.yml`（连接配置）：
```yaml
client:
  hosts: [ "http://es01:9200" ]
  http_auth: "user:pass"
```

`actions.yml`（动作配置）：
```yaml
actions:
  1:
    action: delete_indices
    description: "Delete indices older than 30 days"
    filters:
    - filtertype: age
      source: name
      direction: older
      timestring: '%Y.%m.%d'
      unit: days
      unit_count: 30
```

## 🔧 常用动作

| Action | 用途 |
|---|---|
| `delete_indices` | 删除索引 |
| `close_indices` | 关闭索引 |
| `forcemerge` | 合并段 |
| `reindex` | 重建索引 |
| `snapshot` | 创建快照 |
| `restore` | 恢复 |
| `alias` | 别名管理 |

## 🕐 定时执行

```bash
# crontab 每天凌晨 3 点执行
0 3 * * * curator --config curator.yml actions.yml
```

## 📊 示例：批量清理旧日志索引

```yaml
actions:
  1:
    action: delete_indices
    filters:
    - filtertype: pattern
      kind: prefix
      value: logs-
    - filtertype: age
      source: creation_date
      direction: older
      unit: days
      unit_count: 7
```

## 🆚 Curator vs ILM

| 维度 | Curator | ILM |
|---|---|---|
| 配置 | YAML 文件 | ES API |
| 运行 | 外部 cron | ES 内部自动 |
| 灵活性 | 高 | 中（按阶段） |
| 适用 | **复杂跨索引管理** | 简单时间/大小策略 |

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="curator" :height="400" />

## 📚 延伸阅读
- [ILM 生命周期](/04-ops/ilm)
- [Snapshot 备份](/04-ops/snapshot)
