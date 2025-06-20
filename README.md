# URL短链接生成器

基于FastAPI和Pydantic的功能完整的URL短链接生成微服务。

## 功能特性

- 🔗 URL短链接生成和管理
- 🎯 自定义别名支持
- ⏰ 过期时间设置
- 📊 点击统计功能
- 🔄 URL重定向
- 🛠️ 完整的CRUD操作
- 📝 自动API文档
- ✅ 全面的测试覆盖

## 项目结构

```
norules/
├── main.py                 # FastAPI应用入口
├── requirements.txt        # 项目依赖
├── pytest.ini            # pytest配置
├── README.md              # 项目文档
├── models/                # 数据模型
│   ├── __init__.py
│   └── url_models.py
├── services/              # 服务层
│   ├── __init__.py
│   └── url_service.py
├── routers/               # API路由
│   ├── __init__.py
│   └── url_router.py
├── utils/                 # 工具函数
│   ├── __init__.py
│   ├── url_utils.py
│   └── storage.py
├── exceptions/            # 自定义异常
│   ├── __init__.py
│   └── url_exceptions.py
└── tests/                 # 测试文件
    ├── __init__.py
    ├── conftest.py
    ├── test_utils.py
    ├── test_storage.py
    ├── test_services.py
    └── test_api.py
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python main.py
```

或者使用uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 访问API文档

启动服务后，访问以下地址查看自动生成的API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 核心功能

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/shorten` | 创建短链接 |
| GET | `/{short_id}` | 重定向到原始URL |
| GET | `/api/urls` | 获取所有短链接 |
| GET | `/api/urls/{short_id}` | 获取短链接信息 |
| GET | `/api/urls/{short_id}/stats` | 获取统计信息 |
| PUT | `/api/urls/{short_id}` | 更新短链接 |
| DELETE | `/api/urls/{short_id}` | 删除短链接 |

### 系统功能

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/` | 欢迎页面 |
| GET | `/api/health` | 健康检查 |

## 使用示例

### 创建短链接

```bash
curl -X POST "http://localhost:8000/shorten" \
  -H "Content-Type: application/json" \
  -d '{
    "original_url": "https://www.example.com",
    "custom_alias": "example",
    "expires_at": "2024-12-31T23:59:59"
  }'
```

响应：
```json
{
  "id": "example",
  "original_url": "https://www.example.com",
  "short_url": "http://localhost:8000/example",
  "click_count": 0,
  "created_at": "2024-01-15T10:30:00",
  "expires_at": "2024-12-31T23:59:59",
  "is_active": true
}
```

### 访问短链接

直接在浏览器中访问 `http://localhost:8000/example` 将重定向到原始URL。

### 获取统计信息

```bash
curl "http://localhost:8000/api/urls/example/stats"
```

## 数据模型

### URLCreate (创建请求)
- `original_url`: 原始URL (必需)
- `custom_alias`: 自定义别名 (可选, 3-20字符)
- `expires_at`: 过期时间 (可选)

### URLResponse (响应模型)
- `id`: 短链接ID
- `original_url`: 原始URL
- `short_url`: 短链接URL
- `click_count`: 点击次数
- `created_at`: 创建时间
- `expires_at`: 过期时间
- `is_active`: 是否激活

### URLStats (统计模型)
- 包含所有URLResponse字段
- `last_accessed`: 最后访问时间

## 错误处理

服务定义了以下自定义异常：

- `URLNotFoundError` (404): 短链接不存在
- `URLExpiredError` (410): 短链接已过期
- `URLInactiveError` (410): 短链接已停用
- `InvalidURLError` (400): 无效的URL格式
- `DuplicateAliasError` (409): 别名已存在

## 运行测试

### 运行所有测试

```bash
pytest
```

### 运行特定测试文件

```bash
pytest tests/test_api.py
```

### 运行带覆盖率的测试

```bash
pytest --cov=. --cov-report=html
```

### 测试覆盖

项目包含全面的测试套件：

- **工具函数测试** (`test_utils.py`): 测试URL验证、ID生成等工具函数
- **存储层测试** (`test_storage.py`): 测试数据存储和检索功能
- **服务层测试** (`test_services.py`): 测试业务逻辑和异常处理
- **API测试** (`test_api.py`): 测试HTTP端点和响应

## 技术栈

- **FastAPI**: 现代化的Python Web框架
- **Pydantic**: 数据验证和序列化
- **Uvicorn**: ASGI服务器
- **Pytest**: 测试框架
- **HTTPx**: 异步HTTP客户端（测试用）

## 配置选项

### 存储

当前使用内存存储，在生产环境中可以替换为：
- Redis
- PostgreSQL
- MongoDB
- 其他数据库

### 自定义配置

可以通过修改以下文件进行配置：
- `utils/storage.py`: 存储层实现
- `services/url_service.py`: 业务逻辑
- `main.py`: 应用配置

## 部署

### Docker部署

创建 `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

构建并运行：

```bash
docker build -t url-shortener .
docker run -p 8000:8000 url-shortener
```

### 环境变量

可以设置以下环境变量：
- `HOST`: 服务器主机 (默认: 0.0.0.0)
- `PORT`: 服务器端口 (默认: 8000)
- `BASE_URL`: 短链接基础URL

## 性能考虑

- 使用异步编程提高并发性能
- 内存存储提供快速访问
- 可根据需要扩展到分布式存储
- 支持水平扩展

## 安全性

- URL验证防止恶意链接
- 自定义异常处理防止信息泄露
- CORS配置控制跨域访问
- 输入验证防止注入攻击

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！ 