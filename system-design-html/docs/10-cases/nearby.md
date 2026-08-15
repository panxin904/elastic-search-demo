---
title: 附近的人 LBS
---

# 附近的人 LBS

> 用户打开 App，能看到周围 1 公里内的人 / 商家 / 优惠。**地理位置检索 + 实时性**。

## 1. 什么是 LBS？

```
LBS（Location-Based Service）：
  - 基于位置的服务
  - 输入：用户经纬度
  - 输出：附近的人 / 商家 / 事件

常见产品：
  - 微信「附近的人」
  - 美团「附近商家」
  - 滴滴打车
  - 高德地图 POI 搜索
```

## 2. 核心要求

```
1. 低延迟：
   - 用户打开就返回
   - P99 < 200ms

2. 准确性：
   - 距离计算准确
   - 排序合理

3. 实时性：
   - 用户位置变化要反映
   - 位置过期要清理

4. 隐私：
   - 用户位置是敏感数据
   - 不能泄露精确位置
```

## 3. 整体架构

```
       客户端
         ↓ (经纬度)
    API 网关
         ↓
    LBS 服务
         ↓
   ┌─────┼─────┐
   ↓     ↓     ↓
  Geo   Redis  DB
  Hash   GEO   (备份)
   ↓
  候选列表
         ↓
   距离二次过滤
         ↓
   排序返回
```

## 4. GeoHash 算法

### 4.1 基本思想

```
GeoHash：
  - 把二维经纬度 → 一维字符串
  - 字符串前缀相同的 → 地理位置相近
  - 精度由前缀长度决定

例：北京 (39.928, 116.388)
  - geohash = "wx4g8c"
  - 前缀 wx4  → 范围缩小
  - 前缀 wx4g → 范围更小
```

### 4.2 编码过程

```
步骤：
  1. 经度范围 [-180, 180]，二分
     - 116.388 > 0 → 左半 [-180, 0] 还是右半 [0, 180]？
     - 116.388 > 0 → 左半 [-90, 0] 还是右半 [0, 90]？...

  2. 纬度范围 [-90, 90]，二分
     - 39.928 > 0 → 左 [-90, 0] 还是右 [0, 90]？...

  3. 经度位和纬度位交替组合
     - 形成二进制串

  4. Base32 编码
     - 二进制 5 位 → 一个字符
     - 字符表：0123456789bcdefghjkmnpqrstuvwxyz
```

### 4.3 精度对照

```
GeoHash 长度 → 距离范围：
  - 1 位  → 2500 km    （国家级别）
  - 2 位  → 630 km     （省级别）
  - 3 位  → 78 km      （市级别）
  - 4 位  → 20 km      （区级别）
  - 5 位  → 2.4 km     （商圈）
  - 6 位  → 610 m      （街道）
  - 7 位  → 76 m       （楼宇）
  - 8 位  → 19 m       （精确）
```

### 4.4 边缘问题

```
问题 1：边界穿越
  - 同一栋楼在马路两边，GeoHash 完全不同
  - 解决：查询时取 9 个相邻格
         (中心 + 8 个邻居)

  ┌──┬──┬──┐
  │  │ ↑│  │
  ├──┼──┼──┤
  │← │ ★│ →│
  ├──┼──┼──┤
  │  │ ↓│  │
  └──┴──┴──┘

问题 2：精度突变
  - 长度 5 和长度 6 边界
  - 跨度 2.4km → 610m
  - 解决：先用粗粒度筛选 + 二次精排

问题 3：极点附近
  - 经度二分在极区退化
  - 解决：极点附近使用极坐标
```

## 5. 邻域查询

### 5.1 9 宫格搜索

```
目标：找 (lat, lon) 附近 1km 的人

步骤：
  1. 计算中心点的 geohash（精度 5）
  2. 取 9 个格子（中心 + 8 邻）
  3. 每个格子查 Redis GEO
  4. 合并候选列表
  5. 用 Haversine 公式算精确距离
  6. 过滤 + 排序
```

### 5.2 Haversine 距离

```
两点 (lat1, lon1) 和 (lat2, lon2) 的球面距离：

a = sin²((lat2-lat1)/2) + cos(lat1)·cos(lat2)·sin²((lon2-lon1)/2)
c = 2·atan2(√a, √(1-a))
d = R·c   (R = 6371 km)

📌 用于二次精排，比 GeoHash 精确
```

## 6. 存储方案

### 6.1 Redis GEO

```
Redis 3.2+ 内置 GEO：

  GEOADD nearby 116.388 39.928 user:1001
  GEOADD nearby 116.401 39.915 user:1002

  GEOSEARCH nearby FROMLONLAT 116.388 39.928 \
              BYRADIUS 1 km WITHCOORD WITHDIST

  ZRANGE nearby 0 -1     # 底层是 Sorted Set

底层：
  - 把 lat/lon 编码成 52-bit geohash
  - 存在 Sorted Set 里
  - 用 ZRANGEBYSCORE 查询

📌 Redis GEO 是最常用方案
   单实例 100万级数据，毫秒级响应
```

### 6.2 MongoDB 2dsphere

```
MongoDB 地理空间索引：

  db.users.createIndex({location: "2dsphere"})

  db.users.find({
    location: {
      $near: {
        $geometry: {type: "Point", coordinates: [116.388, 39.928]},
        $maxDistance: 1000
      }
    }
  })

优点：
  - 原生地理空间查询
  - 支持多边形、GeoJSON

缺点：
  - 写入比 Redis 慢
  - 大数据量需要分片
```

