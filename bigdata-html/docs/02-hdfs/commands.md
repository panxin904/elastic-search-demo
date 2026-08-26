---
title: HDFS 命令速查
---
# HDFS 命令速查

## 📁 文件操作

```bash
# 列出
hdfs dfs -ls /                          # 详细
hdfs dfs -ls /data/ | head -10         # 前 10 条
hdfs dfs -ls -R /data/                 # 递归

# 创建目录
hdfs dfs -mkdir /data/new
hdfs dfs -mkdir -p /a/b/c              # 递归

# 上传
hdfs dfs -put local.txt /data/         # 从本地
hdfs dfs -put -f local.txt /data/       # 覆盖
hdfs dfs -moveFromLocal local.txt /data/

# 下载
hdfs dfs -get /data/file ./           # 到本地
hdfs dfs -getmerge /data/*.csv merged.csv  # 合并

# 查
hdfs dfs -cat /data/file | head
hdfs dfs -ls -h /data/                 # 人类可读

# 删
hdfs dfs -rm /data/file
hdfs dfs -rm -r /data/old              # 递归
hdfs dfs -rmdir /data/empty

# 改
hdfs dfs -mv /data/old /data/new       # 改名
hdfs dfs -cp /data/src /data/dst
hdfs dfs -chown alice:alice /data
hdfs dfs -chmod 755 /data
```

## 📊 信息查询

```bash
# 空间
hdfs dfs -du -h /data
hdfs dfs -du -h / | sort -hr | head
hdfs dfs -df -h

# 统计
hdfs dfs -count /data/q=*.json
hdfs dfs -ls / | wc -l

# 文件属性
hdfs dfs -stat %o /data/file         # 权限
hdfs dfs -stat %r /data/file         # 副本数
hdfs dfs -stat %b /data/file         # 大小（字节）
```

## 🛠️ 管理命令

```bash
# 集群状态
hdfs dfsadmin -report
hdfs dfsadmin -safemode get        # safe mode
hdfs dfsadmin -safemode leave
hdfs dfsadmin -saveNamespace

# 平衡（block 重新分布）
hdfs balancer -threshold 10
hdfs balancer -threshold 10 -f balancer.zip

# HA
hdfs haadmin -getServiceState nn1
hdfs haadmin -transitionToActive nn2 --forcemanual

# 校验
hdfs fsck /                          # 健康检查
hdfs fsck /data -files -blocks      # 详细
hdfs fsck / -delete                  # 修复

# 配额
hdfs dfsadmin -setSpaceQuota 1t /user/alice
hdfs dfsadmin -setQuota 1000 /user/alice  # 文件数
```

## 🔧 高级

```bash
# 检查点
hdfs dfsadmin -saveNamespace

# 快照（生产慎用）
hdfs dfs -createSnapshot /data snap1
hdfs dfs -deleteSnapshot /data snap1
hdfs dfs -lsSnapshottableDir

# 加密
hdfs crypto -createZone -path /secure -keyProvider jceks ...
hdfs crypto -createEncryptionZone -path /secure -keyName mykey

# 性能
hdfs dfs -mkdir -p /tmp/staging
hdfs dfs -chmod 1777 /tmp/staging
hdfs dfs -setrep 1 /tmp/staging    # 临时单副本

# 均衡（HDFS balancer）
hdfs balancer -threshold 10

# 磁盘均衡
hdfs diskbalancer -plan mycluster
hdfs diskbalancer -execute myplan.json
```

## 📂 实战脚本

```bash
# 批量上传目录
hadoop fs -put local_dir/ /hdfs/path/

# 批量下载
hadoop fs -getmerge /hdfs/data/* /local/merged.csv

# 找大文件
hdfs dfs -ls -R /data | awk '$5 > 1073741824 {print}' | head

# 找旧文件
hdfs dfs -ls -R /data | awk '{print $6, $7, $8}' | sort | head
```

## 🔍 监控命令

```bash
# 节点状态
hdfs dfsadmin -report -live
hdfs dfsadmin -report -dead
hdfs dfsadmin -report -decommissioning

# Top 用户
hdfs dfsadmin -topUsers

# 集群
hdfs haadmin -getServiceState nn1
hdfs haadmin -getServiceState nn2
```

## 🔗 下一步
- [HDFS 架构](/02-hdfs/architecture)


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
