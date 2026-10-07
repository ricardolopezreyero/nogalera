# N6 · dibujos (secciones de calle, perfil del drenaje) y volcado de todo lo calculado a servicios.json (lo ejecuta n6_servicios.py con todas sus variables)
from html import escape as _e
f0 = lambda x: f"{x:,.0f}"
f1 = lambda x: f"{x:,.1f}"
mill = lambda x: f"${x/1e6:,.1f} millones"

# ---------- secciones a escala ----------
def seccion(titulo, ancho, zonas, ductos, extras, S=40, alto=7.5, hondo=3.6, x0=-2.0):
    """zonas: (x_ini, x_fin, tipo, rótulo) · ductos: (x, prof, diámetro m, rótulo, clase) · extras: SVG ya armado (en metros con X, Y)."""
    pad = 14; W = (ancho - x0 + 2) * S; H = (alto + hondo) * S + 2 * pad + 62
    X = lambda x: pad + (x - x0) * S; Y = lambda z: pad + 18 + (alto - z) * S
    o = [f'<svg viewBox="0 0 {W + 2*pad:.0f} {H:.0f}" role="img" aria-label="{_e(titulo)}">', f'<text x="{pad}" y="{pad}" class="t">{_e(titulo)}</text>']
    o.append(f'<rect x="{X(x0):.1f}" y="{Y(0):.1f}" width="{(ancho - x0 + 2)*S:.1f}" height="{hondo*S:.1f}" class="tierra"/>')
    o += [e(X, Y) for e in extras if getattr(e, 'fondo', False)]
    for a, b, tipo, rot in zonas:
        if tipo == "arroyo":
            o.append(f'<polygon points="{X(a):.1f},{Y(0):.1f} {X((a+b)/2):.1f},{Y(0.07):.1f} {X(b):.1f},{Y(0):.1f} {X(b):.1f},{Y(-0.15):.1f} {X(a):.1f},{Y(-0.15):.1f}" class="concreto"/>')
            o.append(f'<rect x="{X(a):.1f}" y="{Y(-0.15):.1f}" width="{(b-a)*S:.1f}" height="{0.2*S:.1f}" class="base"/>')
            o.append(f'<rect x="{X(a):.1f}" y="{Y(-0.35):.1f}" width="{(b-a)*S:.1f}" height="{0.2*S:.1f}" class="subbase"/>')
        elif tipo == "banqueta":
            o.append(f'<polygon points="{X(a):.1f},{Y(0.15):.1f} {X(b):.1f},{Y(0.15):.1f} {X(b):.1f},{Y(0.05):.1f} {X(a):.1f},{Y(0.05):.1f}" class="concreto"/>')
            o.append(f'<rect x="{X(a):.1f}" y="{Y(0.05):.1f}" width="{(b-a)*S:.1f}" height="{0.05*S:.1f}" class="tierra2"/>')
        elif tipo == "lote":
            o.append(f'<rect x="{X(a):.1f}" y="{Y(0.25):.1f}" width="{(b-a)*S:.1f}" height="{0.25*S:.1f}" class="lote"/>')
        elif tipo == "jardin":
            o.append(f'<polygon points="{X(a):.1f},{Y(0.15):.1f} {X(a+0.3):.1f},{Y(-0.25):.1f} {X(b-0.3):.1f},{Y(-0.25):.1f} {X(b):.1f},{Y(0.15):.1f}" class="jlluvia"/>')
        elif tipo == "sendero":
            o.append(f'<rect x="{X(a):.1f}" y="{Y(0.15):.1f}" width="{(b-a)*S:.1f}" height="{0.1*S:.1f}" class="concreto"/>')
        if tipo in ("arroyo", "banqueta", "jardin", "sendero"):
            o.append(f'<line x1="{X(a):.1f}" y1="{Y(alto-0.4):.1f}" x2="{X(a):.1f}" y2="{Y(alto-0.9):.1f}" class="cota"/><line x1="{X(b):.1f}" y1="{Y(alto-0.4):.1f}" x2="{X(b):.1f}" y2="{Y(alto-0.9):.1f}" class="cota"/>')
            o.append(f'<line x1="{X(a):.1f}" y1="{Y(alto-0.65):.1f}" x2="{X(b):.1f}" y2="{Y(alto-0.65):.1f}" class="cota"/>')
            o.append(f'<text x="{X((a+b)/2):.1f}" y="{Y(alto-0.5):.1f}" class="a" text-anchor="middle">{b-a:.1f}</text>')
            o.append(f'<text x="{X((a+b)/2):.1f}" y="{Y(alto-1.25):.1f}" class="r" text-anchor="middle">{_e(rot)}</text>')
        if tipo in ("arroyo",):
            o.append(f'<line x1="{X(a):.1f}" y1="{Y(0.15):.1f}" x2="{X(a):.1f}" y2="{Y(-0.25):.1f}" class="guarn"/><line x1="{X(b):.1f}" y1="{Y(0.15):.1f}" x2="{X(b):.1f}" y2="{Y(-0.25):.1f}" class="guarn"/>')
    o += [e(X, Y) for e in extras if not getattr(e, 'fondo', False)]
    for x, z, d, rot, cls in ductos:
        r = max(d * S / 2, 2.2)
        o.append(f'<circle cx="{X(x):.1f}" cy="{Y(-z):.1f}" r="{r:.1f}" class="{cls}"/>')
        o.append(f'<line x1="{X(x):.1f}" y1="{Y(-z)+r:.1f}" x2="{X(x):.1f}" y2="{Y(-hondo+0.25):.1f}" class="guia"/>')
    filas = {}
    for x, z, d, rot, cls in sorted(ductos, key=lambda t: t[0]):
        k = 0
        while any(abs(X(x) - X(x2)) < 92 for x2 in filas.get(k, [])): k += 1
        filas.setdefault(k, []).append(x)
        o.append(f'<text x="{X(x):.1f}" y="{Y(-hondo+0.25) + 12 + 11*k:.1f}" class="a" text-anchor="middle">{_e(rot)}</text>')
    o.append("</svg>")
    return "\n".join(o)

