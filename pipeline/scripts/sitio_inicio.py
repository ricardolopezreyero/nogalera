# ======================= LA PÁGINA DEL CLIENTE: /inicio/ (se ejecuta dentro de sitio.py) =======================
# Una sola página, aparte del tablero del proyecto: lo que ve quien quiere comprar. Imágenes: public/inicio/img/ (maqueta, renders.js --lista renders_inicio.json)
# y los renders fotorrealistas de public/renders/foto/img/ (reducidos a public/inicio/img/c/). Llamado principal: descargar el brochure dejando nombre, celular y correo.
INICIO_IMGS = {n: (esc_, hora, vista) for n, esc_, hora, vista in json.load(open(os.path.join(AQUI, "renders_inicio.json"), encoding="utf-8"))}
PIE_IMG = {"hero-noche": "La calle de noche: nogales iluminados desde abajo, arbotantes bajos y las casas encendidas.",
           "calle-dia": "La calle bajo los nogales a mediodía: sombra completa sobre la banqueta y el arroyo.", "calle-atardecer": "La misma calle al atardecer.", "calle-alta": "Las cuadras desde arriba: cada casa con sus nogales.",
           "noche-alta": "Las luces de una cuadra de noche, desde arriba.", "noche-banqueta": "Caminar de noche por la banqueta, con los nogales iluminados.",
           "casa-tarde": "La casa Modelo Nogal, fachada Horizonte, por la tarde.", "casa-noche": "La misma casa de noche, con la luz del portal y las ventanas.", "casa-vecinas": "La cuadra: cada casa con una fachada distinta.",
           "aerea-tarde": "La Nogalera desde el aire: 60 hectáreas de huerta con calles entre los árboles.", "aerea-acceso": "El acceso y el bulevar desde el aire, al atardecer.", "aerea-noche": "El fraccionamiento de noche, desde el aire.",
           "acceso-atardecer": "El acceso: pórtico, caseta y reja, al atardecer.", "acceso-noche": "El acceso de noche.", "acceso-adentro": "Entrando de noche: la calzada y el pórtico.",
           "bulevar-dia": "Bulevar Nogal: dos arroyos y un camellón con la hilera de nogales.", "bulevar-noche": "El bulevar de noche.", "bulevar-atardecer": "El bulevar y las cuadras al atardecer.",
           "parque-dia": "Parque Garza: una huerta que se quedó como parque.", "parque-pergola": "La pérgola del parque al atardecer.", "parque-noche": "El parque de noche, con la pista iluminada.",
           "pista-tarde": "La pista de 3.3 km bajo los nogales, junto a la barda.", "pista-atardecer": "La pista al atardecer.", "club-tarde": "El club social: salón, gimnasio y plaza.", "club-noche": "El club de noche.",
           "interior-tarde": "Sala, comedor y cocina abiertos al portal y al jardín.", "interior-noche": "El interior al atardecer, con el jardín iluminado.", "interior-comedor": "El comedor y la cocina.",
           "portal-atardecer": "El portal y el jardín al atardecer.", "portal-noche": "El portal de noche."}
