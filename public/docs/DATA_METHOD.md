# Método de datos y procedencia

Fecha de corte: 21 de octubre de 2026.

## Principio rector

El MVP distingue dos entidades:

- **Fuente hídrica:** río, lago, estación, pozo, nacimiento o punto de muestreo.
- **Fuente de datos:** institución, publicación, archivo o conjunto de datos que aporta evidencia.

Una fuente de datos puede aparecer en la biblioteca sin aparecer en el mapa. Solo se crea un elemento cartográfico cuando el archivo aporta coordenadas publicadas y plausibles para Guatemala.

## Cadena de transformación

1. `Ghagpt/inventories/archivos_descargados.csv` define la lista canónica de 75 archivos descargados.
2. `Ghagpt/inventories/inventario_maestro.csv` aporta institución, procedencia, cobertura, licencia y estado de acceso.
3. `scripts/build_data.py` copia cada archivo a `fuente_de_datos/` sin modificar el original.
4. La copia conserva su nombre. El manifiesto relaciona ruta original, copia, institución, URL y SHA-256.
5. El script vuelve a calcular SHA-256 y registra el resultado en `verification/copy_integrity.json`.
6. El inicio de la aplicación carga metadatos JSON ligeros. Los archivos fuente se abren solo cuando la persona los solicita.

## Normalización cartográfica

El GeoJSON inicial contiene 155 elementos:

- Puntos de calidad de agua de INSIVUMEH 2023 con latitud y longitud explícitas.
- Puntos de monitoreo de INSIVUMEH 2024 tomados de la hoja `Base`, con latitud y longitud explícitas.
- Una ubicación del Water Quality Portal para el lago de Atitlán. El proveedor marca como desconocidos el método y el datum horizontal; la ficha conserva esa advertencia.
- Tres celdas de consulta NASA POWER para Las Vacas, Motagua medio y la desembocadura. Son datos meteorológicos modelados, no estaciones hidrométricas ni mediciones de calidad de agua.

Los valores `x/y` de AMSCLAE y AMSA no se transformaron en esta versión porque el inventario no documenta de forma completa el sistema de referencia en todos los archivos. Esta decisión evita suponer un datum o zona. Los recursos siguen disponibles en la biblioteca.

## Series y resúmenes

- NASA POWER: el script omite el encabezado de metadatos, conserva los registros diarios y calcula precipitación anual descriptiva para la mini gráfica.
- UVG/Zenodo: calcula el promedio descriptivo anual de oxígeno disuelto entre observaciones disponibles. No corrige por profundidad, campaña o estacionalidad; la etiqueta lo declara.
- MSPAS 2024: suma muestras dentro y fuera del rango reportado por la fuente. No cambia la definición institucional.
- INSIVUMEH: agrupa filas por punto y coordenada para formar una ficha con parámetros y una muestra de valores disponibles.

## Carga y desempeño

La página inicial no abre los 75 archivos ni el ZIP de GEMStat. Carga cuatro archivos normalizados pequeños:

- catálogo;
- resumen;
- selección de 12 conjuntos;
- GeoJSON de elementos cartográficos.

Los PDF, XLSX, CSV, JSON, R y ZIP se abren o descargan bajo demanda. El mapa base proviene de OpenFreeMap y OpenStreetMap; la aplicación muestra atribución visible. Los datos normalizados siguen funcionando si el mapa base no está disponible.

## Controles de calidad ejecutados

- Recuento exacto de 75 archivos.
- Existencia de cada ruta original.
- Coincidencia SHA-256 entre original inventariado y copia.
- Validación de que los puntos tengan coordenadas numéricas.
- Build de TypeScript y Vite.
- Pruebas de búsqueda, filtros y estados vacíos.
- Revisión visual en escritorio y móvil.

## Limitaciones

- Una fila puede representar una muestra, parámetro, mes o unidad administrativa; no se suman como si fueran observaciones equivalentes.
- La cobertura temporal no implica frecuencia continua.
- Un dato modelado no se presenta como medición de campo.
- Los límites de cuenca, departamento y municipio provienen del mapa base cuando están disponibles; el MVP no incorpora todavía geometrías administrativas locales.
- La validación de enlaces externos registra respuesta HTTP, pero una respuesta exitosa no garantiza estabilidad futura ni licencia de redistribución.