def arbol(x):
    f = lambda X, Y: (f'<line x1="{X(x):.1f}" y1="{Y(0.25):.1f}" x2="{X(x):.1f}" y2="{Y(3.2):.1f}" class="tronco"/>'
                         f'<ellipse cx="{X(x):.1f}" cy="{Y(5.4):.1f}" rx="{(X(3.0)-X(0)):.1f}" ry="{(Y(3.2)-Y(5.4)):.1f}" class="copa"/>'
                         f'<text x="{X(x):.1f}" y="{Y(5.3):.1f}" class="a" text-anchor="middle">nogal</text>')
    f.fondo = True
    return f
def poste(x, h, doble=False):
    def f(X, Y):
        s = f'<line x1="{X(x):.1f}" y1="{Y(0.15):.1f}" x2="{X(x):.1f}" y2="{Y(h):.1f}" class="poste"/>'
        for sg in ((1, -1) if doble else (1,)):
            s += f'<line x1="{X(x):.1f}" y1="{Y(h):.1f}" x2="{X(x+sg*1.2):.1f}" y2="{Y(h):.1f}" class="poste"/><rect x="{X(x+sg*1.2)-5:.1f}" y="{Y(h):.1f}" width="10" height="3" class="lum"/>'
        return s + f'<text x="{X(x)+4:.1f}" y="{Y(h/2):.1f}" class="a">{h:.0f} m</text>'
    return f
def texto(x, z, t, anc="middle"):
    return lambda X, Y: f'<text x="{X(x):.1f}" y="{Y(z):.1f}" class="a" text-anchor="{anc}">{_e(t)}</text>'
def linea(pts, cls):
    return lambda X, Y: f'<polyline points="{" ".join(f"{X(a):.1f},{Y(-b):.1f}" for a, b in pts)}" class="{cls}"/>'

d_at_min = min(r["prof_ini"] for r in detalle_ramas); d_at_max = max(r["prof_fin"] for r in detalle_ramas)
SEC_CALLE = seccion("Calle tipo · 11 m de paramento a paramento (las 7 calles largas)", 11,
    [(-2, 0, "lote", ""), (0, 2, "banqueta", "banqueta"), (2, 9, "arroyo", "arroyo · 2 carriles de 3.5"), (9, 11, "banqueta", "banqueta"), (11, 13, "lote", "")],
    [(0.25, 0.4, 0.06, "riego 2\"", "morada"), (0.75, 0.6, 0.05, "fibra 3×2\"", "tel"), (1.4, 1.1, 0.11, "agua 4\"", "agua"),
     (5.5, 2.2, 0.20, f"drenaje Ø20 · {d_at_min:.1f}–{d_at_max:.1f} m", "san"), (9.75, 0.6, 0.05, "alumbrado", "cfe"), (10.25, 0.9, 0.08, "luz 240 V", "cfe"), (10.75, 0.4, 0.06, "riego 2\"", "morada")],
    [arbol(-0.85), arbol(11.85), poste(9.35, 6), linea([(1.4, 1.0), (1.4, 0.9), (11.2, 0.9)], "toma"), linea([(11.8, 0.7), (5.6, 2.12)], "descarga"),
     texto(-1.0, 0.45, "lote", "middle"), texto(12.0, 0.45, "lote", "middle"), texto(5.5, 0.35, "bombeo 2 %"), texto(3.4, -0.6, "concreto 15 · base 20 · subbase 20", "start")])
