"""Clasificador de objetos (huerta sí/no) entrenado con etiquetas visuales."""
import json, numpy as np, warnings
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import accuracy_score, precision_score, recall_score
warnings.filterwarnings("ignore")
d = json.load(open("data/objects2_utm.geojson")); F = d["features"]
lab = {}
for line in open("etiquetas/labels.txt"):
    if line.strip():
        i, l = line.split(); lab[int(i)] = l
FEATS = ["cells", "t19", "t26", "nolu", "urlu", "bld", "resroad", "ndvi", "rf", "c2", "c5", "hm", "slope", "relief", "crop", "built",
         "wc_tree", "wc_built", "river", "lake", "rect", "convex", "elong", "width", "length", "lat", "lat_sp", "lat_pm", "con", "f5", "hstd",
         "win", "spr", "smin", "smean", "nstd"]
def vec(p):
    v = []
    for k in FEATS:
        x = p.get(k, np.nan)
        x = np.nan if x is None else float(x)
        if k in ("cells",): x = np.log(x)
        if k in ("bld", "resroad"): x = x / max(p["cells"], 1)
        v.append(x)
    return v
X = np.array([vec(f["properties"]) for f in F]); X = np.nan_to_num(X, nan=-1)
kind = np.array([f["properties"]["kind"] == "activa" for f in F])
idx = np.array([i for i in lab if lab[i] in ("O", "N", "M")])
y = np.array([1 if lab[i] in ("O", "M") else 0 for i in idx])
clf = RandomForestClassifier(n_estimators=600, min_samples_leaf=2, max_features=0.35, random_state=0, class_weight="balanced")
cv = StratifiedKFold(5, shuffle=True, random_state=0)
p = cross_val_predict(clf, X[idx], y, cv=cv, method="predict_proba")[:, 1]
for th in (0.4, 0.5, 0.6):
    print(f"umbral {th}: exactitud {accuracy_score(y, p >= th):.3f} precisión {precision_score(y, p >= th):.3f} recall {recall_score(y, p >= th):.3f}")
clf.fit(X[idx], y)
imp = sorted(zip(clf.feature_importances_, FEATS), reverse=True)
print("importancias:", ", ".join(f"{k}={v:.3f}" for v, k in imp[:14]))
P = clf.predict_proba(X)[:, 1]
for f, pp in zip(F, P): f["properties"]["p_orch"] = float(pp)
json.dump(d, open("data/objects2_utm.geojson", "w"))
# resumen
ha = np.array([f["properties"]["cells"] for f in F]) / 100
for kname in ("activa", "perdida"):
    m = np.array([f["properties"]["kind"] == kname for f in F])
    for lo, hi in ((0, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 1.01)):
        s = m & (P >= lo) & (P < hi)
        print(f"{kname} p∈[{lo},{hi}): n={s.sum()} ha={ha[s].sum():.0f}")
np.save("data/cv_probs.npy", np.stack([idx, y, p]))
