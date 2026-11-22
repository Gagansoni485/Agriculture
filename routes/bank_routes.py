"""Bank View router.

This file is edited ONLY by the bank-view teammate. It builds on the shared
rule engine (single source of truth for entitlement math and fraud flags) and
adds bank-side business logic:

  * Duplicate-mortgage filtering (land pledged to more than one bank).
  * District bottleneck aggregations (where policy leakage is concentrated).
  * KCC loan-approval decisions (eligible amount, status, reasons).

Mounted by main.py under the /api/bank prefix, so every route below is reached
as /api/bank/<path>.
"""

import fastapi
import pydantic

from shared.rule_engine import load_all_records, evaluate_entitlements_and_flags

router = fastapi.APIRouter()


# ---------------------------------------------------------------------------
# Bank-view policy constants (KCC scale of finance)
# ---------------------------------------------------------------------------
# Per-hectare eligible limit (Rs), by actual irrigation status of the plot.
KCC_LIMIT_PER_HA = {
    "Irrigated": 50000,
    "Unirrigated": 30000,
}
# Hard cap on a single KCC sanction (Rs).
KCC_MAX_LOAN = 200000


# ---------------------------------------------------------------------------
# Request schema for the loan-application endpoint
# ---------------------------------------------------------------------------
class LoanApplication(pydantic.BaseModel):
    requested_amount: float = pydantic.Field(
        ..., ge=0, description="Loan amount requested by the farmer (Rs)."
    )
    tenure_years: int | None = pydantic.Field(
        default=1, ge=1, le=7, description="Repayment tenure in years (1-7)."
    )


# ---------------------------------------------------------------------------
# Internal helpers (kept local to the bank view so shared/ stays untouched)
# ---------------------------------------------------------------------------
def _eligible_kcc_limit(record: dict) -> float:
    """Maximum KCC loan the farmer is eligible for, based on area & irrigation."""
    per_ha = KCC_LIMIT_PER_HA.get(
        record["actual_irrigation"], KCC_LIMIT_PER_HA["Unirrigated"]
    )
    limit = record["area_hectares"] * per_ha
    return float(min(limit, KCC_MAX_LOAN))


def _total_active_mortgage(record: dict) -> float:
    """Sum of all currently active mortgages on the plot."""
    return float(
        sum(
            m["amount"]
            for m in record["active_mortgages"]
            if m.get("status", "Active") == "Active"
        )
    )


