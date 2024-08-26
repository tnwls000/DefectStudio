from jose import jwt
from sqlalchemy.util import deprecated
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from config import settings

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)

def hash_password(password):
    return bcrypt_context.hash(password)

def create_access_token(login_id: str, role: str):
    payload = {'login_id': login_id, 'role': role, 'category': 'access'}
    expiration_minutes = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({'exp': expiration_minutes})
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.ENCODE_ALGORITHM)

def create_refresh_token(login_id: str, role: str):
    payload = {'login_id': login_id, 'role': role, 'category': 'refresh'}
    expiration_minutes = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
    payload.update({'exp': expiration_minutes})
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.ENCODE_ALGORITHM)