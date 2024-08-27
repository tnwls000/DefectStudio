from typing import Annotated

from fastapi.security import OAuth2PasswordRequestForm
from fastapi.params import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
import crud
from core.security import verify_password
from dependencies import get_db
from fastapi import APIRouter

app = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

def authentication_member(username: str, password: str, session):
    member = crud.get_member_by_login_id(session, username)
    if not member:
        return False
    if not verify_password(password, member.password):
        return False
    return member

@app.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                session: Session = Depends(get_db)):
    member = authentication_member(form_data.username, form_data.password, session)
    if not member:
        raise HTTPException(status_code=401, detail="아이디나 비밀번호가 일치하지 않습니다.")

    # TODO: 토큰 로직 추가
    token = "example_token"  # TODO: 임시 토큰 (수정 필요)
    return {'access_token': token, 'token_type': 'bearer'}
