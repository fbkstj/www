@echo off
cd /d "%~dp0"
echo Adding changes to Git (only files already on the site)...
git add -u
echo Committing changes...
git commit -m "Update site"
echo Pulling latest from GitHub...
git pull --rebase origin main
if errorlevel 1 (
    echo.
    echo [ERROR] Pull failed - please resolve conflicts before pushing.
    pause
    exit /b 1
)
echo Pushing to GitHub...
git push origin main
echo Done!
pause
