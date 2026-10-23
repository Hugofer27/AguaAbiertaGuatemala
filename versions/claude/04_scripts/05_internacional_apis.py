"""Descarga datos de fuentes internacionales con API pública y los filtra a Guatemala.

Fuentes: Banco Mundial (WDI), ONU (base global de indicadores ODS, objetivo 6), HydroWASTE
(figshare), NOAA GHCN-Daily, Water Point Data Exchange (WPdx), OpenStreetMap (Overpass) y
DesInventar. Cada archivo queda en 02_datos_originales/<fuente>/ y se registra con SHA-256 en
05_manifiesto/manifiesto_api.csv. Un fallo en una fuente se registra y no detiene las demás.

Uso: python 05_internacional_apis.py <carpeta raíz de Investigación Claude> [fuente ...]
"""
import csv
import datetime as dt
import hashlib
import io
import json
import sys
import time
import zipfile
from pathlib import Path

import pandas as pd
import requests

RAIZ = Path(sys.argv[1])
DATOS = RAIZ / "02_datos_originales"
PROC = RAIZ / "03_datos_procesados"
MANIF = RAIZ / "05_manifiesto" / "manifiesto_api.csv"
S = requests.Session()
S.headers["User-Agent"] = "RiosAbiertosGT-inventario/0.1 (investigacion academica)"
FILAS = []


def guardar(clave, org, url, ruta: Path, contenido: bytes, nota=""):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_bytes(contenido)
    FILAS.append({"clave": clave, "organizacion": org, "url": url,
                  "ruta_local": str(ruta.relative_to(RAIZ)).replace("\\", "/"), "estado": "descargado",
                  "bytes": len(contenido), "sha256": hashlib.sha256(contenido).hexdigest(),
                  "fecha_acceso": dt.datetime.now().isoformat(timespec="seconds"), "nota": nota})
    print("OK", clave, len(contenido), flush=True)


def fallo(clave, org, url, nota):
    FILAS.append({"clave": clave, "organizacion": org, "url": url, "ruta_local": "", "estado": "fallo",
                  "bytes": "", "sha256": "", "fecha_acceso": dt.datetime.now().isoformat(timespec="seconds"),
                  "nota": str(nota)[:250]})
    print("FALLO", clave, str(nota)[:150], flush=True)


# ------------------------------------------------------------------ Banco Mundial
WB_IND = ["SH.H2O.BASW.ZS", "SH.H2O.BASW.RU.ZS", "SH.H2O.BASW.UR.ZS", "SH.H2O.SMDW.ZS", "SH.H2O.SMDW.RU.ZS",
          "SH.H2O.SMDW.UR.ZS", "SH.STA.BASS.ZS", "SH.STA.SMSS.ZS", "SH.STA.ODFC.ZS", "SH.STA.HYGN.ZS",
          "SH.STA.WASH.P5", "ER.H2O.FWTL.K3", "ER.H2O.FWTL.ZS", "ER.H2O.INTR.K3", "ER.H2O.INTR.PC",
          "ER.H2O.FWAG.ZS", "ER.H2O.FWDM.ZS", "ER.H2O.FWIN.ZS", "ER.H2O.FWST.ZS", "ER.GDP.FWTL.M3.KD",
          "AG.LND.PRCP.MM", "AG.LND.IRIG.AG.ZS", "EN.POP.EL5M.ZS", "EG.ELC.HYRO.ZS"]


def bancomundial():
    filas = []
    for ind in WB_IND:
        url = f"https://api.worldbank.org/v2/country/GTM/indicator/{ind}?format=json&per_page=200"
        try:
            d = S.get(url, timeout=60).json()
            for v in d[1] or []:
                filas.append({"indicador": ind, "nombre": v["indicator"]["value"], "anio": v["date"], "valor": v["value"]})
        except Exception as e:
            fallo(f"WB-{ind}", "Banco Mundial", url, e)
        time.sleep(0.3)
    df = pd.DataFrame(filas)
    guardar("WB-WDI-AGUA-GTM", "Banco Mundial", "https://api.worldbank.org/v2/country/GTM/indicator/<ind>",
            DATOS / "BancoMundial" / "wdi_agua_guatemala.csv", df.to_csv(index=False).encode("utf-8"),
            f"{df['indicador'].nunique()} indicadores, {df['valor'].notna().sum()} valores no nulos")


