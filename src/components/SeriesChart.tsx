import type { Serie } from '../types'
import { formatoValor } from '../textos'

/** Gráfico de barras simple en SVG, con tabla equivalente para lectores de pantalla. */
export default function SeriesChart({ serie, color }: { serie: Serie; color: string }) {
  const puntos = serie.puntos
  if (puntos.length < 2) return null
  const valores = puntos.map((p) => p.valor)
  const maximo = Math.max(...valores)
  const minimo = Math.min(0, ...valores)
  // El pH se lee mejor con un eje que no empieza en cero.
  const base = serie.unidad === 'pH' ? Math.floor(Math.min(...valores) * 10) / 10 - 0.1 : minimo
  const rango = maximo - base || 1
  const ancho = 300
  const alto = 120
  const margen = { izq: 4, der: 4, arriba: 14, abajo: 18 }
  const paso = (ancho - margen.izq - margen.der) / puntos.length
  const barra = Math.max(4, paso * 0.68)
  const indiceMax = valores.indexOf(maximo)

  return (
    <figure className="grafico-serie">
      <figcaption>
        <strong>{serie.titulo}</strong>
        <span>{serie.unidad}</span>
      </figcaption>
      <svg viewBox={`0 0 ${ancho} ${alto}`} role="img" aria-label={`${serie.titulo}: de ${puntos[0].etiqueta} a ${puntos.at(-1)!.etiqueta}, máximo ${formatoValor(maximo)} ${serie.unidad} en ${puntos[indiceMax].etiqueta}`}>
        <line x1={margen.izq} x2={ancho - margen.der} y1={alto - margen.abajo} y2={alto - margen.abajo} className="eje" />
        {puntos.map((punto, i) => {
          const h = ((punto.valor - base) / rango) * (alto - margen.arriba - margen.abajo)
          const x = margen.izq + i * paso + (paso - barra) / 2
          const y = alto - margen.abajo - h
          return (
            <g key={punto.etiqueta}>
              <rect x={x} y={y} width={barra} height={Math.max(h, 1)} rx={2} fill={color} opacity={i === indiceMax ? 1 : 0.72}>
                <title>{`${punto.etiqueta}: ${formatoValor(punto.valor)} ${serie.unidad}`}</title>
              </rect>
              {(puntos.length <= 12 || i % 2 === 0) && (
                <text x={x + barra / 2} y={alto - 5} textAnchor="middle" className="etiqueta-eje">{punto.etiqueta}</text>
              )}
              {i === indiceMax && (
                <text x={x + barra / 2} y={Math.max(10, y - 3)} textAnchor="middle" className="valor-max">{formatoValor(punto.valor)}</text>
              )}
            </g>
          )
        })}
      </svg>
      <table className="sr-only">
        <caption>{serie.titulo}</caption>
        <tbody>{puntos.map((p) => <tr key={p.etiqueta}><th>{p.etiqueta}</th><td>{formatoValor(p.valor)} {serie.unidad}</td></tr>)}</tbody>
      </table>
    </figure>
  )
}
