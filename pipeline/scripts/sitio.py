"""La Nogalera · constructor del sitio (tablero: menú a la izquierda, contenido a la derecha).
Solo python3: lee public/datos/*.json (los escribe el pipeline pesado) y los módulos de dibujo, y escribe una carpeta por sección en public/.
    python3 scripts/sitio.py            # desde pipeline/"""
import csv, json, math, os, statistics, sys
from html import escape as e
e_ = e
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
PUB = os.path.join(RAIZ, "public"); DAT = os.path.join(PUB, "datos")
import n6_casa_planta as CP, n6_casa_dibujos as CD, n6_fachadas as NF, n6_acceso as AC, n6_acceso_calc as ACC, n6_terreno as TE, n6_fideicomiso as FI, n6_casa3d as C3D

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
    ("acceso", "Acceso y barda", "05"), ("casa", "Casa Modelo Nogal", "06"), ("fachadas", "Fachadas", "07"), ("renders", "Renders", "08"), ("servicios", "Servicios", "09"), ("agua", "Agua: pozos, red y presión", "10"),
    ("iluminacion", "Iluminación", "11"), ("pista", "Pista y gimnasio", "12"), ("numeros", "Números y fideicomiso", "13"), ("porque", "Por qué $522 por m²", "14"), ("inversionista", "Para el inversionista", "15"), ("comercializador", "Para el comercializador", "16"), ("etapas", "Etapas y siguientes pasos", "17"),
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
  <p class="estado"><a href="/inicio/">Página del cliente →</a></p>
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

def esquema_numeros(calle, q, S=3.2):
    """Una cuadra de una calle con sus números, en planta, desde el plano."""
    idx = R["calles_largas"].index(calle); v = _v_de_calle(calle)
    xs = [_u_de_cruce(n) for n in R["calles_cruce"]]; ua, ub = xs[q - 1], xs[q]
    fs = [f for f in _lotes_f if f["properties"]["dir"].startswith(calle + " ") and f["properties"]["dir"].split()[1].rjust(3, "0")[0] == str(q) and len(f["properties"]["dir"].split()[1]) == 3]
    pad = 14; W = (ub - ua + 30) * S + 2 * pad; H = 70 * S + 2 * pad
    X = lambda u: pad + (u - ua + 15) * S; Y = lambda vv: pad + (v + 35 - vv) * S
    o = [f'<svg viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="Números de una cuadra de {e(calle)}">']
    o.append(f'<rect x="{X(ua-15):.1f}" y="{Y(v+5.5):.1f}" width="{(ub-ua+30)*S:.1f}" height="{11*S:.1f}" class="pm-vial"/>')
    for x in (ua, ub): o.append(f'<rect x="{X(x-5.5):.1f}" y="{Y(v+35):.1f}" width="{11*S:.1f}" height="{70*S:.1f}" class="pm-vial"/>')
    for f in fs:
        pts = " ".join(f"{X(u):.1f},{Y(vv):.1f}" for u, vv in (uv(*c) for c in f["geometry"]["coordinates"][0]))
        o.append(f'<polygon points="{pts}" class="pm-lote" style="stroke:#000;stroke-width:0.8"/>')
        cu, cv = uv(*centro(f)); n = f["properties"]["dir"].split()[1]
        o.append(f'<text x="{X(cu):.1f}" y="{Y(cv)+4:.1f}" font-size="11" text-anchor="middle" fill="#000">{n}</text>')
    o.append(f'<text x="{X((ua+ub)/2):.1f}" y="{Y(v)+4:.1f}" class="pm-rotulo" text-anchor="middle">{e(calle)}</text>')
    for x, n in ((ua, R["calles_cruce"][q - 1]), (ub, R["calles_cruce"][q])):
        o.append(f'<text x="{X(x):.1f}" y="{Y(v+35)-4:.1f}" class="pm-rotulo cruce" text-anchor="middle">{e(n)}</text>')
    o.append(f'<text x="{X(ua-13):.1f}" y="{Y(v+25):.1f}" class="a">norte: impares</text><text x="{X(ua-13):.1f}" y="{Y(v-25):.1f}" class="a">sur: pares</text>')
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
PRECIO_BASE = 3400.0                          # precio de lista por m² del lote de 300 m² en la etapa 1 (ver n6_confort.py); sube FI.ESCALON_ETAPA por etapa
LISTA = FI.lista(PRECIO_BASE)
def precio_lote(p):
    x = PRECIO_BASE - 2 * (p["m2"] - 300)
    return x * (1.08 if p["premio"] == "parque" else 1.05 if p["premio"] == "bulevar" else 1.0)
MESES_VENTA = N / TE.RITMO
PARQUES = [f["properties"]["nombre"] for f in FC["features"] if f["properties"]["capa"] == "parque"]
# ---- la propuesta: $522/m² en fideicomiso = 34.3 % de cada venta ----
X_DUENO = 0.343; PRECIO_FID = 522.0          # la propuesta, fija: $522/m² = 34.3 % de cada venta (el cálculo de n6_terreno.py da 34.35 % y $523; se redondea a favor del proyecto)
AM_SOCIAL = sum(v for k, v in AMEN.items() if "salón" in k or "gimnasio" in k or "acceso" in k); AM_DEP = R["amenidades"] - AM_SOCIAL
MOD = FI.modelo(R["venta"], N, X_DUENO, SV["URB"], dict(social=AM_SOCIAL, deportivo=AM_DEP), PAISAJE, REUBICA, SV["cuota_casa"])
OBRA_TOTAL = SV["URB"] + R["amenidades"] + PAISAJE + REUBICA
DUENO_TOTAL = X_DUENO * R["venta"]
CON = FI.construccion(MOD["ventas"], N)
OPER_10 = sum(f["oper_margen"] for f in MOD["flujo"])
OPER_ANIO = sum(f["oper_margen"] for f in MOD["flujo"][-12:])          # margen de la operadora en el último año (velocidad de crucero)
NOS_SIN = MOD["desarrollador"] + OPER_10; NOS_CON = NOS_SIN + CON["utilidad"]
ESCEN = FI.escenarios(R["venta"], N, X_DUENO, SV["URB"], dict(social=AM_SOCIAL, deportivo=AM_DEP), PAISAJE, REUBICA, SV["cuota_casa"])
_esc0 = FI.ESCALON_ETAPA; FI.ESCALON_ETAPA = 0.0
_m0 = FI.modelo(R["venta"], N, X_DUENO, SV["URB"], dict(social=AM_SOCIAL, deportivo=AM_DEP), PAISAJE, REUBICA, SV["cuota_casa"]); FI.ESCALON_ETAPA = _esc0
ESCEN0 = dict(lotes=_m0["lotes_desarrollador"], desarrollador=_m0["desarrollador"], recupera=_m0["m_recupera"])   # el mismo modelo sin subir la lista por etapa
EJEMPLO = next(p["dir"] for p in sorted(LOTES, key=lambda p: p["n"]) if p["dir"].startswith("Encino 4") and int(p["dir"].split()[1]) % 2 == 1)