# ------------------------------------------------------------------ ODS (UNSD)
def ods():
    base = "https://unstats.un.org/sdgapi/v1/sdg"
    try:
        series = S.get(f"{base}/Series/List", params={"allreleases": "false"}, timeout=120).json()
        codigos = sorted({s["code"] for s in series if "6" in (s.get("goal") or [])})
    except Exception as e:
        fallo("UNSD-SDG6", "ONU - UNSD", base, e)
        return
    filas = []
    for c in codigos:
        try:
            d = S.get(f"{base}/Series/Data", params={"seriesCode": c, "areaCode": 320, "pageSize": 1000}, timeout=60).json()
            for x in d.get("data", []):
                filas.append({"serie": c, "descripcion": x.get("seriesDescription"), "indicador": ";".join(x.get("indicator", [])),
                              "anio": x.get("timePeriodStart"), "valor": x.get("value"),
                              "dimensiones": json.dumps(x.get("dimensions", {}), ensure_ascii=False),
                              "fuente": x.get("source")})
        except Exception as e:
            fallo(f"UNSD-{c}", "ONU - UNSD", base, e)
        time.sleep(0.3)
    df = pd.DataFrame(filas)
    guardar("UNSD-SDG6-GTM", "ONU - División de Estadística (base global ODS)", f"{base}/Series/Data?areaCode=320",
            DATOS / "ONU_ODS" / "ods6_guatemala.csv", df.to_csv(index=False).encode("utf-8"),
            f"{len(codigos)} series consultadas; {df['serie'].nunique() if len(df) else 0} con datos; {len(df)} registros")


# ------------------------------------------------------------------ HydroWASTE
def hydrowaste():
    url = "https://api.figshare.com/v2/articles/14847786/files"
    try:
        files = S.get(url, timeout=60).json()
        f = files[0]
        z = S.get(f["download_url"], timeout=300).content
        guardar("HYDROWASTE-V10", "McGill / HydroSHEDS (HydroWASTE v1.0)", f["download_url"],
                DATOS / "HydroWASTE" / f["name"], z, "archivo global original (CC BY 4.0)")
        with zipfile.ZipFile(io.BytesIO(z)) as zz:
            nombre = [n for n in zz.namelist() if n.lower().endswith(".csv")][0]
            df = pd.read_csv(zz.open(nombre), encoding="latin-1")
        gt = df[df["CNTRY_ISO"] == "GTM"]
        (PROC / "hydrowaste").mkdir(parents=True, exist_ok=True)
        gt.to_csv(PROC / "hydrowaste" / "hydrowaste_guatemala.csv", index=False)
        print("HydroWASTE Guatemala:", len(gt), "plantas", flush=True)
    except Exception as e:
        fallo("HYDROWASTE-V10", "McGill / HydroSHEDS", url, e)


# ------------------------------------------------------------------ GHCN-Daily
def ghcn():
    # Espejo oficial de NOAA en AWS Open Data (NCEI respondió 503 durante la ejecución)
    base = "https://noaa-ghcn-pds.s3.amazonaws.com"
    try:
        est = S.get(f"{base}/ghcnd-stations.txt", timeout=120).text
        inv = S.get(f"{base}/ghcnd-inventory.txt", timeout=300).text
    except Exception as e:
        fallo("GHCN-D", "NOAA NCEI", base, e)
        return
    filas_e = [l for l in est.splitlines() if l.startswith("GT")]
    filas_i = [l for l in inv.splitlines() if l.startswith("GT")]
    if not filas_e:
        fallo("GHCN-D-ESTACIONES-GT", "NOAA NCEI (GHCN-Daily)", f"{base}/ghcnd-stations.txt", "sin estaciones GT (respuesta vacía o error)")
        return
    guardar("GHCN-D-ESTACIONES-GT", "NOAA NCEI (GHCN-Daily)", f"{base}/ghcnd-stations.txt",
            DATOS / "NOAA_GHCN" / "ghcnd-stations_GT.txt", "\n".join(filas_e).encode(), f"{len(filas_e)} estaciones GT")
    guardar("GHCN-D-INVENTARIO-GT", "NOAA NCEI (GHCN-Daily)", f"{base}/ghcnd-inventory.txt",
            DATOS / "NOAA_GHCN" / "ghcnd-inventory_GT.txt", "\n".join(filas_i).encode(), f"{len(filas_i)} filas estación-elemento")
    for l in filas_e:
        sid = l[:11]
        url = f"{base}/csv/by_station/{sid}.csv"
        try:
            r = S.get(url, timeout=120)
            if r.status_code == 200:
                guardar(f"GHCN-D-{sid}", "NOAA NCEI (GHCN-Daily)", url, DATOS / "NOAA_GHCN" / "series" / f"{sid}.csv", r.content)
            else:
                fallo(f"GHCN-D-{sid}", "NOAA NCEI (GHCN-Daily)", url, f"HTTP {r.status_code}")
        except Exception as e:
            fallo(f"GHCN-D-{sid}", "NOAA NCEI (GHCN-Daily)", url, e)
        time.sleep(0.3)


