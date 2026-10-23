# Historial de versiones

## 1.2.0 — 2026-10-23

- Nueva capa **Barreras de plástico (ubicación aproximada)**, apagada por defecto: el Interceptor 006 en el río Las Vacas, la retención de El Quetzalito (barda del MARN e Interceptor 021) y la biobarda de AMSA en el Villalobos. Se dibujan con un ícono de botella.
- Nueva precisión de ubicación **aproximada**, para fuentes que describen el lugar sin publicar la coordenada. El verificador impide que una capa aproximada venga activa por defecto.
- Las fichas enlazan a las notas o comunicados que respaldan un punto cuando su fuente no está en el catálogo, y `sitios.csv` gana la columna `enlaces`.

## 1.1.0 — 2026-10-23

- Nuevo mapa base **Blanco**: fondo blanco sin mosaicos externos, con solo las capas del portal. Sirve para imprimir y funciona sin internet.
- Licencias explícitas: CC BY 4.0 para el contenido propio (catálogo compilado, capas, textos, informes) y MIT para el código. Los datos de terceros conservan su licencia.
- Acerca de, el README y `docs/metodo.md` explican que las búsquedas las hicieron tres asistentes de IA (Claude, ChatGPT/Codex y Google Antigravity), dirigidos y revisados por Hugo Escobar.
- La cita sugerida lleva autoría y versión.
- La carpeta `versions/` se reemplazó por `fuentes/`, que guarda solo los 24 archivos que lee el pipeline (36 MB). El material completo sigue en el historial de git (commit `e81156a`). Los datos publicados no cambian.

## 1.0.1 — 2026-10-23

- La frontera de Petén con México vuelve a seguir el paralelo 17°15′ N, el meridiano 90°59′ O y el paralelo 17°49′ N en la cuenca del Río San Pedro. Antes, una diagonal recortaba el noroeste del departamento.
- Las menciones de una cuenca en el catálogo ya no confunden nombres genéricos; por ejemplo, "San Pedro La Laguna" (Atitlán) ya no cuenta como mención del Río San Pedro (Petén).

## 1.0.0 — 2026-10-23

Primera versión que integra las tres búsquedas de datos en un solo portal.

- Catálogo unificado sin duplicados: 643 fuentes y 1 494 publicaciones. Los IDs anteriores se conservan como alias.
- Nueva pestaña de datos faltantes (42 registros), con el motivo y cómo pedirlos por la Ley de Acceso a la Información Pública.
- Mapa con 14 capas:
  - nuevas: cuencas, lagos, red fluvial del Motagua, caudales mensuales, acidificación costera, fármacos en Las Vacas, plantas de tratamiento, puntos de agua, plásticos y estaciones meteorológicas;
  - botones de enfoque territorial;
  - modo limpio;
  - ficha de cuenca;
  - tabla alternativa al mapa.
- Cada punto declara la precisión de su ubicación. Se excluyeron 81 ubicaciones sin coordenada defendible.
- Mediciones en formato largo con código de parámetro y unidad. El oxígeno disuelto se controla contra la saturación teórica.
- Carpeta `datos/` exportable (CSV y GeoJSON), con diccionario de datos y manifiesto de 342 originales con SHA-256.
- Interfaz rediseñada: tema claro con modo oscuro automático, barra superior y tres secciones (Mapa, Datos, Acerca de).
- Publicación automática en GitHub Pages, con ZIP de datos y ZIP del sitio para usar sin internet.
- Se retiró el "estado narrativo" del agua. La comparación con normas queda en la hoja de ruta.

## 0.1.0 — 2026-10-23

Primera versión publicable de Agua Abierta Guatemala.

- Atlas interactivo con 155 ubicaciones verificadas.
- Biblioteca de 75 fuentes públicas con metadatos y huellas SHA-256.
- Búsqueda, filtros, capas y fichas de evidencia.
- Imágenes satelitales bajo demanda mediante NASA Worldview/GIBS.
- Vista tabular accesible y documentación metodológica.
- Pruebas automatizadas y proceso reproducible de compilación.
