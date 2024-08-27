from pydantic import BaseModel, EmailStr, Field
from enums import Role
import re

class MemberCreate(BaseModel):
    login_id: str = Field(..., min_length=3, max_length=50)
    password: str = Field(pattern=re.compile(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,20}$"))
    name: str = Field(..., min_length=3, max_length=100)
    nickname: str = Field(..., min_length=3, max_length=50, )
    email: EmailStr
    role: Role = Field(default=Role.department_member)
    department_id: int = Field(...)