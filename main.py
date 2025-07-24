from typing import Optional
import time
from datetime import datetime
import tempfile
import logging
import logging.handlers
import uuid
import os

from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import requests

import pandas as pd


port = 8000
logname = "xlsx2json.log"
glog_dir = "/fast_api/logs/8210/"

# pdf解析 和 签章识别 接口  ppstructe
class BeijingFormatter(logging.Formatter):
    """自定义Formatter, 将时间转换为GMT+8时区（通过直接加8小时）"""
    
    def formatTime(self, record, datefmt=None):
        """
        重写时间格式化方法
        record: 日志记录对象
        datefmt: 日期格式(可选)
        """
        # 原始时间戳（UTC时间）加上8小时（28800秒）
        beijing_timestamp = record.created + 8 * 3600
        # 将调整后的时间戳转换为本地时间（注意：这里没有时区信息，只是时间数值调整）
        beijing_time = datetime.fromtimestamp(beijing_timestamp)
        # 应用自定义日期格式
        if datefmt:
            return beijing_time.strftime(datefmt)
        else:
            return beijing_time.isoformat()

# 初始化日志系统
def setup_logging():
    """配置日志系统"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 创建日志目录
    log_dir = glog_dir
    os.makedirs(log_dir, exist_ok=True)

    # 日志格式
    formatter = BeijingFormatter(
        "%(asctime)s - %(levelname)s - [%(request_id)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"  # 自定义时间格式
    )

    # 文件处理器（每天轮换，保留7天）
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=os.path.join(log_dir, logname),
        when="midnight",
        backupCount=7,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

path = './fastapioutput' 
if not os.path.exists(path):
    # 如果是目录，可以创建
    os.makedirs(path, exist_ok=True)

class RequestIdFilter(logging.Filter):
    """为日志记录添加request_id"""
    def filter(self, record):
        if not hasattr(record, 'request_id'):
            record.request_id = "SYSTEM"
        return True

# 应用日志过滤器
for handler in logging.getLogger().handlers:
    handler.addFilter(RequestIdFilter())


@app.post("/xlsx2json")
async def pdf_to_image(
    file_url: str = Body(..., embed=True),
    ):

    request_id = str(uuid.uuid4())[:8]
    file_path = None
    try:
        # 记录请求开始
        logger.info("开始处理请求", extra={"request_id": request_id})
        start_time = time.time()

        # 下载PDF
        logger.info("开始下载要处理文件", extra={"request_id": request_id})
        down_start = time.time()
        response = requests.get(file_url)
        if response.status_code != 200:
            logger.error("文件下载失败，状态码: %d", response.status_code, extra={"request_id": request_id})
            raise HTTPException(status_code=400, detail=f"{file_url}下载失败")
        dl_time = time.time() - down_start
        logger.info("文件下载完成，耗时: %.2fs", dl_time, extra={"request_id": request_id})

        # 保存临时文件
        file_path = f"./fastapioutput/{uuid.uuid4().hex}"
        with open(file_path, "wb") as f:
            f.write(response.content)
        logger.info("临时文件保存至: %s", file_path, extra={"request_id": request_id})

        # TODO
        df = pd.read_excel(file_path)
        # 将每一行转换为字典，并组成一个列表
        # rows_as_dict = df.to_dict(orient='records')
        rows_as_dict = df.replace([float('inf'), -float('inf'), float('nan')], None).to_dict(orient='records')

        total_time = time.time() - start_time
        logger.info("请求处理完成，总耗时: %.2fs", total_time, extra={"request_id": request_id})
        return JSONResponse({
            "success": True,
            "request_id": request_id,
            "processing_time": f"{total_time:.2f}s",
            "rows_as_dict": rows_as_dict
        })

    except HTTPException as he:
        logger.error(f"请求解析的文件 URL为：{file_url}")
        logger.error("HTTP异常: %s", he.detail, extra={"request_id": request_id})
        raise
    except Exception as e:
        logger.error(f"请求解析的文件 URL为：{file_url}")
        logger.exception("处理过程中发生未预期错误", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.debug("临时文件已删除: %s", file_path, extra={"request_id": request_id})
            except Exception as e:
                logger.error("文件删除失败: %s", str(e), extra={"request_id": request_id})




if __name__ == "__main__":
    logger.info("服务启动中...", extra={"request_id": "SYSTEM"})
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_config=None  # 禁用uvicorn默认日志
    )