# ============================================================
#  NK's Yams — Quick start (assumes Node.js is already installed)
#  Run: .\start-server.ps1
# ============================================================

Set-Location $PSScriptRoot

# Install deps if missing
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    npm install
}

Write-Host ""
Write-Host "  Starting server on http://localhost:5000" -ForegroundColor Green
Write-Host "  Frontend preview: http://localhost:8080" -ForegroundColor Cyan
Write-Host "  Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host ""

node server.js
