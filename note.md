这是为你整理的 **《2026最新FastAPI+Tortoise-ORM入门教程》** 的详细笔记，结合了B站视频的课程结构和主流的学习资料。希望能帮你构建一个扎实的知识体系，并顺利过渡到实战项目。你可以把它作为开发速查手册，随时查阅。

---

### 🚀 第一部分：环境搭建与基础

#### 1. 环境搭建 (第2课)

在正式开始编码前，我们需要先准备好开发环境。

*   **创建项目目录**：为你的项目创建一个独立的文件夹。
*   **安装依赖**：打开终端，在项目目录下执行以下命令来安装必要的库：
    ```bash
    # 安装 FastAPI 和 Uvicorn (ASGI 服务器)
    pip install fastapi uvicorn[standard]
    # 安装 Tortoise ORM 及数据库驱动 (以 SQLite 为例)
    pip install tortoise-orm
    ```

    > **说明**：`uvicorn[standard]` 包含了 `uvloop` 和 `httptools` 等高性能依赖，推荐生产环境也使用这个配置。

#### 2. 第一个FastAPI程序

创建一个名为 `main.py` 的文件，写入以下代码：

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello FastAPI"} 
```

启动应用：

```bash
uvicorn main:app --reload
```

访问 `http://127.0.0.1:8000` 即可看到 JSON 响应。 `--reload` 参数会在代码变动时自动重启服务，非常适合开发阶段。

#### 3. 基础路由和请求参数 (第3-4课)

##### 路径参数 (Path Parameters)
```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id} 
```
> 访问 `/users/123` 返回 `{"user_id": 123}`。FastAPI会基于类型提示自动将字符串路径参数解析为指定的Python类型。

##### 查询参数 (Query Parameters)
```python
@app.get("/items/")
async def list_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit} 
```
> 访问 `/items/?skip=5&limit=20` 会得到 `{"skip": 5, "limit": 20}`。参数默认值使其成为可选参数。

##### 请求体 (Request Body) (第5课)
```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = None

@app.post("/items/")
async def create_item(item: Item):
    return item
```
> Pydantic的`BaseModel`自动处理JSON反序列化和数据校验。无效数据会返回清晰的错误信息。

##### 表单与文件上传 (第5-6课)
```python
from fastapi import Form, File, UploadFile

@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    return {"filename": file.filename, "content_type": file.content_type}
```
> - 表单参数使用 `Form(...)`，`...` 表示该参数为必填。对于可选参数，可使用默认值，如 `Form(None)`。
> - `UploadFile` 比 `bytes` 更高效，因为它使用一个**临时文件**来存储上传的内容，非常适合处理大文件。

##### 请求头 (Header) (第6课)
```python
from fastapi import Header

@app.get("/header/")
async def get_header(user_agent: str = Header(None)):
    return {"User-Agent": user_agent}
```
> 当路径、查询、请求体、表单、文件和请求头这几种参数混合使用时，FastAPI的注入顺序是：**路径参数 → 查询参数 → 请求头参数 → 请求体参数**（包括Body、Form、File）。这与参数的声明顺序无关。

##### 一个混合参数的完整示例
下面这个示例包含了路径参数、查询参数、请求体参数和请求头参数，直观展示了它们的声明和自动注入：

```python
from fastapi import FastAPI, Path, Query, Header
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.put("/items/{item_id}")
async def update_item(
    item_id: int = Path(..., description="The ID of the item to update"),  # 路径参数
    q: Optional[str] = Query(None, max_length=50),                        # 查询参数
    item: Item = None,                                                   # 请求体参数
    x_token: str = Header(None),                                        # 请求头参数
):
    result = {"item_id": item_id, "item": item}
    if q:
        result.update({"q": q})
    if x_token:
        result.update({"x_token": x_token})
    return result
```
> - `Path(...)` 为路径参数添加描述信息。
> - `Query(None, max_length=50)` 为查询参数设置默认值 `None` 和最大长度限制。
> - `item: Item = None` 表示请求体可选。
> - `Header(None)` 表示请求头可选。


### 🗄️ 第二部分：Tortoise-ORM深入

Tortoise-ORM是一个原生支持`asyncio`的ORM，其API设计深受Django ORM启发，对熟悉Django的开发者来说非常友好。

#### 1. 模型定义与字段类型 (第7-8课)

