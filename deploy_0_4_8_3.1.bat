@echo off
REM ================================================================
REM  LMU Consistency Coach - Deploy 0.4.8.3.1
REM  Push main + Tag v0.4.8.3.1  ->  GitHub Actions baut den Installer
REM ================================================================
setlocal
set REPO=https://github.com/Pfoetiman76/lmu-consistency-coach.git
set VERSION=0.4.8.3.1
set TAG=v%VERSION%

cd /d "%~dp0"

where git >nul 2>&1
if errorlevel 1 (
  echo [FEHLER] git nicht gefunden. Bitte Git for Windows installieren.
  pause & exit /b 1
)

if not exist ".git" (
  git init
  git branch -M main
  git remote add origin %REPO%
) else (
  git remote set-url origin %REPO% 2>nul || git remote add origin %REPO%
)

REM git-Identitaet sicherstellen (sonst schlaegt commit fehl - war der Fehler beim ersten Setup)
git config user.email >nul 2>&1 || git config user.email "pfoetiman76@users.noreply.github.com"
git config user.name  >nul 2>&1 || git config user.name  "Pfoetiman76"

git add -A
git commit -m "Release %TAG% - Header-Feinschliff (Untertitel aus Version, Titelblock zentriert)" || echo (nichts zu committen)

echo Pushe main ...
git push -u origin main --force
if errorlevel 1 ( echo [FEHLER] push main fehlgeschlagen. & pause & exit /b 1 )

echo Setze Tag %TAG% ...
git tag -d %TAG% 2>nul
git push origin :refs/tags/%TAG% 2>nul
git tag %TAG%
git push origin %TAG%
if errorlevel 1 ( echo [FEHLER] Tag-Push fehlgeschlagen. & pause & exit /b 1 )

echo.
echo Fertig. GitHub Actions baut jetzt den Installer fuer %TAG%.
echo Release: https://github.com/Pfoetiman76/lmu-consistency-coach/releases
pause
endlocal