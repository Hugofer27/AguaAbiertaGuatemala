"""Construye la carpeta pública `datos/` de Agua Abierta Guatemala.

Lee únicamente archivos versionados en `versions/` (inventarios, manifiestos y
datos procesados) y genera:

- datos/catalogo/   catálogo unificado sin duplicados, publicaciones, faltantes
- datos/capas/      un GeoJSON por capa del mapa
- datos/mediciones/ mediciones en formato largo, sitios y diccionario de parámetros
- datos/manifiesto/ archivos originales con SHA-256 para el paquete de respaldo
- datos/app/        JSON compactos que consume la aplicación web

Uso:  python pipeline/construir_datos.py
Requiere Python 3.10+ y solo la biblioteca estándar.
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from comun import (
    DATOS,
    VERSIONES,
    anios,
    clave_laxa,
    clave_texto,
    dentro_de_guatemala,
    escribir_csv,
    escribir_json,
    leer_csv,
    leer_json,
    normalizar_url,
    numero,
    tamano_legible,
)

CLAUDE = VERSIONES / "claude"
CODEX = VERSIONES / "codex"
ANTIGRAVITY = VERSIONES / "antigravity"
PIPELINE = Path(__file__).resolve().parent

VERSION = "1.0.0"
FECHA_CORTE = "2026-10-22"

# ---------------------------------------------------------------------------
# Vocabularios
# ---------------------------------------------------------------------------

TIPOS = {
    "Dataset": "Conjunto de datos",
    "Documento": "Documento",
    "Portal/Servicio": "Portal o servicio",
}

TEMAS = [
    ("Agua subterránea", r"subterr|acu[ií]fer|\bpozos?\b|hidrogeol|groundwater"),
    ("Residuos y plásticos", r"pl[aá]stic|residuos s[oó]lidos|desechos|vertedero|basura|plastic"),
    ("Riesgo e inundaciones", r"inundaci|desastre|amenaza|sequ[ií]a|hurac|flood|riesgo"),
    ("Agua potable y saneamiento", r"potable|consumo humano|abastecimiento|saneamiento|cloro|ptar|aguas residuales|alcantarill|empagua|wash|drinking|sanitation|wastewater|puntos de agua|water points?"),
    ("Calidad del agua", r"calidad|fisicoqu|microbiol|coliform|contamina|metales|nutrient|limnol|\bdbo|\bdqo|ox[ií]geno|icotro|cianobac|cianosem|eutrof|acidificaci|f[aá]rmac|quality"),
    ("Limnología y sedimentos", r"sediment|\bcores?\b|pollen|polen|ostracod|\bxrf\b|geochem|isotop|limnol|lake |lago |laguna "),
    ("Caudales e hidrología", r"caudal|hidrol[oó]g|hidrom|nivel|aforo|escorrent|balance h[ií]dr|discharge|streamflow|r[ií]os\b|hydro|surface water"),
    ("Clima y lluvia", r"clima|meteorol|precipit|lluvia|temperatura|chirps|ghcn|rainfall|weather"),
    ("Cuencas y cartografía", r"cuenca|subcuenca|microcuenca|l[ií]mite|cartograf|mapa|capa|geojson|arcgis|storymap|dashboard|vertiente|watershed"),
    ("Estadística y gobernanza", r"indicador|estad[ií]stic|cuenta|\bods\b|gobernanza|inversi[oó]n|censo|\bley\b|pol[ií]tica|indicator"),
]

INSTITUCIONES_CONOCIDAS = [
    "USAC", "AMSCLAE", "AMSA", "ICC", "INSIVUMEH", "MSPAS", "MARN", "IARNA-URL", "INE",
    "EMPAGUA", "MAGA", "FUNCAGUA", "PANGAEA", "Zenodo", "Figshare", "SEGEPLAN", "SE-CONRED",
    "INFOM", "CEPAL", "JICA", "GIZ", "USGS", "PNUD", "UICN", "AECID", "4ocean", "BID",
    "The Ocean Cleanup", "Banco Mundial", "Banco de Guatemala", "OpenStreetMap", "CONAP",
    "NOAA", "Water Point Data Exchange", "Mendeley Data", "DataverseNO", "CUAHSI",
]

ESTADOS_FALTANTES = {
    "Fragmented / Not Located as Structured Dataset": "No localizado",
    "Proprietary / Unpublished Raw Data": "No publicado",
    "Restricted / Technical Block": "Técnicamente inaccesible",
    "Technical Block / WAF Restriction": "Técnicamente inaccesible",
    "Technical Obstacle / Unreachable Endpoint": "Técnicamente inaccesible",
    "Unpublished / Missing at International Level": "No publicado",
    "Unpublished Online": "No publicado",
    "Detrás de registro/autenticación": "Detrás de registro",
}

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto",
         "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# Títulos legibles para archivos que en el inventario de origen solo tenían nombre de archivo.
TITULOS_MANUALES = {
    "GTW-017": "Informe de calidad de agua para consumo humano 2020 (cuenca del Lago de Atitlán)",
    "GTW-019": "Informe de oscilación del nivel del Lago de Atitlán 2020",
    "GTW-023": "Puntos de contaminación en la cuenca del Lago de Atitlán 2020",
    "GTW-024": "Informe de calidad de ríos tributarios del Lago de Atitlán (archivo rios2016.pdf)",
    "GTW-042": "Microplásticos en el Lago de Amatitlán (DIGI-USAC, 2020)",
    "GTW-049": "Áreas bajo riego de Guatemala, FAO AQUASTAT GMIA (hoja de cálculo)",
    "GTW-050": "Áreas bajo riego de Guatemala, FAO AQUASTAT GMIA (informe)",
    "GTW-031": "NASA POWER: serie meteorológica diaria 2001-2025, Río Las Vacas",
    "GTW-032": "NASA POWER: serie meteorológica diaria 2001-2025, Motagua medio",
    "GTW-033": "NASA POWER: serie meteorológica diaria 2001-2025, desembocadura del Motagua",
    "GTW-051": "Water Quality Portal: estación NALMS en el Lago de Atitlán",
    "GTW-052": "Water Quality Portal: resultados NALMS del Lago de Atitlán 2018-2020",
}

DESTACADOS_EXTRA = {"GT-DAT-0006", "GT-DAT-0038", "GT-DAT-0019", "GT-DAT-0013", "GT-DAT-0021", "GT-DOC-0116"}

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")

# Palabras que llegan con el carácter de reemplazo U+FFFD por una mala decodificación en la fuente.
REPARACIONES = {"Chilasc\ufffd": "Chilascó", "Pet\ufffdn": "Petén"}


def reparar(texto: str) -> str:
    for roto, correcto in REPARACIONES.items():
        texto = texto.replace(roto, correcto)
    return texto


# ---------------------------------------------------------------------------
# Normalización de campos
# ---------------------------------------------------------------------------

def tema(titulo: str, *contexto: str) -> str:
    """Clasifica por el título; usa tipo y parámetros solo si el título no basta."""
    for texto in (titulo, " ".join(t for t in contexto if t)):
        texto = (texto or "").lower()
        for nombre, patron in TEMAS:
            if re.search(patron, texto):
                return nombre
    return "Otros"


def limpiar_institucion(original: str) -> tuple[str, str]:
    """Devuelve (nombre corto para filtros, detalle sin correos personales)."""
    detalle = EMAIL.sub("cuenta particular", (original or "").strip()) or "No indicada"
    if "(ArcGIS Online" in detalle:
        if detalle.upper().startswith("FUNCAGUA"):
            return "FUNCAGUA", detalle
        return "ArcGIS Online (otras cuentas)", detalle
    if re.match(r"^INE\s*/\s*", detalle):
        detalle_productor = re.sub(r"^INE\s*/\s*", "", detalle)
        corto, _ = limpiar_institucion(detalle_productor)
        return corto, f"{detalle_productor} (publicado por el INE)"
    for nombre in INSTITUCIONES_CONOCIDAS:
        if re.match(rf"^{re.escape(nombre)}\b", detalle, flags=re.I):
            return nombre, detalle
    if detalle.startswith("World Bank"):
        return "Banco Mundial", detalle
    corto = re.sub(r"\s*\((vía|via) [^)]*\)$", "", detalle)
    corto = re.sub(r"\s*\([^)]*\)$", "", corto).strip() or detalle
    return corto, detalle


def acceso_simple(texto: str) -> str:
    t = (texto or "").lower()
    if t.startswith("público con registro") or "registration" in t:
        return "Público con registro"
    if t.startswith("público") or t.startswith("public"):
        return "Público"
    if "restring" in t or "solicitud" in t:
        return "Restringido o por solicitud"
    if "no localizado" in t:
        return "No localizado"
    return "No determinado"


def descarga_simple(texto: str) -> str:
    t = (texto or "").lower()
    if t.startswith("descargado") or t.startswith("archivo provisto") or t.startswith("downloaded"):
        return "Archivo descargado"
    if "portal o servicio" in t:
        return "Portal o servicio"
    if "metadatos" in t or t.startswith("verified") or t.startswith("metadata") or t.startswith("documented"):
        return "Solo metadatos"
    return "No descargado"


def titulo_desde_archivo(nombre: str) -> str:
    base = re.sub(r"\.[A-Za-z0-9]{2,5}$", "", nombre or "").replace("_", " ").strip()
    return base[:1].upper() + base[1:]


# ---------------------------------------------------------------------------
# Catálogo
# ---------------------------------------------------------------------------

def sha_por_ruta_claude() -> tuple[dict[str, str], dict[str, int]]:
    sha: dict[str, str] = {}
    for linea in (CLAUDE / "05_manifiesto" / "checksums_sha256.txt").read_text(encoding="utf-8").splitlines():
        partes = linea.strip().split(None, 1)
        if len(partes) == 2:
            sha[partes[1].strip()] = partes[0]
    tamanos: dict[str, int] = {}
    for nombre in ("manifiesto_descargas.csv", "manifiesto_arcgis.csv", "manifiesto_api.csv"):
        for fila in leer_csv(CLAUDE / "05_manifiesto" / nombre):
            if fila.get("ruta_local") and fila.get("bytes"):
                tamanos[fila["ruta_local"]] = int(float(fila["bytes"]))
    return sha, tamanos


def rutas_locales(texto: str) -> list[str]:
    return [p.strip() for p in re.split(r"[;|\n]", texto or "") if p.strip()]


def construir_catalogo() -> dict[str, Any]:
    sha_ruta, _ = sha_por_ruta_claude()
    inventario = leer_csv(CLAUDE / "01_inventario" / "inventario_maestro.csv")
    publicaciones_src = leer_csv(CLAUDE / "01_inventario" / "publicaciones.csv")
    motagua_por_id = {fila["Resource ID"]: fila.get("Motagua / Las Vacas") == "Sí" for fila in inventario}

    registros: dict[str, dict[str, Any]] = {}
    por_sha: dict[str, str] = {}
    por_url: dict[str, str] = {}

    for fila in inventario:
        if fila["Dataset or publication"] == "Publicación":
            continue
        rid = fila["Resource ID"]
        corto, detalle = limpiar_institucion(fila["Organisation"])
        shas = sorted({sha_ruta[r] for r in rutas_locales(fila["Local files"]) if r in sha_ruta})
        a_min, a_max = anios(fila["Years covered"])
        registro = {
            "id": rid,
            "tipo": TIPOS.get(fila["Dataset or publication"], fila["Dataset or publication"]),
            "titulo": reparar(fila["Resource title"].strip()),
            "institucion": corto,
            "institucion_detalle": detalle,
            "categoria": fila["Source category"],
            "tema": tema(fila["Resource title"], fila["Resource type"], fila["Parameters"]),
            "anios": fila["Years covered"],
            "anio_min": a_min,
            "anio_max": a_max,
            "cobertura": fila["Geographic coverage"],
            "parametros": fila["Parameters"],
            "formato": fila["File format"].strip("; ").strip(),
            "registros": fila["Number of records (verified)"],
            "licencia": fila["Licence"].strip(),
            "acceso": acceso_simple(fila["Access status"]),
            "acceso_detalle": fila["Access status"],
            "descarga": descarga_simple(fila["Download status"]),
            "archivos": int(fila["Files retrieved"] or 0),
            "sha256": shas,
            "url_fuente": fila["Original URL"] if fila["Original URL"].startswith("http") else "",
            "url_descarga": fila["Download URL"] if fila["Download URL"].startswith("http") else "",
            "verificacion": fila["Verification status"],
            "http": fila["URL check (HTTP)"],
            "motagua_las_vacas": fila["Motagua / Las Vacas"] == "Sí",
            "prioridad": int(fila["Priority (1-5)"] or 3),
            "notas": EMAIL.sub("cuenta particular", fila["Notes"]),
            "destacado": rid in DESTACADOS_EXTRA,
            "ids_alias": [],
            "fecha_acceso": fila["Access date"],
        }
        registros[rid] = registro
        for valor in shas:
            por_sha.setdefault(valor, rid)
        for url in (registro["url_descarga"], registro["url_fuente"]):
            clave = normalizar_url(url)
            if clave:
                por_url.setdefault(clave, rid)

    publicaciones: dict[str, dict[str, Any]] = {}
    pub_por_url: dict[str, str] = {}
    for fila in publicaciones_src:
        pid = fila["Resource ID"]
        publicaciones[pid] = {
            "id": pid,
            "titulo": reparar(fila["Title"].strip()),
            "autores": fila["Authors"],
            "anio": fila["Year of publication"],
            "url": fila["DOI or permanent URL"],
            "fuente": fila["Institution or journal"],
            "tipo": fila["Publication type"],
            "lugar": fila["Study location"],
            "anios_muestreo": fila["Years when samples were collected"],
            "parametros": fila["Water parameters investigated"],
            "resultados_numericos": fila["Numerical results available"],
            "datos_crudos": fila["Raw data / supplementary files"],
            "acceso": fila["Access"],
            "motagua_las_vacas": motagua_por_id.get(pid, False)
            or bool(re.search(r"motagua|las vacas", f"{fila['Title']} {fila['Study location']}", re.I)),
            "ids_alias": [],
        }
        clave = normalizar_url(fila["DOI or permanent URL"])
        if clave:
            pub_por_url.setdefault(clave, pid)

    equivalencias = {fila["id_origen"]: fila["id_canonico"] for fila in leer_csv(PIPELINE / "equivalencias.csv")}
    alias: dict[str, str] = {}
    nuevos = 0

    def registrar_alias(origen: str, destino: str) -> None:
        alias[origen] = destino
        objetivo = registros.get(destino) or publicaciones.get(destino)
        if objetivo is not None and origen not in objetivo["ids_alias"] and origen != destino:
            objetivo["ids_alias"].append(origen)

    # Archivos normalizados del MVP 0.1 (75 archivos con SHA-256).
    catalogo_codex = leer_json(CODEX / "data" / "catalog.json")
    for item in catalogo_codex:
        cid = item["id"]
        destino = equivalencias.get(cid) or por_sha.get(item["sha256"]) or por_url.get(normalizar_url(item["downloadUrl"]))
        if destino:
            registrar_alias(cid, destino)
            objetivo = registros[destino]
            if item["sha256"] not in objetivo["sha256"]:
                objetivo["sha256"].append(item["sha256"])
            objetivo["destacado"] = objetivo["destacado"] or bool(item.get("selectedMvp"))
            continue
        corto, detalle = limpiar_institucion(item["institution"])
        a_min, a_max = anios(item["period"])
        formato = item["format"]
        registros[cid] = {
            "id": cid,
            "tipo": "Documento" if formato == "PDF" else "Conjunto de datos",
            "titulo": TITULOS_MANUALES.get(cid, titulo_desde_archivo(item["title"])),
            "institucion": corto,
            "institucion_detalle": detalle,
            "categoria": "Gobierno GT" if corto in {"AMSCLAE", "AMSA", "INSIVUMEH", "MSPAS", "INE"} else ("Universidad" if corto == "USAC" else "Internacional"),
            "tema": tema(item["title"], item["topic"], item["summary"]),
            "anios": item["period"],
            "anio_min": a_min,
            "anio_max": a_max,
            "cobertura": item["territory"],
            "parametros": " | ".join(item.get("parameters") or []),
            "formato": formato,
            "registros": item["records"],
            "licencia": item["license"],
            "acceso": "Público",
            "acceso_detalle": "Público",
            "descarga": "Archivo descargado",
            "archivos": 1,
            "sha256": [item["sha256"]],
            "url_fuente": item["sourceUrl"],
            "url_descarga": item["downloadUrl"],
            "verificacion": "Verificado: archivo descargado (SHA-256 en manifiesto)",
            "http": "",
            "motagua_las_vacas": bool(re.search(r"motagua|las vacas", f"{item['title']} {item['territory']}", re.I)),
            "prioridad": 2 if item.get("selectedMvp") else 3,
            "notas": "",
            "destacado": bool(item.get("selectedMvp")),
            "ids_alias": [],
            "fecha_acceso": "2026-10-21",
        }
        por_sha.setdefault(item["sha256"], cid)
        nuevos += 1

    # Inventario maestro de 30 conjuntos con foco Motagua / Las Vacas.
    for fila in leer_csv(ANTIGRAVITY / "inventories" / "master_data_inventory.csv"):
        aid = fila["Resource ID"]
        urls = [normalizar_url(fila["Download URL"]), normalizar_url(fila["Original URL"])]
        destino = equivalencias.get(aid) or next(
            (por_url.get(u) or pub_por_url.get(u) for u in urls if u and (por_url.get(u) or pub_por_url.get(u))), None
        )
        if destino:
            registrar_alias(aid, destino)
            continue
        corto, detalle = limpiar_institucion(fila["Organisation"])
        a_min, a_max = anios(fila["Years covered"])
        clase = fila["Dataset or publication"].lower()
        registros[aid] = {
            "id": aid,
            "tipo": "Conjunto de datos" if ("dataset" in clase or "geospatial" in clase) else "Documento",
            "titulo": fila["Resource title"].strip(),
            "institucion": corto,
            "institucion_detalle": detalle,
            "categoria": "Gobierno GT" if corto in {"INSIVUMEH", "SEGEPLAN / INSIVUMEH"} else ("ONG/privado" if "FUNCAGUA" in corto or "Ocean" in corto else "Internacional"),
            "tema": tema(fila["Resource title"], fila["Resource type"], fila["Parameters"]),
            "anios": fila["Years covered"],
            "anio_min": a_min,
            "anio_max": a_max,
            "cobertura": fila["Geographic coverage"],
            "parametros": fila["Parameters"],
            "formato": fila["File format"],
            "registros": fila["Number of records, if verified"],
            "licencia": fila["Licence"],
            "acceso": acceso_simple(fila["Access status"]),
            "acceso_detalle": fila["Access status"],
            "descarga": descarga_simple(fila["Download status"]),
            "archivos": 1 if descarga_simple(fila["Download status"]) == "Archivo descargado" else 0,
            "sha256": [],
            "url_fuente": fila["Original URL"] if fila["Original URL"].startswith("http") else "",
            "url_descarga": fila["Download URL"] if fila["Download URL"].startswith("http") else "",
            "verificacion": fila["Verification status"],
            "http": "",
            "motagua_las_vacas": bool(re.search(r"motagua|las vacas", f"{fila['Resource title']} {fila['Geographic coverage']} {fila['Notes']}", re.I)),
            "prioridad": 3,
            "notas": fila["Notes"],
            "destacado": False,
            "ids_alias": [],
            "fecha_acceso": "2026-10-21",
        }
        nuevos += 1

    return {
        "fuentes": registros,
        "publicaciones": publicaciones,
        "alias": alias,
        "por_sha": por_sha,
        "nuevos": nuevos,
    }


def resolver(alias: dict[str, str], identificador: str) -> str:
    return alias.get(identificador, identificador)


def construir_faltantes() -> list[dict[str, Any]]:
    filas: list[dict[str, Any]] = []
    for fila in leer_csv(CLAUDE / "01_inventario" / "registro_datos_faltantes.csv"):
        filas.append({
            "institucion": fila["Organisation"],
            "evidencia": fila["Evidence of monitoring/data collection"],
            "dato_esperado": fila["Expected data type"],
            "url_evidencia": fila["Website / evidence URL"],
            "que_se_intento": fila["What was attempted"],
            "motivo": fila["Reason access failed"],
            "estado": ESTADOS_FALTANTES.get(fila["Status category"], fila["Status category"]),
            "solicitud_factible": fila["Formal request feasible"],
            "siguiente_paso": fila["Recommended next action"],
        })
    vistos = {clave_texto(f["institucion"]) for f in filas}
    for fila in leer_csv(ANTIGRAVITY / "inventories" / "missing_data_register.csv"):
        if clave_texto(fila["Organisation"]) in vistos:
            continue
        filas.append({
            "institucion": fila["Organisation"],
            "evidencia": fila["Evidence of monitoring"],
            "dato_esperado": fila["Expected type of data"],
            "url_evidencia": fila["Website or evidence URL"],
            "que_se_intento": fila["What was attempted to access"],
            "motivo": fila["Specific reason access failed"],
            "estado": ESTADOS_FALTANTES.get(fila["Status"], fila["Status"]),
            "solicitud_factible": fila["Formal request feasible?"],
            "siguiente_paso": fila["Recommended next action"],
        })
    for indice, fila in enumerate(filas, start=1):
        fila["id"] = f"FALT-{indice:03d}"
        fila["institucion_corta"] = limpiar_institucion(fila["institucion"].split(" - ")[0])[0]
    return filas


# ---------------------------------------------------------------------------
# Parámetros y mediciones
# ---------------------------------------------------------------------------

PARAMETROS = [
    # código, nombre, unidad, grupo, patrón sobre el nombre original
    ("PH", "pH", "unidades de pH", "Fisicoquímico", r"^ph\b|^ph in situ"),
    ("TEMP_AGUA", "Temperatura del agua", "°C", "Fisicoquímico", r"^temp(eratura)?(_c)?$|temperatura( \(°c\)| muestra| del agua|$)|^temp_c$"),
    ("TEMP_AIRE", "Temperatura ambiente", "°C", "Contexto", r"temperatura ambiente"),
    ("HR", "Humedad relativa", "%", "Contexto", r"humedad relativa"),
    ("COND", "Conductividad eléctrica", "µS/cm", "Fisicoquímico", r"conductividad"),
    ("STD", "Sólidos totales disueltos", "mg/L", "Fisicoquímico", r"s[oó]lidos totales disueltos|\btds\b"),
    ("SST", "Sólidos suspendidos", "mg/L", "Fisicoquímico", r"s[oó]lidos suspendidos"),
    ("SAL", "Salinidad", "PSU", "Fisicoquímico", r"salinidad"),
    ("RES", "Resistividad", "kΩ·cm", "Fisicoquímico", r"resistividad"),
    ("OD_SAT", "Saturación de oxígeno", "%", "Oxígeno y materia orgánica", r"saturaci[oó]n de ox|o2%"),
    ("OD", "Oxígeno disuelto", "mg/L", "Oxígeno y materia orgánica", r"ox[ií]geno disuelto|^od(_mg_l)?$"),
    ("DBO5", "Demanda bioquímica de oxígeno (DBO₅)", "mg/L", "Oxígeno y materia orgánica", r"\bdbo|bioqu[ií]mica"),
    ("DQO", "Demanda química de oxígeno (DQO)", "mg/L", "Oxígeno y materia orgánica", r"\bdqo|qu[ií]mica de ox"),
    ("TURB", "Turbiedad", "NTU", "Fisicoquímico", r"turbi"),
    ("COLOR", "Color real", "U Pt-Co", "Fisicoquímico", r"^color"),
    ("CL", "Cloruros (Cl⁻)", "mg/L", "Iones mayores", r"cloruro"),
    ("DUREZA", "Dureza total (como CaCO₃)", "mg/L", "Iones mayores", r"dureza"),
    ("F", "Fluoruros (F⁻)", "mg/L", "Iones mayores", r"fluoruro"),
    ("SO4", "Sulfatos (SO₄²⁻)", "mg/L", "Iones mayores", r"sulfato"),
    ("ALC", "Alcalinidad total (como CaCO₃)", "mg/L", "Iones mayores", r"alcalinidad"),
    ("CO3", "Carbonatos (CO₃²⁻)", "mg/L", "Iones mayores", r"^carbonato"),
    ("HCO3", "Bicarbonatos (HCO₃⁻)", "mg/L", "Iones mayores", r"bicarbonato"),
    ("SIO2", "Silicatos (SiO₂)", "mg/L", "Iones mayores", r"silicato"),
    ("N_NO3", "Nitrógeno de nitratos (N-NO₃⁻)", "mg/L", "Nutrientes", r"^n-no3"),
    ("NO3", "Nitratos (NO₃⁻)", "mg/L", "Nutrientes", r"^nitratos"),
    ("N_NO2", "Nitrógeno de nitritos (N-NO₂⁻)", "mg/L", "Nutrientes", r"^n-no2"),
    ("NO2", "Nitritos (NO₂⁻)", "mg/L", "Nutrientes", r"^nitritos"),
    ("N_NH4", "Nitrógeno amoniacal (N-NH₄⁺)", "mg/L", "Nutrientes", r"nitr[oó]geno de amonio"),
    ("NH4", "Amonio (NH₄⁺)", "mg/L", "Nutrientes", r"^amonio"),
    ("P_PO4", "Fósforo de fosfatos (P-PO₄³⁻)", "mg/L", "Nutrientes", r"f[oó]sforo de fosfato"),
    ("PO4", "Fosfatos (PO₄³⁻)", "mg/L", "Nutrientes", r"^fosfato"),
    ("CN", "Cianuro libre (CN⁻)", "mg/L", "Tóxicos", r"cianuro"),
    ("SAAM", "Tensoactivos (SAAM)", "mg/L", "Tóxicos", r"tensoactivo"),
    ("SULFADIAZINA", "Sulfadiazina", "ng/L", "Contaminantes emergentes", r"sulfadiazina"),
    ("SULFAMETOXAZOL", "Sulfametoxazol", "ng/L", "Contaminantes emergentes", r"sulfametoxazol"),
    ("CAFEINA", "Cafeína", "ng/L", "Contaminantes emergentes", r"caf+[eé]?[ií]na"),
    ("Q_MENSUAL", "Caudal medio mensual", "m³/s", "Hidrología", r"caudal medio mensual"),
    ("SECCHI", "Profundidad del disco de Secchi", "m", "Limnología", r"secchi"),
    ("PROF_FONDO", "Profundidad al fondo", "m", "Limnología", r"depth, bottom"),
    ("PRECIP_ANUAL", "Precipitación anual (modelada)", "mm/año", "Clima", r"precipitaci[oó]n anual"),
]


def codificar_parametro(nombre_original: str) -> tuple[str, str, str]:
    base = re.sub(r"\s*\([^)]*\)\s*$", "", nombre_original.strip()).strip()
    texto = base.lower()
    for codigo, nombre, unidad, _grupo, patron in PARAMETROS:
        if re.search(patron, texto):
            return codigo, nombre, unidad
    return "OTRO", base, ""


def unidad_declarada(nombre_original: str, unidad: str) -> str:
    """La unidad viene en el nombre ('pH (unidad)') o en el campo de unidad."""
    if unidad and not unidad.lower().startswith("unidad incluida"):
        return unidad
    coincidencia = re.search(r"\(([^)]*)\)\s*$", nombre_original)
    return coincidencia.group(1) if coincidencia else ""


def normalizar_unidad(unidad: str, codigo: str) -> str:
    u = (unidad or "").strip()
    if codigo == "PH" and u.lower() in {"unidad", "unidades", "u", ""}:
        return "unidades de pH"
    return {"µs/cm": "µS/cm", "us/cm": "µS/cm", "μs/cm": "µS/cm", "mg/l": "mg/L", "o2%": "%"}.get(u.lower(), u)


def saturacion_oxigeno(temperatura_c: float) -> float:
    """Concentración de saturación de O₂ en agua dulce a 1 atm (Benson y Krause, APHA 4500-O)."""
    t = temperatura_c + 273.15
    ln_cs = (-139.34411 + 1.575701e5 / t - 6.642308e7 / t**2 + 1.243800e10 / t**3 - 8.621949e11 / t**4)
    return math.exp(ln_cs)


# ---------------------------------------------------------------------------
# Geometría
# ---------------------------------------------------------------------------

def punto_en_anillo(lon: float, lat: float, anillo: list[list[float]]) -> bool:
    dentro = False
    j = len(anillo) - 1
    for i in range(len(anillo)):
        xi, yi = anillo[i][0], anillo[i][1]
        xj, yj = anillo[j][0], anillo[j][1]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-12) + xi:
            dentro = not dentro
        j = i
    return dentro


def punto_en_poligono(lon: float, lat: float, geometria: dict[str, Any]) -> bool:
    poligonos = [geometria["coordinates"]] if geometria["type"] == "Polygon" else geometria["coordinates"]
    return any(poligono and punto_en_anillo(lon, lat, poligono[0]) for poligono in poligonos)


def redondear_geometria(geometria: dict[str, Any], decimales: int = 4) -> dict[str, Any]:
    def r(valor: Any) -> Any:
        if isinstance(valor, (int, float)):
            return round(valor, decimales)
        return [r(v) for v in valor]
    return {"type": geometria["type"], "coordinates": r(geometria["coordinates"])}


def municipios_compatibles(a: str, b: str) -> bool:
    la, lb = clave_laxa(a), clave_laxa(b)
    if not la or not lb:
        return False
    return la == lb or la in lb or lb in la or SequenceMatcher(None, la, lb).ratio() >= 0.8


def buscar_homonimo(nombre: str, municipio: str, candidatos: list[tuple[str, str, Any]], reservados: set[str] = frozenset()) -> Any | None:
    """Devuelve el único candidato con el mismo nombre (exacto, laxo o casi igual) y municipio compatible.

    Si hay más de un candidato en la misma etapa, el emparejamiento se considera ambiguo y no se usa.
    `reservados` son los nombres (clave laxa) de la propia fuente: un nombre casi igual que coincide
    exactamente con otra estación de la fuente no se toma como homónimo (p. ej. Matacuy y Matucuy).
    """
    propio = clave_laxa(nombre)
    pruebas = (
        lambda c: clave_texto(c) == clave_texto(nombre),
        lambda c: clave_laxa(c) == propio,
        lambda c: clave_laxa(c) not in (reservados - {propio}) and SequenceMatcher(None, clave_laxa(c), propio).ratio() >= 0.85,
    )
    for prueba in pruebas:
        hallados = {id(obj): obj for (cn, cm, obj) in candidatos if prueba(cn) and municipios_compatibles(cm, municipio)}
        if len(hallados) == 1:
            return next(iter(hallados.values()))
        if len(hallados) > 1:
            return None
    return None


def simplificar_anillo(puntos: list[list[float]], tolerancia: float) -> list[list[float]]:
    """Douglas-Peucker iterativo; conserva el primer y último vértice del anillo."""
    if len(puntos) < 5:
        return puntos
    conservar = [False] * len(puntos)
    conservar[0] = conservar[-1] = True
    pila = [(0, len(puntos) - 1)]
    while pila:
        inicio, fin = pila.pop()
        ax, ay = puntos[inicio][0], puntos[inicio][1]
        bx, by = puntos[fin][0], puntos[fin][1]
        dx, dy = bx - ax, by - ay
        largo = math.hypot(dx, dy)
        maximo, indice = 0.0, -1
        for i in range(inicio + 1, fin):
            px, py = puntos[i][0], puntos[i][1]
            # En un anillo cerrado el primer y último vértice coinciden: se usa la distancia al vértice.
            distancia = abs(dy * px - dx * py + bx * ay - by * ax) / largo if largo > 1e-12 else math.hypot(px - ax, py - ay)
            if distancia > maximo:
                maximo, indice = distancia, i
        if maximo > tolerancia and indice > 0:
            conservar[indice] = True
            pila.extend(((inicio, indice), (indice, fin)))
    resultado = [punto for punto, mantener in zip(puntos, conservar) if mantener]
    return resultado if len(resultado) >= 4 else puntos


def simplificar_geometria(geometria: dict[str, Any], tolerancia: float) -> dict[str, Any]:
    if geometria["type"] == "Polygon":
        return {"type": "Polygon", "coordinates": [simplificar_anillo(a, tolerancia) for a in geometria["coordinates"]]}
    if geometria["type"] == "MultiPolygon":
        return {"type": "MultiPolygon", "coordinates": [[simplificar_anillo(a, tolerancia) for a in poligono] for poligono in geometria["coordinates"]]}
    return geometria


def distancia_km(a: list[float], b: list[float]) -> float:
    lat = math.radians((a[1] + b[1]) / 2)
    return math.hypot((a[0] - b[0]) * 111.32 * math.cos(lat), (a[1] - b[1]) * 110.57)


# ---------------------------------------------------------------------------
# Capas
# ---------------------------------------------------------------------------

PRECISION = {
    "publicada": "Coordenada publicada por la fuente",
    "homonimo": "Coordenada del punto INSIVUMEH con el mismo nombre y municipio",
    "transcrita": "Coordenada transcrita de un documento (verificar contra el original)",
    "modelada": "Ubicación de un modelo o celda de cálculo, no de una estación en terreno",
}


class Constructor:
    def __init__(self, catalogo: dict[str, Any]):
        self.catalogo = catalogo
        self.alias = catalogo["alias"]
        self.capas: dict[str, dict[str, Any]] = {}
        self.mediciones: list[dict[str, Any]] = []
        self.excluidos: list[dict[str, str]] = []
        self.bundle = leer_json(ANTIGRAVITY / "data" / "processed" / "dashboard_national_data_bundle.json")
        codex = leer_json(CODEX / "data" / "water_features.geojson")["features"]
        self.codex = codex
        self.archivo_codex = {item["fileName"]: item["id"] for item in leer_json(CODEX / "data" / "catalog.json")}

    # -- utilidades -------------------------------------------------------
    def fuente(self, *ids: str) -> list[str]:
        resultado: list[str] = []
        for identificador in ids:
            canonico = resolver(self.alias, identificador)
            if canonico not in resultado:
                resultado.append(canonico)
        return resultado

    def fuente_archivo(self, nombre: str) -> str:
        return resolver(self.alias, self.archivo_codex[nombre])

    def agregar_capa(self, capa_id: str, meta: dict[str, Any], features: list[dict[str, Any]]) -> None:
        self.capas[capa_id] = {"meta": {"id": capa_id, **meta}, "features": features}

    def medir(self, sitio: dict[str, Any], nombre_original: str, valor: Any, unidad: str, fecha: str,
              fuente_id: str, tipo_dato: str = "Medido", unidad_verificada: bool = True, nota: str = "") -> dict[str, Any] | None:
        numero_valor = numero(valor)
        if numero_valor is None:
            return None
        codigo, nombre, unidad_estandar = codificar_parametro(nombre_original)
        unidad = normalizar_unidad(unidad, codigo)
        medicion = {
            "sitio_id": sitio["id"],
            "sitio": sitio["nombre"],
            "capa": sitio["capa"],
            "codigo": codigo,
            "parametro": nombre if codigo != "OTRO" else nombre_original,
            "parametro_original": nombre_original,
            "valor": round(numero_valor, 4),
            "unidad": unidad or unidad_estandar,
            "unidad_verificada": unidad_verificada,
            "fecha": fecha,
            "tipo_dato": tipo_dato,
            "fuente_id": fuente_id,
            "control": "",
            "nota": nota,
        }
        self.mediciones.append(medicion)
        sitio.setdefault("_mediciones", []).append(medicion)
        return medicion

    @staticmethod
    def feature(sitio: dict[str, Any], lon: float, lat: float) -> dict[str, Any]:
        propiedades = {k: v for k, v in sitio.items() if not k.startswith("_")}
        mediciones = [
            {k: m[k] for k in ("codigo", "parametro", "valor", "unidad", "fecha", "fuente_id", "control", "unidad_verificada")}
            for m in sitio.get("_mediciones", [])
        ]
        if mediciones:
            propiedades["mediciones"] = mediciones
        return {
            "type": "Feature",
            "id": sitio["id"],
            "geometry": {"type": "Point", "coordinates": [round(lon, 5), round(lat, 5)]},
            "properties": propiedades,
        }

    @staticmethod
    def sitio_base(capa: str, sid: str, nombre: str, **campos: Any) -> dict[str, Any]:
        base = {
            "id": sid,
            "capa": capa,
            "nombre": nombre,
            "tipo": "",
            "institucion": "",
            "cuerpo_agua": "",
            "cuenca": "",
            "departamento": "",
            "municipio": "",
            "fecha": "",
            "tipo_dato": "Medido",
            "precision": "publicada",
            "fuente_ids": [],
            "advertencia": "",
            "atributos": {},
        }
        base.update(campos)
        return base

    # -- red INSIVUMEH ----------------------------------------------------
    def monitoreo_insivumeh(self) -> None:
        sitios: list[dict[str, Any]] = []
        indice: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        fuente_2023 = self.fuente("GTW-003")[0]
        fuente_2024 = self.fuente("GTW-068")[0]
        fuente_2022 = self.fuente_archivo("7._Calidad_Agua_INSIVUMEH_2022.csv")

        # 2024 primero para que su nombre y coordenada sean las de referencia.
        origen = sorted(
            (f for f in self.codex if f["id"].startswith("insivumeh-")),
            key=lambda f: (0 if "2024" in f["id"] else 1, f["id"]),
        )
        for f in origen:
            p = f["properties"]
            anio = "2024" if "2024" in f["id"] else "2023"
            clave = (clave_texto(p["name"]), clave_laxa(p["municipality"]))
            coords = f["geometry"]["coordinates"]
            sitio = next((s for s in indice[clave] if distancia_km(s["_coords"], coords) < 1.0), None)
            if sitio is None:
                sitio = self.sitio_base(
                    "monitoreo_insivumeh", f"INS-{len(sitios) + 1:03d}", p["name"].strip(),
                    tipo="Punto de monitoreo de calidad del agua",
                    institucion="INSIVUMEH (publicado por el INE)",
                    cuenca=p["basin"], departamento=p["department"], municipio=p["municipality"],
                    fuente_ids=[], advertencia="Campañas puntuales por año; no es una serie continua ni una evaluación del cuerpo de agua.",
                    _coords=coords, _anios=set(),
                )
                sitios.append(sitio)
                indice[clave].append(sitio)
            sitio["_anios"].add(anio)
            fuente_id = fuente_2024 if anio == "2024" else fuente_2023
            if fuente_id not in sitio["fuente_ids"]:
                sitio["fuente_ids"].append(fuente_id)
            for ev in p["evidence"]:
                self.medir(sitio, ev["parameter"], ev["value"], unidad_declarada(ev["parameter"], ev["unit"]), ev["date"], fuente_id)

        # 2022: base INE con ~30 parámetros por punto, unida por nombre y municipio.
        candidatos = [(s["nombre"], s["municipio"], s) for s in sitios]
        reservados = {clave_laxa(f["properties"]["name"]) for f in self.bundle["insivumeh_quality_stations"]["features"]}
        for f in self.bundle["insivumeh_quality_stations"]["features"]:
            p = f["properties"]
            sitio = buscar_homonimo(p["name"], p["municipality"], candidatos, reservados)
            if sitio is None:
                self.excluidos.append({"capa": "monitoreo_insivumeh", "nombre": p["name"], "motivo": "Punto 2022 sin coordenada publicada equivalente (o con más de un candidato)"})
                continue
            sitio["_anios"].add("2022")
            sitio["cuerpo_agua"] = sitio["cuerpo_agua"] or p.get("water_body", "")
            if fuente_2022 not in sitio["fuente_ids"]:
                sitio["fuente_ids"].insert(0, fuente_2022)
            for parametro, valor in p["all_params"].items():
                self.medir(
                    sitio, parametro, valor, "", "2022", fuente_2022, unidad_verificada=False,
                    nota="Último registro del archivo INE 2022 para la variable; la fecha exacta de muestreo no se conservó.",
                )

        features = []
        for s in sitios:
            anios_sitio = sorted(s.pop("_anios"))
            s["fecha"] = f"{anios_sitio[0]}–{anios_sitio[-1]}" if len(anios_sitio) > 1 else anios_sitio[0]
            s["atributos"] = {"Años con datos": ", ".join(anios_sitio)}
            lon, lat = s.pop("_coords")
            features.append(self.feature(s, lon, lat))
        self.sitios_insivumeh = sitios
        self.agregar_capa("monitoreo_insivumeh", {
            "titulo": "Calidad del agua · INSIVUMEH",
            "descripcion": "Puntos de la red nacional de monitoreo del INSIVUMEH con coordenadas publicadas en las bases del INE 2023 y 2024; incluye los valores 2022 del mismo punto.",
            "grupo": "Monitoreo del agua", "geometria": "punto", "tipo_dato": "Medido", "precision": "publicada",
            "fuente_ids": [fuente_2022, fuente_2023, fuente_2024], "visible": True,
        }, features)

    def caudales_insivumeh(self) -> None:
        fuente = self.fuente_archivo("6._Caudales_INSIVUMEH_2022.csv")
        candidatos = [(f["properties"]["nombre"], f["properties"]["municipio"], f) for f in self.capas["monitoreo_insivumeh"]["features"]]
        reservados = {clave_laxa(f["properties"]["name"]) for f in self.bundle["insivumeh_streamflow_stations"]["features"]}
        features = []
        for f in self.bundle["insivumeh_streamflow_stations"]["features"]:
            p = f["properties"]
            referencia = buscar_homonimo(p["name"], p["municipality"], candidatos, reservados)
            if referencia is None:
                self.excluidos.append({"capa": "caudales_insivumeh", "nombre": p["name"], "motivo": "Estación sin punto INSIVUMEH homónimo con coordenada publicada"})
                continue
            lon, lat = referencia["geometry"]["coordinates"]
            sitio = self.sitio_base(
                "caudales_insivumeh", f"CAU-{len(features) + 1:03d}", referencia["properties"]["nombre"],
                tipo="Estación hidrométrica", institucion="INSIVUMEH (publicado por el INE)",
                cuerpo_agua=f"Río {p['water_body']}" if p.get("water_body") else "", cuenca=p.get("basin", ""),
                departamento=p.get("department", ""), municipio=p.get("municipality", ""), fecha="2022",
                precision="homonimo", fuente_ids=[fuente],
                advertencia="Caudal medio mensual 2022 publicado por el INE. La ubicación se toma del punto de monitoreo INSIVUMEH con el mismo nombre y municipio.",
            )
            serie = []
            for mes in MESES:
                valor = numero(p["monthly_flows"].get(mes))
                if valor is None:
                    continue
                serie.append({"etiqueta": mes[:3], "valor": valor})
                self.medir(sitio, "Caudal medio mensual", valor, "m³/s", f"{mes} 2022", fuente)
            if serie:
                valores = [punto["valor"] for punto in serie]
                sitio["serie"] = {"titulo": "Caudal medio mensual 2022", "unidad": "m³/s", "puntos": serie}
                sitio["atributos"] = {
                    "Caudal medio (meses con dato)": f"{sum(valores) / len(valores):.2f} m³/s",
                    "Máximo mensual": f"{max(valores):.2f} m³/s",
                    "Mínimo mensual": f"{min(valores):.2f} m³/s",
                    "Vertiente": p.get("vertiente", ""),
                    "Punto de referencia": referencia["properties"]["nombre"],
                }
            features.append(self.feature(sitio, lon, lat))
        self.agregar_capa("caudales_insivumeh", {
            "titulo": "Caudales · INSIVUMEH 2022",
            "descripcion": "Estaciones hidrométricas con caudal medio mensual 2022 (portal de datos del INE).",
            "grupo": "Monitoreo del agua", "geometria": "punto", "tipo_dato": "Medido", "precision": "homonimo",
            "fuente_ids": [fuente], "visible": True,
        }, features)

    # -- Las Vacas ---------------------------------------------------------
    def usac_las_vacas(self) -> None:
        fuente = self.fuente("GT-H2O-007")[0]
        filas = leer_csv(ANTIGRAVITY / "data" / "processed" / "USAC_ERIS_Motagua_LasVacas_2025_Monitoring_Data.csv")
        columnas = [
            ("oxigeno_disuelto_mg_l", "Oxígeno disuelto", "mg/L"),
            ("ph", "pH", "unidades de pH"),
            ("temperatura_c", "Temperatura del agua", "°C"),
            ("dbo5_mg_l", "DBO5", "mg/L"),
            ("dqo_mg_l", "DQO", "mg/L"),
            ("sulfadiazina_ng_l", "Sulfadiazina", "ng/L"),
            ("sulfametoxazol_ng_l", "Sulfametoxazol", "ng/L"),
            ("cafeina_ng_l", "Cafeína", "ng/L"),
        ]
        features = []
        for fila in filas:
            lon, lat = numero(fila["longitud"]), numero(fila["latitud"])
            if lon is None or lat is None:
                continue
            sitio = self.sitio_base(
                "usac_las_vacas", f"USAC-{fila['estacion_id']}", fila["descripcion"],
                tipo=fila["tipo_sitio"], institucion="USAC · Escuela Regional de Ingeniería Sanitaria (ERIS)",
                cuerpo_agua=fila["cuerpo_agua"], cuenca=fila["cuenca"], fecha="Tesis 2025", precision="transcrita",
                fuente_ids=[fuente],
                advertencia="Valores y coordenadas transcritos de las tablas de la tesis; incluye alcantarillados y descargas hospitalarias, que no son cuerpos de agua.",
                atributos={"Código de estación": fila["estacion_id"]},
            )
            for columna, nombre, unidad in columnas:
                self.medir(sitio, nombre, fila.get(columna), unidad, "2025 (tesis)", fuente)
            features.append(self.feature(sitio, lon, lat))
        self.agregar_capa("usac_las_vacas", {
            "titulo": "Río Las Vacas y drenajes · USAC 2025",
            "descripcion": "Oxígeno, materia orgánica y fármacos (sulfadiazina, sulfametoxazol, cafeína) en ríos, alcantarillados y descargas hospitalarias de la subcuenca Las Vacas.",
            "grupo": "Monitoreo del agua", "geometria": "punto", "tipo_dato": "Medido", "precision": "transcrita",
            "fuente_ids": [fuente], "visible": True,
        }, features)

    def acidificacion_marn(self) -> None:
        fuente = "GT-DAT-0051"
        features = []
        for f in self.bundle["marn_acidification_stations"]["features"]:
            p = f["properties"]
            lon, lat = p.get("Longitud_X"), p.get("Latitud_Y")
            if lon is None:
                lon, lat = f["geometry"]["coordinates"]
            sitio = self.sitio_base(
                "acidificacion_marn", f"MARN-AC-{p['No_']:02d}", p["Sitio"], tipo="Sitio de monitoreo de acidificación costera",
                institucion="MARN", departamento=p.get("Departamen", ""), fecha="2021–2025", fuente_ids=[fuente],
                advertencia="pH anual publicado en la capa del MARN; el número de días monitoreados varía por año.",
            )
            serie = []
            for anio, clave_n in (("2021", "Monitoreo"), ("2022", "MonitoreoB"), ("2023", "MonitoreoC"), ("2024", "MonitoreoD"), ("2025", "MonitoreoE")):
                valor = numero(p.get(f"pH{anio}"))
                if valor is None:
                    continue
                dias = p.get(clave_n)
                serie.append({"etiqueta": anio, "valor": valor})
                self.medir(sitio, "pH", valor, "unidades de pH", anio, fuente, nota=f"{dias} días monitoreados" if dias else "")
            if serie:
                sitio["serie"] = {"titulo": "pH anual", "unidad": "pH", "puntos": serie}
            features.append(self.feature(sitio, lon, lat))
        self.agregar_capa("acidificacion_marn", {
            "titulo": "Acidificación costera · MARN",
            "descripcion": "Sitios costeros del MARN con pH anual 2021-2025.",
            "grupo": "Monitoreo del agua", "geometria": "punto", "tipo_dato": "Medido", "precision": "publicada",
            "fuente_ids": [fuente], "visible": True,
        }, features)

    def atitlan_wqp(self) -> None:
        features = []
        for f in self.codex:
            if not f["id"].startswith("wqp-"):
                continue
            p = f["properties"]
            fuentes = self.fuente(*p["sourceIds"])
            sitio = self.sitio_base(
                "atitlan_wqp", "WQP-ATITLAN", "Lago de Atitlán (NALMS)", tipo="Punto de observación lacustre",
                institucion="North American Lake Management Society · Water Quality Portal", cuerpo_agua="Lago de Atitlán",
                cuenca="Lago de Atitlán", departamento="Sololá", fecha="2018–2020", fuente_ids=fuentes,
                advertencia="El proveedor marca el método y el datum horizontal como desconocidos; la coordenada se conserva sin reinterpretar.",
            )
            for ev in p["evidence"]:
                self.medir(sitio, ev["parameter"], ev["value"], ev["unit"], ev["date"], resolver(self.alias, ev["sourceId"]))
            lon, lat = f["geometry"]["coordinates"]
            features.append(self.feature(sitio, lon, lat))
        self.agregar_capa("atitlan_wqp", {
            "titulo": "Lago de Atitlán · Water Quality Portal",
            "descripcion": "Profundidad y transparencia (disco de Secchi) 2018-2020 del programa NALMS.",
            "grupo": "Monitoreo del agua", "geometria": "punto", "tipo_dato": "Medido", "precision": "publicada",
            "fuente_ids": self.fuente("GTW-051", "GTW-052"), "visible": True,
        }, features)

    # -- presiones e infraestructura --------------------------------------
    def ptar_hydrowaste(self) -> None:
        fuente = "GT-DAT-0018"
        features = []
        for fila in leer_csv(CLAUDE / "03_datos_procesados" / "hydrowaste" / "hydrowaste_guatemala.csv"):
            lon, lat = numero(fila["LON_WWTP"]), numero(fila["LAT_WWTP"])
            if lon is None or lat is None:
                continue
            sitio = self.sitio_base(
                "ptar_hydrowaste", f"PTAR-{fila['WASTE_ID']}", fila["WWTP_NAME"] or f"Planta de tratamiento {fila['WASTE_ID']}",
                tipo="Planta de tratamiento de aguas residuales", institucion="HydroWASTE v1.0 (McGill / HydroSHEDS)",
                tipo_dato="Compilado y estimado", fuente_ids=[fuente], fecha="Compilado 2021",
                advertencia="Base global compilada. Población servida y caudal descargado son estimaciones del modelo (QUAL_POP, QUAL_WASTE).",
                atributos={
                    "Población servida (estimada)": f"{int(float(fila['POP_SERVED'])):,}".replace(",", " ") if fila["POP_SERVED"] else "",
                    "Agua residual descargada (estimada)": f"{float(fila['WASTE_DIS']):,.0f} m³/día".replace(",", " ") if fila["WASTE_DIS"] else "",
                    "Nivel de tratamiento": {"Primary": "Primario", "Secondary": "Secundario", "Advanced": "Avanzado"}.get(fila["LEVEL"], fila["LEVEL"]),
                    "Estado": {"Not Reported": "No reportado", "Operational": "En operación"}.get(fila["STATUS"], fila["STATUS"]),
                },
            )
            features.append(self.feature(sitio, lon, lat))
        self.agregar_capa("ptar_hydrowaste", {
            "titulo": "Plantas de tratamiento · HydroWASTE",
            "descripcion": "Plantas de tratamiento de aguas residuales registradas en la base global HydroWASTE.",
            "grupo": "Presiones e infraestructura", "geometria": "punto", "tipo_dato": "Compilado y estimado", "precision": "publicada",
            "fuente_ids": [fuente], "visible": False,
        }, features)

    def wpdx(self) -> None:
        fuente = "GT-DAT-0019"
        tecnologias = {
            "Gravity Fed System": "Sistema por gravedad",
            "Rainwater Harvesting": "Captación de lluvia",
            "Hand Pump": "Bomba manual",
            "Motorized Pump": "Bomba motorizada",
            "Protected Spring": "Manantial protegido",
            "Borehole": "Pozo perforado",
        }
        features = []
        for f in self.bundle["wpdx_water_points"]["features"]:
            p = f["properties"]
            lon, lat = f["geometry"]["coordinates"]
            estado = {"Functional": "Funcional", "Non-Functional": "No funcional"}.get(p.get("status"), p.get("status") or "No indicado")
            sitio = self.sitio_base(
                "wpdx", f"WPDX-{p['id']}", f"Punto de agua {p['id']}", tipo="Punto de agua comunitario",
                institucion="Water Point Data Exchange (WPdx)", departamento=p.get("department", ""), municipio=p.get("municipality", ""),
                tipo_dato="Reportado", fuente_ids=[fuente], fecha="2013–2021",
                advertencia="Muestra sistemática de 128 de los 1 908 puntos publicados. El estado es el último reportado por la organización instaladora.",
                atributos={"Tecnología": tecnologias.get(p.get("tech", ""), p.get("tech", "")), "Estado reportado": estado, "Instalador": p.get("installer", "")},
            )
            features.append(self.feature(sitio, lon, lat))
        self.agregar_capa("wpdx", {
            "titulo": "Puntos de agua comunitarios · WPdx",
            "descripcion": "Muestra de puntos de agua rurales con su estado de funcionamiento reportado.",
            "grupo": "Presiones e infraestructura", "geometria": "punto", "tipo_dato": "Reportado", "precision": "publicada",
            "fuente_ids": [fuente], "visible": False,
        }, features)

    def plasticos(self) -> None:
        fuente = "GT-DAT-0036"
        features = []
        for fila in leer_csv(ANTIGRAVITY / "data" / "processed" / "Guatemala_River_Plastic_Outlets_Meijer2021.csv"):
            lon, lat = numero(fila["longitud"]), numero(fila["latitud"])
            emision = numero(fila["emision_plastico_toneladas_anio"])
            if lon is None or lat is None:
                continue
            if not self.en_territorio(lon, lat, 3.0):
                self.excluidos.append({"capa": "plasticos", "nombre": f"Desembocadura {fila['point_id']}", "motivo": "Fuera de Guatemala (costa de Belice, Honduras, El Salvador o México)"})
                continue
            sitio = self.sitio_base(
                "plasticos", f"PLAS-{fila['point_id']}", f"Desembocadura modelada {fila['point_id']}",
                tipo="Desembocadura con emisión de plástico (modelo)", institucion="The Ocean Cleanup · Meijer et al. (2021)",
                tipo_dato="Modelado", precision="modelada", fuente_ids=[fuente], fecha="Año modelo 2015",
                advertencia="Estimación de un modelo global de emisiones de plástico fluvial al océano; no es una medición en el sitio.",
                atributos={"Vertiente": fila["vertiente"], "Emisión estimada": f"{emision:,.1f} t/año".replace(",", " ") if emision is not None else ""},
                emision_t=emision or 0,
            )
            features.append(self.feature(sitio, lon, lat))
        self.agregar_capa("plasticos", {
            "titulo": "Plástico hacia el mar · modelo",
            "descripcion": "Desembocaduras de la costa guatemalteca con emisión de plástico estimada por el modelo de Meijer et al. (2021). Se excluyen las que caen en Belice, Honduras, El Salvador o México.",
            "grupo": "Presiones e infraestructura", "geometria": "punto", "tipo_dato": "Modelado", "precision": "modelada",
            "fuente_ids": [fuente], "visible": False,
        }, features)

    # -- clima --------------------------------------------------------------
    def clima(self) -> None:
        features = []
        for f in self.codex:
            if f["properties"]["institution"] != "NASA POWER":
                continue
            p = f["properties"]
            fuentes = self.fuente(*p["sourceIds"])
            sitio = self.sitio_base(
                "clima_nasa", f"NASA-{f['id'].upper()}", p["name"].replace(" · celda NASA POWER", ""), tipo="Celda de modelo meteorológico",
                institucion="NASA POWER", cuenca=p["basin"], tipo_dato="Modelado", precision="modelada", fuente_ids=fuentes,
                fecha="2001–2025", advertencia="Variables meteorológicas modeladas para una celda; no mide calidad de agua ni caudal.",
                atributos={"Variables": ", ".join(p["parameters"])},
            )
            puntos = [{"etiqueta": punto["label"], "valor": punto["value"]} for punto in p["series"]]
            if puntos:
                sitio["serie"] = {"titulo": "Precipitación anual", "unidad": "mm/año", "puntos": puntos}
            for punto in p["series"]:
                self.medir(sitio, "Precipitación anual", punto["value"], "mm/año", punto["label"], fuentes[0], tipo_dato="Modelado")
            lon, lat = f["geometry"]["coordinates"]
            features.append(self.feature(sitio, lon, lat))
        self.agregar_capa("clima_nasa", {
            "titulo": "Lluvia modelada · NASA POWER",
            "descripcion": "Tres celdas de consulta a lo largo de Las Vacas y el Motagua con precipitación anual 2016-2025.",
            "grupo": "Clima", "geometria": "punto", "tipo_dato": "Modelado", "precision": "modelada",
            "fuente_ids": self.fuente("GTW-031", "GTW-032", "GTW-033"), "visible": False,
        }, features)

        fuente = "GT-DAT-0004"
        estaciones = []
        for fila in leer_csv(CLAUDE / "03_datos_procesados" / "insivumeh" / "mapa_estaciones_met_convencional_estaciones.csv"):
            lon, lat = numero(fila["longitud"]), numero(fila["latitud"])
            if lon is None or lat is None:
                continue
            municipio, _, departamento = fila["municipio_departamento"].partition(",")
            sitio = self.sitio_base(
                "estaciones_meteo", f"MET-{fila['codigo']}", fila["estacion"].title(), tipo="Estación meteorológica convencional",
                institucion="INSIVUMEH", municipio=municipio.strip().title(), departamento=departamento.strip().title(),
                fuente_ids=[fuente], fecha="Red vigente", advertencia="Ubicación de la estación; las series diarias no están publicadas en formato abierto.",
                atributos={"Código": fila["codigo"]},
            )
            estaciones.append(self.feature(sitio, lon, lat))
        self.agregar_capa("estaciones_meteo", {
            "titulo": "Estaciones meteorológicas · INSIVUMEH",
            "descripcion": "Red convencional de estaciones meteorológicas del INSIVUMEH.",
            "grupo": "Clima", "geometria": "punto", "tipo_dato": "Ubicación", "precision": "publicada",
            "fuente_ids": [fuente], "visible": False,
        }, estaciones)

    def gemstat(self) -> None:
        fuente = "GT-DAT-0001"
        resumen = {fila["GEMS Station Number"]: fila for fila in leer_csv(CLAUDE / "03_datos_procesados" / "gemstat" / "gemstat_resumen_estaciones_cuencas_compartidas.csv")}
        tipos = {"River station": "Río", "Lake station": "Lago", "Groundwater station": "Agua subterránea", "Reservoir station": "Embalse"}
        features = []
        for fila in leer_csv(CLAUDE / "03_datos_procesados" / "gemstat" / "gemstat_estaciones_region_guatemala.csv"):
            if fila["GEMS Station Number"] not in resumen:
                continue
            lon, lat = numero(fila["Longitude"]), numero(fila["Latitude"])
            if lon is None or lat is None:
                continue
            datos = resumen[fila["GEMS Station Number"]]
            sitio = self.sitio_base(
                "gemstat_mexico", f"GEMS-{fila['GEMS Station Number']}", fila["Station Identifier"].title(),
                tipo=f"Estación GEMStat · {tipos.get(fila['Water Type'], fila['Water Type'])}", institucion=fila["Responsible Collection Agency"] or "GEMStat",
                cuenca=fila["Main Basin"].title(), fecha=f"{datos['anio_min']}–{datos['anio_max']}", fuente_ids=[fuente],
                advertencia="Estación en México dentro de una cuenca compartida con Guatemala. GEMStat no tiene estaciones en territorio guatemalteco.",
                atributos={"Registros": datos["registros"], "Parámetros": datos["parametros"]},
            )
            features.append(self.feature(sitio, lon, lat))
        self.agregar_capa("gemstat_mexico", {
            "titulo": "Cuencas compartidas en México · GEMStat",
            "descripcion": "Estaciones de calidad del agua de CONAGUA en Suchiate, Coatán, Grijalva-Usumacinta, Hondo y Candelaria.",
            "grupo": "Contexto regional", "geometria": "punto", "tipo_dato": "Medido", "precision": "publicada",
            "fuente_ids": [fuente], "visible": False, "fuera_de_guatemala": True,
        }, features)

    # -- territorio --------------------------------------------------------
    def territorio(self) -> None:
        cuencas = []
        for indice, f in enumerate(self.bundle["guatemala_basins_38"]["features"], start=1):
            p = f["properties"]
            nombre = p["name"].replace("Rió", "Río").replace("Rio ", "Río ")
            cuencas.append({
                "type": "Feature", "id": f"CUENCA-{indice:02d}",
                "geometry": redondear_geometria(simplificar_geometria(f["geometry"], 0.0012)),
                "properties": {
                    "id": f"CUENCA-{indice:02d}", "capa": "cuencas", "nombre": nombre, "codigo": p.get("codigo"),
                    "vertiente": {"Pacifico": "Pacífico", "Caribe": "Caribe", "Golfo Mexico": "Golfo de México"}.get(p.get("vertiente"), p.get("vertiente")),
                    "area_km2": p.get("km2"), "fuente_ids": ["GT-DAT-0040"],
                },
            })
        self.agregar_capa("cuencas", {
            "titulo": "Cuencas hidrográficas (38)",
            "descripcion": "Delimitación oficial de 38 cuencas (MAGA, 2001) publicada por el MARN. Geometría simplificada para la web.",
            "grupo": "Territorio", "geometria": "poligono", "tipo_dato": "Cartografía oficial", "precision": "publicada",
            "fuente_ids": ["GT-DAT-0040"], "visible": True,
        }, cuencas)

        lagos = []
        for indice, f in enumerate(self.bundle["guatemala_major_lakes"]["features"], start=1):
            p = f["properties"]
            if (p.get("ha") or 0) < 10:
                continue
            lagos.append({
                "type": "Feature", "id": f"LAGO-{indice:02d}", "geometry": redondear_geometria(simplificar_geometria(f["geometry"], 0.0004)),
                "properties": {"id": f"LAGO-{indice:02d}", "capa": "lagos", "nombre": p["NOMBRE"], "area_ha": p.get("ha"), "fuente_ids": ["GT-DAT-0043"]},
            })
        self.agregar_capa("lagos", {
            "titulo": "Lagos y lagunas principales",
            "descripcion": "Cuerpos de agua lacustres principales (MAGA, 2001) publicados por el MARN.",
            "grupo": "Territorio", "geometria": "poligono", "tipo_dato": "Cartografía oficial", "precision": "publicada",
            "fuente_ids": ["GT-DAT-0043"], "visible": True,
        }, lagos)

        red = leer_json(ANTIGRAVITY / "data" / "processed" / "Motagua_River_Basin_Network.geojson")
        tramos = []
        for f in red["features"]:
            p = f["properties"]
            tramos.append({
                "type": "Feature", "geometry": redondear_geometria(f["geometry"]),
                "properties": {"orden": p.get("strahler_order") or 1, "caudal_m3s": p.get("dis_av_cms"), "longitud_km": p.get("length_km")},
            })
        self.agregar_capa("rios_motagua", {
            "titulo": "Red fluvial del Motagua · HydroRIVERS",
            "descripcion": "1 626 tramos de río de la cuenca del Motagua; el grosor sigue el orden de Strahler. Caudal medio de largo plazo modelado.",
            "grupo": "Territorio", "geometria": "linea", "tipo_dato": "Modelado", "precision": "modelada",
            "fuente_ids": ["GT-DAT-0033"], "visible": True,
        }, tramos)

    def en_territorio(self, lon: float, lat: float, tolerancia_km: float) -> bool:
        """Dentro de alguna de las 38 cuencas o a menos de `tolerancia_km` de su borde (costa)."""
        cuencas = self.capas["cuencas"]["features"]
        if any(punto_en_poligono(lon, lat, c["geometry"]) for c in cuencas):
            return True
        if not hasattr(self, "_vertices"):
            self._vertices = [
                v for c in cuencas
                for poligono in ([c["geometry"]["coordinates"]] if c["geometry"]["type"] == "Polygon" else c["geometry"]["coordinates"])
                for v in poligono[0]
            ]
        return any(distancia_km([lon, lat], v) <= tolerancia_km for v in self._vertices)

    # -- control de calidad y resumen por cuenca --------------------------
    def controlar_oxigeno(self) -> None:
        por_sitio_fecha: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
        for m in self.mediciones:
            por_sitio_fecha[(m["sitio_id"], m["fecha"])][m["codigo"]] = m
        for (_sitio, _fecha), grupo in por_sitio_fecha.items():
            od, temp = grupo.get("OD"), grupo.get("TEMP_AGUA")
            if not od or not temp or temp["valor"] <= 0 or temp["valor"] > 40:
                continue
            saturacion = saturacion_oxigeno(temp["valor"])
            if od["valor"] > 1.4 * saturacion:
                od["control"] = (
                    f"Revisar: {od['valor']:.2f} mg/L supera 140 % de la saturación teórica "
                    f"({saturacion:.2f} mg/L a {temp['valor']:.1f} °C, Benson y Krause)."
                )
            # Coincidencias exactas solo son sospechosas con valores de tres o más decimales.
            con_decimales = abs(od["valor"] * 100 - round(od["valor"] * 100)) > 1e-6
            otros = [v for c, v in grupo.items() if c != "OD" and con_decimales and abs(v["valor"] - od["valor"]) < 1e-9]
            if otros:
                od["control"] = (od["control"] + " " if od["control"] else "") + f"Valor idéntico a {otros[0]['parametro']}: probable error de transcripción."
        # Propaga el control a las fichas.
        for capa in self.capas.values():
            for f in capa["features"]:
                for m in f["properties"].get("mediciones", []):
                    original = next(
                        (x for x in self.mediciones if x["sitio_id"] == f["id"] and x["codigo"] == m["codigo"] and x["fecha"] == m["fecha"] and x["valor"] == m["valor"]),
                        None,
                    )
                    if original:
                        m["control"] = original["control"]

    def asignar_cuencas(self, fuentes: dict[str, dict[str, Any]], publicaciones: dict[str, dict[str, Any]]) -> None:
        cuencas = self.capas["cuencas"]["features"]
        conteos: dict[str, Counter] = defaultdict(Counter)
        for capa_id, capa in self.capas.items():
            if capa["meta"]["geometria"] != "punto":
                continue
            for f in capa["features"]:
                lon, lat = f["geometry"]["coordinates"]
                for cuenca in cuencas:
                    if punto_en_poligono(lon, lat, cuenca["geometry"]):
                        f["properties"]["cuenca_oficial"] = cuenca["properties"]["nombre"]
                        conteos[cuenca["id"]][capa_id] += 1
                        break
        especiales = {"Ostúa Güija": "Ostúa", "Mopán Belice": "Mopán", "Sis": "Sis-Icán"}
        for cuenca in cuencas:
            nombre = cuenca["properties"]["nombre"]
            nucleo = re.sub(r"^(Río|Lago de|Laguna)\s+", "", nombre).split("-")[0].strip()
            nucleo = especiales.get(nucleo, nucleo)
            # Nombres cortos (Paz, Moho) se buscan como "río X" para evitar falsos positivos.
            patron = re.compile(rf"\br[ií]o {re.escape(nucleo)}\b" if len(nucleo) <= 4 else rf"\b{re.escape(nucleo)}\b", re.I)
            mencionan = [r["id"] for r in fuentes.values() if patron.search(f"{r['titulo']} {r['cobertura']}")]
            mencionan_pub = [r["id"] for r in publicaciones.values() if patron.search(f"{r['titulo']} {r['lugar']}")]
            cuenca["properties"]["puntos_por_capa"] = dict(conteos[cuenca["id"]])
            cuenca["properties"]["fuentes_que_la_mencionan"] = len(mencionan)
            cuenca["properties"]["publicaciones_que_la_mencionan"] = len(mencionan_pub)
            cuenca["properties"]["ejemplos_fuentes"] = mencionan[:8]
            cuenca["properties"]["termino_busqueda"] = nucleo


# ---------------------------------------------------------------------------
# Manifiesto de archivos originales
# ---------------------------------------------------------------------------

def carpeta_paquete(institucion: str) -> str:
    limpio = re.sub(r"[^A-Za-z0-9]+", "_", institucion.split("(")[0].strip()).strip("_")
    return limpio[:40] or "Otras_fuentes"


def construir_manifiesto(catalogo: dict[str, Any]) -> list[dict[str, Any]]:
    fuentes = catalogo["fuentes"]
    sha_ruta, tamanos = sha_por_ruta_claude()
    ids_por_ruta: dict[str, list[str]] = defaultdict(list)
    for fila in leer_csv(CLAUDE / "01_inventario" / "inventario_maestro.csv"):
        for ruta in rutas_locales(fila["Local files"]):
            ids_por_ruta[ruta].append(fila["Resource ID"])
    url_por_ruta: dict[str, str] = {}
    for nombre in ("manifiesto_descargas.csv", "manifiesto_arcgis.csv", "manifiesto_api.csv"):
        for fila in leer_csv(CLAUDE / "05_manifiesto" / nombre):
            if fila.get("ruta_local"):
                url_por_ruta[fila["ruta_local"]] = fila["url"]

    archivos: dict[str, dict[str, Any]] = {}

    def agregar(sha: str, nombre: str, bytes_: int | None, url: str, institucion: str, ids: list[str]) -> None:
        if sha in archivos:
            existente = archivos[sha]
            for identificador in ids:
                if identificador not in existente["fuente_ids"]:
                    existente["fuente_ids"].append(identificador)
            existente["url_origen"] = existente["url_origen"] or url
            existente["bytes"] = existente["bytes"] or bytes_
            return
        archivos[sha] = {
            "sha256": sha, "archivo": nombre, "bytes": bytes_, "tamano": tamano_legible(bytes_),
            "url_origen": url, "institucion": institucion, "fuente_ids": list(ids),
        }

    for ruta, sha in sha_ruta.items():
        partes = ruta.split("/")
        institucion = partes[1] if len(partes) > 2 else "Otras_fuentes"
        ids = [resolver(catalogo["alias"], i) for i in ids_por_ruta.get(ruta, [])]
        agregar(sha, partes[-1], tamanos.get(ruta), url_por_ruta.get(ruta, ""), institucion, ids)

    for item in leer_json(CODEX / "data" / "catalog.json"):
        institucion = item["localPath"].split("/")[-2] if "/" in item["localPath"] else item["institution"]
        agregar(item["sha256"], item["fileName"], item["bytes"], item["downloadUrl"], institucion, [resolver(catalogo["alias"], item["id"])])

    prefijos = {"AMSCLAE": "AMSCLAE", "INSIVUMEH": "INSIVUMEH", "USAC": "USAC", "TheOceanCleanup": "The_Ocean_Cleanup",
                "WorldBank": "Banco_Mundial", "GRDC": "GRDC", "HydroRIVERS": "HydroSHEDS", "Guatemala": "Cartografia_SIG"}
    for f in leer_json(ANTIGRAVITY / "manifests" / "data_manifest.json")["files"]:
        if not f["path"].startswith("data/raw/") or f["path"].endswith((".json", ".html")):
            continue
        nombre = f["path"].split("/")[-1]
        institucion = prefijos.get(nombre.split("_")[0], "Otras_fuentes")
        agregar(f["sha256"], nombre, f.get("size_bytes"), "", institucion, [])

    # Ruta única dentro del paquete.
    usados: set[str] = set()
    filas = []
    for sha, a in sorted(archivos.items(), key=lambda kv: (kv[1]["institucion"].lower(), kv[1]["archivo"].lower())):
        carpeta = carpeta_paquete(a["institucion"])
        ruta = f"{carpeta}/{a['archivo']}"
        if ruta.lower() in usados:
            base, punto, ext = a["archivo"].rpartition(".")
            ruta = f"{carpeta}/{base}_{sha[:8]}.{ext}" if punto else f"{carpeta}/{a['archivo']}_{sha[:8]}"
        usados.add(ruta.lower())
        a["ruta_paquete"] = ruta
        a["fuente_ids"] = [i for i in a["fuente_ids"] if i in fuentes or i.startswith("GT-PUB")]
        filas.append(a)
    for indice, fila in enumerate(filas, start=1):
        fila["id"] = f"ORIG-{indice:04d}"
    return filas


# ---------------------------------------------------------------------------
# Escritura
# ---------------------------------------------------------------------------

COLUMNAS_FUENTES = [
    "id", "tipo", "titulo", "institucion", "institucion_detalle", "categoria", "tema", "anios", "anio_min", "anio_max",
    "cobertura", "parametros", "formato", "registros", "licencia", "acceso", "acceso_detalle", "descarga", "archivos",
    "url_fuente", "url_descarga", "sha256", "verificacion", "http", "motagua_las_vacas", "destacado", "prioridad",
    "ids_alias", "fecha_acceso", "notas",
]
COLUMNAS_PUBLICACIONES = [
    "id", "titulo", "autores", "anio", "fuente", "tipo", "url", "lugar", "anios_muestreo", "parametros",
    "resultados_numericos", "datos_crudos", "acceso", "motagua_las_vacas", "ids_alias",
]
COLUMNAS_FALTANTES = [
    "id", "institucion", "institucion_corta", "estado", "dato_esperado", "evidencia", "url_evidencia", "que_se_intento",
    "motivo", "solicitud_factible", "siguiente_paso",
]
COLUMNAS_MEDICIONES = [
    "sitio_id", "sitio", "capa", "codigo", "parametro", "parametro_original", "valor", "unidad", "unidad_verificada",
    "fecha", "tipo_dato", "fuente_id", "control", "nota",
]
COLUMNAS_MANIFIESTO = ["id", "institucion", "archivo", "ruta_paquete", "bytes", "tamano", "sha256", "url_origen", "fuente_ids"]


def main() -> None:
    catalogo = construir_catalogo()
    fuentes = catalogo["fuentes"]
    publicaciones = catalogo["publicaciones"]

    constructor = Constructor(catalogo)
    constructor.territorio()
    constructor.monitoreo_insivumeh()
    constructor.caudales_insivumeh()
    constructor.usac_las_vacas()
    constructor.acidificacion_marn()
    constructor.atitlan_wqp()
    constructor.ptar_hydrowaste()
    constructor.wpdx()
    constructor.plasticos()
    constructor.clima()
    constructor.gemstat()
    constructor.controlar_oxigeno()
    constructor.asignar_cuencas(fuentes, publicaciones)

    # Marca en el catálogo qué fuentes alimentan el mapa.
    en_mapa: dict[str, list[str]] = defaultdict(list)
    for capa_id, capa in constructor.capas.items():
        for fid in capa["meta"]["fuente_ids"]:
            if capa_id not in en_mapa[fid]:
                en_mapa[fid].append(capa_id)
    for r in list(fuentes.values()) + list(publicaciones.values()):
        r["capas"] = en_mapa.get(r["id"], [])

    faltantes = construir_faltantes()
    manifiesto = construir_manifiesto(catalogo)

    lista_fuentes = sorted(fuentes.values(), key=lambda r: r["id"])
    lista_publicaciones = sorted(publicaciones.values(), key=lambda r: r["id"])

    # Organizaciones a partir del catálogo unificado.
    organizaciones: dict[str, dict[str, Any]] = {}
    for r in lista_fuentes:
        o = organizaciones.setdefault(r["institucion"], {
            "institucion": r["institucion"], "categoria": r["categoria"], "conjuntos_de_datos": 0, "documentos": 0,
            "portales": 0, "archivos_descargados": 0, "anio_min": None, "anio_max": None, "temas": Counter(),
        })
        o["conjuntos_de_datos"] += r["tipo"] == "Conjunto de datos"
        o["documentos"] += r["tipo"] == "Documento"
        o["portales"] += r["tipo"] == "Portal o servicio"
        o["archivos_descargados"] += r["archivos"]
        for clave, funcion in (("anio_min", min), ("anio_max", max)):
            if r[clave]:
                o[clave] = r[clave] if o[clave] is None else funcion(o[clave], r[clave])
        o["temas"][r["tema"]] += 1
    lista_orgs = sorted(organizaciones.values(), key=lambda o: -(o["conjuntos_de_datos"] + o["documentos"] + o["portales"]))
    for o in lista_orgs:
        o["temas_principales"] = [t for t, _ in o.pop("temas").most_common(3)]

    # --- datos/catalogo
    destino = DATOS
    escribir_csv(destino / "catalogo" / "fuentes.csv", lista_fuentes, COLUMNAS_FUENTES)
    escribir_csv(destino / "catalogo" / "publicaciones.csv", lista_publicaciones, COLUMNAS_PUBLICACIONES)
    escribir_csv(destino / "catalogo" / "faltantes.csv", faltantes, COLUMNAS_FALTANTES)
    escribir_csv(destino / "catalogo" / "organizaciones.csv", lista_orgs,
                 ["institucion", "categoria", "conjuntos_de_datos", "documentos", "portales", "archivos_descargados", "anio_min", "anio_max", "temas_principales"])
    escribir_csv(destino / "catalogo" / "equivalencias_de_ids.csv",
                 [{"id_origen": k, "id_canonico": v} for k, v in sorted(catalogo["alias"].items())], ["id_origen", "id_canonico"])

    # --- datos/capas
    indice_capas = []
    for capa_id, capa in constructor.capas.items():
        escribir_json(destino / "capas" / f"{capa_id}.geojson", {"type": "FeatureCollection", "features": capa["features"]})
        meta = dict(capa["meta"])
        meta["archivo"] = f"capas/{capa_id}.geojson"
        meta["elementos"] = len(capa["features"])
        meta.setdefault("fuera_de_guatemala", False)
        indice_capas.append(meta)

    # --- datos/mediciones
    sitios = []
    for capa_id, capa in constructor.capas.items():
        if capa["meta"]["geometria"] != "punto":
            continue
        for f in capa["features"]:
            p = f["properties"]
            sitios.append({
                "sitio_id": f["id"], "capa": capa_id, "nombre": p["nombre"], "tipo": p.get("tipo", ""),
                "longitud": f["geometry"]["coordinates"][0], "latitud": f["geometry"]["coordinates"][1],
                "precision": PRECISION.get(p.get("precision", ""), ""), "institucion": p.get("institucion", ""),
                "cuenca_oficial": p.get("cuenca_oficial", ""), "departamento": p.get("departamento", ""),
                "municipio": p.get("municipio", ""), "fecha": p.get("fecha", ""), "tipo_dato": p.get("tipo_dato", ""),
                "fuente_ids": p.get("fuente_ids", []),
            })
    escribir_csv(destino / "mediciones" / "sitios.csv", sitios,
                 ["sitio_id", "capa", "nombre", "tipo", "longitud", "latitud", "precision", "institucion", "cuenca_oficial",
                  "departamento", "municipio", "fecha", "tipo_dato", "fuente_ids"])
    escribir_csv(destino / "mediciones" / "mediciones.csv", constructor.mediciones, COLUMNAS_MEDICIONES)
    usados = Counter(m["codigo"] for m in constructor.mediciones)
    escribir_csv(destino / "mediciones" / "parametros.csv",
                 [{"codigo": c, "nombre": n, "unidad": u, "grupo": g, "mediciones": usados.get(c, 0)} for c, n, u, g, _ in PARAMETROS if usados.get(c)],
                 ["codigo", "nombre", "unidad", "grupo", "mediciones"])

    # --- datos/manifiesto
    escribir_csv(destino / "manifiesto" / "originales.csv", manifiesto, COLUMNAS_MANIFIESTO)

    # --- resumen
    conteo_tipos = Counter(r["tipo"] for r in lista_fuentes)
    resumen = {
        "version": VERSION,
        "fecha_corte": FECHA_CORTE,
        "fuentes": len(lista_fuentes),
        "conjuntos_de_datos": conteo_tipos["Conjunto de datos"],
        "documentos": conteo_tipos["Documento"],
        "portales": conteo_tipos["Portal o servicio"],
        "publicaciones": len(lista_publicaciones),
        "publicaciones_acceso_abierto": sum(1 for p in lista_publicaciones if p["acceso"].lower().startswith("público")),
        "faltantes": len(faltantes),
        "organizaciones": len(lista_orgs),
        "archivos_originales": len(manifiesto),
        "bytes_originales": sum(a["bytes"] or 0 for a in manifiesto),
        "fuentes_con_archivo": sum(1 for r in lista_fuentes if r["descarga"] == "Archivo descargado"),
        "motagua_las_vacas": sum(1 for r in lista_fuentes if r["motagua_las_vacas"]) + sum(1 for p in lista_publicaciones if p["motagua_las_vacas"]),
        "capas": {c["id"]: c["elementos"] for c in indice_capas},
        "puntos_en_mapa": sum(c["elementos"] for c in indice_capas if c["geometria"] == "punto"),
        "mediciones": len(constructor.mediciones),
        "parametros": len(usados),
        "ids_unificados": len(catalogo["alias"]),
        "registros_agregados_sin_equivalente": catalogo["nuevos"],
        "excluidos_del_mapa": constructor.excluidos,
        "controles_de_calidad": sum(1 for m in constructor.mediciones if m["control"]),
        "temas": dict(Counter(r["tema"] for r in lista_fuentes).most_common()),
    }
    escribir_json(destino / "resumen.json", resumen, compacto=False)

    config_ruta = destino / "config.json"
    if not config_ruta.exists():
        escribir_json(config_ruta, {
            "enlace_originales": "",
            "nota": "Pegue en enlace_originales el enlace público de la carpeta o ZIP de originales (por ejemplo, Google Drive).",
        }, compacto=False)

    # --- datos/app (lo que carga la web)
    campos_app = [c for c in COLUMNAS_FUENTES if c not in {"institucion_detalle", "verificacion", "http", "fecha_acceso"}] + ["capas", "institucion_detalle", "verificacion"]
    escribir_json(destino / "app" / "catalogo.json", [{k: r.get(k) for k in campos_app} for r in lista_fuentes])
    escribir_json(destino / "app" / "publicaciones.json", [{k: p.get(k) for k in COLUMNAS_PUBLICACIONES} for p in lista_publicaciones])
    escribir_json(destino / "app" / "faltantes.json", faltantes)
    escribir_json(destino / "app" / "capas.json", indice_capas)
    escribir_json(destino / "app" / "parametros.json",
                  [{"codigo": c, "nombre": n, "unidad": u, "grupo": g} for c, n, u, g, _ in PARAMETROS if usados.get(c)])

    print(f"Fuentes: {resumen['fuentes']} ({resumen['conjuntos_de_datos']} conjuntos, {resumen['documentos']} documentos, {resumen['portales']} portales)")
    print(f"Publicaciones: {resumen['publicaciones']} · Faltantes: {resumen['faltantes']} · Organizaciones: {resumen['organizaciones']}")
    print(f"IDs unificados: {resumen['ids_unificados']} · Registros nuevos: {resumen['registros_agregados_sin_equivalente']}")
    print(f"Capas: {resumen['capas']}")
    print(f"Mediciones: {resumen['mediciones']} · Parámetros: {resumen['parametros']} · Controles: {resumen['controles_de_calidad']}")
    print(f"Archivos originales: {resumen['archivos_originales']} ({tamano_legible(resumen['bytes_originales'])})")
    print(f"Excluidos del mapa: {len(constructor.excluidos)}")


if __name__ == "__main__":
    main()
