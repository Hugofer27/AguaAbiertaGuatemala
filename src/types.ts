export type Vista = 'mapa' | 'datos' | 'acerca'

export type Precision = 'publicada' | 'homonimo' | 'transcrita' | 'modelada'

export interface Fuente {
  id: string
  tipo: 'Conjunto de datos' | 'Documento' | 'Portal o servicio'
  titulo: string
  institucion: string
  institucion_detalle: string
  categoria: string
  tema: string
  anios: string
  anio_min: number | null
  anio_max: number | null
  cobertura: string
  parametros: string
  formato: string
  registros: string
  licencia: string
  acceso: string
  acceso_detalle: string
  descarga: string
  archivos: number
  url_fuente: string
  url_descarga: string
  sha256: string[]
  verificacion: string
  motagua_las_vacas: boolean
  destacado: boolean
  prioridad: number
  ids_alias: string[]
  notas: string
  capas: string[]
}

export interface Publicacion {
  id: string
  titulo: string
  autores: string
  anio: string
  fuente: string
  tipo: string
  url: string
  lugar: string
  anios_muestreo: string
  parametros: string
  resultados_numericos: string
  datos_crudos: string
  acceso: string
  motagua_las_vacas: boolean
  ids_alias: string[]
}

export interface Faltante {
  id: string
  institucion: string
  institucion_corta: string
  estado: string
  dato_esperado: string
  evidencia: string
  url_evidencia: string
  que_se_intento: string
  motivo: string
  solicitud_factible: string
  siguiente_paso: string
}

export interface CapaMeta {
  id: string
  titulo: string
  descripcion: string
  grupo: string
  geometria: 'punto' | 'linea' | 'poligono'
  tipo_dato: string
  precision: Precision
  fuente_ids: string[]
  visible: boolean
  archivo: string
  elementos: number
  fuera_de_guatemala: boolean
}

export interface Medicion {
  codigo: string
  parametro: string
  valor: number
  unidad: string
  fecha: string
  fuente_id: string
  control: string
  unidad_verificada: boolean
}

export interface Serie {
  titulo: string
  unidad: string
  puntos: { etiqueta: string; valor: number }[]
}

export interface SitioPropiedades {
  id: string
  capa: string
  nombre: string
  tipo: string
  institucion: string
  cuerpo_agua: string
  cuenca: string
  cuenca_oficial?: string
  departamento: string
  municipio: string
  fecha: string
  tipo_dato: string
  precision: Precision
  fuente_ids: string[]
  advertencia: string
  atributos: Record<string, string>
  mediciones?: Medicion[]
  serie?: Serie
  emision_t?: number
}

export interface Sitio {
  type: 'Feature'
  id: string
  geometry: { type: 'Point'; coordinates: [number, number] }
  properties: SitioPropiedades
}

export interface CuencaPropiedades {
  id: string
  capa: 'cuencas'
  nombre: string
  codigo: string
  vertiente: string
  area_km2: number
  fuente_ids: string[]
  puntos_por_capa: Record<string, number>
  fuentes_que_la_mencionan: number
  publicaciones_que_la_mencionan: number
  ejemplos_fuentes: string[]
  termino_busqueda: string
}

export interface Cuenca {
  type: 'Feature'
  id: string
  geometry: { type: 'Polygon' | 'MultiPolygon'; coordinates: unknown }
  properties: CuencaPropiedades
}

export interface Coleccion<T = unknown> {
  type: 'FeatureCollection'
  features: T[]
}

export interface Resumen {
  version: string
  fecha_corte: string
  fuentes: number
  conjuntos_de_datos: number
  documentos: number
  portales: number
  publicaciones: number
  publicaciones_acceso_abierto: number
  faltantes: number
  organizaciones: number
  archivos_originales: number
  bytes_originales: number
  fuentes_con_archivo: number
  motagua_las_vacas: number
  capas: Record<string, number>
  puntos_en_mapa: number
  mediciones: number
  parametros: number
  excluidos_del_mapa: { capa: string; nombre: string; motivo: string }[]
  controles_de_calidad: number
}

export interface Config {
  enlace_originales: string
}

export interface DatosApp {
  catalogo: Fuente[]
  faltantes: Faltante[]
  capas: CapaMeta[]
  colecciones: Record<string, Coleccion>
  resumen: Resumen
  config: Config
}

export type Seleccion =
  | { tipo: 'sitio'; sitio: Sitio }
  | { tipo: 'cuenca'; cuenca: Cuenca }
