import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import { createReadStream, statSync } from 'node:fs'
import type { IncomingMessage, ServerResponse } from 'node:http'
import { extname, resolve, sep } from 'node:path'
import type { Plugin } from 'vite'

const libraryRoot = resolve(process.cwd(), 'fuente_de_datos')

const mimeTypes: Record<string, string> = {
  '.csv': 'text/csv; charset=utf-8',
  '.geojson': 'application/geo+json; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.pdf': 'application/pdf',
  '.txt': 'text/plain; charset=utf-8',
  '.xls': 'application/vnd.ms-excel',
  '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  '.zip': 'application/zip',
}

function serveLibrary(req: IncomingMessage, res: ServerResponse, next: () => void) {
  const requestPath = req.url?.split('?')[0]
  if (!requestPath?.startsWith('/fuente_de_datos/')) {
    next()
    return
  }

  let relativePath: string
  try {
    relativePath = decodeURIComponent(requestPath.slice('/fuente_de_datos/'.length))
  } catch {
    res.statusCode = 400
    res.end('Ruta no válida')
    return
  }

  const filePath = resolve(libraryRoot, relativePath)
  if (!filePath.startsWith(`${libraryRoot}${sep}`)) {
    res.statusCode = 403
    res.end('Acceso denegado')
    return
  }

  try {
    if (!statSync(filePath).isFile()) throw new Error('No es un archivo')
    res.setHeader('Content-Type', mimeTypes[extname(filePath).toLowerCase()] ?? 'application/octet-stream')
    res.setHeader('Cache-Control', 'private, max-age=3600')
    createReadStream(filePath).pipe(res)
  } catch {
    res.statusCode = 404
    res.end('Archivo no encontrado')
  }
}

function localLibraryPlugin(): Plugin {
  return {
    name: 'dashboardgpt-local-library',
    configureServer(server) {
      server.middlewares.use(serveLibrary)
    },
    configurePreviewServer(server) {
      server.middlewares.use(serveLibrary)
    },
  }
}

export default defineConfig({
  plugins: [react(), localLibraryPlugin()],
  base: './',
  build: {
    target: 'es2022',
    sourcemap: true,
  },
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
  },
})
