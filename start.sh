#!/usr/bin/env pwsh
# This script is Windows-compatible. Run with: pwsh ./start.sh
# On Windows with PowerShell: Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned; .\start.sh
# Or simply use: powershell -ExecutionPolicy RemoteSigned -File start.sh

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

# Track child processes so we can clean up
$childProcesses = @()

# Cleanup function for graceful shutdown
$cleanupBlock = {
    Write-Host "Shutting down..."
    foreach ($proc in $childProcesses) {
        try {
            if ($proc.HasExited -eq $false) {
                Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            }
        }
        catch {
            # Process may have already exited
        }
    }
}

# Register cleanup on exit
$null = Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action $cleanupBlock

Write-Host "=== Starting Platformă Evaluare Literatură Română ==="

Write-Host ">>> Starting Docker (PostgreSQL + Meilisearch)..."
docker-compose up -d

Write-Host ">>> Waiting for PostgreSQL to be healthy..."
$postgresReady = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        $health = docker-compose ps postgres --format "table {{.Status}}" 2>$null
        if ($health -match "healthy|running") {
            # Double-check that we can actually connect
            $result = docker-compose exec -T postgres pg_isready -U tpln -d tpln 2>&1
            if ($LASTEXITCODE -eq 0 -or $result -match "accepting") {
                Write-Host "PostgreSQL is ready."
                $postgresReady = $true
                break
            }
        }
    }
    catch {
        # Ignore errors while waiting
    }
    Write-Host "  Still waiting for PostgreSQL... ($i/60)"
    Start-Sleep -Seconds 1
}

if (-not $postgresReady) {
    Write-Warning "PostgreSQL did not become ready in time. Attempting to continue..."
}

Write-Host ">>> Waiting for Meilisearch..."
$meiliReady = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:7700/health" -Method Get -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($health.status -eq "available") {
            $meiliReady = $true
            break
        }
    }
    catch {
        # Ignore transient errors
    }
    Start-Sleep -Seconds 2
}

if (-not $meiliReady) {
    Write-Warning "Meilisearch did not become ready in time."
}

Write-Host ">>> Installing backend dependencies..."
pip3 install -r backend/requirements.txt -q

Write-Host ">>> Installing crawler dependencies..."
pip3 install -r crawler/requirements.txt -q

Write-Host ">>> Running database migrations..."
if (Test-Path "backend") {
    Push-Location backend
    $env:DATABASE_URL = "postgresql+asyncpg://tpln:tpln@127.0.0.1:5433/tpln"
    
    # Give postgres a moment to be fully ready for connections
    Start-Sleep -Seconds 2
    
    try {
        for ($attempt = 1; $attempt -le 10; $attempt++) {
            try {
                Write-Host "  Running migrations (attempt $attempt/10)..."
                alembic upgrade head 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "  ✓ Migrations completed successfully."
                    Pop-Location
                    break
                }
                else {
                    throw "Alembic exited with code $LASTEXITCODE"
                }
            }
            catch {
                if ($attempt -lt 10) {
                    Write-Host "  ⚠ Migration attempt $attempt failed, retrying in 2 seconds..."
                    Start-Sleep -Seconds 2
                }
                else {
                    throw $_
                }
            }
        }
    }
    catch {
        Pop-Location
        Write-Warning "Alembic migrations failed after 10 retries."
        Write-Warning "Try running: powershell ./reset-db.ps1"
        Write-Warning "Error details: $_"
    }
}
else {
    Write-Warning "Backend directory not found, skipping migrations."
}

Write-Host ">>> Starting backend (FastAPI)..."
$backendProcess = $null
if (Test-Path "backend") {
    $backendProcess = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" `
        -WorkingDirectory (Join-Path $PSScriptRoot "backend") -PassThru
    $childProcesses += $backendProcess
}
else {
    Write-Warning "Backend directory not found, skipping backend start."
}

Write-Host ">>> Waiting for backend to be ready..."
if ($backendProcess) {
    for ($i = 0; $i -lt 30; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                break
            }
        }
        catch {
            # Backend is still starting
        }
        Start-Sleep -Seconds 2
    }
}

Write-Host ">>> Installing frontend dependencies..."
$frontendProcess = $null
if (Test-Path "frontend") {
    Push-Location frontend
    npm install --silent
    Pop-Location

    Write-Host ">>> Starting frontend (Vite dev server)..."
    $env:VITE_API_BASE = "http://localhost:8000"
    $frontendProcess = Start-Process -FilePath "npm" -ArgumentList "run", "dev" `
        -WorkingDirectory (Join-Path $PSScriptRoot "frontend") -PassThru
    $childProcesses += $frontendProcess
}
else {
    Write-Warning "Frontend directory not found, skipping frontend start."
}

Write-Host ""
Write-Host "=== Ready ==="
Write-Host "  Backend:  http://localhost:8000"
Write-Host "  API Docs: http://localhost:8000/docs"
Write-Host "  Frontend: http://localhost:3000"
Write-Host ""
Write-Host "Press Ctrl+C to stop all services."

# Wait for processes - this will block until Ctrl+C is pressed
try {
    if ($childProcesses.Count -gt 0) {
        foreach ($proc in $childProcesses) {
            Wait-Process -Id $proc.Id -ErrorAction SilentlyContinue
        }
    }
    else {
        # If no processes, just wait indefinitely
        while ($true) { Start-Sleep -Seconds 10 }
    }
}
finally {
    & $cleanupBlock
}
