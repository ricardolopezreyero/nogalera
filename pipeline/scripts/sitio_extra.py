# Secciones nuevas de sitio.py: iluminación (plano y detalles), pista y gimnasio, modelo 3D. Se ejecuta dentro de sitio.py (exec), con todo su espacio de nombres.
LUZ = json.load(open(f"{DAT}/luces.json"))
LUCES = [dict(u=uv(p[0], p[1])[0], v=uv(p[0], p[1])[1], tipo=LUZ["tipos"][p[2]], id=p[3], zona=p[4], lon=p[0], lat=p[1]) for p in LUZ["p"]]
ALTURA_L = {"calle": 6.0, "bulevar": 8.0, "acceso": 9.0, "peatonal": 3.5, "baliza": 0.9, "nogal": 0.0, "estac": 6.0, "cancha": 6.0, "caseta": 3.0, "letrero": 0.6}
# nivel de iluminación aproximado: lúmenes (130 lm/W) × factor de utilización y mantenimiento 0.35 ÷ área que atiende cada luminaria
AREA_L = {"calle": 25.4 * 11, "bulevar": 30 * 30, "acceso": 14 * 15, "peatonal": 30 * 4, "baliza": 20 * 3, "estac": 20 * 10, "cancha": 670 / 6}
LUX_NORMA = {"calle": "4–6 lux (calle local residencial, IES RP-8 / NOM-013-ENER)", "bulevar": "6–9 lux (colectora con camellón)", "acceso": "20–30 lux (zona de control y casetas)", "peatonal": "5 lux (andadores)", "baliza": "3–5 lux (pista deportiva de uso nocturno)", "estac": "10 lux (estacionamiento abierto)", "cancha": "200–300 lux (tenis y pádel recreativos)", "nogal": "sin nivel: ilumina la copa desde abajo", "caseta": "50 lux dentro, con el letrero y las plumas visibles", "letrero": "letrero retroiluminado"}
def lux(t): return LZ["tipos"][t]["watts"] * 130 * 0.35 / AREA_L[t] if t in AREA_L else None

def simbolo_luz(X, Y, l, S=1.0, con_id=False):
    x, y = X(l["u"]), Y(l["v"]); t = l["tipo"]; o = ""
    if t == "calle": o = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{3.2*S:.1f}" fill="#000"/>'
    elif t == "bulevar": o = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{4.4*S:.1f}" fill="#000"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{1.6*S:.1f}" fill="#fff"/>'
    elif t == "acceso": o = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{5*S:.1f}" fill="#000"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{2.6*S:.1f}" fill="#fff"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{1*S:.1f}" fill="#000"/>'
    elif t == "nogal": o = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{3*S:.1f}" fill="#fff" stroke="#000" stroke-width="{1.1*S:.1f}"/>'
    elif t == "baliza": o = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.5*S:.1f}" fill="#666"/>'
    elif t == "peatonal": o = f'<rect x="{x-2.4*S:.1f}" y="{y-2.4*S:.1f}" width="{4.8*S:.1f}" height="{4.8*S:.1f}" fill="#000"/>'
    elif t in ("estac", "cancha"): o = f'<polygon points="{x:.1f},{y-3.6*S:.1f} {x+3.2*S:.1f},{y+2.2*S:.1f} {x-3.2*S:.1f},{y+2.2*S:.1f}" fill="#000"/>'
    elif t == "caseta": o = f'<rect x="{x-4*S:.1f}" y="{y-4*S:.1f}" width="{8*S:.1f}" height="{8*S:.1f}" fill="#000"/><rect x="{x-1.6*S:.1f}" y="{y-1.6*S:.1f}" width="{3.2*S:.1f}" height="{3.2*S:.1f}" fill="#fff"/>'
    elif t == "letrero": o = f'<rect x="{x-5*S:.1f}" y="{y-2*S:.1f}" width="{10*S:.1f}" height="{4*S:.1f}" fill="#000"/>'
    if con_id: o += f'<text x="{x+5*S:.1f}" y="{y-4*S:.1f}" font-size="{7.5*S:.1f}" fill="#000" style="paint-order:stroke;stroke:#fff;stroke-width:3px">{e(l["id"])}</text>'
    return o

LEYENDA_LUZ = [("calle", "Arbotante de calle, 6 m"), ("bulevar", "Arbotante doble del bulevar, 8 m"), ("acceso", "Poste del acceso, 9 m"), ("peatonal", "Poste peatonal, 3.5 m"), ("nogal", "Foco de piso a un nogal"), ("baliza", "Baliza de la pista"), ("estac", "Poste de estacionamiento / proyector de cancha"), ("caseta", "Luz de caseta"), ("letrero", "Letrero iluminado")]
def leyenda_luz(X0, Y0, S=1.0):
    o = []
    for i, (t, nombre) in enumerate(LEYENDA_LUZ):
        y = Y0 + i * 16 * S; l = dict(u=0, v=0, tipo=t)
        o.append(simbolo_luz(lambda u: X0 + 8, lambda v: y, l, S))
        o.append(f'<text x="{X0 + 20:.1f}" y="{y + 3.5:.1f}" font-size="{10*S:.1f}" fill="#000">{e(nombre)}</text>')
    return "".join(o)

