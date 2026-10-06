# Cómo se generan los datos

Todo sale de datos abiertos; no hace falta ninguna clave. Se corre desde `pipeline/` con Python 3.12 o más nuevo y unos 6 GB de disco libre. Tarda alrededor de una hora, sin contar la revisión a ojo.

```bash
cd pipeline
python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
bash descargar.sh
```

## Pasos

| # | Script | Qué hace |
|---|---|---|
| 1 | `overture_extract.py` | Baja de Overture Maps (OpenStreetMap, septiembre de 2026) lo que cae en la Comarca: usos de suelo, caminos, agua, edificios, municipios y localidades. Hay que correrlo una vez por tema (ver abajo). |
| 2 | `chm_aggregate2.py` y `chm_mosaico.py` | Resume la altura de árboles a 1 m (Meta y WRI, imágenes de 2018–2020) en cuadros de ~9 m y los pasa a la malla de 20 m. |
| 3 | `s2_series.py`, `s2_stack.py`, `s2_bands.py` y `s2_10m.py` | Arma la serie de Sentinel-2 de diciembre de 2025 a septiembre de 2026: NDVI de 10 fechas a 20 m, bandas de verano e invierno y color verdadero a 10 m. |
| 4 | `train_tree2026.py` | Entrena un clasificador de «dosel de árbol vivo en 2026». Aprende de la altura de 2018–2020 y lo aplica a la serie de 2026. |
| 5 | `stack10.py`, `terreno.py` y `edificios.py` | Junta todas las capas en una malla UTM de 10 m: árboles, pendiente, ESA WorldCover y conteo de edificios. |
| 6 | `objects2.py` | Recorta las arboledas en objetos, cortados por caminos, canales y ríos. «activa» es la que tiene árboles en 2026; «perdida», la que los tenía en 2018–2020 y hoy ya no. |
| 7 | `lattice_all.py`, `texture_all.py` y `s2feat_fix.py` | Mide cada objeto: si tiene cuadrícula de árboles, la textura de las copas, la fenología y la forma. |
| 8 | Revisión a ojo | `zoomsheet.py`, `sheet.py` y `area_view2.py` hacen hojas de imágenes para revisar. Las etiquetas quedan en `etiquetas/`. |
| 9 | `objclf.py` y `autoclass.py` | Clasificador de objetos (nogalera sí o no) entrenado con las etiquetas. |
| 10 | `urbano.py` | Mancha urbana y distancia de cada punto a la ciudad y a los pueblos. |
| 11 | `final.py` y `finalize.py` | Selección final, medidas, municipio, localidad cercana, precio estimado y exportación a `../public/`. |

Orden de ejecución:

```bash
for t in "theme=base/type=land_use:" "theme=transportation/type=segment:id,geometry,bbox,subtype,class,names,subclass" \
         "theme=base/type=water:id,geometry,bbox,subtype,class,names,is_intermittent,source_tags" \
         "theme=buildings/type=building:id,geometry,bbox,subtype,class,height,num_floors,sources" \
         "theme=divisions/type=division:id,geometry,bbox,subtype,class,names,population,hierarchies,parent_division_id,country,region" \
         "theme=divisions/type=division_area:id,geometry,bbox,subtype,class,names,division_id,country,region,is_land"; do
  tema=${t%%:*}; cols=${t#*:}; nombre=$(echo $tema | sed 's/.*type=//')
  ./venv/bin/python scripts/overture_extract.py "$tema" data/ov_$nombre.parquet $cols
done
mv data/ov_segment.parquet data/ov_segments.parquet; mv data/ov_building.parquet data/ov_buildings.parquet
for t in 023123120 023123121 023123102 023123103; do ./venv/bin/python scripts/chm_aggregate2.py data/chm/$t.tif data/chm/agg2_$t.tif; done
./venv/bin/python scripts/s2_series.py && ./venv/bin/python scripts/s2_stack.py
./venv/bin/python scripts/chm_mosaico.py
./venv/bin/python scripts/s2_bands.py 2026-08 S2C_13RFJ_20260824_0_L2A S2C_13RFH_20260824_0_L2A S2C_13RGJ_20260824_0_L2A S2C_13RFK_20260824_0_L2A S2C_13RGK_20260824_0_L2A
./venv/bin/python scripts/s2_bands.py 2026-01 S2C_13RFJ_20260126_0_L2A S2C_13RFH_20260126_0_L2A S2C_13RGJ_20260126_0_L2A S2C_13RFK_20260126_0_L2A S2C_13RGK_20260126_0_L2A
./venv/bin/python scripts/s2_10m.py 2026-08 S2C_13RFJ_20260824_0_L2A S2C_13RFH_20260824_0_L2A S2C_13RGJ_20260824_0_L2A S2C_13RFK_20260824_0_L2A S2C_13RGK_20260824_0_L2A
./venv/bin/python scripts/train_tree2026.py
./venv/bin/python scripts/stack10.py && ./venv/bin/python scripts/terreno.py && ./venv/bin/python scripts/edificios.py
./venv/bin/python scripts/objects2.py
./venv/bin/python scripts/lattice_all.py && ./venv/bin/python scripts/texture_all.py && ./venv/bin/python scripts/s2feat_fix.py
./venv/bin/python scripts/objclf.py && ./venv/bin/python scripts/autoclass.py
./venv/bin/python scripts/urbano.py
./venv/bin/python scripts/final.py && ./venv/bin/python scripts/finalize.py
```

