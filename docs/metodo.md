# Método

Este documento explica de dónde vienen los datos de Agua Abierta Guatemala, cómo se unificaron y qué controles se aplicaron. Fecha de corte: 22 de octubre de 2026.

## 1. De dónde vienen los datos

Entre el 21 y el 22 de octubre de 2026 se hicieron tres búsquedas independientes de datos públicos sobre el agua en Guatemala, con prioridad en la cuenca del Motagua y el río Las Vacas. Cada búsqueda dejó su inventario, sus manifiestos con SHA-256 y sus scripts. Esos materiales se conservan en `versions/` como entrada del pipeline.

Se cubrieron estos canales:

- **Portales oficiales:** INE (`datos.ine.gob.gt`, conjuntos "Recursos Hídricos" 2022-2024), INSIVUMEH, MARN, AMSA, AMSCLAE, ICC, IARNA-URL, BANGUAT, SEGEPLAN y SE-CONRED. En los sitios WordPress se usó su API pública.
- **Repositorios científicos por API:** OpenAlex, Crossref, DataCite, Zenodo, Figshare, Harvard Dataverse, PANGAEA y HDX.
- **Repositorios universitarios por OAI-PMH:** USAC (EPrints y revistas OJS) y UVG (DSpace).
- **Capas SIG:** servicios públicos del MARN en ArcGIS Online (cuencas, lagos, ríos, límites, sitios de monitoreo) y búsqueda de ítems públicos sobre agua.
- **Bases internacionales:** GEMStat (PNUMA), Banco Mundial, ODS de la ONU, HydroWASTE, HydroSHEDS, WPdx, OpenStreetMap, DesInventar, NOAA GHCN, NASA POWER y Water Quality Portal.

Reglas que se siguieron:

- Solo se descargaron archivos públicos sin autenticación.
- Los sitios con Cloudflare, inicio de sesión o CAPTCHA se registraron como inaccesibles, sin intentar evadirlos.
- De las publicaciones con derechos de autor se guardan metadatos y enlaces legales, no el texto.

## 2. Unificación del catálogo

`pipeline/construir_datos.py` une los tres inventarios. Un mismo recurso hallado más de una vez se reconoce, en este orden:

1. por la **huella SHA-256** del archivo descargado;
2. por la **URL normalizada** de descarga o de la página oficial (incluida la URL o DOI de las publicaciones);
3. por una **tabla de equivalencias revisada a mano** (`pipeline/equivalencias.csv`) para los casos que no se pueden resolver de forma automática: el mismo indicador en dos formatos, la misma tesis con distinta URL, etc.

El identificador canónico es el del inventario más amplio (GT-DAT, GT-DOC, GT-POR, GT-PUB). Los demás se conservan en `ids_alias`, de modo que cualquier referencia anterior sigue siendo válida; el buscador del portal también los encuentra.

Resultado: 84 identificadores unificados y 21 registros que solo aparecían en una búsqueda y se agregaron. El catálogo final tiene 643 fuentes (260 conjuntos de datos, 228 documentos y 155 portales) y 1 494 publicaciones.

## 3. Qué aparece en el mapa

Un lugar solo se dibuja si tiene una coordenada defendible. Cada punto declara la precisión de su ubicación:

- **Publicada.** La coordenada viene de la fuente. Ejemplos: los puntos de monitoreo del INSIVUMEH en las bases del INE 2023 y 2024, los sitios de acidificación del MARN y las estaciones de WPdx.
- **Por punto homónimo.** La base de caudales del INE 2022 no trae coordenadas. Cada estación se ubica en el punto de monitoreo del INSIVUMEH que tiene el mismo nombre y un municipio compatible. Si hay más de un candidato, o si el nombre casi igual corresponde a otra estación de la misma base (por ejemplo, Matacuy y Matucuy), no se ubica.
- **Transcrita.** Coordenadas copiadas de las tablas de un documento, como los 32 sitios de la tesis USAC-ERIS 2025 sobre Las Vacas.
- **Modelada.** Celdas de NASA POWER, tramos de HydroRIVERS y desembocaduras del modelo de plásticos.