def plano_luces_svg():
    PAD = 70; ancho_px = 1400; S = (ancho_px - 2 * PAD) / (U1 - U0); W = ancho_px; H = (V1 - V0) * S + 2 * PAD + 40
    X = lambda u: PAD + (u - U0) * S; Y = lambda v: PAD + (V1 - v) * S
    def pts(f): return " ".join(f"{X(u):.1f},{Y(v):.1f}" for u, v in (uv(*c) for c in f["geometry"]["coordinates"][0]))
    o = [f'<svg viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="Plano de alumbrado" class="plano">']
    for capa in ["pista", "vial", "bulevar", "arroyo", "comunal", "plaza_acceso", "ptar", "parque", "lote", "comercio", "estacionamiento", "salon", "tenis", "padel"]:
        for f in FC["features"]:
            if f["properties"]["capa"] == capa and f["geometry"]["type"] == "Polygon":
                o.append(f'<polygon points="{pts(f)}" fill="{"#fff" if capa == "lote" else "#ececec" if capa in ("pista", "plaza_acceso") else "#d6d6d6" if capa in ("vial", "bulevar", "arroyo", "estacionamiento") else "#c4c4c4"}" stroke="{"#ddd" if capa == "lote" else "none"}" stroke-width="0.3"/>')
    for a in ARB:
        if not a[2]: u, v = uv(a[0], a[1]); o.append(f'<circle cx="{X(u):.1f}" cy="{Y(v):.1f}" r="0.9" fill="#b0b0b0"/>')
    o.append(f'<polygon points="{pts(LIM)}" class="pm-limite"/>')
    for l in sorted(LUCES, key=lambda l: l["tipo"] != "nogal"): o.append(simbolo_luz(X, Y, l, 0.75))
    for nombre in R["calles_largas"]: o.append(f'<text x="{X(U0)-8:.1f}" y="{Y(_v_de_calle(nombre))+4:.1f}" class="pm-rotulo" text-anchor="end">{e(nombre)}</text>')
    for nombre in R["calles_cruce"]: o.append(f'<text x="{X(_u_de_cruce(nombre)):.1f}" y="{Y(V1)-10:.1f}" class="pm-rotulo cruce" text-anchor="middle">{e(nombre)}</text>')
    # leyenda en dos columnas abajo
    for i, (t, nombre) in enumerate(LEYENDA_LUZ):
        col, fila = i % 3, i // 3; x0 = PAD + col * 380; y = H - 58 + fila * 17
        o.append(simbolo_luz(lambda u: x0 + 8, lambda v: y, dict(u=0, v=0, tipo=t), 1.0)); o.append(f'<text x="{x0 + 22:.1f}" y="{y + 3.5:.1f}" font-size="10.5" fill="#000">{e(nombre)}</text>')
    o.append(f'<line x1="{W - PAD - 200*S:.1f}" y1="{H-40:.1f}" x2="{W - PAD:.1f}" y2="{H-40:.1f}" stroke="#000" stroke-width="3"/><text x="{W - PAD - 100*S:.1f}" y="{H-46:.1f}" class="pm-etiqueta" text-anchor="middle">200 m</text>')
    o.append("</svg>")
    return "\n".join(o)

