"""N6 · casa muestra: genera public/n6/casa.html (plantas, emplazamiento con el sol de Torreón, corte y 2 fachadas).
Un solo modelo de casa para los lotes de 12.0 × 24.0 m o más; solo cambia la fachada según hacia dónde da la calle."""
import math, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else "../public/n6/casa.html"

# ---------- datos ----------
LOTE_W, LOTE_D = 12.7, 25.8          # lote muestra (promedio de los 1,109 lotes: 329 m²)
CASA_W = 9.0                         # deja 1.85 m libres a cada lado (1.5 m en lotes de 12.0 m)
FRENTE = 5.5                         # cochera para 2 autos
PB_D, PA_D = 11.0, 14.0              # planta baja cerrada y planta alta (vuela 3 m sobre el portal)
RUMBO_FONDO = {"norte": 329.0, "sur": 149.0}   # hacia dónde mira el jardín según el lado de la calle
SOL = {"ver_med": 87.9, "inv_med": 41.0, "equ_med": 64.4, "ver_puesta": 296.2, "inv_puesta": 243.8, "ver_salida": 63.8, "inv_salida": 116.2}
PB = [("Recámara 1", 0, 0, 3.9, 3.6), ("Baño 1", 0, 3.6, 3.9, 5.4), ("Escalera y vestíbulo", 3.9, 0, 5.7, 5.4),
      ("Cocina", 5.7, 0, 9.0, 5.4), ("Sala", 0, 5.4, 5.0, 11.0), ("Comedor", 5.0, 5.4, 9.0, 11.0)]
PA = [("Recámara 2", 0, 0, 3.9, 3.6), ("Baño 2", 0, 3.6, 3.9, 5.4), ("Escalera", 3.9, 0, 5.7, 5.4),
      ("Recámara 3", 5.7, 0, 9.0, 3.6), ("Baño 3", 5.7, 3.6, 9.0, 5.4), ("Estancia familiar", 0, 5.4, 9.0, 7.6),
      ("Recámara principal", 0, 7.6, 5.4, 14.0), ("Baño y vestidor", 5.4, 7.6, 9.0, 14.0)]
PORTAL = (0, PB_D, CASA_W, PA_D)
area = lambda r: (r[3] - r[1]) * (r[4] - r[2])
m2_pb, m2_pa = CASA_W * PB_D, CASA_W * PA_D
jardin = LOTE_W * LOTE_D - CASA_W * PA_D - 5.85 * FRENTE   # lo que no es casa ni cochera (incluye portal y jardín frontal)

def esc(t): return t.replace("&", "&amp;").replace("<", "&lt;")

