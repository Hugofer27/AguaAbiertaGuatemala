"""ArcGIS Online: (1) busca ítems públicos sobre agua en Guatemala y (2) descarga como GeoJSON
las capas públicas seleccionadas (consulta paginada where=1=1). Solo usa servicios públicos sin
autenticación; un servidor que exige credenciales o bloquea el acceso se registra como fallo.

Uso:
  python 07_arcgis_capas.py <raíz> buscar
  python 07_arcgis_capas.py <raíz> descargar
"""
import csv
import datetime as dt
import hashlib
import json
import re
import sys
import time
from pathlib import Path

import requests

RAIZ = Path(sys.argv[1])
MODO = sys.argv[2]
PAGINA = int(sys.argv[3]) if len(sys.argv) > 3 else 2000  # tamaño de página; bajar si el servidor corta
S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0 (RiosAbiertosGT-inventario; investigacion academica)"
B = "https://www.arcgis.com/sharing/rest"

CONSULTAS = ["Guatemala calidad agua", "Guatemala ríos", "Guatemala rios", "Guatemala cuencas", "Motagua",
             "Atitlán", "Atitlan", "Amatitlán", "Amatitlan", "Izabal", "Petén Itzá", "Guatemala pozos",
             "Guatemala aguas residuales", "Guatemala inundaciones", "Guatemala precipitación",
             "Guatemala hidrología", "Guatemala acuífero", "Guatemala lago", "Guatemala desechos sólidos",
             "Guatemala estaciones meteorológicas", "Guatemala water", "Guatemala river", "Guatemala watershed",
             "Guatemala flood", "Guatemala rainfall", "Guatemala sanitation", "Guatemala drinking water",
             "Las Vacas Guatemala", "Villalobos", "Samalá", "Usumacinta", "Guatemala agua potable",
             "Guatemala humedales", "Guatemala manglar", "Guatemala sequía", "Guatemala microcuencas"]
TIPOS = ("Feature Service", "Map Service", "Web Map", "Web Experience", "Dashboard", "Web Mapping Application",
         "CSV", "Shapefile", "File Geodatabase", "GeoJSON", "Image Service", "Microsoft Excel", "KML",
         "StoryMap", "Hub Site Application")
AGUA = re.compile(r"agua|r[ií]o|cuenca|lago|laguna|pozo|residual|inund|precip|lluvia|hidr|acu[ií]f|desecho|"
                  r"residuo|sequ|humedal|manglar|water|river|basin|watershed|flood|rain|lake|well|sanita|motagua|"
                  r"atitl|amatitl|izabal|samal|usumacinta|villalobos|las vacas|calidad|estaci", re.I)


