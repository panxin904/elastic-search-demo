// Spring Cloud Alibaba 知识图谱数据 - 20 节点 + 关系边
export interface GraphNode {
  id: string
  name: string
  category: string
  value: number
  link: string
}

export interface GraphLink {
  source: string
  target: string
}

export interface GraphData {
  nodes: GraphNode[]
  links: GraphLink[]
}

export const graphData: GraphData = {
  "nodes": [
    {
      "id": "boot-quickstart",
      "name": "Spring Boot 快速开始",
      "category": "springboot",
      "value": 10,
      "link": "/01-springboot/quickstart"
    },
    {
      "id": "boot-autoconfig",
      "name": "自动配置原理",
      "category": "springboot",
      "value": 9,
      "link": "/01-springboot/auto-config"
    },
    {
      "id": "boot-web",
      "name": "Web 开发",
      "category": "springboot",
      "value": 8,
      "link": "/01-springboot/web"
    },
    {
      "id": "boot-data",
      "name": "数据访问",
      "category": "springboot",
      "value": 8,
      "link": "/01-springboot/data"
    },
    {
      "id": "boot-tx",
      "name": "事务管理",
      "category": "springboot",
      "value": 9,
      "link": "/01-springboot/transaction"
    },
    {
      "id": "alibaba-intro",
      "name": "Spring Cloud Alibaba",
      "category": "cloud",
      "value": 8,
      "link": "/02-overview/intro"
    },
    {
      "id": "nacos-discovery",
      "name": "Nacos 服务发现",
      "category": "nacos",
      "value": 10,
      "link": "/02-overview/nacos-discovery"
    },
    {
      "id": "nacos-config",
      "name": "Nacos 配置中心",
      "category": "nacos",
      "value": 10,
      "link": "/02-overview/nacos-config"
    },
    {
      "id": "nacos-namespace",
      "name": "Nacos 命名空间",
      "category": "nacos",
      "value": 6,
      "link": "/02-overview/nacos-config"
    },
    {
      "id": "gateway-basic",
      "name": "Gateway 网关",
      "category": "gateway",
      "value": 9,
      "link": "/03-gateway/basic"
    },
    {
      "id": "gateway-route",
      "name": "路由与断言",
      "category": "gateway",
      "value": 9,
      "link": "/03-gateway/route"
    },
    {
      "id": "gateway-filter",
      "name": "过滤器",
      "category": "gateway",
      "value": 8,
      "link": "/03-gateway/filter"
    },
    {
      "id": "lb-basic",
      "name": "LoadBalancer 负载均衡",
      "category": "rpc",
      "value": 8,
      "link": "/04-loadbalancer/basic"
    },
    {
      "id": "lb-strategy",
      "name": "负载均衡策略",
      "category": "rpc",
      "value": 7,
      "link": "/04-loadbalancer/strategy"
    },
    {
      "id": "security-basic",
      "name": "Spring Security",
      "category": "security",
      "value": 8,
      "link": "/05-security/basic"
    },
    {
      "id": "security-oauth2",
      "name": "OAuth2 + JWT",
      "category": "security",
      "value": 10,
      "link": "/05-security/oauth2"
    },
    {
      "id": "security-authcenter",
      "name": "统一认证中心",
      "category": "security",
      "value": 9,
      "link": "/05-security/auth-center"
    },
    {
      "id": "sentinel-flow",
      "name": "Sentinel 流控",
      "category": "msg",
      "value": 7,
      "link": "/06-practice/comprehensive"
    },
    {
      "id": "seata-at",
      "name": "Seata 分布式事务",
      "category": "msg",
      "value": 8,
      "link": "/06-practice/comprehensive"
    }
  ],
  "links": [
    {
      "source": "boot-quickstart",
      "target": "boot-autoconfig"
    },
    {
      "source": "boot-autoconfig",
      "target": "boot-web"
    },
    {
      "source": "boot-web",
      "target": "boot-data"
    },
    {
      "source": "boot-data",
      "target": "boot-tx"
    },
    {
      "source": "boot-tx",
      "target": "alibaba-intro"
    },
    {
      "source": "alibaba-intro",
      "target": "nacos-discovery"
    },
    {
      "source": "alibaba-intro",
      "target": "nacos-config"
    },
    {
      "source": "nacos-discovery",
      "target": "nacos-namespace"
    },
    {
      "source": "alibaba-intro",
      "target": "gateway-basic"
    },
    {
      "source": "gateway-basic",
      "target": "gateway-route"
    },
    {
      "source": "gateway-route",
      "target": "gateway-filter"
    },
    {
      "source": "gateway-filter",
      "target": "lb-basic"
    },
    {
      "source": "lb-basic",
      "target": "lb-strategy"
    },
    {
      "source": "lb-basic",
      "target": "security-basic"
    },
    {
      "source": "security-basic",
      "target": "security-oauth2"
    },
    {
      "source": "security-oauth2",
      "target": "security-authcenter"
    },
    {
      "source": "gateway-basic",
      "target": "sentinel-flow"
    },
    {
      "source": "boot-tx",
      "target": "seata-at"
    }
  ]
}