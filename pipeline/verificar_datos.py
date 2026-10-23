"""Controles de calidad de la carpeta `datos/`.

Uso:  python pipeline/verificar_datos.py
Termina con código 1 si encuentra errores; las advertencias no detienen el proceso.
"""

from __future__ import annotations

import sys
from collections import Counter

from comun import DATOS, dentro_de_guatemala, leer_csv, leer_json

errores: list[str] = []
advertencias: list[str] = []


def error(mensaje: str) -> None:
    errores.append(mensaje)


def main() -> int:
    requeridos = [
        "resumen.json", "config.json",
        "catalogo/fuentes.csv", "catalogo/publicaciones.csv", "catalogo/faltantes.csv", "catalogo/organizaciones.csv",
        "mediciones/mediciones.csv", "mediciones/sitios.csv", "mediciones/parametros.csv",
        "manifiesto/originales.csv",
        "app/catalogo.json", "app/publicaciones.json", "app/faltantes.json", "app/capas.json", "app/parametros.json",
    ]
    for ruta in requeridos:
        if not (DATOS / ruta).exists():
            error(f"Falta {ruta}. Ejecute primero: python pipeline/construir_datos.py")
    if errores:
        return reportar()

    catalogo = leer_json(DATOS / "app" / "catalogo.json")
    publicaciones = leer_json(DATOS / "app" / "publicaciones.json")
    ids_catalogo = [r["id"] for r in catalogo]
    ids_publicaciones = [p["id"] for p in publicaciones]
    conocidos = set(ids_catalogo) | set(ids_publicaciones)

    # 1. Identificadores únicos y alias que resuelven.
    for nombre, ids in (("catálogo", ids_catalogo), ("publicaciones", ids_publicaciones)):
        repetidos = [i for i, n in Counter(ids).items() if n > 1]
        if repetidos:
            error(f"IDs repetidos en {nombre}: {repetidos[:5]}")
    alias = [a for r in catalogo + publicaciones for a in r.get("ids_alias") or []]
    if set(alias) & conocidos:
        error(f"Un alias coincide con un ID canónico: {sorted(set(alias) & conocidos)[:5]}")
    for fila in leer_csv(DATOS / "catalogo" / "equivalencias_de_ids.csv"):
        if fila["id_canonico"] not in conocidos:
            error(f"La equivalencia {fila['id_origen']} → {fila['id_canonico']} apunta a un ID inexistente")

    # Texto dañado por una mala decodificación (carácter de reemplazo U+FFFD).
    for nombre, filas in (("catálogo", catalogo), ("publicaciones", publicaciones)):
        for r in filas:
            if any(isinstance(v, str) and "\ufffd" in v for v in r.values()):
                error(f"{nombre} {r['id']}: contiene el carácter de reemplazo U+FFFD; agregue la corrección en REPARACIONES")

    # 2. Campos obligatorios del catálogo.
    for r in catalogo:
        for campo in ("titulo", "institucion", "tipo", "tema", "acceso", "descarga"):
            if not r.get(campo):
                error(f"{r['id']}: campo vacío '{campo}'")
        if r["descarga"] == "Archivo descargado" and not (r.get("sha256") or r.get("url_descarga") or r.get("url_fuente")):
            advertencias.append(f"{r['id']}: marcado como descargado sin SHA-256 ni URL")

    # 3. Capas: coordenadas, fuentes y precisión.
    capas = leer_json(DATOS / "app" / "capas.json")
    total_puntos = 0
    for capa in capas:
        ruta = DATOS / capa["archivo"]
        if not ruta.exists():
            error(f"Falta el archivo de la capa {capa['id']}")
            continue
        geo = leer_json(ruta)
        if len(geo["features"]) != capa["elementos"]:
            error(f"{capa['id']}: el índice dice {capa['elementos']} elementos y el archivo tiene {len(geo['features'])}")
        for fid in capa["fuente_ids"]:
            if fid not in conocidos:
                error(f"{capa['id']}: la fuente {fid} no está en el catálogo")
        if capa["geometria"] != "punto":
            continue
        ids_capa = Counter()
        for f in geo["features"]:
            total_puntos += 1
            ids_capa[f["id"]] += 1
            lon, lat = f["geometry"]["coordinates"]
            if not capa.get("fuera_de_guatemala") and not dentro_de_guatemala(lon, lat):
                error(f"{capa['id']}/{f['id']}: coordenada fuera de Guatemala ({lon}, {lat})")
            p = f["properties"]
            if p.get("precision") not in {"publicada", "homonimo", "transcrita", "modelada", "aproximada"}:
                error(f"{capa['id']}/{f['id']}: precisión de ubicación no declarada")
            # Un punto cita registros del catálogo o, si la fuente es una nota o un comunicado, sus enlaces.
            enlaces = p.get("enlaces") or []
            if not p.get("fuente_ids") and not enlaces:
                error(f"{capa['id']}/{f['id']}: sin fuente")
            for e in enlaces:
                if not str(e.get("url", "")).startswith("https://") or not e.get("texto"):
                    error(f"{capa['id']}/{f['id']}: enlace de fuente incompleto o sin https ({e})")
            if p.get("precision") == "aproximada" and capa.get("visible"):
                error(f"{capa['id']}: una capa de ubicación aproximada no puede venir activa por defecto")
            for fid in p.get("fuente_ids", []):
                if fid not in conocidos:
                    error(f"{capa['id']}/{f['id']}: fuente {fid} inexistente")
        repetidos = [i for i, n in ids_capa.items() if n > 1]
        if repetidos:
            error(f"{capa['id']}: IDs repetidos {repetidos[:5]}")

    # 4. Mediciones: unidad, fuente y sitio.
    sitios = {fila["sitio_id"] for fila in leer_csv(DATOS / "mediciones" / "sitios.csv")}
    mediciones = leer_csv(DATOS / "mediciones" / "mediciones.csv")
    for m in mediciones:
        if m["sitio_id"] not in sitios:
            error(f"Medición de un sitio inexistente: {m['sitio_id']}")
        if not m["unidad"]:
            advertencias.append(f"{m['sitio_id']} {m['parametro']}: sin unidad")
        if m["fuente_id"] not in conocidos:
            error(f"{m['sitio_id']}: fuente de medición inexistente {m['fuente_id']}")
    marcadas = sum(1 for m in mediciones if m["control"])

    # 5. Manifiesto de originales.
    manifiesto = leer_csv(DATOS / "manifiesto" / "originales.csv")
    hashes = Counter(a["sha256"] for a in manifiesto)
    rutas = Counter(a["ruta_paquete"].lower() for a in manifiesto)
    if any(n > 1 for n in hashes.values()):
        error("El manifiesto tiene SHA-256 repetidos")
    if any(n > 1 for n in rutas.values()):
        error("El manifiesto tiene rutas de paquete repetidas")
    for a in manifiesto:
        if len(a["sha256"]) != 64:
            error(f"{a['id']}: SHA-256 no válido")

    resumen = leer_json(DATOS / "resumen.json")
    print("Agua Abierta Guatemala · verificación de datos")
    print(f"  Fuentes: {len(catalogo)} · Publicaciones: {len(publicaciones)} · Faltantes: {resumen['faltantes']}")
    print(f"  Capas: {len(capas)} · Puntos: {total_puntos} · Mediciones: {len(mediciones)} ({marcadas} con control de calidad)")
    print(f"  Archivos originales en el manifiesto: {len(manifiesto)}")
    return reportar()


def reportar() -> int:
    for mensaje in advertencias[:20]:
        print(f"  Advertencia: {mensaje}")
    if len(advertencias) > 20:
        print(f"  … y {len(advertencias) - 20} advertencias más")
    if errores:
        for mensaje in errores[:50]:
            print(f"  ERROR: {mensaje}")
        print(f"Verificación fallida: {len(errores)} errores.")
        return 1
    print("Verificación correcta.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