## Etiquetas de la revisión a ojo

- `etiquetas/labels.txt`: objeto «activa» y código. `O` = nogalera, `M` = nogalera con arboleda de río, `N` = no es nogalera, `U` = dudosa (la decide el clasificador). Si un objeto aparece dos veces, vale la última.
- `etiquetas/labels_lost2.txt`: objetos «perdida». `L` = era nogalera; `U`, `N` y `X` no se usan.
- `etiquetas/revision_visual.csv`: las mismas etiquetas, cada una con su punto (lat, lon).

Los números de objeto solo valen para esta corrida. Si cambian los datos de entrada, los objetos se numeran distinto. Para reusar la revisión, cruza `revision_visual.csv` por ubicación: el punto cae dentro del objeto nuevo.

## Precio estimado (a ojo de buen cubero)

En `final.py`, función `precio_m2`:

- Nogalera en producción lejos de todo: **$90/m²**. Terreno ya sin nogales: **$55/m²**.
- Cerca de la mancha urbana sube hasta **$800/m²** junto a Torreón y **$600/m²** junto a Gómez Palacio o Lerdo. Se va diluyendo con la distancia (la diferencia baja a 37 % a los 2.5 km).
- Junto a un pueblo, hasta **$300/m²** (la diferencia baja a 37 % a los 1.5 km).
- Las huertas grandes bajan un poco por m² (factor (ha/10)^−0.12, entre 0.75 y 1.3).
- Rango que se muestra: de −35 % a +50 %.

Calibración, con anuncios de 2025–2026: 50 ha con 1,100 nogales en Matamoros, $34.5 millones (≈ $69/m²; avalúo de $40.1 millones). 30 ha en La Loma, Lerdo, $40.5 millones (≈ $135/m²). 40 ha con 1,300 nogales, $20 millones (≈ $50/m²). Lotes urbanizados de Torreón, $3,500–3,750/m²; terrenos cerca de TSM, $850/m². No es un avalúo.

## N6 (diseño de fraccionamiento)

```bash
./venv/bin/python scripts/n6_optimo.py                              # barrido de lotes de 280 a 330 m² → public/n6/n6.geojson y lotes-*.geojson
./venv/bin/python scripts/n6_arboles.py                             # detecta cada nogal y la cuadrícula → data/n6_arboles.npy, data/n6_grid.npy
./venv/bin/python scripts/n6_final.py data ../public/n6             # diseño alineado a los nogales → public/n6/final.geojson y arboles.json
```

El límite de N6 está en `etiquetas/n6_limite.geojson`.
./venv/bin/python scripts/n6_direcciones.py data ../public/n6       # diseño con confort + nombres de calles, direcciones y capa rentable → public/n6/confort.geojson
