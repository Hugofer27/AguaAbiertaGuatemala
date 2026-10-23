"""Descubrimiento automatizado de publicaciones y conjuntos de datos sobre agua en Guatemala
mediante APIs públicas: OpenAlex, DataCite, Zenodo, HDX (CKAN), Harvard Dataverse, Figshare
y PANGAEA. Cada consulta queda registrada (con su número de resultados) en el log de búsquedas.

Uso: python 03_descubrimiento_apis.py <carpeta raíz de Investigación Claude>
"""
import csv
import datetime as dt
import json
import re
import sys
import time
from pathlib import Path

import requests

RAIZ = Path(sys.argv[1])
INV = RAIZ / "01_inventario" / "auto"
LOG = RAIZ / "06_registro_busquedas"
INV.mkdir(parents=True, exist_ok=True)
HOY = dt.date.today().isoformat()
S = requests.Session()
S.headers["User-Agent"] = "RiosAbiertosGT-inventario/0.1 (investigacion academica)"

LUGARES = re.compile(
    r"guatemal|motagua|atitl[aá]n|amatitl[aá]n|izabal|pet[eé]n|usumacinta|chixoy|polochic|"
    r"las vacas|villalobos|samal[aá]|achiguate|mar[ií]a linda|coyolate|nahualate|sarst[uú]n|"
    r"cahab[oó]n|r[ií]o dulce|lago de g[uü]ija|ixcan|selegua|cuilco|suchiate|paz river|r[ií]o paz|"
    r"quich[eé]|huehuetenango|quetzaltenango|escuintla|chiquimula|zacapa|el progreso|"
    r"alta verapaz|baja verapaz|sacatep[eé]quez|chimaltenango|solol[aá]|totonicap[aá]n|"
    r"san marcos, guat|retalhuleu|suchitep[eé]quez|jutiapa|jalapa|santa rosa, guat|"
    r"tikal|yaxha|pet[eé]n itz[aá]|lake peten|lago pet",
    re.I)
AGUA = re.compile(
    r"water|agua|river|r[ií]o|lake|lago|laguna|lagoon|aquifer|acu[ií]fero|groundwater|"
    r"hydro|hidro|rain|lluvia|precipit|wastewater|residual|sanita|saneamiento|drinking|potable|"
    r"cyanobacteri|cianobacter|eutroph|eutrofi|contamina|pollut|sediment|discharge|caudal|"
    r"flood|inundaci|drought|sequ[ií]a|watershed|cuenca|catchment|basin|plastic|pl[aá]stic|"
    r"wetland|humedal|mangrove|manglar|estuar|coliform|arsenic|ars[eé]nico|nitrate|nitrato|"
    r"fluor|mercury|mercurio|metal|pesticid|plaguicid|limnolog|irrigation|riego|well|pozo|"
    r"spring|manantial|solid waste|desechos|residuos|basura|hurricane|hurac[aá]n|storm|tormenta",
    re.I)

LOG_ROWS = []


def log(fuente, consulta, n, nota=""):
    LOG_ROWS.append({"fecha": HOY, "fuente": fuente, "consulta": consulta, "resultados": n, "nota": nota})


def relevante(*textos):
    t = " ".join(x for x in textos if x)
    return bool(LUGARES.search(t)) and bool(AGUA.search(t))


def get_json(url, **kw):
    err = RuntimeError("sin respuesta")
    for intento in range(4):
        try:
            r = S.get(url, timeout=60, **kw)
            if r.status_code == 429:
                err = RuntimeError("HTTP 429 (límite de tasa)")
                time.sleep(10 * 2 ** intento)
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:  # se registra y se sigue con otra fuente
            err = e
            time.sleep(2)
    raise err


def escribir(nombre, filas):
    if not filas:
        return
    campos = list(dict.fromkeys(k for f in filas for k in f))
    with open(INV / nombre, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)
    print(nombre, len(filas), flush=True)


# ---------------------------------------------------------------- OpenAlex
def abstract(inv):
    if not inv:
        return ""
    pos = sorted((p, w) for w, ps in inv.items() for p in ps)
    return " ".join(w for _, w in pos)


