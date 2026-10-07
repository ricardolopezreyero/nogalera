# ======================= AGUA: POZOS, RED A PRESIÓN, PLANTA Y PLUVIAL (se ejecuta dentro de sitio.py) =======================
SG = json.load(open(f"{DAT}/servicios.geojson"))
RED = SV["agua"]["red"]; POZ = RED["pozos"]
def _capa(c): return [f for f in SG["features"] if f["properties"]["capa"] == c]
def _cuv(f):
    g = f["geometry"]
    if g["type"] == "Point": return [uv(*g["coordinates"])]
    if g["type"] == "LineString": return [uv(*c) for c in g["coordinates"]]
    return [uv(*c) for c in g["coordinates"][0]]

def _simbolo(tipo, x, y):
    if tipo.startswith("linea"):
        _, w, *dash = tipo.split(":"); d = f' stroke-dasharray="{dash[0]}"' if dash else ""
        return f'<line x1="{x}" y1="{y}" x2="{x + 34}" y2="{y}" stroke="#000" stroke-width="{w}"{d}/>'
    if tipo == "circ": return f'<circle cx="{x + 17}" cy="{y}" r="4" fill="#fff" stroke="#000" stroke-width="1.2"/>'
    if tipo == "circneg": return f'<circle cx="{x + 17}" cy="{y}" r="4" fill="#000"/>'
    if tipo == "tri": return f'<polygon points="{x + 12},{y + 5} {x + 22},{y + 5} {x + 17},{y - 5}" fill="#000"/>'
    if tipo == "rayado": return f'<rect x="{x + 7}" y="{y - 7}" width="20" height="14" fill="url(#ray)" stroke="#000"/>'
    if tipo == "negro": return f'<rect x="{x + 7}" y="{y - 7}" width="20" height="14" fill="#000"/>'
    if tipo == "gris": return f'<rect x="{x + 7}" y="{y - 7}" width="20" height="14" fill="#000" fill-opacity="0.35" stroke="#000"/>'
    if tipo == "punteado": return f'<rect x="{x + 7}" y="{y - 7}" width="20" height="14" fill="none" stroke="#000" stroke-width="2" stroke-dasharray="4 3"/>'
    return ""

