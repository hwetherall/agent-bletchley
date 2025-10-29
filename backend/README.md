# Agent Bletchley Backend

FastAPI backend for the Agent Bletchley research system.

## Setup

### Prerequisites

- Python 3.11 or higher
- Virtual environment (recommended)

### Installation

**IMPORTANT: Run all commands from the `backend` directory!**

1. Navigate to the backend directory:
```powershell
cd backend
```

2. Create a virtual environment (if it doesn't exist):
```bash
python -m venv venv
```

3. Activate the virtual environment:
```powershell
# On Windows PowerShell (from backend directory):
.\venv\Scripts\Activate.ps1

# If you get an execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# On Windows Command Prompt:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Configure environment variables:
```bash
# On Windows PowerShell:
Copy-Item .env.example .env

# On macOS/Linux:
cp .env.example .env

# Edit .env with your API keys and configuration
```

### Required Environment Variables

- `OPENROUTER_API_KEY` - Your OpenRouter API key
- `BRAVE_SEARCH_API_KEY` - Your Brave Search API key
- `JINA_READER_API_KEY` - Your Jina Reader API key
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon key

### Running the Server

Development server with auto-reload:
```bash
uvicorn app.main:app --reload
```

Production server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── orchestrator/         # Research orchestration logic
│   ├── tools/                # External API integrations
│   ├── api/                  # REST API routes
│   └── models/               # Pydantic data models
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

### Development

The codebase uses:
- Async/await patterns throughout
- Type hints on all functions
- TODO comments marking areas for implementation
- Proper logging configuration

