"""Cosecha metadatos Dublin Core por OAI-PMH de repositorios institucionales y revistas de
Guatemala, y conserva solo los registros relacionados con agua (tesis, informes, artículos).

Uso: python 06_oai_repositorios.py <carpeta raíz> [nombre_repositorio ...]
"""
import csv
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

RAIZ = Path(sys.argv[1])
OUT = RAIZ / "01_inventario" / "auto"
LOGF = RAIZ / "06_registro_busquedas"
REPOS = {
    "usac_eprints": "http://www.repositorio.usac.edu.gt/cgi/oai2",
    "uvg_dspace": "https://repositorio.uvg.edu.gt/oai/request",
    "revistas_usac_ojs": "https://revistas.usac.edu.gt/index.php/index/oai",
}
NS = {"oai": "http://www.openarchives.org/OAI/2.0/", "dc": "http://purl.org/dc/elements/1.1/",
      "oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/"}
AGUA = re.compile(
    r"\baguas?\b|\br[ií]os?\b|\blagos?\b|\blagunas?\b|\bcuencas?\b|acu[ií]fer|hidrol[oó]g|hidrogr|h[ií]dric|"
    r"\bcaudal|\blluvias?\b|precipitaci[oó]n|saneamiento|residuales|potable|coliform|plaguicida|pesticid|"
    r"metales pesados|ars[eé]nico|nitrat|cianobacter|eutrofi|humedal|manglar|\bpozos?\b|subterr[aá]ne|"
    r"desechos s[oó]lidos|residuos s[oó]lidos|micropl[aá]stic|pl[aá]sticos?\b|\bptar\b|limnol|"
    r"\bwater\b|\brivers?\b|\blakes?\b|watershed|groundwater|wastewater|rainfall|sanitation|drought|sequ[ií]a|"
    r"inundaci|\bflood|escorrent|erosi[oó]n h[ií]dric|riego|irrigation|fitoplancton|zooplancton|macroinvertebrados",
    re.I)
LUGAR = re.compile(r"motagua|las vacas|atitl[aá]n|amatitl[aá]n|izabal|pet[eé]n itz[aá]|villalobos|r[ií]o dulce|"
                   r"chixoy|polochic|usumacinta|samal[aá]|mar[ií]a linda|achiguate|coyolate|naranjo|nahualate|"
                   r"cahab[oó]n|selegua|sarst[uú]n|ocosito|madre vieja|acome|guacalate|platanitos", re.I)
S = requests.Session()
S.headers["User-Agent"] = "RiosAbiertosGT-inventario/0.1 (investigacion academica)"


def cosechar(nombre, base):
    params = {"verb": "ListRecords", "metadataPrefix": "oai_dc"}
    total, filas, paginas = 0, [], 0
    while True:
        for intento in range(4):
            try:
                r = S.get(base, params=params, timeout=120)
                r.raise_for_status()
                raiz = ET.fromstring(r.content)
                break
            except Exception as e:
                err = e
                time.sleep(10 * (intento + 1))
        else:
            print(nombre, "ERROR", err, flush=True)
            return filas, total, f"interrumpido: {err}"[:200]
        paginas += 1
        for rec in raiz.iterfind(".//oai:record", NS):
            if rec.find("oai:header", NS).get("status") == "deleted":
                continue
            md = rec.find(".//oai_dc:dc", NS)
            if md is None:
                continue
            total += 1
            get = lambda t: [e.text.strip() for e in md.iterfind(f"dc:{t}", NS) if e.text]
            titulo, desc, subj = " ".join(get("title")), " ".join(get("description")), " ".join(get("subject"))
            texto = f"{titulo} {subj} {desc[:1500]}"
            if not AGUA.search(f"{titulo} {subj}") and not (AGUA.search(desc[:1500]) and LUGAR.search(texto)):
                continue
            ids = get("identifier")
            url = next((i for i in ids if i.startswith("http")), "")
            filas.append({
                "repositorio": nombre, "oai_id": rec.find("oai:header/oai:identifier", NS).text,
                "titulo": titulo[:400], "autores": "; ".join(get("creator"))[:300],
                "fecha": "; ".join(get("date"))[:60], "tipo": "; ".join(get("type"))[:120],
                "url": url, "otros_identificadores": " | ".join(i for i in ids if i != url)[:400],
                "materias": subj[:300], "lugar_prioritario": "; ".join(sorted({m.lower() for m in LUGAR.findall(texto)})),
                "derechos": "; ".join(get("rights"))[:200], "resumen_inicio": re.sub(r"\s+", " ", desc)[:500],
            })
        tok = raiz.find(".//oai:resumptionToken", NS)
        if paginas % 20 == 0:
            print(nombre, "páginas", paginas, "registros", total, "relevantes", len(filas), flush=True)
        if tok is None or not (tok.text or "").strip():
            break
        params = {"verb": "ListRecords", "resumptionToken": tok.text.strip()}
        time.sleep(0.5)
    return filas, total, "completo"


log = []
for nombre in (sys.argv[2:] or REPOS):
    filas, total, estado = cosechar(nombre, REPOS[nombre])
    log.append({"repositorio": nombre, "endpoint": REPOS[nombre], "registros_revisados": total,
                "relevantes_agua": len(filas), "estado": estado})
    if filas:
        with open(OUT / f"oai_{nombre}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(filas[0]))
            w.writeheader()
            w.writerows(filas)
    print(nombre, total, len(filas), estado, flush=True)

with open(LOGF / f"log_oai_{'_'.join(sys.argv[2:]) or 'todos'}.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["repositorio", "endpoint", "registros_revisados", "relevantes_agua", "estado"])
    w.writeheader()
    w.writerows(log)
