from models import Member
from fastapi import Depends
from schema import MemberCreate
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
        token_quantity=member.token_quantity,
        department_id=member.department_id
    )
    session.add(db_member)
    session.commit()
    session.refresh(db_member)
    return db_member
