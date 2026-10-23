import { useEffect, useMemo, useState } from 'react'
import { createPortal } from 'react-dom'
import { Download, ExternalLink, FileSearch, Map as MapIcon, Search, ShieldCheck, Star, X } from 'lucide-react'
import { cargarPublicaciones, urlDatos } from '../data'
import type { Config, Faltante, Fuente, Publicacion, Resumen } from '../types'
import { usePanelFocus } from '../usePanelFocus'

export type Pestana = 'conjuntos' | 'documentos' | 'portales' | 'publicaciones' | 'faltantes'

const PESTANAS: { id: Pestana; nombre: string; tipo?: Fuente['tipo'] }[] = [
  { id: 'conjuntos', nombre: 'Conjuntos de datos', tipo: 'Conjunto de datos' },
  { id: 'documentos', nombre: 'Documentos', tipo: 'Documento' },
  { id: 'portales', nombre: 'Portales', tipo: 'Portal o servicio' },
  { id: 'publicaciones', nombre: 'Publicaciones' },
  { id: 'faltantes', nombre: 'Datos faltantes' },
]

const TODAS = ''
const POR_PAGINA = 30

interface SourceLibraryProps {
  catalogo: Fuente[]
  faltantes: Faltante[]
  resumen: Resumen
  config: Config
  consulta?: string
  abrirId?: string | null
  onAbrirId: (id: string | null) => void
  onVerCapa: (capaId: string) => void
}

function normalizar(texto: string) {
  return texto.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLocaleLowerCase('es')
}

function opciones(valores: string[]) {
  return Array.from(new Set(valores.filter(Boolean))).sort((a, b) => a.localeCompare(b, 'es'))
}

export function pestanaDeId(id: string, catalogo: Fuente[]): Pestana | null {
  if (id.startsWith('GT-PUB')) return 'publicaciones'
  if (id.startsWith('FALT-')) return 'faltantes'
  const fuente = catalogo.find((f) => f.id === id || f.ids_alias.includes(id))
  return PESTANAS.find((p) => p.tipo === fuente?.tipo)?.id ?? null
}

