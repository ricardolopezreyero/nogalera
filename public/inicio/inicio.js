/* La Nogalera · página del cliente: visor de imágenes, animación al aparecer y los formularios del brochure (guardan en /api/prospecto, Worker de Cloudflare). */
(function () {
  "use strict";
  /* ---------- aparecer al hacer scroll ---------- */
  var rev = Array.prototype.slice.call(document.querySelectorAll(".rev"));
  if ("IntersectionObserver" in window && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add("ver"); io.unobserve(x.target); } }); }, { rootMargin: "0px 0px -8% 0px" });
    rev.forEach(function (el) { io.observe(el); });
  } else rev.forEach(function (el) { el.classList.add("ver"); });
  /* el botón fijo del móvil se esconde mientras el formulario de arriba está a la vista */
  var fijo = document.querySelector(".fijo"), fa = document.getElementById("forma-arriba");
  if (fijo && fa && "IntersectionObserver" in window) new IntersectionObserver(function (es) { fijo.classList.toggle("oculto", es[0].isIntersecting); }, { threshold: 0.2 }).observe(fa);
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
  /* ---------- formularios del brochure (hay dos iguales: arriba y abajo) ---------- */
  var formas = Array.prototype.slice.call(document.querySelectorAll("form.brochure"));
  var datos = null;                                                             // lo que ya mandó (nombre, celular, correo) para la segunda parte
  function enviar(d) {
    return fetch("/api/prospecto", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(d) })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok && !j.error, j: j }; }); });
  }
  formas.forEach(function (f) {
    var estado = f.querySelector(".estado"), boton = f.querySelector("button[type=submit]"), gracias = f.querySelector(".gracias"), mas = f.querySelector(".mas"), estado2 = f.querySelector(".estado2");
    function valor(n) {
      var el = f.querySelector('[name="' + n + '"]');
      if (el && el.type === "radio") { el = f.querySelector('[name="' + n + '"]:checked'); return el ? el.value : ""; }
      return el ? el.value.trim() : "";
    }
    function error(t, el) { (el || estado).textContent = t; (el || estado).className = (el ? "estado2" : "estado") + " error"; }
    f.querySelector('[name="celular"]').addEventListener("input", function (ev) { ev.target.value = ev.target.value.replace(/[^\d+ \-()]/g, "").slice(0, 20); });
    f.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var d = { tipo: "brochure", nombre: valor("nombre"), celular: valor("celular"), correo: valor("correo"), empresa: valor("empresa"), origen: location.pathname + location.search + "#" + f.id };
      estado.className = "estado";
      if (d.nombre.length < 2) return error("Escribe tu nombre.");
      if (d.celular.replace(/\D/g, "").length < 10) return error("El celular necesita 10 dígitos.");
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(d.correo)) return error("Revisa el correo.");
      boton.disabled = true; estado.textContent = "Guardando…";
      enviar(d).then(function (res) {
        boton.disabled = false;
        if (!res.ok) return error(res.j.error || "No se pudo guardar. Intenta de nuevo.");
        datos = d; try { localStorage.setItem("nogalera-prospecto", JSON.stringify({ nombre: d.nombre, fecha: Date.now() })); } catch (e) {}
        Array.prototype.forEach.call(f.children, function (c) { if (c !== gracias) c.hidden = true; });
        gracias.hidden = false; gracias.querySelector("b").textContent = d.nombre.split(" ")[0];
        gracias.scrollIntoView({ behavior: "smooth", block: "center" });
      }).catch(function () { boton.disabled = false; error("Sin conexión. Intenta de nuevo en un momento."); });
    });
    mas.addEventListener("click", function () {
      if (!datos) return;
      var d = { tipo: "completo", nombre: datos.nombre, celular: datos.celular, correo: datos.correo, casa: valor("casa"), credito: valor("credito"), rapidez: valor("rapidez"), mensaje: valor("mensaje"), origen: datos.origen + "+mas" };
      if (!d.casa || !d.credito || !d.rapidez) return error("Falta contestar una de las tres preguntas.", estado2);
      mas.disabled = true; estado2.textContent = "Guardando…"; estado2.className = "estado2";
      enviar(d).then(function (res) {
        if (!res.ok) { mas.disabled = false; return error(res.j.error || "No se pudo guardar.", estado2); }
        estado2.textContent = ""; mas.hidden = true; Array.prototype.forEach.call(gracias.querySelectorAll("fieldset, label"), function (x) { x.hidden = true; }); gracias.querySelector(".listo").hidden = false;
      }).catch(function () { mas.disabled = false; error("Sin conexión. Intenta de nuevo.", estado2); });
    });
  });
})();