*   **定义模型**：创建一个`models.py`文件。
    ```python
    from tortoise import Model, fields

    class User(Model):
        id = fields.IntField(pk=True)
        name = fields.CharField(max_length=255)
        email = fields.CharField(max_length=255, unique=True)
        created_at = fields.DatetimeField(auto_now_add=True)
        class Meta:
            table = "users"  # 指定数据库表名
    ```
    > `CharField` 需指定 `max_length`；`unique=True` 会为 `email` 字段添加唯一约束。

#### 2. 关系字段 (Relationship Fields) (第8-10课)

Tortoise-ORM 提供了清晰的关系定义方式，涵盖了数据库中最常见的三种关系类型：**一对多**、**多对多**和**一对一**。

*   **一对多 (ForeignKeyField)**
    ```python
    class User(Model):
        # ... 其他字段 ...
        pass

    class Post(Model):
        title = fields.CharField(max_length=255)
        content = fields.TextField()
        # 外键关联到 User 模型，related_name 用于反向查询，如 user.posts
        author = fields.ForeignKeyField("models.User", related_name="posts")
    ```
    > 通过 `ForeignKeyField` 建立从 `Post` 到 `User` 的链接，`related_name="posts"` 允许我们通过 `user.posts` 查询该作者的所有文章。

*   **多对多 (ManyToManyField)**
    ```python
    class Tag(Model):
        name = fields.CharField(max_length=50, unique=True)

    class Post(Model):
        # ... 其他字段 ...
        tags = fields.ManyToManyField("models.Tag", related_name="posts")
    ```
    > `ManyToManyField` 会自动创建一张中间表来维护 `Post` 和 `Tag` 的多对多关系。这使得查询和操作变得非常直观。

*   **一对一 (OneToOneField)**：此课程可能未提及，但它是另一个重要的关系类型。`OneToOneField` 用于表示模型间的一对一关系，如用户与其个人资料。
    ```python
    class Profile(Model):
        user = fields.OneToOneField("models.User", related_name="profile", on_delete=fields.CASCADE)
        bio = fields.TextField(null=True)
    ```
    > `on_delete=fields.CASCADE` 表示当关联的用户被删除时，其对应的个人资料记录也会被级联删除。

#### 3. CRUD操作与高级查询 (第7-10课)

Tortoise-ORM 提供了丰富且强大的增删改查（CRUD）方法。

*   **创建 (Create)**
    ```python
    # 方式一：使用 create
    user = await User.create(name="寒枫", email="hanfeng@example.com")
    # 方式二：先实例化再保存
    user = User(name="枫", email="feng@example.com")
    await user.save()
    ```

*   **查询 (Read)**
    ```python
    # 获取单条记录，不存在则抛出 DoesNotExist 异常
    user = await User.get(id=1)
    # 使用 filter 链式查询，返回 QuerySet
    users = await User.filter(name__icontains="枫").all()
    # 获取所有记录
    all_users = await User.all()
    ```

*   **更新 (Update)**
    ```python
    # 方式一：从对象更新
    user.name = "new_name"
    await user.save(update_fields=["name"])
    # 方式二：批量更新
    await User.filter(id=1).update(name="batch_updated_name")
    ```

*   **删除 (Delete)**
    ```python
    # 删除单条记录
    await user.delete()
    # 批量删除
    await User.filter(name__isnull=True).delete()
    ```

*   **高级查询**
    ```python
    # 排序
    users = await User.all().order_by("-created_at")
    # 限制与偏移
    users = await User.all().offset(10).limit(10)
    # 预加载关联字段（解决 N+1 问题）
    posts = await Post.all().prefetch_related("author", "tags")
    for post in posts:
        print(post.author.name, [tag.name for tag in post.tags])
    ```
    > `prefetch_related` 用于预加载关联对象，避免在循环中多次查询数据库，是优化查询性能的关键手段。


### 🔗 第三部分：FastAPI 集成Tortoise-ORM

集成Tortoise-ORM到FastAPI应用，推荐使用 `lifespan` 生命周期管理。

*   **生命周期集成 (`lifespan`)**：在`main.py`中完整集成。
    ```python
    from contextlib import asynccontextmanager
    from fastapi import FastAPI
    from tortoise import Tortoise

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # 启动时执行
        await Tortoise.init(
            db_url="sqlite://db.sqlite3",
            modules={"models": ["models"]}
        )
        await Tortoise.generate_schemas()
        yield
        # 关闭时执行
        await Tortoise.close_connections()

    app = FastAPI(lifespan=lifespan)
    ```
    > `Tortoise.init()` 必须在接收请求前完成，而 `close_connections()` 则在应用停止时优雅地关闭数据库连接，防止连接泄露。

