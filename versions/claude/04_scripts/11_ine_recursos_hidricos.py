"""Consulta el portal CKAN del INE (datos.ine.gob.gt) y agrega a 05_manifiesto/lista_descargas.csv los
archivos de los conjuntos "Recurso(s) Hídrico(s)" 2022, 2023 y 2024 (Sección de Estadísticas Ambientales,
licencia CC BY). Guarda la respuesta de la API en 06_registro_busquedas/ como evidencia.

Agregado el 22-oct-2026: el portal lo halló Codex (Investigación ChatGPT) y Claude no lo había visto.
Después: python 04_descargar.py <carpeta raíz> --solo-nuevas

Uso: python 11_ine_recursos_hidricos.py <carpeta raíz>
"""
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(sys.argv[1])
BASE = "https://datos.ine.gob.gt"
CONJUNTOS = {"1-recurso-hidrico": 2022, "1-recursos-hidricos": 2023, "1-recursos-hidricos-2024": 2024}
LISTA = RAIZ / "05_manifiesto" / "lista_descargas.csv"
ORGS = ("MSPAS", "INSIVUMEH", "AMSCLAE", "AMSA", "EMPAGUA")


def get(url):
    # curl usa el almacén de certificados de Windows (algunos portales .gob.gt fallan con certifi)
    out = subprocess.run(["curl", "-s", "-m", "120", "-A", "Mozilla/5.0 RiosAbiertosGT", url], capture_output=True)
    return json.loads(out.stdout.decode("utf-8"))


with open(LISTA, encoding="utf-8") as fh:
    lista = list(csv.DictReader(fh))
urls_previas = {t["url"].strip() for t in lista}

nuevas = []
for nombre, anio in CONJUNTOS.items():
    d = get(f"{BASE}/api/3/action/package_show?id={nombre}")
    (RAIZ / "06_registro_busquedas" / f"ine_ckan_{nombre}.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    r = d["result"]
    print(f"{r['title']}: {len(r['resources'])} recursos, licencia {r.get('license_title')}")
    for i, x in enumerate(r["resources"], 1):
        if x["url"] in urls_previas:
            continue
        nombre_rec = x["name"].upper().replace("ATITLÁN", "ATITLÁN AMSCLAE")  # "Consolidado de Ríos Atitlán" no nombra a AMSCLAE
        org = next((o for o in ORGS if o in nombre_rec), "INE")
        nuevas.append({"clave": f"INE-RH{anio}-{i:02d}-{org}", "organizacion": f"INE / {org}", "url": x["url"],
                       "carpeta": f"INE/recursos_hidricos_{anio}", "nombre_local": ""})

with open(LISTA, "a", newline="", encoding="utf-8") as fh:
    csv.DictWriter(fh, fieldnames=["clave", "organizacion", "url", "carpeta", "nombre_local"]).writerows(nuevas)
print(f"Agregadas {len(nuevas)} URL a {LISTA.name}")
