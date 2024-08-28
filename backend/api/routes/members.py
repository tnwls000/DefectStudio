from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session, joinedload

import crud
from models import *
from dependencies import get_db
from schema import MemberCreate, MemberRead

app = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@app.post("/signup")
async def signup(member: MemberCreate, session: Session = Depends(get_db)):
    existing_member = crud.get_member_by_login_id(session, member.login_id)
    if existing_member:
        raise HTTPException(status_code=409, detail="이미 동일한 아이디의 회원이 존재합니다.")

    crud.create_member(session, member)

    return HTTPException(status_code=200, detail="회원가입이 완료되었습니다.")


# TODO : 회원정보 조회
@app.get("/members/{member_id}", response_model=MemberRead)
def get_user(member_id: int, session: Session = Depends(get_db)):
    member = session.query(Member).options(joinedload(Member.department)).filter(Member.member_id == member_id).one_or_none()
    return member

# TODO : 회원정보수정

# TODO : 회원삭제