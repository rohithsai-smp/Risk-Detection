# Digital Risk Shield - Automated GitHub Uploader (PowerShell)

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  DIGITAL RISK SHIELD - AUTOMATED GITHUB UPLOADER" -ForegroundColor White
Write-Host "  Target: https://github.com/rohithsai-smp/digital-risk-shield.git" -ForegroundColor Gray
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Git\cmd",
        "C:\Program Files\Git\cmd"
    )
    foreach ($cand in $candidates) {
        if (Test-Path (Join-Path $cand "git.exe")) {
            $env:Path = "$cand;$env:Path"
            break
        }
    }
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Git is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please download & install Git from: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "After installing, close and reopen PowerShell and run this script again."
    Read-Host "Press Enter to exit"
    exit
}

Write-Host "[OK] Git is detected!" -ForegroundColor Green
$repoUrl = "https://github.com/rohithsai-smp/digital-risk-shield.git"

Write-Host ""
Write-Host "Step 1: Initializing Git repository..." -ForegroundColor Yellow
git init

Write-Host "Step 2: Staging all files..." -ForegroundColor Yellow
git add .

Write-Host "Step 3: Committing files..." -ForegroundColor Yellow
git commit -m "Initial commit: Digital Risk Shield platform"

Write-Host "Step 4: Setting branch to main..." -ForegroundColor Yellow
git branch -M main

Write-Host "Step 5: Configuring remote origin..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin $repoUrl

Write-Host "Step 6: Pushing code to GitHub..." -ForegroundColor Yellow
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host "  SUCCESS! Project successfully uploaded to:" -ForegroundColor Green
    Write-Host "  https://github.com/rohithsai-smp/digital-risk-shield" -ForegroundColor Cyan
    Write-Host "======================================================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "If prompted, please complete the GitHub sign-in prompt to authorize the upload." -ForegroundColor Yellow
}
