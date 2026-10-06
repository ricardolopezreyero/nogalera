"""Clasificador de 'dosel de árbol vivo en 2026' (Sentinel-2) entrenado con el CHM 2018-2020 como etiqueta.
Solo trabaja con píxeles que alguna vez tuvieron NDVI >= 0.3 (el resto no es árbol vivo)."""
import numpy as np, rasterio, time, warnings
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, precision_recall_fscore_support
warnings.filterwarnings("ignore")
ts = np.load("data/s2ts/ts.npy")                          # (10, H, W) NDVI
_, H, W = ts.shape
mx = np.nanmax(ts, 0)
cand = (mx >= 0.3) & ~np.isnan(ts).any(axis=0)
ii = np.nonzero(cand.ravel())[0]
print("candidatos", len(ii), flush=True)
def gather(path, scale):
    with rasterio.open(path) as ds:
        out = np.empty((len(ii), ds.count), np.float32)
        for b in range(ds.count):
            out[:, b] = ds.read(b + 1).ravel()[ii].astype(np.float32) / scale
    return out
T = ts.reshape(10, -1)[:, ii].T
BS = gather("data/s2ts/bands_2026-08.tif", 10000); BW = gather("data/s2ts/bands_2026-01.tif", 10000)
BS[BS == 0] = np.nan; BW[BW == 0] = np.nan
gs = T[:, 3:10]
DER = np.stack([gs.min(1), gs.mean(1), gs.std(1), T[:, 0:3].mean(1), gs.mean(1) - T[:, 0:3].mean(1), T.max(1)], 1)
X = np.concatenate([T, BS, BW, DER], 1); del BS, BW
chm = gather("data/chm/chm20.tif", 1)
c2, c5 = chm[:, 0], chm[:, 1]
pos = (c5 >= 0.45) & (T[:, 8] >= 0.35) & (T[:, 7] >= 0.35)
neg = (c2 <= 0.02)
rng = np.random.default_rng(0)
ip = np.nonzero(pos)[0]; ineg = np.nonzero(neg)[0]
ineg = rng.choice(ineg, min(400000, len(ineg)), replace=False)
idx = np.concatenate([ip, ineg]); y = np.concatenate([np.ones(len(ip)), np.zeros(len(ineg))])
rows, cols = ii[idx] // W, ii[idx] % W
blk = (rows // 250) * 1000 + (cols // 250)
test = ((blk * 2654435761) % 5 == 0)
t = time.time()
clf = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.1, max_leaf_nodes=63, l2_regularization=1.0, random_state=0)
clf.fit(X[idx][~test], y[~test])
p = clf.predict_proba(X[idx][test])[:, 1]
print(f"train {(~test).sum()} test {test.sum()} pos {int(y.sum())} | AUC {roc_auc_score(y[test], p):.4f} | {time.time()-t:.0f}s", flush=True)
for th in (0.3, 0.5, 0.7):
    pr, rc, f1, _ = precision_recall_fscore_support(y[test], p >= th, average="binary")
    print(f"  umbral {th}: precisión {pr:.3f} recall {rc:.3f} F1 {f1:.3f}")
clf.fit(X[idx], y)
prob = np.zeros(H * W, np.float32)
prob[ii] = clf.predict_proba(X)[:, 1]
prob = prob.reshape(H, W)
ref = rasterio.open("data/s2ts/ndvi_2026-08.tif")
with rasterio.open("data/s2ts/tree2026_prob.tif", "w", driver="GTiff", width=W, height=H, count=1, dtype="uint8", crs=ref.crs, transform=ref.transform, compress="deflate", tiled=True) as o:
    o.write((prob * 255).astype(np.uint8), 1)
c2f = np.zeros(H * W, np.float32); c2f[ii] = c2; c2f = c2f.reshape(H, W)
print("px prob>=0.5:", int((prob >= 0.5).sum()), "=", (prob >= 0.5).sum() * 0.04, "ha | positivos CHM:", int(pos.sum()), "=", pos.sum()*0.04, "ha")
print("nuevos (prob>=0.5 y c2<=0.02):", int(((prob >= 0.5) & (c2f <= 0.02)).sum()))
