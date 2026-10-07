# ======================= LA OPERADORA, PARA EL INVERSIONISTA Y PARA EL COMERCIALIZADOR (se ejecuta dentro de sitio.py) =======================
# Todo sale de n6_fideicomiso.py (MOD, CON, ESCEN) y de los datos del plano (LOTES, SV). Pesos de 2026, antes de impuestos.
FL = MOD["flujo"]; ULT = FL[-1]
TARIFA_AGUA = FI.AGUA_FIJA + FI.AGUA_M3 * FI.CONSUMO_M3
COSTO_FIJO_DET = [("Seguridad 24 horas", "2 guardias por turno en la caseta y 1 rondín, 3 turnos (9 personas), con prestaciones", 168_000),
                  ("Monitoreo y app", f"central de cámaras ({SV['calles']['camaras_perim']} perimetrales + acceso), app de visitas y tarjetas", 22_000),
                  ("Administración", "gerente de la operadora, contador, cobranza y atención a vecinos", 70_000),
                  ("Seguros y legal", "responsabilidad civil, áreas comunes, equipo", 20_000),
                  ("Vehículo, radios y uniformes", "camioneta de rondín, combustible, radios, uniformes", 20_000),
                  ("Oficina e imprevistos", "oficina en el acceso, papelería, contingencias", 20_000)]
assert abs(sum(c for *_, c in COSTO_FIJO_DET) - FI.COSTO_FIJO_OPER) < 1
COSTO_VAR_DET = [("Jardinería y riego de los nogales", 110), ("Pintura y reparaciones: bardas, mobiliario, pórtico, señales", 120), ("Alumbrado: energía y mantenimiento", 100),
                 ("Planta de tratamiento: operador, energía, químicos, lodos", 80), ("Club, pista y canchas", 40), ("Barrido y basura de áreas comunes", 40), ("Tecnología y cobranza", 30)]
assert abs(sum(c for _, c in COSTO_VAR_DET) - FI.COSTO_VAR_CASA) < 1
COSTO_AGUA_DET = [("Energía de bombeo (pozos y presión de red)", 95), ("Cloración y análisis de laboratorio", 25), ("Operador y mantenimiento de equipos", 60), ("Depreciación de pozos, cisterna y red a 25 años", 120)]
assert abs(sum(c for _, c in COSTO_AGUA_DET) - FI.COSTO_AGUA_CASA) < 1
M_CUOTA_INI = next(f["mes"] for f in FL if f["cuota_ing"] > 0)
M_OPER_POS = next((f["mes"] for f in FL if f["mes"] >= 12 and f["oper_margen"] > 0 and all(g["oper_margen"] > 0 for g in FL[f["mes"]:f["mes"] + 6])), None)
NUEZ_ANIO = FI.N_NOGALES * FI.NUEZ_KG_ARBOL * FI.PRECIO_NUEZ
VALOR_OPER = OPER_ANIO * 6                 # referencia: una administradora con contrato se vende a 6 veces su margen anual

