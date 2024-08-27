import aioredis
from models import Member
from aioredis import Redis
from core.db import Session
from typing import Annotated
from jose import jwt, JWTError
from core.config import settings
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

# Access 토큰만을 리턴
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/login')


async def get_redis() -> Redis:
    redis = await aioredis.create_redis_pool((settings.REDIS_HOST, settings.REDIS_PORT))
    try:
        yield redis
    finally:
        redis.close()
        await redis.wait_closed()


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(session: Depends(get_db), token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ENCODE_ALGORITHM])
        login_id: str = payload.get('sub')
        token_category: str = payload.get('category')

        if not login_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')

        if token_category != 'access':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Incorrect token type.')

        member = session.query(Member).filter(Member.login_id == login_id).first()

        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Member does not exist.')

        return member

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')