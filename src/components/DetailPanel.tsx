import { useEffect, useState } from 'react'
import { Database, ExternalLink, FileDown, Info, LocateFixed, ShieldCheck, X } from 'lucide-react'
import type { CatalogItem, SeriesPoint, WaterFeature } from '../types'
import { usePanelFocus } from '../usePanelFocus'
import SatelliteSnapshot from './SatelliteSnapshot'

function Sparkline({ points }: { points: SeriesPoint[] }) {
  if (points.length < 2) return null
  const values = points.map((point) => point.value)
  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1
  const path = points
    .map((point, index) => {
      const x = 8 + (index / (points.length - 1)) * 264
      const y = 72 - ((point.value - min) / range) * 54
      return `${index === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`
    })
    .join(' ')
  return (
    <figure className="mini-chart">
      <svg viewBox="0 0 280 88" role="img" aria-label="Serie temporal disponible">
        <line x1="8" y1="72" x2="272" y2="72" className="chart-rule" />
        <path d={path} className="chart-line" />
        <circle cx="272" cy={72 - ((values.at(-1)! - min) / range) * 54} r="4" className="chart-dot" />
      </svg>
      <figcaption>
        {points[0].label}–{points.at(-1)?.label} · {points.at(-1)?.unit ?? 'valor descriptivo'}
      </figcaption>
    </figure>
  )
}

interface DetailPanelProps {
  feature: WaterFeature
  catalog: CatalogItem[]
  onClose: () => void
}

function StateReveal({ feature, onFinish }: { feature: WaterFeature; onFinish: () => void }) {
  const props = feature.properties
  const readings = props.evidence.slice(0, 3)
  return (
    <div className="state-reveal">
      <p className="sr-only" role="status" aria-live="polite">{props.emotion}. Preparando archivo, parámetros y procedencia.</p>
      <div className="water-column" aria-hidden="true">
        <span className="water-column-fill" />
        <span className="water-column-scan" />
        <i /><i /><i />
      </div>
      <div className="state-reveal-copy">
        <span className="state-reveal-label">Estado narrativo derivado por el portal</span>
        <strong>{props.emotion}</strong>
        <p>{props.emotionReason}</p>
        {readings.length > 0 && (
          <dl className="reveal-readings">
            {readings.map((item) => (
              <div key={`${item.parameter}-${item.date}`}>
                <dt>{item.parameter}</dt>
                <dd>{item.value.toLocaleString('es-GT')}</dd>
              </div>
            ))}
          </dl>
        )}
        <div className="reveal-progress" aria-hidden="true"><span /></div>
        <small>Preparando archivo, parámetros y procedencia…</small>
        <button className="text-button reveal-skip" onClick={onFinish}>Ver ficha ahora</button>
      </div>
    </div>
  )
}

