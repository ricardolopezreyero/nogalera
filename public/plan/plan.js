/* La Nogalera · plano maestro interactivo (Leaflet). Lo usan /plan/, /terreno/, /iluminacion/ y /servicios/ con distintos modos.
   window.PLAN = { datos: "../datos/", modo: "plan" | "terreno" | "noche" | "servicio", servicio: "pluvial", etapas: {...} } */
(function () {
  "use strict";
  var O = window.PLAN || {};
  var DATOS = O.datos || "../datos/", MODO = O.modo || "plan";
  var nf0 = new Intl.NumberFormat("es-MX", { maximumFractionDigits: 0 });
  var nf1 = new Intl.NumberFormat("es-MX", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  var $ = function (id) { return document.getElementById(id); };
  var map = L.map("map", { zoomControl: false, preferCanvas: true, maxZoom: 20, scrollWheelZoom: MODO === "plan" || O.rueda !== false });
  L.control.zoom({ position: "bottomright", zoomInTitle: "Acercar", zoomOutTitle: "Alejar" }).addTo(map);
  map.attributionControl.setPrefix('<a href="https://leafletjs.com">Leaflet</a>');
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 20, maxNativeZoom: 19, attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' }).addTo(map);
  var lienzo = L.canvas({ padding: 0.5 });
  var estilo = {
    limite: { color: "#000", weight: 3, fill: false },
    pista: { color: "#000", weight: 0.8, dashArray: "4 3", fillColor: "#e6e6e6", fillOpacity: 1 },
    vial: { stroke: false, fillColor: "#c8c8c8", fillOpacity: 1 },
    bulevar: { stroke: false, fillColor: "#a8a8a8", fillOpacity: 1 },
    arroyo: { stroke: false, fillColor: "#7a7a7a", fillOpacity: 1 },
    sendero: { color: "#000", weight: 0.6, dashArray: "4 3", fillColor: "#e6e6e6", fillOpacity: 1 },
    comunal: { color: "#000", weight: 1, fillColor: "#dcdcdc", fillOpacity: 1 },
    salon: { color: "#000", weight: 1, fillColor: "#111", fillOpacity: 1 },
    estacionamiento: { color: "#000", weight: 1, fillColor: "#8a8a8a", fillOpacity: 1 },
    tenis: { color: "#000", weight: 1, fillColor: "#444", fillOpacity: 1 },
    padel: { color: "#000", weight: 1, fillColor: "#444", fillOpacity: 1 },
    parque: { color: "#000", weight: 1, fillColor: "#b9b9b9", fillOpacity: 1 },
    caseta: { color: "#000", weight: 1, fillColor: "#000", fillOpacity: 1 },
    lote: { color: "#000", weight: 0.6, fillColor: "#fafafa", fillOpacity: 1 },
    plaza_acceso: { color: "#000", weight: 1, fillColor: "#e9e9e9", fillOpacity: 1 },
    ptar: { color: "#000", weight: 1, fillColor: "#6a6a6a", fillOpacity: 1 },
    isla: { color: "#000", weight: 1, fillColor: "#fff", fillOpacity: 1 },
    carril: { color: "#fff", weight: 1.2, dashArray: "6 5" },
    pluma: { color: "#000", weight: 3 },
    comercio: { color: "#000", weight: 2.5, fillColor: "#fff", fillOpacity: 1 }
  };
  var ETAPA = { 1: "#1a1a1a", 2: "#6b6b6b", 3: "#b3b3b3", 4: "#e4e4e4" };
  var orden = ["pista", "vial", "bulevar", "arroyo", "sendero", "comunal", "plaza_acceso", "ptar", "parque", "lote", "comercio", "estacionamiento", "salon", "tenis", "padel", "isla", "carril", "pluma", "caseta", "limite"];
  if (MODO === "terreno") orden = ["limite"];
  var capaArboles = L.layerGroup(), rotulos = L.layerGroup(), verArboles = true, verEtapas = false, lotesCapa = null;
  var MPP = 156543.03 * Math.cos(25.56 * Math.PI / 180);
  function radioArbol(h) { var m = MPP / Math.pow(2, map.getZoom()); return Math.max(1.4, Math.min(0.32 * h + 1.2, 6) / m); }
  function tamanoArboles() { capaArboles.eachLayer(function (c) { var r = radioArbol(c.options.h); c.setRadius(r); c.setStyle({ weight: c.options.mover ? (r > 3 ? 1.5 : 0.8) : 0 }); }); }
  function verRotulos() {
    if (map.getZoom() >= 17 && MODO !== "terreno") rotulos.addTo(map); else map.removeLayer(rotulos);
    if (verArboles) { tamanoArboles(); capaArboles.addTo(map); } else map.removeLayer(capaArboles);
  }
  map.on("zoomend", verRotulos);
  function margen() {
    var p = $("panel"), cel = window.matchMedia("(max-width: 60rem)").matches;
    if (!p) return { paddingTopLeft: [12, 12], paddingBottomRight: [60, 12] };
    var r = p.getBoundingClientRect(), c = $("map").getBoundingClientRect();
    return cel ? { paddingTopLeft: [12, r.bottom - c.top + 12], paddingBottomRight: [12, 12] } : { paddingTopLeft: [r.right - c.left + 12, 12], paddingBottomRight: [60, 12] };
  }
  function estiloLote(f) {
    var p = f.properties;
    if (verEtapas && O.etapas && O.etapas[p.n]) return { color: "#000", weight: 0.4, fillColor: ETAPA[O.etapas[p.n]], fillOpacity: 1 };
    return p.premio === "parque" ? { color: "#000", weight: 1.6, fillColor: "#f0f0f0", fillOpacity: 1 } : estilo.lote;
  }
  function slug(t) { return t.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); }
  Promise.all([fetch(DATOS + "confort.geojson").then(function (r) { return r.json(); }), fetch(DATOS + "arboles_confort.json").then(function (r) { return r.json(); })]).then(function (res) {
    var fc = res[0], arb = res[1], s = fc.resumen, todo, porDir = {};
    orden.forEach(function (capa) {
      var g = L.geoJSON({ type: "FeatureCollection", features: fc.features.filter(function (f) { return f.properties.capa === capa; }) }, {
        style: capa === "lote" ? estiloLote : estilo[capa], renderer: lienzo, interactive: capa === "lote",
        onEachFeature: capa === "lote" ? function (f, l) {
          var p = f.properties;
          porDir[p.dir.toLowerCase()] = l;
          l.bindPopup("<b>" + p.dir + "</b><br><span style='color:#5f5f5f'>Fracc. " + s.fraccionamiento + " · Lote " + p.n + (O.etapas && O.etapas[p.n] ? " · Etapa " + O.etapas[p.n] : "") + "</span><br>" +
            nf0.format(p.m2) + " m² · " + nf1.format(p.ancho) + " × " + nf1.format(p.fondo) + " m<br>Frente a " + (p.frente === "bulevar" ? "bulevar" : "calle") + " · " + p.arboles + " nogales en sus linderos" +
            (p.premio === "parque" ? "<br>Frente a parque (+8 %)" : "") + (p.fachada ? "<br>Fachada: <a href='../fachadas/#f-" + slug(p.fachada) + "'>" + p.fachada + "</a>" : ""));
        } : null
      }).addTo(map);
      if (capa === "limite") todo = g;
      if (capa === "lote") lotesCapa = g;
    });
    if (MODO !== "terreno") fc.features.forEach(function (f) {
      var n = f.properties.nombre;
      if (f.properties.capa === "rotulo") {
        L.marker([f.geometry.coordinates[1], f.geometry.coordinates[0]], { icon: L.divIcon({ className: "calle" + (f.properties.eje === "cruce" ? " cruce" : ""), html: n, iconSize: null }), interactive: false }).addTo(rotulos);
        return;
      }
      if (!n) return;
      L.marker(L.geoJSON(f).getBounds().getCenter(), { icon: L.divIcon({ className: "estrella", html: n, iconSize: null }), interactive: false }).addTo(rotulos);
    });
    arb.forEach(function (a) {
      var mover = MODO !== "terreno" && !!a[2];
      L.circleMarker([a[1], a[0]], { renderer: lienzo, radius: 2, h: a[3], mover: mover, weight: 0, color: "#000", fillColor: mover ? "#fff" : "#000", fillOpacity: 1, interactive: false }).addTo(capaArboles);
    });
    verRotulos();
    if ($("dirs")) {
      var lista = Object.keys(porDir).map(function (k) { return porDir[k].feature.properties.dir; });
      lista.sort(function (a, b) { var x = a.split(" "), y = b.split(" "); return x[0] === y[0] ? Number(x[1]) - Number(y[1]) : x[0].localeCompare(y[0], "es"); });
      $("dirs").innerHTML = lista.map(function (d) { return '<option value="' + d + '">'; }).join("");
      function sinAcentos(t) { return t.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/\s+/g, " ").trim(); }
      var indice = {}; Object.keys(porDir).forEach(function (k) { indice[sinAcentos(k)] = porDir[k]; });
      $("buscar").addEventListener("submit", function (e) {
        e.preventDefault();
        var q = sinAcentos($("q").value), l = indice[q], msg = $("q-msg");
        if (!l) { msg.textContent = "No existe esa dirección. Escribe calle y número, por ejemplo: " + (O.ejemplo || "Encino 305") + "."; return; }
        msg.textContent = "";
        var m = margen(); m.maxZoom = 19;
        map.fitBounds(l.getBounds(), m); l.openPopup();
      });
    }
    if ($("chk-arboles")) $("chk-arboles").addEventListener("change", function (e) { verArboles = e.target.checked; verRotulos(); });
    if ($("chk-etapas")) $("chk-etapas").addEventListener("change", function (e) { verEtapas = e.target.checked; lotesCapa.setStyle(estiloLote); });

    /* Iluminación: lo que paga y mantiene el fraccionamiento */
    map.createPane("luces"); map.getPane("luces").style.zIndex = 450;
    var lienzoLuz = L.canvas({ pane: "luces", padding: 0.5 }), capaLuz = L.layerGroup(), luzLista = false, focos = [];
    var HALO = { calle: [11, 0.2], bulevar: [14, 0.24], acceso: [13, 0.26], peatonal: [5, 0.3], baliza: [2.2, 0.45], nogal: [5.5, 0.42], estac: [9, 0.2], cancha: [10, 0.22], caseta: [6, 0.5], letrero: [4, 0.6] };
    function cargarLuz() {
      if (luzLista) return Promise.resolve();
      return fetch(DATOS + "luces.json").then(function (r) { return r.json(); }).then(function (d) {
        var r = d.resumen, t = r.tipos;
        d.p.forEach(function (q) {
          var k = d.tipos[q[2]], h = HALO[k];
          L.circle([q[1], q[0]], { renderer: lienzoLuz, radius: h[0], stroke: false, fillColor: "#ffc766", fillOpacity: h[1], interactive: false }).addTo(capaLuz);
          focos.push(L.circleMarker([q[1], q[0]], { renderer: lienzoLuz, radius: 1, chico: k === "nogal" || k === "baliza", stroke: false, fillColor: "#fff3d6", fillOpacity: 1 }).bindPopup("<b>" + (q[3] || "") + "</b> · " + t[k].nombre + (q[4] ? "<br>" + q[4] : "")).addTo(capaLuz));
        });
        if ($("luz")) $("luz").innerHTML =
          "<p><b>" + nf0.format(r.puntos) + " puntos de luz</b> que paga y mantiene el fraccionamiento. Luz cálida y baja; los focos de los nogales se apagan a medianoche.</p><ul>" +
          ["calle", "bulevar", "nogal", "baliza", "peatonal", "acceso", "caseta", "letrero", "estac", "cancha"].map(function (k) { return "<li><span>" + t[k].nombre + "</span><span>" + nf0.format(t[k].n) + "</span></li>"; }).join("") +
          "</ul><p><a href='../iluminacion/'>Más sobre la iluminación</a></p>";
        luzLista = true;
      });
    }
    function tamanoFocos() { var z = map.getZoom(); focos.forEach(function (f) { f.setRadius(z >= 18 ? (f.options.chico ? 1.8 : 2.6) : z >= 16 ? (f.options.chico ? 1.2 : 1.8) : 0.8); }); }
    map.on("zoomend", tamanoFocos);
    function verLuz(on) {
      $("map").classList.toggle("noche", on);
      if ($("luz")) $("luz").hidden = !on;
      if (on) cargarLuz().then(function () { tamanoFocos(); capaLuz.addTo(map); }); else map.removeLayer(capaLuz);
    }
    var chkLuz = $("chk-luz");
    if (chkLuz) chkLuz.addEventListener("change", function (e) { verLuz(e.target.checked); });
    if (MODO === "noche" || location.hash === "#noche") { if (chkLuz) chkLuz.checked = true; verLuz(true); }

    /* Servicios: una red a la vez sobre el plano atenuado */
    map.createPane("servicios"); map.getPane("servicios").style.zIndex = 440;
    var lienzoServ = L.canvas({ pane: "servicios", padding: 0.5 }), capaServ = null, servDatos = null;
    var GRUPO = {
      pluvial: ["plu_parque", "plu_jardin", "plu_cajas", "vaso", "plu_zanja", "plu_flujo", "plu_flujo_punta", "plu_pozo"],
      sanitario: ["ptar_planta", "san_atarjea", "san_colector", "san_pozo", "san_llegada"],
      agua: ["ptar_planta", "agua_tanque", "agua_pozo", "agua_conduccion", "morada", "agua_linea", "hidrante", "agua_nodo"],
      luz: ["barda_tramo", "camara_perim", "acopio", "mesa", "emergencia", "trafo", "trafo_esp", "emergencia_p", "acceso_obra"]
    };
    var NOTA = {
      pluvial: "Las calles bajan a los cruces (bocas de tormenta y pozos de absorción) y de ahí al bulevar. El camellón es un jardín de lluvia; los parques tienen un bordo de 30 cm; hay zanja bajo la pista, cajas bajo los estacionamientos y un vaso en la punta oriente. El agua de La Nogalera se queda en La Nogalera.",
      sanitario: "Todo por gravedad hacia la punta oriente, el punto más bajo: atarjeas de 20 cm en cada calle, colector bajo la pista y la calle Tórtola, pozos de visita en cada cruce y a no más de 100 m, y planta de tratamiento.",
      agua: "Dos pozos (cuadros rayados) mandan a la cisterna por líneas de 6\" (punto y raya); de ahí, bombeo a presión constante a la red en circuitos: 8\" por el bulevar, 6\" en las transversales, 4\" en las calles. Los círculos son los nodos con su presión; hidrantes a tresbolillo. Punteado: agua tratada de la planta, que riega los nogales.",
      luz: "Transformadores de pedestal (uno cada ≈ 16 casas) y trifásicos para club, acceso y planta; cruces elevados; la barda por tramos (gruesa: muro de identidad) con sus cámaras perimetrales cada 60 m; acceso de obra y salida de emergencia al norte; acopio de basura antes de las plumas."
    };
    function estiloServ(f) {
      var c = f.properties.capa, d = f.properties.d || 0;
      switch (c) {
        case "plu_parque": return { color: "#000", weight: 2.5, dashArray: "6 4", fill: false };
        case "plu_jardin": return { stroke: false, fillColor: "#000", fillOpacity: 0.45 };
        case "plu_cajas": return { color: "#000", weight: 1, fillColor: "#000", fillOpacity: 0.3 };
        case "vaso": return { color: "#000", weight: 1.5, fillColor: "#000", fillOpacity: 0.6 };
        case "plu_zanja": return { color: "#000", weight: 2, dashArray: "2 4" };
        case "plu_flujo": case "plu_flujo_punta": return { color: "#000", weight: 1.6 };
        case "ptar_planta": case "agua_tanque": case "acopio": return { color: "#000", weight: 1, fillColor: "#000", fillOpacity: 1 };
        case "san_atarjea": return { color: "#000", weight: 2 };
        case "san_colector": return { color: "#000", weight: 5 };
        case "agua_linea": return { color: "#000", weight: d >= 250 ? 5.5 : d >= 200 ? 4.5 : d >= 150 ? 2.6 : 1.4 };
        case "agua_conduccion": return { color: "#000", weight: 2.4, dashArray: "10 4 2 4" };
        case "agua_pozo": return { color: "#000", weight: 2, fillColor: "#000", fillOpacity: 0.35 };
        case "morada": return { color: "#000", weight: d >= 100 ? 3 : 2, dashArray: "6 4" };
        case "mesa": return { color: "#000", weight: 1, fillColor: "#000", fillOpacity: 1 };
        case "emergencia": return { color: "#000", weight: 6 };
        case "barda_tramo": return { color: "#000", weight: f.properties.lado === "sur" ? 5 : 2.5, dashArray: f.properties.lado === "poniente" ? "8 4" : null };
      }
      return { color: "#000", weight: 1 };
    }
    function puntoServ(f, ll) {
      var c = f.properties.capa;
      if (c === "emergencia_p") return L.marker(ll, { icon: L.divIcon({ className: "estrella", html: "Salida de emergencia", iconSize: null }), interactive: false });
      var o = { renderer: lienzoServ, color: "#000", weight: 1.5, fillOpacity: 1 };
      if (c === "plu_pozo" || c === "san_pozo") { o.radius = 2.6; o.fillColor = "#fff"; }
      else if (c === "hidrante") { o.radius = 3.6; o.fillColor = "#000"; }
      else if (c === "agua_nodo") { o.radius = f.properties.fuente ? 6 : 3.2; o.fillColor = "#fff"; o.weight = 1.2; }
      else if (c === "trafo") { o.radius = 3; o.fillColor = "#000"; o.weight = 0; }
      else if (c === "camara_perim") { o.radius = 2.4; o.fillColor = "#fff"; o.weight = 1.2; }
      else if (c === "acceso_obra") { o.radius = 7; o.fillColor = "#000"; o.color = "#fff"; o.weight = 2; }
      else { o.radius = 6; o.fillColor = "#000"; o.color = "#fff"; o.weight = 2; }
      return L.circleMarker(ll, o);
    }
    var NOMBRES = { plu_pozo: "Boca de tormenta y pozo de absorción", san_pozo: "Pozo de visita", hidrante: "Hidrante", trafo: "Transformador pedestal 75 kVA", mesa: "Cruce elevado", camara_perim: "Cámara perimetral (poste de 6 m, del lado de la pista)" };
    function verServ(g) {
      if (capaServ) { map.removeLayer(capaServ); capaServ = null; }
      $("map").classList.toggle("serv", !!g);
      var nota = $("serv-nota"); if (nota) nota.hidden = !g;
      if (!g) return;
      if (nota) nota.innerHTML = "<p>" + NOTA[g] + "</p><p><a href='../servicios/#" + g + "'>Especificaciones de esta red</a></p>";
      (servDatos ? Promise.resolve(servDatos) : fetch(DATOS + "servicios.geojson").then(function (r) { return r.json(); })).then(function (d) {
        servDatos = d; capaServ = L.layerGroup();
        GRUPO[g].forEach(function (c) {
          L.geoJSON({ type: "FeatureCollection", features: d.features.filter(function (f) { return f.properties.capa === c; }) }, {
            renderer: lienzoServ, style: estiloServ, pointToLayer: puntoServ, interactive: !/_punta$|plu_flujo/.test(c),
            onEachFeature: function (f, l) { var p = f.properties, t = p.nombre || NOMBRES[p.capa]; if (!t || !l.bindPopup) return;
              if (p.capa === "agua_nodo") t = "<b>" + t + "</b>" + (p.fuente ? "" : "<br>Presión: " + p.p.toFixed(1) + " kg/cm² en la hora pico · " + p.p_inc.toFixed(1) + " con un hidrante abierto" + (p.lotes ? "<br>" + p.lotes + " lotes" : ""));
              else if (p.capa === "agua_linea") t = "<b>" + t + "</b><br>" + p.q + " l/s · " + p.v + " m/s · " + p.j + " m/km de pérdida";
              else if (p.d && p.capa !== "agua_conduccion") t += " · Ø " + (p.capa === "san_atarjea" || p.capa === "san_colector" ? p.d + " cm" : p.d + " mm");
              l.bindPopup(t); }
          }).addTo(capaServ);
        });
        capaServ.addTo(map);
      });
    }
    var selServ = $("sel-serv");
    if (selServ) {
      selServ.addEventListener("change", function (e) { verServ(e.target.value); });
      function servDesdeHash() { var h = location.hash.replace("#", ""); if (GRUPO[h]) { selServ.value = h; verServ(h); } }
      window.addEventListener("hashchange", servDesdeHash); servDesdeHash();
    }
    if (MODO === "servicio" && O.servicio) verServ(O.servicio);

    if ($("kpis")) {
      var quedan = s.arboles - s.reubicar;
      $("kpis").innerHTML =
        "<div><dt>Casas</dt><dd>" + nf0.format(s.lotes) + "</dd></div>" +
        "<div><dt>Lote típico</dt><dd>12.7 × 25.9 m · " + nf0.format(s.lote_mediana) + " m²</dd></div>" +
        "<div><dt>Vendible</dt><dd>" + nf1.format(s.vendible_m2 / 1e4) + " ha (" + nf1.format(s.pct_vendible) + " %)</dd></div>" +
        "<div><dt>Verde y club</dt><dd>" + nf1.format(s.verde_pct) + " %</dd></div>" +
        "<div><dt>Nogales que se quedan</dt><dd>" + nf0.format(quedan) + " de " + nf0.format(s.arboles) + " (" + nf0.format(100 * quedan / s.arboles) + " %)</dd></div>" +
        "<div><dt>Comercio</dt><dd>" + nf0.format(s.predio_comercial_m2) + " m²</dd></div>";
    }
    map.fitBounds(todo.getBounds(), margen());
  });
})();
