from jose import jwt
from aioredis import Redis
from fastapi import Depends, HTTPException, status
from config import settings
from typing import Annotated
from sqlalchemy.util import deprecated
from passlib.context import CryptContext
from dependencies import get_redis, get_current_user
from datetime import datetime, timedelta, timezone

from models import Member

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


async def decode_refresh_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ENCODE_ALGORITHM])
        login_id: str = payload.get('sub')
        role: str = payload.get('role')
        token_category: str = payload.get('category')

        return {'login_id': login_id, 'role': role, 'token_category': token_category}

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

