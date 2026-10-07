"""N6 · casa muestra: genera public/n6/casa.html (plantas, emplazamiento con el sol de Torreón, corte y 9 fachadas).
Un solo modelo de casa para los lotes de 12.0 × 24.0 m o más; cambia solo la fachada (9 tipos, ver n6_fachadas.py)."""
import math, sys
OUT = sys.argv[1] if len(sys.argv) > 1 else "../public/n6/casa.html"
import json, os
_fc = json.load(open(os.path.join(os.path.dirname(os.path.abspath(OUT)), "confort.geojson")))
_lt = [f["properties"] for f in _fc["features"] if f["properties"]["capa"] == "lote"]
N_LOTES = len(_lt); N_CABE = sum(1 for p in _lt if p["ancho"] >= 12.0 and p["fondo"] >= 24.0); M2_MEDIO = sum(p["m2"] for p in _lt) / N_LOTES

# ---------- datos ----------
LOTE_W, LOTE_D = 12.7, 25.8          # lote muestra (cerca del promedio de los lotes)
CASA_W = 9.0                         # deja 1.85 m libres a cada lado (1.5 m en lotes de 12.0 m)
FRENTE = 5.5                         # cochera para 2 autos
RUMBO_FONDO = {"norte": 329.0, "sur": 149.0}   # hacia dónde mira el jardín según el lado de la calle
SOL = {"ver_med": 87.9, "inv_med": 41.0, "equ_med": 64.4, "ver_puesta": 296.2, "inv_puesta": 243.8, "ver_salida": 63.8, "inv_salida": 116.2}
import n6_casa_planta as CP
PB_D, PA_D = CP.PB_D, CP.PA_D        # planta baja cerrada y planta alta (vuela 3 m sobre el portal)
m2_pb, m2_pa = CASA_W * PB_D, CASA_W * PA_D
bx0, by0, bx1, by1 = CP.BODEGA_EXT
m2_bodega = (bx1 - bx0) * (by1 - by0)
jardin = LOTE_W * LOTE_D - CASA_W * PA_D - 5.85 * FRENTE - (bx1 - bx0) * 5.2   # sin casa, cochera, bodega ni patio de servicio (incluye portal y jardín frontal)
sala_m2 = sum((c["r"][2] - c["r"][0]) * (c["r"][3] - c["r"][1]) for c in CP.PB if c["n"] in ("Sala", "Comedor", "Cocina"))

