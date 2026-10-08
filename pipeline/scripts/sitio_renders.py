# ======================= RENDERS (se ejecuta dentro de sitio.py) =======================
import n6_completo                                         # genera public/datos/escenas/*.json (todas las escenas y el modelo completo) al importarse
import n6_escenas as ESC
import renders_ia as RIA
json.dump(RIA.PROMPTS, open(f"{DAT}/escenas/prompts_ia.json", "w"), ensure_ascii=False, indent=1)
RENDERS_10 = ["calle", "casa", "aerea", "acceso", "bulevar", "parque", "pista", "interior", "portal", "noche"]
IDX = {e["id"]: e for e in ESC.INDICE}
HORAS_TXT = dict(dia="mediodía", tarde="tarde", atardecer="atardecer", noche="noche", manana="mañana", amanecer="amanecer", crepusculo="crepúsculo")

FOTOS_LISTA = json.load(open(os.path.join(AQUI, "fotos_lista.json"), encoding="utf-8"))
FOTOS_TXT = {"completo-entrada": "La entrada: pórtico, casetas, reja y los nogales iluminados, al atardecer (modelo completo).", "completo-casa": "La casa Modelo Nogal en su cuadra real, con sus vecinas (modelo completo).", "completo-parque": "Parque Garza: nogales, pérgola, juegos y gente (modelo completo).", "completo-aereo": "El fraccionamiento completo desde el aire: cada casa, cada nogal, cada luminaria.", "completo-sur": "El fraccionamiento desde el sur, con la calzada y las huertas vecinas.", "completo-club": "El club: salón con oficinas, gimnasio, canchas y plaza.", "completo-bulevar": "Bulevar Nogal con su camellón y sendero.", "completo-entrada-alta": "El acceso desde el aire.", "completo-parque-alto": "Parque Garza desde el aire.", "completo-casa-frente": "La casa de frente.", "fachada-horizonte": "Fachada Horizonte: las dos losas que vuelan y la franja de ventanas.", "fachada-cantera": "Fachada Cantera.", "fachada-ladrillo": "Fachada Ladrillo.", "fachada-lamas": "Fachada Lamas.", "fachada-marco": "Fachada Marco.",
             "fachada-hacienda": "Fachada Hacienda.", "fachada-concreto": "Fachada Concreto.", "fachada-celosia": "Fachada Celosía.", "fachada-duela": "Fachada Duela.", "fachada-frente": "Horizonte de frente, desde la banqueta de enfrente.",
             "fachada-atardecer": "Horizonte al atardecer.", "fachada-noche": "Horizonte de noche, con el portal y las ventanas encendidas.", "cuadra-lejos": "La cuadra de lejos, con lente larga: las nueve fachadas seguidas bajo los nogales.",
             "cuadra": "La cuadra en escorzo.", "cuadra-alta": "La cuadra desde arriba.", "calle-dia": "La calle bajo los nogales a mediodía.", "calle-noche": "La calle de noche.", "acceso-atardecer": "El acceso al atardecer.",
             "portal-atardecer": "El portal y el jardín al atardecer.", "parque-dia": "Parque Garza.", "aerea-tarde": "La Nogalera desde el aire.", "aerea-acceso": "El acceso y el bulevar desde el aire."}
def concurso_html():
    """Los renders fotorrealistas (WebGL) que ya existen en public/renders/foto/img, con sus mapas de control."""
    figs = []
    for n, esc_, hora, vista, w, h in FOTOS_LISTA:
        if not os.path.exists(os.path.join(PUB, "renders", "foto", "img", n + ".jpg")): continue
        ctl = " · ".join(f'<a href="/renders/foto/control/{n}-{t}.png">{t}</a>' for t in ("depth", "normal", "lineart") if os.path.exists(os.path.join(PUB, "renders", "foto", "control", f"{n}-{t}.png")))
        figs.append(f'''<figure class="render"><a href="/renders/foto/img/{n}.jpg" target="_blank" rel="noopener"><img src="/renders/foto/img/{n}.jpg" alt="{e_(FOTOS_TXT.get(n, n))}" loading="lazy" width="{w}" height="{h}"></a>
<figcaption><b>{e_(FOTOS_TXT.get(n, n))}</b> <span class="hora">{HORAS_TXT[hora]}</span><p class="nota"><a href="/renders/foto/?escena={esc_}&amp;vista={vista}&amp;hora={hora}">Abrir en el render fotorrealista</a>{" · mapas de control: " + ctl if ctl else ""}</p></figcaption></figure>''')
    return f'<div class="renders">{"".join(figs)}</div>' if figs else "<p class=nota>Todavía no se han generado (node pipeline/scripts/fotos.js --control).</p>"

