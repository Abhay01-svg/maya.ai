@echo off
REM ============================================================
REM Maya AI - Push Local PC Code to GitHub
REM Script: Push code from local PC backup to GitHub repository
REM ============================================================

setlocal enabledelayedexpansion

REM Color codes for output
set "RESET=[0m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"

echo.
echo %BLUE%╔═══════════════════════════════════════════════════════════╗%RESET%
echo %BLUE%║                                                           ║%RESET%
echo %BLUE%║        🚀 MAYA AI - LOCAL TO GITHUB CODE PUSH             ║%RESET%
echo %BLUE%║                                                           ║%RESET%
echo %BLUE%╚═══════════════════════════════════════════════════════════╝%RESET%
echo.

REM ============================================================
REM CONFIGURATION
REM ============================================================

set "LOCAL_BACKUP_PATH=C:\Users\abhay\OneDrive\Desktop\onedrive backup\Maya project updateed code of python"
set "REPO_PATH=%CD%"
set "GITHUB_REPO=Abhay01-svg/maya.ai"
set "BRANCH=update-from-pc"
set "COMMIT_MESSAGE=Update from PC backup - %date% %time%"

echo %YELLOW%[CONFIG] Local Backup Path:%RESET%
echo   %LOCAL_BACKUP_PATH%
echo.
echo %YELLOW%[CONFIG] Repository Path:%RESET%
echo   %REPO_PATH%
echo.
echo %YELLOW%[CONFIG] Target Branch:%RESET%
echo   %BRANCH%
echo.

REM ============================================================
REM VALIDATION
REM ============================================================

echo %BLUE%[STEP 1] Validating paths...%RESET%

if not exist "%LOCAL_BACKUP_PATH%" (
    echo %RED%❌ ERROR: Local backup path does not exist!%RESET%
    echo   Path: %LOCAL_BACKUP_PATH%
    pause
    exit /b 1
)
echo %GREEN%✅ Local backup path found%RESET%

if not exist "%REPO_PATH%\.git" (
    echo %RED%❌ ERROR: Not a Git repository!%RESET%
    echo   Path: %REPO_PATH%
    pause
    exit /b 1
)
echo %GREEN%✅ Git repository found%RESET%
echo.

REM ============================================================
REM CHECK GIT STATUS
REM ============================================================

echo %BLUE%[STEP 2] Checking Git status...%RESET%
cd /d "%REPO_PATH%"
git status
echo.

REM ============================================================
REM SWITCH TO BRANCH
REM ============================================================

echo %BLUE%[STEP 3] Switching to branch: %BRANCH%%RESET%
git fetch origin
git checkout %BRANCH% 2>nul
if errorlevel 1 (
    echo %YELLOW%⚠️  Branch does not exist. Creating new branch...%RESET%
    git checkout -b %BRANCH%
)
echo %GREEN%✅ Switched to branch: %BRANCH%%RESET%
echo.

REM ============================================================
REM COPY FILES FROM LOCAL BACKUP
REM ============================================================

echo %BLUE%[STEP 4] Copying files from local backup...%RESET%
echo   Source: %LOCAL_BACKUP_PATH%
echo   Destination: %REPO_PATH%
echo.

REM Copy Python files
if exist "%LOCAL_BACKUP_PATH%\*.py" (
    echo %YELLOW%  📄 Copying Python files (.py)...%RESET%
    xcopy "%LOCAL_BACKUP_PATH%\*.py" "%REPO_PATH%\maya_ai\" /Y /Q 2>nul
    echo %GREEN%  ✅ Python files copied%RESET%
)

REM Copy modules directory
if exist "%LOCAL_BACKUP_PATH%\modules" (
    echo %YELLOW%  📂 Copying modules directory...%RESET%
    xcopy "%LOCAL_BACKUP_PATH%\modules" "%REPO_PATH%\maya_ai\modules\" /S /Y /Q 2>nul
    echo %GREEN%  ✅ Modules directory copied%RESET%
)

REM Copy requirements
if exist "%LOCAL_BACKUP_PATH%\requirements.txt" (
    echo %YELLOW%  📋 Copying requirements.txt...%RESET%
    copy "%LOCAL_BACKUP_PATH%\requirements.txt" "%REPO_PATH%\maya_ai\" /Y >nul
    echo %GREEN%  ✅ Requirements copied%RESET%
)

