---
title: etcd 源码导读
---

# etcd 源码导读

**etcd = 分布式 KV + Raft + watch**——K8s / 微服务的事实配置/协调中心。

## 一句话总结

> **etcd = Raft 共识 + BoltDB + gRPC + watch + lease**。**Go 让分布式系统代码保持可读**。

---

## 一、etcd 是什么

- **名字**：/`ˈɛtsiːdiː/`，Linux `/etc` 配置目录 + distributed `d`
- **作者**：李响（CoreOS，后 Red Hat / IBM）
- **用途**：K8s 后端存储 / 服务发现 / 配置中心 / 分布式锁
- **CAP**：CP（强一致）

## 二、架构

```
┌──────────────────────────┐
│ Client (curl / etcdctl)  │
└────────────┬─────────────┘
             │ gRPC
             ▼
┌──────────────────────────┐
│   etcd server (v3 API)   │
│  ┌──────────────────┐    │
│  │ Raft consensus   │    │
│  └────────┬─────────┘    │
│  ┌────────▼─────────┐    │
│  │ MVCC tree (BoltDB)│    │
│  └────────┬─────────┘    │
│  ┌────────▼─────────┐    │
│  │ gRPC + watch +   │    │
│  │ lease + auth     │    │
│  └──────────────────┘    │
└──────────────────────────┘
```

## 三、源码结构

```bash
git clone https://github.com/etcd-io/etcd
ls server/        # 核心服务
  etcdserver/    # etcd 主循环
  auth/          # 鉴权
  lease/         # 租约
  mvcc/          # 多版本并发控制
  watcher/       # 监听
ls raft/         # Raft 实现
ls wal/          # Write-Ahead Log
ls store/        # 旧版 v2 store
ls client/       # 客户端 SDK
ls etcdctl/      # CLI
```

## 四、Raft 一致性算法

```go
// raft/raft.go
type raft struct {
    id uint64
    Term uint64
    Vote uint64
    state StateType  // Follower / Candidate / Leader
    
    log          *raftLog
    nextEnts()   []pb.Entry
    // ...
}

// 心跳 + 日志复制
func (r *raft) tickElection() {
    r.electionElapsed++
    if r.promotable() && r.pastElectionTimeout() {
        r.campaign()  // 转 Candidate
    }
}

// 投票
func (r *raft) campaign(t CampaignType) {
    r.becomeCandidate()
    if r.quorum() == r.votes {
        r.becomeLeader()  // 半数以上当选
    }
}
```

**Raft 三种角色**：
- **Follower**：被动接收
- **Candidate**：竞选 Leader
- **Leader**：处理写操作

**Raft 关键概念**：
- **Term**：逻辑时钟
- **Election timeout**：150-300ms 随机
- **Heartbeat**：50ms
- **Log replication**：复制到多数
- **Snapshot**：压缩日志

**Raft vs Paxos**：Raft = 易懂的 Paxos，etcd 用 Raft。

## 五、MVCC 多版本并发控制

```go
// server/mvcc/kvstore.go
type store struct {
    mu    sync.RWMutex
    revMu sync.RWMutex
    
    tree  *btree.BTree   // 内存索引
    
    // 持久化
    ss       *bolt.Session
    bucket   *bolt.Bucket  // "key"
    metaBucket *bolt.Bucket  // "meta"
    
    // 压缩
    compactMainRev int64
}

func (s *store) Put(key, val []byte, leaseID lease.LeaseID) int64 {
    rev := s.currentRev + 1
    s.saveKey(key, val, rev)  // 写到 BoltDB
    s.tree.ReplaceOrInsert(newKey)  // 更新内存索引
    s.currentRev = rev
    return rev
}
```

**核心概念**：
- **revision**：每次写递增的版本号
- **mod_revision**：key 最后修改的 revision
- **create_revision**：key 创建的 revision
- **version**：key 修改次数

**Range 查询支持历史**：给定 revision，可查该时刻的 value。

## 六、BoltDB — 嵌入式 KV

```go
// bolt.Open
db, _ := bolt.Open("etcd.db", 0600, nil)
defer db.Close()

db.Update(func(tx *bolt.Tx) error {
    bucket, _ := tx.CreateBucketIfNotExists([]byte("key"))
    return bucket.Put([]byte("hello"), []byte("world"))
})

db.View(func(tx *bolt.Tx) error {
    bucket := tx.Bucket([]byte("key"))
    val := bucket.Get([]byte("hello"))
    fmt.Println(string(val))  // "world"
    return nil
})
```

**BoltDB 特点**：
- 嵌入式（无 server）
- B+ 树实现
- ACID 事务
- mmap 读写
- 纯 Go（无 CGO）

