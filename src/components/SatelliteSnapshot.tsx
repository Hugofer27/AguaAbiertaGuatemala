import { useEffect, useMemo, useState } from 'react'
import { CalendarDays, ChevronLeft, ChevronRight, ExternalLink, ImageOff, Satellite } from 'lucide-react'
import type { WaterFeature } from '../types'

const NASA_SNAPSHOT_ENDPOINT = 'https://wvs.earthdata.nasa.gov/api/v1/snapshot'
const NASA_WORLDVIEW_ENDPOINT = 'https://worldview.earthdata.nasa.gov/'
const SATELLITE_LAYER = 'MODIS_Aqua_CorrectedReflectance_TrueColor'
const WORLDVIEW_LAYERS = [
  SATELLITE_LAYER,
  'Coastlines_15m',
  'Reference_Features_15m',
]
// Keep the crop tight enough that changing stations produces a visibly different
// view while still leaving enough surrounding terrain to read the location.
const VIEW_RADIUS_DEGREES = 0.18
const VIEW_DIAMETER_KM = Math.round(VIEW_RADIUS_DEGREES * 2 * 111)

function isoDateDaysAgo(daysAgo: number) {
  const date = new Date()
  date.setUTCHours(0, 0, 0, 0)
  date.setUTCDate(date.getUTCDate() - daysAgo)
  return date.toISOString().slice(0, 10)
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('es-GT', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    timeZone: 'UTC',
  }).format(new Date(`${value}T00:00:00Z`)).replace('.', '')
}

export function buildSatelliteUrls(feature: WaterFeature, date: string) {
  const [longitude, latitude] = feature.geometry.coordinates
  const south = Math.max(-89.9, latitude - VIEW_RADIUS_DEGREES)
  const west = Math.max(-179.9, longitude - VIEW_RADIUS_DEGREES)
  const north = Math.min(89.9, latitude + VIEW_RADIUS_DEGREES)
  const east = Math.min(179.9, longitude + VIEW_RADIUS_DEGREES)
  const bbox = [south, west, north, east].map((value) => value.toFixed(5)).join(',')

  const snapshot = new URL(NASA_SNAPSHOT_ENDPOINT)
  snapshot.searchParams.set('REQUEST', 'GetSnapshot')
  snapshot.searchParams.set('TIME', `${date}T00:00:00Z`)
  snapshot.searchParams.set('BBOX', bbox)
  snapshot.searchParams.set('CRS', 'EPSG:4326')
  // The snapshot endpoint expects one WRAP value per requested layer. Keep the
  // exported image to a single true-colour layer; Worldview adds labels itself.
  snapshot.searchParams.set('LAYERS', SATELLITE_LAYER)
  snapshot.searchParams.set('WRAP', 'day')
  snapshot.searchParams.set('FORMAT', 'image/jpeg')
  snapshot.searchParams.set('WIDTH', '960')
  snapshot.searchParams.set('HEIGHT', '720')
  snapshot.searchParams.set('MARKER', `${latitude.toFixed(5)},${longitude.toFixed(5)}`)

  const worldview = new URL(NASA_WORLDVIEW_ENDPOINT)
  worldview.searchParams.set('p', 'geographic')
  worldview.searchParams.set('v', [west, south, east, north].map((value) => value.toFixed(5)).join(','))
  worldview.searchParams.set('t', `${date}-T00:00:00Z`)
  worldview.searchParams.set('l', WORLDVIEW_LAYERS.join(','))
  worldview.searchParams.set('s', `${longitude.toFixed(5)},${latitude.toFixed(5)}`)

  return { snapshot: snapshot.toString(), worldview: worldview.toString() }
}

export default function SatelliteSnapshot({ feature }: { feature: WaterFeature }) {
  const [open, setOpen] = useState(false)
  const [daysAgo, setDaysAgo] = useState(1)
  const [imageState, setImageState] = useState<'loading' | 'ready' | 'error'>('loading')
  const [longitude, latitude] = feature.geometry.coordinates
  const date = isoDateDaysAgo(daysAgo)
  const urls = useMemo(() => buildSatelliteUrls(feature, date), [date, feature])

  useEffect(() => {
    setOpen(false)
    setDaysAgo(1)
    setImageState('loading')
  }, [feature.id])

  const changeDay = (nextDaysAgo: number) => {
    setDaysAgo(nextDaysAgo)
    setImageState('loading')
  }

  return (
    <section className={`satellite-observation ${open ? 'is-open' : ''}`} aria-labelledby="satellite-title">
      <button
        className="satellite-trigger"
        type="button"
        onClick={() => {
          setOpen((value) => !value)
          setImageState('loading')
        }}
        aria-expanded={open}
        aria-controls="satellite-preview"
      >
        <Satellite aria-hidden="true" />
        <span>
          <strong id="satellite-title">{open ? 'Ocultar imagen satelital' : 'Ver imagen satelital reciente'}</strong>
          <small>NASA Worldview · color verdadero · fecha verificable</small>
        </span>
      </button>

      {open && (
        <div id="satellite-preview" className="satellite-preview">
          <div className="satellite-toolbar">
            <button type="button" onClick={() => changeDay(daysAgo + 1)} aria-label="Ver el día anterior">
              <ChevronLeft aria-hidden="true" />
            </button>
            <span><CalendarDays aria-hidden="true" /> {formatDate(date)} UTC</span>
            <button type="button" onClick={() => changeDay(daysAgo - 1)} disabled={daysAgo <= 1} aria-label="Ver el día siguiente">
              <ChevronRight aria-hidden="true" />
            </button>
          </div>

          <figure className={`satellite-frame ${imageState}`} aria-busy={imageState === 'loading'}>
            <div className="satellite-image-wrap">
              {imageState === 'loading' && <div className="satellite-loading" role="status">Solicitando el recorte de esta coordenada a NASA…</div>}
              {imageState === 'error' ? (
                <div className="satellite-error" role="alert">
                  <ImageOff aria-hidden="true" />
                  <strong>No se pudo cargar esta observación.</strong>
                  <span>Pruebe con el día anterior o abra el visor completo de NASA.</span>
                </div>
              ) : (
                <img
                  key={`${feature.id}-${urls.snapshot}`}
                  src={urls.snapshot}
                  alt={`Imagen satelital de color verdadero centrada en ${feature.properties.name}, correspondiente al ${formatDate(date)}`}
                  loading="lazy"
                  onLoad={() => setImageState('ready')}
                  onError={() => setImageState('error')}
                />
              )}
              {imageState === 'ready' && <span className="satellite-coordinate-marker" aria-hidden="true"><span /></span>}
            </div>
            <figcaption>
              <span>MODIS / Aqua · resolución nominal 250 m</span>
              <span>Centro consultado · {latitude.toFixed(5)}°, {longitude.toFixed(5)}°</span>
              <span>La retícula señala la coordenada publicada · recorte aproximado de {VIEW_DIAMETER_KM} km.</span>
            </figcaption>
          </figure>

          <p className="satellite-caveat">
            No es una transmisión en directo. La imagen puede tener horas o días de retraso, nubes o zonas todavía no procesadas.
          </p>
          <a className="satellite-worldview-link" href={urls.worldview} target="_blank" rel="noreferrer">
            Explorar ubicación y fechas en NASA Worldview <ExternalLink aria-hidden="true" />
          </a>
        </div>
      )}
    </section>
  )
}
