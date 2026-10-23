@echo off
setlocal
cd /d "%~dp0"
echo Agua Abierta Guatemala
echo Abriendo http://127.0.0.1:8000/ - mantenga esta ventana abierta mientras usa el sitio.
rem Abre el navegador dos segundos después, cuando el servidor ya está escuchando.
start "" /b cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8000/"
where py >nul 2>nul && (py -m http.server 8000 --bind 127.0.0.1 & goto :eof)
where python >nul 2>nul && (python -m http.server 8000 --bind 127.0.0.1 & goto :eof)
where npx >nul 2>nul && (npx --yes serve -l 8000 . & goto :eof)
echo.
echo No se encontro Python ni Node.js. Instale Python desde https://www.python.org/downloads/ y vuelva a intentarlo.
pause