LOTE_MIN = min(LOTES, key=lambda p: p["m2"]); PRECIO_MIN = precio_lote(LOTE_MIN) * LOTE_MIN["m2"]
LOTE_TIPO_I = 300; PRECIO_TIPO = PRECIO_BASE * LOTE_TIPO_I; PAQUETE_I = PRECIO_TIPO + FI.PRECIO_CASA
LISTA_I = FI.lista(PRECIO_BASE)
FOTO_DIR = os.path.join(PUB, "renders", "foto", "img"); C_DIR = os.path.join(PUB, "inicio", "img", "c")
TEXTO_C = {"completo-entrada": "La entrada al atardecer: pórtico, casetas, reja y los nogales iluminados.", "completo-casa": "La casa Modelo Nogal en su cuadra, de mañana, con sus vecinas.", "completo-parque": "Parque Garza: nogales, pérgola, juegos y gente.",
           "completo-aereo": "Las 60 hectáreas desde el aire: cada casa, cada nogal, cada luminaria.", "completo-sur": "Desde el sur, con la calzada y las huertas vecinas.", "completo-club": "El club: salón con oficinas, gimnasio, canchas y plaza.",
           "completo-bulevar": "Bulevar Nogal con su camellón y sendero.", "completo-entrada-alta": "El acceso desde el aire.", "completo-parque-alto": "Parque Garza desde el aire.", "completo-casa-frente": "La casa de frente.",
           "fachada-horizonte": "Horizonte", "fachada-cantera": "Cantera", "fachada-ladrillo": "Ladrillo", "fachada-lamas": "Lamas", "fachada-marco": "Marco", "fachada-hacienda": "Hacienda", "fachada-concreto": "Concreto", "fachada-celosia": "Celosía", "fachada-duela": "Duela",
           "fachada-frente": "La casa de frente, desde la banqueta de enfrente.", "fachada-atardecer": "La fachada Horizonte al atardecer.", "fachada-noche": "De noche, con el portal y las ventanas encendidas.",
           "cuadra-lejos": "La cuadra de lejos: las nueve fachadas seguidas bajo los nogales.", "cuadra": "La cuadra en escorzo.", "cuadra-alta": "La cuadra desde arriba.",
           "calle-dia": "La calle bajo los nogales a mediodía.", "calle-noche": "La calle de noche: lámparas bajas, ventanas encendidas.", "acceso-atardecer": "El acceso al atardecer.", "portal-atardecer": "El portal y el jardín al atardecer.",
           "parque-dia": "Parque Garza de día.", "aerea-tarde": "La Nogalera desde el aire.", "aerea-acceso": "El acceso y el bulevar desde el aire."}

def reducir(n, ancho=1600):
    """Versión reducida del render fotorrealista para la página (las originales pesan de 1 a 5 MB)."""
    from PIL import Image
    src = os.path.join(FOTO_DIR, n + ".jpg"); dst = os.path.join(C_DIR, n + ".jpg")
    if not os.path.exists(src): return None
    os.makedirs(C_DIR, exist_ok=True)
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
        im = Image.open(src).convert("RGB"); im.thumbnail((ancho, ancho)); im.save(dst, quality=80, optimize=True, progressive=True)
    return f"/inicio/img/c/{n}.jpg"

def foto(n, ancha=False, lazy=True):
    t = PIE_IMG.get(n, n)
    return (f'<figure class="foto{" ancha" if ancha else ""}"><a href="/inicio/img/{n}.jpg" data-grande="/inicio/img/{n}.jpg" data-titulo="{e(t)}">'
            f'<img src="/inicio/img/t/{n}.jpg" alt="{e(t)}" width="960" height="540"{" loading=lazy" if lazy else ""}></a><figcaption>{e(t)}</figcaption></figure>')
def foto_c(n, texto=None, ancha=False, lazy=True, clase="foto"):
    """Render fotorrealista (WebGL) si existe; si no, nada."""
    chica = reducir(n)
    if not chica: return ""
    t = texto or TEXTO_C.get(n, n)
    return (f'<figure class="{clase}{" ancha" if ancha else ""}"><a href="/renders/foto/img/{n}.jpg" data-grande="/renders/foto/img/{n}.jpg" data-titulo="{e(t)}">'
            f'<img src="{chica}" alt="{e(t)}" width="1600" height="900"{" loading=lazy" if lazy else ""}></a><figcaption>{e(t)}</figcaption></figure>')

