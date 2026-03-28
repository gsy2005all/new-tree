from fastapi import APIRouter

user_router = APIRouter(prefix="/users")

@user_router.post("/add")
def add_user():
    return {"你好":"gsy"}
