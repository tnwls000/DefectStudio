from jose import jwt
from aioredis import Redis
from fastapi import Depends, HTTPException, status
from config import settings
from typing import Annotated
from sqlalchemy.util import deprecated
from passlib.context import CryptContext
from dependencies import get_redis, get_current_user
from datetime import datetime, timedelta, timezone

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def hash_password(password):
    return bcrypt_context.hash(password)


def create_access_token(login_id: str, role: str):
    payload = {'sub': login_id, 'role': role, 'category': 'access'}
    expiration_minutes = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({'exp': expiration_minutes})
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.ENCODE_ALGORITHM)


def create_refresh_token(login_id: str, role: str):
    payload = {'sub': login_id, 'role': role, 'category': 'refresh'}
    expiration_minutes = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
    payload.update({'exp': expiration_minutes})
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.ENCODE_ALGORITHM)


async def get_refresh_token(login_id: str, redis: Redis = Depends(get_redis)):
    token = await redis.get(login_id)
    return token


# TODO : 토큰 불러오기 + 토큰 유효성 검사
async def verify_refresh_token(token: str, user_dependency=Depends(get_current_user)):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ENCODE_ALGORITHM]) if token else None
        login_id: str = payload.get('sub')
        token_category: str = payload.get('category')

        if token_category != 'refresh':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Incorrect token type.')

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

