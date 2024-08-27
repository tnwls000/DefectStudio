from typing import Annotated

from fastapi.security import OAuth2PasswordRequestForm
from fastapi.params import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
import crud
from core.security import verify_password, create_access_token, create_refresh_token
from dependencies import get_db
from fastapi import APIRouter

app = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

def authentication_member(username: str, password: str, session):
    member = crud.get_member_by_login_id(session, username)
    if not member:
        raise HTTPException(status_code=404, detail="해당 유저를 찾을 수 없습니다.")
    if not verify_password(password, member.password):
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")
    return member

@app.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                session: Session = Depends(get_db)):
    member = authentication_member(form_data.username, form_data.password, session)
    if not member:
        raise HTTPException(status_code=401, detail="아이디나 비밀번호가 일치하지 않습니다.")

    access_token = create_access_token(member.login_id)
    refresh_token = create_refresh_token(member.login_id)
    return {'token_type': 'bearer', 'access_token': access_token, 'refresh_token': refresh_token}
