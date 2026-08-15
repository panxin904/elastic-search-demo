<template>
  <div class="es-java">
    <div class="es-java__intro">
      ☕ 按 <strong>{{ categories.length }} 大类</strong>整理共 <strong>{{ snippets.length }}</strong> 个 Java Client 代码片段。
      点击分类切换显示该类所有代码，「📋 复制」可直接粘贴到 IDE。
    </div>

    <div class="es-java__banner">
      ⚠️ <strong>关于 RestHighLevelClient</strong>：7.15 起官方已 <strong>deprecated</strong>，8.x 完全移除。
      新项目请用 <code>co.elastic.clients:elasticsearch-java</code>。
      存量项目可点击各分类内代码段上的切换按钮查看 RHLC ↔ New Client 对照。
    </div>

    <details class="es-java__maven" open>
      <summary>📦 Maven 依赖（必读）</summary>
      <pre class="es-java__pre">{{ mavenDep }}</pre>
      <div class="es-java__actions">
        <button class="es-java__btn es-java__btn--sm" @click="copy(mavenDep, 'maven')">
          {{ copiedId === 'maven' ? '已复制 ✓' : '📋 复制' }}
        </button>
      </div>
    </details>

    <div class="es-java__subtabs">
      <button
        v-for="cat in categories"
        :key="cat.id"
        :class="['es-java__subtab', { 'es-java__subtab--active': activeSubTab === cat.id }]"
        @click="activeSubTab = cat.id"
      >
        {{ cat.icon }} {{ cat.label }}
        <span class="es-java__subtab-count">
          ({{ snippets.filter(s => s.category === cat.id).length }})
        </span>
      </button>
    </div>

    <div class="es-java__cat-title">
      {{ currentCat.icon }} {{ currentCat.label }}
    </div>

    <div
      v-for="snippet in filteredSnippets"
      :id="'snippet-' + snippet.id"
      :key="snippet.id"
      class="es-java__item"
    >
      <div class="es-java__item-head">
        <strong>{{ snippet.title }}</strong>
        <div class="es-java__tags">
          <span
            v-for="tag in snippet.tags"
            :key="tag"
            class="es-java__tag"
          >{{ tag }}</span>
        </div>
      </div>
      <div class="es-java__desc">{{ snippet.desc }}</div>

      <!-- 依赖提示 -->
      <div v-if="snippet.deps" class="es-java__deps">
        <strong>📦 依赖：</strong> <code>{{ snippet.deps }}</code>
      </div>

      <!-- 客户端切换标签（仅当两种客户端代码都存在时） -->
      <div v-if="snippet.code && snippet.oldClient" class="es-java__toggle">
        <button
          class="es-java__toggle-btn"
          :class="{ 'es-java__toggle-btn--active': !showAlt[snippet.id] }"
          @click="showAlt[snippet.id] = false"
        >
          <span class="es-java__toggle-dot es-java__toggle-dot--new"></span>
          {{ snippet.codeLabel || '🆕 New Client' }}
        </button>
        <button
          class="es-java__toggle-btn"
          :class="{ 'es-java__toggle-btn--active': showAlt[snippet.id] }"
          @click="showAlt[snippet.id] = true"
        >
          <span class="es-java__toggle-dot es-java__toggle-dot--old"></span>
          {{ snippet.oldClientLabel || '🕰️ RestHighLevelClient' }}
        </button>
        <span class="es-java__toggle-group">{{ showAlt[snippet.id] ? (snippet.oldClientGroup || 'org.elasticsearch.client') : (snippet.codeGroup || 'co.elastic.clients') }}</span>
      </div>

      <!-- 代码块：展示当前选中客户端版本 -->
      <template v-if="showAlt[snippet.id] && snippet.oldClient">
        <pre class="es-java__pre es-java__pre--old">{{ snippet.oldClient }}</pre>
        <div class="es-java__actions">
          <button class="es-java__btn es-java__btn--sm" @click="copy(snippet.oldClient, snippet.id + '-alt')">
            {{ copiedId === snippet.id + '-alt' ? '已复制 ✓' : '📋 复制' }}
          </button>
        </div>
      </template>
      <template v-else-if="snippet.code">
        <pre class="es-java__pre">{{ snippet.code }}</pre>
        <div class="es-java__actions">
          <button class="es-java__btn es-java__btn--sm" @click="copy(snippet.code, snippet.id)">
            {{ copiedId === snippet.id ? '已复制 ✓' : '📋 复制' }}
          </button>
        </div>
      </template>

      <!-- 关键差异说明 -->
      <div v-if="snippet.differences && snippet.differences.length" class="es-java__diffs">
        <div class="es-java__diffs-title">🔍 关键差异</div>
        <ul>
          <li v-for="(d, i) in snippet.differences" :key="i">{{ d }}</li>
        </ul>
      </div>

      <div class="es-java__actions es-java__actions--footer">
        <a
          v-if="snippet.docLink"
          :href="snippet.docLink"
          target="_blank"
          rel="noopener"
          class="es-java__btn es-java__btn--sm es-java__btn--link"
        >
          📖 官方文档
        </a>
      </div>
    </div>

    <div class="es-java__links">
      🔗 本项目源码：
      <a href="https://github.com/your-repo/blob/main/src/main/java/com/example/esdemo/service/ElasticsearchService.java" target="_blank" rel="noopener">
        ElasticsearchService.java
      </a>
      ·
      <a href="https://github.com/your-repo/blob/main/src/test/java/com/example/esdemo/service/ElasticsearchServiceTest.java" target="_blank" rel="noopener">
        ElasticsearchServiceTest.java
      </a>
      ·
      <a href="https://www.elastic.co/guide/en/elasticsearch/client/java-api-client/current/introduction.html" target="_blank" rel="noopener">
        Java Client 文档
      </a>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'

const mavenDep = `<!-- pom.xml (本项目 7.17.10 配套版本) -->
<dependency>
  <groupId>co.elastic.clients</groupId>
  <artifactId>elasticsearch-java</artifactId>
  <version>7.17.10</version>
</dependency>
<dependency>
  <groupId>com.fasterxml.jackson.core</groupId>
  <artifactId>jackson-databind</artifactId>
  <version>2.16.1</version>
</dependency>
<dependency>
  <groupId>org.glassfish</groupId>
  <artifactId>jakarta.json</artifactId>
  <version>2.0.1</version>
</dependency>
<dependency>
  <groupId>org.slf4j</groupId>
  <artifactId>slf4j-api</artifactId>
  <version>2.0.12</version>
</dependency>`

const categories = [
  { id: 'init', label: '客户端初始化', icon: '🔌' },
  { id: 'init_adv', label: '高级配置', icon: '⚙️' },
  { id: 'crud', label: 'CRUD 操作', icon: '📝' },
  { id: 'search', label: '搜索查询', icon: '🔍' },
  { id: 'search_adv', label: '搜索进阶', icon: '🔎' },
  { id: 'agg', label: '聚合分析', icon: '📊' },
  { id: 'bulk', label: '批量操作', icon: '📦' },
  { id: 'ingest', label: 'Ingest Pipeline', icon: '🔄' },
  { id: 'index_mgmt', label: '索引管理', icon: '🗂️' },
  { id: 'snapshot', label: 'Snapshot 管理', icon: '💾' },
  { id: 'alias', label: '别名管理', icon: '🔀' },
  { id: 'advanced', label: '高级特性', icon: '🛠️' }
]

