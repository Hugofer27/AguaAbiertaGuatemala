"""Extrae de GFQA_v3.zip (GEMStat, licencia CC BY 4.0) todas las muestras de las estaciones
mexicanas ubicadas en cuencas compartidas con Guatemala (Suchiate, Coatán, Grijalva-Usumacinta,
Hondo, Candelaria) o dentro de la caja Guatemala+1 grado.

Uso: python 02_gemstat_transfronterizo.py <GFQA_v3.zip> <csv de estaciones> <carpeta salida>
"""
import sys
import zipfile
from pathlib import Path

import pandas as pd

ZIP, ESTACIONES, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
OUT.mkdir(parents=True, exist_ok=True)

ids = set(pd.read_csv(ESTACIONES)["GEMS Station Number"])
partes = []
with zipfile.ZipFile(ZIP) as z:
    for nombre in sorted(z.namelist()):
        if not nombre.endswith(".csv") or nombre.startswith("GEMStat_"):
            continue
        with z.open(nombre) as f:
            for chunk in pd.read_csv(f, chunksize=500_000, encoding="latin-1", dtype=str):
                sel = chunk[chunk["GEMS Station Number"].isin(ids)]
                if len(sel):
                    sel = sel.assign(Archivo=nombre)
                    partes.append(sel)
        print(nombre, "listo", flush=True)

datos = pd.concat(partes, ignore_index=True)
datos.to_csv(OUT / "gemstat_muestras_cuencas_compartidas.csv", index=False, encoding="utf-8")
datos["Anio"] = datos["Sample Date"].str[:4]
resumen = (datos.groupby(["GEMS Station Number"])
           .agg(registros=("Value", "size"), parametros=("Parameter Code", "nunique"),
                anio_min=("Anio", "min"), anio_max=("Anio", "max"))
           .reset_index())
resumen.to_csv(OUT / "gemstat_resumen_estaciones_cuencas_compartidas.csv", index=False, encoding="utf-8")
print("Registros:", len(datos), "| estaciones con datos:", resumen.shape[0],
      "| parámetros:", datos["Parameter Code"].nunique(),
      "| años:", datos["Anio"].min(), "-", datos["Anio"].max())
