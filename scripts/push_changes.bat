@echo off
REM Quick commit and push — run from repo root:
REM   scripts\push_changes.bat "Your commit message"
REM On dev branch by default after workflow setup.

if "%~1"=="" (
    echo Usage: scripts\push_changes.bat "commit message"
    exit /b 1
)

cd /d "%~dp0.."
git add .
git commit -m "%~1"
if errorlevel 1 (
    echo Commit failed. Fix issues and try again.
    exit /b 1
)
git push
if errorlevel 1 (
    echo Push failed. Check branch and remote.
    exit /b 1
)
echo Done.