# ======================= RESUMEN =======================
def resumen():
    tarj = [("terreno", "El terreno", f"{ha(GROSS)} de nogalera en La Paz, al oriente de Torreón; {f0(R['arboles'])} nogales mapeados uno por uno."),
            ("plan", "Plan maestro", f"Mapa interactivo con los {f0(N)} lotes, calles, club, parques, nogales, iluminación y redes."),
            ("calles", "Calles y direcciones", "Nombres, numeración, secciones de calle y bulevar, cruces elevados."),
            ("acceso", "Acceso y barda", "La entrada en seis zonas con plano y alzado, calculada para la hora pico, y la barda por tramos con su estructura, cerca y cámaras."),
            ("casa", "Casa Modelo Nogal", "Modelo 3D a color para girar y destapar, plantas amuebladas, azotea, corte, conjunto y fachadas: todos los planos."),
            ("fachadas", "Fachadas", "Nueve fachadas distintas sobre la misma casa, y cómo se reparten en cada cuadra."),
            ("renders", "Renders", "Los diez renders que más venden el proyecto y el creador para hacer todos los demás, con la geometría real."),
            ("servicios", "Servicios", "Drenaje pluvial y sanitario, planta de tratamiento, agua, luz y fibra, con especificaciones y presupuesto."),
            ("agua", "Agua: pozos, red y presión", "Dónde van los dos pozos, la red con su presión en cada esquina, la planta de tratamiento y el drenaje pluvial, dibujados."),
            ("iluminacion", "Iluminación", f"{f0(LZ['puntos'])} puntos de luz, cada uno en su lugar y con su clave: arbotantes, nogales iluminados, balizas y acceso."),
            ("pista", "Pista y gimnasio", "La pista de 3.3 km bajo los nogales, con estaciones y vueltas, y el gimnasio del club social."),
            ("numeros", "Números y fideicomiso", "Cómo opera el fideicomiso, qué recibe cada quien y el flujo de efectivo mes a mes."),
            ("porque", "Por qué $522 por m²", "Siete razones con números: es el máximo que el proyecto aguanta y más de lo que el dueño obtendría por cualquier otra vía."),
            ("inversionista", "Para el inversionista", "Por qué conviene poner la obra: capital máximo, mes en que recupera, rendimiento, escenarios, garantías y la hoja de una página."),
            ("comercializador", "Para el comercializador", "Lista de precios por etapa, comisiones, metas de venta, argumentos, objeciones, proceso y la hoja de una página."),
            ("etapas", "Etapas y siguientes pasos", "Cuatro etapas desde el acceso, calendario y lo que hay que confirmar.")]
    cuerpo = f"""
<p class="lede ancho" style="max-width:52rem;font-size:1.25rem;margin-top:0">{f0(N)} casas entre {f0(QUEDAN)} nogales, en {ha(GROSS)} al oriente de Torreón. Un fraccionamiento trazado sobre la huerta, con un solo modelo de casa y nueve fachadas, que riega sus propios árboles.</p>
{kpis([("Terreno", ha(GROSS), f"{f0(GROSS)} m² · La Paz, Torreón"), ("Casas", f0(N), f"lote típico de {R['lote_mediana']} m²"), ("Nogales que se quedan", f"{pct(QUEDAN/R['arboles'],0)}", f"{f0(QUEDAN)} de {f0(R['arboles'])}"),
       ("Venta", mill(MOD["venta_total"]), f"{f0(N)} lotes y {f0(R['predio_comercial_m2'])} m² de comercio, lista +{pct(FI.ESCALON_ETAPA, 0)} por etapa"), ("Obra", mill(OBRA_TOTAL), "urbanización, club, parques, acceso, agua e iluminación"),
       ("Para el dueño del terreno", f"{pct(X_DUENO)} de cada venta", f"{mill(MOD['dueno_total'])} en {MOD['fin_ventas']/12:.1f} años"), ("Operadora", f"${f0(FI.CUOTA_CASA)} · ${f0(FI.CUOTA_LOTE)}", "al mes por casa · por lote, más el agua")])}
<p class="frase"><b>🚶 Caminar en el modelo 3D:</b> <a class="boton" href="/renders/foto/?escena=completo&amp;caminar=1">el fraccionamiento completo</a> <a class="boton" href="/renders/foto/?escena=fachadas&amp;caminar=1">la cuadra de las nueve fachadas</a> <a class="boton" href="/renders/foto/?escena=parque&amp;caminar=1">el parque</a> <span class="nota">flechas para avanzar, ratón para mirar.</span></p>
<p class="frase"><b>Así lo ve el cliente:</b> <a href="/inicio/">nogalera.capitaltorreon.com/inicio/</a>. La página de venta, con todos los renders, lo que incluye, los precios de la etapa 1 y el formulario que guarda a cada interesado en la base de datos (nombre, celular, correo, primera o segunda casa, crédito y qué tan rápido quiere comprar). Los prospectos se descargan desde <a href="/datos/#prospectos">Datos</a>.</p>
<p class="frase">La propuesta al dueño: <b>${f0(PRECIO_FID)} por m² en fideicomiso: te damos el {pct(X_DUENO)} de cada venta.</b> Aportas el terreno, no pones un peso más, y cobras conforme se vende: {mill(DUENO_TOTAL)} a precio de arranque, {mill(MOD['dueno_total'])} con la lista subiendo por etapa. Cómo opera, en <a href="/numeros/">Números y fideicomiso</a>.</p>
<figure><div class="dibujo">{plano_svg("plan", titulo="Plano maestro")}</div><figcaption><b>Plano maestro.</b> Cada punto es un nogal en su lugar exacto; los blancos son los {f0(R['reubicar'])} que se reubican. El bulevar Nogal corre por la hilera que ya faltaba en la huerta; el club, por la otra.</figcaption></figure>
<h2 id="secciones">Secciones</h2>
<ul class="tarjetas">{"".join(f'<li><a class="tarjeta" href="/{s_}/"><span class="n">{dict((x[0], x[2]) for x in SECCIONES if x)[s_]}</span><b>{e(t)}</b><p>{e(d)}</p></a></li>' for s_, t, d in tarj)}</ul>
"""
    pagina("", f"{NOMBRE}", "01 · Resumen", "", cuerpo, [("secciones", "Secciones")],
           descripcion=f"{NOMBRE}: fraccionamiento de {f0(N)} casas entre nogales en el oriente de Torreón. Anteproyecto completo.")

# ======================= TERRENO =======================
def terreno():
    alto = sum(1 for h in H_ARB if h >= 10)
    cuerpo = f"""
{kpis([("Superficie", ha(GROSS), f"{f0(GROSS)} m² · {N6['largo_m']} × {N6['ancho_m']} m"), ("Nogales", f0(R['arboles']), f"{f0(alto)} de 10 m o más · hileras cada 12.6 m"), ("Cota", f"{SV['TERR']['z_media']:,.1f} m", f"baja {SV['TERR']['pend_km']:.2f} m/km al oriente"),
       ("En fideicomiso", f"${f0(PRECIO_FID)}/m²", f"{pct(X_DUENO)} de cada venta"), ("Para el dueño", mill(DUENO_TOTAL), f"en {MOD['fin_ventas']/12:.1f} años · ${f0(DUENO_TOTAL/GROSS)}/m²"), ("Ubicación", "La Paz", "oriente de Torreón, Coahuila")])}
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
<h2 id="precio">Cuánto vale y cómo se paga</h2>
<p class="frase"><b>${f0(PRECIO_FID)} por m² en fideicomiso: te damos el {pct(X_DUENO)} de cada venta.</b></p>
<p>El dueño aporta el terreno al fideicomiso y cobra el {pct(X_DUENO)} de cada lote conforme se vende: <b>{mill(DUENO_TOTAL)}</b> en total a lo largo de {MOD['fin_ventas']/12:.1f} años, que son ${f0(DUENO_TOTAL/GROSS)} por m². En pesos de hoy equivale a ${f0(PRECIO_FID)}/m² ({mill(PRECIO_FID*GROSS)}), dentro del rango de ${N6['precio_m2_min']} a ${N6['precio_m2_max']}/m² que el <a href="/nogaleras/#n6">mapa de nogaleras</a> estima para huertas pegadas a Torreón. Cómo opera el fideicomiso y el flujo mes a mes: <a href="/numeros/">Números y fideicomiso</a>.</p>
<h2 id="origen">De dónde salió</h2>
<p>Primero se mapearon <b>todas las nogaleras de la Comarca Lagunera</b> desde satélite ({f0(sum(1 for r in NOG if r['estado']=='activa'))} huertas activas, {f0(sum(float(r['area_m2']) for r in NOG if r['estado']=='activa')/1e4)} ha). De las cinco mejor situadas para urbanizar, esta (N6) es la que da el mayor retorno por m²: grande, plana, con calles por dos lados y a la orilla de la ciudad. El mapa completo está en <a href="/nogaleras/">Nogaleras de La Laguna</a>.</p>
"""
    pagina("terreno", "El terreno", "02 · El terreno", f"Una nogalera de {ha(GROSS)} en La Paz, al oriente de Torreón, con {f0(R['arboles'])} nogales mapeados uno por uno.", cuerpo,
           [("donde", "Dónde está"), ("arboles", "Los nogales"), ("precio", "Cuánto vale y cómo se paga"), ("origen", "De dónde salió")], mapa=False,
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
    <div><input id="q" list="dirs" placeholder="Ej. {EJEMPLO}" autocomplete="off"><button type="submit">Ir</button></div>
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
           script='<script>window.PLAN={datos:"/datos/",modo:"plan",ejemplo:"' + EJEMPLO + '",etapas:' + json.dumps(ETAPA, separators=(",", ":")) + '};</script><script src="/vendor/leaflet/leaflet.js"></script><script src="/plan/plan.js"></script>')

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
<p>Las transversales no tienen casas con frente a ellas: solo cruzan. Los parques toman el nombre de su transversal ({", ".join(PARQUES)}).</p></div>
</div>
<h2 id="numeros">Cómo van los números</h2>
<div class="dos">
<div>
<ul>
<li><b>La centena es la cuadra:</b> cuántas transversales quedan al poniente de la casa. «{EJEMPLO}» está en Encino, pasando la {int(EJEMPLO.split()[1])//100}.ª transversal ({R['calles_cruce'][int(EJEMPLO.split()[1])//100 - 1]}). La primera cuadra, antes de {R['calles_cruce'][0]}, va del 1 al 99.</li>
<li><b>Impares al norte, pares al sur,</b> y el número va por posición en la cuadra (uno cada 12.7 m): la casa de enfrente del 405 es el 404 o el 406, siempre.</li>
<li><b>Los números crecen de poniente a oriente</b> en todas las calles. El más alto es el {R['num_max']}.</li>
<li><b>En la esquina, la placa dice las dos calles y el rango:</b> «Encino 401–423». Con el número sabes la cuadra; con la letra, la calle.</li>
</ul>
</div>
<figure>{esquema_numeros("Encino", 4)}<figcaption><b>Una cuadra de Encino,</b> entre {R['calles_cruce'][2]} y {R['calles_cruce'][3]}: los números tal como quedan en el plano.</figcaption></figure>
</div>
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
           [("nombres", "Nombres y direcciones"), ("numeros", "Cómo van los números"), ("secciones", "Secciones de calle"), ("presupuesto", "Lo que cuestan")])

