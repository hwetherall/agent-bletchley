# Quick Start Guide - Windows PowerShell

## Backend Setup (from project root)

```powershell
# 1. Navigate to backend directory
cd backend

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 3. Install dependencies (if not already installed)
pip install -r requirements.txt

# 4. Create .env file (if not exists)
Copy-Item .env.example .env
# Then edit .env with your API keys

# 5. Start the server
uvicorn app.main:app --reload
```

## Alternative: Use the startup script

From the `backend` directory:
```powershell
.\start.ps1
```

## Verify it's working

Once the server starts, visit:
- API: http://localhost:8000
- Should return: `{"message": "Hello Agent Bletchley"}`
- Docs: http://localhost:8000/docs

## Troubleshooting

**Problem**: `Activate.ps1` not found
- **Solution**: Make sure you're in the `backend` directory, not the root

**Problem**: Execution policy error
- **Solution**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**Problem**: `uvicorn` not found
- **Solution**: Make sure venv is activated (you should see `(venv)` in your prompt)

**Problem**: `requirements.txt` not found
- **Solution**: Make sure you're in the `backend` directory