OPENALEX_Q = [
    "Guatemala water quality", "Guatemala calidad del agua", "Guatemala river pollution",
    "Motagua", "Rio Motagua", "Las Vacas river Guatemala", "Lake Atitlan", "Lago de Atitlan",
    "Lake Amatitlan", "Lago de Amatitlan", "Lake Izabal", "Lago de Izabal", "Lake Peten Itza",
    "Guatemala groundwater", "Guatemala aquifer", "Guatemala drinking water", "Guatemala sanitation",
    "Guatemala wastewater", "Guatemala heavy metals water", "Guatemala arsenic",
    "Guatemala pesticides water", "Guatemala mercury", "Guatemala cyanobacteria",
    "Guatemala river discharge", "Guatemala hydrology", "Guatemala rainfall precipitation",
    "Guatemala flood", "Guatemala drought water", "Guatemala watershed", "Guatemala cuenca hidrografica",
    "Guatemala plastic river", "Guatemala solid waste river", "Guatemala microplastics",
    "Guatemala fluoride water", "Guatemala nitrate", "Guatemala coliform", "Guatemala diarrhea water",
    "Guatemala mining water", "Marlin mine water", "Chixoy", "Usumacinta", "Polochic", "Rio Dulce Guatemala",
    "Samala river", "Guatemala mangrove estuary", "Guatemala Pacific coast rivers", "Guatemala lake sediment",
    "Guatemala limnology", "Guatemala remote sensing water", "Guatemala irrigation water",
    "Guatemala City water supply", "Rio Villalobos", "Rio Paz Guatemala", "Lago de Guija",
    "Guatemala emerging contaminants", "Guatemala pharmaceuticals water", "Guatemala lead water",
    "Guatemala water treatment plant", "Guatemala hurricane Mitch hydrology", "Guatemala Agatha flood",
]


def openalex():
    vistos, filas = set(), []
    consultas = [("search", q) for q in OPENALEX_Q] + [
        ("filter_gt", "water"), ("filter_gt", "agua"), ("filter_gt", "river"), ("filter_gt", "lake"),
        ("filter_gt", "contaminación"), ("filter_gt", "hydrology")]
    for modo, q in consultas:
        n_rel = 0
        for page in (1, 2):
            params = {"per-page": 200, "page": page}
            if modo == "search":
                params["search"] = q
            else:
                params["search"] = q
                params["filter"] = "authorships.institutions.country_code:GT"
            try:
                d = get_json("https://api.openalex.org/works", params=params)
            except Exception as e:
                log("OpenAlex", f"{modo}:{q} p{page}", -1, str(e)[:120])
                break
            res = d.get("results", [])
            for w in res:
                titulo = w.get("title") or ""
                ab = abstract(w.get("abstract_inverted_index"))
                if not relevante(titulo, ab):
                    continue
                n_rel += 1
                if w["id"] in vistos:
                    continue
                vistos.add(w["id"])
                loc = w.get("primary_location") or {}
                src = loc.get("source") or {}
                oa = w.get("open_access") or {}
                autores = [a["author"]["display_name"] for a in w.get("authorships", [])]
                inst = sorted({i.get("display_name", "") for a in w.get("authorships", [])
                               for i in a.get("institutions", [])} - {""})
                filas.append({
                    "openalex_id": w["id"], "doi": w.get("doi") or "", "titulo": titulo,
                    "autores": "; ".join(autores[:12]) + (" et al." if len(autores) > 12 else ""),
                    "anio_publicacion": w.get("publication_year"), "tipo": w.get("type"),
                    "revista_o_fuente": src.get("display_name") or "", "instituciones": "; ".join(inst[:10]),
                    "acceso_abierto": oa.get("is_oa"), "url_oa": oa.get("oa_url") or "",
                    "landing_url": loc.get("landing_page_url") or "", "citas": w.get("cited_by_count"),
                    "consulta": f"{modo}:{q}", "resumen_inicio": ab[:600],
                })
            if len(res) < 200:
                break
            time.sleep(1.5)
        log("OpenAlex", f"{modo}:{q}", n_rel, "resultados relevantes (lugar+agua) en hasta 400 revisados")
    escribir("openalex_publicaciones.csv", filas)