# ---------- planta (casa) ----------
def planta(rooms, titulo, portal=False, S=34):
    W, D = CASA_W, PA_D
    pad = 26; w, h = W * S + 2 * pad, D * S + 2 * pad + 22
    Y = lambda y: pad + 22 + (D - y) * S           # frente abajo, jardín arriba
    X = lambda x: pad + x * S
    o = [f'<svg viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="{esc(titulo)}">', f'<text x="{pad}" y="16" class="t">{esc(titulo)}</text>']
    if portal:
        x0, y0, x1, y1 = PORTAL
        o.append(f'<rect x="{X(x0)}" y="{Y(y1)}" width="{(x1-x0)*S}" height="{(y1-y0)*S}" class="portal"/>')
        o.append(f'<text x="{X(4.5)}" y="{Y(12.6)}" class="r" text-anchor="middle">Portal techado · 27 m²</text>')
        o.append(f'<text x="{X(4.5)}" y="{Y(12.6)+13}" class="a" text-anchor="middle">(abajo de la recámara principal)</text>')
    for n, x0, y0, x1, y1 in rooms:
        o.append(f'<rect x="{X(x0)}" y="{Y(y1)}" width="{(x1-x0)*S}" height="{(y1-y0)*S}" class="cuarto"/>')
        cx, cy = X((x0 + x1) / 2), Y((y0 + y1) / 2)
        if n.startswith("Escalera"):
            pass
        else:
            o.append(f'<text x="{cx}" y="{cy-2}" class="r" text-anchor="middle">{esc(n)}</text>')
            o.append(f'<text x="{cx}" y="{cy+12}" class="a" text-anchor="middle">{(x1-x0):.1f} × {(y1-y0):.1f} m · {area((n,x0,y0,x1,y1)):.0f} m²</text>')
        if n.startswith("Escalera"):
            for k in range(1, 12):
                yy = y0 + 0.4 + k * 0.38
                o.append(f'<line x1="{X(x0+0.15)}" y1="{Y(yy)}" x2="{X(x1-0.15)}" y2="{Y(yy)}" class="esc"/>')
    hd = PB_D if portal else PA_D
    o.append(f'<rect x="{X(0)}" y="{Y(hd)}" width="{W*S}" height="{hd*S}" class="muro"/>')
    # ventanas: frente y fondo (cristal = línea doble blanca sobre el muro)
    def vent(x0, x1, y):
        o.append(f'<line x1="{X(x0)}" y1="{Y(y)}" x2="{X(x1)}" y2="{Y(y)}" class="vidrio"/>')
    if portal:
        vent(0.6, 3.3, 0); vent(6.3, 8.4, 0); vent(0.5, 8.5, PB_D)                     # cancel corredizo a todo lo ancho al portal
        o.append(f'<line x1="{X(4.25)}" y1="{Y(0)}" x2="{X(5.35)}" y2="{Y(0)}" class="puerta"/>')
        o.append(f'<line x1="{X(5.0)}" y1="{Y(5.4)}" x2="{X(5.0)}" y2="{Y(11.0)}" class="div"/>')
    else:
        vent(0.6, 3.3, 0); vent(6.1, 8.6, 0); vent(0.6, 4.8, PA_D); vent(6.2, 8.4, PA_D)
    o.append(f'<text x="{X(4.5)}" y="{h-4}" class="a" text-anchor="middle">↓ calle{" · entrada por la escalera" if portal else ""}</text>')
    o.append("</svg>")
    return "\n".join(o)

# ---------- emplazamiento con sol ----------
def flecha(cx, cy, rumbo_rel, L, cls, texto):
    a = math.radians(rumbo_rel)
    x1, y1 = cx + math.sin(a) * L, cy - math.cos(a) * L
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{cx:.1f}" y2="{cy:.1f}" class="{cls}" marker-end="url(#pf)"/>'
            f'<text x="{x1 + math.sin(a)*12:.1f}" y="{y1 - math.cos(a)*12 + 4:.1f}" class="a" text-anchor="middle">{texto}</text>')

