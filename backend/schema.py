from pydantic import BaseModel, EmailStr, Field, field_validator

from enums import Role

class MemberCreate(BaseModel):
    login_id: str = Field(..., min_length=3, max_length=50)
    password: str = Field(pattern=r'^\d*$') # TODO: 정규식 수정
    name: str = Field(..., min_length=3, max_length=100)
    nickname: str = Field(..., min_length=3, max_length=50, )
    email: EmailStr
    role: Role = Field(default=Role.department_member)
    department_id: int = Field(...)