# ======================= CASA =======================
def casa():
    cuerpo = f"""
{kpis([("Recámaras", "4", "cada una con clóset de paso y baño"), ("Construcción", f"{CD.m2_pb + CD.m2_pa:.0f} m²", f"PB {CD.m2_pb:.0f} + PA {CD.m2_pa:.0f}, más bodega de {CD.m2_bodega:.1f} m²"), ("Sala, comedor y cocina", f"{CD.sala_m2:.0f} m²", "abiertos al portal"),
       ("Portal techado", "27 m²", "comedor de exterior y asador"), ("Para guardar", f"{len(CP.GUARDADO)} lugares", "2 cuartos de blancos y 3 bodegas"), ("Jardín", f"≈ {CD.jardin:.0f} m²", "sin casa, cochera ni patio"), ("Cochera", "2 autos", "con entrada de servicio"), ("Lotes donde cabe", f"{sum(1 for p in LOTES if p['ancho'] >= 12 and p['fondo'] >= 24):,} de {N:,}", "los demás se unen al vecino")])}
<p>Un solo modelo para todo el fraccionamiento: un juego de planos, de moldes y de compras. Todos los lotes miden casi lo mismo (el promedio es de {statistics.mean(p['m2'] for p in LOTES):.0f} m²) y la casa mide 9 m de ancho, así que deja 1.5 m o más libres a cada lado en todos. Lo que cambia es la <a href="/fachadas/">fachada</a>: nueve distintas.</p>
<p><b>Todas las medidas de las plantas son libres, a paño interior de muro</b>: lo que de verdad queda para los muebles. Muros exteriores de 20 cm e interiores de 12 cm. Los muebles están dibujados a escala con medidas comerciales.</p>

<h2 id="3d">La casa en 3D</h2>
<p>Gírala con el ratón o el dedo, acércala con la rueda, quítale el techo o la planta alta para ver cómo está por dentro. Está amueblada tal como las plantas. Fachada <a href="/fachadas/#f-horizonte">Horizonte</a>.</p>
<div class="visor3d">
  <canvas id="c3d" aria-label="Modelo 3D de la casa, con muebles"></canvas>
  <div class="botones">
    <button type="button" data-capa="techo" aria-pressed="true">Techo</button><button type="button" data-capa="pa" aria-pressed="true">Planta alta</button><button type="button" data-capa="muebles" aria-pressed="true">Muebles</button><button type="button" data-capa="arboles" aria-pressed="true">Nogales</button>
    <span class="sep"></span><button type="button" data-vista="esquina">Esquina</button><button type="button" data-vista="frente">Frente</button><button type="button" data-vista="jardin">Jardín</button><button type="button" data-vista="lado">Lado</button><button type="button" data-vista="planta">Desde arriba</button>
    <span class="sep"></span><button type="button" data-zoom="1" aria-label="Acercar">+</button><button type="button" data-zoom="-1" aria-label="Alejar">−</button>
  </div>
</div>
<p class="nota">Modelo generado desde las mismas plantas: muros de 20 y 12 cm con sus colores, ventanas con marco y cristal, puertas, escalera con barandal de cristal, muebles a escala, portal amueblado, cochera, banqueta y calle, patio con bodega y los nogales de los linderos. El visor dibuja con luz de sol, sombra sobre el terreno y contornos; se ve bien también en celular.</p>

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
           [("3d", "La casa en 3D"), ("conjunto", "Planta de conjunto"), ("plantas", "Planta baja y alta"), ("azotea", "Azotea y corte"), ("alzados", "Alzados"), ("guardado", "Dónde se guarda"), ("torreon", "Para Torreón")],
           head=CD.DEFS, script='<script>window.CASA3D=' + json.dumps(C3D.MODELO, separators=(",", ":")) + '</script><script src="/render/render3d.js"></script><script src="/casa/modelo3d.js"></script>')

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
       ("Luz", f"{f0(L_['kva'])} kVA", f"{L_['trafos'] + len(L_['especiales'])} transformadores"), ("Urbanización", mill(SV['URB']), f"${f0(SV['URB']/GROSS)}/m² de terreno"), ("Costo de operar", f"${f0(SV['cuota_casa'])}", f"por casa al mes; la cuota es ${f0(FI.CUOTA_CASA)}")])}
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
<p><b>Dónde van los pozos, la presión en cada esquina y lo que va debajo de la calle están dibujados en <a href="/agua/">Agua: pozos, red y presión</a>.</b></p>
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
<p>Son {mill(SV['URB'])}: ${f0(SV['URB']/GROSS)} por m² de terreno y ${f0(SV['URB']/N)} por lote, con {len(SV['partidas'])} partidas medidas sobre el plano. Cómo se paga la obra está en <a href="/numeros/">Números y fideicomiso</a>.</p>
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
    pagina("servicios", "Servicios", "09 · Servicios", "Calles, drenaje pluvial y sanitario, planta de tratamiento, agua potable, luz y fibra: especificaciones, cantidades y presupuesto, medidos sobre el plano.", cuerpo,
           [("niveles", "Terreno y niveles"), ("pluvial", "Drenaje pluvial"), ("sanitario", "Drenaje sanitario"), ("tratamiento", "Planta y red morada"), ("agua", "Agua potable"), ("luz", "Luz y fibra"), ("barda", "Barda y accesos"), ("presupuesto", "Presupuesto"), ("confirmar", "Por confirmar")],
           head='<link rel="stylesheet" href="/vendor/leaflet/leaflet.css">',
           script='<script>window.PLAN={datos:"/datos/",modo:"servicio",servicio:"pluvial",rueda:false};</script><script src="/vendor/leaflet/leaflet.js"></script><script src="/plan/plan.js"></script>')

# ======================= ILUMINACIÓN, PISTA Y GIMNASIO, 3D (sitio_extra.py) =======================
exec(open(os.path.join(AQUI, "sitio_extra.py"), encoding="utf-8").read())
exec(open(os.path.join(AQUI, "sitio_porque.py"), encoding="utf-8").read())
exec(open(os.path.join(AQUI, "sitio_agua.py"), encoding="utf-8").read())
exec(open(os.path.join(AQUI, "sitio_acceso.py"), encoding="utf-8").read())
exec(open(os.path.join(AQUI, "sitio_renders.py"), encoding="utf-8").read())
exec(open(os.path.join(AQUI, "sitio_hojas.py"), encoding="utf-8").read())
exec(open(os.path.join(AQUI, "sitio_inicio.py"), encoding="utf-8").read())

# ======================= NÚMEROS Y FIDEICOMISO =======================
def esquema_fideicomiso(con=False):
    """Quién aporta qué al fideicomiso y qué recibe. Cajas y flechas."""
    W, H = 1000, 580
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Cómo opera el fideicomiso" class="esquema">',
         '<defs><marker id="fe" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10z" fill="#000"/></marker></defs>']
    def caja(x, y, w, h, titulo, lineas, negra=False):
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{"#111" if negra else "#fff"}" stroke="#000" stroke-width="1.5"/>')
        o.append(f'<text x="{x + w/2}" y="{y + 24}" text-anchor="middle" font-size="15" font-weight="700" fill="{"#fff" if negra else "#000"}">{e(titulo)}</text>')
        for i, l in enumerate(lineas):
            o.append(f'<text x="{x + w/2}" y="{y + 46 + i*17}" text-anchor="middle" font-size="12" fill="{"#ddd" if negra else "#333"}">{e(l)}</text>')
    def flecha(x1, y1, x2, y2, texto, lado="arriba", dx=0):
        o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#000" stroke-width="1.6" marker-end="url(#fe)"/>')
        mx, my = (x1 + x2) / 2 + dx, (y1 + y2) / 2 + (-8 if lado == "arriba" else 16)
        for i, t in enumerate(texto.split("|")):
            o.append(f'<text x="{mx}" y="{my + i*15}" text-anchor="middle" font-size="12" font-weight="{"700" if i == 0 else "400"}" fill="#000" style="paint-order:stroke;stroke:#fff;stroke-width:4px">{e(t)}</text>')
    cx, cy, cw, ch = 350, 210, 300, 160
    caja(cx, cy, cw, ch, f"Fideicomiso {NOMBRE}", ["Banco fiduciario", "Recibe el terreno y el dinero de la obra,", "cobra cada venta y reparte", "según el contrato, sin discreción de nadie."], negra=True)
    caja(20, 230, 250, 120, "Dueño del terreno", [f"Aporta {ha(GROSS)} de nogalera.", "No pone un peso más.", f"Recibe {pct(X_DUENO)} de cada venta:", f"{mill(DUENO_TOTAL)} en {MOD['fin_ventas']/12:.1f} años."])
    caja(360, 20, 280, 120, "Inversionista", [f"Respalda la obra: {mill(OBRA_TOTAL)}.", f"Llega a tener puestos {mill(MOD['capital_pico'])}", f"(mes {next(f['mes'] for f in MOD['flujo'] if f['capital'] == MOD['capital_pico'])}). Recupera todo en el mes {MOD['m_recupera']}", f"con {TASA_INV_TXT} de rendimiento: {mill(MOD['rend'])}."])
    caja(730, 230, 250, 120, "Compradores", [f"{f0(N)} lotes urbanizados", f"y {f0(R['predio_comercial_m2'])} m² de comercio.", f"Pagan {mill(R['venta'])}", f"en {MOD['fin_ventas'] - 8} meses de ventas."])
    if con: caja(360, 430, 280, 120, "Nosotros · desarrollo, casas y operación", ["Ponemos el proyecto, la gestión y las ventas.", f"Cobramos en lotes ({MOD['lotes_desarrollador']:.0f}) y construimos las casas:", f"{CON['casas']:.0f} casas, {mill(CON['utilidad'])} de utilidad.", "Después operamos el agua y el mantenimiento."])
    else: caja(360, 430, 280, 120, "Nosotros · desarrollo y operación", ["Ponemos el proyecto, la gestión y las ventas.", f"Cobramos en lotes: {MOD['lotes_desarrollador']:.0f} lotes ({mill(MOD['desarrollador'])}).", "Después operamos la seguridad, el mantenimiento", f"y el agua (${f0(FI.CUOTA_CASA)} por casa + agua)."])
    flecha(270, 260, cx, 260, "terreno", "arriba"); flecha(cx, 320, 270, 320, f"{pct(X_DUENO)} de cada venta", "abajo")
    flecha(470, 140, 470, cy, "dinero para la obra", "arriba", dx=-70); flecha(530, cy, 530, 140, "capital + rendimiento", "arriba", dx=72)
    flecha(730, 260, cx + cw, 260, "pago de cada lote", "arriba"); flecha(cx + cw, 320, 730, 320, "lote escriturado", "abajo")
    flecha(470, 430, 470, cy + ch, "proyecto, gestión y ventas", "abajo", dx=-84); flecha(530, cy + ch, 530, 430, f"{MOD['lotes_desarrollador']:.0f} lotes", "abajo", dx=52)
    if con:
        o.append(f'<line x1="730" y1="300" x2="640" y2="470" stroke="#000" stroke-width="1.6" stroke-dasharray="5 4" marker-end="url(#fe)"/>')
        o.append(f'<text x="730" y="405" text-anchor="middle" font-size="12" font-weight="700" style="paint-order:stroke;stroke:#fff;stroke-width:4px">casa llave en mano</text><text x="730" y="420" text-anchor="middle" font-size="12" style="paint-order:stroke;stroke:#fff;stroke-width:4px">{mill(FI.PRECIO_CASA, 2)} · fuera del fideicomiso</text>')
    o.append(f'<text x="{W/2}" y="{H - 6}" text-anchor="middle" font-size="11.5" fill="#333">De cada venta: {pct(X_DUENO)} al dueño · {pct(FI.COMISION,0)} ventas y escrituras · el resto paga la obra y devuelve el capital</text>')
    o.append("</svg>")
    return "\n".join(o)

def grafica_flujo(con=False):
    """Flujo de efectivo mes a mes con los puntos de contacto."""
    fl = MOD["flujo"]; fin = fl[-1]["mes"]; W = 1000; izq, der = 64, 24
    X = lambda m: izq + (W - izq - der) * m / fin
    ALTO = 1000 if con else 840
    o = [f'<svg viewBox="0 0 {W} {ALTO}" role="img" aria-label="Flujo de efectivo del fideicomiso" class="flujo">']
    def panel(y0, h, titulo, vmax, unidad):
        o.append(f'<text x="{izq}" y="{y0 - 8}" font-size="12" font-weight="700" fill="#000">{e(titulo)}</text>')
        o.append(f'<line x1="{izq}" y1="{y0 + h}" x2="{W - der}" y2="{y0 + h}" stroke="#000" stroke-width="0.8"/>')
        for k in (0.5, 1.0):
            yy = y0 + h - h * k; o.append(f'<line x1="{izq}" y1="{yy:.1f}" x2="{W - der}" y2="{yy:.1f}" stroke="#ddd" stroke-width="0.6"/><text x="{izq - 6}" y="{yy + 4:.1f}" font-size="10" text-anchor="end" fill="#555">{unidad(vmax * k)}</text>')
        return lambda v: y0 + h - h * v / vmax
    # panel 1: lotes vendidos por mes
    y1, h1 = 112, 110; vmax1 = max(f["lotes"] for f in fl) * 1.15
    Y1 = panel(y1, h1, "Lotes vendidos por mes", vmax1, lambda v: f"{v:.0f}")
    bw = (W - izq - der) / fin * 0.7
    for f in fl:
        if f["lotes"]: o.append(f'<rect x="{X(f["mes"]) - bw/2:.1f}" y="{Y1(f["lotes"]):.1f}" width="{bw:.1f}" height="{y1 + h1 - Y1(f["lotes"]):.1f}" fill="#1a1a1a"/>')
    # panel 2: dinero acumulado
    y2, h2 = 272, 200
    acum_d = []; acum_v = []; td = tv = 0.0
    for f in fl: td += f["dueno"]; tv += f["ingreso"]; acum_d.append(td); acum_v.append(tv)
    vmax2 = max(acum_v) * 1.05
    Y2 = panel(y2, h2, "Dinero acumulado (millones de pesos)", vmax2, lambda v: f"{v/1e6:,.0f}")
    def linea(vals, cls, grueso=2, dash=""):
        o.append('<polyline points="' + " ".join(f"{X(f['mes']):.1f},{Y2(v):.1f}" for f, v in zip(fl, vals)) + f'" fill="none" stroke="#000" stroke-width="{grueso}"{f" stroke-dasharray={chr(34)}{dash}{chr(34)}" if dash else ""}/>')
    o.append('<polygon points="' + f"{X(0):.1f},{Y2(0):.1f} " + " ".join(f"{X(f['mes']):.1f},{Y2(f['capital']):.1f}" for f in fl) + f" {X(fin):.1f},{Y2(0):.1f}" + '" fill="rgba(0,0,0,0.14)"/>')
    linea(acum_v, "", 2.2); linea(acum_d, "", 2.2, "6 4"); linea([f["excedente"] for f in fl], "", 1.6, "2 3")
    ult = fl[-1]
    o.append(f'<text x="{X(fin) - 4}" y="{Y2(acum_v[-1]) - 6:.1f}" font-size="11" text-anchor="end" fill="#000" style="paint-order:stroke;stroke:#fff;stroke-width:4px">ventas cobradas · {mill(acum_v[-1])}</text>')
    o.append(f'<text x="{X(fin) - 4}" y="{Y2(acum_d[-1]) - 6:.1f}" font-size="11" text-anchor="end" fill="#000" style="paint-order:stroke;stroke:#fff;stroke-width:4px">cobrado por el dueño · {mill(acum_d[-1])} (línea punteada)</text>')
    mp = next(f for f in fl if f["capital"] == MOD["capital_pico"])
    o.append(f'<text x="{X(1):.1f}" y="{Y2(mp["capital"]) - 26:.1f}" font-size="11" fill="#000" style="paint-order:stroke;stroke:#fff;stroke-width:4px">capital del inversionista puesto en cada momento (sombreado) · pico {mill(mp["capital"])} en el mes {mp["mes"]}</text>')
    o.append(f'<text x="{X(fin) - 4}" y="{Y2(ult["excedente"]) - 6:.1f}" font-size="11" text-anchor="end" fill="#000" style="paint-order:stroke;stroke:#fff;stroke-width:4px">excedente para el desarrollador, en lotes · {mill(ult["excedente"])}</text>')
    # panel 3: cuotas
    y3, h3 = 522, 110; vmax3 = max(f["cuotas"] for f in fl) * 1.15
    Y3 = panel(y3, h3, "Mantenimiento y agua que cobra la operación, por mes (millones de pesos)", vmax3, lambda v: f"{v/1e6:,.1f}")
    o.append('<polygon points="' + f"{X(0):.1f},{Y3(0):.1f} " + " ".join(f"{X(f['mes']):.1f},{Y3(f['cuotas']):.1f}" for f in fl) + f" {X(fin):.1f},{Y3(0):.1f}" + '" fill="#1a1a1a"/>')
    o.append(f'<text x="{X(fin) - 4}" y="{Y3(ult["cuotas"]) - 6:.1f}" font-size="11" text-anchor="end" fill="#000" style="paint-order:stroke;stroke:#fff;stroke-width:4px">{f0(ult["casas"])} casas · {mill(ult["cuotas"], 2)} al mes</text>')
    yb = y3 + h3
    # panel 4 (con casas): casas que construimos y utilidad acumulada
    if con:
        y4, h4 = y3 + h3 + 60, 110; vmax4 = max(CON["entregas"]) * 1.15
        Y4 = panel(y4, h4, "Casas que construimos nosotros: entregas por mes · línea: utilidad acumulada (millones)", vmax4, lambda v: f"{v:.0f}")
        for m_, n_ in enumerate(CON["entregas"]):
            if n_: o.append(f'<rect x="{X(m_) - bw/2:.1f}" y="{Y4(n_):.1f}" width="{bw:.1f}" height="{y4 + h4 - Y4(n_):.1f}" fill="#1a1a1a"/>')
        vmaxU = max(CON["acum"]) * 1.1; YU = lambda v: y4 + h4 - h4 * v / vmaxU
        o.append('<polyline points="' + " ".join(f"{X(m_):.1f},{YU(v_):.1f}" for m_, v_ in enumerate(CON["acum"])) + '" fill="none" stroke="#000" stroke-width="2.2" stroke-dasharray="6 4"/>')
        o.append(f'<text x="{X(fin) - 4}" y="{YU(CON["acum"][-1]) + 14:.1f}" font-size="11" text-anchor="end" fill="#000" style="paint-order:stroke;stroke:#fff;stroke-width:4px">{CON["casas"]:.0f} casas · utilidad {mill(CON["utilidad"])}</text>')
        yb = y4 + h4
    # panel 5: lo nuestro, acumulado
    y5, h5 = yb + 60, 110
    nos = []; t_ = 0.0
    for m_, f in enumerate(fl): t_ += f["nosotros"] + (CON["util"][m_] if con else 0); nos.append(t_)
    sin_ = []; t_ = 0.0
    for f in fl: t_ += f["nosotros"]; sin_.append(t_)
    vmax5 = max(nos) * 1.12
    Y5 = panel(y5, h5, "Lo nuestro, acumulado (millones): lotes + margen de la operación" + (" + construcción de casas" if con else ""), vmax5, lambda v: f"{v/1e6:,.0f}")
    o.append('<polygon points="' + f"{X(0):.1f},{Y5(0):.1f} " + " ".join(f"{X(m_):.1f},{Y5(v_):.1f}" for m_, v_ in enumerate(nos)) + f" {X(fin):.1f},{Y5(0):.1f}" + '" fill="rgba(0,0,0,0.12)"/>')
    o.append('<polyline points="' + " ".join(f"{X(m_):.1f},{Y5(v_):.1f}" for m_, v_ in enumerate(nos)) + '" fill="none" stroke="#000" stroke-width="2.4"/>')
    if con: o.append('<polyline points="' + " ".join(f"{X(m_):.1f},{Y5(v_):.1f}" for m_, v_ in enumerate(sin_)) + '" fill="none" stroke="#000" stroke-width="1.4" stroke-dasharray="2 3"/>')
    o.append(f'<text x="{X(fin) - 4}" y="{Y5(nos[-1]) - 6:.1f}" font-size="11" text-anchor="end" fill="#000" style="paint-order:stroke;stroke:#fff;stroke-width:4px">a 10 años · {mill(nos[-1])}</text>')
    if con: o.append(f'<text x="{X(fin) - 4}" y="{Y5(sin_[-1]) + 14:.1f}" font-size="11" text-anchor="end" fill="#000" style="paint-order:stroke;stroke:#fff;stroke-width:4px">sin construir casas · {mill(sin_[-1])} (punteada)</text>')
    yb = y5 + h5
    # eje de meses
    for m in range(0, fin + 1, 12):
        o.append(f'<line x1="{X(m):.1f}" y1="{y1}" x2="{X(m):.1f}" y2="{yb}" stroke="#eee" stroke-width="0.6"/><text x="{X(m):.1f}" y="{yb + 16}" font-size="10" text-anchor="middle" fill="#555">{"mes " if m == 0 else ""}{m}</text>')
    for a in range(1, fin // 12 + 1): o.append(f'<text x="{X(a*12):.1f}" y="{yb + 30}" font-size="10.5" text-anchor="middle" fill="#000" font-weight="700">año {a}</text>')
    # puntos de contacto
    ventas = MOD["ventas"]; m_ini = min(ventas); pico_m = max(ventas, key=lambda m: (ventas[m], -m)); valle_m = next(m for m in sorted(ventas) if m > pico_m and ventas[m] < ventas[pico_m] * 0.6)
    m_mant = next(f["mes"] for f in fl if f["casas"] > 0); m_sube = next(f["mes"] for f in fl if f["casas"] >= N * 0.5)
    PUNTOS = [(0, "Se crea el fideicomiso"), (0, "Se aporta el terreno"), (8, "Se aporta para la obra"), (8, "Inicia la construcción"), (m_ini, "Inicia la venta"), (m_ini + 2, "Primeras ventas"),
              (pico_m, "Pico de ventas"), (valle_m, "Valle de ventas"), (33, "Termina la urbanización"), (m_mant, "Se empieza a cobrar mantenimiento"), (m_sube, "El mantenimiento sube"), (MOD["fin_ventas"], "Última venta")]
    if con: PUNTOS += [(m_ini + FI.ARRANQUE_CASA + FI.DURACION_CASA, "Primera casa entregada"), (CON["fin"], "Última casa entregada")]
    PUNTOS.sort(key=lambda t: t[0])
    ultimo = [-99, -99, -99, -99]
    for i, (m, t) in enumerate(PUNTOS, 1):
        fila = next(k for k in range(4) if X(m) - ultimo[k] >= 22); ultimo[fila] = X(m)
        y = y1 - 30 - fila * 22
        o.append(f'<line x1="{X(m):.1f}" y1="{y}" x2="{X(m):.1f}" y2="{yb}" stroke="#000" stroke-width="0.7" stroke-dasharray="3 3"/>')
        o.append(f'<circle cx="{X(m):.1f}" cy="{y}" r="9" fill="#000"/><text x="{X(m):.1f}" y="{y + 4}" font-size="10.5" font-weight="700" text-anchor="middle" fill="#fff">{i}</text>')
    o.append("</svg>")
    lista = "".join(f"<li><b>{i}.</b> {e(t)} <span class='nota'>· mes {m}</span></li>" for i, (m, t) in enumerate(PUNTOS, 1))
    return "\n".join(o), lista

TASA_INV_TXT = f"{FI.TASA_INV*100:.0f} % anual"

def numeros():
    grupos = {"Frente a parque (+8 %)": [p for p in LOTES if p["premio"] == "parque"], "Frente al bulevar (+5 %)": [p for p in LOTES if p["premio"] == "bulevar"], "Frente a calle": [p for p in LOTES if not p["premio"]]}
    filas_v = [(k, f0(len(v)), f0(sum(p["m2"] for p in v)), f"${f0(sum(p['m2'] * precio_lote(p) for p in v) / sum(p['m2'] for p in v))}", f"${f0(sum(p['m2'] * precio_lote(p) for p in v) / len(v))}", mill(sum(p["m2"] * precio_lote(p) for p in v), 1)) for k, v in grupos.items()]
    filas_v.append(("Comercio (súper y frente a Espinoza)", f"{R['lotes_comerciales']} + 1", f0(R["predio_comercial_m2"]), "$6,000", "", mill(VENTA_COM, 1)))
    svg_con, lista_con = grafica_flujo(True); svg_sin, lista_sin = grafica_flujo(False)
    VT = MOD["venta_total"]
    reparto = [("Dueño del terreno", f"{pct(X_DUENO)} de cada venta", mill(MOD["dueno_total"], 1), pct(MOD["dueno_total"] / VT)),
               ("Ventas, comisiones y escrituras", f"{pct(FI.COMISION, 0)} de cada venta", mill(MOD["comis_total"], 1), pct(MOD["comis_total"] / VT)),
               ("Proyecto ejecutivo y permisos", "al inicio", mill(FI.PROYECTO * R["venta"], 1), pct(FI.PROYECTO * R["venta"] / VT)),
               ("Obra: urbanización, club, parques, acceso, agua e iluminación", "por etapas, meses 8 a 33", mill(OBRA_TOTAL, 1), pct(OBRA_TOTAL / VT)),
               ("Rendimiento del inversionista", f"{TASA_INV_TXT} sobre lo que tiene puesto", mill(MOD["rend"], 1), pct(MOD["rend"] / VT)),
               ("Nosotros: pago en lotes", f"{MOD['lotes_desarrollador']:.0f} lotes al precio de lista", mill(MOD["desarrollador"], 1), pct(MOD["desarrollador"] / VT))]
    kp_base = [("Para el dueño", f"{pct(X_DUENO)} de cada venta", f"{mill(MOD['dueno_total'])} en {MOD['fin_ventas']/12:.1f} años · {mill(DUENO_TOTAL)} si todo se vendiera a precio de arranque"), ("Equivale hoy a", f"${f0(PRECIO_FID)}/m²", f"{mill(PRECIO_FID*GROSS)} de contado"),
               ("Venta de lotes", mill(MOD["venta_total"]), f"{f0(N)} lotes y el comercio, con la lista subiendo {pct(FI.ESCALON_ETAPA, 0)} por etapa"), ("Obra", mill(OBRA_TOTAL), "la respalda el inversionista"), ("Capital puesto al mismo tiempo", mill(MOD["capital_pico"]), f"como máximo, en el mes {next(f['mes'] for f in MOD['flujo'] if f['capital'] == MOD['capital_pico'])}")]
    kp_sin = kp_base + [("Nosotros", f"{MOD['lotes_desarrollador']:.0f} lotes", "y la operadora: seguridad, mantenimiento y agua"), ("Lo nuestro a 10 años", mill(NOS_SIN), f"lotes + operadora ({mill(OPER_ANIO)} al año en crucero)")]
    kp_con = kp_base + [("Casas que construimos", f"{CON['casas']:.0f}", f"{pct(FI.ADOPCION, 0)} de los lotes, llave en mano"), ("Utilidad de construcción", mill(CON["utilidad"]), f"{pct(CON['margen'], 0)} sobre {mill(CON['ingresos'])} de venta"), ("Lo nuestro a 10 años", mill(NOS_CON), "lotes + operación + casas")]
    cuerpo = f"""
