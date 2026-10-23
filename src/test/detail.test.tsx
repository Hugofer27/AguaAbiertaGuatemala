import { act, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import DetailPanel from '../components/DetailPanel'
import type { CatalogItem, WaterFeature } from '../types'

const feature: WaterFeature = {
  type: 'Feature',
  id: 'station-1',
  geometry: { type: 'Point', coordinates: [-89.88812, 15.29879] },
  properties: {
    name: 'Matucuy',
    kind: 'Punto de muestreo',
    basin: 'Río Polochic',
    department: 'Alta Verapaz',
    municipality: 'Panzós',
    emotion: 'Sin datos suficientes',
    emotionCode: 'insufficient',
    emotionReason: 'La serie disponible no permite una conclusión científica.',
    latest: '6/02/2023',
    parameters: ['pH (unidad)'],
    institution: 'INE / INSIVUMEH',
    sourceIds: ['GTW-003'],
    confidence: 'Alta para ubicación',
    warning: 'Datos históricos.',
    evidence: [{ parameter: 'pH (unidad)', value: 7.93, unit: 'pH', date: '6/02/2023', station: 'Matucuy', sourceId: 'GTW-003' }],
    series: [],
  },
}

const source: CatalogItem = {
  number: 48,
  id: 'GTW-003',
  title: 'Calidad del agua INSIVUMEH 2023',
  fileName: 'calidad.csv',
  institution: 'INE/INSIVUMEH',
  topic: 'Calidad del agua',
  territory: 'Guatemala',
  period: '2023',
  format: 'CSV',
  bytes: 100,
  size: '100 B',
  accessState: 'Descargado y verificado',
  summary: 'Muestreo',
  sourceUrl: 'https://example.org/source',
  downloadUrl: '',
  localPath: '../fuente_de_datos/INSIVUMEH/calidad.csv',
  license: 'CC BY',
  sha256: 'abc',
  records: '5323',
  dateMin: '2023-02-06',
  dateMax: '2023-12-21',
  parameters: ['pH'],
  coordinates: 'yes',
  selectedMvp: false,
}

afterEach(() => {
  vi.useRealTimers()
})

describe('ficha de un punto del mapa', () => {
  it('revela primero el estado y después el archivo que origina el punto', () => {
    vi.useFakeTimers()
    Object.defineProperty(window, 'matchMedia', {
      configurable: true,
      value: () => ({ matches: false }),
    })

    render(<DetailPanel feature={feature} catalog={[source]} onClose={vi.fn()} />)
    expect(screen.getByText('Estado narrativo derivado por el portal')).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: '¿Por qué aparece este punto?' })).not.toBeInTheDocument()

    act(() => vi.advanceTimersByTime(1100))

    expect(screen.getByRole('heading', { name: '¿Por qué aparece este punto?' })).toBeInTheDocument()
    expect(screen.getByText(source.fileName)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: `Abrir archivo ${source.fileName}` })).toHaveAttribute('href', source.localPath)
    expect(screen.getByText(/Latitud 15.29879/)).toBeInTheDocument()
  })
})
