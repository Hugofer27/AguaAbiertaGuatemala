import { createReadStream, existsSync, statSync } from 'node:fs'
import { createServer } from 'node:http'
import { dirname, extname, resolve, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const distRoot = resolve(projectRoot, 'dist')
const args = process.argv.slice(2)

function argument(name, fallback) {
  const index = args.indexOf(name)
  return index >= 0 && args[index + 1] ? args[index + 1] : fallback
}

const host = argument('--host', '127.0.0.1')
const port = Number(argument('--port', '4173'))
const mimeTypes = {
  '.css': 'text/css; charset=utf-8',
  '.csv': 'text/csv; charset=utf-8',
  '.geojson': 'application/geo+json; charset=utf-8',
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.map': 'application/json; charset=utf-8',
  '.md': 'text/markdown; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.pdf': 'application/pdf',
  '.ttf': 'font/ttf',
  '.txt': 'text/plain; charset=utf-8',
  '.xls': 'application/vnd.ms-excel',
  '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  '.zip': 'application/zip',
}

function safeFile(root, pathname) {
  const relative = pathname.replace(/^\/+/, '')
  const filePath = resolve(root, relative)
  return filePath === root || filePath.startsWith(`${root}${sep}`) ? filePath : null
}

function sendFile(req, res, filePath) {
  const stats = statSync(filePath)
  if (!stats.isFile()) throw new Error('No es un archivo')

  const type = mimeTypes[extname(filePath).toLowerCase()] ?? 'application/octet-stream'
  const range = req.headers.range?.match(/^bytes=(\d*)-(\d*)$/)
  let start = 0
  let end = stats.size - 1
  let status = 200

  if (range) {
    start = range[1] ? Number(range[1]) : 0
    end = range[2] ? Math.min(Number(range[2]), stats.size - 1) : stats.size - 1
    if (!Number.isSafeInteger(start) || !Number.isSafeInteger(end) || start > end || start >= stats.size) {
      res.writeHead(416, { 'Content-Range': `bytes */${stats.size}` })
      res.end()
      return
    }
    status = 206
  }

  const headers = {
    'Accept-Ranges': 'bytes',
    'Cache-Control': 'no-cache',
    'Content-Length': String(end - start + 1),
    'Content-Type': type,
  }
  if (status === 206) headers['Content-Range'] = `bytes ${start}-${end}/${stats.size}`
  res.writeHead(status, headers)
  if (req.method === 'HEAD') {
    res.end()
    return
  }
  createReadStream(filePath, { start, end }).pipe(res)
}

if (!existsSync(resolve(distRoot, 'index.html'))) {
  console.error('No existe dist/index.html. Ejecute npm run build antes de npm run preview.')
  process.exit(1)
}

const server = createServer((req, res) => {
  try {
    const url = new URL(req.url ?? '/', `http://${host}:${port}`)
    const pathname = decodeURIComponent(url.pathname)
    const relativePath = pathname === '/' ? 'index.html' : pathname
    let filePath = safeFile(distRoot, relativePath)

    if (!filePath || !existsSync(filePath) || !statSync(filePath).isFile()) {
      const acceptsHtml = req.headers.accept?.includes('text/html')
      filePath = acceptsHtml ? resolve(distRoot, 'index.html') : null
    }
    if (!filePath) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' })
      res.end('Archivo no encontrado')
      return
    }
    sendFile(req, res, filePath)
  } catch {
    res.writeHead(400, { 'Content-Type': 'text/plain; charset=utf-8' })
    res.end('Solicitud no válida')
  }
})

server.listen(port, host, () => {
  console.log(`Agua Abierta Guatemala lista en http://${host}:${port}/`)
})
