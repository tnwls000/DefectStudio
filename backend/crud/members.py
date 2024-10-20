from datetime import datetime

from fastapi import Depends, HTTPException
from sqlalchemy import cast, Date
from sqlalchemy.exc import SQLAlchemyError
from core.config import settings
from core.security import hash_password
from dependencies import get_db
from models import Member
from schema.members import MemberCreate, MemberRead
from typing import List
from enums import Role
from .departments import get_department_by_name, create_department

def get_all_members(session: Depends(get_db)):
    return session.query(Member).all()

def get_member_by_login_id(session: Depends(get_db), login_id: str):
    return session.query(Member).filter(Member.login_id == login_id).first()

def get_members_by_department_id(session: Depends(get_db), department_id: int):
    return session.query(Member).filter(Member.department_id == department_id).all()

def get_member_by_member_id(session: Depends(get_db), member_id: int):
    return session.query(Member).filter(Member.member_id == member_id).first()

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
        role=Role.guest,
        department_id=member.department_id
    )

    try:
        session.add(db_member)
        session.commit()
        session.refresh(db_member)
        return db_member

    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e.orig))

def create_admin_account():
    # 세션을 수동으로 가져오기
    db = next(get_db())

    try:
        # "System Management" 부서가 있는지 확인
        department = get_department_by_name(db, 'System Management')

        if not department:
            # 부서가 없으면 생성
            department = create_department(db, 'System Management')

        # admin 계정이 이미 있는지 확인
        member = get_member_by_login_id(db, 'admin')

        if member is None:
            # admin 계정 생성과 역할 설정을 동시에 처리
            member = Member(
                login_id=settings.ADMIN_ID,
                password=settings.ADMIN_PASSWORD,  # 비밀번호는 나중에 해시 처리 필요
                name='admin',
                nickname='admin',
                email='admin@domain.com',
                role=Role.super_admin,  # 역할 설정
                department_id=department.department_id
            )

            print("Admin account created.")
        else:
            member.role = Role.super_admin
            print("Admin account already exists.")

        # 새로 생성한 admin 계정을 데이터베이스에 추가
        db.add(member)
        db.commit()  # 변경 사항을 데이터베이스에 반영
        db.refresh(member)  # 변경된 정보를 다시 가져오기

    finally:
        # 세션 닫기
        db.close()
