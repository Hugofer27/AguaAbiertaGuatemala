import { lazy, Suspense, useCallback, useEffect, useMemo, useState } from 'react'
import {
  BookOpen,
  Database,
  Droplets,
  FileText,
  FolderOpen,
  HelpCircle,
  Layers3,
  Map,
  Menu,
  Search,
  TriangleAlert,
  X,
} from 'lucide-react'
import { loadAppData } from './data'
import type { AppData, CatalogItem, ViewName, WaterFeature } from './types'
import DetailPanel from './components/DetailPanel'
import LayerPanel, { type BasemapId } from './components/LayerPanel'
import SourceLibrary from './components/SourceLibrary'

const INITIAL_LAYERS = { monitoring: true, lakes: true, climate: true }
const NATURAL_MAP_STYLE = 'https://tiles.openfreemap.org/styles/liberty'
const MapView = lazy(() => import('./components/MapView'))

export default function App() {
  const [data, setData] = useState<AppData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [view, setView] = useState<ViewName>('explore')
  const [mobileNav, setMobileNav] = useState(false)
  const [selectedFeature, setSelectedFeature] = useState<WaterFeature | null>(null)
  const [layers, setLayers] = useState<Record<string, boolean>>(INITIAL_LAYERS)
  const [focusFeatureId, setFocusFeatureId] = useState<string | null>(null)
  const [mapStatus, setMapStatus] = useState<'loading' | 'ready' | 'fallback'>('loading')
  const [showTable, setShowTable] = useState(false)
  const [libraryQuery, setLibraryQuery] = useState('')
  const [loadAttempt, setLoadAttempt] = useState(0)

  useEffect(() => {
    setError(null)
    loadAppData().then(setData).catch((reason: unknown) => {
      setError(reason instanceof Error ? reason.message : 'No se pudieron cargar los datos del portal.')
    })
  }, [loadAttempt])

  const changeView = (next: ViewName) => {
    setView(next)
    setMobileNav(false)
  }

  if (error) return <LoadError message={error} onRetry={() => setLoadAttempt((value) => value + 1)} />
  if (!data) return <LoadingScreen />

  return (
    <div className="app-shell">
      <Navigation current={view} open={mobileNav} onToggle={() => setMobileNav((value) => !value)} onChange={changeView} />
      <main id="contenido" className="main-stage">
        {view === 'explore' && (
          <ExploreView
            data={data}
            selectedFeature={selectedFeature}
            layers={layers}
            focusFeatureId={focusFeatureId}
            mapStatus={mapStatus}
            showTable={showTable}
            onLayerChange={(id, value) => setLayers((current) => ({ ...current, [id]: value }))}
            onSelect={(feature) => {
              setSelectedFeature(feature)
              setFocusFeatureId(String(feature.id))
            }}
            onCloseDetail={() => {
              setSelectedFeature(null)
              setFocusFeatureId(null)
            }}
            onStatus={setMapStatus}
            onToggleTable={() => setShowTable((value) => !value)}
            onOpenLibrary={(query) => {
              setLibraryQuery(query)
              changeView('library')
            }}
          />
        )}
        {view === 'library' && <SourceLibrary catalog={data.catalog} summary={data.summary} initialQuery={libraryQuery} />}
        {view === 'method' && <MethodView selected={data.selected} />}
      </main>
    </div>
  )
}

function Navigation({ current, open, onToggle, onChange }: { current: ViewName; open: boolean; onToggle: () => void; onChange: (view: ViewName) => void }) {
  const items = [
    { id: 'explore' as const, label: 'Explorar mapa', icon: Map },
    { id: 'library' as const, label: 'Fuentes de datos', icon: Database },
    { id: 'method' as const, label: 'Método y alcance', icon: BookOpen },
  ]
  return (
    <>
      <button className="mobile-menu" onClick={onToggle} aria-expanded={open} aria-controls="primary-navigation">
        {open ? <X aria-hidden="true" /> : <Menu aria-hidden="true" />}<span>Menú</span>
      </button>
      <nav id="primary-navigation" className={`nav-rail ${open ? 'open' : ''}`} aria-label="Navegación principal">
        <div className="brand-mark" aria-label="Agua Abierta Guatemala">
          <Droplets aria-hidden="true" />
          <span>AGUA<br />ABIERTA<br /><b>GUATEMALA</b></span>
        </div>
        <div className="nav-items">
          {items.map(({ id, label, icon: Icon }) => (
            <button key={id} className={current === id ? 'active' : ''} onClick={() => onChange(id)} aria-current={current === id ? 'page' : undefined}>
              <Icon aria-hidden="true" /><span>{label}</span>
            </button>
          ))}
        </div>
        <a className="nav-doc-link" href="./catalogo_fuentes_agua_guatemala.pdf">
          <FileText aria-hidden="true" /><span>Catálogo PDF</span>
        </a>
        <div className="nav-folio">MVP · 01</div>
      </nav>
    </>
  )
}