def operadora_html():
    """La sección de la operadora dentro de Números y fideicomiso."""
    fm = lambda x: "—" if abs(x) < 5e4 else (f"−{mill(-x, 1)}" if x < 0 else mill(x, 1))
    anios = []
    for a in range(10):
        fa = [f for f in FL if a * 12 <= f["mes"] < (a + 1) * 12]
        anios.append((f"Año {a + 1}", f0(fa[-1]["casas"]), f0(fa[-1]["baldios"]), fm(sum(f["cuota_ing"] for f in fa)), fm(sum(f["agua_ing"] for f in fa)), fm(sum(f["nuez"] for f in fa)),
                      fm(sum(f["oper_costo"] for f in fa)), fm(sum(f["reserva"] for f in fa)), f"<b>{fm(sum(f['oper_margen'] for f in fa))}</b>"))
    casa_mes = [("Cuota de mantenimiento y seguridad", f"${f0(FI.CUOTA_CASA)}"), ("Agua: ${:,.0f} fijos + ${:,.0f}/m³ × {:,.0f} m³".format(FI.AGUA_FIJA, FI.AGUA_M3, FI.CONSUMO_M3), f"${f0(TARIFA_AGUA)}"),
                ("<b>Total que paga una casa al mes</b>", f"<b>${f0(FI.CUOTA_CASA + TARIFA_AGUA)}</b>"), ("Lote baldío (sin agua)", f"${f0(FI.CUOTA_LOTE)}")]
    return f"""
<p><b>La cuota no es un gasto que se reparte: es una empresa.</b> La operadora, nuestra, firma un contrato de administración con el fraccionamiento y cobra <b>${f0(FI.CUOTA_CASA)} al mes por casa habitada</b> y <b>${f0(FI.CUOTA_LOTE)} por lote baldío</b> (desde que se escritura: el lote ya tiene calle, luz, barda y nogales regados), más <b>el agua por tarifa</b>. A cambio da seguridad las 24 horas, el fraccionamiento pintado y reparado, los nogales regados y podados, el alumbrado, la planta, el club y la pista. Lo que cuesta dar eso está medido abajo, partida por partida; lo que sobra es el margen de la operadora, y el 10 % de la cuota va a un fondo de reserva que es de los vecinos.</p>
{kpis([("Cuota por casa", f"${f0(FI.CUOTA_CASA)}", "al mes, más el agua"), ("Cuota por lote baldío", f"${f0(FI.CUOTA_LOTE)}", "al mes, desde la escritura"), ("Agua", f"${f0(TARIFA_AGUA)}", f"${f0(FI.AGUA_FIJA)} fijos + ${f0(FI.AGUA_M3)}/m³, casa de 30 m³"),
       ("Cobro mensual lleno", mill(ULT["cuota_ing"] + ULT["agua_ing"], 2), f"{f0(N)} casas, mes {ULT['mes']}"), ("Costo mensual lleno", mill(ULT["oper_costo"], 2), "seguridad, mantenimiento y agua"), ("Margen lleno", mill(ULT["oper_margen"], 2), f"al mes · {pct(ULT['oper_margen'] / (ULT['cuota_ing'] + ULT['agua_ing']), 0)} del cobro"),
       ("Margen a 10 años", mill(OPER_10), f"{mill(OPER_ANIO)} al año en crucero"), ("Lo que vale la operadora", mill(VALOR_OPER), "a 6 veces su margen anual, con contrato")])}
<div class="dos">
<div>
<h3>Lo que paga el vecino</h3>
<div class="scroll sec">{tabla(casa_mes, ["", "Al mes"], "compacta")}
<p>La cuota arranca al {pct(FI.rampa(FI.RAMPA[0]), 0)} en el mes {FI.RAMPA[0]} (con el acceso, la barda y la etapa 1; todavía no hay club ni pista) y sube parejo hasta el 100 % en el mes {FI.RAMPA[1]}, cuando ya está todo. Después se actualiza cada enero con la inflación, por reglamento. Para el comprador son cifras de un fraccionamiento privado con seguridad y club del oriente de Torreón, y el agua va al nivel de un recibo doméstico; la diferencia es que aquí se ve en qué se gasta.</p>
<h3>El agua, cobrada bien</h3>
<p>Los pozos, la cisterna, la red a presión y la planta son del fraccionamiento, y la operadora los opera. Cada casa paga un cargo fijo de ${f0(FI.AGUA_FIJA)} por la red y el bombeo más ${f0(FI.AGUA_M3)} por m³ medido; la casa típica (4 personas, {f0(FI.CONSUMO_M3 * 1000 / 30)} litros al día) paga ${f0(TARIFA_AGUA)}. Darle esa agua cuesta ${f0(FI.COSTO_AGUA_CASA)}:</p>
{tabla([(c, f"${f0(v)}") for c, v in COSTO_AGUA_DET], ["Costo del agua por casa al mes", ""], "compacta", ("<b>Total</b>", f"<b>${f0(FI.COSTO_AGUA_CASA)}</b>"))}
<p>Quedan ${f0(TARIFA_AGUA - FI.COSTO_AGUA_CASA)} por casa al mes ({pct((TARIFA_AGUA - FI.COSTO_AGUA_CASA) / TARIFA_AGUA, 0)}), que incluyen la reposición de los pozos y la red: el agua se paga sola y deja. El riego de los nogales comunes sale del agua tratada, no de la potable, y por eso no se cobra.</p>
</div>
<div>
<h3>Lo que cuesta operar</h3>
{tabla([(c, d, f"${f0(v)}") for c, d, v in COSTO_FIJO_DET], ["Costo fijo al mes (desde el mes 12)", "", ""], "fijo", ("<b>Total fijo</b>", "", f"<b>${f0(FI.COSTO_FIJO_OPER)}</b>"))}
{tabla([(c, f"${f0(v)}") for c, v in COSTO_VAR_DET], ["Costo por casa habitada al mes", ""], "compacta", ("<b>Total por casa</b>", f"<b>${f0(FI.COSTO_VAR_CASA)}</b>"))}
<p>Más ${f0(FI.COSTO_VAR_LOTE)} por lote baldío (limpieza y riego de sus nogales). El costo fijo es la seguridad y la administración: no depende de cuántas casas hay, y por eso la operadora pierde dinero los primeros meses (mes 12 a {M_OPER_POS or "—"}) y gana cada vez más conforme se llena. El presupuesto de <a href="/servicios/">Servicios</a> (${f0(SV['cuota_casa'])} por casa) es lo mínimo para que el fraccionamiento funcione; la operadora presupuesta más porque pinta, repara y repone, y porque es una empresa con nómina formal.</p>
<h3>La nuez</h3>
<p>Los {f0(FI.N_NOGALES)} nogales de las áreas comunes siguen dando nuez: a {f0(FI.NUEZ_KG_ARBOL)} kg por árbol (están entre casas, no en huerta) y ${f0(FI.PRECIO_NUEZ)}/kg, son {mill(NUEZ_ANIO, 1)} cada octubre desde el año {FI.ANIO_NUEZ}, con {pct(FI.COSTO_NUEZ, 0)} de costo de cosecha. La nuez de los nogales de cada lote es del vecino.</p>
</div>
</div>
<h3>La operadora año por año</h3>
<div class="scroll sec">{tabla(anios, ["", "Casas", "Lotes baldíos", "Cuotas", "Agua", "Nuez", "Costo", "Reserva (vecinos)", "Margen"], "", ("<b>10 años</b>", "", "", f"<b>{mill(sum(f['cuota_ing'] for f in FL))}</b>", f"<b>{mill(sum(f['agua_ing'] for f in FL))}</b>", f"<b>{mill(sum(f['nuez'] for f in FL))}</b>", f"<b>{mill(sum(f['oper_costo'] for f in FL))}</b>", f"<b>{mill(sum(f['reserva'] for f in FL))}</b>", f"<b>{mill(OPER_10)}</b>"))}</div>
<p>Casas y lotes al cierre de cada año. La operadora es un negocio que no termina con las ventas: con el fraccionamiento lleno deja {mill(OPER_ANIO)} al año, todos los años, y una administradora con contrato y {f0(N)} casas se vende a unas 6 veces ese margen. Es también lo que hace que el fraccionamiento siga valiendo: un privado bien cuidado se revende más caro, y eso se lo lleva el vecino.</p>
<h3>Lo que hay que hacer para que funcione</h3>
<ul class="decisiones">
<li><b>Contrato desde el primer lote.</b> El reglamento y el contrato de administración (10 años, renovable) se firman con la escritura: la cuota no se vota, se paga; lo que se vota es el uso del fondo de reserva.</li>
<li><b>Cobranza automática.</b> Domiciliación o pago en la app; la morosidad se castiga con interés y con el acceso de visitas limitado, nunca cortando el agua (la ley no lo permite). Meta: menos de 5 % de morosidad.</li>
<li><b>Cuentas abiertas.</b> Estado de cuenta mensual a cada vecino con los gastos y el fondo de reserva. La transparencia es lo que sostiene una cuota alta sin pleitos.</li>
<li><b>Medidores desde la toma.</b> Toma de ¾" con medidor en cada lote y telemetría en los pozos: se cobra lo que se consume y se detectan fugas.</li>
<li><b>Actualización anual.</b> Cuota y tarifa de agua suben cada enero con el INPC, por reglamento, sin asamblea.</li>
<li><b>Fondo de reserva aparte.</b> El 10 % va a una cuenta del fraccionamiento, no de la operadora: paga pavimentos, bombas y renovaciones, y es lo que da confianza para pagar.</li>
</ul>
"""

