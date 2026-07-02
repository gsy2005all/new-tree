"""
打卡证据图片上传。

流程：
  前端选图 -> POST /uploads/proof (multipart)
           -> 后端校验类型/大小 + 用 Pillow 验证是真图片 + 压缩
           -> 保存到 static/uploads/，返回可访问 URL
  前端拿到 URL 后，作为 day_proof 调 /days/add 打卡。

读取：图片直接挂在 /static 下由 FastAPI StaticFiles 提供，
      另外提供 GET /uploads/{filename} 兜底读取（need.md 要求）。
"""
import time
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from middleware.check_auth import check_auth_M
from middleware.http_log import http_log_M
from modules.tree_app_res import TreeAppHttpResponse
from utils.config import get_settings

upload_router = APIRouter(prefix="/uploads", dependencies=[Depends(http_log_M), Depends(check_auth_M)])


def _verify_and_compress(data: bytes, out_path):
    """用 Pillow 验证是否为真实图片，并压缩保存为 JPEG（兼顾体积与兼容性）。"""
    from io import BytesIO

    from PIL import Image

    try:
        img = Image.open(BytesIO(data))
        img.load()  # 强制解码，损坏图会在这里抛异常
    except Exception:
        raise HTTPException(400, "无法识别的图片文件或图片已损坏")

    # 转 RGB（PNG 透明通道等存成 JPEG 需要白底）
    if img.mode in ("RGBA", "P", "LA"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.convert("RGBA").split()[-1])
        img = background
    else:
        img = img.convert("RGB")

    # 限制最长边，避免超大图
    max_side = 1600
    if max(img.size) > max_side:
        img.thumbnail((max_side, max_side))

    img.save(out_path, "JPEG", quality=85, optimize=True)


@upload_router.post("/proof", response_model=TreeAppHttpResponse)
def upload_proof(file: UploadFile = File(...)):
    settings = get_settings()
    raw = file.file.read()
    if len(raw) == 0:
        raise HTTPException(400, "上传文件为空")
    if len(raw) > settings.upload_max_bytes:
        raise HTTPException(
            413, f"文件过大，最大 {settings.upload_max_bytes // 1024 // 1024}MB"
        )
    if file.content_type not in settings.upload_allowed_types:
        raise HTTPException(
            415, f"仅支持 {', '.join(settings.upload_allowed_types)}"
        )

    settings.upload_path.mkdir(parents=True, exist_ok=True)
    # 用 uuid + 时间戳 命名，避免冲突与路径遍历风险
    filename = f"{int(time.time())}_{uuid.uuid4().hex}.jpg"
    out_path = settings.upload_path / filename

    _verify_and_compress(raw, out_path)

    # 由于 static 已挂在 /static 下，uploads 子目录访问路径为：
    url = f"/static/uploads/{filename}"
    return TreeAppHttpResponse(
        message="上传成功", data=[{"url": url, "filename": filename}], total=1
    )


@upload_router.get("/{filename}")
def read_upload(filename: str):
    """兜底读取接口：直接返回上传的原图（满足 need.md 的读取证据图片需求）。"""
    settings = get_settings()
    # 只允许文件名，禁止任何路径穿越
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(400, "非法文件名")
    path = settings.upload_path / filename
    if not path.is_file():
        raise HTTPException(404, "文件不存在")
    return FileResponse(path)
