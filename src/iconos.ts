/** Silueta de botella con la base en (0, 0); mide 14 × 36 unidades. La comparten el mapa y la leyenda. */
export const RUTA_BOTELLA = 'M-3,-36H3V-30L7,-25V-3Q7,0 4,0H-4Q-7,0 -7,-3V-25L-3,-30Z'

/**
 * Dibuja la botella para MapLibre (`map.addImage` con `pixelRatio: 2`).
 * Devuelve null si el navegador no ofrece canvas 2D.
 */
export function imagenBotella(color: string): { width: number; height: number; data: Uint8ClampedArray } | null {
  const ancho = 36
  const alto = 62
  const lienzo = document.createElement('canvas')
  lienzo.width = ancho
  lienzo.height = alto
  const ctx = lienzo.getContext('2d')
  if (!ctx || typeof Path2D === 'undefined') return null
  ctx.translate(ancho / 2, alto - 3)
  ctx.scale(1.5, 1.5)
  const silueta = new Path2D(RUTA_BOTELLA)
  ctx.lineJoin = 'round'
  ctx.strokeStyle = '#ffffff'
  ctx.lineWidth = 2.6
  ctx.stroke(silueta)
  ctx.fillStyle = color
  ctx.fill(silueta)
  // Tapa y etiqueta, para que se lea como botella también a tamaño pequeño.
  ctx.fillStyle = 'rgba(0, 0, 0, 0.35)'
  ctx.fillRect(-3, -36, 6, 3)
  ctx.fillStyle = 'rgba(255, 255, 255, 0.7)'
  ctx.fillRect(-7, -17, 14, 6)
  const { data } = ctx.getImageData(0, 0, ancho, alto)
  return { width: ancho, height: alto, data }
}
