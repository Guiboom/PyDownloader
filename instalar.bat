@echo off
setlocal
title Instalador - PyMediaDownloader
color 0B

echo.
echo ==========================================
echo       PyMediaDownloader - Instalador
echo ==========================================
echo.
echo Este instalador verificara e instalara:
echo   - Python 3
echo   - yt-dlp
echo   - FFmpeg
echo.
echo Deseja continuar?
choice /C SN /N /M "[S] Sim / [N] Nao: "

if errorlevel 2 exit /b 0

echo.
echo [1/3] Verificando Python...

where python >nul 2>&1
if errorlevel 1 (
    echo Python nao encontrado. Instalando...
    winget install --id Python.Python.3.12 --exact --accept-source-agreements
    if errorlevel 1 (
        echo ERRO: Nao foi possivel instalar o Python.
        echo Instale-o manualmente em https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

echo.
echo [2/3] Instalando ou atualizando yt-dlp...

python -m pip install --user --upgrade pip yt-dlp
if errorlevel 1 (
    echo ERRO: Falha ao instalar o yt-dlp.
    pause
    exit /b 1
)

echo.
echo [3/3] Verificando FFmpeg...

where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo FFmpeg nao encontrado. Instalando...
    winget install --id Gyan.FFmpeg --exact --accept-source-agreements
    if errorlevel 1 (
        echo AVISO: Nao foi possivel instalar o FFmpeg.
        echo Instale-o manualmente pelo gerenciador de pacotes.
        pause
        exit /b 1
    )
) else (
    echo FFmpeg ja esta instalado.
)

echo.
echo ==========================================
echo       Instalacao finalizada!
echo ==========================================
echo.
echo Para iniciar o aplicativo, execute:
echo     python main.py
echo.

choice /C SN /N /M "Deseja iniciar o PyMediaDownloader agora? [S/N]: "
if errorlevel 2 goto fim

if exist "%~dp0main.py" (
    cd /d "%~dp0"
    python main.py
) else (
    echo ERRO: main.py nao encontrado na pasta do instalador.
)

:fim
echo.
pause
endlocal