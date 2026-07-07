from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth.jwt_handler import require_admin, get_current_user
from app.models.claim import Claim, ClaimSchema, AuditLog
from pydantic import ValidationError
import csv
import io
from app.audit.logger import log_upload
router = APIRouter(prefix="/claims", tags=["Claims"])
from datetime import date


@router.post("/upload")
def upload_claims(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)  # admin only!
):

    if file.filename is None:
        raise HTTPException(status_code=400, detail="No file provided")

    filename = file.filename
    # 1. CSV file ho ki hoina check
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files accepted")

    # 2. File content read garo
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))

    valid_count = 0
    invalid_count = 0
    errors = []

    # 3. Har row validate + store
    for row_num, row in enumerate(reader, start=2):  # start=2 header skip
        try:
            # Pydantic le validate garchha
            claim_data = ClaimSchema(
                member_id=row["member_id"],
                icd10_code=row["icd10_code"],
                cpt_code=row["cpt_code"],
                paid_amount=float(row["paid_amount"]),
                date_of_service=date.fromisoformat(row["date_of_service"])
            )

            # DB ma store garchha
            db_claim = Claim(
                member_id=claim_data.member_id,
                icd10_code=claim_data.icd10_code,
                cpt_code=claim_data.cpt_code,
                paid_amount=claim_data.paid_amount,
                date_of_service=claim_data.date_of_service
            )
            db.add(db_claim)
            valid_count += 1

        except (ValidationError, ValueError, KeyError) as e:
            invalid_count += 1
            errors.append({
                "row": row_num,
                "data": row,
                "error": str(e)
            })

    # 4. Sabai valid rows ek palta commit
    db.commit()

    log_upload(
        db=db,
        username=current_user["username"],
        filename=filename,
        total=valid_count + invalid_count,
        valid=valid_count,
        invalid=invalid_count
    )

    # 5. Summary return
    return {
        "uploaded_by": current_user["username"],
        "total_records": valid_count + invalid_count,
        "valid": valid_count,
        "invalid": invalid_count,
        "errors": errors
    }


@router.get("/")
def get_claims(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    claims = db.query(Claim).all()
    return {"claims": claims, "total": len(claims)}

@router.get("/audit-logs")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)  # admin only!
):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
    return {"audit_logs": logs, "total": len(logs)}