const snippets = [
  {
    id: 'init-client',
    category: 'init',
    title: '创建 ElasticsearchClient',
    tags: ['7.x', '初始化'],
    desc: '通过 RestClient.builder 创建 ElasticsearchClient。生产环境建议配置连接池与超时。',
    docLink: 'https://www.elastic.co/guide/en/elasticsearch/client/java-api-client/current/installation.html',
    code: `import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.json.jackson.JacksonJsonpMapper;
import co.elastic.clients.transport.ElasticsearchTransport;
import co.elastic.clients.transport.rest_client.RestClientTransport;
import org.apache.http.HttpHost;
import org.elasticsearch.client.RestClient;

RestClient restClient = RestClient.builder(
    new HttpHost("localhost", 9200, "http")
).build();

ElasticsearchTransport transport = new RestClientTransport(
    restClient, new JacksonJsonpMapper()
);

ElasticsearchClient client = new ElasticsearchClient(transport);

// 使用后关闭
// transport.close();
// restClient.close();`,
    oldClient: `import org.elasticsearch.client.RestHighLevelClient;
import org.apache.http.HttpHost;

// RestHighLevelClient —— 直接构建，无需 Transport 层
RestHighLevelClient client = new RestHighLevelClient(
    RestClient.builder(new HttpHost("localhost", 9200, "http"))
);

// 关闭
// client.close();`
  },
  {
    id: 'init-secure',
    category: 'init',
    title: '启用 Basic Auth',
    tags: ['认证', 'xpack'],
    desc: '当 ES 启用了 xpack.security 时，需要在 RestClient 中配置凭据。',
    code: `import org.apache.http.auth.AuthScope;
import org.apache.http.auth.UsernamePasswordCredentials;
import org.apache.http.impl.client.BasicCredentialsProvider;

BasicCredentialsProvider creds = new BasicCredentialsProvider();
creds.setCredentials(
    AuthScope.ANY,
    new UsernamePasswordCredentials("elastic", "changeme")
);

RestClient restClient = RestClient.builder(
    new HttpHost("localhost", 9200, "https")
).setHttpClientConfigCallback(http -> http
    .setSSLContext(sslContext)
    .setDefaultCredentialsProvider(creds)
).build();`,
    oldClient: `import org.elasticsearch.client.RestHighLevelClient;
import org.apache.http.auth.AuthScope;
import org.apache.http.auth.UsernamePasswordCredentials;
import org.apache.http.impl.client.BasicCredentialsProvider;

BasicCredentialsProvider creds = new BasicCredentialsProvider();
creds.setCredentials(AuthScope.ANY,
    new UsernamePasswordCredentials("elastic", "changeme"));

// RHLC：setHttpClientConfigCallback 方式完全相同
RestHighLevelClient client = new RestHighLevelClient(
    RestClient.builder(new HttpHost("localhost", 9200, "https"))
        .setHttpClientConfigCallback(http -> http
            .setSSLContext(sslContext)
            .setDefaultCredentialsProvider(creds)
        )
);`
  },
  {
    id: 'index-create',
    category: 'crud',
    title: '创建索引',
    tags: ['Mapping', 'create'],
    desc: '本项目 ElasticsearchService#createIndex 的实现。生产建议配合索引模板批量创建。',
    docLink: 'https://www.elastic.co/guide/en/elasticsearch/client/java-api-client/current/loading-json.html',
    code: `import co.elastic.clients.elasticsearch.indices.CreateIndexResponse;
import co.elastic.clients.elasticsearch.indices.ExistsRequest;

boolean exists = client.indices()
    .exists(ExistsRequest.of(e -> e.index("products")))
    .value();

    if (!exists) {
    CreateIndexResponse resp = client.indices().create(c -> c
        .index("products")
        .mappings(m -> m
            .properties("name",     p -> p.text(t -> t.analyzer("ik_max_word")))
            .properties("price",    p -> p.double_(d -> d))
            .properties("category", p -> p.keyword(k -> k))
            .properties("created",  p -> p.date(d -> d))
        )
    );
    System.out.println("Created: " + resp.acknowledged());
}`,
    oldClient: `// RHLC：CreateIndexRequest 构建
import org.elasticsearch.client.indices.CreateIndexRequest;
import org.elasticsearch.client.indices.CreateIndexResponse;
import org.elasticsearch.common.xcontent.XContentType;

CreateIndexRequest request = new CreateIndexRequest("products");
request.mapping("{\n" +
    "  \"properties\": {\n" +
    "    \"name\":     { \"type\": \"text\", \"analyzer\": \"ik_max_word\" },\n" +
    "    \"price\":    { \"type\": \"double\" },\n" +
    "    \"category\": { \"type\": \"keyword\" },\n" +
    "    \"created\":  { \"type\": \"date\" }\n" +
    "  }\n" +
    "}", XContentType.JSON);

CreateIndexResponse resp = client.indices().create(request, RequestOptions.DEFAULT);
System.out.println("Created: " + resp.isAcknowledged());`,
    differences: [
      'RHLC 用 CreateIndexRequest 手动拼接 JSON mapping；New Client 用 Lambda DSL 类型安全',
      'RHLC 检查索引是否存在用 RestHighLevelClient.indices().exists() 返回 boolean；New Client 用 ExistsRequest.of()',
      'New Client 的 mapping 定义可直接用 Java 对象，无需拼接字符串'
    ]
  },
  {
    id: 'index-doc',
    category: 'crud',
    title: '索引（写入）文档',
    tags: ['IndexRequest', 'JSON'],
    desc: '本项目 ElasticsearchService#indexProduct 的实现。docPath 是 id，document 是实体对象（Jackson 自动序列化）。',
    code: `import co.elastic.clients.elasticsearch.core.IndexResponse;
import co.elastic.clients.elasticsearch.core.IndexRequest;

IndexRequest<Product> request = IndexRequest.of(i -> i
    .index("products")
    .id(product.getId())
    .document(product)
);

IndexResponse response = client.index(request);
System.out.println("Result: " + response.result()
    + ", ID: " + response.id());`,
    oldClient: `// RHLC：IndexRequest 传 Map 或 String
import org.elasticsearch.action.index.IndexRequest;
import org.elasticsearch.action.index.IndexResponse;

Map<String, Object> doc = new HashMap<>();
doc.put("name", product.getName());
doc.put("price", product.getPrice());

IndexRequest request = new IndexRequest("products")
    .id(product.getId())
    .source(doc);

IndexResponse resp = client.index(request, RequestOptions.DEFAULT);
System.out.println("Result: " + resp.getResult()
    + ", ID: " + resp.getId());`,
    differences: [
      'New Client 直接传入实体对象作为 .document(product)，自动序列化；RHLC 需手动构建 Map',
      'New Client 支持 IndexRequest.of() Lambda DSL；RHLC 用 new IndexRequest() 构造后 setter'
    ]
  },
  {
    id: 'get-doc',
    category: 'crud',
    title: '获取文档',
    tags: ['Get', 'Optional'],
    desc: '本项目 ElasticsearchService#getProduct 的实现。用 Optional<Product> 表达"可能不存在"。',
    code: `import co.elastic.clients.elasticsearch.core.GetRequest;
import co.elastic.clients.elasticsearch.core.GetResponse;

GetResponse<Product> response = client.get(
    GetRequest.of(g -> g.index("products").id("p001")),
    Product.class
);

Optional<Product> product = response.found()
    ? Optional.ofNullable(response.source())
    : Optional.empty();`,
    oldClient: `// RHLC：GetResponse.getSource() 返回 Map 需手动转换
import org.elasticsearch.action.get.GetRequest;
import org.elasticsearch.action.get.GetResponse;

GetRequest request = new GetRequest("products", "p001");
GetResponse resp = client.get(request, RequestOptions.DEFAULT);

    Product product = null;
if (resp.isExists()) {
    Map<String, Object> src = resp.getSource();
    product = om.convertValue(src, Product.class); // Jackson 手动转换
}`,
    differences: [
      'New Client 的 GetResponse<Product> 直接反序列化为强类型；RHLC 返回 Map<String, Object> 需 Jackson 手动转换',
      'New Client 用 Optional<Product> 表达可能不存在；RHLC 需自行判空',
      'New Client 的 found() 方法 vs RHLC 的 isExists() 语义相同'
    ]
  },
  {
    id: 'delete-doc',
    category: 'crud',
    title: '删除文档',
    tags: ['Delete'],
    desc: '删除文档可能由于不存在而返回 "not_found" result，需正确处理。',
    code: `import co.elastic.clients.elasticsearch.core.DeleteResponse;
import co.elastic.clients.elasticsearch.core.DeleteRequest;

DeleteResponse response = client.delete(DeleteRequest.of(d -> d
    .index("products")
    .id("p001")
));

String result = response.result().jsonValue();
// "deleted" 或 "not_found"
if ("deleted".equals(result)) {
    System.out.println("文档已删除");
}`,
    oldClient: `// RHLC：DeleteResponse.getResult()
import org.elasticsearch.action.delete.DeleteRequest;
import org.elasticsearch.action.delete.DeleteResponse;

DeleteRequest request = new DeleteRequest("products", "p001");
DeleteResponse resp = client.delete(request, RequestOptions.DEFAULT);
System.out.println("Result: " + resp.getResult());`,
    differences: [
      'New Client 用 result().jsonValue() 获取操作类型（deleted/not_found）；RHLC 用 getResult()',
      'New Client 的 DeleteRequest 用 Lambda DSL.of()；RHLC 用 new DeleteRequest(index, id)'
    ]
  },
  {
    id: 'update-doc',
    category: 'crud',
    title: '部分更新文档',
    tags: ['Update', 'partial'],
    desc: 'Update API 支持局部字段更新（合并而非替换），底层走 _update endpoint。',
    code: `import co.elastic.clients.elasticsearch.core.UpdateResponse;
import co.elastic.clients.elasticsearch.core.UpdateRequest;

Map<String, Object> partial = Map.of("price", 549.0);

UpdateResponse<Product> response = client.update(
    UpdateRequest.of(u -> u
        .index("products")
        .id("p001")
        .doc(partial)
    ),
    Product.class
);`,
    oldClient: `// RHLC：UpdateRequest.doc() 合并更新
import org.elasticsearch.action.update.UpdateRequest;
import org.elasticsearch.action.update.UpdateResponse;

UpdateRequest request = new UpdateRequest("products", "p001")
    .doc("price", 549.0, "stock", 100);
UpdateResponse resp = client.update(request, RequestOptions.DEFAULT);
System.out.println("Version: " + resp.getVersion());`,
    differences: [
      'New Client 用 Map.of() 或 Partial 对象更新；RHLC 用 .doc() 传 key-value 变参',
      'New Client 的 UpdateResponse<Product> 泛型直接反序列化结果；RHLC 返回 UpdateResponse 需 getVersion() 等',
      'New Client 的 UpdateRequest.of() Lambda 风格；RHLC 用 new UpdateRequest() + setter'
    ]
  },
  {
    id: 'search-match',
    category: 'search',
    title: 'Match 全文检索',
    tags: ['Match', 'Query DSL'],
    desc: '本项目 ElasticsearchService#searchProductsByName 的核心实现：使用 match 查询命中分词后的 token。',
    code: `import co.elastic.clients.elasticsearch.core.SearchResponse;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.elasticsearch.core.search.Hit;

SearchRequest request = SearchRequest.of(s -> s
    .index("products")
    .query(q -> q
        .match(m -> m
            .field("name")
            .query(nameQuery)
        )
    )
);

SearchResponse<Product> resp = client.search(request, Product.class);

List<Product> products = new ArrayList<>();
for (Hit<Product> hit : resp.hits().hits()) {
    if (hit.source() != null) {
        products.add(hit.source());
    }
}`,
    oldClient: `// RHLC：SearchRequest + SearchResponse
import org.elasticsearch.action.search.SearchRequest;
import org.elasticsearch.action.search.SearchResponse;
import org.elasticsearch.index.query.QueryBuilders;
import org.elasticsearch.search.builder.SearchSourceBuilder;

SearchSourceBuilder ssb = new SearchSourceBuilder();
ssb.query(QueryBuilders.matchQuery("name", nameQuery));

SearchRequest request = new SearchRequest("products").source(ssb);
SearchResponse resp = client.search(request, RequestOptions.DEFAULT);

List<Product> products = new ArrayList<>();
for (SearchHit hit : resp.getHits().getHits()) {
    products.add(om.convertValue(hit.getSourceAsMap(), Product.class));
}`
  },
  {
    id: 'search-bool',
    category: 'search',
    title: 'Bool Query 复合查询',
    tags: ['Bool', '复合'],
    desc: '生产最常用的查询形态：must 命中需求 + filter 强制过滤。',
    code: `SearchRequest request = SearchRequest.of(s -> s
    .index("products")
    .query(q -> q
        .bool(b -> b
            .must(m -> m.match(mm -> mm.field("name").query("机械键盘")))
            .filter(f -> f.term(t -> t.field("category").value("电脑外设")))
            .filter(f -> f.range(r -> r.field("price").lte(JsonData.of(1000))))
        )
    )
    .from(0)
    .size(20)
);`,
    oldClient: `// RHLC：BoolQueryBuilder + SearchSourceBuilder
import org.elasticsearch.index.query.QueryBuilders;
import org.elasticsearch.search.builder.SearchSourceBuilder;

SearchSourceBuilder ssb = new SearchSourceBuilder();
ssb.query(QueryBuilders.boolQuery()
    .must(QueryBuilders.matchQuery("name", "机械键盘"))
    .filter(QueryBuilders.termQuery("category", "电脑外设"))
    .filter(QueryBuilders.rangeQuery("price").lte(1000))
);
ssb.from(0).size(20);

SearchRequest request = new SearchRequest("products").source(ssb);`
  },
  {
    id: 'search-highlight',
    category: 'search',
    title: '高亮命中关键字',
    tags: ['Highlight', '前端'],
    desc: '通过 .highlight() 配置高亮字段，配合前端渲染。',
    code: `SearchRequest request = SearchRequest.of(s -> s
    .index("products")
    .query(q -> q.match(m -> m.field("name").query("键盘")))
    .highlight(h -> h
        .fields("name", f -> f
            .preTags("<em>")
            .postTags("</em>")
            .numberOfFragments(3)
        )
    )
);`,
    oldClient: `// RHLC：HighlightBuilder
import org.elasticsearch.search.builder.SearchSourceBuilder;
import org.elasticsearch.search.fetch.subphase.highlight.HighlightBuilder;

SearchSourceBuilder ssb = new SearchSourceBuilder();
ssb.query(QueryBuilders.matchQuery("name", "键盘"));
ssb.highlighter(new HighlightBuilder()
    .field(new HighlightBuilder.Field("name")
        .preTags("<em>").postTags("</em>")
        .numOfFragments(3)
    )
);

SearchRequest request = new SearchRequest("products").source(ssb);`
  },
  {
    id: 'search-pagination',
    category: 'search',
    title: '深度分页 search_after',
    tags: ['分页', 'search_after'],
    desc: '用上次结果末尾的 sort 值作为下次起点，无状态、性能稳定，可跳 10000+ 页。',
    code: `SearchRequest page1 = SearchRequest.of(s -> s
    .index("products")
    .query(q -> q.matchAll(m -> m))
    .sort(o -> o.field(f -> f.field("price").order(SortOrder.Asc)))
    .sort(o -> o.field(f -> f.field("_id").order(SortOrder.Asc)))
    .size(20)
);

SearchResponse<Product> resp1 = client.search(page1, Product.class);

// 取末尾 sort 值
List<FieldValue> lastSort = resp1.hits().hits()
    .get(resp1.hits().hits().size() - 1)
    .sort();

SearchRequest page2 = SearchRequest.of(s -> s
    .index("products")
    .query(q -> q.matchAll(m -> m))
    .sort(o -> o.field(f -> f.field("price").order(SortOrder.Asc)))
    .sort(o -> o.field(f -> f.field("_id").order(SortOrder.Asc)))
    .searchAfter(lastSort)
    .size(20)
);`,
    oldClient: `// RHLC：search_after 使用 Object[]
import org.elasticsearch.action.search.SearchRequest;
import org.elasticsearch.search.builder.SearchSourceBuilder;
import org.elasticsearch.search.sort.SortOrder;

SearchSourceBuilder ssb = new SearchSourceBuilder();
ssb.query(QueryBuilders.matchAllQuery());
ssb.sort("price", SortOrder.ASC).sort("_id", SortOrder.ASC);
ssb.size(20);

SearchRequest request = new SearchRequest("products").source(ssb);
SearchResponse resp = client.search(request, RequestOptions.DEFAULT);

// 排序值作为下一页起点
Object[] searchAfter = resp.getHits().getHits()
    [resp.getHits().getHits().length - 1].getSortValues();

ssb.searchAfter(searchAfter);
SearchRequest nextPage = new SearchRequest("products").source(ssb);`
  },
  {
    id: 'agg-java',
    category: 'agg',
    title: '聚合查询 (Terms + Metrics)',
    tags: ['聚合', 'Terms'],
    desc: 'size=0 让 ES 只返回聚合结果不返回 hits；docsWithAggregation 字段管理 buckets。',
    code: `SearchRequest request = SearchRequest.of(s -> s
    .index("products")
    .size(0)
    .aggregations("by_category", a -> a
        .terms(t -> t.field("category").size(10))
        .aggregations("avg_price", sub -> sub
            .avg(av -> av.field("price"))
        )
    )
);

SearchResponse<Void> resp = client.search(request, Void.class);

resp.aggregations()
    .get("by_category")
    .sterms()
    .buckets()
    .array()
    .forEach(bucket -> {
        System.out.println(bucket.key() + ": "
            + bucket.docCount() + " docs, avg="
            + bucket.aggregations().get("avg_price").avg().value());
    });`,
    oldClient: `// RHLC：AggregationBuilders + ParsedXxx 手动解析
import org.elasticsearch.search.aggregations.AggregationBuilders;
import org.elasticsearch.search.aggregations.bucket.terms.Terms;

SearchSourceBuilder ssb = new SearchSourceBuilder();
ssb.size(0);
ssb.aggregation(AggregationBuilders
    .terms("by_category").field("category").size(10)
    .subAggregation(AggregationBuilders.avg("avg_price").field("price"))
);

SearchResponse resp = client.search(
    new SearchRequest("products").source(ssb), RequestOptions.DEFAULT);

Terms byCat = resp.getAggregations().get("by_category");
for (Terms.Bucket bucket : byCat.getBuckets()) {
    double avg = ((ParsedAvg) bucket.getAggregations()
        .get("avg_price")).getValue();
    System.out.println(bucket.getKeyAsString() + ": "
        + bucket.getDocCount() + " docs, avg=" + avg);
}`
  },
  {
    id: 'agg-datehisto',
    category: 'agg',
    title: 'Date Histogram 时间桶',
    tags: ['聚合', '日期'],
    desc: '按时间窗口分桶，适合折线图、报表。',
    code: `SearchRequest request = SearchRequest.of(s -> s
    .index("orders")
    .size(0)
    .aggregations("daily_sales", a -> a
        .dateHistogram(d -> d
            .field("created_at")
            .calendarInterval(CalendarInterval.Day)
        )
        .aggregations("revenue", sub -> sub.sum(s -> s.field("amount")))
    )
);`,
    oldClient: `// RHLC：DateHistogramAggregationBuilder
import org.elasticsearch.search.aggregations.AggregationBuilders;
import org.elasticsearch.search.aggregations.bucket.histogram.DateHistogramInterval;

SearchSourceBuilder ssb = new SearchSourceBuilder();
ssb.size(0);
ssb.aggregation(AggregationBuilders
    .dateHistogram("daily_sales")
    .field("created_at")
    .calendarInterval(DateHistogramInterval.DAY)
    .subAggregation(AggregationBuilders.sum("revenue").field("amount"))
);`
  },
  {
    id: 'bulk-index',
    category: 'bulk',
    title: 'Bulk 批量操作',
    tags: ['Bulk', '性能'],
    desc: '批量索引/更新/删除性能远高于单条操作；推荐 5-15 MB / 1000-5000 doc / batch。',
    code: `BulkRequest.Builder br = new BulkRequest.Builder();

for (Product p : products) {
    br.operations(op -> op
        .index(idx -> idx
            .index("products")
            .id(p.getId())
            .document(p)
        )
    );
}

BulkResponse resp = client.bulk(br.build());

if (resp.errors()) {
    resp.items().forEach(item -> {
        if (item.error() != null) {
            System.out.println("失败: " + item.error().reason());
        }
    });
}`,
    oldClient: `// RHLC：BulkRequest 逐个 add
import org.elasticsearch.action.bulk.BulkRequest;
import org.elasticsearch.action.bulk.BulkResponse;
import org.elasticsearch.action.index.IndexRequest;
import org.elasticsearch.common.unit.TimeValue;

BulkRequest bulk = new BulkRequest();
for (Product p : products) {
    bulk.add(new IndexRequest("products")
        .id(p.getId())
        .source("name", p.getName(), "price", p.getPrice())
    );
}
bulk.timeout(TimeValue.timeValueMinutes(2));

BulkResponse resp = client.bulk(bulk, RequestOptions.DEFAULT);
if (resp.hasFailures()) {
    for (BulkItemResponse item : resp.getItems()) {
        if (item.isFailed()) {
            System.out.println("失败: " + item.getFailureMessage());
        }
    }
}`
  },
  {
    id: 'reindex',
    category: 'bulk',
    title: 'Reindex 重建索引',
    tags: ['Reindex', '迁移'],
    desc: 'Reindex API 用于跨索引复制数据，常用于修改 mapping / 升级 / 数据迁移。',
    code: `ReindexRequest req = ReindexRequest.of(r -> r
    .source(s -> s.index("products_v1"))
    .dest(d -> d.index("products_v2"))
    .script(sc -> sc
        .source("ctx._source.migrated_at = params.now")
        .params("now", JsonData.of("2026-07-13"))
    )
);

ReindexResponse resp = client.reindex(req);
System.out.println("已迁移: " + resp.total() + " doc");`,
    oldClient: `// RHLC：ReindexRequest 构建方式不同
import org.elasticsearch.index.reindex.ReindexRequest;
import org.elasticsearch.index.reindex.BulkByScrollResponse;
import org.elasticsearch.common.bytes.BytesReference;

ReindexRequest req = new ReindexRequest();
req.setSourceIndices("products_v1");
req.setDestIndex("products_v2");
req.setScript(new Script(
    ScriptType.INLINE, "painless",
    "ctx._source.migrated_at = params.now",
    Collections.singletonMap("now", new Date())
));

BulkByScrollResponse resp = client.reindex(req, RequestOptions.DEFAULT);
System.out.println("已迁移: " + resp.getTotal() + " doc");`
  },
  {
    id: 'index-template',
    category: 'advanced',
    title: '索引模板',
    tags: ['Template', 'Composed'],
    desc: 'Composable Index Template 是 7.8+ 的新模板范式，可组合多个 component template。',
    code: `client.indices().putIndexTemplate(t -> t
    .name("products-template")
    .indexPatterns("products-*")
    .priority(100L)
    .template(tt -> tt
        .settings(s -> s.numberOfShards("2").numberOfReplicas("1"))
        .mappings(m -> m
            .properties("name", p -> p.text(t -> t.analyzer("ik_max_word")))
            .properties("price", p -> p.double_(d -> d))
        )
    )
);

// 之后创建 products-2026-07-13 时会自动应用
client.indices().create(c -> c.index("products-2026-07-13"));`,
    oldClient: `// RHLC：PutIndexTemplateRequest（JSON 格式）
import org.elasticsearch.action.admin.indices.template.put.PutIndexTemplateRequest;

PutIndexTemplateRequest req = new PutIndexTemplateRequest("products-template");
req.patterns(List.of("products-*"));
req.settings(Settings.builder()
    .put("index.number_of_shards", 2)
    .put("index.number_of_replicas", 1)
    .build());
req.mapping("{\n" +
    "  \"properties\": {\n" +
    "    \"name\":  { \"type\": \"text\", \"analyzer\": \"ik_max_word\" },\n" +
    "    \"price\": { \"type\": \"double\" }\n" +
    "  }\n" +
    "}", XContentType.JSON);
client.indices().putTemplate(req, RequestOptions.DEFAULT);`
  },
  {
    id: 'script-query',
    category: 'advanced',
    title: 'Painless 脚本查询',
    tags: ['Script', 'Painless'],
    desc: '用 Painless 写自定义查询逻辑。注意用 doc[field] 而非 _source.field 提升性能。',
    code: `SearchRequest req = SearchRequest.of(s -> s
    .index("products")
    .query(q -> q
        .script(sc -> sc
            .script(scs -> scs
                .inline(i -> i
                    .source("doc['price'].value * doc['stock'].value > 10000")
                )
            )
        )
    )
);`,
    oldClient: `// RHLC：ScriptQueryBuilder
import org.elasticsearch.index.query.ScriptQueryBuilder;

SearchSourceBuilder ssb = new SearchSourceBuilder();
ssb.query(new ScriptQueryBuilder(new Script(
    ScriptType.INLINE, "painless",
    "doc['price'].value * doc['stock'].value > 10000",
    Collections.emptyMap()
)));

SearchRequest req = new SearchRequest("products").source(ssb);`
  },
  {
    id: 'refresh-for-tests',
    category: 'advanced',
    title: '强制 Refresh（测试场景）',
    tags: ['Refresh', 'Test'],
    desc: '本项目 ElasticsearchServiceTest 中用于解决准实时延迟的关键调用。仅测试环境使用。',
    code: `// 默认 Refresh 间隔 1s，测试中立刻让文档可搜
client.indices().refresh(r -> r.index("products"));

// 强制 Flush 持久化
client.indices().flush(f -> f.index("products"));`,
    oldClient: `// RHLC：RefreshRequest / FlushRequest
import org.elasticsearch.action.admin.indices.refresh.RefreshRequest;
import org.elasticsearch.action.admin.indices.flush.FlushRequest;
import org.elasticsearch.action.support.master.AcknowledgedResponse;

client.indices().refresh(new RefreshRequest("products"), RequestOptions.DEFAULT);
client.indices().flush(new FlushRequest("products"), RequestOptions.DEFAULT);`
  },
  {
    id: 'health',
    category: 'advanced',
    title: '集群健康检查',
    tags: ['Health', '监控'],
    desc: '生产监控最常用的接口，返回 green/yellow/red 状态。',
    code: `HealthResponse health = client.cluster().health(h -> h.index("products"));

System.out.println("Status: " + health.status());      // green/yellow/red
System.out.println("Nodes: " + health.numberOfNodes());
System.out.println("Active: " + health.activeShards());
System.out.println("Unassigned: " + health.unassignedShards());`,
    oldClient: `// RHLC：ClusterHealthRequest
import org.elasticsearch.action.admin.cluster.health.ClusterHealthRequest;
import org.elasticsearch.action.admin.cluster.health.ClusterHealthResponse;

ClusterHealthRequest req = new ClusterHealthRequest("products");
ClusterHealthResponse health = client.cluster().health(req, RequestOptions.DEFAULT);
System.out.println("Status: " + health.getStatus());
System.out.println("Nodes: " + health.getNumberOfNodes());`
  },
  // ====== 高级配置 ======
  {
    id: 'init-pool',
    category: 'init_adv',
    title: '连接池 + 超时配置',
    tags: ['生产', '性能'],
    desc: '配置连接池大小、连接超时、socket 超时。生产推荐。',
    code: `RestClient restClient = RestClient.builder(new HttpHost("localhost", 9200))
    .setRequestConfigCallback(rc -> rc
        .setConnectTimeout(5000)   // 连接超时 5s
        .setSocketTimeout(60000)   // socket 读写超时 60s
    )
    .setHttpClientConfigCallback(http -> http
        .setMaxConnTotal(100)       // 最大连接数
        .setMaxConnPerRoute(20)     // 每路由最大连接数
    )
    .build();`,
    oldClient: `// RHLC：setRequestConfigCallback / setHttpClientConfigCallback 方式完全一致
// 因为底层都是 RestClient.builder
RestHighLevelClient client = new RestHighLevelClient(
    RestClient.builder(new HttpHost("localhost", 9200))
        .setRequestConfigCallback(rc -> rc
            .setConnectTimeout(5000)
            .setSocketTimeout(60000)
        )
        .setHttpClientConfigCallback(http -> http
            .setMaxConnTotal(100)
            .setMaxConnPerRoute(20)
        )
);`
  },
  {
    id: 'init-sniff',
    category: 'init_adv',
    title: '节点嗅探 Sniffer',
    tags: ['集群发现', '高可用'],
    desc: '启用嗅探器自动发现集群节点（适合动态扩缩容场景）。注意：嗅探器会定期发请求增加负载。',
    code: `RestClient restClient = RestClient.builder(new HttpHost("localhost", 9200))
    .setHttpClientConfigCallback(http -> http
        .setDefaultCredentialsProvider(creds)
    )
    .build();

// 启用嗅探（默认 5 分钟一次）
ElasticsearchTransport transport = new RestClientTransport(
    restClient, new JacksonJsonpMapper()
);
RestClientHttpHost[] nodes = transport.restClient().getNodes();
// 注意：官方 Java Client 没有内置 Sniffer，需用底层 RestClient 的 NodesSniffer`,
    oldClient: `// RHLC 内置 Sniffer，自动发现集群节点
RestHighLevelClient client = new RestHighLevelClient(
    RestClient.builder(new HttpHost("localhost", 9200))
);

Sniffer sniffer = Sniffer.builder(client.getLowLevelClient()).build();

// 也可用 Sniffer 的 setSniffAfterFailureMode 开启失败后立即嗅探
Sniffer.builder(client.getLowLevelClient())
    .setSniffAfterFailureMode(true)
    .build();`
  },
  {
    id: 'init-custom-json',
    category: 'init_adv',
    title: '自定义 JSON Mapper',
    tags: ['Jackson', '序列化'],
    desc: '替换默认的 JacksonJsonpMapper（如自定义 ObjectMapper 配置日期格式、命名策略）。',
    code: `import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

ObjectMapper mapper = new ObjectMapper()
    .registerModule(new JavaTimeModule())
    .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);

JacksonJsonpMapper jsonpMapper = new JacksonJsonpMapper(mapper);

ElasticsearchTransport transport = new RestClientTransport(restClient, jsonpMapper);
ElasticsearchClient client = new ElasticsearchClient(transport);`,
    oldClient: `// RHLC 无内置 JSON Mapper，需自行处理序列化
import com.fasterxml.jackson.databind.ObjectMapper;
import org.elasticsearch.common.xcontent.XContentType;

ObjectMapper om = new ObjectMapper();

// 写入：直接传 Map，ES 自动序列化
IndexRequest request = new IndexRequest("products")
    .id("1")
    .source("name", "Wireless Mouse", "price", 29.99);

// 读取：getSource() 返回 Map，手动转 POJO
GetResponse getResp = client.get(
    new GetRequest("products", "1"), RequestOptions.DEFAULT);
Map<String, Object> src = getResp.getSource();
Product p = om.convertValue(src, Product.class);`
  },
  {
    id: 'ping',
    category: 'init_adv',
    title: 'Ping 健康探活',
    tags: ['健康', '监控'],
    desc: '简单的连通性检查（200 OK 即为正常）。比 cluster.health 更轻量。',
    code: `BooleanResponse resp = client.ping();
if (resp.value()) {
    System.out.println("ES 可达");
} else {
    System.out.println("ES 不可达");
}`,
    oldClient: `// RHLC：client.ping() 返回 boolean，BulkResponse 可一步判断
boolean isAlive = client.ping(RequestOptions.DEFAULT);
System.out.println("ES 可达: " + isAlive);`
  },
  {
    id: 'info',
    category: 'init_adv',
    title: '集群 Info',
    tags: ['Info', '版本'],
    desc: '获取 ES 集群基本信息（版本、Lucene 版本、集群名）。',
    code: `InfoResponse info = client.info();
System.out.println("ES 版本: " + info.version().number());
System.out.println("Lucene 版本: " + info.version().luceneVersion());
System.out.println("集群名: " + info.clusterName());`,
    oldClient: `// RHLC：MainResponse 返回信息
MainResponse info = client.info(RequestOptions.DEFAULT);
System.out.println("ES 版本: " + info.getVersion().toString());
System.out.println("集群名: " + info.getClusterName().valueString());`
  },
  // ====== 搜索进阶 ======
  {
    id: 'count-api',
    category: 'search_adv',
    title: 'Count API - 仅统计总数',
    tags: ['Count', '性能'],
    desc: '只返回满足条件的文档数，不返回文档内容（性能更好）。',
    code: `CountRequest req = CountRequest.of(c -> c
    .index("products")
    .query(q -> q.term(t -> t.field("category").value("电脑外设")))
);
CountResponse resp = client.count(req);
System.out.println("命中数: " + resp.count());`,
    oldClient: `// RHLC 7.x：SearchRequest 设置 size=0 实现 count
SearchSourceBuilder ssb = new SearchSourceBuilder();
ssb.query(QueryBuilders.termQuery("category", "电脑外设"));
ssb.size(0); // 不需要返回文档

SearchResponse resp = client.search(
    new SearchRequest("products").source(ssb), RequestOptions.DEFAULT);
System.out.println("命中数: " + resp.getHits().getTotalHits().value);`
  },
  {
    id: 'exists-api',
    category: 'search_adv',
    title: 'Exists API - 检查文档是否存在',
    tags: ['Exists', 'bool 替代'],
    desc: '检查某 id 的文档是否存在（比 GET 全文档更轻量）。',
    code: `BooleanResponse exists = client.exists(e -> e
    .index("products")
    .id("p001")
);
if (exists.value()) {
    System.out.println("文档存在");
}`,
    oldClient: `// RHLC：exists 方法接收 GetRequest
import org.elasticsearch.action.get.GetRequest;

GetRequest req = new GetRequest("products", "p001");
boolean exists = client.exists(req, RequestOptions.DEFAULT);
System.out.println("文档存在: " + exists);`
  },
  {
    id: 'multi-get',
    category: 'search_adv',
    title: 'Multi Get - 批量获取文档',
    tags: ['MGet', '批量'],
    desc: '一次请求获取多个文档（按 id 列表）。',
    code: `MGetResponse<Product> resp = client.mget(m -> m
    .index("products")
    .ids("p001", "p002", "p003")
    , Product.class);

resp.docs().forEach(doc -> {
    if (doc.found()) {
        System.out.println(doc.id() + ": " + doc.source());
    }
});`,
    oldClient: `// RHLC：MultiGetRequest 逐个 add Item
import org.elasticsearch.action.get.MultiGetRequest;
import org.elasticsearch.action.get.MultiGetResponse;
import org.elasticsearch.action.get.MultiGetItemResponse;

MultiGetRequest mgr = new MultiGetRequest();
mgr.add(new MultiGetRequest.Item("products", "p001"));
mgr.add(new MultiGetRequest.Item("products", "p002"));
mgr.add(new MultiGetRequest.Item("products", "p003"));

MultiGetResponse resp = client.mget(mgr, RequestOptions.DEFAULT);
for (MultiGetItemResponse item : resp.getResponses()) {
    if (!item.isFailed() && item.getResponse().isExists()) {
        System.out.println(item.getId() + ": "
            + item.getResponse().getSourceAsString());
    }
}`
  },
  {
    id: 'update-by-query',
    category: 'search_adv',
    title: 'Update By Query - 批量更新',
    tags: ['UBQ', '批量'],
    desc: '按 query 匹配批量更新文档（适合批量打标签、价格调整等）。',
    code: `UpdateByQueryResponse resp = client.updateByQuery(u -> u
    .index("products")
    .query(q -> q.term(t -> t.field("category").value("电脑外设")))
    .script(sc -> sc
        .source("ctx._source.price = ctx._source.price * 0.9")
        .lang("painless")
    )
);

System.out.println("更新数: " + resp.updated());
System.out.println("失败数: " + resp.failures().size());`,
    oldClient: `// RHLC：UpdateByQueryRequest + BulkByScrollResponse
import org.elasticsearch.index.reindex.UpdateByQueryRequest;
import org.elasticsearch.index.reindex.BulkByScrollResponse;

UpdateByQueryRequest ubq = new UpdateByQueryRequest("products");
ubq.setQuery(QueryBuilders.termQuery("category", "电脑外设"));
ubq.setScript(new Script(
    ScriptType.INLINE, "painless",
    "ctx._source.price = ctx._source.price * 0.9",
    Collections.emptyMap()
));

BulkByScrollResponse resp = client.updateByQuery(ubq, RequestOptions.DEFAULT);
System.out.println("更新数: " + resp.getUpdated());
System.out.println("失败数: " + resp.getBulkFailures().size());`
  },
  {
    id: 'delete-by-query',
    category: 'search_adv',
    title: 'Delete By Query - 批量删除',
    tags: ['DBQ', '批量'],
    desc: '按 query 匹配批量删除文档。',
    code: `DeleteByQueryResponse resp = client.deleteByQuery(d -> d
    .index("logs-*")
    .query(q -> q.range(r -> r.field("@timestamp").lt(JsonData.of("now-30d"))))
    .refresh(true)
);

System.out.println("删除数: " + resp.deleted());`,
    oldClient: `// RHLC：DeleteByQueryRequest
import org.elasticsearch.index.reindex.DeleteByQueryRequest;
import org.elasticsearch.index.reindex.BulkByScrollResponse;

DeleteByQueryRequest dbq = new DeleteByQueryRequest("logs-*");
dbq.setQuery(QueryBuilders.rangeQuery("@timestamp").lt("now-30d"));
dbq.setRefresh(true);

BulkByScrollResponse resp = client.deleteByQuery(dbq, RequestOptions.DEFAULT);
System.out.println("删除数: " + resp.getDeleted());`
  },
  {
    id: 'field-collapse-java',
    category: 'search_adv',
    title: 'Field Collapse - 按字段去重',
    tags: ['collapse', '分组'],
    desc: '按某字段去重，每个组只取一条（inner_hits 拿同组其他文档）。',
    code: `SearchRequest req = SearchRequest.of(s -> s
    .index("articles")
    .query(q -> q.match(m -> m.field("content").query("elasticsearch")))
    .collapse(c -> c
        .field("author_id")
        .innerHits(ih -> ih.size(1).name("latest"))
    )
);`,
    oldClient: `// RHLC：CollapseBuilder
import org.elasticsearch.search.collapse.CollapseBuilder;

SearchSourceBuilder ssb = new SearchSourceBuilder();
ssb.query(QueryBuilders.matchQuery("content", "elasticsearch"));
ssb.collapse(new CollapseBuilder("author_id")
    .setInnerHits(new InnerHitBuilder("latest").setSize(1))
);`
  },
  {
    id: 'multi-search-java',
    category: 'search_adv',
    title: 'Multi Search - 批量搜索',
    tags: ['MultiSearch', '性能'],
    desc: '一次请求执行多个独立搜索（减少网络往返）。',
    code: `MsearchResponse<Product> resp = client.msearch(MsearchRequest.of(m -> m
    .searches(
        s -> s.header(h -> h.index("products")).body(b -> b.query(q -> q.match(mq -> mq.field("name").query("键盘")))),
        s -> s.header(h -> h.index("orders")).body(b -> b.query(q -> q.match(mq -> mq.field("item").query("键盘"))))
    )
), Product.class);

resp.responses().forEach(r -> System.out.println("结果: " + r.result().hits().total().value()));`
  },
  // ====== 批量进阶 ======
  {
    id: 'scroll-api',
    category: 'bulk',
    title: 'Scroll API - 全量遍历（老 API）',
    tags: ['Scroll', '导出'],
    desc: '传统的全量遍历 API（推荐用 search_after + PIT 替代，但仍是某些场景的选项）。',
    code: `// 第一页：建立 scroll context
SearchResponse<Product> resp1 = client.search(s -> s
    .index("products")
    .query(q -> q.matchAll(m -> m))
    .size(1000)
    .scroll(t -> t.time("1m"))
    , Product.class);
String scrollId = resp1.scrollId();

// 后续页：传入 scrollId
SearchResponse<Product> resp2 = client.scroll(s -> s
    .scrollId(scrollId)
    .scroll(t -> t.time("1m"))
    , Product.class);

// 清理
client.clearScroll(c -> c.scrollId(scrollId));`
  },
  {
    id: 'pit-search-after',
    category: 'bulk',
    title: 'PIT + Search After - 现代深度分页',
    tags: ['PIT', '深度分页'],
    desc: '7.10+ 推荐：用 Point In Time 维持一致性快照 + search_after 无状态分页。',
    code: `// 创建 PIT
OpenPointInTimeResponse pit = client.openPointInTime(o -> o
    .index("products")
    .keepAlive(t -> t.time("2m"))
);
String pitId = pit.id();

// 第一页（用 pit 替代 index）
SearchResponse<Product> page1 = client.search(s -> s
    .pit(p -> p.id(pitId).keepAlive(t -> t.time("2m")))
    .query(q -> q.matchAll(m -> m))
    .sort(o -> o.field(f -> f.field("created_at").order(SortOrder.Asc)))
    .sort(o -> o.field(f -> f.field("_id").order(SortOrder.Asc)))
    .size(100)
    , Product.class);

// 取末尾 sort 值
List<FieldValue> lastSort = page1.hits().hits()
    .get(page1.hits().hits().size() - 1).sort();

// 第二页
SearchResponse<Product> page2 = client.search(s -> s
    .pit(p -> p.id(pitId).keepAlive(t -> t.time("2m")))
    .searchAfter(lastSort)
    .sort(o -> o.field(f -> f.field("created_at").order(SortOrder.Asc)))
    .sort(o -> o.field(f -> f.field("_id").order(SortOrder.Asc)))
    .size(100)
    , Product.class);

// 关闭 PIT
client.closePointInTime(c -> c.id(pitId));`
  },
  // ====== Ingest Pipeline ======
  {
    id: 'pipeline-create',
    category: 'ingest',
    title: '创建 Ingest Pipeline',
    tags: ['Ingest', 'ETL'],
    desc: '定义 ETL 管道：解析、转换、丰富数据。常用于日志解析、字段标准化。',
    code: `client.ingest().putPipeline(p -> p
    .id("logs-pipeline")
    .description("解析 Nginx 访问日志")
    .processors(pr -> pr
        .grok(g -> g
            .field("message")
            .patterns(List.of("%{NGINX_ACCESS}"))
        )
        .date(d -> d
            .field("timestamp")
            .formats(List.of("yyyy-MM-dd HH:mm:ss"))
        )
        .remove(r -> r.field("message"))
    )
);`,
    oldClient: `// RHLC：PutPipelineRequest + XContent
import org.elasticsearch.action.ingest.PutPipelineRequest;
import org.elasticsearch.common.bytes.BytesArray;
import org.elasticsearch.common.xcontent.XContentType;

String pipelineJson = "{\n" +
    "  \"description\": \"解析 Nginx 访问日志\",\n" +
    "  \"processors\": [\n" +
    "    { \"grok\": { \"field\": \"message\", \"patterns\": [\"%{NGINX_ACCESS}\"] } },\n" +
    "    { \"date\": { \"field\": \"timestamp\", \"formats\": [\"yyyy-MM-dd HH:mm:ss\"] } },\n" +
    "    { \"remove\": { \"field\": \"message\" } }\n" +
    "  ]\n" +
    "}";
PutPipelineRequest req = new PutPipelineRequest(
    "logs-pipeline", new BytesArray(pipelineJson), XContentType.JSON);
client.ingest().putPipeline(req, RequestOptions.DEFAULT);`
  },
  {
    id: 'pipeline-simulate',
    category: 'ingest',
    title: '测试 Pipeline',
    tags: ['Ingest', '测试'],
    desc: '用 Simulate API 测试 pipeline 行为（不写索引，仅返回处理后文档）。',
    code: `SimulateResponse resp = client.ingest().simulate(s -> s
    .id("logs-pipeline")
    .docs(d -> d
        .source(Map.of("message", "127.0.0.1 - - [10/Oct/2024:13:55:36 +0000] GET /index.html"))
    )
);

resp.docs().get(0).doc().source().toString();  // 处理后的文档`
  },
  {
    id: 'pipeline-use',
    category: 'ingest',
    title: '写入时使用 Pipeline',
    tags: ['Ingest', '写入'],
    desc: '索引文档时指定 pipeline 处理。',
    code: `IndexRequest<Map<String, Object>> req = IndexRequest.of(i -> i
    .index("logs")
    .id("1")
    .document(Map.of("message", "raw nginx log line..."))
    .pipeline("logs-pipeline")
);
IndexResponse resp = client.index(req);`
  },
  // ====== 索引管理 ======
  {
    id: 'update-settings',
    category: 'index_mgmt',
    title: '动态更新索引 Settings',
    tags: ['Settings', '动态更新'],
    desc: '运行时修改索引设置（refresh_interval、number_of_replicas 等），无需重建。',
    code: `// 调整 refresh_interval（写入密集场景可调大到 30s）
client.indices().putSettings(p -> p
    .index("logs-*")
    .settings(s -> s.refreshInterval(t -> t.time("30s")))
);

// 调整副本数
client.indices().putSettings(p -> p
    .index("products")
    .settings(s -> s.numberOfReplicas("2"))
);`,
    oldClient: `// RHLC：UpdateSettingsRequest
import org.elasticsearch.action.admin.indices.settings.put.UpdateSettingsRequest;

UpdateSettingsRequest req = new UpdateSettingsRequest("logs-*");
req.settings(Map.of("index.refresh_interval", "30s"));
client.indices().putSettings(req, RequestOptions.DEFAULT);

UpdateSettingsRequest req2 = new UpdateSettingsRequest("products");
req2.settings(Map.of("index.number_of_replicas", "2"));
client.indices().putSettings(req2, RequestOptions.DEFAULT);`
  },
  {
    id: 'put-mapping',
    category: 'index_mgmt',
    title: '动态添加 Mapping 字段',
    tags: ['Mapping', '动态'],
    desc: '为已有索引动态添加字段（只能加新字段，不能改已有字段类型）。',
    code: `client.indices().putMapping(p -> p
    .index("products")
    .properties("brand", prop -> prop.keyword(k -> k))
    .properties("rating", prop -> prop.float_(f -> f))
);`,
    oldClient: `// RHLC：PutMappingRequest（JSON 格式）
import org.elasticsearch.action.admin.indices.mapping.put.PutMappingRequest;
import org.elasticsearch.common.xcontent.XContentType;

PutMappingRequest req = new PutMappingRequest("products");
req.source("{\n" +
    "  \"properties\": {\n" +
    "    \"brand\":  { \"type\": \"keyword\" },\n" +
    "    \"rating\": { \"type\": \"float\" }\n" +
    "  }\n" +
    "}", XContentType.JSON);
client.indices().putMapping(req, RequestOptions.DEFAULT);`
  },
  {
    id: 'get-mapping',
    category: 'index_mgmt',
    title: '获取索引 Mapping',
    tags: ['Mapping', '查询'],
    desc: '读取已有索引的字段映射。',
    code: `GetMappingResponse resp = client.indices().getMapping(g -> g.index("products"));
resp.result().get("products").mappings().properties().forEach((name, mapping) -> {
    System.out.println(name + ": " + mapping);
});`
  },
  {
    id: 'delete-index',
    category: 'index_mgmt',
    title: '删除索引',
    tags: ['CRUD', '慎用'],
    desc: '删除整个索引（数据不可恢复，谨慎使用）。',
    code: `DeleteIndexResponse resp = client.indices().delete(d -> d.index("products"));
if (resp.acknowledged()) {
    System.out.println("索引已删除");
}`,
    oldClient: `// RHLC：DeleteIndexRequest
import org.elasticsearch.action.admin.indices.delete.DeleteIndexRequest;

DeleteIndexRequest req = new DeleteIndexRequest("products");
org.elasticsearch.action.support.master.AcknowledgedResponse resp =
    client.indices().delete(req, RequestOptions.DEFAULT);
System.out.println("已删除: " + resp.isAcknowledged());`
  },
  {
    id: 'close-open',
    category: 'index_mgmt',
    title: 'Close / Open 索引',
    tags: ['Cluster Block', '节省资源'],
    desc: '关闭索引后不可读写但仍占元数据。重新打开恢复。常用于历史索引冻结。',
    code: `// 关闭
client.indices().close(c -> c.index("products-2020"));
// 打开
client.indices().open(o -> o.index("products-2020"));`,
    oldClient: `// RHLC：CloseIndexRequest / OpenIndexRequest
import org.elasticsearch.action.admin.indices.close.CloseIndexRequest;
import org.elasticsearch.action.admin.indices.open.OpenIndexRequest;

client.indices().close(new CloseIndexRequest("products-2020"), RequestOptions.DEFAULT);
client.indices().open(new OpenIndexRequest("products-2020"), RequestOptions.DEFAULT);`
  },
  {
    id: 'shrink-index',
    category: 'index_mgmt',
    title: 'Shrink 收缩分片数',
    tags: ['Shrink', '运维'],
    desc: '将索引分片数缩小（如 6 → 1）。要求目标分片数是源分片数的因数。',
    code: `// 1. 标记不可写
client.indices().putSettings(p -> p.index("products").settings(s -> s.blocksWrite(true)));
// 2. Shrink
client.indices().shrink(sh -> sh.index("products").target("products-small"));
// 3. 恢复可写
client.indices().putSettings(p -> p.index("products-small").settings(s -> s.blocksWrite(false)));`
  },
  {
    id: 'force-merge',
    category: 'index_mgmt',
    title: 'Force Merge - 强制段合并',
    tags: ['Merge', '存储优化'],
    desc: '把多个 segment 合并为 1 个（节省存储、提升查询速度，但写入代价高）。生产建议低峰期执行。',
    code: `client.indices().forcemerge(f -> f
    .index("products")
    .maxNumSegments(1)
);`
  },
  // ====== Snapshot 管理 ======
  {
    id: 'snapshot-repo',
    category: 'snapshot',
    title: '注册 Snapshot Repository',
    tags: ['Snapshot', 'Repository'],
    desc: '注册一个存储快照的仓库（共享文件系统 / S3 / GCS）。',
    code: `client.snapshot().createRepository(c -> c
    .name("my-backup-repo")
    .type("fs")
    .settings(s -> s
        .location("/mnt/es-backup")
        .compress(true)
    )
);`,
    oldClient: `// RHLC：PutRepositoryRequest + XContent
import org.elasticsearch.action.admin.cluster.repositories.put.PutRepositoryRequest;
import org.elasticsearch.common.settings.Settings;

PutRepositoryRequest req = new PutRepositoryRequest("my-backup-repo");
req.type("fs");
req.settings(Settings.builder()
    .put("location", "/mnt/es-backup")
    .put("compress", true)
    .build());
client.snapshot().createRepository(req, RequestOptions.DEFAULT);`
  },
  {
    id: 'snapshot-create',
    category: 'snapshot',
    title: '创建快照',
    tags: ['Snapshot', '备份'],
    desc: '为指定索引创建快照。',
    code: `client.snapshot().create(c -> c
    .repository("my-backup-repo")
    .snapshot("snapshot-2026-07-13")
    .indices("products,orders")
    .ignoreUnavailable(true)
    .includeGlobalState(false)
    .waitForCompletion(true)
);`,
    oldClient: `// RHLC：CreateSnapshotRequest
import org.elasticsearch.action.admin.cluster.snapshots.create.CreateSnapshotRequest;

CreateSnapshotRequest req = new CreateSnapshotRequest("my-backup-repo", "snapshot-2026-07-13");
req.indices("products", "orders");
req.ignoreUnavailable(true);
req.includeGlobalState(false);
req.waitForCompletion(true);
client.snapshot().create(req, RequestOptions.DEFAULT);`
  },
  {
    id: 'snapshot-restore',
    category: 'snapshot',
    title: '从快照恢复',
    tags: ['Snapshot', '恢复'],
    desc: '从快照恢复数据。索引冲突时需重命名或 close 后再恢复。',
    code: `client.snapshot().restore(r -> r
    .repository("my-backup-repo")
    .snapshot("snapshot-2026-07-13")
    .indices("products")
    .renamePattern("products(.+)")
    .renameReplacement("restored_products$1")
    .waitForCompletion(true)
);`
  },
  {
    id: 'snapshot-list',
    category: 'snapshot',
    title: '列出与管理快照',
    tags: ['Snapshot', '管理'],
    desc: '列出、查看、删除快照。',
    code: `// 列出所有快照
GetSnapshotResponse list = client.snapshot().get(g -> g
    .repository("my-backup-repo")
);
list.snapshots().forEach(s -> System.out.println(s.snapshot() + " at " + s.startTime()));

// 删除旧快照
client.snapshot().delete(d -> d
    .repository("my-backup-repo")
    .snapshot("snapshot-old")
);`
  },
  // ====== 别名管理 ======
  {
    id: 'alias-add',
    category: 'alias',
    title: '为索引添加别名',
    tags: ['Alias', '零停机切换'],
    desc: '为物理索引添加逻辑别名（多索引共享同一别名）。',
    code: `client.indices().updateAliases(u -> u
    .actions(a -> a.add(add -> add
        .index("products")
        .alias("products-read")
    ))
);`,
    oldClient: `// RHLC：IndicesAliasesRequest
import org.elasticsearch.action.admin.indices.alias.IndicesAliasesRequest;

IndicesAliasesRequest req = new IndicesAliasesRequest();
req.addAliasAction(IndicesAliasesRequest.AliasActions.add()
    .index("products").alias("products-read"));
client.indices().updateAliases(req, RequestOptions.DEFAULT);`
  },
  {
    id: 'alias-atomic-switch',
    category: 'alias',
    title: '别名原子切换（零停机重建索引）',
    tags: ['零停机', 'Alias Switch'],
    desc: 'reindex 到新索引后，原子地从旧索引移除别名并加到新索引（应用层无感知）。',
    code: `// 1. 原子切换别名
client.indices().updateAliases(u -> u
    .actions(a -> a
        .remove(remove -> remove.index("products-v1").alias("products"))
        .add(add -> add.index("products-v2").alias("products"))
    )
);`,
    oldClient: `// RHLC：remove + add 在同一个请求中原子执行
IndicesAliasesRequest req = new IndicesAliasesRequest();
req.addAliasAction(IndicesAliasesRequest.AliasActions.remove()
    .index("products-v1").alias("products"));
req.addAliasAction(IndicesAliasesRequest.AliasActions.add()
    .index("products-v2").alias("products"));
client.indices().updateAliases(req, RequestOptions.DEFAULT);`
  },
  {
    id: 'alias-write-index',
    category: 'alias',
    title: '写入别名（ILM 场景）',
    tags: ['Alias', 'ILM'],
    desc: '为别名指定 write_index，配合 rollover 实现"写入指向最新索引"。',
    code: `client.indices().updateAliases(u -> u
    .actions(a -> a
        .add(add -> add
            .index("products-000001")
            .alias("products")
            .isWriteIndex(true)   // 写入只到这里
        )
    )
);`
  },
  {
    id: 'alias-get',
    category: 'alias',
    title: '查询别名映射',
    tags: ['Alias', '查询'],
    desc: '查询哪些索引包含某个别名，或查询某索引的所有别名。',
    code: `// 哪些索引包含别名 products
GetAliasResponse resp = client.indices().getAlias(g -> g.name("products"));
resp.result().forEach((index, alias) -> {
    System.out.println(index + " -> " + alias.aliases().keySet());
});`
  },
  // ====== 高级特性扩展 ======
  {
    id: 'async-listener',
    category: 'advanced',
    title: '异步调用 + Listener',
    tags: ['Async', 'Listener'],
    desc: '异步发送请求并通过 Listener 回调处理结果（不阻塞主线程）。',
    code: `// 异步搜索
Cancellable cancellable = client.search(s -> s
    .index("products")
    .query(q -> q.matchAll(m -> m))
    , Product.class);

cancellable.whenComplete((response, exception) -> {
    if (exception != null) {
        System.err.println("错误: " + exception.getMessage());
    } else {
        System.out.println("命中: " + response.hits().total().value());
    }
});

// 取消请求（如果还没完成）
cancellable.cancel();`
  },
  {
    id: 'cat-indices-java',
    category: 'advanced',
    title: 'Cat Indices API',
    tags: ['Cat', '运维'],
    desc: '以人类可读形式列出所有索引（大小/文档/分片/健康状态）。',
    code: `// 获取索引统计
IndicesStatsResponse stats = client.indices().stats(s -> s.index("products,*logs-*"));
stats.indices().forEach((name, idx) -> {
    System.out.printf("%s: %d docs, %s store%n",
        name,
        idx.total().docs().count(),
        idx.total().store().size());
});`
  },
  {
    id: 'tasks-list',
    category: 'advanced',
    title: '查询运行中 Task',
    tags: ['Tasks', '监控'],
    desc: '查询当前集群运行中的 task（如 reindex 进度），支持取消长时间运行 task。',
    code: `ListTasksResponse tasks = client.tasks().list(l -> l
    .actions("reindex,update_by_query,delete_by_query")
);

tasks.nodes().forEach((nodeId, node) -> {
    node.tasks().forEach((taskId, task) -> {
        System.out.printf("Task %s: %s running for %s%n",
            taskId, task.action(), task.runningTime());
    });
});`
}
]

