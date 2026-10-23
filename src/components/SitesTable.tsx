import { useMemo, useState } from 'react'
import { Search } from 'lucide-react'
import { estiloDe } from '../capas'
import { PRECISION } from '../textos'
import type { CapaMeta, Coleccion, Sitio } from '../types'

interface SitesTableProps {
  capas: CapaMeta[]
  colecciones: Record<string, Coleccion>
  visibles: Record<string, boolean>
  onAbrir: (sitio: Sitio) => void
}

const LIMITE = 150

/** Alternativa accesible al mapa: todos los puntos en una tabla filtrable. */
export default function SitesTable({ capas, colecciones, visibles, onAbrir }: SitesTableProps) {
  const puntuales = capas.filter((c) => c.geometria === 'punto')
  const [capa, setCapa] = useState('activas')
  const [texto, setTexto] = useState('')
  const filas = useMemo(() => {
    const q = texto.trim().toLocaleLowerCase('es')
    return puntuales
      .filter((c) => (capa === 'activas' ? visibles[c.id] : capa === 'todas' || c.id === capa))
      .flatMap((c) => (colecciones[c.id]?.features as Sitio[] | undefined) ?? [])
      .filter((s) => !q || `${s.properties.nombre} ${s.properties.municipio} ${s.properties.departamento} ${s.properties.cuerpo_agua} ${s.properties.cuenca_oficial ?? ''}`.toLocaleLowerCase('es').includes(q))
  }, [capa, colecciones, puntuales, texto, visibles])
  const titulo = (id: string) => capas.find((c) => c.id === id)?.titulo ?? id

  return (
    <section className="tabla-sitios" aria-labelledby="titulo-tabla-sitios">
      <div className="tabla-sitios-cabeza">
        <h2 id="titulo-tabla-sitios">Puntos del mapa en tabla</h2>
        <label className="campo-busqueda compacto">
          <Search aria-hidden="true" />
          <span className="sr-only">Filtrar puntos</span>
          <input type="search" value={texto} onChange={(e) => setTexto(e.target.value)} placeholder="Filtrar por nombre, municipio, cuenca…" />
        </label>
        <label className="selector">
          <span>Capa</span>
          <select value={capa} onChange={(e) => setCapa(e.target.value)}>
            <option value="activas">Capas activas</option>
            <option value="todas">Todas</option>
            {puntuales.map((c) => <option key={c.id} value={c.id}>{c.titulo}</option>)}
          </select>
        </label>
        <p className="conteo-resultados" role="status">{filas.length.toLocaleString('es-GT')} puntos</p>
      </div>
      <div className="tabla-desplazable">
        <table>
          <thead>
            <tr><th scope="col">Nombre</th><th scope="col">Capa</th><th scope="col">Lugar</th><th scope="col">Fecha</th><th scope="col">Ubicación</th><th scope="col"><span className="sr-only">Acción</span></th></tr>
          </thead>
          <tbody>
            {filas.slice(0, LIMITE).map((s) => (
              <tr key={s.id}>
                <th scope="row">{s.properties.nombre}</th>
                <td><span className="muestra muestra-punto" style={{ '--muestra': estiloDe(s.properties.capa).color } as React.CSSProperties} aria-hidden="true" /> {titulo(s.properties.capa)}</td>
                <td>{[s.properties.municipio, s.properties.departamento].filter(Boolean).join(', ') || s.properties.cuenca_oficial || '—'}</td>
                <td>{s.properties.fecha || '—'}</td>
                <td>{PRECISION[s.properties.precision]?.corto}</td>
                <td><button className="boton-texto" onClick={() => onAbrir(s)}>Abrir ficha</button></td>
              </tr>
            ))}
          </tbody>
        </table>
        {filas.length > LIMITE && <p className="nota-pie">Se muestran los primeros {LIMITE}. Use el filtro o descargue la tabla completa de sitios en Acerca de.</p>}
      </div>
    </section>
  )
}
