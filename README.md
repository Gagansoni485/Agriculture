# Agri-Transparency Backend

Agriculture policy and loan transparency API for Chhattisgarh farmers.

## Project Structure

```
agri-transparency-backend/
├── main.py                  # [LOCKED] FastAPI entry point - connects both routers
├── requirements.txt         # [LOCKED] Shared dependencies
├── .gitignore              # Ignores __pycache__ and .env
│
├── shared/                 # [LOCKED] Single source of truth for data & math
│   ├── mock_db/
│   │   └── records.json    # Synthetic Khasra, Loan, and Payout records
│   └── rule_engine.py      # Pure math functions (MSP, KCC, PMFBY, Mismatch checks)
│
└── routes/
    ├── __init__.py         # Package marker
    ├── farmer_routes.py    # [FARMER TEAM ONLY] Farmer view endpoints
    └── bank_routes.py      # [BANK TEAM ONLY] Bank view endpoints
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Gagansoni485/Agriculture.git
cd agri-transparency-backend
```

### 2. Create Your Feature Branch

**For Farmer View Team:**
```bash
git checkout -b feat/farmer-backend
```

**For Bank View Team:**
```bash
git checkout -b feat/bank-backend
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Locally

```bash
uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs in your browser for the interactive Swagger UI.

## Golden Rules for Collaboration

### ✅ DO:
- **Farmer Team:** ONLY edit `routes/farmer_routes.py`
  - Add grievance generation
  - Add Hindi/Chhattisgarhi LLM translation
  - Add voice endpoints
  
- **Bank Team:** ONLY edit `routes/bank_routes.py`
  - Add duplicate mortgage filters
  - Add district bottleneck aggregations
  - Add loan approval endpoints

### ❌ DON'T:
- Edit `main.py` without coordinating with the other team
- Edit `shared/` files without coordinating with the other team
- Merge conflicts happen when both edit the same file

### 🔄 Updating Shared Data:
If you need to add farmers to `shared/mock_db/records.json`:
1. Switch to main: `git checkout main`
2. Make changes and commit
3. Push to main: `git push origin main`
4. Tell your teammate to pull: `git pull origin main`
5. Switch back to your feature branch: `git checkout feat/<your-branch>`

## API Endpoints

### Farmer View (`/api/farmer`)
- `GET /api/farmer/check/{khasra_no}` - Check farmer entitlements and flags

### Bank View (`/api/bank`)
- `GET /api/bank/verify-all` - Verify all loan applications

## Sample Data

The project includes 2 sample farmer records:
- **101/1** - Suresh Verma (Abhanpur, Raipur) - Clean record
- **102/4** - Rameshwar Sahu (Kurud, Dhamtari) - Has irrigation mismatch and duplicate mortgage

## Testing

Visit http://127.0.0.1:8000/docs after running the server to test all endpoints interactively.

Example test:
```bash
curl http://127.0.0.1:8000/api/farmer/check/101/1
```

## Key Features

- **MSP Calculation:** CG Paddy Rate = ₹3100/quintal
- **KCC Interest Subvention:** 4% if repaid on time, 7% otherwise
- **PMFBY Crop Insurance:** Irrigated = ₹66,000/ha, Unirrigated = ₹45,000/ha
- **Fraud Detection:** Irrigation mismatch, duplicate mortgages, underpayment flags
