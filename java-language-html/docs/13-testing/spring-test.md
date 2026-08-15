---
title: Spring Boot Test
---
# Spring Boot Test
- @SpringBootTest: full context, slow
- @WebMvcTest(UserController.class): slice test for controllers
- @DataJpaTest: slice test for JPA repositories
- TestContainers: real DB in Docker, @Container + @DynamicPropertySource
```java
@WebMvcTest(UserController.class)
class UserControllerTest {
  @Autowired MockMvc mvc;
  @MockBean UserService service;

  @Test void getUser() throws Exception {
    when(service.findById(1L)).thenReturn(new User("Alice"));
    mvc.perform(get("/users/1"))
       .andExpect(status().isOk())
       .andExpect(jsonPath("$.name").value("Alice"));
  }
}
```