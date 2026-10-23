import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import SourceLibrary from '../components/SourceLibrary'
import type { CatalogItem, Summary } from '../types'

const catalog: CatalogItem[] = [
  {
    number: 1,
    id: 'GTW-001',
    title: 'Caudales de ejemplo',
    fileName: 'caudales.csv',
    institution: 'INSIVUMEH',
    topic: 'Hidrología',
    territory: 'Río Motagua',
    period: '2024',
    format: 'CSV',
    bytes: 1024,
    size: '1 KB',
    accessState: 'Descargado y verificado',
    summary: 'Caudal mensual',
    sourceUrl: 'https://example.org',
    downloadUrl: '',
    localPath: '../fuente_de_datos/INSIVUMEH/caudales.csv',
    license: 'CC BY',
    sha256: 'abc',
    records: '12',
    dateMin: '',
    dateMax: '',
    parameters: ['Caudal'],
    coordinates: 'yes',
    selectedMvp: true,
    selectionReason: 'Cobertura oficial',
  },
  {
    number: 2,
    id: 'GTW-002',
    title: 'Calidad del lago',
    fileName: 'lago.pdf',
    institution: 'AMSCLAE',
    topic: 'Calidad del agua',
    territory: 'Lago de Atitlán',
    period: '2020',
    format: 'PDF',
    bytes: 2048,
    size: '2 KB',
    accessState: 'Descargado y verificado',
    summary: 'Informe técnico',
    sourceUrl: 'https://example.org/lago',
    downloadUrl: '',
    localPath: '../fuente_de_datos/AMSCLAE/lago.pdf',
    license: 'No indicada',
    sha256: 'def',
    records: '10 páginas',
    dateMin: '',
    dateMax: '',
    parameters: [],
    coordinates: 'unknown',
    selectedMvp: false,
  },
]

const summary: Summary = {
  cutoff: '2026-10-21',
  inventoriedResources: 113,
  downloadedFiles: 75,
  organizations: 42,
  missingDataRecords: 16,
  selectedMvpDatasets: 12,
  mappedFeatures: 155,
  formats: ['CSV', 'PDF'],
  institutions: ['AMSCLAE', 'INSIVUMEH'],
  topics: ['Calidad del agua', 'Hidrología'],
  accessStates: ['Descargado y verificado'],
  mapStyle: '',
  mapAttribution: '',
}

describe('biblioteca de fuentes', () => {
  it('busca por institución y muestra el estado vacío', () => {
    render(<SourceLibrary catalog={catalog} summary={summary} />)
    const search = screen.getByPlaceholderText('Buscar archivo, institución o territorio…')
    fireEvent.change(search, { target: { value: 'AMSCLAE' } })
    expect(screen.getByText('Calidad del lago')).toBeInTheDocument()
    expect(screen.queryByText('Caudales de ejemplo')).not.toBeInTheDocument()
    fireEvent.change(search, { target: { value: 'sin coincidencias' } })
    expect(screen.getByText('No hay archivos con esos filtros')).toBeInTheDocument()
  })

  it('abre una ficha técnica accesible', () => {
    render(<SourceLibrary catalog={catalog} summary={summary} />)
    fireEvent.click(screen.getByLabelText('Abrir ficha de Caudales de ejemplo'))
    expect(screen.getByRole('heading', { name: 'Caudales de ejemplo' })).toBeInTheDocument()
    expect(screen.getByText('Por qué está en el MVP')).toBeInTheDocument()
    expect(screen.getByText('Cobertura oficial')).toBeInTheDocument()
  })
})