function PointOrigin({ feature, related }: { feature: WaterFeature; related: CatalogItem[] }) {
  const [longitude, latitude] = feature.geometry.coordinates
  return (
    <section className="point-origin" aria-labelledby="point-origin-title">
      <header>
        <Database aria-hidden="true" />
        <div><span>Procedencia cartográfica</span><h3 id="point-origin-title">¿Por qué aparece este punto?</h3></div>
      </header>
      <p>La ubicación se dibuja porque la fuente publicada incluye una coordenada verificable asociada a este registro.</p>
      <div className="origin-coordinate"><LocateFixed aria-hidden="true" /><span>Latitud {latitude.toFixed(5)} · Longitud {longitude.toFixed(5)}</span></div>
      <div className="origin-files">
        {related.map((item) => (
          <article key={item.id}>
            <div className="origin-file-head">
              <span>{item.id} · {item.format}</span>
              <span><ShieldCheck aria-hidden="true" /> {item.accessState}</span>
            </div>
            <strong>{item.title}</strong>
            <div className="origin-file-name"><span>Archivo exacto</span><code>{item.fileName}</code></div>
            <small>{item.institution} · {item.period} · {item.records || 'Registros no indicados'}</small>
            <div>
              <a className="primary-button" href={item.localPath} target="_blank" rel="noreferrer" aria-label={`Abrir archivo ${item.fileName}`}><FileDown aria-hidden="true" /> Abrir archivo</a>
              {item.sourceUrl && <a className="secondary-button" href={item.sourceUrl} target="_blank" rel="noreferrer"><ExternalLink aria-hidden="true" /> Ver procedencia</a>}
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}

export default function DetailPanel({ feature, catalog, onClose }: DetailPanelProps) {
  const panelRef = usePanelFocus<HTMLElement>(onClose)
  const [revealing, setRevealing] = useState(true)
  const props = feature.properties
  const related = catalog.filter((item) => props.sourceIds.includes(item.id))

  useEffect(() => {
    setRevealing(true)
    const reducedMotion = typeof window.matchMedia === 'function' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const timer = window.setTimeout(() => setRevealing(false), reducedMotion ? 420 : 1050)
    return () => window.clearTimeout(timer)
  }, [feature.id])

  return (
    <aside ref={panelRef} className={`detail-panel ${revealing ? 'is-revealing' : 'is-ready'}`} role="dialog" aria-labelledby="detail-title" tabIndex={-1}>
      <header className="detail-header">
        <div>
          <span className="detail-type">{props.kind}</span>
          <h2 id="detail-title">{props.name}</h2>
        </div>
        <button className="icon-button light" onClick={onClose} aria-label="Cerrar ficha">
          <X aria-hidden="true" />
        </button>
      </header>

      {revealing ? <StateReveal feature={feature} onFinish={() => setRevealing(false)} /> : <div className="detail-content">
        <div className="emotion-block" data-emotion={props.emotionCode}>
        <span className="emotion-marker" aria-hidden="true">?</span>
        <div>
          <span>Estado narrativo</span>
          <strong>{props.emotion}</strong>
          <p>{props.emotionReason}</p>
        </div>
        </div>

        <PointOrigin feature={feature} related={related} />

        <SatelliteSnapshot feature={feature} />

        <dl className="fact-grid">
        <div><dt>Cuenca</dt><dd>{props.basin || 'No indicada'}</dd></div>
        <div><dt>Departamento</dt><dd>{props.department || 'No indicado'}</dd></div>
        <div><dt>Municipio</dt><dd>{props.municipality || 'No indicado'}</dd></div>
        <div><dt>Última fecha</dt><dd>{props.latest || 'Sin fecha'}</dd></div>
        <div className="wide"><dt>Institución</dt><dd>{props.institution}</dd></div>
        <div className="wide"><dt>Cobertura / confianza</dt><dd>{props.confidence}</dd></div>
        </dl>

        {props.series.length > 1 && <Sparkline points={props.series} />}

        <section className="detail-section">
        <h3>Parámetros disponibles</h3>
        {props.parameters.length ? (
          <ul className="tag-list">
            {props.parameters.map((parameter) => <li key={parameter}>{parameter}</li>)}
          </ul>
        ) : <p className="empty-copy">Sin parámetros tabulares en la ficha.</p>}
        </section>

        <section className="detail-section">
        <h3>Evidencia consultable</h3>
        {props.evidence.length ? (
          <div className="evidence-table-wrap">
            <table className="evidence-table">
              <thead><tr><th>Parámetro</th><th>Valor</th><th>Fecha</th></tr></thead>
              <tbody>
                {props.evidence.map((item, index) => (
                  <tr key={`${item.parameter}-${index}`}>
                    <td>{item.parameter}<small>{item.station}</small></td>
                    <td>{item.value.toLocaleString('es-GT')}<small>{item.unit}</small></td>
                    <td>{item.date}<small>{item.sourceId}</small></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <p className="empty-copy">Esta ubicación no tiene una vista tabular normalizada en el MVP.</p>}
        </section>

        <div className="warning-note">
        <Info aria-hidden="true" />
        <p>{props.warning}</p>
        </div>

        <button className="future-button" disabled title="Disponible en una fase posterior">
        Reportar problema <span>FASE 2</span>
        </button>
      </div>}
    </aside>
  )
}
