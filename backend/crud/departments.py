from fastapi import Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from dependencies import get_db
from models import Department
from schema.departments import DepartmentRead

def get_departments(session: Depends(get_db)):
    departments = session.query(Department).all()
    department_reads = [DepartmentRead.from_orm(department) for department in departments]
    return department_reads

def get_department_by_name(session: Depends(get_db), name: str):
    # 부서 이름으로 조회
    return session.query(Department).filter(Department.name == name).first()

def create_department(session: Depends(get_db), name: str):
    # 부서 생성
    department = Department(name=name)
    try:
        session.add(department)
        session.commit()
        session.refresh(department)
        return department
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e.orig))