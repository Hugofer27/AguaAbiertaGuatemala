# RÍOS ABIERTOS GT — Repositorio de Descubrimiento y Adquisición de Datos Hídricos de Guatemala

Este repositorio contiene los resultados de la investigación activa, adquisición y verificación de datos hidrológicos, limnológicos, de calidad del agua y macroplásticos para la República de Guatemala, con foco prioritario en la **Cuenca del Río Motagua** y el **Río Las Vacas**.

Investigación ejecutada por el agente **Antigravity**.  
Fecha de Adquisición: **2026-10-21**.  
Volumen de datos preservados: **155.55 MB** (63 archivos verificados con hash SHA-256).

---

## Estructura del Directorio

```text
Investigación Antigravity/
├── data/
│   ├── raw/                        # Datos brutos descargados directamente desde las fuentes
│   │   ├── government/             # INSIVUMEH, AMSCLAE, AMSA, MARN
│   │   ├── academic/               # Tesis USAC (ERIS, Ingeniería) con tablas de laboratorio
│   │   ├── ngos_cleanup/           # The Ocean Cleanup (datos de campo Motagua 2019, shapefiles)
│   │   ├── geospatial/             # HydroRIVERS Centroamérica (USGS/WWF), macrocuencas, vertientes
│   │   ├── international/          # Banco Mundial (WDI), GRDC WMO
│   │   └── publications/           # Metadatos bibliográficos OpenAlex (248 obras) y GitHub
│   └── processed/                  # Datos normalizados, filtrados y estructurados
│       ├── Guatemala_HydroRIVERS_Reaches.csv                 # 23,057 tramos fluviales en GT
│       ├── Motagua_River_Basin_Network.geojson               # 1,626 tramos vectorizados del Motagua
│       ├── USAC_ERIS_Motagua_LasVacas_2025_Monitoring_Data.csv # 32 estaciones DBO, DQO, fármacos
│       ├── TheOceanCleanup_Motagua_Morales_2019_Flux.csv     # Serie mensual macroplásticos Motagua
│       └── Guatemala_River_Plastic_Outlets_Meijer2021.csv   # 140 desembocaduras costeras con vertido
├── inventories/                    # Entregables A, B y C en CSV y XLSX
│   ├── master_data_inventory.csv   # Entregable A: 30 datasets únicos maestros
│   ├── master_data_inventory.xlsx  # Entregable A en formato Excel
│   ├── source_summary.csv          # Entregable B: Agregado por organización
│   ├── source_summary.xlsx         # Entregable B en formato Excel
│   ├── missing_data_register.csv   # Entregable C: Registro de datos faltantes e inaccesibles
│   └── missing_data_register.xlsx  # Entregable C en formato Excel
├── manifests/
│   └── data_manifest.json          # Manifiesto legible por máquina con checksums SHA-256
├── scripts/                        # Scripts reproducibles de descarga, extracción y procesamiento
│   ├── build_all_deliverables.py   # Compila inventarios, resúmenes y genera el manifiesto SHA-256
│   ├── download_hydrorivers.py     # Descarga HydroRIVERS Norte y Centroamérica (66.3 MB)
│   ├── extract_guatemala_rivers.py # Filtra y vectoriza los 23k ríos de GT y la red del Motagua
│   ├── extract_usac_motagua_data.py# Extrae datos de contaminantes de la tesis USAC ERIS 2025
│   ├── download_ocean_cleanup_data.py # Descarga datos de campo de The Ocean Cleanup
│   ├── convert_motagua_xlsx.py     # Parsea XML de la hoja Excel de The Ocean Cleanup
│   ├── export_ocean_cleanup_outlets.py # Extrae desembocaduras de plásticos en GT
│   ├── download_wave2.py           # Descarga boletines INSIVUMEH y tesis USAC
│   ├── download_carlossoto_hidrologia.py # Descarga capas oficiales de cuencas de Guatemala
│   ├── fetch_international_water_data.py # Descarga indicadores WDI del Banco Mundial
│   └── search_openalex.py          # Búsqueda estructurada de literatura en OpenAlex
└── report/
    └── INFORME_EJECUTIVO_RIOS_ABIERTOS_GT.md # Entregable D: Informe ejecutivo en español
```

---

## Reproducibilidad

Todos los scripts están escritos en Python estándar (Python 3.12+) utilizando librerías ampliamente disponibles (`requests`, `pandas`, `xlsxwriter`, `pymupdf`).

Para reproducir la compilación completa de inventarios y el cálculo de hashes SHA-256:

```bash
python scripts/build_all_deliverables.py
```

Para regenerar las capas vectoriales de la cuenca del Río Motagua a partir de HydroRIVERS:

```bash
python scripts/extract_guatemala_rivers.py
```

Para verificar la integridad de cualquier archivo descargado, consulte el manifiesto criptográfico:
`manifests/data_manifest.json`.
