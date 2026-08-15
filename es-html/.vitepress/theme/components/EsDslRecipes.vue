<template>
  <div class="es-dsl">
    <div class="es-dsl__intro">
      📚 按 <strong>7 大类</strong>整理共 <strong>{{ recipes.length }}</strong> 个 Query DSL 模板。
      点击分类切换显示该类所有模板，「🔬 试一下」可一键跳到
      <a href="/05-tools/curl-client">调试器</a> 预填。
    </div>

    <div class="es-dsl__subtabs">
      <button
        v-for="cat in categories"
        :key="cat.id"
        :class="['es-dsl__subtab', { 'es-dsl__subtab--active': activeSubTab === cat.id }]"
        @click="activeSubTab = cat.id"
      >
        {{ cat.icon }} {{ cat.label }}
        <span class="es-dsl__subtab-count">
          ({{ recipes.filter(r => r.category === cat.id).length }})
        </span>
      </button>
    </div>

    <div class="es-dsl__cat-title">
      {{ currentCat.icon }} {{ currentCat.label }}
    </div>

    <div
      v-for="recipe in filteredRecipes"
      :key="recipe.id"
      class="es-dsl__item"
    >
      <div class="es-dsl__item-head">
        <strong>{{ recipe.title }}</strong>
        <div class="es-dsl__tags">
          <span
            v-for="tag in recipe.tags"
            :key="tag"
            class="es-dsl__tag"
          >{{ tag }}</span>
        </div>
      </div>
      <div class="es-dsl__desc">{{ recipe.desc }}</div>
      <details class="es-dsl__details">
        <summary>查看 DSL</summary>
        <pre class="es-dsl__pre">{{ recipe.body }}</pre>
      </details>
      <div class="es-dsl__actions">
        <button class="es-dsl__btn es-dsl__btn--sm es-dsl__btn--primary" @click="tryIt(recipe)">
          🔬 试一下
        </button>
        <button class="es-dsl__btn es-dsl__btn--sm" @click="copy(recipe)">
          {{ copiedId === recipe.id ? '已复制 ✓' : '📋 复制' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const categories = [
  { id: 'leaf', label: '叶子查询 (Leaf)', icon: '🍃' },
  { id: 'compound', label: '复合查询 (Compound)', icon: '🎯' },
  { id: 'compound_ext', label: '复合扩展 (More)', icon: '🔀' },
  { id: 'range', label: '范围查询', icon: '📏' },
  { id: 'fulltext', label: '全文检索', icon: '🔎' },
  { id: 'pattern', label: '模糊与模式', icon: '🔤' },
  { id: 'geo', label: '地理空间', icon: '🌐' },
  { id: 'span', label: 'Span 查询', icon: '🔗' },
  { id: 'join', label: '嵌套与连接', icon: '🔍' },
  { id: 'agg', label: '聚合分析', icon: '📊' },
  { id: 'agg_metric', label: '指标聚合', icon: '🔢' },
  { id: 'agg_bucket', label: '桶聚合', icon: '📈' },
  { id: 'agg_pipeline', label: 'Pipeline 聚合', icon: '🔄' },
  { id: 'sort_hl', label: '排序与高亮', icon: '🔃' },
  { id: 'suggest', label: '联想 Suggest', icon: '💡' },
  { id: 'special', label: '排错与高级', icon: '🛠️' }
]

const recipes = [
  {
    id: 'term',
    category: 'leaf',
    title: 'Term Query - 精确匹配',
    tags: ['精确', 'keyword', '数值'],
    desc: '不做分词的精确匹配，作用于 keyword / 数值 / 日期。term 查询不会经过分析器，所以输入的字符串必须是 term 本身。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "query": {\n    "term": {\n      "category": {\n        "value": "电脑外设"\n      }\n    }\n  }\n}'
  },
  {
    id: 'terms',
    category: 'leaf',
    title: 'Terms Query - 多值精确匹配',
    tags: ['IN', '多值'],
    desc: '等价于 SQL 的 IN 操作，匹配任一 value 即命中。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "query": {\n    "terms": {\n      "category": ["电脑外设", "电脑配件", "手机配件"]\n    }\n  }\n}'
  },
  {
    id: 'exists',
    category: 'leaf',
    title: 'Exists Query - 字段存在性',
    tags: ['字段', '存在'],
    desc: '匹配字段值非 null 的文档。常用于清洗脏数据。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "query": {\n    "exists": {\n      "field": "price"\n    }\n  }\n}'
  },
  {
    id: 'ids',
    category: 'leaf',
    title: 'IDs Query - 按 ID 查询',
    tags: ['_id', '批量'],
    desc: '通过 _id 直接获取文档，比用 term 查询 _id 更高效。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "query": {\n    "ids": {\n      "values": ["p001", "p002", "p003"]\n    }\n  }\n}'
  },
  {
    id: 'bool',
    category: 'compound',
    title: 'Bool Query - 复合条件',
    tags: ['核心', 'must/should/filter'],
    desc: '用 must/should/filter/must_not 组合多个子句。最佳实践：必须满足的可过滤条件放 filter（可缓存，不参与评分）。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "query": {\n    "bool": {\n      "must": [\n        { "match": { "name": "机械键盘" } }\n      ],\n      "filter": [\n        { "term":  { "category": "电脑外设" } },\n        { "range": { "price": { "lte": 1000 } } }\n      ],\n      "must_not": [\n        { "term": { "status": "discontinued" } }\n      ],\n      "should": [\n        { "term": { "is_promoted": true } }\n      ]\n    }\n  }\n}'
  },
  {
    id: 'constant_score',
    category: 'compound',
    title: 'Constant Score - 固定评分',
    tags: ['性能', 'filter 包装'],
    desc: '把 query 包成 filter 上下文，避免评分计算，性能更好。常配合 bool 用。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "query": {\n    "constant_score": {\n      "filter": {\n        "term": { "category": "电脑外设" }\n      },\n      "boost": 1.0\n    }\n  }\n}'
  },
  {
    id: 'range',
    category: 'range',
    title: 'Range Query - 数值/日期范围',
    tags: ['数值', '日期', 'gt/gte/lt/lte'],
    desc: '范围匹配。date 字段支持 now-7d、now+1d 等数学表达式。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "query": {\n    "range": {\n      "price": { "gte": 100, "lte": 1000 }\n    }\n  }\n}'
  },
  {
    id: 'date_range',
    category: 'range',
    title: 'Date Range - 日期范围（数学表达式）',
    tags: ['日期', 'now', '相对时间'],
    desc: '常用于日志和时序数据，结合日期数学表达式 now-7d 等。',
    method: 'POST',
    path: '/logs/_search',
    body: '{\n  "query": {\n    "range": {\n      "@timestamp": {\n        "gte": "now-7d/d",\n        "lte": "now/d"\n      }\n    }\n  }\n}'
  },
  {
    id: 'match',
    category: 'fulltext',
    title: 'Match Query - 标准全文检索',
    tags: ['基础', '分词'],
    desc: '对 text 字段分词后匹配。默认 operator=or（任一命中）；operator=and 要求全部 token 命中。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "query": {\n    "match": {\n      "name": {\n        "query": "机械键盘",\n        "operator": "and"\n      }\n    }\n  }\n}'
  },
  {
    id: 'match_phrase',
    category: 'fulltext',
    title: 'Match Phrase - 短语匹配',
    tags: ['顺序', 'slop'],
    desc: '要求 token 按原顺序相邻出现；slop 参数允许中间间隔少量 token。',
    method: 'POST',
    path: '/articles/_search',
    body: '{\n  "query": {\n    "match_phrase": {\n      "title": {\n        "query": "机械 键盘",\n        "slop": 2\n      }\n    }\n  }\n}'
  },
  {
    id: 'multi_match',
    category: 'fulltext',
    title: 'Multi Match - 多字段全文检索',
    tags: ['跨字段', 'boost'],
    desc: '在多个字段上同时搜。^N 控制字段权重。',
    method: 'POST',
    path: '/articles/_search',
    body: '{\n  "query": {\n    "multi_match": {\n      "query": "机械键盘",\n      "fields": ["title^3", "content^1", "tags^2"]\n    }\n  }\n}'
  },
  {
    id: 'query_string',
    category: 'fulltext',
    title: 'Query String - Lucene 语法',
    tags: ['lucene', 'AND/OR/NOT'],
    desc: '支持 Lucene 查询字符串语法（+ - AND OR NOT 等等）。生产慎用，注入风险较大。',
    method: 'POST',
    path: '/articles/_search',
    body: '{\n  "query": {\n    "query_string": {\n      "default_field": "content",\n      "query": "(机械 AND 键盘) NOT 二手"\n    }\n  }\n}'
  },
  {
    id: 'nested',
    category: 'join',
    title: 'Nested Query - 嵌套对象',
    tags: ['nested', '对象数组'],
    desc: '查询 nested 类型的对象数组内部条件，保持子对象内部关联。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "query": {\n    "nested": {\n      "path": "comments",\n      "query": {\n        "bool": {\n          "must": [\n            { "term": { "comments.user": "alice" } },\n            { "range": { "comments.rating": { "gte": 4 } } }\n          ]\n        }\n      }\n    }\n  }\n}'
  },
  {
    id: 'has_child',
    category: 'join',
    title: 'Has Child Query - 父子文档',
    tags: ['join', 'parent-child'],
    desc: '查询满足子文档条件的父文档。需 mapping 中定义 join 字段。',
    method: 'POST',
    path: '/posts/_search',
    body: '{\n  "query": {\n    "has_child": {\n      "type": "comment",\n      "query": {\n        "match": { "comment.text": "很棒" }\n      }\n    }\n  }\n}'
  },
  {
    id: 'agg_terms',
    category: 'agg',
    title: 'Terms Aggregation - 词频统计',
    tags: ['聚合', '分类统计'],
    desc: '按字段分桶统计文档数，常用于分类计数。size 限制 bucket 数。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "size": 0,\n  "aggs": {\n    "by_category": {\n      "terms": { "field": "category", "size": 10 }\n    }\n  }\n}'
  },
  {
    id: 'agg_metrics',
    category: 'agg',
    title: 'Metrics - 平均/最大/总数',
    tags: ['聚合', '数值'],
    desc: 'avg / sum / min / max / cardinality 等单值聚合。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "size": 0,\n  "aggs": {\n    "avg_price": { "avg": { "field": "price" } },\n    "max_stock": { "max": { "field": "stock" } },\n    "uniq_cats": { "cardinality": { "field": "category" } }\n  }\n}'
  },
  {
    id: 'agg_sub',
    category: 'agg',
    title: 'Sub-Aggregation - 嵌套聚合',
    tags: ['聚合', '嵌套'],
    desc: '在每个 bucket 内进一步聚合，如按类别分组后求均价。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "size": 0,\n  "aggs": {\n    "by_category": {\n      "terms": { "field": "category", "size": 10 },\n      "aggs": {\n        "avg_price":   { "avg": { "field": "price" } },\n        "price_range": {\n          "range": {\n            "field": "price",\n            "ranges": [\n              { "to": 100 },\n              { "from": 100, "to": 500 },\n              { "from": 500 }\n            ]\n          }\n        }\n      }\n    }\n  }\n}'
  },
  {
    id: 'agg_datehist',
    category: 'agg',
    title: 'Date Histogram - 时间序列',
    tags: ['聚合', '时序'],
    desc: '按时间分桶，常用于折线图和时序分析。calendar_interval / fixed_interval 控制粒度。',
    method: 'POST',
    path: '/orders/_search',
    body: '{\n  "size": 0,\n  "aggs": {\n    "sales_over_time": {\n      "date_histogram": {\n        "field": "created_at",\n        "calendar_interval": "day"\n      },\n      "aggs": {\n        "daily_revenue": { "sum": { "field": "amount" } }\n      }\n    }\n  }\n}'
  },
  {
    id: 'profile',
    category: 'special',
    title: 'Profile API - 查询剖析',
    tags: ['性能', '调优', 'debug'],
    desc: '查看查询各阶段耗时与 Lucene 评分细节，定位慢查询。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "profile": true,\n  "query": {\n    "match": { "name": "机械键盘" }\n  }\n}'
  },
  {
    id: 'explain',
    category: 'special',
    title: 'Explain API - 评分明细',
    tags: ['debug', '评分'],
    desc: '返回每个文档的具体评分组成，便于理解排序原因。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "explain": true,\n  "query": {\n    "match": { "name": "机械键盘" }\n  }\n}'
  },
  {
    id: 'function_score',
    category: 'special',
    title: 'Function Score - 加权评分',
    tags: ['评分', '加权'],
    desc: '包装 query 并对每个结果重新计算综合分（如按销量、新品加权）。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "query": {\n    "function_score": {\n      "query": { "match": { "name": "机械键盘" } },\n      "functions": [\n        { "filter": { "term": { "is_promoted": true } }, "weight": 5 },\n        { "gauss": { "created_at": { "origin": "now", "scale": "30d" } } }\n      ],\n      "boost_mode": "multiply"\n    }\n  }\n}'
  },
  // ====== 复合扩展 ======
  {
    id: 'boosting',
    category: 'compound_ext',
    title: 'Boosting - 提升主查询、降级负面查询',
    tags: ['推荐', '降权'],
    desc: '匹配 positive 的文档正常打分，匹配 negative 的文档会被降级（negative_boost 是 0-1 的乘数）。常用于"主推 X 类目，附带 Y 类目但降权"。',
    method: 'POST',
    path: '/articles/_search',
    body: '{\n  "query": {\n    "boosting": {\n      "positive": { "term": { "category": "tech" } },\n      "negative": { "term": { "tags": "deprecated" } },\n      "negative_boost": 0.2\n    }\n  }\n}'
  },
  {
    id: 'dis_max',
    category: 'compound_ext',
    title: 'Disjunction Max - 多子查询取最大分',
    tags: ['dis_max', '最佳匹配'],
    desc: '在多个子句中取最高评分（不像 bool 累加）。适合"任一匹配就足够"的语义，减少累加干扰。',
    method: 'POST',
    path: '/articles/_search',
    body: '{\n  "query": {\n    "dis_max": {\n      "queries": [\n        { "term":  { "title": "elasticsearch" } },\n        { "match": { "body":  "elasticsearch" } }\n      ],\n      "tie_breaker": 0.3\n    }\n  }\n}'
  },
  {
    id: 'more_like_this',
    category: 'compound_ext',
    title: 'More Like This - 找相似文档',
    tags: ['MLT', '相似推荐'],
    desc: '输入一段文本，自动提取特征词查询相似文档。常用于相关文章推荐。',
    method: 'POST',
    path: '/articles/_search',
    body: '{\n  "query": {\n    "more_like_this": {\n      "fields": ["title", "content"],\n      "like": "elasticsearch 是一个分布式搜索和分析引擎",\n      "min_term_freq": 1,\n      "max_query_terms": 25\n    }\n  }\n}'
  },
  {
    id: 'percolate',
    category: 'compound_ext',
    title: 'Percolator - 反向查询',
    tags: ['percolator', '告警'],
    desc: '把 query 当文档存储，给一个新文档，匹配哪些 query 命中。常用于"价格告警"、"订阅推送"。',
    method: 'POST',
    path: '/price-alerts/_search',
    body: '{\n  "query": {\n    "percolate": {\n      "field": "query",\n      "document_type": "alert",\n      "document": { "product_id": "p001", "price": 599 }\n    }\n  }\n}'
  },
  // ====== 模糊与模式 ======
  {
    id: 'prefix',
    category: 'pattern',
    title: 'Prefix - 前缀匹配',
    tags: ['前缀', '自动补全'],
    desc: '匹配字段以指定前缀开头的文档。常用于自动补全。注意会展开为大量 term，高基数字段慎用。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "query": {\n    "prefix": {\n      "name": {\n        "value": "机"\n      }\n    }\n  }\n}'
  },
  {
    id: 'wildcard',
    category: 'pattern',
    title: 'Wildcard - 通配符',
    tags: ['*', '?'],
    desc: '* 匹配 0+ 字符，? 匹配 1 字符。生产慎用，展开为大量 term。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "query": {\n    "wildcard": {\n      "sku": {\n        "value": "KEY-*-BLK"\n      }\n    }\n  }\n}'
  },
  {
    id: 'fuzzy',
    category: 'pattern',
    title: 'Fuzzy - 模糊匹配（容错拼写）',
    tags: ['拼写错误', '容错'],
    desc: '基于 Levenshtein 编辑距离做容错匹配，如 "color" 也能匹配 "colour"。',
    method: 'POST',
    path: '/articles/_search',
    body: '{\n  "query": {\n    "fuzzy": {\n      "title": {\n        "value": "elasticsarch",\n        "fuzziness": 2\n      }\n    }\n  }\n}'
  },
  {
    id: 'regexp',
    category: 'pattern',
    title: 'Regexp - 正则表达式',
    tags: ['正则', '复杂模式'],
    desc: '使用正则表达式匹配字段。性能较差（仍会展开 term）。',
    method: 'POST',
    path: '/logs/_search',
    body: '{\n  "query": {\n    "regexp": {\n      "host": {\n        "value": "web-(0[1-9]|1[0-9]|20)\\\\..*",\n        "flags": "ALL"\n      }\n    }\n  }\n}'
  },
  {
    id: 'match_phrase_prefix',
    category: 'pattern',
    title: 'Match Phrase Prefix - 前缀短语',
    tags: ['短语', '前缀'],
    desc: '短语 + 最后一词做前缀。适合搜索建议（typeahead），但性能差。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "query": {\n    "match_phrase_prefix": {\n      "name": "机械键"\n    }\n  }\n}'
  },
  {
    id: 'simple_query_string',
    category: 'pattern',
    title: 'Simple Query String - 安全的 Lucene 语法',
    tags: ['生产推荐', '可注入安全'],
    desc: 'query_string 的安全替代：忽略无效语法、不抛异常、不会让用户用恶意语法攻击。',
    method: 'POST',
    path: '/articles/_search',
    body: '{\n  "query": {\n    "simple_query_string": {\n      "query": "elasticsearch +tutorial -deprecated",\n      "fields": ["title^3", "content"],\n      "default_operator": "and"\n    }\n  }\n}'
  },
  // ====== 地理空间 ======
  {
    id: 'geo_bounding_box',
    category: 'geo',
    title: 'Geo Bounding Box - 矩形范围',
    tags: ['geo_point', '矩形'],
    desc: '查找地理点位于指定矩形边界内的文档。top_left / bottom_right 经纬度。',
    method: 'POST',
    path: '/shops/_search',
    body: '{\n  "query": {\n    "geo_bounding_box": {\n      "location": {\n        "top_left":     { "lat": 40.73, "lon": -74.1 },\n        "bottom_right": { "lat": 40.01, "lon": -71.12 }\n      }\n    }\n  }\n}'
  },
  {
    id: 'geo_distance',
    category: 'geo',
    title: 'Geo Distance - 中心点 + 半径',
    tags: ['geo_point', '距离', '周边搜索'],
    desc: '查找距离中心点指定半径内的文档。distance_unit: m/km/mi。distance_type: arc / plane。',
    method: 'POST',
    path: '/shops/_search',
    body: '{\n  "query": {\n    "bool": {\n      "filter": {\n        "geo_distance": {\n          "distance": "5km",\n          "location": { "lat": 40.7128, "lon": -74.0060 }\n        }\n      }\n    }\n  }\n}'
  },
  {
    id: 'geo_polygon',
    category: 'geo',
    title: 'Geo Polygon - 多边形范围',
    tags: ['geo_point', '多边形', '区域'],
    desc: '查找地理点位于任意多边形内的文档（区域搜索、配送范围）。',
    method: 'POST',
    path: '/shops/_search',
    body: '{\n  "query": {\n    "geo_polygon": {\n      "location": {\n        "points": [\n          { "lat": 40.0, "lon": -75.0 },\n          { "lat": 41.0, "lon": -75.0 },\n          { "lat": 41.0, "lon": -73.0 },\n          { "lat": 40.0, "lon": -73.0 }\n        ]\n      }\n    }\n  }\n}'
  },
  {
    id: 'geo_shape',
    category: 'geo',
    title: 'Geo Shape - 复杂形状查询',
    tags: ['geo_shape', '复杂地理'],
    desc: 'geo_shape 字段类型的复杂形状查询（与矩形/多边形/距离关系）。',
    method: 'POST',
    path: '/zones/_search',
    body: '{\n  "query": {\n    "geo_shape": {\n      "area": {\n        "shape": {\n          "type": "envelope",\n          "coordinates": [[-74.1, 40.73], [-71.12, 40.01]]\n        },\n        "relation": "within"\n      }\n    }\n  }\n}'
  },
  // ====== Span 查询 ======
  {
    id: 'span_term',
    category: 'span',
    title: 'Span Term - 邻近查询的原子单元',
    tags: ['span', '邻近'],
    desc: 'Span 查询的最底层单元，匹配单个 term。常作为 span_near/span_or 的子句。',
    method: 'POST',
    path: '/articles/_search',
    body: '{\n  "query": {\n    "span_term": { "title": { "value": "elasticsearch" } }\n  }\n}'
  },
  {
    id: 'span_near',
    category: 'span',
    title: 'Span Near - 邻近词组查询',
    tags: ['span', '词邻近'],
    desc: '要求多个 span 子句按顺序相邻出现，slop 控制间隔 token 数。比 match_phrase 更精细。',
    method: 'POST',
    path: '/articles/_search',
    body: '{\n  "query": {\n    "span_near": {\n      "clauses": [\n        { "span_term": { "title": { "value": "elasticsearch" } } },\n        { "span_term": { "title": { "value": "性能" } } }\n      ],\n      "slop": 5,\n      "in_order": true\n    }\n  }\n}'
  },
  {
    id: 'span_or',
    category: 'span',
    title: 'Span Or - 多 span 子句任一匹配',
    tags: ['span', '多匹配'],
    desc: '多个 span 子句任一匹配即可（span 版的 bool/should）。',
    method: 'POST',
    path: '/articles/_search',
    body: '{\n  "query": {\n    "span_or": {\n      "clauses": [\n        { "span_term": { "title": { "value": "elasticsearch" } } },\n        { "span_term": { "title": { "value": "lucene" } } }\n      ]\n    }\n  }\n}'
  },
  // ====== 指标聚合 ======
  {
    id: 'agg_percentiles',
    category: 'agg_metric',
    title: 'Percentiles - 分位数（P50/P95/P99）',
    tags: ['聚合', '分位数', '监控'],
    desc: '计算指定分位的值，常用于延迟监控（P95/P99 延迟）。',
    method: 'POST',
    path: '/orders/_search',
    body: '{\n  "size": 0,\n  "aggs": {\n    "latency_percentiles": {\n      "percentiles": {\n        "field": "latency_ms",\n        "percents": [50, 90, 95, 99]\n      }\n    }\n  }\n}'
  },
  {
    id: 'agg_stats',
    category: 'agg_metric',
    title: 'Stats - 完整统计',
    tags: ['聚合', '统计', 'min/max/avg/sum'],
    desc: '一次返回 count/min/max/avg/sum/平方和/方差/标准差。',
    method: 'POST',
    path: '/orders/_search',
    body: '{\n  "size": 0,\n  "aggs": {\n    "amount_stats": {\n      "stats": { "field": "amount" }\n    }\n  }\n}'
  },
  {
    id: 'agg_extended_stats',
    category: 'agg_metric',
    title: 'Extended Stats - 扩展统计',
    tags: ['聚合', '方差', 'std_deviation'],
    desc: 'Stats 加上方差、标准差、两倍标准差边界（用于离群值检测）。',
    method: 'POST',
    path: '/orders/_search',
    body: '{\n  "size": 0,\n  "aggs": {\n    "amount_ext_stats": {\n      "extended_stats": { "field": "amount", "sigma": 2 }\n    }\n  }\n}'
  },
  {
    id: 'agg_cardinality',
    category: 'agg_metric',
    title: 'Cardinality - 去重计数',
    tags: ['聚合', 'UV', '基数'],
    desc: '使用 HyperLogLog++ 算法做近似去重计数（适合大基数场景，精度可调 precision_threshold）。',
    method: 'POST',
    path: '/users/_search',
    body: '{\n  "size": 0,\n  "aggs": {\n    "unique_users": {\n      "cardinality": { "field": "user_id", "precision_threshold": 10000 }\n    }\n  }\n}'
  },
  {
    id: 'agg_value_count',
    category: 'agg_metric',
    title: 'Value Count - 非空字段计数',
    tags: ['聚合', '统计'],
    desc: '统计字段非空的文档数（与 doc_count 不同：doc_count 是查询命中数）。',
    method: 'POST',
    path: '/users/_search',
    body: '{\n  "size": 0,\n  "aggs": {\n    "users_with_email": {\n      "value_count": { "field": "email" }\n    }\n  }\n}'
  },
  {
    id: 'agg_scripted_metric',
    category: 'agg_metric',
    title: 'Scripted Metric - 自定义聚合',
    tags: ['聚合', '脚本', 'Painless'],
    desc: '用 Painless 脚本完全自定义聚合逻辑（init_script / map_script / combine_script / reduce_script）。',
    method: 'POST',
    path: '/transactions/_search',
    body: '{\n  "size": 0,\n  "aggs": {\n    "profit": {\n      "scripted_metric": {\n        "init_script": "state.transactions = []",\n        "map_script": "state.transactions.add(doc[\'amount\'].value)",\n        "combine_script": "double sum = 0; for (t in state.transactions) { sum += t } return sum",\n        "reduce_script": "double profit = 0; for (a in states) { profit += a } return profit"\n      }\n    }\n  }\n}'
  },
  {
    id: 'agg_top_hits',
    category: 'agg_metric',
    title: 'Top Hits - 桶内前 N',
    tags: ['聚合', '嵌套', '取样'],
    desc: '在每个聚合 bucket 内取前 N 条原始文档。常用于"按类别聚合 + 每类展示前 3"。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "size": 0,\n  "aggs": {\n    "by_category": {\n      "terms": { "field": "category", "size": 5 },\n      "aggs": {\n        "top_products": {\n          "top_hits": { "size": 3, "_source": [ "name", "price" ] }\n        }\n      }\n    }\n  }\n}'
  },
  // ====== 桶聚合 ======
  {
    id: 'agg_histogram',
    category: 'agg_bucket',
    title: 'Histogram - 数值直方图',
    tags: ['聚合', '数值', '直方图'],
    desc: '按数值字段等宽分桶（不同于 date_histogram 处理日期）。',
    method: 'POST',
    path: '/orders/_search',
    body: '{\n  "size": 0,\n  "aggs": {\n    "amount_distribution": {\n      "histogram": { "field": "amount", "interval": 100, "min_doc_count": 1 }\n    }\n  }\n}'
  },
  {
    id: 'agg_range',
    category: 'agg_bucket',
    title: 'Range Aggregation - 自定义区间',
    tags: ['聚合', '区间', '分布'],
    desc: '按自定义数值区间分桶。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "size": 0,\n  "aggs": {\n    "price_ranges": {\n      "range": {\n        "field": "price",\n        "ranges": [\n          { "to": 100,   "key": "便宜" },\n          { "from": 100, "to": 500,   "key": "中等" },\n          { "from": 500,                "key": "高端" }\n        ]\n      }\n    }\n  }\n}'
  },
  {
    id: 'agg_geo_distance',
    category: 'agg_bucket',
    title: 'Geo Distance Agg - 按距离聚合',
    tags: ['聚合', '地理', '周边'],
    desc: '按距中心点的距离分桶（常用于"500m / 1km / 5km"的统计）。',
    method: 'POST',
    path: '/shops/_search',
    body: '{\n  "size": 0,\n  "aggs": {\n    "distance_rings": {\n      "geo_distance": {\n        "field": "location",\n        "origin": { "lat": 40.7128, "lon": -74.0060 },\n        "unit": "km",\n        "ranges": [\n          { "to": 1 }, { "from": 1, "to": 5 }, { "from": 5 }\n        ]\n      }\n    }\n  }\n}'
  },
  {
    id: 'agg_ip_range',
    category: 'agg_bucket',
    title: 'IP Range - IP 段聚合',
    tags: ['聚合', 'IP', '网络段'],
    desc: '按 IP 段聚合，常用于日志按网段分组。',
    method: 'POST',
    path: '/logs/_search',
    body: '{\n  "size": 0,\n  "aggs": {\n    "by_subnet": {\n      "ip_range": {\n        "field": "client_ip",\n        "ranges": [\n          { "key": "internal", "to": "10.0.0.0/8" },\n          { "key": "external", "from": "10.0.0.0/8" }\n        ]\n      }\n    }\n  }\n}'
  },
  {
    id: 'agg_missing',
    category: 'agg_bucket',
    title: 'Missing - 字段缺失文档',
    tags: ['聚合', '脏数据', 'NULL'],
    desc: '对指定字段为 null/missing 的文档做聚合（清洗脏数据用）。',
    method: 'POST',
    path: '/users/_search',
    body: '{\n  "size": 0,\n  "aggs": {\n    "no_email_users": {\n      "missing": { "field": "email" }\n    }\n  }\n}'
  },
  // ====== Pipeline 聚合 ======
  {
    id: 'agg_derivative',
    category: 'agg_pipeline',
    title: 'Derivative - 差分（一阶导数）',
    tags: ['pipeline', '差分', '趋势'],
    desc: '对前一个 bucket 的值做差分（如"环比增长")。',
    method: 'POST',
    path: '/orders/_search',
    body: '{\n  "size": 0,\n  "aggs": {\n    "by_month": {\n      "date_histogram": { "field": "created_at", "calendar_interval": "month" },\n      "aggs": { "sales": { "sum": { "field": "amount" } } }\n    },\n    "sales_diff": {\n      "derivative": { "buckets_path": "by_month>sales" }\n    }\n  }\n}'
  },
  {
    id: 'agg_cumulative_sum',
    category: 'agg_pipeline',
    title: 'Cumulative Sum - 累计求和',
    tags: ['pipeline', '累计', '总额'],
    desc: '对每个 bucket 与之前所有 bucket 的值做累加。',
    method: 'POST',
    path: '/orders/_search',
    body: '{\n  "size": 0,\n  "aggs": {\n    "by_month\": {\n      "date_histogram": { "field": "created_at", "calendar_interval": "month" },\n      "aggs": { "sales": { "sum": { "field": "amount" } } }\n    },\n    "cumulative_sales": {\n      "cumulative_sum": { "buckets_path": "by_month>sales" }\n    }\n  }\n}'
  },
  {
    id: 'agg_moving_avg',
    category: 'agg_pipeline',
    title: 'Moving Average - 移动平均',
    tags: ['pipeline', '平滑', '趋势'],
    desc: '滑动窗口移动平均线（监控告警、波动平滑）。',
    method: 'POST',
    path: '/metrics/_search',
    body: '{\n  "size": 0,\n  "aggs": {\n    "by_minute\": {\n      "date_histogram": { "field": "@timestamp", "fixed_interval": \"1m\" },\n      "aggs": { "value\": { "avg": { "field": \"cpu\" } } }\n    },\n    "moving_avg_5\": {\n      "moving_avg\": { "buckets_path\": \"by_minute>value\", \"window\": 5 }\n    }\n  }\n}'
  },
  {
    id: 'agg_bucket_sort',
    category: 'agg_pipeline',
    title: 'Bucket Sort - 桶内排序截取',
    tags: ['pipeline', 'top N'],
    desc: '对聚合的 bucket 排序并截取前 N（如"取销售额前 5 的产品类别")。',
    method: 'POST',
    path: '/orders/_search',
    body: '{\n  "size": 0,\n  "aggs": {\n    "by_category\": {\n      "terms": { "field": \"category\", \"size\": 100 },\n      "aggs\": { \"revenue\": { \"sum\": { \"field\": \"amount\" } } }\n    },\n    \"top_categories\": {\n      \"bucket_sort\": {\n        \"buckets_path\": \"by_category\",\n        \"sort\": [{ \"revenue\": { \"order\": \"desc\" } }],\n        \"size\": 5\n      }\n    }\n  }\n}'
  },
  {
    id: 'agg_bucket_selector',
    category: 'agg_pipeline',
    title: 'Bucket Selector - 桶过滤',
    tags: ['pipeline', '过滤', 'HAVING'],
    desc: '类似 SQL HAVING：只保留满足条件的桶（avg > 100 等）。',
    method: 'POST',
    path: '/orders/_search',
    body: '{\n  "size": 0,\n  "aggs": {\n    "by_category\": {\n      \"terms\": { \"field\": \"category\" },\n      \"aggs\": {\n        \"avg_amount\": { \"avg\": { \"field\": \"amount\" } },\n        \"big_categories\": {\n          \"bucket_selector\": {\n            \"buckets_path\": { \"avgAmt\": \"avg_amount\" },\n            \"script\": \"params.avgAmt > 100\"\n          }\n        }\n      }\n    }\n  }\n}'
  },
  // ====== 排序与高亮 ======
  {
    id: 'sort_multi',
    category: 'sort_hl',
    title: 'Sort - 多字段排序',
    tags: ['排序', 'Tiebreaker'],
    desc: '多个 sort 字段可指定 tiebreaker（必须唯一，如 _id）。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "query": { "match_all\": {} },\n  "sort": [\n    { "is_promoted": { "order\": \"desc\" } },\n    { \"price\": { \"order\": \"asc\" } },\n    { \"_score\": { \"order\": \"desc\" } },\n    { \"_id\": { \"order\": \"asc\" } }\n  ]\n}'
  },
  {
    id: 'sort_script',
    category: 'sort_hl',
    title: 'Sort by Script - 自定义排序',
    tags: ['排序', '脚本', '复杂逻辑'],
    desc: '用 Painless 脚本按计算值排序（如按销量除以库存的"周转率"排）。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "query\": { "match_all\": {} },\n  "sort": [\n    {\n      \"_script\": {\n        \"type\": \"number\",\n        \"script\": {\n          \"source\": \"doc[\'sales\'].value * 1.0 / (doc[\'stock\'].value + 1)\"\n        },\n        \"order\": \"desc\"\n      }\n    }\n  ]\n}'
  },
  {
    id: 'source_filter',
    category: 'sort_hl',
    title: 'Source Filtering - 字段过滤',
    tags: ['字段过滤', '_source'],
    desc: '只返回指定字段，减少网络带宽（ES 默认返回全部字段）。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  \"_source\": {\n    \"includes\": [ \"name\", \"price\" ],\n    \"excludes\": [ \"description\" ]\n  },\n  \"query\": { \"match_all\": {} }\n}'
  },
  {
    id: 'highlight_advanced',
    category: 'sort_hl',
    title: 'Highlight Advanced - 多字段高亮',
    tags: ['高亮', 'fragmenter'],
    desc: '多字段高亮 + 自定义 fragment_size / number_of_fragments / boundary_scanner。',
    method: 'POST',
    path: '/articles/_search',
    body: '{\n  \"query\": { \"multi_match\": { \"query\": \"elasticsearch\", \"fields\": [\"title\", \"content\"] } },\n  \"highlight\": {\n    \"pre_tags\":  [\"<mark>\"],\n    \"post_tags\": [\"</mark>\"],\n    \"fields\": {\n      \"title\":   { \"number_of_fragments\": 0 },\n      \"content\": { \"fragment_size\": 150, \"number_of_fragments\": 3, \"boundary_scanner\": \"word\" }\n    },\n    \"require_field_match\": false\n  }\n}'
  },
  {
    id: 'collapse',
    category: 'sort_hl',
    title: 'Field Collapsing - 按字段去重',
    tags: ['去重', '每个类别一个'],
    desc: '按某字段去重，每组只返回一条（类似 SQL DISTINCT ON）。inner_hits 可拿到每组的其他匹配。',
    method: 'POST',
    path: '/articles/_search',
    body: '{\n  \"query\": { \"match\": { \"content\": \"elasticsearch\" } },\n  \"collapse\": {\n    \"field\": \"author_id\",\n    \"inner_hits\": {\n      \"name\": \"latest\",\n      \"size\": 1,\n      \"sort\": [ { \"created_at\": \"desc\" } ]\n    }\n  }\n}'
  },
  // ====== Suggest ======
  {
    id: 'completion',
    category: 'suggest',
    title: 'Completion Suggester - 自动补全',
    tags: ['补全', 'completion', '搜索建议'],
    desc: '使用 completion 字段做极快的搜索补全（毫秒级）。前缀匹配 + 模糊匹配。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  \"_source\": false,\n  \"suggest\": {\n    \"product_suggest\": {\n      \"prefix\": \"机\",\n      \"completion\": {\n        \"field\": \"name_suggest\",\n        \"size\": 5,\n        \"skip_duplicates\": true\n      }\n    }\n  }\n}'
  },
  {
    id: 'term_suggester',
    category: 'suggest',
    title: 'Term Suggester - 拼写纠错',
    tags: ['拼写检查', 'term suggester'],
    desc: '基于编辑距离的拼写纠错（"elasticseach" → "elasticsearch"）。',
    method: 'POST',
    path: '/articles/_search',
    body: '{\n  \"_source\": false,\n  \"suggest\": {\n    \"text\": \"elasticsarch\",\n    \"my_suggestion\": {\n      \"term\": {\n        \"field\": \"title\",\n        \"suggest_mode\": \"missing\",\n        \"edit_distance\": 2\n      }\n    }\n  }\n}'
  },
  {
    id: 'phrase_suggester',
    category: 'suggest',
    title: 'Phrase Suggester - 短语纠错',
    tags: ['短语纠错', 'ngram'],
    desc: '对短语/句子做纠错（比 term 更精确但更慢），依赖 ngram 模型。',
    method: 'POST',
    path: '/articles/_search',
    body: '{\n  \"_source\": false,\n  \"suggest\": {\n    \"text\": \"elasticsarch performence tunning\",\n    \"phrase_suggestion\": {\n      \"phrase\": {\n        \"field\": \"title\",\n        \"gram_size\": 3,\n        \"max_errors\": 2,\n        \"confidence\": 0.5\n      }\n    }\n  }\n}'
  },
  // ====== 排错与高级扩展 ======
  {
    id: 'count',
    category: 'special',
    title: 'Count API - 仅统计总数',
    tags: ['count', '性能'],
    desc: '只返回满足条件的文档数，不返回文档内容（性能更好）。',
    method: 'POST',
    path: '/products/_count',
    body: '{\n  \"query\": {\n    \"bool\": {\n      \"filter\": [\n        { \"term\":  { \"category\": \"电脑外设\" } },\n        { \"range\": { \"price\": { \"lte\": 1000 } } }\n      ]\n    }\n  }\n}'
  },
  {
    id: 'validate',
    category: 'special',
    title: 'Validate API - 检查 query 合法性',
    tags: ['validate', '调试'],
    desc: '检查 query 是否合法，不执行搜索。常用于 query 构造错误的快速定位。',
    method: 'POST',
    path: '/products/_validate/query',
    body: '{\n  \"query\": {\n    \"bool\": {\n      \"must\": [{ \"match\": { \"name\": \"机械键盘\" } }]\n    }\n  }\n}'
  },
  {
    id: 'inner_hits',
    category: 'special',
    title: 'Inner Hits - 关联文档',
    tags: ['nested', 'has_child', 'inner_hits'],
    desc: '在 nested/has_child 查询中同时返回关联文档（不只是父/子 ID）。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  \"query\": {\n    \"nested\": {\n      \"path\": \"comments\",\n      \"query\": { \"match\": { \"comments.text\": \"很棒\" } },\n      \"inner_hits\": {\n        \"size\": 3,\n        \"highlight\": { \"fields\": { \"comments.text\": {} } }\n      }\n    }\n  }\n}'
  },
  {
    id: 'script_query_painless',
    category: 'special',
    title: 'Script Query - Painless 复杂查询',
    tags: ['Painless', '脚本查询'],
    desc: '在 query 中嵌入 Painless 脚本（性能差，慎用）。如"销量+浏览量综合评分"。',
    method: 'POST',
    path: '/products/_search',
    body: '{\n  "query": {\n    "script_score": {\n      "query": { "match_all": {} },\n      "script": {\n        "source": "Math.log10(doc[\'sales\'].value + 1) * doc[\'is_promoted\'].value ? 2.0 : 1.0"\n      }\n    }\n  }\n}'
  }
]

const activeSubTab = ref('leaf')
const copiedId = ref('')

const currentCat = computed(() =>
  categories.find((c) => c.id === activeSubTab.value) || categories[0]
)

const filteredRecipes = computed(() =>
  recipes.filter((r) => r.category === activeSubTab.value)
)

async function copy(recipe) {
  try {
    await navigator.clipboard.writeText(recipe.body)
    copiedId.value = recipe.id
    setTimeout(() => (copiedId.value = ''), 1500)
  } catch (_) {
    alert('复制失败，请手动复制')
  }
}

function tryIt(recipe) {
  try {
    sessionStorage.setItem(
      'es-prefill',
      JSON.stringify({
        method: recipe.method,
        path: recipe.path,
        body: recipe.body
      })
    )
  } catch (_) {}
  window.location.href = '/05-tools/curl-client'
}
</script>

<style scoped>
.es-dsl {
  margin: 16px 0;
}

.es-dsl__intro {
  margin-bottom: 16px;
  padding: 10px 12px;
  background: var(--vp-c-bg-mute);
  border-radius: 6px;
  font-size: 13px;
  color: var(--vp-c-text-2);
}

.es-dsl__intro a {
  color: var(--vp-c-brand-1);
}

.es-dsl__subtabs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 16px;
  padding: 8px 0;
  border-bottom: 1px dashed var(--vp-c-divider);
}

.es-dsl__subtab {
  padding: 6px 12px;
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg);
  color: var(--vp-c-text-2);
  border-radius: 16px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.15s;
  white-space: nowrap;
}

