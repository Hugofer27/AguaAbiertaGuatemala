import { useEffect, useRef } from 'react'
import {
  Map as MapLibreMap,
  Marker,
  NavigationControl,
  ScaleControl,
  setWorkerUrl,
  type MapGeoJSONFeature,
  type MapMouseEvent,
  type StyleSpecification,
} from 'maplibre-gl'
import mapLibreWorkerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url'
import type { WaterFeature, WaterFeatureCollection } from '../types'

setWorkerUrl(mapLibreWorkerUrl)

interface MapViewProps {
  data: WaterFeatureCollection
  styleUrl: string
  visibleLayers: Record<string, boolean>
  hydrologyEmphasis: boolean
  focusFeatureId: string | null
  onSelect: (feature: WaterFeature) => void
  onStatus: (status: 'loading' | 'ready' | 'fallback') => void
}

const FALLBACK_STYLE: StyleSpecification = {
  version: 8,
  name: 'Atlas local de respaldo',
  sources: {},
  layers: [{ id: 'background', type: 'background', paint: { 'background-color': '#071f27' } }],
}

const LAYERS = [
  { id: 'monitoring', color: '#34b7a8', radius: 5.5, minzoom: 5 },
  { id: 'lakes', color: '#73d7ca', radius: 8, minzoom: 4 },
  { id: 'climate', color: '#ffb36a', radius: 6, minzoom: 4.7 },
] as const

function withLayerGroups(collection: WaterFeatureCollection) {
  return {
    type: 'FeatureCollection' as const,
    features: collection.features.map((item) => ({
      ...item,
      properties: {
        ...item.properties,
        featureId: String(item.id),
        layerGroup: item.properties.kind.includes('meteorológica')
          ? 'climate'
          : item.properties.kind.includes('Lago')
            ? 'lakes'
            : 'monitoring',
      },
    })),
  }
}

type HydrologyPaintProperty =
  | 'line-color'
  | 'line-width'
  | 'line-opacity'
  | 'fill-color'
  | 'fill-opacity'
  | 'text-color'
  | 'text-halo-color'
  | 'text-halo-width'

function applyHydrologyEmphasis(map: MapLibreMap, enabled: boolean, originals: Map<string, unknown>) {
  const layers = map.getStyle().layers ?? []
  const remember = (layerId: string, property: HydrologyPaintProperty) => {
    const key = `${layerId}:${property}`
    if (!originals.has(key)) originals.set(key, map.getPaintProperty(layerId, property))
    return originals.get(key)
  }
  const set = (layerId: string, property: HydrologyPaintProperty, emphasized: unknown) => {
    const original = remember(layerId, property)
    map.setPaintProperty(layerId, property, (enabled ? emphasized : original) as never)
  }

  layers.forEach((layer) => {
    const sourceLayer = 'source-layer' in layer ? String(layer['source-layer'] ?? '') : ''
    const signature = `${layer.id} ${sourceLayer}`.toLowerCase()
    const isFlowLine = layer.type === 'line' && /(waterway|river|stream|canal|drain)/.test(signature)
    const isWaterArea = layer.type === 'fill' && /(^|[-_ ])water($|[-_ ])|lake|reservoir/.test(signature)
    const isWaterLabel = layer.type === 'symbol' && /(water|river|stream|lake)/.test(signature)

    if (isFlowLine) {
      set(layer.id, 'line-color', [
        'interpolate', ['linear'], ['zoom'],
        5, '#3a9fc5',
        9, '#157fae',
        13, '#075f91',
      ])
      set(layer.id, 'line-width', [
        'interpolate', ['linear'], ['zoom'],
        5, 1.15,
        9, 2.15,
        13, 4.1,
      ])
      set(layer.id, 'line-opacity', 0.94)
    } else if (isWaterArea) {
      set(layer.id, 'fill-color', '#8ecde8')
      set(layer.id, 'fill-opacity', 0.82)
    } else if (isWaterLabel) {
      set(layer.id, 'text-color', '#075f82')
      set(layer.id, 'text-halo-color', '#f7fcfd')
      set(layer.id, 'text-halo-width', 1.4)
    }
  })
}

