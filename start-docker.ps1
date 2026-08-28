# ============================================================
#  NK's Yams — Docker start script
#  Run: .\start-docker.ps1
#  Builds the image once, then starts the container.
#  Re-run any time to restart with latest code changes.
# ============================================================

$IMAGE_NAME  = "nks-yams"
$CONTAINER   = "nks-yams-api"
$HOST_PORT   = 5000
$ROOT        = $PSScriptRoot

Set-Location $ROOT

Write-Host ""
Write-Host "  =============================================" -ForegroundColor Yellow
Write-Host "   NK's Yams — Docker Backend Launcher" -ForegroundColor Yellow
Write-Host "  =============================================" -ForegroundColor Yellow
Write-Host ""

# ---- Verify Docker is running ----
# Try to find docker.exe if not on PATH
$dockerExe = "docker"
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    $candidates = @(
        "C:\Program Files\Docker\Docker\resources\bin\docker.exe",
        "$env:ProgramFiles\Docker\Docker\resources\bin\docker.exe",
        "$env:LOCALAPPDATA\Docker\resources\bin\docker.exe"
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { $dockerExe = $c; break }
    }
    if ($dockerExe -eq "docker") {
        Write-Host ""
        Write-Host "  ERROR: Docker not found on this machine." -ForegroundColor Red
        Write-Host ""
        Write-Host "  Install Docker Desktop from: https://docker.com/get-started/" -ForegroundColor Yellow
        Write-Host "  After installing, restart PowerShell and run this script again." -ForegroundColor Yellow
        Write-Host ""
        Read-Host "  Press Enter to exit"
        exit 1
    }
    Write-Host "  Found Docker at: $dockerExe" -ForegroundColor Gray
}

$dockerCheck = & $dockerExe info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Docker is installed but not running." -ForegroundColor Red
    Write-Host "  Please start Docker Desktop and try again." -ForegroundColor Yellow
    Read-Host "  Press Enter to exit"
    exit 1
}
Write-Host "  Docker is running." -ForegroundColor Green

# ---- Stop and remove any existing container ----
$existing = & $dockerExe ps -aq --filter "name=$CONTAINER" 2>&1
if ($existing) {
    Write-Host "  Stopping existing container..." -ForegroundColor Cyan
    & $dockerExe stop $CONTAINER 2>&1 | Out-Null
    & $dockerExe rm   $CONTAINER 2>&1 | Out-Null
}

# ---- Build the image ----
Write-Host "  Building Docker image '$IMAGE_NAME'..." -ForegroundColor Cyan
& $dockerExe build -t $IMAGE_NAME .
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Docker build failed. Check errors above." -ForegroundColor Red
    Read-Host "  Press Enter to exit"
    exit 1
}
Write-Host "  Image built successfully." -ForegroundColor Green

# ---- Load .env values to pass as --env-file ----
$envFile = Join-Path $ROOT ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "  WARNING: .env file not found. Server will start without DB." -ForegroundColor Yellow
}

# ---- Run the container ----
Write-Host "  Starting container '$CONTAINER' on port $HOST_PORT..." -ForegroundColor Cyan

if (Test-Path $envFile) {
    & $dockerExe run -d `
        --name $CONTAINER `
        -p "${HOST_PORT}:5000" `
        --env-file "$envFile" `
        --restart unless-stopped `
        $IMAGE_NAME
} else {
    & $dockerExe run -d `
        --name $CONTAINER `
        -p "${HOST_PORT}:5000" `
        --restart unless-stopped `
        $IMAGE_NAME
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "  Failed to start container. Check errors above." -ForegroundColor Red
    Read-Host "  Press Enter to exit"
    exit 1
}

# ---- Wait for server to be ready ----
Write-Host "  Waiting for server to start..." -ForegroundColor Gray
$maxWait = 20
$ready   = $false
for ($i = 0; $i -lt $maxWait; $i++) {
    Start-Sleep -Seconds 1
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$HOST_PORT/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $ready = $true
            break
        }
    } catch {}
    Write-Host "  ." -NoNewline -ForegroundColor Gray
}

Write-Host ""
if ($ready) {
    Write-Host ""
    Write-Host "  =============================================" -ForegroundColor Green
    Write-Host "   SERVER IS LIVE!" -ForegroundColor Green
    Write-Host "  =============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  API server  :  http://localhost:$HOST_PORT" -ForegroundColor Cyan
    Write-Host "  Health check:  http://localhost:$HOST_PORT/health" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Frontend    :  http://localhost:8080/index.html" -ForegroundColor Cyan
    Write-Host "  Register    :  http://localhost:8080/register.html" -ForegroundColor Cyan
    Write-Host "  Login       :  http://localhost:8080/login.html" -ForegroundColor Cyan
    Write-Host "  Admin       :  http://localhost:8080/admin.html" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  To view logs:  & '$dockerExe' logs -f $CONTAINER" -ForegroundColor Gray
    Write-Host "  To stop     :  & '$dockerExe' stop $CONTAINER" -ForegroundColor Gray
    Write-Host "  =============================================" -ForegroundColor Green
    Write-Host ""
    # Open browser to the frontend
    Start-Process "http://localhost:8080/index.html"
} else {
    Write-Host "  Server did not respond in time. Check container logs:" -ForegroundColor Yellow
    Write-Host "    docker logs $CONTAINER" -ForegroundColor Cyan
}
