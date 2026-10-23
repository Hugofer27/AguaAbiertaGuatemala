import { useMemo } from 'react'
import { AlertTriangle, Download, ExternalLink, FileText, Info, MapPin, X } from 'lucide-react'
import { estiloDe } from '../capas'
import { urlDatos } from '../data'
import { PRECISION, TIPO_DATO, formatoValor } from '../textos'
import type { CapaMeta, Fuente, Medicion, Sitio } from '../types'
import { usePanelFocus } from '../usePanelFocus'
import SatelliteSnapshot from './SatelliteSnapshot'
import SeriesChart from './SeriesChart'

interface DetailPanelProps {
  sitio: Sitio
  capa: CapaMeta | undefined
  catalogo: Fuente[]
  onClose: () => void
  onAbrirFuente: (id: string) => void
}

function agrupar(mediciones: Medicion[]) {
  const grupos = new Map<string, Medicion[]>()
  for (const m of mediciones) {
    const lista = grupos.get(m.fecha) ?? []
    lista.push(m)
    grupos.set(m.fecha, lista)
  }
  return [...grupos.entries()]
}

export default function DetailPanel({ sitio, capa, catalogo, onClose, onAbrirFuente }: DetailPanelProps) {
  const panelRef = usePanelFocus<HTMLElement>(onClose)
  const p = sitio.properties
  const [lon, lat] = sitio.geometry.coordinates
  const fuentes = useMemo(() => p.fuente_ids.map((id) => catalogo.find((f) => f.id === id)).filter(Boolean) as Fuente[], [catalogo, p.fuente_ids])
  const grupos = useMemo(() => agrupar(p.mediciones ?? []), [p.mediciones])
  const unaSerie = (p.mediciones?.length ?? 0) > 1 && new Set(p.mediciones!.map((m) => m.codigo)).size === 1
  const hayUnidadInferida = (p.mediciones ?? []).some((m) => !m.unidad_verificada)
  const lugar = [p.municipio, p.departamento].filter(Boolean).join(', ')
  const atributos = Object.entries(p.atributos ?? {}).filter(([, v]) => v)
  const color = estiloDe(p.capa).color

  return (
    <aside ref={panelRef} className="ficha" role="dialog" aria-labelledby="ficha-titulo" tabIndex={-1}>
      <header className="ficha-cabeza" style={{ '--acento-capa': color } as React.CSSProperties}>
        <div>
          <span className="ficha-tipo">{p.tipo}</span>
          <h2 id="ficha-titulo">{p.nombre}</h2>
          <p className="ficha-sub">{[p.institucion, p.fecha].filter(Boolean).join(' · ')}</p>
        </div>
        <button className="boton-icono" onClick={onClose} aria-label="Cerrar ficha"><X aria-hidden="true" /></button>
      </header>

      <div className="ficha-cuerpo">
        <div className="insignias">
          <span className="insignia" title={TIPO_DATO[p.tipo_dato] ?? ''}>{p.tipo_dato}</span>
          <span className={`insignia precision-${p.precision}`} title={PRECISION[p.precision]?.largo}>{PRECISION[p.precision]?.corto}</span>
          {capa && <span className="insignia neutra">{capa.titulo}</span>}
        </div>

        {p.serie && <SeriesChart serie={p.serie} color={color} />}

        {grupos.length > 0 && (
          <section className="ficha-seccion" aria-labelledby="ficha-mediciones">
            <h3 id="ficha-mediciones">Mediciones</h3>
            {unaSerie ? (
              <details className="grupo-mediciones" open={!p.serie}>
                <summary><span>{p.mediciones![0].parametro}</span><small>{p.mediciones!.length} valores</small></summary>
                <table className="tabla-mediciones">
                  <thead><tr><th scope="col">Fecha</th><th scope="col">Valor</th></tr></thead>
                  <tbody>
                    {p.mediciones!.map((m, i) => (
                      <tr key={`${m.fecha}-${i}`} className={m.control ? 'con-control' : ''}>
                        <th scope="row">{m.fecha}{m.control && <span className="control-calidad"><AlertTriangle aria-hidden="true" />{m.control}</span>}</th>
                        <td>{formatoValor(m.valor)} <span className="unidad">{m.unidad}{!m.unidad_verificada && '*'}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </details>
            ) : grupos.map(([fecha, lista], indice) => (
              <details key={fecha} className="grupo-mediciones" open={indice === 0 || grupos.length <= 2}>
                <summary><span>{fecha}</span><small>{lista.length} {lista.length === 1 ? 'valor' : 'valores'}</small></summary>
                <table className="tabla-mediciones">
                  <thead><tr><th scope="col">Parámetro</th><th scope="col">Valor</th></tr></thead>
                  <tbody>
                    {lista.map((m, i) => (
                      <tr key={`${m.codigo}-${i}`} className={m.control ? 'con-control' : ''}>
                        <th scope="row">
                          {m.parametro}
                          {m.control && <span className="control-calidad"><AlertTriangle aria-hidden="true" />{m.control}</span>}
                        </th>
                        <td>{formatoValor(m.valor)} <span className="unidad">{m.unidad}{!m.unidad_verificada && '*'}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </details>
            ))}
            {hayUnidadInferida && <p className="nota-pie">* Unidad habitual del parámetro; el archivo de origen no la declara en esta extracción.</p>}
          </section>
        )}

        {atributos.length > 0 && (
          <dl className="datos-clave">
            {atributos.map(([clave, valor]) => <div key={clave}><dt>{clave}</dt><dd>{valor}</dd></div>)}
          </dl>
        )}

        <section className="ficha-seccion" aria-labelledby="ficha-ubicacion">
          <h3 id="ficha-ubicacion">Ubicación</h3>
          <dl className="datos-clave">
            {p.cuerpo_agua && <div><dt>Cuerpo de agua</dt><dd>{p.cuerpo_agua}</dd></div>}
            {lugar && <div><dt>Municipio</dt><dd>{lugar}</dd></div>}
            {(p.cuenca_oficial || p.cuenca) && <div><dt>Cuenca</dt><dd>{p.cuenca_oficial || p.cuenca}</dd></div>}
            <div><dt>Coordenadas</dt><dd className="mono">{lat.toFixed(5)}, {lon.toFixed(5)}</dd></div>
          </dl>
          <p className="texto-suave"><MapPin aria-hidden="true" /> {PRECISION[p.precision]?.largo}</p>
        </section>

        {p.advertencia && (
          <div className="aviso"><Info aria-hidden="true" /><p>{p.advertencia}</p></div>
        )}

        <section className="ficha-seccion" aria-labelledby="ficha-fuentes">
          <h3 id="ficha-fuentes">De dónde vienen estos datos</h3>
          <ul className="lista-fuentes">
            {fuentes.map((f) => (
              <li key={f.id}>
                <button className="enlace-fuente" onClick={() => onAbrirFuente(f.id)}>
                  <FileText aria-hidden="true" />
                  <span><strong>{f.titulo}</strong><small>{f.institucion} · {f.id}</small></span>
                </button>
                {f.url_fuente && <a className="enlace-externo" href={f.url_fuente} target="_blank" rel="noreferrer" aria-label={`Fuente oficial de ${f.titulo}`}><ExternalLink aria-hidden="true" /></a>}
              </li>
            ))}
            {(p.enlaces ?? []).map((e) => (
              <li key={e.url}>
                <a className="enlace-fuente" href={e.url} target="_blank" rel="noreferrer">
                  <ExternalLink aria-hidden="true" />
                  <span><strong>{e.texto}</strong><small>{new URL(e.url).hostname.replace(/^www\./, '')}</small></span>
                </a>
              </li>
            ))}
          </ul>
        </section>

        <SatelliteSnapshot feature={sitio} />

        <div className="descargas-ficha">
          {capa && <a className="boton secundario" href={urlDatos(capa.archivo)} download><Download aria-hidden="true" /> Capa (GeoJSON)</a>}
          {grupos.length > 0 && <a className="boton secundario" href={urlDatos('mediciones/mediciones.csv')} download><Download aria-hidden="true" /> Mediciones (CSV)</a>}
        </div>
      </div>
    </aside>
  )
}