REM Copy config
if exist "%LOCAL_BACKUP_PATH%\config.py" (
    echo %YELLOW%  ⚙️  Copying config.py...%RESET%
    copy "%LOCAL_BACKUP_PATH%\config.py" "%REPO_PATH%\maya_ai\" /Y >nul
    echo %GREEN%  ✅ Config copied%RESET%
)

REM Copy templates
if exist "%LOCAL_BACKUP_PATH%\templates" (
    echo %YELLOW%  🎨 Copying templates directory...%RESET%
    xcopy "%LOCAL_BACKUP_PATH%\templates" "%REPO_PATH%\maya_ai\templates\" /S /Y /Q 2>nul
    echo %GREEN%  ✅ Templates copied%RESET%
)

echo.
echo %GREEN%✅ All files copied successfully!%RESET%
echo.

REM ============================================================
REM GIT STAGING
REM ============================================================

echo %BLUE%[STEP 5] Staging files for Git...%RESET%
git add -A
echo %GREEN%✅ Files staged%RESET%
echo.

REM ============================================================
REM SHOW CHANGES
REM ============================================================

echo %BLUE%[STEP 6] Showing staged changes...%RESET%
git status
echo.

REM ============================================================
REM COMMIT
REM ============================================================

echo %BLUE%[STEP 7] Committing changes...%RESET%
echo   Commit Message: %COMMIT_MESSAGE%
git commit -m "%COMMIT_MESSAGE%"
if errorlevel 1 (
    echo %YELLOW%⚠️  No changes to commit or commit failed%RESET%
) else (
    echo %GREEN%✅ Changes committed%RESET%
)
echo.

REM ============================================================
REM PUSH TO GITHUB
REM ============================================================

echo %BLUE%[STEP 8] Pushing to GitHub...%RESET%
echo   Repository: %GITHUB_REPO%
echo   Branch: %BRANCH%
echo.

git push origin %BRANCH%
if errorlevel 1 (
    echo %RED%❌ Push failed!%RESET%
    echo.
    echo %YELLOW%Troubleshooting tips:%RESET%
    echo   1. Check your GitHub credentials
    echo   2. Verify remote URL: git remote -v
    echo   3. Ensure you have push permissions
    echo   4. Try: git push -u origin %BRANCH% --force
    pause
    exit /b 1
)
echo %GREEN%✅ Successfully pushed to GitHub!%RESET%
echo.

REM ============================================================
REM SUMMARY
REM ============================================================

echo %BLUE%╔═══════════════════════════════════════════════════════════╗%RESET%
echo %BLUE%║                    PUSH COMPLETED! ✅                     ║%RESET%
echo %BLUE%╚═══════════════════════════════════════════════════════════╝%RESET%
echo.
echo %GREEN%📊 Summary:%RESET%
echo   Repository: %GITHUB_REPO%
echo   Branch: %BRANCH%
echo   Source: %LOCAL_BACKUP_PATH%
echo   Time: %date% %time%
echo.
echo %GREEN%🔗 View on GitHub:%RESET%
echo   https://github.com/%GITHUB_REPO%/tree/%BRANCH%
echo.
echo %GREEN%📝 Next Steps:%RESET%
echo   1. Review changes at: https://github.com/%GITHUB_REPO%/tree/%BRANCH%
echo   2. Create Pull Request if needed
echo   3. Merge to main branch when ready
echo.

REM ============================================================
REM CREATE PULL REQUEST OPTION
REM ============================================================

echo %YELLOW%Would you like to create a Pull Request? (Y/N)%RESET%
set /p create_pr="Enter choice: "
if /i "%create_pr%"=="Y" (
    echo.
    echo %BLUE%Creating PR details...%RESET%
    echo   Title: Update from PC - Python Code Updated
    echo   Branch: %BRANCH% ^> main
    echo.
    echo %YELLOW%Please visit:%RESET%
    echo   https://github.com/%GITHUB_REPO%/compare/main...%BRANCH%
    echo.
    echo %YELLOW%To create a PR automatically, use:%RESET%
    echo   gh pr create --title "Update from PC" --body "Latest Python code updates" --base main --head %BRANCH%
    echo.
)

echo.
echo %BLUE%✅ Script completed successfully!%RESET%
echo.

pause
