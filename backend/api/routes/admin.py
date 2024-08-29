from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from models import Member
from schema import TokenCreate
from enums import Role
import crud
from dependencies import get_db, get_current_user

from typing import List
from functools import wraps

app = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

# role decorator
def role_required(allowed_roles: List[Role]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: Member =Depends(get_current_user), **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(status_code=403, detail="권한이 없습니다.")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

@app.post("/token")
@role_required([Role.super_admin]) # only super_admin can issue token
async def issue_token(token: TokenCreate, session: Session = Depends(get_db)):
    crud.create_token(session, token)
    return HTTPException(status_code=201, detail="토큰이 발급되었습니다.")

