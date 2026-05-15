$backendPath = "C:\Users\Son\.openclaw\workspace\coastalrisk_webapp_v1\backend"
$pythonExe = Join-Path $backendPath ".venv\Scripts\python.exe"
Set-Location $backendPath
& $pythonExe -m uvicorn app.main:app --host 127.0.0.1 --port 8010
