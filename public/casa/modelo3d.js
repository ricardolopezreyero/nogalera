/* La Nogalera · visor 3D del Modelo Nogal: usa el motor /render/render3d.js. window.CASA3D = { prismas, centro } */
(function () {
  "use strict";
  var cv = document.getElementById("c3d"), r = new Render3D(cv, window.CASA3D, {});
  r.capas = { techo: true, pa: true, muebles: true, arboles: true };
  r.orbita();
  document.querySelectorAll("[data-capa]").forEach(function (b) {
    b.addEventListener("click", function () {
      var k = b.getAttribute("data-capa"); r.capas[k] = !r.capas[k]; b.setAttribute("aria-pressed", r.capas[k]);
      if (k === "pa" && !r.capas.pa) { r.capas.techo = false; var t = document.querySelector('[data-capa="techo"]'); if (t) t.setAttribute("aria-pressed", "false"); }
      r.construir(); r.pedir();
    });
  });
  var VISTAS = { frente: [0.0, 0.35], esquina: [0.62, 0.52], jardin: [Math.PI + 0.5, 0.5], planta: [0.0, 1.5], lado: [Math.PI / 2, 0.3] };
  document.querySelectorAll("[data-vista]").forEach(function (b) {
    b.addEventListener("click", function () { var v = VISTAS[b.getAttribute("data-vista")]; r.cam.az = v[0]; r.cam.el = v[1]; r.pedir(); });
  });
  document.querySelectorAll("[data-zoom]").forEach(function (b) { b.addEventListener("click", function () { r.cam.zoom += +b.getAttribute("data-zoom"); r.pedir(); }); });
  window.addEventListener("resize", r.pedir);
  r.pedir();
})();
