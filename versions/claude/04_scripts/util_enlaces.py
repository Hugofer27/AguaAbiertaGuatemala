"""Extrae de una o varias páginas web los enlaces a archivos de datos o documentos (PDF, Excel,
CSV, ZIP, KMZ, SHP, etc.), iframes y enlaces a portales externos. Solo lectura de HTML público.

Uso: python util_enlaces.py <csv salida> <url1> [url2 ...]
"""
import csv
import re
import sys
import time
from urllib.parse import urljoin, urlparse

import requests

EXT = re.compile(r"\.(pdf|xlsx?|csv|zip|rar|7z|kmz|kml|shp|geojson|json|txt|docx?|nc|tif|tiff|dbf|mdb|accdb)(\?|$)", re.I)
S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0 (RiosAbiertosGT-inventario; investigacion academica)"

salida, paginas = sys.argv[1], sys.argv[2:]
filas = []
for p in paginas:
    try:
        r = S.get(p, timeout=60)
        html = r.text
        estado = r.status_code
    except Exception as e:
        filas.append({"pagina": p, "estado": f"error {e}"[:80], "tipo": "", "url": "", "texto": ""})
        continue
    dom = urlparse(p).netloc
    vistos = set()
    for m in re.finditer(r'<(a|iframe|embed|object)\b[^>]*?(?:href|src|data)=["\']([^"\']+)["\'][^>]*>(.*?)(?:</a>|</iframe>|$)',
                         html, re.I | re.S):
        etiqueta, href, texto = m.group(1).lower(), m.group(2), re.sub(r"<[^>]+>|\s+", " ", m.group(3) or "").strip()
        u = urljoin(r.url, href)
        if u in vistos or u.startswith(("mailto:", "javascript:", "tel:")):
            continue
        es_archivo = bool(EXT.search(u))
        externo = urlparse(u).netloc not in ("", dom) and not re.search(
            r"facebook|twitter|instagram|youtube|linkedin|whatsapp|google\.com/maps|wordpress|gravatar|x\.com", u, re.I)
        if es_archivo or etiqueta != "a" or externo:
            vistos.add(u)
            filas.append({"pagina": p, "estado": estado, "tipo": "archivo" if es_archivo else etiqueta if etiqueta != "a" else "externo",
                          "url": u, "texto": texto[:120]})
    print(p, estado, len(vistos), flush=True)
    time.sleep(0.5)

with open(salida, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["pagina", "estado", "tipo", "url", "texto"])
    w.writeheader()
    w.writerows(filas)
