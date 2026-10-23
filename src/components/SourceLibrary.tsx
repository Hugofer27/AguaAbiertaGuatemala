import { useMemo, useState } from 'react'
import { createPortal } from 'react-dom'
import { Download, ExternalLink, FileSearch, Filter, Search, ShieldCheck, X } from 'lucide-react'
import type { CatalogItem, Summary } from '../types'
import { usePanelFocus } from '../usePanelFocus'

interface SourceLibraryProps {
  catalog: CatalogItem[]
  summary: Summary
  initialQuery?: string
}

const ALL = 'Todas'

function uniq(values: string[]) {
  return [ALL, ...Array.from(new Set(values.filter(Boolean))).sort((a, b) => a.localeCompare(b, 'es'))]
}

function matches(value: string, filter: string) {
  return filter === ALL || value === filter
}

export default function SourceLibrary({ catalog, summary, initialQuery = '' }: SourceLibraryProps) {
  const [query, setQuery] = useState(initialQuery)
  const [institution, setInstitution] = useState(ALL)
  const [topic, setTopic] = useState(ALL)
  const [territory, setTerritory] = useState(ALL)
  const [period, setPeriod] = useState(ALL)
  const [format, setFormat] = useState(ALL)
  const [access, setAccess] = useState(ALL)
  const [sort, setSort] = useState('relevance')
  const [selected, setSelected] = useState<CatalogItem | null>(null)

  const options = useMemo(() => ({
    institutions: uniq(catalog.map((item) => item.institution)),
    topics: uniq(catalog.map((item) => item.topic)),
    territories: uniq(catalog.map((item) => item.territory)),
    periods: uniq(catalog.map((item) => item.period)),
    formats: uniq(catalog.map((item) => item.format)),
    access: uniq(catalog.map((item) => item.accessState)),
  }), [catalog])

  const filtered = useMemo(() => {
    const normalized = query.trim().toLocaleLowerCase('es')
    const rows = catalog.filter((item) => {
      const haystack = `${item.title} ${item.fileName} ${item.institution} ${item.topic} ${item.territory}`.toLocaleLowerCase('es')
      return (!normalized || haystack.includes(normalized))
        && matches(item.institution, institution)
        && matches(item.topic, topic)
        && matches(item.territory, territory)
        && matches(item.period, period)
        && matches(item.format, format)
        && matches(item.accessState, access)
    })
    return [...rows].sort((a, b) => {
      if (sort === 'date') return b.period.localeCompare(a.period, 'es', { numeric: true })
      if (sort === 'source') return a.institution.localeCompare(b.institution, 'es')
      if (sort === 'name') return a.title.localeCompare(b.title, 'es')
      if (sort === 'size') return b.bytes - a.bytes
      return Number(b.selectedMvp) - Number(a.selectedMvp) || a.number - b.number
    })
  }, [access, catalog, format, institution, period, query, sort, territory, topic])

  const reset = () => {
    setQuery('')
    setInstitution(ALL)
    setTopic(ALL)
    setTerritory(ALL)
    setPeriod(ALL)
    setFormat(ALL)
    setAccess(ALL)
    setSort('relevance')
  }

  return (
    <section className="library-view" aria-labelledby="library-title">
      <header className="library-titlebar">
        <div>
          <span className="section-context">Índice verificable</span>
          <h1 id="library-title">Fuentes de datos</h1>
          <p>Los 75 archivos descargados están disponibles desde el inicio. El contenido detallado se abre solo cuando lo solicita.</p>
        </div>
        <div className="library-count">
          <strong>{filtered.length}</strong>
          <span>de {summary.downloadedFiles} archivos</span>
        </div>
      </header>

      <div className="library-toolbar">
        <label className="search-field wide">
          <Search aria-hidden="true" />
          <span className="sr-only">Buscar por archivo o institución</span>
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar archivo, institución o territorio…" />
          {query && <button onClick={() => setQuery('')} aria-label="Limpiar búsqueda"><X aria-hidden="true" /></button>}
        </label>
        <label className="sort-field">
          <span>Ordenar</span>
          <select value={sort} onChange={(event) => setSort(event.target.value)}>
            <option value="relevance">Relevancia MVP</option>
            <option value="date">Fecha / periodo</option>
            <option value="source">Fuente</option>
            <option value="name">Nombre</option>
            <option value="size">Tamaño</option>
          </select>
        </label>
      </div>

      <div className="library-layout">
        <aside className="filter-rail" aria-label="Filtros del catálogo">
          <div className="filter-title"><Filter aria-hidden="true" /><h2>Filtrar</h2></div>
          <FilterSelect label="Institución" value={institution} options={options.institutions} onChange={setInstitution} />
          <FilterSelect label="Tema" value={topic} options={options.topics} onChange={setTopic} />
          <FilterSelect label="Territorio o cuenca" value={territory} options={options.territories} onChange={setTerritory} />
          <FilterSelect label="Periodo" value={period} options={options.periods} onChange={setPeriod} />
          <FilterSelect label="Formato" value={format} options={options.formats} onChange={setFormat} />
          <FilterSelect label="Estado de acceso" value={access} options={options.access} onChange={setAccess} />
          <button className="text-button" onClick={reset}>Restablecer filtros</button>
        </aside>

        <p className="sr-only" role="status" aria-live="polite">{filtered.length} de {summary.downloadedFiles} archivos visibles.</p>
        <div className="source-results">
          {filtered.length ? filtered.map((item) => (
            <article className="source-row" key={item.id}>
              <button className="source-main" onClick={() => setSelected(item)} aria-label={`Abrir ficha de ${item.title}`}>
                <span className="source-number">{String(item.number).padStart(2, '0')}</span>
                <span className="source-name"><strong>{item.title}</strong><small>{item.fileName}</small></span>
                <span className="source-org">{item.institution}</span>
                <span className="source-period">{item.period}</span>
                <span className="source-format">{item.format}</span>
                <span className={`access-label ${item.accessState === 'Descargado y verificado' ? 'verified' : ''}`}>
                  {item.accessState === 'Descargado y verificado' && <ShieldCheck aria-hidden="true" />}
                  {item.accessState}
                </span>
                {item.selectedMvp && <span className="mvp-mark">MVP</span>}
              </button>
            </article>
          )) : (
            <div className="empty-state">
              <FileSearch aria-hidden="true" />
              <h2>No hay archivos con esos filtros</h2>
              <p>Pruebe otra institución, periodo o término de búsqueda.</p>
              <button className="primary-button" onClick={reset}>Restablecer filtros</button>
            </div>
          )}
        </div>

        {selected && <SourceDetail item={selected} onClose={() => setSelected(null)} />}
      </div>
    </section>
  )
}

