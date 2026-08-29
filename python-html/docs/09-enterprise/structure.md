---
title: 项目结构
---

# 🏗️ 项目结构

> 良好的**项目结构**是 Python 企业级开发的基础。本章介绍主流项目组织方式和最佳实践。

## 🎯 主流项目结构

### 方式 1：简单项目

```
myproject/
├── README.md
├── LICENSE
├── requirements.txt        # 生产依赖
├── requirements-dev.txt    # 开发依赖
├── setup.py / pyproject.toml
├── .gitignore
├── src/
│   └── myproject/
│       ├── __init__.py
│       ├── main.py
│       ├── core.py
│       └── utils.py
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   └── test_utils.py
└── docs/
    ├── conf.py
    └── index.rst
```

### 方式 2：Flask Web 项目

```
flask-app/
├── app/
│   ├── __init__.py          # create_app()
│   ├── config.py            # 配置类
│   ├── extensions.py        # 扩展实例
│   ├── blueprints/          # 蓝图
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── api.py
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── order.py
│   ├── services/            # 业务逻辑
│   │   ├── __init__.py
│   │   └── user_service.py
│   ├── utils/               # 工具
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── validators.py
│   ├── static/              # 静态文件
│   ├── templates/            # 模板
│   └── views/               # 视图
│       ├── __init__.py
│       ├── auth.py
│       └── order.py
├── migrations/              # 数据库迁移
├── tests/
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── scripts/                 # 工具脚本
├── config.py
├── requirements.txt
├── .env.example
└── run.py                   # 启动入口
```

### 方式 3：Django 项目

```
django-project/
├── manage.py
├── project/                # 项目配置
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   └── wsgi.py
├── apps/                   # 业务应用
│   ├── users/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── serializers.py
│   │   ├── services.py
│   │   ├── tests/
│   │   └── migrations/
│   └── orders/
├── static/
├── templates/
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
└── manage.py
```

### 方式 4：微服务项目

```
microservices/
├── services/
│   ├── user-service/
│   │   ├── app/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   └── README.md
│   ├── order-service/
│   │   └── ...
│   └── product-service/
│       └── ...
├── shared/
│   ├── common/              # 公共库
│   │   ├── auth/
│   │   ├── logging/
│   │   └── utils/
│   └── proto/               # protobuf 定义
├── deploy/
│   ├── docker-compose.yml
│   ├── k8s/
│   └── helm/
├── docs/
└── README.md
```

## 🛠️ 关键设计原则

### 单一职责原则（SRP）

```
每个模块/类只负责一件事

示例：
  - models/ 只放数据模型
  - services/ 只放业务逻辑
  - views/ 只放 HTTP 接口
  - utils/ 只放工具函数
```

### 分层架构

```
┌─────────────────┐
│  API Layer      │  ← 处理 HTTP 请求
│  (views/)       │
├─────────────────┤
│  Service Layer  │  ← 业务逻辑
│  (services/)    │
├─────────────────┤
│  Data Layer     │  ← 数据访问
│  (models/)      │
├─────────────────┤
│  Infrastructure │  ← 基础设施
│  (db, cache)    │
└─────────────────┘
```

### 依赖注入

```python
# 方式 1：构造函数注入
class UserService:
    def __init__(self, user_repo, email_service):
        self.user_repo = user_repo
        self.email_service = email_service
    
    def create_user(self, data):
        user = self.user_repo.create(data)
        self.email_service.send_welcome(user.email)
        return user

# 方式 2：使用依赖注入框架（dependency-injector）
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    user_repo = providers.Factory(UserRepository, db=...)
    email_service = providers.Factory(EmailService, smtp=...)
    user_service = providers.Factory(
        UserService,
        user_repo=user_repo,
        email_service=email_service
    )
```

## 🛠️ 配置管理

### 环境变量

```python
# .env
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
DEBUG=False
LOG_LEVEL=INFO
```

### 使用 pydantic Settings

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MyApp"
    debug: bool = False
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
print(settings.database_url)
```

### 多环境配置

```python
from pydantic_settings import BaseSettings

class BaseConfig(BaseSettings):
    app_name: str = "MyApp"
    
class DevConfig(BaseConfig):
    debug: bool = True
    database_url: str = "sqlite:///dev.db"

class ProdConfig(BaseConfig):
    debug: bool = False
    database_url: str

# 根据环境变量加载
import os
env = os.getenv("APP_ENV", "dev")
config = DevConfig() if env == "dev" else ProdConfig()
```

## 🛠️ 日志配置

```python
import logging
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "json",
            "level": "INFO"
        }
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "INFO"
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
```

## 🛠️ 异常处理

```python
# 自定义异常
class AppError(Exception):
    """应用基础异常"""
    pass

class NotFoundError(AppError):
    """资源未找到"""
    pass

class ValidationError(AppError):
    """数据验证失败"""
    pass

class PermissionError(AppError):
    """权限不足"""
    pass

# 统一异常处理
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    status_code_map = {
        NotFoundError: 404,
        ValidationError: 400,
        PermissionError: 403
    }
    return JSONResponse(
        status_code=status_code_map.get(type(exc), 500),
        content={"error": exc.__class__.__name__, "message": str(exc)}
    )
```

## 🛠️ 实战：完整项目模板

```python
# src/myproject/__init__.py
"""MyProject - A scalable Python application."""

__version__ = "1.0.0"

from myproject.app import create_app

__all__ = ["create_app"]
```

```python
# src/myproject/app.py
from myproject.config import settings
from myproject.logging import configure_logging
from myproject.api import router as api_router

def create_app():
    configure_logging(settings.log_level)
    app = FastAPI(title=settings.app_name, version="1.0.0")
    app.include_router(api_router)
    return app

app = create_app()
```

```python
# src/myproject/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MyApp"
    debug: bool = False
    log_level: str = "INFO"
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

```python
# src/myproject/api/users.py
from fastapi import APIRouter, HTTPException, Depends
from myproject.schemas.user import User, UserCreate
from myproject.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, service: UserService = Depends()):
    user = service.get(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

@router.post("/", response_model=User)
def create_user(data: UserCreate, service: UserService = Depends()):
    return service.create(data)
```

## 🎯 总结

**项目结构核心要点**：
- ✅ 单一职责原则（SRP）
- ✅ 分层架构（API / Service / Data / Infrastructure）
- ✅ 依赖注入
- ✅ 配置管理（pydantic Settings）
- ✅ 统一异常处理
- ✅ 日志配置（结构化）
- ✅ 测试目录独立
- ✅ 文档齐全
- ⚠️ 避免过度设计
- ⚠️ 按业务复杂度选择结构

**下一步：** [📦 依赖管理](/09-enterprise/dependencies) — pip / poetry


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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [java](https://java-px.bot.cd/java-web-manual/):Java 对比
- [ai](https://java-px.bot.cd/ai/):AI / 机器学习
- [bigdata](https://java-px.bot.cd/bigdata/):大数据 / 数据处理
