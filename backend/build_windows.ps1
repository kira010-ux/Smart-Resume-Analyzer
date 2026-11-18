param(
    [string]$Python = ".\.venv\Scripts\python.exe"
)

& $Python -m pip install pyinstaller
$root = Resolve-Path "$PSScriptRoot\.."
& $Python -m PyInstaller --clean --onefile --name smart-resume-api `
    --distpath (Join-Path $root "backend-dist") `
    --workpath (Join-Path $root "backend-build") `
    (Join-Path $root "backend\main.py")