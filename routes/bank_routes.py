from fastapi import APIRouter
from shared.rule_engine import load_all_records, evaluate_entitlements_and_flags

router = APIRouter()

@router.get("/verify-all")
def verify_all_applications():
    records = load_all_records()
    return [evaluate_entitlements_and_flags(r) for r in records]