def _loan_decision(record: dict, requested_amount: float | None = None) -> dict:
    """Compute a KCC loan-approval decision for a single record.

    Policy rules:
      * DUPLICATE_MORTGAGE_DETECTED -> REVIEW (land pledged to multiple banks)
      * IRRIGATION_MISMATCH         -> REVIEW (irrigation status disputed)
      * KCC_SUBVENTION_MISSING      -> REVIEW (existing interest overcharged)
      * Existing exposure >= eligible limit (no other review flag) -> DECLINED
      * Otherwise -> APPROVED

    If a specific requested_amount is supplied, the approved amount is capped
    at the eligible limit.
    """
    evaluation = evaluate_entitlements_and_flags(record)
    flags = evaluation["flags"]
    eligible = _eligible_kcc_limit(record)
    existing_exposure = _total_active_mortgage(record)

    status = "APPROVED"
    reasons = []

    # --- Review-triggering flags -------------------------------------------------
    if "DUPLICATE_MORTGAGE_DETECTED" in flags:
        status = "REVIEW"
        reasons.append(
            "Plot is already mortgaged to more than one bank; manual verification "
            "required before a fresh sanction."
        )
    if "IRRIGATION_MISMATCH" in flags:
        status = "REVIEW"
        reasons.append(
            "Bank-recorded irrigation differs from the actual status; field "
            "verification required."
        )
    if "KCC_SUBVENTION_MISSING" in flags:
        status = "REVIEW"
        reasons.append(
            "Existing KCC interest exceeds the subvention rate; correct the "
            "running loan before sanctioning a new one."
        )

    # --- Exposure vs eligible limit ---------------------------------------------
    overexposed = existing_exposure >= eligible and existing_exposure > 0
    if overexposed:
        if status == "APPROVED":
            status = "DECLINED"
            reasons.append(
                f"Existing mortgage exposure (Rs {existing_exposure:,.0f}) meets or "
                f"exceeds the eligible KCC limit (Rs {eligible:,.0f})."
            )
        else:
            # Already heading to manual review; surface exposure as information.
            reasons.append(
                f"Existing mortgage exposure (Rs {existing_exposure:,.0f}) also "
                f"meets/exceeds the eligible limit (Rs {eligible:,.0f}); review "
                f"exposure before sanction."
            )

    # --- Approved amount --------------------------------------------------------
    if requested_amount is not None:
        if status == "APPROVED":
            if requested_amount <= eligible:
                approved_amount = float(requested_amount)
            else:
                approved_amount = eligible
                status = "APPROVED_WITH_CAP"
                reasons.append(
                    f"Requested Rs {requested_amount:,.0f} exceeds the eligible "
                    f"limit; approving up to Rs {eligible:,.0f}."
                )
        else:
            approved_amount = 0.0
    else:
        approved_amount = eligible if status == "APPROVED" else 0.0

    return {
        "khasra_no": record["khasra_no"],
        "owner_name": record["owner_name"],
        "village": record["village"],
        "district": record["district"],
        "crop": record["crop"],
        "area_hectares": record["area_hectares"],
        "actual_irrigation": record["actual_irrigation"],
        "eligible_loan_amount": eligible,
        "existing_mortgage_exposure": existing_exposure,
        "active_mortgages": record["active_mortgages"],
        "flags": flags,
        "decision": status,
        "approved_amount": approved_amount,
        "requested_amount": requested_amount,
        "reasons": reasons,
    }


# ---------------------------------------------------------------------------
# Existing endpoint (kept intact)
# ---------------------------------------------------------------------------
@router.get("/verify-all")
def verify_all_applications():
    """Return entitlements and fraud flags for every record on file."""
    records = load_all_records()
    return [evaluate_entitlements_and_flags(r) for r in records]


# ---------------------------------------------------------------------------
# 1. Duplicate-mortgage filters
# ---------------------------------------------------------------------------
@router.get("/duplicate-mortgages")
def duplicate_mortgages(
    district: str | None = fastapi.Query(
        default=None, description="Filter to a single district (e.g. Dhamtari)."
    ),
    bank: str | None = fastapi.Query(
        default=None, description="Filter to cases involving a specific bank."
    ),
):
    """Return every plot carrying more than one active mortgage (duplicate
    financing risk), optionally narrowed by district and/or participating bank.
    """
    records = load_all_records()
    results = []
    for rec in records:
        mortgages = rec["active_mortgages"]
        if len(mortgages) <= 1:
            continue
        if district is not None and rec["district"] != district:
            continue
        if bank is not None and not any(m["bank"] == bank for m in mortgages):
            continue
        evaluation = evaluate_entitlements_and_flags(rec)
        results.append(
            {
                "khasra_no": rec["khasra_no"],
                "owner_name": rec["owner_name"],
                "village": rec["village"],
                "district": rec["district"],
                "mortgage_count": len(mortgages),
                "total_mortgage_amount": sum(m["amount"] for m in mortgages),
                "mortgages": mortgages,
                "flags": evaluation["flags"],
            }
        )

    total_exposure = sum(r["total_mortgage_amount"] for r in results)
    return {
        "count": len(results),
        "total_duplicate_exposure": total_exposure,
        "records": results,
    }


