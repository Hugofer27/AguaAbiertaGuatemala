import type { Precision, Vista } from './types'

/** Textos compartidos de la interfaz, reunidos para facilitar una futura traducción. */

export const NOMBRE = 'Agua Abierta Guatemala'

export const VISTAS: Record<Vista, string> = {
  mapa: 'Mapa',
  datos: 'Datos',
  acerca: 'Acerca de',
}

export const PRECISION: Record<Precision, { corto: string; largo: string }> = {
  publicada: {
    corto: 'Ubicación publicada',
    largo: 'La coordenada viene tal cual de la fuente.',
  },
  homonimo: {
    corto: 'Ubicación por punto homónimo',
    largo: 'La fuente no publica la coordenada de esta estación; se usa la del punto de monitoreo del INSIVUMEH con el mismo nombre y municipio.',
  },
  transcrita: {
    corto: 'Ubicación transcrita',
    largo: 'La coordenada se transcribió de un documento (tesis o informe). Conviene verificarla en el original.',
  },
  modelada: {
    corto: 'Ubicación de un modelo',
    largo: 'Es una celda o punto de cálculo de un modelo, no una estación en terreno.',
  },
}

export const TIPO_DATO: Record<string, string> = {
  Medido: 'Valores medidos en campo o laboratorio.',
  Modelado: 'Valores estimados por un modelo, no medidos en el sitio.',
  'Compilado y estimado': 'Base compilada; algunos valores son estimaciones.',
  Reportado: 'Información reportada por terceros (estado de funcionamiento).',
  Ubicación: 'Solo la ubicación; la serie de datos no está publicada en formato abierto.',
  'Cartografía oficial': 'Límites y cuerpos de agua de la cartografía oficial.',
}

export const AVISO_GENERAL =
  'Agua Abierta Guatemala muestra valores con su procedencia. No califica la calidad del agua ni sustituye una evaluación técnica o sanitaria.'

export const CITA = (anio: string, url: string) =>
  `Agua Abierta Guatemala (${anio}). Catálogo y atlas de datos públicos sobre el agua en Guatemala, versión 1.0. ${url}`

export function fechaCorte(valor: string) {
  const fecha = new Date(`${valor}T00:00:00`)
  return new Intl.DateTimeFormat('es-GT', { day: 'numeric', month: 'long', year: 'numeric' }).format(fecha)
}

export function numero(valor: number, decimales = 0) {
  return valor.toLocaleString('es-GT', { maximumFractionDigits: decimales })
}

export function formatoValor(valor: number) {
  const absoluto = Math.abs(valor)
  const decimales = absoluto >= 1000 ? 0 : absoluto >= 100 ? 1 : absoluto >= 1 ? 2 : 3
  return valor.toLocaleString('es-GT', { maximumFractionDigits: decimales })
}