def detalle_luz(u0, v0, u1, v1, titulo, S=4.0, notas=()):
    """Zoom de una zona: lotes, calles, nogales y cada luminaria con su clave."""
    PAD = 10; W = (u1 - u0) * S + 2 * PAD; H = (v1 - v0) * S + 2 * PAD + 22
    X = lambda u: PAD + (u - u0) * S; Y = lambda v: PAD + 22 + (v1 - v) * S
    def pts(f): return " ".join(f"{X(u):.1f},{Y(v):.1f}" for u, v in (uv(*c) for c in f["geometry"]["coordinates"][0]))
    o = [f'<svg viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="{e(titulo)}" class="plano"><text x="{PAD}" y="15" class="t">{e(titulo)}</text><clipPath id="cl{abs(hash(titulo))%99999}"><rect x="{PAD}" y="{PAD+22}" width="{(u1-u0)*S:.1f}" height="{(v1-v0)*S:.1f}"/></clipPath><g clip-path="url(#cl{abs(hash(titulo))%99999})">']
    o.append(f'<rect x="{PAD}" y="{PAD+22}" width="{(u1-u0)*S:.1f}" height="{(v1-v0)*S:.1f}" fill="#f4f4f4"/>')
    for capa in ["vial", "bulevar", "arroyo", "sendero", "comunal", "plaza_acceso", "parque", "lote", "comercio", "estacionamiento", "salon", "tenis", "padel", "isla", "caseta"]:
        for f in FC["features"]:
            if f["properties"]["capa"] != capa or f["geometry"]["type"] != "Polygon": continue
            cs = [uv(*c) for c in f["geometry"]["coordinates"][0]]
            if max(c[0] for c in cs) < u0 or min(c[0] for c in cs) > u1 or max(c[1] for c in cs) < v0 or min(c[1] for c in cs) > v1: continue
            fill = {"lote": "#fff", "vial": "#d9d9d9", "bulevar": "#d9d9d9", "arroyo": "#bdbdbd", "sendero": "#e9e9e9", "comunal": "#e3e3e3", "plaza_acceso": "#ececec", "parque": "#cfcfcf", "comercio": "#fff", "estacionamiento": "#c4c4c4", "salon": "#555", "tenis": "#777", "padel": "#777", "isla": "#fff", "caseta": "#000"}[capa]
            o.append(f'<polygon points="{pts(f)}" fill="{fill}" stroke="#999" stroke-width="0.5"/>')
    for a in ARB:
        u, v = uv(a[0], a[1])
        if u0 - 5 < u < u1 + 5 and v0 - 5 < v < v1 + 5:
            r = (0.32 * a[3] + 1.2) * S
            o.append(f'<circle cx="{X(u):.1f}" cy="{Y(v):.1f}" r="{r:.1f}" fill="rgba(0,0,0,0.05)" stroke="#888" stroke-width="0.5" stroke-dasharray="2 2"/><circle cx="{X(u):.1f}" cy="{Y(v):.1f}" r="{1.2*S/2:.1f}" fill="{"#fff" if a[2] else "#000"}" stroke="#000" stroke-width="0.6"/>')
    for f in _rot:
        u, v = uv(*f["geometry"]["coordinates"])
        if u0 < u < u1 and v0 < v < v1: o.append(f'<text x="{X(u):.1f}" y="{Y(v)+3:.1f}" class="pm-rotulo{" cruce" if f["properties"]["eje"] == "cruce" else ""}" text-anchor="middle" font-size="9">{e(f["properties"]["nombre"])}</text>')
    for l in LUCES:
        if u0 < l["u"] < u1 and v0 < l["v"] < v1: o.append(simbolo_luz(X, Y, l, 1.2, con_id=True))
    o.append("</g>")
    for i, n in enumerate(notas): o.append(f'<text x="{W - PAD:.1f}" y="{PAD + 36 + i*12:.1f}" font-size="9.5" fill="#000" text-anchor="end" style="paint-order:stroke;stroke:#fff;stroke-width:3px">{e(n)}</text>')
    o.append(f'<line x1="{X(u0)+10:.1f}" y1="{H-8:.1f}" x2="{X(u0)+10+20*S:.1f}" y2="{H-8:.1f}" stroke="#000" stroke-width="2"/><text x="{X(u0)+10+10*S:.1f}" y="{H-12:.1f}" font-size="9" text-anchor="middle">20 m</text>')
    o.append("</svg>")
    return "\n".join(o)

