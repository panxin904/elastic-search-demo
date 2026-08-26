---
title: 代理模式
---

# 代理模式

为其他对象提供代理，控制对原对象的访问。

## Java Web 中的应用

- **Spring AOP**：JDK 动态代理（接口代理）+ CGLIB（类代理）
- **MyBatis Mapper**：接口没有实现类，运行时生成代理对象
- **@Transactional**：生成代理，在方法前后开启/提交/回滚事务

## JDK 动态代理 vs CGLIB

| | JDK 动态代理 | CGLIB |
|---|---|---|
| 机制 | 基于接口 | 基于继承 |
| 要求 | 必须有接口 | final 类/方法不行 |
| 性能 | 反射调用 | 字节码，略快 |

## 🛠️ 何时用代理模式

**使用场景**：想在原方法前后**无侵入**加逻辑（AOP 切面），或**延迟加载**资源
（lazy proxy / hibernate lazy loading）。

**JDK 动态代理 vs CGLIB**：
- 有接口 → JDK 动态代理（无依赖）
- 无接口 → 必须 CGLIB（Spring 默认 fallback）

**Spring AOP**：默认 JDK 动态代理 + CGLIB 混合；配置 `spring.aop.proxy-target-class=true` 强制 CGLIB。

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="proxy-pattern" :height="400" />


<!-- auto-enrich:do-not-edit -->

## 实战示例

\`\`\`bash
# TODO: 在此补充本页主题的实战命令
echo "hello"
\`\`\`

\`\`\`yaml
# TODO: 配置示例
key: value
\`\`\`

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