# ---------- historial de renders: cada subida al repositorio que cambió public/renders/foto/img es un lote ----------
HIST_DIR = os.path.join(PUB, "renders", "foto", "historial")
MESES_H = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
def _git(*args):
    import subprocess
    return subprocess.run(["git", *args], cwd=os.path.dirname(PUB), capture_output=True, text=True).stdout
def lotes_git():
    """Lotes anteriores, del más nuevo al más viejo: [{id, fecha, fecha_txt, titulo, archivos:[nombre…]}]. El lote más reciente
    del repositorio se omite cuando la carpeta img/ no tiene cambios sin subir (entonces ese lote es el que va hasta arriba)."""
    from datetime import datetime
    try:
        from zoneinfo import ZoneInfo; tz = ZoneInfo("America/Monterrey")
    except Exception: tz = None
    rel = "public/renders/foto/img"; lotes = []
    for linea in _git("log", "--format=%h|%cI|%s", "--", rel).splitlines():
        h, iso, asunto = linea.split("|", 2)
        archivos = [os.path.basename(a)[:-4] for a in _git("show", "--name-only", "--diff-filter=AM", "--format=", h, "--", rel).split() if a.endswith(".jpg") and not os.path.basename(a).startswith("p-")]
        if not archivos: continue
        f = datetime.fromisoformat(iso); f = f.astimezone(tz) if tz else f
        lotes.append({"id": f.strftime("%Y%m%d-%H%M") + "-" + h, "hash": h, "fecha": f.isoformat(), "fecha_txt": f"{f.day} de {MESES_H[f.month - 1]} de {f.year}, {f:%H:%M}", "titulo": asunto.split(":")[0][:110], "archivos": archivos})
    if lotes and not _git("status", "--porcelain", "--", rel).strip(): lotes = lotes[1:]
    return lotes
def extraer_lotes(lotes):
    """Saca de git las imágenes de cada lote a historial/<lote>/ y hace miniaturas; escribe historial/index.json para la galería."""
    from PIL import Image
    import subprocess
    salida = []
    for l in lotes:
        d = os.path.join(HIST_DIR, l["id"]); os.makedirs(os.path.join(d, "mini"), exist_ok=True); arch = []
        for n in l["archivos"]:
            dest = os.path.join(d, n + ".jpg"); mini = os.path.join(d, "mini", n + ".jpg")
            if not os.path.exists(dest):
                with open(dest, "wb") as fh: subprocess.run(["git", "show", f'{l["hash"]}:public/renders/foto/img/{n}.jpg'], cwd=os.path.dirname(PUB), stdout=fh)
            if not os.path.exists(mini):
                im = Image.open(dest).convert("RGB"); im.thumbnail((720, 720)); im.save(mini, quality=82, optimize=True)
            w, h = Image.open(mini).size
            arch.append({"n": n, "src": f"/renders/foto/historial/{l['id']}/{n}.jpg", "mini": f"/renders/foto/historial/{l['id']}/mini/{n}.jpg", "w": w, "h": h, "t": FOTOS_TXT.get(n, n)})
        salida.append({**l, "archivos": arch})
    os.makedirs(HIST_DIR, exist_ok=True)
    json.dump(salida, open(os.path.join(HIST_DIR, "index.json"), "w", encoding="utf-8"), ensure_ascii=False)
    return salida
def historial_html():
    lotes = extraer_lotes(lotes_git())
    if not lotes: return "<p class=nota>Todavía no hay lotes anteriores.</p>"
    partes = []
    for l in lotes:
        figs = "".join(f'<figure class="render mini"><a href="{a["src"]}" target="_blank" rel="noopener"><img src="{a["mini"]}" alt="{e_(a["t"])}" loading="lazy" width="{a["w"]}" height="{a["h"]}"></a><figcaption>{e_(a["t"])}</figcaption></figure>' for a in l["archivos"])
        cuantos = f'{len(l["archivos"])} render' + ("" if len(l["archivos"]) == 1 else "s")
        partes.append(f'<details class="lote"><summary><b>{e_(l["fecha_txt"])}</b> · {cuantos} <span class="nota">· {e_(l["titulo"])}</span> · <a href="/renders/concurso/?lote={l["id"]}">galería</a></summary>\n<div class="renders minis">{figs}</div></details>')
    return "\n".join(partes)

