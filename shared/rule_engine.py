import json
from pathlib import Path

DATA_PATH = Path(__file__).parent / "mock_db" / "records.json"

def load_all_records():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_record_by_khasra(khasra_no: str):
    records = load_all_records()
    for rec in records:
        if rec["khasra_no"] == khasra_no:
            return rec
    return None

def evaluate_entitlements_and_flags(record: dict) -> dict:
    # 1. MSP Calculation (CG Paddy Rate = Rs 3100/quintal)
    expected_msp = record["quintals_sold"] * 3100
    msp_gap = expected_msp - record["msp_received"]

    # 2. KCC Interest Subvention (4% if repaid on time, else 7%)
    expected_interest = 4.0 if record["repaid_on_time"] else 7.0
    subvention_missing = record["interest_charged_pct"] > expected_interest

    # 3. PMFBY Crop Insurance (Irrigated = Rs 66,000/ha, Unirrigated = Rs 45,000/ha)
    sum_insured_per_ha = 66000 if record["actual_irrigation"] == "Irrigated" else 45000
    expected_pmfby = int(record["area_hectares"] * sum_insured_per_ha * (record["crop_loss_pct"] / 100))
    pmfby_gap = expected_pmfby - record["pmfby_claim_received"]

    # 4. Discrepancy & Fraud Flags
    flags = []
    if record["actual_irrigation"] != record["bank_recorded_irrigation"]:
        flags.append("IRRIGATION_MISMATCH")
    if subvention_missing:
        flags.append("KCC_SUBVENTION_MISSING")
    if pmfby_gap > 0:
        flags.append("PMFBY_UNDERPAYMENT")
    if len(record["active_mortgages"]) > 1:
        flags.append("DUPLICATE_MORTGAGE_DETECTED")

    return {
        "khasra_no": record["khasra_no"],
        "owner_name": record["owner_name"],
        "village": record["village"],
        "district": record["district"],
        "expected_msp": expected_msp,
        "actual_msp": record["msp_received"],
        "msp_gap": msp_gap,
        "expected_interest_pct": expected_interest,
        "actual_interest_pct": record["interest_charged_pct"],
        "expected_pmfby": expected_pmfby,
        "actual_pmfby": record["pmfby_claim_received"],
        "pmfby_gap": pmfby_gap,
        "active_mortgages": record["active_mortgages"],
        "flags": flags
    }
