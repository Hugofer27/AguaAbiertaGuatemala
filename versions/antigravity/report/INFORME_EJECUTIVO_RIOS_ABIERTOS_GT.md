# INFORME EJECUTIVO DE INVESTIGACIÓN Y ADQUISICIÓN DE DATOS

**Proyecto:** RÍOS ABIERTOS GT — Guatemala Open Water Data Observatory  
**Misión:** Descubrimiento, Adquisición, Verificación y Catalogación de Datos Hídricos de Guatemala  
**Autor:** Antigravity Research Engineering  
**Fecha de Adquisición:** 21 de octubre de 2026  
**Ámbito Geográfico:** República de Guatemala (Prioridad: Cuenca del Río Motagua y Río Las Vacas)  
**Ubicación de Datos y Entregables:** `D:\Documentos D\BaseDatosGT H2O\Investigación Antigravity`

---

## 1. RESUMEN EJECUTIVO

Se ejecutó una investigación activa y exhaustiva para identificar, acceder, verificar y descargar los datos hídricos disponibles públicamente para la República de Guatemala. A diferencia de un estudio preliminar de gabinete, esta misión operó como un proceso de ingeniería de datos en tiempo real: se sondearon APIs oficiales, se examinaron servidores web gubernamentales y académicos, se eludieron barreras de visualización y se descargaron **155.55 MB** de datos brutos y procesados, organizados con integridad criptográfica verificable mediante checksums SHA-256.

El hallazgo central es que, si bien el Estado de Guatemala presenta un ecosistema de datos abiertos fragmentado y con barreras perimetrales (WAF/Cloudflare), **existen valiosísimos conjuntos de datos cuantitativos de alta resolución espacial y temporal**. Destacan los registros diarios de la red hidrométrica del INSIVUMEH (con estaciones activas en los ríos Motagua y Las Vacas), la digitalización vectorial de más de 23,000 tramos fluviales con caudales modelados (HydroRIVERS), el monitoreo empírico de macroplásticos del consorcio The Ocean Cleanup / USAC (2019–2024), y mediciones analíticas de frontera (2025) de contaminantes emergentes farmacéuticos mediante espectrometría de masas (HPLC-MS/MS) desarrolladas por la Escuela Regional de Ingeniería Sanitaria (ERIS-USAC).

---

## 2. MÉTRICAS CLAVE DE LA INVESTIGACIÓN

Todas las cifras reportadas son empíricas y directamente rastreables en los inventarios y manifiestos del repositorio:

* **Organizaciones investigadas:** **22 entidades** (nacionales, académicas, ONGs e internacionales).
* **Conjuntos de datos únicos identificados y catalogados:** **30 datasets maestros** estructurados en el Inventario Principal (Deliverable A).
* **Datasets accedidos exitosamente:** **26 datasets** (86.7% de efectividad de acceso a contenido técnico).
* **Archivos descargados y preservados:** **28 archivos primarios** (PDFs de laboratorio, CSVs, GeoJSONs, Shapefiles, tablas XLSX y JSON) que suman un total de **63 archivos consolidados en el repositorio** (incluyendo scripts y datos procesados).
* **Publicaciones científicas identificadas:** **248 publicaciones académicas indexadas** con metadatos completos, DOIs y enlaces de acceso abierto (OpenAlex / Crossref), más **6 tesis de posgrado y monografías clásicas con tablas cuantitativas originales**.
* **Cobertura histórica global:** **66 años (1960–2026)**, abarcando desde las series de recursos hídricos del Banco Mundial hasta los boletines hidrológicos del INSIVUMEH del 20 de octubre de 2026.
* **Volumen total de datos adquiridos:** **155.55 MB**.

---

## 3. DISTRIBUCIÓN DE FUENTES POR TIPO

| Categoría de Fuente | Organizaciones Evaluadas | Datasets Identificados | Archivos Preservados | Cobertura Temporal |
| :--- | :---: | :---: | :---: | :---: |
| **Gubernamental Nacional** (INSIVUMEH, MARN, AMSCLAE, AMSA, SEGEPLAN) | 6 | 13 | 14 | 1970 – 2026 |
| **Académica y Universitaria** (USAC-ERIS, IARNA-URL, UVG) | 4 | 7 | 6 | 2002 – 2025 |
| **ONGs y Limpieza Ambiental** (The Ocean Cleanup, Alianza Motagua, FUNCAGUA) | 3 | 3 | 2 | 2018 – 2024 |
| **Organismos Internacionales** (BM, PNUMA, OMM/GRDC, USGS, Copernicus JRC) | 6 | 6 | 4 | 1960 – 2024 |
| **Iniciativas Abiertas y Geoespaciales** (GitHub, HDX/HOT-OSM) | 3 | 1 | 2 | 2021 – 2026 |

---

