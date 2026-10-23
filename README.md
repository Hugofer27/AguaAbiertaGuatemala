# Agua Abierta Guatemala

Catálogo y atlas abierto de los datos públicos sobre el agua en Guatemala: quién mide qué, dónde, desde cuándo y dónde conseguirlo.

**Sitio web:** https://hugofer27.github.io/AguaAbiertaGuatemala/ (se publica solo desde la rama `main`).

| | |
|---|---|
| Fuentes | 643 conjuntos de datos, documentos y portales de 85 instituciones |
| Publicaciones | 1 494 artículos, tesis e informes (1 199 de acceso abierto) |
| Datos faltantes | 42 registros con el motivo y cómo pedirlos por la LAIP |
| Mapa | 14 capas y 796 puntos, cada uno con la precisión de su ubicación |
| Mediciones | 3 632 valores de 39 parámetros, con unidad, fecha y fuente |
| Originales | 342 archivos (~2 GB) verificados con SHA-256 |

Datos al 22 de octubre de 2026. El portal muestra valores con su procedencia y no califica la calidad del agua.

## Usar los datos sin la web

Todo está en la carpeta [`datos/`](datos/), en CSV y GeoJSON. El diccionario de columnas está en [`datos/LEEME.md`](datos/LEEME.md).

```python
import pandas as pd, geopandas as gpd
mediciones = pd.read_csv("datos/mediciones/mediciones.csv")
puntos = gpd.read_file("datos/capas/monitoreo_insivumeh.geojson")
```

```r
library(readr); library(sf)
fuentes <- read_csv("datos/catalogo/fuentes.csv")
cuencas <- st_read("datos/capas/cuencas.geojson")
```

En Excel, abra cualquier CSV. En QGIS, arrastre los `.geojson`.

## Ejecutar el sitio en su computadora

Requiere [Node.js](https://nodejs.org/) 20 o posterior.

- **Windows:** doble clic en `ABRIR_DASHBOARD.cmd`.
- **Cualquier sistema:**

```bash
npm install
npm run dev        # http://localhost:5173/
```

Comandos útiles:

| Comando | Qué hace |
|---|---|
| `npm test` | Pruebas de la interfaz y de la carpeta `datos/` |
| `npm run build` | Construye el sitio en `dist/` (incluye `dist/datos/`) |
| `npm run preview` | Sirve `dist/` en http://127.0.0.1:4173/ |
| `npm run datos` | Regenera y verifica `datos/` (requiere Python 3.10+) |

## Cómo está organizado

```
datos/        Carpeta pública: catálogo, capas, mediciones y manifiesto (lo que usa la web)
pipeline/     Python sin dependencias externas
  construir_datos.py       versions/ → datos/
  verificar_datos.py       controles de calidad (los corre la publicación)
  empaquetar_originales.py arma el paquete de archivos originales para Drive
  equivalencias.csv        equivalencias de IDs revisadas a mano
src/          Aplicación web (React + TypeScript + MapLibre)
  capas.ts                 colores, grupos y enfoques del mapa
  textos.ts                textos compartidos de la interfaz
docs/         metodo.md y hoja_de_ruta.md
versions/     Material de las búsquedas de origen (entrada del pipeline)
```

### Agregar o cambiar datos

1. Modifique `pipeline/construir_datos.py`. Para una capa nueva, cree un método en la clase `Constructor` siguiendo el patrón de las existentes.
2. Si es una capa, agregue su color en `src/capas.ts`.
3. Ejecute `npm run datos` y luego `npm test`.

La publicación vuelve a generar `datos/` y falla si no coincide con lo subido. Así, la web y los archivos descargables nunca quedan desfasados.

## Archivos originales (Drive)

Los ~2 GB de originales no caben en GitHub. Para armar el paquete desde las carpetas de investigación de su computadora:

```bash
python pipeline/empaquetar_originales.py --buscar "RUTA/Investigación Claude" --buscar "RUTA/Ghagpt" --buscar "RUTA/Investigación Antigravity" --zip
```

1. El script verifica cada archivo contra su SHA-256 y crea `originales/` y `AguaAbiertaGT_originales.zip`, con un informe de lo que faltó.
2. Suba la carpeta o el ZIP a Drive y compártalo con "Cualquier persona con el enlace".
3. Pegue ese enlace en `datos/config.json` (`enlace_originales`). Desde ahí, las fichas muestran el botón **Copia de respaldo**.

## Publicación

El flujo [`.github/workflows/pages.yml`](.github/workflows/pages.yml) verifica los datos, corre las pruebas y construye el sitio en cada push. En `main` además publica en GitHub Pages. También genera dos descargas:

- `descargas/agua-abierta-guatemala-datos.zip`, con la carpeta de datos;
- `descargas/agua-abierta-guatemala-sitio.zip`, con el sitio para usar sin internet.

**Activación (una sola vez):** en el repositorio, *Settings → Pages → Build and deployment → Source: GitHub Actions*.

## Método y límites

Vea [`docs/metodo.md`](docs/metodo.md). En resumen:

- Solo se mapean coordenadas defendibles y cada punto declara su precisión.
- Se excluyeron 81 ubicaciones que no cumplían ese criterio.
- Los valores son campañas con fecha, no datos en tiempo real.
- Un dato modelado nunca se presenta como medición.

Los próximos pasos, incluida la comparación con COGUANOR NTG 29001, NOM-127-SSA1-2021 y las guías de la OMS, están en [`docs/hoja_de_ruta.md`](docs/hoja_de_ruta.md).

## Cómo citar

> Agua Abierta Guatemala (2026). Catálogo y atlas de datos públicos sobre el agua en Guatemala, versión 1.0. https://hugofer27.github.io/AguaAbiertaGuatemala/

Cada conjunto de datos conserva la licencia de su institución. Revise la columna `licencia` de `datos/catalogo/fuentes.csv` antes de redistribuir un archivo.
