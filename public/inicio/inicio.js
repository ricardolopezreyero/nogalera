/* La Nogalera · página del cliente: visor de imágenes y formulario que guarda en /api/prospecto (Worker de Cloudflare). */
(function () {
  "use strict";
  /* ---------- visor ---------- */
  var fotos = Array.prototype.slice.call(document.querySelectorAll("figure.foto a[data-grande]"));
  var visor = document.getElementById("visor"), vImg = visor && visor.querySelector("img"), vCap = visor && visor.querySelector("figcaption"), i = 0;
  function muestra(k) {
    i = (k + fotos.length) % fotos.length; var a = fotos[i];
    vImg.src = a.getAttribute("data-grande"); vImg.alt = a.querySelector("img").alt; vCap.textContent = a.getAttribute("data-titulo") || vImg.alt;
    if (!visor.open) visor.showModal();
  }
  if (visor) {
    fotos.forEach(function (a, k) { a.addEventListener("click", function (ev) { ev.preventDefault(); muestra(k); }); });
    visor.querySelector(".cerrar").addEventListener("click", function () { visor.close(); });
    visor.querySelector(".ant").addEventListener("click", function () { muestra(i - 1); });
    visor.querySelector(".sig").addEventListener("click", function () { muestra(i + 1); });
    visor.addEventListener("click", function (ev) { if (ev.target === visor) visor.close(); });
    document.addEventListener("keydown", function (ev) { if (!visor.open) return; if (ev.key === "ArrowRight") muestra(i + 1); if (ev.key === "ArrowLeft") muestra(i - 1); });
  }
  /* ---------- formulario ---------- */
  var f = document.getElementById("forma"), estado = document.getElementById("estado"), boton = f && f.querySelector("button[type=submit]");
  if (!f) return;
  function valor(n) {
    var el = f.querySelector('[name="' + n + '"]');
    if (el && el.type === "radio") { el = f.querySelector('[name="' + n + '"]:checked'); return el ? el.value : ""; }
    return el ? el.value.trim() : "";
  }
  f.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var d = { nombre: valor("nombre"), celular: valor("celular"), correo: valor("correo"), casa: valor("casa"), credito: valor("credito"), rapidez: valor("rapidez"), mensaje: valor("mensaje"), empresa: valor("empresa"), origen: location.pathname + location.search };
    estado.className = "estado";
    if (d.nombre.length < 2) return error("Escribe tu nombre.");
    if (d.celular.replace(/\D/g, "").length < 10) return error("El celular necesita 10 dígitos.");
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(d.correo)) return error("Revisa el correo.");
    if (!d.casa || !d.credito || !d.rapidez) return error("Falta contestar una de las tres preguntas.");
    boton.disabled = true; estado.textContent = "Guardando…";
    fetch("/api/prospecto", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(d) })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (res) {
        boton.disabled = false;
        if (!res.ok || res.j.error) return error(res.j.error || "No se pudo guardar. Intenta de nuevo.");
        try { localStorage.setItem("nogalera-prospecto", JSON.stringify({ nombre: d.nombre, fecha: Date.now() })); } catch (e) {}
        f.hidden = true;
        var g = document.getElementById("gracias"); g.hidden = false; g.querySelector("b").textContent = d.nombre.split(" ")[0];
        g.scrollIntoView({ behavior: "smooth", block: "center" });
      })
      .catch(function () { boton.disabled = false; error("Sin conexión. Intenta de nuevo en un momento."); });
  });
  function error(t) { estado.textContent = t; estado.className = "estado error"; }
  f.querySelector('[name="celular"]').addEventListener("input", function (ev) { ev.target.value = ev.target.value.replace(/[^\d+ \-()]/g, "").slice(0, 20); });
})();
