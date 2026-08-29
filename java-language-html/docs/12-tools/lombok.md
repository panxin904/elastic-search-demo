---
title: Lombok / MapStruct
date: 2026-08-15  # date-auto-injected
---
# Lombok / MapStruct
- @Data = @Getter + @Setter + @ToString + @EqualsAndHashCode + @RequiredArgsConstructor
- @Builder: fluent builder pattern
- @Slf4j: private static final Logger log
- MapStruct: compile-time bean mapping, @Mapper @Mapping
```java
@Mapper(componentModel = "spring")
public interface UserMapper {
  UserDto toDto(User user);
  @Mapping(target = "id", ignore = true)
  User toEntity(UserDto dto);
}
```