const activeSubTab = ref('init')
const copiedId = ref('')
const showAlt = reactive({})

const currentCat = computed(() =>
  categories.find((c) => c.id === activeSubTab.value) || categories[0]
)

const filteredSnippets = computed(() =>
  snippets.filter((s) => s.category === activeSubTab.value)
)

async function copy(text, id) {
  try {
    await navigator.clipboard.writeText(text)
    copiedId.value = id
    setTimeout(() => (copiedId.value = ''), 1500)
  } catch (_) {
    alert('复制失败，请手动复制')
  }
}
</script>

<style scoped>
.es-java {
  margin: 16px 0;
}

.es-java__intro {
  margin-bottom: 16px;
  padding: 10px 12px;
  background: var(--vp-c-bg-mute);
  border-radius: 6px;
  font-size: 13px;
  color: var(--vp-c-text-2);
}

.es-java__maven {
  margin-bottom: 20px;
  padding: 12px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg);
}

.es-java__maven summary {
  cursor: pointer;
  font-weight: 600;
  color: var(--vp-c-text-1);
  padding: 4px 0;
  user-select: none;
  font-size: 14px;
}

.es-java__subtabs {
  display: flex;
  flex-wrap: nowrap;
  gap: 6px;
  margin-bottom: 16px;
  padding: 8px 0;
  border-bottom: 1px dashed var(--vp-c-divider);
  overflow-x: auto;
  scrollbar-width: thin;
  -webkit-overflow-scrolling: touch;
}
.es-java__subtabs::-webkit-scrollbar {
  height: 4px;
}
.es-java__subtabs::-webkit-scrollbar-thumb {
  background: var(--vp-c-divider);
  border-radius: 2px;
}

