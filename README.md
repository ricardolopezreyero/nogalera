# Nogaleras de La Laguna

Mapa en blanco y negro de las nogaleras de Torreón, Gómez Palacio, Lerdo y alrededores (toda la Comarca Lagunera). Para cada una muestra:

- cuánto mide (hectáreas, m², largo y ancho),
- cuánto podría costar el m² y la huerta completa, a ojo de buen cubero,
- dónde está, con botones para llegar con Google Maps o Waze.

También marca las huertas que tenían nogales en 2018–2020 y que en 2026 ya no los tienen, aparte las que ya se urbanizaron.

Sitio: **https://nogalera.capitaltorreon.com**

## Qué hay en el repositorio

```
public/                 el sitio (lo que se publica, tal cual)
  index.html            página
  style.css, app.js     estilo y mapa (Leaflet + OpenStreetMap en escala de grises)
  nogaleras.geojson     las nogaleras (polígonos y datos)
  nogaleras.csv         lo mismo en tabla, para Excel
  base.geojson          fondo de respaldo sin teselas (carreteras, ríos y pueblos); se usa con ?fondo=vector
  vendor/leaflet/       Leaflet 1.9.4
  _headers              cabeceras de Cloudflare
pipeline/               cómo se generaron los datos (ver pipeline/README.md)
wrangler.jsonc          configuración de Cloudflare
```

No tiene paso de build: es HTML, CSS y JavaScript sin dependencias. Para verlo en tu computadora:

```bash
cd public && python3 -m http.server 8000   # y abre http://localhost:8000
```

## Publicar en Cloudflare (una sola vez)

La zona `capitaltorreon.com` ya está en Cloudflare. Se publica como Worker de archivos estáticos conectado a este repositorio:

1. En Cloudflare, **Workers & Pages → Create → Import a repository** y elige `ricardolopezreyero/nogalera`.
2. Nombre del proyecto: `nogalera`. Así se llama en `wrangler.jsonc` y deben coincidir.
3. **Build command:** vacío. **Deploy command:** `npx wrangler deploy`. Rama de producción: `main`.
4. Pulsa **Deploy**.

**Página del cliente y prospectos.** `/inicio/` es la página de venta (la arma `pipeline/scripts/sitio_inicio.py`; sus imágenes salen de `node pipeline/scripts/renders.js --lista pipeline/scripts/renders_inicio.json` a `public/inicio/img/`). El llamado principal es «Descargar el brochure» (nombre, celular y correo; `tipo: brochure`), con una segunda parte opcional (primera o segunda casa, crédito, rapidez). Al que pide el brochure se le contesta en el momento por correo (Resend) diciéndole que se le manda en cuanto esté listo; para eso hacen falta los secretos `RESEND_API_KEY` y `AVISO_DESDE` (un remitente de un dominio verificado en Resend). Sin la llave, el prospecto se guarda igual y no se manda nada. El formulario manda a `POST /api/prospecto` y el Worker guarda cada registro en un Durable Object con SQLite (`Prospectos`, declarado en `wrangler.jsonc`: no hay que crear nada en Cloudflare, el primer deploy lo crea). Para descargarlos: `/api/prospectos?clave=…&formato=csv`. La clave es el secreto `ADMIN_CLAVE` (si no está, `RENDER_CLAVE`); mientras no haya ninguno, la clave provisional es `123` (igual para el creador de renders con IA). Para recibir un correo por cada prospecto, secretos `RESEND_API_KEY` y `AVISO_CORREO` (opcional `AVISO_DESDE`). Las instrucciones también están en `/datos/#prospectos`.