SEC_BUL = seccion("Bulevar Nogal · 30 m", 30,
    [(-2, 0, "lote", ""), (0, 5.2, "banqueta", "banqueta"), (5.2, 12.2, "arroyo", "arroyo 7.0"), (12.2, 13.8, "jardin", "lluvia"), (13.8, 16.2, "sendero", "sendero"),
     (16.2, 17.8, "jardin", "lluvia"), (17.8, 24.8, "arroyo", "arroyo 7.0"), (24.8, 30, "banqueta", "banqueta"), (30, 32, "lote", "")],
    [(0.8, 0.6, 0.05, "fibra", "tel"), (1.8, 0.9, 0.08, "luz", "cfe"), (3.5, 1.15, 0.21, "agua 8\"", "agua"), (4.6, 0.4, 0.06, "riego", "morada"),
     (8.7, 2.2, 0.20, "drenaje Ø20", "san"), (15.0, 0.7, 0.11, "tratada 4\"", "morada"), (21.3, 2.2, 0.20, "drenaje Ø20", "san"),
     (25.4, 0.4, 0.06, "riego", "morada"), (26.5, 1.15, 0.21, "agua 8\"", "agua"), (28.2, 1.1, 0.10, "luz 13.2 kV", "cfe"), (29.2, 0.6, 0.05, "fibra", "tel")],
    [arbol(2.4), arbol(27.6), poste(15.0, 8, doble=True), texto(13.0, -0.6, "← corte en guarnición cada 10 m", "end"), texto(17.0, -0.6, "corte en guarnición →", "start")], S=22)

# ---------- perfil del drenaje: bulevar sur + colector hasta la planta ----------
rb = next(r for r in ramas if r[0] == "Bulevar Nogal (sur)")
(xa, ya), (xb, yb) = rb[1][0], rb[1][-1]
zi0 = zf(xa, ya) - H0; Lb = math.dist(rb[1][0], rb[1][-1])
pf = [(s_, zf(xa + (xb - xa) * s_ / Lb, ya), zi0 - S_AT * s_) for s_ in np.linspace(0, Lb, 30)]
k0 = next(i for i, c_ in enumerate(col) if math.dist(c_["p"], (U_TOR, vb - 6.3)) < 1)
s_ = Lb
for a_, b_ in zip(col[k0:-1], col[k0 + 1:]):
    s_ += math.dist(a_["p"], b_["p"]); pf.append((s_, zf(*b_["p"]), b_["inv"]))
pf[30 - 1] = (Lb, pf[29][1], min(pf[29][2], col[k0]["inv"]))
def perfil_svg():
    W, H, pad = 760, 300, 40
    smax = pf[-1][0]; zmin = min(p[2] for p in pf) - 0.4; zmax = max(p[1] for p in pf) + 0.4
    X = lambda s: pad + s / smax * (W - 2 * pad); Y = lambda z: pad / 2 + (zmax - z) / (zmax - zmin) * (H - pad * 2)
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Perfil del drenaje sanitario">']
    for zz_ in np.arange(math.ceil(zmin), zmax, 1.0):
        o.append(f'<line x1="{pad}" y1="{Y(zz_):.1f}" x2="{W-pad}" y2="{Y(zz_):.1f}" class="rej"/><text x="{pad-4}" y="{Y(zz_)+3:.1f}" class="a" text-anchor="end">{zz_:.0f}</text>')
    o.append(f'<polygon points="{X(0):.1f},{Y(zmin):.1f} ' + " ".join(f"{X(p[0]):.1f},{Y(p[1]):.1f}" for p in pf) + f' {X(smax):.1f},{Y(zmin):.1f}" class="tierraP"/>')
    o.append('<polyline points="' + " ".join(f"{X(p[0]):.1f},{Y(p[1]):.1f}" for p in pf) + '" class="terr"/>')
    o.append('<polyline points="' + " ".join(f"{X(p[0]):.1f},{Y(p[2]):.1f}" for p in pf) + '" class="tubo"/>')
    for s0 in np.arange(0, smax, 100.0):
        p = min(pf, key=lambda q: abs(q[0] - s0)); o.append(f'<line x1="{X(p[0]):.1f}" y1="{Y(p[1]):.1f}" x2="{X(p[0]):.1f}" y2="{Y(p[2]):.1f}" class="pozoP"/>')
    for p, t_, y_, anc in ((pf[0], "inicio del bulevar", Y(pf[0][1]) - 7, "start"), (pf[29], "fin del bulevar", Y(pf[-1][2]) + 16, "end"), (pf[-1], "llega a la planta", Y(pf[-1][2]) + 29, "end")):
        o.append(f'<text x="{X(p[0]):.1f}" y="{y_:.1f}" class="a" text-anchor="{anc}">{t_}: {p[1]-p[2]:.1f} m de profundidad</text>')
    o.append(f'<text x="{W/2:.0f}" y="{H-4}" class="a" text-anchor="middle">{f0(smax)} m · escala vertical exagerada {round(((H - pad*2)/(zmax-zmin)) / ((W-2*pad)/smax)):.0f} veces · líneas verticales: pozos de visita</text>')
    o.append("</svg>")
    return "\n".join(o)

