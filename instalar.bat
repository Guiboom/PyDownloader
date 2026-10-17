```bat
@echo off
setlocal EnableExtensions
title Instalador - PyMediaDownloader
color 0B

cd /d "%~dp0"

echo.
echo ==========================================
echo       PyMediaDownloader - Instalador
echo ==========================================
echo.
echo Este instalador verificara e instalara:
echo   - Python 3
echo   - pip
echo   - yt-dlp
echo   - FFmpeg
echo.

choice /C SN /N /M "[S] Sim / [N] Nao: "
if errorlevel 2 exit /b 0

echo.
echo ==========================================
echo [1/4] Verificando Python
echo ==========================================

set "PYTHON_CMD="

where py >nul 2>&1
if not errorlevel 1 (
    py -3 --version >nul 2>&1
    if not errorlevel 1 set "PYTHON_CMD=py -3"
)

if not defined PYTHON_CMD (
    where python >nul 2>&1
    if not errorlevel 1 (
        python --version >nul 2>&1
        if not errorlevel 1 set "PYTHON_CMD=python"
    )
)

if not defined PYTHON_CMD (
    echo Python nao encontrado.

    where winget >nul 2>&1
    if errorlevel 1 (
        echo.
        echo ERRO: winget nao esta disponivel.
        echo Instale o Python manualmente:
        echo https://www.python.org/downloads/windows/
        pause
        exit /b 1
    )

    echo Instalando Python 3.12...

    winget install --id Python.Python.3.12 --exact --accept-package-agreements --accept-source-agreements

    echo.
    echo Verificando Python instalado...

    where py >nul 2>&1
    if not errorlevel 1 (
        py -3 --version >nul 2>&1
        if not errorlevel 1 set "PYTHON_CMD=py -3"
    )

    if not defined PYTHON_CMD (
        where python >nul 2>&1
        if not errorlevel 1 (
            python --version >nul 2>&1
            if not errorlevel 1 set "PYTHON_CMD=python"
        )
    )

    if not defined PYTHON_CMD (
        echo.
        echo ERRO: Python instalado, mas nao foi localizado.
        echo Reinicie o terminal e execute novamente.
        pause
        exit /b 1
    )
)

echo Python encontrado:
%PYTHON_CMD% --version

echo.
echo ==========================================
echo [2/4] Verificando pip
echo ==========================================

%PYTHON_CMD% -m pip --version >nul 2>&1

if errorlevel 1 (
    echo Tentando configurar o pip...
    %PYTHON_CMD% -m ensurepip --upgrade

    if errorlevel 1 (
        echo ERRO: Nao foi possivel configurar o pip.
        pause
        exit /b 1
    )
)

echo Atualizando pip...
%PYTHON_CMD% -m pip install --user --upgrade pip

if errorlevel 1 (
    echo AVISO: Nao foi possivel atualizar o pip.
    echo Continuando com a versao existente...
)

echo.
echo ==========================================
echo [3/4] Instalando yt-dlp
echo ==========================================

%PYTHON_CMD% -m pip install --user --upgrade yt-dlp

if errorlevel 1 (
    echo.
    echo ERRO: Falha ao instalar o yt-dlp.
    echo Verifique sua conexao com a internet.
    pause
    exit /b 1
)

%PYTHON_CMD% -m yt_dlp --version >nul 2>&1

if errorlevel 1 (
    echo ERRO: O yt-dlp nao foi instalado corretamente.
    pause
    exit /b 1
)

echo yt-dlp instalado com sucesso!

echo.
echo ==========================================
echo [4/4] Instalando e verificando FFmpeg
echo ==========================================

set "FFMPEG_OK="

where ffmpeg >nul 2>&1
if not errorlevel 1 (
    ffmpeg -version >nul 2>&1
    if not errorlevel 1 set "FFMPEG_OK=1"
)

if defined FFMPEG_OK (
    echo FFmpeg ja esta instalado e funcionando.
    goto iniciar
)

echo FFmpeg nao encontrado. Verificando winget...

where winget >nul 2>&1
if errorlevel 1 (
    echo.
    echo AVISO: winget nao esta disponivel.
    goto ffmpeg_manual
)

echo.
echo Tentando instalar FFmpeg...
echo.

winget install --id Gyan.FFmpeg.Shared --exact --accept-package-agreements --accept-source-agreements

echo.
echo Verificando FFmpeg novamente...

where ffmpeg >nul 2>&1
if not errorlevel 1 (
    ffmpeg -version >nul 2>&1
    if not errorlevel 1 (
        set "FFMPEG_OK=1"
        goto ffmpeg_sucesso
    )
)

echo.
echo FFmpeg ainda nao foi localizado no PATH.
echo Tentando localizar a instalacao...

set "FFMPEG_DIR=%LOCALAPPDATA%\Microsoft\WinGet\Links"

if exist "%FFMPEG_DIR%\ffmpeg.exe" (
    set "PATH=%FFMPEG_DIR%;%PATH%"
)

where ffmpeg >nul 2>&1
if not errorlevel 1 (
    ffmpeg -version >nul 2>&1
    if not errorlevel 1 (
        set "FFMPEG_OK=1"
        goto ffmpeg_sucesso
    )
)

echo.
echo Tentando instalar a versao padrao do FFmpeg...

winget install --id Gyan.FFmpeg --exact --accept-package-agreements --accept-source-agreements

echo.
echo Verificando instalacao...

where ffmpeg >nul 2>&1
if not errorlevel 1 (
    ffmpeg -version >nul 2>&1
    if not errorlevel 1 (
        set "FFMPEG_OK=1"
        goto ffmpeg_sucesso
    )
)

goto ffmpeg_manual

:ffmpeg_sucesso
echo.
echo FFmpeg instalado e funcionando!
goto iniciar

:ffmpeg_manual
echo.
echo ==========================================
echo AVISO: FFmpeg nao foi localizado
echo ==========================================
echo.
echo O programa pode funcionar sem FFmpeg,
echo mas algumas conversoes e downloads podem falhar.
echo.
echo Download oficial:
echo https://www.gyan.dev/ffmpeg/builds/
echo.
echo Se instalar manualmente, adicione a pasta bin
echo do FFmpeg ao PATH do Windows.
echo.

choice /C SN /N /M "Deseja continuar mesmo sem FFmpeg? [S/N]: "
if errorlevel 2 (
    echo.
    echo Instalacao interrompida pelo usuario.
    pause
    exit /b 1
)

:iniciar
echo.
echo ==========================================
echo       Instalacao concluida
echo ==========================================
echo.

if not exist "%~dp0main.py" (
    echo AVISO: main.py nao foi encontrado nesta pasta.
    echo As dependencias foram instaladas.
    goto fim
)

choice /C SN /N /M "Deseja iniciar o PyMediaDownloader agora? [S/N]: "
if errorlevel 2 goto fim

echo.
echo Iniciando PyMediaDownloader...
echo.

%PYTHON_CMD% "%~dp0main.py"

if errorlevel 1 (
    echo.
    echo O programa foi encerrado com erro.
)

:fim
echo.
pause
endlocal
```
