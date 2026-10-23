---
name: Gaceta de hallazgos · RÍOS ABIERTOS GT
description: Hallazgos de investigación publicados como gaceta oficial impresa, en papel gris frío, tinta negra y una sola tinta de color, añil.
colors:
  papel: "#e4e7ea"
  papel-hondo: "#d8dce0"
  tinta: "#151515"
  tinta-2: "#383936"
  atenuada: "#62635d"
  anil: "#1d3a94"
  filete-tenue: "color-mix(in srgb, #151515 28%, transparent)"
typography:
  display:
    fontFamily: "Barlow Condensed, Arial Narrow, sans-serif"
    fontSize: "4.3rem"
    fontWeight: 800
    lineHeight: 0.92
    letterSpacing: "-0.01em"
  headline:
    fontFamily: "Barlow Condensed, Arial Narrow, sans-serif"
    fontSize: "2.75rem"
    fontWeight: 800
    lineHeight: 0.95
    letterSpacing: "-0.005em"
  title:
    fontFamily: "Barlow Condensed, Arial Narrow, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "0.02em"
  sumario:
    fontFamily: "PT Serif, Georgia, serif"
    fontSize: "1.22rem"
    fontWeight: 400
    lineHeight: 1.45
  body:
    fontFamily: "PT Serif, Georgia, serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
    fontFeature: "lnum"
  nota:
    fontFamily: "PT Serif, Georgia, serif"
    fontSize: "0.86rem"
    fontWeight: 400
    lineHeight: 1.4
  label:
    fontFamily: "Barlow Condensed, Arial Narrow, sans-serif"
    fontSize: "1rem"
    fontWeight: 800
    lineHeight: 1.5
    letterSpacing: "0.08em"
  cifra:
    fontFamily: "Barlow Condensed, Arial Narrow, sans-serif"
    fontSize: "1.2em"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "0.01em"
    fontFeature: "tnum, lnum"
  dato:
    fontFamily: "PT Mono, Consolas, monospace"
    fontSize: "0.92em"
    fontWeight: 400
rounded:
  none: "0"
spacing:
  fino: "1px"
  grueso: "5px"
  margen: "clamp(1.25rem, 3.2vw, 3rem)"
  col: "62ch"
  raiz-lamina: "clamp(14px, min(1.38vw, 2.1vh), 26px)"
components:
  cabezal:
    backgroundColor: "{colors.papel}"
    textColor: "{colors.tinta}"
    typography: "{typography.label}"
    padding: "0 0 0.45rem"
  rotulo:
    textColor: "{colors.anil}"
    typography: "{typography.label}"
  boton-navegacion:
    backgroundColor: "transparent"
    textColor: "{colors.tinta}"
    rounded: "{rounded.none}"
    padding: "0.3rem 0.75rem"
    height: "2.25rem"
  boton-navegacion-hover:
    backgroundColor: "{colors.tinta}"
    textColor: "{colors.papel}"
  boton-navegacion-disabled:
    backgroundColor: "transparent"
    textColor: "{colors.atenuada}"
  celda-tabla:
    textColor: "{colors.atenuada}"
    padding: "0.32rem 0.6rem 0.32rem 0"
  celda-tabla-lidera:
    textColor: "{colors.tinta}"
    typography: "{typography.cifra}"
  ir-sumario:
    backgroundColor: "{colors.papel}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.none}"
    padding: "0.55rem 1rem"
    height: "2.75rem"
    width: "100%"
  ir-sumario-hover:
    backgroundColor: "{colors.tinta}"
    textColor: "{colors.papel}"
  panel-sumario:
    backgroundColor: "{colors.papel}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.none}"
    padding: "1.4rem 1.6rem"
    width: "min(26rem, 92vw)"
---

# Design System: Gaceta de hallazgos · RÍOS ABIERTOS GT

## Overview

**Creative North Star: "La Gaceta Oficial"**

