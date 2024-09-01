from apscheduler.schedulers.background import BackgroundScheduler
from core.db import Session
from datetime import datetime

import crud

def expire_tokens(batch_size=100):
    with Session() as session:
        current_date = datetime.now()
        offset = 0

        while True:
            expired_tokens = crud.get_expired_active_tokens_with_usages_and_members(session, current_date, offset=offset, limit=batch_size)
            if not expired_tokens:
                break

            for token, usage, member in expired_tokens:
                token.is_active = False
                if member:
                    member.token_quantity -= usage.quantity
                session.delete(usage)
            session.commit()

            offset += batch_size