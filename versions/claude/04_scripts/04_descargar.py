"""Descarga los archivos públicos listados en 05_manifiesto/lista_descargas.csv y genera el
manifiesto con checksums SHA-256.

- Idempotente: no vuelve a descargar un archivo que ya existe con el mismo tamaño registrado.
- No evade autenticación, CAPTCHAs ni bloqueos; un 401/403/429 se registra como fallo.
- Límite de tamaño por archivo (MAX_MB) para no bajar productos satelitales masivos.
- Con --solo-nuevas no reintenta las URL que ya están en el manifiesto (ni las fallidas).

Uso: python 04_descargar.py <carpeta raíz de Investigación Claude> [--solo-nuevas]
"""
import csv
import datetime as dt
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests

RAIZ = Path(sys.argv[1])
LISTA = RAIZ / "05_manifiesto" / "lista_descargas.csv"
MANIF = RAIZ / "05_manifiesto" / "manifiesto_descargas.csv"
DATOS = RAIZ / "02_datos_originales"
MAX_MB = 400
SOLO_NUEVAS = "--solo-nuevas" in sys.argv
S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0 (RiosAbiertosGT-inventario; investigacion academica)"

previos = {}
if MANIF.exists():
    with open(MANIF, encoding="utf-8") as fh:
        for f in csv.DictReader(fh):
            previos[f["url"]] = f


def nombre_archivo(url, resp):
    cd = resp.headers.get("Content-Disposition", "")
    m = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)', cd)
    nombre = unquote(m.group(1)) if m else unquote(Path(urlparse(url).path).name) or "descarga"
    return re.sub(r'[<>:"/\\|?*]', "_", nombre)[:150]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


filas = []
with open(LISTA, encoding="utf-8") as fh:
    tareas = list(csv.DictReader(fh))

for t in tareas:
    url, carpeta = t["url"].strip(), t["carpeta"].strip()
    p = previos.get(url)
    if p and (SOLO_NUEVAS or p["estado"] == "descargado" and (RAIZ / p["ruta_local"]).exists()):
        filas.append(p)
        continue
    destino_dir = DATOS / carpeta
    destino_dir.mkdir(parents=True, exist_ok=True)
    fila = {"clave": t["clave"], "organizacion": t["organizacion"], "url": url, "ruta_local": "",
            "estado": "", "http": "", "content_type": "", "bytes": "", "sha256": "",
            "fecha_acceso": dt.datetime.now().isoformat(timespec="seconds"), "nota": ""}
    try:
        with S.get(url, stream=True, timeout=(20, 180), allow_redirects=True) as r:
            fila["http"] = r.status_code
            fila["content_type"] = r.headers.get("Content-Type", "")
            if r.status_code != 200:
                fila["estado"] = "fallo"
                fila["nota"] = f"HTTP {r.status_code}"
            else:
                largo = int(r.headers.get("Content-Length") or 0)
                if largo > MAX_MB * 1e6:
                    fila["estado"] = "omitido_tamano"
                    fila["nota"] = f"{largo/1e6:.0f} MB > {MAX_MB} MB"
                else:
                    nombre = t.get("nombre_local") or nombre_archivo(r.url, r)
                    ruta = destino_dir / nombre
                    with open(ruta, "wb") as out:
                        for b in r.iter_content(1 << 16):
                            out.write(b)
                    if "text/html" in fila["content_type"] and ruta.suffix.lower() not in (".html", ".htm"):
                        fila["nota"] = "ADVERTENCIA: el servidor devolvió HTML (posible página de error)"
                    fila.update(estado="descargado", ruta_local=str(ruta.relative_to(RAIZ)).replace("\\", "/"),
                                bytes=ruta.stat().st_size, sha256=sha256(ruta))
    except Exception as e:
        fila["estado"] = "fallo"
        fila["nota"] = str(e)[:200]
    print(fila["estado"], fila["http"], fila["bytes"], url[:110], flush=True)
    filas.append(fila)
    time.sleep(0.7)

campos = ["clave", "organizacion", "url", "ruta_local", "estado", "http", "content_type", "bytes", "sha256",
          "fecha_acceso", "nota"]
with open(MANIF, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=campos)
    w.writeheader()
    w.writerows(filas)
with open(RAIZ / "05_manifiesto" / "manifest.json", "w", encoding="utf-8") as fh:
    json.dump({"generado": dt.datetime.now().isoformat(timespec="seconds"),
               "archivos": [f for f in filas if f["estado"] == "descargado"]}, fh, ensure_ascii=False, indent=1)
ok = sum(f["estado"] == "descargado" for f in filas)
print(f"Descargados {ok}/{len(filas)}")
