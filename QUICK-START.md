# AI PLC Platform - Quick Start Guide

## ✅ Frontend is Now Running!

### Access Your Application:
- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🚀 Quick Start Options

### Option 1: Start Everything (Easiest)
Double-click: `start-all.bat`

This will open both backend and frontend in separate windows.

### Option 2: Start Individually

**Start Backend:**
```bash
# Double-click: start-backend.bat
# OR run in terminal:
cd backend
python -m uvicorn app.main:app --reload
```

**Start Frontend:**
```bash
# Double-click: frontend/start-frontend.bat
# OR run in terminal:
cd frontend
npm run dev
```

---

## 📝 Important Notes

### PowerShell Script Execution Issue
If you get a PowerShell execution policy error, use one of these solutions:

**Solution 1: Use the .bat files** (Recommended)
- Just double-click the `.bat` files instead

**Solution 2: Use CMD instead of PowerShell**
```cmd
cmd
cd frontend
npm run dev
```

**Solution 3: Enable PowerShell scripts** (Admin rights needed)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 🔧 Troubleshooting

### Frontend won't start:
```bash
cd frontend
npm install
npm run dev
```

### Backend won't start:
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Port already in use:
- Backend: Edit `backend/app/config.py` to change port
- Frontend: Edit `frontend/vite.config.js` to change port

---

## 📂 Project Structure

```
ai-plc-platform/
├── start-all.bat          ← Start both servers
├── start-backend.bat      ← Start backend only
├── backend/               ← FastAPI backend
│   └── app/
├── frontend/              ← React frontend
│   └── start-frontend.bat ← Start frontend only
└── data/                  ← Application data
```

---

## 🎯 Next Steps

1. Open browser: http://localhost:5173
2. The frontend will connect to backend automatically
3. Start using your AI PLC Platform!

---

**Happy Coding! 🚀**
