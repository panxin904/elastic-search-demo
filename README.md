# Elasticsearch 7 + JDK 17 + Testcontainers Demo 项目

本项目是一个基于 **Maven** 构建的 Elasticsearch 7 演示项目。项目使用 **JDK 17** 进行编译，通过官方最新的 **Elasticsearch Java Client** 客户端对 ES 进行操作，并使用 **Testcontainers** 库在集成测试中自动拉取和运行真实的 Elasticsearch Docker 容器。

---

## 🛠️ 技术栈
- **开发语言**：Java 17 (使用 OpenJDK 17)
- **构建工具**：Apache Maven 3.9+
- **搜索引擎**：Elasticsearch 7.17.10
- **测试框架**：JUnit 5 (Jupiter) & Testcontainers 1.19.8
- **日志框架**：SLF4J & Logback

---

## 📂 项目结构

```text
elastic-search-demo/
├── pom.xml                               # Maven 依赖配置
├── README.md                             # 项目说明文档
└── src
    ├── main
    │   ├── java
    │   │   └── com/example/esdemo
    │   │       ├── model
    │   │       │   └── Product.java      # 商品实体类（ES 文档映射）
    │   │       └── service
    │   │           └── ElasticsearchService.java # ES 常用操作封装服务
    │   └── resources
    │       └── logback.xml               # 日志配置文件
    └── test
        ├── java
        │   └── com/example/esdemo
        │       └── service
        │           └── ElasticsearchServiceTest.java # 集成测试类（包含 Testcontainers）
```

---

## 🔗 核心代码文件链接

- 📄 [pom.xml](file:///Users/a1111/work_space/elastic-search-demo/pom.xml)
- 📄 [Product.java](file:///Users/a1111/work_space/elastic-search-demo/src/main/java/com/example/esdemo/model/Product.java)
- 📄 [ElasticsearchService.java](file:///Users/a1111/work_space/elastic-search-demo/src/main/java/com/example/esdemo/service/ElasticsearchService.java)
- 📄 [ElasticsearchServiceTest.java](file:///Users/a1111/work_space/elastic-search-demo/src/test/java/com/example/esdemo/service/ElasticsearchServiceTest.java)
- 📄 [logback.xml](file:///Users/a1111/work_space/elastic-search-demo/src/main/resources/logback.xml)

---

## ⚙️ 环境依赖要求

1. **JDK 17**：建议配置环境变量指向本地 JDK 17 安装路径。
2. **Maven 3.9+**：用于构建和依赖管理。
3. **Docker Engine**：由于 Testcontainers 运行测试时需要动态启动容器，请确保本地 Docker 守护进程（如 Docker Desktop, Colima 等）已启动并正常工作。

---

## 🚀 快速开始

### 1. 编译项目
使用 JDK 17 编译源码和测试类：
```bash
JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home mvn clean test-compile
```

### 2. 运行集成测试
运行测试前请确保 Docker/Colima 已经启动。

由于 Colima 的虚拟机文件系统挂载限制，Testcontainers 的清理辅助容器 Ryuk 可能会遇到挂载 `docker.sock` 失败的问题。因此在 macOS + Colima 环境下运行时，**必须禁用 Ryuk 进程**。

请使用以下命令执行测试：
```bash
JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home TESTCONTAINERS_RYUK_DISABLED=true mvn test
```

---

## 💡 核心设计与实现说明

### Elasticsearch 客户端选择
本项目使用更现代、类型安全的官方 `co.elastic.clients:elasticsearch-java` 客户端，而不是已经废弃的 `RestHighLevelClient`。

### 测试即时搜索（Refresh）
由于 Elasticsearch 在索引文档后有准实时（Near Real-Time）的延迟，我们在测试类中写入文档后，显式调用了：
```java
client.indices().refresh(r -> r.index(INDEX_NAME));
```
以强制将内存中的缓存段写入磁盘，使得写入的数据能被接下来的搜索接口立即查询到，避免测试环境下的异步不稳定性。