def forma_brochure(id_, oscura=True):
    return f'''<form class="brochure" id="{id_}" novalidate>
  <p class="ojo">El brochure</p>
  <h3>Descarga el brochure</h3>
  <p class="nota">Plano con los lotes de la etapa 1, lista de precios, la casa con sus nueve fachadas y cómo se compra. Te lo mandamos por correo. Sin compromiso.</p>
  <label>Nombre <input type="text" name="nombre" autocomplete="name" required maxlength="120" placeholder="Tu nombre"></label>
  <label>Celular <input type="tel" name="celular" autocomplete="tel" inputmode="tel" required placeholder="871 000 0000"></label>
  <label>Correo <input type="email" name="correo" autocomplete="email" required placeholder="tu@correo.com"></label>
  <label class="trampa" aria-hidden="true">Empresa <input type="text" name="empresa" tabindex="-1" autocomplete="off"></label>
  <p class="estado" aria-live="polite"></p>
  <button type="submit" class="boton grande">Quiero el brochure</button>
  <p class="privacidad">Al enviar aceptas que {NOMBRE} te escriba por correo, teléfono o WhatsApp sobre este proyecto. No compartimos tus datos.</p>
  <div class="gracias" hidden>
    <h3>Gracias, <b></b>.</h3>
    <p>Ya tenemos tus datos. <b>En cuanto el brochure esté listo te lo mandamos a tu correo.</b> Si nos cuentas un poco más, te preparamos la propuesta a tu medida:</p>
    <fieldset><legend>¿Sería tu primera casa o tu segunda casa?</legend><div class="opciones">
      <label><input type="radio" name="casa" value="primera"> Primera casa</label><label><input type="radio" name="casa" value="segunda"> Segunda casa</label></div></fieldset>
    <fieldset><legend>¿Tienes acceso a un crédito de más de 4 millones de pesos?</legend><div class="opciones">
      <label><input type="radio" name="credito" value="si"> Sí</label><label><input type="radio" name="credito" value="no"> No</label><label><input type="radio" name="credito" value="nose"> No lo sé</label></div></fieldset>
    <fieldset><legend>¿Qué tan rápido quisieras comprar?</legend><div class="opciones">
      <label><input type="radio" name="rapidez" value="viendo"> Estoy viendo</label><label><input type="radio" name="rapidez" value="ya"> Quiero comprar ya</label></div></fieldset>
    <label>¿Algo más? (opcional) <textarea name="mensaje" maxlength="1000" placeholder="Qué lote te gustaría, cuándo, para quién…"></textarea></label>
    <p class="estado2" aria-live="polite"></p>
    <button type="button" class="boton linea mas">Enviar</button>
    <p class="listo" hidden>Listo. Te escribimos hoy mismo.</p>
  </div>
</form>'''

