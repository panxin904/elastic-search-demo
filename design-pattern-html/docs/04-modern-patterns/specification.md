---
title: Specification 规格模式
description: 查询条件可组合 + JPA Specification + Laravel Query Builder + 函数式 filter
---

# Specification 规格模式

## 核心问题

业务中需要多个动态查询条件组合（电商筛选、权限规则、复杂查询），用 SQL 拼接 / if-else 嵌套会导致：
1. 代码冗长（每个查询写一堆 if-else）
2. 难以复用（相同条件散落各处）
3. 难以测试（SQL 拼接难单元测试）
4. 业务方关心的是「条件」，不是 SQL

## 核心思想

把查询/筛选条件封装成 **first-class 对象**，可以自由组合（AND / OR / NOT）、复用、传递。

**Composite Specification**：多个条件用 boolean operator 组合

## TypeScript：函数式 Specification

```typescript
// Specification 接口
interface Specification<T> {
    isSatisfiedBy(entity: T): boolean;
    and(other: Specification<T>): Specification<T>;
    or(other: Specification<T>): Specification<T>;
    not(): Specification<T>;
}

// 实现
class UserSpec implements Specification<User> {
    constructor(private predicate: (u: User) => boolean) {}

    isSatisfiedBy(u: User) { return this.predicate(u); }

    and(other: Specification<User>) {
        return new UserSpec(u => this.isSatisfiedBy(u) && other.isSatisfiedBy(u));
    }

    or(other: Specification<User>) {
        return new UserSpec(u => this.isSatisfiedBy(u) || other.isSatisfiedBy(u));
    }

    not() {
        return new UserSpec(u => !this.isSatisfiedBy(u));
    }
}

// 静态工厂
class UserSpecs {
    static isActive() {
        return new UserSpec(u => u.status === 'active');
    }
    static isAdult() {
        return new UserSpec(u => u.age >= 18);
    }
    static isInCountry(country: string) {
        return return new UserSpec(u => u.country === country);
    }
}

// 用法：自由组合
const spec = UserSpecs.isActive()
    .and(UserSpecs.isAdult())
    .and(UserSpecs.isInCountry('CN'))
    .or(UserSpecs.isInCountry('US'));

const result = users.filter(spec.isSatisfiedBy.bind(spec));
```

## Go：函数式 Specification

```go
type UserSpec func(User) bool

func (s UserSpec) IsSatisfiedBy(u User) bool { return s(u) }
func (s UserSpec) And(other UserSpec) UserSpec {
    return func(u User) bool { return s(u) && other(u) }
}
func (s UserSpec) Or(other UserSpec) UserSpec {
    return func(u User) bool { return s(u) && other(u) }
}
func (s UserSpec) Not() UserSpec {
    return func(u User) bool { return !s(u) }
}

// 静态规格
var (
    IsActive = UserSpec(func(u User) bool { return u.Status == "active" })
    IsAdult  = UserSpec(func(u User) bool { return u.Age >= 18 })
)

// 组合
spec := IsActive.And(IsAdult)
filtered := lo.Filter(users, func(u User, _ int) bool { return spec(u) })
```

## JPA Specification

```java
// JPA 自带 Specification API
public class OrderSpecs {
    public static Specification<Order> hasUser(long userId) {
        return (root, q, cb) -> cb.equal(root.get("userId"), userId);
    }

    public static Specification<Order> createdAfter(LocalDateTime time) {
        return (root, q, cb) -> cb.greaterThan(root.get("createdAt"), time);
    }

    public static Specification<Order> totalGreaterThan(BigDecimal min) {
        return (root, q, cb) -> cb.greaterThan(root.get("total"), min);
    }

    public static Specification<Order> statusIn(OrderStatus... statuses) {
        return (root, q, cb) -> root.get("status").in(Arrays.asList(statuses));
    }
}

// Repository
public interface OrderRepository extends JpaRepository<Order, Long>, JpaSpecificationExecutor<Order> {
    // findAll(Specification) 已由 JpaSpecificationExecutor 提供
}

// Service
@Service
public class OrderService {
    @Autowired OrderRepository repo;

    public List<Order> search(OrderSearchCriteria criteria) {
        Specification<Order> spec = Specification.where(null);

        if (criteria.getUserId() != null) spec = spec.and(OrderSpecs.hasUser(criteria.getUserId()));
        if (criteria.getMinTotal() != null) spec = spec.and(OrderSpecs.totalGreaterThan(criteria.getMinTotal()));
        if (criteria.getStatuses() != null && !criteria.getStatuses().isEmpty())
            spec = spec.and(OrderSpecs.statusIn(criteria.getStatuses().toArray(new OrderStatus[0])));

        return repo.findAll(spec);
    }
}
```

