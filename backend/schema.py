from pydantic import BaseModel, EmailStr, Field
from enums import Role
import re
from models import *
from typing import Optional


class MemberCreate(BaseModel):
    login_id: str = Field(..., min_length=3, max_length=50)
    password: str = Field(pattern=re.compile(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,20}$"))
    name: str = Field(..., min_length=3, max_length=100)
    nickname: str = Field(..., min_length=3, max_length=50, )
    email: EmailStr
    role: Role = Field(default=Role.department_member)
    department_id: int = Field(...)


class MemberRead(BaseModel):
    login_id: str
    nickname: str
    email: EmailStr
    role: Role
    department_name: str

    @classmethod
    def from_orm(cls, member: 'Member') -> 'MemberRead':
        return cls(
            login_id=member.login_id,
            nickname=member.nickname,
            email=member.email,
            role=member.role,
            department_name=member.department.name if member.department else "null"
        )

class MemberUpdate(BaseModel):
    password: Optional[str] = Field(None, pattern=re.compile(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,20}$"))
    nickname: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None