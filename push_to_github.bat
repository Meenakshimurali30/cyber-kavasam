@echo off
setlocal
echo ========================================================
echo        Cyber Kavasam - Push to Your GitHub
echo ========================================================
echo.
cd /d "%~dp0"

echo Your local repository is ready on branch 'main'.
echo.

set /p REPO_URL="Paste your GitHub repository URL (e.g. https://github.com/username/cyber-kavasam.git): "
if "%REPO_URL%"=="" (
    echo Error: No repository URL entered.
    pause
    exit /b 1
)

echo.
echo [1/3] Configuring remote origin...
git remote remove origin >nul 2>&1
git remote add origin %REPO_URL%

echo [2/3] Setting default branch to 'main'...
git branch -M main

echo [3/3] Uploading code to GitHub...
echo (If prompted, sign in via browser or Personal Access Token)
git push -u origin main

if errorlevel 1 (
    echo.
    echo [!] Push encountered an issue.
    echo Common reasons:
    echo 1. The GitHub repository was initialized with a README already (create an empty repo on GitHub without checking "Add README").
    echo 2. If it has a README on GitHub, run: git pull origin main --rebase and then try again.
    echo 3. Check that you are logged into your GitHub account.
) else (
    echo.
    echo ========================================================
    echo  SUCCESS! Your project is now published on GitHub!
    echo ========================================================
)
echo.
pause
