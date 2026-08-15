<template>
  <div class="cs-container">
    <div class="cs-search">
      <input v-model="search" type="text" placeholder="🔍 搜索配置（输入关键字过滤）..." class="cs-input" />
      <select v-model="category" class="cs-select">
        <option value="all">全部</option>
        <option value="nacos">Nacos</option>
        <option value="gateway">Gateway</option>
        <option value="lb">负载均衡</option>
        <option value="security">安全/认证</option>
        <option value="rpc">RPC</option>
        <option value="msg">消息</option>
        <option value="sentinel">Sentinel</option>
        <option value="seata">Seata</option>
      </select>
    </div>

    <div v-for="(item, i) in filtered" :key="i" class="cs-item">
      <div class="cs-title">
        <span class="cs-tag" :data-cat="item.category">{{ categoryLabel(item.category) }}</span>
        {{ item.title }}
        <button class="cs-copy" @click="copy(item.yaml)">{{ copied === i ? '✓ 已复制' : '📋 复制' }}</button>
      </div>
      <div v-if="item.desc" class="cs-desc">{{ item.desc }}</div>
      <pre class="cs-code">{{ item.yaml }}</pre>
    </div>

    <div v-if="filtered.length === 0" class="cs-empty">
      <p>😅 没有匹配「{{ search }}」的配置</p>
      <p>试试搜索关键字：nacos、gateway、jwt、loadbalancer...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const search = ref('')
const category = ref('all')
const copied = ref(-1)

