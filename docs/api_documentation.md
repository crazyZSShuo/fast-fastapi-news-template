# AI新闻网站API文档

## 项目概述

这是一个基于FastAPI构建的新闻网站后端API服务，提供新闻文章管理、用户认证、评论管理、访问统计等功能。

## 技术栈

- **Web框架**: FastAPI
- **数据库**: PostgreSQL/MySQL (SQLAlchemy ORM)
- **缓存**: Redis
- **认证**: JWT (JSON Web Tokens)
- **API文档**: Swagger UI / ReDoc
- **性能监控**: 自定义性能监控模块

## 系统架构

### 核心模块

1. **认证模块** (`app/api/v1/endpoints/auth.py`)
   - JWT token认证
   - 用户注册和登录
   - Token刷新机制

2. **用户模块** (`app/api/v1/endpoints/users.py`)
   - 用户信息管理
   - 权限控制

3. **文章模块** (`app/api/v1/endpoints/articles.py`)
   - 文章CRUD操作
   - 文章分类和标签
   - 浏览量统计

4. **评论模块** (`app/api/v1/endpoints/comments.py`)
   - 评论管理
   - 多级评论支持
   - 评论审核

5. **访问统计模块** (`app/api/v1/endpoints/visits.py`)
   - 访问记录
   - 访问统计分析

6. **仪表盘模块** (`app/api/v1/endpoints/dashboard.py`)
   - 数据统计
   - 趋势分析

### 数据模型

1. **用户模型** (User)
```sql
- id: Integer (主键)
- username: String(50) (唯一)
- email: String(100) (唯一)
- hashed_password: String(100)
- role: String(20)
- is_active: Boolean
- created_at: DateTime
- updated_at: DateTime
```

2. **文章模型** (Article)
```sql
- id: Integer (主键)
- title: String(200)
- content: Text
- category: String(50)
- tags: JSON
- status: Enum('draft', 'published')
- views: Integer
- author_id: Integer
- created_at: DateTime
- updated_at: DateTime
```

3. **评论模型** (Comment)
```sql
- id: Integer (主键)
- content: String(500)
- article_id: Integer (外键)
- user_id: Integer (外键)
- parent_id: Integer (外键，用于多级评论)
- status: String(20) (pending/approved/rejected)
- created_at: DateTime
- updated_at: DateTime
```

4. **访问记录模型** (Visit)
```sql
- id: Integer (主键)
- ip: String(50)
- location: String(200)
- user_agent: String(500)
- path: String(200)
- created_at: DateTime
```

## API接口

### 认证相关 (/auth)