*   **在路径操作中使用**：在`main.py`或其他路由文件中，直接调用模型方法即可。
    ```python
    from fastapi import FastAPI, HTTPException
    from models import User
    from pydantic import BaseModel

    app = FastAPI()

    class UserCreate(BaseModel):
        name: str
        email: str

    @app.post("/users/", response_model=UserCreate)
    async def create_user(user: UserCreate):
        user_obj = await User.create(**user.dict())
        return user_obj

    @app.get("/users/{user_id}")
    async def read_user(user_id: int):
        user = await User.get_or_none(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"id": user.id, "name": user.name, "email": user.email}
    ```
    > `response_model=UserCreate` 会自动过滤并格式化API的响应数据，只返回模型中定义的字段。而 `get_or_none()` 方法在记录不存在时返回 `None` 而不是抛出异常，配合 `HTTPException` 可以优雅地处理404错误。


### 🚢 第四部分：进阶与生产环境准备

完成基础开发后，为投入生产环境，以下实践是必不可少的一步。

*   **数据库迁移 (Migrations with Aerich)**：生产环境中，当模型发生变化时，绝不能手动去修改数据库表结构。`Aerich` 就是Tortoise-ORM的官方迁移工具，它能像版本控制一样管理你的数据库Schema变更。以下是 `Aerich` 的完整使用流程：
    1.  **安装Aerich**:
        ```bash
        pip install aerich
        ```
    2.  **初始化Aerich** (在项目根目录):
        ```bash
        aerich init -t app.database.TORTOISE_ORM
        aerich init-db
        ```
    3.  **创建和运行迁移**:
        ```bash
        # 模型变更后，生成迁移文件
        aerich migrate --name "add_user_table"
        # 应用迁移到数据库
        aerich upgrade
        ```
    > 其中 `app.database.TORTOISE_ORM` 是你存放Tortoise-ORM配置的变量路径。在实际使用前，请务必参考官方文档进行详细配置。

*   **Pydantic 模型 (Schemas)**：为API的请求和响应定义专门的Pydantic模型，可以更好地实现数据验证、序列化和API文档自动化。
    ```python
    from pydantic import BaseModel
    from typing import Optional

    class UserBase(BaseModel):
        name: str
        email: str

    class UserCreate(UserBase):
        password: str

    class UserResponse(UserBase):
        id: int
        class Config:
            from_attributes = True  # 允许从ORM对象创建
    ```
    > 在路径操作函数中，使用 `UserCreate` 接收请求体，使用 `UserResponse` 作为 `response_model`，这样可以清晰地分离输入和输出模型，避免敏感信息泄露。

### 📝 常见问题与排错

*   **循环导入问题 (Circular Import)**：当 `models.py` 文件中的模型相互引用时，可能会出现循环导入。Tortoise-ORM使用字符串引用（如 `"models.User"`）来延迟解析，可以有效避免此问题。
*   **数据库连接未关闭**：务必在应用关闭时调用 `Tortoise.close_connections()`，以防止连接泄露。使用 `lifespan` 生命周期可以确保这一点。
*   **异步操作未 `await`**：所有 Tortoise-ORM 的数据库操作（如 `create`, `filter`, `save`）都是异步的，调用时必须使用 `await` 关键字，否则会得到一个协程对象而不是预期结果。
*   **类型注解问题**：在路径操作函数中，如果没有为参数提供默认值，FastAPI 默认会将其视为必填。使用 `Query()`、`Path()` 等函数可以更精确地控制参数行为（如设置默认值、描述信息等）。

### 🎯 总结与后续路线图

恭喜你，到这里你已经掌握了这门课的核心内容。你将能用FastAPI快速构建API，并用Tortoise-ORM高效地操作数据库。

**🚀 后续学习路线：**

1.  **巩固基础**：尝试用课程知识，独立实现一个简单的博客或待办事项应用后端。
2.  **进阶集成**：学习 **Aerich** 进行数据库迁移。
3.  **完善工程**：为项目添加认证授权、中间件、后台任务、WebSocket等模块。
4.  **部署上线**：学习如何将你的FastAPI应用部署到服务器或云平台（如Deta, Heroku等）。

最后，建议开启项目的交互式API文档（`/docs`），它是你学习和调试的好帮手。在你后续的实战旅程中，遇到任何具体的技术难题，都可以随时再来问我。