.es-dsl__subtab:hover {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-text-1);
}

.es-dsl__subtab--active {
  background: var(--vp-c-brand-1);
  color: white;
  border-color: var(--vp-c-brand-1);
  font-weight: 600;
}

.es-dsl__subtab-count {
  opacity: 0.75;
  font-weight: 400;
}

.es-dsl__cat-title {
  margin: 0 0 12px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--vp-c-divider);
  font-size: 15px;
  color: var(--vp-c-brand-1);
}

.es-dsl__item {
  padding: 12px;
  margin-bottom: 8px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg);
}

.es-dsl__item-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.es-dsl__item-head strong {
  font-size: 14px;
  color: var(--vp-c-text-1);
}

.es-dsl__tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.es-dsl__tag {
  display: inline-block;
  padding: 1px 6px;
  font-size: 10px;
  border-radius: 8px;
  background: var(--vp-c-bg-mute);
  color: var(--vp-c-text-2);
}

.es-dsl__desc {
  font-size: 13px;
  line-height: 1.5;
  color: var(--vp-c-text-2);
  margin: 4px 0 8px;
}

.es-dsl__details {
  font-size: 13px;
  margin: 8px 0;
}

.es-dsl__details summary {
  cursor: pointer;
  color: var(--vp-c-brand-1);
  padding: 4px 0;
  user-select: none;
}

.es-dsl__pre {
  background: #0f172a;
  color: #e2e8f0;
  padding: 16px;
  margin: 8px 0 0;
  border-radius: 6px;
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  font-size: 13px;
  line-height: 1.5;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.es-dsl__actions {
  display: flex;
  gap: 6px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.es-dsl__btn {
  padding: 4px 10px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 12px;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  transition: all 0.15s;
}

.es-dsl__btn:hover {
  background: var(--vp-c-bg-mute);
  border-color: var(--vp-c-brand-1);
}

.es-dsl__btn--sm {
  padding: 4px 10px;
  font-size: 12px;
}

.es-dsl__btn--primary {
  background: var(--vp-c-brand-1);
  color: white;
  border-color: var(--vp-c-brand-1);
  font-weight: 600;
}

.es-dsl__btn--primary:hover {
  background: var(--vp-c-brand-2);
  border-color: var(--vp-c-brand-2);
}
</style>
