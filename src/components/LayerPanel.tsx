import { useState } from 'react'
import { ChevronDown, CircleDashed, CloudRain, Database, Droplets, MapPinned, Moon, Mountain, TriangleAlert, Waves } from 'lucide-react'

export type BasemapId = 'natural' | 'dark'

interface LayerPanelProps {
  values: Record<string, boolean>
  counts: Record<string, number>
  basemap: BasemapId
  hydrologyEmphasis: boolean
  groundwaterSourceCount: number
  onChange: (id: string, value: boolean) => void
  onBasemapChange: (basemap: BasemapId) => void
  onHydrologyEmphasisChange: (value: boolean) => void
}

const LAYERS = [
  { id: 'monitoring', label: 'Monitoreo de agua', icon: MapPinned, tone: 'turquoise' },
  { id: 'lakes', label: 'Lagos y observaciones', icon: Droplets, tone: 'aqua' },
  { id: 'climate', label: 'Meteorología de apoyo', icon: CloudRain, tone: 'amber' },
] as const

export default function LayerPanel({ values, counts, basemap, hydrologyEmphasis, groundwaterSourceCount, onChange, onBasemapChange, onHydrologyEmphasisChange }: LayerPanelProps) {
  const [expanded, setExpanded] = useState(false)
  return (
    <section className={`layer-panel ${expanded ? 'expanded' : 'collapsed'}`} aria-labelledby="layer-heading">
      <div className="layer-heading">
        <div><span>Vista</span><h2 id="layer-heading">Capas</h2></div>
        <Database aria-hidden="true" />
        <button className="layer-toggle" onClick={() => setExpanded((value) => !value)} aria-expanded={expanded} aria-controls="layer-panel-body">
          {expanded ? 'Ocultar' : 'Mostrar'} <ChevronDown aria-hidden="true" />
        </button>
      </div>
      <div id="layer-panel-body" className="layer-body">
        <div className="basemap-control" role="group" aria-label="Mapa base">
          <span>Mapa base</span>
          <div>
            <button className={basemap === 'natural' ? 'active' : ''} onClick={() => onBasemapChange('natural')} aria-pressed={basemap === 'natural'}>
              <Mountain aria-hidden="true" /> Natural
            </button>
            <button className={basemap === 'dark' ? 'active' : ''} onClick={() => onBasemapChange('dark')} aria-pressed={basemap === 'dark'}>
              <Moon aria-hidden="true" /> Atlas
            </button>
          </div>
        </div>
        <div className="layer-list">
          <label className="layer-row hydrology-row">
            <input type="checkbox" checked={hydrologyEmphasis} onChange={(event) => onHydrologyEmphasisChange(event.target.checked)} />
            <span className="layer-swatch river"><Waves aria-hidden="true" /></span>
            <span>Red hídrica destacada<small>Ríos y cuerpos de agua del mapa base</small></span>
          </label>
          {LAYERS.map(({ id, label, icon: Icon, tone }) => (
            <label key={id} className="layer-row">
              <input type="checkbox" checked={values[id]} onChange={(event) => onChange(id, event.target.checked)} />
              <span className={`layer-swatch ${tone}`}><Icon aria-hidden="true" /></span>
              <span>{label}<small>{counts[id] ?? 0} elementos</small></span>
            </label>
          ))}
          <div className="layer-row unavailable" aria-disabled="true">
            <span className="empty-checkbox" aria-hidden="true" />
            <span className="layer-swatch underground"><CircleDashed aria-hidden="true" /></span>
            <span>Agua subterránea<small>{groundwaterSourceCount} fuentes · sin coordenadas verificadas</small></span>
          </div>
          <div className="layer-row unavailable" aria-disabled="true">
            <span className="empty-checkbox" aria-hidden="true" />
            <span className="layer-swatch carmine"><TriangleAlert aria-hidden="true" /></span>
            <span>Sitios de contaminación<small>Sin coordenadas verificadas</small></span>
          </div>
        </div>
        <div className="legend">
          <span><i className="legend-dot verified" /> Ubicación publicada</span>
          <span><i className="legend-ring" /> Seleccionable</span>
          <span><i className="legend-mark">?</i> Sin clasificación suficiente</span>
        </div>
      </div>
    </section>
  )
}
