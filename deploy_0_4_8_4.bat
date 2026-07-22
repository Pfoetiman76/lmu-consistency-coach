@echo off
REM ============================================================
REM  LMU Consistency Coach - Deploy 0.4.8.4
REM  Force-Push main + Tag v0.4.8.4 -> loest release.yml (CI) aus.
REM  Voraussetzung: git + GitHub CLI (gh) mit Browser-Login.
REM  Doppelklick in einem frischen, entpackten Versions-Ordner.
REM ============================================================
setlocal
set REPO=https://github.com/Pfoetiman76/lmu-consistency-coach.git
set VERSION=0.4.8.4
set TAG=v%VERSION%

cd /d "%~dp0"
echo.
echo === Deploy LMU Consistency Coach %VERSION% ===
echo Ordner: %CD%
echo.

REM --- git-Identitaet sicherstellen (Fallback, falls global nicht gesetzt) ---
git config user.email >nul 2>&1 || git config user.email "deploy@lmu-coach.local"
git config user.name  >nul 2>&1 || git config user.name  "LMU Coach Deploy"

REM --- Repo initialisieren, falls noch keins vorhanden ---
if not exist ".git" (
    echo [1/6] git init
    git init -b main || goto :err
) else (
    echo [1/6] vorhandenes Repo, ueberspringe init
    git checkout -B main >nul 2>&1
)

echo [2/6] Remote setzen
git remote remove origin >nul 2>&1
git remote add origin %REPO% || goto :err

echo [3/6] Dateien stagen
git add -A || goto :err

echo [4/6] Commit
git commit -m "Release %VERSION%: Live-Coaching (F11), helles Design, Header-Fix" || echo (nichts zu committen, weiter)

echo [5/6] Force-Push main
git push -f origin main || goto :err

echo [6/6] Tag %TAG% setzen und pushen (triggert CI-Release)
git tag -f %TAG% || goto :err
git push -f origin %TAG% || goto :err

echo.
echo === Fertig. CI baut jetzt den Installer fuer %TAG%. ===
echo Release-Fortschritt: https://github.com/Pfoetiman76/lmu-consistency-coach/actions
echo.
pause
exit /b 0

:err
echo.
echo *** FEHLER beim Deploy - siehe Ausgabe oben. ***
echo Pruefe: git installiert? gh eingeloggt? Internet? Repo-Rechte?
echo.
pause
exit /b 1