Cada lámina es un acto publicado: una mancheta con filete doble, un titular condensado en mayúsculas, los considerandos (la evidencia, con su fuente) y una resolución que concluye. El sistema imita una gaceta impresa en papel periódico gris frío, con tinta negra y una sola tinta de color, añil, usada con compromiso total. La autoridad viene de la tipografía, los filetes y las llamadas de nota; no hay tarjetas, fondos de color, degradados ni iconografía.

La densidad es de página impresa: texto oficial en serif con medida de 58 a 72 caracteres, notas al pie a dos columnas y procedencia firmada al pie de cada hoja. En modo lámina toda la página escala con el viewport, como una hoja proyectada. En pantallas angostas la misma gaceta se lee de corrido, hoja tras hoja, separadas por filete grueso.

El estado de una fuente nunca es un color: es una marca dibujada (cuadro lleno, medio lleno, vacío, tachado o raya) acompañada de su palabra. La comparación entre agentes no usa colores por agente; el valor que lidera se imprime en tinta plena y los demás en tinta atenuada.

**Key Characteristics:**
- Papel gris frío, tinta negra, una sola tinta de color (añil), sin segundo acento.
- Mancheta con filete doble grueso-fino; filetes como única estructura.
- Grotesca condensada en mayúsculas para titulares, rótulos y UI; serif de tipos públicos para leer; mono para rutas e IDs.
- Gramática de decreto: Considerando, Por tanto, Artículos, Fe de erratas, Notas, Procedencia, Firma.
- Estado por marca dibujada más palabra; lidera la tinta plena.
- Esquinas rectas en todo; plano, sin sombras de profundidad salvo el panel de sumario.

## Colors

Paleta de imprenta: un papel, tres grises de tinta y una sola tinta de color.

### Primary
- **Añil de imprenta** (`anil`): la única tinta de color. Rótulos de decreto (Considerando, Por tanto, Artículo N., Glosario, Fe de erratas), nombres de agente en el despacho y la cronología, llamadas de nota (`sup.ref`) y números de nota, encabezados de grupo de la matriz con su filete fino, enlaces, foco, selección y caret. Nunca rellena superficies grandes ni codifica un estado.

### Neutral
- **Papel periódico frío** (`papel`): fondo de toda hoja, del panel de sumario y de la banda inferior. En impresión se sustituye por blanco.
- **Papel hondo** (`papel-hondo`): solo el carril de la barra de desplazamiento.
- **Tinta negra** (`tinta`): texto principal, titulares, filetes gruesos y finos, marcas de estado, valor que lidera. El alias `--filete` vale lo mismo.
- **Tinta segunda** (`tinta-2`): edición del cabezal, procedencia, notas, rutas `.dato`, leyenda, "Donde dice / Debe decir".
- **Tinta atenuada** (`atenuada`): valores que no lideran en tablas comparativas, botones deshabilitados, filas de la cronología con evidencia citada pero no obtenida (`li.falta`). Contraste sobre papel de 4,9:1.
- **Filete tenue** (`filete-tenue`): separadores entre considerandos, artículos, filas de tabla, índice, cronología y columnas. Es la tinta al 28 %, mezclada con transparencia.

### Named Rules
**The Una Sola Tinta Rule.** Solo existe un color además de los grises: añil. No se añade un segundo acento, ni colores por agente, ni colores de estado.

**The Tinta Plena Lidera Rule.** En toda comparación aparecen los tres valores; el que lidera va en `tinta` con peso 700-800 y los demás en `atenuada`. La jerarquía es de tinta, no de tono.

## Typography

**Display Font:** Barlow Condensed (con Arial Narrow, sans-serif), pesos 500 a 800, autoalojada.
**Body Font:** PT Serif (con Georgia, serif), regular, negrita e itálica, autoalojada.
**Label/Mono Font:** PT Mono (con Consolas, monospace) para rutas de archivo e IDs (`.dato`).

**Character:** Grotesca condensada de titular de periódico frente a una serif de tipos públicos con aire de texto oficial. Dos caras con funciones fijas, más una mono que solo marca lo que es literal y rastreable.