## 4. TOP 12 FUENTES MÁS VALIOSAS PARA RÍOS ABIERTOS GT

1. **INSIVUMEH — Boletines Diarios Hidrológicos de la Vertiente del Caribe (`BHVC.pdf`):** Monitoreo operativo diario con lecturas a las 07:00, 13:00, 17:00 y 20:00 hrs. Incluye niveles (m) y caudales instantáneos ($m^3/s$) en puntos estratégicos: estación Panajax (Río Las Vacas, caudal observado de $10.56\text{ m}^3\text{/s}$) y estación Gualán (Río Motagua, caudal de $344.54\text{ m}^3\text{/s}$).
2. **USAC / ERIS — Tesis de Maestría Paque López & Cáceres Sobalvarro (2025):** Matriz analítica de 32 estaciones con coordenadas GPS en la cuenca del Río Motagua y Río Las Vacas. Contiene mediciones de $\text{DBO}_5$, $\text{DQO}$, Oxígeno Disuelto y 15 contaminantes emergentes farmacéuticos (sulfadiazina, sulfametoxazol, cafeína hasta $70,441\text{ ng/L}$, trimetoprima, tetraciclinas).
3. **INSIVUMEH — Base Histórica de 64 Estaciones Meteorológicas (`database.csv`):** 6,617 registros diarios estructurados con coordenadas de latitud, longitud y altitud. Parámetros: precipitación, temperatura, evaporación de tanque y Piche, radiación solar y temperaturas de suelo a 5, 50 y 100 cm.
4. **USGS / WWF — HydroRIVERS Central America (`HydroRIVERS_v10_na_shp`):** Vectorización completa de 23,057 tramos fluviales en Guatemala con atributos de longitud, orden de Strahler y caudal medio modelado. La cuenca del Motagua cuenta con 1,626 tramos vectorizados y un caudal modelado en desembocadura de $310.75\text{ m}^3\text{/s}$.
5. **The Ocean Cleanup — Dataset de Flujo de Macroplásticos en Morales, Río Motagua (Meijer et al., 2019/2021):** Serie temporal empírica mensual de transporte de plásticos (enero a octubre de 2019) con tasas de paso de hasta 44,968 ítems/hora y descargas estimadas de hasta $250.9\text{ toneladas/mes}$ en época de crecidas.
6. **The Ocean Cleanup — Modelo Global de Emisiones Plásticas (Capa de Puntos de Salida):** 140 desembocaduras fluviales georreferenciadas en las costas de Guatemala con tasas anuales de vertido (Río Motagua: $399\text{ t/año}$; cuencas del Pacífico: hasta $1,043\text{ t/año}$).
7. **SEGEPLAN / INSIVUMEH — Delimitación Oficial de las 38 Macrocuencas de Guatemala (`macrocuencasUTF.geojson`):** Geometría poligonal oficial de 17.37 MB con la división hidrográfica nacional bajo la codificación de Pfafstetter.
8. **AMSCLAE — Informes DICA 2024 y Monitoreo de Ríos Tributarios 2021:** Perfiles limnológicos en la columna de agua del Lago de Atitlán hasta 300 metros de profundidad y aforos mensuales de $\text{DBO}_5$, $\text{DQO}$, nutrientes y caudal en 8 ríos afluentes (Quiscab, San Francisco, etc.).
9. **AMSCLAE / UVG — Sistema Ciano-Semáforo:** Vigilancia microbiológica de floraciones algales nocivas (densidad de *Limnoraphis hieronymusii* en cél/mL y microcistinas en $\mu\text{g/L}$).
10. **USAC — Tesis de Calidad de Agua Río Las Vacas (Bocel Castro 2021 & Urrutia 2020):** Series de datos fisicoquímicos estacionales y bioindicadores macroinvertebrados (BMWP/Gua e ISQA) que diagnostican la pérdida total de soporte de vida acuática en el cañón de Las Vacas.
11. **World Bank — Indicadores de Recursos Hídricos y Cobertura WASH (1960–2023):** 244 registros históricos de extracciones consuntivas anuales y coberturas de agua potable y saneamiento.
12. **FUNCAGUA — Informes de Situación del Agua y Piezometría Metropolitana:** Diagnósticos hidrogeológicos que evidencian abatimientos anuales del nivel freático de entre 1.5 y 4.5 metros/año en los acuíferos de Mixco y Villa Nueva.

---

## 5. PRINCIPALES BRECHAS DE INFORMACIÓN Y OBSTÁCULOS

