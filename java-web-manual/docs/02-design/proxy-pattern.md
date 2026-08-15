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

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="proxy-pattern" :height="400" />