export default function SourceLibrary({ catalogo, faltantes, resumen, config, consulta = '', abrirId, onAbrirId, onVerCapa }: SourceLibraryProps) {
  const [pestana, setPestana] = useState<Pestana>(() => (abrirId && pestanaDeId(abrirId, catalogo)) || 'conjuntos')
  const [texto, setTexto] = useState(consulta)
  const [institucion, setInstitucion] = useState(TODAS)
  const [tema, setTema] = useState(TODAS)
  const [acceso, setAcceso] = useState(TODAS)
  const [estado, setEstado] = useState(TODAS)
  const [soloMotagua, setSoloMotagua] = useState(false)
  const [soloArchivo, setSoloArchivo] = useState(false)
  const [soloMapa, setSoloMapa] = useState(false)
  const [orden, setOrden] = useState('destacados')
  const [limite, setLimite] = useState(POR_PAGINA)
  const [publicaciones, setPublicaciones] = useState<Publicacion[] | null>(null)
  const [errorPublicaciones, setErrorPublicaciones] = useState('')

  useEffect(() => setTexto(consulta), [consulta])
  useEffect(() => {
    if (abrirId) {
      const destino = pestanaDeId(abrirId, catalogo)
      if (destino) setPestana(destino)
    }
  }, [abrirId, catalogo])
  useEffect(() => setLimite(POR_PAGINA), [pestana, texto, institucion, tema, acceso, estado, soloMotagua, soloArchivo, soloMapa, orden])
  useEffect(() => {
    if (pestana !== 'publicaciones' || publicaciones) return
    cargarPublicaciones().then(setPublicaciones).catch(() => setErrorPublicaciones('No se pudieron cargar las publicaciones.'))
  }, [pestana, publicaciones])

  const tipo = PESTANAS.find((p) => p.id === pestana)?.tipo
  const delTipo = useMemo(() => catalogo.filter((f) => f.tipo === tipo), [catalogo, tipo])
  const filtros = useMemo(() => ({
    instituciones: opciones(delTipo.map((f) => f.institucion)),
    temas: opciones(delTipo.map((f) => f.tema)),
    accesos: opciones(delTipo.map((f) => f.acceso)),
    estados: opciones(faltantes.map((f) => f.estado)),
  }), [delTipo, faltantes])

  const q = normalizar(texto.trim())

  const fuentesFiltradas = useMemo(() => {
    const filas = delTipo.filter((f) => {
      const pajar = normalizar(`${f.titulo} ${f.institucion} ${f.institucion_detalle} ${f.cobertura} ${f.parametros} ${f.tema} ${f.id} ${f.ids_alias.join(' ')}`)
      return (!q || pajar.includes(q))
        && (!institucion || f.institucion === institucion)
        && (!tema || f.tema === tema)
        && (!acceso || f.acceso === acceso)
        && (!soloMotagua || f.motagua_las_vacas)
        && (!soloArchivo || f.descarga === 'Archivo descargado')
        && (!soloMapa || f.capas.length > 0)
    })
    return filas.sort((a, b) => {
      if (orden === 'recientes') return (b.anio_max ?? 0) - (a.anio_max ?? 0) || a.titulo.localeCompare(b.titulo, 'es')
      if (orden === 'nombre') return a.titulo.localeCompare(b.titulo, 'es')
      if (orden === 'institucion') return a.institucion.localeCompare(b.institucion, 'es') || a.titulo.localeCompare(b.titulo, 'es')
      return Number(b.destacado) - Number(a.destacado) || Number(b.capas.length > 0) - Number(a.capas.length > 0) || a.prioridad - b.prioridad || a.id.localeCompare(b.id)
    })
  }, [acceso, delTipo, institucion, orden, q, soloArchivo, soloMapa, soloMotagua, tema])

  const publicacionesFiltradas = useMemo(() => {
    if (!publicaciones) return []
    const filas = publicaciones.filter((p) => {
      const pajar = normalizar(`${p.titulo} ${p.autores} ${p.fuente} ${p.lugar} ${p.parametros} ${p.id} ${p.ids_alias.join(' ')}`)
      return (!q || pajar.includes(q)) && (!soloMotagua || p.motagua_las_vacas)
    })
    return filas.sort((a, b) => (orden === 'nombre' ? a.titulo.localeCompare(b.titulo, 'es') : Number(b.anio || 0) - Number(a.anio || 0)))
  }, [orden, publicaciones, q, soloMotagua])

  const faltantesFiltrados = useMemo(() => faltantes.filter((f) => {
    const pajar = normalizar(`${f.institucion} ${f.dato_esperado} ${f.motivo} ${f.siguiente_paso}`)
    return (!q || pajar.includes(q)) && (!estado || f.estado === estado)
  }), [estado, faltantes, q])

  const conteo = { conjuntos: resumen.conjuntos_de_datos, documentos: resumen.documentos, portales: resumen.portales, publicaciones: resumen.publicaciones, faltantes: resumen.faltantes }
  const visibles = pestana === 'publicaciones' ? publicacionesFiltradas.length : pestana === 'faltantes' ? faltantesFiltrados.length : fuentesFiltradas.length

  const limpiar = () => {
    setTexto(''); setInstitucion(TODAS); setTema(TODAS); setAcceso(TODAS); setEstado(TODAS)
    setSoloMotagua(false); setSoloArchivo(false); setSoloMapa(false); setOrden('destacados')
  }

  const abierto = abrirId
    ? catalogo.find((f) => f.id === abrirId || f.ids_alias.includes(abrirId)) ?? publicaciones?.find((p) => p.id === abrirId || p.ids_alias.includes(abrirId)) ?? null
    : null

  const csv = pestana === 'publicaciones' ? 'catalogo/publicaciones.csv' : pestana === 'faltantes' ? 'catalogo/faltantes.csv' : 'catalogo/fuentes.csv'

  return (
    <section className="vista-datos" aria-labelledby="titulo-datos">
      <header className="vista-cabeza">
        <div>
          <h1 id="titulo-datos">Datos</h1>
          <p>Todo lo que se encontró sobre el agua en Guatemala: conjuntos de datos, informes, portales y publicaciones, con su procedencia. Lo que no se pudo obtener también está registrado.</p>
        </div>
        <a className="boton secundario" href={urlDatos(csv)} download><Download aria-hidden="true" /> Descargar esta lista (CSV)</a>
      </header>

      <div className="pestanas" role="tablist" aria-label="Tipo de registro">
        {PESTANAS.map((p) => (
          <button key={p.id} role="tab" id={`pestana-${p.id}`} aria-selected={pestana === p.id} aria-controls="panel-datos" className={pestana === p.id ? 'activa' : ''} onClick={() => setPestana(p.id)}>
            {p.nombre} <span className="cuenta">{conteo[p.id].toLocaleString('es-GT')}</span>
          </button>
        ))}
      </div>

      <div id="panel-datos" role="tabpanel" aria-labelledby={`pestana-${pestana}`} className="panel-datos">
        <div className="filtros">
          <label className="campo-busqueda">
            <Search aria-hidden="true" />
            <span className="sr-only">Buscar</span>
            <input type="search" value={texto} onChange={(e) => setTexto(e.target.value)} placeholder={pestana === 'publicaciones' ? 'Buscar por título, autor, lugar…' : 'Buscar por título, institución, río, lago, ID…'} />
          </label>
          {tipo && (
            <>
              <Selector etiqueta="Institución" valor={institucion} opciones={filtros.instituciones} onCambio={setInstitucion} />
              <Selector etiqueta="Tema" valor={tema} opciones={filtros.temas} onCambio={setTema} />
              <Selector etiqueta="Acceso" valor={acceso} opciones={filtros.accesos} onCambio={setAcceso} />
            </>
          )}
          {pestana === 'faltantes' && <Selector etiqueta="Estado" valor={estado} opciones={filtros.estados} onCambio={setEstado} />}
          {pestana !== 'faltantes' && (
            <label className="selector">
              <span>Ordenar</span>
              <select value={orden} onChange={(e) => setOrden(e.target.value)}>
                {tipo && <option value="destacados">Destacados primero</option>}
                <option value="recientes">Más recientes</option>
                <option value="nombre">Nombre</option>
                {tipo && <option value="institucion">Institución</option>}
              </select>
            </label>
          )}
          <div className="interruptores">
            {pestana !== 'faltantes' && <Interruptor etiqueta="Motagua / Las Vacas" valor={soloMotagua} onCambio={setSoloMotagua} />}
            {tipo && <Interruptor etiqueta="Con archivo descargado" valor={soloArchivo} onCambio={setSoloArchivo} />}
            {tipo && <Interruptor etiqueta="En el mapa" valor={soloMapa} onCambio={setSoloMapa} />}
          </div>
        </div>

        <p className="conteo-resultados" role="status" aria-live="polite">{visibles.toLocaleString('es-GT')} resultados</p>

        {pestana === 'faltantes' ? (
          <ul className="lista-faltantes">
            {faltantesFiltrados.map((f) => <TarjetaFaltante key={f.id} faltante={f} />)}
          </ul>
        ) : pestana === 'publicaciones' ? (
          publicaciones === null ? (
            <p className="texto-suave" role="status">{errorPublicaciones || 'Cargando publicaciones…'}</p>
          ) : (
            <ul className="lista-registros">
              {publicacionesFiltradas.slice(0, limite).map((p) => (
                <li key={p.id}>
                  <button className="registro" onClick={() => onAbrirId(p.id)}>
                    <span className="registro-titulo">{p.titulo}</span>
                    <span className="registro-meta">{[p.autores.split(';')[0], p.anio, p.fuente].filter(Boolean).join(' · ')}</span>
                    <span className="registro-etiquetas"><span>{p.tipo}</span>{p.acceso && <span>{p.acceso}</span>}</span>
                  </button>
                </li>
              ))}
            </ul>
          )
        ) : (
          <ul className="lista-registros">
            {fuentesFiltradas.slice(0, limite).map((f) => (
              <li key={f.id}>
                <button className="registro" onClick={() => onAbrirId(f.id)}>
                  <span className="registro-titulo">{f.destacado && <Star aria-label="Destacado" className="destacado" />}{f.titulo}</span>
                  <span className="registro-meta">{[f.institucion, f.anios, f.formato].filter(Boolean).join(' · ')}</span>
                  <span className="registro-etiquetas">
                    <span>{f.tema}</span>
                    {f.descarga === 'Archivo descargado' && <span className="ok"><ShieldCheck aria-hidden="true" /> Archivo verificado</span>}
                    {f.capas.length > 0 && <span className="mapa"><MapIcon aria-hidden="true" /> En el mapa</span>}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}

        {visibles === 0 && (publicaciones !== null || pestana !== 'publicaciones') && (
          <div className="vacio">
            <FileSearch aria-hidden="true" />
            <h2>No hay resultados con esos filtros</h2>
            <button className="boton" onClick={limpiar}>Quitar filtros</button>
          </div>
        )}
        {pestana !== 'faltantes' && visibles > limite && (
          <button className="boton secundario mas" onClick={() => setLimite((l) => l + POR_PAGINA * 2)}>
            Mostrar más ({(visibles - limite).toLocaleString('es-GT')} restantes)
          </button>
        )}
      </div>

      {abierto && <FichaRegistro registro={abierto} config={config} onClose={() => onAbrirId(null)} onVerCapa={onVerCapa} />}
    </section>
  )
}

function Selector({ etiqueta, valor, opciones: lista, onCambio }: { etiqueta: string; valor: string; opciones: string[]; onCambio: (v: string) => void }) {
  return (
    <label className="selector">
      <span>{etiqueta}</span>
      <select value={valor} onChange={(e) => onCambio(e.target.value)}>
        <option value="">Todas</option>
        {lista.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    </label>
  )
}

function Interruptor({ etiqueta, valor, onCambio }: { etiqueta: string; valor: boolean; onCambio: (v: boolean) => void }) {
  return (
    <label className="interruptor">
      <input type="checkbox" checked={valor} onChange={(e) => onCambio(e.target.checked)} />
      <span>{etiqueta}</span>
    </label>
  )
}

function TarjetaFaltante({ faltante: f }: { faltante: Faltante }) {
  return (
    <li className="tarjeta-faltante">
      <div className="faltante-cabeza">
        <h3>{f.institucion}</h3>
        <span className="insignia neutra">{f.estado}</span>
      </div>
      <dl>
        <div><dt>Qué falta</dt><dd>{f.dato_esperado}</dd></div>
        <div><dt>Por qué no se obtuvo</dt><dd>{f.motivo}</dd></div>
        <div><dt>Cómo pedirlo</dt><dd>{f.siguiente_paso}</dd></div>
      </dl>
      {f.url_evidencia.startsWith('http') && (
        <a className="enlace" href={f.url_evidencia.split(' ')[0]} target="_blank" rel="noreferrer">Evidencia de que existe <ExternalLink aria-hidden="true" /></a>
      )}
    </li>
  )
}

function esFuente(r: Fuente | Publicacion): r is Fuente {
  return 'institucion' in r
}

function FichaRegistro({ registro, config, onClose, onVerCapa }: { registro: Fuente | Publicacion; config: Config; onClose: () => void; onVerCapa: (id: string) => void }) {
  const panelRef = usePanelFocus<HTMLElement>(onClose, true)
  const fuente = esFuente(registro) ? registro : null
  const pub = esFuente(registro) ? null : registro
  const filas: [string, string][] = fuente
    ? [
        ['Institución', fuente.institucion_detalle],
        ['Tipo', fuente.tipo],
        ['Tema', fuente.tema],
        ['Años', fuente.anios],
        ['Cobertura', fuente.cobertura],
        ['Parámetros', fuente.parametros],
        ['Formato', fuente.formato],
        ['Registros', fuente.registros],
        ['Licencia', fuente.licencia],
        ['Acceso', fuente.acceso_detalle],
        ['Descarga', fuente.descarga + (fuente.archivos > 1 ? ` (${fuente.archivos} archivos)` : '')],
        ['Verificación', fuente.verificacion],
      ]
    : [
        ['Autores', pub!.autores],
        ['Año', pub!.anio],
        ['Revista o institución', pub!.fuente],
        ['Tipo', pub!.tipo],
        ['Lugar de estudio', pub!.lugar],
        ['Años de muestreo', pub!.anios_muestreo],
        ['Parámetros', pub!.parametros],
        ['Resultados numéricos', pub!.resultados_numericos],
        ['Datos crudos', pub!.datos_crudos],
        ['Acceso', pub!.acceso],
      ]
  const url = fuente ? fuente.url_fuente : pub!.url
  return createPortal(
    <>
      <div className="velo" aria-hidden="true" onClick={onClose} />
      <aside ref={panelRef} className="ficha-registro" role="dialog" aria-modal="true" aria-labelledby="registro-titulo" tabIndex={-1}>
        <header className="ficha-cabeza">
          <div>
            <span className="ficha-tipo">{registro.id}{registro.ids_alias.length > 0 && ` · también ${registro.ids_alias.join(', ')}`}</span>
            <h2 id="registro-titulo">{registro.titulo}</h2>
          </div>
          <button className="boton-icono" onClick={onClose} aria-label="Cerrar ficha"><X aria-hidden="true" /></button>
        </header>
        <div className="ficha-cuerpo">
          <div className="acciones">
            {url?.startsWith('http') && <a className="boton" href={url} target="_blank" rel="noreferrer"><ExternalLink aria-hidden="true" /> {fuente ? 'Fuente oficial' : 'Abrir publicación'}</a>}
            {fuente?.url_descarga && fuente.url_descarga !== url && <a className="boton secundario" href={fuente.url_descarga} target="_blank" rel="noreferrer"><Download aria-hidden="true" /> Descarga directa</a>}
            {fuente?.descarga === 'Archivo descargado' && config.enlace_originales && <a className="boton secundario" href={config.enlace_originales} target="_blank" rel="noreferrer"><Download aria-hidden="true" /> Copia de respaldo</a>}
            {fuente && fuente.capas.length > 0 && <button className="boton secundario" onClick={() => onVerCapa(fuente.capas[0])}><MapIcon aria-hidden="true" /> Ver en el mapa</button>}
          </div>
          <dl className="datos-clave apilado">
            {filas.filter(([, v]) => v && v.trim()).map(([k, v]) => <div key={k}><dt>{k}</dt><dd>{v}</dd></div>)}
          </dl>
          {fuente?.notas && <div className="aviso"><p>{fuente.notas}</p></div>}
          {fuente && fuente.sha256.length > 0 && (
            <details className="tecnico">
              <summary>Huella SHA-256 de los archivos ({fuente.sha256.length})</summary>
              <ul>{fuente.sha256.map((h) => <li key={h}><code>{h}</code></li>)}</ul>
              <p className="nota-pie">Sirve para comprobar que una copia es idéntica al archivo descargado. Ver datos/manifiesto/originales.csv.</p>
            </details>
          )}
        </div>
      </aside>
    </>,
    document.body,
  )
}
