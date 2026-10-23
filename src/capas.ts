import type { StyleSpecification } from 'maplibre-gl'

/**
 * Presentación de cada capa del mapa. Los datos y metadatos vienen de
 * datos/app/capas.json; aquí solo se define cómo se dibujan.
 * Para agregar una capa: genere su GeoJSON en el pipeline y añada aquí su estilo.
 */

export interface EstiloCapa {
  color: string
  /** Radio base del círculo a zoom 10 (puntos) o grosor (líneas). */
  tamano: number
  minzoom?: number
  orden: number
}

// Paleta inspirada en Okabe-Ito, distinguible con daltonismo frecuente.
export const ESTILOS: Record<string, EstiloCapa> = {
  monitoreo_insivumeh: { color: '#0072B2', tamano: 6.5, orden: 1 },
  caudales_insivumeh: { color: '#009E73', tamano: 6.5, orden: 2 },
  usac_las_vacas: { color: '#D55E00', tamano: 6, orden: 3 },
  acidificacion_marn: { color: '#CC79A7', tamano: 6.5, orden: 4 },
  atitlan_wqp: { color: '#56B4E9', tamano: 7, orden: 5 },
  ptar_hydrowaste: { color: '#8C6D31', tamano: 6.5, orden: 6 },
  wpdx: { color: '#E69F00', tamano: 4.5, orden: 7 },
  plasticos: { color: '#7A5195', tamano: 4, orden: 8 },
  clima_nasa: { color: '#999933', tamano: 7, orden: 9 },
  estaciones_meteo: { color: '#6B7A80', tamano: 4.5, orden: 10 },
  gemstat_mexico: { color: '#882255', tamano: 4, orden: 11 },
  rios_motagua: { color: '#2B7BB9', tamano: 1, orden: 12 },
  lagos: { color: '#7FC3E0', tamano: 1, orden: 13 },
  cuencas: { color: '#0A706C', tamano: 1, orden: 14 },
}

export const GRUPOS = ['Monitoreo del agua', 'Presiones e infraestructura', 'Clima', 'Territorio', 'Contexto regional']

export interface Enfoque {
  id: string
  nombre: string
  limites: [[number, number], [number, number]]
}

export const ENFOQUES: Enfoque[] = [
  { id: 'guatemala', nombre: 'Toda Guatemala', limites: [[-92.3, 13.7], [-88.2, 17.85]] },
  { id: 'motagua', nombre: 'Motagua y Las Vacas', limites: [[-90.95, 14.5], [-88.2, 15.8]] },
  { id: 'atitlan', nombre: 'Atitlán', limites: [[-91.4, 14.56], [-91.0, 14.86]] },
  { id: 'amatitlan', nombre: 'Amatitlán', limites: [[-90.75, 14.4], [-90.45, 14.66]] },
  { id: 'izabal', nombre: 'Izabal y Río Dulce', limites: [[-89.6, 15.2], [-88.6, 15.9]] },
  { id: 'costa-sur', nombre: 'Costa Sur', limites: [[-92.25, 13.75], [-90.0, 14.8]] },
]

/** Fondo blanco sin mosaicos externos: solo se ven las capas propias. Sirve para imprimir y funciona sin internet. */
const ESTILO_BLANCO: StyleSpecification = {
  version: 8,
  name: 'Blanco',
  sources: {},
  layers: [{ id: 'fondo', type: 'background', paint: { 'background-color': '#ffffff' } }],
}

/** `estilo` es la URL de un estilo de mosaicos o un estilo completo. */
export const MAPAS_BASE = {
  claro: { nombre: 'Claro', estilo: 'https://tiles.openfreemap.org/styles/positron' },
  blanco: { nombre: 'Blanco', estilo: ESTILO_BLANCO },
  relieve: { nombre: 'Relieve', estilo: 'https://tiles.openfreemap.org/styles/liberty' },
  oscuro: { nombre: 'Oscuro', estilo: 'https://tiles.openfreemap.org/styles/dark' },
} as const

export type MapaBase = keyof typeof MAPAS_BASE

export function estiloDe(capaId: string): EstiloCapa {
  return ESTILOS[capaId] ?? { color: '#555555', tamano: 5, orden: 99 }
}
