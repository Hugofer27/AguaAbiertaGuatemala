import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { ESTILOS, GRUPOS } from '../capas'
import type { CapaMeta, Coleccion, Fuente, Sitio } from '../types'

const leer = <T,>(ruta: string) => JSON.parse(readFileSync(resolve(process.cwd(), 'datos', ruta), 'utf-8')) as T
const catalogo = leer<Fuente[]>('app/catalogo.json')
const capas = leer<CapaMeta[]>('app/capas.json')

describe('carpeta de datos', () => {
  it('tiene un catálogo sin IDs repetidos y con alias que no chocan', () => {
    const ids = catalogo.map((f) => f.id)
    expect(new Set(ids).size).toBe(ids.length)
    const alias = catalogo.flatMap((f) => f.ids_alias)
    expect(alias.filter((a) => ids.includes(a))).toEqual([])
    expect(catalogo.length).toBeGreaterThan(600)
  })

  it('cada capa tiene estilo, grupo y archivo con el número declarado de elementos', () => {
    for (const capa of capas) {
      expect(ESTILOS[capa.id], capa.id).toBeDefined()
      expect(GRUPOS).toContain(capa.grupo)
      const coleccion = leer<Coleccion>(capa.archivo)
      expect(coleccion.features).toHaveLength(capa.elementos)
    }
  })

  it('cada punto declara precisión y fuentes existentes, y está en Guatemala salvo el contexto regional', () => {
    const conocidos = new Set(catalogo.flatMap((f) => [f.id]))
    for (const capa of capas.filter((c) => c.geometria === 'punto')) {
      for (const sitio of leer<Coleccion<Sitio>>(capa.archivo).features) {
        const [lon, lat] = sitio.geometry.coordinates
        expect(['publicada', 'homonimo', 'transcrita', 'modelada', 'aproximada']).toContain(sitio.properties.precision)
        expect(sitio.properties.fuente_ids.length + (sitio.properties.enlaces?.length ?? 0), sitio.id).toBeGreaterThan(0)
        for (const enlace of sitio.properties.enlaces ?? []) expect(enlace.url).toMatch(/^https:\/\//)
        for (const id of sitio.properties.fuente_ids) {
          expect(conocidos.has(id) || id.startsWith('GT-PUB'), `${sitio.id} → ${id}`).toBe(true)
        }
        if (!capa.fuera_de_guatemala) {
          expect(lon).toBeGreaterThan(-92.6)
          expect(lon).toBeLessThan(-88.1)
          expect(lat).toBeGreaterThan(13.5)
          expect(lat).toBeLessThan(18)
        }
      }
    }
  })

  it('las capas de ubicación aproximada vienen apagadas y lo dicen en el título', () => {
    const aproximadas = capas.filter((c) => c.precision === 'aproximada')
    expect(aproximadas.map((c) => c.id)).toContain('barreras_plastico')
    for (const capa of aproximadas) {
      expect(capa.visible, capa.id).toBe(false)
      expect(capa.titulo).toMatch(/aproximada/)
    }
  })

  it('las mediciones traen unidad y fecha', () => {
    for (const capa of capas.filter((c) => c.geometria === 'punto')) {
      for (const sitio of leer<Coleccion<Sitio>>(capa.archivo).features) {
        for (const m of sitio.properties.mediciones ?? []) {
          expect(m.unidad, `${sitio.id} ${m.parametro}`).not.toBe('')
          expect(m.fecha).not.toBe('')
          expect(Number.isFinite(m.valor)).toBe(true)
        }
      }
    }
  })
})
