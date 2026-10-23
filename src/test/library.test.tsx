import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import SourceLibrary from '../components/SourceLibrary'
import type { Faltante, Fuente, Resumen } from '../types'

const base: Omit<Fuente, 'id' | 'titulo' | 'institucion' | 'tema'> = {
  tipo: 'Conjunto de datos', institucion_detalle: '', categoria: 'Gobierno GT', anios: '2024', anio_min: 2024, anio_max: 2024,
  cobertura: '', parametros: '', formato: 'CSV', registros: '', licencia: 'CC BY', acceso: 'Público', acceso_detalle: 'Público',
  descarga: 'Archivo descargado', archivos: 1, url_fuente: 'https://example.org', url_descarga: '', sha256: ['abc'], verificacion: '',
  motagua_las_vacas: false, destacado: false, prioridad: 3, ids_alias: [], notas: '', capas: [],
}

const catalogo: Fuente[] = [
  { ...base, id: 'GT-DAT-0001', titulo: 'Calidad del agua AMSA 2024', institucion: 'AMSA', tema: 'Calidad del agua', ids_alias: ['GTW-069'], destacado: true },
  { ...base, id: 'GT-DAT-0002', titulo: 'Caudales del Motagua', institucion: 'INSIVUMEH', tema: 'Caudales e hidrología', motagua_las_vacas: true, capas: ['caudales_insivumeh'] },
  { ...base, id: 'GT-DOC-0001', tipo: 'Documento', titulo: 'Informe limnológico de Atitlán', institucion: 'AMSCLAE', tema: 'Calidad del agua' },
]

const faltantes: Faltante[] = [{
  id: 'FALT-001', institucion: 'MARN - SIA', institucion_corta: 'MARN', estado: 'Técnicamente inaccesible', dato_esperado: 'Puntos de monitoreo nacional',
  evidencia: '', url_evidencia: 'https://example.org/evidencia', que_se_intento: '', motivo: 'HTTP 403', solicitud_factible: 'Sí', siguiente_paso: 'Solicitud por la LAIP',
}]

const resumen = { conjuntos_de_datos: 2, documentos: 1, portales: 0, publicaciones: 0, faltantes: 1 } as Resumen

function renderizar(abrirId: string | null = null, onAbrirId = vi.fn()) {
  return render(
    <SourceLibrary catalogo={catalogo} faltantes={faltantes} resumen={resumen} config={{ enlace_originales: '' }} abrirId={abrirId} onAbrirId={onAbrirId} onVerCapa={vi.fn()} />,
  )
}

describe('vista de datos', () => {
  it('busca por título y por ID anterior (alias)', () => {
    renderizar()
    const buscar = screen.getByPlaceholderText(/Buscar por título/)
    fireEvent.change(buscar, { target: { value: 'GTW-069' } })
    expect(screen.getByText('Calidad del agua AMSA 2024')).toBeInTheDocument()
    expect(screen.queryByText('Caudales del Motagua')).not.toBeInTheDocument()
    fireEvent.change(buscar, { target: { value: 'nada que coincida' } })
    expect(screen.getByText('No hay resultados con esos filtros')).toBeInTheDocument()
  })

  it('filtra por Motagua / Las Vacas y separa documentos', () => {
    renderizar()
    fireEvent.click(screen.getByLabelText('Motagua / Las Vacas'))
    expect(screen.getByText('Caudales del Motagua')).toBeInTheDocument()
    expect(screen.queryByText('Calidad del agua AMSA 2024')).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('tab', { name: /Documentos/ }))
    expect(screen.queryByText('Informe limnológico de Atitlán')).not.toBeInTheDocument()
  })

  it('muestra los datos faltantes con cómo pedirlos', () => {
    renderizar()
    fireEvent.click(screen.getByRole('tab', { name: /Datos faltantes/ }))
    expect(screen.getByText('MARN - SIA')).toBeInTheDocument()
    expect(screen.getByText('Solicitud por la LAIP')).toBeInTheDocument()
  })

  it('abre la ficha con el enlace a la fuente oficial y los alias', () => {
    const cerrar = vi.fn()
    renderizar('GTW-069', cerrar)
    expect(screen.getByRole('dialog', { name: 'Calidad del agua AMSA 2024' })).toBeInTheDocument()
    expect(screen.getByText(/también GTW-069/)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Fuente oficial/ })).toHaveAttribute('href', 'https://example.org')
    fireEvent.click(screen.getByRole('button', { name: 'Cerrar ficha' }))
    expect(cerrar).toHaveBeenCalledWith(null)
  })
})
