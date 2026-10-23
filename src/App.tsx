import { lazy, Suspense, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { AlertTriangle, Droplets, Eye, EyeOff, Map as MapIcon, Search, Table2, Waves, X, FileText } from 'lucide-react'
import { cargarDatos } from './data'
import { ENFOQUES, type MapaBase } from './capas'
import { NOMBRE, VISTAS, fechaCorte, numero } from './textos'
import type { Cuenca, DatosApp, Seleccion, Sitio, Vista } from './types'
import AboutView from './components/AboutView'
import BasinPanel from './components/BasinPanel'
import DetailPanel from './components/DetailPanel'
import LayerPanel from './components/LayerPanel'
import SitesTable from './components/SitesTable'
import SourceLibrary from './components/SourceLibrary'
import type { EstadoMapa } from './components/MapView'

const MapView = lazy(() => import('./components/MapView'))

interface Ruta {
  vista: Vista
  params: URLSearchParams
}

function leerRuta(): Ruta {
  const [camino, consulta = ''] = window.location.hash.replace(/^#\/?/, '').split('?')
  const vista = (Object.keys(VISTAS) as Vista[]).includes(camino as Vista) ? (camino as Vista) : 'mapa'
  return { vista, params: new URLSearchParams(consulta) }
}

function hashDe(vista: Vista, params: Record<string, string | null | undefined> = {}) {
  const consulta = new URLSearchParams(Object.entries(params).filter(([, v]) => v) as [string, string][]).toString()
  return `#/${vista}${consulta ? `?${consulta}` : ''}`
}

function prefiereOscuro() {
  const tema = document.documentElement.dataset.theme
  if (tema) return tema === 'dark'
  return typeof window.matchMedia === 'function' && window.matchMedia('(prefers-color-scheme: dark)').matches
}

export default function App() {
  const [datos, setDatos] = useState<DatosApp | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [intento, setIntento] = useState(0)
  const [ruta, setRuta] = useState<Ruta>(leerRuta)

  useEffect(() => {
    setError(null)
    cargarDatos().then(setDatos).catch((motivo: unknown) => setError(motivo instanceof Error ? motivo.message : 'No se pudieron cargar los datos.'))
  }, [intento])

  useEffect(() => {
    const alCambiar = () => setRuta(leerRuta())
    window.addEventListener('hashchange', alCambiar)
    return () => window.removeEventListener('hashchange', alCambiar)
  }, [])

  const navegar = useCallback((vista: Vista, params?: Record<string, string | null | undefined>, reemplazar = false) => {
    const destino = hashDe(vista, params)
    if (reemplazar) {
      try {
        window.history.replaceState(null, '', destino)
      } catch {
        // Algunos marcos incrustados bloquean el historial; el hash sigue funcionando.
        window.location.hash = destino
      }
      setRuta(leerRuta())
    } else if (window.location.hash !== destino) {
      window.location.hash = destino
    } else {
      setRuta(leerRuta())
    }
  }, [])

  if (error) return <PantallaError mensaje={error} onReintentar={() => setIntento((n) => n + 1)} />
  if (!datos) return <PantallaCarga />
  return <Portal datos={datos} ruta={ruta} navegar={navegar} />
}

function Portal({ datos, ruta, navegar }: { datos: DatosApp; ruta: Ruta; navegar: (v: Vista, p?: Record<string, string | null | undefined>, r?: boolean) => void }) {
  const [visibles, setVisibles] = useState<Record<string, boolean>>(() => Object.fromEntries(datos.capas.map((c) => [c.id, c.visible])))
  const [mapaBase, setMapaBase] = useState<MapaBase>(() => (prefiereOscuro() ? 'oscuro' : 'claro'))
  const [resaltarRios, setResaltarRios] = useState(true)
  const [enfoque, setEnfoque] = useState<{ id: string; vez: number } | null>(null)
  const [modoLimpio, setModoLimpio] = useState(false)
  const [comoTabla, setComoTabla] = useState(false)
  const [estadoMapa, setEstadoMapa] = useState<EstadoMapa>('cargando')

  const sitios = useMemo(
    () => datos.capas.filter((c) => c.geometria === 'punto').flatMap((c) => (datos.colecciones[c.id]?.features as Sitio[]) ?? []),
    [datos],
  )
  const cuencas = useMemo(() => (datos.colecciones.cuencas?.features as Cuenca[]) ?? [], [datos])

  const idSitio = ruta.vista === 'mapa' ? ruta.params.get('sitio') : null
  const idCuenca = ruta.vista === 'mapa' ? ruta.params.get('cuenca') : null
  const seleccion: Seleccion | null = useMemo(() => {
    const sitio = idSitio ? sitios.find((s) => s.id === idSitio) : undefined
    if (sitio) return { tipo: 'sitio', sitio }
    const cuenca = idCuenca ? cuencas.find((c) => c.id === idCuenca) : undefined
    return cuenca ? { tipo: 'cuenca', cuenca } : null
  }, [cuencas, idCuenca, idSitio, sitios])

  // Si se abre un enlace a un punto de una capa apagada, se enciende la capa.
  useEffect(() => {
    if (seleccion?.tipo !== 'sitio') return
    const capa = seleccion.sitio.properties.capa
    setVisibles((v) => (v[capa] ? v : { ...v, [capa]: true }))
  }, [seleccion])

  const seleccionar = useCallback((s: Seleccion | null) => {
    navegar('mapa', s?.tipo === 'sitio' ? { sitio: s.sitio.id } : s?.tipo === 'cuenca' ? { cuenca: s.cuenca.id } : {}, true)
  }, [navegar])
  const estadoEstable = useCallback((e: EstadoMapa) => setEstadoMapa(e), [])
  const abrirFuente = useCallback((id: string | null) => navegar('datos', { id, q: ruta.params.get('q') }), [navegar, ruta.params])
  const verCapa = useCallback((capaId: string) => {
    setVisibles((v) => ({ ...v, [capaId]: true }))
    setComoTabla(false)
    navegar('mapa')
  }, [navegar])

  const capaSeleccion = seleccion?.tipo === 'sitio' ? datos.capas.find((c) => c.id === seleccion.sitio.properties.capa) : undefined

  return (
    <div className={`portal en-${ruta.vista} ${modoLimpio && ruta.vista === 'mapa' ? 'modo-limpio' : ''}`}>
      <BarraSuperior
        vista={ruta.vista}
        datos={datos}
        sitios={sitios}
        cuencas={cuencas}
        onVista={(v) => navegar(v)}
        onSitio={(s) => { setComoTabla(false); seleccionar({ tipo: 'sitio', sitio: s }) }}
        onCuenca={(c) => { setComoTabla(false); setVisibles((v) => ({ ...v, cuencas: true })); seleccionar({ tipo: 'cuenca', cuenca: c }) }}
        onFuente={(id) => abrirFuente(id)}
        onBuscarEnDatos={(q) => navegar('datos', { q })}
      />

      <main id="contenido" className="escenario">
        <section className="vista-mapa" hidden={ruta.vista !== 'mapa'} aria-label="Mapa">
          <div className={`mapa-area ${comoTabla ? 'oculto' : ''}`}>
            <Suspense fallback={<div className="mapa-cargando" role="status"><Droplets aria-hidden="true" /> Cargando el mapa…</div>}>
              <MapView
                capas={datos.capas}
                colecciones={datos.colecciones}
                visibles={visibles}
                mapaBase={mapaBase}
                resaltarRios={resaltarRios}
                enfoque={enfoque}
                seleccion={seleccion}
                oscuro={mapaBase === 'oscuro'}
                onSeleccion={seleccionar}
                onEstado={estadoEstable}
              />
            </Suspense>

            {!modoLimpio && (
              <>
                <nav className="enfoques" aria-label="Enfoque territorial">
                  {ENFOQUES.map((e) => (
                    <button key={e.id} className={enfoque?.id === e.id ? 'activo' : ''} onClick={() => setEnfoque({ id: e.id, vez: Date.now() })}>{e.nombre}</button>
                  ))}
                </nav>
                <LayerPanel
                  capas={datos.capas}
                  visibles={visibles}
                  mapaBase={mapaBase}
                  resaltarRios={resaltarRios}
                  onCambio={(id, valor) => setVisibles((v) => ({ ...v, [id]: valor }))}
                  onMapaBase={setMapaBase}
                  onResaltarRios={setResaltarRios}
                />
              </>
            )}
            {estadoMapa === 'respaldo' && (
              <p className="estado-mapa" role="status"><AlertTriangle aria-hidden="true" /> El mapa base no está disponible; los datos siguen visibles.</p>
            )}
          </div>

          {comoTabla && <SitesTable capas={datos.capas} colecciones={datos.colecciones} visibles={visibles} onAbrir={(s) => { setComoTabla(false); seleccionar({ tipo: 'sitio', sitio: s }) }} />}

          <div className="herramientas-mapa">
            {!modoLimpio && (
              <button className="boton-flotante" onClick={() => setComoTabla((v) => !v)} aria-pressed={comoTabla}>
                {comoTabla ? <><MapIcon aria-hidden="true" /> Ver mapa</> : <><Table2 aria-hidden="true" /> Ver tabla</>}
              </button>
            )}
            {!comoTabla && (
              <button className="boton-flotante" onClick={() => setModoLimpio((v) => !v)} aria-pressed={modoLimpio}>
                {modoLimpio ? <><Eye aria-hidden="true" /> Mostrar paneles</> : <><EyeOff aria-hidden="true" /> Modo limpio</>}
              </button>
            )}
          </div>

          {seleccion && !modoLimpio && !comoTabla && (seleccion.tipo === 'sitio' ? (
            <DetailPanel
              key={seleccion.sitio.id}
              sitio={seleccion.sitio}
              capa={capaSeleccion}
              catalogo={datos.catalogo}
              onClose={() => seleccionar(null)}
              onAbrirFuente={(id) => abrirFuente(id)}
            />
          ) : (
            <BasinPanel
              key={seleccion.cuenca.id}
              cuenca={seleccion.cuenca}
              capas={datos.capas}
              catalogo={datos.catalogo}
              onClose={() => seleccionar(null)}
              onBuscarEnDatos={(q) => navegar('datos', { q })}
              onAbrirFuente={(id) => abrirFuente(id)}
              onActivarCapa={(id) => setVisibles((v) => ({ ...v, [id]: true }))}
            />
          ))}
        </section>

        {ruta.vista === 'datos' && (
          <SourceLibrary
            catalogo={datos.catalogo}
            faltantes={datos.faltantes}
            resumen={datos.resumen}
            config={datos.config}
            consulta={ruta.params.get('q') ?? ''}
            abrirId={ruta.params.get('id')}
            onAbrirId={(id) => abrirFuente(id)}
            onVerCapa={verCapa}
          />
        )}
        {ruta.vista === 'acerca' && <AboutView resumen={datos.resumen} capas={datos.capas} config={datos.config} />}
      </main>
    </div>
  )
}

interface BarraProps {
  vista: Vista
  datos: DatosApp
  sitios: Sitio[]
  cuencas: Cuenca[]
  onVista: (v: Vista) => void
  onSitio: (s: Sitio) => void
  onCuenca: (c: Cuenca) => void
  onFuente: (id: string) => void
  onBuscarEnDatos: (q: string) => void
}

function normalizar(texto: string) {
  return texto.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLocaleLowerCase('es')
}

function BarraSuperior({ vista, datos, sitios, cuencas, onVista, onSitio, onCuenca, onFuente, onBuscarEnDatos }: BarraProps) {
  const [texto, setTexto] = useState('')
  const [abierta, setAbierta] = useState(false)
  const [buscadorMovil, setBuscadorMovil] = useState(false)
  const contenedor = useRef<HTMLDivElement | null>(null)
  const q = normalizar(texto.trim())

  const resultados = useMemo(() => {
    if (q.length < 2) return { sitios: [], cuencas: [], fuentes: [] }
    return {
      sitios: sitios.filter((s) => normalizar(`${s.properties.nombre} ${s.properties.municipio} ${s.properties.cuerpo_agua}`).includes(q)).slice(0, 6),
      cuencas: cuencas.filter((c) => normalizar(c.properties.nombre).includes(q)).slice(0, 3),
      fuentes: datos.catalogo.filter((f) => normalizar(`${f.titulo} ${f.institucion} ${f.id} ${f.ids_alias.join(' ')}`).includes(q)).slice(0, 5),
    }
  }, [cuencas, datos.catalogo, q, sitios])
  const total = resultados.sitios.length + resultados.cuencas.length + resultados.fuentes.length

  useEffect(() => {
    const cerrar = (e: MouseEvent) => {
      if (contenedor.current && !contenedor.current.contains(e.target as Node)) setAbierta(false)
    }
    document.addEventListener('mousedown', cerrar)
    return () => document.removeEventListener('mousedown', cerrar)
  }, [])

  const elegir = (accion: () => void) => {
    accion()
    setAbierta(false)
    setBuscadorMovil(false)
    setTexto('')
  }

  return (
    <header className="barra">
      <a className="marca" href="#/mapa" aria-label={`${NOMBRE}, inicio`}>
        <Waves aria-hidden="true" />
        <span>Agua Abierta <b>Guatemala</b></span>
      </a>
      <nav className="navegacion" aria-label="Secciones">
        {(Object.keys(VISTAS) as Vista[]).map((v) => (
          <button key={v} className={vista === v ? 'activa' : ''} aria-current={vista === v ? 'page' : undefined} onClick={() => onVista(v)}>{VISTAS[v]}</button>
        ))}
      </nav>
      <div ref={contenedor} className={`buscador ${buscadorMovil ? 'abierto-movil' : ''}`}>
        <button className="buscador-abrir boton-icono" onClick={() => setBuscadorMovil(true)} aria-label="Buscar"><Search aria-hidden="true" /></button>
        <label className="campo-busqueda">
          <Search aria-hidden="true" />
          <span className="sr-only">Buscar en el mapa y en el catálogo</span>
          <input
            type="search"
            value={texto}
            onChange={(e) => { setTexto(e.target.value); setAbierta(true) }}
            onFocus={() => setAbierta(true)}
            onKeyDown={(e) => {
              if (e.key === 'Escape') { setAbierta(false); setBuscadorMovil(false) }
              if (e.key === 'Enter' && texto.trim()) elegir(() => onBuscarEnDatos(texto.trim()))
            }}
            placeholder="Buscar río, lago, municipio, fuente…"
            autoComplete="off"
          />
          {buscadorMovil && <button className="boton-icono" onClick={() => setBuscadorMovil(false)} aria-label="Cerrar búsqueda"><X aria-hidden="true" /></button>}
        </label>
        {abierta && q.length >= 2 && (
          <div className="resultados-busqueda" role="region" aria-label="Resultados de búsqueda">
            {resultados.sitios.length > 0 && <p className="grupo-resultados">En el mapa</p>}
            {resultados.sitios.map((s) => (
              <button key={s.id} onClick={() => elegir(() => onSitio(s))}>
                <MapIcon aria-hidden="true" />
                <span><strong>{s.properties.nombre}</strong><small>{[s.properties.tipo, s.properties.municipio].filter(Boolean).join(' · ')}</small></span>
              </button>
            ))}
            {resultados.cuencas.map((c) => (
              <button key={c.id} onClick={() => elegir(() => onCuenca(c))}>
                <Waves aria-hidden="true" />
                <span><strong>Cuenca {c.properties.nombre}</strong><small>Vertiente del {c.properties.vertiente}</small></span>
              </button>
            ))}
            {resultados.fuentes.length > 0 && <p className="grupo-resultados">En el catálogo</p>}
            {resultados.fuentes.map((f) => (
              <button key={f.id} onClick={() => elegir(() => onFuente(f.id))}>
                <FileText aria-hidden="true" />
                <span><strong>{f.titulo}</strong><small>{f.institucion} · {f.tipo}</small></span>
              </button>
            ))}
            {total === 0 && <p className="sin-resultados">Sin coincidencias en el mapa ni en los títulos.</p>}
            <button className="buscar-todo" onClick={() => elegir(() => onBuscarEnDatos(texto.trim()))}>
              <Search aria-hidden="true" /><span><strong>Buscar “{texto.trim()}” en todo el catálogo</strong><small>Incluye publicaciones y documentos</small></span>
            </button>
          </div>
        )}
      </div>
      <p className="corte">Datos al {fechaCorte(datos.resumen.fecha_corte)} · {numero(datos.resumen.fuentes + datos.resumen.publicaciones)} registros</p>
    </header>
  )
}

function PantallaCarga() {
  return (
    <main className="pantalla-estado" aria-live="polite">
      <Droplets aria-hidden="true" />
      <p>Cargando {NOMBRE}…</p>
    </main>
  )
}

function PantallaError({ mensaje, onReintentar }: { mensaje: string; onReintentar: () => void }) {
  return (
    <main className="pantalla-estado error" role="alert">
      <AlertTriangle aria-hidden="true" />
      <h1>No se pudieron cargar los datos</h1>
      <p>{mensaje}</p>
      <p>Si abrió el archivo index.html directamente, use un servidor local (vea el README).</p>
      <button className="boton" onClick={onReintentar}>Reintentar</button>
    </main>
  )
}