<p class="frase" style="font-size:1.25rem"><b>${f0(PRECIO_FID)} por m² en fideicomiso: te damos el {pct(X_DUENO)} de cada venta.</b></p>
<div class="switch"><label><input type="checkbox" id="sw-casas" checked> <b>Con construcción de casas</b> <span>apágalo para ver el negocio solo con lotes; al dueño no le cambia nada</span></label></div>
<div class="v-con">{kpis(kp_con)}</div><div class="v-sin">{kpis(kp_sin)}</div>
<p>El dueño aporta el terreno a un fideicomiso con un banco y cobra el {pct(X_DUENO)} de cada lote conforme se vende: no pone dinero, no corre con la obra y no espera al final. Cada peso que entra se reparte según el contrato: primero el dueño, luego las ventas y la obra, luego el capital del inversionista con su rendimiento, y lo que sobra es la paga del desarrollador, en lotes.</p>
<div class="v-con"><p><b>Además construimos las casas.</b> El comprador que quiere su casa lista la encarga con nosotros: el Modelo Nogal con la fachada que le tocó, al precio de cualquier constructor de Torreón, pero con el molde, las compras y las cuadrillas ya montadas. Es un negocio aparte del fideicomiso y es el que más deja: ver <a href="#casas">Construir las casas</a>.</p></div>

