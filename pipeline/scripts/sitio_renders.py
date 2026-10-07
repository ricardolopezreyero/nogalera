# ======================= RENDERS (se ejecuta dentro de sitio.py) =======================
import n6_escenas as ESC                                   # genera public/datos/escenas/*.json al importarse
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
<p class="nota">Las escenas están en <code>public/datos/escenas/</code> y las arma <code>pipeline/scripts/n6_escenas.py</code> (casas con sus nueve fachadas, calles, nogales, autos y gente). Para agregar una escena nueva se escribe ahí, con las mismas piezas. Los diez renders de arriba se generan con <code>pipeline/scripts/renders.js</code>.</p>
"""
    pagina("renders", "Renders", "08 · Renders", "Los diez renders que más venden La Nogalera, hechos con la geometría real del proyecto, y el creador para hacer todos los demás.", cuerpo,
           [("crear", "Creador de renders")], script='<script src="/render/render3d.js"></script><script src="/renders/creador.js"></script>',
           descripcion="Renders de La Nogalera: la calle bajo los nogales, la casa, el acceso, el bulevar, el parque, la pista, el interior y el jardín; y el creador de renders.")