Exclusiones documentadas en `datos/resumen.json`:

- **70 desembocaduras del modelo global de plásticos** (Meijer et al., 2021) que estaban rotuladas como guatemaltecas, pero caen en Belice, Honduras, El Salvador o México. Se conservan solo las que están dentro de las cuencas de Guatemala o a menos de 3 km de su costa.
- **5 puntos de calidad 2022** sin un punto equivalente con coordenada publicada.
- **6 estaciones de caudal** sin un punto homónimo con coordenada publicada, entre ellas Matacuy.
- **Las estaciones de AMSA y AMSCLAE.** Sus archivos usan coordenadas x/y sin un sistema de referencia documentado. Se mantienen en el catálogo y quedan en la hoja de ruta.
- **Ubicaciones aproximadas por centroide municipal**, y **valores de laboratorio que no se pudieron rastrear a una fuente**.

## 4. Mediciones

Las mediciones se guardan en formato largo (`datos/mediciones/mediciones.csv`): sitio, parámetro, código armonizado, valor, unidad, fecha y fuente. Este formato sigue la recomendación de modelos como WaterML 2.0 y ODM2 y facilita comparar con normas.

- **INSIVUMEH 2022.** De la base del INE se toma el último registro por variable y punto; la fecha exacta de muestreo no se conservó en la extracción. El archivo no declara las unidades, así que se usa la unidad habitual del parámetro y la medición queda marcada con `unidad_verificada = no`.
- **INSIVUMEH 2023 y 2024.** Los valores incluidos en la normalización de las bases del INE, con la unidad declarada en el nombre de cada columna.
- **Caudales.** Caudal medio mensual 2022 en m³/s.

## 5. Controles de calidad

`pipeline/verificar_datos.py` se ejecuta en cada publicación y detiene el proceso si encuentra:

- identificadores repetidos o alias que apunten a un registro inexistente;
- puntos fuera de Guatemala (salvo la capa de contexto regional de GEMStat), sin precisión de ubicación o sin fuente;
- mediciones de sitios inexistentes o con una fuente desconocida;
- huellas SHA-256 inválidas o repetidas en el manifiesto de originales.

Además, el oxígeno disuelto se compara con la concentración de saturación en agua dulce a 1 atm, calculada con la ecuación de Benson y Krause (APHA 4500-O). Se marca para revisión si:

- supera el 140 % de la saturación a la temperatura medida, o
- coincide exactamente, con tres o más decimales, con otro parámetro del mismo sitio y fecha.

Esto último ocurrió en un sitio de la tesis USAC-ERIS: un oxígeno disuelto de 14,894 mg/L a 25 °C coincide con el valor de sulfadiazina, lo que indica un probable error de transcripción. El valor se conserva con la marca y no se borra.

## 6. Archivos originales

Los ~2 GB de archivos originales no se guardan en Git. `datos/manifiesto/originales.csv` registra los 342 archivos únicos con su URL de origen, tamaño y SHA-256. `pipeline/empaquetar_originales.py` los reúne desde las carpetas locales de investigación, verifica cada huella y arma una carpeta o un ZIP para publicarlo en Drive o en otro almacenamiento.

## 7. Limitaciones

- Se hizo una búsqueda amplia, pero no se garantiza que sea exhaustiva. No encontrar un dato no prueba que no exista.
- La clasificación por tema es automática, por palabras clave del título, y puede tener errores.
- La cobertura temporal de un conjunto no implica que la frecuencia de medición sea continua.
- Las cuencas se simplificaron para la web (tolerancia de ~130 m). Para análisis espacial fino, use la capa original del MARN.
- Una respuesta HTTP correcta al 22-oct-2026 no garantiza que el enlace siga estable ni que el archivo pueda redistribuirse.
