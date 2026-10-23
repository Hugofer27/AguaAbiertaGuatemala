import { useEffect, useRef } from 'react'
import {
  Map as MapLibreMap,
  Marker,
  NavigationControl,
  Popup,
  ScaleControl,
  setWorkerUrl,
  type ExpressionSpecification,
  type MapGeoJSONFeature,
  type StyleSpecification,
} from 'maplibre-gl'
import mapLibreWorkerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url'
import { ENFOQUES, MAPAS_BASE, estiloDe, type MapaBase } from '../capas'
import type { CapaMeta, Coleccion, Cuenca, Seleccion, Sitio } from '../types'

setWorkerUrl(mapLibreWorkerUrl)

export type EstadoMapa = 'cargando' | 'listo' | 'respaldo'

interface MapViewProps {
  capas: CapaMeta[]
  colecciones: Record<string, Coleccion>
  visibles: Record<string, boolean>
  mapaBase: MapaBase
  resaltarRios: boolean
  enfoque: { id: string; vez: number } | null
  seleccion: Seleccion | null
  oscuro: boolean
  onSeleccion: (seleccion: Seleccion) => void
  onEstado: (estado: EstadoMapa) => void
}

const NOMBRE_RESPALDO = 'Mapa local de respaldo'

function estiloRespaldo(oscuro: boolean): StyleSpecification {
  return {
    version: 8,
    name: NOMBRE_RESPALDO,
    sources: {},
    layers: [{ id: 'fondo', type: 'background', paint: { 'background-color': oscuro ? '#0d1b1e' : '#eef3f3' } }],
  }
}

type PropiedadRio = 'line-color' | 'line-width' | 'line-opacity' | 'fill-color' | 'fill-opacity'

/** Resalta ríos y cuerpos de agua del mapa base, recordando los valores originales para revertir. */
function resaltarHidrografia(map: MapLibreMap, activo: boolean, originales: Map<string, unknown>, oscuro: boolean) {
  for (const capa of map.getStyle().layers ?? []) {
    if (capa.id.startsWith('aa-')) continue
    const fuente = 'source-layer' in capa ? String(capa['source-layer'] ?? '') : ''
    const firma = `${capa.id} ${fuente}`.toLowerCase()
    const asignar = (propiedad: PropiedadRio, valor: unknown) => {
      const clave = `${capa.id}:${propiedad}`
      if (!originales.has(clave)) originales.set(clave, map.getPaintProperty(capa.id, propiedad))
      map.setPaintProperty(capa.id, propiedad, (activo ? valor : originales.get(clave)) as never)
    }
    if (capa.type === 'line' && /(waterway|river|stream|canal)/.test(firma)) {
      asignar('line-color', oscuro ? '#4ea8d6' : '#3b8fc4')
      asignar('line-width', ['interpolate', ['linear'], ['zoom'], 5, 0.8, 9, 1.6, 13, 3.2])
      asignar('line-opacity', 0.9)
    } else if (capa.type === 'fill' && /(^|[-_ ])water($|[-_ ])|lake|reservoir/.test(firma)) {
      asignar('fill-color', oscuro ? '#1d4f66' : '#b9dcef')
      asignar('fill-opacity', 0.9)
    }
  }
}

function radioPunto(capaId: string, tamano: number): ExpressionSpecification {
  if (capaId === 'plasticos') {
    return ['interpolate', ['linear'], ['zoom'],
      5, ['+', 1.8, ['*', 0.11, ['sqrt', ['get', 'emision_t']]]],
      10, ['+', 3, ['*', 0.24, ['sqrt', ['get', 'emision_t']]]],
    ]
  }
  return ['interpolate', ['linear'], ['zoom'], 5, tamano * 0.55, 10, tamano, 14, tamano * 1.5]
}

function limitesDe(coordenadas: unknown): [[number, number], [number, number]] | null {
  let oeste = Infinity, sur = Infinity, este = -Infinity, norte = -Infinity
  const recorrer = (valor: unknown) => {
    if (!Array.isArray(valor)) return
    if (typeof valor[0] === 'number') {
      const [lon, lat] = valor as number[]
      oeste = Math.min(oeste, lon); este = Math.max(este, lon); sur = Math.min(sur, lat); norte = Math.max(norte, lat)
      return
    }
    valor.forEach(recorrer)
  }
  recorrer(coordenadas)
  return Number.isFinite(oeste) ? [[oeste, sur], [este, norte]] : null
}

