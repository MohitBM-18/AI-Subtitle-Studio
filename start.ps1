#!/usr/bin/env pwsh
# start.ps1  – Activate the venv and start the dev server
# Usage: .\start.ps1

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (-not (Test-Path "$root\.env")) {
    Copy-Item "$root\.env.example" "$root\.env"
    Write-Host "⚠️  Created .env from .env.example – add your OPENAI_API_KEY before testing AI features."
}

Write-Host "🚀 Starting AI Subtitle Studio at http://127.0.0.1:8000"
& "$root\venv\Scripts\uvicorn.exe" backend.main:app --host 127.0.0.1 --port 8000 --reload
