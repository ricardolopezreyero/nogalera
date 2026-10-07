"""N6 · página de la entrada: plano a escala del acceso y cálculo de hora pico → public/n6/acceso.html"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from n6_acceso_calc import res, CARRILES, CASETA_V, ISLA_V0, RETORNO, ANCHO, CAP, CASAS, AUTO_M
OUT = sys.argv[1] if len(sys.argv) > 1 else "../public/n6/acceso.html"
man, tar = res["mañana (7 a 8)"], res["tarde (6 a 7 pm)"]

def plano(S=9):
    u0, u1 = ANCHO[0] - 52, ANCHO[1] + 55          # súper a la izquierda, estacionamiento de visitas a la derecha
    v0, v1 = -32, CASETA_V + 32
    pad = 20
    w, h = (u1 - u0) * S + 2 * pad, (v1 - v0) * S + 2 * pad
    X = lambda u: pad + (u - u0) * S; Y = lambda v: pad + (v1 - v) * S
    R = lambda a, b, c, d, cls, extra="": f'<rect x="{X(a):.1f}" y="{Y(d):.1f}" width="{(b-a)*S:.1f}" height="{(d-c)*S:.1f}" class="{cls}" {extra}/>'
    T = lambda u, v, t, cls="a", anc="middle", rot=None: (f'<text x="{X(u):.1f}" y="{Y(v):.1f}" class="{cls}" text-anchor="{anc}"' + (f' transform="rotate({rot} {X(u):.1f} {Y(v):.1f})"' if rot else "") + f'>{t}</text>')
    o = [f'<svg viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="Plano de la entrada">',
         '<defs><marker id="fl" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0L10,5L0,10z" fill="#000"/></marker></defs>']
    o.append(R(u0, u1, v0, -18, "calzada")); o.append(T((u0 + u1) / 2, -26, "CALZADA JOSÉ VASCONCELOS (derecho de vía por confirmar)", "r"))
    o.append(R(u0, u1, -18, 0, "franja")); o.append(T(u0 + 2, -9, "franja entre la calzada y el terreno", "a", "start"))
    o.append(R(u0, u1, 0, 5, "pista")); o.append(T(u0 + 2, 1.5, "pista para correr", "a", "start"))
    o.append(R(ANCHO[0] - 48, ANCHO[0] - 4, 8, 30, "super")); o.append(T(ANCHO[0] - 26, 20, "MINI SÚPER", "r inv"))
    o.append(T(ANCHO[0] - 26, 15.5, "abre a la calle", "a inv"))
    o.append(R(ANCHO[1] + 4, ANCHO[1] + 51, 8, 28, "estac")); o.append(T(ANCHO[1] + 27.5, 19, "estacionamiento", "a")); o.append(T(ANCHO[1] + 27.5, 15.5, "visitas y súper", "a"))
    # carriles
    o.append(R(ANCHO[0], ANCHO[1], -18, CASETA_V + 25, "asfalto"))
    for n, a, b, t in CARRILES:
        cx = (a + b) / 2
        if t == "isla":
            o.append(R(a, b, ISLA_V0, RETORNO[0], "isla")); o.append(R(a, b, RETORNO[1], CASETA_V + 6, "isla"))
            o.append(R(a + 0.3, b - 0.3, CASETA_V - 2.5, CASETA_V + 2.5, "caseta"))
        elif t == "peaton":
            o.append(R(a, b, -18, CASETA_V + 25, "banq")); o.append(T(cx, CASETA_V - 18, "puerta peatonal", "a", rot=-90))
        else:
            o.append(f'<line x1="{X(a+0.2):.1f}" y1="{Y(CASETA_V):.1f}" x2="{X(b-0.4):.1f}" y2="{Y(CASETA_V):.1f}" class="pluma"/>')
            y1, y2 = (8, 20) if t == "entra" else (20, 8)
            o.append(f'<line x1="{X(cx):.1f}" y1="{Y(y1):.1f}" x2="{X(cx):.1f}" y2="{Y(y2):.1f}" class="fl" marker-end="url(#fl)"/>')
            o.append(T(cx + 0.55, CASETA_V - 24, n.replace("Entrada residentes", "residentes").replace("Entrada visitas", "visitas").replace("Salida ", "sale "), "c", rot=-90))
    for (n1, a1, b1, t1), (n2, a2, b2, t2) in zip(CARRILES[:-1], CARRILES[1:]):
        if t1 == t2 and t1 in ("entra", "sale"):
            o.append(f'<line x1="{X(b1):.1f}" y1="{Y(-16):.1f}" x2="{X(b1):.1f}" y2="{Y(CASETA_V+10):.1f}" class="div"/>')
    # filas en hora pico (95 %) frente a las plumas
    for n, a, b, t in CARRILES:
        if n.startswith("Entrada residentes"): L = tar["entrada_residentes_2_carriles"]["fila95_m"]
        elif n.startswith("Entrada visitas"): L = tar["entrada_visitas_2_carriles"]["fila95_m"]
        else: continue
        o.append(R(a + 0.6, b - 0.6, CASETA_V - L, CASETA_V - 0.5, "fila"))
    o.append(f'<path d="M{X(9):.1f},{Y(RETORNO[0]+2):.1f} C{X(9):.1f},{Y(RETORNO[1]+4):.1f} {X(-12):.1f},{Y(RETORNO[1]+4):.1f} {X(-12):.1f},{Y(RETORNO[0]):.1f}" class="ret" marker-end="url(#fl)"/>')
    o.append(T(-1.5, RETORNO[1] + 7.5, "retorno", "a"))
    o.append(T(ANCHO[1] + 3, CASETA_V + 1, f"plumas y casetas a {CASETA_V} m", "a", "start"))
    o.append(T(ANCHO[1] + 3, CASETA_V - 30, "en gris: fila de la", "a", "start")); o.append(T(ANCHO[1] + 3, CASETA_V - 32.2, "hora pico (95 %)", "a", "start"))
    o.append(T(ANCHO[1] + 3, CASETA_V + 16, "↑ al fraccionamiento:", "a", "start")); o.append(T(ANCHO[1] + 3, CASETA_V + 13.8, "calle de 2 carriles", "a", "start"))
    o.append(f'<line x1="{X(ANCHO[0]-1.5):.1f}" y1="{Y(0):.1f}" x2="{X(ANCHO[0]-1.5):.1f}" y2="{Y(CASETA_V):.1f}" class="cota"/>')
    o.append(T(ANCHO[0] - 2.4, CASETA_V - 12, f"{CASETA_V} m", "a", rot=-90))
    o.append(f'<line x1="{X(ANCHO[0]):.1f}" y1="{Y(CASETA_V+20):.1f}" x2="{X(ANCHO[1]):.1f}" y2="{Y(CASETA_V+20):.1f}" class="cota"/>')
    o.append(T((ANCHO[0] + ANCHO[1]) / 2, CASETA_V + 21.5, f"{ANCHO[1]-ANCHO[0]:.0f} m", "a"))
    o.append("</svg>")
    return "\n".join(o)

def fila(t, d):
    if d.get("espera_s") is None: return f"<tr><td>{t}</td><td>{d['rho']*100:.0f} %</td><td colspan=2><b>se satura</b>: la fila no deja de crecer</td></tr>"
    return f"<tr><td>{t}</td><td>{d['rho']*100:.0f} %</td><td>{d['espera_s']} s</td><td>{d['fila95']} autos · {d['fila95_m']} m</td></tr>"

HTML = f"""<!doctype html>
<html lang="es-MX">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>N6 · Acceso</title>
<meta name="description" content="Entrada de N6: 2 carriles de residentes y 2 de visitas para entrar, 1 y 1 para salir, calculada para la hora pico.">
<link rel="icon" href="../favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="../style.css">
<style>
  html, body {{ height: auto; }} body {{ background: var(--papel); }}
  .doc {{ max-width: 64rem; margin: 0 auto; padding: 1rem 1rem 3rem; }}
  .nav {{ display: flex; flex-wrap: wrap; border: 1px solid var(--linea); margin-bottom: 1rem; max-width: 42rem; }}
  .nav a {{ flex: 1 0 auto; text-align: center; padding: 0.35rem 0.5rem; text-decoration: none; font-size: 0.8125rem; border-right: 1px solid var(--linea); }}
  .nav a:last-child {{ border-right: 0; }} .nav a[aria-current="page"] {{ background: var(--tinta); color: var(--papel); }}
  h1 {{ font-size: 1.75rem; margin: 0 0 0.25rem; }} h1 span {{ display: block; font-size: 0.9375rem; font-weight: 400; color: var(--gris); }}
  h2 {{ font-size: 1.0625rem; margin: 2rem 0 0.5rem; border-top: 1px solid var(--linea); padding-top: 0.75rem; }}
  p, ul {{ max-width: 46rem; }} li {{ margin: 0.3rem 0; }}
  .datos {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr)); gap: 0.5rem 1rem; margin: 1rem 0; }}
  .datos div {{ border-top: 2px solid var(--tinta); padding-top: 0.3rem; }} .datos dt {{ font-size: 0.75rem; color: var(--gris); }} .datos dd {{ margin: 0; font-weight: 700; }}
  .scroll {{ overflow-x: auto; }}
  svg {{ width: 100%; min-width: 40rem; height: auto; display: block; font-family: inherit; }}
  svg .a {{ font-size: 14px; fill: #333; }} svg .r {{ font-size: 16px; font-weight: 700; fill: #000; }} svg .c {{ font-size: 12px; fill: #000; }} svg .inv {{ fill: #fff; }}
  svg .calzada {{ fill: #bdbdbd; }} svg .franja {{ fill: #ececec; }} svg .pista {{ fill: #fff; stroke: #000; stroke-width: 0.6; stroke-dasharray: 3 2; }}
  svg .asfalto {{ fill: #d6d6d6; }} svg .isla {{ fill: #fff; stroke: #000; stroke-width: 1; }} svg .caseta {{ fill: #000; }}
  svg .banq {{ fill: #f2f2f2; stroke: #000; stroke-width: 0.6; }} svg .super {{ fill: #111; }} svg .estac {{ fill: #fff; stroke: #000; stroke-width: 0.8; stroke-dasharray: 4 2; }}
  svg .pluma {{ stroke: #000; stroke-width: 2.5; }} svg .div {{ stroke: #fff; stroke-width: 1.2; stroke-dasharray: 6 5; }}
  svg .fl {{ stroke: #000; stroke-width: 1.2; }} svg .fila {{ fill: rgba(0,0,0,0.18); }} svg .ret {{ fill: none; stroke: #000; stroke-width: 1; stroke-dasharray: 4 3; }}
  svg .cota {{ stroke: #000; stroke-width: 0.6; }}
  table {{ border-collapse: collapse; font-size: 0.875rem; font-variant-numeric: tabular-nums; width: 100%; max-width: 46rem; margin: 0.5rem 0 1rem; }}
  th, td {{ border-bottom: 1px solid var(--suave); padding: 0.25rem 0.35rem; text-align: right; }} th:first-child, td:first-child {{ text-align: left; }}
  th {{ font-size: 0.75rem; color: var(--gris); font-weight: 400; }}
  .nota {{ color: var(--gris); font-size: 0.8125rem; }}
</style></head>
<body><main class="doc">
  <nav class="nav" aria-label="Pestañas del proyecto">
    <a href="../">Nogaleras</a><a href="./">N6 · diseño</a><a href="acceso.html" aria-current="page">Acceso</a><a href="casa.html">Casa muestra</a><a href="terreno.html">Terreno</a><a href="base.html">N6 · base</a><a href="tamanos.html">N6 · tamaños</a>
  </nav>
  <h1>Acceso <span>Entran 2 carriles de residentes y 2 de visitas. Salen 1 de residentes y 1 de visitas.</span></h1>
  <dl class="datos">
    <div><dt>Casas</dt><dd>{CASAS:,}</dd></div>
    <div><dt>Hora pico de la tarde</dt><dd>{tar['entran_h']} autos entran</dd></div>
    <div><dt>Hora pico de la mañana</dt><dd>{man['salen_h']} autos salen</dd></div>
    <div><dt>Espera del residente</dt><dd>≈ {tar['entrada_residentes_2_carriles']['espera_s']} s al entrar</dd></div>
    <div><dt>Casetas</dt><dd>a {CASETA_V} m de la calle</dd></div>
    <div><dt>Ancho del acceso</dt><dd>{ANCHO[1]-ANCHO[0]:.0f} m</dd></div>
  </dl>

  <h2>Plano</h2>
  <div class="scroll">{plano()}</div>
  <ul>
    <li><b>Se maneja por la derecha.</b> Los residentes entran por los 2 carriles del centro, con tag, y la pluma abre sola. Las visitas van por los 2 carriles de la derecha y se registran en la caseta, que queda entre los dos grupos de carriles.</li>
    <li><b>Las plumas van a {CASETA_V} m de la calle.</b> En el peor cuarto de hora de la tarde, 95 de cada 100 veces la fila es de {tar['entrada_residentes_2_carriles']['fila95']} autos o menos por carril de residentes y de {tar['entrada_visitas_2_carriles']['fila95']} o menos por carril de visitas (hasta {tar['entrada_visitas_2_carriles']['fila95_m']} m), así que nunca llega a la calle ni tapa la entrada del súper.</li>
    <li><b>Retorno antes de las plumas:</b> la visita que no está registrada se regresa por el hueco de las islas sin dar reversa y sin estorbar a nadie.</li>
    <li><b>El súper y su estacionamiento quedan antes de las plumas.</b> Sus clientes de afuera no pasan por la caseta. Los vecinos llegan caminando por la puerta peatonal.</li>
    <li><b>Salida 1 + 1.</b> En la salida de residentes, de 6:30 a 9:00 la pluma se queda arriba y una cámara lee las placas. El resto del día abre con el tag.</li>
    <li>Pasando las plumas, la calle de acceso vuelve a ser de 2 carriles, como el resto del fraccionamiento.</li>
  </ul>

  <h2>Cálculo de hora pico</h2>
  <p>Viajes por casa en la hora pico: 0.85 en la mañana (75 % salen) y 1.0 en la tarde (63 % entran). Son tasas de tráfico residencial de casas solas, ajustadas un poco hacia arriba por la ida a la escuela. Se usa el cuarto de hora más cargado (factor 0.85). Visitas, servicios y apps: 15 % de lo que entra y 8 % de lo que sale. Las cuentas son por carril, con un modelo de colas conservador.</p>
  <table>
    <tr><th>Tarde · entrada ({tar['entran_h']} autos/h)</th><th>Ocupación</th><th>Espera media</th><th>Fila (95 %)</th></tr>
    {fila(f"Residentes, 1 carril ({tar['res_entran']}/h)", tar['entrada_residentes_1_carril'])}
    {fila("Residentes, <b>2 carriles</b>", tar['entrada_residentes_2_carriles'])}
    {fila(f"Visitas, 1 carril ({tar['vis_entran']}/h)", tar['entrada_visitas_1_carril'])}
    {fila("Visitas, <b>2 carriles</b>", tar['entrada_visitas_2_carriles'])}
  </table>
  <table>
    <tr><th>Mañana · salida ({man['salen_h']} autos/h)</th><th>Ocupación</th><th>Espera media</th><th>Fila (95 %)</th></tr>
    {fila(f"Residentes, 1 carril con pluma ({man['res_salen']}/h)", man['salida_residentes_pluma'])}
    {fila("Residentes, 1 carril, <b>pluma arriba en hora pico</b>", man['salida_residentes_libre'])}
    {fila(f"Visitas, 1 carril ({man['vis_salen']}/h)", man['salida_visitas_1_carril'])}
  </table>
  <p>Capacidad por carril: residentes con tag, {CAP['res_entra']} autos/h (6 s por auto); visitas con registro en caseta, {CAP['vis_entra_registro']}/h (40 s), o {CAP['vis_entra_qr']}/h si el visitante trae un QR de la app del fraccionamiento (15 s); salida con pluma, {CAP['res_sale_pluma']}/h; salida con la pluma arriba, {CAP['res_sale_libre']}/h. Cada auto ocupa {AUTO_M} m de fila.</p>
  <ul>
    <li><b>Un solo carril de residentes no alcanza:</b> en la tarde llegan {tar['res_entran']} autos/h a un carril que da para {CAP['res_entra']}, y la fila nunca se vacía. Con 2 carriles se espera unos segundos.</li>
    <li><b>Visitas: 2 carriles.</b> Uno solo se satura en la tarde si cada registro tarda 40 s. Si se usa QR (el residente registra a su visita desde el celular), con un carril bastaría: el segundo puede quedar para paquetería y apps.</li>
    <li><b>La salida de la mañana es el punto fino:</b> con pluma, la fila llega a {man['salida_residentes_pluma']['fila95_m']} m dentro del fraccionamiento. Con la pluma arriba en hora pico baja a {man['salida_residentes_libre']['fila95_m']} m.</li>
  </ul>
  <p class="nota">Por confirmar: el derecho de vía entre el terreno y la Calzada José Vasconcelos (≈ 30 m) y el permiso de conexión con el municipio. La vuelta a la izquierda para salir a la calzada es lo que más puede frenar la salida; conviene pedir semáforo o una glorieta en ese cruce. El reglamento suele pedir una salida de emergencia, que puede ser una reja cerrada en el lado norte del terreno.</p>
</main></body></html>
"""
open(OUT, "w").write(HTML)
print("ok", OUT)
