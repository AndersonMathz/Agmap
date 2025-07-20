@echo off
chcp 65001 >nul
title WebGIS - Servidor Flask

echo.
echo ========================================
echo    WebGIS - Sistema de Informações
echo ========================================
echo.

echo Verificando arquivos necessários...
if not exist "app.py" (
    echo ❌ Erro: Arquivo app.py não encontrado!
    echo Certifique-se de que está na pasta correta.
    pause
    exit /b 1
)

if not exist "config.py" (
    echo ❌ Erro: Arquivo config.py não encontrado!
    pause
    exit /b 1
)

if not exist "models.py" (
    echo ❌ Erro: Arquivo models.py não encontrado!
    pause
    exit /b 1
)

echo ✅ Arquivos principais encontrados!

if not exist "WEBGIS_ANDERSON\OSM_BLACK" (
    echo ⚠️  Aviso: Pasta de dados não encontrada!
    echo    O WebGIS pode não funcionar sem os arquivos KML.
    echo.
)

echo.
echo 🚀 Iniciando servidor WebGIS Flask...
echo.
echo 📋 Instruções:
echo 1. O navegador será aberto automaticamente
echo 2. Faça login com suas credenciais
echo 3. Use os controles na sidebar para navegar
echo 4. Para parar o servidor, feche esta janela
echo.

python app.py

echo.
echo 🛑 Servidor parado.
pause 