from fastapi import APIRouter
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, Response, status, Depends

import crud
from models import *
from dependencies import get_db, get_current_user
from schema import MemberCreate, MemberRead, MemberUpdate

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

    return Response(status_code=status.HTTP_200_OK, content="회원가입이 완료되었습니다.")


@app.get("/members/{member_id}", response_model=MemberRead)
def read_member_by_id(member_id: int, session: Session = Depends(get_db)):
    member = session.query(Member).options(joinedload(Member.department)).filter(Member.member_id == member_id).one_or_none()
    response = MemberRead.from_orm(member)
    return response

@app.patch("/members", response_model=MemberRead)
def update_member_me(request: MemberUpdate, member: Member = Depends(get_current_user), session: Session = Depends(get_db)):
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다.")

    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(member, key, value)

    session.commit()
    session.refresh(member)
    response = MemberRead.from_orm(member)
    return response


# TODO : 회원삭제