---
title: pytest 测试
---

# 🧪 pytest 测试

> **pytest** 是 Python **最流行的测试框架**。简单、强大、可扩展，是几乎所有 Python 项目的首选。

## 🎯 为什么选 pytest？

```
✅ 简单（assert 即可）
✅ 强大（fixture、参数化、mock）
✅ 丰富插件（pytest-cov、pytest-xdist 等）
✅ 详细报告
✅ 并行执行

对比：
  - unittest：标准库，但 API 复杂
  - pytest：推荐（90% Python 项目使用）
```

## 🚀 快速开始

### 安装

```bash
pip install pytest
pip install pytest-cov          # 覆盖率
pip install pytest-mock         # mock
pip install pytest-xdist        # 并行
pip install pytest-asyncio      # 异步
```

### 第一个测试

```python
# test_sample.py
def add(a, b):
    return a + b

def test_add():
    assert add(1, 2) == 3
    assert add(0, 0) == 0
    assert add(-1, 1) == 0

def test_add_negative():
    assert add(-1, -1) == -2
```

```bash
pytest test_sample.py
# ============================= test session starts ==============================
# collected 2 items
#
# test_sample.py .                                                  [ 50%]
# test_sample.py .                                                  [100%]
#
# ============================== 2 passed in 0.01s ==============================
```

## 📝 编写测试

### 基本断言

```python
def add(a, b):
    return a + b

def test_add():
    # 基本断言
    assert add(1, 2) == 3
    assert add(0, 0) != 1
    
    # 包含断言
    assert "hello" in "hello world"
    assert 3 in [1, 2, 3]
    
    # 布尔断言
    assert add(1, 1)
    assert not add(-1, -1) == 0
    
    # 类型断言
    assert isinstance(add(1, 2), int)
    
    # 异常断言
    import pytest
    with pytest.raises(ZeroDivisionError):
        1 / 0
    
    with pytest.raises(ValueError, match="invalid"):
        int("invalid")
```

### 异常测试

```python
import pytest

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def test_divide_by_zero():
    with pytest.raises(ValueError) as exc_info:
        divide(10, 0)
    assert "zero" in str(exc_info.value)

def test_divide_normal():
    assert divide(10, 2) == 5
```

## 🔧 Fixture（测试夹具）

### 基本使用

```python
import pytest

@pytest.fixture
def user_data():
    return {
        "name": "Alice",
        "email": "alice@example.com",
        "age": 30
    }

def test_user_name(user_data):
    assert user_data["name"] == "Alice"

def test_user_email(user_data):
    assert user_data["email"].endswith("@example.com")
```

### 带 setup 和 teardown

```python
import pytest

@pytest.fixture
def database():
    # setup
    db = connect_to_test_db()
    db.create_tables()
    
    yield db  # 测试运行
    
    # teardown
    db.drop_tables()
    db.close()

def test_query(database):
    result = database.query("SELECT * FROM users")
    assert len(result) == 0
```

### Fixture 作用域

```python
# function（默认）：每个测试函数执行一次
@pytest.fixture
def user():
    return create_user()

# class：每个类执行一次
@pytest.fixture(scope="class")
def db_class():
    return connect_to_test_db()

# module：每个模块执行一次
@pytest.fixture(scope="module")
def db_module():
    return connect_to_test_db()

# session：整个测试会话执行一次
@pytest.fixture(scope="session")
def app():
    return create_app()
```

### Fixture 参数化

```python
import pytest

@pytest.fixture(params=["mysql", "postgresql", "sqlite"])
def db(request):
    if request.param == "mysql":
        return connect_mysql()
    elif request.param == "postgresql":
        return connect_postgresql()
    else:
        return connect_sqlite()

def test_query(db):
    result = db.query("SELECT 1")
    assert result == 1
```

### 自动使用

```python
import pytest
import tempfile
import os

@pytest.fixture(autouse=True)
def temp_file():
    # 每个测试前自动创建
    fd, path = tempfile.mkstemp()
    
    yield path
    
    # 每个测试后自动清理
    os.close(fd)
    os.unlink(path)

def test_write():
    with open("/tmp/test", "w") as f:
        f.write("hello")
    # 不需要手动清理
```

## 🎯 参数化测试

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (10, 20),
    (0, 0),
    (-1, -2),
])
def test_double(input, expected):
    assert input * 2 == expected
```

运行结果：
```
test_sample.py::test_double[1-2]     PASSED
test_sample.py::test_double[2-4]     PASSED
test_sample.py::test_double[3-6]     PASSED
test_sample.py::test_double[10-20]   PASSED
test_sample.py::test_double[0-0]     PASSED
test_sample.py::test_double[-1--2]   PASSED
```

### 参数化 ID

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
], ids=["one_to_two", "two_to_four"])
def test_double(input, expected):
    assert input * 2 == expected
```

## 🎭 Mock（模拟对象）