def iluminacion():
    t = LZ["tipos"]; orden = ["calle", "bulevar", "nogal", "baliza", "peatonal", "acceso", "caseta", "letrero", "estac", "cancha"]
    v_enc = _v_de_calle("Encino"); u_g, u_gr = _u_de_cruce("Garza"), _u_de_cruce("Grulla"); v_bul = _v_de_calle("Nogal")
    ua, va = uv(*_acc_lonlat)
    parque = next(f for f in FC["features"] if f["properties"]["capa"] == "parque")
    pcs = [uv(*c) for c in parque["geometry"]["coordinates"][0]]; pu0, pu1, pv0, pv1 = min(c[0] for c in pcs), max(c[0] for c in pcs), min(c[1] for c in pcs), max(c[1] for c in pcs)
    reglas = [("Arbotantes de calle (C)", f"En la banqueta, a 4.6 m del eje de la calle (1.1 m adentro de la guarnición), uno cada 25.4 m (dos lotes), alternando acera: a tresbolillo. Cada uno se corre hasta ±4 m para quedar lo más lejos posible de los troncos. En cada cruce van dos en esquinas opuestas (noroeste y sureste), a 7 m del eje de la transversal: el peatón cruza con luz. {t['calle']['n']} en total."),
              ("Bulevar Nogal (B y P)", f"Arbotante doble de 8 m en el eje del camellón cada 30 m ({t['bulevar']['n']}) y un poste peatonal de 3.5 m en el sendero a la mitad entre dos dobles. Cada nogal de las dos banquetas lleva su foco de piso."),
              ("Focos de piso a los nogales (N)", f"Uno por nogal en el bulevar, los parques, el club y la plaza de acceso: {t['nogal']['n']}. Empotrado en el piso a 1.2 m del tronco del lado de la calle, LED 12 W, 2700 K, óptica de 25° apuntando a la copa, con rejilla antideslumbrante. Se apagan a medianoche."),
              ("Pista (Z)", f"Baliza de 90 cm cada 20 m por el lado de afuera de la pista, a 50 cm del borde, luz hacia abajo y hacia la pista: {t['baliza']['n']}. El km 0 está frente al acceso."),
              ("Parques (N y P)", "Foco de piso a cada nogal y postes peatonales cada 30 m en la orilla, mirando hacia adentro. Sin postes altos: la luz viene de los árboles."),
              ("Acceso (A, K y L)", f"Postes de 9 m en las dos orillas cada 14 m y en las islas, desde la calzada hasta pasando las plumas ({t['acceso']['n']}); luz en las dos casetas y las plumas; letrero retroiluminado en los dos muros de entrada. Es la zona más iluminada: la cámara lee placas y el guardia ve caras."),
              ("Estacionamientos y canchas (E y Q)", f"Poste de 6 m al centro cada 20 m en los tres estacionamientos ({t['estac']['n']}); 6 proyectores en la cancha de tenis y 4 en cada pádel ({t['cancha']['n']}), solo encendidos cuando se usan, con apagado automático."),
              ("Control", "Todo en circuitos subterráneos por los ductos de la banqueta, con fotocelda y reloj astronómico; los circuitos de nogales y canchas con horario propio. Cada luminaria tiene clave (en el mapa y en el inventario) para reportar fallas por la app del fraccionamiento.")]
    filas = []
    for k in orden:
        lx = lux(k); filas.append((e(t[k]['nombre']), f0(t[k]['n']), f"{ALTURA_L[k]:.1f} m" if ALTURA_L[k] else "piso", f"{t[k]['watts']} W · {t[k]['watts']*130:,} lm", f"≈ {lx:.0f} lux" if lx else "—", e(LUX_NORMA[k]), f"${f0(t[k]['costo'])}"))
    cuerpo = f"""
{kpis([("Puntos de luz", f0(LZ['puntos']), "cada uno con clave y coordenadas"), ("Nogales iluminados", f0(LZ['nogales_iluminados']), "desde el piso, en bulevar, parques, club y acceso"), ("Inversión", mill(LZ['inversion']), f"{mill(LZ['inversion_calles'])} de calle + {mill(LZ['inversion_paisaje'])} de paisaje"),
       ("Energía", f"{f0(LZ['kwh_anual'])} kWh/año", f"${f0(LZ['energia_anual'])} al año"), ("Mantenimiento", f"${f0(LZ['mantenimiento_anual'])}", "al año, 4 % de la inversión"), ("Por casa", f"${f0(LZ['cuota_casa_mes'])}", "al mes, dentro de la cuota")])}
<p class="descargas"><a href="/datos/luminarias.csv" download>Descargar el inventario de luminarias (CSV)</a><a href="/plan/#noche">Ver la vista de noche en el mapa</a></p>
<p><b>Luz cálida y baja, y los nogales como protagonistas.</b> Las calles se iluminan con arbotantes de 6 m puestos entre los árboles; en el bulevar, los parques, el club y la plaza de acceso cada nogal se ilumina desde abajo, de modo que de noche se ve la arboleda. El acceso es la zona más iluminada; la pista lleva balizas al ras del piso. Todo a 2700–3000 K, con ópticas que alumbran hacia abajo sin deslumbrar ni meterse a las ventanas.</p>
<h2 id="plano">Dónde va cada luz</h2>
<figure><div class="dibujo">{plano_luces_svg()}</div><figcaption><b>Plano de alumbrado: las {f0(LZ['puntos'])} luminarias en su lugar.</b> Cada una tiene una clave (C-001, B-012, N-204…) con sus coordenadas en el <a href="/datos/luminarias.csv">inventario</a>; en el <a href="/plan/#noche">mapa</a>, al tocar un punto, sale su clave y dónde está.</figcaption></figure>
<h2 id="detalles">Detalles por zona</h2>
<div class="dos">
<figure><div class="dibujo">{detalle_luz(u_g - 12, v_enc - 24, u_gr + 12, v_enc + 24, "Una cuadra de Encino, entre Garza y Grulla", 4.2, ("arbotantes a tresbolillo cada 25.4 m", "esquinas noroeste y sureste en cada cruce", "ninguno a menos de 2.5 m de un tronco"))}</div><figcaption><b>Calle tipo.</b> Los arbotantes van en la banqueta, alternando acera, y se corren para no quedar junto a un nogal. En cada cruce, dos esquinas opuestas.</figcaption></figure>
<figure><div class="dibujo">{detalle_luz(u_g - 10, v_bul - 26, u_g + 150, v_bul + 26, "Bulevar Nogal, un tramo de 160 m", 4.2, ("arbotante doble cada 30 m en el camellón", "poste peatonal entre cada dos, en el sendero", "foco de piso a cada nogal de las banquetas"))}</div><figcaption><b>Bulevar.</b> Tres capas de luz: la alta de los arbotantes dobles, la baja del sendero y los nogales iluminados desde el piso.</figcaption></figure>
<figure><div class="dibujo">{detalle_luz(ua - 70, va - 6, ua + 70, va + 100, "El acceso", 4.2, ("postes de 9 m en las orillas cada 14 m y en las islas", "casetas, plumas y letrero iluminados", "nogales de la plaza con foco de piso"))}</div><figcaption><b>Acceso.</b> De la calzada a las plumas, 20 a 30 lux: se ven las placas, las caras y el letrero desde lejos.</figcaption></figure>
<figure><div class="dibujo">{detalle_luz(pu0 - 15, pv0 - 15, pu1 + 15, pv1 + 15, parque["properties"]["nombre"], 4.2, ("foco de piso a cada nogal", "postes peatonales de 3.5 m cada 30 m en la orilla", "sin postes altos adentro"))}</div><figcaption><b>Parque.</b> La luz sale de los árboles; en la orilla, postes bajos cada 30 m para los andadores.</figcaption></figure>
</div>
<h2 id="reglas">Las reglas de colocación</h2>
<ul>{"".join(f"<li><b>{e(a)}</b> {e(b)}</li>" for a, b in reglas)}</ul>
<h2 id="cuenta">Cuántas, de qué tipo y cuánta luz dan</h2>
{tabla(filas, ["Luminaria", "Cuántas", "Altura", "Potencia · flujo", "Nivel", "Referencia", "Costo instalado"], "", ("<b>Total</b>", f"<b>{f0(LZ['puntos'])}</b>", "", f"{f0(LZ['kwh_anual'])} kWh al año", "", "", f"<b>${f0(LZ['inversion'])}</b>"))}
<p>El nivel es el promedio aproximado sobre el área que atiende cada luminaria (LED de 130 lm/W, factor de utilización y mantenimiento de 0.35). Los {f0(t['calle']['n'])} arbotantes de calle ({mill(LZ['inversion_calles'])}) van dentro del presupuesto de urbanización; el resto ({mill(LZ['inversion_paisaje'])}) se suma como iluminación de paisaje. Energía a $5/kWh y mantenimiento de 4 % al año: ${f0(LZ['cuota_casa_mes'])} por casa al mes, dentro de la <a href="/numeros/#cuota">cuota</a>.</p>
<div class="mapa-chico"><div id="map" role="region" aria-label="Vista de noche del plan maestro"></div></div>
<p class="nota">Vista de noche: toca una luminaria para ver su clave y dónde está. Costos de 2026 con su parte de cable y ducto; el proyecto ejecutivo de alumbrado (cálculo fotométrico por calle) se hace sobre este inventario.</p>
"""
    pagina("iluminacion", "Iluminación", "09 · Iluminación", f"{f0(LZ['puntos'])} puntos de luz cálida, cada uno en su lugar y con su clave: arbotantes entre los nogales, nogales iluminados desde el piso, balizas en la pista y el acceso bien iluminado.", cuerpo,
           [("plano", "Dónde va cada luz"), ("detalles", "Detalles por zona"), ("reglas", "Reglas"), ("cuenta", "Cuántas y cuánta luz")],
           head='<link rel="stylesheet" href="/vendor/leaflet/leaflet.css">',
           script='<script>window.PLAN={datos:"/datos/",modo:"noche",rueda:false};</script><script src="/vendor/leaflet/leaflet.js"></script><script src="/plan/plan.js"></script>')