# ---------------------------------------------------------------------------
# 2. District bottleneck aggregations
# ---------------------------------------------------------------------------
@router.get("/district-bottlenecks")
def district_bottlenecks():
    """Aggregate entitlement gaps and fraud flags per district so the bank can
    see where policy leakage and verification backlogs concentrate. Districts
    are ranked by a composite bottleneck score (worst first).
    """
    records = load_all_records()

    flag_weights = {
        "IRRIGATION_MISMATCH": 1,
        "KCC_SUBVENTION_MISSING": 2,
        "PMFBY_UNDERPAYMENT": 2,
        "DUPLICATE_MORTGAGE_DETECTED": 3,
    }

    agg: dict = {}
    for rec in records:
        evaluation = evaluate_entitlements_and_flags(rec)
        district = rec["district"]
        bucket = agg.setdefault(
            district,
            {
                "district": district,
                "farmer_count": 0,
                "total_area_hectares": 0.0,
                "total_msp_gap": 0,
                "total_pmfby_gap": 0,
                "duplicate_mortgage_cases": 0,
                "total_duplicate_exposure": 0,
                "flag_counts": {k: 0 for k in flag_weights},
            },
        )
        bucket["farmer_count"] += 1
        bucket["total_area_hectares"] += rec["area_hectares"]
        bucket["total_msp_gap"] += max(evaluation["msp_gap"], 0)
        bucket["total_pmfby_gap"] += max(evaluation["pmfby_gap"], 0)
        if "DUPLICATE_MORTGAGE_DETECTED" in evaluation["flags"]:
            bucket["duplicate_mortgage_cases"] += 1
            bucket["total_duplicate_exposure"] += _total_active_mortgage(rec)
        for flag in evaluation["flags"]:
            if flag in bucket["flag_counts"]:
                bucket["flag_counts"][flag] += 1

    rows = []
    for bucket in agg.values():
        score = sum(
            bucket["flag_counts"][flag] * weight for flag, weight in flag_weights.items()
        )
        # Duplicate financing carries extra weight as a direct fraud signal.
        score += bucket["duplicate_mortgage_cases"] * 2
        bucket["bottleneck_score"] = score
        bucket["total_area_hectares"] = round(bucket["total_area_hectares"], 2)
        rows.append(bucket)

    rows.sort(key=lambda r: r["bottleneck_score"], reverse=True)
    return {"district_count": len(rows), "districts": rows}


# ---------------------------------------------------------------------------
# 3. Loan-approval endpoints
# ---------------------------------------------------------------------------
@router.get("/loan-approvals")
def loan_approvals_overview():
    """Bulk KCC loan decisions for every record on file, with a summary of the
    approval pipeline.
    """
    records = load_all_records()
    decisions = [_loan_decision(r) for r in records]
    summary: dict = {}
    for decision in decisions:
        summary[decision["decision"]] = summary.get(decision["decision"], 0) + 1
    return {
        "total_applications": len(decisions),
        "decision_summary": summary,
        "total_eligible_amount": sum(d["eligible_loan_amount"] for d in decisions),
        "decisions": decisions,
    }


@router.get("/loan/{khasra_no:path}")
def loan_decision(khasra_no: str):
    """Pre-approval KCC loan decision for a single farmer (eligible amount,
    status, and reasons), without the farmer submitting a specific request.
    """
    records = load_all_records()
    record = next((r for r in records if r["khasra_no"] == khasra_no), None)
    if record is None:
        raise fastapi.HTTPException(status_code=404, detail="Khasra number not found")
    return _loan_decision(record)


@router.post("/loan/{khasra_no:path}")
def apply_for_loan(khasra_no: str, application: LoanApplication):
    """Farmer submits a KCC loan application for a specific amount against a
    plot. The bank returns the decision, capping the approved amount at the
    eligible limit when the request exceeds it.
    """
    records = load_all_records()
    record = next((r for r in records if r["khasra_no"] == khasra_no), None)
    if record is None:
        raise fastapi.HTTPException(status_code=404, detail="Khasra number not found")
    return _loan_decision(record, requested_amount=application.requested_amount)
