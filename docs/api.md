# News API 接口文档

## 目录

- [基本信息](#基本信息)
- [认证相关](#认证相关)
- [用户管理](#用户管理)
- [文章管理](#文章管理)
- [评论管理](#评论管理)
- [系统相关](#系统相关)

## 基本信息

- 基础URL: `/api/v1`
- 认证方式: Bearer Token
- 响应格式: 
  ```json
  {
    "code": 200,
    "message": "Success",
    "data": {}
  }
  ```

## 认证相关

### 用户注册
- **接口**: `POST /auth/register`
- **描述**: 新用户注册
- **请求体**:
  ```json
  {
    "email": "user@example.com",
    "password": "string",
    "username": "string"
  }
  ```
- **响应**: 返回新创建的用户信息

### 用户登录
- **接口**: `POST /auth/login`
- **描述**: 用户登录获取token
- **请求体** (form-data):
  ```
  username: "user@example.com"
  password: "string"
  ```
- **响应**:
  ```json
  {
    "access_token": "string",
    "token_type": "bearer",
    "refresh_token": "string"
  }
  ```

### 刷新Token
- **接口**: `POST /auth/refresh`
- **描述**: 使用refresh token获取新的access token
- **请求体**:
  ```json
  {
    "refresh_token": "string"
  }
  ```
- **响应**: 同登录接口

## 用户管理

### 获取当前用户信息
- **接口**: `GET /users/me`
- **描述**: 获取当前登录用户的详细信息
- **权限**: 需要登录
- **响应**: 返回用户详细信息

### 更新当前用户信息
- **接口**: `PUT /users/me`
- **描述**: 更新当前登录用户的信息
- **权限**: 需要登录
- **请求体**:
  ```json
  {
    "username": "string",
    "password": "string"  // 可选
  }
  ```
- **响应**: 返回更新后的用户信息

### 获取用户列表
- **接口**: `GET /users`
- **描述**: 获取所有用户的列表
- **权限**: 仅管理员
- **查询参数**:
  - skip: 跳过的记录数
  - limit: 返回的最大记录数
- **响应**: 返回用户列表

### 获取指定用户信息
- **接口**: `GET /users/{user_id}`
- **描述**: 获取指定用户的详细信息
- **权限**: 管理员或用户本人
- **响应**: 返回用户详细信息

## 文章管理

### 获取文章列表
- **接口**: `GET /articles`
- **描述**: 获取文章列表，支持分页和筛选
- **权限**: 需要登录
- **查询参数**:
  - page: 页码
  - per_page: 每页数量
  - keyword: 搜索关键词（可选）
  - category: 文章分类（可选）
  - author_id: 作者ID（可选）
- **响应**: 返回文章列表和分页信息

### 获取文章详情
- **接口**: `GET /articles/{article_id}`
- **描述**: 获取指定文章的详细信息
- **权限**: 需要登录
- **响应**: 返回文章详细信息，包括浏览量

### 创建文章
- **接口**: `POST /articles`
- **描述**: 创建新文章
- **权限**: 需要登录
- **请求体**:
  ```json
  {
    "title": "string",
    "content": "string",
    "summary": "string",
    "category": "string"
  }
  ```
- **响应**: 返回创建的文章信息

### 更新文章
- **接口**: `PUT /articles/{article_id}`
- **描述**: 更新指定文章
- **权限**: 管理员或文章作者
- **请求体**: 同创建文章
- **响应**: 返回更新后的文章信息

### 删除文章
- **接口**: `DELETE /articles/{article_id}`
- **描述**: 删除指定文章
- **权限**: 管理员或文章作者
- **响应**: 返回被删除的文章信息

## 评论管理

### 获取文章评论
- **接口**: `GET /comments/article/{article_id}`
- **描述**: 获取指定文章的评论列表
- **权限**: 需要登录
- **查询参数**:
  - page: 页码
  - per_page: 每页数量
  - parent_id: 父评论ID（可选，用于获取回复）
- **响应**: 返回评论列表，包含回复信息

### 创建评论
- **接口**: `POST /comments`
- **描述**: 创建新评论或回复
- **权限**: 需要登录
- **请求体**:
  ```json
  {
    "content": "string",
    "article_id": 0,
    "parent_id": 0  // 可选，回复时需要
  }
  ```
- **响应**: 返回创建的评论信息

### 删除评论
- **接口**: `DELETE /comments/article/{article_id}/comment/{comment_id}`
- **描述**: 删除指定评论
- **权限**: 管理员或评论作者
- **响应**: 返回被删除的评论信息

## 系统相关

### 健康检查
- **接口**: `GET /health`
- **描述**: 检查系统服务状态
- **权限**: 无需认证
- **响应**:
  ```json
  {
    "status": "healthy",
    "timestamp": 1704521234,
    "version": "1.0.0",
    "service": "News API",
    "database": "connected"
  }
  ```

## 错误码说明

- 200: 成功
- 400: 请求参数错误
- 401: 未认证或认证失败
- 403: 权限不足
- 404: 资源不存在
- 500: 服务器内部错误

## 注意事项

1. 所有需要认证的接口都需要在请求头中携带 token：
   ```
   Authorization: Bearer <access_token>
   ```

2. 分页接口统一使用 page 和 per_page 参数

3. 评论系统支持二级评论（回复），不支持更深层级的嵌套回复

4. 文章标题不允许重复

5. 用户邮箱作为唯一标识，不允许重复注册

6. access_token 有效期为 30 分钟，refresh_token 有效期为 7 天