# ======================= PISTA Y GIMNASIO =======================
def _anillo():
    """La pista como anillo en uv (2.5 m adentro del límite), con la distancia desde el km 0 frente al acceso."""
    ring = [uv(*c) for c in LIM["geometry"]["coordinates"][0]]
    if ring[0] == ring[-1]: ring = ring[:-1]
    cx_, cy_ = sum(p[0] for p in ring) / len(ring), sum(p[1] for p in ring) / len(ring)
    ring = [(cx_ + (p[0] - cx_) * 0.996, cy_ + (p[1] - cy_) * 0.99) for p in ring]          # ≈ 2.5 m hacia adentro
    # orientar en sentido contrario a las manecillas (área positiva) y empezar en el punto más cercano al acceso
    area = sum(ring[i][0] * ring[(i + 1) % len(ring)][1] - ring[(i + 1) % len(ring)][0] * ring[i][1] for i in range(len(ring)))
    if area < 0: ring = ring[::-1]
    ua, va = uv(*_acc_lonlat)
    def proy(p, a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]; t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy))); return (a[0] + t * dx, a[1] + t * dy)
    mejor = min(((math.dist(proy((ua, va), ring[i], ring[(i + 1) % len(ring)]), (ua, va)), i) for i in range(len(ring))))
    i0 = mejor[1]; p0 = proy((ua, va), ring[i0], ring[(i0 + 1) % len(ring)])
    pts = [p0] + [ring[(i0 + 1 + k) % len(ring)] for k in range(len(ring))] + [p0]
    s = [0.0]
    for a, b in zip(pts[:-1], pts[1:]): s.append(s[-1] + math.dist(a, b))
    return pts, s
PISTA_PTS, PISTA_S = _anillo(); PISTA_L = PISTA_S[-1]
def punto_pista(d):
    d = d % PISTA_L
    for i in range(len(PISTA_S) - 1):
        if PISTA_S[i] <= d <= PISTA_S[i + 1]:
            t = (d - PISTA_S[i]) / max(PISTA_S[i + 1] - PISTA_S[i], 1e-9); a, b = PISTA_PTS[i], PISTA_PTS[i + 1]
            return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
    return PISTA_PTS[-1]
def cruces_pista(u):
    """Dónde corta la transversal u al anillo: (distancia sur, distancia norte) desde el km 0."""
    hits = []
    for i in range(len(PISTA_PTS) - 1):
        a, b = PISTA_PTS[i], PISTA_PTS[i + 1]
        if (a[0] - u) * (b[0] - u) <= 0 and a[0] != b[0]:
            t = (u - a[0]) / (b[0] - a[0]); hits.append((PISTA_S[i] + t * (PISTA_S[i + 1] - PISTA_S[i]), a[1] + t * (b[1] - a[1])))
    hits.sort(key=lambda h: h[1]); return hits[0], hits[-1]
