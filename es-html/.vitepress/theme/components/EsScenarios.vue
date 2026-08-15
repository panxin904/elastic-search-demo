<template>
  <div class="es-scenarios">
    <div class="es-scenarios__intro">
      <p>
        按<strong>业务场景</strong>组织的 ES 落地方案：每个场景含典型用例、数据特征、关键
        Mapping、索引设计、查询模式、常见陷阱与最佳实践。
        点开折叠详情查看完整代码与可跳转到 <a href="/05-tools/java">Java SDK 速查</a> 的关联 snippet。
      </p>
    </div>

    <div
      v-for="sc in scenarios"
      :key="sc.id"
      class="es-scenario"
    >
      <div class="es-scenario__head">
        <span class="es-scenario__icon">{{ sc.icon }}</span>
        <div class="es-scenario__title-block">
          <strong class="es-scenario__title">{{ sc.title }}</strong>
          <div class="es-scenario__summary">{{ sc.summary }}</div>
        </div>
      </div>

      <!-- 概览：典型场景（始终可见） -->
      <div class="es-scenario__section es-scenario__section--overview">
        <div class="es-scenario__section-title">📌 典型场景</div>
        <div class="es-scenario__usecase">{{ sc.useCase }}</div>
      </div>

      <!-- 概览：数据特征（始终可见） -->
      <div class="es-scenario__section es-scenario__section--overview">
        <div class="es-scenario__section-title">📊 数据特征</div>
        <ul class="es-scenario__features">
          <li v-for="(f, i) in sc.dataFeatures" :key="i">{{ f }}</li>
        </ul>
      </div>

      <!-- 概览：关键 Mapping（始终可见） -->
      <div class="es-scenario__section es-scenario__section--overview">
        <div class="es-scenario__section-title">🗂️ 关键 Mapping（核心字段）</div>
        <pre class="es-scenario__pre">{{ sc.keyMapping }}</pre>
      </div>

      <!-- 折叠详情 -->
      <details class="es-scenario__details">
        <summary class="es-scenario__details-summary">
          <span class="es-scenario__details-icon">🔍</span>
          查看更多：索引设计 / 完整查询 / 常见陷阱 / 最佳实践 / 关联 Snippet
        </summary>

        <div class="es-scenario__details-body">
          <div class="es-scenario__section">
            <div class="es-scenario__section-title">🏗️ 索引设计（命名 + 滚动策略）</div>
            <pre class="es-scenario__pre">{{ sc.indexDesign }}</pre>
          </div>

          <div class="es-scenario__section">
            <div class="es-scenario__section-title">🔎 典型查询模式</div>
            <pre class="es-scenario__pre">{{ sc.queryPatterns }}</pre>
          </div>

          <div class="es-scenario__pitfalls">
            <div class="es-scenario__section-title">⚠️ 常见陷阱</div>
            <ul>
              <li v-for="(p, i) in sc.pitfalls" :key="i">{{ p }}</li>
            </ul>
          </div>

          <div class="es-scenario__best">
            <div class="es-scenario__section-title">✨ 最佳实践</div>
            <ul>
              <li v-for="(b, i) in sc.bestPractices" :key="i">{{ b }}</li>
            </ul>
          </div>

          <div v-if="sc.snippetRefs && sc.snippetRefs.length" class="es-scenario__links">
            <div class="es-scenario__section-title">🔗 关联代码片段</div>
            <div class="es-scenario__link-grid">
              <a
                v-for="refId in sc.snippetRefs"
                :key="refId"
                :href="`/05-tools/java#snippet-${refId}`"
                class="es-scenario__link-btn"
              >
                <span class="es-scenario__link-icon">📄</span>
                <span class="es-scenario__link-text">
                  <span class="es-scenario__link-title">{{ snippetTitleMap[refId] || refId }}</span>
                  <span class="es-scenario__link-cat">跳转到 Java SDK →</span>
                </span>
              </a>
            </div>
          </div>
        </div>
      </details>
    </div>
  </div>
</template>

