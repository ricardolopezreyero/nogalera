"""La Nogalera · constructor del sitio (tablero: menú a la izquierda, contenido a la derecha).
Solo python3: lee public/datos/*.json (los escribe el pipeline pesado) y los módulos de dibujo, y escribe una carpeta por sección en public/.
    python3 scripts/sitio.py            # desde pipeline/"""
import csv, json, math, os, statistics, sys
from html import escape as e
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
PUB = os.path.join(RAIZ, "public"); DAT = os.path.join(PUB, "datos")
import n6_casa_planta as CP, n6_casa_dibujos as CD, n6_fachadas as NF, n6_acceso as AC, n6_acceso_calc as ACC, n6_terreno as TE

FC = json.load(open(f"{DAT}/confort.geojson")); R = FC["resumen"]; GROSS = FC["bruto_m2"]
SV = json.load(open(f"{DAT}/servicios.json")); LZ = json.load(open(f"{DAT}/luces.json"))["resumen"]
ARB = json.load(open(f"{DAT}/arboles_confort.json"))
NOG = list(csv.DictReader(open(f"{DAT}/nogaleras.csv", encoding="utf-8-sig")))
N6 = next(r for r in NOG if r["id"] == "6")
LOTES = [f["properties"] for f in FC["features"] if f["properties"]["capa"] == "lote"]
FID = TE.fideicomiso(FC)
N = R["lotes"]; VERSION = "Versión 2 · 7 de octubre de 2026"; NOMBRE = R["fraccionamiento"]

f0 = lambda x: f"{x:,.0f}"
f1 = lambda x: f"{x:,.1f}"
f2 = lambda x: f"{x:,.2f}"
def mill(x, d=None):
    d = (0 if abs(x) >= 1e8 else 1) if d is None else d
    return f"${x/1e6:,.{d}f} millones"
pct = lambda x, d=1: f"{100*x:.{d}f} %"
ha = lambda m2: f"{m2/1e4:,.1f} ha"

# ======================= estructura =======================
SECCIONES = [
    ("", "Resumen", "01"), ("terreno", "El terreno", "02"), ("plan", "Plan maestro", "03"), ("calles", "Calles y direcciones", "04"),
    ("acceso", "Acceso", "05"), ("casa", "Casa Modelo Nogal", "06"), ("fachadas", "Fachadas", "07"), ("servicios", "Servicios", "08"),
    ("iluminacion", "Iluminación", "09"), ("numeros", "Números", "10"), ("etapas", "Etapas y siguientes pasos", "11"),
    None, ("nogaleras", "Nogaleras de La Laguna", "A"), ("datos", "Datos para descargar", "B"),
]
def menu(actual, sub):
    o = []
    for s in SECCIONES:
        if s is None: o.append('<li class="sep" aria-hidden="true"></li>'); continue
        slug, nombre, num = s
        cur = ' aria-current="page"' if slug == actual else ""
        o.append(f'<li><a href="/{slug + "/" if slug else ""}"{cur}><span class="num">{num}</span><span>{e(nombre)}</span></a>')
        if slug == actual and sub: o.append('<ul class="sub">' + "".join(f'<li><a href="#{a}">{e(t)}</a></li>' for a, t in sub) + "</ul>")
        o.append("</li>")
    return "".join(o)

def pagina(slug, titulo, ojo, lede, cuerpo, sub=(), mapa=False, head="", script="", descripcion=""):
    leaflet = '<link rel="stylesheet" href="/vendor/leaflet/leaflet.css">' if mapa else ""
    cab = "" if mapa else f'<header class="cab"><p class="ojo">{e(ojo)}</p><h1>{titulo}</h1>{f"<p class=lede>{lede}</p>" if lede else ""}</header>'
    cuerpo_html = f'<main class="contenido mapa">{cuerpo}</main>' if mapa else f'<main class="contenido"><div class="doc">{cab}{cuerpo}<p class="nota pie-doc">{NOMBRE} · {VERSION}. Anteproyecto: cifras de referencia, no cotizaciones ni avalúos. Todo se genera desde <code>pipeline/</code>.</p></div></main>'
    html = f"""<!doctype html>
<html lang="es-MX">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo if slug else NOMBRE)} · {NOMBRE}</title>
<meta name="description" content="{e(descripcion or lede or titulo)}">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{leaflet}<link rel="stylesheet" href="/estilo.css">
{head}</head>
<body>
<aside class="lateral" id="lateral">
  <div class="cabl"><a class="marca" href="/"><b>{NOMBRE}</b><span>Fraccionamiento en N6 · La Paz, Torreón</span></a><button type="button" id="menu-btn" aria-expanded="false" aria-controls="menu-nav">Menú</button></div>
  <p class="estado">{VERSION}</p>
  <nav id="menu-nav" aria-label="Secciones del proyecto"><ul class="menu">{menu(slug, sub)}</ul></nav>
  <p class="pie">Anteproyecto. Lindero por confirmar con catastro. Mapas: © colaboradores de <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>.</p>
</aside>
{cuerpo_html}
<script>(function(){{var b=document.getElementById("menu-btn"),l=document.getElementById("lateral");b.addEventListener("click",function(){{var o=l.classList.toggle("abierto");b.setAttribute("aria-expanded",o);b.textContent=o?"Cerrar":"Menú";}});}})();</script>
{script}
</body>
</html>
"""
    d = os.path.join(PUB, slug) if slug else PUB
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(html)
    print("ok", slug or "/")

def kpis(items, chica=False):
    return f'<dl class="kpis{" chica" if chica else ""}">' + "".join(f"<div><dt>{e(t)}</dt><dd>{v}{f'<small>{s}</small>' if s else ''}</dd></div>" for t, v, s in items) + "</dl>"
def tabla(rows, cols, clase="", tot=None):
    h = "".join(f'<th{" class=izq" if i in (0,) else ""}>{c}</th>' for i, c in enumerate(cols))
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    if tot: b += '<tr class="tot">' + "".join(f"<td>{c}</td>" for c in tot) + "</tr>"
    return f'<div class="scroll"><table class="{clase}"><tr>{h}</tr>{b}</table></div>'
def partidas(serv):
    xs = [x for x in SV["partidas"] if x["servicio"] in serv]
    return tabla([(f'<b>{e(x["elemento"])}</b>', e(x["especificacion"]), f'{f0(x["cantidad"])} {x["unidad"]}', f'${f0(x["importe"])}') for x in xs],
                 ["Elemento", "Especificación", "Cantidad", "Importe (MXN)"], "spec", ("<b>Subtotal</b>", "", "", f"<b>${f0(sum(x['importe'] for x in xs))}</b>"))

# ======================= plano maestro estático (SVG) =======================
LIM = next(f for f in FC["features"] if f["properties"]["capa"] == "limite")
_lon0 = sum(c[0] for c in LIM["geometry"]["coordinates"][0]) / len(LIM["geometry"]["coordinates"][0])
_lat0 = sum(c[1] for c in LIM["geometry"]["coordinates"][0]) / len(LIM["geometry"]["coordinates"][0])
_t = math.radians(SV["geo"]["th"])
def uv(lon, lat):
    x = (lon - _lon0) * math.cos(math.radians(_lat0)) * 111320.0; y = (lat - _lat0) * 110574.0
    return x * math.cos(_t) + y * math.sin(_t), -x * math.sin(_t) + y * math.cos(_t)
_lim_uv = [uv(*c) for c in LIM["geometry"]["coordinates"][0]]
U0, U1 = min(p[0] for p in _lim_uv), max(p[0] for p in _lim_uv); V0, V1 = min(p[1] for p in _lim_uv), max(p[1] for p in _lim_uv)
_cu, _cv = (U0 + U1) / 2, (V0 + V1) / 2                         # centro del límite en uv; en servicios.json las calles están centradas en (cx, cy) de la cuadrícula
_u_acc = SV["calles"]["u_acceso"]
# desfase entre el marco de servicios.json (centrado en cx, cy de la cuadrícula) y el nuestro (centrado en el centroide del límite): lo da el acceso
_acc_lonlat = None
for f in FC["features"]:
    if f["properties"]["capa"] == "caseta": _acc_lonlat = f["geometry"]["coordinates"][0][0]; break
_du = uv(*_acc_lonlat)[0] - _u_acc if _acc_lonlat else 0.0
_rot = [f for f in FC["features"] if f["properties"]["capa"] == "rotulo"]
def _v_de_calle(nombre):
    ys = [uv(*f["geometry"]["coordinates"])[1] for f in _rot if f["properties"]["eje"] == "largo" and f["properties"]["nombre"].replace("Bulevar ", "") == nombre]
    return statistics.median(ys)
def _u_de_cruce(nombre):
    xs = [uv(*f["geometry"]["coordinates"])[0] for f in _rot if f["properties"]["eje"] == "cruce" and f["properties"]["nombre"] == nombre]
    return statistics.median(xs)
ETAPA = {}
def centro(f):
    cs = f["geometry"]["coordinates"][0]; return sum(c[0] for c in cs) / len(cs), sum(c[1] for c in cs) / len(cs)
