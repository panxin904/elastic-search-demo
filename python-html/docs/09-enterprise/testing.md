---
title: 单元测试
---

# 🧪 单元测试

> **单元测试**是保证代码质量的基础。本章详解 pytest 框架和最佳实践。

## 🎯 测试金字塔

```
       /\
      /E2E\        少量（慢、贵）
     /----\
    /集成  \      一些
   /--------\
  /单元测试  \   大量（快、便宜）
 /------------\
```

| 测试类型 | 速度 | 数量 | 目的 |
|---------|------|------|------|
| 单元测试 | 快 | 多 | 测试单个函数/类 |
| 集成测试 | 中 | 中 | 测试模块间交互 |
| E2E 测试 | 慢 | 少 | 测试完整流程 |

## 🛠️ pytest 基础

### 安装

```bash
pip install pytest pytest-cov pytest-mock pytest-asyncio
```

### 第一个测试

```python
# test_calculator.py
def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

# 测试
def test_add():
    assert add(1, 2) == 3
    assert add(0, 0) == 0
    assert add(-1, 1) == 0

def test_divide():
    assert divide(10, 2) == 5
    assert divide(-6, 3) == -2

def test_divide_by_zero():
    import pytest
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)
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
    assert "@" in user_data["email"]
```

### 带 setup 和 teardown

```python
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

### conftest.py

```python
# conftest.py
import pytest

@pytest.fixture(scope="session")
def app():
    """整个测试会话共享的应用实例"""
    from myapp import create_app
    return create_app()

@pytest.fixture
def client(app):
    """测试客户端"""
    return app.test_client()

@pytest.fixture
def db():
    """测试数据库"""
    db = connect_to_test_db()
    yield db
    db.cleanup()
```

## 🎯 参数化测试

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (0, 0),
    (-1, -2),
    (10, 20),
])
def test_double(input, expected):
    assert input * 2 == expected

# 多参数组合
@pytest.mark.parametrize("a", [1, 2, 3])
@pytest.mark.parametrize("b", [10, 20])
def test_add(a, b):
    assert a + b == a + b

# 自定义 ID
@pytest.mark.parametrize("a,b,expected", [
    (1, 1, 2),
    (2, 3, 5),
], ids=["one_plus_one", "two_plus_three"])
def test_add_ids(a, b, expected):
    assert a + b == expected
```

## 🎭 Mock（模拟对象）

```python
# 使用 unittest.mock
from unittest.mock import Mock, patch

# 1. Mock 对象
def test_with_mock():
    mock = Mock()
    mock.method.return_value = 42
    assert mock.method() == 42
    mock.method.assert_called_once()

# 2. Patch 函数
def get_user_from_api(user_id):
    import requests
    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()

def test_api():
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"id": 1, "name": "Alice"}
        
        result = get_user_from_api(1)
        assert result["name"] == "Alice"
        mock_get.assert_called_once_with("https://api.example.com/users/1")

# 3. pytest-mock 插件
def test_with_pytest_mock(mocker):
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.json.return_value = {"ok": True}
    
    # 测试代码
    assert requests.get("url").json()["ok"] is True
```

## 🔧 实战：测试 Web 应用（Flask）

```python
# tests/test_app.py
import pytest
from myapp import create_app
from myapp.models import db, User

@pytest.fixture
def app():
    app = create_app({"TESTING": True, "DATABASE_URL": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200

def test_register(client):
    response = client.post("/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "secret"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["username"] == "alice"

def test_login(client):
    # 先注册
    client.post("/register", json={...})
    
    # 测试登录
    response = client.post("/login", json={
        "username": "alice",
        "password": "secret"
    })
    assert response.status_code == 200
    assert "token" in response.get_json()
```

## 🔧 实战：测试 FastAPI

