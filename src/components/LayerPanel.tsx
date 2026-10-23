import { useState } from 'react'
import { ChevronDown, Layers } from 'lucide-react'
import { GRUPOS, MAPAS_BASE, estiloDe, type MapaBase } from '../capas'
import type { CapaMeta } from '../types'

interface LayerPanelProps {
  capas: CapaMeta[]
  visibles: Record<string, boolean>
  mapaBase: MapaBase
  resaltarRios: boolean
  onCambio: (id: string, valor: boolean) => void
  onMapaBase: (base: MapaBase) => void
  onResaltarRios: (valor: boolean) => void
}

function Muestra({ capa }: { capa: CapaMeta }) {
  const { color } = estiloDe(capa.id)
  return <span className={`muestra muestra-${capa.geometria}`} style={{ '--muestra': color } as React.CSSProperties} aria-hidden="true" />
}

export default function LayerPanel({ capas, visibles, mapaBase, resaltarRios, onCambio, onMapaBase, onResaltarRios }: LayerPanelProps) {
  const [abierto, setAbierto] = useState(() => typeof window.matchMedia !== 'function' || !window.matchMedia('(max-width: 760px)').matches)
  const grupos = GRUPOS.map((grupo) => ({ grupo, capas: capas.filter((c) => c.grupo === grupo).sort((a, b) => estiloDe(a.id).orden - estiloDe(b.id).orden) }))
    .filter((g) => g.capas.length)

  return (
    <section className={`panel-capas ${abierto ? 'abierto' : 'cerrado'}`} aria-labelledby="titulo-capas">
      <button className="panel-capas-cabeza" onClick={() => setAbierto((v) => !v)} aria-expanded={abierto} aria-controls="cuerpo-capas">
        <Layers aria-hidden="true" />
        <h2 id="titulo-capas">Capas</h2>
        <span className="panel-capas-cuenta">{capas.filter((c) => visibles[c.id]).length} activas</span>
        <ChevronDown aria-hidden="true" className="chevron" />
      </button>
      <div id="cuerpo-capas" className="panel-capas-cuerpo" hidden={!abierto}>
        {grupos.map(({ grupo, capas: lista }) => (
          <fieldset key={grupo} className="grupo-capas">
            <legend>{grupo}</legend>
            {lista.map((capa) => (
              <label key={capa.id} className="fila-capa" title={capa.descripcion}>
                <input type="checkbox" checked={Boolean(visibles[capa.id])} onChange={(e) => onCambio(capa.id, e.target.checked)} />
                <Muestra capa={capa} />
                <span className="fila-capa-texto">
                  <span>{capa.titulo}</span>
                  <small>{capa.elementos.toLocaleString('es-GT')} · {capa.tipo_dato.toLowerCase()}</small>
                </span>
              </label>
            ))}
          </fieldset>
        ))}
        <fieldset className="grupo-capas mapa-base">
          <legend>Mapa base</legend>
          <div className="segmentado" role="group" aria-label="Mapa base">
            {(Object.keys(MAPAS_BASE) as MapaBase[]).map((id) => (
              <button key={id} className={mapaBase === id ? 'activo' : ''} aria-pressed={mapaBase === id} onClick={() => onMapaBase(id)}>
                {MAPAS_BASE[id].nombre}
              </button>
            ))}
          </div>
          <label className="fila-capa compacta">
            <input type="checkbox" checked={resaltarRios} onChange={(e) => onResaltarRios(e.target.checked)} />
            <span className="fila-capa-texto"><span>Resaltar ríos del mapa base</span></span>
          </label>
        </fieldset>
      </div>
    </section>
  )
}
