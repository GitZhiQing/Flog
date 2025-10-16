# Flog 博客系统 API 接入文档

## 基本信息

- **API 基础路径**: `/api`
- **版本**: v0.1.0
- **认证方式**: Basic Auth (部分接口需要)
- **响应格式**: JSON

## 通用响应格式

所有 API 响应都遵循统一的格式：

```json
{
  "code": 200,
  "msg": "success",
  "data": {} // 具体数据
}
```

分页响应格式：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "total": 100, // 总记录数
    "page": 1, // 当前页码
    "size": 10, // 每页大小
    "items": [] // 当前页数据列表
  }
}
```

## API 端点

### 1. 系统信息

#### 获取系统信息

- **URL**: `GET /`
- **描述**: 获取 API 基本信息和平台配置
- **认证**: 无需认证
- **响应示例**:

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "api": {
      "name": "Seek2Game API",
      "environment": "development",
      "host": "127.0.0.1",
      "port": 8080,
      "api_prefix": "/api",
      "version": "0.1.0"
    },
    // 平台配置信息
    "platform": {
      "name": "Flog",
      "description": "Fast Log Your Life~",
      "footer": "&copy; 2025 QING"
    }
  }
}
```

### 2. 文章管理

#### 获取文章列表

- **URL**: `GET /api/posts`
- **描述**: 获取文章列表，支持分页和状态筛选
- **认证**: 可选（获取隐藏文章需要认证）
- **查询参数**:
  - `page`: 页码，默认 1，最小 1
  - `size`: 每页数量，默认 10，范围 1-100
  - `status`: 文章状态，可选值：`show`（默认）、`hide`
- **响应示例**:

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "total": 50,
    "page": 1,
    "size": 10,
    "items": [
      {
        "slug": "example-post",
        "title": "示例文章",
        "category": "技术",
        "status": "show",
        "view_count": 100,
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
      }
    ]
  }
}
```

#### 根据 slug 获取文章详情

- **URL**: `GET /api/posts/slug/{post_slug}`
- **描述**: 通过文章 slug 获取文章内容和元数据
- **认证**: 可选（获取隐藏文章需要认证）
- **路径参数**:
  - `post_slug`: 文章 slug
- **响应示例**:

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "slug": "example-post",
    "title": "示例文章",
    "category": "技术",
    "content": "# 文章内容\n\n这里是文章的Markdown内容..."
  }
}
```

#### 更新文章状态

- **URL**: `PATCH /api/posts/slug/{post_slug}/status`
- **描述**: 更新文章的显示状态
- **认证**: 需要
- **路径参数**:
  - `post_slug`: 文章 slug
- **查询参数**:
  - `status`: 文章状态，可选值：`show`、`hide`
- **响应示例**:

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "slug": "example-post",
    "title": "示例文章",
    "category": "技术",
    "status": "show",
    "view_count": 100,
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00"
  }
}
```

#### 同步文章到数据库

- **URL**: `POST /api/posts/actions/sync`
- **描述**: 将 Markdown 文件同步到数据库
- **认证**: 需要
- **响应示例**:

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "created": 5,
    "updated": 3,
    "deleted": 0
  }
}
```

### 3. 评论管理

#### 获取评论列表

- **URL**: `GET /api/comments`
- **描述**: 获取评论列表，支持分页和筛选
- **认证**: 可选（获取隐藏评论需要认证）
- **查询参数**:
  - `page`: 页码，默认 1，最小 1
  - `size`: 每页数量，默认 10，范围 1-100
  - `post_slug`: 文章 slug 筛选（可选）
  - `status`: 评论状态，可选值：`show`（默认）、`hide`
- **响应示例**:

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "total": 30,
    "page": 1,
    "size": 10,
    "items": [
      {
        "id": 1,
        "content": "这是一条评论",
        "author_name": "张三",
        "author_email": "zhangsan@example.com",
        "author_link": "https://zhangsan.com",
        "post_slug": "example-post",
        "parent_id": null,
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
      }
    ]
  }
}
```

#### 创建评论

- **URL**: `POST /api/comments`
- **描述**: 创建新评论
- **认证**: 无需认证
- **请求体**:

```json
{
  "content": "这是一条评论",
  "author_name": "张三",
  "author_email": "zhangsan@example.com",
  "author_link": "https://zhangsan.com",
  "post_slug": "example-post",
  "parent_id": null
}
```

- **响应示例**:

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 1,
    "content": "这是一条评论",
    "author_name": "张三",
    "author_email": "zhangsan@example.com",
    "author_link": "https://zhangsan.com",
    "post_slug": "example-post",
    "parent_id": null,
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00"
  }
}
```

