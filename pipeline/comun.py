"""Utilidades compartidas por los scripts del pipeline de Agua Abierta Guatemala."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Iterable

RAIZ = Path(__file__).resolve().parents[1]
FUENTES = RAIZ / "fuentes"
DATOS = RAIZ / "datos"

# Recuadro de Guatemala con un margen de ~25 km para coordenadas costeras.
BBOX_GT = (-92.5, 13.5, -88.1, 18.0)


def leer_csv(ruta: Path) -> list[dict[str, str]]:
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        return list(csv.DictReader(archivo))


def escribir_csv(ruta: Path, filas: Iterable[dict[str, Any]], columnas: list[str]) -> int:
    """Escribe CSV con BOM para que Excel reconozca UTF-8 al abrirlo."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with ruta.open("w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas, extrasaction="ignore", lineterminator="\n")
        escritor.writeheader()
        for fila in filas:
            escritor.writerow({clave: formatear_celda(fila.get(clave)) for clave in columnas})
            total += 1
    return total


def formatear_celda(valor: Any) -> Any:
    if isinstance(valor, bool):
        return "sí" if valor else "no"
    if isinstance(valor, (list, tuple)):
        return "; ".join(str(item) for item in valor)
    if valor is None:
        return ""
    return valor


def leer_json(ruta: Path) -> Any:
    return json.loads(ruta.read_text(encoding="utf-8"))


def escribir_json(ruta: Path, valor: Any, compacto: bool = True) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    if compacto:
        texto = json.dumps(valor, ensure_ascii=False, separators=(",", ":"))
    else:
        texto = json.dumps(valor, ensure_ascii=False, indent=2)
    ruta.write_text(texto + "\n", encoding="utf-8", newline="\n")


def sin_acentos(texto: str) -> str:
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()


def clave_texto(texto: str) -> str:
    """Clave de comparación: minúsculas, sin acentos ni signos."""
    limpio = re.sub(r"[^a-z0-9 ]", " ", sin_acentos(texto).lower())
    return re.sub(r"\s+", " ", limpio).strip()


def clave_laxa(texto: str) -> str:
    """Clave tolerante a numerales romanos, artículos y espacios."""
    limpio = clave_texto(texto)
    limpio = re.sub(r"\b(i|ii|iii|iv|v|la|las|el|los|de|del|punto)\b", " ", limpio)
    return re.sub(r"\s+", "", limpio)


def normalizar_url(url: str) -> str:
    url = (url or "").strip().lower()
    if not url.startswith("http"):
        return ""
    url = re.sub(r"^https?://(www\.)?", "", url)
    url = url.split("#")[0].rstrip("/")
    return url


def anios(texto: str) -> tuple[int | None, int | None]:
    encontrados = [int(valor) for valor in re.findall(r"(?<!\d)(1[89]\d\d|20[0-3]\d)(?!\d)", texto or "")]
    if not encontrados:
        return None, None
    return min(encontrados), max(encontrados)


def sha256_archivo(ruta: Path) -> str:
    resumen = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            resumen.update(bloque)
    return resumen.hexdigest()


def tamano_legible(bytes_: int | None) -> str:
    if not bytes_:
        return ""
    valor = float(bytes_)
    for unidad in ("B", "KB", "MB", "GB"):
        if valor < 1024 or unidad == "GB":
            return f"{valor:.0f} {unidad}" if unidad == "B" else f"{valor:.1f} {unidad}"
        valor /= 1024
    return ""


def numero(valor: Any) -> float | None:
    if valor is None or valor == "":
        return None
    try:
        resultado = float(str(valor).replace(",", "."))
    except ValueError:
        return None
    return resultado if resultado == resultado else None


def dentro_de_guatemala(lon: float, lat: float) -> bool:
    oeste, sur, este, norte = BBOX_GT
    return oeste <= lon <= este and sur <= lat <= norte
