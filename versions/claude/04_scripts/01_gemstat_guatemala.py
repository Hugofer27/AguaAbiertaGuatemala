"""Revisa si GEMStat (GFQA_v3.zip, en la carpeta raíz del proyecto) contiene estaciones de
Guatemala o de cuencas transfronterizas vecinas.

Uso: python 01_gemstat_guatemala.py <ruta a GFQA_v3.zip> <carpeta de salida>
"""
import io
import sys
import zipfile
from pathlib import Path

import pandas as pd

ZIP = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

# Caja envolvente aproximada de Guatemala ampliada 1 grado para captar cuencas compartidas
BBOX = dict(lat_min=12.7, lat_max=18.9, lon_min=-93.3, lon_max=-87.2)
VECINOS = ["Guatemala", "Mexico", "Belize", "Honduras", "El Salvador"]

with zipfile.ZipFile(ZIP) as z:
    st = pd.read_csv(io.BytesIO(z.read("GEMStat_station_metadata.csv")), encoding="latin-1")
    readme = z.read("README_output_format.txt").decode("latin-1", errors="replace")

paises = st["Country Name"].value_counts()
(OUT / "gemstat_paises_estaciones.csv").write_text(paises.to_csv(), encoding="utf-8")

lat = pd.to_numeric(st["Latitude"], errors="coerce")
lon = pd.to_numeric(st["Longitude"], errors="coerce")
en_caja = st[lat.between(BBOX["lat_min"], BBOX["lat_max"]) & lon.between(BBOX["lon_min"], BBOX["lon_max"])]
en_caja.to_csv(OUT / "gemstat_estaciones_region_guatemala.csv", index=False, encoding="utf-8")

vec = st[st["Country Name"].isin(VECINOS)]
print("Estaciones totales:", len(st), "| países:", st["Country Name"].nunique())
print("Estaciones por país vecino:")
print(vec["Country Name"].value_counts().to_string())
print("Estaciones dentro de la caja Guatemala+1°:", len(en_caja))
print(en_caja[["GEMS Station Number", "Country Name", "Water Type", "Station Identifier",
               "Water Body Name", "Main Basin", "Latitude", "Longitude"]].to_string())
print("\nREADME (primeras líneas):\n", readme[:1500])