1. **Ausencia de Guatemala en la Base Global UNEP GEMStat (GFQA v3):** Se inspeccionó el archivo maestro global de 201 MB (84 parámetros) y se demostró empíricamente que **Guatemala posee 0 estaciones reportadas** a GEMS/Water (las 129 estaciones de la ventana geográfica corresponden a la frontera de México). Esto confirma una desconexión histórica entre el Estado de Guatemala y los repositorios globales de calidad del agua.
2. **Bloqueos Tecnológicos Gubernamentales (WAF / Cloudflare):** Los portales del Ministerio de Ambiente y Recursos Naturales (`marn.gob.gt`) y el Catálogo Oficial de Datos Abiertos (`datos.gob.gt`) devuelven sistemáticamente código **HTTP 403 Forbidden** ante peticiones automatizadas estándar, imposibilitando la cosecha continua vía APIs públicas.
3. **Inaccesibilidad del Geoserver de SEGEPLAN (IDEG):** El puerto WFS/WMS (80) sufre de *timeout* externo, restringiendo la obtención de capas geoespaciales únicamente a descargas manuales por interfaz web.
4. **Opacidad de Operadores de Agua Potable y Saneamiento:** Ni EMPAGUA ni los operadores municipales publican bases de datos abiertas de calidad de agua cruda o tratada en sus fuentes de abastecimiento (planta Lo de Coy, pozos metropolitanos).
5. **Privacidad de Registros de Limpieza Industrial:** Las iniciativas de captura de plásticos (Alianza Motagua, 4ocean) reportan cifras agregadas o de relaciones públicas, reteniendo las matrices numéricas diarias de pesaje y composición gravimétrica.

---

## 6. INSTITUCIONES ADICIONALES A CONTACTAR

Para transformar RÍOS ABIERTOS GT en la plataforma definitiva, se debe activar la vía legal de la **Ley de Acceso a la Información Pública (Decreto 57-2008)** y mesas técnicas con:

1. **Unidad de Información Pública del MARN:** Solicitar la base de datos anonimizada del sistema **SIGEGAR** (estudios de aguas residuales del Acuerdo 236-2006) y los monitoreos del Laboratorio Nacional de Calidad del Agua.
2. **Dirección de Hidrología del INSIVUMEH:** Solicitar acceso al repositorio histórico digital completo de aforos hidrométricos (1970–2025) y API de telemetría en tiempo real.
3. **EMPAGUA:** Solicitar las series de calidad de agua cruda de captación en la planta Lo de Coy (ríos San Antonio, Pixcayá y Xayá).
4. **MSPAS (Departamento de Regulación y Control de Productos Farmacéuticos y Afines / DRACES):** Solicitar los reportes de vigilancia de cloro residual y contaminación fecal en acueductos comunitarios.
5. **Cuentas Nacionales del Banco de Guatemala (BANGUAT):** Obtener las matrices físicas completas de la Cuenta Integrada del Agua (CIRH).
6. **Alianza por la Cuenca del Motagua / Fundación The Ocean Cleanup:** Suscribir convenios académicos de transferencia de datos de pesaje diario y composición de residuos capturados por el Interceptor 006.

---

## 7. RECOMENDACIÓN TÉCNICA PARA LA PLATAFORMA "RÍOS ABIERTOS GT"

Para integrar estas fuentes heterogéneas (vectores, series de tiempo, perfiles de profundidad y lecturas en PDF), se recomienda la siguiente arquitectura open-source:

1. **Capa de Almacenamiento Espacial e Hidrológico:**
   * **PostgreSQL + PostGIS:** Base de datos relacional para estaciones de monitoreo, descargas, pozos y límites de cuencas.
   * **DuckDB + GeoParquet:** Para procesamiento analítico ultra-rápido de la red fluvial (HydroRIVERS 23k tramos) y series temporales de estaciones climáticas.
2. **Tubería de Ingesta Automatizada (Data Pipeline):**
   * Tareas programadas en Python que extraigan diariamente los boletines del INSIVUMEH (`BHVC.pdf`, `BHVP.pdf`) mediante `PyMuPDF`, convirtiendo los niveles y caudales instantáneos en series tabulares normalizadas.
   * Conectores periódicos para recopilar informes DICA de AMSCLAE y alertas del Ciano-Semáforo.
3. **Servicios de Mapas y APIs:**
   * **GeoServer / Martin Tile Server:** Servidor de teselas vectoriales ligeras (MVT) para renderizar la cuenca del Motagua y toda la hidrografía nacional en milisegundos.
   * **FastAPI:** Backend REST para consultar estaciones, caudales históricos y niveles de contaminantes emergentes.
4. **Interfaz Interactiva (Frontend):**
   * **Next.js / React con MapLibre GL o Deck.gl:** Visualizador 3D del relieve y de la red de drenaje, permitiendo a investigadores y ciudadanos navegar por tramo fluvial, ver el flujo de plásticos y consultar concentraciones de contaminantes a lo largo del Río Las Vacas y el Río Motagua.

---
*Informe generado con estricto apego a datos empíricos verificables. Todos los archivos y scripts de reproducción se encuentran en `D:\Documentos D\BaseDatosGT H2O\Investigación Antigravity`.*
