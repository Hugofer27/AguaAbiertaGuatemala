"""Arma el paquete de archivos originales para subirlo a Drive (u otro almacenamiento).

Los ~2 GB de archivos originales no caben en GitHub. Este script los busca en las
carpetas de investigación de su computadora, verifica cada uno contra el SHA-256 de
`datos/manifiesto/originales.csv`, los copia sin duplicados a `originales/`
organizados por institución y, si se pide, genera un ZIP.

Ejemplo (Windows):

    python pipeline\\empaquetar_originales.py ^
        --buscar "D:\\Documentos D\\BaseDatosGT H2O\\Investigación Claude" ^
        --buscar "D:\\Documentos D\\BaseDatosGT H2O\\Investigación ChatGPT" ^
        --buscar "D:\\Documentos D\\BaseDatosGT H2O\\Investigación Antigravity" ^
        --zip

Después suba `originales/` o el ZIP a Drive, comparta el enlace como
"Cualquier persona con el enlace" y péguelo en `datos/config.json`.
"""

from __future__ import annotations

import argparse
import csv
import shutil
import sys
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from comun import DATOS, RAIZ, leer_csv, sha256_archivo, tamano_legible

LEEME = """Agua Abierta Guatemala · archivos originales
=============================================

Esta carpeta contiene copias sin modificar de los archivos públicos descargados de
instituciones guatemaltecas e internacionales. Cada archivo está verificado con su
huella SHA-256 (ver MANIFIESTO.csv).

- MANIFIESTO.csv: archivo, institución, URL de origen, tamaño, SHA-256 e IDs del catálogo.
- INFORME_EMPAQUETADO.txt: qué se encontró y qué faltó al armar el paquete.

Las licencias son las de cada institución. Antes de redistribuir un archivo, revise la
licencia indicada en datos/catalogo/fuentes.csv del proyecto.
"""


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Empaqueta los archivos originales verificados por SHA-256.")
    parser.add_argument("--buscar", action="append", default=[], help="Carpeta donde buscar originales (repetible).")
    parser.add_argument("--salida", default=str(RAIZ / "originales"), help="Carpeta de salida (por defecto originales/).")
    parser.add_argument("--manifiesto", default=str(DATOS / "manifiesto" / "originales.csv"), help="Manifiesto de originales.")
    parser.add_argument("--zip", action="store_true", help="Genera también AguaAbiertaGT_originales.zip junto a la carpeta de salida.")
    return parser.parse_args()


def main() -> int:
    args = argumentos()
    manifiesto = leer_csv(Path(args.manifiesto))
    salida = Path(args.salida).resolve()
    carpetas = [Path(c).expanduser().resolve() for c in args.buscar]
    if not carpetas:
        print("Indique al menos una carpeta con --buscar. Use --help para ver un ejemplo.")
        return 2
    for carpeta in carpetas:
        if not carpeta.is_dir():
            print(f"No existe la carpeta: {carpeta}")
            return 2

    por_sha = {fila["sha256"]: fila for fila in manifiesto}
    por_tamano: dict[int, list[str]] = defaultdict(list)
    sin_tamano_por_nombre: dict[str, list[str]] = defaultdict(list)
    for fila in manifiesto:
        if fila["bytes"]:
            por_tamano[int(float(fila["bytes"]))].append(fila["sha256"])
        else:
            sin_tamano_por_nombre[fila["archivo"].lower()].append(fila["sha256"])

    encontrados: dict[str, Path] = {}
    revisados = 0
    print(f"Buscando {len(manifiesto)} archivos en {len(carpetas)} carpeta(s)…")
    for carpeta in carpetas:
        for ruta in carpeta.rglob("*"):
            if not ruta.is_file() or salida in ruta.parents:
                continue
            try:
                tamano = ruta.stat().st_size
            except OSError:
                continue
            candidatos = por_tamano.get(tamano, []) + sin_tamano_por_nombre.get(ruta.name.lower(), [])
            candidatos = [c for c in candidatos if c not in encontrados]
            if not candidatos:
                continue
            revisados += 1
            huella = sha256_archivo(ruta)
            if huella in candidatos:
                encontrados[huella] = ruta

    salida.mkdir(parents=True, exist_ok=True)
    copiados = ya_presentes = 0
    filas_salida = []
    for fila in manifiesto:
        origen = encontrados.get(fila["sha256"])
        destino = salida / fila["ruta_paquete"]
        estado = "no encontrado"
        if destino.exists() and sha256_archivo(destino) == fila["sha256"]:
            estado = "ya presente"
            ya_presentes += 1
        elif origen is not None:
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origen, destino)
            estado = "copiado"
            copiados += 1
        filas_salida.append({**fila, "estado": estado})

    columnas = list(manifiesto[0].keys()) + ["estado"] if manifiesto else ["estado"]
    with (salida / "MANIFIESTO.csv").open("w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas_salida)
    (salida / "LEEME.txt").write_text(LEEME, encoding="utf-8")

    faltan = [f for f in filas_salida if f["estado"] == "no encontrado"]
    total_bytes = sum((salida / f["ruta_paquete"]).stat().st_size for f in filas_salida if f["estado"] != "no encontrado")
    informe = [
        "Agua Abierta Guatemala · informe de empaquetado",
        f"Fecha: {datetime.now().isoformat(timespec='seconds')}",
        f"Carpetas revisadas: {', '.join(str(c) for c in carpetas)}",
        f"Archivos en el manifiesto: {len(manifiesto)}",
        f"Copiados: {copiados} · Ya presentes: {ya_presentes} · No encontrados: {len(faltan)}",
        f"Tamaño del paquete: {tamano_legible(total_bytes)}",
        f"Archivos con tamaño coincidente que se verificaron por SHA-256: {revisados}",
        "",
        "No encontrados (se pueden volver a descargar desde url_origen):",
    ] + [f"- {f['ruta_paquete']}  {f['url_origen'] or '(sin URL registrada)'}" for f in faltan]
    (salida / "INFORME_EMPAQUETADO.txt").write_text("\n".join(informe) + "\n", encoding="utf-8")

    print("\n".join(informe[:7]))
    if args.zip:
        destino_zip = salida.parent / "AguaAbiertaGT_originales.zip"
        with zipfile.ZipFile(destino_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as paquete:
            for ruta in sorted(salida.rglob("*")):
                if ruta.is_file():
                    paquete.write(ruta, Path("originales") / ruta.relative_to(salida))
        print(f"ZIP generado: {destino_zip} ({tamano_legible(destino_zip.stat().st_size)})")
    print(f"Carpeta lista: {salida}")
    print("Siguiente paso: suba la carpeta o el ZIP a Drive y pegue el enlace en datos/config.json.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
