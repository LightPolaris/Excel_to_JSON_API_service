# Excel转JSON API服务

一个基于FastAPI的Web服务，用于将Excel文件转换为JSON格式数据。

## 功能特性

- 📊 支持Excel文件(.xlsx, .xls)转JSON格式
- 🌐 通过URL下载Excel文件进行处理
- 📝 完整的日志记录系统，支持按天轮换
- 🕒 北京时间(GMT+8)日志时间戳
- 🆔 每个请求分配唯一ID用于追踪
- 🧹 自动清理临时文件
- ⚡ 异步处理，高性能

## 技术栈

- **FastAPI**: 现代、快速的Web框架
- **Pandas**: Excel文件读取和数据处理
- **Uvicorn**: ASGI服务器
- **Requests**: HTTP请求库

## 安装依赖

```bash
pip install fastapi uvicorn pandas requests openpyxl xlrd
```

## 项目结构

```
8210/
├── main.py              # 主应用文件
├── fastapioutput/       # 临时文件存储目录
└── README.md           # 项目文档
```

## 配置说明

### 服务配置
- **端口**: 8000
- **主机**: 0.0.0.0 (监听所有网络接口)
- **日志目录**: `/fast_api/logs/8210/`
- **日志文件**: `xlsx2json.log`

### 日志配置
- 日志级别: INFO
- 日志轮换: 每天午夜
- 保留天数: 7天
- 时区: 北京时间(GMT+8)
- 格式: `年-月-日 时:分:秒 - 级别 - [请求ID] - 消息`

## API接口

### POST /xlsx2json

将Excel文件转换为JSON格式数据。

#### 请求参数

```json
{
  "file_url": "https://example.com/file.xlsx"
}
```

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| file_url | string | 是 | Excel文件的下载URL |

#### 响应格式

**成功响应 (200)**:
```json
{
  "success": true,
  "request_id": "a1b2c3d4",
  "processing_time": "1.23s",
  "rows_as_dict": [
    {
      "列1": "值1",
      "列2": "值2",
      "列3": "值3"
    },
    {
      "列1": "值4",
      "列2": "值5",
      "列3": "值6"
    }
  ]
}
```

**错误响应**:
```json
{
  "detail": "错误描述信息"
}
```

#### 响应字段说明

- `success`: 处理是否成功
- `request_id`: 唯一请求标识符
- `processing_time`: 处理耗时
- `rows_as_dict`: Excel数据转换后的JSON数组，每行数据作为一个对象

## 启动服务

### 开发环境

```bash
python main.py
```

### 生产环境

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 使用Docker (可选)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

## 使用示例

### cURL请求

```bash
curl -X POST "http://localhost:8000/xlsx2json" \
     -H "Content-Type: application/json" \
     -d '{"file_url": "https://example.com/sample.xlsx"}'
```

### Python请求

```python
import requests

url = "http://localhost:8000/xlsx2json"
data = {
    "file_url": "https://example.com/sample.xlsx"
}

response = requests.post(url, json=data)
result = response.json()
print(result)
```

### JavaScript请求

```javascript
fetch('http://localhost:8000/xlsx2json', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        file_url: 'https://example.com/sample.xlsx'
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

## 错误处理

服务包含完善的错误处理机制：

- **400**: 文件下载失败
- **500**: 服务器内部错误(如文件格式不支持、解析失败等)

所有错误都会记录到日志文件中，包含详细的错误信息和请求ID。

## 日志监控

日志文件位置: `/fast_api/logs/8210/xlsx2json.log`

### 查看实时日志

```bash
tail -f /fast_api/logs/8210/xlsx2json.log
```

### 日志格式示例

```
2024-07-24 14:30:25 - INFO - [a1b2c3d4] - 开始处理请求
2024-07-24 14:30:25 - INFO - [a1b2c3d4] - 开始下载要处理文件
2024-07-24 14:30:26 - INFO - [a1b2c3d4] - 文件下载完成，耗时: 0.85s
2024-07-24 14:30:26 - INFO - [a1b2c3d4] - 临时文件保存至: ./fastapioutput/abc123def456
2024-07-24 14:30:26 - INFO - [a1b2c3d4] - 请求处理完成，总耗时: 1.23s
```

## 性能特性

- 支持大型Excel文件处理
- 自动处理无穷值和NaN值(转换为null)
- 内存优化的文件处理流程
- 请求完成后自动清理临时文件

## 注意事项

1. 确保有足够的磁盘空间存储临时文件
2. 大文件处理可能需要较长时间，建议设置合适的超时时间
3. 服务启动前确保日志目录存在且有写入权限
4. Excel文件必须通过HTTP/HTTPS协议访问

## 故障排查

### 常见问题

1. **文件下载失败**
   - 检查URL是否正确
   - 确认文件服务器是否可访问

2. **日志写入失败**
   - 检查日志目录权限
   - 确认磁盘空间充足

3. **Excel解析失败**
   - 检查文件格式是否正确
   - 确认文件是否损坏

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持Excel转JSON功能
- 完整的日志系统
- 错误处理和临时文件清理