<script setup>
// 8 个企业级场景：日志 / 搜索 / 时序 / 电商 / 向量 / 地理 / 审计 / 报表
// 每个场景 = 概览（useCase + dataFeatures + keyMapping）+ 折叠详情（设计 + 查询 + 陷阱 + 实践 + 关联）
const scenarios = [
  {
    id: 'log-analytics',
    title: '日志分析（ELK 经典栈）',
    icon: '📋',
    summary: '聚合 Nginx / 应用 / 系统日志做检索与告警，按天滚动 + ILM 冷热分层。',
    useCase: '微服务架构下，统一聚合所有服务的访问日志（Access Log）、应用日志（App Log）、系统日志（Syslog），配合 Kibana 做实时查询与可视化告警。',
    dataFeatures: [
      'Append-only 写入，几乎无更新/删除',
      '时间序列，单条文档 1-5 KB',
      '写入吞吐高（高峰期 GB/分钟），查询集中在近 24h-7d',
      '字段基数中等（host、service、level），message 文本大'
    ],
    indexDesign: "// 推荐索引命名：滚动 + 别名写入\\n// 物理索引：logs-app-2025.07.16 / logs-app-2025.07.17 ...\\n// 写入别名：logs-app-write（始终指向当天物理索引）\\n// 读取别名：logs-app（覆盖所有历史物理索引）",
    keyMapping: "// Index Template 核心字段（所有 logs-* 索引自动应用）\\n{\\n  \"settings\": {\\n    \"index.refresh_interval\": \"5s\",\\n    \"index.number_of_shards\": 1,\\n    \"index.number_of_replicas\": 1,\\n    \"index.lifecycle.name\": \"logs-lifecycle\"\\n  },\\n  \"mappings\": {\\n    \"properties\": {\\n      \"@timestamp\":    { \"type\": \"date\" },\\n      \"level\":         { \"type\": \"keyword\" },\\n      \"service\":       { \"type\": \"keyword\" },\\n      \"host\":          { \"type\": \"keyword\" },\\n      \"trace_id\":      { \"type\": \"keyword\" },\\n      \"message\":       { \"type\": \"text\" }\\n    }\\n  }\\n}",
    queryPatterns: "// 1) 最近 1h ERROR 日志 + 按 service 聚合\\nGET logs-*/_search\\n{\\n  \"query\": {\\n    \"bool\": {\\n      \"filter\": [\\n        { \"term\":  { \"level\": \"ERROR\" } },\\n        { \"range\": { \"@timestamp\": { \"gte\": \"now-1h\" } } }\\n      ]\\n    }\\n  },\\n  \"aggs\": { \"by_service\": { \"terms\": { \"field\": \"service\" } } }\\n}\\n\\n// 2) trace_id 全链路追踪\\nGET logs-*/_search\\n{ \"query\": { \"term\": { \"trace_id\": \"abc-123\" } }, \"sort\": [{ \"@timestamp\": \"asc\" }] }",
    pitfalls: [
      '❌ 用 default analyzer 分词 message → keyword 即可，避免大文本建倒排',
      '❌ 每个服务建独立索引 → 用 service 字段过滤即可，分片过多反而拖累集群',
      '❌ 设置 replicas=2 → 日志索引 1 副本足够，配合 ILM 冷热分层降成本',
      '❌ 直接 PUT /logs/_doc 写数据 → 必须用别名 + rollover，避免单索引爆炸',
      '✅ 用 ILM 策略自动 rollover（30 GB / 7d）→ 热 → 温（7d 后）→ 冷（30d 后）→ 删除'
    ],
    bestPractices: [
      '✅ Filebeat 直推 ES（轻量、低耦合），不用 Logstash 中转',
      '✅ 用 index template 统一 mapping，禁止业务代码 PUT 索引',
      '✅ 用 ILM + Data Streams（8.x）替代手工 rollover',
      '✅ 监控索引大小：GET _cat/indices/logs-*?h=index,store.size&bytes=b'
    ],
    snippetRefs: ['init-client', 'bulk-index', 'reindex', 'index-template']
  },

  {
    id: 'fulltext-search',
    title: '全文搜索（文档/文章搜索）',
    icon: '🔍',
    summary: '文章、博客、文档库的全文检索，重点是中文分词 + 相关性排序。',
    useCase: 'CMS 系统、技术博客、知识库、企业内部文档搜索，重点是高亮 + 相关性 + 检索速度。',
    dataFeatures: [
      '读写比约 10:1，查询密集',
      '中文文本必须分词（IK / 拼音），英文按空格分词',
      '用户期望前 10 条结果即命中（Top-N 优化）',
      '字段较多（title / content / author / tags / category）'
    ],
    indexDesign: "// 索引命名：单索引（数据量 < 千万级）\\n// docs-v1（小数据量单索引）或 docs-YYYY.MM（按月滚动，大数据量）",
    keyMapping: "{\\n  \"settings\": {\\n    \"index.number_of_shards\": 3,\\n    \"index.number_of_replicas\": 1,\\n    \"analysis\": {\\n      \"analyzer\": {\\n        \"ik_smart_pinyin\": {\\n          \"type\": \"custom\",\\n          \"tokenizer\": \"ik_max_word\",\\n          \"filter\": [\"pinyin_filter\"]\\n        }\\n      }\\n    }\\n  },\\n  \"mappings\": {\\n    \"properties\": {\\n      \"title\":   {\\n        \"type\": \"text\",\\n        \"analyzer\": \"ik_max_word\",\\n        \"search_analyzer\": \"ik_smart\",\\n        \"fields\": {\\n          \"keyword\": { \"type\": \"keyword\", \"ignore_above\": 256 }\\n        }\\n      },\\n      \"content\": { \"type\": \"text\", \"analyzer\": \"ik_max_word\" },\\n      \"author\":  { \"type\": \"keyword\" },\\n      \"tags\":    { \"type\": \"keyword\" },\\n      \"category\":{ \"type\": \"keyword\" },\\n      \"publish_date\": { \"type\": \"date\" },\\n      \"view_count\":   { \"type\": \"integer\" }\\n    }\\n  }\\n}",
    queryPatterns: "// 1) multi_match 跨字段搜索 + 字段权重\\nGET docs/_search\\n{\\n  \"query\": {\\n    \"multi_match\": {\\n      \"query\": \"elasticsearch 集群优化\",\\n      \"fields\": [\"title^3\", \"content\", \"tags^2\"],\\n      \"type\": \"best_fields\"\\n    }\\n  },\\n  \"highlight\": {\\n    \"fields\": {\\n      \"title\":   { \"pre_tags\": [\"<em>\"], \"post_tags\": [\"</em>\"] },\\n      \"content\": { \"fragment_size\": 150, \"number_of_fragments\": 2 }\\n    }\\n  }\\n}\\n\\n// 2) function_score 提升热门文章\\nGET docs/_search\\n{\\n  \"query\": {\\n    \"function_score\": {\\n      \"query\": { \"match\": { \"content\": \"性能\" } },\\n      \"functions\": [\\n        { \"field_value_factor\": { \"field\": \"view_count\", \"modifier\": \"log1p\", \"missing\": 1 } }\\n      ],\\n      \"boost_mode\": \"sum\"\\n    }\\n  }\\n}",
    pitfalls: [
      '❌ 用 standard analyzer 索引中文 → 整句作为一个 term，无召回',
      '❌ 高亮但没配 term_vector → 高亮会重查源字段，慢',
      '❌ 用 wildcard "elasticsearch*" 前缀匹配 → 极慢（需遍历所有 term）',
      '❌ from + size 深分页（page=1000） → 用 search_after 替代',
      '❌ 把 title 同时设为 text 和 keyword 但 ignore_above=8191 → keyword 过大浪费内存'
    ],
    bestPractices: [
      '✅ 中文必须装 IK 分词插件，title 索引用 ik_max_word，查询用 ik_smart',
      '✅ 优先用 multi_match（best_fields）而非 multi_disjoint，或用 copy_to 合并字段',
      '✅ 高亮用 unified 高亮器（默认）+ fragment_size 控制片段长度',
      '✅ 深分页用 search_after（基于 sort 值游标），不用 from+size'
    ],
    snippetRefs: ['search-match', 'search-bool', 'search-highlight', 'search-pagination']
  },

  {
    id: 'time-series-monitoring',
    title: '时序数据/监控指标',
    icon: '📈',
    summary: 'APM、IoT、设备指标的高频写入 + 聚合查询，按时间窗口降采样。',
    useCase: '应用性能监控（APM）、IoT 传感器数据、服务器 / 容器 / 业务指标（QPS / Latency / Error Rate）。',
    dataFeatures: [
      '写入密集（每秒数万~百万 metrics）',
      '时间衰减查询：最近 1h/24h 查得最多，历史几乎不查',
      '单条文档小（200 字节左右），但标签基数高（host × region × service）',
      '聚合计算密集（avg / max / p99 / rate）'
    ],
    indexDesign: "// 推荐：metrics-YYYY.MM.dd + downsampling + 数据流（8.x Data Streams）\\n// 或使用 TSDB-like 模式：metrics-prod-write（写入别名，rollover 自动）",
    keyMapping: "{\\n  \"settings\": {\\n    \"index.refresh_interval\": \"10s\",\\n    \"index.number_of_shards\": 3,\\n    \"index.lifecycle.name\": \"metrics-lifecycle\",\\n    \"index.codec\": \"best_compression\"\\n  },\\n  \"mappings\": {\\n    \"properties\": {\\n      \"@timestamp\":   { \"type\": \"date\" },\\n      \"metric_name\":  { \"type\": \"keyword\" },\\n      \"value\":        { \"type\": \"double\" },\\n      \"host\":         { \"type\": \"keyword\" },\\n      \"region\":       { \"type\": \"keyword\" },\\n      \"service\":      { \"type\": \"keyword\" },\\n      \"tags\":         { \"type\": \"object\", \"dynamic\": true }\\n    }\\n  }\\n}",
    queryPatterns: "// 1) 最近 1h 服务的 p99 延迟（聚合计算）\\nGET metrics-*/_search\\n{\\n  \"size\": 0,\\n  \"query\": {\\n    \"bool\": {\\n      \"filter\": [\\n        { \"term\":  { \"service\": \"order-api\" } },\\n        { \"range\": { \"@timestamp\": { \"gte\": \"now-1h\" } } }\\n      ]\\n    }\\n  },\\n  \"aggs\": {\\n    \"timeline\": {\\n      \"date_histogram\": { \"field\": \"@timestamp\", \"fixed_interval\": \"1m\" },\\n      \"aggs\": {\\n        \"p99\": { \"percentiles\": { \"field\": \"value\", \"percents\": [99] } },\\n        \"avg\": { \"avg\": { \"field\": \"value\" } }\\n      }\\n    }\\n  }\\n}\\n\\n// 2) 多服务对比（terms 聚合 + 子聚合）\\n{\\n  \"aggs\": {\\n    \"by_service\": {\\n      \"terms\": { \"field\": \"service\", \"size\": 20 },\\n      \"aggs\": { \"avg_latency\": { \"avg\": { \"field\": \"value\" } } }\\n    }\\n  }\\n}",
    pitfalls: [
      '❌ tags 字段设为 text + 默认分词 → 高基数 keyword 会爆 mapping',
      '❌ 每个 metric_name 建独立索引 → 写入打散，索引爆炸',
      '❌ 没设 refresh_interval=10s → 默认 1s 写入吞吐减半',
      '❌ 长期保留明细数据 → 30 天后用 downsampling 降为 1m/1h 桶',
      '❌ 直接查原始 metrics 做 dashboard → 用 Transform 预聚合'
    ],
    bestPractices: [
      '✅ 高基数标签（user_id、request_id）不进 ES，用 ClickHouse / Doris',
      '✅ 用 Transform（持续聚合）预计算 dashboard 所需指标',
      '✅ 用 downsampling（8.x）把 1s → 1m → 1h 自动降采样',
      '✅ 时序数据启用 _source: false + 单独列存原始字段（7.16+ runtime fields）'
    ],
    snippetRefs: ['agg-java', 'agg-datehisto', 'bulk-index', 'pipeline-create']
  },

  {
    id: 'ecommerce-search',
    title: '电商商品搜索',
    icon: '🛒',
    summary: '多条件筛选 + 排序 + 聚合分面 + 自动补全，nested 字段处理 SKU。',
    useCase: '电商平台的商品列表页、搜索结果页、详情页关联推荐，核心是「搜得到 + 筛得准 + 排得对」。',
    dataFeatures: [
      '字段多（几十个），含 nested 变体（SKU/规格）',
      '查询模式复杂：关键词 + 品牌 + 类目 + 价格区间 + 评分',
      '需聚合分面（facet）：类目/品牌/价格段 计数',
      '热门商品需置顶（销量/评分加权）'
    ],
    indexDesign: "// 索引命名：products-v1（大类目） 或 products-{category}-v1（分类拆分）\\n// 单索引 < 千万级商品；按类目拆分可独立调整 mapping",
    keyMapping: "{\\n  \"settings\": {\\n    \"index.number_of_shards\": 5,\\n    \"analysis\": {\\n      \"analyzer\": { \"ik_smart_pinyin\": { \"type\": \"custom\", \"tokenizer\": \"ik_smart\" } }\\n    }\\n  },\\n  \"mappings\": {\\n    \"properties\": {\\n      \"title\":       {\\n        \"type\": \"text\",\\n        \"analyzer\": \"ik_max_word\",\\n        \"search_analyzer\": \"ik_smart\",\\n        \"fields\": {\\n          \"pinyin\":   { \"type\": \"text\", \"analyzer\": \"pinyin\" },\\n          \"keyword\":  { \"type\": \"keyword\", \"ignore_above\": 256 }\\n        }\\n      },\\n      \"category_id\": { \"type\": \"integer\" },\\n      \"brand\":       { \"type\": \"keyword\" },\\n      \"price\":       { \"type\": \"scaled_float\", \"scaling_factor\": 100 },\\n      \"stock\":       { \"type\": \"integer\" },\\n      \"rating\":      { \"type\": \"float\" },\\n      \"sales_count\": { \"type\": \"long\" },\\n      \"status\":      { \"type\": \"keyword\" },\\n      \"created_at\":  { \"type\": \"date\" },\\n      \"variants\": {\\n        \"type\": \"nested\",\\n        \"properties\": {\\n          \"sku_id\": { \"type\": \"keyword\" },\\n          \"color\":  { \"type\": \"keyword\" },\\n          \"size\":   { \"type\": \"keyword\" },\\n          \"price\":  { \"type\": \"double\" },\\n          \"stock\":  { \"type\": \"integer\" }\\n        }\\n      },\\n      \"title_suggest\": { \"type\": \"completion\" }\\n    }\\n  }\\n}",
    queryPatterns: "// 1) 关键词 + 多条件筛选 + 排序 + 分面聚合（典型搜索页）\\nGET products/_search\\n{\\n  \"query\": {\\n    \"bool\": {\\n      \"must\":   [{ \"multi_match\": { \"query\": \"机械键盘\", \"fields\": [\"title^3\", \"title.pinyin\"] } }],\\n      \"filter\": [\\n        { \"term\":  { \"status\": \"on_sale\" } },\\n        { \"terms\": { \"category_id\": [101, 102] } },\\n        { \"range\": { \"price\": { \"gte\": 100, \"lte\": 1000 } } },\\n        { \"range\": { \"rating\": { \"gte\": 4.0 } } }\\n      ]\\n    }\\n  },\\n  \"sort\": [\\n    { \"_score\": \"desc\" },\\n    { \"sales_count\": \"desc\" }\\n  ],\\n  \"aggs\": {\\n    \"by_brand\":  { \"terms\": { \"field\": \"brand\", \"size\": 20 } },\\n    \"by_rating\": { \"range\": { \"field\": \"rating\", \"ranges\": [{ \"to\": 3 }, { \"from\": 3, \"to\": 4 }, { \"from\": 4 }] } },\\n    \"variants\":  {\\n      \"nested\": { \"path\": \"variants\" },\\n      \"aggs\":   { \"by_color\": { \"terms\": { \"field\": \"variants.color\" } } }\\n    }\\n  }\\n}\\n\\n// 2) SKU 嵌套查询（查找\"红色 256GB\"）\\n{\\n  \"query\": {\\n    \"nested\": {\\n      \"path\": \"variants\",\\n      \"query\": {\\n        \"bool\": {\\n          \"must\": [\\n            { \"term\": { \"variants.color\": \"red\" } },\\n            { \"term\": { \"variants.size\": \"256GB\" } },\\n            { \"range\": { \"variants.stock\": { \"gt\": 0 } } }\\n          ]\\n        }\\n      }\\n    }\\n  }\\n}",
    pitfalls: [
      '❌ price 用 double → 浮点误差，必须用 scaled_float 或 long（分）',
      '❌ SKU 变体用 object 存 → object 数组扁平化，组合查询错乱，必须 nested',
      '❌ 深分页 page=500 → ES 默认 max_result_window=10000，超限报错',
      '❌ status 字段不区分大小写 → keyword 不分词，必须全小写存储',
      '❌ 搜索结果用 _score desc 单一排序 → 加 sales_count 等业务权重'
    ],
    bestPractices: [
      '✅ 价格用 scaled_float（scaling_factor=100 存分为单位）',
      '✅ 多规格变体一律用 nested（不要用 object 数组）',
      '✅ 自动补全用 completion suggester（带 contexts：类目/品牌过滤）',
      '✅ 排序用 function_score 综合 BM25 + 销量 + 评分 + 时新性',
      '✅ 拼音搜索：安装 pinyin 插件 + 多字段 title.pinyin'
    ],
    snippetRefs: ['search-match', 'search-bool', 'agg-java', 'search-pagination']
  },

  {
    id: 'vector-search-rag',
    title: '向量搜索/RAG（AI 时代重点）',
    icon: '🤖',
    summary: '文档问答、语义搜索、图片相似度，dense_vector + knn + 混合检索。',
    useCase: '基于大模型的 RAG（检索增强生成）、企业内部知识库问答、电商相似商品推荐、以文搜图。',
    dataFeatures: [
      '文档切分后入库，每段 200-1000 字 + 对应 embedding',
      'embedding 维度：OpenAI text-embedding-3=1536/3072，BGE=1024',
      '需混合检索：BM25（关键词）+ 向量（语义）',
      '召回后用 RRF（倒数排序融合） 或 reranker 模型精排'
    ],
    indexDesign: "// 必须 ES 8.x+（knn 检索 + RRF 原生支持）\\n// 索引命名：rag-docs-v1（知识库）/ products-embed-v1（商品向量）",
    keyMapping: "{\\n  \"settings\": {\\n    \"index.number_of_shards\": 3,\\n    \"index.knn\": true,\\n    \"index.knn.algo_param.ef_construction\": 200,\\n    \"index.knn.algo_param.m\": 16\\n  },\\n  \"mappings\": {\\n    \"properties\": {\\n      \"title\":     { \"type\": \"text\", \"analyzer\": \"ik_max_word\" },\\n      \"content\":   { \"type\": \"text\", \"analyzer\": \"ik_max_word\" },\\n      \"embedding\": {\\n        \"type\": \"dense_vector\",\\n        \"dims\": 1024,\\n        \"index\": true,\\n        \"similarity\": \"cosine\"\\n      },\\n      \"metadata\": {\\n        \"properties\": {\\n          \"source\":    { \"type\": \"keyword\" },\\n          \"chunk_idx\": { \"type\": \"integer\" },\\n          \"tags\":      { \"type\": \"keyword\" }\\n        }\\n      },\\n      \"created_at\": { \"type\": \"date\" }\\n    }\\n  }\\n}",
    queryPatterns: "// 1) 纯向量检索（knn）\\nPOST rag-docs/_search\\n{\\n  \"knn\": {\\n    \"field\": \"embedding\",\\n    \"query_vector\": [0.12, -0.34, ...],\\n    \"k\": 10,\\n    \"num_candidates\": 100\\n  },\\n  \"_source\": [\"title\", \"content\", \"metadata.source\"]\\n}\\n\\n// 2) 混合检索（BM25 + 向量，8.x RRF 原生融合）\\nPOST rag-docs/_search\\n{\\n  \"query\": {\\n    \"match\": { \"content\": \"elasticsearch 集群脑裂\" }\\n  },\\n  \"knn\": {\\n    \"field\": \"embedding\",\\n    \"query_vector\": [...],\\n    \"k\": 10,\\n    \"num_candidates\": 100,\\n    \"boost\": 0.7\\n  },\\n  \"rank\": {\\n    \"rrf\": {\\n      \"window_size\": 50,\\n      \"rank_constant\": 60\\n    }\\n  }\\n}",
    pitfalls: [
      '❌ 用 ES 7.x 做向量检索 → 7.x 无原生 knn，需用 painless 脚本慢 100x',
      '❌ embedding 维度与索引不一致 → 索引报错或查询报错',
      '❌ similarity 选错：cosine 需先归一化，dot_product 不用归一化',
      '❌ num_candidates 设等于 k → 检索不准，建议 k×10',
      '❌ 向量字段未压缩 → 1024 维 float[] 占 4KB/文档，大规模用 int8_hnsw 量化'
    ],
    bestPractices: [
      '✅ ES 8.x+ 使用原生 knn + RRF（比 7.x 脚本方式快 10-100x）',
      '✅ embedding 模型先选定再定 dims：OpenAI 1536、BGE-large-zh 1024、M3E-large 1024',
      '✅ 大规模（亿级）用 int8_hnsw 量化，节省 75% 内存',
      '✅ 召回 k=10-50，再用 reranker 模型（bge-reranker）精排到 top-5'
    ],
    snippetRefs: ['search-match', 'search-bool', 'agg-java', 'search-highlight']
  },

  {
    id: 'geo-search',
    title: '地理位置搜索',
    icon: '🌍',
    summary: '附近门店、外卖配送、物流追踪，geo_point + geo_distance + 距离排序。',
    useCase: '附近门店查找、外卖配送范围、配送员实时位置、物流轨迹回放。',
    dataFeatures: [
      '每个 POI/人员有经纬度（lat, lon）',
      '查询模式：以"我"为中心，半径/矩形/多边形筛选',
      '需按距离排序（geohash 网格加速）',
      '可能的边界：城市边界、配送区（geo_shape polygon）'
    ],
    indexDesign: "// 索引命名：stores-v1 / couriers-v1（量小单索引）\\n// 大规模按城市分：stores-{city}-v1",
    keyMapping: "{\\n  \"settings\": {\\n    \"index.number_of_shards\": 3\\n  },\\n  \"mappings\": {\\n    \"properties\": {\\n      \"name\":     { \"type\": \"text\", \"fields\": { \"keyword\": { \"type\": \"keyword\" } } },\\n      \"category\": { \"type\": \"keyword\" },\\n      \"address\":  { \"type\": \"text\" },\\n      \"city\":     { \"type\": \"keyword\" },\\n      \"location\": { \"type\": \"geo_point\" },\\n      \"service_area\": {\\n        \"type\": \"geo_shape\",\\n        \"tree\": \"quadtree\",\\n        \"precision\": \"10m\"\\n      },\\n      \"rating\":   { \"type\": \"float\" },\\n      \"open_time\": { \"type\": \"keyword\" }\\n    }\\n  }\\n}",
    queryPatterns: "// 1) 附近 3km 内的所有餐饮（按距离排序）\\nGET stores/_search\\n{\\n  \"query\": {\\n    \"bool\": {\\n      \"must\": { \"match_all\": {} },\\n      \"filter\": {\\n        \"geo_distance\": {\\n          \"distance\": \"3km\",\\n          \"location\": { \"lat\": 39.9087, \"lon\": 116.3975 }\\n        }\\n      }\\n    }\\n  },\\n  \"sort\": [\\n    {\\n      \"_geo_distance\": {\\n        \"location\": { \"lat\": 39.9087, \"lon\": 116.3975 },\\n        \"order\": \"asc\",\\n        \"unit\": \"km\",\\n        \"distance_type\": \"arc\"\\n      }\\n    }\\n  ]\\n}\\n\\n// 2) 矩形范围内 + 多边形范围（配送区）\\nGET stores/_search\\n{\\n  \"query\": {\\n    \"bool\": {\\n      \"filter\": [\\n        { \"geo_bounding_box\": {\\n          \"location\": {\\n            \"top_left\":     { \"lat\": 39.95, \"lon\": 116.30 },\\n            \"bottom_right\": { \"lat\": 39.85, \"lon\": 116.50 }\\n          }\\n        }},\\n        { \"geo_shape\": {\\n          \"service_area\": {\\n            \"shape\": { \"type\": \"point\", \"coordinates\": [116.40, 39.90] },\\n            \"relation\": \"within\"\\n          }\\n        }}\\n      ]\\n    }\\n  }\\n}",
    pitfalls: [
      '❌ 经纬度顺序写反 → ES 用 lat,lon 顺序（GeoJSON 用 lon,lat），混淆必出错',
      '❌ 用 text 存坐标 → 必须 geo_point / geo_shape',
      '❌ 距离单位混用 km/mile → 必须显式指定 unit',
      '❌ 配送区用 geo_point 多点连成线 → 必须 geo_shape polygon',
      '❌ 跨城市查询性能差 → 按城市前缀分片索引'
    ],
    bestPractices: [
      '✅ 写入坐标前校验：lat ∈ [-90, 90], lon ∈ [-180, 180]',
      '✅ 默认用 arc 距离（球面），精确但慢；小范围用 plane 距离快',
      '✅ 配送区用 geo_shape + quadtree 精度 1km 即可，节省存储',
      '✅ 按城市分片（stores-beijing-v1）避免跨城市全局查询'
    ],
    snippetRefs: ['search-match', 'search-bool', 'agg-java', 'search-pagination']
  },

  {
    id: 'security-audit',
    title: '安全审计/合规',
    icon: '🔒',
    summary: '金融交易、操作日志、权限审计，append-only + 长期保留 + 防篡改。',
    useCase: '金融交易流水、用户操作审计、API 调用记录、权限变更记录，需满足 GDPR/等保/SOX 合规。',
    dataFeatures: [
      'append-only 写入，绝不更新 / 删除（合规要求）',
      '保留周期长（3-7 年），需冷归档',
      '查询模式固定（按用户 / 按时间 / 按资源）',
      '防篡改：哈希链 / 签名 / 加密存储'
    ],
    indexDesign: "// 索引命名：audit-finance-YYYY（按年滚动，物理隔离）\\n// 写入别名：audit-finance-write\\n// 读取别名：audit-finance-read",
    keyMapping: "{\\n  \"settings\": {\\n    \"index.number_of_shards\": 1,\\n    \"index.number_of_replicas\": 2,\\n    \"index.lifecycle.name\": \"audit-lifecycle\",\\n    \"index.routing.allocation.require.box_type\": \"warm\"\\n  },\\n  \"mappings\": {\\n    \"properties\": {\\n      \"@timestamp\":     { \"type\": \"date\" },\\n      \"user_id\":        { \"type\": \"keyword\" },\\n      \"user_role\":      { \"type\": \"keyword\" },\\n      \"action\":         { \"type\": \"keyword\" },\\n      \"resource_type\":  { \"type\": \"keyword\" },\\n      \"resource_id\":    { \"type\": \"keyword\" },\\n      \"result\":         { \"type\": \"keyword\" },\\n      \"ip\":             { \"type\": \"ip\" },\\n      \"user_agent\":     { \"type\": \"keyword\", \"ignore_above\": 512 },\\n      \"request_id\":     { \"type\": \"keyword\" },\\n      \"amount\":         { \"type\": \"scaled_float\", \"scaling_factor\": 100 },\\n      \"currency\":       { \"type\": \"keyword\" },\\n      \"metadata\":       { \"type\": \"object\", \"enabled\": true },\\n      \"prev_hash\":      { \"type\": \"keyword\", \"index\": false },\\n      \"record_hash\":    { \"type\": \"keyword\", \"index\": false }\\n    }\\n  }\\n}",
    queryPatterns: "// 1) 查询某用户最近 30 天所有失败操作\\nGET audit-finance-*/_search\\n{\\n  \"query\": {\\n    \"bool\": {\\n      \"filter\": [\\n        { \"term\":  { \"user_id\": \"u_10086\" } },\\n        { \"term\":  { \"result\": \"failure\" } },\\n        { \"range\": { \"@timestamp\": { \"gte\": \"now-30d\" } } }\\n      ]\\n    }\\n  },\\n  \"sort\": [{ \"@timestamp\": \"desc\" }],\\n  \"size\": 100\\n}\\n\\n// 2) 来自某 IP 段的异常登录\\nGET audit-finance-*/_search\\n{\\n  \"query\": {\\n    \"bool\": {\\n      \"filter\": [\\n        { \"term\":  { \"action\": \"login\" } },\\n        { \"term\":  { \"result\": \"failure\" } },\\n        { \"range\": { \"ip\": { \"gte\": \"203.0.113.0\", \"lte\": \"203.0.113.255\" } } }\\n      ]\\n    }\\n  }\\n}",
    pitfalls: [
      '❌ 在应用层 UPDATE 审计日志（修正错误）→ 必须 append-only，业务改正用追加补充日志',
      '❌ 只设 1 副本 → 审计数据必须 2 副本 + 跨节点分布',
      '❌ 用默认 mapping 不指定 ip 类型 → 用 ip 类型支持 CIDR 高效查询',
      '❌ 没做定期 snapshot → 必须按月 snapshot 到 S3/OSS 做长期归档',
      '❌ 索引暴露公网 → 强制 xpack.security + IP 白名单'
    ],
    bestPractices: [
      '✅ append-only：应用层禁用 update/delete API（用 ILM readonly block + 权限控制）',
      '✅ 哈希链防篡改：每条记录存 prev_hash + record_hash，校验时串联哈希',
      '✅ ILM 策略：hot(0-30d) → warm(30d-1y) → cold(1y-3y) → frozen(3y-7y) → delete(7y+)',
      '✅ 按月 snapshot 到对象存储（S3/OSS/COS），保留期独立于 ES',
      '✅ 启用 audit log（ES 自身 xpack），记录所有访问审计日志的操作'
    ],
    snippetRefs: ['init-secure', 'bulk-index', 'snapshot-create', 'update-settings']
  },

  {
    id: 'real-time-analytics',
    title: '实时报表/BI 分析',
    icon: '📊',
    summary: '业务仪表板、用户行为分析，重点是预聚合 + composite 分桶 + 缓存。',
    useCase: '电商 GMV 实时大屏、用户行为漏斗、留存分析、A/B 测试报表。',
    dataFeatures: [
      '写入：用户行为埋点（点击/曝光/下单），高吞吐',
      '查询：dashboard 实时刷新（5-30 秒一次）',
      '聚合维度多（时间 + 渠道 + 城市 + 用户分群）',
      '查询 QPS 高，但结果集小（聚合结果）'
    ],
    indexDesign: "// 双层架构：\\n// 1) 原始事件索引：events-YYYY.MM.dd（高写入，保留 30 天）\\n// 2) 预聚合索引：metrics_dashboard（Transform 持续聚合，长期保留）",
    keyMapping: "{\\n  \"settings\": {\\n    \"index.refresh_interval\": \"5s\",\\n    \"index.number_of_shards\": 3,\\n    \"index.lifecycle.name\": \"events-lifecycle\"\\n  },\\n  \"mappings\": {\\n    \"properties\": {\\n      \"@timestamp\":   { \"type\": \"date\" },\\n      \"event_type\":   { \"type\": \"keyword\" },\\n      \"user_id\":      { \"type\": \"keyword\" },\\n      \"session_id\":   { \"type\": \"keyword\" },\\n      \"page_id\":      { \"type\": \"keyword\" },\\n      \"channel\":      { \"type\": \"keyword\" },\\n      \"city\":         { \"type\": \"keyword\" },\\n      \"device\":       { \"type\": \"keyword\" },\\n      \"amount\":       { \"type\": \"scaled_float\", \"scaling_factor\": 100 },\\n      \"is_new_user\":  { \"type\": \"boolean\" },\\n      \"ab_group\":     { \"type\": \"keyword\" }\\n    }\\n  }\\n}",
    queryPatterns: "// 1) 当日实时 GMV + 订单数（每分钟刷新）\\nGET metrics_dashboard/_search\\n{\\n  \"size\": 0,\\n  \"query\": { \"term\": { \"metric_type\": \"gmv_realtime\" } },\\n  \"aggs\": {\\n    \"by_minute\": {\\n      \"date_histogram\": { \"field\": \"bucket_time\", \"fixed_interval\": \"1m\" },\\n      \"aggs\": {\\n        \"total_amount\": { \"sum\": { \"field\": \"amount\" } },\\n        \"order_count\":  { \"value_count\": { \"field\": \"order_id\" } }\\n      }\\n    }\\n  }\\n}\\n\\n// 2) 漏斗分析（每步转化率）—— 用 filters aggregation\\n{\\n  \"aggs\": {\\n    \"step_view\":   { \"filter\": { \"term\": { \"event_type\": \"view\" } } },\\n    \"step_click\":  { \"filter\": { \"term\": { \"event_type\": \"click\" } } },\\n    \"step_order\":  { \"filter\": { \"term\": { \"event_type\": \"order\" } } },\\n    \"step_pay\":    { \"filter\": { \"term\": { \"event_type\": \"pay\" } } }\\n  }\\n}",
    pitfalls: [
      '❌ 直接在原始事件索引上跑 dashboard 查询 → 慢且资源消耗大',
      '❌ 大聚合返回上千个 bucket → 用 composite aggregation 分页',
      '❌ script 聚合（painless）→ 慢，能用内置聚合就用内置',
      '❌ 指标计算放应用层做 group by → 放进 ES 聚合或 Transform',
      '❌ dashboard 每秒刷新 → 至少 30 秒一次，配合 10 秒缓存'
    ],
    bestPractices: [
      '✅ 用 Transform 持续预聚合（每 1m/5m 一次），dashboard 查预聚合索引',
      '✅ 复合维度聚合用 composite aggregation + after 参数分页',
      '✅ 漏斗分析用 filters aggregation（多 filter 子句），不要用 script',
      '✅ 长期报表数据导出到 ClickHouse/Doris，ES 只保留近 90 天明细'
    ],
    snippetRefs: ['agg-java', 'agg-datehisto', 'update-by-query', 'pipeline-create']
  }
]