def esc(t): return t.replace("&", "&amp;").replace("<", "&lt;")

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
    xc = LOTE_W - 0.3 - 5.85
    o.append(f'<rect x="{X(xc)}" y="{Y(FRENTE)}" width="{5.85*S}" height="{(FRENTE-0.3)*S}" class="cochera"/>')
    o.append(f'<text x="{X(xc + 2.9)}" y="{Y(2.8)}" class="a" text-anchor="middle">cochera</text>')
    o.append(f'<rect x="{X(hx + CASA_W)}" y="{Y(FRENTE + 3.0)}" width="{(LOTE_W - hx - CASA_W)*S}" height="{3.0*S}" class="cochera"/>')
    o.append(f'<rect x="{X(hx + bx0)}" y="{Y(FRENTE + by1)}" width="{(bx1 - bx0)*S}" height="{(by1 - by0)*S}" class="casa"/>')
    o.append(f'<text x="{X(LOTE_W) + 6}" y="{Y(FRENTE + 1.5) + 4}" class="a">patio de servicio</text>')
    o.append(f'<text x="{X(LOTE_W) + 6}" y="{Y(FRENTE + 4.1) + 4}" class="a">bodega</text>')
    o.append(f'<text x="{X(hx / 2)}" y="{Y(2.8)}" class="a" text-anchor="middle">jardín</text>')
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
from n6_fachadas import NOMBRES, SEQ, slug, fachada_de
S = 30                                     # unidades de dibujo por metro (las mismas en todas las fachadas y en la cuadra)
ESTUCO, BLANCO, NEGRO, VIDRIO, SOMBRA = "#f5f5f5", "#ffffff", "#161616", "#2c2c2c", "rgba(0,0,0,0.17)"
DEFS = f"""<svg width="0" height="0" style="position:absolute;width:0;height:0;overflow:hidden" aria-hidden="true"><defs>
<pattern id="p-cantera" width="36" height="27" patternUnits="userSpaceOnUse"><rect width="36" height="27" fill="#e2e2e2"/><path d="M0 13.5H36M0 27H36M0.35 0V13.5M18 13.5V27" stroke="#9a9a9a" stroke-width="0.7" fill="none"/></pattern>
<pattern id="p-ladrillo" width="21.6" height="7.2" patternUnits="userSpaceOnUse"><rect width="21.6" height="7.2" fill="#b3b3b3"/><path d="M0 3.6H21.6M0 7.2H21.6M0.3 0V3.6M10.8 0V3.6M5.4 3.6V7.2M16.2 3.6V7.2" stroke="#f2f2f2" stroke-width="0.7" fill="none"/></pattern>
<pattern id="p-soldado" width="3.6" height="8" patternUnits="userSpaceOnUse"><rect width="3.6" height="8" fill="#b0b0b0"/><path d="M0.3 0V8" stroke="#f2f2f2" stroke-width="0.6"/></pattern>
<pattern id="p-madera" width="3.6" height="10" patternUnits="userSpaceOnUse"><rect width="3.6" height="10" fill="#9b9b9b"/><path d="M0.4 0V10" stroke="#5c5c5c" stroke-width="0.9"/></pattern>
<pattern id="p-viga" width="20" height="3" patternUnits="userSpaceOnUse"><rect width="20" height="3" fill="#585858"/><path d="M0 1.5H12M6 0.4H20" stroke="#3a3a3a" stroke-width="0.5"/></pattern>
<pattern id="p-concreto" width="36" height="18" patternUnits="userSpaceOnUse"><rect width="36" height="18" fill="#d5d5d5"/><path d="M0 9H36M0 18H36" stroke="#bdbdbd" stroke-width="0.6"/><circle cx="9" cy="4.5" r="0.9" fill="#8a8a8a"/><circle cx="27" cy="4.5" r="0.9" fill="#8a8a8a"/></pattern>
<pattern id="p-celosia" width="9" height="9" patternUnits="userSpaceOnUse"><rect width="9" height="9" fill="#eeeeee"/><circle cx="4.5" cy="4.5" r="3" fill="#3a3a3a"/></pattern>
<pattern id="p-petatillo" width="9" height="9" patternUnits="userSpaceOnUse"><rect width="9" height="9" fill="#c4c4c4"/><rect x="2.2" y="2.2" width="4.6" height="4.6" fill="#333"/></pattern>
<pattern id="p-lamas" width="10" height="4.5" patternUnits="userSpaceOnUse"><rect width="10" height="2.8" fill="#dcdcdc"/><path d="M0 2.8H10" stroke="#6e6e6e" stroke-width="0.6"/></pattern>
</defs></svg>"""

class Dib:
    """Dibujo en metros: x a lo ancho de la fachada (0 = esquina izquierda de la casa), z hacia arriba (0 = piso)."""
    def __init__(self, ox, ztop): self.o, self.ox, self.zt = [], ox, ztop
    def X(self, x): return (x + self.ox) * S
    def Z(self, z): return (self.zt - z) * S
    def r(self, x0, x1, z0, z1, fill, stroke=None, sw=1.0):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.o.append(f'<rect x="{self.X(x0):.1f}" y="{self.Z(z1):.1f}" width="{(x1-x0)*S:.1f}" height="{(z1-z0)*S:.1f}" fill="{fill}"{st}/>')
    def ln(self, x0, z0, x1, z1, color="#000", sw=1.0):
        self.o.append(f'<line x1="{self.X(x0):.1f}" y1="{self.Z(z0):.1f}" x2="{self.X(x1):.1f}" y2="{self.Z(z1):.1f}" stroke="{color}" stroke-width="{sw}"/>')
    def c(self, x, z, rad, fill):
        self.o.append(f'<circle cx="{self.X(x):.1f}" cy="{self.Z(z):.1f}" r="{rad*S:.1f}" fill="{fill}"/>')
    def vidrio(self, x0, x1, z0, z1, cols=1, rows=1, marco=NEGRO):
        self.r(x0, x1, z0, z1, VIDRIO, marco, 1.4)
        self.o.append(f'<polygon points="{self.X(x0):.1f},{self.Z(z1):.1f} {self.X(x0+(x1-x0)*0.45):.1f},{self.Z(z1):.1f} {self.X(x0):.1f},{self.Z(z1-(z1-z0)*0.55):.1f}" fill="rgba(255,255,255,0.09)"/>')
        for k in range(1, cols): self.ln(x0 + (x1 - x0) * k / cols, z0, x0 + (x1 - x0) * k / cols, z1, "#8c8c8c", 1.1)
        for k in range(1, rows): self.ln(x0, z0 + (z1 - z0) * k / rows, x1, z0 + (z1 - z0) * k / rows, "#8c8c8c", 1.1)
    def sombra(self, x0, x1, z0, z1): self.r(x0, x1, z0, z1, SOMBRA)
    def suelo(self, x0, x1): self.ln(x0, 0, x1, 0, "#000", 2.2)