function FilterSelect({ label, value, options, onChange }: { label: string; value: string; options: string[]; onChange: (value: string) => void }) {
  return (
    <label className="filter-field">
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => <option key={option}>{option}</option>)}
      </select>
    </label>
  )
}

function SourceDetail({ item, onClose }: { item: CatalogItem; onClose: () => void }) {
  const panelRef = usePanelFocus<HTMLElement>(onClose, true)
  return createPortal(
    <>
      <div className="source-detail-backdrop" aria-hidden="true" onClick={onClose} />
      <aside ref={panelRef} className="source-detail" role="dialog" aria-modal="true" aria-labelledby="source-detail-title" tabIndex={-1}>
        <div className="source-detail-head">
          <span>{item.id} · {item.format}</span>
          <button className="icon-button light" onClick={onClose} aria-label="Cerrar ficha de fuente"><X aria-hidden="true" /></button>
        </div>
        <h2 id="source-detail-title">{item.title}</h2>
        <p>{item.summary}</p>
        <dl className="source-facts">
          <div><dt>Institución</dt><dd>{item.institution}</dd></div>
          <div><dt>Tema</dt><dd>{item.topic}</dd></div>
          <div><dt>Territorio</dt><dd>{item.territory}</dd></div>
          <div><dt>Periodo</dt><dd>{item.period}</dd></div>
          <div><dt>Tamaño</dt><dd>{item.size}</dd></div>
          <div><dt>Estado</dt><dd>{item.accessState}</dd></div>
          <div><dt>Licencia / uso</dt><dd>{item.license}</dd></div>
          <div><dt>Coordenadas</dt><dd>{item.coordinates}</dd></div>
        </dl>
        {item.selectedMvp && <div className="selection-reason"><strong>Por qué está en el MVP</strong><p>{item.selectionReason ?? 'Conjunto representativo procesado para la primera versión.'}</p></div>}
        {item.parameters.length > 0 && <ul className="tag-list">{item.parameters.map((parameter) => <li key={parameter}>{parameter}</li>)}</ul>}
        <details className="technical-detail">
          <summary>Ficha técnica avanzada</summary>
          <dl><dt>SHA-256</dt><dd>{item.sha256}</dd><dt>Registros / páginas</dt><dd>{item.records || 'No indicado'}</dd></dl>
        </details>
        <div className="source-actions">
          <a className="primary-button" href={item.localPath}><Download aria-hidden="true" /> Abrir archivo local</a>
          {item.sourceUrl && <a className="secondary-button" href={item.sourceUrl} target="_blank" rel="noreferrer"><ExternalLink aria-hidden="true" /> Visitar procedencia</a>}
        </div>
      </aside>
    </>,
    document.body,
  )
}
