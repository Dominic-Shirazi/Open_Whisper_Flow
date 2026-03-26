$ScriptDir = $PSScriptRoot
$PythonPath = Join-Path $ScriptDir ".venv\Scripts\python.exe"
$ScriptPath = Join-Path $ScriptDir "whisper_api.py"

Write-Host "Starting Whisper API Keep-Alive... (Press Ctrl+C to stop)" -ForegroundColor Cyan

while ($true) {
    Write-Host "[$(Get-Date)] Launching Whisper API..." -ForegroundColor Green
    & $PythonPath $ScriptPath
    
    Write-Host "[$(Get-Date)] Whisper API stopped. Restarting in 5 seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
}
