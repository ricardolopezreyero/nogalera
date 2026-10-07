# ======================= ACCESO Y BARDA (se ejecuta dentro de sitio.py) =======================
BT = SV["calles"]["barda_tramos"]; REJA_ACC = SV["calles"]["reja_acceso"]; CAM_PERIM = SV["calles"]["camaras_perim"]; CAM_CADA = SV["calles"]["cam_cada"]

def corte_barda_svg():
    """Corte de la barda tipo: cimiento, muro, dalas, cerca, pista y cámara del lado de adentro."""
    S = 60; W, H = 920, 470; x0 = 200; zg = 360
    X = lambda m: x0 + m * S; Z = lambda m: zg - m * S
    R = lambda a, b, c, d, cls: f'<rect x="{X(a):.1f}" y="{Z(d):.1f}" width="{(b-a)*S:.1f}" height="{(d-c)*S:.1f}" class="{cls}"/>'
    T = lambda x, y, t, cls="a", anc="middle": f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anc}">{t}</text>'
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Corte de la barda perimetral" class="esquema">']
    o.append(f'<rect x="0" y="{zg}" width="{W}" height="{H-zg}" class="tierra"/>')
    o.append(T(30, 22, "Corte de la barda tipo (muro ciego)", "r", "start"))
    o.append(T(60, zg - 10, "AFUERA", "r", "start")); o.append(T(W - 20, zg - 10, "ADENTRO · pista", "r", "end"))
    # cimiento corrido, cadena y muro
    o.append(R(-0.3, 0.3, -1.0, -0.4, "cimiento")); o.append(R(-0.075, 0.075, -0.4, -0.2, "dala")); o.append(R(-0.075, 0.075, -0.2, 3.0, "muroC"))
    for z in (1.4, 2.8): o.append(R(-0.075, 0.075, z, z + 0.2, "dala"))
    o.append(R(-0.1, 0.1, 3.0, 3.08, "remate"))
    for k in range(6): o.append(f'<line x1="{X(-0.05):.1f}" y1="{Z(3.1 + 0.1 * k):.1f}" x2="{X(0.05):.1f}" y2="{Z(3.1 + 0.1 * k):.1f}" class="cerca"/>')
    o.append(f'<line x1="{X(0):.1f}" y1="{Z(3.0):.1f}" x2="{X(0):.1f}" y2="{Z(3.7):.1f}" class="poste"/>')
    # pista y cámara
    o.append(R(0.075, 5.1, -0.1, 0, "pistaC")); o.append(T(X(2.6), Z(-0.25) + 12, "pista para correr · 5 m · ronda en bici", "c"))
    o.append(f'<line x1="{X(4.6):.1f}" y1="{Z(0):.1f}" x2="{X(4.6):.1f}" y2="{Z(6.0):.1f}" class="poste"/><rect x="{X(4.6)-12:.1f}" y="{Z(6.0):.1f}" width="14" height="7" class="lum"/>')
    o.append(T(X(4.9), Z(5.6), "cámara en poste de 6 m", "c", "start")); o.append(T(X(4.9), Z(5.2), "mira a lo largo del muro", "c", "start"))
    o.append(f'<line x1="{X(3.7):.1f}" y1="{Z(0):.1f}" x2="{X(3.7):.1f}" y2="{Z(0.9):.1f}" class="poste"/><rect x="{X(3.7)-3:.1f}" y="{Z(0.9):.1f}" width="6" height="4" class="lum"/>'); o.append(T(X(3.7), Z(1.15), "baliza", "c"))
    # cotas y rótulos
    o.append(f'<line x1="{X(-0.9):.1f}" y1="{Z(0):.1f}" x2="{X(-0.9):.1f}" y2="{Z(3.0):.1f}" class="cota"/>'); o.append(T(X(-1.0), Z(1.5), "3.0 m", "a", "end"))
    o.append(f'<line x1="{X(-0.9):.1f}" y1="{Z(3.0):.1f}" x2="{X(-0.9):.1f}" y2="{Z(3.7):.1f}" class="cota"/>'); o.append(T(X(-1.0), Z(3.35), "+0.6 cerca", "a", "end"))
    o.append(T(X(-1.0), Z(-0.7), "cimiento 60 × 40", "a", "end")); o.append(T(X(-1.0), Z(-0.3), "cadena de desplante", "a", "end"))
    o.append(T(X(0.25), Z(1.5), "block 15 cm · castillos K1 cada 3 m", "c", "start")); o.append(T(X(0.25), Z(1.2), "dala intermedia a 1.5 m", "c", "start")); o.append(T(X(0.25), Z(2.9), "dala de cerramiento 15 × 20", "c", "start"))
    o.append(T(X(0.25), Z(3.35), "6 hilos electrificados", "c", "start"))
    o.append(T(W / 2, H - 8, "Afuera: aplanado y pintura; adentro, los 5 m de pista separan la barda de todos los lotes: nadie puede brincar a un patio y el rondín ve el muro completo.", "a"))
    o.append("</svg>")
    return "\n".join(o)