<h2 id="esquema">Cómo opera</h2>
<figure><div class="dibujo"><div class="v-con">{esquema_fideicomiso(True)}</div><div class="v-sin">{esquema_fideicomiso(False)}</div></div><figcaption><b>Cuatro partes y un fiduciario.</b> El banco cobra cada venta y reparte sin que nadie tenga que confiar en nadie: el contrato dice a quién le toca qué.</figcaption></figure>

<h2 id="reparto">Qué recibe cada quien</h2>
{tabla([(e(a), e(b), c, d) for a, b, c, d in reparto], ["", "Cómo", "Importe", "De la venta de lotes"], "", ("<b>Venta de lotes</b>", f"lista de ${f0(PRECIO_BASE)}/m² en la etapa 1, +{pct(FI.ESCALON_ETAPA, 0)} por etapa", f"<b>{mill(MOD['venta_total'], 1)}</b>", "<b>100 %</b>"))}
<p class="nota">Si todo se vendiera al precio de arranque (${f0(PRECIO_BASE)}/m², sin subir la lista por etapa) la venta sería {mill(R['venta'])}, el dueño cobraría {mill(DUENO_TOTAL)} y a nosotros nos quedarían {ESCEN0['lotes']:.0f} lotes: la lista que sube por etapa es la que paga al desarrollador, y le da al dueño {mill(MOD['dueno_total'] - DUENO_TOTAL)} más. El <a href="/porque/">{pct(X_DUENO)}</a> está calculado sobre el precio de arranque, a favor del dueño.</p>
<div class="v-con">{tabla([("Nosotros: construcción de las casas", f"{CON['casas']:.0f} casas a {mill(FI.PRECIO_CASA, 2)}, fuera del fideicomiso", mill(CON['ingresos'], 1), f"utilidad {mill(CON['utilidad'], 1)} ({pct(CON['margen'], 0)})"),
   ("Nosotros: la operadora", f"cuota de ${f0(FI.CUOTA_CASA)} por casa y ${f0(FI.CUOTA_LOTE)} por lote, el agua por tarifa y la nuez, 10 años", mill(OPER_10, 1), f"{mill(OPER_ANIO, 1)} al año cuando está lleno")], ["Aparte del fideicomiso", "Cómo", "Margen", ""], "")}</div>