// 关联 snippet ID → 中文标题（用于跳转按钮文案）
const snippetTitleMap = {
  'init-client': '创建 ElasticsearchClient',
  'init-secure': '启用 Basic Auth',
  'init-pool': '连接池 + 超时配置',
  'init-sniff': '节点嗅探 Sniffer',
  'init-custom-json': '自定义 JSON Mapper',
  'ping': 'Ping 健康探活',
  'info': '集群 Info',
  'index-create': '创建索引',
  'index-doc': '索引（写入）文档',
  'get-doc': '获取文档',
  'delete-doc': '删除文档',
  'update-doc': '部分更新文档',
  'search-match': 'Match Query',
  'search-bool': 'Bool Query 组合',
  'search-highlight': '高亮命中关键字',
  'search-pagination': '深度分页 search_after',
  'count-api': 'Count API',
  'exists-api': 'Exists API',
  'multi-get': 'Multi Get',
  'update-by-query': 'Update By Query',
  'delete-by-query': 'Delete By Query',
  'field-collapse-java': 'Field Collapse',
  'multi-search-java': 'Multi Search',
  'scroll-api': 'Scroll API',
  'pit-search-after': 'PIT + Search After',
  'agg-java': '聚合查询 Terms + Metrics',
  'agg-datehisto': 'Date Histogram',
  'bulk-index': 'Bulk 批量操作',
  'reindex': 'Reindex 重建索引',
  'pipeline-create': '创建 Ingest Pipeline',
  'pipeline-simulate': '测试 Pipeline',
  'pipeline-use': '写入时使用 Pipeline',
  'update-settings': '动态更新 Settings',
  'put-mapping': '动态添加 Mapping',
  'get-mapping': '获取索引 Mapping',
  'delete-index': '删除索引',
  'close-open': 'Close / Open 索引',
  'shrink-index': 'Shrink 收缩分片',
  'force-merge': 'Force Merge',
  'snapshot-repo': '注册 Snapshot 仓库',
  'snapshot-create': '创建快照',
  'snapshot-restore': '从快照恢复',
  'snapshot-list': '列出与管理快照',
  'alias-add': '添加别名',
  'alias-atomic-switch': '原子切换别名',
  'alias-write-index': '写入别名',
  'alias-get': '查询别名映射',
  'async-listener': '异步调用 + Listener',
  'cat-indices-java': 'Cat Indices API',
  'tasks-list': '查询运行中 Task',
  'script-query': 'Painless 脚本查询',
  'refresh-for-tests': '强制 Refresh',
  'health': '集群健康检查',
  'index-template': '索引模板'
}
</script>