por_serv = {}
for x in P_: por_serv[x["servicio"]] = por_serv.get(x["servicio"], 0) + x["importe"]
ret_tot = sum(almacen.values())
E10t, E50t = E10["calles"] + E10["verde"], E50["calles"] + E50["verde"]
riego_pct = trat_anual / riego_total * 100
calles_txt = ", ".join(LARGAS)
N_ANTES = 1109                                                  # lotes antes de reservar la punta para la planta
MEJORAS = [
    ("Los nogales se riegan con el agua del propio fraccionamiento.", f"Planta de tratamiento de {Q_PTAR} l/s en la punta oriente, el punto más bajo, y red morada con goteo a cada nogal desde la banqueta. El agua tratada ({f0(trat_anual)} m³ al año) {'alcanza para todo el riego de los ' + f0(n_nogales) + ' nogales, los parques y el bulevar, y sobra ' + f'{riego_pct-100:.0f}' + ' %' if riego_pct >= 100 else 'cubre ' + f'{riego_pct:.0f}' + ' % del riego de los ' + f0(n_nogales) + ' nogales, los parques y el bulevar'}. Ningún nogal depende de que un vecino lo riegue. Para hacerle lugar salen {N_ANTES - N} lotes de la punta."),
    ("Drenaje pluvial sin tirar agua a la calle de afuera.", f"Cada lote guarda su lluvia en el jardín, 10 cm abajo de la banqueta. Las calles bajan a los cruces y de ahí al bulevar, cuyo camellón es un jardín de lluvia. Los parques tienen un bordo de 30 cm y se encharcan como se regaba la huerta. Hay zanja de infiltración bajo la pista, cajas de infiltración bajo los estacionamientos y un vaso de tormentas en la punta oriente. Cabe una tormenta de 50 años ({P50:.0f} mm en una hora)."),
    ("Drenaje sanitario 100 % por gravedad.", f"El terreno baja {TERR['desnivel']:.1f} m hacia el oriente. Todas las atarjeas corren a favor y llegan a la planta sin bombeo, con {d_at_max:.1f} m de profundidad máxima en las calles y {prof_llegada:.1f} m en la llegada."),
    ("Agua potable en circuitos.", f"Válvulas en cada cruce para cortar una sola cuadra, {len(hidrantes)} hidrantes a tresbolillo (ninguna casa a más de 150 m) y una cisterna de {f0(CISTERNA)} m³ con bombeo a presión constante. Se usa el pozo de la huerta pasando sus derechos de uso agrícola a público urbano."),
    ("Calles de concreto hidráulico con secciones fijas.", f"Las calles son de 11 m (7 m de arroyo) y el bulevar de 30 m, con bombeo, guarniciones y rampas en cada esquina. {len(mesas)} cruces elevados en el bulevar y frente al club, y 30 km/h en todo el fraccionamiento."),
    ("Todo subterráneo: luz, fibra y alumbrado.", f"Sin postes ni cables a la vista. La luz va en media tensión en anillo, con {len(trafos)} transformadores de pedestal, uno cada ≈ 16 casas. La fibra va en ductos abiertos a cualquier operador, con un ducto de reserva."),
    ("Salida de emergencia al norte.", f"Portón para bomberos y ambulancias a la calle del norte, en la transversal {CRUCES[cruces.index(x_em)]}. El reglamento la pide y no le quita nada al acceso principal."),
    ("Acopio de basura antes de las plumas.", "Junto al estacionamiento de visitas: el camión de la basura no entra al fraccionamiento ni hace fila en la caseta."),
    ("Presupuesto de urbanización por partida.", f"Sustituye los supuestos globales (calles a $1,400/m² y redes a $250/m²) por {len(P_)} partidas medidas sobre el plano: {mill(URB)}, ${f0(URB/gross)} por m² de terreno."),
    ("Cuota de mantenimiento calculada.", f"${f0(cuota_casa)} por casa al mes, con seguridad 24 h, jardinería, planta, iluminación, club y fondo de reserva. Es lo que se le puede prometer al comprador."),
]


