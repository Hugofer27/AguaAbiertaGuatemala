"""Compila el inventario maestro de RÍOS ABIERTOS GT a partir de:
- registros manuales verificados (01_inventario/manual/*.jsonl)
- manifiestos de descarga (05_manifiesto/manifiesto_*.csv)
- resultados automáticos de APIs y cosechas OAI (01_inventario/auto/*.csv)

Genera CSV y XLSX con: inventario maestro, publicaciones, resumen por organización, registro de
datos faltantes, duplicados detectados, archivos descargados y diccionario de campos.

Uso: python 09_compilar_inventario.py <carpeta raíz> [--sin-verificar-urls]
"""
import concurrent.futures as cf
import csv
import datetime as dt
import json
import re
import subprocess
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

RAIZ = Path(sys.argv[1])
VERIFICAR = "--sin-verificar-urls" not in sys.argv
INV = RAIZ / "01_inventario"
HOY = dt.date.today().isoformat()
csv.field_size_limit(10**8)

CAMPOS = ["Resource ID", "Organisation", "Resource title", "Resource type", "Dataset or publication",
          "Original URL", "Download URL", "File format", "Years covered", "Geographic coverage", "Parameters",
          "Number of records (verified)", "Licence", "Access status", "Download status", "Verification status",
          "Notes", "Source category", "Priority (1-5)", "Files retrieved", "Local files", "Discovery channel",
          "Access date", "URL check (HTTP)", "Motagua / Las Vacas"]

# ----------------------------------------------------------------- utilidades
LUGAR_GT = re.compile(
    r"guatemal|motagua|las vacas|atitl[aá]n|amatitl[aá]n|izabal|pet[eé]n|usumacinta|chixoy|polochic|villalobos|"
    r"samal[aá]|achiguate|mar[ií]a linda|coyolate|nahualate|sarst[uú]n|cahab[oó]n|r[ií]o dulce|g[uü]ija|"
    r"chiquimulilla|monterrico|quich[eé]|huehuetenango|quetzaltenango|escuintla|chiquimula|zacapa|alta verapaz|"
    r"baja verapaz|sacatep[eé]quez|chimaltenango|solol[aá]|totonicap[aá]n|retalhuleu|suchitep[eé]quez|jutiapa|"
    r"sayaxch|tikal|yaxh[aá]|puerto barrios|chinautla|mixco|villa nueva|ocosito|madre vieja|los esclavos|"
    r"pansalic|platanitos|pinula|michatoya|suchiate|coat[aá]n|selegua|cuilco|naranjo|la pasi[oó]n|sacpuy|macanch", re.I)
AGUA_ESTRICTO = re.compile(
    r"\bagua\b|\baguas\b|\bwater\b|\br[ií]os?\b|\brivers?\b|\blagos?\b|\blakes?\b|\blagunas?\b|\blagoons?\b|"
    r"\bcuencas?\b|\bwatersheds?\b|\bcatchments?\b|\bbasins?\b|acu[ií]fer|aquifer|groundwater|subterr[aá]ne|"
    r"hidrol[oó]g|hydrolog|hidrogeol|hydrogeol|h[ií]dric|\bcaudal|discharge|streamflow|runoff|escorrent|"
    r"\blluvias?\b|rainfall|precipitaci[oó]n|precipitation|saneamiento|sanitation|wastewater|aguas residuales|"
    r"drinking|potable|coliform|e\. coli|cianobacter|cyanobacter|eutrof|eutroph|limnol|humedal|wetland|manglar|"
    r"mangrove|estuar|\bpozos?\b|\bwells?\b|plaguicida|pesticide|ars[eé]nic|nitrat|fluor|mercur|metales pesados|"
    r"heavy metals|micropl[aá]stic|microplastic|desechos s[oó]lidos|residuos s[oó]lidos|solid waste|pl[aá]sticos?\b|"
    r"plastics?\b|inundaci|\bfloods?|flooding|sequ[ií]a|drought|riego|irrigation|sediment|calidad del agua|"
    r"water quality|fitoplancton|phytoplankton|zooplancton|macroinvertebr|diatom|hurac[aá]n|hurricane|"
    r"tormenta tropical|tropical storm|diarrea|diarrhea|diarrhoea|cholera|c[oó]lera|fish kill|mortandad", re.I)
PARAMS = [("pH", r"\bph\b"), ("temperatura", r"temperatur"), ("oxígeno disuelto", r"ox[ií]geno disuelto|dissolved oxygen"),
          ("conductividad", r"conductiv"), ("turbidez", r"turbid"), ("DBO", r"\bdbo|\bbod\b|demanda bioqu|biochemical oxygen"),
          ("DQO", r"\bdqo|\bcod\b|demanda qu[ií]mica|chemical oxygen"), ("nitrógeno/nitratos", r"nitr[oa]|nitrog"),
          ("fósforo", r"f[oó]sfor|phosph"), ("coliformes/E. coli", r"coliform|e\. ?coli|escherichia"),
          ("arsénico", r"ars[eé]nic"), ("plomo", r"\bplomo\b|\blead\b"), ("mercurio", r"mercur"), ("cadmio", r"cadmi"),
          ("metales pesados", r"metales|heavy metal|trace metal"), ("plaguicidas", r"plaguicid|pesticid|malat"),
          ("microplásticos", r"micropl[aá]stic|microplastic"), ("cianobacterias", r"cianobac|cyanobac|microcist|microcyst"),
          ("clorofila", r"clorofil|chlorophyll"), ("fluoruro", r"fluor"), ("sólidos/sedimentos", r"s[oó]lidos|sediment|tss\b"),
          ("caudal", r"caudal|discharge|streamflow"), ("precipitación", r"precipit|rainfall|lluvia"),
          ("fármacos/contaminantes emergentes", r"f[aá]rmac|pharmac|emergente|emerging"),
          ("macroinvertebrados/bioindicadores", r"macroinvert|bioindic|diatom"), ("residuos sólidos/plásticos", r"desechos|residuos s|solid waste|pl[aá]stic")]
NEGATIVO = re.compile(
    r"m[aá]quina|extrus|empaque|envase|llenado|calentamiento de agua|paneles? solar|planchas? pl[aá]stic|tornillo|"
    r"molde|inyecci[oó]n|bebida|cerveza|refresco|jugo|sheetpress|matr[ií]cula|estudiantil|hospital|g[aá]stric|"
    r"odontol|dental|occurrence download|arqueol|archaeolog|ceramic|cer[aá]mica|preface|pr[oó]logo|grebe|zambull|"
    r"seismic|s[ií]smic|heat flow|nodule|dsdp|\bodp\b|ocean drilling|guatemala basin|equatorial|building footprint|"
    r"poverty index|displacement|desplazamiento|education|educaci[oó]n b[aá]sica|soil fertility|mining resistance|"
    r"community resistance|^(figs?|figures?|tables?)\b|subspecies|storm surge|hurricanes poster|tile layer|global food webs|\bfault\b|falla geol|paleoseism|conquest|conquista|colonial|juego de pelota|ball ?court|log[ií]stica|otter|nutria|cocodrilo|crocodyl|tapir|jaguar|abejas?\b|bees?\b|murci[eé]lago|bats?\b", re.I)
