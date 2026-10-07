/* La Nogalera · visor 3D del Modelo Nogal. Sin librerías: cajas proyectadas en un canvas, estilo plano en blanco y negro.
   window.CASA3D = { cajas: [[x,y,z,w,d,h,color,grupo],…], centro: [x,y,z] } */
(function () {
  "use strict";
  var M = window.CASA3D, cv = document.getElementById("c3d"), ctx = cv.getContext("2d");
  var az = 0.62, el = 0.52, zoom = 2, cx = M.centro[0], cy = M.centro[1], cz = M.centro[2];
  var ver = { techo: true, pa: true, muebles: true, arboles: true, fach: true, ext: true, pb: true };
  var luz = [-0.4, -0.5, 0.77];
  var caras = [];
  function construir() {
    caras = [];
    M.cajas.forEach(function (b) {
      if (ver[b[7]] === false) return;
      var x = b[0], y = b[1], z = b[2], w = b[3], d = b[4], h = b[5];
      var v = [[x, y, z], [x + w, y, z], [x + w, y + d, z], [x, y + d, z], [x, y, z + h], [x + w, y, z + h], [x + w, y + d, z + h], [x, y + d, z + h]];
      var F = [[0, 3, 2, 1, [0, 0, -1]], [4, 5, 6, 7, [0, 0, 1]], [0, 1, 5, 4, [0, -1, 0]], [2, 3, 7, 6, [0, 1, 0]], [1, 2, 6, 5, [1, 0, 0]], [3, 0, 4, 7, [-1, 0, 0]]];
      F.forEach(function (f) { caras.push({ p: [v[f[0]], v[f[1]], v[f[2]], v[f[3]]], n: f[4], c: b[6], g: b[7], sb: b[8] }); });
    });
  }
  function proy(p) {
    var ca = Math.cos(az), sa = Math.sin(az), ce = Math.cos(el), se = Math.sin(el);
    var x = p[0] - cx, y = p[1] - cy, z = p[2] - cz;
    var x1 = x * ca - y * sa, y1 = x * sa + y * ca;
    return [x1, y1 * se + z * ce, y1 * ce - z * se];     // pantalla x, pantalla y (arriba), profundidad (más es más lejos)
  }
  function dibujar() {
    var W = cv.clientWidth, H = cv.clientHeight, r = window.devicePixelRatio || 1;
    if (cv.width !== W * r || cv.height !== H * r) { cv.width = W * r; cv.height = H * r; }
    ctx.setTransform(r, 0, 0, r, 0, 0); ctx.clearRect(0, 0, W, H);
    var esc = Math.min(W, H) / 32 * Math.pow(1.15, zoom);
    var ca = Math.cos(az), sa = Math.sin(az), ce = Math.cos(el), se = Math.sin(el);
    var vista = [0, ce, -se];                              // hacia dónde mira la cámara (en el marco girado)
    var lista = [];
    for (var i = 0; i < caras.length; i++) {
      var f = caras[i], n = f.n, nx = n[0] * ca - n[1] * sa, ny = n[0] * sa + n[1] * ca, nz = n[2];
      if (nx * vista[0] + ny * vista[1] + nz * vista[2] > 0) continue;   // mira para otro lado
      var q = [proy(f.p[0]), proy(f.p[1]), proy(f.p[2]), proy(f.p[3])];
      var prof = (q[0][2] + q[1][2] + q[2][2] + q[3][2]) / 4;
      var sombra = 0.78 + 0.22 * Math.max(0, nx * luz[0] + ny * luz[1] + nz * luz[2]);
      lista.push({ q: q, prof: prof, c: f.c, s: sombra, sb: f.sb });
    }
    lista.sort(function (a, b) { return b.prof - a.prof; });
    ctx.lineWidth = 0.7; ctx.lineJoin = "round";
    for (var k = 0; k < lista.length; k++) {
      var L = lista[k], col = L.c, alpha = 1;
      if (col.indexOf("rgba") === 0) { var m = /rgba\((\d+),(\d+),(\d+),([\d.]+)\)/.exec(col); col = tono(+m[1], +m[2], +m[3], L.s); alpha = +m[4]; }
      else { var rr = parseInt(col.slice(1, 3), 16), gg = parseInt(col.slice(3, 5), 16), bb = parseInt(col.slice(5, 7), 16); col = tono(rr, gg, bb, L.s); }
      ctx.globalAlpha = alpha; ctx.fillStyle = col; ctx.strokeStyle = "#000";
      ctx.beginPath();
      for (var j = 0; j < 4; j++) { var p = L.q[j], sx = W / 2 + p[0] * esc, sy = H / 2 - p[1] * esc; if (j) ctx.lineTo(sx, sy); else ctx.moveTo(sx, sy); }
      ctx.closePath(); ctx.fill(); ctx.globalAlpha = 1; if (!L.sb) ctx.stroke();
    }
  }
  function tono(r, g, b, s) { return "rgb(" + Math.round(r * s) + "," + Math.round(g * s) + "," + Math.round(b * s) + ")"; }
  var pendiente = false;
  function pedir() { if (!pendiente) { pendiente = true; requestAnimationFrame(function () { pendiente = false; dibujar(); }); } }
  /* ratón y dedo: arrastrar gira; rueda acerca */
  var arr = null;
  cv.addEventListener("pointerdown", function (e) { arr = [e.clientX, e.clientY, az, el]; cv.setPointerCapture(e.pointerId); });
  cv.addEventListener("pointermove", function (e) { if (!arr) return; az = arr[2] + (e.clientX - arr[0]) * 0.01; el = Math.min(1.5, Math.max(0.08, arr[3] + (e.clientY - arr[1]) * 0.006)); pedir(); });
  cv.addEventListener("pointerup", function () { arr = null; }); cv.addEventListener("pointercancel", function () { arr = null; });
  cv.addEventListener("wheel", function (e) { e.preventDefault(); zoom += e.deltaY < 0 ? 1 : -1; zoom = Math.max(-8, Math.min(14, zoom)); pedir(); }, { passive: false });
  document.querySelectorAll("[data-capa]").forEach(function (b) {
    b.addEventListener("click", function () {
      var k = b.getAttribute("data-capa"); ver[k] = !ver[k]; b.setAttribute("aria-pressed", ver[k]);
      if (k === "pa" && !ver.pa) { ver.techo = false; var t = document.querySelector('[data-capa="techo"]'); if (t) t.setAttribute("aria-pressed", "false"); }
      construir(); pedir();
    });
  });
  var VISTAS = { frente: [0.0, 0.35], esquina: [0.62, 0.52], jardin: [Math.PI + 0.5, 0.5], planta: [0.0, 1.5], lado: [Math.PI / 2, 0.3] };
  document.querySelectorAll("[data-vista]").forEach(function (b) {
    b.addEventListener("click", function () { var v = VISTAS[b.getAttribute("data-vista")]; az = v[0]; el = v[1]; pedir(); });
  });
  document.querySelectorAll("[data-zoom]").forEach(function (b) { b.addEventListener("click", function () { zoom += +b.getAttribute("data-zoom"); pedir(); }); });
  window.addEventListener("resize", pedir);
  construir(); dibujar();
})();
