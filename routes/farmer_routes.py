from fastapi import APIRouter, HTTPException
from shared.rule_engine import get_record_by_khasra, evaluate_entitlements_and_flags

router = APIRouter()

@router.get("/check/{khasra_no:path}")
def check_farmer_entitlement(khasra_no: str):
    record = get_record_by_khasra(khasra_no)
    if not record:
        raise HTTPException(status_code=404, detail="Khasra number not found")
    return evaluate_entitlements_and_flags(record)