# ===== todo lo que necesita el sitio (sitio.py) =====
J = dict(
    N=N, POB=POB, HAB=HAB, DOT=DOT, EXTRA=EXTRA, APORTA=APORTA, gross=gross,
    TERR=dict(z_media=float(TERR["z_media"]), pend_km=float(TERR["pend_km"]), rumbo=float(TERR["rumbo"]), desnivel=float(TERR["desnivel"])),
    agua=dict(Qmed=Qmed, Qmd=Qmd, Qmh=Qmh, vol_anual=vol_anual, CISTERNA=CISTERNA, hidrantes=len(hidrantes), valvulas=valvulas, L_agua={str(k): v for k, v in L_agua.items()}),
    sanitario=dict(Qs_med=Qs_med, Qs_max=Qs_max, Qs_ext=Qs_ext, harmon=harmon(POB), S_AT=S_AT, S_COL=S_COL, L_atarjea=L_atarjea, L_colector=L_colector, d_col=d_col,
                   d_at_min=d_at_min, d_at_max=d_at_max, prof_llegada=prof_llegada, pozos=len(pozos), ramas=detalle_ramas, perfil=perfil_svg()),
    pluvial=dict(P10=P10, P50=P50, E10=E10, E50=E50, ret_lotes=ret_lotes, almacen=almacen, ret_tot=ret_tot, bocas=len(bocas), E10t=E10t, E50t=E50t),
    tratamiento=dict(Q_PTAR=Q_PTAR, trat_dia=trat_dia, trat_anual=trat_anual, n_nogales=n_nogales, M2_ARBOL=M2_ARBOL, ET_NOGAL=ET_NOGAL, FRAC_RIEGO=FRAC_RIEGO,
                     riego_nogal=riego_nogal, riego_otros=riego_otros, riego_total=riego_total, riego_pct=riego_pct, TANQUE_TRAT=TANQUE_TRAT, L_morada={str(k): v for k, v in L_morada.items()}, L_goteo=L_goteo),
    luz=dict(DEM_CASA=DEM_CASA, kva=kva, trafos=len(trafos), especiales=[e[2] for e in especiales], puntos=luz["puntos"]),
    calles=dict(SEC_CALLE=SEC_CALLE, SEC_BUL=SEC_BUL, mesas=len(mesas), cruces_n=cruces_n, L_largo=L_largo, L_cruce=L_cruce, L_bul=L_bul, L_total=L_calles_tot,
                A_pav=A_pav, A_pav_bul=A_pav_bul, A_banq=A_banq, L_guarn=L_guarn, emergencia=CRUCES[cruces.index(x_em)], barda=barda,
                largas=LARGAS, cruces=CRUCES, u_cruces=[float(c) for c in cruces], u_largas=[float(c) for c, _ in ejes], u_acceso=float(c_pri)),
    partidas=P_, por_servicio=por_serv, URB=URB, antes=antes, URB_CALLE=URB_CALLE, URB_BASE=URB_BASE,
    cuota=[dict(concepto=a, incluye=b, mes=c) for a, b, c in CUOTA], cuota_total=cuota_total, cuota_casa=cuota_casa,
    mejoras=[dict(titulo=t, texto=d) for t, d in MEJORAS],
    geo=dict(th=float(th), cx=float(cx), cy=float(cy)),
)
def _lim(o):
    if isinstance(o, dict): return {k: _lim(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [_lim(v) for v in o]
    if isinstance(o, (np.floating,)): return float(o)
    if isinstance(o, (np.integer,)): return int(o)
    return o
json.dump(_lim(J), open(f"{OUT}/servicios.json", "w"), ensure_ascii=False, separators=(",", ":"))
print("ok servicios.json")
