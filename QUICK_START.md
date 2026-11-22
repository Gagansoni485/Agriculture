# 🚀 Quick Start Guide

## For Farmer View Team

```bash
git clone https://github.com/Gagansoni485/Agriculture.git
cd agri-transparency-backend
git checkout -b feat/farmer-backend
pip install -r requirements.txt
```

**Your file:** `routes/farmer_routes.py`

**Run tests:**
```bash
python test_setup.py
uvicorn main:app --reload
```

**Visit:** http://127.0.0.1:8000/docs

---

## For Bank View Team

```bash
git clone https://github.com/Gagansoni485/Agriculture.git
cd agri-transparency-backend
git checkout -b feat/bank-backend
pip install -r requirements.txt
```

**Your file:** `routes/bank_routes.py`

**Run tests:**
```bash
python test_setup.py
uvicorn main:app --reload
```

**Visit:** http://127.0.0.1:8000/docs

---

## Test Endpoints

### Farmer API
```bash
# Check specific farmer
curl http://127.0.0.1:8000/api/farmer/check/101/1
```

### Bank API
```bash
# Verify all applications
curl http://127.0.0.1:8000/api/bank/verify-all
```

---

## Sample Khasra Numbers

- `101/1` - Suresh Verma (Clean record, no flags)
- `102/4` - Rameshwar Sahu (Has multiple issues: irrigation mismatch, duplicate mortgages, underpayment)

---

## Golden Rules

1. ✅ **Farmer Team:** ONLY edit `routes/farmer_routes.py`
2. ✅ **Bank Team:** ONLY edit `routes/bank_routes.py`
3. 🔒 **Both Teams:** DON'T edit `main.py` or `shared/` without coordination
4. 🔄 **Daily:** Run `git pull origin main` before starting work
5. 🧪 **Always:** Test with `python test_setup.py` before committing

---

## Need Help?

- **Full workflow:** See `TEAM_WORKFLOW.md`
- **Project details:** See `README.md`
- **API docs:** Run server and visit http://127.0.0.1:8000/docs
