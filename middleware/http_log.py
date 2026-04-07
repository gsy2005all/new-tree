from fastapi import Request
from loguru import logger

def http_log_M(request: Request):
    logger.info(f"HTTP Request: {request.method} {request.url}")
    return request