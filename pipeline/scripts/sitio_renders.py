# ======================= RENDERS (se ejecuta dentro de sitio.py) =======================
import n6_escenas as ESC                                   # genera public/datos/escenas/*.json al importarse
import renders_ia as RIA
json.dump(RIA.PROMPTS, open(f"{DAT}/escenas/prompts_ia.json", "w"), ensure_ascii=False, indent=1)
RENDERS_10 = ["calle", "casa", "aerea", "acceso", "bulevar", "parque", "pista", "interior", "portal", "noche"]
IDX = {e["id"]: e for e in ESC.INDICE}
HORAS_TXT = dict(dia="mediodía", tarde="tarde", atardecer="atardecer", noche="noche")

def renders():
    figs = []
    for i, k in enumerate(RENDERS_10):
        e = IDX[k]
        figs.append(f'''<figure class="render"><a href="/renders/img/{k}.jpg" target="_blank" rel="noopener"><img src="/renders/img/{k}.jpg" alt="{e(e_["titulo"]) if False else e_(e["titulo"])}" loading="lazy" width="1920" height="1080"></a>
<figcaption><span class="n">{i + 1:02d}</span> <b>{e_(e["titulo"])}</b> <span class="hora">{HORAS_TXT[e["hora"]]}</span><p>{e_(e["porque"])}</p><p class="nota"><a href="/renders/?escena={k}#crear">Abrir en el creador</a> · {e["prismas"]:,} piezas</p></figcaption></figure>''')
    extras = [e for e in ESC.INDICE if e["id"] not in RENDERS_10]
    cuerpo = f"""
<p class="frase"><b>Diez imágenes que venden el proyecto, hechas con la geometría real del proyecto.</b> No son fotos ni ilustraciones: cada render sale del mismo plano, la misma casa y los mismos nogales que el resto del sitio, con un motor de render propio. Abajo está el creador: cualquiera de estas escenas se puede girar, cambiar de hora y descargar en alta resolución para hacer los que hagan falta.</p>
<div class="renders">{"".join(figs)}</div>
<p class="nota">Estilo de maqueta: volúmenes, sombra de sol, cristales, bruma y contornos. Sirven para la presentación al dueño y al inversionista, y como guía exacta (encuadre, luz, qué se ve) para un render fotorrealista por computadora cuando se necesite. Más escenas en el creador: {", ".join(e_(e["titulo"]) for e in extras)}.</p>

<h2 id="crear">Creador de renders</h2>
<p>Elige la escena y la hora, gira con el ratón o el dedo (rueda para acercar), usa las vistas guardadas o los controles, y descarga el JPG en la resolución que quieras: pantalla, redes o impresión. «Copiar ajustes» guarda el encuadre exacto para repetirlo.</p>
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
           [("crear", "Creador de renders"), ("ia", "Render fotorrealista con IA")], script='<script src="/render/render3d.js"></script><script src="/renders/creador.js"></script>',
           descripcion="Renders de La Nogalera: la calle bajo los nogales, la casa, el acceso, el bulevar, el parque, la pista, el interior y el jardín; y el creador de renders.")