def plano_red_svg(titulo, dibujar, leyenda, ancho_px=1400):
    """Plano con el fondo del plan maestro y una red encima. dibujar(o, X, Y, S, P) agrega la red; leyenda: [(símbolo, texto)]."""
    PAD = 70; S = (ancho_px - 2 * PAD) / (U1 - U0); W = ancho_px
    filas_ley = (len(leyenda) + 2) // 3; LEY = 24 * filas_ley + 16; H = (V1 - V0) * S + 2 * PAD + LEY
    X = lambda u: PAD + (u - U0) * S; Y = lambda v: PAD + (V1 - v) * S
    P = lambda cs: " ".join(f"{X(u):.1f},{Y(v):.1f}" for u, v in cs)
    o = [f'<svg viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="{e(titulo)}" class="plano">',
         '<defs><pattern id="ray" width="6" height="6" patternUnits="userSpaceOnUse"><path d="M0,6 L6,0" stroke="#000" stroke-width="1"/></pattern></defs>']
    cls = {"pista": "pm-pista", "vial": "pm-vial", "bulevar": "pm-bulevar", "arroyo": "pm-bulevar", "sendero": "pm-pista", "comunal": "pm-club", "plaza_acceso": "pm-pista", "ptar": "pm-ptar",
           "parque": "pm-parque", "lote": "pm-lote", "comercio": "pm-comercio", "estacionamiento": "pm-vial"}
    for capa in ["pista", "vial", "bulevar", "arroyo", "sendero", "comunal", "plaza_acceso", "ptar", "parque", "lote", "comercio", "estacionamiento"]:
        for f in FC["features"]:
            if f["properties"]["capa"] == capa and f["geometry"]["type"] == "Polygon":
                o.append(f'<polygon points="{P([uv(*c) for c in f["geometry"]["coordinates"][0]])}" class="{cls[capa]}" opacity="0.55"/>')
    o.append(f'<polygon points="{P(_lim_uv)}" class="pm-limite"/>')
    for nombre in R["calles_largas"]:
        v = _v_de_calle(nombre); o.append(f'<text x="{X(U0)-8:.1f}" y="{Y(v)+4:.1f}" class="pm-rotulo" text-anchor="end">{e(nombre)}</text>')
    for nombre in R["calles_cruce"]:
        u = _u_de_cruce(nombre); o.append(f'<text x="{X(u):.1f}" y="{Y(V1)-10:.1f}" class="pm-rotulo cruce" text-anchor="middle">{e(nombre)}</text>')
    dibujar(o, X, Y, S, P)
    nx, ny = math.sin(_t), -math.cos(_t); cx_, cy_ = W - PAD + 20, PAD + 30
    o.append(f'<circle cx="{cx_}" cy="{cy_}" r="22" fill="#fff" stroke="#000"/><line x1="{cx_ - nx*16:.1f}" y1="{cy_ - ny*16:.1f}" x2="{cx_ + nx*16:.1f}" y2="{cy_ + ny*16:.1f}" stroke="#000" stroke-width="2.5"/>'
             f'<polygon points="{cx_ + nx*22:.1f},{cy_ + ny*22:.1f} {cx_ + nx*8 - ny*6:.1f},{cy_ + ny*8 + nx*6:.1f} {cx_ + nx*8 + ny*6:.1f},{cy_ + ny*8 - nx*6:.1f}" fill="#000"/>'
             f'<text x="{cx_ + nx*34:.1f}" y="{cy_ + ny*34 + 4:.1f}" class="pm-etiqueta" text-anchor="middle" font-weight="700">N</text>')
    yb = H - LEY - PAD / 2
    o.append(f'<line x1="{PAD}" y1="{yb:.1f}" x2="{PAD + 200*S:.1f}" y2="{yb:.1f}" stroke="#000" stroke-width="3"/><text x="{PAD + 100*S:.1f}" y="{yb-6:.1f}" class="pm-etiqueta" text-anchor="middle">200 m</text>')
    o.append(f'<text x="{PAD}" y="{PAD - 40}" class="pm-rotulo" font-size="14">{e(titulo)}</text>')
    if _acc_lonlat:
        ua, va = uv(*_acc_lonlat); o.append(f'<text x="{X(ua):.1f}" y="{Y(V0)+22:.1f}" class="pm-etiqueta" text-anchor="middle" font-weight="700">▲ acceso · Calzada José Vasconcelos</text>')
    colw = (W - 2 * PAD) / 3
    for i, (sym, txt) in enumerate(leyenda):
        x = PAD + (i % 3) * colw; y = H - LEY + 12 + 24 * (i // 3)
        o.append(_simbolo(sym, x, y) + f'<text x="{x + 42}" y="{y + 4}" class="pm-etiqueta">{e(txt)}</text>')
    o.append("</svg>")
    return "\n".join(o)

def _dib_agua(o, X, Y, S, P):
    for f in _capa("morada"): o.append(f'<polyline points="{P(_cuv(f))}" fill="none" stroke="#000" stroke-width="1.6" stroke-dasharray="5 4" opacity="0.6"/>')
    for f in _capa("agua_linea"):
        d = f["properties"]["d"]; w = {100: 1.6, 150: 2.8, 200: 4.6, 250: 5.6}.get(d, 6)
        o.append(f'<polyline points="{P(_cuv(f))}" fill="none" stroke="#000" stroke-width="{w}" stroke-linecap="round"/>')
    for f in _capa("agua_conduccion"): o.append(f'<polyline points="{P(_cuv(f))}" fill="none" stroke="#000" stroke-width="3" stroke-dasharray="12 4 3 4"/>')
    for f in _capa("agua_tanque"): o.append(f'<polygon points="{P(_cuv(f))}" fill="#000"/>')
    for f in _capa("agua_pozo"):
        cs = _cuv(f); o.append(f'<polygon points="{P(cs)}" fill="url(#ray)" stroke="#000" stroke-width="1.6"/>')
        cu = sum(c[0] for c in cs) / len(cs); cv = sum(c[1] for c in cs) / len(cs); k = f["properties"]["pozo"]
        o.append(f'<text x="{X(cu):.1f}" y="{Y(cv) - 14:.1f}" class="pm-etiqueta" text-anchor="middle" font-weight="700" font-size="13">{"POZO 1" if k == "p1" else "POZO 2"}</text>')
    for f in _capa("hidrante"):
        u, v = _cuv(f)[0]; o.append(f'<polygon points="{X(u)-4:.1f},{Y(v)+4:.1f} {X(u)+4:.1f},{Y(v)+4:.1f} {X(u):.1f},{Y(v)-5:.1f}" fill="#000"/>')
    pmin = min(n["p"] for n in RED["nodos"])
    for f in _capa("agua_nodo"):
        p = f["properties"]; u, v = _cuv(f)[0]
        if p.get("fuente"):
            o.append(f'<circle cx="{X(u):.1f}" cy="{Y(v):.1f}" r="7" fill="#fff" stroke="#000" stroke-width="2"/><text x="{X(u)+10:.1f}" y="{Y(v)+4:.1f}" class="pm-etiqueta" font-weight="700">CISTERNA · {p["p"]:.1f}</text>')
            continue
        peor = abs(p["p"] - pmin) < 0.005
        o.append(f'<circle cx="{X(u):.1f}" cy="{Y(v):.1f}" r="{5 if peor else 3.2}" fill="#fff" stroke="#000" stroke-width="{2 if peor else 1.1}"/>')
        o.append(f'<text x="{X(u)+5:.1f}" y="{Y(v)-5:.1f}" class="pm-etiqueta" font-size="9" font-weight="{700 if peor else 400}">{p["p"]:.1f}</text>')

def _dib_pluvial(o, X, Y, S, P):
    for f in _capa("plu_jardin"): o.append(f'<polygon points="{P(_cuv(f))}" fill="#000" fill-opacity="0.45" stroke="none"/>')
    for f in _capa("plu_parque"): o.append(f'<polygon points="{P(_cuv(f))}" fill="none" stroke="#000" stroke-width="2.4" stroke-dasharray="6 4"/>')
    for f in _capa("plu_cajas"): o.append(f'<polygon points="{P(_cuv(f))}" fill="#000" fill-opacity="0.3" stroke="#000"/>')
    for f in _capa("vaso"): o.append(f'<polygon points="{P(_cuv(f))}" fill="#000" fill-opacity="0.6" stroke="#000" stroke-width="1.5"/>')
    for f in _capa("plu_zanja"): o.append(f'<polyline points="{P(_cuv(f))}" fill="none" stroke="#000" stroke-width="2" stroke-dasharray="2 4"/>')
    for c in ("plu_flujo", "plu_flujo_punta"):
        for f in _capa(c): o.append(f'<polyline points="{P(_cuv(f))}" fill="none" stroke="#000" stroke-width="1.6" stroke-linejoin="round"/>')
    for f in _capa("plu_pozo"):
        u, v = _cuv(f)[0]; o.append(f'<circle cx="{X(u):.1f}" cy="{Y(v):.1f}" r="3" fill="#fff" stroke="#000" stroke-width="1.3"/>')

def _dib_sanitario(o, X, Y, S, P):
    for f in _capa("san_atarjea"): o.append(f'<polyline points="{P(_cuv(f))}" fill="none" stroke="#000" stroke-width="2.2"/>')
    for f in _capa("san_colector"): o.append(f'<polyline points="{P(_cuv(f))}" fill="none" stroke="#000" stroke-width="5"/>')
    for f in _capa("ptar_planta"): o.append(f'<polygon points="{P(_cuv(f))}" fill="#000"/>')
    for f in _capa("san_pozo"):
        u, v = _cuv(f)[0]; o.append(f'<circle cx="{X(u):.1f}" cy="{Y(v):.1f}" r="2.6" fill="#fff" stroke="#000" stroke-width="1.2"/>')
    for f in _capa("san_llegada"):
        u, v = _cuv(f)[0]; o.append(f'<circle cx="{X(u):.1f}" cy="{Y(v):.1f}" r="6" fill="#000" stroke="#fff" stroke-width="2"/><text x="{X(u)-10:.1f}" y="{Y(v)+4:.1f}" class="pm-etiqueta" text-anchor="end" font-weight="700">PLANTA</text>')

def pozo_regadera_svg():
    """Del pozo a la regadera: la cadena completa con la presión en cada punto."""
    W, H = 1180, 450
    b = RED["bombas"]; pz = RED["pozo"]; pmin = RED["p_min"]; pset = RED["H_set"] / 10
    p_toma = pmin - 0.15; p_pb = p_toma - 0.05 - 0.2; p_pa = p_pb - 0.32
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Del pozo a la regadera" class="esquema">',
         '<defs><pattern id="ray2" width="6" height="6" patternUnits="userSpaceOnUse"><path d="M0,6 L6,0" stroke="#000" stroke-width="0.8"/></pattern><marker id="fa" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0L10,5L0,10z" fill="#000"/></marker></defs>']
    T = lambda x, y, t, w=400, s=12, a="middle": o.append(f'<text x="{x}" y="{y}" text-anchor="{a}" font-size="{s}" font-weight="{w}">{e(t)}</text>')
    # terreno
    o.append(f'<rect x="0" y="230" width="{W}" height="{H-230}" fill="#eee"/><line x1="0" y1="230" x2="{W}" y2="230" stroke="#000" stroke-width="1.5"/>')
    # pozo
    o.append('<rect x="60" y="230" width="28" height="180" fill="#fff" stroke="#000" stroke-width="1.5"/><rect x="60" y="230" width="28" height="60" fill="url(#ray2)" stroke="#000"/>')
    o.append('<rect x="66" y="330" width="16" height="40" fill="#000"/><line x1="74" y1="230" x2="74" y2="330" stroke="#000" stroke-width="3"/>')
    o.append('<rect x="48" y="200" width="52" height="30" fill="#fff" stroke="#000" stroke-width="1.5"/>')
    T(74, 190, "POZO 1", 700, 13); T(74, 219, "caseta", 400, 10); T(74, 275, "sello", 400, 9); T(100, 350, f"bomba sumergible", 400, 10, "start"); T(100, 363, f"{pz['hp']:.0f} HP · {pz['q']} l/s", 400, 10, "start")
    T(100, 310, "nivel dinámico", 400, 9, "start"); T(100, 322, "≈ 150 m (por confirmar)", 400, 9, "start"); T(74, 398, "200 m", 400, 9)
    # conducción al tanque
    o.append('<line x1="88" y1="236" x2="250" y2="236" stroke="#000" stroke-width="4" stroke-dasharray="12 4 3 4"/>'); T(170, 252, f"conducción 6\" · {pz['L_cond']['p1']:.0f} m", 400, 10)
    # cisterna
    o.append('<rect x="250" y="236" width="150" height="70" fill="#fff" stroke="#000" stroke-width="1.5"/><rect x="250" y="262" width="150" height="44" fill="#000" fill-opacity="0.25"/>')
    T(325, 254, f"CISTERNA {f0(SV['agua']['CISTERNA'])} m³", 700, 12); T(325, 294, "11 h del gasto máximo diario", 400, 9); T(325, 226, "cloración · macromedidor", 400, 10)
    # bombas
    o.append('<rect x="420" y="246" width="110" height="50" fill="#fff" stroke="#000" stroke-width="1.5"/>')
    for i in range(4): o.append(f'<circle cx="{437 + i*24}" cy="271" r="8" fill="{"#000" if i < 3 else "#fff"}" stroke="#000"/>')
    o.append('<line x1="400" y1="286" x2="420" y2="286" stroke="#000" stroke-width="3"/>')
    T(475, 238, f"{b['n']} + 1 bombas con variador", 700, 11); T(475, 312, f"{b['q']:.0f} l/s a {b['H']:.0f} m c/u · {b['hp']:.0f} HP", 400, 10); T(475, 326, f"presión constante {pset:.1f} kg/cm²", 700, 11)
    # red
    o.append('<line x1="530" y1="271" x2="640" y2="271" stroke="#000" stroke-width="5"/><line x1="640" y1="271" x2="730" y2="271" stroke="#000" stroke-width="3.2"/><line x1="730" y1="271" x2="830" y2="271" stroke="#000" stroke-width="2"/>')
    T(585, 262, 'bulevar 8"', 400, 10); T(685, 262, 'transversal 6"', 400, 10); T(780, 262, 'calle 4"', 400, 10)
    T(585, 290, f"{pset:.1f} kg/cm²", 700, 11); T(780, 290, f"{pmin:.2f} en la peor esquina", 700, 11); T(780, 303, "en la hora de más consumo", 400, 9)
    # toma y medidor
    o.append('<line x1="830" y1="271" x2="870" y2="271" stroke="#000" stroke-width="1.6"/><rect x="862" y="262" width="16" height="18" fill="#fff" stroke="#000"/><line x1="878" y1="271" x2="905" y2="271" stroke="#000" stroke-width="1.6"/>')
    T(870, 246, 'toma 3/4" · medidor', 400, 10); T(870, 258, f"{p_toma:.2f} kg/cm²", 700, 10)
    # casa
    o.append('<rect x="905" y="70" width="230" height="120" fill="#fff" stroke="#000" stroke-width="1.5"/><line x1="905" y1="130" x2="1135" y2="130" stroke="#000" stroke-width="1"/>')
    o.append('<polygon points="900,70 1020,30 1140,70" fill="#fff" stroke="#000" stroke-width="1.5"/>')
    o.append('<rect x="915" y="238" width="70" height="40" fill="#fff" stroke="#000" stroke-width="1.5"/><rect x="915" y="252" width="70" height="26" fill="#000" fill-opacity="0.25"/>')
    T(950, 232, "cisterna 5 m³ bajo la cochera", 400, 9); T(1000, 322, "+ hidroneumático de respaldo (solo si falta la red)", 400, 9)
    o.append('<line x1="905" y1="271" x2="915" y2="271" stroke="#000" stroke-width="1.6"/><polyline points="985,258 1000,258 1000,110 1095,110" fill="none" stroke="#000" stroke-width="2.4"/><polyline points="1000,170 1095,170" fill="none" stroke="#000" stroke-width="2.4"/>')
    o.append('<text x="993" y="200" font-size="9" text-anchor="middle" transform="rotate(-90 993 200)">subida 1"</text>'); T(1010, 184, 'ramal 3/4"', 400, 9, "start")
    for yy, pp, piso in ((110, p_pa, "regadera planta alta"), (170, p_pb, "regadera planta baja")):
        o.append(f'<polyline points="1095,{yy} 1110,{yy} 1110,{yy+8}" fill="none" stroke="#000" stroke-width="2"/>')
        for k in range(3): o.append(f'<line x1="{1104 + k*6}" y1="{yy+10}" x2="{1101 + k*6}" y2="{yy+22}" stroke="#000" stroke-width="1"/>')
        T(1118, yy + 36, piso, 400, 9, "end"); T(1118, yy + 48, f"{pp:.1f} kg/cm² · ≈ {10 + 1.2*(pp-1.5)*10/3:.0f} l/min", 700, 10, "end")
    T(1020, 62, "MODELO NOGAL", 700, 11); T(1020, 22, "sin tinaco en la azotea", 400, 10)
    T(W / 2, H - 22, "La presión no depende de un tinaco: la red llega a la casa a 2.5–3.0 kg/cm² y el calentador de paso y las regaderas trabajan con esa presión.", 400, 10.5)
    T(W / 2, H - 8, "La cisterna de la casa y su hidroneumático solo entran si la red falla.", 400, 10.5)
    o.append("</svg>")
    return "\n".join(o)

