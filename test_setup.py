#!/usr/bin/env python3
"""Quick test to verify the backend setup works correctly."""

import sys
from pathlib import Path

# Test imports
try:
    from fastapi import FastAPI
    from shared.rule_engine import load_all_records, get_record_by_khasra, evaluate_entitlements_and_flags
    from routes import farmer_routes, bank_routes
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test data loading
try:
    records = load_all_records()
    print(f"✅ Loaded {len(records)} farmer records")
except Exception as e:
    print(f"❌ Data loading failed: {e}")
    sys.exit(1)

# Test record retrieval
try:
    record = get_record_by_khasra("101/1")
    if record:
        print(f"✅ Found record for Khasra 101/1: {record['owner_name']}")
    else:
        print("❌ Could not find test record")
        sys.exit(1)
except Exception as e:
    print(f"❌ Record retrieval failed: {e}")
    sys.exit(1)

# Test entitlement evaluation
try:
    result = evaluate_entitlements_and_flags(record)
    print(f"✅ Entitlement calculation successful")
    print(f"   - Owner: {result['owner_name']}")
    print(f"   - Expected MSP: ₹{result['expected_msp']:,}")
    print(f"   - MSP Gap: ₹{result['msp_gap']:,}")
    print(f"   - Flags: {', '.join(result['flags']) if result['flags'] else 'None'}")
except Exception as e:
    print(f"❌ Entitlement evaluation failed: {e}")
    sys.exit(1)

# Test second record with flags
try:
    record2 = get_record_by_khasra("102/4")
    result2 = evaluate_entitlements_and_flags(record2)
    print(f"✅ Second record evaluation successful")
    print(f"   - Owner: {result2['owner_name']}")
    print(f"   - Flags: {', '.join(result2['flags'])}")
except Exception as e:
    print(f"❌ Second record failed: {e}")
    sys.exit(1)

print("\n🎉 All tests passed! Backend setup is correct.")
print("\nTo run the server:")
print("  uvicorn main:app --reload")
print("\nThen visit: http://127.0.0.1:8000/docs")