interface ExploreProps {
  data: AppData
  selectedFeature: WaterFeature | null
  layers: Record<string, boolean>
  focusFeatureId: string | null
  mapStatus: 'loading' | 'ready' | 'fallback'
  showTable: boolean
  onLayerChange: (id: string, value: boolean) => void
  onSelect: (feature: WaterFeature) => void
  onCloseDetail: () => void
  onStatus: (status: 'loading' | 'ready' | 'fallback') => void
  onToggleTable: () => void
  onOpenLibrary: (query: string) => void
}

function ExploreView({
  data,
  selectedFeature,
  layers,
  focusFeatureId,
  mapStatus,
  showTable,
  onLayerChange,
  onSelect,
  onCloseDetail,
  onStatus,
  onToggleTable,
  onOpenLibrary,
}: ExploreProps) {
  const [query, setQuery] = useState('')
  const [searchOpen, setSearchOpen] = useState(false)
  const [basemap, setBasemap] = useState<BasemapId>('natural')
  const [hydrologyEmphasis, setHydrologyEmphasis] = useState(true)
  const stableStatus = useCallback(onStatus, [onStatus])
  const mapResults = useMemo(() => {
    const normalized = query.trim().toLocaleLowerCase('es')
    if (!normalized) return []
    return data.features.features.filter((feature) => {
      const props = feature.properties
      return `${props.name} ${props.kind} ${props.basin} ${props.department} ${props.municipality}`.toLocaleLowerCase('es').includes(normalized)
    }).slice(0, 5)
  }, [data.features.features, query])
  const sourceResults = useMemo(() => {
    const normalized = query.trim().toLocaleLowerCase('es')
    if (!normalized) return []
    return data.catalog.filter((item) => `${item.title} ${item.institution} ${item.territory}`.toLocaleLowerCase('es').includes(normalized)).slice(0, 4)
  }, [data.catalog, query])
  const layerCounts = useMemo(() => ({
    monitoring: data.features.features.filter((item) => !item.properties.kind.includes('meteorológica') && !item.properties.kind.includes('Lago')).length,
    lakes: data.features.features.filter((item) => item.properties.kind.includes('Lago')).length,
    climate: data.features.features.filter((item) => item.properties.kind.includes('meteorológica')).length,
  }), [data.features.features])
  const groundwaterSourceCount = useMemo(() => data.catalog.filter((item) =>
    /subterr|acuífer|pozo/i.test(`${item.topic} ${item.title} ${item.summary}`),
  ).length, [data.catalog])

  return (
    <section className="explore-view" aria-labelledby="explore-title">
      <header className="explore-header">
        <div className="explore-heading">
          <span>Atlas público · Guatemala</span>
          <h1 id="explore-title">Agua, territorio y evidencia</h1>
        </div>
        <div className="global-search">
          <label className="search-field map-search">
            <Search aria-hidden="true" />
            <span className="sr-only">Buscar fuente hídrica o archivo</span>
            <input
              value={query}
              onChange={(event) => { setQuery(event.target.value); setSearchOpen(true) }}
              onFocus={() => setSearchOpen(true)}
              onKeyDown={(event) => { if (event.key === 'Escape') setSearchOpen(false) }}
              placeholder="Buscar río, lago, municipio o archivo…"
              autoComplete="off"
            />
            {query && <button onClick={() => setQuery('')} aria-label="Limpiar búsqueda"><X aria-hidden="true" /></button>}
          </label>
          {searchOpen && query && (
            <div className="search-results" role="region" aria-label="Resultados de búsqueda">
              {mapResults.map((feature) => (
                <button key={feature.id} onClick={() => { onSelect(feature); setSearchOpen(false) }}>
                  <Map aria-hidden="true" /><span><strong>{feature.properties.name}</strong><small>{feature.properties.kind} · {feature.properties.department || feature.properties.basin}</small></span>
                </button>
              ))}
              {sourceResults.map((item) => (
                <button key={item.id} onClick={() => onOpenLibrary(item.fileName)}>
                  <FolderOpen aria-hidden="true" /><span><strong>{item.title}</strong><small>Fuente de datos · {item.institution}</small></span>
                </button>
              ))}
              {!mapResults.length && !sourceResults.length && <div className="no-search-result">No se encontraron coincidencias.</div>}
            </div>
          )}
        </div>
        <div className="coverage-strip" aria-label="Resumen de cobertura">
          <div><strong>{data.summary.downloadedFiles}</strong><span>archivos verificados</span></div>
          <div><strong>{data.summary.mappedFeatures}</strong><span>ubicaciones publicadas</span></div>
          <div><strong>{data.summary.selectedMvpDatasets}</strong><span>conjuntos en el MVP</span></div>
          <div className="updated"><span>Fecha de corte</span><strong>{formatCutoff(data.summary.cutoff)}</strong></div>
        </div>
      </header>

      <div className={`map-workspace ${selectedFeature ? 'with-detail' : ''}`}>
        <div className="map-frame">
          <Suspense fallback={<div className="map-module-loading" role="status"><Droplets aria-hidden="true" /><span>Cargando motor cartográfico…</span></div>}>
            <MapView
              data={data.features}
              styleUrl={basemap === 'natural' ? NATURAL_MAP_STYLE : data.summary.mapStyle}
              visibleLayers={layers}
              hydrologyEmphasis={hydrologyEmphasis}
              focusFeatureId={focusFeatureId}
              onSelect={onSelect}
              onStatus={stableStatus}
            />
          </Suspense>
          <div className={`map-status ${mapStatus}`} role="status">
            <span className="status-pulse" />
            {mapStatus === 'loading' && 'Cargando cartografía abierta'}
            {mapStatus === 'ready' && 'Cartografía abierta conectada'}
            {mapStatus === 'fallback' && 'Mapa base no disponible · datos locales activos'}
          </div>
          <LayerPanel
            values={layers}
            counts={layerCounts}
            basemap={basemap}
            hydrologyEmphasis={hydrologyEmphasis}
            groundwaterSourceCount={groundwaterSourceCount}
            onChange={onLayerChange}
            onBasemapChange={setBasemap}
            onHydrologyEmphasisChange={setHydrologyEmphasis}
          />
          <button className="table-toggle" onClick={onToggleTable} aria-expanded={showTable}>
            <Layers3 aria-hidden="true" /> {showTable ? 'Ocultar tabla' : 'Ver datos en tabla'}
          </button>
          <div className="map-caption">
            <span>Coordenadas: fuentes publicadas</span>
            <span>{basemap === 'natural' ? 'Base natural · ' : 'Base oscura · '}{data.summary.mapAttribution}</span>
          </div>
        </div>

        {selectedFeature && <DetailPanel feature={selectedFeature} catalog={data.catalog} onClose={onCloseDetail} />}
      </div>

      {showTable && <MapTable features={data.features.features} onSelect={onSelect} />}

      <aside className="featured-datasets" aria-label="Selección del MVP">
        <div><span>Levantamiento MVP</span><strong>12 conjuntos</strong></div>
        {data.selected.slice(0, 3).map((item) => (
          <button key={item.id} onClick={() => onOpenLibrary(item.fileName)}>
            <span>{item.id}</span><strong>{item.title}</strong><small>{item.institution} · {item.period}</small>
          </button>
        ))}
        <button className="all-datasets" onClick={() => onOpenLibrary('')}>Ver los 75 archivos</button>
      </aside>
    </section>
  )
}