def alzado_barda_svg():
    """Alzado de 12 m de muro ciego y 12 m de muro de identidad, lado a lado."""
    S = 30; W, H = 980, 250; x0 = 40; zg = 190
    X = lambda m: x0 + m * S; Z = lambda m: zg - m * S
    R = lambda a, b, c, d, cls: f'<rect x="{X(a):.1f}" y="{Z(d):.1f}" width="{(b-a)*S:.1f}" height="{(d-c)*S:.1f}" class="{cls}"/>'
    T = lambda x, y, t, cls="a", anc="middle": f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anc}">{t}</text>'
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Alzado de la barda" class="esquema">']
    o.append(f'<rect x="0" y="{zg}" width="{W}" height="{H-zg}" class="tierra"/>')
    o.append(T(X(6), 22, "Muro ciego · módulo de 12 m (norte, oriente, poniente)", "r")); o.append(T(X(21), 22, "Muro de identidad · módulo de 12 m (frente a la calzada)", "r"))
    o.append(R(0, 12, 0, 3.0, "muroA"))
    for k in range(5): o.append(R(3 * k - 0.075, 3 * k + 0.075, 0, 3.0, "castillo"))
    for z in (1.4, 2.8): o.append(R(0, 12, z, z + 0.2, "dalaA"))
    for k in range(6): o.append(f'<line x1="{X(0):.1f}" y1="{Z(3.1 + 0.1 * k):.1f}" x2="{X(12):.1f}" y2="{Z(3.1 + 0.1 * k):.1f}" class="cerca"/>')
    o.append(T(X(6), Z(1.5), "castillos cada 3 m · dalas a 1.5 y 3.0 m", "c"))
    o.append(R(15, 27, 0, 3.0, "muroA"))
    for k in range(3): o.append(R(15 + 6 * k - 0.2, 15 + 6 * k + 0.2, 0, 3.2, "pilastra"))
    o.append(R(15, 27, 3.0, 3.15, "remate"))
    for k in range(2): o.append(R(15.6 + 6 * k, 15.6 + 6 * k + 4.8, 0.6, 2.4, "reveal"))
    for k in range(6): o.append(f'<line x1="{X(15):.1f}" y1="{Z(3.25 + 0.1 * k):.1f}" x2="{X(27):.1f}" y2="{Z(3.25 + 0.1 * k):.1f}" class="cerca"/>')
    o.append(T(X(21), Z(1.5), "pilastras de 40 × 40 cada 6 m · paños rehundidos · remate", "c"))
    o.append(f'<line x1="{X(28):.1f}" y1="{Z(0):.1f}" x2="{X(28):.1f}" y2="{Z(3.0):.1f}" class="cota"/>'); o.append(T(X(28.3), Z(1.5), "3.0 m", "a", "start"))
    o.append("</svg>")
    return "\n".join(o)

