from core.db import Base
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Date
from sqlalchemy.orm import relationship
from enums import Role

class Department(Base):
    __tablename__ = 'department'

    department_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    members = relationship("Member", back_populates="department")

class Member(Base):
    __tablename__ = 'member'

    member_id = Column(Integer, primary_key=True)
    login_id = Column(String(50), nullable=False)
    password = Column(String, nullable=False)
    name = Column(String(100), nullable=False)
    nickname = Column(String(100), nullable=False, unique=True)
    email = Column(String(255), nullable=False)
    role = Column(Enum(Role), nullable=False)
    token_quantity = Column(Integer, nullable=False)
    department_id = Column(Integer, ForeignKey('department.department_id'))
    department = relationship("Department", back_populates="members")
