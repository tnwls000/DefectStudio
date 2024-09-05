from fastapi import Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from core.security import hash_password
from dependencies import get_db
from models import Member
from schema.members import MemberCreate
from typing import List

def get_member_by_login_id(session: Depends(get_db), login_id: str):
    return session.query(Member).filter(Member.login_id == login_id).first()

def get_members_by_department_id(session: Depends(get_db), department_id: int):
    return session.query(Member).filter(Member.department_id == department_id).all()

def get_members_by_member_ids(session: Depends(get_db), member_ids: List[int]):
    return session.query(Member).filter(Member.member_id.in_(member_ids)).all()

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

    try:
        session.add(db_member)
        session.commit()
        session.refresh(db_member)
        return db_member

    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e.orig))