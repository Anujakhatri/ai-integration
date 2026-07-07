from sqlalchemy.orm import Session
from app.models.claim import AuditLog

def log_upload(
    db: Session,
    username: str,
    filename: str,
    total: int,
    valid: int,
    invalid: int
):
    log = AuditLog(
        username=username,
        action="CSV_UPLOAD",
        filename=filename,
        total=total,
        valid=valid,
        invalid=invalid
    )
    db.add(log)
    db.commit()