# ---------------------------------------------------------------- DataCite
def datacite():
    filas, vistos = [], set()
    for q in ["Guatemala water", "Guatemala agua", "Guatemala river", "Guatemala lake", "Guatemala rainfall",
              "Guatemala hydrology", "Atitlan", "Amatitlan", "Motagua", "Izabal", "Peten Itza",
              "Guatemala groundwater", "Guatemala sanitation", "Guatemala wastewater", "Guatemala precipitation",
              "Guatemala sediment", "Guatemala watershed", "Guatemala plastic", "Usumacinta", "Guatemala flood"]:
        url = "https://api.datacite.org/dois"
        params = {"query": q, "resource-type-id": "dataset", "page[size]": 100}
        try:
            d = get_json(url, params=params)
        except Exception as e:
            log("DataCite", q, -1, str(e)[:120]); continue
        n = 0
        for it in d.get("data", []):
            a = it["attributes"]
            titulo = (a.get("titles") or [{}])[0].get("title", "")
            desc = " ".join(x.get("description", "") or "" for x in a.get("descriptions") or [])
            subj = " ".join(x.get("subject", "") for x in a.get("subjects") or [])
            geo = json.dumps(a.get("geoLocations") or [])
            if not relevante(titulo, desc, subj, geo):
                continue
            n += 1
            if it["id"] in vistos:
                continue
            vistos.add(it["id"])
            filas.append({
                "doi": "https://doi.org/" + it["id"], "titulo": titulo,
                "autores": "; ".join(c.get("name", "") for c in (a.get("creators") or [])[:10]),
                "editor": a.get("publisher") if isinstance(a.get("publisher"), str) else (a.get("publisher") or {}).get("name", ""),
                "anio": a.get("publicationYear"), "url": a.get("url") or "",
                "licencia": "; ".join(r.get("rightsIdentifier") or r.get("rights", "") for r in a.get("rightsList") or []),
                "formatos": "; ".join(a.get("formats") or []), "tamanos": "; ".join(a.get("sizes") or []),
                "consulta": q, "descripcion_inicio": re.sub(r"\s+", " ", desc)[:500],
            })
        log("DataCite", q + " [dataset]", n)
        time.sleep(0.3)
    escribir("datacite_datasets.csv", filas)


# ---------------------------------------------------------------- Zenodo
def zenodo():
    filas, vistos = [], set()
    for q in ["Guatemala water", "Guatemala agua", "Guatemala river", "Guatemala lake", "Atitlan", "Amatitlan",
              "Motagua", "Izabal", "Guatemala rainfall", "Guatemala hydrology", "Guatemala groundwater",
              "Guatemala plastic", "Guatemala wastewater", "Guatemala sanitation", "Guatemala sediment"]:
        hits = []
        try:
            for pag in (1, 2, 3, 4):
                d = get_json("https://zenodo.org/api/records", params={"q": q, "size": 25, "page": pag})
                hits += d.get("hits", {}).get("hits", [])
                if len(d.get("hits", {}).get("hits", [])) < 25:
                    break
                time.sleep(1)
        except Exception as e:
            log("Zenodo", q, -1, str(e)[:120])
            if not hits:
                continue
        n = 0
        for h in hits:
            m = h.get("metadata", {})
            desc = re.sub("<[^>]+>", " ", m.get("description", "") or "")
            if not relevante(m.get("title", ""), desc, " ".join(m.get("keywords") or [])):
                continue
            n += 1
            if h["id"] in vistos:
                continue
            vistos.add(h["id"])
            files = h.get("files") or []
            filas.append({
                "zenodo_id": h["id"], "doi": h.get("doi_url") or "", "titulo": m.get("title", ""),
                "tipo": (m.get("resource_type") or {}).get("type", ""),
                "autores": "; ".join(c.get("name", "") for c in (m.get("creators") or [])[:10]),
                "fecha": m.get("publication_date"), "licencia": (m.get("license") or {}).get("id", ""),
                "acceso": m.get("access_right"), "url": h.get("links", {}).get("self_html", ""),
                "n_archivos": len(files), "archivos": "; ".join(f.get("key", "") for f in files[:15]),
                "bytes_total": sum(f.get("size", 0) for f in files), "consulta": q,
                "descripcion_inicio": re.sub(r"\s+", " ", desc)[:500],
            })
        log("Zenodo", q, n)
        time.sleep(1)
    escribir("zenodo_registros.csv", filas)