export default function MapView({
  capas,
  colecciones,
  visibles,
  mapaBase,
  resaltarRios,
  enfoque,
  seleccion,
  oscuro,
  onSeleccion,
  onEstado,
}: MapViewProps) {
  const contenedor = useRef<HTMLDivElement | null>(null)
  const mapa = useRef<MapLibreMap | null>(null)
  const listo = useRef(false)
  const props = useRef({ capas, colecciones, visibles, resaltarRios, oscuro, seleccion, onSeleccion, onEstado })
  const originales = useRef(new Map<string, unknown>())
  const marcador = useRef<Marker | null>(null)

  props.current = { capas, colecciones, visibles, resaltarRios, oscuro, seleccion, onSeleccion, onEstado }

  const capasPunto = () => props.current.capas.filter((c) => c.geometria === 'punto').map((c) => `aa-${c.id}`)

  // Crear el mapa una sola vez.
  useEffect(() => {
    if (!contenedor.current || mapa.current) return
    const map = new MapLibreMap({
      container: contenedor.current,
      style: MAPAS_BASE[mapaBase].estilo,
      bounds: ENFOQUES[0].limites,
      fitBoundsOptions: { padding: 24 },
      minZoom: 4.5,
      maxZoom: 15,
      maxPitch: 50,
      attributionControl: { compact: true },
    })
    mapa.current = map
    map.addControl(new NavigationControl({ showCompass: true, visualizePitch: true }), 'bottom-right')
    map.addControl(new ScaleControl({ maxWidth: 110, unit: 'metric' }), 'bottom-left')
    const etiqueta = new Popup({ closeButton: false, closeOnClick: false, offset: 10, className: 'etiqueta-mapa' })

    const agregarCapas = () => {
      const { capas: metas, colecciones: datos, visibles: vis } = props.current
      resaltarHidrografia(map, props.current.resaltarRios, originales.current, props.current.oscuro)
      if (map.getSource('aa-cuencas')) return
      const ordenadas = [...metas].sort((a, b) => estiloDe(b.id).orden - estiloDe(a.id).orden)
      for (const meta of ordenadas) {
        const fuente = `aa-${meta.id}`
        const estilo = estiloDe(meta.id)
        const visibilidad = vis[meta.id] ? 'visible' : 'none'
        map.addSource(fuente, { type: 'geojson', data: datos[meta.id] as never, promoteId: 'id' })
        if (meta.id === 'cuencas') {
          map.addLayer({ id: 'aa-cuencas', type: 'fill', source: fuente, layout: { visibility: visibilidad }, paint: { 'fill-color': estilo.color, 'fill-opacity': 0.035 } })
          map.addLayer({ id: 'aa-cuencas-borde', type: 'line', source: fuente, layout: { visibility: visibilidad }, paint: { 'line-color': estilo.color, 'line-opacity': 0.45, 'line-width': ['interpolate', ['linear'], ['zoom'], 5, 0.6, 10, 1.4] } })
          const elegida = props.current.seleccion?.tipo === 'cuenca' ? props.current.seleccion.cuenca.id : ''
          map.addLayer({ id: 'aa-cuencas-seleccion', type: 'line', source: fuente, filter: ['==', ['get', 'id'], elegida], paint: { 'line-color': estilo.color, 'line-width': 3 } })
        } else if (meta.geometria === 'poligono') {
          map.addLayer({ id: fuente, type: 'fill', source: fuente, layout: { visibility: visibilidad }, paint: { 'fill-color': estilo.color, 'fill-opacity': 0.55, 'fill-outline-color': '#3d8fb8' } })
        } else if (meta.geometria === 'linea') {
          map.addLayer({
            id: fuente, type: 'line', source: fuente, layout: { visibility: visibilidad, 'line-cap': 'round', 'line-join': 'round' },
            paint: {
              'line-color': estilo.color,
              'line-opacity': 0.85,
              'line-width': ['interpolate', ['linear'], ['zoom'], 6, ['*', 0.28, ['get', 'orden']], 11, ['*', 0.9, ['get', 'orden']]],
            },
          })
        } else {
          map.addLayer({
            id: fuente, type: 'circle', source: fuente, minzoom: estilo.minzoom ?? 0, layout: { visibility: visibilidad },
            paint: {
              'circle-radius': radioPunto(meta.id, estilo.tamano),
              'circle-color': estilo.color,
              'circle-opacity': meta.id === 'plasticos' ? 0.75 : 0.92,
              'circle-stroke-color': props.current.oscuro ? '#0d1b1e' : '#ffffff',
              'circle-stroke-width': 1.2,
            },
          })
        }
      }
      listo.current = true
      props.current.onEstado(map.getStyle().name === NOMBRE_RESPALDO ? 'respaldo' : 'listo')
    }

    map.on('style.load', agregarCapas)

    map.on('click', (evento) => {
      const caja: [[number, number], [number, number]] = [[evento.point.x - 6, evento.point.y - 6], [evento.point.x + 6, evento.point.y + 6]]
      const activas = capasPunto().filter((id) => map.getLayer(id))
      const punto = map.queryRenderedFeatures(caja, { layers: activas })[0] as MapGeoJSONFeature | undefined
      if (punto) {
        const capaId = punto.layer.id.slice(3)
        const original = (props.current.colecciones[capaId]?.features as Sitio[] | undefined)?.find((f) => f.id === punto.properties?.id)
        if (original) props.current.onSeleccion({ tipo: 'sitio', sitio: original })
        return
      }
      if (map.getLayer('aa-cuencas') && map.getLayoutProperty('aa-cuencas', 'visibility') !== 'none') {
        const cuenca = map.queryRenderedFeatures(evento.point, { layers: ['aa-cuencas'] })[0]
        const original = (props.current.colecciones.cuencas?.features as Cuenca[] | undefined)?.find((f) => f.id === cuenca?.properties?.id)
        if (original) props.current.onSeleccion({ tipo: 'cuenca', cuenca: original })
      }
    })

    map.on('mousemove', (evento) => {
      const activas = capasPunto().filter((id) => map.getLayer(id))
      const punto = activas.length ? map.queryRenderedFeatures(evento.point, { layers: activas })[0] : undefined
      map.getCanvas().style.cursor = punto ? 'pointer' : ''
      if (punto && window.matchMedia?.('(hover: hover)').matches) {
        etiqueta.setLngLat(evento.lngLat).setText(String(punto.properties?.nombre ?? '')).addTo(map)
      } else {
        etiqueta.remove()
      }
    })
    map.on('mouseout', () => etiqueta.remove())

    map.on('error', (evento) => {
      const mensaje = String(evento.error?.message || '').toLowerCase()
      if (!listo.current && mensaje.includes('style')) {
        map.setStyle(estiloRespaldo(props.current.oscuro), { diff: false })
      } else if (listo.current && /tile|fetch|network|request|failed to load/.test(mensaje)) {
        props.current.onEstado('respaldo')
      }
    })
    const temporizador = window.setTimeout(() => {
      if (!listo.current) map.setStyle(estiloRespaldo(props.current.oscuro), { diff: false })
    }, 8000)

    const observador = new ResizeObserver(() => map.resize())
    observador.observe(contenedor.current)

    return () => {
      window.clearTimeout(temporizador)
      observador.disconnect()
      etiqueta.remove()
      marcador.current?.remove()
      marcador.current = null
      originales.current.clear()
      map.remove()
      mapa.current = null
      listo.current = false
    }
    // El mapa se crea una vez; los cambios posteriores se aplican en los efectos de abajo.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Cambio de mapa base.
  useEffect(() => {
    const map = mapa.current
    if (!map || !listo.current) return
    listo.current = false
    originales.current.clear()
    onEstado('cargando')
    map.setStyle(MAPAS_BASE[mapaBase].estilo, { diff: false })
  }, [mapaBase, onEstado])

  useEffect(() => {
    const map = mapa.current
    if (map && listo.current) resaltarHidrografia(map, resaltarRios, originales.current, oscuro)
  }, [resaltarRios, oscuro])

  // Visibilidad de capas.
  useEffect(() => {
    const map = mapa.current
    if (!map || !listo.current) return
    for (const meta of capas) {
      const ids = meta.id === 'cuencas' ? ['aa-cuencas', 'aa-cuencas-borde', 'aa-cuencas-seleccion'] : [`aa-${meta.id}`]
      for (const id of ids) {
        if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', visibles[meta.id] ? 'visible' : 'none')
      }
    }
  }, [capas, visibles])

  // Enfoque territorial.
  useEffect(() => {
    const map = mapa.current
    const destino = ENFOQUES.find((e) => e.id === enfoque?.id)
    if (!map || !destino) return
    const reducido = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    map.fitBounds(destino.limites, { padding: { top: 72, bottom: 40, left: 40, right: 40 }, duration: reducido ? 0 : 900 })
  }, [enfoque])

  // Selección.
  useEffect(() => {
    const map = mapa.current
    marcador.current?.remove()
    marcador.current = null
    if (!map) return
    if (map.getLayer('aa-cuencas-seleccion')) {
      map.setFilter('aa-cuencas-seleccion', ['==', ['get', 'id'], seleccion?.tipo === 'cuenca' ? seleccion.cuenca.id : ''])
    }
    const reducido = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    // Deja libre la zona que cubre la ficha: a la derecha en escritorio, abajo en móvil.
    const { clientWidth: ancho, clientHeight: alto } = map.getContainer()
    const relleno = ancho < 760
      ? { top: 60, bottom: Math.round(alto * 0.62), left: 24, right: 24 }
      : { top: 72, bottom: 40, left: 40, right: 460 }
    if (seleccion?.tipo === 'cuenca') {
      const limites = limitesDe(seleccion.cuenca.geometry.coordinates)
      if (limites) map.fitBounds(limites, { padding: relleno, maxZoom: 10, duration: reducido ? 0 : 800 })
      return
    }
    if (seleccion?.tipo !== 'sitio') return
    const elemento = document.createElement('div')
    elemento.className = 'marcador-seleccion'
    elemento.setAttribute('aria-hidden', 'true')
    elemento.append(document.createElement('span'))
    const coordenadas = seleccion.sitio.geometry.coordinates
    marcador.current = new Marker({ element: elemento, anchor: 'center' }).setLngLat(coordenadas).addTo(map)
    const zoom = Math.max(map.getZoom(), 8.5)
    map.easeTo({ center: coordenadas, zoom, padding: relleno, duration: reducido ? 0 : 700 })
  }, [seleccion])

  return <div ref={contenedor} className="mapa-lienzo" role="region" aria-label="Mapa interactivo de datos del agua" />
}
