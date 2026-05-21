# Fork hubsonsss/TSP-Bottleneck na konto sandrawar i push main
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

gh auth status | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Brak logowania. Uruchom: gh auth login -h github.com -p https -w" -ForegroundColor Yellow
    exit 1
}

$login = gh api user -q .login
Write-Host "Zalogowano jako: $login" -ForegroundColor Green

# Utworz fork (jesli nie istnieje)
$forkInfo = gh repo fork hubsonsss/TSP-Bottleneck --clone=false 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host $forkInfo -ForegroundColor Red
    exit 1
}
$forkUrl = "https://github.com/$login/TSP-Bottleneck.git"

git remote remove fork 2>$null
git remote add fork $forkUrl
Write-Host "Push do: $forkUrl" -ForegroundColor Cyan
git push -u fork main

Write-Host "`nGotowe. Fork: https://github.com/$login/TSP-Bottleneck" -ForegroundColor Green
Write-Host "Utworz PR: gh pr create --repo hubsonsss/TSP-Bottleneck --head ${login}:main --title 'Add test suite'" -ForegroundColor Cyan