def inicio():
    fachadas_c = "".join(foto_c(n, clase="foto fach") for n in ["fachada-horizonte", "fachada-cantera", "fachada-ladrillo", "fachada-lamas", "fachada-marco", "fachada-hacienda", "fachada-concreto", "fachada-celosia", "fachada-duela"])
    fachadas = "".join(f'<figure>{CD.fachada(n)}<figcaption><b>{e(n)}</b>{e(CD.TEXTO[n])}</figcaption></figure>' for n in NF.NOMBRES)
    todas_c = [n for n in TEXTO_C if os.path.exists(os.path.join(FOTO_DIR, n + ".jpg")) and not n.startswith("fachada-") or n in ("fachada-frente", "fachada-atardecer", "fachada-noche")]
    todas = [n for n in INICIO_IMGS if n != "hero-noche"]
    hero = reducir("completo-entrada", 2560) or "/inicio/img/hero-noche.jpg"
    html = f"""<!doctype html>
<html lang="es-MX">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{NOMBRE} · Vivir entre nogales, al oriente de Torreón</title>
<meta name="description" content="{NOMBRE}: {f0(N)} casas entre {f0(QUEDAN)} nogales adultos en {ha(GROSS)} al oriente de Torreón. Lotes desde {mill(PRECIO_MIN, 2)} y casa de {FI.M2_CASA:.0f} m² lista en 8 meses. Descarga el brochure.">
<meta property="og:title" content="{NOMBRE} · Vivir entre nogales">
<meta property="og:description" content="Sombra de cuarenta años, agua propia a presión, calles iluminadas y seguridad 24 horas. Lotes desde {mill(PRECIO_MIN, 2)}. Descarga el brochure.">
<meta property="og:image" content="https://nogalera.capitaltorreon.com{hero}">
<meta name="theme-color" content="#0e120f">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&family=Inter:wght@400;500;600&display=swap">
<link rel="stylesheet" href="/inicio/inicio.css">
<link rel="preload" as="image" href="{hero}">
</head>
<body>
<header class="cab"><div class="ancho">
  <a class="marca" href="/inicio/"><b>{NOMBRE}</b><span>La Paz · Torreón</span></a>
  <nav class="nav" aria-label="Secciones"><a href="#huerta">La huerta</a><a href="#casa">La casa</a><a href="#dia">Un día aquí</a><a href="#noches">Las noches</a><a href="#precios">Precios</a><a class="boton" href="#brochure">Descargar el brochure</a></nav>
</div></header>

<section class="hero">
  <img src="{hero}" alt="" fetchpriority="high">
  <div class="ancho hero-grid">
    <div class="hero-texto">
      <p class="ojo">Preventa · Etapa 1 · Oriente de Torreón</p>
      <h1>Vivir entre nogales de cuarenta años.</h1>
      <p class="lede">{f0(N)} casas en una huerta de {ha(GROSS)} que se queda como huerta: {f0(QUEDAN)} nogales adultos en pie, calles bajo su sombra e iluminadas de noche, agua propia a presión y seguridad las 24 horas. Lujo de verdad, a un precio que sí se puede.</p>
      <ul class="chips"><li>Lotes desde {mill(PRECIO_MIN, 2)}</li><li>Casa de {FI.M2_CASA:.0f} m² lista en 8 meses</li><li>Club, pista de 3.3 km y parques</li><li>A 15 minutos del oriente de Torreón</li></ul>
    </div>
    <div class="hero-forma">{forma_brochure("forma-arriba")}</div>
  </div>
  <span class="bajar">Baja ↓</span>
</section>

<div class="cifras"><div class="ancho"><dl>
  <div><dt>Nogales adultos</dt><dd>{f0(QUEDAN)}<small>mapeados uno por uno, se quedan</small></dd></div>
  <div><dt>Hectáreas</dt><dd>{GROSS/1e4:,.0f}<small>una sola huerta, al oriente</small></dd></div>
  <div><dt>Casas</dt><dd>{f0(N)}<small>lotes de {LOTE_MIN['m2']:,.0f} a {max(p['m2'] for p in LOTES):,.0f} m²</small></dd></div>
  <div><dt>Pista</dt><dd>3.3 km<small>bajo los nogales, iluminada</small></dd></div>
  <div><dt>Fachadas</dt><dd>{len(NF.NOMBRES)}<small>una sola casa, nueve caras</small></dd></div>
  <div><dt>Seguridad</dt><dd>24 h<small>barda, cámaras y acceso con pórtico</small></dd></div>
</dl></div></div>

<section id="huerta"><div class="ancho">
  <div class="dos rev">
    <div class="texto"><p class="ojo">La huerta</p><h2>La sombra ya está puesta.</h2>
      <p class="lede">Un fraccionamiento nuevo tarda veinte años en tener árboles. Aquí los nogales llevan cuarenta: {f0(QUEDAN)} de los {f0(R['arboles'])} que hay en la huerta se quedan donde están, y las calles se trazaron entre ellos. Cada lote tiene los suyos, y el fraccionamiento los riega y los poda.</p>
      <p>En verano, la copa de un nogal baja varios grados la temperatura de la casa y de la calle. Es lo que ningún otro desarrollo de Torreón puede vender: sombra de verdad, desde el primer día. Y en octubre, nuez.</p></div>
    {foto_c("completo-parque", lazy=False)}
  </div>
  <div class="galeria grande rev" style="margin-top:1rem">{foto_c("completo-bulevar")}{foto_c("calle-dia")}{foto_c("completo-aereo", ancha=True)}</div>
</div></section>

<section id="casa" class="crema2"><div class="ancho">
  <div class="dos inv rev">
    <div class="texto"><p class="ojo">La casa</p><h2>Una casa pensada hasta el último clóset.</h2>
      <p class="lede">Modelo Nogal: {FI.M2_CASA:.0f} m² en dos plantas, cuatro recámaras cada una con su baño, sala, comedor y cocina abiertos al portal y al jardín, azotea aprovechable y cochera para dos. Se construye con molde y cuadrillas en serie: se entrega en 8 meses, con garantía, al precio de cualquier constructor.</p>
      <p>Y nueve fachadas distintas sobre la misma casa, asignadas por lote, para que la calle se vea rica y pareja. Tú eliges el lote por la fachada que te gusta.</p></div>
    {foto_c("completo-casa")}
  </div>
  <h3 class="centrado rev" style="margin:3rem 0 1rem">Una casa, nueve fachadas</h3>
  <div class="fachadas-c rev">{fachadas_c}</div>
  <div class="galeria rev" style="margin-top:1.5rem">{foto("interior-tarde")}{foto("interior-comedor")}{foto("portal-atardecer")}{foto_c("cuadra-lejos", ancha=True)}</div>
  <details class="planos rev"><summary>Ver las nueve fachadas en plano</summary><div class="fachadas">{fachadas}</div></details>
</div></section>

<section id="dia"><div class="ancho">
  <p class="ojo rev">Un día aquí</p><h2 class="rev">De la mañana a la noche.</h2>
  <div class="tres rev">
    <div><span class="hora">7:30</span>{foto_c("completo-casa-frente", "Sales a correr por la pista, 3.3 km bajo los nogales, y regresas a desayunar en el portal.")}</div>
    <div><span class="hora">14:00</span>{foto_c("cuadra", "A mediodía la calle está en sombra completa: los niños van en bici al parque sin cruzar una sola avenida.")}</div>
    <div><span class="hora">21:00</span>{foto_c("calle-noche", "De noche, las lámparas bajas y los nogales iluminados. Caminas al club y regresas a la casa encendida.")}</div>
  </div>
</div></section>

<section id="noches" class="oscuro"><div class="ancho">
  <p class="ojo rev">Las noches</p><h2 class="rev">De noche es cuando más se nota.</h2>
  <p class="lede rev">Los nogales se iluminan desde abajo, las calles llevan arbotantes bajos y cálidos, la pista y los parques tienen balizas, y el acceso se ve desde la calzada. {f0(LZ['puntos'])} puntos de luz, cada uno en su lugar. Caminar de noche bajo los árboles, con la casa encendida al fondo, es la razón por la que la gente se queda.</p>
  <div class="galeria grande rev" style="margin-top:2rem">{foto_c("completo-entrada", ancha=True)}{foto_c("fachada-noche")}{foto("noche-banqueta")}{foto("portal-noche")}{foto("parque-noche")}{foto("noche-alta")}{foto("aerea-noche")}</div>
</div></section>

<section id="incluye"><div class="ancho">
  <p class="ojo rev">Lo que incluye</p><h2 class="rev">Todo lo que hace que valga.</h2>
  <ul class="incluye rev">
    <li><b>Seguridad 24 horas</b><p>Barda perimetral con cámaras cada 60 m, acceso con pórtico, caseta, reja y control de visitas por app. Guardias y rondín las 24 horas.</p></li>
    <li><b>Agua propia, a presión</b><p>Dos pozos, cisterna y una red calculada esquina por esquina: 3 kg/cm² en la regadera a cualquier hora. Planta de tratamiento propia; los nogales se riegan con agua tratada.</p></li>
    <li><b>Club social y deportivo</b><p>Salón con oficinas, gimnasio de dos niveles, canchas de tenis y pádel, y dos parques dentro de la huerta.</p></li>
    <li><b>La pista</b><p>3.3 km bajo los nogales, junto a la barda, con estaciones e iluminación: para correr o caminar sin salir del fraccionamiento.</p></li>
    <li><b>Calles de verdad</b><p>Bulevar de acceso con camellón de nogales, cruces elevados, banquetas anchas, alumbrado, fibra óptica y drenaje pluvial.</p></li>
    <li><b>Una operadora profesional</b><p>Mantenimiento, jardinería, pintura y seguridad con cuentas abiertas: cada mes sabes en qué se gasta tu cuota, y hay fondo de reserva.</p></li>
  </ul>
  <div class="galeria rev" style="margin-top:2.5rem">{foto_c("acceso-atardecer")}{foto_c("completo-club")}{foto("pista-tarde")}{foto_c("completo-parque-alto")}</div>
</div></section>

<section id="precios" class="crema2"><div class="ancho">
  <p class="ojo rev">Precios de la etapa 1</p><h2 class="rev">Lujo a un precio que sí se puede.</h2>
  <p class="lede rev">La etapa 1 sale al precio más bajo que va a tener el proyecto: la lista sube {pct(FI.ESCALON_ETAPA, 0)} en cada etapa, conforme se construye el resto. Quien compra primero, compra más barato y ve subir su lote.</p>
  <div class="precios rev">
    <div class="precio"><p class="ojo">Lote desde</p><strong>{mill(PRECIO_MIN, 2)}</strong><p>{LOTE_MIN['m2']:,.0f} m² urbanizado: calle, agua, luz, fibra, barda y sus nogales.</p></div>
    <div class="precio"><p class="ojo">Lote típico</p><strong>{mill(PRECIO_TIPO, 2)}</strong><p>{LOTE_TIPO_I} m² a ${f0(PRECIO_BASE)}/m². Frente a parque o bulevar, un poco más.</p></div>
    <div class="precio"><p class="ojo">Casa Modelo Nogal</p><strong>{mill(FI.PRECIO_CASA, 2)}</strong><p>{FI.M2_CASA:.0f} m² llave en mano en 8 meses, con la fachada de tu lote y garantía.</p></div>
    <div class="precio destacado"><p class="ojo">Lote típico + casa</p><strong>{mill(PAQUETE_I, 2)}</strong><p>Una casa nueva de {FI.M2_CASA:.0f} m² en {LOTE_TIPO_I} m² entre nogales, con club, pista y seguridad.</p></div>
  </div>
  <p class="nota" style="margin-top:1.25rem">Contado, crédito hipotecario o plan directo con 30 % de enganche y hasta 18 meses. Mantenimiento y seguridad: ${f0(FI.CUOTA_CASA)} al mes por casa, más el agua medida. Precios de referencia en pesos de 2026; la lista vigente viene en el brochure.</p>
  <h3 class="rev" style="margin:3rem 0 1rem">Cómo se compra</h3>
  <ol class="pasos rev">
    <li><b>1 · El brochure</b><p>Déjanos tu nombre, celular y correo. Te mandamos el plano con los lotes de la etapa 1, la lista de precios y la casa con sus fachadas.</p></li>
    <li><b>2 · La visita</b><p>Recorres la huerta con nosotros, eliges tu lote por su fachada y sus nogales, y te enseñamos la casa muestra.</p></li>
    <li><b>3 · El apartado</b><p>Apartas con un pago chico; firmas con el notario cuando tu crédito o tu plan está listo. Tu lote queda a tu nombre desde el primer día.</p></li>
  </ol>
</div></section>

<section id="galeria"><div class="ancho">
  <p class="ojo rev">Todas las imágenes</p><h2 class="rev">Recórrelo.</h2>
  <p class="lede rev">Las imágenes salen de la maqueta digital del proyecto: el plano real, los nogales en su lugar exacto y la casa con sus fachadas. Toca cualquiera para verla grande.</p>
  <div class="galeria rev" style="margin-top:2rem">{"".join(foto_c(n) for n in todas_c)}{"".join(foto(n) for n in todas)}</div>
</div></section>

<section id="brochure" class="contacto"><div class="ancho">
  <div class="dos">
    <div class="texto rev"><p class="ojo">El brochure</p><h2>Llévate La Nogalera en el bolsillo.</h2>
      <p class="lede">El brochure trae el plano con los lotes de la etapa 1 y sus nogales, la lista de precios, la casa Modelo Nogal con sus nueve fachadas, lo que incluye el fraccionamiento y cómo se compra.</p>
      <ul class="lista-brochure"><li>Plano con lotes disponibles y precio de cada uno</li><li>La casa: plantas, fachadas y acabados</li><li>Club, pista, parques, agua y seguridad</li><li>Formas de pago y pasos para comprar</li></ul>
      <p class="nota">Contestamos el mismo día. Tus datos solo los usa el equipo de ventas de {NOMBRE}.</p></div>
    <div class="rev">{forma_brochure("forma-abajo")}</div>
  </div>
</div></section>

<footer><div class="ancho"><span>{NOMBRE} · La Paz, Torreón, Coahuila. Anteproyecto: las imágenes son de la maqueta digital del proyecto, no fotografías; cifras de referencia.</span><span><a href="/">Proyecto técnico</a></span></div></footer>
<a class="boton fijo" href="#brochure">Descargar el brochure</a>
<dialog class="visor" id="visor" aria-label="Imagen"><figure><img src="" alt=""><figcaption></figcaption></figure><button type="button" class="cerrar">Cerrar ✕</button><button type="button" class="flecha ant" aria-label="Anterior">‹</button><button type="button" class="flecha sig" aria-label="Siguiente">›</button></dialog>
<script src="/inicio/inicio.js" defer></script>
</body>
</html>
"""
    d = os.path.join(PUB, "inicio"); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(html)
    print("ok inicio")
