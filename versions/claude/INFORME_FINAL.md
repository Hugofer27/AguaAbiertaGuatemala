# RÍOS ABIERTOS GT — Informe de descubrimiento y adquisición de datos de agua de Guatemala

**Investigación de Claude (Opus 5.5) · 21 de octubre de 2026; actualizada el 22 de octubre de 2026, 08:18, con las 37 bases del INE (sección 14).** Los identificadores entre paréntesis (GT-…) remiten a `01_inventario/inventario_maestro.csv`; las cifras globales salen de `01_inventario/estadisticas_inventario.json`.

## 1. Resumen ejecutivo

Guatemala sí mide su agua, pero casi nada de lo que mide es abierto. Se identificaron **2 116 recursos únicos** sobre agua en Guatemala. De ellos, 300 archivos originales (1,80 GB) se descargaron y verificaron con SHA-256. Los datos crudos más valiosos no vienen del Estado central sino de autoridades de lago y de centros de investigación:

- **AMSA:** base de 1 607 muestras del Lago de Amatitlán y 8 ríos tributarios, 2018-2024, con más de 50 parámetros, incluidos metales y microcistinas (GT-DAT-0006).
- **UVG y AMSCLAE:** perfiles mensuales del Lago de Atitlán 2010-2024, con 30 826 filas y licencia CC BY 4.0 (GT-DAT-0038).
- **ICC:** caudales semanales de la temporada seca en hasta 77 ríos de la costa sur, 2017-2026 (GT-DOC-0079…0084).

La base nacional de calidad de agua del MARN existe, pero está bloqueada. El Sistema de Información Ambiental declara un servicio `Calidad_Agua_DINA_monitoreos`, y el servidor que lo aloja rechaza todo acceso automatizado; en el navegador los indicadores no cargan (GT-POR-0012).

Para la cuenca del Motagua y el Río Las Vacas no hay series públicas. Solo hay informes puntuales de la USAC (GT-DOC-0137, -0144, -0181, -0187), comunicados de ONG y un incidente de coloración roja del Las Vacas en septiembre de 2026 (GT-DOC-0210).

## 2. Organizaciones investigadas

Se investigaron de forma dirigida **69 organizaciones**: 60 con recursos en el registro manual (incluida la adenda del INE) y 29 en el registro de faltantes, con solapamiento entre ambos. Algunos grupos cuentan como una sola, por ejemplo "Universidad Rafael Landívar y Universidad Galileo". El inventario contiene además recursos de 178 organizaciones o editores no bibliográficos, encontrados por APIs y cosechas OAI-PMH.

## 3-6. Cifras principales

| Indicador | Valor |
|---|---:|
| Recursos únicos en el inventario | 2 116 |
| Datasets únicos | 246 |
| Datasets con datos descargados (archivo o API) | 77 |
| Recursos con al menos un archivo descargado | 276 |
| Archivos descargados (originales) | 300 (1,80 GB) |
| Descargas fallidas documentadas | 28 |
| Documentos e informes técnicos | 221 |
| Portales y servicios | 155 |
| Publicaciones científicas, tesis e informes académicos | 1 494 (1 199 en acceso abierto) |
| Duplicados detectados y excluidos | 347 |
| Registros de datos faltantes o inaccesibles | 34 |

Las 1 494 publicaciones incluyen 769 tesis (sobre todo de los repositorios de la USAC y la UVG) y 597 artículos.

## 7. Cobertura histórica

- **1856-1882:** primeras mediciones de lluvia en la Ciudad de Guatemala (GT-DAT-0089).
- **1905-2015:** 7 588 fichas de desastres, de las cuales 1 571 son inundaciones (DesInventar, GT-DAT-0021).
- **Desde 1961:** indicadores del Banco Mundial (GT-DAT-0015).
- **2012-2021:** GEMStat, pero solo en estaciones mexicanas de cuencas compartidas (GT-DAT-0001).
- **2013-2025:** monitoreo del Lago de Atitlán (AMSCLAE, GT-DOC-0001…).
- **2017-2026:** caudales de la costa sur (ICC).