# ---------------------------------------------------------------- HDX
def hdx():
    filas = []
    try:
        d = get_json("https://data.humdata.org/api/3/action/package_search",
                     params={"fq": "groups:gtm", "rows": 1000})
    except Exception as e:
        log("HDX", "groups:gtm", -1, str(e)[:120]); return
    res = d["result"]["results"]
    log("HDX", "groups:gtm (todos)", len(res), "se filtra por términos de agua")
    for p in res:
        tags = " ".join(t["name"] for t in p.get("tags", []))
        texto = f"{p.get('title','')} {p.get('notes','')} {tags}"
        if not AGUA.search(texto):
            continue
        recursos = p.get("resources", [])
        filas.append({
            "hdx_name": p["name"], "titulo": p.get("title"), "organizacion": (p.get("organization") or {}).get("title", ""),
            "url": "https://data.humdata.org/dataset/" + p["name"], "licencia": p.get("license_title"),
            "fecha_modificacion": p.get("metadata_modified"), "cobertura_temporal": p.get("dataset_date"),
            "tags": tags, "n_recursos": len(recursos),
            "formatos": "; ".join(sorted({(r.get("format") or "").upper() for r in recursos})),
            "descargas": "; ".join(r.get("url", "") for r in recursos[:8]),
        })
    escribir("hdx_datasets.csv", filas)


# ---------------------------------------------------------------- Dataverse
def dataverse():
    filas, vistos = [], set()
    for q in ["Guatemala water", "Guatemala agua", "Guatemala river", "Guatemala lake", "Atitlan",
              "Guatemala sanitation", "Guatemala rainfall", "Guatemala drinking water", "Guatemala hydrology"]:
        try:
            d = get_json("https://dataverse.harvard.edu/api/search", params={"q": q, "type": "dataset", "per_page": 100})
        except Exception as e:
            log("Harvard Dataverse", q, -1, str(e)[:120]); continue
        n = 0
        for it in d["data"]["items"]:
            if not relevante(it.get("name", ""), it.get("description", ""), " ".join(it.get("keywords") or [])):
                continue
            n += 1
            if it.get("global_id") in vistos:
                continue
            vistos.add(it.get("global_id"))
            filas.append({
                "id": it.get("global_id"), "titulo": it.get("name"), "url": it.get("url"),
                "autores": "; ".join(it.get("authors") or []), "publicado": it.get("published_at"),
                "n_archivos": it.get("fileCount"), "consulta": q,
                "descripcion_inicio": re.sub(r"\s+", " ", it.get("description", ""))[:500],
            })
        log("Harvard Dataverse", q, n)
        time.sleep(0.5)
    escribir("dataverse_datasets.csv", filas)


# ---------------------------------------------------------------- Figshare
def figshare():
    filas, vistos = [], set()
    for q in ["Guatemala water", "Guatemala river", "Guatemala lake", "Atitlan", "Motagua", "Amatitlan",
              "Guatemala groundwater", "Guatemala rainfall", "Guatemala sanitation"]:
        try:
            r = S.post("https://api.figshare.com/v2/articles/search",
                       json={"search_for": q, "page_size": 100}, timeout=60)
            r.raise_for_status()
            res = r.json()
        except Exception as e:
            log("Figshare", q, -1, str(e)[:120]); continue
        n = 0
        for it in res:
            if not relevante(it.get("title", "")):
                continue
            n += 1
            if it["id"] in vistos:
                continue
            vistos.add(it["id"])
            filas.append({"figshare_id": it["id"], "titulo": it.get("title"), "doi": it.get("doi"),
                          "url": it.get("url_public_html"), "tipo": it.get("defined_type_name"),
                          "publicado": it.get("published_date"), "consulta": q})
        log("Figshare", q, n, "relevancia evaluada solo por título")
        time.sleep(0.5)
    escribir("figshare_items.csv", filas)


