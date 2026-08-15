---
title: Mockito
---
# Mockito
- @Mock create mock, @InjectMocks inject mocks into target
- when().thenReturn() stub, verify() check invocation
- ArgumentCaptor capture arguments, @Spy partial mock
```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
  @Mock UserRepository repo;
  @InjectMocks UserService service;

  @Test
  void findById() {
    when(repo.findById(1L)).thenReturn(Optional.of(new User("Alice")));
    var user = service.findById(1L);
    assertEquals("Alice", user.getName());
    verify(repo, times(1)).findById(1L);
  }
}
```