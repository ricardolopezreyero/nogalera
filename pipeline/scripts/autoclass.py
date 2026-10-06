import json, numpy as np
d = json.load(open("data/objects2_utm.geojson")); F = d["features"]
def cls(p):
    lat = p["lat"] if p["lat"] == p["lat"] else 0.0
    if p["ndvi"] == 0 or p["ndvi"] < -1: return "sin_dato"
    if p["kind"] == "activa":
        if p["nolu"] >= 0.5 or p["lake"] >= 0.3: return "no"
        if p["c2"] < 0.05 and p["cells"] < 150: return "no"
        if lat >= 0.25 and p["river"] < 0.3 and p["lake"] < 0.1 and p["nolu"] < 0.3 and p["c2"] >= 0.05: return "si"
        if p["rect"] >= 0.8 and p["c5"] >= 0.4 and p["river"] < 0.1 and p["lake"] < 0.1 and p["nolu"] < 0.3: return "si"
        return "revisar"
    else:
        if p["nolu"] >= 0.5 or p["lake"] >= 0.3: return "no"
        if lat >= 0.2: return "si"
        if lat < 0.1: return "no"
        return "revisar"
from collections import Counter
c = Counter(); ha = Counter()
for f in F:
    k = cls(f["properties"]); f["properties"]["auto"] = k
    c[(f["properties"]["kind"], k)] += 1; ha[(f["properties"]["kind"], k)] += f["properties"]["cells"] / 100
for k in sorted(c): print(k, c[k], round(ha[k]), "ha")
json.dump(d, open("data/objects2_utm.geojson", "w"))
rev = [i for i, f in enumerate(F) if f["properties"]["auto"] == "revisar"]
rev.sort(key=lambda i: -F[i]["properties"]["cells"])
open("data/_rev_all.txt", "w").write(",".join(map(str, rev)))
print("revisar", len(rev), "por tamaño:", sum(F[i]["properties"]["cells"] >= 200 for i in rev), ">=2ha;", sum(F[i]["properties"]["cells"] < 200 for i in rev), "<2ha")
