# ============================================================
#  NK's Yams — Auto-install Node.js + start server
#  Right-click this file → "Run with PowerShell"
#  OR open PowerShell and run: .\install-node-and-run.ps1
# ============================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "  =============================================" -ForegroundColor Yellow
Write-Host "   NK's Yams — Setup & Start" -ForegroundColor Yellow
Write-Host "  =============================================" -ForegroundColor Yellow
Write-Host ""

# ---- Check if Node is already installed ----
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
if ($nodeCmd) {
    $nodeVersion = & node --version 2>&1
    Write-Host "  Node.js already installed: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "  Node.js not found. Downloading installer..." -ForegroundColor Cyan
    $nodeUrl      = "https://nodejs.org/dist/v20.18.0/node-v20.18.0-x64.msi"
    $installerPath = "$env:TEMP\node-installer.msi"
    
    Write-Host "  Downloading from $nodeUrl ..." -ForegroundColor Gray
    Invoke-WebRequest -Uri $nodeUrl -OutFile $installerPath -UseBasicParsing
    
    Write-Host "  Installing Node.js (this may take a minute)..." -ForegroundColor Cyan
    Start-Process msiexec.exe -ArgumentList "/i `"$installerPath`" /quiet /norestart" -Wait
    
    # Refresh PATH
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
    
    $nodeCmd = Get-Command node -ErrorAction SilentlyContinue
    if ($nodeCmd) {
        Write-Host "  Node.js installed successfully!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "  Node.js was installed but PATH was not updated yet." -ForegroundColor Yellow
        Write-Host "  Please CLOSE this window, open a NEW PowerShell, and run:" -ForegroundColor Yellow
        Write-Host "    cd '$PSScriptRoot'" -ForegroundColor Cyan
        Write-Host "    npm install" -ForegroundColor Cyan
        Write-Host "    node server.js" -ForegroundColor Cyan
        Write-Host ""
        Read-Host "  Press Enter to exit"
        exit 0
    }
}

# ---- Check .env ----
$envFile = Join-Path $PSScriptRoot ".env"
$envContent = Get-Content $envFile -Raw -ErrorAction SilentlyContinue
if ($envContent -match "postgresql://username:password") {
    Write-Host ""
    Write-Host "  ⚠️  IMPORTANT: You haven't set your DATABASE_URL yet!" -ForegroundColor Red
    Write-Host "  Open the .env file and replace the DATABASE_URL with your Neon connection string." -ForegroundColor Yellow
    Write-Host "  Get it from: https://console.neon.tech" -ForegroundColor Cyan
    Write-Host ""
    $ans = Read-Host "  Continue anyway without a database? (y/n)"
    if ($ans -ne 'y') {
        Write-Host "  Exiting. Set DATABASE_URL in .env and re-run this script." -ForegroundColor Gray
        exit 0
    }
}

# ---- Install dependencies ----
$nodeModules = Join-Path $PSScriptRoot "node_modules"
if (-not (Test-Path $nodeModules)) {
    Write-Host ""
    Write-Host "  Installing npm dependencies..." -ForegroundColor Cyan
    Set-Location $PSScriptRoot
    & npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  npm install failed. Check error above." -ForegroundColor Red
        Read-Host "  Press Enter to exit"
        exit 1
    }
    Write-Host "  Dependencies installed!" -ForegroundColor Green
} else {
    Write-Host "  node_modules already present, skipping npm install." -ForegroundColor Gray
}

# ---- Start the server ----
Write-Host ""
Write-Host "  Starting NK's Yams backend server..." -ForegroundColor Cyan
Write-Host ""
Set-Location $PSScriptRoot
& node server.js