def emplazamiento(lado, S=13):
    B = RUMBO_FONDO[lado]                      # rumbo del jardín (pantalla: arriba)
    pad = 150; w, h = LOTE_W * S + 2 * pad, LOTE_D * S + 2 * pad
    X = lambda x: pad + x * S; Y = lambda y: pad + (LOTE_D - y) * S
    hx = (LOTE_W - CASA_W) / 2
    tit = "Lote del lado norte de la calle · jardín al NNO" if lado == "norte" else "Lote del lado sur de la calle · jardín al SSE"
    o = [f'<svg viewBox="0 0 {w:.0f} {h+20:.0f}" role="img" aria-label="{tit}">',
         '<defs><marker id="pf" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" fill="currentColor"/></marker></defs>',
         f'<text x="10" y="18" class="t">{tit}</text>']
    o.append(f'<rect x="{X(0)}" y="{Y(LOTE_D)}" width="{LOTE_W*S}" height="{LOTE_D*S}" class="lote"/>')
    o.append(f'<rect x="{X(-3)}" y="{Y(0)}" width="{(LOTE_W+6)*S}" height="{0.9*S}" class="calle"/>')
    o.append(f'<text x="{X(LOTE_W/2)}" y="{Y(0)+0.9*S+13}" class="a" text-anchor="middle">calle</text>')
    o.append(f'<rect x="{X(0.3)}" y="{Y(FRENTE)}" width="{5.85*S}" height="{(FRENTE-0.3)*S}" class="cochera"/>')
    o.append(f'<text x="{X(3.2)}" y="{Y(2.8)}" class="a" text-anchor="middle">cochera</text>')
    o.append(f'<rect x="{X(hx)}" y="{Y(FRENTE+PA_D)}" width="{CASA_W*S}" height="{PA_D*S}" class="casa"/>')
    o.append(f'<rect x="{X(hx)}" y="{Y(FRENTE+PA_D)}" width="{CASA_W*S}" height="{3*S}" class="portal2"/>')
    o.append(f'<text x="{X(LOTE_W/2)}" y="{Y(FRENTE+5)}" class="r inv" text-anchor="middle">CASA</text>')
    o.append(f'<text x="{X(LOTE_W/2)}" y="{Y(FRENTE+PA_D-1.6)}" class="a" text-anchor="middle">portal</text>')
    o.append(f'<text x="{X(LOTE_W/2)}" y="{Y(FRENTE+PA_D+3.4)}" class="r" text-anchor="middle">JARDÍN</text>')
    for tx, ty in ((0, 0.8), (LOTE_W, 0.8), (0, 13.4), (LOTE_W, 13.4), (0, 25.8), (LOTE_W, 25.8)):
        o.append(f'<circle cx="{X(tx)}" cy="{Y(ty)}" r="{4.3*S}" class="copa"/><circle cx="{X(tx)}" cy="{Y(ty)}" r="4" class="tronco"/>')
    o.append(f'<text x="{X(LOTE_W)+6}" y="{Y(13.4)+4}" class="a">nogal</text>')
    # norte y sol (rumbo relativo a "arriba" = B)
    cx, cy = X(LOTE_W) + 62, Y(LOTE_D) - 45
    a = math.radians((0 - B) % 360)
    o.append(f'<circle cx="{cx}" cy="{cy}" r="22" class="rosa"/>'
             f'<line x1="{cx - math.sin(a)*18:.1f}" y1="{cy + math.cos(a)*18:.1f}" x2="{cx + math.sin(a)*18:.1f}" y2="{cy - math.cos(a)*18:.1f}" class="norte" marker-end="url(#pf)"/>'
             f'<text x="{cx + math.sin(a)*32:.1f}" y="{cy - math.cos(a)*32 + 4:.1f}" class="r" text-anchor="middle">N</text>')
    hc = (X(LOTE_W/2), Y(FRENTE + PA_D / 2))
    o.append(flecha(*hc, (180 - B) % 360, 205, "sol", "sol de invierno, mediodía"))
    o.append(flecha(*hc, (SOL["ver_puesta"] - B) % 360, 205, "sol2", "sol de verano, tarde"))
    o.append(f'<text x="10" y="{h+14}" class="a">Medidas en metros. Lote 12.7 × 25.8 m. Los nogales quedan en los linderos.</text>')
    o.append("</svg>")
    return "\n".join(o)

