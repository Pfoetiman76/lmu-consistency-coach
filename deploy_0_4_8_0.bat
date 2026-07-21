@echo off
setlocal
cd /d "%~dp0"
echo == Deploy LMU Consistency Coach 0.4.8.0 ==
where git >nul 2>nul || (echo [FEHLER] git fehlt: https://git-scm.com/download/win ^& pause ^& exit /b 1)
if not exist ".git" git init
git config user.name  >nul 2>nul || git config user.name  "Pfoetiman76"
git config user.email >nul 2>nul || git config user.email "Pfoetiman76@users.noreply.github.com"
git add -A
git commit -m "Release 0.4.8.0" 2>nul
git branch -M main
git remote get-url origin >nul 2>nul || git remote add origin https://github.com/Pfoetiman76/lmu-consistency-coach.git
echo Pushe Stand nach GitHub (ueberschreibt main mit 0.4.8.0) ...
git push -f origin main
if errorlevel 1 goto PUSHFAIL
git tag v0.4.8.0 2>nul
git push origin v0.4.8.0
echo.
echo Fertig. Der Installer wird jetzt gebaut:
echo    https://github.com/Pfoetiman76/lmu-consistency-coach/actions
echo Nach ~5-10 Min erscheint das 0.4.8.0-Release mit Installer hier:
echo    https://github.com/Pfoetiman76/lmu-consistency-coach/releases
goto END
:PUSHFAIL
echo [FEHLER] Push fehlgeschlagen. Bist du eingeloggt? Sonst einmal: gh auth login
:END
pause