_lotes_f = [f for f in FC["features"] if f["properties"]["capa"] == "lote"]
_orden = sorted(_lotes_f, key=lambda f: abs(uv(*centro(f))[0] - (_u_acc + _du)))
for i, f in enumerate(_orden): ETAPA[f["properties"]["n"]] = 1 + min(3, i * 4 // len(_orden))
json.dump(ETAPA, open(f"{DAT}/etapas.json", "w"), separators=(",", ":"))

def plano_svg(modo="plan", ancho_px=1400, titulo=""):
    """modo: plan | etapas | arboles | calles"""
    PAD = 70; S = (ancho_px - 2 * PAD) / (U1 - U0)
    W = ancho_px; H = (V1 - V0) * S + 2 * PAD
    X = lambda u: PAD + (u - U0) * S; Y = lambda v: PAD + (V1 - v) * S
    def pts(f): return " ".join(f"{X(u):.1f},{Y(v):.1f}" for u, v in (uv(*c) for c in f["geometry"]["coordinates"][0]))
    o = [f'<svg viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="{e(titulo or "Plano maestro")}" class="plano">']
    capas = {"plan": ["pista", "vial", "bulevar", "arroyo", "sendero", "comunal", "plaza_acceso", "ptar", "parque", "lote", "comercio", "estacionamiento", "salon", "tenis", "padel", "isla", "caseta"],
             "etapas": ["pista", "vial", "bulevar", "arroyo", "comunal", "plaza_acceso", "ptar", "parque", "lote", "comercio"],
             "arboles": ["pista"], "calles": ["pista", "vial", "bulevar", "arroyo", "sendero", "comunal", "plaza_acceso", "ptar", "parque", "lote", "comercio"]}[modo]
    cls = {"pista": "pm-pista", "vial": "pm-vial", "bulevar": "pm-bulevar", "arroyo": "pm-bulevar", "sendero": "pm-pista", "comunal": "pm-club", "plaza_acceso": "pm-pista", "ptar": "pm-ptar", "parque": "pm-parque",
           "lote": "pm-lote", "comercio": "pm-comercio", "estacionamiento": "pm-vial", "salon": "pm-ptar", "tenis": "pm-ptar", "padel": "pm-ptar", "isla": "pm-pista", "caseta": "pm-ptar"}
    for capa in capas:
        for f in FC["features"]:
            if f["properties"]["capa"] != capa or f["geometry"]["type"] != "Polygon": continue
            c = cls[capa]
            if modo == "etapas" and capa == "lote": c = f"pm-e{ETAPA[f['properties']['n']]}"
            o.append(f'<polygon points="{pts(f)}" class="{c}"/>')
    if modo in ("arboles", "plan"):
        for a in ARB:
            u, v = uv(a[0], a[1]); r = 0.9 + 0.12 * a[3] if modo == "arboles" else 1.1
            o.append(f'<circle cx="{X(u):.1f}" cy="{Y(v):.1f}" r="{r*S if modo == "arboles" else 1.1:.1f}" class="pm-arbol{" mover" if a[2] and modo == "plan" else ""}"/>')
    o.append(f'<polygon points="{pts(LIM)}" class="pm-limite"/>')
    if modo in ("calles", "plan", "etapas"):
        for nombre in R["calles_largas"]:
            v = _v_de_calle(nombre); o.append(f'<text x="{X(U0)-8:.1f}" y="{Y(v)+4:.1f}" class="pm-rotulo" text-anchor="end">{e(nombre)}</text>')
        for nombre in R["calles_cruce"]:
            u = _u_de_cruce(nombre); o.append(f'<text x="{X(u):.1f}" y="{Y(V1)-10:.1f}" class="pm-rotulo cruce" text-anchor="middle">{e(nombre)}</text>')
    # norte, escala y acceso
    nx, ny = math.sin(_t), -math.cos(_t)
    cx_, cy_ = W - PAD + 20, PAD + 30
    o.append(f'<circle cx="{cx_}" cy="{cy_}" r="22" fill="#fff" stroke="#000"/><line x1="{cx_ - nx*16:.1f}" y1="{cy_ - ny*16:.1f}" x2="{cx_ + nx*16:.1f}" y2="{cy_ + ny*16:.1f}" stroke="#000" stroke-width="2.5"/>'
             f'<polygon points="{cx_ + nx*22:.1f},{cy_ + ny*22:.1f} {cx_ + nx*8 - ny*6:.1f},{cy_ + ny*8 + nx*6:.1f} {cx_ + nx*8 + ny*6:.1f},{cy_ + ny*8 - nx*6:.1f}" fill="#000"/>'
             f'<text x="{cx_ + nx*34:.1f}" y="{cy_ + ny*34 + 4:.1f}" class="pm-etiqueta" text-anchor="middle" font-weight="700">N</text>')
    o.append(f'<line x1="{PAD}" y1="{H-PAD/2:.1f}" x2="{PAD + 200*S:.1f}" y2="{H-PAD/2:.1f}" stroke="#000" stroke-width="3"/><text x="{PAD + 100*S:.1f}" y="{H-PAD/2-6:.1f}" class="pm-etiqueta" text-anchor="middle">200 m</text>')
    if _acc_lonlat:
        ua, va = uv(*_acc_lonlat); o.append(f'<text x="{X(ua):.1f}" y="{Y(V0)+22:.1f}" class="pm-etiqueta" text-anchor="middle" font-weight="700">▲ acceso · Calzada José Vasconcelos</text>')
    if modo == "etapas":
        for k in range(1, 5):
            fs = [f for f in _lotes_f if ETAPA[f["properties"]["n"]] == k]
            us = [uv(*centro(f))[0] for f in fs]; vs = [uv(*centro(f))[1] for f in fs]
            o.append(f'<text x="{X(statistics.median(us)):.1f}" y="{Y(V0)+42:.1f}" class="pm-etiqueta" text-anchor="middle" font-weight="700">Etapa {k} · {len(fs)} lotes</text>')
    o.append("</svg>")
    return "\n".join(o)

# ======================= cifras comunes =======================
QUEDAN = R["arboles"] - R["reubicar"]
H_ARB = [a[3] for a in ARB]
VENTA_COM = R["predio_comercial_m2"] * 6000
VENTA_LOTES = R["venta"] - VENTA_COM
TERRENO_V = R["terreno_m2_precio"] * GROSS
REUBICA = R["reubicar"] * 12000
BLANDOS = 0.12 * R["venta"]
PAISAJE = LZ["inversion_paisaje"]
AMEN = R["amenidades_detalle"]
COSTOS = [("Terreno", TERRENO_V, f"{f0(GROSS)} m² a ${f0(R['terreno_m2_precio'])}/m²"), ("Urbanización", SV["URB"], f"{len(SV['partidas'])} partidas medidas sobre el plano"),
          ("Amenidades", R["amenidades"], "club social, club deportivo, parques y acceso"), ("Iluminación de paisaje y acceso", PAISAJE, "los arbotantes de calle van en urbanización"),
          ("Reubicar nogales", REUBICA, f"{R['reubicar']} nogales a $12,000"), ("Ventas, permisos y proyecto", BLANDOS, "12 % de la venta")]
def precio_lote(p):
    x = 3400 - 2 * (p["m2"] - 300)
    return x * (1.08 if p["premio"] == "parque" else 1.05 if p["premio"] == "bulevar" else 1.0)
MESES_VENTA = N / TE.RITMO

# ======================= RESUMEN =======================
def resumen():
    dec = [
        ("Trazado sobre los nogales.", f"Las calles corren entre hileras y los linderos de los lotes caen sobre las columnas de árboles: se quedan {f0(QUEDAN)} de {f0(R['arboles'])} nogales ({pct(QUEDAN/R['arboles'],0)}). Es lo que hace distinto al fraccionamiento."),
        ("Un solo modelo de casa, nueve fachadas.", "La misma casa de 243 m² en todos los lotes (4 recámaras, cada una con clóset y baño) y 9 fachadas repartidas para que ninguna se repita con la de al lado ni con la de enfrente."),
        ("Un acceso calculado para la hora pico.", "2 carriles de residentes y 2 de visitas para entrar, 1 y 1 para salir; las casetas a 60 m de la calle para que la fila nunca salga a la calzada."),
        ("Los nogales se riegan con agua del propio fraccionamiento.", f"Planta de tratamiento en la punta oriente y red morada con goteo a cada nogal. Cubre el riego de los nogales, los parques y el bulevar y sobra {SV['tratamiento']['riego_pct']-100:.0f} %."),
        ("La lluvia se queda adentro.", "Jardines 10 cm abajo de la banqueta, camellón que es jardín de lluvia, parques con bordo, zanja bajo la pista, cajas bajo los estacionamientos y un vaso de tormentas. No se descarga a la calle de afuera."),
        ("Drenaje por gravedad, luz y fibra subterráneas.", f"El terreno baja {SV['TERR']['desnivel']:.1f} m al oriente: todo llega a la planta sin bombeo. Sin postes: media tensión en anillo con {SV['luz']['trafos']} transformadores de pedestal."),
        ("Direcciones de una palabra y un número.", f"Calles largas con nombre de árbol y transversales con nombre de ave, las dos en orden alfabético: «Encino 65, Fracc. {NOMBRE}». Impares al norte, pares al sur."),
        ("Lo común, y nada más.", "Club social (salón con oficinas arriba y gimnasio), club deportivo (tenis y 2 de pádel), 2 parques en las manzanas de nogales más grandes, bulevar con sendero, pista de 3.3 km y mini súper antes de las plumas."),
        ("Presupuesto por partida y cuota calculada.", f"Urbanización de {mill(SV['URB'])} en {len(SV['partidas'])} partidas, y una cuota de ${f0(SV['cuota_casa'])} por casa al mes que se le puede prometer al comprador."),
        ("El precio del terreno que aguanta el proyecto.", f"De contado hasta ${f0(FID['p_contado'])}/m²; en fideicomiso, {pct(FID['X_viable'])} de las ventas (≈ ${f0(FID['p_fid'])}/m²), dejando 20 % de margen."),
    ]
    tarj = [("terreno", "El terreno", f"{ha(GROSS)} de nogalera en La Paz, al oriente de Torreón; {f0(R['arboles'])} nogales mapeados uno por uno."),
            ("plan", "Plan maestro", f"Mapa interactivo con los {f0(N)} lotes, calles, club, parques, nogales, iluminación y redes."),
            ("calles", "Calles y direcciones", "Nombres, numeración, secciones de calle y bulevar, cruces elevados."),
            ("acceso", "Acceso", "Entrada calculada para la hora pico: carriles, casetas, filas y esperas."),
            ("casa", "Casa Modelo Nogal", "Plantas amuebladas, azotea, corte, conjunto y fachadas: todos los planos."),
            ("fachadas", "Fachadas", "Nueve fachadas distintas sobre la misma casa, y cómo se reparten en cada cuadra."),
            ("servicios", "Servicios", "Drenaje pluvial y sanitario, planta de tratamiento, agua, luz y fibra, con especificaciones y presupuesto."),
            ("iluminacion", "Iluminación", f"{f0(LZ['puntos'])} puntos de luz: arbotantes, nogales iluminados, balizas y acceso."),
            ("numeros", "Números", "Ventas, costos, margen, fideicomiso del terreno y cuota de mantenimiento."),
            ("etapas", "Etapas y siguientes pasos", "Cuatro etapas desde el acceso, calendario y lo que hay que confirmar.")]
    cuerpo = f"""
<p class="lede ancho" style="max-width:52rem;font-size:1.25rem;margin-top:0">{f0(N)} casas entre {f0(QUEDAN)} nogales, en {ha(GROSS)} al oriente de Torreón. Un fraccionamiento trazado sobre la huerta, con un solo modelo de casa y nueve fachadas, que riega sus propios árboles.</p>
{kpis([("Terreno", ha(GROSS), f"{f0(GROSS)} m² · La Paz, Torreón"), ("Casas", f0(N), f"lote típico de {R['lote_mediana']} m²"), ("Nogales que se quedan", f"{pct(QUEDAN/R['arboles'],0)}", f"{f0(QUEDAN)} de {f0(R['arboles'])}"),
       ("Venta", mill(R["venta"]), f"{f0(N)} lotes y {f0(R['predio_comercial_m2'])} m² de comercio"), ("Urbanización", mill(SV["URB"]), f"${f0(SV['URB']/GROSS)}/m² de terreno"),
       ("Margen", f"{mill(R['margen'])}", f"{R['roi']:.1f} % sobre el costo, de contado a $670/m²"), ("Cuota de mantenimiento", f"${f0(SV['cuota_casa'])}", "por casa al mes"), ("Plazo de venta", f"{MESES_VENTA/12:.1f} años", f"{TE.RITMO} lotes al mes desde el mes {TE.INICIO}")])}
<figure><div class="dibujo">{plano_svg("plan", titulo="Plano maestro")}</div><figcaption><b>Plano maestro.</b> Cada punto es un nogal en su lugar exacto; los blancos son los {f0(R['reubicar'])} que se reubican. El bulevar Nogal corre por la hilera que ya faltaba en la huerta; el club, por la otra.</figcaption></figure>
<h2 id="decisiones">El proyecto en 10 decisiones</h2>
<ol class="decisiones">{"".join(f"<li><b>{e(t)}</b>{e(d)}</li>" for t, d in dec)}</ol>
<h2 id="secciones">Secciones</h2>
<ul class="tarjetas">{"".join(f'<li><a class="tarjeta" href="/{s}/"><span class="n">{dict((x[0], x[2]) for x in SECCIONES if x)[s]}</span><b>{e(t)}</b><p>{e(d)}</p></a></li>' for s, t, d in tarj)}</ul>
<h2 id="estado">Dónde está el proyecto</h2>
<div class="dos">
<div><h3>Lo que ya está</h3><ul>
<li>Terreno identificado y medido, con los {f0(R['arboles'])} nogales mapeados (altura y posición).</li>
<li>Plan maestro completo: lotes, calles con nombre y número, acceso, club, parques, pista y comercio.</li>
<li>Casa modelo con plantas amuebladas y 9 fachadas; una fachada asignada a cada lote.</li>
<li>Redes de servicios trazadas y presupuestadas partida por partida; cuota de mantenimiento.</li>
<li>Precio del terreno y porcentaje justo en fideicomiso, calculados.</li></ul></div>
<div><h3>Lo que sigue</h3><ul>
<li>Confirmar el lindero y la tenencia del predio con catastro y el Registro Público; revisar el título de agua de la huerta.</li>
<li>Acuerdo con el dueño: compra o fideicomiso (ver <a href="/numeros/#fideicomiso">Números</a>).</li>
<li>Levantamiento topográfico, mecánica de suelos y pruebas de infiltración.</li>
<li>Factibilidades: uso de suelo (municipio), SIMAS, CFE y Protección Civil.</li>
<li>Proyecto ejecutivo y licencia; arranque de la etapa 1 (ver <a href="/etapas/">Etapas</a>).</li></ul></div>
</div>
"""
    pagina("", f"{NOMBRE}", "01 · Resumen", "", cuerpo, [("decisiones", "10 decisiones"), ("secciones", "Secciones"), ("estado", "Dónde está el proyecto")],
           descripcion=f"{NOMBRE}: fraccionamiento de {f0(N)} casas entre nogales en el oriente de Torreón. Anteproyecto completo.")

# ======================= TERRENO =======================
def terreno():
    alto = sum(1 for h in H_ARB if h >= 10)
    cuerpo = f"""
{kpis([("Superficie", ha(GROSS), f"{f0(GROSS)} m² · {N6['largo_m']} × {N6['ancho_m']} m"), ("Nogales", f0(R['arboles']), f"{f0(alto)} de 10 m o más · hileras cada 12.6 m"), ("Cota", f"{SV['TERR']['z_media']:,.1f} m", f"baja {SV['TERR']['pend_km']:.2f} m/km al oriente"),
       ("Precio de referencia", f"${f0(R['terreno_m2_precio'])}/m²", f"rango ${N6['precio_m2_min']}–{N6['precio_m2_max']}"), ("Valor de contado", mill(TERRENO_V), "sobre toda la superficie"), ("Ubicación", "La Paz", "oriente de Torreón, Coahuila")])}
<div class="mapa-chico"><div id="map" role="region" aria-label="Mapa del terreno con sus nogales"></div></div>
<p class="nota">Cada punto es un nogal detectado desde satélite (altura de árboles de Meta y WRI a 1 m). El lindero es el de la arboleda; hay que confirmarlo con catastro.</p>
<h2 id="donde">Dónde está</h2>
<div class="dos">
<div>
<p>Al oriente de Torreón, junto a la colonia La Paz, entre la <b>Calzada José Vasconcelos</b> (al sur, donde va el acceso) y la <b>Calle Juan Agustín de Espinoza</b> (al poniente, una vialidad primaria: los lotes que dan a ella se venden como comercio). A {N6['dist_ref_km']} km en línea recta de Real del Nogalar.</p>
<p>Coordenadas del centro: {N6['lat']}, {N6['lon']}. <a href="https://www.google.com/maps/search/?api=1&query={N6['lat']},{N6['lon']}" target="_blank" rel="noopener">Abrir en Google Maps</a>.</p>
<p>Es una huerta de nogal en producción, regada por inundación: por eso está casi plana ({SV['TERR']['desnivel']:.1f} m de desnivel de punta a punta) y tiene pozo propio con derechos de agua agrícolas.</p>
</div>
<div>
<h3>La huerta, en números</h3>
{tabla([("Nogales", f0(R['arboles'])), ("Altura: mediana · máxima", f"{statistics.median(H_ARB):.1f} m · {max(H_ARB):.0f} m"), ("Nogales de 10 m o más", f0(alto)), ("Separación entre hileras", "12.6 m"), ("Separación en la hilera", "≈ 12.7 m"),
        ("Hileras que ya faltaban", "2 (ahí van el bulevar y el club)"), ("Sombra de copa (promedio)", f"≈ {math.pi * (0.32 * statistics.mean(H_ARB) + 1.2) ** 2:.0f} m² por árbol")], ["Dato", "Valor"], "compacta")}
</div></div>
<h2 id="arboles">Los nogales, uno por uno</h2>
<figure><div class="dibujo">{plano_svg("arboles", titulo="Los nogales del terreno")}</div><figcaption><b>Cada círculo es un nogal, dibujado a su tamaño de copa.</b> La cuadrícula de la huerta es la que ordena todo el diseño: las calles van en los pasillos entre hileras y los lotes se cortan donde están los árboles.</figcaption></figure>
<h2 id="precio">Cuánto vale</h2>
<p>El mapa de <a href="/nogaleras/#n6">nogaleras de La Laguna</a> estima <b>${f0(R['terreno_m2_precio'])}/m²</b> para este predio: nogalera en producción pegada a la mancha urbana de Torreón, en un rango de ${N6['precio_m2_min']} a ${N6['precio_m2_max']}/m². Sobre las {ha(GROSS)} son <b>{mill(TERRENO_V)} de contado</b>. No es un avalúo: el agua, la tenencia y el acceso mueven el precio.</p>
<p>Con la urbanización completa, el proyecto aguanta hasta <b>${f0(FID['p_contado'])}/m² de contado</b> o, en fideicomiso, <b>{pct(FID['X_viable'])} de las ventas</b> para el dueño (≈ ${f0(FID['p_fid'])}/m²). La cuenta completa está en <a href="/numeros/#fideicomiso">Números</a>.</p>
<h2 id="origen">De dónde salió</h2>
<p>Primero se mapearon <b>todas las nogaleras de la Comarca Lagunera</b> desde satélite ({f0(sum(1 for r in NOG if r['estado']=='activa'))} huertas activas, {f0(sum(float(r['area_m2']) for r in NOG if r['estado']=='activa')/1e4)} ha). De las cinco mejor situadas para urbanizar, esta (N6) es la que da el mayor retorno por m²: grande, plana, con calles por dos lados y a la orilla de la ciudad. El mapa completo está en <a href="/nogaleras/">Nogaleras de La Laguna</a>.</p>
"""
    pagina("terreno", "El terreno", "02 · El terreno", f"Una nogalera de {ha(GROSS)} en La Paz, al oriente de Torreón, con {f0(R['arboles'])} nogales mapeados uno por uno.", cuerpo,
           [("donde", "Dónde está"), ("arboles", "Los nogales"), ("precio", "Cuánto vale"), ("origen", "De dónde salió")], mapa=False,
           head='<link rel="stylesheet" href="/vendor/leaflet/leaflet.css">',
           script='<script>window.PLAN={datos:"/datos/",modo:"terreno",rueda:false};</script><script src="/vendor/leaflet/leaflet.js"></script><script src="/plan/plan.js"></script>')

# ======================= PLAN MAESTRO (mapa) =======================
def plan():
    cuerpo = f"""
<div id="map" role="region" aria-label="Plano maestro interactivo"></div>
<section class="panel" id="panel" aria-labelledby="titulo">
  <h1 id="titulo">Plan maestro <span>{NOMBRE} · toca un lote para ver su dirección, medidas y fachada</span></h1>
  <dl class="kpis" id="kpis"><div><dt>Cargando…</dt><dd></dd></div></dl>
  <form class="buscar" id="buscar" role="search">
    <label for="q">Busca una dirección</label>
    <div><input id="q" list="dirs" placeholder="Ej. Encino 65" autocomplete="off"><button type="submit">Ir</button></div>
    <datalist id="dirs"></datalist>
    <p id="q-msg" class="q-msg" role="status"></p>
  </form>
  <h2>Capas</h2>
  <label class="chk"><input type="checkbox" id="chk-arboles" checked> Nogales (negro se queda, blanco se reubica)</label>
  <label class="chk"><input type="checkbox" id="chk-etapas"> Etapas de construcción</label>
  <label class="chk"><input type="checkbox" id="chk-luz"> Iluminación (vista de noche)</label>
  <div class="luz" id="luz" hidden aria-live="polite"></div>
  <label class="chk" for="sel-serv">Redes de servicios</label>
  <select id="sel-serv" class="sel">
    <option value="">Ninguna</option>
    <option value="pluvial">Drenaje pluvial</option>
    <option value="sanitario">Drenaje sanitario y planta</option>
    <option value="agua">Agua potable y agua tratada</option>
    <option value="luz">Luz, cruces elevados y accesos</option>
  </select>
  <div class="luz" id="serv-nota" hidden aria-live="polite"></div>
  <div class="leyenda" aria-hidden="true">
    <span><i style="background:#fafafa"></i>Lote</span><span><i style="background:#c8c8c8"></i>Calle</span><span><i style="background:#7a7a7a"></i>Bulevar</span>
    <span><i style="background:#e6e6e6;border-style:dashed"></i>Pista</span><span><i style="background:#b9b9b9"></i>Parque</span><span><i style="background:#111"></i>Club</span>
    <span><i style="background:#fff;border-width:2px;border-style:double"></i>Comercio</span><span><i style="background:#6a6a6a"></i>Planta</span>
  </div>
  <div class="notas">
    <p><b>Lotes de 12.7 × 25.9 m (328 m²)</b> sobre la cuadrícula de nogales. Calles entre hileras; los árboles quedan en los linderos.</p>
    <p><b>Un acceso</b> frente a la Calzada José Vasconcelos, con el mini súper antes de las plumas. <b>Club</b> en la hilera vacía; <b>2 parques</b> en las manzanas de nogales más grandes; <b>pista</b> de 3.3 km por el perímetro; <b>planta de tratamiento</b> en la punta oriente.</p>
  </div>
</section>
"""
    pagina("plan", "Plan maestro", "03 · Plan maestro", "", cuerpo, mapa=True, descripcion=f"Plano maestro interactivo de {NOMBRE}: lotes con dirección y fachada, calles, club, parques, nogales, iluminación y redes.",
           script='<script>window.PLAN={datos:"/datos/",modo:"plan",etapas:' + json.dumps(ETAPA, separators=(",", ":")) + '};</script><script src="/vendor/leaflet/leaflet.js"></script><script src="/plan/plan.js"></script>')

# ======================= CALLES =======================
def calles():
    C = SV["calles"]
    por_calle = {}
    for p in LOTES: por_calle[p["dir"].rsplit(" ", 1)[0]] = por_calle.get(p["dir"].rsplit(" ", 1)[0], 0) + 1
    cuerpo = f"""
{kpis([("Calles largas", "8", "nombre de árbol, de sur a norte"), ("Transversales", "9", "nombre de ave, de poniente a oriente"), ("Calles", f"{f1(C['L_total']/1000)} km", f"{f1(C['L_largo']/1000)} largas · {f1(C['L_cruce']/1000)} transversales · {f1(C['L_bul']/1000)} bulevar"),
       ("Sección", "11 m", "7 m de arroyo y 2 banquetas de 2 m"), ("Bulevar Nogal", "30 m", "2 arroyos, camellón con sendero"), ("Cruces elevados", f"{C['mesas']}", "en el bulevar y frente al club"), ("Velocidad", "30 km/h", "en todo el fraccionamiento")])}
<figure><div class="dibujo">{plano_svg("calles", titulo="Calles con nombre")}</div><figcaption><b>Las calles largas llevan nombre de árbol y las transversales, de ave; las dos en orden alfabético.</b> Si sabes la letra, sabes dónde está la calle.</figcaption></figure>
<h2 id="nombres">Nombres y direcciones</h2>
<div class="dos">
<div><h3>De sur a norte</h3>{tabla([(("<b>Bulevar " if n == "Nogal" else "") + e(n) + ("</b>" if n == "Nogal" else ""), f0(por_calle.get(n, 0))) for n in R['calles_largas']], ["Calle larga", "Casas"], "compacta")}</div>
<div><h3>De poniente a oriente</h3>{tabla([(e(n), "transversal") for n in R['calles_cruce']], ["Calle transversal", ""], "compacta")}
<p>Las transversales no tienen casas con frente a ellas: solo cruzan. Los parques toman el nombre de su transversal (Parque Cenzontle, Parque Garza).</p></div>
</div>
<ul>
<li><b>La dirección es una palabra y un número:</b> «Encino 65, Fracc. {NOMBRE}». Impares del lado norte de la calle, pares del lado sur; los números crecen de poniente a oriente. El número más alto es el {R['num_max']}.</li>
<li><b>Placas en cada esquina</b> con el nombre de las dos calles y el rango de números de esa cuadra. {C['cruces_n']} cruces señalizados.</li>
<li>En el <a href="/plan/">plan maestro</a> se puede buscar cualquier dirección.</li>
</ul>
<h2 id="secciones">Secciones de calle</h2>
<div class="scroll sec">{C['SEC_CALLE']}</div>
<div class="scroll sec">{C['SEC_BUL']}</div>
<ul>
<li><b>Arroyo de 7.0 m</b> con 2 carriles de 3.5 m: se puede estacionar de un lado sin cerrar el paso. Concreto hidráulico de 15 cm (18 cm en el bulevar y el acceso) sobre base y subbase.</li>
<li><b>Banquetas de 2 m</b> libres: los nogales quedan 85 cm adentro del lote, sobre el lindero. Rampas en todas las esquinas, radio de giro de 6 m (pasa el camión de bomberos).</li>
<li><b>Bulevar:</b> 2 arroyos de 7 m, camellón de 5.6 m con sendero de 2.4 m y 2 jardines de lluvia, banquetas de 5.2 m con los nogales.</li>
<li><b>Todo por debajo de la banqueta:</b> agua, luz, fibra, riego y drenaje van ordenados en la sección, cada uno en su franja, para abrir sin romper lo demás.</li>
<li><b>Cruces elevados</b> ({C['mesas']}): mesas de concreto de 3.5 m con rampas 1:10 en el bulevar y frente al club. Los niños cruzan al parque a nivel de banqueta.</li>
</ul>
<h2 id="presupuesto">Lo que cuestan las calles</h2>
{partidas(["Terracerías", "Calles"])}
<p class="nota">Precios de 2026 sin IVA, de referencia. El detalle de todas las redes está en <a href="/servicios/">Servicios</a>.</p>
"""
    pagina("calles", "Calles y direcciones", "04 · Calles y direcciones", "Ocho calles largas con nombre de árbol, nueve transversales con nombre de ave y una dirección de una palabra y un número.", cuerpo,
           [("nombres", "Nombres y direcciones"), ("secciones", "Secciones de calle"), ("presupuesto", "Lo que cuestan")])

# ======================= ACCESO =======================
def acceso():
    man, tar = AC.man, AC.tar
    def fila(t, d):
        if d.get("espera_s") is None: return (t, f"{d['rho']*100:.0f} %", "<b>se satura</b>", "la fila no deja de crecer")
        return (t, f"{d['rho']*100:.0f} %", f"{d['espera_s']} s", f"{d['fila95']} autos · {d['fila95_m']} m")
    cuerpo = f"""
{kpis([("Entrada", "2 + 2 carriles", "residentes con tag · visitas con registro"), ("Salida", "1 + 1 carriles", "pluma arriba en la hora pico"), ("Casetas", f"a {AC.CASETA_V} m", "la fila queda dentro del terreno"),
       ("Tarde, hora pico", f"{tar['entran_h']} autos/h", "entran"), ("Mañana, hora pico", f"{man['salen_h']} autos/h", "salen"), ("Espera del residente", f"≈ {tar['entrada_residentes_2_carriles']['espera_s']} s", "al entrar en la tarde"), ("Ancho del acceso", f"{AC.ANCHO[1]-AC.ANCHO[0]:.0f} m", "con islas y banqueta")])}
<h2 id="plano">Plano</h2>
<div class="scroll sec plano-acceso">{AC.plano()}</div>
<ul>
<li><b>Se maneja por la derecha.</b> Los residentes entran por los 2 carriles del centro, con tag, y la pluma abre sola. Las visitas van por los 2 carriles de la derecha y se registran en la caseta, que queda entre los dos grupos de carriles.</li>
<li><b>Las plumas van a {AC.CASETA_V} m de la calle.</b> En el peor cuarto de hora de la tarde, 95 de cada 100 veces la fila es de {tar['entrada_residentes_2_carriles']['fila95']} autos o menos por carril de residentes y de {tar['entrada_visitas_2_carriles']['fila95']} o menos por carril de visitas (hasta {tar['entrada_visitas_2_carriles']['fila95_m']} m): nunca llega a la calle ni tapa la entrada del súper.</li>
<li><b>Retorno antes de las plumas:</b> la visita que no está registrada se regresa por el hueco de las islas sin dar reversa.</li>
<li><b>El súper y su estacionamiento quedan antes de las plumas.</b> Sus clientes de afuera no pasan por la caseta; los vecinos llegan caminando por la puerta peatonal. El acopio de basura también queda afuera: el camión no entra.</li>
<li><b>Salida 1 + 1.</b> De 6:30 a 9:00 la pluma de residentes se queda arriba y una cámara lee las placas. El resto del día abre con el tag.</li>
<li>Pasando las plumas, la calle vuelve a ser de 2 carriles, como el resto del fraccionamiento.</li>
</ul>
<h2 id="calculo">Cálculo de hora pico</h2>
<p>Viajes por casa en la hora pico: 0.85 en la mañana (75 % salen) y 1.0 en la tarde (63 % entran): tasas de tráfico residencial de casas solas, un poco arriba por la ida a la escuela. Se usa el cuarto de hora más cargado (factor 0.85). Visitas, servicios y apps: 15 % de lo que entra y 8 % de lo que sale. Las cuentas son por carril, con un modelo de colas conservador.</p>
<h3>Tarde · entrada ({tar['entran_h']} autos/h)</h3>
{tabla([fila(f"Residentes, 1 carril ({tar['res_entran']}/h)", tar['entrada_residentes_1_carril']), fila("Residentes, <b>2 carriles</b>", tar['entrada_residentes_2_carriles']),
        fila(f"Visitas, 1 carril ({tar['vis_entran']}/h)", tar['entrada_visitas_1_carril']), fila("Visitas, <b>2 carriles</b>", tar['entrada_visitas_2_carriles'])], ["", "Ocupación", "Espera media", "Fila (95 %)"])}
<h3>Mañana · salida ({man['salen_h']} autos/h)</h3>
{tabla([fila(f"Residentes, 1 carril con pluma ({man['res_salen']}/h)", man['salida_residentes_pluma']), fila("Residentes, 1 carril, <b>pluma arriba en hora pico</b>", man['salida_residentes_libre']),
        fila(f"Visitas, 1 carril ({man['vis_salen']}/h)", man['salida_visitas_1_carril'])], ["", "Ocupación", "Espera media", "Fila (95 %)"])}
<p>Capacidad por carril: residentes con tag, {AC.CAP['res_entra']} autos/h (6 s por auto); visitas con registro en caseta, {AC.CAP['vis_entra_registro']}/h (40 s), o {AC.CAP['vis_entra_qr']}/h con QR de la app del fraccionamiento (15 s); salida con pluma, {AC.CAP['res_sale_pluma']}/h; con la pluma arriba, {AC.CAP['res_sale_libre']}/h. Cada auto ocupa {AC.AUTO_M} m de fila.</p>
<ul>
<li><b>Un solo carril de residentes no alcanza:</b> en la tarde llegan {tar['res_entran']} autos/h a un carril que da para {AC.CAP['res_entra']}, y la fila nunca se vacía. Con 2 carriles se espera unos segundos.</li>
<li><b>Visitas: 2 carriles.</b> Uno solo se satura si cada registro tarda 40 s. Con QR bastaría uno; el segundo queda para paquetería y apps.</li>
<li><b>La salida de la mañana es el punto fino:</b> con pluma, la fila llega a {man['salida_residentes_pluma']['fila95_m']} m dentro del fraccionamiento; con la pluma arriba baja a {man['salida_residentes_libre']['fila95_m']} m.</li>
</ul>
<p class="nota">Por confirmar: el derecho de vía entre el terreno y la Calzada José Vasconcelos (≈ 30 m) y el permiso de conexión con el municipio. La vuelta a la izquierda para salir a la calzada es lo que más puede frenar la salida; conviene pedir semáforo o glorieta en ese cruce. La salida de emergencia va en el lado norte (ver <a href="/servicios/#barda">Servicios</a>).</p>
"""
    pagina("acceso", "Acceso", "05 · Acceso", "Dos carriles de residentes y dos de visitas para entrar, uno y uno para salir, calculados para la hora pico de las 1,105 casas.".replace("1,105", f0(N)), cuerpo,
           [("plano", "Plano"), ("calculo", "Cálculo de hora pico")])

# ======================= CASA =======================
def casa():
    cuerpo = f"""
{kpis([("Recámaras", "4", "cada una con clóset de paso y baño"), ("Construcción", f"{CD.m2_pb + CD.m2_pa:.0f} m²", f"PB {CD.m2_pb:.0f} + PA {CD.m2_pa:.0f}, más bodega de {CD.m2_bodega:.1f} m²"), ("Sala, comedor y cocina", f"{CD.sala_m2:.0f} m²", "abiertos al portal"),
       ("Portal techado", "27 m²", "comedor de exterior y asador"), ("Para guardar", f"{len(CP.GUARDADO)} lugares", "2 cuartos de blancos y 3 bodegas"), ("Jardín", f"≈ {CD.jardin:.0f} m²", "sin casa, cochera ni patio"), ("Cochera", "2 autos", "con entrada de servicio"), ("Lotes donde cabe", f"{sum(1 for p in LOTES if p['ancho'] >= 12 and p['fondo'] >= 24):,} de {N:,}", "los demás se unen al vecino")])}
<p>Un solo modelo para todo el fraccionamiento: un juego de planos, de moldes y de compras. Todos los lotes miden casi lo mismo (el promedio es de {statistics.mean(p['m2'] for p in LOTES):.0f} m²) y la casa mide 9 m de ancho, así que deja 1.5 m o más libres a cada lado en todos. Lo que cambia es la <a href="/fachadas/">fachada</a>: nueve distintas.</p>
<p><b>Todas las medidas de las plantas son libres, a paño interior de muro</b>: lo que de verdad queda para los muebles. Muros exteriores de 20 cm e interiores de 12 cm. Los muebles están dibujados a escala con medidas comerciales.</p>

<h2 id="conjunto">Planta de conjunto</h2>
<div class="dos">
  <figure>{CD.emplazamiento("norte")}<figcaption><b>Lotes del lado norte de la calle:</b> jardín al NNO. La sala queda fresca todo el año; el sol de la tarde de verano entra de lado al portal, donde van una celosía corrediza y los nogales del fondo.</figcaption></figure>
  <figure>{CD.emplazamiento("sur")}<figcaption><b>Lotes del lado sur:</b> jardín al SSE. En invierno el sol entra hasta la sala; de marzo a octubre el portal la deja en sombra. Es la mejor orientación.</figcaption></figure>
</div>
<ul>
<li><b>El sol en Torreón:</b> en verano, al mediodía, pega casi vertical (88°) y se pone al ONO; en invierno sube solo 41° y viene del sur. Lo que más calienta es el sol de la tarde en verano.</li>
<li><b>Los costados miran al ENE y al OSO</b>, los lados del sol de la mañana y la tarde: por eso quedan casi ciegos, y la casa vecina, a 3.7 m, les da sombra.</li>
<li><b>Los nogales hacen el resto:</b> tiran la hoja en invierno y dan sombra en verano. Cada lote conserva unos 3 en sus linderos.</li>
<li><b>Cochera del lado del patio de servicio:</b> de la cochera al patio, a la lavandería y a la cocina. El mandado y la ropa sucia no cruzan la sala. En el patio, una bodega de {CD.m2_bodega:.1f} m² para herramienta, bicicletas y adornos.</li>
</ul>

<h2 id="plantas">Planta baja y planta alta</h2>
<div class="dos">
  <figure>{CP.planta("PB", f"Planta baja · {CD.m2_pb:.0f} m²")}</figure>
  <figure>{CP.planta("PA", f"Planta alta · {CD.m2_pa:.0f} m²")}</figure>
</div>
<ul>
<li><b>Cada recámara sigue el mismo orden: recámara, clóset de paso y baño.</b> Para llegar al baño se pasa por el clóset: se sale de bañar y se viste ahí, y la ropa no queda a la vista de la cama. Los 3 baños de enfrente quedan uno encima del otro, con la tubería en línea.</li>
<li><b>La escalera sube hacia la fachada</b>, de la sala a la ventana alta del frente. Abajo, en la parte alta, el medio baño de visitas; en la parte baja, una bodega. Arriba, el vacío de la escalera se ilumina con la ventana del frente.</li>
<li><b>La cocina es de dos frentes paralelos</b> con 1.70 m entre cubiertas y el triángulo refri, parrilla y tarja a menos de dos pasos; se abre al comedor y a la sala. Comedor para 8.</li>
<li><b>La recámara principal da al jardín</b> y vuela sobre el portal. Se entra por un recibidor; de la recámara se pasa al vestidor y del vestidor al baño, con doble lavabo, regadera de 1.50 m sin escalón y WC en nicho.</li>
<li><b>La estancia de arriba</b> es para tele o para trabajar en casa, lejos de la sala.</li>
</ul>
<h3>Medidas y muebles, cuarto por cuarto</h3>
<h4>Planta baja</h4>{CP.tabla("PB")}
<h4>Planta alta</h4>{CP.tabla("PA")}

<h2 id="azotea">Planta de azotea</h2>
<div class="dos">
  <figure>{CD.azotea()}<figcaption><b>Azotea de trabajo:</b> 12 paneles solares (5.5 kW, cubren el consumo de una casa con minisplits), calentador solar, tinaco, condensadoras lejos de las recámaras y 4 bajadas que descargan al jardín. Losa con aislante y acabado blanco reflejante: es la superficie que más calor recibe.</figcaption></figure>
  <figure>{CD.corte()}<figcaption><b>Corte longitudinal.</b> La planta alta vuela 3 m sobre el portal: lo techa sin una losa extra y da sombra al cancel de la sala de marzo a octubre, y en invierno deja entrar el sol hasta adentro.</figcaption></figure>
</div>

<h2 id="alzados">Alzados</h2>
<div class="dos">
  <figure>{CD.fachada_posterior()}<figcaption><b>Fachada posterior, al jardín.</b> Es igual en las 9 versiones: portal de 9 × 3 m con dos columnas delgadas, cancel de 8.2 m a la sala y el comedor, y arriba la recámara principal con alero y las ventanas altas del baño.</figcaption></figure>
  <figure>{CD.fachada("Cantera")}<figcaption><b>Fachada principal, a la calle.</b> Una de las nueve (Cantera). Las otras ocho, la regla para repartirlas y cómo se ve una cuadra están en <a href="/fachadas/">Fachadas</a>.</figcaption></figure>
</div>

<h2 id="guardado">Dónde se guardan las cosas</h2>
<p>Una casa con lugar para cada cosa se siente más grande y se mantiene ordenada sola. El Modelo Nogal tiene {len(CP.GUARDADO)} lugares para guardar, además de los gabinetes de cocina y baños:</p>
<ul class="guardado">{"".join(f"<li><b>{e(a)}</b>{e(b)}</li>" for a, b in CP.GUARDADO)}</ul>
<ul>
<li><b>Clósets:</b> 60 cm de fondo libre, doble barra, una sección de barra larga para vestidos y abrigos, cajonera de 4 cajones y maletero arriba hasta el techo. Puertas de piso a techo para que no quede polvo encima.</li>
<li><b>Baños:</b> regadera sin escalón con coladera lineal y cancel fijo de cristal; nicho en el muro de la regadera; mueble de lavabo con cajones; WC lejos de la puerta; extractor y ventana alta en cada baño de enfrente.</li>
<li><b>Blancos:</b> entrepaños de 45 cm (una toalla doblada en 3 cabe justa) a 35 cm entre sí; el de arriba, a 2.20 m, para lo que se usa poco.</li>
</ul>

<h2 id="torreon">Pensada para Torreón</h2>
<ul>
<li>Losa con aislante y acabado blanco reflejante; doble vidrio en las ventanas del frente y el fondo; los costados casi no llevan ventanas.</li>
<li>Ventilación cruzada: todo se abre de frente a fondo.</li>
<li>Azotea libre para paneles y calentador solar, sin sombra de vecinos más altos: todo el fraccionamiento es de 2 niveles.</li>
<li>Jardín de bajo consumo de agua bajo los nogales: grava, plantas del desierto y una zona de pasto chica. Los nogales se riegan con la red morada del fraccionamiento.</li>
</ul>
<p class="nota">Anteproyecto: falta revisar el reglamento de construcción de Torreón (restricciones, coeficientes) y el cálculo estructural.</p>
"""
    pagina("casa", "Casa Modelo Nogal", "06 · Casa Modelo Nogal", "Una sola casa de 243 m² para todo el fraccionamiento: 4 recámaras, cada una con clóset de paso y baño, y lugar para guardar todo. Todos los planos.", cuerpo,
           [("conjunto", "Planta de conjunto"), ("plantas", "Planta baja y alta"), ("azotea", "Azotea y corte"), ("alzados", "Alzados"), ("guardado", "Dónde se guarda"), ("torreon", "Para Torreón")],
           head=CD.DEFS)

# ======================= FACHADAS =======================
def fachadas():
    cuenta = {}
    for p in LOTES: cuenta[p["fachada"]] = cuenta.get(p["fachada"], 0) + 1
    cuerpo = f"""
<p>Detrás de las 9 fachadas está la misma casa: mismos muros, losas, instalaciones y huecos de ventana. Cambian el material, los marcos, los remates y lo que da sombra. Así cada casa tiene identidad y la obra sigue siendo de un solo modelo.</p>
<div class="fachadas">
{"".join(f'<figure id="f-{NF.slug(n)}">{CD.fachada(n)}<figcaption><b>{i}. {n}</b>{e(CD.TEXTO[n])} <span>Sombra: {e(CD.SOMBRA_DE[n])}. · {cuenta.get(n, 0)} casas.</span></figcaption></figure>' for i, n in enumerate(NF.NOMBRES, 1))}
</div>
<h2 id="cuadra">Así se ve una cuadra</h2>
<div class="scroll">{CD.cuadra()}</div>
<ul>
<li><b>Cada lote ya tiene su fachada asignada</b> (en el <a href="/plan/">plan maestro</a>, al tocar un lote). La regla: la casa de al lado y la de enfrente nunca repiten, y cada calle empieza la serie en otro punto. El mismo tipo vuelve a salir hasta 9 casas después.</li>
<li><b>Sirven para las dos orientaciones.</b> Cada tipo trae su manera de dar sombra a las ventanas del frente: en las calles que reciben sol (lotes del lado norte, frente al SSE) esa protección trabaja; en las de sombra, da privacidad.</li>
<li><b>Los nogales de los linderos quedan delante de las casas</b> y unen la cuadra: de la calle se ve una arboleda con casas distintas, no una fila de casas iguales.</li>
<li><b>La fachada posterior</b> (al jardín) es la misma en las nueve; está en <a href="/casa/#alzados">Casa Modelo Nogal</a>.</li>
</ul>
<h2 id="reparto">Reparto</h2>
{tabla([(f"{i}. {e(n)}", f0(cuenta.get(n, 0)), e(CD.SOMBRA_DE[n])) for i, n in enumerate(NF.NOMBRES, 1)], ["Fachada", "Casas", "Lo que da sombra"], "compacta", ("<b>Total</b>", f"<b>{f0(sum(cuenta.values()))}</b>", ""))}
"""
    pagina("fachadas", "Fachadas", "07 · Fachadas", "Nueve fachadas completamente distintas sobre la misma casa, repartidas para que ninguna se repita con la de al lado ni con la de enfrente.", cuerpo,
           [("cuadra", "Una cuadra"), ("reparto", "Reparto")], head=CD.DEFS)

# ======================= SERVICIOS =======================
def servicios():
    A, S_, P_, T_, L_, C_ = SV["agua"], SV["sanitario"], SV["pluvial"], SV["tratamiento"], SV["luz"], SV["calles"]
    por = SV["por_servicio"]
    cuerpo = f"""
{kpis([("Casas", f"{f0(N)}", f"{f0(SV['POB'])} habitantes"), ("Agua potable", f"{f1(A['Qmd'])} l/s", "gasto máximo diario"), ("Drenaje sanitario", f"{f1(S_['Qs_med'])} l/s", "medio, todo por gravedad"), ("Planta de tratamiento", f"{T_['Q_PTAR']} l/s", "riega los nogales"),
       ("Luz", f"{f0(L_['kva'])} kVA", f"{L_['trafos'] + len(L_['especiales'])} transformadores"), ("Urbanización", mill(SV['URB']), f"${f0(SV['URB']/GROSS)}/m² de terreno"), ("Cuota de mantenimiento", f"${f0(SV['cuota_casa'])}", "por casa al mes")])}
<div class="mapa-chico"><div id="map" role="region" aria-label="Redes de servicios sobre el plano"></div></div>
<p class="descargas"><label for="sel-serv" class="boton" style="border:0;padding-left:0">Ver en el mapa:</label><select id="sel-serv" class="sel" style="width:auto;display:inline-block"><option value="pluvial">Drenaje pluvial</option><option value="sanitario">Drenaje sanitario y planta</option><option value="agua">Agua potable y agua tratada</option><option value="luz">Luz, cruces elevados y accesos</option></select>
<a href="/datos/especificaciones.csv" download>Descargar las especificaciones (CSV)</a></p>
<div class="luz" id="serv-nota" hidden></div>

<h2 id="niveles">Terreno y niveles</h2>
<p>Cota media: <b>{SV['TERR']['z_media']:,.1f} m sobre el nivel del mar</b>. El terreno baja {SV['TERR']['pend_km']:.2f} m por km hacia el rumbo {SV['TERR']['rumbo']:.0f}° (casi al oriente): {SV['TERR']['desnivel']:.1f} m de punta a punta. Era una huerta regada por inundación, así que está casi plana. Por eso todo se diseña con pendientes mínimas y los puntos bajos se hacen a propósito.</p>
<ul>
<li><b>Calles largas:</b> un parteaguas a media cuadra y pendiente de 0.3 % hacia cada cruce, donde están las bocas de tormenta. Las transversales bajan al bulevar.</li>
<li><b>Piso terminado de cada casa:</b> 30 cm arriba de la banqueta. Jardín 10 cm abajo de la banqueta.</li>
<li><b>Despalme de 20 cm</b> y terraplenes compactados al 95 % Proctor. La tierra del despalme se queda para los jardines y los parques.</li>
</ul>

<h2 id="pluvial">Drenaje pluvial</h2>
<p>Regla: <b>el agua que cae en {NOMBRE} se queda en {NOMBRE}</b> y riega los nogales. Tormenta de proyecto: {P_['P10']:.0f} mm en una hora (periodo de retorno de 10 años); revisión con {P_['P50']:.0f} mm (50 años). Son valores de referencia para Torreón; hay que confirmarlos con las isoyetas de la SCT y Conagua.</p>
{tabla([("Lotes (azotea, cochera y jardín)", f0(P_['E10']['lotes']), f0(P_['E50']['lotes']), f"jardín 10 cm abajo: {f0(P_['ret_lotes'])} m³"), ("Calles y banquetas", f0(P_['E10']['calles']), f0(P_['E50']['calles']), ""),
        ("Parques, club y áreas verdes", f0(P_['E10']['verde']), f0(P_['E50']['verde']), "")], ["Escurrimiento (m³)", f"Tr 10 · {P_['P10']:.0f} mm", f"Tr 50 · {P_['P50']:.0f} mm", "Dónde se guarda"],
       tot=("A guardar fuera de los lotes", f0(P_['E10t']), f0(P_['E50t']), f"capacidad: {f0(P_['ret_tot'])} m³"))}
{tabla([("Jardines de lluvia del camellón", f0(P_['almacen']['jardines_lluvia'])), ("Parques con bordo de 30 cm", f0(P_['almacen']['parques'])), ("Zanja de infiltración bajo la pista", f0(P_['almacen']['zanja_pista'])),
        ("Cajas de infiltración bajo los 3 estacionamientos", f0(P_['almacen']['cajas'])), (f"Pozos de absorción ({P_['bocas']//2})", f0(P_['almacen']['pozos'])), ("Vaso de tormentas (punta oriente)", f0(P_['almacen']['vaso']))],
       ["Almacenamiento", "m³"], "compacta", ("<b>Total</b>", f"<b>{f0(P_['ret_tot'])}</b>"))}
<ul>
<li><b>Las lluvias chicas</b> (casi todas en Torreón) se meten en las bocas de tormenta y se infiltran en los pozos de absorción de cada cruce.</li>
<li><b>Las tormentas</b> corren por la cuneta (máximo 15 cm de tirante, sin pasar la banqueta) hasta el bulevar. Entran a los jardines de lluvia por cortes en la guarnición y lo que sobra sigue al vaso del oriente, que rebosa a la calle del norte solo con tormentas de más de 50 años.</li>
</ul>
{partidas(["Drenaje pluvial"])}

<h2 id="sanitario">Drenaje sanitario</h2>
{tabla([("Población", f"{f0(SV['POB'])} hab ({SV['HAB']:.0f} por casa)"), ("Dotación", f"{SV['DOT']:.0f} l/hab/día (clima cálido seco), +{(SV['EXTRA']-1)*100:.0f} % club, súper y comercio"), ("Aportación", f"{SV['APORTA']*100:.0f} % del agua"),
        ("Gasto medio", f"{f1(S_['Qs_med'])} l/s"), ("Gasto máximo instantáneo", f"{f1(S_['Qs_max'])} l/s (Harmon {S_['harmon']:.2f})"), ("Gasto máximo extraordinario", f"{f1(S_['Qs_ext'])} l/s"),
        ("Atarjeas", f"Ø 20 cm, pendiente {S_['S_AT']*1000:.1f} al millar, {f0(S_['L_atarjea'])} m"), ("Colector", f"Ø {S_['d_col']*100:.0f} cm, pendiente {S_['S_COL']*1000:.0f} al millar, {f0(S_['L_colector'])} m"),
        ("Profundidad", f"{S_['d_at_min']:.1f} m al inicio de cada calle, {S_['d_at_max']:.1f} m la más honda, {S_['prof_llegada']:.1f} m en la llegada a la planta"), ("Pozos de visita", f"{S_['pozos']}, en cada cruce, cada cambio de dirección y a no más de 100 m")], ["Dato", "Valor"])}
<h3>Perfil: del poniente del bulevar a la planta</h3>
<div class="scroll sec">{S_['perfil']}</div>
{tabla([(e(r["nombre"]), f0(r["largo"]), f0(r["lotes"]), f1(r["q"]), f'{r["diam"]*100:.0f}', f'{r["prof_ini"]:.2f}', f'{r["prof_fin"]:.2f}') for r in S_["ramas"]], ["Atarjea", "Largo (m)", "Lotes", "Gasto máx. ext. (l/s)", "Ø (cm)", "Prof. inicio (m)", "Prof. final (m)"])}
{partidas(["Drenaje sanitario"])}

<h2 id="tratamiento">Planta de tratamiento y red morada</h2>
<p>La planta va en la punta oriente, el punto más bajo: ahí llega todo el drenaje por gravedad. Es compacta y cerrada, con lodos activados (SBR) y desinfección UV; el agua sale con la calidad de la NOM-003-SEMARNAT para riego con contacto. Tiene acceso de servicio por la calle del norte para retirar lodos sin entrar al fraccionamiento.</p>
{tabla([("Agua tratada disponible", f"{f0(T_['trat_dia'])} m³ al día · {f0(T_['trat_anual'])} m³ al año"), ("Riego de los nogales", f"{f0(T_['n_nogales'])} nogales × {T_['M2_ARBOL']:.0f} m² × {T_['ET_NOGAL']:.2f} m × {T_['FRAC_RIEGO']*100:.0f} % = {f0(T_['riego_nogal'])} m³ al año"),
        ("Riego de pasto y jardineras", f"{f0(T_['riego_otros'])} m³ al año"), ("<b>Cobertura</b>", f"<b>{T_['riego_pct']:.0f} %</b> del riego del año. En junio y julio el riego sube; la diferencia se cubre con el tanque de {f0(T_['TANQUE_TRAT'])} m³ y, si falta, con el pozo.")], ["Balance", "Valor"])}
{partidas(["Tratamiento"])}

<h2 id="agua">Agua potable</h2>
{tabla([("Gasto medio", f"{f1(A['Qmed'])} l/s"), ("Gasto máximo diario", f"{f1(A['Qmd'])} l/s (× 1.4)"), ("Gasto máximo horario", f"{f1(A['Qmh'])} l/s (× 1.55)"), ("Volumen al año", f"{f0(A['vol_anual'])} m³"),
        ("Cisterna", f"{f0(A['CISTERNA'])} m³ (11 h del gasto máximo diario), en la plaza de acceso, enterrada y con jardín encima"), ("Presión", "2.0 a 3.5 kg/cm² en toda la red, con bombeo a presión constante"),
        ("Hidrantes", f"{A['hidrantes']}, de 15 l/s cada uno durante 2 h, además del gasto máximo horario"), ("Válvulas", f"{A['valvulas']} cajas de válvulas: se puede cortar una cuadra sin dejar sin agua al resto")], ["Dato", "Valor"])}
<p>Fuente: el pozo de la huerta. Sus derechos de uso agrícola se pasan a uso público urbano ante Conagua y se ceden al organismo operador (SIMAS Torreón), como pide el municipio para dar la factibilidad. Una nogalera de este tamaño suele tener derechos por más de {f0(A['vol_anual'] / 1e3 * 1.2)} mil m³ al año, más de lo que necesita el fraccionamiento. Hay que revisar el título.</p>
{partidas(["Agua potable"])}

<h2 id="luz">Electricidad, alumbrado y telecomunicaciones</h2>
{tabla([("Demanda por casa", f"{L_['DEM_CASA']:.1f} kVA diversificados (4 recámaras con minisplit en verano)"), ("Demanda total", f"{f0(L_['kva'])} kVA, con club, súper, planta, bombeo y alumbrado"),
        ("Transformadores", f"{L_['trafos']} monofásicos de 75 kVA tipo pedestal (≈ 16 casas cada uno) + {len(L_['especiales'])} trifásicos: " + "; ".join(e(x) for x in L_['especiales'])),
        ("Media tensión", "13.2 kV subterránea en anillo, alimentada desde la línea de CFE de la calzada (por confirmar)"), ("Alumbrado", f"{f0(L_['puntos'])} puntos, con fotocelda y reloj (ver <a href='/iluminacion/'>Iluminación</a>)"),
        ("Fibra", "3 ductos de 2\" en todas las calles; cualquier operador puede entrar sin romper banquetas"), ("Gas", "Gas natural si la distribuidora tiene red cerca (por confirmar); si no, tanque estacionario en la azotea de cada casa")], ["Dato", "Valor"])}
{partidas(["Electricidad", "Alumbrado", "Telecomunicaciones"])}

<h2 id="barda">Barda, salida de emergencia y basura</h2>
<ul>
<li><b>Barda perimetral</b> de {f0(C_['barda'])} m: block de 15 cm, 2.8 m de alto, con castillos cada 3 m.</li>
<li><b>Salida de emergencia</b> al norte, en la transversal {e(C_['emergencia'])}: portón de 6 m con cerradura de bomberos. El reglamento la pide y no le quita nada al acceso principal.</li>
<li><b>Acopio de basura y reciclaje</b> antes de las plumas, junto al estacionamiento de visitas: el camión no entra ni hace fila en la caseta.</li>
</ul>
{partidas(["Barda y accesos"])}

<h2 id="presupuesto">Presupuesto de urbanización</h2>
{tabla([(e(k), f"${f0(v)}", f"{v/SV['URB']*100:.1f} %", f"${f0(v/N)}") for k, v in por.items()], ["Servicio", "Importe (MXN sin IVA)", "Parte", "Por lote"], "", ("<b>Total</b>", f"<b>${f0(SV['URB'])}</b>", "<b>100 %</b>", f"<b>${f0(SV['URB']/N)}</b>"))}
<p>Son {mill(SV['URB'])}: ${f0(SV['URB']/GROSS)} por m² de terreno y ${f0(SV['URB']/N)} por lote, con {len(SV['partidas'])} partidas medidas sobre el plano. Lo que significa para el margen del proyecto está en <a href="/numeros/">Números</a>.</p>
{partidas(["Indirectos"])}

<h2 id="confirmar">Por confirmar antes del proyecto ejecutivo</h2>
<ul>
<li>Levantamiento topográfico a cada 10 m. Aquí se usó un modelo de elevación de 30 m, que sirve para saber hacia dónde baja el terreno, no para dar cotas de obra.</li>
<li>Mecánica de suelos y pruebas de infiltración en 6 puntos: de eso dependen los pozos de absorción y las zanjas.</li>
<li>Factibilidades de SIMAS (agua y drenaje, o permiso de planta propia y reúso), CFE (punto de conexión y aportación) y Protección Civil (salida de emergencia e hidrantes).</li>
<li>Título de los derechos de agua de la huerta y estado del pozo.</li>
<li>Isoyetas de lluvia de la SCT o Conagua para Torreón.</li>
</ul>
<p class="nota">Precios de 2026 en pesos, sin IVA, como referencia para decidir; no son una cotización. Las cantidades las mide <code>pipeline/scripts/n6_servicios.py</code> sobre el plano.</p>
"""
    pagina("servicios", "Servicios", "08 · Servicios", "Calles, drenaje pluvial y sanitario, planta de tratamiento, agua potable, luz y fibra: especificaciones, cantidades y presupuesto, medidos sobre el plano.", cuerpo,
           [("niveles", "Terreno y niveles"), ("pluvial", "Drenaje pluvial"), ("sanitario", "Drenaje sanitario"), ("tratamiento", "Planta y red morada"), ("agua", "Agua potable"), ("luz", "Luz y fibra"), ("barda", "Barda y accesos"), ("presupuesto", "Presupuesto"), ("confirmar", "Por confirmar")],
           head='<link rel="stylesheet" href="/vendor/leaflet/leaflet.css">',
           script='<script>window.PLAN={datos:"/datos/",modo:"servicio",servicio:"pluvial",rueda:false};</script><script src="/vendor/leaflet/leaflet.js"></script><script src="/plan/plan.js"></script>')

# ======================= ILUMINACIÓN =======================
def iluminacion():
    t = LZ["tipos"]; orden = ["calle", "bulevar", "nogal", "baliza", "peatonal", "acceso", "caseta", "letrero", "estac", "cancha"]
    cuerpo = f"""
{kpis([("Puntos de luz", f0(LZ['puntos']), "que paga y mantiene el fraccionamiento"), ("Nogales iluminados", f0(LZ['nogales_iluminados']), "desde el piso, en bulevar, parques, club y acceso"), ("Inversión", mill(LZ['inversion']), f"{mill(LZ['inversion_calles'])} de calle + {mill(LZ['inversion_paisaje'])} de paisaje"),
       ("Energía", f"{f0(LZ['kwh_anual'])} kWh/año", f"${f0(LZ['energia_anual'])} al año"), ("Mantenimiento", f"${f0(LZ['mantenimiento_anual'])}", "al año, 4 % de la inversión"), ("Por casa", f"${f0(LZ['cuota_casa_mes'])}", "al mes, dentro de la cuota")])}
<div class="mapa-chico"><div id="map" role="region" aria-label="Vista de noche del plan maestro"></div></div>
<p class="nota">Vista de noche: cada punto cálido es una luminaria; el halo es lo que ilumina. Toca un punto para ver qué es.</p>
<h2 id="idea">La idea</h2>
<p><b>Luz cálida y baja, y los nogales como protagonistas.</b> Las calles se iluminan con arbotantes de 6 m puestos entre los árboles, a tresbolillo, corridos para no quedar junto a ningún tronco. En el bulevar, los parques, el club y la plaza de acceso, cada nogal tiene un foco de piso que lo ilumina desde abajo: de noche se ve la arboleda. El acceso lleva postes más altos, las casetas y el letrero bien iluminados, y la pista para correr, balizas cada 20 m.</p>
<ul>
<li><b>2700 a 3000 K</b> en todo: nada de luz blanca azulosa. Ópticas que alumbran hacia abajo, sin deslumbrar ni iluminar ventanas.</li>
<li><b>Horarios:</b> arbotantes y balizas toda la noche; los focos de los nogales se apagan a medianoche; las canchas, solo cuando se usan.</li>
<li><b>Todo subterráneo</b>, en los ductos de la banqueta, con fotocelda y reloj por circuito.</li>
</ul>
<h2 id="cuenta">Cuántas y de qué tipo</h2>
{tabla([(e(t[k]['nombre']), f0(t[k]['n']), f"${f0(t[k]['costo'])}", f"${f0(t[k]['n'] * t[k]['costo'])}", f"{t[k]['watts']} W · {t[k]['horas']:.0f} h") for k in orden], ["Luminaria", "Cuántas", "Costo instalado", "Importe", "Potencia · horas por noche"],
       "", ("<b>Total</b>", f"<b>{f0(LZ['puntos'])}</b>", "", f"<b>${f0(LZ['inversion'])}</b>", f"{f0(LZ['kwh_anual'])} kWh al año"))}
<p>Los {f0(t['calle']['n'])} arbotantes de calle ({mill(LZ['inversion_calles'])}) van dentro del presupuesto de urbanización; el resto ({mill(LZ['inversion_paisaje'])}: nogales, bulevar, parques, pista y acceso) se suma aparte como iluminación de paisaje. La energía (a $5/kWh de alumbrado) y el mantenimiento (4 % de la inversión al año) suman ${f0(LZ['cuota_casa_mes'])} por casa al mes, ya incluidos en la <a href="/numeros/#cuota">cuota de mantenimiento</a>.</p>
<p class="nota">Costos de luminarias de 2026 con su parte de cable y ducto; tarifa de alumbrado aproximada. Un render de la vista nocturna puede salir de la capa de luces (<code>datos/luces.json</code>).</p>
"""
    pagina("iluminacion", "Iluminación", "09 · Iluminación", f"{f0(LZ['puntos'])} puntos de luz cálida: arbotantes entre los nogales, nogales iluminados desde el piso, balizas en la pista y el acceso bien iluminado.", cuerpo,
           [("idea", "La idea"), ("cuenta", "Cuántas y de qué tipo")],
           head='<link rel="stylesheet" href="/vendor/leaflet/leaflet.css">',
           script='<script>window.PLAN={datos:"/datos/",modo:"noche",rueda:false};</script><script src="/vendor/leaflet/leaflet.js"></script><script src="/plan/plan.js"></script>')

# ======================= NÚMEROS =======================
def numeros():
    F = FID; A, S, P = F["A"], F["S"], F["P"]
    grupos = {"Frente a parque (+8 %)": [p for p in LOTES if p["premio"] == "parque"], "Frente al bulevar (+5 %)": [p for p in LOTES if p["premio"] == "bulevar"], "Frente a calle": [p for p in LOTES if not p["premio"]]}
    filas_v = [(k, f0(len(v)), f0(sum(p["m2"] for p in v)), f"${f0(sum(p['m2'] * precio_lote(p) for p in v) / sum(p['m2'] for p in v))}", f"${f0(sum(p['m2'] * precio_lote(p) for p in v) / len(v))}", mill(sum(p["m2"] * precio_lote(p) for p in v), 1)) for k, v in grupos.items()]
    filas_v.append(("Comercio (súper y frente a Espinoza)", f"{R['lotes_comerciales']} + 1", f0(R["predio_comercial_m2"]), "$6,000", "", mill(VENTA_COM, 1)))
    costo_total = sum(c[1] for c in COSTOS)
    def esc(dp, dr):
        v = R["venta"] * (1 + dp); c = costo_total - BLANDOS + 0.12 * v; return v - c, (v - c) / c
    filas_s = []
    for dp in (-0.10, 0.0, 0.10):
        m, roi = esc(dp, 0); filas_s.append((f"Lotes {'+' if dp > 0 else ''}{dp*100:.0f} % ({f'${f0(3400*(1+dp))}' }/m²)", mill(R["venta"] * (1 + dp)), mill(m), pct(roi)))
    cuerpo = f"""
{kpis([("Venta total", mill(R["venta"]), f"{f0(N)} lotes y {f0(R['predio_comercial_m2'])} m² de comercio"), ("Costo total", mill(R["costo"]), "con el terreno de contado a $670/m²"), ("Margen", mill(R["margen"]), f"{R['roi']:.1f} % sobre el costo"),
       ("Terreno", mill(TERRENO_V), f"{pct(TERRENO_V/R['venta'])} de la venta"), ("Urbanización", mill(SV["URB"]), f"{pct(SV['URB']/R['venta'])} de la venta"), ("Plazo", f"{MESES_VENTA/12:.1f} años de venta", f"{TE.RITMO} lotes al mes desde el mes {TE.INICIO}"),
       ("Cuota de mantenimiento", f"${f0(SV['cuota_casa'])}", "por casa al mes")])}
<h2 id="ventas">Ventas</h2>
<p>El lote se vende urbanizado, sin casa, a <b>≈ $3,400/m²</b> para 300 m² (baja $2 por cada m² de más, para que el lote grande no castigue el precio total), con 8 % más frente a parque y 5 % más frente al bulevar. El comercio se vende a $6,000/m². Son precios de 2026 comparables con lotes urbanizados de Torreón ($3,500–3,750/m²).</p>
{tabla(filas_v, ["Lotes", "Cuántos", "m²", "Precio por m²", "Precio por lote", "Venta"], "", ("<b>Total</b>", f"<b>{f0(N)}</b>", f"<b>{f0(R['vendible_m2'] + R['predio_comercial_m2'])}</b>", "", "", f"<b>{mill(R['venta'], 1)}</b>"))}
<h2 id="costos">Costos</h2>
{tabla([(e(k), mill(v, 1), pct(v / costo_total), e(n)) for k, v, n in COSTOS], ["Concepto", "Importe", "Parte", "Nota"], "", ("<b>Total</b>", f"<b>{mill(costo_total, 1)}</b>", "<b>100 %</b>", ""))}
<h3>Amenidades</h3>
{tabla([(e(k), mill(v, 1)) for k, v in AMEN.items()], ["Amenidad", "Costo"], "compacta", ("<b>Total</b>", f"<b>{mill(R['amenidades'], 1)}</b>"))}
<h3>Urbanización por servicio</h3>
{tabla([(e(k), mill(v, 1), pct(v / SV['URB'])) for k, v in SV['por_servicio'].items()], ["Servicio", "Importe", "Parte"], "compacta", ("<b>Total</b>", f"<b>{mill(SV['URB'], 1)}</b>", "<b>100 %</b>"))}
<p>El detalle partida por partida está en <a href="/servicios/#presupuesto">Servicios</a>.</p>
<h2 id="margen">Margen y lo que aguanta el proyecto</h2>
<p>De contado, con el terreno a ${f0(R['terreno_m2_precio'])}/m², el margen es de <b>{mill(R['margen'])} ({R['roi']:.1f} %)</b>. Es poco para un fraccionamiento: lo sano es 20 % o más sobre lo que se pone. Lo que mueve el resultado es el precio del terreno:</p>
<ul>
<li><b>De contado, el terreno puede costar hasta ${f0(F['p_contado'])}/m²</b> ({mill(F['p_contado'] * A)}) para que al proyecto le quede {pct(F['MARGEN_OBJ'], 0)}.</li>
<li><b>En fideicomiso, el dueño puede llevarse hasta el {pct(F['X_viable'])} de las ventas</b>, que es el porcentaje justo para un terreno de <b>${f0(F['p_fid'])}/m²</b>.</li>
</ul>
<h3>Si los lotes se venden a otro precio</h3>
{tabla(filas_s, ["Escenario", "Venta", "Margen", "Sobre el costo"])}
<h2 id="fideicomiso">El terreno en fideicomiso</h2>
<p>El dueño aporta el terreno a un fideicomiso con un banco y cobra un porcentaje de cada venta, conforme se cobra. <b>El porcentaje justo es el que deja al dueño y al proyecto con la misma ganancia, en pesos de hoy, frente a una venta de contado.</b> Al dueño, esperar un año por su dinero le cuesta {pct(F['R_DUENO'], 0)}; al proyecto, tener el dinero un año le cuesta {pct(F['R_PROY'], 0)}, porque tendría que pedir prestado o poner capital. Por esa diferencia los dos ganan con el fideicomiso.</p>
{kpis([("A $670/m² de contado", mill(P), f"{f0(A)} m²"), ("Porcentaje justo", pct(F['X'], 2), f"≈ {mill(F['cobra'])} en {F['meses']/12:.1f} años · ${f0(F['cobra']/A)}/m²"), ("Lo que gana cada parte", mill(F['gana']), "el dueño y el proyecto, lo mismo, en pesos de hoy"), ("Margen del proyecto", pct(F['margen_fid']/F['costo_fid']), "con ese porcentaje: no conviene")])}
<p class="frase">Para negociar: «Tu terreno vale ${f0(F['p_fid'])} por m² en fideicomiso: te damos el <b>{pct(F['X_viable'])} de cada venta</b>. Es el porcentaje en el que tú y el proyecto ganan lo mismo contra una venta de contado, y el máximo que el proyecto aguanta con las calles, los drenajes, la planta y la barda completos.»</p>
{tabla([("Piso (lo mínimo que le conviene al dueño)", pct(F['X_piso'], 2), mill(F['X_piso']*S), mill(F['X_piso']*F['VPd']), mill(F['X_piso']*F['VPp'])),
        ("<b>Equilibrio a $670/m²</b>", f"<b>{pct(F['X'], 2)}</b>", f"<b>{mill(F['X']*S)}</b>", f"<b>{mill(F['X']*F['VPd'])}</b>", f"<b>{mill(F['X']*F['VPp'])}</b>"),
        ("Techo (lo máximo que le conviene al proyecto)", pct(F['X_techo'], 2), mill(F['X_techo']*S), mill(F['X_techo']*F['VPd']), mill(F['X_techo']*F['VPp']))],
       ["", "Porcentaje de las ventas", "Cobra en total", "Vale hoy para el dueño", "Vale hoy para el proyecto"])}
<p>Fórmula: <code>X = 2 × valor del terreno ÷ (valor de hoy de las ventas para el dueño + para el proyecto)</code>. Ventas de {mill(S)} desde el mes {F['INICIO']} a {F['RITMO']} lotes por mes.</p>
<h3>Si se negocia otro precio por metro</h3>
<p>Cada $100/m² son {pct(2*100*A/(F['VPd']+F['VPp']), 2)} de las ventas.</p>
{tabla([(f"${f0(p)}/m²", mill(p*A), pct(2*p*A/(F['VPd']+F['VPp']), 2), mill(2*p*A/(F['VPd']+F['VPp'])*S), pct(F['m_fid'](p))) for p in sorted({350, 450, round(F['p_fid']), 550, F['PM2'], 750})],
       ["Precio del metro", "Valor de contado", "Porcentaje justo", "Cobra en total", "Margen del proyecto"])}
<h3>Si las ventas van más lentas o más rápidas</h3>
<p>En el fideicomiso el dueño cobra cuando se vende. Si el proyecto vende más despacio, cobra lo mismo pero más tarde, y eso vale menos hoy. Con el {pct(F['X_viable'])}:</p>
{tabla([(f"{rt} lotes al mes ({N/rt/12:.1f} años)", mill(F['X_viable']*S), mill(F['X_viable']*F['vp'](F['R_DUENO'], rt)), f"${f0(F['X_viable']*F['vp'](F['R_DUENO'], rt)/A)}/m²") for rt in (15, 20, 25, 35)], ["Ritmo de ventas", "Cobra en total", "Vale hoy (al 10 %)", "Equivale a"])}
<p class="nota">Cuentas antes de impuestos y con precios de venta fijos (si los lotes suben de precio, el dueño gana en proporción). El fideicomiso de desarrollo lo administra un banco: el dueño aporta el terreno libre de gravámenes, el proyecto pone todo lo demás y el banco le paga al dueño su porcentaje de cada cobro.</p>
<h2 id="cuota">Cuota de mantenimiento</h2>
{tabla([(e(c['concepto']), e(c['incluye']), f"${f0(c['mes'])}") for c in SV['cuota']], ["Concepto", "Qué incluye", "Al mes"], "", ("<b>Total al mes · por casa</b>", "", f"<b>${f0(SV['cuota_total'])} · ${f0(SV['cuota_casa'])}</b>"))}
<p>Es lo que se le puede prometer al comprador: seguridad 24 horas, los nogales regados y podados, la planta operando, la iluminación, el club y un fondo de reserva para pavimentos y bombas.</p>
"""
    pagina("numeros", "Números", "10 · Números", "Ventas, costos, margen, el precio del terreno que aguanta el proyecto, el fideicomiso y la cuota de mantenimiento.", cuerpo,
           [("ventas", "Ventas"), ("costos", "Costos"), ("margen", "Margen"), ("fideicomiso", "Fideicomiso"), ("cuota", "Cuota")])

# ======================= ETAPAS =======================
def etapas():
    por = {k: [p for p in LOTES if ETAPA[p["n"]] == k] for k in range(1, 5)}
    filas = []; mes = TE.INICIO; cal = []
    for k in range(1, 5):
        v = sum(p["m2"] * precio_lote(p) for p in por[k]); dur = len(por[k]) / TE.RITMO
        cal.append((k, mes, mes + dur)); filas.append((f"Etapa {k}", f0(len(por[k])), f0(sum(p['m2'] for p in por[k])), mill(v), f"mes {mes:.0f} a {mes + dur:.0f}")); mes += dur
    fin = cal[-1][2]
    barras = [("Lindero, tenencia y título de agua", 0, 3, 1), ("Acuerdo del terreno (compra o fideicomiso)", 1, 4, 1), ("Topografía, suelos e infiltración", 2, 5, 1), ("Factibilidades: municipio, SIMAS, CFE, Protección Civil", 3, 8, 1),
              ("Proyecto ejecutivo y licencia", 3, 9, 1), ("Obra etapa 1: acceso, bulevar, planta, club social", 8, 15, 0), ("Casa muestra y oficina de ventas", 9, 14, 0),
              ("Ventas etapa 1", cal[0][1], cal[0][2], 1), ("Obra etapa 2 + club deportivo y parques", 14, 21, 0), ("Ventas etapa 2", cal[1][1], cal[1][2], 1),
              ("Obra etapa 3", 20, 27, 0), ("Ventas etapa 3", cal[2][1], cal[2][2], 1), ("Obra etapa 4", 26, 33, 0), ("Ventas etapa 4", cal[3][1], cal[3][2], 1),
              ("Construcción de casas (12 meses después de cada venta)", cal[0][1] + 3, fin + 12, 0)]
    def gantt():
        W, fila_h, izq, pad = 1000, 22, 330, 20; meses = int(fin + 13); H = pad * 2 + fila_h * (len(barras) + 1)
        X = lambda m: izq + (W - izq - pad) * m / meses
        o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Calendario del proyecto" class="gantt">']
        for y in range(0, meses + 1, 6):
            o.append(f'<line x1="{X(y):.1f}" y1="{pad}" x2="{X(y):.1f}" y2="{H - pad}" class="gantt-eje"/><text x="{X(y):.1f}" y="{pad - 6}" class="gantt-a" text-anchor="middle">{"mes " if y == 0 else ""}{y}</text>')
        for yr in range(1, int(meses / 12) + 1): o.append(f'<text x="{X(yr*12):.1f}" y="{H - pad + 14}" class="gantt-a" text-anchor="middle">año {yr}</text>')
        for i, (t, a, b, claro) in enumerate(barras):
            y = pad + fila_h * (i + 0.5)
            o.append(f'<text x="{izq - 10}" y="{y + 4:.1f}" class="gantt-t" text-anchor="end">{e(t)}</text><rect x="{X(a):.1f}" y="{y - 7:.1f}" width="{max(X(b) - X(a), 2):.1f}" height="14" class="gantt-barra{" clara" if claro else ""}"/>')
        o.append("</svg>")
        return "\n".join(o)
    cuerpo = f"""
{kpis([("Etapas", "4", "desde el acceso hacia los dos lados"), ("Lotes por etapa", f"≈ {f0(N/4)}", "11 meses de venta cada una"), ("Arranque de ventas", f"mes {TE.INICIO}", "con la licencia"), ("Última venta", f"mes {fin:.0f}", f"{fin/12:.1f} años"), ("Ritmo", f"{TE.RITMO} lotes/mes", "supuesto del modelo")])}
<figure><div class="dibujo">{plano_svg("etapas", titulo="Etapas de construcción")}</div><figcaption><b>Las etapas crecen desde el acceso.</b> La etapa 1 lleva lo que se tiene que ver desde el primer día: acceso, mini súper, club social, bulevar, planta de tratamiento y los lotes de alrededor. Cada etapa se urbaniza completa (calles, redes, alumbrado, nogales regados) antes de entregar lotes.</figcaption></figure>
{tabla(filas, ["Etapa", "Lotes", "m² vendibles", "Venta", "Ventas"], "", ("<b>Total</b>", f"<b>{f0(N)}</b>", f"<b>{f0(R['vendible_m2'])}</b>", f"<b>{mill(VENTA_LOTES)}</b>", ""))}
<h2 id="calendario">Calendario</h2>
<div class="scroll sec" style="--min:52rem"><div class="dibujo">{gantt()}</div></div>
<ul>
<li><b>Meses 0 a 9: papeles.</b> Lindero y tenencia con catastro y el Registro Público, título de agua, acuerdo con el dueño, topografía y mecánica de suelos, factibilidades y proyecto ejecutivo. Las ventas empiezan con la licencia.</li>
<li><b>La obra va una etapa adelante de las ventas:</b> cuando se vende la etapa 1 ya se está urbanizando la 2. La planta de tratamiento y la cisterna son de la etapa 1 porque sirven a todo.</li>
<li><b>Casas:</b> el comprador construye con el Modelo Nogal y una de las 9 fachadas (o encarga la casa al mismo proyecto). Un año después de cada venta hay casas habitadas, y el club y los parques ya están.</li>
</ul>
<h2 id="siguientes">Siguientes pasos</h2>
<ol>
<li><b>Confirmar el predio:</b> lindero, superficie real, tenencia (propiedad privada o ejido) y gravámenes; título de concesión de agua del pozo y su volumen.</li>
<li><b>Sentarse con el dueño</b> con las dos opciones calculadas: compra de contado (hasta ${f0(FID['p_contado'])}/m²) o fideicomiso ({pct(FID['X_viable'])} de las ventas). Ver <a href="/numeros/#fideicomiso">Números</a>.</li>
<li><b>Uso de suelo:</b> consulta en Desarrollo Urbano de Torreón sobre densidad, restricciones, áreas de donación y la conexión a la Calzada José Vasconcelos.</li>
<li><b>Estudios de campo:</b> topografía a cada 10 m, mecánica de suelos y pruebas de infiltración.</li>
<li><b>Factibilidades</b> de SIMAS (o permiso de planta propia y reúso), CFE y Protección Civil.</li>
<li><b>Proyecto ejecutivo</b> de lotificación, vialidades y redes, con este anteproyecto como base, y licencia.</li>
<li><b>Imagen y ventas:</b> renders (vista de día y de noche, la cuadra, la casa muestra), nombre definitivo y oficina de ventas en el acceso.</li>
</ol>
<p class="nota">El calendario es un supuesto de trabajo con el ritmo de ventas del modelo ({TE.RITMO} lotes al mes). Los plazos de trámites dependen del municipio y de los organismos.</p>
"""
    pagina("etapas", "Etapas y siguientes pasos", "11 · Etapas y siguientes pasos", "Cuatro etapas que crecen desde el acceso, un calendario de obra y ventas, y la lista de lo que hay que confirmar para arrancar.", cuerpo,
           [("calendario", "Calendario"), ("siguientes", "Siguientes pasos")])

# ======================= NOGALERAS (mapa de La Laguna) =======================
def nogaleras():
    cuerpo = f"""
<div id="map" role="region" aria-label="Mapa de nogaleras de La Laguna"></div>
<section class="panel" id="panel" aria-labelledby="titulo">
  <h1 id="titulo">Nogaleras de La Laguna <span>Torreón, Gómez Palacio, Lerdo y alrededores: de aquí salió N6</span></h1>
  <p class="stats" id="stats">Cargando…</p>
  <ul class="legend" aria-label="Qué se muestra">
    <li><label><input type="checkbox" data-estado="activa" checked> <i class="sw sw-activa" aria-hidden="true"></i> Nogalera <b id="n-activa"></b></label></li>
    <li><label><input type="checkbox" data-estado="desmontada" checked> <i class="sw sw-desmontada" aria-hidden="true"></i> Ya sin nogales <b id="n-desmontada"></b></label></li>
    <li><label><input type="checkbox" data-estado="urbanizada" checked> <i class="sw sw-urbanizada" aria-hidden="true"></i> Urbanizada <b id="n-urbanizada"></b></label></li>
  </ul>
  <div class="actions">
    <button type="button" id="btn-lista" aria-expanded="false" aria-controls="lista">Lista</button>
    <button type="button" id="btn-ubicacion">Mi ubicación</button>
    <button type="button" id="btn-info" aria-haspopup="dialog">Cómo se hizo</button>
  </div>
  <div class="seleccion" aria-labelledby="sel-titulo">
    <h2 id="sel-titulo"><label><input type="checkbox" id="chk-seleccion" checked> Las 5 aptas para urbanizar</label></h2>
    <ol id="sel-items"></ol>
    <p class="sel-nota">Pegadas a la mancha urbana, de 20 a 58 ha y con confianza alta. N6 es la elegida: <a href="/terreno/">El terreno</a>.</p>
  </div>
</section>
<aside class="lista" id="lista" hidden aria-labelledby="lista-titulo">
  <div class="lista-head"><h2 id="lista-titulo">Cerca de <span id="ref-nombre">Real del Nogalar</span></h2><button type="button" class="cerrar" id="cerrar-lista" aria-label="Cerrar lista">×</button></div>
  <div class="lista-orden"><label for="orden">Ordenar por</label><select id="orden"><option value="dist">Distancia</option><option value="area">Tamaño</option><option value="precio">Precio por m²</option><option value="valor">Valor</option></select></div>
  <ol id="items"></ol>
</aside>
<dialog id="info" aria-labelledby="info-titulo">
  <div class="info-head"><h2 id="info-titulo">Cómo se hizo este mapa</h2><button type="button" class="cerrar" id="cerrar-info" aria-label="Cerrar">×</button></div>
  <div class="info-body">
    <p><b>Qué hay:</b> todas las huertas de nogal que se pudieron detectar en la Comarca Lagunera, de Nazas y Lerdo a San Pedro y de Tlahualilo a Viesca. Cada polígono es una huerta o un bloque de huerta.</p>
    <p><b>Cómo se encontraron:</b> en OpenStreetMap solo había 6 nogaleras dibujadas, así que se sacaron de imágenes de satélite: el mapa de altura de árboles a 1&nbsp;m de Meta y el WRI (2018–2020) y la serie de Sentinel-2 de diciembre de 2025 a septiembre de 2026. Una nogalera se reconoce por su cuadrícula de árboles altos, que tiran la hoja en invierno y están verdes de abril a septiembre. Se revisaron a ojo cerca de 800 casos. Acierta en unos 9 de cada 10.</p>
    <p><b>Medidas:</b> la superficie es la de la arboleda vista desde el satélite (cuadros de 10&nbsp;m), no la de la escritura: ±5 a 10&nbsp;%.</p>
    <p><b>Precio, a ojo de buen cubero:</b> una nogalera en producción lejos de la ciudad vale unos $90/m². Sube conforme se acerca a la mancha urbana: hasta $800/m² pegada a Torreón, $600 a Gómez o Lerdo y $300 a los pueblos. Calibrado con anuncios de 2025 y 2026. <b>No es un avalúo.</b></p>
    <p><b>Fuentes:</b> Meta y WRI; Sentinel-2 (Copernicus, ESA); ESA WorldCover; Copernicus DEM; OpenStreetMap vía Overture Maps (septiembre de 2026). Datos: <a href="/datos/nogaleras.geojson" download data-descarga>GeoJSON</a> · <a href="/datos/nogaleras.csv" download data-descarga>CSV</a>.</p>
  </div>
</dialog>
"""
    pagina("nogaleras", "Nogaleras de La Laguna", "A · Nogaleras de La Laguna", "", cuerpo, mapa=True, descripcion="Mapa de todas las nogaleras de Torreón, Gómez Palacio, Lerdo y alrededores, con superficie y precio estimado.",
           script='<script src="/vendor/leaflet/leaflet.js"></script><script src="/nogaleras/app.js"></script>')

# ======================= DATOS =======================
def datos():
    archivos = [("confort.geojson", "Plan maestro: lotes con dirección y fachada, calles, club, parques, planta, con el resumen de cifras del proyecto."), ("arboles_confort.json", "Los 2,305 nogales: longitud, latitud, si se reubica y altura."),
                ("servicios.geojson", "Redes: drenaje pluvial y sanitario, agua, agua tratada, transformadores, cruces elevados, salida de emergencia."), ("luces.json", "Los 1,027 puntos de luz, por tipo."),
                ("servicios.json", "Todos los cálculos de servicios, partidas y cuota."), ("especificaciones.csv", "Hoja de especificaciones y presupuesto de urbanización, partida por partida."), ("etapas.json", "Etapa de construcción de cada lote."),
                ("nogaleras.geojson", "Todas las nogaleras de La Laguna, con superficie, estado y precio estimado."), ("nogaleras.csv", "Lo mismo en tabla."), ("base.geojson", "Fondo vectorial de La Laguna (OpenStreetMap vía Overture).")]
    filas = []
    for n, d in archivos:
        p = os.path.join(DAT, n); kb = os.path.getsize(p) / 1024 if os.path.exists(p) else 0
        filas.append((f'<a href="/datos/{n}" download>{n}</a>', e(d), f"{kb:,.0f} KB"))
    cuerpo = f"""
<p>Todo lo que muestra el sitio sale de estos archivos, y estos salen del código en <code>pipeline/</code> del repositorio. Coordenadas en WGS 84 (longitud, latitud). Cifras en pesos de 2026 sin IVA.</p>
{tabla(filas, ["Archivo", "Qué tiene", "Tamaño"], "spec")}
<h2 id="como">Cómo se hizo</h2>
<ul>
<li><b>Nogaleras:</b> detección desde satélite (altura de árboles de Meta y WRI a 1 m, serie de Sentinel-2 2025–2026) con revisión a ojo. Mapa en <a href="/nogaleras/">Nogaleras de La Laguna</a>.</li>
<li><b>Nogales de N6:</b> cada árbol se ubica en el mapa de altura a 1 m; de ahí sale la cuadrícula (hileras cada 12.6 m, rumbo 59°) que ordena el diseño.</li>
<li><b>Diseño:</b> calles sobre los pasillos entre hileras, linderos sobre las columnas de árboles, bulevar y club sobre las dos hileras que ya faltaban. Todo está programado: si cambia un dato, se vuelve a generar todo.</li>
<li><b>Servicios:</b> cantidades medidas sobre el plano; pendientes del modelo de elevación Copernicus de 30 m.</li>
<li><b>Fondo de los mapas:</b> © colaboradores de OpenStreetMap.</li>
</ul>
"""
    pagina("datos", "Datos para descargar", "B · Datos", "Los archivos con los que está hecho el proyecto, para abrirlos en QGIS, Excel o cualquier otro programa.", cuerpo, [("como", "Cómo se hizo")])

if __name__ == "__main__":
    for fn in (resumen, terreno, plan, calles, acceso, casa, fachadas, servicios, iluminacion, numeros, etapas, nogaleras, datos): fn()