# huecos (iguales en las 9): recámara 1, puerta, cocina; recámara 2, escalera, recámara 3
W1, PU, W2 = (0.6, 3.3), (4.25, 5.35), (6.3, 8.4)
W3, ES, W4 = (0.6, 3.3), (4.35, 5.25), (6.1, 8.6)

def puerta_madera(d, x0=PU[0], x1=PU[1], z1=2.6, marco=NEGRO):
    d.r(x0 - 0.1, x1 + 0.1, 0, z1 + 0.1, marco); d.r(x0, x1, 0, z1, "url(#p-madera)", "#000", 0.8); d.ln(x1 - 0.18, 0.9, x1 - 0.18, 1.5, "#fff", 2)

def f_cantera(d):
    d.r(0, 9, 0, 6.95, ESTUCO, "#000", 1.6)
    d.r(0, 9, 0, 3.3, "url(#p-cantera)", "#000", 1.2)
    d.r(-0.06, 9.06, 3.25, 3.47, "url(#p-cantera)", "#000", 0.8)                     # imposta de cantera
    d.sombra(0, 9, 6.55, 6.75); d.r(-0.15, 9.15, 6.75, 7.0, "url(#p-cantera)", "#000", 1)   # cornisa
    for (a, b), z0, z1, cols in ((W3, 4.2, 5.9, 2), (W4, 4.2, 5.9, 2)):
        d.r(a - 0.18, b + 0.18, z0 - 0.25, z1 + 0.18, "url(#p-cantera)", "#000", 1)
        d.vidrio(a, b, z0, z1, cols); d.sombra(a - 0.18, b + 0.18, z0 - 0.4, z0 - 0.25)
    d.r(ES[0] - 0.15, ES[1] + 0.15, 3.65, 6.3, "url(#p-cantera)", "#000", 1); d.vidrio(*ES, 3.8, 6.15, 1, 3)
    for (a, b), z0, z1 in ((W1, 0.9, 2.5), (W2, 1.1, 2.5)):
        d.vidrio(a, b, z0, z1, 2); d.sombra(a, b, z1 - 0.14, z1); d.r(a - 0.1, b + 0.1, z0 - 0.1, z0, "#d0d0d0", "#000", 0.6)
    d.r(4.05, 5.55, 0, 2.85, NEGRO); puerta_madera(d, z1=2.65, marco=NEGRO)

def f_celosia(d):
    d.r(0, 9, 0, 6.9, ESTUCO, "#000", 1.6); d.r(0, 9, 0, 0.35, "#cfcfcf", "#000", 0.8)
    d.vidrio(*W1, 0.9, 2.6, 2); d.vidrio(*W2, 1.1, 2.6); puerta_madera(d)
    d.sombra(0.4, 5.7, 3.38, 3.55)
    d.r(0.25, 5.55, 3.55, 6.45, "url(#p-celosia)", "#000", 1.4)                          # celosía de barro sobre recámara y escalera
    d.r(5.95, 8.75, 4.0, 6.1, BLANCO, "#000", 1.2); d.vidrio(*W4, 4.15, 5.95, 2)
    d.sombra(W4[0], W4[1], 5.78, 5.95); d.sombra(W4[0], W4[0] + 0.15, 4.15, 5.78)
    d.ln(0, 6.9, 9, 6.9, "#000", 2.5)

def f_marco(d):
    d.r(0, 9, 0, 3.3, "url(#p-madera)", "#000", 1.4)
    d.vidrio(*W1, 0.5, 2.7, 3); d.vidrio(*W2, 1.0, 2.7, 2)
    d.r(PU[0] - 0.05, PU[1] + 0.05, 0, 2.75, NEGRO); d.ln(PU[1] - 0.2, 0.8, PU[1] - 0.2, 1.9, "#bbb", 2)
    d.sombra(0, 9, 2.85, 3.3)
    d.r(-0.25, 9.25, 3.3, 7.05, NEGRO)                                                 # caja con marco negro
    d.r(0.15, 8.85, 3.65, 6.7, ESTUCO); d.sombra(0.15, 8.85, 6.42, 6.7); d.sombra(0.15, 0.38, 3.65, 6.42)
    d.vidrio(*W3, 4.1, 6.0, 2); d.vidrio(*ES, 3.85, 6.25); d.vidrio(*W4, 4.1, 6.0, 2)