def vueltas():
    """Vueltas que se pueden armar con la pista y una transversal (ida por la pista, regreso por la calle)."""
    out = []
    for n in R["calles_cruce"]:
        u = _u_de_cruce(n); (s_s, v_s), (s_n, v_n) = cruces_pista(u)
        calle = abs(v_n - v_s)
        arco_este = (s_n - s_s) % PISTA_L; arco_oeste = PISTA_L - arco_este
        out.append((n, round((min(arco_este, arco_oeste) + calle) / 1000, 2), "oriente" if arco_este < arco_oeste else "poniente"))
    return out

def pista_svg():
    PAD = 70; ancho_px = 1400; S = (ancho_px - 2 * PAD) / (U1 - U0); W = ancho_px; H = (V1 - V0) * S + 2 * PAD
    X = lambda u: PAD + (u - U0) * S; Y = lambda v: PAD + (V1 - v) * S
    def pts(f): return " ".join(f"{X(u):.1f},{Y(v):.1f}" for u, v in (uv(*c) for c in f["geometry"]["coordinates"][0]))
    o = [f'<svg viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="La pista para correr" class="plano">']
    for capa in ["pista", "vial", "bulevar", "arroyo", "comunal", "plaza_acceso", "parque", "lote", "salon", "tenis", "padel"]:
        for f in FC["features"]:
            if f["properties"]["capa"] == capa and f["geometry"]["type"] == "Polygon":
                o.append(f'<polygon points="{pts(f)}" fill="{"#fff" if capa == "lote" else "#ededed" if capa in ("pista", "plaza_acceso") else "#dcdcdc" if capa in ("vial", "bulevar", "arroyo") else "#c4c4c4" if capa == "parque" else "#8a8a8a" if capa in ("salon", "tenis", "padel") else "#e3e3e3"}" stroke="{"#ddd" if capa == "lote" else "none"}" stroke-width="0.3"/>')
    o.append(f'<polygon points="{pts(LIM)}" class="pm-limite"/>')
    o.append('<polyline points="' + " ".join(f"{X(p[0]):.1f},{Y(p[1]):.1f}" for p in PISTA_PTS) + '" fill="none" stroke="#000" stroke-width="4"/>')
    for d in range(0, int(PISTA_L), 500):
        p = punto_pista(d); o.append(f'<circle cx="{X(p[0]):.1f}" cy="{Y(p[1]):.1f}" r="9" fill="#000"/><text x="{X(p[0]):.1f}" y="{Y(p[1])+3.5:.1f}" font-size="9" font-weight="700" fill="#fff" text-anchor="middle">{d/1000:.1f}</text>')
    for d in range(100, int(PISTA_L), 100):
        if d % 500: p = punto_pista(d); o.append(f'<circle cx="{X(p[0]):.1f}" cy="{Y(p[1]):.1f}" r="2.2" fill="#000"/>')
    # estaciones (barras, paralelas, banco, fuente): km 0 en el club, los dos parques y la punta oriente
    est = [(punto_pista(0), "km 0 · club: fuente, baños, regaderas, reloj")]
    for f in FC["features"]:
        if f["properties"]["capa"] == "parque":
            cs = [uv(*c) for c in f["geometry"]["coordinates"][0]]; cu, cv = sum(c[0] for c in cs) / len(cs), sum(c[1] for c in cs) / len(cs)
            est.append(((cu, cv), f"{f['properties']['nombre']}: estación de ejercicio y fuente"))
    est.append((punto_pista(PISTA_L * 0.5), "mitad de la vuelta: estación y fuente"))
    for (u, v), txt in est:
        o.append(f'<rect x="{X(u)-7:.1f}" y="{Y(v)-7:.1f}" width="14" height="14" fill="#fff" stroke="#000" stroke-width="2"/><text x="{X(u)+11:.1f}" y="{Y(v)+4:.1f}" class="pm-etiqueta" font-size="10.5">{e(txt)}</text>')
    for nombre in R["calles_cruce"]: o.append(f'<text x="{X(_u_de_cruce(nombre)):.1f}" y="{Y(V1)-10:.1f}" class="pm-rotulo cruce" text-anchor="middle">{e(nombre)}</text>')
    o.append(f'<text x="{X(U0)+10:.1f}" y="{H-PAD/2+4:.1f}" class="pm-etiqueta">● cada 500 m con el kilómetro · · cada 100 m · ▢ estaciones · sentido sugerido: contra las manecillas del reloj</text>')
    o.append("</svg>")
    return "\n".join(o)

