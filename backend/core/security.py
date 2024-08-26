from passlib.context import CryptContext
from datetime import datetime, timedelta

from sqlalchemy.util import deprecated

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)

def hash_password(password):
    return bcrypt_context.hash(password)