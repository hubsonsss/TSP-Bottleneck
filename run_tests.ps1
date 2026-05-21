# Uruchomienie testów Bottleneck TSP
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python nie znaleziony w PATH."
}

python -m pip install -q -r requirements-dev.txt
Write-Host "`n=== Testy poprawnosci ===" -ForegroundColor Cyan
python -m pytest tests/test_correctness.py

Write-Host "`n=== Testy wydajnosci (performance) ===" -ForegroundColor Cyan
python -m pytest tests/test_performance.py -m performance -s