<ul>
<li><b>El dueño cobra primero y de cada venta.</b> Si el proyecto vende más caro, cobra más; si vende más despacio, cobra lo mismo pero más tarde. Nunca pone dinero.</li>
<li><b>El inversionista respalda toda la obra ({mill(OBRA_TOTAL)})</b>, pero como las ventas la van pagando, nunca llega a tener puestos más de {mill(MOD['capital_pico'])} al mismo tiempo. Recupera todo en el mes {MOD['m_recupera']} con {TASA_INV_TXT} de rendimiento sobre lo que tenga puesto cada mes.</li>
<li><b>Nosotros cobramos en lotes</b>, no en dinero: {MOD['lotes_desarrollador']:.0f} lotes al precio de lista, que se nos entregan al final, cuando el inversionista ya recuperó. Y nos quedamos con <b>la operadora</b>: seguridad 24 horas, mantenimiento de todo el fraccionamiento y el agua (pozos, cisterna, red y planta), cobrando ${f0(FI.CUOTA_CASA)} por casa habitada, ${f0(FI.CUOTA_LOTE)} por lote baldío y el agua por tarifa. Es un negocio en sí mismo: ver <a href="#operadora">La operadora</a>.</li>
</ul>

<h2 id="flujo">Flujo de efectivo a 10 años</h2>
<div class="v-con"><div class="scroll sec"><div class="dibujo">{svg_con}</div></div><ol class="puntos">{lista_con}</ol></div>
<div class="v-sin"><div class="scroll sec"><div class="dibujo">{svg_sin}</div></div><ol class="puntos">{lista_sin}</ol></div>
<p>Los lotes se venden conforme se urbanizan: arranque lento en la etapa 1, un pico cuando ya se ve el club y el bulevar, un valle a media obra y un cierre parejo. El modelo supone que el comprador paga el lote completo al escriturar (contado o crédito bancario); si se vende a plazos, el dueño cobra su {pct(X_DUENO)} de cada mensualidad.</p>