def f_duela(d):
    d.r(0, 9, 0, 3.3, ESTUCO, "#000", 1.6)
    d.r(0, 9, 3.3, 6.85, "url(#p-madera)", "#000", 1.4); d.r(-0.05, 9.05, 6.85, 7.0, BLANCO, "#000", 1)
    d.r(0, 9, 3.22, 3.36, NEGRO)
    d.vidrio(*W3, 4.1, 6.0, 2); d.r(1.85, 3.6, 4.0, 6.1, "url(#p-madera)", "#000", 1.2); d.sombra(3.6, 3.72, 4.0, 6.1)   # postigo corrido
    d.vidrio(*W4, 4.1, 6.0, 2); d.r(5.9, 7.7, 4.0, 6.1, "url(#p-madera)", "#000", 1.2); d.sombra(7.7, 7.82, 4.0, 6.1)
    d.vidrio(*ES, 3.7, 6.3)
    for k in range(1, 6): d.ln(ES[0] + k * 0.15, 3.7, ES[0] + k * 0.15, 6.3, "#9b9b9b", 2.2)
    d.vidrio(*W1, 0.6, 2.7, 3); d.vidrio(*W2, 1.1, 2.7, 2); puerta_madera(d, z1=2.7)

def f_ladrillo(d):
    d.r(0, 9, 0, 6.95, "url(#p-ladrillo)", "#000", 1.6)
    d.r(0, 9, 3.3, 3.5, "#e0e0e0", "#000", 0.8); d.r(-0.05, 9.05, 6.8, 6.98, "#e0e0e0", "#000", 0.8)
    for (a, b), z0, z1, cols in ((W1, 0.9, 2.5, 2), (W2, 1.1, 2.5, 1), (W3, 4.1, 5.8, 2), (W4, 4.1, 5.8, 2)):
        d.vidrio(a, b, z0, z1, cols); d.r(a - 0.12, b + 0.12, z1, z1 + 0.27, "url(#p-soldado)", "#000", 0.6)
        d.r(a - 0.06, b + 0.06, z0 - 0.08, z0, "#e0e0e0", "#000", 0.5)
    d.r(ES[0] - 0.1, ES[1] + 0.1, 3.75, 6.55, "url(#p-petatillo)", "#000", 1)            # celosía de ladrillo (petatillo)
    d.r(PU[0], PU[1], 0, 2.6, NEGRO); d.r(PU[1] - 0.3, PU[1] - 0.15, 0.2, 2.4, "#6a6a6a")
    d.r(PU[0] - 0.12, PU[1] + 0.12, 2.6, 2.87, "url(#p-soldado)", "#000", 0.6)

def f_hacienda(d):
    d.r(0, 9, 0, 6.95, BLANCO, "#000", 1.8); d.r(0, 9, 0, 0.45, "#d6d6d6", "#000", 0.8)    # rodapié
    for (a, b), z0, z1, rej in ((W1, 0.9, 2.4, True), (W2, 1.1, 2.4, True), (W3, 4.1, 5.7, False), (W4, 4.1, 5.7, False)):
        d.vidrio(a, b, z0, z1, 2, 2); d.sombra(a, b, z1 - 0.2, z1); d.sombra(a, a + 0.2, z0, z1 - 0.2)    # muro grueso: hueco hondo
        d.r(a - 0.4, b + 0.4, z1, z1 + 0.22, "url(#p-viga)", "#000", 0.6)                 # cerramiento de madera
        d.r(a - 0.05, b + 0.05, z0 - 0.08, z0, "#d6d6d6", "#000", 0.5)
        if rej:
            for k in range(1, int((b - a) / 0.16)): d.ln(a + k * 0.16, z0, a + k * 0.16, z1, "#000", 1.3)
            d.ln(a, (z0 + z1) / 2, b, (z0 + z1) / 2, "#000", 1.3)
    d.vidrio(*ES, 3.9, 5.9, 1, 3); d.sombra(ES[0], ES[1], 5.7, 5.9); d.r(ES[0] - 0.3, ES[1] + 0.3, 5.9, 6.1, "url(#p-viga)", "#000", 0.6)
    d.r(PU[0] - 0.15, PU[1] + 0.15, 0, 2.75, "url(#p-madera)", "#000", 1); d.ln(4.8, 0, 4.8, 2.75, "#000", 1)
    for x in (4.45, 4.63, 4.97, 5.15):                                                  # clavos de la puerta
        for j in range(4): d.c(x, 0.5 + j * 0.6, 0.035, "#000")
    d.r(PU[0] - 0.5, PU[1] + 0.5, 2.75, 2.98, "url(#p-viga)", "#000", 0.6)
    for k in range(15): d.c(0.3 + k * 0.6, 6.5, 0.09, "#4a4a4a")                       # rollizos (puntas de las vigas)
    for g in (1.95, 7.35):                                                             # gárgolas
        d.r(g - 0.12, g + 0.12, 6.6, 6.78, "#3a3a3a"); d.ln(g, 6.6, g, 5.95, "#9a9a9a", 0.8)

