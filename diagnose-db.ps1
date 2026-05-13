#!/usr/bin/env pwsh
# Diagnose database connection issues

Write-Host "=== Database Connection Diagnostics ==="
Write-Host ""

# Check if Docker is running
Write-Host "1. Checking Docker..."
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "  ✓ Docker is installed: $dockerVersion"
}
catch {
    Write-Host "  ✗ Docker is not available"
    exit 1
}

# Check if containers are running
Write-Host ""
Write-Host "2. Checking Docker containers..."
try {
    $containers = docker-compose ps --format "table {{.Service}}\t{{.Status}}" 2>&1
    Write-Host $containers
}
catch {
    Write-Host "  ✗ Could not get container status"
}

# Check PostgreSQL connectivity
Write-Host ""
Write-Host "3. Testing PostgreSQL connection..."
try {
    $result = docker-compose exec -T postgres pg_isready -U tpln -d tpln 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ PostgreSQL is accepting connections"
    }
    else {
        Write-Host "  ✗ PostgreSQL is NOT accepting connections"
        Write-Host "  Output: $result"
    }
}
catch {
    Write-Host "  ✗ Could not connect to PostgreSQL"
    Write-Host "  Error: $_"
}

# Check PostgreSQL logs for errors
Write-Host ""
Write-Host "4. Recent PostgreSQL logs:"
try {
    $logs = docker-compose logs postgres --tail 20 2>&1
    Write-Host $logs
}
catch {
    Write-Host "  Could not retrieve logs"
}

# Check if the database and user exist
Write-Host ""
Write-Host "5. Checking database and user..."
try {
    $users = docker-compose exec -T postgres psql -U tpln -d tpln -c "\du" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Can connect as tpln user"
        Write-Host $users
    }
    else {
        Write-Host "  ✗ Cannot connect as tpln user"
        Write-Host "  Output: $users"
    }
}
catch {
    Write-Host "  ✗ Error checking users"
}

# Summary and recommendations
Write-Host ""
Write-Host "=== Recommendations ==="
Write-Host ""
Write-Host "If PostgreSQL is not accepting connections:"
Write-Host "  1. Run: powershell ./reset-db.ps1"
Write-Host "  2. Then: powershell ./start.sh"
Write-Host ""
Write-Host "If you see authentication errors after reset:"
Write-Host "  1. Check Docker logs: docker-compose logs postgres"
Write-Host "  2. Make sure no other service is using port 5433"
Write-Host "  3. Verify credentials match in docker-compose.yml and config.py"