### Hierarchy
- **Display** (800, 4.3rem, 0.92): titular de portada, en mayúsculas, `text-wrap: balance`. En lectura continua baja a `clamp(2.3rem, 9.5vw, 3.6rem)`.
- **Headline** (800, 2.75rem, 0.95): titular de cada lámina, en mayúsculas. En lectura continua `clamp(1.8rem, 7.4vw, 2.6rem)`.
- **Title** (700, 1.25rem, 1.1, 0.02em): títulos menores ("Sumario" del índice y del panel).
- **Sumario** (PT Serif 400, 1.22rem, 1.45, máx. 58ch): entradilla bajo el titular.
- **Body** (PT Serif 400, 1rem, 1.5, máx. 62ch): considerandos, artículos, resolución (en negrita 700 dentro de Por tanto). Numerales de caja alta.
- **Nota** (PT Serif 400, 0.86rem, 1.4): notas al pie, procedencia, leyenda.
- **Label** (Barlow Condensed 800, 1rem, 0.08em, mayúsculas): rótulos de decreto en añil; cabezal y botones en 600-700 con 0.04-0.05em.
- **Cifra** (Barlow Condensed 700, 1.2em, 1.05, numerales tabulares): cifras en tablas; 800 cuando lideran. Años de la cronología en 800 a 1.55rem.
- **Dato** (PT Mono 400, 0.92em, `tinta-2`): rutas e IDs, con corte en cualquier punto.

### Named Rules
**The Dos Caras Rule.** Barlow Condensed habla (titulares, rótulos, cabezal, botones, cifras, firma); PT Serif argumenta (todo texto corrido). PT Mono solo para lo literal: rutas e IDs.

**The Escala de Hoja Rule.** En modo lámina la raíz es `clamp(14px, min(1.38vw, 2.1vh), 26px)` y todo se mide en rem, de modo que la hoja entera escala como una página proyectada.

## Layout

Cada lámina es una hoja a pantalla completa con rejilla de tres filas: cabezal, cuerpo y pie. El margen lateral es `margen`; el relleno vertical es `clamp(0.9rem, 2.2vh, 1.6rem)` arriba y `clamp(0.7rem, 1.8vh, 1.2rem)` abajo. El cuerpo es una rejilla con separación `clamp(0.9rem, 1.7vw, 2rem)`.

Composiciones recurrentes:
- **Portada**: titular y sumario a la izquierda (1.65fr), índice como navegación a la derecha (mín. 16rem), y el despacho de tres columnas anclado abajo bajo filete grueso.
- **Dos columnas** (1.1fr / 1fr): titular a todo el ancho, dos listas de considerandos separadas por filete fino vertical, y el Por tanto (`.pie-acto`) anclado al pie a todo el ancho.
- **Agente** (0.95fr / 1.25fr): columna lateral con titular, sumario y Por tanto; considerandos a la derecha.
- **Matriz** (0.72fr / 2fr): lateral con titular, leyenda vertical y nota; tabla de marcas a la derecha.
- **Pila**: titular, tabla o artículos, y Por tanto al pie.
- **Cronología**: rejilla de 3 columnas por 4 filas que fluye por columna (`grid-auto-flow: column`), con año en columna fija de 4.2rem.
- **Artículos**: `auto-fit` con mínimo 19rem por columna.

Densidad: las láminas marcadas `.holgada` (solo escritorio) suben el cuerpo de considerandos (1.2rem), tablas y artículos (1.1rem) y estiran el cuerpo para llenar la hoja, empujando la resolución al pie. En hojas 16:10 (`max-aspect-ratio: 17/10`) la fe de erratas baja a 1.06rem para cerrar sobre la resolución.

Modos:
- **Modo lámina**: `min-width: 821px` y `min-height: 521px`, sin `.lectura`. Una hoja visible a la vez.
- **Lectura continua**: `max-width: 820px` o `max-height: 520px`, o `?modo=lectura`. Raíz a 106.25 %, todas las rejillas a una columna, hojas apiladas separadas por filete grueso, notas a una columna, tablas anchas con desplazamiento horizontal (mín. 34rem), botones de pie ocultos y banda `.ir-sumario` fija abajo.
- **Impresión**: A4 apaisado, margen 10mm, una hoja por página, fondo blanco, sin navegación.

