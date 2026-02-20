@echo off
title ORION GIT UPLOAD
color 0a

echo ========================================
echo   ENVIANDO ORION PARA O GITHUB
echo ========================================
echo.

cd /d %~dp0

echo Status atual:
git status
echo.

echo Adicionando arquivos...
git add .

echo.
echo Criando commit...
git commit -m "Update ORION Platform"

echo.
echo Enviando para GitHub...
git push

echo.
echo ========================================
echo   FINALIZADO
echo ========================================
pause
