import { fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import SatelliteSnapshot, { buildSatelliteUrls } from '../components/SatelliteSnapshot'
import type { WaterFeature } from '../types'

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
    evidence: [],
    series: [],
  },
}

afterEach(() => {
  vi.useRealTimers()
})

describe('imagen satelital reciente', () => {
  it('construye una solicitud NASA fechada y centrada en la coordenada publicada', () => {
    const urls = buildSatelliteUrls(feature, '2026-10-21')
    const snapshot = new URL(urls.snapshot)
    const worldview = new URL(urls.worldview)

    expect(snapshot.hostname).toBe('wvs.earthdata.nasa.gov')
    expect(snapshot.searchParams.get('TIME')).toBe('2026-10-21T00:00:00Z')
    expect(snapshot.searchParams.get('BBOX')).toBe('15.11879,-90.06812,15.47879,-89.70812')
    expect(snapshot.searchParams.get('MARKER')).toBe('15.29879,-89.88812')
    expect(snapshot.searchParams.get('LAYERS')).toContain('MODIS_Aqua_CorrectedReflectance_TrueColor')
    expect(worldview.searchParams.get('v')).toBe('-90.06812,15.11879,-89.70812,15.47879')
    expect(worldview.searchParams.get('s')).toBe('-89.88812,15.29879')
  })

  it('genera un recorte diferente para otra coordenada', () => {
    const easternFeature: WaterFeature = {
      ...feature,
      id: 'station-2',
      geometry: { type: 'Point', coordinates: [-88.29, 15.73] },
      properties: { ...feature.properties, name: 'El Quetzalito' },
    }
    const first = new URL(buildSatelliteUrls(feature, '2026-10-21').snapshot)
    const second = new URL(buildSatelliteUrls(easternFeature, '2026-10-21').snapshot)

    expect(second.searchParams.get('BBOX')).toBe('15.55000,-88.47000,15.91000,-88.11000')
    expect(second.searchParams.get('MARKER')).toBe('15.73000,-88.29000')
    expect(second.searchParams.get('BBOX')).not.toBe(first.searchParams.get('BBOX'))
  })

  it('solo solicita la imagen después de que el usuario abre el módulo', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-10-22T12:00:00Z'))

    render(<SatelliteSnapshot feature={feature} />)
    expect(screen.queryByRole('img')).not.toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /Ver imagen satelital reciente/i }))

    const image = screen.getByRole('img')
    expect(image).toHaveAttribute('src', expect.stringContaining('TIME=2026-10-21T00%3A00%3A00Z'))
    expect(screen.getByText(/Centro consultado · 15.29879°, -89.88812°/)).toBeInTheDocument()
    expect(screen.getByText(/recorte aproximado de 40 km/)).toBeInTheDocument()
    expect(screen.getByText(/No es una transmisión en directo/)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Explorar ubicación y fechas en NASA Worldview/i })).toHaveAttribute('target', '_blank')
  })
})
