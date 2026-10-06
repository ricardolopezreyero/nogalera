import sys, re, json, urllib.request
B = "https://sentinel-cogs.s3.us-west-2.amazonaws.com"
sq, months = sys.argv[1], sys.argv[2:]
for ym in months:
    y, m = ym.split("-")
    x = urllib.request.urlopen(f"{B}/?list-type=2&prefix=sentinel-s2-l2a-cogs/13/R/{sq}/{y}/{int(m)}/&delimiter=/").read().decode()
    for p in re.findall(r"<Prefix>([^<]+L2A/)</Prefix>", x):
        sid = p.rstrip("/").rsplit("/", 1)[1]
        try:
            it = json.load(urllib.request.urlopen(f"{B}/{p}{sid}.json"))
            pr = it["properties"]
            print(sid, pr.get("datetime","")[:10], "cloud", pr.get("eo:cloud_cover"), "nodata", pr.get("s2:nodata_pixel_percentage"))
        except Exception as e:
            print(sid, "ERR", e)
