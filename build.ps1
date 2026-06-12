$ErrorActionPreference = "Stop"

python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --name "StarCitizenMiningOverlay" `
    --collect-all "PySide6" `
    --add-data "src;src" `
    "src\main.py"

Write-Host "Executable genere dans dist\StarCitizenMiningOverlay" -ForegroundColor Green
