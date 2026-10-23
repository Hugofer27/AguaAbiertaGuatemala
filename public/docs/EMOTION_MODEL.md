# Modelo de estados narrativos del agua

## Propósito

La “emoción” es una capa narrativa para facilitar la lectura de evidencia. No sustituye una clasificación normativa, un índice oficial de calidad, una declaración sanitaria ni una evaluación ecológica.

## Taxonomía preparada

- **Serena:** evidencia reciente y suficiente compatible con el objetivo técnico definido, sin señales activas de deterioro.
- **En observación:** evidencia reciente con una señal que requiere seguimiento o con cobertura todavía incompleta.
- **Tensa:** varias señales convergentes de presión o una tendencia sostenida adversa.
- **Herida:** deterioro confirmado para el uso evaluado y respaldado por un criterio técnico aplicable.
- **Crítica:** riesgo alto confirmado, excedencia severa o emergencia respaldada por la autoridad competente.
- **En recuperación:** mejora sostenida después de un estado adverso, con serie suficiente para establecer dirección.
- **Sin datos suficientes:** no existe información bastante, comparable y trazable para asignar otro estado.

## Regla activa en el MVP

La única regla activada es **Sin datos suficientes**. Se aplica cuando ocurre una o más de estas condiciones:

1. Falta una definición del uso del agua que se va a evaluar.
2. No existe una serie temporal comparable por sitio.
3. La evidencia corresponde a una campaña aislada, una celda modelada o un resumen administrativo.
4. Faltan metadatos de QA/QC, método, límite de detección o unidad para los parámetros decisivos.
5. No existe un límite técnico aplicable y citado para el uso, territorio y fecha.
6. Los parámetros disponibles no cubren las dimensiones mínimas requeridas por la evaluación futura.

Por estas razones, los elementos del mapa de esta primera versión se muestran como **Sin datos suficientes**. La ausencia de datos nunca se interpreta como buena calidad.

## Parámetros preparados para una fase posterior

El modelo de datos admite:

- pH;
- oxígeno disuelto;
- temperatura;
- turbidez y sólidos;
- conductividad;
- nutrientes;
- DBO y DQO;
- E. coli y coliformes;
- cloro residual para sistemas de abastecimiento;
- metales, microcistinas y contaminantes emergentes cuando existan método y límites;
- caudal, nivel y contexto meteorológico;
- fecha, estación, unidad, método, límite de detección y fuente.

No todos estos parámetros son pertinentes para todos los usos. Antes de activar otro estado se debe seleccionar el marco técnico correspondiente: agua para consumo, agua recreacional, vida acuática, descarga, abastecimiento o vigilancia operativa.

## Fechas consideradas

Cada evidencia conserva su fecha o periodo original. La ficha muestra la última fecha disponible. En el futuro, la regla de recencia debe definirse por tipo de medición y frecuencia esperada; este MVP no convierte automáticamente la antigüedad en una emoción de calidad.

## Límites y fuentes normativas

No se aplican límites numéricos en esta primera versión. Antes de activarlos se debe documentar, por parámetro y uso:

- nombre exacto de la norma o guía;
- autoridad y jurisdicción;
- versión y fecha de vigencia;
- valor, unidad y estadístico;
- condiciones de aplicación;
- tratamiento de valores no detectados;
- regla para mediciones repetidas.

Si la fuente no declara un límite o una licencia, la aplicación debe mostrar “No indicado” y no completar el dato por inferencia.

## Incertidumbre y cobertura

La incertidumbre se comunica con texto además de color:

- **Alta:** coordenada, fecha, unidad, método y procedencia explícitos.
- **Media:** ubicación y procedencia explícitas, pero cobertura o método incompletos.
- **Baja:** dato agregado, coordenada con datum desconocido o evidencia documental sin tabla reutilizable.

El nivel describe la cobertura de la ficha, no la calidad del agua. Cada estado futuro deberá exponer los valores, unidades, fechas, estaciones y fuentes que lo activaron.

## Diferencia entre emoción y estado técnico

La emoción resume una lectura narrativa. El estado técnico responde a una norma, índice o protocolo con propósito definido. Si ambos existen, la interfaz debe mostrar primero el estado técnico, después la emoción y, por último, la evidencia que permite reproducir la clasificación. Nunca se debe presentar una emoción como diagnóstico científico.