def gimnasio_svg():
    """Programa del gimnasio: dos plantas de 32 × 16 m."""
    S = 11; W = 32 * S * 2 + 90; H = 16 * S + 60
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Programa del gimnasio" class="plano">']
    PB = [("Cardio", 0, 0, 13, 9, "12 caminadoras, 8 bicis, 4 elípticas, 4 remos"), ("Pesas libres", 13, 0, 24, 9, "4 racks, mancuernas 2–50 kg, 4 bancos"), ("Máquinas", 24, 0, 32, 9, "12 máquinas de placas"),
          ("Recepción", 0, 9, 7, 16, "tienda y lockers"), ("Vestidores mujeres", 7, 9, 16, 16, "6 regaderas, lockers"), ("Vestidores hombres", 16, 9, 25, 16, "6 regaderas, lockers"), ("Baños", 25, 9, 32, 16, "y limpieza")]
    PA = [("Salón 1 · yoga, pilates", 0, 0, 11, 9, "20 personas"), ("Salón 2 · spinning", 11, 0, 21, 9, "20 bicis"), ("Funcional y cross", 21, 0, 32, 9, "rig, sogas, trineos; puerta a la terraza"),
          ("Fisioterapia y nutrición", 0, 9, 8, 16, "2 consultorios"), ("Oficina", 8, 9, 14, 16, "y monitoreo"), ("Terraza al jardín", 14, 9, 32, 16, "estiramiento, clases al aire libre")]
    for k, (plano, x0) in enumerate(((PB, 20), (PA, 32 * S + 70))):
        o.append(f'<text x="{x0}" y="18" class="t">{"Planta baja · 512 m²" if k == 0 else "Planta alta · 512 m²"}</text>')
        for n, a, b, c, d, nota in plano:
            o.append(f'<rect x="{x0 + a*S}" y="{30 + b*S}" width="{(c-a)*S}" height="{(d-b)*S}" fill="{"#fff" if "Terraza" not in n else "#ececec"}" stroke="#000" stroke-width="1.2"/>')
            ancho = (c - a) * S
            def lineas(txt, por):
                out, cur = [], ""
                for w_ in txt.replace(", ", ",| ").split("| ") if False else txt.split(" "):
                    if cur and len(cur) + 1 + len(w_) > por: out.append(cur); cur = w_
                    else: cur = (cur + " " + w_).strip()
                return out + [cur]
            tit = lineas(n, max(8, int(ancho / 7.2))); notas = lineas(nota, max(10, int(ancho / 5.2))) if nota else []
            y0_ = 30 + (b + d) / 2 * S - (len(tit) + len(notas)) * 6
            for i_, l_ in enumerate(tit): o.append(f'<text x="{x0 + (a+c)/2*S}" y="{y0_ + i_*12}" font-size="10.5" font-weight="700" text-anchor="middle">{e(l_)}</text>')
            for i_, l_ in enumerate(notas): o.append(f'<text x="{x0 + (a+c)/2*S}" y="{y0_ + len(tit)*12 + i_*11}" font-size="8.5" fill="#444" text-anchor="middle">{e(l_)}</text>')
        o.append(f'<text x="{x0 + 16*S}" y="{H - 8}" font-size="9.5" fill="#444" text-anchor="middle">↑ ventanas al norte, a los nogales del club · 32 × 16 m</text>')
    o.append("</svg>")
    return "\n".join(o)