def f_horizonte(d):
    d.r(0, 9, 0, 6.6, ESTUCO, "#000", 1.6)
    d.r(0.3, 8.7, 4.0, 6.25, "#8a8a8a", "#000", 1)                                     # franja corrida
    d.vidrio(*W3, 4.15, 6.1, 3); d.vidrio(*ES, 4.15, 6.1); d.vidrio(*W4, 4.15, 6.1, 3)
    d.sombra(0, 9, 2.95, 3.2); d.sombra(0, 9, 6.3, 6.6)
    d.r(-0.6, 9.6, 3.2, 3.45, NEGRO); d.r(-0.6, 9.6, 6.6, 6.95, NEGRO)                 # losas voladas 60 cm
    d.vidrio(*W1, 0.45, 2.85, 3); d.vidrio(*W2, 1.2, 2.85, 2); puerta_madera(d, z1=2.85)
    d.r(5.75, 9.35, 0, 0.6, "url(#p-concreto)", "#000", 1)                              # jardinera
    for k in range(7): d.c(6.0 + k * 0.5, 0.75, 0.17, "#7a7a7a")

def f_lamas(d):
    d.r(0, 9, 0, 6.9, ESTUCO, "#000", 1.6); d.r(0, 9, 0, 0.3, "#cfcfcf", "#000", 0.8)
    d.sombra(0.4, 8.95, 3.45, 3.65)
    d.r(0.25, 8.75, 3.65, 6.5, NEGRO); d.r(0.35, 8.65, 3.75, 6.4, VIDRIO)
    d.r(0.35, 8.65, 3.75, 6.4, "url(#p-lamas)")                                         # piel de lamas de aluminio
    for x in (3.0, 5.7): d.ln(x, 3.75, x, 6.4, NEGRO, 2)
    d.vidrio(*W1, 0.8, 2.6, 2); d.vidrio(*W2, 1.1, 2.6)
    d.r(PU[0] - 0.1, PU[1] + 0.1, 0, 3.0, NEGRO); d.r(PU[0], PU[1], 0, 2.9, "url(#p-madera)", "#000", 0.8); d.ln(PU[0] + 0.2, 0.7, PU[0] + 0.2, 2.2, "#fff", 2)

def f_concreto(d):
    d.r(0, 9, 0, 6.95, "url(#p-concreto)", "#000", 1.6)
    d.sombra(0.42, 3.72, 3.7, 3.9)
    d.r(0.3, 3.6, 3.9, 6.25, BLANCO, "#000", 1.4)                                       # cajón blanco
    d.vidrio(*W3, 4.2, 5.95); d.sombra(W3[0], W3[1], 5.8, 5.95); d.sombra(W3[0], W3[0] + 0.14, 4.2, 5.8)
    d.r(4.15, 5.45, 0, 6.5, NEGRO)                                                      # ranura de piso a techo
    d.r(PU[0], PU[1], 0, 2.6, "url(#p-madera)", "#000", 0.8); d.vidrio(*ES, 3.0, 6.35, 1, 1, "#555")
    d.vidrio(*W4, 4.2, 5.9, 1, 1, "#555"); d.vidrio(*W1, 1.0, 2.5, 1, 1, "#555"); d.vidrio(*W2, 1.1, 2.4, 1, 1, "#555")

DIBUJO = dict(zip(NOMBRES, [f_cantera, f_celosia, f_marco, f_duela, f_ladrillo, f_hacienda, f_horizonte, f_lamas, f_concreto]))
TEXTO = {
    "Cantera": "Planta baja de cantera, planta alta lisa y ventanas enmarcadas en cantera, con cornisa. Mexicana y sobria.",
    "Celosía": "Una celosía de barro tapa la recámara y la escalera: de día filtra el sol y de noche la casa brilla a través de ella.",
    "Marco": "La planta alta es una caja con marco negro que vuela sobre una planta baja forrada de madera.",
    "Duela": "Planta alta forrada de duela de madera, con postigos corredizos que se abren o se cierran según el sol. Planta baja blanca.",
    "Ladrillo": "Ladrillo aparente, cerramientos de ladrillo parado y una celosía de petatillo en la escalera.",
    "Hacienda": "Muros blancos gruesos, vigas de madera, herrería, rollizos y gárgolas. Lagunera de siempre.",
    "Horizonte": "Dos losas que vuelan 60 cm y una franja de ventanas corrida en la planta alta. Se ve larga y baja.",
    "Lamas": "Una piel de lamas de aluminio cubre toda la planta alta: da sombra y privacidad sin perder la vista.",
    "Concreto": "Concreto aparente con huella de cimbra, un cajón blanco en la ventana principal y una ranura de piso a techo en la entrada.",
}
SOMBRA_DE = {"Cantera": "ventanas remetidas en su marco", "Celosía": "la celosía", "Marco": "la caja, que vuela", "Duela": "los postigos",
             "Ladrillo": "el hueco hondo del ladrillo", "Hacienda": "el muro grueso y las vigas", "Horizonte": "las losas voladas",
             "Lamas": "las lamas", "Concreto": "el cajón y la ranura"}