def _dib_barda(o, X, Y, S, P):
    for f in _capa("barda_tramo"):
        lado = f["properties"]["lado"]; w = 5 if lado == "sur" else 2.6; dash = ' stroke-dasharray="9 4"' if lado == "poniente" else ""
        o.append(f'<polyline points="{P(_cuv(f))}" fill="none" stroke="#000" stroke-width="{w}"{dash}/>')
    for f in _capa("camara_perim"):
        u, v = _cuv(f)[0]; o.append(f'<circle cx="{X(u):.1f}" cy="{Y(v):.1f}" r="3" fill="#fff" stroke="#000" stroke-width="1.3"/>')
    for f in _capa("acceso_obra"):
        u, v = _cuv(f)[0]; o.append(f'<circle cx="{X(u):.1f}" cy="{Y(v):.1f}" r="8" fill="#000" stroke="#fff" stroke-width="2"/><text x="{X(u):.1f}" y="{Y(v) + 24:.1f}" class="pm-etiqueta" text-anchor="middle" font-weight="700">ACCESO DE OBRA · SALIDA DE EMERGENCIA</text>')
    if _acc_lonlat:
        ua, va = uv(*_acc_lonlat); o.append(f'<rect x="{X(ua) - 16:.1f}" y="{Y(va) - 6:.1f}" width="32" height="12" fill="#fff" stroke="#000" stroke-width="2"/><text x="{X(ua):.1f}" y="{Y(va) - 12:.1f}" class="pm-etiqueta" text-anchor="middle" font-weight="700">ACCESO</text>')
    for f in _capa("ptar_planta"): o.append(f'<polygon points="{P(_cuv(f))}" fill="#000"/>')
    for f in _capa("vaso"):
        cs = _cuv(f); cu = sum(c[0] for c in cs) / len(cs); cv = max(c[1] for c in cs)
        o.append(f'<text x="{X(cu):.1f}" y="{Y(cv) - 8:.1f}" class="pm-etiqueta" text-anchor="middle">vertedor del vaso en el muro norte</text>')

