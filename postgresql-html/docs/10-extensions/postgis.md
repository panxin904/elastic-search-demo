---
title: PostGIS 空间数据库
date: 2026-08-15  # date-auto-injected
---

# PostGIS 空间数据库

> PostgreSQL 的"地理信息系统"——GIS 行业的事实标准。**PostGIS + OpenStreetMap = 全球最强开源 GIS**。

## 1. 什么是 PostGIS？

```
PostGIS：
  - PostgreSQL 的空间数据库扩展
  - 支持地理空间数据（点 / 线 / 多边形）
  - 实现 OGC 标准（Simple Features / SQL/MM）
  - GIS 应用的事实标准

为什么需要 PostGIS：
  - 关系型数据库存不了地理空间
  - 需要几何运算（距离 / 包含 / 相交）
  - 需要投影转换（WGS84 / Web Mercator）
  - 需要空间索引（R-Tree / GiST）

📌 PostGIS 已是 GIS 行业的事实标准
   QGIS / GeoServer / Mapbox / CARTO 都基于 PostGIS
```

## 2. 安装与启用

```bash
# Ubuntu
sudo apt install postgresql-17-postgis-3

# macOS
brew install postgis

# 在数据库中启用
psql mydb -c "CREATE EXTENSION postgis;"
psql mydb -c "CREATE EXTENSION postgis_topology;"  -- 拓扑
psql mydb -c "CREATE EXTENSION postgis_tiger_geocoder;"  -- TIGER（美国）

# 验证
SELECT PostGIS_Version();
```

## 3. 数据类型

### 3.1 几何类型

```sql
-- 2D 几何
SELECT 'POINT(1 1)'::geometry;
SELECT 'LINESTRING(0 0, 1 1, 2 0)'::geometry;
SELECT 'POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))'::geometry;
SELECT 'MULTIPOINT((0 0), (1 1))'::geometry;
SELECT 'MULTILINESTRING((0 0, 1 1), (2 2, 3 3))'::geometry;
SELECT 'MULTIPOLYGON(((0 0, 1 0, 1 1, 0 1)), ((2 2, 3 2, 3 3)))'::geometry;
SELECT 'GEOMETRYCOLLECTION(POINT(2 0), POLYGON((0 0, 1 0, 1 1, 0 1)))'::geometry;
```

### 3.2 地理类型

```sql
-- 地理（基于 WGS84 球面）
SELECT 'POINT(-122.4194 37.7749)'::geography;  -- 旧金山

-- Geometry vs Geography：
-- Geometry：平面坐标（笛卡尔）
-- Geography：球面坐标（经纬度）
-- Geography 距离用米，Geometry 距离用坐标单位
```

### 3.3 常用函数

```sql
-- 创建点
SELECT ST_SetSRID(ST_MakePoint(116.388, 39.928), 4326);  -- 北京，WGS84

-- 距离（米，球面）
SELECT ST_Distance(
  'POINT(-122.4194 37.7749)'::geography,  -- 旧金山
  'POINT(-73.9857 40.7484)'::geography   -- 纽约
);
-- 约 4128 km

-- 长度
SELECT ST_Length('LINESTRING(0 0, 1 1, 2 0)'::geography);

-- 面积
SELECT ST_Area('POLYGON((0 0, 1 0, 1 1, 0 1))'::geography);
```

## 4. 表设计与插入

```sql
-- 创建带空间列的表
CREATE TABLE restaurants (
  id         BIGSERIAL PRIMARY KEY,
  name       TEXT NOT NULL,
  cuisine    TEXT,
  location   geography(POINT, 4326) NOT NULL  -- WGS84 经纬度
);

-- 插入
INSERT INTO restaurants (name, cuisine, location) VALUES
  ('老王牛肉面', 'chinese', ST_SetSRID(ST_MakePoint(116.388, 39.928), 4326)::geography),
  ('北京烤鸭店', 'chinese', ST_SetSRID(ST_MakePoint(116.395, 39.915), 4326)::geography),
  ('加州披萨', 'american', ST_SetSRID(ST_MakePoint(-122.4194, 37.7749), 4326)::geography);

-- 多边形：行政区
CREATE TABLE districts (
  id        BIGSERIAL PRIMARY KEY,
  name      TEXT,
  boundary  geography(POLYGON, 4326)
);
```