# ---------- corte ----------
def corte(S=22):
    pad = 30; w, h = (LOTE_D + 9) * S + 2 * pad, 16 * S
    gy = h - 40
    X = lambda y: pad + (y + 2) * S; Z = lambda z: gy - z * S
    o = [f'<svg viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="Corte con el sol">', f'<text x="{pad}" y="18" class="t">Corte: el portal da sombra de marzo a octubre y deja entrar el sol de invierno</text>']
    o.append(f'<line x1="{X(-2)}" y1="{gy}" x2="{X(LOTE_D+2)}" y2="{gy}" class="suelo"/>')
    f0 = FRENTE
    o.append(f'<rect x="{X(f0)}" y="{Z(6.6)}" width="{PA_D*S}" height="{3.3*S}" class="corteM"/>')      # planta alta
    o.append(f'<rect x="{X(f0)}" y="{Z(3.3)}" width="{PB_D*S}" height="{3.3*S}" class="corteM"/>')      # planta baja
    o.append(f'<text x="{X(f0+PA_D/2)}" y="{Z(5)}" class="r" text-anchor="middle">Planta alta: 3 recámaras con baño</text>')
    o.append(f'<text x="{X(f0+PB_D/2)}" y="{Z(1.6)}" class="r" text-anchor="middle">Planta baja: recámara, cocina, sala-comedor</text>')
    gx = f0 + PB_D                                   # cristal hacia el portal
    o.append(f'<line x1="{X(gx)}" y1="{Z(0)}" x2="{X(gx)}" y2="{Z(2.7)}" class="vidrioC"/>')
    o.append(f'<text x="{X(f0+PB_D+1.5)}" y="{Z(1.3)}" class="a" text-anchor="middle">portal</text>')
    edge = (f0 + PA_D, 3.0)
    for alt, cls, t in ((SOL["inv_med"], "sol", f"invierno {SOL['inv_med']:.0f}°: entra"), (SOL["equ_med"], "sol2", f"marzo y sept. {SOL['equ_med']:.0f}°: sombra"), (SOL["ver_med"], "sol2", f"verano {SOL['ver_med']:.0f}°: sombra")):
        a = math.radians(alt)
        L = 6.0
        x1, z1 = edge[0] + L * math.cos(a), edge[1] + L * math.sin(a)
        zg = edge[1] - (edge[0] - gx) * math.tan(a)   # dónde pega en el cristal
        x2, z2 = (gx, max(zg, 0)) if zg > 0 else (edge[0] - edge[1] / math.tan(a), 0)
        o.append(f'<line x1="{X(x1)}" y1="{Z(z1)}" x2="{X(x2)}" y2="{Z(z2)}" class="{cls}" marker-end="url(#pf2)"/>')
        o.append(f'<text x="{X(x1)-4}" y="{Z(z1)-4}" class="a" text-anchor="end">{t}</text>')
    o.insert(1, '<defs><marker id="pf2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10z" fill="currentColor"/></marker></defs>')
    # nogal al fondo
    tx = LOTE_D + 1.5
    o.append(f'<line x1="{X(tx)}" y1="{Z(0)}" x2="{X(tx)}" y2="{Z(4)}" class="tronco2"/><ellipse cx="{X(tx)}" cy="{Z(8)}" rx="{4.3*S}" ry="{4*S}" class="copaC"/>')
    o.append(f'<text x="{X(tx)}" y="{Z(8)}" class="a" text-anchor="middle">nogal</text><text x="{X(tx)}" y="{Z(8)+12}" class="a" text-anchor="middle">sombra en verano,</text><text x="{X(tx)}" y="{Z(8)+24}" class="a" text-anchor="middle">sin hojas en invierno</text>')
    o.append(f'<text x="{X(f0/2)}" y="{gy+16}" class="a" text-anchor="middle">calle · cochera</text><text x="{X(f0+PA_D+3.4)}" y="{gy+16}" class="a" text-anchor="middle">jardín</text>')
    o.append("</svg>")
    return "\n".join(o)

# ---------- fachadas ----------
def fachada(tipo, S=34):
    pad = 24; W = CASA_W; H = 7.0
    w, h = W * S + 2 * pad, H * S + 2 * pad + 22
    X = lambda x: pad + x * S; Z = lambda z: pad + 22 + (H - z) * S
    sol = tipo == "sol"
    tit = "Fachada A · calle al SSE (lotes del lado norte)" if sol else "Fachada B · calle al NNO (lotes del lado sur)"
    o = [f'<svg viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="{tit}">', f'<text x="{pad}" y="16" class="t">{tit}</text>']
    o.append(f'<rect x="{X(0)}" y="{Z(6.9)}" width="{W*S}" height="{6.9*S}" class="fach"/>')
    o.append(f'<line x1="{X(0)}" y1="{Z(3.3)}" x2="{X(W)}" y2="{Z(3.3)}" class="div"/>')
    def ven(x0, x1, z0, z1):
        o.append(f'<rect x="{X(x0)}" y="{Z(z1)}" width="{(x1-x0)*S}" height="{(z1-z0)*S}" class="ven"/>')
        if sol:   # alero profundo y celosía de madera
            o.append(f'<rect x="{X(x0-0.3)}" y="{Z(z1+0.35)}" width="{(x1-x0+0.6)*S}" height="{0.25*S}" class="alero"/>')
            for k in range(int((x1 - x0) / 0.25) + 1):
                xx = x0 + 0.1 + k * 0.25
                if xx < x1 - 0.05: o.append(f'<line x1="{X(xx)}" y1="{Z(z1)}" x2="{X(xx)}" y2="{Z(z0)}" class="celos"/>')
        else:
            o.append(f'<rect x="{X(x0-0.1)}" y="{Z(z1+0.15)}" width="{(x1-x0+0.2)*S}" height="{0.12*S}" class="alero"/>')
    if sol:
        ven(0.6, 3.3, 1.0, 2.4); ven(6.3, 8.4, 1.1, 2.3); ven(0.6, 3.3, 4.3, 5.7); ven(6.1, 8.6, 4.3, 5.7)
    else:
        ven(0.6, 3.3, 0.5, 2.5); ven(6.3, 8.4, 0.9, 2.4); ven(0.6, 3.3, 3.9, 6.0); ven(6.1, 8.6, 3.9, 6.0)
    o.append(f'<rect x="{X(4.25)}" y="{Z(2.5)}" width="{1.1*S}" height="{2.5*S}" class="puertaF"/>')
    o.append(f'<rect x="{X(4.35)}" y="{Z(6.2)}" width="{0.9*S}" height="{2.6*S}" class="ven"/>')   # ventana alta de la escalera
    o.append(f'<line x1="{X(-0.4)}" y1="{Z(0)}" x2="{X(W+0.4)}" y2="{Z(0)}" class="suelo"/>')
    o.append("</svg>")
    return "\n".join(o)