def acceso():
    man, tar = AC.man, AC.tar
    def fila(t, d):
        if d.get("espera_s") is None: return (t, f"{d['rho']*100:.0f} %", "<b>se satura</b>", "la fila no deja de crecer")
        return (t, f"{d['rho']*100:.0f} %", f"{d['espera_s']} s", f"{d['fila95']} autos · {d['fila95_m']} m")
    barda_total = sum(BT.values())
    tramos = [("Sur · frente a la calzada José Vasconcelos", "Muro de identidad: 3.0 m con pilastras cada 6 m, paños rehundidos y remate; 40 m de reja a cada lado del acceso; el nombre junto al acceso", f0(BT["sur"] - REJA_ACC), f0((BT["sur"] - REJA_ACC) * 6800 + REJA_ACC * 9500)),
              ("Poniente · calle Juan Agustín de Espinoza", "Los 13 lotes comerciales dan a la calle; la barda corre por detrás de ellos (hacia la pista), así que el perímetro seguro no se rompe", f0(BT["poniente"]), f0(BT["poniente"] * 5200)),
              ("Norte · calle del norte", "Muro ciego de 3.0 m; aquí van el acceso de obra (temporal) y la salida de emergencia, y el vertedor del vaso de tormentas", f0(BT["norte"]), f0(BT["norte"] * 5200)),
              ("Oriente · colindancia con otras huertas", "Muro ciego de 3.0 m, aplanado por fuera; la planta de tratamiento queda en esta punta", f0(BT["oriente"]), f0(BT["oriente"] * 5200))]
    leyenda = [("linea:5", "Muro de identidad (calzada)"), ("linea:2.6", "Muro ciego"), ("linea:2.6:9 4", "Muro ciego detrás del frente comercial"), ("circ", f"Cámara perimetral cada {CAM_CADA:.0f} m ({CAM_PERIM})"), ("negro", "Planta de tratamiento")]
    cuerpo = f"""
{kpis([("Entrada", "2 + 2 carriles", "residentes con tag · visitas y proveedores"), ("Salida", "1 + 1 carriles", "pluma arriba en la hora pico"), ("Plumas", f"a {AC.CASETA_V} m", "la fila queda dentro del terreno"), ("Pórtico", f"{AC.PORTICO_H} m libres", "pasan bomberos y mudanzas"),
       ("Espera del residente", f"≈ {tar['entrada_residentes_2_carriles']['espera_s']} s", "al entrar en la tarde"), ("Barda", f"{f0(barda_total)} m", "3.0 m + cerca electrificada"), ("Cámaras perimetrales", f"{CAM_PERIM}", f"una cada {CAM_CADA:.0f} m, del lado de la pista"), ("Acceso y barda", mill(SV['por_servicio']['Barda y accesos']), "en el presupuesto de urbanización")])}
<p class="frase"><b>La entrada es la cara del fraccionamiento y la barda es su seguridad.</b> La entrada se organiza en seis zonas, de la calzada a la mesa reductora, cada una con su medida y su función; la barda se resuelve por tramos, con la pista de 5 m por dentro como ronda y una cámara cada {CAM_CADA:.0f} m. Las dos se construyen completas en la etapa 1.</p>

<h2 id="revision">Lo que se revisó y lo que cambia</h2>
<ul>
<li><b>Se queda:</b> plumas a {AC.CASETA_V} m para que la fila de la hora pico no salga a la calle; súper, estacionamiento de visitas y acopio de basura fuera de las plumas; retorno antes de la caseta; salida con la pluma arriba de 6:30 a 9:00 y cámara de placas.</li>
<li><b>La calzada entra al proyecto.</b> Faltaba lo de afuera: carril de desaceleración de {AC.DESACEL} m para entrar por la derecha, bahía de vuelta izquierda de {AC.BAHIA} m para el que viene de Torreón y carril de aceleración de {AC.ACEL} m a la salida. Es proyecto vial con permiso municipal, y es lo que evita que la entrada se vuelva un cuello de botella en la calzada.</li>
<li><b>Umbral con identidad:</b> muro de identidad de 3.0 m con el nombre en letras de acero, {AC.REJA} m de reja a cada lado para que desde la calzada se vean los nogales de la plaza, y un pórtico de {AC.PORTICO_H} m libres sobre los carriles (un camión de bomberos mide 4.2 m; una mudanza, 4.3).</li>
<li><b>Una caseta principal, no dos iguales:</b> de 3 × 6 m entre residentes y visitas, con baño, lockers, monitoreo y cristal laminado; la de salida es de 2 × 3 m. Bolardos fijos delante y detrás de cada una.</li>
<li><b>Control sin fila:</b> el tag se lee a 10 m antes de la pluma (la pluma ya está abierta cuando el auto llega), cámara de placas en los 6 carriles, QR de la app para la visita registrada y lockers de paquetería en la plaza: el repartidor no entra. El segundo carril de visitas queda para proveedores y mudanzas.</li>
<li><b>Peatones y bicis</b> tienen su puerta con torniquete de cuerpo completo y lector; el que llega caminando al súper entra desde adentro sin pasar por la caseta.</li>
<li><b>La obra no pasa por la entrada.</b> Durante las etapas 1 a 4 los camiones y las mudanzas entran por un acceso de obra en la calle del norte, en el mismo claro que después queda como salida de emergencia. El acceso principal se estrena terminado, con sus nogales y su jardín, no como entrada de obra.</li>
<li><b>Con la luz cortada sigue funcionando:</b> planta de emergencia de 30 kVA para plumas, casetas, cámaras, cerca y alumbrado del acceso.</li>
<li><b>Mesa reductora</b> a los {AC.MESA_V} m: de la pluma al bulevar se entra a 30 km/h.</li>
</ul>

<h2 id="zonas">Las seis zonas de la entrada</h2>
{tabla([(f"<b>{n}</b>", e(t), e(d)) for n, t, d in AC.ZONAS], ["", "Zona", "Qué tiene"], "spec")}

<h2 id="plano">Plano</h2>
<div class="scroll sec plano-acceso">{AC.plano()}</div>
<ul>
<li><b>Se maneja por la derecha.</b> Los residentes entran por los 2 carriles del centro, con tag, y la pluma abre sola. Las visitas y los proveedores van por los 2 carriles de la derecha y se registran en la caseta principal, que queda entre los dos grupos de carriles.</li>
<li><b>Las plumas van a {AC.CASETA_V} m de la calle.</b> En el peor cuarto de hora de la tarde, 95 de cada 100 veces la fila es de {tar['entrada_residentes_2_carriles']['fila95']} autos o menos por carril de residentes y de {tar['entrada_visitas_2_carriles']['fila95']} o menos por carril de visitas (hasta {tar['entrada_visitas_2_carriles']['fila95_m']} m): nunca llega a la calle ni tapa la entrada del súper.</li>
<li><b>Retorno antes de las plumas:</b> la visita que no está registrada se regresa por el hueco de las islas sin dar reversa.</li>
<li>Pasando las plumas, la calle vuelve a ser de 2 carriles, con la mesa reductora, y entra al bulevar.</li>
</ul>

<h2 id="alzado">Alzado desde la calzada</h2>
<div class="scroll sec alzado-acceso">{AC.alzado()}</div>
<p>Lo que ve el que pasa por la calzada: el muro de identidad con el nombre, la reja con los nogales atrás, el pórtico con las letras y, al fondo, las casetas. Postes de 9 m en las dos orillas del acceso y el letrero iluminado (ya contados en <a href="/iluminacion/">Iluminación</a>).</p>

<h2 id="control">Control y operación</h2>
{tabla([("Residentes", "Tag RFID UHF en el parabrisas (uno por auto registrado); lectura a 10 m; la pluma abre antes de llegar. Si el tag falla, cámara de placas y lista blanca."),
        ("Visitas", "Pre-registro en la app: QR que la visita muestra en el lector del carril; sin registro, el guardia pide identificación, toma foto de la placa y avisa a la casa por interfón."),
        ("Proveedores y mudanzas", "Carril ancho de la derecha; horario de 8 a 18; mudanzas con cita y depósito; durante la obra, por el acceso del norte."),
        ("Paquetería", "Lockers inteligentes en la plaza; el repartidor deja y la app avisa. Comida a domicilio: entrega en la plaza o pasa como visita con QR."),
        ("Peatones y bicis", "Torniquete de cuerpo completo con el mismo tag o la app; puerta ancha para bicis y carriolas con el guardia."),
        ("Salida", "Pluma arriba de 6:30 a 9:00 con cámara de placas; el resto del día abre con el tag. Vuelta a la izquierda hacia Torreón: pedir semáforo o glorieta con el estudio de impacto vial."),
        ("Guardias", "2 por turno en la caseta y 1 de rondín (ya en la cuota de mantenimiento); monitoreo de las cámaras del acceso y del perímetro desde la caseta principal."),
        ("Emergencias", "Cerradura de bomberos en la salida de emergencia; las plumas se abren a mano sin luz; planta de emergencia con transferencia automática.")], ["Quién", "Cómo"], "spec")}

<h2 id="calculo">Cálculo de hora pico</h2>
<p>Viajes por casa en la hora pico: 0.85 en la mañana (75 % salen) y 1.0 en la tarde (63 % entran): tasas de tráfico residencial de casas solas, un poco arriba por la ida a la escuela. Se usa el cuarto de hora más cargado (factor 0.85). Visitas, servicios y apps: 15 % de lo que entra y 8 % de lo que sale. Las cuentas son por carril, con un modelo de colas conservador.</p>
<h3>Tarde · entrada ({tar['entran_h']} autos/h)</h3>
{tabla([fila(f"Residentes, 1 carril ({tar['res_entran']}/h)", tar['entrada_residentes_1_carril']), fila("Residentes, <b>2 carriles</b>", tar['entrada_residentes_2_carriles']),
        fila(f"Visitas, 1 carril ({tar['vis_entran']}/h)", tar['entrada_visitas_1_carril']), fila("Visitas, <b>2 carriles</b>", tar['entrada_visitas_2_carriles'])], ["", "Ocupación", "Espera media", "Fila (95 %)"])}
<h3>Mañana · salida ({man['salen_h']} autos/h)</h3>
{tabla([fila(f"Residentes, 1 carril con pluma ({man['res_salen']}/h)", man['salida_residentes_pluma']), fila("Residentes, 1 carril, <b>pluma arriba en hora pico</b>", man['salida_residentes_libre']),
        fila(f"Visitas, 1 carril ({man['vis_salen']}/h)", man['salida_visitas_1_carril'])], ["", "Ocupación", "Espera media", "Fila (95 %)"])}
<p>Capacidad por carril: residentes con tag, {AC.CAP['res_entra']} autos/h (6 s por auto); visitas con registro en caseta, {AC.CAP['vis_entra_registro']}/h (40 s), o {AC.CAP['vis_entra_qr']}/h con QR de la app (15 s); salida con pluma, {AC.CAP['res_sale_pluma']}/h; con la pluma arriba, {AC.CAP['res_sale_libre']}/h. Cada auto ocupa {AC.AUTO_M} m de fila. Con los lockers y el QR, la carga de los carriles de visitas baja más todavía: el segundo carril es holgura para proveedores y mudanzas.</p>

<h2 id="barda">La barda perimetral</h2>
<figure><div class="scroll sec"><div class="dibujo">{plano_red_svg("Barda perimetral por tramos, cámaras cada 60 m, acceso, acceso de obra y salida de emergencia", _dib_barda, leyenda)}</div></div>
<figcaption><b>{f0(barda_total)} m de barda y la pista por dentro.</b> Los 5 m de pista separan la barda de todos los lotes: ningún patio toca el muro, el rondín en bicicleta recorre los 3.3 km viendo el muro completo, y las {CAM_PERIM} cámaras en postes de 6 m miran a lo largo de él con analítica de cruce de línea.</figcaption></figure>
{tabla(tramos, ["Tramo", "Solución", "Largo (m)", "Importe (MXN)"], "spec", ("<b>Total</b>", "", f"<b>{f0(barda_total)}</b>", f"<b>${f0((BT['sur'] - REJA_ACC) * 6800 + REJA_ACC * 9500 + (BT['poniente'] + BT['norte'] + BT['oriente']) * 5200)}</b>"))}
<h3>Cómo está hecha</h3>
<div class="scroll sec"><div class="dibujo">{corte_barda_svg()}</div></div>
<div class="scroll sec"><div class="dibujo">{alzado_barda_svg()}</div></div>
<ul>
<li><b>Estructura:</b> cimiento corrido de mampostería o concreto de 60 × 40 cm, cadena de desplante, block de concreto de 15 cm, castillos K1 cada 3 m (en el muro de identidad, pilastras de 40 × 40 cada 6 m), dala intermedia a 1.5 m y dala de cerramiento de 15 × 20. La dala intermedia es la que aguanta las tolvaneras de Torreón en un muro de 3 m; sin ella se agrieta.</li>
<li><b>Altura:</b> 3.0 m de muro más 0.6 m de cerca electrificada de 6 hilos, con energizadores por sector de 500 m, batería y alarma a la caseta: 3.6 m en total. Afuera va aplanado y pintado; en la calzada, con pilastras, paños rehundidos y remate.</li>
<li><b>Vigilancia:</b> {CAM_PERIM} cámaras fijas con infrarrojo cada {CAM_CADA:.0f} m del lado de la pista, con fibra a la caseta, más las balizas de la pista cada 20 m y la ronda. La cerca y las cámaras se instalan en la etapa 1 completas: protegen la obra desde el primer día.</li>
<li><b>Agua:</b> el drenaje pluvial no cruza la barda salvo en el vertedor del vaso de tormentas, en el muro norte, que solo trabaja en tormentas de más de 50 años. Lo de afuera no entra: el terreno de la huerta queda al mismo nivel y la calle del norte más baja.</li>
<li><b>Frente comercial:</b> los 13 lotes que dan a Espinoza tienen su fachada a la calle y su propia barda al fondo; la barda del fraccionamiento corre por detrás de ellos, pegada a la pista, así que la seguridad no depende de los comercios.</li>
</ul>

<h2 id="presupuesto">Lo que cuesta el acceso y la barda</h2>
{partidas(["Barda y accesos"])}
<p class="nota">Por confirmar: el derecho de vía entre el terreno y la calzada (≈ 30 m) y el permiso de conexión y de los carriles en la calzada (estudio de impacto vial); las colindancias del oriente y del norte; la mecánica de suelos para el cimiento de la barda. El cálculo de hora pico está en <code>pipeline/scripts/n6_acceso_calc.py</code> y las cantidades en <code>n6_servicios.py</code>.</p>
"""
    pagina("acceso", "Acceso y barda", "05 · Acceso y barda", f"La entrada en seis zonas, de la calzada a la mesa reductora, calculada para la hora pico de las {f0(N)} casas; y la barda de {f0(barda_total)} m por tramos, con la pista por dentro como ronda y una cámara cada {CAM_CADA:.0f} m.", cuerpo,
           [("revision", "Lo que cambia"), ("zonas", "Las seis zonas"), ("plano", "Plano"), ("alzado", "Alzado"), ("control", "Control y operación"), ("calculo", "Hora pico"), ("barda", "La barda"), ("presupuesto", "Lo que cuesta")],
           descripcion="La entrada y la barda perimetral de La Nogalera: zonas, carriles, pórtico, casetas, control, hora pico, tramos de barda y su estructura.")
