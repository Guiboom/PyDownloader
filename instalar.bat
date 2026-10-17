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
echo   - Python 3
echo   - pip atualizado
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
        echo ERRO: winget nao esta disponivel.
        echo Instale Python em:
        echo https://www.python.org/downloads/windows/
        pause
        exit /b 1
    )

    echo Instalando Python 3.12...

    winget install --id Python.Python.3.12 --exact --accept-package-agreements --accept-source-agreements

    echo.
    echo Verificando Python...

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
        echo ERRO: Python instalado, mas nao localizado.
        echo Reinicie o terminal e execute novamente.
        pause
        exit /b 1
    )
)

echo Python encontrado:
%PYTHON_CMD% --version

echo.
echo ==========================================
echo [2/4] Atualizando pip
echo ==========================================

%PYTHON_CMD% -m ensurepip --upgrade >nul 2>&1

%PYTHON_CMD% -m pip install --upgrade pip

if errorlevel 1 (
    echo.
    echo AVISO: Nao foi possivel atualizar o pip.
    echo Tentando continuar com a versao instalada...
)

echo.
echo ==========================================
echo [3/4] Instalando yt-dlp
echo ==========================================

%PYTHON_CMD% -m pip install --user --upgrade yt-dlp

if errorlevel 1 (
    echo.
    echo ERRO: Falha ao instalar yt-dlp.
    echo Verifique sua conexao com a internet.
    pause
    exit /b 1
)

%PYTHON_CMD% -m yt_dlp --version >nul 2>&1

if errorlevel 1 (
    echo ERRO: yt-dlp nao esta funcionando.
    pause
    exit /b 1
)

echo yt-dlp instalado e funcionando!

echo.
echo ==========================================
echo [4/4] Instalando e verificando FFmpeg
echo ==========================================

set "FFMPEG_EXE="

REM 1. Verifica se o comando ja funciona.
where ffmpeg >nul 2>&1
if not errorlevel 1 (
    for /f "delims=" %%F in ('where ffmpeg 2^>nul') do (
        if not defined FFMPEG_EXE set "FFMPEG_EXE=%%F"
    )
)

REM 2. Verifica os atalhos do WinGet.
if not defined FFMPEG_EXE (
    if exist "%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe" (
        set "FFMPEG_EXE=%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe"
    )
)

REM 3. Se nao encontrou, tenta instalar.
if not defined FFMPEG_EXE (
    echo FFmpeg nao encontrado. Verificando winget...

    where winget >nul 2>&1
    if errorlevel 1 goto ffmpeg_manual

    echo.
    echo Instalando FFmpeg...

    winget install --id Gyan.FFmpeg --exact --accept-package-agreements --accept-source-agreements

    REM O WinGet pode atualizar o PATH sem atualizar o terminal atual.
    if exist "%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe" (
        set "FFMPEG_EXE=%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe"
    )
)

REM 4. Verifica novamente o comando.
if not defined FFMPEG_EXE (
    for /f "delims=" %%F in ('where ffmpeg 2^>nul') do (
        if not defined FFMPEG_EXE set "FFMPEG_EXE=%%F"
    )
)

REM 5. Valida o executavel encontrado.
if defined FFMPEG_EXE (
    "%FFMPEG_EXE%" -version >nul 2>&1
    if not errorlevel 1 goto ffmpeg_sucesso
)

REM 6. Procura uma instalacao existente nos locais comuns.
if exist "%LOCALAPPDATA%\Microsoft\WinGet\Packages" (
    for /f "delims=" %%F in ('where /r "%LOCALAPPDATA%\Microsoft\WinGet\Packages" ffmpeg.exe 2^>nul') do (
        if not defined FFMPEG_EXE set "FFMPEG_EXE=%%F"
    )
)

if defined FFMPEG_EXE (
    "%FFMPEG_EXE%" -version >nul 2>&1
    if not errorlevel 1 goto ffmpeg_sucesso
)

goto ffmpeg_manual

:ffmpeg_sucesso
echo.
echo FFmpeg instalado e funcionando!
echo Executavel:
echo %FFMPEG_EXE%

REM Disponibiliza o FFmpeg para este processo e para o programa.
for %%D in ("%FFMPEG_EXE%") do set "PATH=%%~dpD;%PATH%"

goto iniciar

:ffmpeg_manual
echo.
echo ==========================================
echo AVISO: Nao foi possivel localizar FFmpeg
echo ==========================================
echo.
echo Se o WinGet informou que a instalacao foi
echo concluida, feche o terminal e tente novamente.
echo.
echo Download:
echo https://www.gyan.dev/ffmpeg/builds/
echo.

choice /C SN /N /M "Continuar sem FFmpeg? [S/N]: "
if errorlevel 2 (
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
    echo AVISO: main.py nao encontrado nesta pasta.
    echo Dependencias instaladas, mas o programa
    echo nao pode ser iniciado.
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