## 5. 空间查询

### 5.1 距离查询

```sql
-- 找北京附近 1km 内的餐厅
SELECT id, name,
       ST_Distance(location, ST_SetSRID(ST_MakePoint(116.388, 39.928), 4326)::geography) AS dist_m
FROM restaurants
WHERE ST_DWithin(
  location,
  ST_SetSRID(ST_MakePoint(116.388, 39.928), 4326)::geography,
  1000  -- 1 km
)
ORDER BY dist_m;
```

### 5.2 包含查询

```sql
-- 行政区内的餐厅
SELECT r.*, d.name AS district
FROM restaurants r
JOIN districts d ON ST_Within(r.location, d.boundary)
WHERE d.name = '东城区';

-- 多边形相交
SELECT * FROM restaurants
WHERE ST_Intersects(
  location,
  'POLYGON((116.3 39.8, 116.5 39.8, 116.5 40.0, 116.3 40.0))'::geography
);
```

### 5.3 邻近排序

```sql
-- 找最近 5 家餐厅（KNN）
SELECT id, name,
       ST_Distance(location, 'POINT(116.388 39.928)'::geography) AS dist_m
FROM restaurants
ORDER BY location <-> 'POINT(116.388 39.928)'::geography  -- KNN 操作符
LIMIT 5;
```

### 5.4 几何运算

```sql
-- 两个点的中心
SELECT ST_Centroid(ST_Collect(
  ST_SetSRID(ST_MakePoint(116.388, 39.928), 4326)::geography,
  ST_SetSRID(ST_MakePoint(116.395, 39.915), 4326)::geography
));

-- 缓冲区
SELECT ST_Buffer(
  'POINT(116.388 39.928)'::geography,
  500  -- 500 米
);

-- 两个区域的并集
SELECT ST_Union(boundary) FROM districts WHERE name IN ('东城区', '西城区');
```

## 6. 空间索引（关键性能）

### 6.1 GiST 索引

```sql
-- GiST 是 PostGIS 的默认空间索引
CREATE INDEX idx_restaurants_location ON restaurants USING GIST (location);

-- 查询用上了索引
EXPLAIN ANALYZE
SELECT * FROM restaurants
WHERE ST_DWithin(location, 'POINT(116.388 39.928)'::geography, 1000);
--  Bitmap Heap Scan on restaurants
--    ->  Bitmap Index Scan on idx_restaurants_location
```

### 6.2 SP-GiST 索引

```sql
-- SP-GiST 也支持，适合特定分布
CREATE INDEX idx_districts_boundary ON districts USING SPGIST (boundary);
```

### 6.3 索引类型选型

| 索引 | 适用 |
|---|---|
| GiST | 默认，最常用 |
| SP-GiST | 点 / 线（平衡树） |
| BRIN | 大表（时序） |

## 7. 投影与坐标转换

```sql
-- SRID 4326：WGS84（GPS 用的）
-- SRID 3857：Web Mercator（地图瓦片用的）

-- 转换
SELECT ST_Transform(
  ST_SetSRID(ST_MakePoint(116.388, 39.928), 4326),
  3857
);

-- 投影信息
SELECT * FROM spatial_ref_sys WHERE srid = 4326;
```

## 8. 数据导入导出

### 8.1 GeoJSON

```sql
-- 导入 GeoJSON
INSERT INTO districts (name, boundary)
SELECT 'Beijing',
       ST_GeomFromGeoJSON($1${
         "type": "Polygon",
         "coordinates": [[[116.3, 39.8], [116.5, 39.8], [116.5, 40.0], [116.3, 40.0]]]
       }$1$)::geography;

-- 导出 GeoJSON
SELECT ST_AsGeoJSON(boundary) FROM districts WHERE name = 'Beijing';
```

### 8.2 WKT

```sql
-- WKT（Well-Known Text）
SELECT ST_AsText(ST_GeomFromText('POINT(116.388 39.928)', 4326));

-- WKB（二进制，更高效）
SELECT ST_AsBinary(geom);
```

