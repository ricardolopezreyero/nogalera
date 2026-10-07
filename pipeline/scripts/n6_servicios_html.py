# N6 · hoja de especificaciones de servicios → public/n6/servicios.html (lo ejecuta n6_servicios.py con todas sus variables)
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

def tabla(rows, cols, clase=""):
    h = "".join(f"<th>{_e(c)}</th>" for c in cols)
    return f'<div class="scroll"><table class="{clase}"><tr>{h}</tr>' + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</table></div>"
def partidas(serv):
    xs = [x for x in P_ if x["servicio"] in serv]
    return tabla([(f'<b>{_e(x["elemento"])}</b>', _e(x["especificacion"]), f'{f0(x["cantidad"])} {x["unidad"]}', f'${f0(x["importe"])}') for x in xs], ["Elemento", "Especificación", "Cantidad", "Importe"], "spec")

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

HTML_S = f"""<!doctype html>
<html lang="es-MX">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>N6 · Servicios</title>
<meta name="description" content="N6: hoja de especificaciones de calles, drenaje pluvial y sanitario, tratamiento, agua, electricidad y telecomunicaciones, con presupuesto por partida.">
<link rel="icon" href="../favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="../style.css">
<style>
  html, body {{ height: auto; }} body {{ background: var(--papel); }}
  .doc {{ max-width: 64rem; margin: 0 auto; padding: 1rem 1rem 3rem; }}
  .nav {{ display: flex; flex-wrap: wrap; gap: 1px; background: var(--linea); border: 1px solid var(--linea); margin-bottom: 1rem; max-width: 52rem; }}
  .nav a {{ flex: 1 0 auto; text-align: center; padding: 0.35rem 0.5rem; text-decoration: none; font-size: 0.8125rem; background: var(--papel); white-space: nowrap; }}
  .nav a[aria-current="page"] {{ background: var(--tinta); color: var(--papel); }}
  h1 {{ font-size: 1.75rem; margin: 0 0 0.25rem; }} h1 span {{ display: block; font-size: 0.9375rem; font-weight: 400; color: var(--gris); }}
  h2 {{ font-size: 1.125rem; margin: 2.25rem 0 0.5rem; border-top: 2px solid var(--linea); padding-top: 0.75rem; }}
  h3 {{ font-size: 1rem; margin: 1.25rem 0 0.4rem; }}
  p, ul, ol {{ max-width: 48rem; }} li {{ margin: 0.35rem 0; }}
  .datos {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr)); gap: 0.5rem 1rem; margin: 1rem 0; }}
  .datos div {{ border-top: 2px solid var(--tinta); padding-top: 0.3rem; }} .datos dt {{ font-size: 0.75rem; color: var(--gris); }} .datos dd {{ margin: 0; font-weight: 700; }}
  .mejoras li b {{ display: block; }}
  .scroll {{ overflow-x: auto; }}
  table {{ border-collapse: collapse; font-size: 0.8125rem; font-variant-numeric: tabular-nums; width: 100%; margin: 0.5rem 0 1rem; }}
  th, td {{ border-bottom: 1px solid var(--suave); padding: 0.3rem 0.4rem; text-align: right; vertical-align: top; }}
  th:first-child, td:first-child {{ text-align: left; }} th {{ font-size: 0.75rem; color: var(--gris); font-weight: 400; }}
  table.spec td:nth-child(2) {{ text-align: left; color: #333; min-width: 18rem; }} table.spec th:nth-child(2) {{ text-align: left; }}
  td.izq, th.izq {{ text-align: left; }}
  tr.tot td {{ font-weight: 700; border-top: 2px solid var(--tinta); }}
  svg {{ width: 100%; height: auto; display: block; font-family: inherit; }}
  .sec svg {{ min-width: 40rem; }}
  svg .t {{ font-size: 13px; font-weight: 700; }} svg .r {{ font-size: 10px; font-weight: 700; }} svg .a {{ font-size: 9.5px; fill: #444; }}
  svg .tierra {{ fill: #efefef; }} svg .tierra2 {{ fill: #d8d8d8; }} svg .tierraP {{ fill: #efefef; }}
  svg .concreto {{ fill: #bdbdbd; stroke: #000; stroke-width: 0.8; }} svg .base {{ fill: #dcdcdc; stroke: #999; stroke-width: 0.5; }} svg .subbase {{ fill: #e8e8e8; stroke: #999; stroke-width: 0.5; }}
  svg .lote {{ fill: #fff; stroke: #000; stroke-width: 0.6; stroke-dasharray: 3 2; }} svg .jlluvia {{ fill: #fff; stroke: #000; stroke-width: 0.8; stroke-dasharray: 2 2; }}
  svg .guarn {{ stroke: #000; stroke-width: 2.5; }} svg .cota {{ stroke: #000; stroke-width: 0.5; }} svg .guia {{ stroke: #999; stroke-width: 0.5; stroke-dasharray: 2 2; }}
  svg .tronco {{ stroke: #000; stroke-width: 3; }} svg .copa {{ fill: rgba(0,0,0,0.05); stroke: #000; stroke-width: 0.7; stroke-dasharray: 3 2; }} svg .nada {{ display: none; }}
  svg .poste {{ stroke: #000; stroke-width: 2; }} svg .lum {{ fill: #000; }}
  svg .agua {{ fill: #fff; stroke: #000; stroke-width: 2; }} svg .san {{ fill: #000; }} svg .morada {{ fill: #fff; stroke: #000; stroke-width: 1; stroke-dasharray: 2 1; }}
  svg .cfe {{ fill: #777; }} svg .tel {{ fill: #fff; stroke: #777; stroke-width: 1.2; }}
  svg .toma {{ fill: none; stroke: #000; stroke-width: 0.8; stroke-dasharray: 5 2; }} svg .descarga {{ fill: none; stroke: #000; stroke-width: 1.4; }}
  svg .rej {{ stroke: #ddd; stroke-width: 0.6; }} svg .terr {{ fill: none; stroke: #000; stroke-width: 1.5; }} svg .tubo {{ fill: none; stroke: #000; stroke-width: 3; }} svg .pozoP {{ stroke: #000; stroke-width: 0.6; stroke-dasharray: 2 2; }}
  .nota {{ color: var(--gris); font-size: 0.8125rem; }}
  .descargas a {{ display: inline-block; border: 1px solid var(--linea); padding: 0.3rem 0.6rem; text-decoration: none; margin-right: 0.4rem; font-size: 0.875rem; }}
  .descargas a:hover {{ background: var(--tinta); color: var(--papel); }}
  @media print {{ .nav, .descargas {{ display: none; }} h2 {{ break-before: auto; }} .doc {{ max-width: none; }} }}
</style></head>
<body><main class="doc">
  <nav class="nav" aria-label="Pestañas del proyecto">
    <a href="../">Nogaleras</a><a href="./">N6 · diseño</a><a href="acceso.html">Acceso</a><a href="casa.html">Casa muestra</a><a href="servicios.html" aria-current="page">Servicios</a><a href="terreno.html">Terreno</a><a href="base.html">N6 · base</a><a href="tamanos.html">N6 · tamaños</a>
  </nav>
  <h1>Servicios <span>Hoja de especificaciones de calles, drenajes, agua, tratamiento, luz y fibra · Fracc. {FRACC} (N6)</span></h1>
  <dl class="datos">
    <div><dt>Casas</dt><dd>{f0(N)} · {f0(POB)} habitantes</dd></div>
    <div><dt>Agua potable</dt><dd>{f1(Qmd)} l/s (día máximo)</dd></div>
    <div><dt>Drenaje sanitario</dt><dd>{f1(Qs_med)} l/s medio</dd></div>
    <div><dt>Planta de tratamiento</dt><dd>{Q_PTAR} l/s</dd></div>
    <div><dt>Luz</dt><dd>{f0(kva)} kVA · {len(trafos) + len(especiales)} transformadores</dd></div>
    <div><dt>Urbanización</dt><dd>{mill(URB)}</dd></div>
    <div><dt>Cuota de mantenimiento</dt><dd>${f0(cuota_casa)} por casa al mes</dd></div>
  </dl>
  <p class="descargas"><a href="especificaciones.csv" download>Descargar especificaciones (CSV)</a><a href="./#servicios">Ver las redes en el mapa</a></p>

  <h2 id="mejoras">Proyecto: 10 mejoras</h2>
  <ol class="mejoras">{"".join(f"<li><b>{_e(t)}</b>{_e(d)}</li>" for t, d in MEJORAS)}</ol>

  <h2 id="terreno">Terreno y niveles</h2>
  <p>Cota media: <b>{TERR['z_media']:,.1f} m sobre el nivel del mar</b>. El terreno baja {TERR['pend_km']:.2f} m por km hacia el rumbo {TERR['rumbo']}° (casi al oriente): {TERR['desnivel']:.1f} m de punta a punta. Era una huerta regada por inundación, así que está casi plana. Por eso todo se diseña con pendientes mínimas y los puntos bajos se hacen a propósito.</p>
  <ul>
    <li><b>Calles largas:</b> un parteaguas a media cuadra y pendiente de 0.3 % hacia cada cruce, donde están las bocas de tormenta. Las transversales bajan al bulevar.</li>
    <li><b>Piso terminado de cada casa:</b> 30 cm arriba de la banqueta. Jardín 10 cm abajo de la banqueta.</li>
    <li><b>Despalme de 20 cm</b> y terraplenes compactados al 95 % Proctor. La tierra del despalme se queda para los jardines y los parques.</li>
  </ul>
  {partidas(["Terracerías"])}

  <h2 id="calles">Calles</h2>
  <div class="scroll sec">{SEC_CALLE}</div>
  <div class="scroll sec">{SEC_BUL}</div>
  <ul>
    <li><b>Nombres:</b> calles largas ({calles_txt}) y transversales ({", ".join(CRUCES)}). Placas en cada esquina con el nombre y los números de esa cuadra.</li>
    <li><b>Velocidad:</b> 30 km/h. Radio de giro de 6 m en las esquinas (pasa el camión de bomberos), rampas para silla de ruedas en todas las esquinas y en cada cruce elevado.</li>
    <li><b>Arroyo:</b> 7.0 m, con 2 carriles de 3.5 m. Se puede estacionar de un lado sin cerrar el paso.</li>
    <li><b>Bulevar:</b> 2 arroyos de 7.0 m. El camellón de 5.6 m lleva el sendero de 2.4 m y 2 jardines de lluvia de 1.6 m. Las banquetas de 5.2 m llevan los nogales.</li>
    <li><b>Banquetas:</b> 2 m en las calles. Los nogales quedan 0.85 m adentro del lote, sobre el lindero, así que la banqueta queda libre.</li>
  </ul>
  {partidas(["Calles"])}

  <h2 id="pluvial">Drenaje pluvial</h2>
  <p>Regla: <b>el agua que cae en N6 se queda en N6</b> y riega los nogales. Tormenta de proyecto: {P10:.0f} mm en una hora (periodo de retorno de 10 años). Revisión con {P50:.0f} mm (50 años). Son valores de referencia para Torreón; hay que confirmarlos con las isoyetas de la SCT y Conagua.</p>
  {tabla([("Lotes (azotea, cochera y jardín)", f0(E10["lotes"]), f0(E50["lotes"]), f"jardín 10 cm abajo: {f0(ret_lotes)} m³"),
          ("Calles y banquetas", f0(E10["calles"]), f0(E50["calles"]), ""), ("Parques, club y áreas verdes", f0(E10["verde"]), f0(E50["verde"]), ""),
          ("<b>A guardar fuera de los lotes</b>", f"<b>{f0(E10t)}</b>", f"<b>{f0(E50t)}</b>", f"<b>capacidad: {f0(ret_tot)} m³</b>")],
         ["Escurrimiento (m³)", f"Tr 10 · {P10:.0f} mm", f"Tr 50 · {P50:.0f} mm", "Dónde se guarda"])}
  {tabla([("Jardines de lluvia del camellón", f0(V_jl)), ("Parques con bordo de 30 cm", f0(V_par)), ("Zanja de infiltración bajo la pista", f0(V_zanja)),
          ("Cajas de infiltración bajo los 3 estacionamientos", f0(V_cajas)), (f"Pozos de absorción ({len(bocas)//2})", f0(V_pozos)), ("Vaso de tormentas (punta oriente)", f0(V_vaso)),
          ("<b>Total</b>", f"<b>{f0(ret_tot)}</b>")], ["Almacenamiento", "m³"])}
  <ul>
    <li><b>Las lluvias chicas</b> (casi todas en Torreón) se meten en las bocas de tormenta y se infiltran en los pozos de absorción de cada cruce.</li>
    <li><b>Las tormentas</b> corren por la cuneta (máximo 15 cm de tirante, sin pasar la banqueta) hasta el bulevar. Entran a los jardines de lluvia por cortes en la guarnición y lo que sobra sigue al vaso del oriente.</li>
    <li>El vaso rebosa a la calle del norte solo con tormentas de más de 50 años.</li>
  </ul>
  {partidas(["Drenaje pluvial"])}

  <h2 id="sanitario">Drenaje sanitario</h2>
  {tabla([("Población", f"{f0(POB)} hab ({HAB:.0f} por casa)"), ("Dotación", f"{DOT:.0f} l/hab/día (clima cálido seco), +{(EXTRA-1)*100:.0f} % club, súper y comercio"), ("Aportación", f"{APORTA*100:.0f} % del agua"),
          ("Gasto medio", f"{f1(Qs_med)} l/s"), ("Gasto máximo instantáneo", f"{f1(Qs_max)} l/s (Harmon {harmon(POB):.2f})"), ("Gasto máximo extraordinario", f"{f1(Qs_ext)} l/s"),
          ("Atarjeas", f"Ø 20 cm, pendiente {S_AT*1000:.1f} al millar, {f0(L_atarjea)} m"), ("Colector", f"Ø {d_col*100:.0f} cm, pendiente {S_COL*1000:.0f} al millar, {f0(L_colector)} m"),
          ("Profundidad", f"{d_at_min:.1f} m al inicio de cada calle, {d_at_max:.1f} m la más honda, {prof_llegada:.1f} m en la llegada a la planta"),
          ("Pozos de visita", f"{len(pozos)}, en cada cruce, cada cambio de dirección y a no más de 100 m")], ["Dato", "Valor"])}
  <h3>Perfil: del poniente del bulevar a la planta</h3>
  <div class="scroll sec">{perfil_svg()}</div>
  {tabla([(_e(r["nombre"]), f0(r["largo"]), f0(r["lotes"]), f1(r["q"]), f'{r["diam"]*100:.0f}', f'{r["prof_ini"]:.2f}', f'{r["prof_fin"]:.2f}') for r in detalle_ramas],
         ["Atarjea", "Largo (m)", "Lotes", "Gasto máx. ext. (l/s)", "Ø (cm)", "Prof. inicio (m)", "Prof. final (m)"])}
  {partidas(["Drenaje sanitario"])}

  <h2 id="tratamiento">Planta de tratamiento y red morada</h2>
  <p>La planta va en la punta oriente, que es el punto más bajo: ahí llega todo el drenaje por gravedad. Es compacta y cerrada, con lodos activados (SBR) y desinfección UV. El agua sale con la calidad de la NOM-003-SEMARNAT para riego con contacto. Hay acceso de servicio por la calle del norte para retirar lodos sin entrar al fraccionamiento.</p>
  {tabla([("Agua tratada disponible", f"{f0(trat_dia)} m³ al día · {f0(trat_anual)} m³ al año"), ("Riego de los nogales", f"{f0(n_nogales)} nogales × {M2_ARBOL:.0f} m² × {ET_NOGAL:.2f} m × {FRAC_RIEGO*100:.0f} % = {f0(riego_nogal)} m³ al año"),
          ("Riego de pasto y jardineras", f"{f0(riego_otros)} m³ al año"), ("<b>Cobertura</b>", f"<b>{riego_pct:.0f} %</b> del riego en el año. En junio y julio el riego sube; la diferencia se cubre con el tanque de {f0(TANQUE_TRAT)} m³ y, si falta, con el pozo.")],
         ["Balance", "Valor"])}
  {partidas(["Tratamiento"])}

  <h2 id="agua">Agua potable</h2>
  {tabla([("Gasto medio", f"{f1(Qmed)} l/s"), ("Gasto máximo diario", f"{f1(Qmd)} l/s (× 1.4)"), ("Gasto máximo horario", f"{f1(Qmh)} l/s (× 1.55)"), ("Volumen al año", f"{f0(vol_anual)} m³"),
          ("Cisterna", f"{f0(CISTERNA)} m³ (11 h del gasto máximo diario), en la plaza de acceso, enterrada y con jardín encima"), ("Presión", "2.0 a 3.5 kg/cm² en toda la red, con bombeo a presión constante"),
          ("Hidrantes", f"{len(hidrantes)}, de 15 l/s cada uno durante 2 h, además del gasto máximo horario")], ["Dato", "Valor"])}
  <p>Fuente: el pozo de la huerta. Sus derechos de uso agrícola se pasan a uso público urbano ante Conagua y se ceden al organismo operador (SIMAS Torreón), como pide el municipio para dar la factibilidad. Una nogalera de este tamaño suele tener derechos de más de {f0(vol_anual / 1e3 * 1.2)} mil m³ al año, más de lo que necesita el fraccionamiento. Hay que revisar el título.</p>
  {partidas(["Agua potable"])}

  <h2 id="luz">Electricidad, alumbrado y telecomunicaciones</h2>
  {tabla([("Demanda por casa", f"{DEM_CASA:.1f} kVA diversificados (4 recámaras con minisplit en verano)"), ("Demanda total", f"{f0(kva)} kVA, con club, súper, planta, bombeo y alumbrado"),
          ("Transformadores", f"{len(trafos)} monofásicos de 75 kVA tipo pedestal (≈ 16 casas cada uno) + {len(especiales)} trifásicos"),
          ("Media tensión", "13.2 kV subterránea en anillo, alimentada desde la línea de CFE de la calzada (por confirmar)"),
          ("Alumbrado", f"{luz['puntos']} puntos (ver la capa de iluminación del mapa), circuitos con fotocelda y reloj"),
          ("Fibra", "3 ductos de 2\" en todas las calles; cualquier operador puede entrar sin romper banquetas"),
          ("Gas", "Gas natural si la distribuidora tiene red cerca (por confirmar). Si no, tanque estacionario en cada casa, en la azotea.")], ["Dato", "Valor"])}
  {partidas(["Electricidad", "Alumbrado", "Telecomunicaciones"])}

  <h2 id="barda">Barda, accesos y basura</h2>
  {partidas(["Barda y accesos"])}

  <h2 id="presupuesto">Presupuesto de urbanización</h2>
  {tabla([(_e(k), f"${f0(v)}", f"{v/URB*100:.1f} %", f"${f0(v/N)}") for k, v in por_serv.items()] + [("<b>Total</b>", f"<b>${f0(URB)}</b>", "<b>100 %</b>", f"<b>${f0(URB/N)}</b>")],
         ["Servicio", "Importe (MXN sin IVA)", "Parte", "Por lote"])}
  <p>Son {mill(URB)}: ${f0(URB/gross)} por m² de terreno, ${f0(URB/N)} por lote. Antes el modelo usaba ${f0(URB_CALLE)}/m² de calle más ${f0(URB_BASE)}/m² de redes, o sea {mill(antes)}, y le faltaban la planta, la barda, el pozo, la cisterna y los transformadores. Con el presupuesto por partida, el margen del proyecto queda en <b>{mill(res['margen'])} ({res['roi']:.1f} %)</b>. El precio del terreno que todavía deja buen margen está en la pestaña <a href="terreno.html">Terreno</a>.</p>

  <h2 id="cuota">Cuota de mantenimiento</h2>
  {tabla([(_e(a), _e(b), f"${f0(c)}") for a, b, c in CUOTA] + [("<b>Total al mes</b>", "", f"<b>${f0(cuota_total)}</b>"), ("<b>Por casa al mes</b>", "", f"<b>${f0(cuota_casa)}</b>")], ["Concepto", "Qué incluye", "Al mes"])}

  <h2 id="confirmar">Por confirmar antes del proyecto ejecutivo</h2>
  <ul>
    <li>Levantamiento topográfico a cada 10 m. Aquí se usó un modelo de elevación de 30 m, que sirve para saber hacia dónde baja el terreno, no para dar cotas de obra.</li>
    <li>Mecánica de suelos y pruebas de infiltración en 6 puntos: de eso dependen los pozos de absorción y las zanjas.</li>
    <li>Factibilidades de SIMAS (agua y drenaje, o permiso de planta propia y reúso), CFE (punto de conexión y aportación) y Protección Civil (salida de emergencia e hidrantes).</li>
    <li>Título de los derechos de agua de la huerta y estado del pozo.</li>
    <li>Isoyetas de lluvia de la SCT o Conagua para Torreón.</li>
  </ul>
  <p class="nota">Precios de 2026 en pesos, sin IVA, como referencia para decidir; no son una cotización. Todo sale de <code>pipeline/scripts/n6_servicios.py</code>, que mide las cantidades sobre el plano.</p>
</main></body></html>
"""
open(f"{OUT}/servicios.html", "w").write(HTML_S)
print("ok servicios.html")