```python
import pytest
from fastapi.testclient import TestClient
from myapp.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_create_user(client):
    response = client.post("/users", json={
        "name": "Alice",
        "email": "alice@example.com"
    })
    assert response.status_code == 201
    assert response.json()["name"] == "Alice"

def test_get_user(client):
    response = client.get("/users/1")
    assert response.status_code == 200

def test_validation_error(client):
    response = client.post("/users", json={"name": ""})
    assert response.status_code == 422
```

## 🔧 异步测试

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    import asyncio
    await asyncio.sleep(0.1)
    result = await fetch_data()
    assert result == "data"

# pytest-asyncio 配置
# pytest.ini
[pytest]
asyncio_mode = auto
```

## 📊 测试覆盖率

```bash
# 安装 pytest-cov
pip install pytest-cov

# 运行测试 + 覆盖率
pytest --cov=myapp --cov-report=html tests/

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

```ini
# .coveragerc
[run]
source = myapp
omit = 
    myapp/tests/*
    myapp/migrations/*

[report]
exclude_lines =
    pragma: no cover
    raise NotImplementedError
    if __name__ == .__main__.:
```

## 📊 高级特性

### 标记

```python
import pytest

@pytest.mark.slow
def test_slow():
    pass

@pytest.mark.integration
def test_integration():
    pass

# 运行特定标记
# pytest -m "not slow"
# pytest -m "integration"
```

```ini
# pytest.ini
[pytest]
markers =
    slow: marks tests as slow
    integration: integration tests
    unit: unit tests
```

### 跳过

```python
import pytest
import sys

@pytest.mark.skip(reason="not implemented")
def test_future():
    pass

@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires Python 3.10+")
def test_new_feature():
    pass

@pytest.mark.xfail(reason="known bug")
def test_known_bug():
    assert False  # 预期失败
```

### 异常测试

```python
import pytest

def test_zero_division():
    with pytest.raises(ZeroDivisionError):
        1 / 0

def test_specific_exception():
    with pytest.raises(ValueError, match="invalid"):
        int("invalid")

def test_exception_info():
    with pytest.raises(ValueError) as exc_info:
        int("invalid")
    assert "invalid" in str(exc_info.value)
    assert exc_info.type is ValueError
```

### 参数化 + Fixture

```python
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

## 🔧 实战：完整测试项目

```
tests/
├── conftest.py            # 共享 fixture
├── unit/
│   ├── conftest.py
│   ├── test_services.py
│   ├── test_utils.py
│   └── test_models.py
├── integration/
│   ├── conftest.py
│   ├── test_api.py
│   └── test_db.py
└── e2e/
    ├── conftest.py
    └── test_workflows.py
```

```python
# conftest.py
import pytest
from myapp import create_app
from myapp.db import db

@pytest.fixture(scope="session")
def app():
    app = create_app(testing=True)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db_session(app):
    with app.app_context():
        db.create_all()
        yield db.session
        db.drop_all()

# 标记
slow = pytest.mark.slow
integration = pytest.mark.integration
```

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow
    integration: integration tests
```

## 📊 性能对比

```python
import time

def test_benchmark():
    """比较 list vs set 查找"""
    data = list(range(10000))
    data_set = set(data)
    
    start = time.time()
    for _ in range(1000):
        5000 in data  # O(n)
    list_time = time.time() - start
    
    start = time.time()
    for _ in range(1000):
        5000 in data_set  # O(1)
    set_time = time.time() - start
    
    assert set_time < list_time  # set 快 100x+
```

## 🎯 总结

**单元测试核心要点**：
- ✅ pytest 是 Python 测试首选
- ✅ Fixture 强大（setup/teardown/作用域）
- ✅ 参数化测试（@pytest.mark.parametrize）
- ✅ Mock 模拟依赖
- ✅ 覆盖率（pytest-cov）
- ✅ 标记（slow/integration/skip）
- ✅ conftest.py 共享 fixture
- ✅ 异步测试（pytest-asyncio）
- ⚠️ 测试要快、独立、可重复
- ⚠️ 避免脆弱测试

**下一步：** [🚀 性能优化](/09-enterprise/performance) — Python 性能调优