function MapTable({ features, onSelect }: { features: WaterFeature[]; onSelect: (feature: WaterFeature) => void }) {
  return (
    <section className="map-table-section" aria-labelledby="map-table-title">
      <div><span>Alternativa al mapa</span><h2 id="map-table-title">Elementos georreferenciados</h2></div>
      <div className="map-table-scroll">
        <table>
          <thead><tr><th>Nombre</th><th>Tipo</th><th>Cuenca</th><th>Territorio</th><th>Última fecha</th><th>Estado</th><th /></tr></thead>
          <tbody>{features.map((feature) => (
            <tr key={feature.id}>
              <td>{feature.properties.name}</td>
              <td>{feature.properties.kind}</td>
              <td>{feature.properties.basin || 'No indicada'}</td>
              <td>{[feature.properties.municipality, feature.properties.department].filter(Boolean).join(', ') || 'No indicado'}</td>
              <td>{feature.properties.latest}</td>
              <td>{feature.properties.emotion}</td>
              <td><button onClick={() => onSelect(feature)}>Abrir ficha</button></td>
            </tr>
          ))}</tbody>
        </table>
      </div>
    </section>
  )
}

function MethodView({ selected }: { selected: CatalogItem[] }) {
  return (
    <section className="method-view" aria-labelledby="method-title">
      <header>
        <span className="section-context">Procedencia antes que interpretación</span>
        <h1 id="method-title">Método y alcance del MVP</h1>
        <p>Esta versión prioriza evidencia trazable. La ausencia de datos no se interpreta como buena calidad y ninguna ubicación se crea sin coordenadas publicadas.</p>
        <div className="doc-links">
          <a href="./docs/DATA_METHOD.md"><FileText aria-hidden="true" /> Transformación y procedencia</a>
          <a href="./docs/EMOTION_MODEL.md"><HelpCircle aria-hidden="true" /> Modelo de estados</a>
          <a href="./catalogo_fuentes_agua_guatemala.html"><Database aria-hidden="true" /> Catálogo HTML</a>
        </div>
      </header>
      <div className="method-grid">
        <section className="method-principles">
          <h2>Reglas de esta versión</h2>
          <ol>
            <li><strong>Archivo original intacto.</strong><span>Las 75 copias se validan contra el SHA-256 del inventario.</span></li>
            <li><strong>Coordenadas publicadas.</strong><span>Los recursos sin georreferencia permanecen en la biblioteca, no en el mapa.</span></li>
            <li><strong>Carga ligera.</strong><span>El inicio usa JSON normalizado; los archivos grandes se abren bajo demanda.</span></li>
            <li><strong>Estado prudente.</strong><span>El MVP muestra “Sin datos suficientes” cuando una conclusión técnica no está respaldada.</span></li>
          </ol>
        </section>
        <section className="emotion-method">
          <h2>Estado narrativo</h2>
          <p>La taxonomía está preparada, pero esta primera versión no fuerza una clasificación de calidad a partir de campañas parciales.</p>
          <ul>
            {['Serena', 'En observación', 'Tensa', 'Herida', 'Crítica', 'En recuperación', 'Sin datos suficientes'].map((state) => <li key={state}><span className={state === 'Sin datos suficientes' ? 'active' : ''} />{state}</li>)}
          </ul>
          <div className="warning-note"><TriangleAlert aria-hidden="true" /><p>La emoción narrativa nunca sustituye el estado técnico ni una evaluación regulatoria.</p></div>
        </section>
      </div>
      <section className="dataset-selection">
        <div><span>Profundización inicial</span><h2>Los 12 conjuntos seleccionados</h2></div>
        <div className="selection-table-wrap">
          <table>
            <thead><tr><th>ID</th><th>Conjunto</th><th>Institución</th><th>Periodo</th><th>Razón de selección</th></tr></thead>
            <tbody>{selected.map((item) => <tr key={item.id}><td>{item.id}</td><td>{item.title}</td><td>{item.institution}</td><td>{item.period}</td><td>{item.selectionReason}</td></tr>)}</tbody>
          </table>
        </div>
      </section>
    </section>
  )
}

function LoadingScreen() {
  return <main className="load-screen" aria-live="polite"><Droplets aria-hidden="true" /><p>Preparando el atlas y sus fuentes verificadas…</p><span /></main>
}

function formatCutoff(value: string) {
  const date = new Date(`${value}T00:00:00`)
  return new Intl.DateTimeFormat('es-GT', { day: '2-digit', month: 'short', year: 'numeric' }).format(date).replace('.', '').toLocaleUpperCase('es')
}

function LoadError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return <main className="load-screen error" role="alert"><TriangleAlert aria-hidden="true" /><h1>No se pudieron cargar los datos</h1><p>{message}</p><p>Compruebe que abrió la dirección del servidor local y vuelva a intentarlo.</p><button className="primary-button" onClick={onRetry}>Reintentar carga</button></main>
}
