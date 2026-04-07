# 初始化日志记录器
from os import environ
from loguru import logger
from datetime import datetime


def init_logger():
    logger.add(f"tree_{datetime.now().strftime('%Y-%m-%d')}.log", format=environ.get("LOG_FORMAT", "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"))
    logger.info("The application is starting up")