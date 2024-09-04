from fastapi import APIRouter
from sqlalchemy.orm import Session
from dependencies import get_db
from fastapi import HTTPException, Response, status, Depends
import crud

router = APIRouter(
    prefix="/departments",
    tags=["departments"]
)

@router.get("")
async def get_departments(session: Session = Depends(get_db)):
    return crud.get_departments(session)