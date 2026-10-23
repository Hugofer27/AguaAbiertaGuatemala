import { useEffect, useState } from 'react'
import { Copy, Download, ExternalLink } from 'lucide-react'
import { urlDatos } from '../data'
import { AVISO_GENERAL, CITA, REPOSITORIO, fechaCorte, numero } from '../textos'
import type { CapaMeta, Config, Resumen } from '../types'

const ZIP_DATOS = 'descargas/agua-abierta-guatemala-datos.zip'
const ZIP_SITIO = 'descargas/agua-abierta-guatemala-sitio.zip'

function useExiste(ruta: string) {
  const [existe, setExiste] = useState(false)
  useEffect(() => {
    let vigente = true
    fetch(ruta, { method: 'HEAD' })
      // Un servidor de desarrollo puede responder con index.html a cualquier ruta.
      .then((r) => vigente && setExiste(r.ok && !r.headers.get('content-type')?.includes('text/html')))
      .catch(() => vigente && setExiste(false))
    return () => {
      vigente = false
    }
  }, [ruta])
  return existe
}

export default function AboutView({ resumen, capas, config }: { resumen: Resumen; capas: CapaMeta[]; config: Config }) {
  const zipDatos = useExiste(`./${ZIP_DATOS}`)
  const zipSitio = useExiste(`./${ZIP_SITIO}`)
  const [copiado, setCopiado] = useState(false)
  const direccion = typeof window !== 'undefined' ? `${window.location.origin}${window.location.pathname}` : ''
  const cita = CITA(resumen.fecha_corte.slice(0, 4), resumen.version, direccion)

  const tablas = [
    { nombre: 'Catálogo de fuentes', ruta: 'catalogo/fuentes.csv', detalle: `${numero(resumen.fuentes)} conjuntos de datos, documentos y portales` },
    { nombre: 'Publicaciones', ruta: 'catalogo/publicaciones.csv', detalle: `${numero(resumen.publicaciones)} artículos, tesis e informes` },
    { nombre: 'Datos faltantes', ruta: 'catalogo/faltantes.csv', detalle: `${resumen.faltantes} registros con motivo y cómo pedirlos` },
    { nombre: 'Organizaciones', ruta: 'catalogo/organizaciones.csv', detalle: `${resumen.organizaciones} instituciones` },
    { nombre: 'Mediciones', ruta: 'mediciones/mediciones.csv', detalle: `${numero(resumen.mediciones)} valores en formato largo (sitio, parámetro, valor, unidad, fecha, fuente)` },
    { nombre: 'Sitios', ruta: 'mediciones/sitios.csv', detalle: `${numero(resumen.puntos_en_mapa)} puntos del mapa con coordenadas y precisión` },
    { nombre: 'Parámetros', ruta: 'mediciones/parametros.csv', detalle: `${resumen.parametros} parámetros con código y unidad` },
    { nombre: 'Manifiesto de originales', ruta: 'manifiesto/originales.csv', detalle: `${numero(resumen.archivos_originales)} archivos con URL y SHA-256` },
  ]

  return (
    <article className="vista-acerca" aria-labelledby="titulo-acerca">
      <header className="vista-cabeza">
        <div>
          <h1 id="titulo-acerca">Acerca de Agua Abierta Guatemala</h1>
          <p className="entradilla">
            Un catálogo y un atlas de los datos públicos que existen sobre el agua en Guatemala: quién mide qué, dónde, desde cuándo y dónde
            conseguirlo. Versión {resumen.version}, con datos al {fechaCorte(resumen.fecha_corte)}.
          </p>
        </div>
      </header>

      <div className="acerca-rejilla">
        <section>
          <h2>Qué es y qué no es</h2>
          <ul className="lista-simple">
            <li><strong>Es</strong> un índice verificable: cada punto del mapa y cada registro enlaza a su fuente.</li>
            <li><strong>Es</strong> una forma de ver juntos datos dispersos en INE, INSIVUMEH, MARN, autoridades de lagos, universidades y bases internacionales.</li>
            <li><strong>No es</strong> un monitoreo en tiempo real: los valores son de campañas y archivos publicados, con su fecha.</li>
            <li><strong>No es</strong> una evaluación de la calidad del agua. {AVISO_GENERAL}</li>
          </ul>
        </section>

        <section>
          <h2>Cómo se reunieron los datos</h2>
          <p>
            En octubre de 2026 se hicieron tres búsquedas independientes en portales oficiales (INE, INSIVUMEH, MARN, AMSA, AMSCLAE, ICC),
            repositorios científicos (OpenAlex, DataCite, Zenodo, PANGAEA, HDX), los repositorios de la USAC y la UVG, y capas SIG públicas en ArcGIS Online.
          </p>
          <p>
            Cada búsqueda la hizo un asistente de inteligencia artificial distinto: Claude (Anthropic), ChatGPT/Codex (OpenAI) y Google Antigravity.
            Hugo Escobar las dirigió y revisó. Las IA no generaron datos: localizaron, descargaron y ordenaron archivos publicados por las
            instituciones. Cada enlace se comprobó y cada archivo descargado lleva su huella SHA-256 para verificar que es el original.
          </p>
          <p>
            Los resultados se unificaron: un mismo archivo hallado dos veces se reconoce por su huella SHA-256, su URL o su DOI, y conserva sus
            identificadores anteriores como alias. Solo se descargaron archivos públicos, sin evadir bloqueos ni registros.
          </p>
          <p>
            En el mapa solo aparecen lugares con coordenadas defendibles. Cada punto declara la precisión de su ubicación (publicada, de un punto
            homónimo, transcrita de un documento o de un modelo). Se excluyeron {resumen.excluidos_del_mapa.length} ubicaciones que no cumplían
            ese criterio, por ejemplo desembocaduras de un modelo global que en realidad están en Belice, Honduras o El Salvador.
          </p>
          <p>
            Los valores de oxígeno disuelto se comparan con la saturación teórica según la temperatura (Benson y Krause). Si un valor resulta
            imposible o sospechoso, se marca para revisión y no se borra.
          </p>
        </section>
      </div>

      <section className="acerca-descargas" aria-labelledby="titulo-descargas">
        <h2 id="titulo-descargas">Descargas</h2>
        <p>Todos los archivos son abiertos y se pueden usar en Excel, R, Python o QGIS. Los CSV usan UTF-8 y los GeoJSON usan WGS 84 (EPSG:4326).</p>
        <div className="descargas-destacadas">
          {zipDatos && (
            <a className="tarjeta-descarga" href={`./${ZIP_DATOS}`} download>
              <Download aria-hidden="true" /><span><strong>Toda la carpeta de datos (ZIP)</strong><small>Catálogo, capas, mediciones y manifiesto</small></span>
            </a>
          )}
          {zipSitio && (
            <a className="tarjeta-descarga" href={`./${ZIP_SITIO}`} download>
              <Download aria-hidden="true" /><span><strong>Sitio para usar sin internet (ZIP)</strong><small>Incluye instrucciones para abrirlo en su computadora</small></span>
            </a>
          )}
          {config.enlace_originales ? (
            <a className="tarjeta-descarga" href={config.enlace_originales} target="_blank" rel="noreferrer">
              <ExternalLink aria-hidden="true" /><span><strong>Archivos originales</strong><small>{numero(resumen.archivos_originales)} archivos verificados por SHA-256</small></span>
            </a>
          ) : (
            <div className="tarjeta-descarga pendiente">
              <Download aria-hidden="true" /><span><strong>Archivos originales</strong><small>Paquete de respaldo en preparación. Mientras tanto, cada ficha enlaza a la fuente oficial.</small></span>
            </div>
          )}
        </div>
        <div className="tabla-descargas">
          <table>
            <thead><tr><th scope="col">Tabla</th><th scope="col">Contenido</th><th scope="col"><span className="sr-only">Descargar</span></th></tr></thead>
            <tbody>
              {tablas.map((t) => (
                <tr key={t.ruta}><th scope="row">{t.nombre}</th><td>{t.detalle}</td><td><a href={urlDatos(t.ruta)} download>CSV</a></td></tr>
              ))}
              {capas.map((c) => (
                <tr key={c.id}><th scope="row">{c.titulo}</th><td>{c.descripcion}</td><td><a href={urlDatos(c.archivo)} download>GeoJSON</a></td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <div className="acerca-rejilla">
        <section>
          <h2>Próximos pasos</h2>
          <ol className="lista-simple numerada">
            <li><strong>Comparar mediciones con normas</strong>, cada una con su uso: COGUANOR NTG 29001 y NOM-127-SSA1-2021 para agua de consumo, guías de la OMS, NOM-001-SEMARNAT-2021 y el Acuerdo Gubernativo 236-2006 para descargas. La tabla de mediciones ya trae código de parámetro y unidad para hacerlo.</li>
            <li><strong>Ubicar las estaciones de AMSA y AMSCLAE</strong> cuando se documente el sistema de coordenadas de sus archivos.</li>
            <li><strong>Capas completas</strong>: los 1 908 puntos de WPdx, la red fluvial nacional del MAGA y las subcuencas, a partir del paquete de originales.</li>
            <li><strong>Solicitudes de información pública</strong> (Decreto 57-2008) para los datos de la pestaña Datos faltantes.</li>
            <li><strong>Actualización periódica</strong> del portal del INE y verificación automática de enlaces.</li>
          </ol>
        </section>
        <section>
          <h2>Cómo citar</h2>
          <blockquote className="cita">{cita}</blockquote>
          <button className="boton secundario" onClick={() => navigator.clipboard?.writeText(cita).then(() => setCopiado(true))}>
            <Copy aria-hidden="true" /> {copiado ? 'Cita copiada' : 'Copiar cita'}
          </button>
          <h2>Licencias</h2>
          <ul className="lista-simple">
            <li>
              <strong>Contenido de este portal</strong> (catálogo compilado, capas, tablas y textos):{' '}
              <a href={`${REPOSITORIO}/blob/main/LICENSE-CONTENIDO.md`} target="_blank" rel="noreferrer">CC BY 4.0</a>. Puede usarlo y adaptarlo
              libremente, también con fines comerciales, citando la fuente.
            </li>
            <li><strong>Código</strong>: <a href={`${REPOSITORIO}/blob/main/LICENSE`} target="_blank" rel="noreferrer">MIT</a>.</li>
            <li>
              <strong>Datos de terceros</strong>: cada conjunto conserva la licencia de su institución (columna licencia del catálogo). Revísela
              antes de redistribuir un archivo original.
            </li>
          </ul>
        </section>
      </div>
    </article>
  )
}
