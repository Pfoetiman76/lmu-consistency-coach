@echo off
setlocal
cd /d "%~dp0"
echo == Release 0.4.8.0 veroeffentlichen ==
git add -A
git commit -m "Release 0.4.8.0"
git tag v0.4.8.0 2>nul
git push origin main
git push origin v0.4.8.0
echo.
echo Fertig. Installer-Build laeuft: https://github.com/Pfoetiman76/lmu-consistency-coach/actions
pause