#### POST /auth/register
注册新用户
- 请求体:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string"
  }
  ```
- 响应:
  ```json
  {
    "code": 200,
    "data": {
      "id": "integer",
      "username": "string",
      "email": "string",
      "role": "string",
      "is_active": "boolean"
    },
    "message": "string"
  }
  ```

#### POST /auth/login
用户登录
- 请求体:
  ```json
  {
    "username": "string", // 实际使用email
    "password": "string"
  }
  ```
- 响应:
  ```json
  {
    "access_token": "string",
    "token_type": "bearer",
    "refresh_token": "string"
  }
  ```

#### POST /auth/refresh
刷新访问令牌
- 请求体:
  ```json
  {
    "refresh_token": "string"
  }
  ```
- 响应:
  ```json
  {
    "code": 200,
    "data": {
      "access_token": "string",
      "token_type": "bearer",
      "refresh_token": "string"
    },
    "message": "string"
  }
  ```

### 文章相关 (/articles)

#### GET /articles
获取文章列表
- 查询参数:
  - page: int (默认1)
  - per_page: int (默认10)
  - category: string (可选)
  - status: string (可选)
  - tag: string (可选)
- 响应:
  ```json
  {
    "code": 200,
    "data": {
      "total": "integer",
      "items": [
        {
          "id": "integer",
          "title": "string",
          "category": "string",
          "tags": ["string"],
          "status": "string",
          "views": "integer",
          "created_at": "datetime"
        }
      ],
      "page": "integer",
      "per_page": "integer"
    },
    "message": "string"
  }
  ```

#### GET /articles/{article_id}
获取文章详情
- 路径参数:
  - article_id: int
- 响应:
  ```json
  {
    "code": 200,
    "data": {
      "id": "integer",
      "title": "string",
      "content": "string",
      "category": "string",
      "tags": ["string"],
      "status": "string",
      "views": "integer",
      "author_id": "integer",
      "created_at": "datetime",
      "updated_at": "datetime"
    },
    "message": "string"
  }
  ```

#### POST /articles
创建新文章
- 请求体:
  ```json
  {
    "title": "string",
    "content": "string",
    "category": "string",
    "tags": ["string"],
    "status": "string"
  }
  ```
- 响应: 返回创建的文章详情

#### PUT /articles/{article_id}
更新文章
- 路径参数:
  - article_id: int
- 请求体:
  ```json
  {
    "title": "string",
    "content": "string",
    "category": "string",
    "tags": ["string"],
    "status": "string"
  }
  ```
- 响应: 返回更新后的文章详情

#### DELETE /articles/{article_id}
删除文章
- 路径参数:
  - article_id: int
- 响应: 返回被删除的文章详情

### 评论相关 (/comments)

#### GET /comments/article/{article_id}
获取文章评论
- 路径参数:
  - article_id: int
- 查询参数:
  - page: int (默认1)
  - per_page: int (默认10)
  - parent_id: int (可选，获取回复)
- 响应:
  ```json
  {
    "code": 200,
    "data": {
      "total": "integer",
      "items": [
        {
          "id": "integer",
          "content": "string",
          "user_id": "integer",
          "article_id": "integer",
          "parent_id": "integer",
          "status": "string",
          "created_at": "datetime",
          "replies": [
            {
              "id": "integer",
              "content": "string",
              "user_id": "integer",
              "created_at": "datetime"
            }
          ],
          "reply_count": "integer"
        }
      ],
      "page": "integer",
      "per_page": "integer"
    },
    "message": "string"
  }
  ```

#### POST /comments
创建评论
- 请求体:
  ```json
  {
    "content": "string",
    "article_id": "integer",
    "parent_id": "integer" // 可选
  }
  ```
- 响应: 返回创建的评论详情

#### POST /comments/{comment_id}/review
审核评论（仅管理员）
- 路径参数:
  - comment_id: int
- 查询参数:
  - status: string (approved/rejected)
- 响应: 返回更新后的评论详情

#### DELETE /comments/article/{article_id}/comment/{comment_id}
删除评论
- 路径参数:
  - article_id: int
  - comment_id: int
- 响应: 返回被删除的评论详情

### 仪表盘相关 (/dashboard)

#### GET /dashboard/stats
获取统计数据
- 响应:
  ```json
  {
    "code": 200,
    "data": {
      "article_count": "integer",
      "comment_count": "integer",
      "user_count": "integer",
      "trend_data": {
        "dates": ["string"],
        "articles": ["integer"],
        "comments": ["integer"]
      }
    },
    "message": "string"
  }
  ```

### 访问统计相关 (/visits)

#### POST /visits
记录访问信息
- 自动记录
  - IP地址
  - User Agent
  - 访问路径
- 响应: 返回访问记录详情

#### GET /visits/stats
获取访问统计（仅管理员）
- 响应:
  ```json
  {
    "code": 200,
    "data": {
      "total_visits": "integer",
      "unique_visitors": "integer",
      "popular_pages": [
        {
          "path": "string",
          "count": "integer"
        }
      ]
    },
    "message": "string"
  }
  ```

## 错误处理

API使用标准的HTTP状态码表示请求的结果：

- 200: 请求成功
- 400: 请求参数错误
- 401: 未认证
- 403: 无权限
- 404: 资源不存在
- 500: 服务器内部错误

错误响应格式：
```json
{
  "code": "integer",
  "message": "string",
  "detail": "string"
}
```

## 安全性

1. **认证机制**
   - 使用JWT进行用户认证
   - Access Token有效期较短
   - Refresh Token用于更新Access Token
   - 密码加密存储

2. **权限控制**
   - 基于角色的访问控制(RBAC)
   - 用户角色: admin/user
   - 特定接口仅管理员可访问

3. **数据验证**
   - 请求数据验证
   - SQL注入防护
   - XSS防护

## 性能优化

1. **缓存策略**
   - Redis缓存热门文章
   - 缓存统计数据
   - 防止缓存穿透和雪崩

2. **数据库优化**
   - 索引优化
   - 分页查询
   - 关联查询优化

3. **监控**
   - 性能指标收集
   - 访问统计
   - 错误日志

## 部署要求

1. **环境要求**
   - Python 3.8+
   - PostgreSQL/MySQL
   - Redis

2. **配置项**
   - 数据库连接
   - Redis连接
   - JWT密钥
   - 跨域设置
   - 日志配置

3. **环境变量**
   ```
   DATABASE_URL=postgresql://user:password@localhost/dbname
   REDIS_URL=redis://localhost
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```
