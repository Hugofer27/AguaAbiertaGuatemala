# Sistema visual del portal

## Dirección

El portal extiende el lenguaje de “atlas de levantamiento hidrográfico” a una herramienta cartográfica de uso continuo. La interfaz prioriza navegación conocida, densidad legible, procedencia y estados operativos explícitos antes que ornamentación.

## Tokens

- Tinta profunda: `#071f27`
- Tinta naval: `#0e2d36`
- Tinta intermedia: `#0a2933`
- Agua: `#0a706c`
- Agua brillante: `#34b7a8`
- Aqua de apoyo: `#73d7ca`
- Papel técnico: `#edf5f3`
- Papel de profundidad: `#dfecea`
- Papel blanco: `#fbfdfc`
- Regla cartográfica: `#91adae`
- Regla oscura: `#31525a`
- Texto secundario: `#45656b`
- Anotación carmín: `#b34238`
- Anotación coral sobre oscuro: `#ff9187`
- Apoyo meteorológico y estado de respaldo: `#ffb36a`

## Tipografía

- Rótulos, cifras y navegación: Ubuntu Condensed bajo el nombre local `Atlas`.
- Lectura, formularios y tablas: Ubuntu bajo el nombre local `AtlasText`, en pesos 400 y 700.
- Las fuentes se sirven desde `public/fonts/` y no requieren red.

## Componentes

- Navegación lateral de tinta naval con selección turquesa. En móvil se convierte en un menú superpuesto; cuando está cerrado usa `visibility: hidden` y `pointer-events: none`, por lo que sus controles no entran en el orden de tabulación.
- Mapa dominante con controles de MapLibre adaptados al sistema. Usa OpenFreeMap Liberty como mapa natural por defecto y ofrece Atlas oscuro como alternativa, con una inclinación leve que aporta profundidad sin comprometer la lectura. El estado visible distingue carga, cartografía conectada (`ready`) y respaldo (`fallback`); si falla el mapa base, permanecen activos los datos locales sobre un fondo cartográfico mínimo.
- La selección cartográfica confirma la coordenada exacta con un pulso o *ripple* localizado, sin desplazar ni exagerar el punto seleccionado.
- La ficha permite solicitar bajo demanda una observación satelital reciente de NASA Worldview/GIBS. Cada petición usa un recorte de aproximadamente 40 km centrado en la coordenada del registro; una retícula propia y el par latitud/longitud hacen verificable el centro incluso cuando la imagen está cubierta por nubes o contiene huecos orbitales. La imagen conserva fecha UTC, navegación diaria, atribución y una advertencia explícita de que no es una transmisión en directo. No se descarga hasta que el usuario abre el módulo.
- Panel de capas oscuro con recuentos, estados disponibles/no disponibles y leyenda redundante en texto, forma y color. En móvil inicia colapsado y se expande mediante un botón con `aria-expanded` y `aria-controls`.
- Ficha de ubicación integrada junto al mapa en escritorio, superpuesta en tableta y presentada como *bottom sheet* de hasta 68% del alto en móvil. Tras seleccionar un punto, una secuencia breve de unos 900 ms presenta primero un estado narrativo del agua y después revela la ficha y su evidencia; permite omisión manual y se resuelve de inmediato con `prefers-reduced-motion`. El estado narrativo es una capa de orientación de la interfaz, no una declaración científica sobre la fuente. Se conserva “Sin datos suficientes” cuando la evidencia no permite clasificar.
- Ficha de procedencia presentada como modal lateral mediante un portal al `body`: el contenido principal queda `inert`, se bloquea el desplazamiento de fondo, el foco permanece dentro, `Escape` cierra y el foco regresa al control que la abrió. Expone coordenadas, ID del conjunto de datos, formato y estado, nombre exacto del archivo local y enlace oficial.
- Búsqueda global cuyos resultados forman una región etiquetada y accionable mediante botones; cada resultado conserva nombre, tipo y contexto de procedencia.
- Paneles rectos, sin esquinas redondeadas ni sombras ambientales. Las sombras se reservan para superficies superpuestas que necesitan separación funcional.
- Carmín reservado para brechas, alertas, selección crítica y foco. Las fichas de evidencia explicitan institución, fecha, cobertura y advertencia.

## Responsive

- Escritorio: navegación fija, mapa dominante y ficha lateral simultánea.
- Tableta: navegación compacta y ficha de mapa superpuesta para conservar el área cartográfica.
- Móvil (`≤700px`): navegación desplegable, mapa a ancho completo, capas colapsables y ficha de mapa como lámina inferior; la ficha de fuente ocupa el ancho completo.
- Las tablas densas conservan desplazamiento horizontal y el catálogo reduce columnas secundarias por etapas.

## Accesibilidad

- Contraste de lectura sobre superficies oscuras y claras. El foco visible combina contorno carmín de 3 px con halo blanco para mantener alto contraste en ambos fondos.
- Navegación por teclado, enlace de salto y controles con nombre accesible; la navegación móvil cerrada no retiene elementos tabulables.
- Los resultados de búsqueda se exponen como región con nombre accesible y acciones de botón, sin depender de gestos ni de la apariencia de una lista.
- Los modales gestionan foco inicial, confinamiento de `Tab`, cierre con `Escape`, fondo `inert` y retorno de foco.
- El mapa tiene alternativa tabular y comunica por texto sus estados `loading`, `ready` y `fallback`; el color solo refuerza el mensaje.
- `prefers-reduced-motion` reduce animaciones y transiciones casi a cero. El reenfoque cartográfico usa `jumpTo` en lugar de `flyTo` cuando el usuario solicita movimiento reducido.