LUGAR_CON_AGUA = re.compile(r"volc[aá]n de agua|agua (colorada|blanca|caliente|escondida|zarca|fr[ií]a|tibia|dulce|bonita|amarga)\b|"
                            r"r[ií]o hondo|ojo de agua|entre r[ií]os|cuatro r[ií]os|dos r[ií]os|r[ií]o bravo|r[ií]o blanco", re.I)


CUERPO_AGUA = re.compile(r"\br[ií]os?\b|\brivers?\b|\blagos?\b|\blakes?\b|\blagunas?\b|\blagoons?\b|\bcuencas?\b|\bbasins?\b", re.I)
FOTO = re.compile(r"photograph|fotograf|\bca\. ?1[89]\d\d|1[89]\d0s|church|iglesia|convento|village|scene on|women washing|"
                  r"wall fountain|old house|caldera|zircon|tephra|u-pb|\bglass\b|oral literature|literatura oral|ecomuseo|"
                  r"orfanato|psicol[oó]g|fossil vertebrates|cathedral|catedral|fa[cç]ade|aerial views|,\s*1[89]\d\d\s*$", re.I)


def tema_agua(t):
    """Términos temáticos de agua, sin contar nombres de cuerpos de agua."""
    t = CUERPO_AGUA.sub(" ", LUGAR_CON_AGUA.sub(" ", str(t or "")))
    return AGUA_ESTRICTO.findall(t)


def titulo_agua(t):
    t = str(t or "")
    if NEGATIVO.search(t) or FOTO.search(t):
        return False
    if tema_agua(t):
        return True
    return bool(CUERPO_AGUA.search(LUGAR_CON_AGUA.sub(" ", t))) and "__permitir_cuerpo__" in t


def titulo_agua_datos(t):
    """Para capas y conjuntos de datos: 'Ríos de Guatemala' o 'Cuencas' son el tema del dataset."""
    t = str(t or "")
    if NEGATIVO.search(t) or FOTO.search(t):
        return False
    return titulo_agua(t) or bool(CUERPO_AGUA.search(LUGAR_CON_AGUA.sub(" ", t)))


PRIMARIO_MOTAGUA = re.compile(r"motagua|las vacas|chinautla|tzalj[aá]|omoa", re.I)


def norm(t):
    t = unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def norm_doi(d):
    d = str(d or "").lower().strip()
    d = re.sub(r"^(https?://(dx\.)?doi\.org/|https?://doi\.pangaea\.de/|doi:)", "", d)
    return d if d.startswith("10.") else ""


def lugares(texto):
    vistos = []
    for m in LUGAR_GT.finditer(texto or ""):
        v = m.group(0).lower()
        if v not in vistos:
            vistos.append(v)
    return ", ".join(vistos[:6])


def parametros(texto):
    return ", ".join(n for n, p in PARAMS if re.search(p, texto or "", re.I))


def anios_muestreo(texto):
    t = texto or ""
    pats = [r"(?:between|entre|from|desde|de)\s+((?:19|20)\d{2})\s+(?:and|y|to|a|hasta)\s+((?:19|20)\d{2})",
            r"((?:19|20)\d{2})\s*[-–]\s*((?:19|20)\d{2})",
            r"(?:in|en|during|durante)\s+(?:(?:january|february|march|april|may|june|july|august|september|october|november|december|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+(?:of\s+|de\s+)?)?((?:19|20)\d{2})"]
    for p in pats:
        m = re.search(p, t, re.I)
        if m:
            return "-".join(m.groups()) + " (inferido del resumen)"
    return "No determinado (requiere revisar el texto completo)"


def leer_jsonl(p):
    out = []
    for linea in open(p, encoding="utf-8"):
        linea = linea.strip()
        if linea:
            out.append(json.loads(linea))
    return out


def leer_csv(p):
    return list(csv.DictReader(open(p, encoding="utf-8"))) if p.exists() else []


# ----------------------------------------------------------------- manifiestos
manif = []
for nombre in ["manifiesto_descargas.csv", "manifiesto_api.csv", "manifiesto_arcgis.csv"]:
    for r in leer_csv(RAIZ / "05_manifiesto" / nombre):
        r["_manifiesto"] = nombre
        manif.append(r)
descargados = [r for r in manif if r["estado"] == "descargado"]
por_clave = {r["clave"]: r for r in manif}

# títulos de documentos descargados: DIGI + primera página del PDF (caché)
titulos = {}
for f in ["digi_usac_informes_agua_titulos.csv", "digi_puirna_2018_2025_titulos_agua.csv"]:
    for r in leer_csv(RAIZ / "06_registro_busquedas" / f):
        titulos[f"USAC-DIGI-{r['codigo']}"] = r["titulo"]
