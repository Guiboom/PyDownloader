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
echo Este instalador verificara:
echo   - Python 3.10 ou superior
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
        echo.
        echo Durante a instalacao, marque Add Python to PATH.
        pause
        exit /b 1
    )

    echo Instalando Python 3...
    winget install --id Python.Python.3.12 --exact --scope user --accept-package-agreements --accept-source-agreements

    echo.
    echo Verificando a instalacao...

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
        echo Reinicie o terminal ou instale o Python manualmente.
        echo https://www.python.org/downloads/windows/
        pause
        exit /b 1
    )
)

echo Python localizado.
%PYTHON_CMD% --version

echo.
echo ==========================================
echo [2/4] Verificando pip
echo ==========================================

%PYTHON_CMD% -m pip --version >nul 2>&1
if errorlevel 1 (
    echo Tentando instalar o pip...
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

echo yt-dlp instalado com sucesso.

echo.
echo ==========================================
echo [4/4] Verificando FFmpeg
echo ==========================================

where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo FFmpeg nao encontrado.

    where winget >nul 2>&1
    if errorlevel 1 (
        echo.
        echo AVISO: winget nao esta disponivel.
        echo Instale o FFmpeg manualmente:
        echo https://ffmpeg.org/download.html
        goto iniciar
    )

    echo Tentando instalar FFmpeg...
    winget install --id Gyan.FFmpeg --exact --scope user --accept-package-agreements --accept-source-agreements

    echo.
    echo Verificando FFmpeg...

    where ffmpeg >nul 2>&1
    if errorlevel 1 (
        echo AVISO: FFmpeg pode ter sido instalado, mas nao esta no PATH.
        echo Reinicie o terminal e verifique novamente.
    ) else (
        echo FFmpeg instalado com sucesso.
    )
) else (
    echo FFmpeg ja esta instalado.
    ffmpeg -version 2>nul | findstr /B /C:"ffmpeg version"
)

:iniciar
echo.
echo ==========================================
echo       Instalacao concluida
echo ==========================================
echo.

if not exist "%~dp0main.py" (
    echo AVISO: main.py nao foi encontrado nesta pasta.
    echo As dependencias foram instaladas, mas o programa nao pode ser iniciado.
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
    echo Verifique as mensagens exibidas acima.
)

:fim
echo.
pause
endlocal
```
