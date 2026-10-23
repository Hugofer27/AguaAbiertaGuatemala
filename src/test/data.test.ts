import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import catalog from '../../public/data/catalog.json'
import selected from '../../public/data/selected_datasets.json'

const features = JSON.parse(
  readFileSync(resolve(process.cwd(), 'public/data/water_features.geojson'), 'utf-8'),
) as {
  features: Array<{
    geometry: { coordinates: [number, number] }
    properties: { emotion: string }
  }>
}

describe('paquete de datos del MVP', () => {
  it('incluye los 75 archivos descargados', () => {
    expect(catalog).toHaveLength(75)
    expect(new Set(catalog.map((item) => item.sha256)).size).toBe(75)
  })

  it('selecciona exactamente 12 conjuntos representativos', () => {
    expect(selected).toHaveLength(12)
    expect(selected.every((item) => item.selectedMvp && item.selectionReason)).toBe(true)
  })

  it('solo publica coordenadas numéricas en el GeoJSON', () => {
    expect(features.features.length).toBeGreaterThan(100)
    for (const item of features.features) {
      const [longitude, latitude] = item.geometry.coordinates
      expect(Number.isFinite(longitude)).toBe(true)
      expect(Number.isFinite(latitude)).toBe(true)
      expect(longitude).toBeGreaterThanOrEqual(-93)
      expect(longitude).toBeLessThanOrEqual(-88)
      expect(latitude).toBeGreaterThanOrEqual(13)
      expect(latitude).toBeLessThanOrEqual(18)
      expect(item.properties.emotion).toBe('Sin datos suficientes')
    }
  })
})
