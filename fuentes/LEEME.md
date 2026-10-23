# Fuentes de entrada del pipeline

Esta carpeta guarda solo los archivos que leen `pipeline/construir_datos.py` y el análisis: inventarios, manifiestos con SHA-256 y datos ya procesados. Vienen de las tres búsquedas de datos de octubre de 2026, que hicieron tres asistentes de IA (Claude de Anthropic, ChatGPT/Codex de OpenAI y Google Antigravity), dirigidos y revisados por Hugo Escobar.

| Carpeta | Búsqueda | Qué se usa |
|---|---|---|
| `claude/` | Claude | Inventario maestro (2 116 recursos), publicaciones, faltantes, incidentes, manifiestos y datos procesados de GEMStat, HydroWASTE e INSIVUMEH |
| `codex/` | ChatGPT/Codex | Catálogo de 75 archivos con SHA-256 y puntos de monitoreo normalizados (MVP 0.1) |
| `antigravity/` | Antigravity | Inventario de 30 conjuntos, faltantes, manifiesto, capas nacionales (cuencas, lagos, caudales), red del Motagua, tesis USAC-ERIS, plásticos y HydroRIVERS |

No edite estos archivos. Si hay que corregir algo, hágalo en el pipeline, como las reparaciones de texto o la frontera de Petén.

## Material completo de las búsquedas

Los informes, scripts, prototipos y registros completos se retiraron del árbol principal en la versión 1.1.0, pero siguen en el historial de git. Para recuperarlos:

```bash
git checkout e81156a -- versions/
```

El commit `e81156a` es la versión 1.0.1, la última que incluye la carpeta `versions/`.