<style scoped>
.es-scenarios {
  margin-top: 12px;
}
.es-scenarios__intro {
  padding: 12px 16px;
  margin-bottom: 16px;
  background: var(--vp-c-bg-soft);
  border-left: 3px solid var(--vp-c-brand-1);
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.7;
  color: var(--vp-c-text-1);
}
.es-scenarios__intro a {
  color: var(--vp-c-brand-1);
  font-weight: 500;
}

.es-scenario {
  margin: 16px 0;
  padding: 0;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 10px;
  overflow: hidden;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.es-scenario:hover {
  border-color: var(--vp-c-brand-1);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.es-scenario__head {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 18px;
  background: linear-gradient(135deg, var(--vp-c-brand-soft), transparent);
  border-bottom: 1px solid var(--vp-c-divider);
}
.es-scenario__icon {
  font-size: 28px;
  line-height: 1.2;
  flex-shrink: 0;
}
.es-scenario__title-block {
  flex: 1;
  min-width: 0;
}
.es-scenario__title {
  display: block;
  font-size: 17px;
  font-weight: 600;
  color: var(--vp-c-text-1);
  margin-bottom: 4px;
}
.es-scenario__summary {
  font-size: 13px;
  color: var(--vp-c-text-2);
  line-height: 1.5;
}

.es-scenario__section {
  padding: 14px 18px;
  border-bottom: 1px solid var(--vp-c-divider);
}
.es-scenario__section:last-child {
  border-bottom: none;
}
.es-scenario__section--overview {
  background: var(--vp-c-bg);
}
.es-scenario__section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--vp-c-brand-1);
  margin-bottom: 8px;
  letter-spacing: 0.02em;
}
.es-scenario__usecase {
  font-size: 14px;
  line-height: 1.7;
  color: var(--vp-c-text-1);
}
.es-scenario__features {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  line-height: 1.8;
  color: var(--vp-c-text-1);
}
.es-scenario__features li {
  margin-bottom: 2px;
}
.es-scenario__pre {
  margin: 0;
  padding: 12px 14px;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  font-size: 12px;
  line-height: 1.55;
  font-family: var(--vp-font-family-mono);
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--vp-c-text-1);
}

