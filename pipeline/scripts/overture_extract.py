"""Extrae de Overture (GeoParquet en S3) los elementos dentro de un bbox.
Uso: python overture_extract.py <theme/type> <salida.parquet> [filtro_columnas]
"""
import sys, re, json, urllib.request, concurrent.futures as cf
import pyarrow as pa, pyarrow.parquet as pq, pyarrow.compute as pc
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from httpfile import HTTPRangeFile

BASE = "https://overturemaps-us-west-2.s3.us-west-2.amazonaws.com"
REL = "release/2026-09-23.1"
W, S, E, N = -104.05, 25.10, -102.55, 26.33

def list_files(tt):
    keys, token = [], None
    while True:
        u = f"{BASE}/?list-type=2&prefix={REL}/{tt}/"
        if token: u += "&continuation-token=" + urllib.parse.quote(token)
        x = urllib.request.urlopen(u, timeout=60).read().decode()
        keys += [(k, int(s)) for k, s in re.findall(r"<Key>([^<]+)</Key>.*?<Size>(\d+)</Size>", x)]
        m = re.search(r"<NextContinuationToken>([^<]+)", x)
        if not m: break
        token = m.group(1)
    return [k for k in keys if k[0].endswith(".parquet")]

def leaf_index(md, name):
    sch = md.schema
    for i in range(len(sch)):
        if sch.column(i).path == name:
            return i
    raise KeyError(name)

def scan(key, size, columns):
    f = HTTPRangeFile(f"{BASE}/{key}", size=size)
    pf = pq.ParquetFile(f)
    md = pf.metadata
    ix = {k: leaf_index(md, f"bbox.{k}") for k in ("xmin", "xmax", "ymin", "ymax")}
    hits = []
    for rg in range(md.num_row_groups):
        r = md.row_group(rg)
        st = {k: r.column(i).statistics for k, i in ix.items()}
        if any(s is None or not s.has_min_max for s in st.values()):
            hits.append(rg); continue
        if st["xmin"].min <= E and st["xmax"].max >= W and st["ymin"].min <= N and st["ymax"].max >= S:
            hits.append(rg)
    tables = []
    for rg in hits:
        t = pf.read_row_group(rg, columns=columns)
        bb = t.column("bbox")
        xmin = pc.struct_field(bb, "xmin"); xmax = pc.struct_field(bb, "xmax")
        ymin = pc.struct_field(bb, "ymin"); ymax = pc.struct_field(bb, "ymax")
        m = pc.and_(pc.and_(pc.less_equal(xmin, E), pc.greater_equal(xmax, W)),
                    pc.and_(pc.less_equal(ymin, N), pc.greater_equal(ymax, S)))
        t = t.filter(m)
        if t.num_rows: tables.append(t)
    return key, len(hits), md.num_row_groups, f.bytes_fetched, tables

if __name__ == "__main__":
    tt, out = sys.argv[1], sys.argv[2]
    columns = sys.argv[3].split(",") if len(sys.argv) > 3 else None
    files = list_files(tt)
    print(len(files), "archivos", flush=True)
    allt = []
    with cf.ThreadPoolExecutor(8) as ex:
        futs = [ex.submit(scan, k, s, columns) for k, s in files]
        for fu in cf.as_completed(futs):
            key, nh, nrg, nb, tables = fu.result()
            rows = sum(t.num_rows for t in tables)
            print(f"{key.rsplit('/',1)[1][:12]} rg {nh}/{nrg} bajado {nb/1e6:.1f} MB filas {rows}", flush=True)
            allt += tables
    if allt:
        t = pa.concat_tables(allt, promote_options="default")
        pq.write_table(t, out)
        print("total filas", t.num_rows)
    else:
        print("sin resultados")