Las series hidrométricas del INSIVUMEH empiezan en 1962, pero solo se publican boletines recientes y, en el portal del INE, el caudal medio mensual de 2022 a 2024 (GT-DAT-0002; bases del INE: GT-DAT-0217, -0223 y -0237).

## 8. Distribución por tipo de fuente

| Tipo de fuente | Recursos |
|---|---:|
| Universidades (USAC, UVG, IARNA-URL) | 920 |
| Publicaciones científicas | 651 |
| Plataformas SIG | 210 |
| Gobierno de Guatemala | 174 |
| Internacionales | 55 |
| Repositorios de datos | 49 |
| ONG y sector privado | 40 |
| Satelitales y globales | 12 |
| Prensa o investigación periodística | 3 |

## 9. Fuentes más valiosas

1. **AMSA, base de control ambiental:** mediciones crudas 2018-2024 con coordenadas (GT-DAT-0006). También hay datos de clima, descargas industriales y residuos sólidos (GT-DAT-0007…).
2. **UVG/AGLGL, Atitlán 2010-2024 en Zenodo:** perfiles de 0 a 315 m de temperatura, oxígeno y nutrientes (GT-DAT-0038).
3. **AMSCLAE, informes DICA 2015-2025:** limnología, ríos, PTAR, caudales, nivel del lago, agua de consumo y playas; 49 PDF descargados.
4. **ICC, Sistema de Información de Ríos de la Costa Sur:** caudales 2017-2026 (GT-DOC-0079…0084) y red meteorológica de hasta 38 estaciones (GT-DOC-0085…0089).
5. **Capas SIG MAGA/IGN/MARN:** 20 capas descargadas en GeoJSON. Incluyen 10 934 tramos de río, 38 cuencas, 313 subcuencas, 2 391 microcuencas, 1 660 fuentes de agua y amenaza de inundación costera (GT-DAT-0039…0058).
6. **INSIVUMEH:** boletines hidrológicos, boletín de calidad del agua, índices de contaminación y 64 estaciones con coordenadas extraídas (GT-DAT-0002 a -0004, GT-DOC-0050/51).
7. **DIGI-USAC:** 62 informes descargados. Cubren Motagua (2003, 2008, 2024), Las Vacas (2021), Izabal, Atitlán, Petén Itzá, acuíferos volcánicos y agua subterránea.
8. **Repositorios USAC y UVG:** 844 tesis y artículos sobre agua, con metadatos obtenidos por OAI-PMH.
9. **IARNA-URL:** balance hidrológico por subcuenca (GT-DOC-0116) y 8 mapas hídricos nacionales.
10. **BANGUAT SCAE:** cuenta de agua 2013-2024 (GT-DAT-0013).
11. **WPdx:** 1 908 puntos de agua rurales, 2013-2021 (GT-DAT-0019).
12. **DesInventar:** inundaciones y otros eventos 1905-2015 (GT-DAT-0021).
13. **ODS 6 de la ONU:** 40 series, incluida calidad de lagos por satélite (GT-DAT-0016).
14. **GEMStat:** 394 823 registros de cuencas compartidas con México (GT-DAT-0001).
15. **Productos globales para llenar vacíos:** CHIRPS, GloFAS y Sentinel-2 (GT-DAT-0028, -0031, -0034).
16. **INE, "Recursos Hídricos" 2022-2024:** 37 bases oficiales con licencia CC BY. Incluyen vigilancia del MSPAS, caudal mensual y calidad del INSIVUMEH, calidad de Amatitlán (AMSA), limnología de Atitlán (AMSCLAE) y producción de EMPAGUA (GT-DAT-0210…0246; hallazgo de Codex, sección 14).

## 10. Vacíos de información importantes

