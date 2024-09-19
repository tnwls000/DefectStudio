from datetime import datetime
from typing import Optional

from fastapi import Depends
from dependencies import get_db
from enums import LogType, UseType
from models import TokenLog
from schema.token_logs import TokenUsageLogRead, TokenLogRead, TokenLogCreate

def create_token_log(session: Depends(get_db), token_log: TokenLogCreate):
    db_token_log = TokenLog(
        create_date=datetime.today(),
        log_type=token_log.log_type,
        use_type=token_log.use_type,
        member_id=token_log.member_id,
        quantity=token_log.quantity,
        department_id=token_log.department_id,
        image_quantity=token_log.image_quantity,
        model=token_log.model
    )
    session.add(db_token_log)
    session.commit()
    session.refresh(db_token_log)
    return db_token_log

def get_token_usage_logs(session: Depends(get_db),
                         member_id: int,
                         start_date: datetime,
                         end_date: datetime,
                         use_type: UseType):
    query = session.query(TokenLog).filter(
                TokenLog.log_type == LogType.use,
                TokenLog.member_id == member_id,
                TokenLog.use_type == use_type)

    if start_date:
        query = query.filter(TokenLog.create_date >= start_date)

    if end_date:
        query = query.filter(TokenLog.create_date <= end_date)

    token_logs = query.all()

    return [TokenUsageLogRead.from_orm(token_log) for token_log in token_logs]

def get_token_logs(session: Depends(get_db), log_type: LogType, start_date: datetime, end_date: datetime, department_id: int):
    query = session.query(TokenLog).filter(
        TokenLog.department_id == department_id,
        TokenLog.log_type == log_type)

    if start_date:
        query = query.filter(TokenLog.create_date >= start_date)

    if end_date:
        query = query.filter(TokenLog.create_date <= end_date)

    token_logs = query.all()

    return [TokenLogRead.from_orm(token_log) for token_log in token_logs]