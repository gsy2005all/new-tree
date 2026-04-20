import os
from fastapi import APIRouter, Depends
from middleware.http_log import http_log_M
from modules.tree_app_res import TreeAppHttpResponse 

app_router = APIRouter(prefix="/app", dependencies=[Depends(http_log_M)])

@app_router.get("/version", response_model=TreeAppHttpResponse)
def get_version():
    return TreeAppHttpResponse(message="The version has been queried successfully", data=[os.getenv("VERSION")], total=1)