## Elevation & Depth

Sistema plano. La profundidad se expresa con filetes y peso de tinta, no con capas. Hay dos usos de `box-shadow` y solo uno es profundidad.

### Shadow Vocabulary
- **Filete fino de mancheta** (`box-shadow: 0 4px 0 -2px var(--papel), 0 5px 0 -2px var(--filete)`): no es sombra; dibuja el filete fino bajo el grueso del cabezal.
- **Panel lateral** (`box-shadow: -8px 0 24px rgba(21,21,21,0.18)`): única sombra de profundidad, para el panel de sumario que se superpone a la hoja.

### Named Rules
**The Plano Impreso Rule.** Nada flota salvo el panel de sumario. La banda `.ir-sumario` se separa con filete grueso superior, no con sombra.

## Shapes

Todo es rectangular con esquinas rectas (`rounded.none`). La forma la dan los filetes: grueso (`grueso`) para mancheta, apertura de resolución, encabezados de tabla, despacho, separación de hojas y bordes de banda y panel; fino (`fino`) para pie, botones y filete fino de mancheta; tenue para separar elementos de lista. Las marcas de estado son cuadros dibujados en un viewBox de 16, con trazo de 1.5.

### Named Rules
**The Filete Doble Rule.** La mancheta siempre cierra con filete grueso (5px) seguido de filete fino (1px) separados por un hilo de papel.

## Components

### Buttons (navegación)
Botones de imprenta: texto, no iconos.
- **Shape:** rectangulares, esquinas rectas, borde `fino` en `tinta`, altura mínima 2.25rem.
- **Default:** fondo transparente, Barlow Condensed 700 a 0.95rem, mayúsculas, 0.05em. Rótulos: Anterior, Sumario, Siguiente.
- **Hover:** se invierte a fondo `tinta` y texto `papel`, sin transición.
- **Disabled:** texto y borde en `atenuada`.
- **Focus:** contorno 2px `anil` con separación de 3px (global en `:focus-visible`).

### Navigation
- **Cabezal (mancheta):** rejilla de tres partes: nombre (800, 0.06em), edición centrada en `tinta-2` y fecha con número de lámina a la derecha con numerales tabulares. En lectura continua la edición pasa a segunda línea.
- **Índice / sumario:** lista con número de lámina alineado a la derecha en Barlow 700 tabular, filas separadas por filete tenue, hover en añil. Aparece en la portada y en el panel.
- **Panel de sumario:** hoja lateral derecha `min(26rem, 92vw)` con filete grueso izquierdo; se abre con el botón Sumario o la tecla S y se cierra con Escape, clic fuera o Cerrar.
- **Banda `.ir-sumario`:** solo en lectura continua; ancho total, fija abajo, filete grueso superior, "Sumario" a la izquierda y "Lám. n/12" a la derecha en `tinta-2`; respeta `safe-area-inset-bottom`. Hover invertido.
- **Teclado y gesto:** flechas, RePág/AvPág, espacio, Inicio, Fin y deslizamiento táctil de 60px en modo lámina.

### Gramática de decreto (componente distintivo)
- **Considerando:** lista sin viñetas, máx. `col`, cada punto separado por filete tenue. El primero abre con el rótulo.
- **Rótulo:** palabra de la forma del decreto (Considerando, Considerando además, Por tanto, Veredicto, Glosario de marcas, Fe de erratas) en Barlow 800, mayúsculas, 0.08em, añil, en línea propia sobre el texto.
- **Por tanto / pie de acto:** abre con filete grueso; resolución en PT Serif 700. Como `.pie-acto` se ancla al pie del cuerpo a todo el ancho, con medida de 72ch.
- **Artículos:** contador automático "Artículo N." en Barlow 800 añil sobre cada párrafo.
- **Fe de erratas:** "Donde dice:" y "Debe decir:" en Barlow 700 mayúsculas `tinta-2`, cada errata en línea propia.
- **Notas:** número en Barlow 700 añil, dos columnas de 22rem, sin cortes dentro de una nota; llamadas `sup.ref` en Barlow 700 añil a 0.68em.
- **Procedencia y firma:** al pie; la etiqueta inicial (Procedencia., Lectura., Fuentes., Base legal.) corre en línea en Barlow 700 mayúsculas; la firma "Firmado: Claude (Opus 5.5) · fecha, hora" en Barlow 700 mayúsculas.

