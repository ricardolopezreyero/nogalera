/* Nogaleras de La Laguna: mapa en blanco y negro con Leaflet + OpenStreetMap. */
(function () {
  "use strict";

  var REF_INICIAL = { nombre: "Real del Nogalar", lat: 25.60174, lon: -103.39234 };
  var ref = REF_INICIAL;
  var ESTADOS = ["activa", "desmontada", "urbanizada"];
  var NOMBRE_ESTADO = { activa: "Nogalera", desmontada: "Ya sin nogales", urbanizada: "Urbanizada" };
  var ESTILO = {
    activa: { color: "#000", weight: 1.2, opacity: 1, fillColor: "#000", fillOpacity: 0.38 },
    desmontada: { color: "#000", weight: 1.5, opacity: 1, dashArray: "5 4", fillColor: "#000", fillOpacity: 0.04 },
    urbanizada: { color: "#555", weight: 1.5, opacity: 1, dashArray: "2 4", fillColor: "#666", fillOpacity: 0.2 }
  };
  var ZOOM_ETIQUETAS = 14;
  var ZOOM_PUNTOS = 13;

  var nf0 = new Intl.NumberFormat("es-MX", { maximumFractionDigits: 0 });
  var nf1 = new Intl.NumberFormat("es-MX", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  var $ = function (id) { return document.getElementById(id); };
  var track = function (e, p) { if (window.slTrack) window.slTrack(e, p); };

  function hectareas(m2) { return nf1.format(m2 / 1e4) + " ha"; }
  function millones(x) { return x >= 1e7 ? nf0.format(x / 1e6) : nf1.format(x / 1e6); }
  function dinero(x) {
    if (x >= 1e9) return "$" + nf1.format(x / 1e9) + " mil millones";
    if (x >= 1e6) return "$" + millones(x) + " millones";
    return "$" + nf0.format(x);
  }
  function rangoDinero(a, b) {
    if (a >= 1e6) return "$" + millones(a) + "–" + millones(b) + " millones";
    return "$" + nf0.format(a) + "–" + nf0.format(b);
  }
  function distanciaTexto(d) { return d < 1 ? nf0.format(Math.round(d * 1000 / 10) * 10) + " m" : nf1.format(d) + " km"; }
  function distanciaKm(lat1, lon1, lat2, lon2) {
    var r = Math.PI / 180, dLat = (lat2 - lat1) * r, dLon = (lon2 - lon1) * r;
    var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(lat1 * r) * Math.cos(lat2 * r) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
    return 12742 * Math.asin(Math.sqrt(a));
  }
  function escapar(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function aviso(texto, ms) {
    var previo = document.querySelector(".aviso");
    if (previo) previo.remove();
    var el = document.createElement("div");
    el.className = "aviso"; el.setAttribute("role", "status"); el.textContent = texto;
    document.body.appendChild(el);
    setTimeout(function () { el.remove(); }, ms || 2600);
  }
  var esCelular = function () { return window.matchMedia("(max-width: 40rem)").matches; };
  /* Espacio que tapan el panel y la lista, para no esconder la nogalera debajo. */
  function margenes() {
    var p = document.getElementById("panel").getBoundingClientRect();
    var l = document.getElementById("lista");
    if (esCelular()) {
      var abajo = l.hidden ? 12 : window.innerHeight - l.getBoundingClientRect().top + 12;
      return { tl: [12, p.bottom + 12], br: [12, abajo] };
    }
    var der = l.hidden ? 60 : window.innerWidth - l.getBoundingClientRect().left + 12;
    return { tl: [p.right + 12, 12], br: [der, 12] };
  }

  /* ---------- Mapa ---------- */
  var map = L.map("map", { zoomControl: false, preferCanvas: true, minZoom: 8 });
  L.control.zoom({ position: "bottomright", zoomInTitle: "Acercar", zoomOutTitle: "Alejar" }).addTo(map);
  map.attributionControl.setPrefix('<a href="https://leafletjs.com">Leaflet</a>');
  if (window.NOGALERA_BASE === "vector" || /[?&]fondo=vector/.test(location.search)) baseVectorial();
  else L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map);
  map.setView([25.65, -103.35], 10);

  /* Fondo de respaldo sin teselas: carreteras, ríos, manchas urbanas y pueblos (base.geojson, de OpenStreetMap). */
  function baseVectorial() {
    map.createPane("base").style.zIndex = 250;
    var lienzoBase = L.canvas({ pane: "base", padding: 0.5 });
    var est = {
      urbano: { stroke: false, fillColor: "#e2e2e2", fillOpacity: 1 },
      motorway: { color: "#111", weight: 2.4 }, trunk: { color: "#111", weight: 2.2 },
      primary: { color: "#333", weight: 1.6 }, secondary: { color: "#555", weight: 1.2 },
      tertiary: { color: "#9a9a9a", weight: 0.8 }, rio: { color: "#b5b5b5", weight: 1 }
    };
    var nombres = L.layerGroup().addTo(map), locs = [];
    function rotular() {
      nombres.clearLayers();
      var z = map.getZoom(), b = map.getBounds();
      locs.forEach(function (f) {
        var p = f.properties, c = f.geometry.coordinates;
        if (!b.contains([c[1], c[0]]) || (p.p < 20000 && z < 11) || (p.p < 5000 && z < 12)) return;
        L.marker([c[1], c[0]], { icon: L.divIcon({ className: "pueblo" + (p.p >= 20000 ? " grande" : ""), html: escapar(p.n), iconSize: null }), interactive: false, keyboard: false }).addTo(nombres);
      });
    }
    fetch("base.geojson").then(function (r) { return r.json(); }).then(function (fc) {
      locs = fc.features.filter(function (f) { return f.properties.k === "loc"; });
      L.geoJSON(fc, {
        filter: function (f) { return f.properties.k !== "loc"; },
        style: function (f) { return est[f.properties.k]; },
        interactive: false, renderer: lienzoBase
      }).addTo(map);
      rotular();
      map.on("zoomend moveend", rotular);
    }).catch(function () { /* sin fondo: el mapa sigue funcionando */ });
    map.attributionControl.addAttribution('© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>');
  }
  var lienzo = L.canvas({ padding: 0.5, tolerance: 4 });

  var grupos = {}, puntos = {};
  ESTADOS.forEach(function (e) { grupos[e] = L.layerGroup().addTo(map); puntos[e] = L.layerGroup().addTo(map); });
  var capaEtiquetas = L.layerGroup().addTo(map);
  var capaRef = L.layerGroup().addTo(map);
  var visibles = { activa: true, desmontada: true, urbanizada: true };
  var feats = [], porId = {}, capaPorId = {}, seleccion = null;

  function dibujarRef() {
    capaRef.clearLayers();
    L.marker([ref.lat, ref.lon], { icon: L.divIcon({ className: "ref-icono", iconSize: null }), keyboard: false, interactive: false }).addTo(capaRef);
    L.marker([ref.lat, ref.lon], { icon: L.divIcon({ className: "ref-texto", html: escapar(ref.nombre), iconSize: null }), keyboard: false, interactive: false }).addTo(capaRef);
  }

  function contenido(f) {
    var p = f.properties;
    var d = distanciaKm(ref.lat, ref.lon, p.lat, p.lon);
    var h = '<div class="pop">';
    h += "<h3>Nogalera " + p.id + " <small>" + NOMBRE_ESTADO[p.estado] + "</small></h3>";
    h += '<p class="grande">' + hectareas(p.area_m2) + "</p>";
    h += '<p class="rango">' + nf0.format(p.area_m2) + " m² · ≈ " + nf0.format(p.largo_m) + " × " + nf0.format(p.ancho_m) + " m</p>";
    h += "<dl>";
    if (p.precio_m2) {
      h += "<dt>Precio</dt><dd>≈ $" + nf0.format(p.precio_m2) + '/m² <span class="rango">($' + nf0.format(p.precio_m2_min) + "–" + nf0.format(p.precio_m2_max) + ")</span></dd>";
      h += "<dt>Valor</dt><dd>≈ " + dinero(p.valor) + ' <span class="rango">(' + rangoDinero(p.valor_min, p.valor_max) + ")</span></dd>";
    } else {
      h += "<dt>Precio</dt><dd>Sin estimar: ya urbanizada</dd>";
    }
    h += "<dt>Dónde</dt><dd>" + escapar(p.municipio || "—") + (p.cerca_de ? ", cerca de " + escapar(p.cerca_de) : "") + "</dd>";
    h += "<dt>Distancia</dt><dd>" + distanciaTexto(d) + " de " + escapar(ref.nombre) + " (en línea recta)</dd>";
    h += "</dl>";
    if (p.grupo_bloques) h += '<p class="nota">Es un bloque de un conjunto de ' + p.grupo_bloques + " bloques pegados que suma " + hectareas(p.grupo_m2) + ".</p>";
    if (p.estado === "desmontada") h += '<p class="nota">Había nogales en 2018–2020; en 2026 ya no hay. El precio es el del terreno.</p>';
    if (p.estado === "urbanizada") h += '<p class="nota">Había nogales en 2018–2020; hoy ya hay calles o casas.</p>';
    if (p.mixta) h += '<p class="nota">Incluye arboleda de río: la superficie de nogal puede ser menor.</p>';
    if (p.confianza === "media") h += '<p class="nota">Confianza media: conviene verla en persona.</p>';
    var ll = p.lat + "," + p.lon;
    h += '<div class="botones">';
    h += '<a href="https://www.google.com/maps/dir/?api=1&destination=' + ll + '" target="_blank" rel="noopener" data-llegar="google">Cómo llegar</a>';
    h += '<a href="https://waze.com/ul?ll=' + ll + '&navigate=yes" target="_blank" rel="noopener" data-llegar="waze">Waze</a>';
    h += '<button type="button" data-copiar="' + p.lat + ", " + p.lon + '">Copiar coordenadas</button>';
    h += '<button type="button" data-compartir="' + p.id + '">Compartir</button>';
    h += "</div></div>";
    return h;
  }

  function abrir(id, centrar) {
    var f = porId[id], capa = capaPorId[id];
    if (!f || !capa) return;
    if (!visibles[f.properties.estado]) {
      visibles[f.properties.estado] = true;
      document.querySelector('input[data-estado="' + f.properties.estado + '"]').checked = true;
      aplicarVisibles();
    }
    var m = margenes();
    if (centrar) map.fitBounds(capa.getBounds(), { maxZoom: 16, paddingTopLeft: m.tl, paddingBottomRight: m.br, animate: false });
    L.popup({ maxWidth: 320, autoPanPaddingTopLeft: m.tl, autoPanPaddingBottomRight: m.br })
      .setLatLng([f.properties.lat, f.properties.lon])
      .setContent(contenido(f))
      .openOn(map);
    resaltar(id);
    try { history.replaceState(null, "", "#n" + id); } catch (e) { /* sin historial */ }
    track("nogalera_abrir", { nogalera_id: id, nogalera_estado: f.properties.estado });
  }

  function resaltar(id) {
    if (seleccion != null && capaPorId[seleccion]) capaPorId[seleccion].setStyle(ESTILO[porId[seleccion].properties.estado]);
    seleccion = id;
    if (id != null && capaPorId[id]) capaPorId[id].setStyle({ weight: 3.5, fillOpacity: 0.55 });
  }

  map.on("popupclose", function () {
    resaltar(null);
    try { history.replaceState(null, "", location.pathname + location.search); } catch (e) { /* sin historial */ }
  });

  /* Botones dentro de la ventana de cada nogalera */
  document.addEventListener("click", function (ev) {
    var t = ev.target.closest ? ev.target.closest("[data-copiar],[data-compartir],[data-llegar],[data-descarga]") : null;
    if (!t) return;
    if (t.hasAttribute("data-copiar")) {
      var txt = t.getAttribute("data-copiar");
      (navigator.clipboard ? navigator.clipboard.writeText(txt) : Promise.reject()).then(
        function () { aviso("Coordenadas copiadas: " + txt); },
        function () { aviso("Coordenadas: " + txt, 8000); });
    } else if (t.hasAttribute("data-compartir")) {
      var id = t.getAttribute("data-compartir");
      var url = location.origin + location.pathname + "#n" + id;
      var copiar = function () {
        (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.reject()).then(
          function () { aviso("Enlace copiado"); }, function () { aviso(url, 8000); });
      };
      if (navigator.share) navigator.share({ title: "Nogalera " + id, url: url }).catch(function (e) { if (!e || e.name !== "AbortError") copiar(); });
      else copiar();
      track("nogalera_compartir", { nogalera_id: Number(id) });
    } else if (t.hasAttribute("data-llegar")) {
      track("como_llegar_click", { nogalera_id: seleccion, link_url: t.href });
    } else if (t.hasAttribute("data-descarga")) {
      track("descarga", { link_url: t.href });
    }
  });

  /* ---------- Etiquetas de tamaño ---------- */
  function etiquetar() {
    capaEtiquetas.clearLayers();
    var z = map.getZoom();
    ESTADOS.forEach(function (e) {
      if (z >= ZOOM_PUNTOS) map.removeLayer(puntos[e]);
      else if (visibles[e]) puntos[e].addTo(map);
    });
    if (z < ZOOM_ETIQUETAS) return;
    var b = map.getBounds().pad(0.2);
    feats.forEach(function (f) {
      var p = f.properties;
      if (!visibles[p.estado] || !b.contains([p.lat, p.lon])) return;
      var txt = (z >= 16 ? "N" + p.id + " · " : "") + hectareas(p.area_m2);
      L.marker([p.lat, p.lon], {
        icon: L.divIcon({ className: "etiqueta" + (p.estado === "activa" ? "" : " perdida"), html: txt, iconSize: null }),
        interactive: false, keyboard: false
      }).addTo(capaEtiquetas);
    });
  }
  map.on("zoomend moveend", etiquetar);

  /* ---------- Capas visibles ---------- */
  function aplicarVisibles() {
    ESTADOS.forEach(function (e) {
      if (visibles[e]) grupos[e].addTo(map); else map.removeLayer(grupos[e]);
    });
    etiquetar();
    pintarLista();
  }
  document.querySelectorAll(".legend input").forEach(function (inp) {
    inp.addEventListener("change", function () {
      visibles[inp.getAttribute("data-estado")] = inp.checked;
      aplicarVisibles();
    });
  });

  /* ---------- Lista ---------- */
  var orden = $("orden"), lista = $("lista"), btnLista = $("btn-lista");
  function pintarLista() {
    if (lista.hidden) return;
    var crit = orden.value;
    var arr = feats.filter(function (f) { return visibles[f.properties.estado]; }).map(function (f) {
      return { f: f, d: distanciaKm(ref.lat, ref.lon, f.properties.lat, f.properties.lon) };
    });
    arr.sort(function (a, b) {
      var p = a.f.properties, q = b.f.properties;
      if (crit === "area") return q.area_m2 - p.area_m2;
      if (crit === "precio") return (q.precio_m2 || 0) - (p.precio_m2 || 0);
      if (crit === "valor") return (q.valor || 0) - (p.valor || 0);
      return a.d - b.d;
    });
    var html = "";
    arr.forEach(function (x) {
      var p = x.f.properties;
      html += '<li><button type="button" data-id="' + p.id + '"><span class="num">N' + p.id + "</span><span>" + hectareas(p.area_m2) +
        (p.precio_m2 ? " · $" + nf0.format(p.precio_m2) + "/m²" : "") + "</span><span>" + distanciaTexto(x.d) + '</span><span class="det">' +
        (p.estado !== "activa" ? '<span class="est">' + NOMBRE_ESTADO[p.estado] + "</span> · " : "") +
        escapar(p.municipio || "") + (p.cerca_de ? " · cerca de " + escapar(p.cerca_de) : "") + "</span></button></li>";
    });
    $("items").innerHTML = html;
    $("ref-nombre").textContent = ref.nombre;
  }
  $("items").addEventListener("click", function (ev) {
    var b = ev.target.closest("button[data-id]");
    if (!b) return;
    if (esCelular()) cerrarLista();
    abrir(Number(b.getAttribute("data-id")), true);
  });
  function abrirLista() { lista.hidden = false; btnLista.setAttribute("aria-expanded", "true"); pintarLista(); track("lista_abrir"); }
  function cerrarLista() { lista.hidden = true; btnLista.setAttribute("aria-expanded", "false"); }
  btnLista.addEventListener("click", function () { if (lista.hidden) abrirLista(); else cerrarLista(); });
  $("cerrar-lista").addEventListener("click", cerrarLista);
  orden.addEventListener("change", function () { pintarLista(); track("lista_orden", { orden: orden.value }); });

  /* ---------- Mi ubicación ---------- */
  if ($("btn-ubicacion")) $("btn-ubicacion").addEventListener("click", function () {
    if (!navigator.geolocation) { aviso("Tu navegador no comparte la ubicación"); return; }
    aviso("Buscando tu ubicación…");
    navigator.geolocation.getCurrentPosition(function (pos) {
      ref = { nombre: "tu ubicación", lat: pos.coords.latitude, lon: pos.coords.longitude };
      dibujarRef();
      map.setView([ref.lat, ref.lon], Math.max(map.getZoom(), 12));
      if (lista.hidden) abrirLista(); else pintarLista();
      track("ubicacion_usar");
    }, function () { aviso("No se pudo obtener tu ubicación"); }, { enableHighAccuracy: true, timeout: 15000, maximumAge: 60000 });
  });

  /* ---------- Cómo se hizo ---------- */
  var info = $("info");
  $("btn-info").addEventListener("click", function () {
    if (info.showModal) info.showModal(); else info.setAttribute("open", "");
    track("info_abrir");
  });
  $("cerrar-info").addEventListener("click", function () { if (info.close) info.close(); else info.removeAttribute("open"); });
  info.addEventListener("click", function (ev) { if (ev.target === info && info.close) info.close(); });

  /* ---------- Mi selección: 5 aptas para urbanizar ---------- */
  var SELECCION = [
    { id: 24, nota: "58 ha pegadas a Los Olivos, Gómez Palacio" },
    { id: 6, nota: "40 ha junto a La Paz, oriente de Torreón" },
    { id: 25, nota: "36 ha junto a Santa Fe, Torreón" },
    { id: 22, nota: "33 ha (2 bloques) junto a Los Olivos, Gómez" },
    { id: 29, nota: "20 ha junto a Santa Fe, Torreón" }
  ];
  var capaSeleccion = L.layerGroup().addTo(map);
  function pintarSeleccion() {
    capaSeleccion.clearLayers();
    var html = "";
    SELECCION.forEach(function (s, i) {
      var f = porId[s.id];
      if (!f) return;
      var p = f.properties;
      L.geoJSON(f, { style: { color: "#000", weight: 4, dashArray: "8 5", fill: false }, interactive: false }).addTo(capaSeleccion);
      L.marker([p.lat, p.lon], { icon: L.divIcon({ className: "estrella", html: "★" + (i + 1), iconSize: null }), interactive: false, keyboard: false }).addTo(capaSeleccion);
      html += '<li><button type="button" data-sel="' + s.id + '"><span>' + (i + 1) + ". N" + s.id + " · " + escapar(s.nota) + "</span><b>≈ " + dinero(p.valor) + "</b></button></li>";
    });
    $("sel-items").innerHTML = html;
  }
  $("sel-items").addEventListener("click", function (ev) {
    var b = ev.target.closest("button[data-sel]");
    if (b) { abrir(Number(b.getAttribute("data-sel")), true); track("seleccion_abrir", { nogalera_id: Number(b.getAttribute("data-sel")) }); }
  });
  $("chk-seleccion").addEventListener("change", function (ev) {
    if (ev.target.checked) capaSeleccion.addTo(map); else map.removeLayer(capaSeleccion);
  });

  /* ---------- Datos ---------- */
  function iniciar(fc) {
    feats = fc.features;
    var n = { activa: 0, desmontada: 0, urbanizada: 0 }, haAct = 0, valAct = 0;
    var todos = L.latLngBounds([]);
    feats.forEach(function (f) {
      var p = f.properties;
      porId[p.id] = f;
      n[p.estado]++;
      if (p.estado === "activa") { haAct += p.area_m2; valAct += p.valor || 0; }
      var capa = L.geoJSON(f, { style: ESTILO[p.estado], renderer: lienzo });
      capa.on("click", function () { abrir(p.id, false); });
      capa.addTo(grupos[p.estado]);
      capaPorId[p.id] = capa;
      L.circleMarker([p.lat, p.lon], {
        renderer: lienzo, radius: p.area_m2 >= 200000 ? 4.5 : 3.2,
        color: p.estado === "activa" ? "#000" : "#555", weight: 1, fillColor: p.estado === "activa" ? "#000" : "#fff", fillOpacity: 1
      }).on("click", function () { abrir(p.id, true); }).addTo(puntos[p.estado]);
      todos.extend(capa.getBounds());
    });
    $("n-activa").textContent = nf0.format(n.activa);
    $("n-desmontada").textContent = nf0.format(n.desmontada);
    $("n-urbanizada").textContent = nf0.format(n.urbanizada);
    $("stats").textContent = nf0.format(n.activa) + " nogaleras · " + nf0.format(haAct / 1e4) + " ha · valor estimado ≈ " + dinero(valAct);
    dibujarRef();
    pintarSeleccion();
    var m = /^#n=?(\d+)$/.exec(location.hash);
    if (m && porId[Number(m[1])]) {
      abrir(Number(m[1]), true);
    } else {
      var mg = margenes();
      map.fitBounds(todos, { paddingTopLeft: mg.tl, paddingBottomRight: mg.br });
    }
    etiquetar();
  }

  fetch("nogaleras.geojson")
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(iniciar)
    .catch(function () { $("stats").textContent = "No se pudieron cargar los datos. Recarga la página."; });
})();
