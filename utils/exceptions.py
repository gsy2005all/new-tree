"""
全局异常处理：把未被路由捕获的异常统一包装成项目约定的响应格式，
避免直接把 500 + 堆栈泄露给前端。
"""
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception):
        logger.error(f"未处理异常 {request.method} {request.url.path}: {exc}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "message": "服务器内部错误，请稍后重试",
                "data": [],
                "total": 0,
                # FastAPI 的 HTTPException 由其自身处理；这里只兜底其它异常
            },
        )