# ======================= PARA EL INVERSIONISTA =======================
def _tabla_inv_anios():
    fm = lambda x: "—" if abs(x) < 5e4 else (f"−{mill(-x, 1)}" if x < 0 else mill(x, 1))
    filas = []; ap = dv = rd = 0.0
    for a in range(10):
        fa = [f for f in FL if a * 12 <= f["mes"] < (a + 1) * 12]
        aporta = sum(-f["inv"] for f in fa if f["inv"] < 0); cobra = sum(f["inv"] for f in fa if f["inv"] > 0)
        ap += aporta; dv += cobra
        filas.append((f"Año {a + 1}", mill(aporta, 1) if aporta else "—", mill(cobra, 1) if cobra else "—", fm(fa[-1]["capital"]), fm(dv - ap)))
    return filas

def inversionista():
    pico_m = next(f["mes"] for f in FL if f["capital"] == MOD["capital_pico"])
    uso = [(k, v) for k, v in SV["por_servicio"].items()] + [(k, v) for k, v in AMEN.items()] + [("Iluminación de paisaje y acceso", PAISAJE), (f"Reubicar {R['reubicar']} nogales", REUBICA), ("Proyecto ejecutivo y permisos", FI.PROYECTO * R["venta"])]
    uso_total = sum(v for _, v in uso)
    esc_filas = []
    for s_ in ESCEN:
        base = s_["nombre"] == "Base"
        esc_filas.append((f"<b>{s_['nombre']}</b>" if base else s_["nombre"], mill(s_["venta"]), mill(s_["pico"]), f"mes {s_['recupera']}" if s_["recupera"] else "no en 10 años", pct(s_["tir"], 1) if s_["tir"] is not None else "—", f"{s_['moic']:.2f}×", mill(s_["rend"]),
                          mill(s_["desarrollador"]) if s_["desarrollador"] > 1e6 else "—"))
    cuerpo = f"""
<p class="frase" style="font-size:1.25rem"><b>Pones la obra de un fraccionamiento de {f0(N)} casas sin comprar el terreno, cobras {TASA_INV_TXT} sobre lo que tengas puesto y recuperas en el mes {MOD['m_recupera']}: antes que el desarrollador, con un banco repartiendo.</b></p>
{kpis([("Capital máximo", mill(MOD['capital_pico']), f"en el mes {pico_m}, de una obra de {mill(OBRA_TOTAL)}"), ("Recupera todo", f"mes {MOD['m_recupera']}", f"{MOD['m_recupera']/12:.1f} años desde la firma"), ("Rendimiento", TASA_INV_TXT, f"preferente, sobre el saldo de cada mes: {mill(MOD['rend'])}"),
       ("TIR", pct(MOD['tir_inv'], 1), "sobre el flujo mensual real de aportaciones y cobros"), ("Múltiplo", f"{MOD['moic']:.2f}×", f"recibe {mill(MOD['devuelto'] + MOD['rend'])} por {mill(MOD['aportado'])} puestos"), ("Venta", mill(MOD['venta_total']), f"{f0(N)} lotes y comercio, con {pct(FI.ESCALON_ETAPA, 0)} más por etapa"),
       ("Cobertura", f"{MOD['venta_total'] / MOD['aportado']:.1f}×", "las ventas cubren lo aportado"), ("Primero que el desarrollador", "sí", f"nosotros cobramos {MOD['lotes_desarrollador']:.0f} lotes al final")])}
<p>Esta página es para quien va a poner el dinero de la obra. Dice qué se le pide, cuándo, qué recibe, en qué orden cobra, qué pasa si las ventas van mal y qué garantías tiene. Los números salen del mismo modelo que el resto del sitio (<code>pipeline/scripts/n6_fideicomiso.py</code>) y se pueden repetir. Al final está la <a href="#hoja">hoja de una página</a>.</p>

<h2 id="porque">Por qué conviene</h2>
<ul class="decisiones">
<li><b>No se compra el terreno.</b> El dueño lo aporta al fideicomiso y cobra {pct(X_DUENO)} de cada venta: {mill(DUENO_TOTAL)} que el proyecto nunca tiene que financiar. En un desarrollo normal el terreno es lo primero que se paga y lo último que se recupera; aquí no existe ese peso.</li>
<li><b>Las ventas pagan la obra.</b> La obra cuesta {mill(OBRA_TOTAL)}, pero las ventas de cada etapa financian la siguiente: el capital puesto al mismo tiempo nunca pasa de {mill(MOD['capital_pico'])} ({pct(MOD['capital_pico'] / OBRA_TOTAL, 0)} de la obra).</li>
<li><b>Cobras antes que nosotros.</b> Orden de cada peso que entra: dueño, ventas y escrituras, obra en curso, <em>tu capital y tu rendimiento</em>, y solo después los lotes del desarrollador. Si el proyecto rinde menos, el que pierde primero es el desarrollador.</li>
<li><b>Rendimiento preferente, no una promesa.</b> {TASA_INV_TXT} simple sobre el saldo que tengas puesto cada mes, acumulado y pagado con los primeros excedentes. Es un contrato con el fiduciario, no una expectativa de utilidad.</li>
<li><b>Un banco reparte.</b> El fideicomiso cobra cada escritura y aplica la prelación del contrato; nadie toca el dinero antes. Comité técnico con un asiento tuyo y veto sobre cambios de precio, de presupuesto de obra y de reparto.</li>
<li><b>Colateral real.</b> Los {f0(N)} lotes están en el fideicomiso; mientras no recuperes, los lotes sin vender responden por tu capital. El terreno vale hoy {mill(TERRENO_V)} como huerta y mucho más urbanizado.</li>
<li><b>Producto probado.</b> Lotes urbanizados de {R['lote_mediana']} m² en el oriente de Torreón, donde ya se venden a $3,500–3,750/m²; la lista arranca en ${f0(PRECIO_BASE)} y sube {pct(FI.ESCALON_ETAPA, 0)} por etapa. Ritmo del modelo: {TE.RITMO} lotes al mes, un fraccionamiento que ya existe en la zona en tamaño y precio.</li>
<li><b>Lo que no se ve en otros: la diferenciación.</b> {f0(QUEDAN)} nogales adultos en pie, una sola casa con nueve fachadas, agua propia a presión y pista de 3.3 km bajo los árboles. Es lo que sostiene el precio y el ritmo frente a los fraccionamientos de la misma zona.</li>
</ul>

<h2 id="calendario">Qué pones y cuándo lo recuperas</h2>
<div class="dos">
<div>
{tabla(_tabla_inv_anios(), ["", "Aportas", "Cobras", "Saldo puesto al cierre", "Neto acumulado"], "", ("<b>Total</b>", f"<b>{mill(MOD['aportado'], 1)}</b>", f"<b>{mill(MOD['devuelto'] + MOD['rend'], 1)}</b>", "—", f"<b>+{mill(MOD['rend'], 1)}</b>"))}
<p>Las aportaciones se hacen mes a mes contra el déficit real de caja (obra ejecutada menos ventas cobradas), no por adelantado: el dinero entra cuando hace falta y sale en cuanto sobra. El pico es en el mes {pico_m}, al final de la obra de la etapa 2; desde ahí el saldo baja cada mes hasta cero en el mes {MOD['m_recupera']}.</p>
</div>
<div>
{tabla([(e(k), mill(v, 1), pct(v / uso_total, 0)) for k, v in uso], ["Uso de los fondos", "Importe", ""], "compacta", ("<b>Total</b>", f"<b>{mill(uso_total, 1)}</b>", "<b>100 %</b>"))}
<p class="nota">Partida por partida en <a href="/servicios/#presupuesto">Servicios</a>, <a href="/agua/">Agua</a> y <a href="/acceso/">Acceso y barda</a>. Los pagos a contratistas salen del fideicomiso contra estimaciones aprobadas por un supervisor externo.</p>
</div>
</div>

<h2 id="escenarios">Qué pasa si sale peor (o mejor)</h2>
<div class="scroll sec">{tabla(esc_filas, ["Escenario", "Venta", "Capital máximo", "Recupera", "TIR", "Múltiplo", "Rendimiento cobrado", "Desarrollador"], "")}</div>
<p>«Ventas 30 % más lentas» estira la curva de {MOD['fin_ventas']} a {ESCEN[1]['fin']} meses; «precio 10 % menor» baja toda la lista. En los casos malos, <b>el primero que deja de cobrar es el desarrollador</b> (sus lotes desaparecen antes de que tú pierdas un peso de rendimiento), y el múltiplo se mantiene arriba de 1.2× aun con precio 10 % menor. En el escenario doble, el capital tarda más de 10 años en volver completo: ese es el riesgo real y por eso el proyecto está armado para no caer ahí: etapa 1 por debajo del mercado, obra por etapas (se puede parar entre etapas sin dejar nada a medias) y la operadora cobrando desde el mes {M_CUOTA_INI}.</p>

<h2 id="riesgos">Riesgos y cómo están cubiertos</h2>
{tabla([("Ventas más lentas", "La obra va por etapas y cada una se arranca cuando la anterior lleva 60 % vendida: no se urbaniza lo que no se vende. Precio de arranque bajo el mercado."),
        ("Precio menor", "El dueño cobra porcentaje, no precio fijo: la baja la absorben las tres partes, y primero el desarrollador. Lista por etapas con 5 % entre cada una: hay margen para no subir antes de bajar."),
        ("Sobrecosto de obra", "Presupuesto medido sobre el plano, partida por partida, con 10 % de imprevistos dentro; contratos a precio alzado por etapa; supervisor externo aprueba estimaciones."),
        ("Agua y permisos", "Dos pozos con título de concesión a confirmar antes de firmar; planta de tratamiento propia y reúso: no depende de SIMAS. Factibilidades (municipio, CFE, Protección Civil) son condición para la primera aportación."),
        ("Terreno", "Lindero, tenencia y gravámenes se verifican antes de aportar; el terreno entra limpio al fideicomiso o no entra."),
        ("El desarrollador", "Cobra al final y en lotes; su paga depende de que tú hayas recuperado. Rinde cuentas mensuales al comité técnico y puede ser sustituido por el fiduciario por incumplimiento.")],
       ["Riesgo", "Cómo está cubierto"], "spec")}</div>

<h2 id="terminos">Los términos</h2>
<ul>
<li><b>Vehículo:</b> fideicomiso irrevocable de administración y desarrollo con un banco fiduciario. Fideicomitentes: el dueño (terreno) y el inversionista (dinero para la obra). Fideicomisario en segundo lugar: el desarrollador.</li>
<li><b>Aportación:</b> hasta {mill(MOD['capital_pico'])}, en llamadas de capital mensuales contra el déficit de caja aprobado por el comité técnico, con un calendario estimado (tabla de arriba) y un tope.</li>
<li><b>Rendimiento:</b> {TASA_INV_TXT} simple sobre el saldo puesto, acumulado mes a mes y pagado antes que el capital en cuanto hay excedente.</li>
<li><b>Prelación de cada cobro:</b> 1) {pct(X_DUENO)} al dueño; 2) {pct(FI.COMISION, 0)} ventas, comisiones y escrituras; 3) obra del mes; 4) rendimiento devengado; 5) capital; 6) excedente al desarrollador, en lotes, al final.</li>
<li><b>Gobierno:</b> comité técnico de tres (dueño, inversionista, desarrollador); el inversionista tiene veto en precio de lista, presupuesto de obra, cambios al reparto y venta de lotes del desarrollador antes de la recuperación.</li>
<li><b>Información:</b> reporte mensual del fiduciario (ventas, cobros, obra, saldos), avance de obra con supervisor externo, auditoría anual.</li>
<li><b>Salida:</b> natural, al recuperar capital y rendimiento (mes {MOD['m_recupera']}); anticipada, con derecho de preferencia del desarrollador para comprar la posición al saldo más el rendimiento devengado.</li>
<li><b>Más allá del fideicomiso:</b> la construcción de las casas ({CON['casas']:.0f} casas, {mill(CON['utilidad'])} de utilidad) y la operadora ({mill(OPER_ANIO)} al año en crucero) son negocios del desarrollador, fuera de este flujo. Si el inversionista quiere participar en ellos se negocia aparte; no se mezclan con la prelación de la obra.</li>
</ul>

<h2 id="hoja">Hoja de una página</h2>
<section class="hoja" id="hoja-inv">
<header><p class="ojo">{NOMBRE} · Para el inversionista · {VERSION.split(" · ")[1]}</p><h3>{f0(N)} casas entre {f0(QUEDAN)} nogales, en {ha(GROSS)} al oriente de Torreón</h3></header>
<div class="hoja-grid">
<dl><dt>Qué financias</dt><dd>La obra: calles, redes, agua, luz, club, parques, acceso y barda. {mill(OBRA_TOTAL)} en 4 etapas, meses 8 a 33.</dd></dl>
<dl><dt>Cuánto pones como máximo</dt><dd>{mill(MOD['capital_pico'])} (mes {pico_m}). Las ventas pagan el resto.</dd></dl>
<dl><dt>Qué cobras</dt><dd>{TASA_INV_TXT} sobre el saldo puesto, antes que el desarrollador. {mill(MOD['rend'])} de rendimiento.</dd></dl>
<dl><dt>Cuándo recuperas</dt><dd>Mes {MOD['m_recupera']} ({MOD['m_recupera']/12:.1f} años). TIR {pct(MOD['tir_inv'], 1)}, múltiplo {MOD['moic']:.2f}×.</dd></dl>
<dl><dt>Venta total</dt><dd>{mill(MOD['venta_total'])}: {f0(N)} lotes de {R['lote_mediana']} m² a ${f0(PRECIO_BASE)}/m² (+{pct(FI.ESCALON_ETAPA, 0)} por etapa) y {f0(R['predio_comercial_m2'])} m² de comercio.</dd></dl>
<dl><dt>Terreno</dt><dd>No se compra: el dueño lo aporta y cobra {pct(X_DUENO)} de cada venta ({mill(DUENO_TOTAL)}).</dd></dl>
<dl><dt>Quién reparte</dt><dd>Banco fiduciario, con prelación en el contrato: dueño, ventas, obra, tu rendimiento, tu capital, desarrollador.</dd></dl>
<dl><dt>Garantías</dt><dd>Lotes sin vender en el fideicomiso; veto en precio, obra y reparto; supervisor externo; auditoría anual.</dd></dl>
<dl><dt>Si sale mal</dt><dd>Ventas 30 % más lentas: recuperas en el mes {ESCEN[1]['recupera']}. Precio 10 % menor: múltiplo {ESCEN[2]['moic']:.2f}×. El desarrollador pierde primero.</dd></dl>
<dl><dt>Siguiente paso</dt><dd>Carta de intención, verificación del predio y del agua (90 días), contrato de fideicomiso. Primera aportación con licencia y factibilidades.</dd></dl>
</div>
<p class="nota">Pesos de 2026, antes de impuestos. Anteproyecto: cifras de referencia, no una oferta pública ni una cotización. Detalle en nogalera.capitaltorreon.com/inversionista/</p>
</section>
<p><button type="button" class="boton" onclick="window.print()">Imprimir esta página</button> <span class="nota">La hoja sale en una cuartilla; el resto de la página, detrás.</span></p>
"""
    pagina("inversionista", "Para el inversionista", "15 · Para el inversionista", f"Por qué conviene poner la obra: {mill(MOD['capital_pico'])} como máximo, recuperas en el mes {MOD['m_recupera']} con {TASA_INV_TXT}, antes que el desarrollador y con un banco repartiendo. Escenarios, garantías, términos y la hoja de una página.", cuerpo,
           [("porque", "Por qué conviene"), ("calendario", "Qué pones y cuándo"), ("escenarios", "Escenarios"), ("riesgos", "Riesgos"), ("terminos", "Términos"), ("hoja", "Hoja de una página")],
           descripcion=f"La Nogalera para el inversionista: capital máximo, mes de recuperación, rendimiento, escenarios, garantías y términos del fideicomiso.")