def patio(d):
    """Costado derecho: bodega de servicio detrás de la reja de madera del patio de servicio."""
    d.r(9.0, 10.7, 0, 2.6, "#e4e4e4", "#000", 1.0)
    d.r(9.08, 10.62, 0, 2.15, "url(#p-madera)", "#000", 1.0)

def fachada(nombre):
    d = Dib(0.9, 7.5)
    patio(d); DIBUJO[nombre](d); d.suelo(-0.8, 11.2)
    w, h = (9 + 0.9 + 2.2) * S, 7.85 * S
    return f'<svg viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="Fachada {nombre}">' + "".join(d.o) + "</svg>"

def cuadra(n=6, calle_i=0, lado_norte=True, calle="Álamo"):
    """Elevación de una acera: n lotes seguidos, con los nogales en los linderos."""
    zt, mx = 11.8, 0.6
    tipos = [fachada_de(k, lado_norte, calle_i) for k in range(n)]
    o = []
    for k, t in enumerate(tipos):
        d = Dib(mx + k * LOTE_W + (LOTE_W - CASA_W) / 2, zt); patio(d); DIBUJO[t](d); o += d.o
        num = 2 * k + (1 if lado_norte else 2)
        o.append(f'<text x="{(mx + k * LOTE_W + LOTE_W / 2) * S:.0f}" y="{(zt + 0.75) * S:.0f}" font-size="26" font-weight="700" fill="#000" text-anchor="middle">{calle} {num} · {t}</text>')
    d = Dib(mx, zt)
    for k in range(n + 1):                                   # nogales en los linderos, delante de las casas
        x = k * LOTE_W
        d.ln(x, 0, x, 3.4, "#000", 4)
        d.o.append(f'<ellipse cx="{d.X(x):.1f}" cy="{d.Z(7.2):.1f}" rx="{4.4*S:.1f}" ry="{3.6*S:.1f}" fill="rgba(0,0,0,0.04)" stroke="#000" stroke-width="1" stroke-dasharray="5 4"/>')
    d.suelo(-mx, n * LOTE_W + mx)
    o += d.o
    w, h = (n * LOTE_W + 2 * mx) * S, (zt + 1.3) * S
    return f'<svg class="cuadra" viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="Una cuadra de {calle}">' + "".join(o) + "</svg>"


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
  svg .cuarto {{ fill: #fff; }} svg .cuarto.guardar {{ fill: #f1f1f1; }} svg .cuarto.bano {{ fill: #fafafa; }}
  svg .muroE {{ fill: #1a1a1a; }} svg .hueco {{ fill: #fff; }} svg .ventana {{ fill: #fff; stroke: #000; stroke-width: 0.8; }}
  svg .hoja {{ stroke: #000; stroke-width: 1.4; }} svg .arco {{ fill: none; stroke: #000; stroke-width: 0.6; stroke-dasharray: 3 2; }}
  svg .mueble {{ fill: #fff; stroke: #000; stroke-width: 0.9; }} svg .cubierta {{ fill: #e6e6e6; stroke: #000; stroke-width: 0.9; }}
  svg .closet {{ fill: #d9d9d9; stroke: #000; stroke-width: 0.9; }} svg .barra {{ stroke: #000; stroke-width: 0.8; stroke-dasharray: 5 3; }}
  svg .fino {{ stroke: #555; stroke-width: 0.5; fill: none; }} svg .fino2 {{ fill: none; stroke: #000; stroke-width: 0.7; }}
  svg .almohada {{ fill: #fff; stroke: #000; stroke-width: 0.6; }} svg .respaldo {{ fill: #cfcfcf; stroke: #000; stroke-width: 0.6; }}
  svg .silla {{ fill: #fff; stroke: #000; stroke-width: 0.6; }} svg .regadera {{ fill: #fff; stroke: #000; stroke-width: 0.9; }}
  svg .negro {{ fill: #000; }} svg .corte {{ stroke: #000; stroke-width: 1.2; }} svg .barandal {{ stroke: #000; stroke-width: 2; }}
  svg .m {{ font-size: 7.5px; fill: #333; }}
  svg text.r, svg text.a {{ paint-order: stroke; stroke: #fff; stroke-width: 3px; stroke-linejoin: round; }} svg text.inv {{ stroke: none; }}
  table.cuartos {{ max-width: none; }} table.cuartos td {{ vertical-align: top; }} table.cuartos td:nth-child(2), table.cuartos td:nth-child(3) {{ white-space: nowrap; text-align: right; }}
  td.izq, th.izq {{ text-align: left !important; }}
  .guardado {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 17rem), 1fr)); gap: 0.75rem 1.5rem; padding: 0; list-style: none; max-width: none; }}
  .guardado li {{ border-top: 2px solid var(--tinta); padding-top: 0.35rem; margin: 0; }} .guardado b {{ display: block; }}
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
  .fachadas {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 18rem), 1fr)); gap: 1.5rem 1.5rem; margin: 1rem 0; }}
  .fachadas figure {{ margin: 0; }} .fachadas figcaption {{ font-size: 0.875rem; margin-top: 0.375rem; }}
  .fachadas figcaption b {{ display: block; font-size: 1rem; }} .fachadas figcaption span {{ display: block; color: var(--gris); font-size: 0.8125rem; margin-top: 0.2rem; }}
  h3 {{ font-size: 1rem; margin: 1.5rem 0 0.5rem; }}
  .scroll {{ overflow-x: auto; }} svg.cuadra {{ min-width: 52rem; }}
  table {{ border-collapse: collapse; font-size: 0.875rem; font-variant-numeric: tabular-nums; width: 100%; max-width: 22rem; }}
  td {{ border-bottom: 1px solid var(--suave); padding: 0.2rem 0.3rem; }} td:last-child {{ text-align: right; }}
  ul {{ padding-left: 1.1rem; max-width: 44rem; }} li {{ margin: 0.3rem 0; }}
</style>
</head>
<body>
{DEFS}
<main class="doc">
  <nav class="nav" aria-label="Pestañas del proyecto">
    <a href="../">Nogaleras</a><a href="./">N6 · diseño</a><a href="acceso.html">Acceso</a><a href="casa.html" aria-current="page">Casa muestra</a><a href="servicios.html">Servicios</a><a href="terreno.html">Terreno</a><a href="base.html">N6 · base</a><a href="tamanos.html">N6 · tamaños</a>
  </nav>
  <h1>Casa muestra · Modelo Nogal <span>Un solo modelo para todo el fraccionamiento, con 9 fachadas distintas.</span></h1>
  <dl class="datos">
    <div><dt>Recámaras</dt><dd>4, cada una con clóset y baño</dd></div>
    <div><dt>Construcción</dt><dd>{m2_pb + m2_pa:.0f} m² en 2 niveles + bodega de {m2_bodega:.1f} m²</dd></div>
    <div><dt>Sala, comedor y cocina</dt><dd>{sala_m2:.0f} m² abiertos al portal</dd></div>
    <div><dt>Para guardar</dt><dd>{len(CP.GUARDADO)} lugares, 2 cuartos de blancos</dd></div>
    <div><dt>Portal techado</dt><dd>27 m²</dd></div>
    <div><dt>Jardín (sin casa ni cochera)</dt><dd>≈ {jardin:.0f} m²</dd></div>
    <div><dt>Cochera</dt><dd>2 autos</dd></div>
    <div><dt>Lotes donde cabe</dt><dd>{N_CABE:,} de {N_LOTES:,} ({100*N_CABE/N_LOTES:.0f} %)</dd></div>
  </dl>

  <h2>Por qué un solo modelo</h2>
  <p>Todos los lotes miden casi lo mismo: el promedio es de {M2_MEDIO:.0f} m², y {N_CABE:,} lotes miden al menos 12.0 × 24.0 m. La casa mide 9 m de ancho y deja 1.5 m o más libres a cada lado, así que entra igual en todos. Un solo juego de planos, de moldes y de compras: se construye más rápido y más barato. Los {N_LOTES - N_CABE} lotes que no la aceptan son remates angostos en las esquinas; conviene unirlos con el lote vecino o venderlos como lote sin casa.</p>
  <p>Las calles corren al ENE–OSO (rumbo 59°), así que los lotes solo pueden mirar de dos maneras: jardín al NNO o jardín al SSE. La casa es la misma en los dos casos y solo cambia la fachada que da a la calle.</p>

  <h2>Plantas amuebladas</h2>
  <p>Todas las medidas son <b>libres, a paño interior de muro</b>: lo que de verdad queda para los muebles. Muros exteriores de 20 cm y muros interiores de 12 cm. Los muebles están dibujados a escala con medidas comerciales.</p>
  <div class="dos">
    <div>{CP.planta("PB", f"Planta baja · {m2_pb:.0f} m²")}</div>
    <div>{CP.planta("PA", f"Planta alta · {m2_pa:.0f} m²")}</div>
  </div>
  <ul>
    <li><b>Cada recámara tiene el mismo orden: recámara, clóset de paso y baño.</b> Para llegar al baño se pasa por el clóset: se sale de bañar y se viste ahí, y la ropa no queda a la vista de la cama. Los 3 baños de enfrente quedan uno encima del otro, con la tubería en línea.</li>
    <li><b>La escalera sube hacia la fachada</b>, de la sala a la ventana alta del frente. Abajo, en la parte alta, queda el medio baño de visitas y, en la parte baja, una bodega. Arriba, el vacío de la escalera se ilumina con la ventana del frente.</li>
    <li><b>Entrada de servicio:</b> de la cochera al patio de servicio, a la lavandería y a la cocina. El mandado y la ropa sucia no cruzan la sala.</li>
    <li><b>La cocina es de dos frentes paralelos</b> con 1.70 m entre cubiertas, con el triángulo refri, parrilla y tarja a menos de 2 pasos, y se abre al comedor y a la sala.</li>
    <li><b>La recámara principal da al jardín</b> y vuela sobre el portal. Se entra por un recibidor; de la recámara se pasa al vestidor y del vestidor al baño.</li>
    <li><b>La estancia de arriba</b> sirve para tele o para trabajar en casa, lejos de la sala.</li>
  </ul>

  <h3>Medidas y muebles, cuarto por cuarto</h3>
  <h4>Planta baja</h4>
  {CP.tabla("PB")}
  <h4>Planta alta</h4>
  {CP.tabla("PA")}

  <h2 id="guardado">Dónde se guardan las cosas</h2>
  <p>Una casa con lugar para cada cosa se siente más grande y se mantiene ordenada sola. El Modelo Nogal tiene {len(CP.GUARDADO)} lugares para guardar, además de los gabinetes de cocina y baños:</p>
  <ul class="guardado">{"".join(f"<li><b>{esc(a)}</b>{esc(b)}</li>" for a, b in CP.GUARDADO)}</ul>
  <ul>
    <li><b>Clósets:</b> 60 cm de fondo libre, doble barra (camisas arriba y abajo), una sección de barra larga para vestidos y abrigos, cajonera de 4 cajones y maletero arriba hasta el techo. Puertas corredizas o abatibles de piso a techo para que no quede polvo encima.</li>
    <li><b>Baños:</b> regadera sin escalón, con piso a la coladera lineal y cancel fijo de cristal; nicho en el muro de la regadera; mueble de lavabo con cajones; WC lejos de la puerta; extractor y ventana alta en cada baño de enfrente.</li>
    <li><b>Blancos:</b> entrepaños de 45 cm (una toalla doblada en 3 cabe justa) a 35 cm entre sí; el de arriba, a 2.20 m para lo que se usa poco.</li>
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

  <h2 id="fachadas">Fachadas: 9 tipos, una sola casa</h2>
  <p>Detrás de las 9 fachadas está la misma casa: mismos muros, losas, instalaciones y huecos de ventana. Cambian el material, los marcos, los remates y lo que da sombra. Así cada casa tiene su identidad y la obra sigue siendo de un solo modelo.</p>
  <div class="fachadas">
{"".join(f'    <figure id="f-{slug(n)}">{fachada(n)}<figcaption><b>{i}. {n}</b> {TEXTO[n]} <span>Sombra: {SOMBRA_DE[n]}.</span></figcaption></figure>' + chr(10) for i, n in enumerate(NOMBRES, 1))}  </div>
  <h3>Así se ve una cuadra</h3>
  <div class="scroll">{cuadra()}</div>
  <ul>
    <li><b>Cada lote ya tiene su fachada asignada</b> (en el mapa, al tocar un lote). La regla: la casa de al lado y la de enfrente nunca repiten, y cada calle empieza la serie en otro punto. El mismo tipo vuelve a salir hasta 9 casas después.</li>
    <li><b>Sirven para las dos orientaciones.</b> Cada tipo ya trae su manera de dar sombra a las ventanas del frente. En las calles que reciben sol (lotes del lado norte, frente al SSE) esa protección trabaja; en las de sombra, da privacidad.</li>
    <li>Los nogales de los linderos quedan delante de las casas y unen la cuadra: de la calle se ve una arboleda con casas distintas, no una fila de casas iguales.</li>
  </ul>

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