<h2 id="casas">Construir las casas</h2>
<p><b>La lógica.</b> El comprador del lote va a construir una casa de todas formas, y casi siempre la misma: el Modelo Nogal con la fachada asignada a su lote (el reglamento del fraccionamiento lo pide). Un constructor cualquiera le cobra ≈ ${f0(FI.PRECIO_M2_MERCADO)}/m² llave en mano y gana {pct(CON['margen_tipico'], 0)}, porque cada casa la empieza de cero. Nosotros ya tenemos el proyecto ejecutivo, el molde de aluminio para muros y losas, los precios de volumen con proveedores y cuadrillas que hacen la misma casa una y otra vez: nos cuesta ≈ ${f0(FI.COSTO_M2_NOSOTROS)}/m², {pct(1 - FI.COSTO_M2_NOSOTROS / FI.COSTO_M2_TIPICO, 0)} menos. Cobramos lo mismo que el mercado y ganamos <b>{pct(CON['margen'], 0)} de cada casa</b>. El comprador recibe la casa en 8 meses, con garantía y sin pelearse con un contratista; el fraccionamiento se construye parejo y rápido; el dueño del terreno no entra en esto.</p>
{tabla([("Casa Modelo Nogal", f"{FI.M2_CASA:.0f} m² en 2 plantas, con acabados medios-altos y la fachada del lote"), ("Precio al comprador", f"${f0(FI.PRECIO_M2_MERCADO)}/m² · {mill(FI.PRECIO_CASA, 2)} por casa (igual que el mercado)"),
        ("Costo de un constructor típico", f"${f0(FI.COSTO_M2_TIPICO)}/m² · margen {pct(CON['margen_tipico'], 0)}"), ("Nuestro costo", f"${f0(FI.COSTO_M2_NOSOTROS)}/m² · {mill(FI.COSTO_CASA, 2)} por casa · margen <b>{pct(CON['margen'], 0)}</b> ({mill(FI.MARGEN_CASA, 2)} por casa)"),
        ("Cuántas", f"{pct(FI.ADOPCION, 0)} de los compradores la encargan con nosotros: <b>{CON['casas']:.0f} casas</b> (el resto construye por su cuenta con los mismos planos)"), ("Cómo se paga", f"{pct(FI.PAGO_CASA[0], 0)} de anticipo, {pct(FI.PAGO_CASA[1], 0)} en estimaciones durante los {FI.DURACION_CASA} meses de obra y {pct(FI.PAGO_CASA[2], 0)} a la entrega: la casa se paga sola, no necesita capital"),
        ("Ritmo", f"arranca {FI.ARRANQUE_CASA} meses después de la venta del lote; en el pico hay {CON['pico_obra']:.0f} casas en obra a la vez (≈ 8 frentes de 25 casas)"), ("Total", f"<b>{mill(CON['ingresos'])} de venta, {mill(CON['costos'])} de costo, {mill(CON['utilidad'])} de utilidad</b> entre el mes {min(MOD['ventas']) + FI.ARRANQUE_CASA} y el {CON['fin']}")],
       ["", ""], "spec")}
<div class="v-con">
<h3>Con y sin: lo nuestro a 10 años</h3>
{tabla([("Lotes que nos tocan del fideicomiso", mill(MOD['desarrollador']), mill(MOD['desarrollador'])), ("Margen de la operación (agua y mantenimiento), 10 años", mill(OPER_10), mill(OPER_10)), ("Construcción de las casas", "—", mill(CON['utilidad']))],
       ["", "Sin construir casas", "Construyendo las casas"], "", ("<b>Total</b>", f"<b>{mill(NOS_SIN)}</b>", f"<b>{mill(NOS_CON)}</b>"))}
<p>Construir las casas multiplica por {NOS_CON / NOS_SIN:.0f} lo que deja el proyecto para nosotros, sin cambiar un peso de lo que recibe el dueño ni el inversionista. Lo que pide a cambio es una constructora de verdad: {CON['pico_obra']:.0f} casas en obra al mismo tiempo en el pico, compras centralizadas y control de calidad de serie.</p>
</div>
<div class="v-sin"><p class="nota">Con el interruptor apagado, el proyecto es solo lotes: nos quedan los {MOD['lotes_desarrollador']:.0f} lotes y la operación. Enciéndelo para ver qué pasa si además construimos las casas.</p></div>