# ======================= PARA EL COMERCIALIZADOR =======================
COMISION_DET = [("Vendedor o bróker que cierra", 0.025, "sobre el precio del lote, al escriturar (50 % al contrato, 50 % a la escritura)"), ("Gerente de ventas", 0.005, "sobre todo lo que vende el equipo"),
                ("Publicidad, casa muestra y oficina de ventas", 0.03, "digital, renders, eventos, casa muestra amueblada en el acceso"), ("Escrituración, notaría y legal", 0.02, "la escritura del lote al comprador dentro del fideicomiso")]
assert abs(sum(x for _, x, _ in COMISION_DET) - FI.COMISION) < 1e-9
LOTE_TIPO = 300; M2_MED = R["lote_mediana"]
def _precio_tipo(m2, etapa, premio):
    x = (PRECIO_BASE - 2 * (m2 - LOTE_TIPO)) * (1 + FI.ESCALON_ETAPA) ** etapa
    return x * (1.08 if premio == "parque" else 1.05 if premio == "bulevar" else 1.0)

def comercializador():
    ventas = MOD["ventas"]; meses = sorted(ventas)
    # metas por etapa: cada etapa es la cuarta parte de los lotes
    etapas_v = []; acum = 0; k = 0; ini = meses[0]
    for m in meses:
        acum += ventas[m]
        if acum >= (k + 1) * N / FI.ETAPAS_VENTA - 0.5 or m == meses[-1]:
            etapas_v.append((k, ini, m)); k += 1; ini = m + 1
            if k == FI.ETAPAS_VENTA: break
    por_etapa = [p for p in LOTES]
    lista_filas = []
    for k, a, b in etapas_v:
        n_et = round(N / FI.ETAPAS_VENTA) if k < FI.ETAPAS_VENTA - 1 else N - 3 * round(N / FI.ETAPAS_VENTA)
        lista_filas.append((f"<b>Etapa {k + 1}</b>", f"meses {a}–{b}", f0(n_et), f"${f0(LISTA[k])}", f"${f0(LISTA[k] * 1.05)}", f"${f0(LISTA[k] * 1.08)}", f"${f0(LISTA[k] * LOTE_TIPO)}", f"${f0(_precio_tipo(M2_MED, k, '') * M2_MED)}"))
    paquete = LISTA[0] * LOTE_TIPO + FI.PRECIO_CASA
    pico_m = max(ventas, key=lambda m: (ventas[m], -m)); vend = math.ceil(ventas[pico_m] / 4)
    metas = [(f"Mes {m}", f0(ventas[m]), mill(ventas[m] * LISTA[min(3, int(sum(ventas[x] for x in meses if x < m) * 4 / N))] * M2_MED, 1)) for m in meses if m in (meses[0], meses[2], meses[5], pico_m, meses[len(meses) // 2], meses[-1])]
    anios_v = []
    for a in range(5):
        n_a = sum(v for m, v in ventas.items() if a * 12 <= m < (a + 1) * 12)
        if n_a: anios_v.append((f"Año {a + 1}", f0(n_a), f0(round(n_a / 12)), mill(sum(f["ingreso"] for f in FL if a * 12 <= f["mes"] < (a + 1) * 12))))
    cuerpo = f"""
<p class="frase" style="font-size:1.25rem"><b>{f0(N)} lotes urbanizados entre nogales, de {mill(LISTA[0] * LOTE_TIPO, 2)} el típico, con una casa de {FI.M2_CASA:.0f} m² lista en 8 meses: a {TE.RITMO} lotes por mes, se vende en {MOD['fin_ventas'] - meses[0] + 1} meses.</b></p>
{kpis([("Lotes", f0(N), f"mediana {M2_MED} m² · de {min(p['m2'] for p in LOTES):,.0f} a {max(p['m2'] for p in LOTES):,.0f} m²"), ("Precio etapa 1", f"${f0(LISTA[0])}/m²", f"lote típico de {LOTE_TIPO} m²: {mill(LISTA[0] * LOTE_TIPO, 2)}"), ("Sube por etapa", pct(FI.ESCALON_ETAPA, 0), f"etapa 4: ${f0(LISTA[3])}/m²"),
       ("Casa llave en mano", mill(FI.PRECIO_CASA, 2), f"{FI.M2_CASA:.0f} m², 8 meses, 9 fachadas"), ("Paquete lote + casa", mill(paquete, 2), "etapa 1, lote típico"), ("Meta", f"{TE.RITMO} lotes/mes", f"pico de {ventas[pico_m]} en el mes {pico_m}"),
       ("Comisión de cierre", pct(COMISION_DET[0][1], 1), f"${f0(COMISION_DET[0][1] * LISTA[0] * LOTE_TIPO)} por lote típico en etapa 1"), ("Equipo", f"{vend} vendedores", "+ gerente, en el pico")])}
<p>Esta página es para quien va a vender: qué se vende, a cuánto, cómo se cobra, cuánto gana quien cierra, cuántos hay que vender cada mes, qué decir, qué contestar y cómo es el proceso de la primera visita a la escritura. Al final está la <a href="#hoja">hoja de una página</a> para llevar en el teléfono.</p>

<h2 id="lista">Lista de precios</h2>
<div class="scroll sec"><div class="scroll sec">{tabla(lista_filas, ["Etapa", "Cuándo", "Lotes", "Frente a calle", "Frente al bulevar (+5 %)", "Frente a parque (+8 %)", f"Lote típico de {LOTE_TIPO} m²", f"Lote mediano de {M2_MED} m²"], "")}</div>
<p>Precio por m² para 300 m²; cada m² de más baja $2 el precio por m² (un lote de 400 m² frente a calle en etapa 1: ${f0(_precio_tipo(400, 0, ''))}/m², {mill(_precio_tipo(400, 0, '') * 400, 2)}). La lista sube {pct(FI.ESCALON_ETAPA, 0)} al abrir cada etapa, y <b>eso es un argumento de venta, no una amenaza</b>: quien compra en la etapa 1 compra {pct(LISTA[3] / LISTA[0] - 1, 0)} más barato que el último y ve subir su lote mientras se construye el resto. Los lotes de cada etapa, con su fachada y su dirección, están en el <a href="/plan/">plan maestro</a> y en <a href="/etapas/">Etapas</a>. El comercio (súper y frente a Espinoza) se vende aparte, a $6,000/m².</p>
{tabla([("Casa Modelo Nogal llave en mano", f"{mill(FI.PRECIO_CASA, 2)} (${f0(FI.PRECIO_M2_MERCADO)}/m² × {FI.M2_CASA:.0f} m²), con la fachada asignada al lote, entregada en {FI.DURACION_CASA} meses con garantía"),
        ("Cómo se paga la casa", f"{pct(FI.PAGO_CASA[0], 0)} al firmar, {pct(FI.PAGO_CASA[1], 0)} en estimaciones mensuales durante la obra, {pct(FI.PAGO_CASA[2], 0)} a la entrega; o con crédito hipotecario terreno + construcción"),
        ("Paquete lote típico + casa, etapa 1", f"<b>{mill(paquete, 2)}</b>: una casa nueva de {FI.M2_CASA:.0f} m² en {LOTE_TIPO} m² entre nogales, con club, pista y seguridad"),
        ("Mantenimiento y agua", f"${f0(FI.CUOTA_CASA)} al mes por casa (seguridad 24 h, nogales, alumbrado, club, pista, pintura y reparaciones) + agua ${f0(TARIFA_AGUA)} típico; ${f0(FI.CUOTA_LOTE)} al mes mientras el lote está baldío")],
       ["", ""], "spec")}</div>

<h2 id="pago">Formas de pago</h2>
<div class="scroll sec">{tabla([("Contado", "100 % a la firma de la escritura (30 días después del contrato). Precio de lista.", "Dueño, obra e inversionista cobran de inmediato."),
        ("Crédito bancario", "Enganche 20–30 % y crédito hipotecario de terreno (o terreno + construcción si lleva la casa). Precio de lista.", "Igual que contado para el fideicomiso: el banco paga a la escritura."),
        ("Plan directo", f"30 % de enganche, saldo en hasta 18 mensualidades con 1 % mensual sobre saldo; la escritura, al liquidar. Apartado de $50,000 a cuenta.", "El fideicomiso cobra cada mensualidad y reparte igual; los intereses van al proyecto."),
        ("Preventa de etapa", "Dos meses antes de abrir cada etapa, con 10 % de apartado, al precio de la etapa anterior.", "Llena la etapa antes de que exista la calle: es el 5 % que el comprador se ahorra.")],
       ["Forma", "Cómo", "Qué significa para el proyecto"], "spec")}</div>
<p class="nota">No se entrega lote sin pagar completo: la escritura la firma el fiduciario cuando el lote está liquidado. El reglamento y el contrato de administración de la operadora se firman con la escritura.</p>

<h2 id="comisiones">Comisiones</h2>
<div class="scroll sec">{tabla([(c, pct(x, 1), f"${f0(x * LISTA[0] * LOTE_TIPO)}", d) for c, x, d in COMISION_DET], ["", "Del precio", "Por lote típico, etapa 1", "Cuándo y cómo"], "", ("<b>Total blandos de venta</b>", f"<b>{pct(FI.COMISION, 0)}</b>", f"<b>${f0(FI.COMISION * LISTA[0] * LOTE_TIPO)}</b>", f"{mill(MOD['comis_total'])} en todo el proyecto"))}
<p>El {pct(FI.COMISION, 0)} es la bolsa completa de ventas del fideicomiso y es fija: si el comercializador trae su propia publicidad, negocia dentro de ella, no encima. Bonos: 0.5 % extra para el vendedor que cierra su meta trimestral, y 1 % sobre la casa llave en mano cuando se vende el paquete (lo paga la constructora, no el fideicomiso). Un vendedor que cierra {math.ceil(TE.RITMO / vend)} lotes al mes gana ${f0(math.ceil(TE.RITMO / vend) * COMISION_DET[0][1] * LISTA[0] * LOTE_TIPO)} mensuales en etapa 1, más el bono.</p>

<h2 id="metas">Metas</h2>
<div class="dos">
<div>{tabla(anios_v, ["", "Lotes", "Al mes", "Venta"], "compacta", ("<b>Total</b>", f"<b>{f0(N)}</b>", "", f"<b>{mill(MOD['venta_total'])}</b>"))}
<p>La curva del modelo: arranque lento con la licencia (mes {meses[0]}), pico de {ventas[pico_m]} lotes al mes cuando ya se ve el club y el bulevar, un valle a media obra y un cierre parejo; última venta en el mes {MOD['fin_ventas']}. El objetivo del equipo es ir <b>adelante de esa curva</b>: cada mes de adelanto es un mes menos de capital puesto.</p></div>
<div>{tabla([("Lotes al mes en el pico", f"{ventas[pico_m]}"), ("Cierres por vendedor al mes", "4"), ("Vendedores en el pico", f"{vend} + gerente"), ("Visitas por cierre", "8 (1 de cada 8 visitas compra)"), ("Visitas al mes en el pico", f"{ventas[pico_m] * 8}"), ("Prospectos digitales por visita", "5"), ("Prospectos al mes", f"{f0(ventas[pico_m] * 40)}"), ("Costo por prospecto a presupuesto", f"≈ ${f0(COMISION_DET[2][1] * LISTA[0] * LOTE_TIPO * ventas[pico_m] / (ventas[pico_m] * 40) * 0.6)}")], ["Embudo", ""], "compacta")}
<p class="nota">El embudo es el supuesto de trabajo con el que se dimensiona el equipo y la publicidad; se ajusta con los datos reales de los primeros tres meses.</p></div>
</div>

<h2 id="argumentos">Qué se vende y cómo se dice</h2>
<ul class="decisiones">
<li><b>Vives entre nogales de 40 años.</b> {f0(QUEDAN)} árboles adultos se quedan, mapeados uno por uno; cada lote tiene los suyos, regados por el fraccionamiento. Nadie más en Torreón vende sombra ya crecida.</li>
<li><b>Una sola casa, nueve fachadas.</b> El Modelo Nogal de {FI.M2_CASA:.0f} m² en dos plantas, con la fachada asignada a cada lote: la calle se ve pareja y rica, y no hay casas raras al lado.</li>
<li><b>Agua propia a presión.</b> Dos pozos, cisterna y red calculada esquina por esquina: 3 kg/cm² en la regadera a cualquier hora, planta de tratamiento propia y nogales regados con agua tratada.</li>
<li><b>Seguridad de verdad.</b> Barda perimetral con cámaras cada 60 m, acceso con pórtico, reja y control de visitas por app, guardias las 24 horas. Está dibujado y presupuestado, no prometido.</li>
<li><b>Club, pista y parques desde la etapa 1.</b> Club social con gimnasio, club deportivo y la pista de 3.3 km bajo los nogales, que se ven en la primera visita.</li>
<li><b>Compra en etapa 1, compra {pct(LISTA[3] / LISTA[0] - 1, 0)} más barato.</b> La lista sube {pct(FI.ESCALON_ETAPA, 0)} por etapa; el lote de hoy vale más en cuanto abre la siguiente.</li>
<li><b>Fideicomiso con banco.</b> El comprador escritura con un fiduciario, no con una inmobiliaria: su lote existe, está libre y el dinero de la obra está comprometido.</li>
<li><b>La casa en 8 meses, al precio del mercado, con garantía.</b> El mismo proyecto construye la casa con molde y cuadrillas en serie: se entrega en 8 meses, cobra por avance y da garantía.</li>
<li><b>Mantenimiento con cuentas abiertas.</b> ${f0(FI.CUOTA_CASA)} al mes por una operadora profesional que pinta, repara, riega y vigila, con estado de cuenta mensual y fondo de reserva de los vecinos.</li>
<li><b>A 15 minutos del oriente de Torreón</b> por la Calzada José Vasconcelos, en La Paz, en la zona a la que la ciudad está creciendo.</li>
</ul>

<h2 id="objeciones">Objeciones y respuestas</h2>
{tabla([("«Está lejos.»", "Es la misma zona donde ya se venden lotes a $3,500–3,750/m²; estás comprando antes de que termine de llegar la ciudad, y por eso a este precio."),
        ("«Los nogales tiran mucha hoja y nuez.»", "Los nogales de las áreas comunes los barre y poda la operadora; los del lote, el vecino, y la nuez es suya. La sombra baja 6 °C la casa en verano: menos aire acondicionado."),
        ("«¿Y si no construyen el club?»", "El club social va en la etapa 1 y el deportivo en la 2, dentro del presupuesto que financia el inversionista a través del fideicomiso; el comprador puede ver el reporte de obra del fiduciario."),
        ("«La cuota es alta.»", f"${f0(FI.CUOTA_CASA)} incluye seguridad 24 h con barda y cámaras, alumbrado, riego de nogales, club, pista, pintura y reparaciones. Un privado con lo mismo cobra eso o más; aquí además ves en qué se gasta cada mes."),
        ("«Quiero mi propia fachada.»", "El reglamento asigna una de nueve fachadas a cada lote para que la calle valga más; adentro la casa es libre, y puedes elegir lote por la fachada que te gusta."),
        ("«¿Hay agua?»", "Dos pozos con concesión, cisterna de regulación y red a presión calculada esquina por esquina, y planta de tratamiento propia. Está dibujado con diámetros y presiones en la sección Agua."),
        ("«Mejor espero a la siguiente etapa.»", f"La siguiente etapa sale {pct(FI.ESCALON_ETAPA, 0)} más cara y los lotes frente a parque y bulevar de esta ya no estarán."),
        ("«¿Puedo construir con mi arquitecto?»", "Sí, con los planos del Modelo Nogal y la fachada del lote (se entregan con la escritura). O lo construimos nosotros en 8 meses, al precio del mercado y con garantía.")],
       ["Objeción", "Respuesta"], "spec")}</div>

<h2 id="proceso">El proceso, de la visita a la escritura</h2>
<ol>
<li><b>Prospecto</b> (digital, referido o de la carretera) → cita en la oficina de ventas del acceso: plano maestro con disponibilidad en pantalla, renders, casa muestra amueblada.</li>
<li><b>Recorrido</b> por el bulevar, el club y el lote, bajo los nogales. Se enseña la fachada asignada y la dirección del lote.</li>
<li><b>Apartado</b> de $50,000 (a cuenta del precio, reembolsable 10 días) y expediente: identificación, comprobantes, forma de pago.</li>
<li><b>Contrato</b> de promesa con el fiduciario en 10 días; enganche o pago; se entrega el reglamento y el contrato de la operadora.</li>
<li><b>Escritura</b> con el fiduciario al liquidar (contado y banco: 30 días; plan directo: al final). Comisión del vendedor: 50 % al contrato, 50 % a la escritura.</li>
<li><b>Entrega</b> del lote con sus mojoneras, toma de agua con medidor, acometida eléctrica y fibra, y los planos del Modelo Nogal. Alta en la app de la operadora.</li>
<li><b>Casa</b>: si va con nosotros, el contrato de construcción se firma el mismo día y la obra arranca a los 2 meses.</li>
</ol>
<p><b>Material de venta:</b> los <a href="/renders/">diez renders</a> y el creador para hacer el de cada lote, el <a href="/plan/">plan maestro</a> interactivo con disponibilidad, la <a href="/casa/">casa</a> en 3D con sus <a href="/fachadas/">nueve fachadas</a>, la sección de <a href="/agua/">agua</a> y la de <a href="/acceso/">acceso y barda</a> para quien pregunta por lo técnico, y la casa muestra en el acceso desde el mes 14.</p>

<h2 id="hoja">Hoja de una página</h2>
<section class="hoja" id="hoja-com">
<header><p class="ojo">{NOMBRE} · Para el comercializador · {VERSION.split(" · ")[1]}</p><h3>{f0(N)} lotes entre {f0(QUEDAN)} nogales, en {ha(GROSS)} al oriente de Torreón</h3></header>
<div class="hoja-grid">
<dl><dt>Producto</dt><dd>Lote urbanizado de {M2_MED} m² (mediana) con calle, agua a presión, luz, fibra, barda, seguridad y nogales; casa Modelo Nogal de {FI.M2_CASA:.0f} m² en 8 meses, 9 fachadas.</dd></dl>
<dl><dt>Precio etapa 1</dt><dd>${f0(LISTA[0])}/m² frente a calle, ${f0(LISTA[0] * 1.05)} bulevar, ${f0(LISTA[0] * 1.08)} parque. Lote típico de {LOTE_TIPO} m²: {mill(LISTA[0] * LOTE_TIPO, 2)}.</dd></dl>
<dl><dt>Sube por etapa</dt><dd>+{pct(FI.ESCALON_ETAPA, 0)} al abrir cada etapa: {" · ".join(f"${f0(x)}" for x in LISTA)}.</dd></dl>
<dl><dt>Casa</dt><dd>{mill(FI.PRECIO_CASA, 2)} llave en mano; paquete lote típico + casa {mill(paquete, 2)}. {pct(FI.PAGO_CASA[0], 0)} / {pct(FI.PAGO_CASA[1], 0)} / {pct(FI.PAGO_CASA[2], 0)}.</dd></dl>
<dl><dt>Pago</dt><dd>Contado o banco a 30 días; plan directo 30 % + 18 meses al 1 % mensual; preventa de etapa con 10 %.</dd></dl>
<dl><dt>Mantenimiento</dt><dd>${f0(FI.CUOTA_CASA)}/mes casa, ${f0(FI.CUOTA_LOTE)}/mes lote baldío, agua ${f0(TARIFA_AGUA)} típico. Operadora profesional con cuentas abiertas.</dd></dl>
<dl><dt>Comisión</dt><dd>{pct(COMISION_DET[0][1], 1)} al que cierra (50 % contrato, 50 % escritura) + 0.5 % bono trimestral + 1 % sobre la casa.</dd></dl>
<dl><dt>Meta</dt><dd>{TE.RITMO} lotes al mes, 4 por vendedor, 8 visitas por cierre; pico {ventas[pico_m]} en el mes {pico_m}; última venta mes {MOD['fin_ventas']}.</dd></dl>
<dl><dt>Tres frases</dt><dd>Sombra de 40 años ya crecida. Agua propia a presión. Compra hoy {pct(LISTA[3] / LISTA[0] - 1, 0)} más barato que el último.</dd></dl>
<dl><dt>Proceso</dt><dd>Visita → apartado $50,000 → contrato en 10 días → escritura con el fiduciario → entrega con medidor, acometidas y planos.</dd></dl>
</div>
<p class="nota">Pesos de 2026. Lista de precios de referencia del anteproyecto; la vigente la publica el comité técnico. nogalera.capitaltorreon.com/comercializador/</p>
</section>
<p><button type="button" class="boton" onclick="window.print()">Imprimir esta página</button></p>
"""
    pagina("comercializador", "Para el comercializador", "16 · Para el comercializador", f"Lista de precios por etapa, formas de pago, comisiones, metas, argumentos, objeciones y el proceso de la visita a la escritura; y la hoja de una página.", cuerpo,
           [("lista", "Lista de precios"), ("pago", "Formas de pago"), ("comisiones", "Comisiones"), ("metas", "Metas"), ("argumentos", "Argumentos"), ("objeciones", "Objeciones"), ("proceso", "Proceso"), ("hoja", "Hoja de una página")],
           descripcion="La Nogalera para el comercializador: lista de precios por etapa, comisiones, metas de venta, argumentos, objeciones y proceso.")
