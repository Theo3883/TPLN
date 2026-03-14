$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

Write-Host "=== Starting Literature Evaluation Platform ==="

Write-Host ">>> Starting Docker (PostgreSQL + Meilisearch)..."
docker compose up -d

Write-Host ">>> Waiting for PostgreSQL..."
$postgresReady = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        docker compose exec -T postgres pg_isready -U tpln -d tpln *> $null
        if ($LASTEXITCODE -eq 0) {
            $postgresReady = $true
            break
        }
    }
    catch {
        # Ignore transient startup errors while waiting for service health.
    }
    Start-Sleep -Seconds 2
}

if (-not $postgresReady) {
    throw "PostgreSQL did not become ready in time."
}

Write-Host ">>> Waiting for Meilisearch..."
$meiliReady = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:7700/health" -Method Get -TimeoutSec 2
        if ($health.status -eq "available") {
            $meiliReady = $true
            break
        }
    }
    catch {
        # Ignore transient startup errors while waiting for service health.
    }
    Start-Sleep -Seconds 2
}

if (-not $meiliReady) {
    throw "Meilisearch did not become ready in time."
}

Write-Host ">>> Installing backend dependencies..."
python -m pip install -r backend/requirements.txt -q

Write-Host ">>> Installing crawler dependencies..."
python -m pip install -r crawler/requirements.txt -q

Write-Host ">>> Installing UI dependencies..."
python -m pip install -r ui/requirements.txt -q

Write-Host ">>> Running database migrations..."
Push-Location backend
alembic upgrade head
Pop-Location

Write-Host ">>> Starting backend (FastAPI)..."
$backendProcess = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" -WorkingDirectory (Join-Path $PSScriptRoot "backend") -PassThru

Write-Host ">>> Waiting for backend to be ready..."
do {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing -TimeoutSec 2
        if ($response.Content -match "Platform") {
            break
        }
    }
    catch {
        # Backend is still starting.
    }
    Start-Sleep -Seconds 2
} while ($true)

Write-Host ">>> Starting Streamlit UI..."
$uiProcess = Start-Process -FilePath "python" -ArgumentList "-m", "streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0" -WorkingDirectory (Join-Path $PSScriptRoot "ui") -PassThru

Write-Host ""
Write-Host "=== Ready ==="
Write-Host "  Backend:  http://localhost:8000"
Write-Host "  API Docs: http://localhost:8000/docs"
Write-Host "  UI:       http://localhost:8501"
Write-Host ""
Write-Host "Press Ctrl+C to stop all services."

try {
    Wait-Process -Id $backendProcess.Id, $uiProcess.Id
}
finally {
    foreach ($proc in @($backendProcess, $uiProcess)) {
        if ($null -ne $proc) {
            try {
                $running = Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
                if ($null -ne $running) {
                    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
                }
            }
            catch {
                # Process already stopped.
            }
        }
    }
}