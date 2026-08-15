---
title: Repository 仓储模式
description: 封装数据访问 + Spring Data JPA / TypeORM / EF Core / Go sqlc + Repository vs DAO
---

# Repository 仓储模式

## 核心问题

业务层直接使用 JDBC / JPA / MongoDB driver，耦合数据库细节。导致：
1. 业务层充斥 SQL 拼接
2. 难以切换数据库（MySQL → PG）
3. 单测需要真实数据库
4. 业务逻辑分散在多个层

## 核心思想

把数据访问逻辑封装到独立的接口层（`Repository`），让业务层只依赖 Repository 接口，不依赖具体的数据库技术。

**关键点**：
- Repository 接口放在**领域层**（业务侧）
- Repository 实现在**基础设施层**（技术侧）
- 返回**领域对象**（不是 Entity / DTO）

## Java 实战

```java
// 领域层：定义接口
public interface OrderRepository {
    Optional<Order> findById(long id);
    List<Order> findByUser(long userId);
    void save(Order order);
    void delete(long id);
}

// 业务层：只依赖接口
@Service
public class OrderService {
    private final OrderRepository repo;

    public OrderService(OrderRepository repo) { this.repo = repo; }

    public Order getOrder(long id) {
        return repo.findById(id).orElseThrow(OrderNotFoundException::new);
    }

    @Transactional
    public Order create(OrderRequest req) {
        Order order = Order.create(req);
        repo.save(order);
        return order;
    }
}

// 基础设施层：JDBC 实现
@Repository
public class JdbcOrderRepository implements OrderRepository {
    @Autowired private JdbcTemplate jdbc;

    @Override
    public Optional<Order> findById(long id) {
        try {
            Order o = jdbc.queryForObject(
                "SELECT id, user_id, total, status FROM orders WHERE id = ?",
                (rs, rowNum) -> new Order(
                    rs.getLong("id"),
                    rs.getLong("user_id"),
                    rs.getBigDecimal("total"),
                    OrderStatus.valueOf(rs.getString("status"))
                ),
                id
            );
            return Optional.ofNullable(o);
        } catch (EmptyResultDataAccessException e) {
            return Optional.empty();
        }
    }

    @Override
    @Transactional
    public void save(Order order) {
        jdbc.update(
            "INSERT INTO orders(id, user_id, total, status) VALUES(?, ?, ?, ?)",
            order.getId(), order.getUserId(), order.getTotal(), order.getStatus().name()
        );
    }

    // ...
}

// 切换数据库：只需要新增 JpaOrderRepository，业务层零修改
```

## Spring Data JPA

```java
// Spring Data JPA：自动生成实现
public interface OrderRepository extends JpaRepository<Order, Long> {
    // 自动实现：findById / findAll / save / delete
    List<Order> findByUserId(long userId);

    @Query("SELECT o FROM Order o WHERE o.status = :status")
    List<Order> findByStatus(@Param("status") OrderStatus status);
}

// 用法
@Service
public class OrderService {
    private final OrderRepository repo;

    public OrderService(OrderRepository repo) { this.repo = repo; }

    public List<Order> getPaidOrders() {
        return repo.findByStatus(OrderStatus.PAID);
    }
}
```

Spring Data JPA 在运行时通过 JDK 动态代理自动生成 Repository 实现，业务方完全不用写 SQL。

## TypeScript：TypeORM / Prisma

```typescript
// TypeORM
@EntityRepository(Order)
class OrderRepository {
    async findById(id: number): Promise<Order | null> {
        return this.findOne({ where: { id } });
    }

    async findByUser(userId: number): Promise<Order[]> {
        return this.find({ where: { userId } });
    }

    async save(order: Order): Promise<Order> {
        return this.manager.save(order);
    }
}

// Prisma（schema-first）
const user = await prisma.user.findUnique({
    where: { id: 1 },
    include: { orders: true },
});
```

## Go sqlc（编译期生成）

```sql
-- queries.sql
-- name: GetOrder :one
SELECT * FROM orders WHERE id = $1 LIMIT 1;

-- name: ListOrdersByUser :many
SELECT * FROM orders WHERE user_id = $1 ORDER BY created_at DESC;
```

```bash
# sqlc 生成 Go 代码
sqlc generate
```

```go
// 自动生成的 repository.go
type OrderRepository struct {
    db *sql.DB
    q  *Queries
}

func (r *OrderRepository) GetOrder(ctx context.Context, id int64) (Order, error) {
    return r.q.GetOrder(ctx, id)
}
```

sqlc 是编译期生成的 Type-safe SQL 客户端，比 ORM 更快更明确。

## Repository vs DAO

| | Repository | DAO |
|---|---|---|
| 抽象层级 | 聚合根为单位 | 表为单位 |
| 方法命名 | `findByUser` 业务语义 | `selectByUserId` SQL 语义 |
| 返回值 | 领域对象 | Entity / DTO |
| 业务封装 | 含业务校验 / 不变量 | 仅数据访问 |
| 适用 | DDD / 复杂业务 | 简单 CRUD |

## 与 Specification 配合

```java
public interface OrderRepository {
    List<Order> findBySpecification(Specification<Order> spec);
}

// 用法：组合多个条件
Specification<Order> spec = OrderSpecs.hasUser(123)
    .and(OrderSpecs.createdAfter(lastWeek))
    .and(OrderSpecs.totalGreaterThan(minTotal));

List<Order> orders = repo.findBySpecification(spec);
```

## 适用边界

✅ **使用场景**：
- 业务层要访问数据库（所有业务系统）
- 业务对象持久化逻辑复杂（DDD）
- 多数据源（写 MySQL + 读 Redis / ES）

❌ **避免场景**：
- 业务极简（直接用 ORM）
- 一个方法调用就完成（过度抽象）
- 性能敏感（Repository 抽象有开销）

🔄 **演进路径**：
- 直接 ORM → Repository 接口（解耦）
- Repository + Specification（条件组合）
- Repository + CQRS（读写分离）

💡 **最佳实践**：
- Repository 接口放在领域层
- 实现放在基础设施层
- 每个聚合根一个 Repository
- 返回值用领域对象（不是 Entity）
- 业务校验在 Repository 内（不变量保护）
