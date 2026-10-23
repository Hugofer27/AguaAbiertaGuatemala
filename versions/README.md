# Versiones de investigación

Este directorio conserva como instantáneas separadas el trabajo previo de los agentes Claude y Antigravity. Se mantienen sus nombres de archivo, informes, inventarios y scripts para poder comparar enfoques y reutilizar resultados sin confundirlos con la aplicación integrada de `src/`.

## Claude

`claude/` incluye los entregables de inventario, datos procesados, scripts de adquisición y compilación, manifiestos con SHA-256, registros de búsqueda, presentación e informes. La copia local original se encontraba en `Investigación Claude`.

No se incluyen los archivos de `02_datos_originales/`: la carpeta pesa aproximadamente 1.72 GB y contiene archivos individuales de hasta 483 MB, por encima del límite de GitHub. `05_manifiesto/` conserva las rutas, tamaños y hashes necesarios para identificarlos.

## Antigravity

`antigravity/` incluye los prototipos HTML del dashboard, datos procesados, inventarios, scripts reproducibles, manifiestos e informes. La copia local original se encontraba en `Investigación Antigravity`.

No se incluyen los archivos de `data/raw/`, que son copias descargadas de fuentes externas y ocupan aproximadamente 158 MB. Los datos procesados y los manifiestos sí se conservan.

## Codex

`codex/` conserva el MVP 0.1 que antes estaba en la raíz: metadatos normalizados (`data/`), scripts de compilación (`scripts/build_data.py`, que leía la carpeta local `Ghagpt/`), el catálogo HTML/PDF y su documentación de método.

## Uso en la versión 1.0

Estas carpetas son la **entrada** de `pipeline/construir_datos.py`, que genera la carpeta pública `datos/`. La aplicación mantenida está en la raíz del repositorio (`src/`). El destino final de estas carpetas está pendiente de decisión.
