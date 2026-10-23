export type ViewName = 'explore' | 'library' | 'method'

export interface Evidence {
  parameter: string
  value: number
  unit: string
  date: string
  station: string
  sourceId: string
}

export interface SeriesPoint {
  label: string
  value: number
  unit?: string
}

export interface WaterFeatureProperties {
  name: string
  kind: string
  basin: string
  department: string
  municipality: string
  emotion: string
  emotionCode: string
  emotionReason: string
  latest: string
  parameters: string[]
  institution: string
  sourceIds: string[]
  confidence: string
  warning: string
  evidence: Evidence[]
  series: SeriesPoint[]
}

export interface WaterFeature {
  type: 'Feature'
  id: string
  geometry: { type: 'Point'; coordinates: [number, number] }
  properties: WaterFeatureProperties
}

export interface WaterFeatureCollection {
  type: 'FeatureCollection'
  features: WaterFeature[]
}

export interface CatalogItem {
  number: number
  id: string
  title: string
  fileName: string
  institution: string
  topic: string
  territory: string
  period: string
  format: string
  bytes: number
  size: string
  accessState: string
  summary: string
  sourceUrl: string
  downloadUrl: string
  localPath: string
  license: string
  sha256: string
  records: string
  dateMin: string
  dateMax: string
  parameters: string[]
  coordinates: string
  selectedMvp: boolean
  selectionReason?: string
  profile?: Record<string, unknown>
}

export interface Summary {
  cutoff: string
  inventoriedResources: number
  downloadedFiles: number
  organizations: number
  missingDataRecords: number
  selectedMvpDatasets: number
  mappedFeatures: number
  formats: string[]
  institutions: string[]
  topics: string[]
  accessStates: string[]
  mapStyle: string
  mapAttribution: string
}

export interface AppData {
  catalog: CatalogItem[]
  selected: CatalogItem[]
  features: WaterFeatureCollection
  summary: Summary
}
