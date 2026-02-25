@echo off
title ORION GIT UPLOAD
color 0a

cd /d %~dp0

echo ========================================
echo   ORION - SUBIR PARA O GITHUB
echo ========================================
echo.

git status

git add .

git diff --cached --quiet
if %errorlevel%==0 (
  echo.
  echo Nenhuma mudanca para commit.
  echo.
  pause
  exit /b 0
)

git commit -m "Update ORION Platform"
git push

echo.
echo ========================================
echo   FINALIZADO
echo ========================================
pause