.es-java__subtab {
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

.es-java__subtab:hover {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-text-1);
}

.es-java__subtab--active {
  background: var(--vp-c-brand-1);
  color: white;
  border-color: var(--vp-c-brand-1);
  font-weight: 600;
}

.es-java__subtab-count {
  opacity: 0.75;
  font-weight: 400;
}

.es-java__cat-title {
  margin: 0 0 12px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--vp-c-divider);
  font-size: 15px;
  color: var(--vp-c-brand-1);
}

.es-java__item {
  padding: 12px;
  margin-bottom: 8px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg);
}

.es-java__item-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.es-java__item-head strong {
  font-size: 14px;
  color: var(--vp-c-text-1);
}

.es-java__tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.es-java__tag {
  display: inline-block;
  padding: 1px 6px;
  font-size: 10px;
  border-radius: 8px;
  background: var(--vp-c-bg-mute);
  color: var(--vp-c-text-2);
}

.es-java__desc {
  font-size: 13px;
  line-height: 1.5;
  color: var(--vp-c-text-2);
  margin: 4px 0 8px;
}

.es-java__pre {
  background: #0f172a;
  color: #e2e8f0;
  padding: 16px;
  margin: 0 0 8px;
  border-radius: 6px;
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  font-size: 13px;
  line-height: 1.5;
  overflow-x: auto;
  max-height: 600px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.es-java__pre--old {
  background: #1c1917;
  color: #d6d3d1;
  border-left: 3px solid #92400e;
}

.es-java__deps {
  margin: 4px 0 8px;
  padding: 6px 10px;
  background: var(--vp-c-bg-mute);
  border-radius: 4px;
  font-size: 12px;
  color: var(--vp-c-text-2);
}

.es-java__deps code {
  background: transparent;
  padding: 0;
  font-size: 12px;
  color: var(--vp-c-text-1);
}

.es-java__diffs {
  margin-top: 10px;
  padding: 10px 14px;
  border-left: 3px solid #f59e0b;
  background: #fef3c7;
  border-radius: 4px;
  font-size: 12px;
  color: #78350f;
}

.es-java__diffs-title {
  font-weight: 600;
  margin-bottom: 4px;
  color: #92400e;
}

.es-java__diffs ul {
  margin: 0;
  padding-left: 20px;
}

.es-java__diffs li {
  margin: 3px 0;
  line-height: 1.5;
}

.es-java__actions {
  display: flex;
  gap: 6px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.es-java__actions--footer {
  margin-top: 12px;
  border-top: 1px dashed var(--vp-c-divider);
  padding-top: 8px;
}

/* ---- 客户端切换标签 ---- */
.es-java__toggle {
  display: flex;
  align-items: center;
  gap: 4px;
  margin: 8px 0;
  padding: 4px;
  background: var(--vp-c-bg-mute);
  border-radius: 6px;
}

.es-java__toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  border: 1px solid transparent;
  border-radius: 4px;
  background: transparent;
  color: var(--vp-c-text-2);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}

.es-java__toggle-btn:hover {
  color: var(--vp-c-text-1);
}

.es-java__toggle-btn--active {
  background: var(--vp-c-bg);
  border-color: var(--vp-c-divider);
  color: var(--vp-c-text-1);
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.es-java__toggle-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.es-java__toggle-dot--new {
  background: #059669;
}

.es-java__toggle-dot--old {
  background: #d97706;
}

.es-java__toggle-group {
  margin-left: auto;
  font-size: 11px;
  color: var(--vp-c-text-2);
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  padding-right: 4px;
}

.es-java__btn {
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

.es-java__btn:hover {
  background: var(--vp-c-bg-mute);
  border-color: var(--vp-c-brand-1);
}

.es-java__btn--sm {
  padding: 4px 10px;
  font-size: 12px;
}

.es-java__btn--link {
  text-decoration: none;
}

.es-java__links {
  margin-top: 20px;
  padding: 12px;
  background: var(--vp-c-bg-mute);
  border-radius: 6px;
  font-size: 13px;
  color: var(--vp-c-text-2);
}

.es-java__links a {
  color: var(--vp-c-brand-1);
  margin: 0 4px;
}
</style>
