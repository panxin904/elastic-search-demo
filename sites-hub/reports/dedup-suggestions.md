# 跨子站重复标题治理建议

> 自动生成 by `sites-hub/scripts/dedup-suggest.py`（§8.66）
> 共 253 组重复，按主题分类：
> - 概念类（需跨站链接 / 合并）：18 组
> - 配置类（建议加白名单）：8 组
> - 章节类（建议加站前缀）：227 组

## 一、概念类重复（需治理）

> 同一概念在多站展开。建议：
> 1. **主版本**（通常是 architecture / system-design）保留完整内容
> 2. 其他站加跨站链接，指向主版本
> 3. 不必合并（多视角价值高）

| 标题 | 主题 | 重复数 | 涉及站 |
|------|------|------:|--------|
| 📚 跨站参考：📊 监控告警 | devops | 20 | kafka, mysql, video |
| 📊 监控告警 | devops | 4 | kafka, mysql, video |
| 📚 跨站参考：🧰 常用场景快速索引 | database | 3 | kafka, python, redis |
| 🧰 常用场景快速索引 | database | 3 | kafka, python, redis |
| CAP 定理 | architecture | 2 | architecture, system-design |
| JOIN 类型 | database | 2 | clickhouse, postgresql |
| Prometheus 告警规则 | devops | 2 | mysql, observability |
| Raft 共识算法 | architecture | 2 | architecture, system-design |
| Saga 分布式事务 | architecture | 2 | architecture, design-pattern |
| Sidecar 模式 | architecture | 2 | architecture, cloud-native |
| 事务隔离级别 | architecture | 2 | java, postgresql |
| 多级缓存架构 | architecture | 2 | architecture, system-design |
| 监控 mount | devops | 2 | filesystem, linux |
| 缓存一致性 | architecture | 2 | architecture, system-design |
| 聚合窗口函数 | database | 2 | clickhouse, postgresql |
| 🎯 为什么需要分布式事务？ | architecture | 2 | cloud, mysql |
| 📑 章节快速索引 | database | 2 | android, game |
| 🚨 告警规则 | devops | 2 | cloud-native, mysql |

## 二、配置类重复（建议加白名单）

> 配置示例标题（application.yml / docker-compose.yml / *.conf 等）。多站引用同一配置模板，预期重复。
> 建议加到 `audit-content.py` 的 `TEMPLATE_TITLES` 白名单。

```python
# sites-hub/scripts/audit-content.py · TEMPLATE_TITLES 新增：
        '/etc/default/grub',
        '/etc/sysctl.conf',
        '/etc/systemd/system/myapp.service',
        'alertmanager.yml',
        'application-dev.yml',
        'application-prod.yml',
        'application-test.yml',
        'dbt_project.yml',
```

## 三、章节类重复（建议加站前缀或白名单）

> 编号章节（如 "4. 验证"）或通用操作标题。建议加站前缀或加白名单。

共 227 个不同章节标题：

- `1. 业务场景`
- `1. 业务背景`
- `1. 准备数据`
- `1. 创建应用`
- `1. 安装`
- `1. 是什么`
- `1. 核心思想`
- `1. 连接`
- `1. 配置`
- `10. 一句话总结`
- `10. 参考资料`
- `10. 实战 checklist`
- `10. 实战建议`
- `10. 实战案例`
- `11. 参考资料`
- `11. 实战 checklist`
- `11. 实战案例`
- `12. 一句话总结`
- `12. 实战 checklist`
- `13. 参考资料`
- ... 等 207 个

## 四、建议处理优先级

1. **P1**：将"配置类重复"加入 `TEMPLATE_TITLES` 白名单（一次提交，影响几十个 dups）
2. **P2**：高频"概念类重复"（> 3 站）加跨站引用段落
3. **P3**：低频概念重复按站逐个处理
4. **P4**：章节类重复加白名单（如果确实是模板生成的）