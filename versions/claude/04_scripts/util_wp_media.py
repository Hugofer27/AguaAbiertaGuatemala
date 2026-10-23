"""Enumera los archivos publicados (PDF, Excel, CSV, ZIP, KMZ...) de un sitio WordPress mediante su
API REST pública /wp-json/wp/v2/media. No requiere autenticación ni evade protecciones; si el
sitio no expone la API se registra el error.

Uso: python util_wp_media.py <dominio> <csv salida> [término de búsqueda]
"""
import csv
import sys
import time

import requests

dominio, salida = sys.argv[1], sys.argv[2]
busqueda = sys.argv[3] if len(sys.argv) > 3 else None
S = requests.Session()
S.headers["User-Agent"] = "RiosAbiertosGT-inventario/0.1 (investigacion academica)"
TIPOS_IGNORADOS = ("image/", "video/", "audio/")

filas, pagina, total_paginas = [], 1, None
while True:
    params = {"per_page": 100, "page": pagina, "_fields": "id,date,title,source_url,mime_type,media_details"}
    if busqueda:
        params["search"] = busqueda
    try:
        r = S.get(f"https://{dominio}/wp-json/wp/v2/media", params=params, timeout=60)
    except Exception as e:
        print("ERROR", e)
        break
    if r.status_code != 200:
        print("HTTP", r.status_code, r.text[:200])
        break
    total_paginas = int(r.headers.get("X-WP-TotalPages", 1))
    for m in r.json():
        if m.get("mime_type", "").startswith(TIPOS_IGNORADOS):
            continue
        filas.append({
            "id": m["id"], "fecha": m["date"][:10], "titulo": m["title"]["rendered"],
            "url": m["source_url"], "mime": m["mime_type"],
            "bytes": (m.get("media_details") or {}).get("filesize", ""),
        })
    print(f"página {pagina}/{total_paginas}: {len(filas)} documentos", flush=True)
    if pagina >= total_paginas:
        break
    pagina += 1
    time.sleep(0.5)

with open(salida, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["id", "fecha", "titulo", "url", "mime", "bytes"])
    w.writeheader()
    w.writerows(filas)
print("TOTAL", len(filas))
