/* La Nogalera · Worker de Cloudflare: sirve el sitio estático (public/) y expone /api/render-ia, que genera renders
   fotorrealistas con el modelo de imágenes de OpenAI usando los secretos del Worker:
     OPENAI_API_KEY  la llave de OpenAI (npx wrangler secret put OPENAI_API_KEY)
     RENDER_CLAVE    una contraseña que se pide en el creador para que nadie más gaste la llave (npx wrangler secret put RENDER_CLAVE)
   POST /api/render-ia  JSON { clave, prompt, modelo, calidad, tamano, variantes, referencia (data URL JPEG/PNG de la maqueta, opcional) }
   GET  /api/render-ia  → { listo, clave } para saber si los secretos están configurados. */
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/api/render-ia") return renderIA(request, env);
    return env.ASSETS.fetch(request);
  }
};

const json = (o, status = 200) => new Response(JSON.stringify(o), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

async function renderIA(request, env) {
  if (request.method === "GET") return json({ listo: !!env.OPENAI_API_KEY, clave: !!env.RENDER_CLAVE });
  if (request.method !== "POST") return json({ error: "Usa POST" }, 405);
  if (!env.OPENAI_API_KEY) return json({ error: "Falta el secreto OPENAI_API_KEY en el Worker (Settings → Variables and Secrets, o npx wrangler secret put OPENAI_API_KEY)." }, 503);
  if (!env.RENDER_CLAVE) return json({ error: "Falta el secreto RENDER_CLAVE en el Worker: es la contraseña que pide el creador para generar." }, 503);
  let cuerpo;
  try { cuerpo = await request.json(); } catch (e) { return json({ error: "Cuerpo inválido" }, 400); }
  const clave = request.headers.get("x-clave") || cuerpo.clave || "";
  if (clave !== env.RENDER_CLAVE) return json({ error: "Clave incorrecta" }, 401);
  const prompt = String(cuerpo.prompt || "").slice(0, 6000);
  if (prompt.length < 20) return json({ error: "Falta el prompt" }, 400);
  const modelo = /^[a-z0-9.-]+$/i.test(cuerpo.modelo || "") ? cuerpo.modelo : "gpt-image-2";
  const calidad = ["low", "medium", "high", "auto"].includes(cuerpo.calidad) ? cuerpo.calidad : "high";
  const tamano = ["1024x1024", "1536x1024", "1024x1536", "auto"].includes(cuerpo.tamano) ? cuerpo.tamano : "1536x1024";
  const n = Math.max(1, Math.min(4, parseInt(cuerpo.variantes || 1, 10) || 1));
  const t0 = Date.now();
  let r;
  try {
    if (cuerpo.referencia && /^data:image\/(jpeg|png);base64,/.test(cuerpo.referencia)) {
      // con la maqueta como referencia: images/edits (multipart)
      const [cab, b64] = cuerpo.referencia.split(",");
      const tipo = cab.includes("png") ? "image/png" : "image/jpeg";
      const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
      const fd = new FormData();
      fd.append("model", modelo); fd.append("prompt", prompt); fd.append("n", String(n)); fd.append("size", tamano); fd.append("quality", calidad);
      fd.append("image[]", new Blob([bin], { type: tipo }), "maqueta." + (tipo === "image/png" ? "png" : "jpg"));
      r = await fetch("https://api.openai.com/v1/images/edits", { method: "POST", headers: { authorization: "Bearer " + env.OPENAI_API_KEY }, body: fd });
    } else {
      r = await fetch("https://api.openai.com/v1/images/generations", { method: "POST", headers: { authorization: "Bearer " + env.OPENAI_API_KEY, "content-type": "application/json" },
        body: JSON.stringify({ model: modelo, prompt, n, size: tamano, quality: calidad }) });
    }
  } catch (e) { return json({ error: "No se pudo llamar a OpenAI: " + String(e) }, 502); }
  const texto = await r.text();
  if (!r.ok) return json({ error: "OpenAI respondió " + r.status, detalle: texto.slice(0, 1500) }, 502);
  let datos; try { datos = JSON.parse(texto); } catch (e) { return json({ error: "Respuesta inválida de OpenAI" }, 502); }
  const imagenes = (datos.data || []).map(d => d.b64_json ? "data:image/png;base64," + d.b64_json : d.url).filter(Boolean);
  return json({ imagenes, modelo, calidad, tamano, ms: Date.now() - t0, uso: datos.usage || null });
}
