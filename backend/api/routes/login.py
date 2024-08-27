from typing import Annotated
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter
from alembic.util import status
from fastapi.params import Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException, Response, status, Request

import crud
from dependencies import get_db
from core.config import settings
from core.security import verify_password, create_access_token, create_refresh_token, decode_refresh_token

app = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@app.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                session: Session = Depends(get_db)):
    member = authentication_member(form_data.username, form_data.password, session)
    if not member:
        raise HTTPException(status_code=401, detail="아이디나 비밀번호가 일치하지 않습니다.")

    response = create_response_with_tokens(member.login_id)
    return response


@app.post("/reissue")
def reissue(request: Request):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token is missing")

    decoded_refresh_token = decode_refresh_token(refresh_token)
    login_id = decoded_refresh_token.get("login_id")

    response = create_response_with_tokens(login_id)
    return response


def authentication_member(username: str, password: str, session):
    member = crud.get_member_by_login_id(session, username)
    if not member:
        raise HTTPException(status_code=404, detail="해당 유저를 찾을 수 없습니다.")
    if not verify_password(password, member.password):
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다.")
    return member


def create_response_with_tokens(login_id: str):
    access_token = create_access_token(login_id)
    refresh_token = create_refresh_token(login_id)

    headers = {"Authorization": f"Bearer {access_token}"}
    response = Response(status_code=status.HTTP_200_OK, headers=headers)
    expiration_time = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        expires=expiration_time,
        httponly=True,
        secure=True,  # HTTPS
        samesite="Lax"
    )

    return response