def renders():
    figs = []
    for i, k in enumerate(RENDERS_10):
        e = IDX[k]
        figs.append(f'''<figure class="render"><a href="/renders/img/{k}.jpg" target="_blank" rel="noopener"><img src="/renders/img/{k}.jpg" alt="{e(e_["titulo"]) if False else e_(e["titulo"])}" loading="lazy" width="1920" height="1080"></a>
<figcaption><span class="n">{i + 1:02d}</span> <b>{e_(e["titulo"])}</b> <span class="hora">{HORAS_TXT[e["hora"]]}</span><p>{e_(e["porque"])}</p><p class="nota"><a href="/renders/?escena={k}#crear">Abrir en el creador</a> · {e["prismas"]:,} piezas</p></figcaption></figure>''')
    extras = [e for e in ESC.INDICE if e["id"] not in RENDERS_10]
    cuerpo = f"""
<p class="frase" style="font-size:1.1rem"><b>🎬 Creador de renders fotorrealistas:</b> <a class="boton" href="/renders/foto/?escena=completo">abrir el creador</a> <span class="nota">cielo, nubes y sol de Torreón calculados por hora y fecha (amanecer, mediodía, atardecer, crepúsculo y noche con las luces encendidas), bruma, exposición, cámara con órbita, capas, calidad hasta 4K y mapas para IA. Arrastra para girar; la imagen se afina sola al soltar.</span></p>
<p class="frase" style="font-size:1.1rem"><b>🚶 Camina dentro del modelo 3D.</b> <a class="boton" href="/renders/foto/?escena=completo&amp;caminar=1">Caminar por el fraccionamiento completo</a> <a class="boton" href="/renders/foto/?escena=fachadas&amp;caminar=1">Caminar por la cuadra de las nueve fachadas</a> <a class="boton" href="/renders/foto/?escena=parque&amp;caminar=1">Caminar por el parque</a><br><span class="nota">Flechas para avanzar y girar, ratón o dedo para mirar, altura de la vista a pie, a 2 m, desde un balcón o a 10 m, y «Foto de aquí» para guardar el encuadre. El modelo completo pesa 47 MB: en computadora va bien; en celular usa la cuadra o el parque.</span></p>
<h2 id="concurso">Últimos renders</h2>
<p class="nota">Siempre aparecen aquí los más recientes; todos los anteriores quedan abajo, en el <a href="#historial">historial</a>.</p>
<p>Hechos con el motor fotorrealista (WebGL: materiales físicos, follaje de hojas, cielo con sol, sombras y oclusión ambiental) a 2560 × 1440. Cada uno trae sus mapas de profundidad, normales y líneas para llevarlo a fotografía con FLUX + ControlNet en una máquina con GPU (<code>pipeline/comfy/README.md</code>), o con gpt-image-2 desde el Worker (<code>renders_worker.py</code>).</p>
<p><a class="boton" href="/renders/concurso/">Ver la galería a pantalla completa</a> <span class="nota">clic a la derecha para avanzar, a la izquierda para regresar, F para pantalla completa.</span></p>
{concurso_html()}
<h2 id="historial">Historial de renders</h2>
<p>Cada vez que se sube un lote nuevo, el anterior baja aquí con su fecha. Nada se pierde: cada lote conserva sus imágenes en tamaño completo y su propia galería.</p>
{historial_html()}
<h3>Lo que hay en el modelo completo</h3>
<p class="nota">Cada lote: casa con su fachada, cochera con pérgola, andador, jardín con pasto, flores, arbustos recortados, agaves o grava, seto, árbol joven con tutor, balizas de jardín, llave de manguera, macetas junto a la puerta, tapete, interfón, medidor de luz, buzón y número, tambo de basura, bardas y rejas; patio con mesa y sillas, asador, sombrilla, columpio o trampolín, alberca en algunos, perro; azotea con tinaco, equipos de aire, calentador solar, paneles solares, antena y domo; canalón y bajadas de agua. Calles: arroyo con raya central amarilla y flechas, guarniciones, banquetas, rampas en las esquinas, pasos peatonales, señales de alto, velocidad y nomenclatura, bolardos, botes de basura, registros, bocas de tormenta, alcorques en los nogales de banqueta, pedestales de fibra, transformadores, hidrantes, cámaras de la barda, arbotantes y balizas reales, autos, bicicletas, gente caminando y perros. Parques: bordo, senderos, pérgola, bancas, botes, bebedero, ciclopuerto, aparatos de ejercicio, estación de la pista, fuente, kiosco, mesas de picnic, área de perros cercada, cancha de básquet con tableros, porterías, gradas, juegos de colores (columpios, torre con resbaladilla, trepador, sube y baja, casita), jardineras de flores, árboles jóvenes, arbustos, farolas y pájaros. Club: salón con oficinas, gimnasio, alberca con camastros, sombrillas y palmeras, fuente, canchas de tenis y pádel con malla sombra, gradas, plaza con pérgolas, bancas y macetones, estacionamientos con pluma y bolardos. Acceso: pórtico con letrero y cámaras, casetas, plumas, reja, muro de identidad, astas con banderas, jardineras con flores, bancas de espera, cajones de visitas, mini súper, señales, calzada con carriles. Servicios: planta de tratamiento, vaso de tormentas, pozos, cisterna, acopio. Y los 1,943 nogales en su sitio, cada uno distinto, con nueces.</p>
<h2 id="diez">Los diez renders de maqueta</h2>
<p class="frase"><b>Diez imágenes que venden el proyecto, hechas con la geometría real del proyecto.</b> No son fotos ni ilustraciones: cada render sale del mismo plano, la misma casa y los mismos nogales que el resto del sitio, con un motor de render propio. Abajo está el creador: cualquiera de estas escenas se puede girar, cambiar de hora y descargar en alta resolución para hacer los que hagan falta.</p>
<div class="renders">{"".join(figs)}</div>
<p class="nota">Estilo de maqueta: volúmenes, sombra de sol, cristales, bruma y contornos. Sirven para la presentación al dueño y al inversionista, y como guía exacta (encuadre, luz, qué se ve) para un render fotorrealista por computadora cuando se necesite. Más escenas en el creador: {", ".join(e_(e["titulo"]) for e in extras)}.</p>

<h2 id="crear">Creador rápido (maqueta)</h2>
<p>Versión ligera, sin WebGL, para el teléfono o para encuadrar rápido: elige la escena y la hora, gira con el ratón o el dedo (rueda para acercar), usa las vistas guardadas o los controles y descarga el JPG. «Copiar ajustes» guarda el encuadre exacto; el mismo encuadre se abre en el <a href="/renders/foto/">creador fotorrealista</a>.</p>
<div class="creador">
  <div class="cr-lienzo"><canvas id="cr-canvas" aria-label="Render"></canvas><p id="cr-estado" class="nota">Cargando…</p></div>
  <div class="cr-controles">
    <label>Escena <select id="cr-escena" class="sel"></select></label>
    <label>Hora <select id="cr-hora" class="sel"><option value="dia">Mediodía</option><option value="tarde">Tarde</option><option value="atardecer">Atardecer</option><option value="noche">Noche</option></select></label>
    <div class="cr-fila"><span>Vistas</span><div id="cr-vistas" class="cr-botones"></div></div>
    <div class="cr-fila"><span>Mover</span><div class="cr-botones"><button type="button" data-mover="izq">←</button><button type="button" data-mover="adelante">↑</button><button type="button" data-mover="atras">↓</button><button type="button" data-mover="der">→</button></div></div>
    <label>Giro <input type="range" id="cr-az" min="-3.1416" max="6.2832" step="0.01"></label>
    <label>Altura de la mirada <input type="range" id="cr-el" min="0" max="1.5" step="0.005"></label>
    <label>Acercamiento <input type="range" id="cr-zoom" min="-30" max="16" step="1"></label>
    <label>Distancia <input type="range" id="cr-dist" min="4" max="2000" step="1"></label>
    <label>Altura del centro <input type="range" id="cr-cz" min="-2" max="40" step="0.1"></label>
    <label>Contornos <input type="range" id="cr-cont" min="0" max="1" step="0.05"></label>
    <label>Resolución <select id="cr-res" class="sel"><option value="1920x1080">1920 × 1080 (pantalla)</option><option value="2560x1440">2560 × 1440</option><option value="3840x2160">3840 × 2160 (4K, impresión)</option><option value="1080x1080">1080 × 1080 (Instagram)</option><option value="1080x1350">1080 × 1350 (vertical)</option><option value="1080x1920">1080 × 1920 (historia)</option></select></label>
    <div class="cr-botones"><button type="button" id="cr-descargar" class="boton">Descargar JPG</button><button type="button" id="cr-copiar">Copiar ajustes</button></div>
    <textarea id="cr-ajustes" rows="3" readonly aria-label="Ajustes del encuadre"></textarea>
  </div>
</div>
<h2 id="foto">Render fotorrealista (WebGL) y mapas de control</h2>
<p>El mismo modelo, renderizado con materiales físicos, follaje de hojas, cielo con sol, sombras suaves y oclusión ambiental: <a href="/renders/foto/">abrir el render fotorrealista</a>. Además saca los mapas de <b>profundidad, normales y líneas</b> de cada encuadre, que son lo que una IA con ControlNet (FLUX) necesita para convertir el modelo en una fotografía respetando la geometría exacta. La tubería completa, con el flujo de ComfyUI para una máquina con GPU, está en <code>pipeline/comfy/README.md</code>; los renders de concurso se generan con <code>node pipeline/scripts/fotos.js --control</code>.</p>
<h2 id="ia">Render fotorrealista con IA</h2>
<p>Toma el encuadre que tengas arriba en el creador, lo manda como referencia al modelo de imágenes de OpenAI junto con un prompt muy detallado del proyecto (nogales pecaneros, las nueve fachadas, materiales, luz de Torreón) y devuelve una fotografía. La llave de OpenAI vive en los secretos del Worker de Cloudflare, nunca en el sitio; la clave de abajo es la contraseña que protege el gasto. Cada imagen en alta calidad cuesta centavos de dólar y tarda de 30 a 90 segundos.</p>
<div class="creador">
  <div class="cr-lienzo"><div id="ia-salida" class="renders"></div><p id="ia-estado" class="nota">Comprobando…</p></div>
  <div class="cr-controles">
    <label>Clave <input type="password" id="ia-clave" class="sel" autocomplete="off" placeholder="RENDER_CLAVE del Worker"></label>
    <label>Modelo <select id="ia-modelo" class="sel"><option value="gpt-image-2">gpt-image-2</option><option value="gpt-image-1">gpt-image-1</option></select></label>
    <label>Calidad <select id="ia-calidad" class="sel"><option value="high">Alta</option><option value="medium">Media</option><option value="low">Baja (pruebas)</option></select></label>
    <label>Tamaño <select id="ia-tamano" class="sel"><option value="1536x1024">1536 × 1024 (horizontal)</option><option value="1024x1536">1024 × 1536 (vertical)</option><option value="1024x1024">1024 × 1024</option></select></label>
    <label><input type="checkbox" id="ia-ref" checked> Usar el encuadre del creador como referencia</label>
    <label>Prompt (edítalo si quieres) <textarea id="ia-prompt" rows="12"></textarea></label>
    <div class="cr-botones"><button type="button" id="ia-generar" class="boton">Generar render fotorrealista</button></div>
  </div>
</div>
<p class="nota">Los prompts de cada escena están en <code>pipeline/scripts/renders_ia.py</code> (y en <code>public/datos/escenas/prompts_ia.json</code>); el mismo archivo genera las diez imágenes en lote desde una computadora con la llave en la variable <code>OPENAI_API_KEY</code>: <code>python3 pipeline/scripts/renders_ia.py</code>. El endpoint es <code>worker/index.js</code>.</p>
<p class="nota">Las escenas están en <code>public/datos/escenas/</code> y las arma <code>pipeline/scripts/n6_escenas.py</code> (casas con sus nueve fachadas, calles, nogales, autos y gente). Para agregar una escena nueva se escribe ahí, con las mismas piezas. Los diez renders de arriba se generan con <code>pipeline/scripts/renders.js</code>.</p>
"""
    pagina("renders", "Renders", "08 · Renders", "Los diez renders que más venden La Nogalera, hechos con la geometría real del proyecto, y el creador para hacer todos los demás.", cuerpo,
           [("concurso", "Últimos renders"), ("historial", "Historial"), ("diez", "Los diez de maqueta"), ("crear", "Creador rápido (maqueta)"), ("foto", "Creador fotorrealista"), ("ia", "Render con IA")], script='<script src="/render/render3d.js"></script><script src="/renders/creador.js"></script>',
           descripcion="Renders de La Nogalera: la calle bajo los nogales, la casa, el acceso, el bulevar, el parque, la pista, el interior y el jardín; y el creador de renders.")