const items = [
  // Nacos
  { category: 'nacos', title: 'Nacos 服务注册（基础配置）', desc: 'Spring Cloud Alibaba 应用连接 Nacos Server 的最小配置', yaml: `# application.yml
spring:
  application:
    name: order-service
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848   # Nacos Server 地址
        namespace: public              # 命名空间（默认 public）
        group: DEFAULT_GROUP            # 分组

  # 必须加 web 依赖才能注册
  web:
    port: 8081` },
  { category: 'nacos', title: 'Nacos 服务发现（带元数据）', desc: '注册时附带版本、机房等元数据', yaml: `spring:
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
        metadata:
          version: 1.0.0
          zone: cn-east-1
          cluster: order-cluster` },
  { category: 'nacos', title: 'Nacos 配置中心（基础）', desc: '启用 Nacos 作为配置中心，支持动态刷新', yaml: `spring:
  cloud:
    nacos:
      config:
        server-addr: 127.0.0.1:8848
        file-extension: yaml        # 默认配置后缀
        refresh-enabled: true       # 开启自动刷新
        extension-configs:          # 扩展配置（可选）
          - dataId: redis.yaml
            group: DEFAULT_GROUP
            refresh: true` },
  { category: 'nacos', title: 'Nacos 命名空间隔离', desc: '通过 namespace 隔离 dev / test / prod 环境', yaml: `spring:
  cloud:
    nacos:
      discovery:
        namespace: dev               # 启动时传 -Dnacos.namespace=dev
      config:
        namespace: dev
        ext-config:
          - data-id: common.yaml
            group: COMMON_GROUP` },

  // Gateway
  { category: 'gateway', title: 'Gateway 基础路由（Path 路由）', desc: '把 /api/order/** 路由到 order-service', yaml: `spring:
  cloud:
    gateway:
      routes:
        - id: order_route
          uri: lb://order-service       # lb:// = 负载均衡
          predicates:
            - Path=/api/order/**         # 路径匹配
          filters:
            - StripPrefix=1            # 去掉 /api 前缀` },
  { category: 'gateway', title: 'Gateway 路由 + 限流', desc: '使用 Sentinel 在网关层限流', yaml: `spring:
  cloud:
    gateway:
      routes:
        - id: order_route
          uri: lb://order-service
          predicates:
            - Path=/api/order/**
          filters:
            - StripPrefix=1
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 100   # 每秒 100 个令牌
                redis-rate-limiter.burstCapacity: 200` },
  { category: 'gateway', title: 'Gateway 全局 CORS 配置', desc: '配置允许跨域请求', yaml: `spring:
  cloud:
    gateway:
      globalcors:
        cors-configurations:
          '[/**]':
            allowedOriginPatterns: "*"
            allowedMethods: "*"
            allowedHeaders: "*"
            allowCredentials: true
            maxAge: 3600` },
  { category: 'gateway', title: 'Gateway 自定义过滤器', desc: '鉴权过滤器（示例）', yaml: `# Java 代码
@Component
public class AuthFilter implements GlobalFilter {
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String token = exchange.getRequest().getHeaders().getFirst("Authorization");
        if (token == null || !token.startsWith("Bearer ")) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }
        return chain.filter(exchange);
    }
}` },

  // 负载均衡
  { category: 'lb', title: 'Spring Cloud LoadBalancer（替代 Ribbon）', desc: 'Spring Cloud 2020+ 默认的负载均衡器', yaml: `# application.yml（无需特殊配置，默认开启）
# 用 RestTemplate / WebClient 调用即可自动负载均衡
@LoadBalanced
@Bean
public RestTemplate restTemplate() {
    return new RestTemplate();
}

// 调用（自动负载均衡到 user-service 的某个实例）
restTemplate.getForObject("http://user-service/users/1", User.class);` },
  { category: 'lb', title: '自定义负载均衡策略', desc: '基于版本号 / 权重的路由', yaml: `# Java 代码
@Configuration
public class LoadBalancerConfig {
    
    @Bean
    public ReactorLoadBalancer<ServiceInstance> randomLoadBalancer(
        Environment environment, LoadBalancerClientFactory factory
    ) {
        String name = factory.getName(environment);
        return new RandomLoadBalancer(factory.getLazyProvider(name), name);
    }
}` },

  // Security
  { category: 'security', title: 'Spring Security + JWT 基础配置', desc: '无状态 JWT 认证（适合前后端分离）', yaml: `spring:
  security:
    user:
      name: admin
      password: \$2a\$10\$...  # BCrypt 加密` },
  { category: 'security', title: 'OAuth2 Resource Server（JWT 验证）', desc: '资源服务器只验证 token，不发 token', yaml: `spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: http://auth-center:9000
          jwk-set-uri: http://auth-center:9000/.well-known/jwks.json` },
  { category: 'security', title: 'Gateway + OAuth2 统一认证', desc: '在 Gateway 统一做 token 校验', yaml: `# Gateway 的 application.yml
spring:
  cloud:
    gateway:
      default-filters:
        - TokenRelay=
      routes:
        - id: api_route
          uri: lb://order-service
          predicates:
            - Path=/api/**` },

  // RPC / OpenFeign
  { category: 'rpc', title: 'OpenFeign 声明式调用', desc: '像调用本地方法一样调用远程服务', yaml: `# 1. 添加依赖
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-openfeign</artifactId>
</dependency>

# 2. 启用
@EnableFeignClients
@SpringBootApplication
public class OrderApplication {}

# 3. 定义 Feign 客户端
@FeignClient("user-service")
public interface UserClient {
    @GetMapping("/users/{id}")
    User getById(@PathVariable Long id);
}` },

  // Sentinel
  { category: 'sentinel', title: 'Sentinel 流量控制', desc: '流控、熔断、降级', yaml: `spring:
  cloud:
    sentinel:
      transport:
        dashboard: 127.0.0.1:8080   # Sentinel 控制台
      datasource:
        ds1:
          nacos:
            server-addr: 127.0.0.1:8848
            dataId: sentinel-flow-rules
            ruleType: flow` },
  { category: 'sentinel', title: 'Sentinel 熔断降级', desc: '配置熔断规则', yaml: `# @SentinelResource 注解
@SentinelResource(
    value = "getOrder",
    fallback = "fallbackMethod",
    blockHandler = "blockHandlerMethod"
)
public Order getOrder(Long id) {
    return orderService.getById(id);
}

// fallback 方法（参数要一致）
public Order fallbackMethod(Long id, Throwable e) {
    return Order.empty();
}` },

  // Seata
  { category: 'seata', title: 'Seata AT 模式（最常用）', desc: '分布式事务，零侵入', yaml: `# 1. 引入依赖
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-seata</artifactId>
</dependency>

# 2. application.yml
spring:
  cloud:
    alibaba:
      seata:
        tx-service-group: my_tx_group

# 3. 业务方法加注解
@GlobalTransactional(name = "create-order", rollbackFor = Exception.class)
public boolean createOrder(OrderDTO dto) {
    // 跨服务调用会自动加入全局事务
    return true;
}` },

  // 消息
  { category: 'msg', title: 'RocketMQ 集成', desc: '异步消息 + 事务消息保证最终一致', yaml: `spring:
  cloud:
    stream:
      rocketmq:
        binder:
          brokers: 127.0.0.1:9876
          secret-key: SecretKey
          access-key: AccessKey
        bindings:
          output:
            destination: order-topic
          input:
            destination: order-topic
            group: order-group` }
]

const filtered = computed(() => {
  return items.filter(item => {
    const matchCat = category.value === 'all' || item.category === category.value
    const matchSearch = !search.value ||
      item.title.toLowerCase().includes(search.value.toLowerCase()) ||
      item.yaml.toLowerCase().includes(search.value.toLowerCase()) ||
      (item.desc && item.desc.toLowerCase().includes(search.value.toLowerCase()))
    return matchCat && matchSearch
  })
})

function categoryLabel(c) {
  const map = { nacos: 'Nacos', gateway: 'Gateway', lb: 'LoadBalancer', security: 'Security', rpc: 'OpenFeign', msg: '消息', sentinel: 'Sentinel', seata: 'Seata' }
  return map[c] || c
}

function copy(yaml) {
  navigator.clipboard.writeText(yaml)
  copied.value = items.findIndex(i => i.yaml === yaml)
  setTimeout(() => copied.value = -1, 1500)
}
</script>

<style scoped>
.cs-empty p { margin: 4px 0; }
</style>