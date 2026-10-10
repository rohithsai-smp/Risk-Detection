@echo off
setlocal enabledelayedexpansion

echo ======================================================================
echo   DIGITAL RISK SHIELD - AUTOMATED GITHUB UPLOADER
echo   Repository: https://github.com/rohithsai-smp/digital-risk-shield.git
echo ======================================================================
echo.

where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    if exist "%LOCALAPPDATA%\Programs\Git\cmd\git.exe" (
        set "PATH=%LOCALAPPDATA%\Programs\Git\cmd;%PATH%"
    ) else if exist "C:\Program Files\Git\cmd\git.exe" (
        set "PATH=C:\Program Files\Git\cmd;%PATH%"
    )
)

where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Git is not installed or not in PATH.
    echo Please install Git quickly from: https://git-scm.com/download/win
    echo After installing, reopen terminal and run this script again.
    pause
    exit /b 1
)

echo [OK] Git is detected!
set REPO_URL=https://github.com/rohithsai-smp/digital-risk-shield.git

echo.
echo Step 1: Initializing Git repository...
git init

echo Step 2: Staging all project files...
git add .

echo Step 3: Committing files...
git commit -m "Initial commit: Digital Risk Shield platform"

echo Step 4: Setting branch to main...
git branch -M main

echo Step 5: Linking remote repository...
git remote remove origin >nul 2>nul
git remote add origin %REPO_URL%

echo Step 6: Pushing to GitHub...
git push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo ======================================================================
    echo   SUCCESS! Your project is now live on GitHub:
    echo   https://github.com/rohithsai-smp/digital-risk-shield
    echo ======================================================================
) else (
    echo.
    echo [NOTE] If a GitHub login window appears, please authorize the push.
)

echo.
pause