### Tablas comparativas
- Encabezado en Barlow 800 mayúsculas sobre filete grueso; filas separadas por filete tenue; numerales tabulares.
- Celdas en `atenuada`; `.lidera` en `tinta` 700, con la cifra en 800. Las cifras van en Barlow con su glosa en `small` debajo.

### Matriz de marcas
- Cinco símbolos SVG dibujados: `#m-desc` (cuadro lleno, Descargado), `#m-parc` (cuadro con triángulo lleno, Parcial), `#m-loc` (cuadro vacío, Localizado), `#m-bloq` (cuadro tachado en aspa, Bloqueado), `#m-no` (raya, No hallado). Tamaño 1.05rem, color `currentColor` en tinta.
- Cada marca en tabla lleva `role="img"` y `aria-label` con la palabra de estado; la leyenda y el glosario las repiten con su palabra visible.
- Grupos de filas con encabezado Barlow 800 añil a 0.82rem sobre filete fino añil.
- **El golpe:** al entrar en la lámina, las marcas pasan de opacidad 0.16 a 1 fila por fila cada 70ms, sin transición, como sellos. Con `prefers-reduced-motion`, en lectura continua y en impresión aparecen todas impresas.

### Despacho y cronología
- **Despacho:** tres columnas bajo filete grueso, separadas por filete tenue vertical; línea en Barlow 700 a 1.4rem con nombre de agente en línea, en 800 mayúsculas añil terminado en punto.
- **Cronología:** año en Barlow 800 a 1.55rem, quién en Barlow 700 mayúsculas añil con punto en línea, ID en `.dato` debajo. Las filas `.falta` van en `atenuada`.

## Do's and Don'ts

### Do:
- **Do** usar solo `anil` como color; todo lo demás es papel y grises de tinta.
- **Do** mostrar cada estado con su marca dibujada y su palabra (leyenda, glosario o `aria-label`).
- **Do** imprimir el valor que lidera en `tinta` 700-800 y los demás en `atenuada`, con los tres valores presentes.
- **Do** cerrar la mancheta con filete grueso (5px) más filete fino (1px).
- **Do** abrir cada bloque de evidencia y resolución con su palabra de decreto en el rótulo añil.
- **Do** llevar cada cifra a su fuente con llamada de nota, ID en `.dato` o línea de procedencia, y firmar y fechar el pie.
- **Do** escalar la hoja con la raíz `clamp(14px, min(1.38vw, 2.1vh), 26px)` en modo lámina y medir en rem.
- **Do** imprimir la matriz fila por fila sin transición y respetar `prefers-reduced-motion`.
- **Do** mantener esquinas rectas y separar con filetes.

### Don't:
- **Don't** añadir un segundo color de acento, colores por agente ni colores de estado.
- **Don't** codificar un estado solo con color.
- **Don't** poner rótulos o antetítulos sobre los titulares; las únicas etiquetas sobre texto son las palabras de la forma del decreto.
- **Don't** usar sombras de profundidad salvo el panel de sumario; la banda inferior se separa con filete.
- **Don't** usar tarjetas, fondos de color, degradados, esquinas redondeadas ni iconos de glifo.
- **Don't** usar transiciones o animaciones suavizadas; los cambios de estado son de golpe.
- **Don't** usar Barlow Condensed para texto corrido ni PT Serif para titulares o UI.
