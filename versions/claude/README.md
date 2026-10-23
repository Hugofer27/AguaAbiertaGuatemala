# RÍOS ABIERTOS GT — Inventario de datos de agua de Guatemala (investigación de Claude)

Carpeta de resultados de Claude (Opus 5.5) para el reto de descubrimiento y adquisición de datos de agua de Guatemala. Fecha de ejecución: 21 de octubre de 2026.

## Qué hay en cada carpeta

| Carpeta | Contenido |
|---|---|
| `INFORME_FINAL.md` | Informe ejecutivo en español (entregable D). |
| `01_inventario/` | Entregables A, B y C: inventario maestro, resumen por organización, publicaciones, datos faltantes y duplicados (CSV y `inventario_rios_abiertos_gt.xlsx`). |
| `01_inventario/manual/` | Registros curados a mano en JSONL (fuentes verificadas una por una) y registro de faltantes. |
| `01_inventario/auto/` | Resultados crudos de APIs y cosechas OAI-PMH, antes de filtrar y deduplicar. |
| `02_datos_originales/` | Archivos originales descargados, sin modificar, organizados por organización. |
| `03_datos_procesados/` | Productos derivados (extracto GEMStat de cuencas compartidas, plantas HydroWASTE de Guatemala). Nunca se mezclan con los originales. |
| `04_scripts/` | Scripts de descarga, descubrimiento y compilación (Python 3.12). |
| `05_manifiesto/` | `lista_descargas.csv` (entrada), manifiestos con SHA-256, `manifest.json` y `checksums_sha256.txt`. |
| `06_registro_busquedas/` | Registro de consultas (incluidas las que no dieron resultados), listados WordPress, títulos extraídos y logs. |

## Cómo se hizo

1. **GEMStat local**: se revisó `../GFQA_v3.zip` completo (`01_gemstat_guatemala.py`, `02_gemstat_transfronterizo.py`).
2. **Descubrimiento por API** (`03_descubrimiento_apis.py`): OpenAlex, DataCite, Zenodo, HDX, Harvard Dataverse, Figshare y PANGAEA, con filtros de lugar (Guatemala y sus cuencas) y tema (agua).
3. **Sitios gubernamentales**: enumeración de documentos con la API REST pública de WordPress (`util_wp_media.py`) y extracción de enlaces (`util_enlaces.py`) en INSIVUMEH, AMSCLAE, AMSA, ICC, IARNA-URL, Selva Maya y UVG.
4. **Descargas** (`04_descargar.py`): lista explícita en `05_manifiesto/lista_descargas.csv`; guarda HTTP, tamaño y SHA-256; no reintenta evadir bloqueos.
5. **Fuentes internacionales por API** (`05_internacional_apis.py`): Banco Mundial, ODS de la ONU, HydroWASTE, WPdx, OpenStreetMap (Overpass), DesInventar y NOAA GHCN-Daily.
6. **Repositorios universitarios** (`06_oai_repositorios.py`): cosecha OAI-PMH de USAC (EPrints), UVG (DSpace) y portal de revistas USAC (OJS).
7. **Capas SIG** (`07_arcgis_capas.py`): capas públicas del MARN en ArcGIS Online descargadas como GeoJSON y búsqueda de ítems públicos sobre agua en Guatemala.
8. **Portales CKAN** (`08_ckan_portales.py`): AmeriGEOSS, World Bank Water Data, BID, SE-CONRED y SEGEPLAN.
9. **Compilación** (`09_compilar_inventario.py`): une registros manuales, manifiestos y resultados automáticos; aplica filtros de relevancia, deduplica por DOI, URL y título; verifica URLs (HTTP) y genera las tablas.
10. **Adenda del 22-oct-2026, portal del INE** (`11_ine_recursos_hidricos.py`): agrega a la lista de descargas los 37 archivos de los conjuntos "Recurso(s) Hídrico(s)" 2022-2024 de `datos.ine.gob.gt` (CC BY), hallados por Codex. Se descargan con `04_descargar.py --solo-nuevas`, que no reintenta las URL que ya están en el manifiesto. Sus registros van en `01_inventario/manual/adenda_*.jsonl`, y el compilador les asigna los ID al final (GT-DAT-0210 a GT-DAT-0246), así los ID publicados el 21-oct no cambian.

## Reproducir

```bash
python -m venv venv
venv/Scripts/pip install pandas requests openpyxl pypdf pyshp
venv/Scripts/python 04_scripts/04_descargar.py "<ruta a Investigación Claude>"
venv/Scripts/python 04_scripts/09_compilar_inventario.py "<ruta a Investigación Claude>"
```

Los demás scripts se ejecutan igual, con la ruta raíz como primer argumento (ver el encabezado de cada script).

## Reglas seguidas

- Solo se descargaron archivos públicos sin autenticación. Los sitios con Cloudflare, inicio de sesión o CAPTCHA se registraron como inaccesibles; no se intentó evadirlos.
- No se descargaron artículos con derechos de autor de editoriales; de las publicaciones se guardan metadatos y enlaces legales.
- "Descargado" significa que el archivo original está en `02_datos_originales`. Un registro con solo metadatos o página de aterrizaje no cuenta como descarga.
- Los años marcados "(publicación)" son años de publicación, no de muestreo.
- Los campos de la tabla de publicaciones marcados "inferido" o "No determinado" vienen de reglas automáticas sobre el resumen y deben confirmarse leyendo el texto.

## Limitaciones conocidas

- La cosecha OAI del repositorio de la USAC se interrumpió por un XML mal formado después de 6 882 registros; el resto del repositorio no se revisó por esa vía.
- Las búsquedas de OpenAlex revisan hasta 400 resultados por consulta; algunas páginas fallaron por límite de tasa (ver `06_registro_busquedas/log_apis_*.csv`).
- Google Scholar no se consultó de forma automatizada porque sus condiciones de uso lo prohíben.
- El filtro de relevancia de los canales automáticos es por palabras clave; puede quedar algún falso positivo y algún falso negativo.
