# Renders de súper alta calidad: modelo 3D → mapas de control → FLUX + ControlNet → 4K

Es la tubería de `archviz-ai` adaptada a La Nogalera. La diferencia con un render «a mano» es que la IA no inventa la casa: recibe la
**geometría exacta** (profundidad, normales y líneas de nuestro modelo) y sólo pone materiales, luz y vegetación fotorrealistas encima.

```
public/datos/escenas/*.json  (nuestro modelo)
        │  node pipeline/scripts/fotos.js --control
        ▼
public/renders/foto/img/<nombre>.jpg          render WebGL (referencia de color y luz)
public/renders/foto/control/<nombre>-depth.png    profundidad (cerca = blanco)
public/renders/foto/control/<nombre>-normal.png   normales en espacio de cámara
public/renders/foto/control/<nombre>-lineart.png  líneas (negro sobre blanco)
        │  python3 pipeline/comfy/correr.py  (ComfyUI en una máquina con GPU de 24 GB)
        ▼
pipeline/comfy/salida/<nombre>.png            FLUX.1-dev + ControlNet Union (depth + canny) a 2K → Real-ESRGAN ×2 → 4K
```

## Qué hace falta (una sola vez, en la máquina con GPU o en RunPod/Vast)

1. **ComfyUI** (https://github.com/comfyanonymous/ComfyUI) con el manager.
2. Modelos, en las carpetas de ComfyUI:
   - `models/unet/flux1-dev.safetensors` (black-forest-labs/FLUX.1-dev, requiere aceptar la licencia en Hugging Face)
   - `models/clip/t5xxl_fp16.safetensors` y `models/clip/clip_l.safetensors`
   - `models/vae/ae.safetensors`
   - `models/controlnet/FLUX.1-dev-ControlNet-Union-Pro-2.0.safetensors` (Shakker-Labs)
   - `models/upscale_models/RealESRGAN_x4plus.safetensors`
3. Arrancar ComfyUI: `python main.py --listen 0.0.0.0 --port 8188`.
4. Copiar aquí `public/renders/foto/img/` y `public/renders/foto/control/` (o clonar el repositorio).
5. `python3 pipeline/comfy/correr.py --comfy http://localhost:8188 --nombre fachada-horizonte` (o sin `--nombre` para todos los de `fotos_lista.json`).

`nogalera_flux_controlnet.json` es el flujo en formato API de ComfyUI (el que acepta `POST /prompt`). `correr.py` lo rellena por imagen:
sube los dos mapas de control, pone el prompt de la escena (`public/datos/escenas/prompts_ia.json` + materiales de la fachada), lanza, espera
y guarda el resultado en `pipeline/comfy/salida/`. Parámetros: 2048 × 1152 base, 28 pasos, guidance 3.5, fuerza del ControlNet 0.65
(profundidad) y 0.45 (líneas): respeta la geometría sin que se vea «dibujada». Para 4K reales, el flujo termina con Real-ESRGAN ×2.

## Sin GPU: el Worker con gpt-image-2

`python3 pipeline/scripts/renders_worker.py --clave 123 --nombre fachada-horizonte` manda el render WebGL como referencia al endpoint
`/api/render-ia` del sitio (la llave de OpenAI vive en Cloudflare) y guarda la imagen en `pipeline/comfy/salida/`. Menos control que
FLUX + ControlNet (gpt-image-2 no lee mapas de profundidad), pero sale en un minuto desde cualquier computadora.