## 七、gRPC API

```protobuf
service KV {
  rpc Range(RangeRequest) returns (RangeResponse) {}
  rpc Put(PutRequest) returns (PutResponse) {}
  rpc DeleteRange(DeleteRangeRequest) returns (DeleteRangeResponse) {}
  rpc Txn(TxnRequest) returns (TxnResponse) {}
  rpc Compact(CompactionRequest) returns (CompactionResponse) {}
}

service Watch {
  rpc Watch(WatchRequest) returns (stream WatchResponse) {}
}

service Lease {
  rpc LeaseGrant(LeaseGrantRequest) returns (LeaseGrantResponse) {}
  rpc LeaseKeepAlive(stream LeaseKeepAliveRequest) returns (stream LeaseKeepAliveResponse) {}
}
```

**V3 全部用 gRPC**，V2 REST API 仍兼容。

## 八、Watch 监听

```go
// server/mvcc/watcher.go
type watcher struct {
    id     WatchID
    unsynced watcherSet  // 未同步的
    synced  watcherSet  // 已同步的
    ch     chan WatchResponse
}

func (w *watcher) notify(e mvccpb.Event) {
    select {
    case w.ch <- WatchResponse{...}:
    case <-time.After(3*time.Second):
        // 慢消费者
    }
}
```

**Watch 机制**：
- 客户端订阅 key 前缀
- server 推送变更事件
- 支持 progress_notify（防止事件丢失）
- 支持 compact_revision 过滤

**真实使用**：K8s 内部 list+watch 通过 etcd watch 实现。

## 九、Lease 租约

```go
// server/lease/lessor.go
type lessor struct {
    mu     sync.Mutex
    leases map[LeaseID]*Lease
    
    // 过期检查
    leaseExpiredNotifier *Notifier
}

type Lease struct {
    ID      LeaseID
    ttl     int64
    itemSet map[WatchID]struct{}  // 关联的 key
    expiry  time.Time
}

// KeepAlive（10s 一次）
lease, _ := client.Grant(ctx, 10)  // 10s TTL
client.Put(ctx, "key", "val", clientv3.WithLease(lease.ID))
ch, _ := client.KeepAlive(ctx, lease.ID)  // 持续 keepalive
```

**Lease vs TTL**：
- **TTL**：key 单独过期
- **Lease**：key 绑定租约，租约过期 key 全删

## 十、客户端使用

```go
import "go.etcd.io/etcd/client/v3"

cli, _ := clientv3.New(clientv3.Config{
    Endpoints:   []string{"localhost:2379"},
    DialTimeout: 5 * time.Second,
})
defer cli.Close()

// Put
cli.Put(ctx, "key", "value")

// Get
resp, _ := cli.Get(ctx, "key", clientv3.WithPrefix())
for _, kv := range resp.Kvs {
    fmt.Printf("%s = %s\n", kv.Key, kv.Value)
}

// Watch
rch := cli.Watch(ctx, "key", clientv3.WithPrefix())
for wresp := range rch {
    for _, ev := range wresp.Events {
        fmt.Printf("Type: %s Key: %s Value: %s\n", ev.Type, ev.Kv.Key, ev.Kv.Value)
    }
}

// Txn
cli.Txn(ctx).
    If(clientv3.Compare(clientv3.Value("lock"), "=", "owner1")).
    Then(clientv3.OpPut("lock", "owner2")).
    Else(clientv3.OpGet("lock")).
    Commit()
```

## 十一、性能调优

```bash
# etcd 启动参数
--data-dir=/var/lib/etcd
--listen-client-urls=http://0.0.0.0:2379
--advertise-client-urls=http://node1:2379
--listen-peer-urls=http://0.0.0.0:2380
--initial-advertise-peer-urls=http://node1:2380
--initial-cluster=node1=http://node1:2380,node2=http://node2:2380,node3=http://node3:2380
--initial-cluster-token=etcd-cluster-1
--initial-cluster-state=new

# 调优
--quota-backend-bytes=8589934592  # 8GB 存储上限
--max-request-bytes=10485760       # 10MB 请求
--election-timeout=1000
--heartbeat-interval=100
```

**K8s 性能建议**：
- 3-5 节点，奇数
- SSD 存储
- CPU 4-8 核
- 内存 8-16GB
- 网络 1Gbps+

## 关联章节

- **04-cloud-native/kubernetes-internals**：K8s 用 etcd
- **04-cloud-native/prometheus-internals**：另一种存储
- **04-cloud-native/cncf-ecosystem**：CNCF 全景

## 一句话总结

> **etcd = Raft + MVCC + BoltDB + gRPC**。**Go + BoltDB 让 etcd 成为分布式协调的瑞士军刀**。
