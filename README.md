# Agua Abierta Guatemala

Versión 0.1.0 de un portal local para explorar recursos hídricos y fuentes públicas de agua de Guatemala. La aplicación usa React, TypeScript, Vite y MapLibre. No necesita claves privadas ni un backend.

## Versiones de investigación incluidas

- `src/` contiene la aplicación integrada de Agua Abierta Guatemala.
- `versions/claude/` conserva los informes, inventarios, scripts, manifiestos, registros de búsqueda y datos procesados producidos por Claude.
- `versions/antigravity/` conserva los prototipos HTML, informes, inventarios, scripts, manifiestos y datos procesados producidos por Antigravity.

Consulte [`versions/README.md`](versions/README.md) para conocer la procedencia y las exclusiones por tamaño.

## Qué incluye

- Mapa MapLibre con 155 ubicaciones derivadas únicamente de coordenadas publicadas.
- Búsqueda de fuentes hídricas y fuentes de datos.
- Capas activables, visibilidad progresiva por escala, leyenda y fichas de evidencia.
- Imagen satelital reciente bajo demanda para cada ubicación, mediante NASA Worldview/GIBS y sin clave privada; cada recorte se centra en las coordenadas del punto y las muestra junto a una retícula visible.
- Alternativa tabular completa para la información del mapa.
- Biblioteca con los 75 archivos descargados, filtros, orden, fichas técnicas y SHA-256.
- Selección documentada de 12 conjuntos para el MVP.
- Copias organizadas en `fuente_de_datos/` sin modificar los originales de `Ghagpt/data/raw/`.
- Catálogo maestro en HTML y PDF.
- Modelo conservador de estados narrativos y documentación de procedencia.

## Ejecutar localmente

Requiere Node.js 20 o posterior.

La forma más sencilla en Windows es hacer doble clic en `ABRIR_DASHBOARD.cmd`. El archivo instala las dependencias si faltan, abre el navegador y deja el servidor activo mientras la ventana permanezca abierta.

```powershell
cd AguaAbiertaGuatemala
npm install
npm run dev -- --host 127.0.0.1 --port 4173
```

Abra `http://127.0.0.1:4173/`. No abra `index.html` directamente: la aplicación necesita el servidor local para cargar sus módulos y los archivos de la biblioteca. El mapa base requiere conexión a internet; los 155 elementos normalizados, la biblioteca y la documentación son locales. Si OpenFreeMap no responde, la aplicación conserva un fondo cartográfico local de respaldo y mantiene visibles los puntos.

## Construir y probar

```powershell
npm run test
npm run build
npm run preview -- --host 127.0.0.1 --port 4173
```

El resultado de interfaz se genera en `dist/`. La vista previa incluida sirve también `fuente_de_datos/` bajo demanda sin duplicar sus aproximadamente 303 MB. Para publicar la experiencia completa en un hosting estático, copie esa carpeta como `dist/fuente_de_datos/` antes de subir el contenido de `dist/`.

## Regenerar metadatos y copias

El script necesita Python 3.11+ y `openpyxl` para leer los XLSX de 2024.

```powershell
python .\scripts\build_data.py
python .\scripts\build_pdf.py
```

`build_data.py` usa como fuente la carpeta hermana `Ghagpt/`, copia los 75 archivos listados en `archivos_descargados.csv`, vuelve a calcular SHA-256 y genera:

- `public/data/catalog.json`
- `public/data/selected_datasets.json`
- `public/data/water_features.geojson`
- `public/data/summary.json`
- `fuente_de_datos/manifest_fuentes.csv`
- `verification/copy_integrity.json`
- `catalogo_fuentes_agua_guatemala.html`

Las copias de `fuente_de_datos/` no se guardan en Git porque incluyen archivos que superan el límite de tamaño de GitHub. Los metadatos normalizados necesarios para desarrollar y probar la interfaz sí forman parte del repositorio. Para reconstruir el archivo documental completo, coloque `Ghagpt/` junto a la carpeta del proyecto y ejecute los scripts anteriores.

## Límites del MVP

- No existe backend, autenticación ni moderación de reportes.
- “Reportar problema” está deshabilitado y marcado como Fase 2.
- No se afirma que los datos sean en tiempo real. La interfaz muestra la fecha de corte real.
- La imagen satelital tampoco es una transmisión en directo: usa color verdadero MODIS/Aqua en un recorte aproximado de 40 km, muestra la fecha UTC solicitada y puede tener retrasos, nubes o áreas todavía no procesadas. Puntos muy próximos pueden compartir píxeles y nubosidad por la resolución nominal de 250 m.
- El estado narrativo no emite conclusiones de calidad del agua en esta versión: las fuentes aparecen como “Sin datos suficientes” cuando la evidencia no permite una clasificación responsable.
- Los recursos sin coordenadas verificables permanecen en la biblioteca y no se colocan en el mapa.

Consulte [DATA_METHOD.md](DATA_METHOD.md), [EMOTION_MODEL.md](EMOTION_MODEL.md) y [MVP_DATASETS.md](MVP_DATASETS.md) para el detalle metodológico.
