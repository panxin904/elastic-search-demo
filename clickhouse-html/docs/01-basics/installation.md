---
title: 安装部署
date: 2026-08-15  # date-auto-injected
description: ClickHouse 单机 / 集群 / Docker / Kubernetes / 云服务全模式安装指南
---

# 安装部署

## 单机部署（最简方式）

### Debian / Ubuntu

```bash
# 添加官方仓库
sudo apt-get install -y apt-transport-https ca-certificates dirmngr
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 8919F6BD2B48D754
echo "deb https://packages.clickhouse.com/deb stable main" | sudo tee /etc/apt/sources.list.d/clickhouse.list
sudo apt-get update

# 安装 server 和 client
sudo apt-get install -y clickhouse-server clickhouse-client

# 启动（默认 9000 端口）
sudo service clickhouse-server start
clickhouse-client  # 进入交互式客户端
```

### CentOS / RHEL

```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://packages.clickhouse.com/rpm/clickhouse.repo
sudo yum install -y clickhouse-server clickhouse-client

sudo /etc/init.d/clickhouse-server start
clickhouse-client
```

### macOS（开发用）

```bash
brew install clickhouse
brew services start clickhouse
clickhouse-client
```

## Docker（推荐用于测试）

```bash
# 单机版
docker run -d --name clickhouse-server \
  -p 9000:9000 -p 8123:8123 \
  -v /path/to/data:/var/lib/clickhouse \
  -v /path/to/logs:/var/log/clickhouse-server \
  clickhouse/clickhouse-server

# 验证
docker exec -it clickhouse-server clickhouse-client
```

## 集群部署（生产推荐）

ClickHouse 集群由以下组件构成：

```text
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  ClickHouse     │  │  ClickHouse     │  │  ClickHouse     │
│  Shard 1        │  │  Shard 2        │  │  Shard 3        │
│  Replica A + B  │  │  Replica A + B  │  │  Replica A + B  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
        ▲                    ▲                    ▲
        └────────────────────┼────────────────────┘
                             │
                    ┌─────────────────┐
                    │  ClickHouse     │
                    │  Keeper         │
                    │  (3/5 节点)     │
                    └─────────────────┘
```

### 关键配置（`/etc/clickhouse-server/config.xml`）

```xml
<!-- 集群拓扑 -->
<remote_servers>
    <my_cluster>
        <shard>
            <internal_replication>true</internal_replication>
            <replica>
                <host>ch-shard1-replica1</host>
                <port>9000</port>
            </replica>
            <replica>
                <host>ch-shard1-replica2</host>
                <port>9000</port>
            </replica>
        </shard>
        <shard>
            <replica>
                <host>ch-shard2-replica1</host>
                <port>9000</port>
            </replica>
            <replica>
                <host>ch-shard2-replica2</host>
                <port>9000</port>
            </replica>
        </shard>
    </my_cluster>
</remote_servers>

<!-- Keeper 配置 -->
<zookeeper>
    <node>
        <host>keeper1</host>
        <port>9181</port>
    </node>
    <node>
        <host>keeper2</host>
        <port>9181</port>
    </node>
    <node>
        <host>keeper3</host>
        <port>9181</port>
    </node>
</zookeeper>

<!-- 监听地址 -->
<listen_host>0.0.0.0</listen_host>
```

### 启动集群

```bash
# 在每台机器上启动
sudo service clickhouse-server start

# 验证集群状态
clickhouse-client --query "SELECT * FROM system.clusters FORMAT Vertical"
clickhouse-client --query "SELECT * FROM system.replicas FORMAT Vertical"
```

## Kubernetes 部署

推荐使用 **Altinity Operator**：

```bash
# 安装 Operator
kubectl apply -f https://raw.githubusercontent.com/Altinity/clickhouse-operator/master/deploy/operator/clickhouse-operator-install-bundle.yaml

# 创建 ClickHouse 集群
cat <<EOF | kubectl apply -f -
apiVersion: clickhouse.altinity.com/v1
kind: ClickHouseInstallation
metadata:
  name: chi-demo
spec:
  configuration:
    clusters:
      - name: cluster-1
        shards:
          - name: shard-1
            replicas:
              - name: replica-1
                template:
                  spec:
                    containers:
                      - name: clickhouse
                        image: clickhouse/clickhouse-server:24.3
                        resources:
                          requests:
                            memory: "4Gi"
                            cpu: "2"
EOF

# 查看状态
kubectl get chi -o wide
```

## 云服务（一键部署）

### ClickHouse Cloud（官方）

- **地址**：https://clickhouse.cloud/
- **特点**：存算分离、按查询计费、自动扩缩容
- **试用**：14 天免费试用

### 阿里云 ClickHouse

```bash
# 在阿里云控制台购买 ClickHouse 集群
# 阿里云提供完整的运维、监控、备份服务
```

### 腾讯云 ClickHouse

类似阿里云，国内用户访问更快。

## 硬件推荐

### 写入密集型（埋点/日志）

- CPU：32+ cores（向量化执行 + SIMD 受益）
- 内存：128 GB+（buffer pool + 字典缓存）
- 磁盘：NVMe SSD（写入延迟 < 1ms）
- 网络：10 Gbps（副本同步 + 客户端连接）

### 查询密集型（BI 看板）

- CPU：16+ cores
- 内存：64 GB+
- 磁盘：SATA SSD（查询对磁盘 IO 敏感度低）
- 网络：1 Gbps 足够

## 性能调优 checklist

- ✅ 关闭透明大页（`echo never > /sys/kernel/mm/transparent_hugepage/enabled`）
- ✅ 调整 `max_threads`（默认 = 物理核数）
- ✅ 配置 `merge_tree` 缓存（`mark_cache_size`）
- ✅ 开启 `query_log` 记录慢查询
- ✅ 监控 `system.merges` 看后台合并延迟

## 升级与备份

### 升级

```bash
# 关闭所有写入
clickhouse-client --query "SYSTEM STOP MERGES"
clickhouse-client --query "SYSTEM FLUSH LOGS"

# 升级包
sudo apt-get update && sudo apt-get upgrade clickhouse-server

# 重启
sudo service clickhouse-server restart
```

### 备份

推荐使用 `clickhouse-backup`：

```bash
# 安装
wget https://github.com/AlexAkulov/clickhouse-backup/releases/download/v2.5.0/clickhouse-backup.tar.gz
tar -xzf clickhouse-backup.tar.gz

# 全量备份
clickhouse-backup create --tables="db1.*" full_backup

# 备份到 S3
clickhouse-backup create --tables="db1.*" --storage=remote full_backup_s3

# 恢复
clickhouse-backup restore full_backup
```

## 下一步

- 学习 SQL 基础：见 [02-sql/select-aggregate.md](../02-sql/select-aggregate.md)
- 学习表引擎：见 [03-table-engine/overview.md](../03-table-engine/overview.md)
