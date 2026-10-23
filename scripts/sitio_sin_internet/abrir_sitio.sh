#!/bin/sh
# Agua Abierta Guatemala: abre el sitio con un servidor local (macOS y Linux).
cd "$(dirname "$0")" || exit 1
echo "Abriendo http://127.0.0.1:8000/ (Ctrl+C para cerrar)"
( sleep 1; command -v open >/dev/null && open "http://127.0.0.1:8000/" || xdg-open "http://127.0.0.1:8000/" ) >/dev/null 2>&1 &
exec python3 -m http.server 8000 --bind 127.0.0.1