export default function MapView({
  data,
  styleUrl,
  visibleLayers,
  hydrologyEmphasis,
  focusFeatureId,
  onSelect,
  onStatus,
}: MapViewProps) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const mapRef = useRef<MapLibreMap | null>(null)
  const loadedRef = useRef(false)
  const featureDataRef = useRef(withLayerGroups(data))
  const onSelectRef = useRef(onSelect)
  const visibleLayersRef = useRef(visibleLayers)
  const hydrologyEmphasisRef = useRef(hydrologyEmphasis)
  const hydrologyOriginalsRef = useRef(new Map<string, unknown>())
  const selectedMarkerRef = useRef<Marker | null>(null)

  useEffect(() => {
    onSelectRef.current = onSelect
  }, [onSelect])

  useEffect(() => {
    visibleLayersRef.current = visibleLayers
  }, [visibleLayers])

  useEffect(() => {
    hydrologyEmphasisRef.current = hydrologyEmphasis
    const map = mapRef.current
    if (map && loadedRef.current) applyHydrologyEmphasis(map, hydrologyEmphasis, hydrologyOriginalsRef.current)
  }, [hydrologyEmphasis])

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return

    loadedRef.current = false
    onStatus('loading')
    const map = new MapLibreMap({
      container: containerRef.current,
      style: styleUrl,
      center: [-90.35, 15.35],
      zoom: 6.15,
      pitch: 18,
      bearing: -3,
      minZoom: 4.8,
      maxZoom: 14,
      maxPitch: 55,
      attributionControl: { compact: true },
    })
    mapRef.current = map
    map.addControl(new NavigationControl({ showCompass: true }), 'bottom-right')
    map.addControl(new ScaleControl({ maxWidth: 120, unit: 'metric' }), 'bottom-left')

    const addDataLayers = () => {
      applyHydrologyEmphasis(map, hydrologyEmphasisRef.current, hydrologyOriginalsRef.current)
      if (map.getSource('water-features')) return
      map.addSource('water-features', { type: 'geojson', data: featureDataRef.current as never })
      LAYERS.forEach((layer) => {
        map.addLayer({
          id: `water-${layer.id}`,
          type: 'circle',
          source: 'water-features',
          minzoom: layer.minzoom,
          filter: ['==', ['get', 'layerGroup'], layer.id],
          layout: { visibility: visibleLayersRef.current[layer.id] ? 'visible' : 'none' },
          paint: {
            'circle-radius': ['interpolate', ['linear'], ['zoom'], 5, layer.radius - 1.5, 10, layer.radius + 2.5],
            'circle-color': layer.color,
            'circle-stroke-color': '#071f27',
            'circle-stroke-width': 1.5,
            'circle-opacity': 0.92,
          },
        })
      })
      const activeGroups = LAYERS.filter(({ id }) => visibleLayersRef.current[id]).map(({ id }) => id)
      map.addLayer({
        id: 'water-hit-areas',
        type: 'circle',
        source: 'water-features',
        minzoom: 4,
        filter: ['in', ['get', 'layerGroup'], ['literal', activeGroups]],
        paint: {
          'circle-radius': ['interpolate', ['linear'], ['zoom'], 5, 16, 10, 22],
          'circle-color': '#071f27',
          'circle-opacity': 0.01,
          'circle-stroke-opacity': 0,
        },
      })
      map.on('mouseenter', 'water-hit-areas', () => {
        map.getCanvas().style.cursor = 'pointer'
      })
      map.on('mouseleave', 'water-hit-areas', () => {
        map.getCanvas().style.cursor = ''
      })
      map.on('click', 'water-hit-areas', (event) => {
        const hit = (event as MapMouseEvent & { features?: MapGeoJSONFeature[] }).features?.[0]
        const featureId = hit?.properties?.featureId ?? hit?.id
        if (featureId === undefined || featureId === null) return
        const original = data.features.find((item) => String(item.id) === String(featureId))
        if (original) onSelectRef.current(original)
      })
      loadedRef.current = true
      onStatus(map.getStyle().name === FALLBACK_STYLE.name ? 'fallback' : 'ready')
    }

    map.on('load', addDataLayers)
    map.on('style.load', addDataLayers)
    map.on('error', (event) => {
      const errorMessage = String(event.error?.message || '').toLowerCase()
      if (!loadedRef.current && errorMessage.includes('style')) {
        map.setStyle(FALLBACK_STYLE)
        onStatus('fallback')
      } else if (loadedRef.current && /tile|fetch|network|request|cors|failed to load/.test(errorMessage)) {
        onStatus('fallback')
      }
    })

    const fallbackTimer = window.setTimeout(() => {
      if (!loadedRef.current) {
        map.setStyle(FALLBACK_STYLE)
        onStatus('fallback')
      }
    }, 8000)

    const observer = new ResizeObserver(() => map.resize())
    observer.observe(containerRef.current)

    return () => {
      window.clearTimeout(fallbackTimer)
      observer.disconnect()
      selectedMarkerRef.current?.remove()
      selectedMarkerRef.current = null
      hydrologyOriginalsRef.current.clear()
      map.remove()
      mapRef.current = null
    }
  }, [data.features, onStatus, styleUrl])

  useEffect(() => {
    const map = mapRef.current
    if (!map || !loadedRef.current) return
    LAYERS.forEach(({ id }) => {
      const mapLayer = `water-${id}`
      if (map.getLayer(mapLayer)) {
        map.setLayoutProperty(mapLayer, 'visibility', visibleLayers[id] ? 'visible' : 'none')
      }
    })
    if (map.getLayer('water-hit-areas')) {
      const activeGroups = LAYERS.filter(({ id }) => visibleLayers[id]).map(({ id }) => id)
      map.setFilter('water-hit-areas', ['in', ['get', 'layerGroup'], ['literal', activeGroups]] as never)
    }
  }, [visibleLayers])

  useEffect(() => {
    const map = mapRef.current
    selectedMarkerRef.current?.remove()
    selectedMarkerRef.current = null
    if (!map || !focusFeatureId) return
    const target = data.features.find((item) => String(item.id) === focusFeatureId)
    if (!target) return

    const markerElement = document.createElement('div')
    markerElement.className = 'selected-water-marker'
    markerElement.setAttribute('aria-hidden', 'true')
    markerElement.append(document.createElement('span'))
    selectedMarkerRef.current = new Marker({ element: markerElement, anchor: 'center' })
      .setLngLat(target.geometry.coordinates)
      .addTo(map)

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      map.jumpTo({ center: target.geometry.coordinates, zoom: 9 })
    } else {
      map.flyTo({ center: target.geometry.coordinates, zoom: 9, essential: false })
    }
  }, [data.features, focusFeatureId, styleUrl])

  return <div ref={containerRef} className="map-canvas" aria-label="Mapa interactivo de fuentes hídricas" />
}