## 实际查询生成的 SQL

```sql
SELECT * FROM orders
WHERE user_id = 123
  AND total > 100
  AND status IN ('PAID', 'SHIPPED')
  AND created_at > '2024-01-01'
ORDER BY created_at DESC
```

## 实战：电商筛选

```typescript
interface ProductFilters {
    category?: string;
    brand?: string[];
    minPrice?: number;
    maxPrice?: number;
    minRating?: number;
    inStock?: boolean;
    searchQuery?: string;
}

class ProductSpec implements Specification<Product> {
    constructor(private predicate: (p: Product) => boolean) {}

    isSatisfiedBy(p: Product) { return this.predicate(p); }
    and(other: Specification<Product>) { return new ProductSpec(p => this.isSatisfiedBy(p) && other.isSatisfiedBy(p)); }
    // ...
}

function buildProductSpec(filters: ProductFilters): Specification<Product> {
    let spec: Specification<Product> = new ProductSpec(() => true);

    if (filters.category) {
        spec = spec.and(new ProductSpec(p => p.category === filters.category));
    }
    if (filters.brand?.length) {
        spec = spec.and(new ProductSpec(p => filters.brand!.includes(p.brand)));
    }
    if (filters.minPrice !== undefined) {
        spec = spec.and(new ProductSpec(p => p.price >= filters.minPrice!));
    }
    if (filters.maxPrice !== undefined) {
        spec = spec.and(new ProductSpec(p => p.price <= filters.maxPrice!));
    }
    if (filters.minRating !== undefined) {
        spec = spec.and(new ProductSpec(p => p.rating >= filters.minRating!));
    }
    if (filters.inStock) {
        spec = spec.and(new ProductSpec(p => p.stock > 0));
    }
    if (filters.searchQuery) {
        const q = filters.searchQuery.toLowerCase();
        spec = spec.and(new ProductSpec(p =>
            p.name.toLowerCase().includes(q) || p.description.toLowerCase().includes(q)
        ));
    }

    return spec;
}

// 用法
const spec = buildProductSpec({
    category: 'electronics',
    brand: ['Apple', 'Samsung'],
    minPrice: 1000,
    maxPrice: 5000,
    minRating: 4.5,
    inStock: true,
});

const filtered = products.filter(spec.isSatisfiedBy.bind(spec));
```

## 适用边界

✅ **使用场景**：
- 多条件动态组合查询（电商筛选）
- 复杂权限规则（角色 + 资源 + 状态）
- 查询条件复用（多个 controller 共享）
- 业务规则抽象（Specification 可被业务逻辑调用）

❌ **避免场景**：
- 单一固定条件（直接传参）
- 业务方不需要组合（增加复杂度）
- 性能极敏感（Specification 多了一层包装）

🔄 **替代方案**：
- **Query Builder**：Laravel / Knex 等
- **DSL**：jOOQ / QueryDSL
- **简单 if-else**：单条件查询

💡 **最佳实践**：
- Specification 是无状态对象（可以被复用、缓存）
- 组合方法（and/or/not）返回新对象（不可变）
- JPA Specification 配合 JpaSpecificationExecutor
- TS/Go 用函数式 Specification 更简洁


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

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

- [java-language](https://java-px.bot.cd/java-language/):Java 设计模式
- [java](https://java-px.bot.cd/java-web-manual/):Java 实现
- [architecture](https://java-px.bot.cd/architecture/):架构模式