<h2 id="ventas">De dónde salen las ventas</h2>
<p>El lote se vende urbanizado, sin casa, a <b>${f0(PRECIO_BASE)}/m²</b> para 300 m² en la etapa 1 (baja $2 por cada m² de más), con 8 % más frente a parque y 5 % más frente al bulevar. El comercio, a $6,000/m². Son precios de 2026 comparables con lotes urbanizados de Torreón ($3,500–3,750/m²): la etapa 1 arranca por debajo del mercado para vender rápido, y <b>la lista sube {pct(FI.ESCALON_ETAPA, 0)} en cada etapa</b> ({" → ".join(f"${f0(x)}" for x in LISTA)}), porque cada etapa se vende con más fraccionamiento construido. Eso suma {pct(MOD['escalacion'], 1)} a la venta ({mill(MOD['venta_total'] - R['venta'])} más), y el dueño cobra su {pct(X_DUENO)} también de ese extra. La tabla va a precios de etapa 1; la lista completa está en <a href="/comercializador/#lista">Para el comercializador</a>.</p>
{tabla(filas_v, ["Lotes", "Cuántos", "m²", "Precio por m²", "Precio por lote", "Venta"], "", ("<b>Total</b>", f"<b>{f0(N)}</b>", f"<b>{f0(R['vendible_m2'] + R['predio_comercial_m2'])}</b>", "", "", f"<b>{mill(R['venta'], 1)}</b>"))}
<h3>La obra</h3>
{tabla([(e(k), mill(v, 1)) for k, v in SV['por_servicio'].items()] + [(e(k), mill(v, 1)) for k, v in AMEN.items()] + [("Iluminación de paisaje y acceso", mill(PAISAJE, 1)), (f"Reubicar {R['reubicar']} nogales", mill(REUBICA, 1))],
       ["Concepto", "Importe"], "compacta", ("<b>Total de la obra</b>", f"<b>{mill(OBRA_TOTAL, 1)}</b>"))}
<p>El detalle partida por partida está en <a href="/servicios/#presupuesto">Servicios</a>.</p>

<h2 id="porque">De dónde sale el {pct(X_DUENO)}</h2>
<p>Es el porcentaje en el que el dueño y el proyecto ganan lo mismo frente a una venta de contado, y el máximo que el proyecto aguanta con la obra completa dejando 20 % de margen. Al dueño, esperar un año por su dinero le cuesta {pct(FID['R_DUENO'], 0)}; al proyecto, tener el dinero puesto un año le cuesta {pct(FID['R_PROY'], 0)}: por esa diferencia los dos ganan con el fideicomiso. Cada $100/m² más de precio son {pct(2*100*GROSS/(FID['VPd']+FID['VPp']), 2)} más de las ventas para el dueño, que salen del margen del proyecto. La argumentación completa, con el mercado, el calendario de cobro y lo que pasa si se pide más: <a href="/porque/">Por qué $522 por m²</a>.</p>

<h2 id="operadora">La operadora: seguridad, mantenimiento y agua como negocio</h2>
{operadora_html()}
<p class="nota">Cuentas en pesos de 2026, antes de impuestos. El fideicomiso de desarrollo lo administra un banco: el dueño aporta el terreno libre de gravámenes, el inversionista pone la obra, nosotros el proyecto, la gestión y las ventas, y el banco le paga a cada quien su parte de cada cobro. Todo sale de <code>pipeline/scripts/n6_fideicomiso.py</code>.</p>
"""
    pagina("numeros", "Números y fideicomiso", "13 · Números y fideicomiso", f"El dueño aporta el terreno y cobra el {pct(X_DUENO)} de cada venta; el inversionista pone la obra; nosotros cobramos en lotes y operamos el agua y el mantenimiento.", cuerpo,
           [("esquema", "Cómo opera"), ("reparto", "Qué recibe cada quien"), ("flujo", "Flujo a 10 años"), ("casas", "Construir las casas"), ("ventas", "Ventas y obra"), ("porque", f"De dónde sale el {pct(X_DUENO)}"), ("operadora", "La operadora")],
           script='<script>(function(){var s=document.getElementById("sw-casas"),d=document.querySelector(".doc");function f(){d.classList.toggle("con",s.checked);d.classList.toggle("sin",!s.checked);}s.addEventListener("change",f);if(location.hash==="#sin")s.checked=false;f();})();</script>')

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
<li><b>Sentarse con el dueño</b> con la propuesta: ${f0(PRECIO_FID)}/m² en fideicomiso, {pct(X_DUENO)} de cada venta. Ver <a href="/numeros/">Números y fideicomiso</a>.</li>
<li><b>Uso de suelo:</b> consulta en Desarrollo Urbano de Torreón sobre densidad, restricciones, áreas de donación y la conexión a la Calzada José Vasconcelos.</li>
<li><b>Estudios de campo:</b> topografía a cada 10 m, mecánica de suelos y pruebas de infiltración.</li>
<li><b>Factibilidades</b> de SIMAS (o permiso de planta propia y reúso), CFE y Protección Civil.</li>
<li><b>Proyecto ejecutivo</b> de lotificación, vialidades y redes, con este anteproyecto como base, y licencia.</li>
<li><b>Imagen y ventas:</b> renders (vista de día y de noche, la cuadra, la casa muestra), nombre definitivo y oficina de ventas en el acceso.</li>
</ol>
<p class="nota">El calendario es un supuesto de trabajo con el ritmo de ventas del modelo ({TE.RITMO} lotes al mes). Los plazos de trámites dependen del municipio y de los organismos.</p>
"""
    pagina("etapas", "Etapas y siguientes pasos", "17 · Etapas y siguientes pasos", "Cuatro etapas que crecen desde el acceso, un calendario de obra y ventas, y la lista de lo que hay que confirmar para arrancar.", cuerpo,
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
                ("servicios.geojson", "Redes: drenaje pluvial y sanitario, agua, agua tratada, transformadores, cruces elevados, salida de emergencia."), ("luces.json", "Los puntos de luz, por tipo, con clave y zona."), ("luminarias.csv", "Inventario de luminarias: clave, tipo, dónde está, coordenadas, altura y potencia."),
                ("servicios.json", "Todos los cálculos de servicios, partidas y cuota."), ("especificaciones.csv", "Hoja de especificaciones y presupuesto de urbanización, partida por partida."), ("etapas.json", "Etapa de construcción de cada lote."),
                ("nogaleras.geojson", "Todas las nogaleras de La Laguna, con superficie, estado y precio estimado."), ("nogaleras.csv", "Lo mismo en tabla."), ("base.geojson", "Fondo vectorial de La Laguna (OpenStreetMap vía Overture).")]
    filas = []
    for n, d in archivos:
        p = os.path.join(DAT, n); kb = os.path.getsize(p) / 1024 if os.path.exists(p) else 0
        filas.append((f'<a href="/datos/{n}" download>{n}</a>', e(d), f"{kb:,.0f} KB"))
    cuerpo = f"""
<p>Todo lo que muestra el sitio sale de estos archivos, y estos salen del código en <code>pipeline/</code> del repositorio. Coordenadas en WGS 84 (longitud, latitud). Cifras en pesos de 2026 sin IVA.</p>
{tabla(filas, ["Archivo", "Qué tiene", "Tamaño"], "spec")}
<h2 id="prospectos">Prospectos de la página del cliente</h2>
<p>Cada persona que deja sus datos en <a href="/inicio/">/inicio/</a> queda guardada en la base de datos del Worker de Cloudflare (un Durable Object con SQLite: no hay nada que crear ni pagar). Se descargan con una clave: mientras no haya secretos en el Worker, la clave es <b>123</b>; cuando pongas el secreto <code>ADMIN_CLAVE</code> (o <code>RENDER_CLAVE</code>), manda ese.</p>
<ul>
<li>Excel: <a href="/api/prospectos?clave=123&amp;formato=csv"><code>https://nogalera.capitaltorreon.com/api/prospectos?clave=123&amp;formato=csv</code></a> (abre o descarga un CSV con fecha, nombre, celular, correo, primera o segunda casa, crédito, rapidez, mensaje, ciudad y página).</li>
<li>JSON: la misma dirección sin <code>&amp;formato=csv</code>.</li>
<li>Aviso por correo de cada prospecto nuevo: poner en el Worker los secretos <code>RESEND_API_KEY</code> (cuenta de Resend) y <code>AVISO_CORREO</code> (uno o varios correos separados por coma); opcional <code>AVISO_DESDE</code>.</li>
</ul>
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
    for fn in (resumen, terreno, plan, calles, acceso, casa, fachadas, renders, servicios, agua, iluminacion, pista, numeros, porque, inversionista, comercializador, etapas, nogaleras, datos, inicio): fn()