### 8.3 Shapefile

```bash
# 用 shp2pgsql 导入
shp2pgsql -I -s 4326 data.shp districts | psql mydb

# 反向导出
pgsql2shp -f output.shp mydb "SELECT * FROM districts"
```

## 9. 高级特性

### 9.1 拓扑

```sql
-- 拓扑：点 / 线 / 面 的连通关系
CREATE EXTENSION postgis_topology;

-- 用于网络分析（道路 / 河流）
SELECT * FROM topology.topology
WHERE name = 'road_network';
```

### 9.2 栅格

```sql
-- 栅格数据（卫星图 / DEM）
CREATE EXTENSION postgis_raster;

-- 导入栅格
INSERT INTO dem (rast)
SELECT ST_FromGDALRaster('/path/to/dem.tif');
```

### 9.3 路由

```sql
-- pgRouting：最短路径
CREATE EXTENSION pgrouting;

-- Dijkstra
SELECT * FROM pgr_dijkstra(
  'SELECT id, source, target, cost, reverse_cost FROM ways',
  1,  -- 起点
  100  -- 终点
);
```

## 10. 经典案例

### 10.1 外卖配送

```sql
-- 找 5km 内所有餐厅，按距离排序
CREATE INDEX idx_restaurants_location ON restaurants USING GIST (location);

SELECT id, name,
       ST_Distance(location, 'POINT(116.388 39.928)'::geography) / 1000 AS dist_km
FROM restaurants
WHERE ST_DWithin(location, 'POINT(116.388 39.928)'::geography, 5000)
ORDER BY location <-> 'POINT(116.388 39.928)'::geography
LIMIT 50;
```

### 10.2 Uber 司机调度

```sql
-- 找最近的空闲司机
SELECT driver_id, ST_AsText(location) AS location,
       ST_Distance(location, 'POINT(116.388 39.928)'::geography) AS dist
FROM drivers
WHERE available = TRUE
ORDER BY location <-> 'POINT(116.388 39.928)'::geography
LIMIT 5;
```

### 10.3 房产搜索

```sql
-- 学区内 + 离地铁 < 1km
SELECT p.id, p.address, p.price
FROM properties p
JOIN schools s ON ST_Within(p.location, s.district_boundary)
WHERE s.name = '实验小学'
  AND EXISTS (
    SELECT 1 FROM metro_stations m
    WHERE ST_DWithin(p.location, m.location, 1000)
  );
```

## 11. 性能基准

```
数据集：100 万 POI（餐厅 / 商店）

无索引：
  - 顺序扫描：5000ms

GiST 索引：
  - ST_DWithin 查询：5-10ms（500x 提升）
  - 索引大小：~50 MB
  - KNN ORDER BY <->：10ms

地理类型 vs 几何类型：
  - Geography（球面）距离准确
  - Geometry（平面）距离快
  - 选择：跨城市用 geography，城内用 geometry
```

## 12. 一句话总结

```
📌 PostGIS = PG 的 GIS 扩展，GIS 行业标准
📌 类型：geometry（平面）+ geography（球面）+ 多种几何体
📌 函数：ST_Distance / ST_Within / ST_Intersects / ST_Buffer
📌 索引：GiST（默认）+ SP-GiST（点线）+ BRIN（大表）
📌 数据格式：GeoJSON / WKT / WKB / Shapefile
📌 性能：100万 POI ST_DWithin 5-10ms
📌 实战：外卖配送 / 出行调度 / 房产 / 物流
📌 进阶：拓扑 + 栅格 + 路由（pgRouting）
📌 vs MongoDB / Redis GEO：PostGIS 功能强 10x，适合复杂 GIS
```

## 13. 参考资料

- PostGIS 官方文档
- "PostGIS in Action"（O'Reilly）
- OpenStreetMap + PostGIS 实践
- pgRouting 文档
- QGIS + PostGIS 工作流
- CARTO / Mapbox 案例


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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 对比
- [clickhouse](https://java-px.bot.cd/clickhouse/):ClickHouse OLAP
- [system-design](https://java-px.bot.cd/system-design/):数据库选型
