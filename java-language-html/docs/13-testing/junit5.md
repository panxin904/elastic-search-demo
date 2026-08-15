---
title: JUnit5
---
# JUnit5
- @Test/@BeforeEach/@AfterEach/@BeforeAll (static)
- @ParameterizedTest + @CsvSource/@MethodSource
- assertThrows, assertTimeout, assertAll (group assertions)
- @Nested for hierarchical tests, @Tag for filtering
```java
@Test
void test() {
  assertEquals(4, 2 + 2);
  assertThrows(IllegalArgumentException.class, () -> new User(null));
}
@ParameterizedTest @CsvSource({"1,2,3", "-1,1,0"})
void testAdd(int a, int b, int expected) {
  assertEquals(expected, Calc.add(a, b));
}
```