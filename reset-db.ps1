#!/usr/bin/env pwsh
# Reset the PostgreSQL database - use this if you get authentication errors

Write-Host "=== Resetting Database ==="
Write-Host "This will delete all data in PostgreSQL and reinitialize it."
Write-Host ""

$confirm = Read-Host "Are you sure? Type 'yes' to confirm"
if ($confirm -ne "yes") {
    Write-Host "Cancelled."
    exit 0
}

Write-Host ""
Write-Host ">>> Stopping Docker containers and removing volumes..."
docker-compose down -v

Write-Host ">>> Starting Docker containers fresh..."
docker-compose up -d

Write-Host ">>> Waiting for PostgreSQL to initialize..."
Start-Sleep -Seconds 10

Write-Host ">>> Verifying PostgreSQL connection..."
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $result = docker-compose exec -T postgres pg_isready -U tpln -d tpln 2>&1
        if ($result -match "accepting" -or $LASTEXITCODE -eq 0) {
            $ready = $true
            break
        }
    }
    catch {
        # Still initializing
    }
    Write-Host "  Attempt $($i+1)/30..."
    Start-Sleep -Seconds 1
}

if ($ready) {
    Write-Host ""
    Write-Host "✓ Database reset successfully!"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Run the migrations: cd backend && alembic upgrade head"
    Write-Host "  2. Start the application: .\start.sh"
}
else {
    Write-Host ""
    Write-Host "⚠ Database initialization timed out. Try again or check Docker logs:"
    Write-Host "    docker-compose logs postgres"
    exit 1
}
