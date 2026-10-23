# Hoja de ruta

## Versión 1.0 (actual)

- Catálogo unificado de fuentes, publicaciones y datos faltantes.
- Atlas con 15 capas y precisión de ubicación declarada por punto.
- Mediciones en formato largo con código de parámetro y unidad.
- Sitio publicado en GitHub Pages y carpeta `datos/` descargable.
- La versión 1.0 no califica la calidad del agua.

## Próximas versiones

### 1. Comparación con normas y guías

El objetivo es mostrar, para cada medición, la referencia aplicable según el uso del agua, sin emitir un dictamen.

| Marco | Uso al que aplica |
|---|---|
| COGUANOR NTG 29001 | Agua para consumo humano en Guatemala |
| NOM-127-SSA1-2021 | Agua para uso y consumo humano en México |
| Guías de la OMS para la calidad del agua de consumo humano | Referencia internacional para agua de consumo |
| NOM-001-SEMARNAT-2021 | Descargas de aguas residuales en cuerpos receptores (México) |
| Acuerdo Gubernativo 236-2006 | Descargas y reúso de aguas residuales en Guatemala |

Pasos previstos:

1. Crear `datos/normas/limites.csv` con `marco`, `uso`, `codigo` (el mismo de `mediciones/parametros.csv`), `limite`, `unidad`, `tipo_limite` (máximo, mínimo, intervalo), `version` y `cita`. Cada valor se toma del documento oficial, con página o tabla.
2. Convertir unidades cuando haga falta; por ejemplo, NO₃⁻ frente a N-NO₃⁻ (factor 4,427) y NH₄⁺ frente a N-NH₄⁺.
3. Comparar solo cuando el uso coincide con el del sitio. Un límite de agua potable no se aplica a un río ni a un drenaje sin aclararlo.
4. En la ficha, mostrar la referencia junto al valor ("Referencia NTG 29001: …"), sin colores de aprobado o reprobado ni índices globales.

### 2. Más ubicaciones

- Documentar el sistema de coordenadas (GTM u otro) de las bases de AMSA y AMSCLAE y transformarlas a WGS 84.
- Ubicar las estaciones de caudal que hoy quedan fuera, con el catálogo oficial de estaciones del INSIVUMEH.

### 3. Capas completas desde los originales

Una vez armado el paquete de originales, agregar al pipeline:

- los 1 908 puntos de WPdx (hoy se muestra una muestra de 128);
- la red fluvial nacional del MAGA (10 934 tramos), las 313 subcuencas y las 2 391 microcuencas;
- las series diarias de NASA POWER y los perfiles de Atitlán de la UVG (2010-2024).

### 4. Datos faltantes

- Presentar solicitudes por la Ley de Acceso a la Información Pública (Decreto 57-2008) para los registros de `datos/catalogo/faltantes.csv` que tienen la solicitud marcada como factible.
- Registrar en el portal el estado de cada solicitud.

### 5. Actualización y participación

- Cosecha periódica del portal CKAN del INE y verificación automática de enlaces.
- Reportes ciudadanos con moderación (fase 2).
- Interfaz en inglés (los textos de la interfaz ya están reunidos en `src/textos.ts`).