def boca_tormenta_svg():
    """Corte de una boca de tormenta con su pozo de absorción, en el cruce."""
    W, H = 760, 440
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Boca de tormenta y pozo de absorción" class="esquema">',
         '<defs><pattern id="grava" width="8" height="8" patternUnits="userSpaceOnUse"><circle cx="4" cy="4" r="1.6" fill="#000"/></pattern><pattern id="arena" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="0.7" fill="#000"/></pattern></defs>']
    T = lambda x, y, t, w=400, s=11, a="middle": o.append(f'<text x="{x}" y="{y}" text-anchor="{a}" font-size="{s}" font-weight="{w}">{e(t)}</text>')
    o.append(f'<rect x="0" y="120" width="{W}" height="{H-120}" fill="#eee"/>')
    # calle con bombeo, guarnición y banqueta
    o.append('<polygon points="40,118 300,110 300,120 40,128" fill="#bbb" stroke="#000"/><rect x="300" y="100" width="12" height="20" fill="#888" stroke="#000"/><rect x="312" y="100" width="120" height="8" fill="#ccc" stroke="#000"/>')
    T(170, 100, "arroyo · 2 % hacia la cuneta", 400, 10); T(372, 94, "banqueta", 400, 10); T(306, 94, "guarn.", 400, 8)
    # rejilla y caja
    o.append('<rect x="240" y="114" width="60" height="6" fill="#000"/><rect x="240" y="120" width="60" height="70" fill="#fff" stroke="#000" stroke-width="1.5"/>')
    for k in range(6): o.append(f'<line x1="{246 + k*10}" y1="114" x2="{246 + k*10}" y2="120" stroke="#fff" stroke-width="2"/>')
    T(270, 160, "caja", 400, 10); T(270, 172, "desarenadora", 400, 9); T(270, 205, "rejilla 90 × 60 cm", 400, 10)
    # pozo de absorción
    o.append('<rect x="470" y="150" width="70" height="240" fill="url(#grava)" stroke="#000" stroke-width="1.5"/><rect x="455" y="150" width="15" height="240" fill="url(#arena)" stroke="#000"/><rect x="540" y="150" width="15" height="240" fill="url(#arena)" stroke="#000"/>')
    o.append('<line x1="300" y1="140" x2="470" y2="160" stroke="#000" stroke-width="5"/><rect x="455" y="120" width="100" height="30" fill="#fff" stroke="#000" stroke-width="1.5"/>')
    T(385, 134, 'tubo Ø 30 cm', 400, 10); T(505, 139, "brocal y tapa", 400, 10)
    o.append('<line x1="580" y1="150" x2="580" y2="390" stroke="#000" stroke-width="1"/><line x1="575" y1="150" x2="585" y2="150" stroke="#000"/><line x1="575" y1="390" x2="585" y2="390" stroke="#000"/>')
    T(600, 272, "10 m", 700, 11, "start"); T(600, 288, "Ø 1.2 m · ademe de tabique", 400, 10, "start"); T(600, 301, "junteado a hueso", 400, 10, "start"); T(600, 317, "grava 1–2\" y filtro de arena", 400, 10, "start")
    T(600, 333, "infiltra ≈ 10 mm/h (por confirmar", 400, 10, "start"); T(600, 346, "con la prueba de infiltración)", 400, 10, "start")
    # rebose
    o.append('<line x1="236" y1="106" x2="90" y2="106" stroke="#000" stroke-width="3" stroke-dasharray="6 4" marker-end="url(#fa)"/>'); T(165, 100, "cuando se llena, la tormenta sigue por la cuneta al bulevar", 400, 9)
    T(W / 2, H - 22, "En cada cruce hay dos bocas (una por lado) y un pozo de absorción: las lluvias chicas se infiltran ahí;", 400, 10.5)
    T(W / 2, H - 8, "las tormentas siguen por la cuneta hasta el jardín de lluvia del bulevar y el vaso del oriente.", 400, 10.5)
    o.append("</svg>")
    return "\n".join(o)