def buscar():
    vistos, filas, log = set(), [], []
    for q in CONSULTAS:
        n = 0
        for start in (1, 101):
            try:
                r = S.get(f"{B}/search", params={"q": q, "num": 100, "start": start, "f": "json"}, timeout=60).json()
            except Exception as e:
                log.append({"consulta": q, "resultados": -1, "nota": str(e)[:100]})
                break
            for x in r.get("results", []):
                texto = f"{x.get('title','')} {x.get('snippet','')} {' '.join(x.get('tags') or [])}"
                ext = x.get("extent") or []
                en_gt = bool(ext) and -93 < ext[0][0] < -87.5 and 13 < ext[0][1] < 18.5
                if x["type"] not in TIPOS or not AGUA.search(texto) or not (en_gt or re.search(r"guatemal|atitl|motagua|amatitl|izabal|pet[eé]n", texto, re.I)):
                    continue
                n += 1
                if x["id"] in vistos:
                    continue
                vistos.add(x["id"])
                filas.append({"item_id": x["id"], "titulo": x["title"], "tipo": x["type"], "propietario": x.get("owner"),
                              "org_id": x.get("orgId"), "url_servicio": x.get("url") or "",
                              "url_item": f"https://www.arcgis.com/home/item.html?id={x['id']}",
                              "creado": dt.datetime.fromtimestamp(x["created"] / 1000).date().isoformat(),
                              "modificado": dt.datetime.fromtimestamp(x["modified"] / 1000).date().isoformat(),
                              "licencia": re.sub("<[^>]+>", " ", x.get("licenseInfo") or "")[:150],
                              "resumen": (x.get("snippet") or "")[:300], "tags": "; ".join(x.get("tags") or [])[:200],
                              "consulta": q})
            if r.get("nextStart", -1) == -1:
                break
            time.sleep(0.5)
        log.append({"consulta": q, "resultados": n, "nota": "ArcGIS Online search, ítems públicos"})
    out = RAIZ / "01_inventario" / "auto" / "arcgis_online_items.csv"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    with open(RAIZ / "06_registro_busquedas" / "log_arcgis_busqueda.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["consulta", "resultados", "nota"])
        w.writeheader()
        w.writerows(log)
    print("ítems:", len(filas))


# Capas públicas de la organización ArcGIS Online del MARN (alojadas en services1.arcgis.com)
MARN = "https://services1.arcgis.com/1ZwElXgfK1bj5Hq0/arcgis/rest/services"
CAPAS = {
    "MARN_Rios_MAGA_2016": f"{MARN}/Rios_MAGA/FeatureServer/0",
    "MARN_Cuencas_38_MAGA_2001": f"{MARN}/Cuencas_38/FeatureServer/0",
    "MARN_Subcuencas_MAGA_2001": f"{MARN}/Subcuencas_Hidrgráficas_MAGA_2001/FeatureServer/0",
    "MARN_Microcuencas": f"{MARN}/Microcuencas/FeatureServer/0",
    "MARN_Lagos_Lagunas_MAGA_2001": f"{MARN}/Lagos_y_Lagunas_MAGA_2001/FeatureServer/0",
    "MARN_Cuerpos_agua_MAGA": f"{MARN}/Cuerpos_de_agua_MAGA/FeatureServer/0",
    "MARN_Rios_25m_ancho": f"{MARN}/Ríos_25m_ancho/FeatureServer/0",
    "MARN_Fuentes_agua": f"{MARN}/Fuentes_agua/FeatureServer/0",
    "MARN_Rio_Samala": f"{MARN}/Rio_Samala/FeatureServer/0",
    "MARN_Cuenca_Rio_Samala_Riesgo": f"{MARN}/Cuenca_Rio_Samala_Riesgo/FeatureServer/0",
    "MARN_Inundaciones_ZMC": f"{MARN}/Inundaciones_ZMC/FeatureServer/0",
    "MARN_Cuencas_ZMC": f"{MARN}/CUENCAS_ZMC_GT/FeatureServer/0",
    "MARN_Sitios_monitoreo_acidificacion": f"{MARN}/Sitios_monitoreo_acidificación/FeatureServer/0",
    "MARN_Potencial_mun_cuenca": f"{MARN}/POTEN_MUN_CUENC/FeatureServer/0",
    "MARN_Produccion_acuicola_salinera": f"{MARN}/PRODUCCIÓN_ACUICOLA_SALINERA/FeatureServer/0",
    "MARN_Ranking_municipal_residuos": f"{MARN}/Rankin_Municipal/FeatureServer/0",
    "MARN_Limite_costero": f"{MARN}/Limite_Costero/FeatureServer/0",
    "MARN_Erosion_potencial": f"{MARN}/EROSION_POTENCIAL/FeatureServer/0",
    "MARN_Poblados_INE_2018": f"{MARN}/Poblados_INE_2018/FeatureServer/0",
    "MARN_Limites_municipales_IGN_2016": f"{MARN}/Limites_Municipales_IGN_2016/FeatureServer/0",
}


def descargar_capa(nombre, url, carpeta):
    meta = S.get(url, params={"f": "json"}, timeout=60)
    m = meta.json()
    if "error" in m:
        raise RuntimeError(m["error"])
    maxr = min(m.get("maxRecordCount") or 1000, 2000, PAGINA)
    feats, offset = [], 0
    while True:
        r = S.get(f"{url}/query", params={"where": "1=1", "outFields": "*", "f": "geojson", "outSR": 4326,
                                           "resultOffset": offset, "resultRecordCount": maxr}, timeout=300)
        d = r.json()
        if "error" in d:
            raise RuntimeError(d["error"])
        lote = d.get("features", [])
        feats += lote
        if len(lote) < maxr and not d.get("properties", {}).get("exceededTransferLimit"):
            break
        offset += len(lote)
        if not lote:
            break
        time.sleep(0.3)
    gj = {"type": "FeatureCollection", "name": nombre, "fuente": url, "descargado": dt.datetime.now().isoformat(timespec="seconds"),
          "campos": [f["name"] for f in m.get("fields", [])], "features": feats}
    ruta = carpeta / f"{nombre}.geojson"
    contenido = json.dumps(gj, ensure_ascii=False).encode("utf-8")
    ruta.write_bytes(contenido)
    return ruta, len(feats), m.get("geometryType"), contenido


def descargar():
    carpeta = RAIZ / "02_datos_originales" / "MARN_ArcGIS"
    carpeta.mkdir(parents=True, exist_ok=True)
    manif = RAIZ / "05_manifiesto" / "manifiesto_arcgis.csv"
    previos = {}
    if manif.exists():
        previos = {r["clave"]: r for r in csv.DictReader(open(manif, encoding="utf-8"))}
    filas = []
    for nombre, url in CAPAS.items():
        prev = previos.get(f"ARCGIS-{nombre}")
        if prev and prev["estado"] == "descargado" and (RAIZ / prev["ruta_local"]).exists():
            filas.append(prev)
            continue
        fila = {"clave": f"ARCGIS-{nombre}", "organizacion": "MARN (ArcGIS Online)", "url": url, "ruta_local": "",
                "estado": "", "bytes": "", "sha256": "", "fecha_acceso": dt.datetime.now().isoformat(timespec="seconds"), "nota": ""}
        try:
            ruta, n, geom, contenido = descargar_capa(nombre, url, carpeta)
            fila.update(ruta_local=str(ruta.relative_to(RAIZ)).replace("\\", "/"), estado="descargado", bytes=len(contenido),
                        sha256=hashlib.sha256(contenido).hexdigest(), nota=f"{n} entidades; {geom}")
        except Exception as e:
            fila.update(estado="fallo", nota=str(e)[:200])
        print(fila["estado"], nombre, fila["nota"], flush=True)
        filas.append(fila)
    with open(manif, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)


{"buscar": buscar, "descargar": descargar}[MODO]()
