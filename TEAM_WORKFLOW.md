# Team Collaboration Workflow

## 🎯 Quick Start for Each Team Member

### **Farmer View Team** (Working on farmer-facing features)

```bash
# Clone and setup
git clone https://github.com/Gagansoni485/Agriculture.git
cd agri-transparency-backend

# Create your feature branch
git checkout -b feat/farmer-backend

# Install dependencies
pip install -r requirements.txt

# Your work file
# ✅ ONLY EDIT: routes/farmer_routes.py

# Test your changes
python test_setup.py
uvicorn main:app --reload  # Visit http://127.0.0.1:8000/docs
```

**Your Features to Implement:**
- ✅ Grievance generation based on entitlement gaps
- ✅ Hindi/Chhattisgarhi LLM translation service
- ✅ Voice input/output endpoints
- ✅ Farmer-friendly response formatting

---

### **Bank View Team** (Working on bank/admin features)

```bash
# Clone and setup
git clone https://github.com/Gagansoni485/Agriculture.git
cd agri-transparency-backend

# Create your feature branch
git checkout -b feat/bank-backend

# Install dependencies
pip install -r requirements.txt

# Your work file
# ✅ ONLY EDIT: routes/bank_routes.py

# Test your changes
python test_setup.py
uvicorn main:app --reload  # Visit http://127.0.0.1:8000/docs
```

**Your Features to Implement:**
- ✅ Duplicate mortgage detection filters
- ✅ District-wise bottleneck aggregations
- ✅ Loan approval workflow endpoints
- ✅ Fraud detection dashboard data

---

## 🔐 File Ownership Rules

### ✅ Safe to Edit (Your Own Files)

**Farmer Team:**
- `routes/farmer_routes.py` ← YOUR FILE ONLY

**Bank Team:**
- `routes/bank_routes.py` ← YOUR FILE ONLY

### 🔒 Locked Files (Coordinate Before Changing)

These files are shared. If you need to change them, follow the **Shared File Update Process** below:
- `main.py`
- `shared/rule_engine.py`
- `shared/mock_db/records.json`
- `requirements.txt`

---

## 📝 Daily Workflow

### 1. Start Your Day
```bash
# Get latest changes from main
git checkout main
git pull origin main

# Switch back to your feature branch
git checkout feat/<your-branch-name>

# Merge main into your branch
git merge main
```

### 2. Make Your Changes
```bash
# Edit your designated file only
# routes/farmer_routes.py OR routes/bank_routes.py

# Test locally
python test_setup.py
uvicorn main:app --reload
```

### 3. Commit Your Work
```bash
# Stage your file
git add routes/<your-file>.py

# Commit with descriptive message
git commit -m "feat: add grievance generation endpoint"

# Push to your feature branch
git push origin feat/<your-branch-name>
```

### 4. Create Pull Request
```bash
# Using GitHub CLI (if installed)
gh pr create --title "Add farmer grievance features" --body "Implements grievance generation and translation"

# OR manually on GitHub:
# Visit https://github.com/Gagansoni485/Agriculture/pulls
# Click "New Pull Request"
```

---

## 🔄 Shared File Update Process

If you need to add farmer records or change shared logic:

### Option 1: Quick Shared Update (Small Changes)
```bash
# Switch to main
git checkout main

# Make your change to shared/mock_db/records.json
# Add 2-3 new farmer records

# Commit and push
git add shared/mock_db/records.json
git commit -m "data: add 3 new farmer test records"
git push origin main

# Notify your teammate in your group chat
# "Hey, I added new farmer data to main. Run 'git pull origin main'"

# Return to your branch and merge
git checkout feat/<your-branch>
git merge main
```

### Option 2: Coordinated Update (Complex Changes)
1. **Discuss in team chat:** "I need to update rule_engine.py to add new calculation"
2. **Get approval from both teams**
3. **Create separate PR:** `feat/shared-update`
4. **Both teams review and approve**
5. **Merge to main**
6. **Both teams pull main**

