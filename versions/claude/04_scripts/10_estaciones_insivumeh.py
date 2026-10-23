"""Extrae coordenadas, nombre, código y ubicación de las estaciones meteorológicas de la red
convencional del INSIVUMEH desde los mapas Folium/Leaflet publicados (HTML original en
02_datos_originales). Cada marcador tiene un popup en un iframe codificado en base64.

Uso: python 10_estaciones_insivumeh.py <carpeta raíz>
"""
import base64
import csv
import html
import re
import sys
from pathlib import Path

RAIZ = Path(sys.argv[1])
ORIG = RAIZ / "02_datos_originales" / "INSIVUMEH" / "estaciones"
OUT = RAIZ / "03_datos_procesados" / "insivumeh"
OUT.mkdir(parents=True, exist_ok=True)

for nombre in ["mapa_estaciones_met_convencional.html", "mapa_variables_clima.html"]:
    h = (ORIG / nombre).read_text(encoding="utf-8", errors="replace")
    filas = []
    for b64 in re.findall(r"data:text/html;charset=utf-8;base64,([A-Za-z0-9+/=]+)", h):
        t = base64.b64decode(b64).decode("utf-8", "replace")
        t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S)
        texto = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip()
        m = re.search(r"iframe (.*?) Estaci[oó]n .*?ID: (\S+) Ubicaci[oó]n: Lat: ([-\d.]+), Lon: ([-\d.]+) (.*?)$", texto)
        if m:
            filas.append({"estacion": m.group(1).strip(), "codigo": m.group(2), "latitud": float(m.group(3)),
                          "longitud": float(m.group(4)), "municipio_departamento": m.group(5).strip()[:80]})
        else:
            filas.append({"estacion": "", "codigo": "", "latitud": "", "longitud": "", "municipio_departamento": texto[:120]})
    salida = OUT / nombre.replace(".html", "_estaciones.csv")
    with open(salida, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["estacion", "codigo", "latitud", "longitud", "municipio_departamento"])
        w.writeheader()
        w.writerows(filas)
    print(nombre, len(filas), "estaciones;", sum(bool(f["codigo"]) for f in filas), "con código")
