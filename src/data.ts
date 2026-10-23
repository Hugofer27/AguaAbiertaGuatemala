import type { AppData } from './types'

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(path)
  if (!response.ok) {
    throw new Error(`No se pudo cargar ${path} (${response.status})`)
  }
  return response.json() as Promise<T>
}

export async function loadAppData(): Promise<AppData> {
  const [catalog, selected, features, summary] = await Promise.all([
    getJson<AppData['catalog']>('./data/catalog.json'),
    getJson<AppData['selected']>('./data/selected_datasets.json'),
    getJson<AppData['features']>('./data/water_features.geojson'),
    getJson<AppData['summary']>('./data/summary.json'),
  ])
  return { catalog, selected, features, summary }
}