---

## 🚫 Avoiding Merge Conflicts

### The #1 Rule: Stay in Your Lane
```
Farmer Team: ONLY touch routes/farmer_routes.py
Bank Team:   ONLY touch routes/bank_routes.py
```

### If You Accidentally Get a Conflict
```bash
# Don't panic! Here's how to fix it:

# 1. See what's conflicted
git status

# 2. Open the conflicted file
# Look for <<<<<<< HEAD markers

# 3. Keep both changes (usually)
# Delete the conflict markers, keep both team's code

# 4. Mark as resolved
git add <conflicted-file>
git commit -m "fix: resolve merge conflict"

# 5. Ask for help in team chat if stuck!
```

---

## 🧪 Testing Checklist

Before every commit, run:
```bash
# 1. Verify imports work
python test_setup.py

# 2. Start server
uvicorn main:app --reload

# 3. Test in browser
# Visit http://127.0.0.1:8000/docs
# Click "Try it out" on your new endpoints

# 4. Test specific endpoint
# Farmer team: GET /api/farmer/check/101/1
# Bank team:   GET /api/bank/verify-all
```

---

## 📦 Sample API Responses

### Farmer Endpoint Response
```json
{
  "khasra_no": "101/1",
  "owner_name": "Suresh Verma",
  "village": "Abhanpur",
  "district": "Raipur",
  "expected_msp": 93000,
  "actual_msp": 93000,
  "msp_gap": 0,
  "expected_interest_pct": 4.0,
  "actual_interest_pct": 4.0,
  "expected_pmfby": 0,
  "actual_pmfby": 0,
  "pmfby_gap": 0,
  "active_mortgages": [
    { "bank": "State Bank of India", "amount": 80000, "status": "Active" }
  ],
  "flags": []
}
```

### Bank Endpoint Response
```json
[
  { /* farmer 1 data */ },
  { /* farmer 2 data */ }
]
```

---

## 🆘 Common Issues & Solutions

### "ModuleNotFoundError: No module named 'fastapi'"
```bash
pip install -r requirements.txt
```

### "File not found: records.json"
```bash
# Make sure you're in the right directory
cd agri-transparency-backend
python test_setup.py
```

### "Port 8000 is already in use"
```bash
# Kill the existing process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Then restart
uvicorn main:app --reload
```

### "My teammate's changes aren't showing up"
```bash
git checkout main
git pull origin main
git checkout feat/<your-branch>
git merge main
```

---

## 🎓 Git Commands Cheat Sheet

```bash
# See what changed
git status
git diff

# Save your work
git add <file>
git commit -m "message"
git push origin <branch-name>

# Get teammate's changes
git pull origin main
git merge main

# Create new branch
git checkout -b feat/new-feature

# Switch branches
git checkout main
git checkout feat/farmer-backend

# See all branches
git branch -a

# Undo last commit (keep changes)
git reset --soft HEAD~1
```

---

## 📞 Communication Protocol

### Use Your Team Chat For:
- ✅ "I'm working on the grievance endpoint"
- ✅ "I need to add 5 new farmer records to shared data"
- ✅ "My PR is ready for review"
- ✅ "I'm stuck with a merge conflict, can someone help?"
- ✅ "Server is running, let's test together"

### Use GitHub Issues For:
- 🐛 Bug reports
- ✨ Feature requests
- 📚 Documentation improvements

### Use Pull Request Comments For:
- 💬 Code review feedback
- ❓ Questions about implementation
- ✅ Approval/rejection

---

## 🚀 Ready to Start?

1. **Clone the repo**
2. **Create your feature branch**
3. **Run test_setup.py to verify**
4. **Start coding in your designated file**
5. **Test frequently**
6. **Commit often with good messages**
7. **Create PR when feature is ready**
8. **Review each other's code**
9. **Celebrate when merged! 🎉**

---

**Questions? Check with your teammate first, then reach out in the group chat!**
