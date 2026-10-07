/* La Nogalera · creador de renders: elige escena, hora, vista y resolución; descarga el JPG. Usa /render/render3d.js. */
(function () {
  "use strict";
  var $ = function (id) { return document.getElementById(id); };
  var cv = $("cr-canvas"), selEsc = $("cr-escena"), selHora = $("cr-hora"), vistas = $("cr-vistas"), selRes = $("cr-res"), estado = $("cr-estado");
  var sl = { az: $("cr-az"), el: $("cr-el"), zoom: $("cr-zoom"), dist: $("cr-dist"), cz: $("cr-cz"), cont: $("cr-cont") };
  var r = null, esc = null, indice = [], listoRes;
  var C = window.CREADOR = { listo: new Promise(function (res) { listoRes = res; }) };
  function q(k) { return new URLSearchParams(location.search).get(k); }
  function leer() {
    if (!r) return; var c = r.cam;
    c.az = +sl.az.value; c.el = +sl.el.value; c.zoom = +sl.zoom.value; c.dist = +sl.dist.value; c.cz = +sl.cz.value; r.contornos = +sl.cont.value;
    r.pedir(); ajustes();
  }
  function escribir() {
    var c = r.cam; sl.az.value = c.az; sl.el.value = c.el; sl.zoom.value = c.zoom; sl.dist.value = c.dist; sl.cz.value = c.cz; sl.cont.value = r.contornos; ajustes();
  }
  function ajustes() {
    if (!r) return; var c = r.cam;
    $("cr-ajustes").value = JSON.stringify({ escena: esc.id, hora: r.hora, az: +c.az.toFixed(3), el: +c.el.toFixed(3), zoom: c.zoom, dist: +c.dist.toFixed(1), cx: +c.cx.toFixed(1), cy: +c.cy.toFixed(1), cz: +c.cz.toFixed(1), contornos: r.contornos });
  }
  function cargar(id, vista, hora) {
    esc = indice.filter(function (e) { return e.id === id; })[0] || indice[0];
    estado.textContent = "Cargando " + esc.titulo + "…";
    fetch("/datos/escenas/" + esc.id + ".json").then(function (x) { return x.json(); }).then(function (d) {
      d.id = esc.id; d.contornos = d.contornos === undefined ? 0.6 : d.contornos;
      if (hora) d.hora = hora;
      r = new Render3D(cv, d, { escalaRapida: d.prismas.length > 4000 ? 0.5 : 1 });
      var cam = (vista && d.vistas && d.vistas[vista]) || d.cam; Object.assign(r.cam, cam);
      r.onCam = escribir; r.orbita();
      vistas.innerHTML = "";
      Object.keys(d.vistas || {}).forEach(function (k) {
        var b = document.createElement("button"); b.type = "button"; b.textContent = k;
        b.addEventListener("click", function () { Object.assign(r.cam, d.vistas[k]); escribir(); r.pedir(); }); vistas.appendChild(b);
      });
      selHora.value = r.hora; escribir(); r.pedir();
      estado.textContent = esc.titulo + " · " + d.prismas.length.toLocaleString("es-MX") + " piezas · arrastra para girar, rueda para acercar";
      listoRes(true);
    });
  }
  C.imagen = function (w, h, ss, tipo, calidad) { return r.imagen(w, h, ss || 2, tipo, calidad); };
  fetch("/datos/escenas/index.json").then(function (x) { return x.json(); }).then(function (ix) {
    indice = ix;
    ix.forEach(function (e) { var o = document.createElement("option"); o.value = e.id; o.textContent = e.titulo; selEsc.appendChild(o); });
    var id = q("escena") || ix[0].id; selEsc.value = id;
    cargar(id, q("vista"), q("hora"));
  });
  selEsc.addEventListener("change", function () { cargar(selEsc.value); history.replaceState(null, "", "?escena=" + selEsc.value + "#crear"); });
  selHora.addEventListener("change", function () { if (!r) return; r.hora = selHora.value; r.construir(); r.pedir(); ajustes(); });
  Object.keys(sl).forEach(function (k) { sl[k].addEventListener("input", leer); });
  document.querySelectorAll("[data-mover]").forEach(function (b) {
    b.addEventListener("click", function () {
      if (!r) return; var m = b.getAttribute("data-mover"), c = r.cam, paso = Math.max(0.5, c.dist / 20), ca = Math.cos(c.az), sa = Math.sin(c.az);
      // adelante/atrás a lo largo de la mirada, izquierda/derecha de lado
      if (m === "adelante") { c.cx += sa * paso; c.cy += ca * paso; } else if (m === "atras") { c.cx -= sa * paso; c.cy -= ca * paso; }
      else if (m === "izq") { c.cx -= ca * paso; c.cy += sa * paso; } else if (m === "der") { c.cx += ca * paso; c.cy -= sa * paso; }
      r.pedir(); ajustes();
    });
  });
  $("cr-descargar").addEventListener("click", function () {
    if (!r) return; var p = selRes.value.split("x"), W = +p[0], H = +p[1];
    estado.textContent = "Generando " + W + " × " + H + "…";
    setTimeout(function () {
      var url = r.imagen(W, H, 2, "image/jpeg", 0.92), a = document.createElement("a");
      a.href = url; a.download = "nogalera-" + esc.id + "-" + r.hora + "-" + W + "x" + H + ".jpg"; document.body.appendChild(a); a.click(); a.remove();
      estado.textContent = "Listo: " + a.download;
    }, 30);
  });
  $("cr-copiar").addEventListener("click", function () { $("cr-ajustes").select(); document.execCommand("copy"); });
  window.addEventListener("resize", function () { if (r) r.pedir(); });
})();