def agua():
    A, T_, P_, S_, C_ = SV["agua"], SV["tratamiento"], SV["pluvial"], SV["sanitario"], SV["calles"]
    b = RED["bombas"]; pz = RED["pozo"]
    nod = sorted(RED["nodos"], key=lambda n: n["p"])
    por_d = RED["por_diametro"]
    filas_d = [(f'Ø {int(d)} mm ({ {100: 4, 150: 6, 200: 8, 250: 10}.get(int(d), int(d)//25) }")', {"100": "calles, banqueta norte", "150": "transversales", "200": "bulevar (dos líneas) y alimentación", "250": "alimentación"}.get(d, ""), f0(x["L"]), f1(x["q_max"]), f2(x["v_max"]), f1(x["j_max"])) for d, x in por_d.items()]
    filas_p = [(e(n["nombre"]), f0(n["lotes"]), f"{n['p']:.2f}", f"{n['p_inc']:.2f}") for n in nod[:6]] + [("…", "", "", "")] + [(e(n["nombre"]), f0(n["lotes"]), f"{n['p']:.2f}", f"{n['p_inc']:.2f}") for n in nod[-3:]]
    planta_mes = next((c["mes"] for c in SV["cuota"] if "Planta" in c["concepto"]), 0)
    cap_trat = SV["por_servicio"].get("Tratamiento", 0)
    riego = T_["riego_total"]; extra_pozo = riego / A["vol_anual"]
    leyenda_agua = [("linea:4.6", 'Línea de 8" (200 mm)'), ("linea:2.8", 'Línea de 6" (150 mm)'), ("linea:1.6", 'Línea de 4" (100 mm)'), ("linea:3:12 4 3 4", 'Conducción de los pozos, 6"'), ("rayado", "Pozo (cercado)"), ("negro", "Cisterna y bombeo"),
                    ("circ", "Nodo: presión en kg/cm² en la hora pico"), ("tri", "Hidrante"), ("linea:1.6:5 4", "Agua tratada (red morada)")]
    leyenda_plu = [("linea:1.6", "Hacia dónde escurre la calle"), ("circ", "Boca de tormenta + pozo de absorción"), ("gris", "Jardín de lluvia del camellón"), ("punteado", "Parque con bordo de 30 cm"), ("linea:2:2 4", "Zanja de infiltración bajo la pista"), ("negro", "Vaso de tormentas · cajas bajo estacionamientos")]
    leyenda_san = [("linea:2.2", "Atarjea Ø 20 cm"), ("linea:5", f"Colector Ø {S_['d_col']*100:.0f} cm"), ("circ", "Pozo de visita"), ("negro", "Planta de tratamiento")]
    cuerpo = f"""
{kpis([("Pozos", "2", f"{pz['q']} l/s cada uno · 1 trabaja, 1 de respaldo"), ("Cisterna", f"{f0(A['CISTERNA'])} m³", "11 h del gasto máximo diario"), ("Bombeo", f"{RED['H_set']/10:.1f} kg/cm²", f"constante · {b['n']} + 1 bombas de {b['hp']:.0f} HP"),
       ("En la peor esquina", f"{RED['p_min']:.2f} kg/cm²", f"hora pico · {e(RED['nodo_min'])}"), ("Con un hidrante abierto", f"{RED['p_min_inc_nodo']:.2f} kg/cm²", "mínimo en toda la red"), ("Red", f"{f0(sum(x['L'] for x in por_d.values()))} m", f"{RED['n_tubos']} tramos · {RED['n_nodos']} nodos · {A['hidrantes']} hidrantes"),
       ("Planta de tratamiento", "Sí", f"{T_['Q_PTAR']} l/s · riega {f0(T_['n_nogales'])} nogales"), ("Agua", mill(SV['por_servicio']['Agua potable']), "pozos, cisterna, bombeo y red")])}
<p class="frase"><b>Que nadie tenga tema con el agua.</b> Dos pozos propios, una cisterna que guarda medio día, bombeo a presión constante de {RED['H_set']/10:.1f} kg/cm² y una red en malla donde ninguna esquina baja de {RED['p_min']:.2f} kg/cm² ni en la hora de más consumo. La casa recibe esa presión directa: sin tinaco. La lluvia se infiltra en el propio fraccionamiento y el drenaje llega por gravedad a la planta, que devuelve el agua a los nogales.</p>

<h2 id="pozo">Dónde van los pozos</h2>
<p><b>Pozo 1, el principal, junto a la cisterna</b>, en el lado poniente de la plaza de acceso: aguas arriba de todo el fraccionamiento (el terreno baja hacia el oriente), a {f0(POZ['p1']['planta'])} m de la planta de tratamiento, a {POZ['p1']['absorcion']} m del pozo de absorción más cercano y a {POZ['p1']['drenaje']} m del drenaje. La conducción a la cisterna mide {f0(pz['L_cond']['p1'])} m. Queda en un cuadro cercado de 14 × 14 m con caseta, macromedidor y tablero, y no tapa ningún nogal.</p>
<p><b>Pozo 2, el de respaldo, en {e(POZ['p2']['parque'])}</b>: un cuadro cercado de 12 × 12 m dentro del parque, a {f0(POZ['p2']['planta'])} m de la planta y a {POZ['p2']['absorcion']} m del pozo de absorción más cercano, con {f0(pz['L_cond']['p2'])} m de conducción por el bulevar hasta la cisterna. Si el pozo que ya tiene la huerta está sano, con su título y bien ubicado, <b>se rehabilita y toma el lugar del pozo 2</b> (o del 1, si está cerca del acceso) y se mueve lo demás. Ninguno de los dos manda agua directo a la red: todo pasa por la cisterna, donde se clora y se mide.</p>
{tabla([("Distancia a la planta de tratamiento", f"{f0(POZ['p1']['planta'])} m", f"{f0(POZ['p2']['planta'])} m", "≥ 500 m"), ("Distancia al vaso de tormentas", f"{f0(POZ['p1']['vaso'])} m", f"{f0(POZ['p2']['vaso'])} m", "≥ 100 m"),
        ("Distancia al pozo de absorción más cercano", f"{POZ['p1']['absorcion']} m", f"{POZ['p2']['absorcion']} m", "≥ 50 m"), ("Distancia al drenaje sanitario", f"{POZ['p1']['drenaje']} m", f"{POZ['p2']['drenaje']} m", "≥ 20 m, con sello sanitario de 20 m"),
        ("Conducción a la cisterna (6\")", f"{f0(pz['L_cond']['p1'])} m", f"{f0(pz['L_cond']['p2'])} m", ""), ("Nogales que tapa", f"{POZ['p1']['nogales']}", f"{POZ['p2']['nogales']}", "0")],
       ["", "Pozo 1 (junto a la cisterna)", f"Pozo 2 ({e(POZ['p2']['parque'])})", "Regla"], "spec")}
<ul>
<li><b>Cada pozo da {pz['q']} l/s</b> (el gasto máximo diario de {f1(A['Qmd'])} l/s trabajando 20 horas), con bomba sumergible de {pz['hp']:.0f} HP para una columna de 150 m. Perforación de 12" a 200 m, ademe de acero, filtro de grava y sello sanitario de 20 m: la profundidad y el equipo se ajustan con el estudio geohidrológico y el aforo.</li>
<li><b>Derechos:</b> el volumen del fraccionamiento es {f0(A['vol_anual'])} m³ al año. Una nogalera de {ha(GROSS)} suele tener concesión de riego por más que eso; se cambia el uso (agrícola a público urbano) ante Conagua y el título queda a nombre del fideicomiso. El riego de los nogales no sale del pozo: sale de la planta.</li>
<li><b>Dos pozos y no uno:</b> si uno falla o se le da mantenimiento, el otro llena la cisterna; la cisterna aguanta 11 horas del día de más consumo. Planta de emergencia para el bombeo.</li>
</ul>

<h2 id="red">La red: diámetros y presión en cada esquina</h2>
<figure><div class="scroll sec"><div class="dibujo">{plano_red_svg("Agua potable: pozos, cisterna, red y presión en cada nodo (kg/cm², hora de máximo consumo)", _dib_agua, leyenda_agua)}</div></div>
<figcaption><b>Red en malla, no en árbol.</b> Cada calle está alimentada por los dos extremos y por cada transversal: si se cierra una cuadra para una reparación, el resto sigue con agua. La presión se calculó nodo por nodo con Hazen-Williams (PVC, C = 150) en la hora de máximo consumo ({f1(A['Qmh'])} l/s) y con un hidrante de 15 l/s abierto en la peor esquina.</figcaption></figure>
{tabla(filas_d, ["Diámetro", "Dónde", "Largo (m)", "Gasto máx. (l/s)", "Velocidad máx. (m/s)", "Pérdida máx. (m/km)"], "spec", ("<b>Total</b>", "", f"<b>{f0(sum(x['L'] for x in por_d.values()))}</b>", "", "", ""))}
<p>Las velocidades quedan abajo de 1.5 m/s y las pérdidas abajo de 8 m por km: los diámetros no se pueden bajar sin que la última calle sufra, y subirlos no mejora nada. Las líneas de 4" van bajo la banqueta norte de cada calle a 1.1 m; las de 6" por las transversales; las dos de 8" por las banquetas del bulevar, en circuito.</p>
<h3>Las esquinas con menos y con más presión</h3>
{tabla(filas_p, ["Nodo", "Lotes que alimenta", "Hora pico (kg/cm²)", "Con hidrante abierto (kg/cm²)"], "compacta")}
<p>La diferencia entre la mejor y la peor esquina es de {RED['p_max'] - RED['p_min']:.2f} kg/cm²: el terreno es casi plano y la malla reparte. Con un hidrante abierto en la peor esquina ninguna casa baja de {RED['p_min_inc_nodo']:.2f} kg/cm² (la norma pide 1.0). Las {A['valvulas']} válvulas de seccionamiento van en cada cruce.</p>

<h2 id="casa">Del pozo a la regadera</h2>
<figure><div class="scroll sec"><div class="dibujo">{pozo_regadera_svg()}</div></div>
<figcaption><b>Sin tinaco.</b> Un tinaco a 2 m sobre la regadera da 0.2 kg/cm² y 5 litros por minuto; la red da diez veces más presión. Por eso las tomas son de 3/4" (no de 1/2") y la casa se instala para presión de red: subida de 1", ramales de 3/4", calentador de paso y regaderas de 1/2".</figcaption></figure>
{tabla([("Toma domiciliaria", "PEAD 3/4\" con abrazadera, llave de banqueta y medidor de 3/4\" en nicho"), ("Dentro de la casa", "Subida de 1\" de cobre o PPR; ramales de 3/4\" a cada baño; 1/2\" solo del ramal al mueble"), ("Agua caliente", "Calentador de paso de 16 l/min (gas) o bomba de calor; retorno de agua caliente al baño principal"),
        ("Regaderas", "Regadera de 1/2\" sin restrictor: 10 a 12 l/min a 2.0 kg/cm²; mezcladora con balance de presión para que no cambie la temperatura cuando alguien abre otra llave"), ("Respaldo", "Cisterna de 5 m³ bajo la cochera (5 días) con hidroneumático de 3/4 HP y válvula de conmutación automática: solo trabaja si la red cae de 1.5 kg/cm²"),
        ("Azotea", "Sin tinaco: solo los equipos de aire y, si se quiere, el calentador solar")], ["", "Especificación"], "spec")}

<h2 id="calle">Lo que va debajo de la calle</h2>
<div class="scroll sec">{C_['SEC_CALLE']}</div>
<div class="scroll sec">{C_['SEC_BUL']}</div>
<p>En la calle tipo: agua potable de 4" bajo la banqueta norte a 1.1 m; drenaje sanitario de 20 cm al centro, de {S_['d_at_min']:.1f} a {S_['d_at_max']:.1f} m de profundidad; riego de 2" bajo las dos banquetas (goteo a cada nogal); fibra y luz bajo la banqueta sur. En el bulevar: dos líneas de 8" (una por banqueta), dos atarjeas, la red morada de 4" por el camellón y la media tensión. El drenaje pluvial no va entubado por las calles: corre por la cuneta hasta el cruce.</p>

<h2 id="planta">¿Planta de tratamiento o no? Sí</h2>
{tabla([("Inversión", mill(cap_trat), "Emisor hasta el colector de SIMAS más cercano (por confirmar dónde está; hoy La Paz no tiene red) más derechos de conexión"),
        ("Operación", f"${f0(planta_mes)} al mes (ya en la cuota)", "Cuota de drenaje de SIMAS en cada recibo"),
        ("Riego de los nogales", f"{f0(T_['trat_anual'])} m³ al año de agua tratada: cubre el {T_['riego_pct']:.0f} % del riego", f"Saldría del pozo: {f0(riego)} m³ al año, {pct(extra_pozo, 0)} más de extracción y de energía de bombeo"),
        ("Permiso", "Planta propia y reúso (NOM-003): lo que piden Conagua y el municipio cuando no hay red municipal", "Factibilidad de SIMAS: la red tendría que llegar hasta la huerta"),
        ("Si falla", "Tanque de agua tratada de " + f0(T_['TANQUE_TRAT']) + " m³ y planta cerrada con desinfección UV: sin olor y sin descarga a la calle", "Nada que operar")],
       ["", "Con planta propia (lo que proponemos)", "Sin planta (descargar a SIMAS)"], "spec")}
<p>La planta va en la punta oriente, el punto más bajo: todo el drenaje llega por gravedad, sin cárcamos de bombeo en el camino. Es compacta y cerrada (lodos activados SBR, desinfección UV), de {T_['Q_PTAR']} l/s, y produce {f0(T_['trat_dia'])} m³ al día. Esa agua es la que riega los {f0(T_['n_nogales'])} nogales por goteo desde la banqueta: <b>sin planta no hay con qué regar la huerta sin exprimir el pozo</b>. El pozo 1 queda a {f0(POZ['p1']['planta'])} m de ella, en la punta contraria.</p>
<figure><div class="scroll sec"><div class="dibujo">{plano_red_svg("Drenaje sanitario: todo por gravedad a la planta", _dib_sanitario, leyenda_san)}</div></div><figcaption>Atarjeas de 20 cm en cada calle con {S_['S_AT']*1000:.1f} al millar; colector de {S_['d_col']*100:.0f} cm bajo la pista y la transversal del oriente; {S_['pozos']} pozos de visita. El perfil completo y las profundidades están en <a href="/servicios/#sanitario">Servicios</a>.</figcaption></figure>

<h2 id="pluvial">Drenaje pluvial: el agua que cae se queda</h2>
<figure><div class="scroll sec"><div class="dibujo">{plano_red_svg("Drenaje pluvial: hacia dónde escurre cada calle y dónde se infiltra", _dib_pluvial, leyenda_plu)}</div></div>
<figcaption><b>Sin tubería pluvial bajo las calles.</b> Cada calle tiene su parteaguas a media cuadra y baja al cruce, donde hay dos bocas de tormenta con un pozo de absorción; las transversales bajan al bulevar, cuyo camellón es un jardín de lluvia, y lo que sobra llega al vaso del oriente. Tormenta de proyecto: {P_['P10']:.0f} mm en una hora; capacidad de guardar {f0(P_['ret_tot'])} m³ fuera de los lotes contra {f0(P_['E10t'])} m³ que escurren.</figcaption></figure>
<figure><div class="scroll sec"><div class="dibujo">{boca_tormenta_svg()}</div></div><figcaption>{P_['bocas']} bocas de tormenta y {P_['bocas']//2} pozos de absorción de 1.2 m de diámetro y 10 m de profundidad. Las cantidades, el presupuesto y los volúmenes por tipo de almacenamiento están en <a href="/servicios/#pluvial">Servicios</a>.</figcaption></figure>

<h2 id="presupuesto">Lo que cuesta el agua</h2>
{partidas(["Agua potable"])}
{partidas(["Tratamiento"])}
<p class="nota">Cálculo hidráulico en <code>pipeline/scripts/n6_servicios.py</code> (método nodal con Hazen-Williams, demanda por lote asignada al nodo más cercano, hora pico {f1(A['Qmh'])} l/s, incendio = gasto máximo diario + 15 l/s). Por confirmar antes del proyecto ejecutivo: estudio geohidrológico y aforo de los pozos, título de concesión de la huerta (REPDA), prueba de infiltración para los pozos de absorción, y topografía a cada 10 m. Presiones en kg/cm² (1 kg/cm² = 10 m de columna de agua).</p>
"""
    pagina("agua", "Agua: pozos, red y presión", "09 · Agua", f"Dos pozos, cisterna, bombeo a presión constante y una red en malla donde ninguna esquina baja de {RED['p_min']:.1f} kg/cm²; la planta riega los nogales y la lluvia se infiltra en el propio terreno.", cuerpo,
           [("pozo", "Dónde van los pozos"), ("red", "Diámetros y presión"), ("casa", "Del pozo a la regadera"), ("calle", "Debajo de la calle"), ("planta", "¿Planta o no?"), ("pluvial", "Drenaje pluvial"), ("presupuesto", "Lo que cuesta")],
           descripcion="Agua de La Nogalera: dónde van los pozos, la red con su presión en cada esquina, la planta de tratamiento y el drenaje pluvial.")
