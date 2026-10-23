import type { CapaMeta, Coleccion, Config, DatosApp, Faltante, Fuente, Publicacion, Resumen } from './types'

const BASE = './datos/'

async function getJson<T>(ruta: string): Promise<T> {
  const respuesta = await fetch(`${BASE}${ruta}`)
  if (!respuesta.ok) {
    throw new Error(`No se pudo cargar ${ruta} (${respuesta.status})`)
  }
  return respuesta.json() as Promise<T>
}

export async function cargarDatos(): Promise<DatosApp> {
  const [catalogo, faltantes, capas, resumen, config] = await Promise.all([
    getJson<Fuente[]>('app/catalogo.json'),
    getJson<Faltante[]>('app/faltantes.json'),
    getJson<CapaMeta[]>('app/capas.json'),
    getJson<Resumen>('resumen.json'),
    getJson<Config>('config.json').catch(() => ({ enlace_originales: '' })),
  ])
  const colecciones = Object.fromEntries(
    await Promise.all(capas.map(async (capa) => [capa.id, await getJson<Coleccion>(capa.archivo)] as const)),
  )
  return { catalogo, faltantes, capas, colecciones, resumen, config }
}

let publicaciones: Promise<Publicacion[]> | null = null

/** Las 1 494 publicaciones se cargan solo cuando se abre su pestaña. */
export function cargarPublicaciones(): Promise<Publicacion[]> {
  publicaciones ??= getJson<Publicacion[]>('app/publicaciones.json').catch((error: unknown) => {
    publicaciones = null
    throw error
  })
  return publicaciones
}

export function urlDatos(ruta: string): string {
  return `${BASE}${ruta}`
}
