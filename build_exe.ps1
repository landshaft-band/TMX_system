$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    $Python = "python"
}

& $Python -m pip install -r requirements.txt
& $Python -m PyInstaller --clean --noconfirm WagonWMS.spec

Write-Host ""
Write-Host "EXE создан: $ProjectRoot\dist\WagonWMS.exe"
Write-Host "Папка отчётов по умолчанию рядом с exe: $ProjectRoot\dist\reports"