- **Calidad de agua nacional:** existe en el MARN (82 puntos ISQA en 2024 según prensa) pero no es accesible (GT-POR-0012).
- **Caudales históricos:** no hay series diarias públicas de las estaciones del INSIVUMEH, incluida Gualán en el Motagua. El portal del INE (`datos.ine.gob.gt`) solo publica el caudal medio mensual por estación de 2022 a 2024, con Concuá II, Gualán y Morales en el Motagua (corrección del 22-oct-2026; hallazgo de Codex; en el inventario como GT-DAT-0217, -0223 y -0237).
- **Motagua y Las Vacas:** no hay monitoreo continuo publicado. El diagnóstico transfronterizo del proyecto PNUD/FMAM (GT-DOC-0197), los resultados de metales de UICN-MAR2R y el estudio de 2026 de la Alianza no se localizaron.
- **Agua potable:** la vigilancia del MSPAS (unos 12 500 sistemas) solo está publicada como totales anuales 2022-2024 en el portal del INE: por sistema en 2022-2023 y por municipio en 2024. No hay resultados por muestra ni años anteriores (GT-POR-0014; corrección del 22-oct-2026, hallazgo de Codex; las bases están en el inventario dentro de GT-DAT-0210…0246).
- **Infraestructura:** no hay inventario nacional de PTAR ni de vertederos. HydroWASTE solo registra 8 plantas en Guatemala (GT-DAT-0018).
- **Agua subterránea:** no hay red pública de niveles ni de calidad de acuíferos.
- **Clima en redes globales:** GHCN-Daily solo contiene 1 estación guatemalteca (GT-DAT-0023).
- **Residuos plásticos:** las cifras de The Ocean Cleanup y 4ocean son agregadas, sin datos abiertos (GT-DOC-0200).

## 11. Por qué faltan recursos esperados

Los 34 casos se agrupan así (`registro_datos_faltantes.csv`):

| Causa | Casos |
|---|---:|
| Datos no publicados | 9 |
| Bloqueo técnico: Cloudflare o 403 (MARN, MSPAS, CONAP, portal SIG del MARN), servidores sin respuesta (IGN, AMPI, AMASURLI, INDE, OpenKM del INSIVUMEH) o archivos con 404 | 10 |
| No localizados | 8 |
| Detrás de registro, solicitud, herramienta específica o política restringida (archivos de CONRED en SharePoint con inicio de sesión, Redatam del censo 2018, GEMStat LIMITED) | 5 |
| Publicados solo en parte: cortes anuales 2022-2024 del MSPAS y del INSIVUMEH en el portal del INE (corregido el 22-oct-2026) | 2 |

Las causas de fondo se repiten:

- Guatemala no tiene una ley de aguas ni una norma de calidad de ríos que obligue a publicar.
- Los sitios web se reestructuran y dejan enlaces rotos: 9 archivos de AMSCLAE aparecen en su API pero devuelven 404, y 7 boletines del INSIVUMEH indexados por buscadores también devuelven 404.
- Los portales de datos abiertos (CONRED, SEGEPLAN) casi no contienen datos de agua.

No encontrar un dato no prueba que no exista.

## 12. Instituciones a contactar

Prioridad alta, mediante solicitudes por la Ley de Acceso a la Información Pública (Decreto 57-2008):

- **MARN-DINA:** exportación de `Calidad_Agua_DINA_monitoreos` y del Informe del Agua 2024.
- **INSIVUMEH:** caudales diarios y boletines del Laboratorio Hidroquímico.
- **MSPAS:** resultados por muestra de la vigilancia de agua de consumo y años anteriores a 2022.
- **AMSCLAE, AMPI y AMASURLI:** bases de laboratorio de sus lagos.
- **EMPAGUA, Municipalidad de Chinautla y Municipalidad de Guatemala:** datos de PTAR y de calidad de fuentes.
- **SE-CONRED:** habilitar el acceso anónimo a sus archivos.

