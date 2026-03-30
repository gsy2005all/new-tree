from fastapi import APIRouter

from db.db import SessionDep
from modules.user import User

user_router = APIRouter(prefix="/users")

@user_router.post("/add", response_model=User)
def add_user(x: User, session: SessionDep):
    session.add(x)
    session.commit()
    session.refresh(x)
    return x
