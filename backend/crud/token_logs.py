from datetime import datetime
from typing import Optional

from fastapi import Depends
from dependencies import get_db
from enums import LogType, UseType
from models import TokenLog
from schema.token_logs import TokenUsageLogRead, TokenLogRead


def get_token_usage_logs(session: Depends(get_db),
                         member_id: int,
                         start_date: Optional[datetime],
                         end_date: Optional[datetime],
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

def get_token_logs(session: Depends(get_db), log_type: LogType, start_date: Optional[datetime], end_date: Optional[datetime], department_id: int):
    query = session.query(TokenLog).filter(
        TokenLog.department_id == department_id,
        TokenLog.log_type == log_type)

    if start_date:
        query = query.filter(TokenLog.create_date >= start_date)

    if end_date:
        query = query.filter(TokenLog.create_date <= end_date)

    token_logs = query.all()

    return [TokenLogRead.from_orm(token_log) for token_log in token_logs]