# ------------------------------------------------------------------ WPdx
def wpdx():
    url = "https://data.waterpointdata.org/resource/jfkt-jmqa.json"
    try:
        r = S.get(url, params={"$where": "country_name='Guatemala'", "$limit": 50000}, timeout=120)
        datos = r.json()
        if isinstance(datos, dict):
            raise RuntimeError(datos)
        guardar("WPDX-GT", "Water Point Data Exchange (WPdx)", url + "?country_name=Guatemala",
                DATOS / "WPdx" / "wpdx_guatemala.json", json.dumps(datos, ensure_ascii=False).encode("utf-8"),
                f"{len(datos)} puntos de agua")
    except Exception as e:
        fallo("WPDX-GT", "Water Point Data Exchange (WPdx)", url, e)


# ------------------------------------------------------------------ OpenStreetMap
OSM_Q = {
    "plantas_tratamiento_aguas_residuales": 'nwr["man_made"="wastewater_plant"](area.gt);',
    "plantas_potabilizadoras": 'nwr["man_made"="water_works"](area.gt);',
    "pozos_agua": 'nwr["man_made"="water_well"](area.gt);',
    "tanques_torres_agua": 'nwr["man_made"~"water_tower|reservoir_covered|storage_tank"]["content"!="oil"](area.gt);',
    "represas_presas": 'nwr["waterway"~"dam|weir"](area.gt);',
    "rellenos_vertederos": 'nwr["landuse"="landfill"](area.gt);',
    "estaciones_monitoreo_agua": 'nwr["man_made"="monitoring_station"](area.gt);',
    "fuentes_manantiales": 'nwr["natural"="spring"](area.gt);',
    "rios_principales": 'way["waterway"="river"](area.gt);',
}


def osm():
    url = "https://overpass-api.de/api/interpreter"
    hechos = {p.stem.replace("osm_", "") for p in (DATOS / "OpenStreetMap").glob("osm_*.json")}
    for nombre, q in OSM_Q.items():
        if nombre in hechos:
            continue
        consulta = f'[out:json][timeout:600];area["ISO3166-1"="GT"][admin_level=2]->.gt;({q});out center tags;'
        try:
            r = S.post(url, data={"data": consulta}, timeout=660)
            r.raise_for_status()
            d = r.json()
            guardar(f"OSM-{nombre}", "OpenStreetMap (Overpass API)", url, DATOS / "OpenStreetMap" / f"osm_{nombre}.json",
                    r.content, f"{len(d.get('elements', []))} elementos; licencia ODbL")
        except Exception as e:
            fallo(f"OSM-{nombre}", "OpenStreetMap (Overpass API)", url, e)
        time.sleep(15)


# ------------------------------------------------------------------ DesInventar
def desinventar():
    for url in ["https://www.desinventar.net/DesInventar/download/DI_export_gtm.zip",
                "https://www.desinventar.net/DesInventar/download_base.jsp?countrycode=gtm"]:
        try:
            r = S.get(url, timeout=300)
            if r.status_code == 200 and r.content[:2] == b"PK":
                guardar("DESINVENTAR-GTM", "UNDRR - DesInventar", url, DATOS / "DesInventar" / "DI_export_gtm.zip", r.content)
                return
            fallo("DESINVENTAR-GTM", "UNDRR - DesInventar", url, f"HTTP {r.status_code} {r.headers.get('Content-Type')}")
        except Exception as e:
            fallo("DESINVENTAR-GTM", "UNDRR - DesInventar", url, e)


if __name__ == "__main__":
    fuentes = sys.argv[2:] or ["bancomundial", "ods", "hydrowaste", "wpdx", "osm", "desinventar", "ghcn"]
    for f in fuentes:
        try:
            globals()[f]()
        except Exception as e:
            fallo(f.upper(), f, "", f"error general: {e}")
    previos = []
    if MANIF.exists():
        previos = [r for r in csv.DictReader(open(MANIF, encoding="utf-8")) if r["clave"] not in {x["clave"] for x in FILAS}]
    campos = ["clave", "organizacion", "url", "ruta_local", "estado", "bytes", "sha256", "fecha_acceso", "nota"]
    with open(MANIF, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(previos + FILAS)