#### 更新评论状态

- **URL**: `PATCH /api/comments/{comment_id}/status`
- **描述**: 更新评论的显示状态
- **认证**: 需要
- **路径参数**:
  - `comment_id`: 评论 ID
- **查询参数**:
  - `status`: 评论状态，可选值：`show`、`hide`
- **响应示例**:

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 1,
    "content": "这是一条评论",
    "author_name": "张三",
    "author_email": "zhangsan@example.com",
    "author_link": "https://zhangsan.com",
    "post_slug": "example-post",
    "parent_id": null,
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00"
  }
}
```

#### 删除评论

- **URL**: `DELETE /api/comments/{comment_id}`
- **描述**: 删除指定评论
- **认证**: 需要
- **路径参数**:
  - `comment_id`: 评论 ID
- **响应示例**:

```json
{
  "code": 200,
  "msg": "success",
  "data": null
}
```

### 4. 分类管理

#### 获取分类列表

- **URL**: `GET /api/categories`
- **描述**: 获取所有文章分类
- **认证**: 无需认证
- **响应示例**:

```json
{
  "code": 200,
  "msg": "success",
  "data": ["技术", "生活", "随笔"]
}
```

#### 根据分类获取文章列表

- **URL**: `GET /api/categories/{category_name}/posts`
- **描述**: 获取指定分类下的可见文章列表
- **认证**: 无需认证
- **路径参数**:
  - `category_name`: 分类名称
- **查询参数**:
  - `page`: 页码，默认 1
  - `size`: 每页数量，默认 10
- **响应示例**:

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "total": 20,
    "page": 1,
    "size": 10,
    "items": [
      {
        "slug": "example-post",
        "title": "示例文章",
        "category": "技术",
        "status": "show",
        "view_count": 100,
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
      }
    ]
  }
}
```

## 错误处理

API 使用标准 HTTP 状态码表示请求结果：

- `200`: 请求成功
- `400`: 请求参数错误
- `401`: 未认证
- `403`: 权限不足
- `404`: 资源不存在
- `500`: 服务器内部错误

错误响应格式：

```json
{
  "code": 400,
  "msg": "错误描述",
  "data": null
}
```

## 认证

部分 API 需要 Basic Auth 认证。认证信息在请求头中提供：

```
Authorization: Basic <base64(username:password)>
```

认证信息在环境变量中配置：

- `BASIC_AUTH_USERNAME`: 用户名
- `BASIC_AUTH_PASSWORD`: 密码

## 状态枚举

### 文章状态 (PostStatusEnum)

- `show`: 可见
- `hide`: 隐藏

### 评论状态 (CommentStatusEnum)

- `show`: 可见
- `hide`: 隐藏

## 示例代码

### JavaScript (Fetch API)

```javascript
// 获取文章列表
fetch("/api/posts?page=1&size=10")
  .then((response) => response.json())
  .then((data) => console.log(data));

// 创建评论
fetch("/api/comments", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    content: "这是一条评论",
    author_name: "张三",
    post_slug: "example-post",
  }),
})
  .then((response) => response.json())
  .then((data) => console.log(data));

// 需要认证的请求
fetch("/api/posts/actions/sync", {
  method: "POST",
  headers: {
    Authorization: "Basic " + btoa("username:password"),
  },
})
  .then((response) => response.json())
  .then((data) => console.log(data));
```

### Python (requests)

```python
import requests
import base64

# 获取文章列表
response = requests.get('/api/posts', params={'page': 1, 'size': 10})
print(response.json())

# 创建评论
response = requests.post('/api/comments', json={
    'content': '这是一条评论',
    'author_name': '张三',
    'post_slug': 'example-post'
})
print(response.json())

# 需要认证的请求
credentials = base64.b64encode(b'username:password').decode('utf-8')
headers = {'Authorization': f'Basic {credentials}'}
response = requests.post('/api/posts/actions/sync', headers=headers)
print(response.json())
```
