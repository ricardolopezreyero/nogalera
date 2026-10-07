# ======================= LA PÁGINA DEL CLIENTE: /inicio/ (se ejecuta dentro de sitio.py) =======================
# Una sola página, aparte del tablero del proyecto: lo que ve quien quiere comprar. Imágenes: public/inicio/img/ (renders.js --lista renders_inicio.json).
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

def foto(n, ancha=False, lazy=True):
    t = PIE_IMG.get(n, n)
    return (f'<figure class="foto{" ancha" if ancha else ""}"><a href="/inicio/img/{n}.jpg" data-grande="/inicio/img/{n}.jpg" data-titulo="{e(t)}">'
            f'<img src="/inicio/img/t/{n}.jpg" alt="{e(t)}" width="960" height="540"{" loading=lazy" if lazy else ""}></a><figcaption>{e(t)}</figcaption></figure>')

def inicio():
    fachadas = "".join(f'<figure>{CD.fachada(n)}<figcaption><b>{e(n)}</b>{e(CD.TEXTO[n])}</figcaption></figure>' for n in NF.NOMBRES)
    todas = [n for n in INICIO_IMGS if n != "hero-noche"]
    html = f"""<!doctype html>
<html lang="es-MX">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{NOMBRE} · Vivir entre nogales, al oriente de Torreón</title>
<meta name="description" content="{NOMBRE}: {f0(N)} casas entre {f0(QUEDAN)} nogales adultos en {ha(GROSS)} al oriente de Torreón. Lotes desde {mill(PRECIO_MIN, 2)} y casa de {FI.M2_CASA:.0f} m² lista en 8 meses. Deja tus datos.">
<meta property="og:title" content="{NOMBRE} · Vivir entre nogales">
<meta property="og:description" content="Sombra de 40 años, agua propia a presión, calles iluminadas y seguridad 24 horas. Lotes desde {mill(PRECIO_MIN, 2)}.">
<meta property="og:image" content="https://nogalera.capitaltorreon.com/inicio/img/hero-noche.jpg">
<meta name="theme-color" content="#0e120f">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Inter:wght@400;600&display=swap">
<link rel="stylesheet" href="/inicio/inicio.css">
<link rel="preload" as="image" href="/inicio/img/hero-noche.jpg">
</head>
<body>
<header class="cab"><div class="ancho">
  <a class="marca" href="/inicio/"><b>{NOMBRE}</b><span>La Paz · Torreón</span></a>
  <nav class="nav" aria-label="Secciones"><a href="#huerta">La huerta</a><a href="#casa">La casa</a><a href="#noches">Las noches</a><a href="#incluye">Lo que incluye</a><a href="#precios">Precios</a><a class="boton" href="#contacto">Quiero información</a></nav>
</div></header>

<section class="hero">
  <img src="/inicio/img/hero-noche.jpg" alt="" fetchpriority="high">
  <div class="ancho">
    <p class="ojo">Preventa · Etapa 1 · Oriente de Torreón</p>
    <h1>Vivir entre nogales de cuarenta años.</h1>
    <p class="lede">{f0(N)} casas en una huerta de {ha(GROSS)} que se queda como huerta: {f0(QUEDAN)} nogales adultos en pie, calles bajo su sombra e iluminadas de noche, agua propia a presión y seguridad las 24 horas. Lujo de verdad, a un precio que sí se puede.</p>
    <div class="acciones"><a class="boton" href="#contacto">Déjame tus datos</a><a class="boton linea" href="#casa">Ver la casa</a></div>
    <ul class="chips"><li>Lotes desde {mill(PRECIO_MIN, 2)}</li><li>Casa de {FI.M2_CASA:.0f} m² lista en 8 meses</li><li>Club, pista de 3.3 km y parques</li><li>A 15 minutos del oriente de Torreón</li></ul>
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
  <div class="dos">
    <div class="texto"><p class="ojo">La huerta</p><h2>La sombra ya está puesta.</h2>
      <p class="lede">Un fraccionamiento nuevo tarda veinte años en tener árboles. Aquí los nogales llevan cuarenta: {f0(QUEDAN)} de los {f0(R['arboles'])} que hay en la huerta se quedan donde están, y las calles se trazaron entre ellos. Cada lote tiene los suyos, y el fraccionamiento los riega y los poda.</p>
      <p>En verano, la copa de un nogal baja varios grados la temperatura de la casa y de la calle. Es lo que ningún otro desarrollo de Torreón puede vender: sombra de verdad, desde el primer día.</p></div>
    {foto("calle-dia", lazy=False)}
  </div>
  <div class="galeria" style="margin-top:1rem">{foto("calle-atardecer")}{foto("parque-dia")}{foto("bulevar-dia")}{foto("aerea-tarde")}</div>
</div></section>

<section id="casa" class="crema2"><div class="ancho">
  <div class="dos inv">
    <div class="texto"><p class="ojo">La casa</p><h2>Una casa pensada hasta el último clóset.</h2>
      <p class="lede">Modelo Nogal: {FI.M2_CASA:.0f} m² en dos plantas, cuatro recámaras cada una con su baño, sala, comedor y cocina abiertos al portal y al jardín, azotea aprovechable y cochera para dos. Se construye con molde y cuadrillas en serie: se entrega en 8 meses, con garantía, al precio de cualquier constructor.</p>
      <p>Y nueve fachadas distintas sobre la misma casa, asignadas por lote, para que la calle se vea rica y pareja: cantera, celosía, ladrillo, duela, concreto… Tú eliges el lote por la fachada que te gusta.</p></div>
    {foto("casa-tarde")}
  </div>
  <div class="galeria" style="margin-top:1rem">{foto("interior-tarde")}{foto("interior-comedor")}{foto("portal-atardecer")}{foto("casa-vecinas")}</div>
  <h3 style="margin:2.5rem 0 1rem">Las nueve fachadas</h3>
  <div class="fachadas">{fachadas}</div>
</div></section>

<section id="noches" class="oscuro"><div class="ancho">
  <p class="ojo">Las noches</p><h2>De noche es cuando más se nota.</h2>
  <p class="lede">Los nogales se iluminan desde abajo, las calles llevan arbotantes bajos y cálidos, la pista y los parques tienen balizas, y el acceso se ve desde la calzada. {f0(LZ['puntos'])} puntos de luz, cada uno en su lugar. Caminar de noche bajo los árboles, con la casa encendida al fondo, es la razón por la que la gente se queda.</p>
  <div class="galeria grande" style="margin-top:2rem">{foto("noche-banqueta", ancha=True)}{foto("casa-noche")}{foto("portal-noche")}{foto("acceso-noche")}{foto("bulevar-noche")}{foto("parque-noche")}{foto("noche-alta")}{foto("aerea-noche", ancha=True)}</div>
</div></section>

<section id="incluye"><div class="ancho">
  <p class="ojo">Lo que incluye</p><h2>Todo lo que hace que valga.</h2>
  <ul class="incluye">
    <li><b>Seguridad 24 horas</b><p>Barda perimetral con cámaras cada 60 m, acceso con pórtico, caseta, reja y control de visitas por app. Guardias y rondín las 24 horas.</p></li>
    <li><b>Agua propia, a presión</b><p>Dos pozos, cisterna y una red calculada esquina por esquina: 3 kg/cm² en la regadera a cualquier hora. Planta de tratamiento propia; los nogales se riegan con agua tratada.</p></li>
    <li><b>Club social y deportivo</b><p>Salón con oficinas, gimnasio de dos niveles, canchas de tenis y pádel, y dos parques dentro de la huerta.</p></li>
    <li><b>La pista</b><p>3.3 km bajo los nogales, junto a la barda, con estaciones e iluminación: para correr o caminar sin salir del fraccionamiento.</p></li>
    <li><b>Calles de verdad</b><p>Bulevar de acceso con camellón de nogales, cruces elevados, banquetas anchas, alumbrado, fibra óptica y drenaje pluvial.</p></li>
    <li><b>Una operadora profesional</b><p>Mantenimiento, jardinería, pintura y seguridad con cuentas abiertas: cada mes sabes en qué se gasta tu cuota, y hay fondo de reserva.</p></li>
  </ul>
  <div class="galeria" style="margin-top:2.5rem">{foto("acceso-atardecer")}{foto("club-tarde")}{foto("pista-tarde")}{foto("parque-pergola")}</div>
</div></section>

<section id="precios" class="crema2"><div class="ancho">
  <p class="ojo">Precios de la etapa 1</p><h2>Lujo a un precio que sí se puede.</h2>
  <p class="lede">La etapa 1 sale al precio más bajo que va a tener el proyecto: la lista sube {pct(FI.ESCALON_ETAPA, 0)} en cada etapa, conforme se construye el resto. Quien compra primero, compra más barato y ve subir su lote.</p>
  <div class="precios">
    <div class="precio"><p class="ojo">Lote desde</p><strong>{mill(PRECIO_MIN, 2)}</strong><p>{LOTE_MIN['m2']:,.0f} m² urbanizado: calle, agua, luz, fibra, barda y sus nogales.</p></div>
    <div class="precio"><p class="ojo">Lote típico</p><strong>{mill(PRECIO_TIPO, 2)}</strong><p>{LOTE_TIPO_I} m² a ${f0(PRECIO_BASE)}/m². Frente a parque o bulevar, un poco más.</p></div>
    <div class="precio"><p class="ojo">Casa Modelo Nogal</p><strong>{mill(FI.PRECIO_CASA, 2)}</strong><p>{FI.M2_CASA:.0f} m² llave en mano en 8 meses, con la fachada de tu lote y garantía.</p></div>
    <div class="precio destacado"><p class="ojo">Lote típico + casa</p><strong>{mill(PAQUETE_I, 2)}</strong><p>Una casa nueva de {FI.M2_CASA:.0f} m² en {LOTE_TIPO_I} m² entre nogales, con club, pista y seguridad.</p></div>
  </div>
  <p class="nota" style="margin-top:1.25rem">Contado, crédito hipotecario o plan directo con 30 % de enganche y hasta 18 meses. Mantenimiento y seguridad: ${f0(FI.CUOTA_CASA)} al mes por casa, más el agua medida. Precios de referencia en pesos de 2026; la lista vigente la da el equipo de ventas.</p>
</div></section>

<section id="galeria"><div class="ancho">
  <p class="ojo">Todas las imágenes</p><h2>Recórrelo.</h2>
  <p class="lede">Las imágenes salen de la maqueta digital del proyecto: el plano real, los nogales en su lugar exacto y la casa con sus fachadas. Toca cualquiera para verla grande.</p>
  <div class="galeria" style="margin-top:2rem">{"".join(foto(n) for n in todas)}</div>
</div></section>

<section id="contacto" class="contacto"><div class="ancho">
  <div class="dos">
    <div class="texto"><p class="ojo">Quiero información</p><h2>Déjanos tus datos y te contamos todo.</h2>
      <p class="lede">Te mandamos la lista de precios con los lotes disponibles, el plano para elegir el tuyo y una cita para recorrer la huerta. Sin compromiso.</p>
      <p class="nota">Contestamos el mismo día. Tus datos solo los usa el equipo de ventas de {NOMBRE}.</p></div>
    <div>
      <form id="forma" novalidate>
        <label>Nombre <input type="text" name="nombre" autocomplete="name" required maxlength="120"></label>
        <label>Celular <input type="tel" name="celular" autocomplete="tel" inputmode="tel" required placeholder="871 000 0000"></label>
        <label>Correo <input type="email" name="correo" autocomplete="email" required></label>
        <fieldset><legend>¿Sería tu primera casa o tu segunda casa?</legend><div class="opciones">
          <label><input type="radio" name="casa" value="primera" required> Primera casa</label><label><input type="radio" name="casa" value="segunda"> Segunda casa</label></div></fieldset>
        <fieldset><legend>¿Tienes acceso a un crédito de más de 4 millones de pesos?</legend><div class="opciones">
          <label><input type="radio" name="credito" value="si" required> Sí</label><label><input type="radio" name="credito" value="no"> No</label><label><input type="radio" name="credito" value="nose"> No lo sé</label></div></fieldset>
        <fieldset><legend>¿Qué tan rápido quisieras comprar?</legend><div class="opciones">
          <label><input type="radio" name="rapidez" value="viendo" required> Estoy viendo</label><label><input type="radio" name="rapidez" value="ya"> Quiero comprar ya</label></div></fieldset>
        <label>¿Algo que quieras decirnos? (opcional) <textarea name="mensaje" maxlength="1000"></textarea></label>
        <label class="trampa" aria-hidden="true">Empresa <input type="text" name="empresa" tabindex="-1" autocomplete="off"></label>
        <p id="estado" class="estado" aria-live="polite"></p>
        <div><button type="submit" class="boton">Enviar mis datos</button></div>
        <p class="privacidad">Al enviar aceptas que {NOMBRE} te contacte por teléfono, WhatsApp o correo sobre este proyecto. No compartimos tus datos con nadie más.</p>
      </form>
      <div id="gracias" class="gracias" hidden><h3>Gracias, <b></b>.</h3><p>Ya tenemos tus datos. Te escribimos hoy mismo con la lista de precios, el plano y la cita para recorrer la huerta.</p><p class="nota">Mientras, puedes seguir viendo las <a href="#galeria">imágenes</a> o <a href="#casa">la casa</a>.</p></div>
    </div>
  </div>
</div></section>

<footer><div class="ancho"><span>{NOMBRE} · La Paz, Torreón, Coahuila. Anteproyecto: las imágenes son de la maqueta digital del proyecto, no fotografías; cifras de referencia.</span><span><a href="/">Proyecto técnico</a></span></div></footer>
<a class="boton fijo" href="#contacto">Quiero información</a>
<dialog class="visor" id="visor" aria-label="Imagen"><figure><img src="" alt=""><figcaption></figcaption></figure><button type="button" class="cerrar">Cerrar ✕</button><button type="button" class="flecha ant" aria-label="Anterior">‹</button><button type="button" class="flecha sig" aria-label="Siguiente">›</button></dialog>
<script src="/inicio/inicio.js" defer></script>
</body>
</html>
"""
    d = os.path.join(PUB, "inicio"); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(html)
    print("ok inicio")
