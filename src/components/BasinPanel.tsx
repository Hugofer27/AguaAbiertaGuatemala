import { FileText, Search, X } from 'lucide-react'
import { estiloDe } from '../capas'
import { numero } from '../textos'
import type { CapaMeta, Cuenca, Fuente } from '../types'
import { usePanelFocus } from '../usePanelFocus'

interface BasinPanelProps {
  cuenca: Cuenca
  capas: CapaMeta[]
  catalogo: Fuente[]
  onClose: () => void
  onBuscarEnDatos: (termino: string) => void
  onAbrirFuente: (id: string) => void
  onActivarCapa: (id: string) => void
}

export default function BasinPanel({ cuenca, capas, catalogo, onClose, onBuscarEnDatos, onAbrirFuente, onActivarCapa }: BasinPanelProps) {
  const panelRef = usePanelFocus<HTMLElement>(onClose)
  const p = cuenca.properties
  const conteos = capas
    .filter((c) => p.puntos_por_capa[c.id])
    .map((c) => ({ capa: c, n: p.puntos_por_capa[c.id] }))
    .sort((a, b) => estiloDe(a.capa.id).orden - estiloDe(b.capa.id).orden)
  const ejemplos = p.ejemplos_fuentes.map((id) => catalogo.find((f) => f.id === id)).filter(Boolean) as Fuente[]

  return (
    <aside ref={panelRef} className="ficha" role="dialog" aria-labelledby="ficha-cuenca-titulo" tabIndex={-1}>
      <header className="ficha-cabeza" style={{ '--acento-capa': estiloDe('cuencas').color } as React.CSSProperties}>
        <div>
          <span className="ficha-tipo">Cuenca hidrográfica · vertiente del {p.vertiente}</span>
          <h2 id="ficha-cuenca-titulo">{p.nombre}</h2>
          <p className="ficha-sub">{numero(p.area_km2)} km² · delimitación MAGA 2001</p>
        </div>
        <button className="boton-icono" onClick={onClose} aria-label="Cerrar ficha"><X aria-hidden="true" /></button>
      </header>
      <div className="ficha-cuerpo">
        <section className="ficha-seccion" aria-labelledby="cuenca-puntos">
          <h3 id="cuenca-puntos">Puntos del mapa dentro de la cuenca</h3>
          {conteos.length ? (
            <ul className="conteo-capas">
              {conteos.map(({ capa, n }) => (
                <li key={capa.id}>
                  <button onClick={() => onActivarCapa(capa.id)} title="Mostrar esta capa">
                    <span className={`muestra muestra-${capa.geometria}`} style={{ '--muestra': estiloDe(capa.id).color } as React.CSSProperties} aria-hidden="true" />
                    <span>{capa.titulo}</span>
                    <strong>{n}</strong>
                  </button>
                </li>
              ))}
            </ul>
          ) : <p className="texto-suave">Ninguna capa de puntos tiene ubicaciones dentro de esta cuenca.</p>}
        </section>

        <section className="ficha-seccion" aria-labelledby="cuenca-fuentes">
          <h3 id="cuenca-fuentes">Fuentes que la mencionan</h3>
          <p className="cifras-cuenca">
            <span><strong>{p.fuentes_que_la_mencionan}</strong> en el catálogo</span>
            <span><strong>{p.publicaciones_que_la_mencionan}</strong> publicaciones</span>
          </p>
          {ejemplos.length > 0 && (
            <ul className="lista-fuentes">
              {ejemplos.map((f) => (
                <li key={f.id}>
                  <button className="enlace-fuente" onClick={() => onAbrirFuente(f.id)}>
                    <FileText aria-hidden="true" />
                    <span><strong>{f.titulo}</strong><small>{f.institucion} · {f.tipo}</small></span>
                  </button>
                </li>
              ))}
            </ul>
          )}
          <button className="boton secundario" onClick={() => onBuscarEnDatos(p.termino_busqueda)}>
            <Search aria-hidden="true" /> Buscar “{p.termino_busqueda}” en Datos
          </button>
          <p className="nota-pie">Las menciones se cuentan por el nombre de la cuenca en el título o la cobertura; es una búsqueda aproximada.</p>
        </section>
      </div>
    </aside>
  )
}
