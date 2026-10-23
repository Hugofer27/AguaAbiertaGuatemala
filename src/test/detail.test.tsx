import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import DetailPanel from '../components/DetailPanel'
import type { CapaMeta, Fuente, Sitio } from '../types'

const sitio: Sitio = {
  type: 'Feature',
  id: 'INS-001',
  geometry: { type: 'Point', coordinates: [-90.43423, 14.90354] },
  properties: {
    id: 'INS-001',
    capa: 'monitoreo_insivumeh',
    nombre: 'Panajax I',
    tipo: 'Punto de monitoreo de calidad del agua',
    institucion: 'INSIVUMEH (publicado por el INE)',
    cuerpo_agua: 'Motagua',
    cuenca: 'Río Motagua',
    cuenca_oficial: 'Río Motagua',
    departamento: 'Guatemala',
    municipio: 'Chuarrancho',
    fecha: '2022–2024',
    tipo_dato: 'Medido',
    precision: 'publicada',
    fuente_ids: ['GT-DAT-0239'],
    advertencia: 'Campañas puntuales por año.',
    atributos: { 'Años con datos': '2022, 2024' },
    mediciones: [
      { codigo: 'PH', parametro: 'pH', valor: 8.36, unidad: 'unidades de pH', fecha: 'Marzo 2024', fuente_id: 'GT-DAT-0239', control: '', unidad_verificada: true },
      { codigo: 'OD', parametro: 'Oxígeno disuelto', valor: 14.9, unidad: 'mg/L', fecha: '2022', fuente_id: 'GT-DAT-0218', control: 'Revisar: supera la saturación teórica.', unidad_verificada: false },
    ],
  },
}

const fuente = {
  id: 'GT-DAT-0239',
  titulo: 'Base de monitoreo del agua INSIVUMEH 2024',
  institucion: 'INSIVUMEH',
  url_fuente: 'https://datos.ine.gob.gt/dataset/ejemplo',
} as Fuente

const capa = { id: 'monitoreo_insivumeh', titulo: 'Calidad del agua · INSIVUMEH', archivo: 'capas/monitoreo_insivumeh.geojson' } as CapaMeta

describe('ficha de un punto del mapa', () => {
  it('muestra mediciones agrupadas por campaña, la precisión y el control de calidad', () => {
    render(<DetailPanel sitio={sitio} capa={capa} catalogo={[fuente]} onClose={vi.fn()} onAbrirFuente={vi.fn()} />)
    expect(screen.getByRole('heading', { name: 'Panajax I' })).toBeInTheDocument()
    expect(screen.getByText('Marzo 2024')).toBeInTheDocument()
    expect(screen.getByText('2022')).toBeInTheDocument()
    expect(screen.getByText('Ubicación publicada')).toBeInTheDocument()
    expect(screen.getByText('Revisar: supera la saturación teórica.')).toBeInTheDocument()
    expect(screen.getByText(/Unidad habitual del parámetro/)).toBeInTheDocument()
    expect(screen.getByText('14.90354, -90.43423')).toBeInTheDocument()
  })

  it('en una barrera de ubicación aproximada avisa la precisión y enlaza a las notas que la respaldan', () => {
    const barrera: Sitio = {
      type: 'Feature',
      id: 'BAR-003',
      geometry: { type: 'Point', coordinates: [-90.5684, 14.4874] },
      properties: {
        ...sitio.properties,
        id: 'BAR-003',
        capa: 'barreras_plastico',
        nombre: 'Biobarda de AMSA en el Villalobos',
        precision: 'aproximada',
        fuente_ids: [],
        mediciones: undefined,
        atributos: { Opera: 'AMSA' },
        enlaces: [{ texto: 'La Hora (7 de julio de 2024)', url: 'https://lahora.gt/nacionales/ejemplo/' }],
      },
    }
    render(<DetailPanel sitio={barrera} capa={{ ...capa, id: 'barreras_plastico', archivo: 'capas/barreras_plastico.geojson' }} catalogo={[fuente]} onClose={vi.fn()} onAbrirFuente={vi.fn()} />)
    expect(screen.getByText('Ubicación aproximada')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /La Hora \(7 de julio de 2024\)/ })).toHaveAttribute('href', 'https://lahora.gt/nacionales/ejemplo/')
  })

  it('enlaza a la fuente del catálogo y a la fuente oficial', () => {
    const abrir = vi.fn()
    render(<DetailPanel sitio={sitio} capa={capa} catalogo={[fuente]} onClose={vi.fn()} onAbrirFuente={abrir} />)
    fireEvent.click(screen.getByRole('button', { name: /Base de monitoreo del agua INSIVUMEH 2024/ }))
    expect(abrir).toHaveBeenCalledWith('GT-DAT-0239')
    expect(screen.getByRole('link', { name: /Fuente oficial de Base de monitoreo/ })).toHaveAttribute('href', fuente.url_fuente)
    expect(screen.getByRole('link', { name: /Capa \(GeoJSON\)/ })).toHaveAttribute('href', './datos/capas/monitoreo_insivumeh.geojson')
  })
})
