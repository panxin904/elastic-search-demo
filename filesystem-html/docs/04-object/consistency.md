---
title: 一致性模型
date: 2026-08-15  # date-auto-injected
---

# 对象存储一致性 — 读到的版本 vs 实际版本

> <span class="kg-badge kg-badge--object">对象存储</span>
> 强一致 vs 最终一致 · 列表收敛 · 自定义业务

对象存储是一个**分布式系统**。多副本、多区域、不同节点对同一对象的视图可能短暂不一致。

理解一致性模型对开发**正确**的程序至关重要。

## 1. 三个一致性等级

| 等级 | 含义 | 例子 |
|------|------|------|
| 强一致（strong） | 写后立刻读，**总是**最新 | 关系型数据库、S3 2020 起 |
| 最终一致（eventual） | 写后读可能短暂看到旧版，几秒收敛 | 老 S3、CDN、DNS |
| 因果一致（causal） | 有依赖关系的操作有顺序，但无关操作可乱序 | 部分 NoSQL |

## 2. AWS S3 的一致性变化（关键历史）

```
2006 - 2020：eventual consistency
  - PUT 后立刻读可能拿到旧版
  - 老用户记得：要 sleep 几秒再读

2020-12-01 起：强一致（read-after-write）
  - PUT / DELETE / overwrite 后立刻 GET 拿到最新版
  - **但**：LIST 仍是 eventual（几秒收敛）
```

**为什么 LIST 难强一致**：LIST 要聚合多个分区的元数据，强一致 LIST 要所有分区都同步最新元数据 → 性能差。

## 3. 各家厂商的一致性

| 服务 | 强一致？ | 备注 |
|------|----------|------|
| AWS S3 | ✅（2020+） | LIST eventual |
| 阿里云 OSS | ✅（2019 起） | 同上 |
| 腾讯云 COS | ✅ | 写后读强一致 |
| Google GCS | ✅ | LIST 也强一致 |
| Azure Blob | ✅ | 强一致 |
| MinIO | ✅ | 自己控制 |
| Ceph RGW | ⚠️ 默认最终，可调 | 与 pg 数有关 |

## 4. 一致性测试脚本（验证 S3 类服务）

```python
import boto3, time

s3 = boto3.client('s3', endpoint_url='...')

KEY = 'test-consistency.txt'
s3.put_object(Bucket='bkt', Key=KEY, Body=b'v1')

# 立刻读
obj = s3.get_object(Bucket='bkt', Key=KEY)
v1 = obj['Body'].read()
assert v1 == b'v1', f"不一致：{v1}"

# 改写
s3.put_object(Bucket='bkt', Key=KEY, Body=b'v2')

# 立刻读
obj = s3.get_object(Bucket='bkt', Key=KEY)
v2 = obj['Body'].read()
assert v2 == b'v2', f"不一致：{v2}"
print("强一致 OK")
```

## 5. List 一致性怎么解决

```python
# 方案 1：写完后再 sleep
time.sleep(2)
list_result = s3.list_objects_v2(Bucket='bkt', Prefix='xxx')

# 方案 2：用 ListObjectVersions + 排序
versions = s3.list_object_versions(Bucket='bkt', Prefix='xxx')
# 拿 LatestVersion

# 方案 3：业务端用元数据库（DB）跟踪"应有"的列表
# 写：先写 DB（事务）→ 再 PUT 对象
# 读：先查 DB → 用 DB 里的 key 去 GET

# 方案 4：使用对象元数据 ETag
# ETag = 对象内容 MD5，PUT 后 ETag 变了 → 拿到新版本
```

## 6. 跨区域复制（CRR）的一致性

跨区域复制是**异步**：

```
源 bucket (PUT v1)
    ↓ 异步复制（几秒~几十秒）
目标 bucket (GET 可能还看不到 v1)
```

**RPO**：通常 1~10 秒（配置越好，复制越快）。

如果业务对 RPO 敏感：用**强一致**的同区域副本 + 异地跨区异步复制（双层）。

## 7. 业务应用：避免读到旧值

### 7.1 头像上传 → 显示

```python
# 反模式
user.upload_avatar(file)
time.sleep(2)             # 等同步
user.profile_page()        # 此时头像应该是新版

# 正确模式
key = f"avatar/{user_id}.png?v={int(time.time()*1000)}"
s3.put_object(Key=key, Body=file)  # URL 永远最新
```

**用 query string + 时间戳破缓存**——比靠对象存储一致性更可靠。

### 7.2 删除 → 读不到

```python
# 写入应用数据库
db.execute("UPDATE file SET deleted=true WHERE key=?", key)
# 删除对象
s3.delete_object(Key=key)

# 应用层：先查 DB（事务边界）→ 决定要不要显示
```

### 7.3 共享文档

用户 A 写，用户 B 读：

```python
# 用强一致存储 + 通知
s3.put_object(Key='doc.txt', Body=new_content)
sns.publish(TopicArn=..., Subject='doc updated', Message=key)
# 用户 B 收到通知 → GET → 拿到新版
```

## 8. 数据版本控制（Versioning）

开启 Versioning 后：

- 每次写都生成新版本（不覆盖旧版本）
- GET 默认拿最新版
- 可指定 GET 某个 version ID

```python
# 看历史
versions = s3.list_object_versions(Bucket='bkt', Prefix='doc.txt')
for v in versions['Versions']:
    print(v['VersionId'], v['LastModified'], v['Size'])

# 取特定版本
obj = s3.get_object(Bucket='bkt', Key='doc.txt', VersionId='abc123')
```

**代价**：版本多 = 存储多，配合生命周期清理老版本。

## 9. 强一致 vs 最终一致：何时选

| 业务 | 一致性需求 | 推荐 |
|------|-----------|------|
| 金融结算、订单 | 强一致 | 关系数据库 + 对象存储 |
| 用户头像、附件 | 最终一致可接受（前端加 hash） | 对象存储直接 |
| 数据备份、归档 | 最终一致可接受 | 对象存储 + 校验任务 |
| 配置中心 | 强一致 | Redis/DB |

## 10. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| S3 2020 后强一致 | "2020=read-after-write" |
| LIST 仍是 eventual | "LIST 收敛慢" |
| 跨区异步复制 | "CRR=异步" |
| 业务破缓存靠 query hash | "加 query 破缓存" |
| 强一致≠历史版本 | "Versioning 管历史" |

## 参考

- AWS S3 强一致公告：<https://aws.amazon.com/blogs/aws/amazon-s3-update-strong-read-after-write-consistency/>
- 一致性模型（CAP 定理）
- 阿里云 OSS 强一致白皮书