**Creador de renders fotorrealistas (`/renders/foto/`).** Motor WebGL propio (`public/render/foto3d.js`, three.js vendido en `public/vendor/three/`) que lee las mismas escenas del modelo 3D (`public/datos/escenas/*.json`) y las dibuja con materiales con textura, nogales con hojas y nueces, pasto, sombras suaves, oclusión ambiental, bloom y mapeo tonal. El sol se calcula para Torreón según la hora y la fecha (`sol`, `luzSolar`, `horaPreset`); la barra de abajo mueve la hora de 0 a 24 con marcas de salida y puesta, presets relativos a la fecha, animación del día completo y fecha; los paneles controlan cámara, nubes (capa de cúmulos con cobertura, viento y velo de nublado), bruma, fuerza del sol, exposición, luces y calidad; de noche hay estrellas y se encienden luminarias y cristales. También hay modo caminar (`?caminar=1`) y mapas de control (profundidad, normales, líneas) para ControlNet. Los renders del concurso se generan sin abrir el navegador con `NODE_PATH=/opt/node-tools/node_modules node pipeline/scripts/fotos.js --control` (lista en `pipeline/scripts/fotos_lista.json`, salida en `public/renders/foto/img/` y `control/`), con un servidor local en el puerto 8787 (`cd public && python3 -m http.server 8787`).

**Secretos del Worker (render fotorrealista con IA).** El creador de renders (`/renders/#ia`) llama a `/api/render-ia`, que vive en `worker/index.js` y usa dos secretos del Worker `nogalera`: `OPENAI_API_KEY` (la llave de OpenAI) y `RENDER_CLAVE` (la contraseña que se escribe en la página para poder generar). Se ponen en Cloudflare → Workers & Pages → nogalera → Settings → Variables and Secrets (tipo *Secret*), o con `npx wrangler secret put OPENAI_API_KEY` y `npx wrangler secret put RENDER_CLAVE`. Con los dos puestos, el siguiente deploy los toma; la página avisa si falta alguno.

`wrangler.jsonc` ya trae el dominio `nogalera.capitaltorreon.com` («custom domain»): al publicar, Cloudflare crea solo el registro DNS y el certificado. Si marca error de zona (porque `capitaltorreon.com` está en otra cuenta), borra el bloque `routes` de `wrangler.jsonc` y agrega el dominio a mano en **nogalera → Settings → Domains & Routes → Add → Custom domain**.

Desde ese momento, cada cambio en `main` se publica solo en uno o dos minutos.

## Campos de los datos

| Campo | Qué es |
|---|---|
| `id` | Número de la nogalera (N1 es la más cercana a Real del Nogalar). |
| `estado` | `activa` (hay nogales en 2026), `desmontada` (había en 2018–2020; hoy no hay y tampoco hay casas) o `urbanizada` (hoy hay calles o casas). |
| `confianza` | `alta` o `media` (conviene verla en persona). |
| `area_m2`, `perimetro_m`, `largo_m`, `ancho_m` | Medidas de la arboleda vista desde el satélite (cuadros de 10 m; error típico de ±5 a 10 %). |
| `precio_m2`, `precio_m2_min`, `precio_m2_max` | Precio estimado por m² en pesos y su rango. |
| `valor`, `valor_min`, `valor_max` | Precio estimado de toda la huerta y su rango. |
| `municipio`, `cerca_de` | Municipio y localidad más cercana (OpenStreetMap). |
| `lat`, `lon` | Un punto dentro de la huerta (para navegar). |
| `dist_ref_km` | Distancia en línea recta a Real del Nogalar. |
| `d_ciudad_km` | Distancia a la mancha urbana de Torreón, Gómez Palacio y Lerdo. |
| `grupo`, `grupo_bloques`, `grupo_m2` | Si la huerta está partida en bloques pegados: cuántos son y cuánto suman. |

## Fuentes y licencias

- Altura de árboles a 1 m: Meta y World Resources Institute (CC BY 4.0).
- Sentinel-2 L2A: Copernicus (ESA), vía Earth Search de Element 84.
- ESA WorldCover 2021 (CC BY 4.0) y Copernicus DEM.
- OpenStreetMap, vía Overture Maps, para caminos, ríos, edificios, municipios y localidades. © colaboradores de OpenStreetMap ([ODbL](https://www.openstreetmap.org/copyright)). Los datos derivados de OSM en `nogaleras.geojson` (municipio y localidad cercana) quedan bajo la misma licencia.
- Mapa base: teselas de OpenStreetMap.

Los precios son una estimación, no un avalúo.
