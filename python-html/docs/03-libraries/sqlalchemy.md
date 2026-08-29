---
title: SQLAlchemy ORM
date: 2026-08-15  # date-auto-injected
---

# 🗄️ SQLAlchemy ORM

> **SQLAlchemy** 是 Python **最流行的 ORM 库**。提供 **Core（SQL 工具包）** 和 **ORM（对象关系映射）** 两层抽象。

## 🎯 SQLAlchemy 两大组件

```
1. Core（SQL 工具包）
   - SQL 表达式语言
   - 数据库连接池
   - 事务管理

2. ORM（对象关系映射）
   - 类 → 表
   - 对象 → 行
   - 属性 → 列
   - 关系 → 外键
```

## 🚀 快速开始

### 安装

```bash
pip install sqlalchemy
# 或带异步支持
pip install sqlalchemy[asyncio]
# 特定数据库驱动
pip install psycopg2-binary   # PostgreSQL
pip install pymysql           # MySQL
```

### 连接数据库

```python
from sqlalchemy import create_engine

# SQLite
engine = create_engine("sqlite:///test.db")

# PostgreSQL
engine = create_engine("postgresql://user:pass@localhost/dbname")

# MySQL
engine = create_engine("mysql+pymysql://user:pass@localhost/dbname")

# 带连接池
engine = create_engine(
    "postgresql://user:pass@localhost/dbname",
    pool_size=10,           # 连接池大小
    max_overflow=20,        # 最大溢出
    pool_pre_ping=True,     # 健康检查
    pool_recycle=3600,      # 连接回收时间
)
```

## 🏗️ ORM 基础

### 定义模型

```python
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True)
    age = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}')>"

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.now)
    
    author = relationship("User", back_populates="posts")
```

### 创建表

```python
# 创建所有表
Base.metadata.create_all(engine)

# 删除所有表（⚠️ 慎用）
Base.metadata.drop_all(engine)
```

## 🛠️ Session（会话）

### 创建 Session

```python
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 使用 Session
session = SessionLocal()
try:
    # 业务逻辑
    user = User(name="Alice", email="alice@example.com")
    session.add(user)
    session.commit()
except Exception:
    session.rollback()
    raise
finally:
    session.close()
```

### Session 生命周期

```python
# 短 Session（推荐）
def get_user(user_id):
    session = SessionLocal()
    try:
        return session.query(User).filter_by(id=user_id).first()
    finally:
        session.close()

# 上下文管理器
from contextlib import contextmanager

@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# 使用
with session_scope() as session:
    user = User(name="Bob")
    session.add(user)
```

## 📝 CRUD 操作

### Create（创建）

```python
# 方式 1：单条
user = User(name="Alice", email="alice@example.com", age=30)
session.add(user)
session.commit()

# 方式 2：批量
session.add_all([
    User(name="Bob", email="bob@example.com"),
    User(name="Carol", email="carol@example.com")
])
session.commit()

# 方式 3：merge（处理已存在的对象）
existing = session.merge(User(id=1, name="Updated"))
```

### Read（查询）

```python
# 查询所有
users = session.query(User).all()

# 按主键
user = session.query(User).get(1)
user = session.get(User, 1)  # 新版推荐

# 条件查询
user = session.query(User).filter_by(name="Alice").first()
user = session.query(User).filter(User.name == "Alice").first()

# 复杂查询
users = session.query(User).filter(
    User.age >= 18,
    User.age <= 60,
    User.name.like("A%")
).all()

# 排序
users = session.query(User).order_by(User.created_at.desc()).all()

# 限制
users = session.query(User).limit(10).offset(0).all()

# 聚合
from sqlalchemy import func
count = session.query(func.count(User.id)).scalar()
avg_age = session.query(func.avg(User.age)).scalar()

# 关联查询
users_with_posts = session.query(User).join(Post).filter(
    Post.title.like("Python%")
).all()
```

### Update（更新）

```python
# 方式 1：修改对象
user = session.query(User).get(1)
user.age = 31
session.commit()

# 方式 2：批量更新
session.query(User).filter(User.age < 18).update(
    {User.age: 18},
    synchronize_session=False
)
session.commit()

# 方式 3：update 后使用 returning
result = session.query(User).filter(User.id == 1).update(
    {"name": "Alice New"},
    synchronize_session="fetch"
)
session.commit()
```

### Delete（删除）

```python
# 单个
user = session.query(User).get(1)
session.delete(user)
session.commit()

# 批量
session.query(User).filter(User.age < 18).delete()
session.commit()
```

## 🔗 关系映射

### 一对多

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    author = relationship("User", back_populates="posts")

# 使用
user = session.query(User).get(1)
for post in user.posts:
    print(post.title)

# 预加载（避免 N+1 查询）
from sqlalchemy.orm import joinedload
users = session.query(User).options(joinedload(User.posts)).all()
```

### 多对多

```python
# 关联表
student_course = Table(
    "student_course",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True)
)

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    courses = relationship("Course", secondary=student_course, back_populates="students")

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    students = relationship("Student", secondary=student_course, back_populates="courses")

# 使用
student = session.query(Student).get(1)
for course in student.courses:
    print(course.title)
```

### 一对一

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    profile = relationship("Profile", uselist=False, back_populates="user")

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    bio = Column(String)
    user = relationship("User", back_populates="profile")
```

## 🛠️ 实战：完整示例

```python
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100), unique=True)
    created_at = Column(DateTime, default=datetime.now)
    
    orders = relationship("Order", back_populates="user")
    
    def __repr__(self):
        return f"<User({self.name})>"

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="orders")
    
    def __repr__(self):
        return f"<Order(id={self.id}, amount={self.amount})>"

# 初始化
engine = create_engine("sqlite:///shop.db")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

# 使用
session = SessionLocal()

# 创建
user = User(name="Alice", email="alice@example.com")
session.add(user)
session.commit()

order = Order(user_id=user.id, amount=9999, status="paid")
session.add(order)
session.commit()

# 查询
users = session.query(User).all()
for u in users:
    print(f"{u.name}: {len(u.orders)} orders")
    for o in u.orders:
        print(f"  - {o.amount} ({o.status})")

session.close()
```

## 🎯 总结

**SQLAlchemy ORM 核心要点**：
- ✅ Core + ORM 两层抽象
- ✅ 支持多种数据库（MySQL/PostgreSQL/SQLite/Oracle）
- ✅ 类型映射（类 → 表，对象 → 行）
- ✅ 关系映射（一对多、多对多、一对一）
- ✅ Session 管理（连接池、事务）
- ✅ 预加载（解决 N+1）
- ✅ 异步支持（SQLAlchemy 2.0+）
- ⚠️ N+1 查询需用 joinedload 解决
- ⚠️ 复杂查询考虑用 Core（更可控）

**下一步：** [📊 pandas 数据分析](/03-libraries/pandas) — 数据处理库


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