rows_pb = "".join(f"<tr><td>{n}</td><td>{area((n,a,b,c,d)):.0f} m²</td></tr>" for n, a, b, c, d in PB)
rows_pa = "".join(f"<tr><td>{n}</td><td>{area((n,a,b,c,d)):.0f} m²</td></tr>" for n, a, b, c, d in PA)

HTML = f"""<!doctype html>
<html lang="es-MX">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>N6 · Casa muestra</title>
<meta name="description" content="Casa muestra para N6: 4 recámaras con baño, sala-comedor y jardín, orientada al sol de Torreón.">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="../style.css">
<style>
  html, body {{ height: auto; }}
  body {{ background: var(--papel); }}
  .doc {{ max-width: 64rem; margin: 0 auto; padding: 1rem 1rem 3rem; }}
  .nav {{ display: flex; flex-wrap: wrap; border: 1px solid var(--linea); margin-bottom: 1rem; max-width: 36rem; }}
  .nav a {{ flex: 1 0 auto; text-align: center; padding: 0.35rem 0.5rem; text-decoration: none; font-size: 0.8125rem; border-right: 1px solid var(--linea); }}
  .nav a:last-child {{ border-right: 0; }}
  .nav a[aria-current="page"] {{ background: var(--tinta); color: var(--papel); }}
  h1 {{ font-size: 1.75rem; margin: 0 0 0.25rem; letter-spacing: -0.01em; }}
  h1 span {{ display: block; font-size: 0.9375rem; font-weight: 400; color: var(--gris); }}
  h2 {{ font-size: 1.0625rem; margin: 2rem 0 0.5rem; border-top: 1px solid var(--linea); padding-top: 0.75rem; }}
  p {{ max-width: 44rem; margin: 0.5rem 0; }}
  .datos {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(9.5rem, 1fr)); gap: 0.5rem 1rem; margin: 1rem 0; font-variant-numeric: tabular-nums; }}
  .datos div {{ border-top: 2px solid var(--tinta); padding-top: 0.3rem; }}
  .datos dt {{ font-size: 0.75rem; color: var(--gris); }}
  .datos dd {{ margin: 0; font-weight: 700; font-size: 1.0625rem; }}
  .dos {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 22rem), 1fr)); gap: 1rem 2rem; align-items: start; }}
  svg {{ width: 100%; height: auto; display: block; color: var(--tinta); font-family: inherit; }}
  svg .t {{ font-size: 13px; font-weight: 700; fill: currentColor; }}
  svg .r {{ font-size: 11px; font-weight: 700; fill: currentColor; }}
  svg .a {{ font-size: 9.5px; fill: var(--gris); }}
  svg .inv {{ fill: #fff; }}
  svg .cuarto {{ fill: #fff; stroke: #000; stroke-width: 1.2; }}
  svg .muro {{ fill: none; stroke: #000; stroke-width: 4; }}
  svg .portal {{ fill: #ededed; stroke: #000; stroke-width: 1; stroke-dasharray: 4 3; }}
  svg .vidrio {{ stroke: #fff; stroke-width: 2.5; }}
  svg .puerta {{ stroke: #fff; stroke-width: 4; }}
  svg .div {{ stroke: #000; stroke-width: 0.8; stroke-dasharray: 3 3; }}
  svg .esc {{ stroke: #000; stroke-width: 0.6; }}
  svg .lote {{ fill: #f4f4f4; stroke: #000; stroke-width: 1.5; }}
  svg .calle {{ fill: #cfcfcf; }}
  svg .cochera {{ fill: #e2e2e2; stroke: #000; stroke-width: 0.6; }}
  svg .casa {{ fill: #111; }}
  svg .portal2 {{ fill: #8a8a8a; }}
  svg .copa {{ fill: rgba(0,0,0,0.06); stroke: #000; stroke-width: 0.6; stroke-dasharray: 3 2; }}
  svg .tronco {{ fill: #000; }}
  svg .norte {{ stroke: #000; stroke-width: 2.5; color: #000; }}
  svg .rosa {{ fill: #fff; stroke: #000; stroke-width: 1; }}
  svg .sol {{ stroke: #000; stroke-width: 2; color: #000; }}
  svg .sol2 {{ stroke: #000; stroke-width: 1.2; stroke-dasharray: 5 3; color: #000; }}
  svg .suelo {{ stroke: #000; stroke-width: 2; }}
  svg .corteM {{ fill: #fff; stroke: #000; stroke-width: 2.5; }}
  svg .vidrioC {{ stroke: #000; stroke-width: 1; stroke-dasharray: 2 2; }}
  svg .copaC {{ fill: rgba(0,0,0,0.06); stroke: #000; stroke-width: 0.8; stroke-dasharray: 3 2; }}
  svg .tronco2 {{ stroke: #000; stroke-width: 4; }}
  svg .fach {{ fill: #f2f2f2; stroke: #000; stroke-width: 2.5; }}
  svg .ven {{ fill: #fff; stroke: #000; stroke-width: 1.2; }}
  svg .alero {{ fill: #000; }}
  svg .celos {{ stroke: #6a6a6a; stroke-width: 1.4; }}
  svg .puertaF {{ fill: #111; }}
  table {{ border-collapse: collapse; font-size: 0.875rem; font-variant-numeric: tabular-nums; width: 100%; max-width: 22rem; }}
  td {{ border-bottom: 1px solid var(--suave); padding: 0.2rem 0.3rem; }} td:last-child {{ text-align: right; }}
  ul {{ padding-left: 1.1rem; max-width: 44rem; }} li {{ margin: 0.3rem 0; }}
</style>
</head>
<body>
<main class="doc">
  <nav class="nav" aria-label="Pestañas del proyecto">
    <a href="../">Nogaleras</a><a href="./">N6 · diseño</a><a href="casa.html" aria-current="page">Casa muestra</a><a href="base.html">N6 · base</a><a href="tamanos.html">N6 · tamaños</a>
  </nav>
  <h1>Casa muestra · Modelo Nogal <span>Un solo modelo para todo el fraccionamiento. Solo cambia la fachada según hacia dónde da la calle.</span></h1>
  <dl class="datos">
    <div><dt>Recámaras</dt><dd>4, cada una con baño</dd></div>
    <div><dt>Construcción</dt><dd>{m2_pb + m2_pa:.0f} m² en 2 niveles</dd></div>
    <div><dt>Sala-comedor</dt><dd>50 m², abierta al jardín</dd></div>
    <div><dt>Portal techado</dt><dd>27 m²</dd></div>
    <div><dt>Jardín (sin casa ni cochera)</dt><dd>≈ {jardin:.0f} m²</dd></div>
    <div><dt>Lote muestra</dt><dd>12.7 × 25.8 m · 328 m²</dd></div>
    <div><dt>Cochera</dt><dd>2 autos</dd></div>
    <div><dt>Lotes donde cabe</dt><dd>1,060 de 1,109 (96 %)</dd></div>
  </dl>

  <h2>Por qué un solo modelo</h2>
  <p>Todos los lotes miden casi lo mismo: el promedio es de 329 m², y 1,060 lotes miden al menos 12.0 × 24.0 m. La casa mide 9 m de ancho y deja 1.5 m o más libres a cada lado, así que entra igual en todos. Un solo juego de planos, de moldes y de compras: se construye más rápido y más barato. Los 49 lotes que no la aceptan son remates angostos en las esquinas; conviene unirlos con el lote vecino o venderlos como lote sin casa.</p>
  <p>Las calles corren al ENE–OSO (rumbo 59°), así que los lotes solo pueden mirar de dos maneras: jardín al NNO o jardín al SSE. La casa es la misma en los dos casos y solo cambia la fachada que da a la calle.</p>

  <h2>Plantas</h2>
  <div class="dos">
    <div>{planta(PB, "Planta baja", portal=True)}<table>{rows_pb}<tr><td><b>Total planta baja</b></td><td><b>{m2_pb:.0f} m²</b></td></tr></table></div>
    <div>{planta(PA, "Planta alta")}<table>{rows_pa}<tr><td><b>Total planta alta</b></td><td><b>{m2_pa:.0f} m²</b></td></tr></table></div>
  </div>
  <ul>
    <li><b>La vida va al fondo:</b> sala, comedor y recámara principal miran al jardín, lejos de la calle y de los autos. Las recámaras 1, 2 y 3 dan al frente.</li>
    <li><b>Una recámara en planta baja</b> con su baño, para visitas, papás o quien no quiera subir escaleras. Bajo la escalera cabe un medio baño para las visitas.</li>
    <li><b>La planta alta vuela 3 m sobre el portal:</b> el portal queda techado sin una losa extra y da sombra a todo el cancel de la sala.</li>
    <li><b>Ventilación cruzada:</b> todo se abre de frente a fondo. Los muros de los costados quedan casi ciegos.</li>
  </ul>

  <h2>Cómo se acomoda en el lote, con el sol de Torreón</h2>
  <div class="dos">
    <div>{emplazamiento("norte")}</div>
    <div>{emplazamiento("sur")}</div>
  </div>
  <ul>
    <li><b>El sol en Torreón:</b> en verano, al mediodía, pega casi vertical (88°) y se pone al ONO (296°). En invierno, al mediodía, sube solo 41° y viene del sur. Lo que más calienta es el sol de la tarde en verano.</li>
    <li><b>Los costados miran al ENE y al OSO</b>, los lados del sol de la mañana y de la tarde. Por eso quedan casi ciegos, y la casa vecina, a 3.7 m, les da sombra.</li>
    <li><b>Jardín al SSE</b> (lotes del lado sur de la calle): en invierno el sol entra hasta la sala, y de marzo a octubre el portal la deja en sombra. Es la mejor orientación.</li>
    <li><b>Jardín al NNO</b> (lotes del lado norte): la sala casi no recibe sol directo y queda fresca todo el año. El sol de la tarde de verano entra de lado al portal: ahí van una celosía corrediza de madera y los nogales del fondo.</li>
    <li><b>Los nogales hacen el resto:</b> tiran la hoja en invierno y dan sombra en verano. Cada lote conserva unos 3 en sus linderos, y su copa cubre parte de la azotea y del jardín.</li>
  </ul>

  <h2>Corte</h2>
  {corte()}

  <h2>Fachadas: lo único que cambia</h2>
  <div class="dos">
    <div>{fachada("sol")}<p>Esta calle recibe sol: aleros de 60 cm y celosía de madera en las ventanas de la planta alta. Ventanas de tamaño normal.</p></div>
    <div>{fachada("sombra")}<p>Esta calle casi no recibe sol: ventanas más altas para ganar luz y aleros delgados.</p></div>
  </div>
  <p>Mismos muros, mismas losas, mismas instalaciones y los mismos huecos estructurales en las dos versiones. Cambian solo los aleros, la celosía y la altura de algunas ventanas. Los materiales y el color pueden variar por calle para que no se vea repetido.</p>

  <h2>Para Torreón</h2>
  <ul>
    <li>Losa con aislante y acabado blanco reflejante: es la superficie que más calor recibe en verano.</li>
    <li>Doble vidrio en las ventanas del frente y el fondo. Los costados casi no llevan ventanas.</li>
    <li>Azotea libre para calentador y paneles solares, sin sombra de vecinos más altos (todo el fraccionamiento es de 2 niveles).</li>
    <li>Jardín de bajo consumo de agua bajo los nogales: grava, plantas del desierto y una zona de pasto chica.</li>
  </ul>
  <p style="color:var(--gris);font-size:0.8125rem">Borrador de anteproyecto: falta revisar el reglamento de construcción de Torreón (restricciones, coeficientes) y el cálculo estructural.</p>
</main>
</body>
</html>
"""
open(OUT, "w").write(HTML)
print("ok", OUT, f"construcción {m2_pb + m2_pa:.0f} m², jardín {jardin:.0f} m²")
