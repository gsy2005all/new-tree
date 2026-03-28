# 初始化日志记录器
from os import environ
from loguru import logger


def init_logger():
    logger.add("file.log", format=environ.get("LOG_FORMAT", "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"))
    logger.info("The application is starting up")