### 6.3 Elasticsearch geo_point

```
ES 地理字段：

  PUT /users
  {
    "mappings": {
      "properties": {
        "location": {"type": "geo_point"}
      }
    }
  }

  POST /users/_search
  {
    "query": {
      "geo_distance": {
        "distance": "1km",
        "location": {"lat": 39.928, "lon": 116.388}
      }
    }
  }

优点：
  - 全文 + 地理混合查询
  - 复杂过滤（距离 + 标签 + 评分）
```

## 7. 工程实现

### 7.1 用户位置上报

```
方式 1：定时上报
  - App 启动 / 每 30s / 每 1km
  - 服务端存储 (user_id, lat, lon, ts)
  - 节省流量和电量

方式 2：服务端主动询问
  - 不推荐，耗电

方式 3：Wi-Fi / 基站定位
  - 备选方案，定位精度低
```

### 7.2 位置缓存

```
Redis GEO 数据：
  - key: "geo:nearby"
  - value: 城市 / 商圈级别分组
  - 过期：用户 30 分钟无活动，删除 GEO 数据

两级缓存：
  - L1：内存缓存（热点城市）
  - L2：Redis GEO（全量）
```

### 7.3 实时性保障

```
更新策略：
  - 用户移动：客户端定时上报
  - 移动距离 > 50m 才上报
  - 避免位置抖动
  - 服务端做"最后位置"覆盖

清理策略：
  - 用户下线 → 立即删除 GEO 数据
  - 30 分钟无更新 → 后台任务清理
  - 心跳维持
```

## 8. 隐私与安全

### 8.1 位置脱敏

```
方法 1：位置精度截断
  - 上报到服务端时，保留 4 位小数
  - 116.3881234 → 116.3881
  - 精度约 11m

方法 2：GeoHash 精度截断
  - 客户端只算 5 位 GeoHash
  - 服务端查不到 6 位以下

方法 3：服务端只暴露"距离"
  - 不返回绝对位置
  - 只返回距离值
  - 前端显示"距您 500m"
```

### 8.2 防作弊

```
问题：
  - 用户改 GPS → 漂到某个位置
  - 模拟定位软件

方案：
  1. 多源定位（GPS + Wi-Fi + 基站）交叉验证
  2. 移动速度检测（瞬移不合理）
  3. 历史轨迹分析
  4. 设备指纹

📌 金融场景（如 LBS 风控）要求更高
```

## 9. 性能与扩展

### 9.1 性能基准

```
单 Redis 实例：
  - 100 万 GEO 数据
  - GEOSEARCH 9 宫格：5-10ms
  - 1000 万数据：20-50ms

单 ES shard：
  - 1 亿数据
  - geo_distance：50-200ms
```

### 9.2 分片策略

```
按城市分片：
  - 每个城市独立 Redis
  - key 前缀：geo:{city}:nearby
  - 跨城市查询走 ES

按 GeoHash 前缀分片：
  - 前 3 位分 32 个 shard
  - 数据按地理位置分布
  - 查询时带中心 geohash 路由
```

### 9.3 高可用

```
Redis Sentinel / Cluster：
  - 1 主 2 从
  - 主挂了从自动接管
  - GEO 数据可以从 DB 重建

降级方案：
  - Redis 挂了 → 用 ES
  - ES 也挂了 → 用 DB 兜底
  - 都挂了 → 返回"暂不可用"
```

## 10. 经典面试题

### 10.1 设计附近的人

```
Q：设计微信"附近的人"
A：
  1. 客户端定时上报经纬度
  2. Redis GEO 存 (geo:city, score=geohash)
  3. 查询时取中心点 9 宫格
  4. Haversine 算精确距离
  5. 按距离 + 在线状态排序
  6. 返回 Top 20

追问：百万级 QPS 怎么抗？
  - Redis Cluster 分片
  - 9 宫格并行查询
  - 本地缓存热点城市
  - CDN 缓存列表

追问：怎么保护隐私？
  - 精度截断
  - 不返回绝对位置
  - 反作弊
```

### 10.2 找最近商家

```
Q：美团找附近 1km 的奶茶店
A：
  1. 用户位置 → Redis GEO 查询
  2. 9 宫格 → 候选商家
  3. 二次过滤（营业中、评分）
  4. 按距离 + 评分综合排序
  5. ES geo_distance 兜底

追问：跨城市怎么查？
  - 按城市路由 Redis
  - 跨城市走 ES 全量索引
  - 应用层做分页
```

## 11. 一句话总结

```
📌 LBS = GeoHash 编码 + 9 宫格查询 + Haversine 精排
📌 GeoHash：二维 → 一维，前缀匹配，边界用 9 宫格
📌 存储：Redis GEO（首选） / MongoDB 2dsphere / ES geo_point
📌 性能：Redis 100万级 10ms，ES 1亿级 100ms
📌 隐私：精度截断 + 不暴露绝对位置 + 反作弊
📌 实时性：定时上报 + 距离阈值 + 服务端覆盖
📌 高可用：Redis Cluster + ES 兜底 + 多级降级
```

## 12. 参考资料

- GeoHash 算法 (Niemeyer, 2008)
- Redis GEO 命令文档
- MongoDB Geospatial Queries
- Elasticsearch geo_point / geo_shape
- Haversine 公式 (Wikipedia)
- 系统设计面试 (Alex Xu, 2020)
