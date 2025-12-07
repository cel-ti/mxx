#!/usr/bin/env pwsh
# Install or upgrade mxx and all plugins globally
# Usage: .\dev-install.ps1 [-Upgrade]

param(
    [switch]$Upgrade
)

function Bump-PluginVersion {
    param([string]$PyProjectPath)
    
    $content = Get-Content $PyProjectPath -Raw
    
    # Match version = "x.y.z" pattern
    if ($content -match 'version\s*=\s*"(\d+)\.(\d+)\.(\d+)"') {
        $major = $matches[1]
        $minor = $matches[2]
        $patch = [int]$matches[3] + 1
        $newVersion = "$major.$minor.$patch"
        
        $content = $content -replace 'version\s*=\s*"\d+\.\d+\.\d+"', "version = `"$newVersion`""
        Set-Content -Path $PyProjectPath -Value $content -NoNewline
        
        Write-Host "    Bumped version to $newVersion" -ForegroundColor Gray
    }
}

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
    
    # Bump version before installing
    $pyproject = Join-Path $_.FullName "pyproject.toml"
    if (Test-Path $pyproject) {
        Bump-PluginVersion -PyProjectPath $pyproject
    }
    
    if ($Upgrade) {
        pip install -U "plugins/$($_.Name)"
    } else {
        pip install "plugins/$($_.Name)"
    }
}

Write-Host "`n$action complete!" -ForegroundColor Green
Write-Host "`nInstalled packages:" -ForegroundColor Cyan
pip list | Select-String -Pattern "mxx"
