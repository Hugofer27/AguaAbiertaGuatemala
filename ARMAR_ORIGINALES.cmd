@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul

echo Agua Abierta Guatemala - paquete de archivos originales
echo.
echo Arrastre a esta ventana la carpeta donde guarda las tres investigaciones
echo (Claude, ChatGPT/Codex y Antigravity) y presione Enter.
echo Se revisan tambien sus subcarpetas; basta con la carpeta que las contiene.
echo.
set "CARPETA="
set /p "CARPETA=Carpeta: "
if not defined CARPETA (
  echo.
  echo No escribio ninguna carpeta.
  goto :error
)
set "CARPETA=%CARPETA:"=%"
if not exist "%CARPETA%\" (
  echo.
  echo No se encontro la carpeta "%CARPETA%".
  goto :error
)

set "PYTHON=python"
where python >nul 2>nul || set "PYTHON=py"
where %PYTHON% >nul 2>nul || (
  echo.
  echo Falta Python 3.10 o posterior. Instalelo desde https://www.python.org/downloads/
  goto :error
)

echo.
echo Buscando y verificando los archivos. Puede tardar unos minutos...
%PYTHON% pipeline\empaquetar_originales.py --buscar "%CARPETA%" --zip
if errorlevel 1 goto :error

echo.
echo Listo. Revise originales\INFORME_EMPAQUETADO.txt para ver si falto algun archivo.
echo Siguiente paso:
echo   1. Suba AguaAbiertaGT_originales.zip a Google Drive.
echo   2. Compartir: "Cualquier persona con el enlace" como lector.
echo   3. Pegue el enlace en datos\config.json, en "enlace_originales".
echo.
pause
goto :eof

:error
echo.
echo No se pudo armar el paquete. Revise el mensaje anterior.
pause
exit /b 1