cache_tit = RAIZ / "06_registro_busquedas" / "cache_titulos_pdf.json"
cache = json.load(open(cache_tit, encoding="utf-8")) if cache_tit.exists() else {}
try:
    from pypdf import PdfReader
    import logging
    logging.disable(logging.WARNING)
    for r in descargados:
        ruta = RAIZ / r["ruta_local"]
        if r["clave"] in titulos or r["clave"] in cache or ruta.suffix.lower() != ".pdf":
            continue
        try:
            rd = PdfReader(str(ruta))
            meta = (rd.metadata or {}).get("/Title") if rd.metadata else None
            txt = re.sub(r"\s+", " ", rd.pages[0].extract_text() or "")[:300]
            cache[r["clave"]] = {"meta": str(meta or ""), "texto": txt, "paginas": len(rd.pages)}
        except Exception as e:
            cache[r["clave"]] = {"meta": "", "texto": "", "paginas": "", "error": str(e)[:80]}
    json.dump(cache, open(cache_tit, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
except ImportError:
    pass

MARN_CAPAS = {
    "MARN_Rios_MAGA_2016": ("Ríos de Guatemala (MAGA, 2016)", "Red hidrográfica (líneas)"),
    "MARN_Cuencas_38_MAGA_2001": ("Cuencas hidrográficas de Guatemala - 38 cuencas (MAGA, 2001)", "Límites de cuenca"),
    "MARN_Subcuencas_MAGA_2001": ("Subcuencas hidrográficas (MAGA, 2001)", "Límites de subcuenca"),
    "MARN_Microcuencas": ("Microcuencas de Guatemala", "Límites de microcuenca"),
    "MARN_Lagos_Lagunas_MAGA_2001": ("Lagos y lagunas (MAGA, 2001)", "Cuerpos de agua lénticos"),
    "MARN_Cuerpos_agua_MAGA": ("Cuerpos de agua (MAGA)", "Cuerpos de agua"),
    "MARN_Rios_25m_ancho": ("Ríos de más de 25 m de ancho (polígonos)", "Cauces principales"),
    "MARN_Fuentes_agua": ("Fuentes de agua (puntos)", "Fuentes/nacimientos de agua"),
    "MARN_Rio_Samala": ("Río Samalá (eje)", "Río Samalá"),
    "MARN_Cuenca_Rio_Samala_Riesgo": ("Cuenca del Río Samalá - zonificación de riesgo", "Riesgo en cuenca"),
    "MARN_Inundaciones_ZMC": ("Amenaza por inundaciones - zona marino-costera", "Amenaza de inundación"),
    "MARN_Cuencas_ZMC": ("Cuencas de la zona marino-costera", "Cuencas costeras"),
    "MARN_Sitios_monitoreo_acidificacion": ("Sitios de monitoreo de acidificación oceánica", "Acidificación (puntos de monitoreo)"),
    "MARN_Potencial_mun_cuenca": ("Potencial por municipio y cuenca", "Uso potencial del territorio por cuenca"),
    "MARN_Produccion_acuicola_salinera": ("Producción acuícola y salinera (zona costera)", "Acuicultura y salinas"),
    "MARN_Ranking_municipal_residuos": ("Ranking municipal (gestión ambiental y de residuos)", "Indicadores municipales de gestión de residuos"),
    "MARN_Limite_costero": ("Límite costero (IGN, 2016)", "Línea de costa"),
    "MARN_Erosion_potencial": ("Erosión potencial", "Erosión hídrica potencial"),
    "MARN_Poblados_INE_2018": ("Lugares poblados (INE, 2018)", "Poblados (para cruzar con fuentes de agua)"),
    "MARN_Limites_municipales_IGN_2016": ("Límites municipales (IGN, 2016)", "Límites administrativos"),
}

# ----------------------------------------------------------------- filas manuales
filas, usados = [], set()
seq = Counter()


def nuevo_id(prefijo):
    seq[prefijo] += 1
    return f"{prefijo}-{seq[prefijo]:04d}"


def archivos_de(serie):
    if not serie:
        return []
    pref = [s for s in serie.split("|") if s]
    return [r for r in descargados if any(r["clave"].startswith(p) for p in pref)]


def fila_base(m, canal):
    return {
        "Organisation": m.get("org", ""), "Resource title": m.get("tit", ""), "Resource type": m.get("tipo", ""),
        "Dataset or publication": m.get("clase", ""), "Original URL": m.get("url", ""), "Download URL": m.get("dl", ""),
        "File format": m.get("fmt", ""), "Years covered": m.get("anios", ""), "Geographic coverage": m.get("geo", ""),
        "Parameters": m.get("params", ""), "Number of records (verified)": m.get("nreg", ""), "Licence": m.get("lic", ""),
        "Access status": m.get("acceso", ""), "Verification status": m.get("verif", ""), "Notes": m.get("notas", ""),
        "Source category": m.get("cat", ""), "Priority (1-5)": m.get("prio", ""), "Discovery channel": canal,
        "Access date": HOY,
    }


def fila_manual(m, arch, canal):
    f = fila_base(m, canal)
    f["Files retrieved"] = len(arch)
    f["Local files"] = "; ".join(a["ruta_local"] for a in arch[:20]) + (" …" if len(arch) > 20 else "")
    f["Download status"] = f"Descargado ({len(arch)} archivo{'s' if len(arch) != 1 else ''})" if arch else (
        "No descargado (portal o servicio)" if m.get("clase") == "Portal/Servicio" else "No descargado")
    if arch and m.get("dl") == "":
        f["Download URL"] = arch[0]["url"]
    if m.get("dlst"):
        f["Download status"] = m["dlst"]
    pref = {"Dataset": "GT-DAT", "Documento": "GT-DOC", "Portal/Servicio": "GT-POR", "Publicación": "GT-PUB"}.get(m.get("clase"), "GT-OTR")
    f["Resource ID"] = nuevo_id(pref)
    return f


manuales = []
for p in sorted((INV / "manual").glob("registro_*.jsonl")):
    manuales += leer_jsonl(p)
# Registros agregados después del corte del 21-oct-2026: sus ID se asignan al final para no mover los ya publicados
adenda = []
for p in sorted((INV / "manual").glob("adenda_*.jsonl")):
    adenda += leer_jsonl(p)

for m in manuales:
    arch = archivos_de(m.get("serie", ""))
    expandir = m.get("clase") == "Documento" and len(arch) >= 2
    if expandir:
        for a in arch:
            usados.add(a["clave"])
            f = fila_base(m, "Búsqueda dirigida / sitio oficial")
            tit = titulos.get(a["clave"]) or (cache.get(a["clave"], {}).get("meta") or "").strip()
            anio = re.findall(r"(?:19|20)\d{2}", a["clave"] + " " + a["ruta_local"])
            sufijo = Path(a["ruta_local"]).name
            f["Resource title"] = f"{m['tit']} — {tit}" if tit and len(tit) > 8 else f"{m['tit']} — {sufijo}"
            f["Years covered"] = anio[-1] if anio else m.get("anios", "")
            f["Download URL"] = a["url"]
            f["Files retrieved"] = 1
            f["Local files"] = a["ruta_local"]
            f["Download status"] = "Descargado"
            f["Verification status"] = "Verificado: archivo descargado (SHA-256 en manifiesto)"
            f["Resource ID"] = nuevo_id("GT-DOC")
            f["Notes"] = (f["Notes"] + " | Serie: " + m["k"]).strip(" |")
            f["Motagua / Las Vacas"] = "Sí" if PRIMARIO_MOTAGUA.search(tit or sufijo) else ""
            filas.append(f)
    else:
        for a in arch:
            usados.add(a["clave"])
        filas.append(fila_manual(m, arch, "Búsqueda dirigida / sitio oficial"))

for m in adenda:
    usados.update(a["clave"] for a in archivos_de(m.get("serie", "")))

# archivos descargados que no pertenecen a una serie manual
for a in descargados:
    if a["clave"] in usados:
        continue
    nombre = Path(a["ruta_local"]).name
    clave = a["clave"]
    f = {k: "" for k in CAMPOS}
    if clave.startswith("ARCGIS-"):
        capa = clave.replace("ARCGIS-", "")
        tit, par = MARN_CAPAS.get(capa, (capa, ""))
        f.update({"Organisation": "MARN (capas MAGA/IGN/INE/MARN publicadas en ArcGIS Online)", "Resource title": tit,
                  "Resource type": "Capa SIG (GeoJSON)", "Dataset or publication": "Dataset", "File format": "GeoJSON (EPSG:4326)",
                  "Parameters": par, "Geographic coverage": "Nacional" if "ZMC" not in capa and "Samala" not in capa else "Zona marino-costera / cuenca del Samalá",
                  "Number of records (verified)": a.get("nota", ""), "Licence": "No indicada (servicio público ArcGIS Online)",
                  "Access status": "Público", "Source category": "Gobierno GT", "Priority (1-5)": 2,
                  "Original URL": "https://www.arcgis.com/home/search.html?q=orgid%3A1ZwElXgfK1bj5Hq0"})
    elif clave.startswith("GHCN-D-GT"):
        continue  # se agregan en la fila del dataset GHCN
    else:
        org = a.get("organizacion", "")
        tit = titulos.get(clave) or (cache.get(clave, {}).get("meta") or "").strip() or nombre
        f.update({"Organisation": org, "Resource title": tit, "Resource type": "Documento/archivo descargado",
                  "Dataset or publication": "Documento", "File format": Path(nombre).suffix.upper().strip("."),
                  "Access status": "Público", "Source category": "Gobierno GT" if re.search(r"AMSA|INSIVUMEH|AMSCLAE|INE|INFOM|BANGUAT|MARN", org) else
                  ("Universidad" if re.search(r"USAC|IARNA|UVG", org) else "Internacional"), "Priority (1-5)": 3,
                  "Original URL": a["url"]})
        if clave.startswith("USAC-DIGI-"):
            f.update({"Resource type": "Informe final de investigación (DIGI-USAC)", "Original URL": "https://digi.usac.edu.gt/bvirtual/",
                      "Years covered": (re.findall(r"INF-(\d{4})", clave) or [""])[0] + " (año del informe)", "Source category": "Universidad",
                      "Priority (1-5)": 2 if PRIMARIO_MOTAGUA.search(tit) else 3})
    f.update({"Download URL": a["url"], "Files retrieved": 1, "Local files": a["ruta_local"], "Download status": "Descargado",
              "Verification status": "Verificado: archivo descargado (SHA-256 en manifiesto)",
              "Discovery channel": "Búsqueda dirigida / API", "Access date": a.get("fecha_acceso", "")[:10],
              "Resource ID": nuevo_id("GT-DAT" if f["Dataset or publication"] == "Dataset" else "GT-DOC")})
    filas.append(f)

# GHCN: actualizar conteo de estaciones descargadas
ghcn = [a for a in descargados if a["clave"].startswith("GHCN-D-GT")]
for f in filas:
    if f["Organisation"].startswith("NOAA NCEI") and "GHCN" in f["Resource title"]:
        f["Files retrieved"] = len(ghcn) + len(archivos_de("GHCN-D-ESTACIONES|GHCN-D-INVENTARIO"))
        if ghcn:
            f["Number of records (verified)"] = f"{len(ghcn)} series de estación descargadas"
            f["Download status"] = f"Descargado ({len(ghcn)} series)"
            f["Local files"] = "02_datos_originales/NOAA_GHCN/series/"

# ----------------------------------------------------------------- fuentes automáticas
AUTO = INV / "auto"
claves_vistas = {}  # clave de deduplicación -> Resource ID
duplicados = []


def claves_dedup(doi, url, titulo, anio):
    ks = []
    if norm_doi(doi):
        ks.append("doi:" + norm_doi(doi))
    if url:
        ks.append("url:" + re.sub(r"^https?://(www\.)?", "", url.lower()).rstrip("/"))
    nt = norm(titulo)
    if len(nt) > 25:
        ks.append("tit:" + nt[:120])
    elif len(nt) > 6:
        ks.append("titcorto:" + nt + "|" + norm(url)[:40])
    return ks


for f in filas:
    for k in claves_dedup("", f["Original URL"] if f["Dataset or publication"] != "Portal/Servicio" else "", f["Resource title"], ""):
        if k.startswith("url:") and f["Files retrieved"] not in ("", 0) and f["Dataset or publication"] == "Documento":
            claves_vistas.setdefault(k, f["Resource ID"])
        elif k.startswith("tit:"):
            claves_vistas.setdefault(k, f["Resource ID"])
    if f["Download URL"]:
        claves_vistas.setdefault("url:" + re.sub(r"^https?://(www\.)?", "", f["Download URL"].lower()).rstrip("/"), f["Resource ID"])


def agregar_auto(f, doi, canal):
    ks = claves_dedup(doi, f["Original URL"], f["Resource title"], f["Years covered"])
    previo = next((claves_vistas[k] for k in ks if k in claves_vistas), None)
    if previo:
        duplicados.append({"Duplicate of": previo, "Discovery channel": canal, "Title": f["Resource title"][:250],
                           "URL": f["Original URL"], "Match key": next(k for k in ks if k in claves_vistas)[:140]})
        return False
    pref = {"Dataset": "GT-DAT", "Publicación": "GT-PUB", "Portal/Servicio": "GT-POR"}.get(f["Dataset or publication"], "GT-DOC")
    f["Resource ID"] = nuevo_id(pref)
    for k in ks:
        claves_vistas[k] = f["Resource ID"]
    f["Discovery channel"] = canal
    f["Access date"] = f.get("Access date") or HOY
    filas.append(f)
    return True


pubs_extra = {}  # Resource ID -> datos extra de publicación


def es_relevante(*t):
    texto = " ".join(str(x or "") for x in t)
    return bool(LUGAR_GT.search(texto)) and bool(AGUA_ESTRICTO.search(texto))


# OAI (tesis y artículos de repositorios guatemaltecos: la ubicación en Guatemala es implícita)
for nombre_csv, org in [("oai_uvg_dspace.csv", "Universidad del Valle de Guatemala (repositorio institucional)"),
                        ("oai_usac_eprints.csv", "Universidad de San Carlos de Guatemala (repositorio institucional)"),
                        ("oai_revistas_usac_ojs.csv", "Universidad de San Carlos de Guatemala (portal de revistas)")]:
    for r in leer_csv(AUTO / nombre_csv):
        texto = f"{r['titulo']} {r['materias']}"
        cuerpo = bool(CUERPO_AGUA.search(LUGAR_CON_AGUA.sub(" ", r["titulo"])))
        if not (titulo_agua(r["titulo"]) or (cuerpo and not FOTO.search(r["titulo"]) and not NEGATIVO.search(r["titulo"])
                                            and len(tema_agua(r["materias"] + " " + r["resumen_inicio"])) >= 2)):
            continue
        anio = (re.findall(r"(?:19|20)\d{2}", r["fecha"]) or [""])[0]
        tipo = r["tipo"].lower()
        es_tesis = bool(re.search(r"thesis|tesis|trabajo de grad", tipo)) or "repositorio institucional" in org
        f = {k: "" for k in CAMPOS}
        f.update({"Organisation": org, "Resource title": r["titulo"], "Resource type": "Tesis" if es_tesis and "revista" not in org else "Artículo científico",
                  "Dataset or publication": "Publicación", "Original URL": r["url"], "File format": "PDF (repositorio)",
                  "Years covered": f"{anio} (publicación)" if anio else "", "Geographic coverage": lugares(texto + " " + r["resumen_inicio"]) or "Guatemala (implícito)",
                  "Parameters": parametros(texto + " " + r["resumen_inicio"]), "Licence": r["derechos"][:120] or "No indicada",
                  "Access status": "Público (repositorio abierto)", "Download status": "No descargado (metadatos; texto completo enlazado)",
                  "Verification status": "Verificado: metadatos OAI-PMH del repositorio", "Source category": "Universidad",
                  "Priority (1-5)": 2 if PRIMARIO_MOTAGUA.search(texto) else 3, "Notes": f"Autores: {r['autores'][:150]}",
                  "Motagua / Las Vacas": "Sí" if PRIMARIO_MOTAGUA.search(texto + r["resumen_inicio"]) else ""})
        if agregar_auto(f, "", f"OAI-PMH {nombre_csv[4:-4]}"):
            pubs_extra[f["Resource ID"]] = {"autores": r["autores"], "anio": anio, "revista": org, "doi": "",
                                            "resumen": r["resumen_inicio"], "tipo": f["Resource type"]}

# OpenAlex
for r in leer_csv(AUTO / "openalex_publicaciones.csv"):
    texto = f"{r['titulo']} {r['resumen_inicio']}"
    if not es_relevante(r["titulo"], r["resumen_inicio"]):
        continue
    if not (LUGAR_GT.search(r["titulo"]) or len(LUGAR_GT.findall(r["resumen_inicio"])) >= 2):
        continue  # menciones de paso a Guatemala
    if NEGATIVO.search(r["titulo"]):
        continue
    if FOTO.search(r["titulo"]):
        continue
    cuerpo = bool(CUERPO_AGUA.search(LUGAR_CON_AGUA.sub(" ", r["titulo"])))
    if not (titulo_agua(r["titulo"]) or (cuerpo and len(tema_agua(r["resumen_inicio"])) >= 2)):
        continue  # el agua no es tema central
    oa = str(r["acceso_abierto"]).lower() == "true"
    f = {k: "" for k in CAMPOS}
    f.update({"Organisation": r["revista_o_fuente"] or (r["instituciones"].split(";")[0] if r["instituciones"] else "OpenAlex"),
              "Resource title": r["titulo"], "Resource type": {"article": "Artículo científico", "dissertation": "Tesis",
              "book-chapter": "Capítulo de libro", "dataset": "Dataset", "report": "Informe", "book": "Libro"}.get(r["tipo"], r["tipo"]),
              "Dataset or publication": "Dataset" if r["tipo"] == "dataset" else "Publicación",
              "Original URL": r["doi"] or r["landing_url"], "Download URL": r["url_oa"], "File format": "PDF/HTML",
              "Years covered": f"{r['anio_publicacion']} (publicación)", "Geographic coverage": lugares(texto),
              "Parameters": parametros(texto), "Licence": "Acceso abierto (ver editor)" if oa else "Según editor",
              "Access status": "Público (acceso abierto)" if oa else "Restringido o no determinado (suscripción)",
              "Download status": "No descargado (metadatos; se respeta derecho de autor)",
              "Verification status": "Verificado: metadatos OpenAlex API", "Source category": "Publicación científica",
              "Priority (1-5)": 2 if PRIMARIO_MOTAGUA.search(texto) else 3,
              "Notes": f"Autores: {r['autores'][:150]} | Instituciones: {r['instituciones'][:150]} | Citas: {r['citas']}",
              "Motagua / Las Vacas": "Sí" if PRIMARIO_MOTAGUA.search(texto) else ""})
    if agregar_auto(f, r["doi"], "OpenAlex API"):
        pubs_extra[f["Resource ID"]] = {"autores": r["autores"], "anio": r["anio_publicacion"], "revista": r["revista_o_fuente"],
                                        "doi": r["doi"], "resumen": r["resumen_inicio"], "tipo": f["Resource type"]}

# Crossref (complementa OpenAlex; se deduplica por DOI)
for r in leer_csv(AUTO / "crossref_publicaciones.csv"):
    texto = f"{r['titulo']} {r['resumen_inicio']}"
    if FOTO.search(r["titulo"]) or NEGATIVO.search(r["titulo"]) or not es_relevante(texto):
        continue
    if not (LUGAR_GT.search(r["titulo"]) or len(LUGAR_GT.findall(r["resumen_inicio"])) >= 2):
        continue
    cuerpo = bool(CUERPO_AGUA.search(LUGAR_CON_AGUA.sub(" ", r["titulo"])))
    if not (titulo_agua(r["titulo"]) or (cuerpo and len(tema_agua(r["resumen_inicio"])) >= 2)):
        continue
    f = {k: "" for k in CAMPOS}
    f.update({"Organisation": r["revista"] or "Crossref", "Resource title": r["titulo"],
              "Resource type": {"journal-article": "Artículo científico", "dissertation": "Tesis", "book-chapter": "Capítulo de libro",
                                "dataset": "Dataset", "report": "Informe", "posted-content": "Preprint"}.get(r["tipo"], r["tipo"]),
              "Dataset or publication": "Dataset" if r["tipo"] == "dataset" else "Publicación", "Original URL": r["doi"],
              "File format": "PDF/HTML", "Years covered": f"{r['anio']} (publicación)", "Geographic coverage": lugares(texto),
              "Parameters": parametros(texto), "Licence": "Según editor", "Access status": "No determinado (ver editor)",
              "Download status": "No descargado (metadatos; se respeta derecho de autor)", "Verification status": "Verificado: metadatos Crossref API",
              "Source category": "Publicación científica", "Priority (1-5)": 2 if PRIMARIO_MOTAGUA.search(texto) else 3,
              "Notes": f"Autores: {r['autores'][:150]}", "Motagua / Las Vacas": "Sí" if PRIMARIO_MOTAGUA.search(texto) else ""})
    if agregar_auto(f, r["doi"], "Crossref API"):
        pubs_extra[f["Resource ID"]] = {"autores": r["autores"], "anio": r["anio"], "revista": r["revista"], "doi": r["doi"],
                                        "resumen": r["resumen_inicio"], "tipo": f["Resource type"]}

# Repositorios de datos (DataCite, Zenodo, Dataverse, Figshare, PANGAEA)
for r in leer_csv(AUTO / "datacite_datasets.csv"):
    texto = f"{r['titulo']} {r['descripcion_inicio']}"
    if FOTO.search(r["titulo"]) or not es_relevante(texto) or not titulo_agua(r["titulo"]) and not re.search(r"lake|lago|sediment|precipit|meteorolog", r["titulo"], re.I):
        continue
    if NEGATIVO.search(r["titulo"]) or re.search(r"\b(19[0-4]\d)\b\s*$", r["titulo"]):
        continue  # fotografías históricas y descargas de ocurrencias
    f = {k: "" for k in CAMPOS}
    f.update({"Organisation": r["editor"], "Resource title": r["titulo"], "Resource type": "Dataset (repositorio DOI)",
              "Dataset or publication": "Dataset", "Original URL": r["doi"], "Download URL": r["url"], "File format": r["formatos"] or "No indicado",
              "Years covered": f"{r['anio']} (publicación del dataset)", "Geographic coverage": lugares(texto), "Parameters": parametros(texto),
              "Licence": r["licencia"] or "No indicada", "Access status": "Público (repositorio)", "Download status": "No descargado (metadatos)",
              "Verification status": "Verificado: metadatos DataCite API", "Source category": "Repositorio de datos", "Priority (1-5)": 3,
              "Notes": f"Autores: {r['autores'][:150]} | Tamaño: {r['tamanos'][:60]}", "Motagua / Las Vacas": "Sí" if PRIMARIO_MOTAGUA.search(texto) else ""})
    agregar_auto(f, r["doi"], "DataCite API")

for r in leer_csv(AUTO / "zenodo_registros.csv"):
    texto = f"{r['titulo']} {r['descripcion_inicio']}"
    if not es_relevante(texto) or not titulo_agua(r["titulo"]):
        continue
    es_ds = r["tipo"] in ("dataset", "software", "image", "video")
    f = {k: "" for k in CAMPOS}
    f.update({"Organisation": "Zenodo (" + r["autores"][:60] + ")", "Resource title": r["titulo"], "Resource type": f"Zenodo: {r['tipo']}",
              "Dataset or publication": "Dataset" if es_ds else "Publicación", "Original URL": r["doi"] or r["url"], "Download URL": r["url"],
              "File format": ", ".join(sorted({Path(x).suffix.upper().strip('.') for x in r["archivos"].split("; ") if x})),
              "Years covered": f"{r['fecha'][:4]} (publicación)", "Geographic coverage": lugares(texto), "Parameters": parametros(texto),
              "Number of records (verified)": f"{r['n_archivos']} archivos; {int(float(r['bytes_total'] or 0))/1e6:.1f} MB",
              "Licence": r["licencia"], "Access status": "Público" if r["acceso"] == "open" else r["acceso"], "Download status": "No descargado (metadatos)",
              "Verification status": "Verificado: metadatos Zenodo API", "Source category": "Repositorio de datos", "Priority (1-5)": 3,
              "Motagua / Las Vacas": "Sí" if PRIMARIO_MOTAGUA.search(texto) else ""})
    agregar_auto(f, r["doi"], "Zenodo API")

for r in leer_csv(AUTO / "dataverse_datasets.csv"):
    texto = f"{r['titulo']} {r['descripcion_inicio']}"
    if not es_relevante(texto) or not titulo_agua(r["titulo"]):
        continue
    f = {k: "" for k in CAMPOS}
    f.update({"Organisation": "Harvard Dataverse", "Resource title": r["titulo"], "Resource type": "Dataset (Dataverse)", "Dataset or publication": "Dataset",
              "Original URL": r["url"], "Years covered": f"{r['publicado'][:4]} (publicación)", "Geographic coverage": lugares(texto),
              "Parameters": parametros(texto), "Number of records (verified)": f"{r['n_archivos']} archivos", "Access status": "Público (repositorio)",
              "Download status": "No descargado (metadatos)", "Verification status": "Verificado: metadatos Dataverse API",
              "Source category": "Repositorio de datos", "Priority (1-5)": 3, "Notes": f"Autores: {r['autores'][:150]}"})
    agregar_auto(f, r["id"].replace("doi:", "https://doi.org/") if r["id"].startswith("doi:") else "", "Harvard Dataverse API")

for r in leer_csv(AUTO / "figshare_items.csv"):
    if not es_relevante(r["titulo"]) or not titulo_agua(r["titulo"]):
        continue
    f = {k: "" for k in CAMPOS}
    f.update({"Organisation": "Figshare", "Resource title": r["titulo"], "Resource type": f"Figshare: {r['tipo']}",
              "Dataset or publication": "Dataset" if r["tipo"] in ("dataset", "figure", "fileset") else "Publicación",
              "Original URL": r["url"], "Years covered": f"{r['publicado'][:4]} (publicación)", "Geographic coverage": lugares(r["titulo"]),
              "Access status": "Público (repositorio)", "Download status": "No descargado (metadatos)",
              "Verification status": "Verificado: metadatos Figshare API", "Source category": "Repositorio de datos", "Priority (1-5)": 4})
    agregar_auto(f, r["doi"], "Figshare API")

for r in leer_csv(AUTO / "pangaea_datasets.csv"):
    if NEGATIVO.search(r["texto"][:250]) or FOTO.search(r["texto"][:250]) or not re.search(r"lake|lago|pet[eé]n|atitl|izabal|amatitl|river|r[ií]o|meteorolog|precipitation|rainfall|spring|cave|drip|speleothem", r["texto"][:300], re.I):
        continue
    f = {k: "" for k in CAMPOS}
    f.update({"Organisation": "PANGAEA", "Resource title": r["texto"][:300], "Resource type": "Dataset (PANGAEA)", "Dataset or publication": "Dataset",
              "Original URL": r["doi"], "Geographic coverage": lugares(r["texto"]), "Parameters": parametros(r["texto"]), "Licence": "CC BY (PANGAEA, típico)",
              "Access status": "Público", "Download status": "No descargado (metadatos)", "Verification status": "Verificado: búsqueda PANGAEA API",
              "Source category": "Repositorio de datos", "Priority (1-5)": 4, "Notes": "Mayormente núcleos de sedimento/paleolimnología."})
    agregar_auto(f, r["doi"], "PANGAEA API")

# HDX, CKAN y ArcGIS Online
for r in leer_csv(AUTO / "hdx_datasets.csv"):
    texto = f"{r['titulo']} {r['tags']}"
    if not titulo_agua_datos(r["titulo"]):
        continue
    f = {k: "" for k in CAMPOS}
    f.update({"Organisation": r["organizacion"] + " (vía HDX)", "Resource title": r["titulo"], "Resource type": "Dataset (HDX)",
              "Dataset or publication": "Dataset", "Original URL": r["url"], "Download URL": r["descargas"].split("; ")[0],
              "File format": r["formatos"], "Years covered": r["cobertura_temporal"], "Geographic coverage": "Guatemala",
              "Parameters": parametros(texto) or r["tags"][:120], "Licence": r["licencia"], "Access status": "Público",
              "Download status": "No descargado (metadatos)", "Verification status": "Verificado: metadatos HDX CKAN API",
              "Source category": "Internacional", "Priority (1-5)": 4, "Number of records (verified)": f"{r['n_recursos']} recursos"})
    agregar_auto(f, "", "HDX CKAN API")

for r in leer_csv(AUTO / "ckan_portales.csv"):
    texto = f"{r['titulo']} {r['resumen']}"
    if r["portal"] in ("SE-CONRED", "SEGEPLAN"):
        continue  # ya representados como portales en el registro manual
    if not (titulo_agua_datos(r["titulo"]) and (LUGAR_GT.search(texto) or re.search(r"trifinio", texto, re.I))):
        continue
    f = {k: "" for k in CAMPOS}
    f.update({"Organisation": (r["organizacion"] or r["portal"]) + f" (vía {r['portal']})", "Resource title": r["titulo"],
              "Resource type": f"Dataset ({r['portal']})", "Dataset or publication": "Dataset", "Original URL": r["url"],
              "Download URL": r["recursos"].split(" | ")[0], "File format": r["formatos"], "Geographic coverage": lugares(texto) or "Guatemala",
              "Parameters": parametros(texto), "Licence": r["licencia"], "Access status": "Público", "Download status": "No descargado (metadatos)",
              "Verification status": f"Verificado: metadatos CKAN API ({r['portal']})", "Source category": "Internacional", "Priority (1-5)": 4,
              "Number of records (verified)": f"{r['n_recursos']} recursos"})
    agregar_auto(f, "", f"CKAN API {r['portal']}")

for r in leer_csv(AUTO / "arcgis_online_items.csv"):
    texto = f"{r['titulo']} {r['resumen']} {r['tags']}"
    if not titulo_agua_datos(r["titulo"]) or re.search(r"belize|belice|honduras|el salvador|m[eé]xico|mexico", r["titulo"], re.I) and not LUGAR_GT.search(r["titulo"]):
        continue
    if r["org_id"] == "1ZwElXgfK1bj5Hq0" and r["url_servicio"] and "services1.arcgis.com" in r["url_servicio"]:
        nombre_capa = r["url_servicio"].rstrip("/").split("/")[-2] if r["url_servicio"].endswith("FeatureServer") else ""
        if any(nombre_capa and nombre_capa.lower().startswith(c.split("_")[1].lower()) for c in MARN_CAPAS):
            continue
    f = {k: "" for k in CAMPOS}
    es_portal = r["tipo"] in ("Web Map", "Web Experience", "Dashboard", "Web Mapping Application", "StoryMap", "Hub Site Application")
    f.update({"Organisation": f"{r['propietario']} (ArcGIS Online, org {r['org_id']})", "Resource title": r["titulo"],
              "Resource type": f"ArcGIS: {r['tipo']}", "Dataset or publication": "Portal/Servicio" if es_portal else "Dataset",
              "Original URL": r["url_item"], "Download URL": r["url_servicio"], "File format": r["tipo"],
              "Years covered": f"{r['creado'][:4]}-{r['modificado'][:4]} (creación-modificación del ítem)",
              "Geographic coverage": lugares(texto) or "Guatemala (extensión del ítem)", "Parameters": parametros(texto),
              "Licence": r["licencia"] or "No indicada", "Access status": "Público (ítem ArcGIS Online)", "Download status": "No descargado (metadatos)",
              "Verification status": "Verificado: metadatos ArcGIS Online API", "Source category": "Plataforma SIG", "Priority (1-5)": 4,
              "Notes": r["resumen"][:200], "Motagua / Las Vacas": "Sí" if PRIMARIO_MOTAGUA.search(texto) else ""})
    agregar_auto(f, "", "ArcGIS Online search API")

# ----------------------------------------------------------------- adenda (ID al final de cada serie)
for m in adenda:
    filas.append(fila_manual(m, archivos_de(m.get("serie", "")), m.get("canal") or "Adenda posterior al corte"))

# ----------------------------------------------------------------- verificación de URLs (filas no bibliográficas)


def chequear(url):
    if not url or not url.startswith("http"):
        return url, ""
    try:
        out = subprocess.run(["curl", "-s", "-o", "NUL", "-L", "-m", "25", "-r", "0-0", "-A", "Mozilla/5.0 (RiosAbiertosGT)",
                              "-w", "%{http_code}", url], capture_output=True, timeout=40)
        return url, out.stdout.decode().strip() or "sin respuesta"
    except Exception:
        return url, "sin respuesta"


if VERIFICAR:
    urls = sorted({f["Original URL"] for f in filas if f["Discovery channel"].startswith("Búsqueda") and f["Original URL"]})
    with cf.ThreadPoolExecutor(12) as ex:
        res = dict(ex.map(chequear, urls))
    for f in filas:
        if f["Original URL"] in res:
            c = res[f["Original URL"]]
            f["URL check (HTTP)"] = f"{c} ({HOY})"
            if f["Verification status"].startswith("Por verificar"):
                if c in ("200", "202", "206"):
                    f["Verification status"] = f"Verificado: URL responde HTTP {c}"
                elif c == "403":
                    f["Verification status"] = "URL hallada en buscador; el servidor responde 403 a clientes automáticos (protección anti-bots)"
                else:
                    f["Verification status"] = f"URL con problema: HTTP {c}"

for f in filas:
    if not f.get("Motagua / Las Vacas"):
        texto = " ".join(str(f[c]) for c in ["Resource title", "Geographic coverage", "Notes"])
        f["Motagua / Las Vacas"] = "Sí" if PRIMARIO_MOTAGUA.search(texto) else ""
    for c in CAMPOS:
        f.setdefault(c, "")

df = pd.DataFrame(filas, columns=CAMPOS)

# ----------------------------------------------------------------- tabla de publicaciones
pubs = []
for f in filas:
    if f["Dataset or publication"] != "Publicación" and not f["Resource type"].startswith(("Informe final", "Tesis", "Artículo")):
        continue
    x = pubs_extra.get(f["Resource ID"], {})
    texto = f"{f['Resource title']} {x.get('resumen', '')}"
    numeros = bool(re.search(r"\d+(?:[.,]\d+)?\s*(?:mg/?l|µg|ug/l|ng/l|nmp|ufc|cfu|m3/s|m³/s|%|°c|mm)", x.get("resumen", ""), re.I))
    pubs.append({
        "Resource ID": f["Resource ID"], "Title": f["Resource title"], "Authors": x.get("autores", ""),
        "Year of publication": x.get("anio") or (re.findall(r"(?:19|20)\d{2}", f["Years covered"]) or [""])[0],
        "DOI or permanent URL": x.get("doi") or f["Original URL"] or f["Download URL"],
        "Institution or journal": x.get("revista") or f["Organisation"], "Publication type": f["Resource type"],
        "Study location": f["Geographic coverage"], "Years when samples were collected": anios_muestreo(x.get("resumen", "")),
        "Water parameters investigated": f["Parameters"] or "No determinado",
        "Numerical results available": "Probable (el resumen reporta valores con unidades)" if numeros else "No determinado (requiere texto completo)",
        "Raw data / supplementary files": "Sí (archivo descargado)" if f["Files retrieved"] not in ("", 0) else "No verificado",
        "Access": f["Access status"], "Already identified elsewhere": "", "Discovery channel": f["Discovery channel"],
    })
dup_por_id = defaultdict(list)
for d in duplicados:
    dup_por_id[d["Duplicate of"]].append(d["Discovery channel"])
for p in pubs:
    if p["Resource ID"] in dup_por_id:
        p["Already identified elsewhere"] = "Sí: también en " + ", ".join(sorted(set(dup_por_id[p["Resource ID"]])))
dpub = pd.DataFrame(pubs)

# ----------------------------------------------------------------- resumen por organización


def org_raiz(o):
    o = re.sub(r"\s*\(.*?\)", "", o or "")
    return o.split(" - ")[0].split(" / ")[0].strip()[:90]


def rango(serie):
    anios = []
    for v in serie:
        anios += [int(a) for a in re.findall(r"(?:19|20)\d{2}", str(v)) if 1900 < int(a) <= 2026]
    return f"{min(anios)}-{max(anios)}" if anios else ""


df_core = df[~df["Discovery channel"].isin(["OpenAlex API"])]
res = []
for o, g in df_core.groupby(df_core["Organisation"].map(org_raiz)):
    params = Counter(p.strip() for v in g["Parameters"] for p in str(v).split(",") if p.strip() and len(p.strip()) < 40)
    res.append({"Organisation": o, "Source category": g["Source category"].mode().iat[0] if len(g) else "",
                "Resources (rows)": len(g), "Unique datasets": int((g["Dataset or publication"] == "Dataset").sum()),
                "Documents/reports": int((g["Dataset or publication"] == "Documento").sum()),
                "Publications": int((g["Dataset or publication"] == "Publicación").sum()),
                "Portals/services": int((g["Dataset or publication"] == "Portal/Servicio").sum()),
                "Files retrieved": int(pd.to_numeric(g["Files retrieved"], errors="coerce").fillna(0).sum()),
                "Data years": rango(g["Years covered"]), "Main variables": ", ".join(k for k, _ in params.most_common(6)),
                "Accessibility": g["Access status"].mode().iat[0] if len(g) else ""})
pubs_org = Counter(org_raiz(o) for o in df[df["Discovery channel"] == "OpenAlex API"]["Organisation"])
dres = pd.DataFrame(res).sort_values(["Files retrieved", "Resources (rows)"], ascending=False)

# ----------------------------------------------------------------- faltantes, archivos, diccionario
dfalt = pd.DataFrame([{"Organisation": x["org"], "Evidence of monitoring/data collection": x["evidencia"],
                       "Expected data type": x["tipo_esperado"], "Website / evidence URL": x["url"],
                       "What was attempted": x["intento"], "Reason access failed": x["razon"],
                       "Status category": x["categoria"], "Formal request feasible": x["solicitud"],
                       "Recommended next action": x["accion"]} for x in leer_jsonl(INV / "manual" / "faltantes.jsonl")])
darch = pd.DataFrame([{k: r.get(k, "") for k in ["clave", "organizacion", "url", "ruta_local", "estado", "http", "bytes", "sha256", "fecha_acceso", "nota", "_manifiesto"]} for r in manif])
ddup = pd.DataFrame(duplicados)
dicc = pd.DataFrame([
    ("Resource ID", "Identificador único: GT-DAT (dataset), GT-DOC (documento/informe), GT-PUB (publicación), GT-POR (portal/servicio)."),
    ("Dataset or publication", "Clase del recurso: Dataset, Documento, Publicación o Portal/Servicio."),
    ("Years covered", "Años de los datos cuando se verificaron; '(publicación)' indica año de publicación, no de muestreo."),
    ("Number of records (verified)", "Solo se llena cuando se contó en el archivo o en la API."),
    ("Download status", "'Descargado' significa que el archivo original está en 02_datos_originales; los metadatos no cuentan como descarga."),
    ("Verification status", "Cómo se verificó: archivo descargado, metadatos de API, URL con HTTP 200, o pendiente/fallido."),
    ("URL check (HTTP)", "Código HTTP de la URL original el día de la compilación (solo filas de búsqueda dirigida)."),
    ("Discovery channel", "Canal por el que se halló el recurso (búsqueda dirigida, OpenAlex, OAI-PMH, DataCite, etc.)."),
    ("Motagua / Las Vacas", "Marca recursos de la prioridad 2 (cuenca del Motagua: Motagua, Las Vacas, Chinautla, Tzaljá; desembocadura en Omoa)."),
], columns=["Campo", "Definición"])

# ----------------------------------------------------------------- salidas
df.to_csv(INV / "inventario_maestro.csv", index=False, encoding="utf-8-sig")
dpub.to_csv(INV / "publicaciones.csv", index=False, encoding="utf-8-sig")
dres.to_csv(INV / "resumen_por_organizacion.csv", index=False, encoding="utf-8-sig")
dfalt.to_csv(INV / "registro_datos_faltantes.csv", index=False, encoding="utf-8-sig")
ddup.to_csv(INV / "duplicados_detectados.csv", index=False, encoding="utf-8-sig")
with pd.ExcelWriter(INV / "inventario_rios_abiertos_gt.xlsx", engine="openpyxl") as xw:
    df.to_excel(xw, sheet_name="Inventario maestro", index=False)
    dres.to_excel(xw, sheet_name="Resumen por organización", index=False)
    dpub.to_excel(xw, sheet_name="Publicaciones", index=False)
    dfalt.to_excel(xw, sheet_name="Datos faltantes", index=False)
    ddup.to_excel(xw, sheet_name="Duplicados", index=False)
    darch.to_excel(xw, sheet_name="Archivos descargados", index=False)
    dicc.to_excel(xw, sheet_name="Diccionario", index=False)
    for hoja in xw.sheets.values():
        hoja.freeze_panes = "B2"
        for col in hoja.columns:
            hoja.column_dimensions[col[0].column_letter].width = min(60, max(10, max(len(str(c.value or "")) for c in col[:50]) + 2))

with open(RAIZ / "05_manifiesto" / "checksums_sha256.txt", "w", encoding="utf-8") as fh:
    for r in descargados:
        fh.write(f"{r['sha256']}  {r['ruta_local']}\n")

no_bib = df[df["Dataset or publication"] != "Publicación"]
est = {
    "fecha": HOY,
    "filas_inventario": len(df),
    "por_clase": df["Dataset or publication"].value_counts().to_dict(),
    "por_categoria": df["Source category"].value_counts().to_dict(),
    "por_canal": df["Discovery channel"].value_counts().to_dict(),
    "datasets_unicos": int((df["Dataset or publication"] == "Dataset").sum()),
    "datasets_con_archivo_descargado": int(((df["Dataset or publication"] == "Dataset") & (pd.to_numeric(df["Files retrieved"], errors="coerce").fillna(0) > 0)).sum()),
    "recursos_con_archivo_descargado": int((pd.to_numeric(df["Files retrieved"], errors="coerce").fillna(0) > 0).sum()),
    "archivos_descargados": len(descargados),
    "bytes_descargados": int(sum(int(r["bytes"] or 0) for r in descargados)),
    "descargas_fallidas": len([r for r in manif if r["estado"] != "descargado"]),
    "publicaciones": int((df["Dataset or publication"] == "Publicación").sum()),
    "publicaciones_acceso_abierto": int(((df["Dataset or publication"] == "Publicación") & df["Access status"].str.startswith("Público")).sum()),
    "organizaciones_no_bibliograficas": int(no_bib["Organisation"].map(org_raiz).nunique()),
    "organizaciones_en_resumen": len(dres),
    "faltantes": len(dfalt),
    "duplicados_detectados": len(ddup),
    "motagua_las_vacas": int((df["Motagua / Las Vacas"] == "Sí").sum()),
    "rango_anios_global": rango(no_bib["Years covered"]),
    "urls_chequeadas": int(df["URL check (HTTP)"].astype(bool).sum()),
    "urls_ok": int(df["URL check (HTTP)"].str.match(r"^(200|202|206)").sum()),
    "urls_403": int(df["URL check (HTTP)"].str.match(r"^403").sum()),
    "urls_404_u_otro": int(df["URL check (HTTP)"].str.match(r"^(404|000|5|sin)").sum()),
}
json.dump(est, open(INV / "estadisticas_inventario.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(est, ensure_ascii=False, indent=1))
