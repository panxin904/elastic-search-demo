---
title: JPA / Hibernate
---
# JPA / Hibernate
- Spring Data JPA: findByXxx, @Query, @Modifying for DML
- N+1 problem: LAZY loading + loop → 1 + N queries. Fix: @EntityGraph, @Query with JOIN FETCH
- Lock: @Lock(LockModeType.PESSIMISTIC_WRITE) for select-for-update
```java
@Entity @Table(name = "users")
public class User {
  @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;
  private String name;
  @OneToMany(mappedBy = "user", fetch = FetchType.LAZY)
  private List<Order> orders;
}
public interface UserRepo extends JpaRepository<User, Long> {
  @Query("SELECT u FROM User u JOIN FETCH u.orders WHERE u.id = :id")
  Optional<User> findByIdWithOrders(@Param("id") Long id);
}
```