def pista():
    vs = vueltas(); bal = LZ["cuenta"]["baliza"]
    POB = SV["POB"]; socios = round(POB * 0.25); pico = round(socios * 0.07)
    cuerpo = f"""
{kpis([("Pista", f"{PISTA_L/1000:.2f} km", "la vuelta completa, por el perímetro, bajo los nogales"), ("Ancho", "3 m", "2 m para correr + 1 m para caminar"), ("Marcas", "cada 100 m", "placa con el kilómetro cada 500 m"), ("Luz", f"{bal} balizas", "cada 20 m, al ras del piso"),
       ("Estaciones", "4", "con fuente de agua, en el club, los parques y a media vuelta"), ("Gimnasio", "1,024 m²", "2 plantas en el club social, junto al km 0"), ("Aforo del gimnasio", f"{pico} personas", f"a la hora pico, para ≈ {f0(socios)} socios")])}
<h2 id="pista">La pista</h2>
<figure><div class="dibujo">{pista_svg()}</div><figcaption><b>{PISTA_L/1000:.2f} km por el perímetro, dentro de la barda y sin cruzar un solo auto</b> (solo el acceso, donde pasa por un cruce elevado). El km 0 está frente al acceso, en el club social: ahí están los baños, las regaderas del gimnasio, una fuente y el reloj.</figcaption></figure>
<div class="dos">
<div>
<h3>Cómo está hecha</h3>
<ul>
<li><b>3 m de ancho en dos franjas:</b> 2 m de carpeta suave para correr (asfalto con capa de caucho de 13 mm, color tierra, la misma que usan las pistas de parque) y 1 m de grava fina compactada para caminar. Las dos drenan a la zanja de infiltración que va debajo.</li>
<li><b>Plana:</b> el terreno tiene {SV['TERR']['desnivel']:.1f} m de desnivel en 1.4 km. No hay subidas, no hay escalones, no hay guarniciones que brincar.</li>
<li><b>Bajo los nogales del lindero:</b> la pista corre por la franja de 5 m entre la barda y los lotes, donde quedan los árboles de la orilla de la huerta. Sombra de abril a octubre y sol en invierno.</li>
<li><b>Un solo sentido sugerido</b> (contra las manecillas del reloj), pintado en el piso: nadie se cruza de frente. Marcas cada 100 m y una placa con el kilómetro cada 500 m, que dicen también la calle más cercana.</li>
<li><b>De noche:</b> {bal} balizas cada 20 m, luz cálida hacia el piso; se ve el camino y no se deslumbra a nadie. Ver <a href="/iluminacion/">Iluminación</a>.</li>
<li><b>Cruce del acceso:</b> la pista cruza los carriles de entrada y salida por un cruce elevado con pintura y señal; es el único punto donde se encuentra con un auto, y ahí el auto va a paso de hombre.</li>
</ul>
</div>
<div>
<h3>Vueltas que se pueden armar</h3>
<p>Ida por la pista y regreso por una transversal, sin repetir calle:</p>
{tabla([(f"Vuelta {e(n)}", f"{km:.2f} km", f"lado {lado}") for n, km, lado in vs] + [("<b>Vuelta completa</b>", f"<b>{PISTA_L/1000:.2f} km</b>", "todo el perímetro"), ("Bulevar Nogal, ida y vuelta por el sendero", f"{2*R['sendero_bulevar_km']:.1f} km", "a la sombra del camellón")], ["Vuelta", "Largo", ""], "compacta")}
</div>
</div>
<h3>Las 4 estaciones</h3>
<ul>
<li><b>Km 0, en el club social:</b> fuente de agua, baños, regaderas y lockers del gimnasio, reloj con cronómetro, bancas y una pared de estiramiento. Es el punto de reunión de los grupos de corredores.</li>
<li><b>{PARQUES[0]} y {PARQUES[1]}:</b> estación de ejercicio al aire libre bajo los nogales (barras de dominadas a tres alturas, paralelas, banco de abdominales, escalera horizontal) y fuente de agua.</li>
<li><b>A media vuelta</b> (km {PISTA_L/2000:.1f}): fuente de agua, banca y estación de estiramiento. Nadie corre más de 900 m sin agua.</li>
</ul>

<h2 id="gimnasio">El gimnasio</h2>
<figure><div class="dibujo">{gimnasio_svg()}</div><figcaption><b>Dos plantas de 32 × 16 m en el club social,</b> con ventanas al norte hacia los nogales del club (luz pareja, nunca sol directo en la tarde) y la terraza de la planta alta hacia el jardín.</figcaption></figure>
<div class="dos">
<div>
<h3>Cómo se dimensionó</h3>
<ul>
<li>{f0(N)} casas × {SV['HAB']:.0f} personas = {f0(POB)} habitantes. En un fraccionamiento con gimnasio incluido, uno de cada cuatro lo usa: <b>≈ {f0(socios)} socios</b>.</li>
<li>La hora pico (6 a 8 de la mañana y 7 a 9 de la noche) junta a 7 % de los socios: <b>{pico} personas al mismo tiempo</b>. A 6 m² por persona en piso de aparatos son 460 m²; con clases, vestidores y recepción, 1,000 m². Las dos plantas dan 1,024.</li>
<li><b>Aparatos:</b> 12 caminadoras, 8 bicicletas, 4 elípticas y 4 remos (cardio, 28 puestos); 4 racks con barra olímpica, mancuernas de 2 a 50 kg y 4 bancos (pesas libres); 12 máquinas de placas (circuito completo). 56 puestos de trabajo en piso.</li>
<li><b>Clases:</b> yoga y pilates (20 personas), spinning (20 bicis) y funcional con rig y terraza. Cada salón con piso de caucho, espejo y aire propio.</li>
<li><b>Vestidores</b> de 9 × 7 m cada uno, con 6 regaderas, 60 lockers y sauna seco. Toalla incluida en la cuota.</li>
<li><b>Fisioterapia y nutrición:</b> dos consultorios en renta para profesionales de afuera, con cita por la app.</li>
</ul>
</div>
<div>
<h3>Cómo opera</h3>
<ul>
<li><b>Horario:</b> 5:30 a 22:30 todos los días; acceso con el mismo tag de la casa, sin recepcionista en las horas bajas (cámaras y botón de emergencia).</li>
<li><b>Incluido en la cuota</b> para los residentes; las clases con instructor y los consultorios tienen costo aparte. Invitados con pase diario.</li>
<li><b>Operación:</b> 2 entrenadores en piso en hora pico, 1 el resto del día; limpieza en cada cambio de turno. Está en la partida «Club y áreas comunes» de la <a href="/numeros/#cuota">cuota</a>.</li>
<li><b>Equipo:</b> línea comercial con contrato de mantenimiento; cardio con pantalla y app; renovación de la mitad del equipo cada 6 años con el fondo de reserva.</li>
<li><b>Ambiente:</b> doble altura en pesas libres, aire acondicionado por zona, música por zona, agua filtrada, estación de limpieza en cada área.</li>
<li><b>Con la pista:</b> el gimnasio es el km 0. Los corredores entran por la terraza, se duchan y salen. El reloj y el marcador del club son el punto de salida de las carreras del fraccionamiento (5 y 10 km, cada mes).</li>
</ul>
</div>
</div>
<p class="nota">La pista y el gimnasio están en el presupuesto: la pista en «Drenaje pluvial · zanja de infiltración» y «Barda» (la franja de 5 m), y el gimnasio en las amenidades ($14 millones, 2 niveles). Las estaciones de ejercicio, fuentes y placas son una partida chica (≈ $1.2 millones) que se suma al club.</p>
"""
    pagina("pista", "Pista y gimnasio", "10 · Pista y gimnasio", f"Una pista de {PISTA_L/1000:.2f} km por el perímetro, plana y bajo los nogales, con estaciones cada kilómetro, y un gimnasio de 1,024 m² en el club social, en el km 0.", cuerpo,
           [("pista", "La pista"), ("gimnasio", "El gimnasio")])
