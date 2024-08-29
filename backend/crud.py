from datetime import datetime

from models import Member, Token
from fastapi import Depends
from schema import MemberCreate, TokenCreate
from dependencies import get_db
from core.security import hash_password

def get_member_by_login_id(session: Depends(get_db), login_id: str):
    return session.query(Member).filter(Member.login_id == login_id).first()

def create_member(session: Depends(get_db), member: MemberCreate):
    hashed_password = hash_password(member.password)
    db_member = Member(
        login_id=member.login_id,
        password=hashed_password,
        name=member.name,
        nickname=member.nickname,
        email=member.email,
        role=member.role,
        department_id=member.department_id
    )
    session.add(db_member)
    session.commit()
    session.refresh(db_member)
    return db_member

def create_token(session: Depends(get_db), token: TokenCreate):
    db_token = Token(
        start_date=datetime.today(),
        end_date=token.end_date,
        origin_quantity=token.quantity,
        remain_quantity=token.quantity,
        is_active=True, # 토큰 발급 시 활성화되어 발급됨
        department_id=token.department_id
    )

    session.add(db_token)
    session.commit()
    session.refresh(db_token)
    return db_token