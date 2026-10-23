# Datos de Agua Abierta Guatemala

Esta carpeta contiene todos los datos del portal en formatos abiertos. Se puede usar sola, sin la aplicación web:

- Los CSV están en UTF-8 (con BOM, para que Excel muestre bien los acentos).
- Los GeoJSON usan WGS 84 (EPSG:4326) y se abren en QGIS, R (`sf`) o Python (`geopandas`).

Fecha de corte: 22 de octubre de 2026 · Versión 1.1.0. La generan `pipeline/construir_datos.py` y `pipeline/verificar_datos.py`. No edite estos archivos a mano: cambie el pipeline y vuelva a ejecutarlo.

## Contenido

| Archivo | Qué contiene |
|---|---|
| `catalogo/fuentes.csv` | 643 conjuntos de datos, documentos y portales, sin duplicados |
| `catalogo/publicaciones.csv` | 1 494 artículos, tesis e informes académicos |
| `catalogo/faltantes.csv` | 42 datos que existen pero no se pudieron obtener, con el motivo y cómo pedirlos |
| `catalogo/organizaciones.csv` | Resumen por institución |
| `catalogo/equivalencias_de_ids.csv` | IDs anteriores que apuntan al mismo registro (alias) |
| `capas/*.geojson` | Una capa por archivo; la lista y su descripción están en `app/capas.json` |
| `mediciones/mediciones.csv` | 3 632 valores en formato largo |
| `mediciones/sitios.csv` | Los 796 puntos del mapa con coordenadas y precisión de ubicación |
| `mediciones/parametros.csv` | Código, nombre, unidad y grupo de cada parámetro |
| `manifiesto/originales.csv` | Los 342 archivos originales con URL de origen, tamaño y SHA-256 |
| `resumen.json` | Recuentos generales y lista de ubicaciones excluidas del mapa |
| `config.json` | Enlace al paquete de archivos originales (Drive u otro) |
| `app/*.json` | Las mismas tablas en JSON compacto para la web |

## `catalogo/fuentes.csv`

| Columna | Descripción |
|---|---|
| `id` | Identificador estable (GT-DAT conjuntos, GT-DOC documentos, GT-POR portales, GTW / GT-H2O otros) |
| `tipo` | Conjunto de datos, Documento o Portal o servicio |
| `titulo`, `institucion`, `institucion_detalle` | Nombre del recurso e institución (corta y completa) |
| `categoria` | Gobierno GT, Universidad, Internacional, Plataforma SIG, etc. |
| `tema` | Clasificación temática automática por palabras clave del título |
| `anios`, `anio_min`, `anio_max` | Años cubiertos (texto original y extremos numéricos) |
| `cobertura`, `parametros`, `formato`, `registros` | Lo que declara la fuente o lo que se verificó en el archivo |
| `licencia` | Licencia declarada. *No indicada* significa que se debe consultar a la institución antes de redistribuir |
| `acceso`, `acceso_detalle` | Público, Público con registro, Restringido o por solicitud, etc. |
| `descarga` | Archivo descargado, Solo metadatos, Portal o servicio, No descargado |
| `archivos`, `sha256` | Número de archivos descargados y sus huellas SHA-256 |
| `url_fuente`, `url_descarga` | Página oficial y enlace directo |
| `verificacion`, `http` | Cómo se verificó y respuesta HTTP del enlace al 22-oct-2026 |
| `motagua_las_vacas` | `sí` si el recurso trata la cuenca del Motagua o el río Las Vacas |
| `destacado`, `prioridad` | Selección editorial (prioridad 1 = más valioso) |
| `ids_alias` | IDs con los que el mismo recurso aparecía en búsquedas anteriores |
| `notas` | Observaciones de verificación |

## `mediciones/mediciones.csv`

Una fila por valor medido. Está pensada para comparar después con normas y guías de calidad del agua: cada valor trae código de parámetro, unidad y fuente.

| Columna | Descripción |
|---|---|
| `sitio_id`, `sitio`, `capa` | Punto del mapa al que pertenece (ver `sitios.csv`) |
| `codigo`, `parametro` | Código armonizado (por ejemplo `OD`, `PH`, `DBO5`, `Q_MENSUAL`) y nombre |
| `parametro_original` | Nombre tal como aparece en el archivo de origen |
| `valor`, `unidad` | Valor numérico y unidad |
| `unidad_verificada` | `no` si la unidad es la habitual del parámetro pero el archivo de origen no la declara en esta extracción |
| `fecha` | Fecha o periodo de la campaña tal como lo publica la fuente |
| `tipo_dato` | Medido, Modelado, etc. |
| `fuente_id` | Registro de `catalogo/fuentes.csv` del que proviene el valor |
| `control` | Aviso de control de calidad (por ejemplo, oxígeno disuelto por encima de la saturación teórica) |
| `nota` | Aclaraciones sobre la extracción |

## Precisión de ubicación (`precision`)

| Valor | Significado |
|---|---|
| `publicada` | La coordenada viene tal cual de la fuente |
| `homonimo` | La fuente no publica la coordenada; se usa la del punto INSIVUMEH con el mismo nombre y municipio |
| `transcrita` | Transcrita de un documento (tesis o informe); conviene verificarla |
| `modelada` | Celda o punto de un modelo, no una estación en terreno |

## Advertencias

- Los valores son campañas puntuales con su fecha. No describen condiciones actuales ni califican la calidad del agua.
- Una fila de `mediciones.csv` puede ser una muestra, un promedio mensual o un valor anual: revise `fecha` y `nota` antes de sumar o promediar.
- Los datos modelados (NASA POWER, HydroRIVERS, emisiones de plástico) no son mediciones en el sitio.
