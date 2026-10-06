#!/usr/bin/env bash
# Descarga los datos base (≈ 450 MB) a pipeline/data/. Correr desde pipeline/.
set -euo pipefail
mkdir -p data/chm data/dem data/s2ts

# Altura de árboles a 1 m de Meta y WRI (imágenes 2018–2020), teselas quadkey de La Laguna.
CHM=https://dataforgood-fb-data.s3.amazonaws.com/forests/v1/alsgedi_global_v6_float/chm
for t in 023123120 023123121 023123102 023123103; do
  curl -sf -o "data/chm/$t.tif" "$CHM/$t.tif"
done

# Copernicus DEM 30 m.
DEM=https://copernicus-dem-30m.s3.amazonaws.com
for t in N25_00_W104_00 N25_00_W103_00 N26_00_W104_00 N26_00_W103_00; do
  curl -sf -o "data/dem/$t.tif" "$DEM/Copernicus_DSM_COG_10_${t}_DEM/Copernicus_DSM_COG_10_${t}_DEM.tif"
done
echo "listo"
