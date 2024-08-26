from pydantic import BaseModel, EmailStr
from enums import Role

class MemberCreate(BaseModel):
    login_id: str
    password: str
    name: str
    nickname: str
    email: EmailStr
    role: Role
    token_quantity: int
    department_id: int