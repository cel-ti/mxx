#!/usr/bin/env pwsh
# Install or upgrade mxx and all plugins globally
# Usage: .\dev-install.ps1 [-Upgrade]

param(
    [switch]$Upgrade
)

$action = if ($Upgrade) { "Upgrading" } else { "Installing" }

Write-Host "$action mxx..." -ForegroundColor Cyan
if ($Upgrade) {
    pip install -U .
} else {
    pip install .
}

Write-Host "`n$action plugins..." -ForegroundColor Cyan
Get-ChildItem -Path "plugins" -Directory | ForEach-Object {
    Write-Host "  $action $($_.Name)..." -ForegroundColor Yellow
    if ($Upgrade) {
        pip install -U "plugins/$($_.Name)"
    } else {
        pip install "plugins/$($_.Name)"
    }
}

Write-Host "`n$action complete!" -ForegroundColor Green
Write-Host "`nInstalled packages:" -ForegroundColor Cyan
pip list | Select-String -Pattern "mxx"