# ---------------------------------------------------------------- PANGAEA
def pangaea():
    filas, vistos = [], set()
    for q in ["Guatemala", "Atitlan", "Peten Itza", "Izabal", "Amatitlan", "Motagua", "Guatemala lake",
              "Guatemala river"]:
        try:
            d = get_json("https://www.pangaea.de/advanced/search.php",
                         params={"q": q, "count": 500, "offset": 0})
        except Exception as e:
            log("PANGAEA", q, -1, str(e)[:120]); continue
        res = d.get("results", [])
        n = 0
        for it in res:
            html = it.get("html", "")
            titulo = re.sub("<[^>]+>", " ", html)
            titulo = re.sub(r"\s+", " ", titulo).strip()
            if not LUGARES.search(titulo):
                continue
            n += 1
            uri = it.get("URI")
            if uri in vistos:
                continue
            vistos.add(uri)
            filas.append({"doi": uri, "texto": titulo[:400], "score": it.get("score"),
                          "tipo": it.get("type"), "consulta": q})
        log("PANGAEA", q, n, f"{d.get('totalCount', '?')} totales")
        time.sleep(0.5)
    escribir("pangaea_datasets.csv", filas)


# ---------------------------------------------------------------- Crossref
def crossref():
    filas, vistos = [], set()
    for q in ["Guatemala water quality", "Guatemala river", "Motagua", "Lake Atitlan", "Lake Amatitlan", "Lake Izabal",
              "Guatemala groundwater", "Guatemala wastewater", "Guatemala drinking water", "Guatemala hydrology",
              "Guatemala calidad del agua", "Guatemala cuenca hidrográfica", "Guatemala rainfall", "Las Vacas Guatemala",
              "Guatemala flood", "Guatemala cyanobacteria", "Peten Itza lake", "Guatemala plastic river"]:
        try:
            d = get_json("https://api.crossref.org/works", params={"query.bibliographic": q, "rows": 200,
                                                                    "select": "DOI,title,author,issued,container-title,type,abstract,URL"})
        except Exception as e:
            log("Crossref", q, -1, str(e)[:120]); continue
        n = 0
        for it in d["message"]["items"]:
            titulo = " ".join(it.get("title") or [])
            ab = re.sub("<[^>]+>", " ", it.get("abstract") or "")
            if not relevante(titulo, ab):
                continue
            n += 1
            if it["DOI"] in vistos:
                continue
            vistos.add(it["DOI"])
            autores = [f"{a.get('family','')}, {a.get('given','')}".strip(", ") for a in it.get("author", [])]
            filas.append({"doi": "https://doi.org/" + it["DOI"], "titulo": titulo,
                          "autores": "; ".join(autores[:12]), "anio": ((it.get("issued") or {}).get("date-parts") or [[None]])[0][0],
                          "revista": " ".join(it.get("container-title") or []), "tipo": it.get("type"),
                          "url": it.get("URL"), "consulta": q, "resumen_inicio": re.sub(r"\s+", " ", ab)[:600]})
        log("Crossref", q, n, "resultados relevantes en 200 revisados")
        time.sleep(1)
    escribir("crossref_publicaciones.csv", filas)


if __name__ == "__main__":
    fuentes = sys.argv[2:] or ["openalex", "datacite", "zenodo", "hdx", "dataverse", "figshare", "pangaea"]
    for f in fuentes:
        try:
            globals()[f]()
        except Exception as e:
            log(f, "(fuente completa)", -1, f"error: {e}"[:200])
            print("ERROR", f, e, flush=True)
    with open(LOG / f"log_apis_{'_'.join(fuentes) if len(fuentes) < 3 else 'todas'}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["fecha", "fuente", "consulta", "resultados", "nota"])
        w.writeheader()
        w.writerows(LOG_ROWS)
