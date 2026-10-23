@echo off
setlocal
cd /d "%~dp0"

if not exist "node_modules" (
  echo Instalando dependencias de Agua Abierta Guatemala...
  call npm install
  if errorlevel 1 goto :error
)

echo Abriendo Agua Abierta Guatemala en http://127.0.0.1:4173/
echo Mantenga esta ventana abierta mientras usa el sitio.
call npm run dev -- --host 127.0.0.1 --port 4173 --open
goto :eof

:error
echo.
echo No se pudo iniciar Agua Abierta Guatemala. Revisa el mensaje anterior.
pause