Para acuerdos de datos: PNUD/FMAM Motagua, UICN-CCAD, The Ocean Cleanup, 4ocean, Alianza por la Cuenca del Motagua, ICC, FUNCAGUA y USAC (CEMA, ERIS, DIGI).

## 13. Recomendación técnica para la plataforma

1. **Modelo de datos común:** estaciones, muestras y mediciones en formato largo (estilo WaterML 2.0 / ODM2), con códigos de parámetro y unidades armonizados, más un campo de licencia y procedencia por registro.
2. **Primera carga:**
   - bases oficiales del INE 2022-2024 (GT-DAT-0210…0246), con licencia CC BY;
   - mediciones crudas de AMSA (GT-DAT-0006) y de UVG-Atitlán (GT-DAT-0038);
   - tablas digitalizadas de los informes de AMSCLAE, ICC y DIGI-USAC (Motagua y Las Vacas);
   - capa base de ríos y cuencas del MAGA (GT-DAT-0039…0042).
3. **Pipelines reproducibles:** extracción de PDF con revisión humana, cosecha programada de los sitios WordPress y CKAN, y verificación periódica de URLs con checksums. Los scripts de `04_scripts/` sirven de base.
4. **Capa satelital para la cuenca del Motagua:** CHIRPS (lluvia), GloFAS (caudal modelado) y Sentinel-2 (turbidez y color), para cubrir la falta de estaciones abiertas mientras se gestionan los datos oficiales.
5. **Publicación:** API abierta (por ejemplo, PostgreSQL/PostGIS con pygeoapi o SensorThings) y descarga en CSV y GeoParquet con licencia CC BY 4.0 cuando la fuente lo permita.

## 14. Adenda del 22 de octubre de 2026: bases del INE

Codex encontró el portal `datos.ine.gob.gt`, que Claude no había visto. Tiene tres conjuntos "Recurso(s) Hídrico(s)" (2022, 2023 y 2024) de la Sección de Estadísticas Ambientales del INE, con licencia CC BY. Claude descargó sus 37 archivos (10,3 MB):

| Productor | Archivos |
|---|---:|
| MSPAS | 13 |
| AMSA | 9 |
| AMSCLAE | 8 |
| INSIVUMEH | 6 |
| EMPAGUA | 1 |

Cada archivo se verificó contra la API CKAN del portal y se abrió para registrar filas, cobertura y parámetros. Los 37 son idénticos por SHA-256 a las copias de Codex.

- **Inventario:** son los registros GT-DAT-0210 a GT-DAT-0246 (`01_inventario/manual/adenda_01_ine_recursos_hidricos.jsonl`). Sus ID se asignan al final de la serie para que los ID publicados el 21 de octubre no cambien.
- **Registro de faltantes:** las filas del MSPAS y del INSIVUMEH (Servicios Hídricos) pasaron a "Publicado parcialmente", porque el INE solo publica totales anuales y promedios mensuales. Lo que sigue sin publicarse (resultados por muestra y series diarias) se mantiene como pedido por ley de acceso.
- **Reproducción:**
  1. `04_scripts/11_ine_recursos_hidricos.py`
  2. `04_descargar.py --solo-nuevas`
  3. `09_compilar_inventario.py`
- **Cifras del 21 de octubre, antes de la adenda:** 2 079 recursos, 263 archivos y 1,79 GB.

## Limitaciones

- El inventario de publicaciones se filtró por palabras clave y puede tener falsos positivos residuales.
- La cosecha OAI de la USAC quedó incompleta por un XML mal formado.
- OpenAlex agotó su cuota diaria gratuita, así que algunas páginas de resultados no se revisaron.
- Los años de muestreo de las publicaciones solo se infirieron del resumen (100 casos) y deben confirmarse leyendo el texto completo.
- No se afirma una cobertura exhaustiva del país.