```python
import pytest
from unittest.mock import Mock, patch

# 简单 Mock
def test_with_mock():
    mock_obj = Mock()
    mock_obj.method.return_value = 42
    
    assert mock_obj.method() == 42
    mock_obj.method.assert_called_once()

# Patch 替换
def get_user_from_api(user_id):
    import requests
    r = requests.get(f"https://api.example.com/users/{user_id}")
    return r.json()

def test_api():
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"id": 1, "name": "Alice"}
        
        result = get_user_from_api(1)
        assert result["name"] == "Alice"
        mock_get.assert_called_once()
```

### pytest-mock 插件

```python
def test_with_pytest_mock(mocker):
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.json.return_value = {"ok": True}
    
    response = requests.get("https://api.example.com")
    assert response.json()["ok"] is True
```

## 📊 Fixtures 的高级用法

### conftest.py

```python
# conftest.py（自动加载）
import pytest

@pytest.fixture(scope="session")
def app():
    return create_app()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db():
    db = Database()
    yield db
    db.cleanup()

# 自动应用到所有测试
@pytest.fixture(autouse=True)
def setup_teardown():
    setup()
    yield
    teardown()
```

### conftest.py 目录结构

```
tests/
├── conftest.py              # 共享 fixture
├── unit/
│   ├── conftest.py         # 单元测试 fixture
│   └── test_user.py
├── integration/
│   ├── conftest.py         # 集成测试 fixture
│   └── test_api.py
```

## 🛠️ 实战：测试 UserService

```python
# user_service.py
class UserService:
    def __init__(self, db):
        self.db = db
    
    def get_user(self, user_id):
        user = self.db.query("SELECT * FROM users WHERE id = ?", user_id)
        if not user:
            return None
        return user
    
    def create_user(self, name, email):
        if "@" not in email:
            raise ValueError("Invalid email")
        return self.db.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (name, email)
        )

# test_user_service.py
import pytest
from user_service import UserService

@pytest.fixture
def mock_db():
    """模拟数据库"""
    class MockDB:
        def __init__(self):
            self.users = {}
        
        def query(self, sql, *args):
            return self.users.get(args[0])
        
        def execute(self, sql, *args):
            user_id = len(self.users) + 1
            self.users[user_id] = {"name": args[0], "email": args[1]}
            return user_id
    
    return MockDB()

@pytest.fixture
def service(mock_db):
    return UserService(mock_db)

def test_get_user_not_found(service):
    assert service.get_user(999) is None

def test_create_user(service):
    user_id = service.create_user("Alice", "alice@example.com")
    assert user_id == 1

def test_create_user_invalid_email(service):
    with pytest.raises(ValueError, match="Invalid email"):
        service.create_user("Bob", "invalid-email")

def test_get_user_exists(service, mock_db):
    user_id = service.create_user("Alice", "alice@example.com")
    user = service.get_user(user_id)
    assert user["name"] == "Alice"
```

## 📈 覆盖率

```bash
# 安装 pytest-cov
pip install pytest-cov

# 运行测试 + 覆盖率
pytest --cov=myapp --cov-report=html

# 输出
---------- coverage: platform linux, python 3.11 -----------
Name                 Stmts   Miss  Cover
----------------------------------------
myapp/__init__.py         0      0   100%
myapp/services.py        50     10    80%
myapp/utils.py           20      2    90%
----------------------------------------
TOTAL                    70     12    83%

# HTML 报告
open htmlcov/index.html
```

## 🚀 运行测试

```bash
# 运行所有测试
pytest

# 运行指定文件
pytest test_user.py

# 运行指定测试
pytest test_user.py::test_login

# 显示详细信息
pytest -v

# 失败时停止
pytest -x

# 第一个失败后停止
pytest --maxfail=1

# 并行运行（4 进程）
pytest -n 4

# 跳过慢测试
pytest -m "not slow"

# 只运行特定标记
pytest -m "smoke"

# 生成报告
pytest --html=report.html --self-contained-html
```

## 🏷️ 标记

```python
import pytest

@pytest.mark.slow
def test_slow():
    pass

@pytest.mark.integration
def test_api():
    pass

@pytest.mark.skip(reason="not implemented yet")
def test_skip():
    pass

@pytest.mark.skipif(condition, reason="...")
def test_conditional_skip():
    pass

@pytest.mark.xfail(reason="known bug")
def test_known_bug():
    assert False
```

```bash
# 只运行 smoke 测试
pytest -m smoke

# 跳过 slow 测试
pytest -m "not slow"

# pytest.ini / pyproject.toml
[tool.pytest.ini_options]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
]
```

## 🎯 总结

**pytest 核心要点**：
- ✅ Python 最流行的测试框架
- ✅ 简单 `assert` 即可编写测试
- ✅ Fixture 强大（setup/teardown/参数化）
- ✅ 参数化测试（@pytest.mark.parametrize）
- ✅ Mock（pytest-mock 或 unittest.mock）
- ✅ 标记（slow、integration、skip）
- ✅ 覆盖率（pytest-cov）
- ✅ 并行运行（pytest-xdist）
- ⚠️ Fixture 作用域影响性能
- ⚠️ 异步测试用 pytest-asyncio

**下一步：** [🧵 threading 多线程](/04-concurrency/threading) — 并发编程基础


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
