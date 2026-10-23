import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import { cpSync, createReadStream, existsSync, statSync } from 'node:fs'
import type { IncomingMessage, ServerResponse } from 'node:http'
import { extname, resolve, sep } from 'node:path'
import type { Plugin } from 'vite'

// La carpeta datos/ es la fuente única de los datos: se sirve en desarrollo y se copia al sitio construido.
const raizDatos = resolve(process.cwd(), 'datos')

const tipos: Record<string, string> = {
  '.csv': 'text/csv; charset=utf-8',
  '.geojson': 'application/geo+json; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.md': 'text/markdown; charset=utf-8',
}

function servirDatos(req: IncomingMessage, res: ServerResponse, next: () => void) {
  const ruta = req.url?.split('?')[0] ?? ''
  const indice = ruta.indexOf('/datos/')
  if (indice < 0) {
    next()
    return
  }
  let relativa: string
  try {
    relativa = decodeURIComponent(ruta.slice(indice + '/datos/'.length))
  } catch {
    res.statusCode = 400
    res.end('Ruta no válida')
    return
  }
  const archivo = resolve(raizDatos, relativa)
  if (!archivo.startsWith(`${raizDatos}${sep}`) || !existsSync(archivo) || !statSync(archivo).isFile()) {
    next()
    return
  }
  res.setHeader('Content-Type', tipos[extname(archivo).toLowerCase()] ?? 'application/octet-stream')
  res.setHeader('Cache-Control', 'no-cache')
  createReadStream(archivo).pipe(res)
}

function carpetaDatos(): Plugin {
  let salida = 'dist'
  return {
    name: 'agua-abierta-datos',
    configResolved(config) {
      salida = resolve(config.root, config.build.outDir)
    },
    configureServer(server) {
      server.middlewares.use(servirDatos)
    },
    closeBundle() {
      if (existsSync(raizDatos)) cpSync(raizDatos, resolve(salida, 'datos'), { recursive: true })
    },
  }
}

export default defineConfig({
  plugins: [react(), carpetaDatos()],
  base: './',
  build: {
    target: 'es2022',
    sourcemap: false,
  },
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
  },
})
