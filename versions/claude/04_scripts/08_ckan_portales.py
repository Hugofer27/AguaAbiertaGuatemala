"""Consulta portales CKAN públicos (API package_search) y guarda los conjuntos de datos sobre agua
relacionados con Guatemala: AmeriGEOSS, World Bank Water Data, BID (data.iadb.org), CONRED y
SEGEPLAN. HDX se consulta en 03_descubrimiento_apis.py.

Uso: python 08_ckan_portales.py <carpeta raíz>
"""
import csv
import re
import subprocess
import sys
import json
from pathlib import Path

RAIZ = Path(sys.argv[1])
PORTALES = {
    "AmeriGEOSS": ("https://data.amerigeoss.org", ["Guatemala"]),
    "World Bank Water Data": ("https://wbwaterdata.org", ["Guatemala", "Central America", "Mesoamerica", "global"]),
    "BID data.iadb.org": ("https://data.iadb.org", ["Guatemala agua", "Guatemala water", "Guatemala saneamiento"]),
    "SE-CONRED": ("https://datos.conred.gob.gt", [""]),
    "SEGEPLAN": ("https://datos.segeplan.gob.gt", [""]),
}
AGUA = re.compile(r"agua|water|r[ií]o|river|lago|lake|cuenca|basin|watershed|hidro|hydro|flood|inund|lluvia|rain|"
                  r"precip|sanea|sanita|wash|residu|waste|drought|sequ|aquifer|acu[ií]f|groundwater|wetland|"
                  r"humedal|incidente|amenaza|coast|costa|mangrove|manglar|irrig|riego|climate|clima", re.I)


def get(url):
    # curl usa el almacén de certificados de Windows (algunos portales .gob.gt fallan con certifi)
    out = subprocess.run(["curl", "-s", "-m", "120", "-A", "Mozilla/5.0 RiosAbiertosGT", url], capture_output=True)
    return json.loads(out.stdout.decode("utf-8"))


filas, log = [], []
for nombre, (base, consultas) in PORTALES.items():
    vistos = set()
    for q in consultas:
        try:
            d = get(f"{base}/api/3/action/package_search?rows=1000&q={q.replace(' ', '+')}")["result"]
        except Exception as e:
            log.append({"portal": nombre, "consulta": q, "total": -1, "relevantes": 0, "nota": str(e)[:150]})
            continue
        n = 0
        for p in d["results"]:
            texto = f"{p.get('title','')} {p.get('notes','')} {' '.join(t['name'] for t in p.get('tags', []))}"
            geo = re.search(r"guatemal|central america|centroam[eé]rica|mesoam|global|world|latin", texto, re.I)
            if not AGUA.search(texto) or (nombre in ("World Bank Water Data", "AmeriGEOSS") and not geo):
                continue
            n += 1
            if p["name"] in vistos:
                continue
            vistos.add(p["name"])
            rec = p.get("resources", [])
            filas.append({
                "portal": nombre, "id": p["name"], "titulo": p.get("title"),
                "organizacion": (p.get("organization") or {}).get("title", ""),
                "url": f"{base}/dataset/{p['name']}", "licencia": p.get("license_title"),
                "modificado": (p.get("metadata_modified") or "")[:10], "n_recursos": len(rec),
                "formatos": "; ".join(sorted({(r.get("format") or "").upper() for r in rec})),
                "recursos": " | ".join((r.get("url") or "") for r in rec[:6])[:600],
                "resumen": re.sub(r"\s+", " ", p.get("notes") or "")[:400], "consulta": q,
            })
        log.append({"portal": nombre, "consulta": q, "total": d["count"], "relevantes": n, "nota": ""})
        print(nombre, q, d["count"], n, flush=True)

with open(RAIZ / "01_inventario" / "auto" / "ckan_portales.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(filas[0]))
    w.writeheader()
    w.writerows(filas)
with open(RAIZ / "06_registro_busquedas" / "log_ckan_portales.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["portal", "consulta", "total", "relevantes", "nota"])
    w.writeheader()
    w.writerows(log)
print("total", len(filas))