.es-scenario__details {
  border-top: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg-mute);
}
.es-scenario__details-summary {
  padding: 12px 18px;
  font-size: 13px;
  font-weight: 500;
  color: var(--vp-c-brand-1);
  cursor: pointer;
  list-style: none;
  user-select: none;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background 0.15s;
}
.es-scenario__details-summary:hover {
  background: var(--vp-c-bg);
}
.es-scenario__details-summary::-webkit-details-marker {
  display: none;
}
.es-scenario__details[open] .es-scenario__details-summary {
  border-bottom: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg);
}
.es-scenario__details[open] .es-scenario__details-summary::before {
  content: '▼';
  font-size: 9px;
  color: var(--vp-c-brand-1);
  margin-right: 2px;
}
.es-scenario__details:not([open]) .es-scenario__details-summary::before {
  content: '▶';
  font-size: 9px;
  color: var(--vp-c-text-2);
  margin-right: 2px;
}
.es-scenario__details-icon {
  font-size: 14px;
}
.es-scenario__details-body {
  padding: 4px 0;
}

.es-scenario__pitfalls,
.es-scenario__best {
  padding: 14px 18px;
  border-bottom: 1px solid var(--vp-c-divider);
}
.es-scenario__pitfalls ul,
.es-scenario__best ul {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  line-height: 1.8;
  font-family: var(--vp-font-family-mono);
}
.es-scenario__pitfalls li {
  color: var(--vp-c-text-1);
  margin-bottom: 2px;
}
.es-scenario__best li {
  color: var(--vp-c-text-1);
  margin-bottom: 2px;
}

.es-scenario__links {
  padding: 14px 18px;
}
.es-scenario__link-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 8px;
}
.es-scenario__link-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  transition: all 0.15s;
  text-decoration: none;
  color: inherit;
}
.es-scenario__link-btn:hover {
  border-color: var(--vp-c-brand-1);
  background: var(--vp-c-brand-soft);
  transform: translateY(-1px);
}
.es-scenario__link-icon {
  font-size: 16px;
  flex-shrink: 0;
}
.es-scenario__link-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.es-scenario__link-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--vp-c-text-1);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.es-scenario__link-cat {
  font-size: 11px;
  color: var(--vp-c-text-2);
  font-family: var(--vp-font-family-mono);
}
</style>