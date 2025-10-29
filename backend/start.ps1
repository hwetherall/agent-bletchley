# PowerShell script to start the backend development server
# Run this script from the backend directory: .\start.ps1

Write-Host "Agent Bletchley Backend - Starting..." -ForegroundColor Cyan

# Change to backend directory if not already there
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "$scriptPath\venv\Scripts\Activate.ps1"

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "Please edit .env file with your API keys!" -ForegroundColor Red
}

# Install/upgrade dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Run the server
Write-Host "Starting FastAPI server..." -ForegroundColor Green
uvicorn app.main:app --reload

