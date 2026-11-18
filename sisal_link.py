#!/usr/bin/env python3
"""Links the OSM caves of this site to the SISAL sites (PRIMER.md, step S5).

Reads   data/seeds/sisal-sites.csv      the 305 SISAL sites (site_id, site_name, wkt, number of d18O and d13C samples)
        data/raw/osm/overpass/*.json    the OSM nodes of the harvest
        data/seeds/sisal-overrides.csv  your decisions (site_id, osm_id, decision accept|reject, note)
Writes  data/seeds/sisal-matches.csv    every candidate pair within 5 km with distance, name similarity, score and status
        data/csv/                       the properties P114 to P120 and, for every pair with status sure or accepted, a statement
                                        "SISAL site" on the item of the OSM node (rows without `origin`, so `import-osm` keeps them)

Status: sure = the names agree (similarity 0.8 or more), or the site lies within 250 m and the names mostly agree (0.65), or within 50 m;
check = names half agree or the site lies within 1 km (decide in sisal-overrides.csv); weak = the rest.
Score = 0.7 * name similarity + 0.3 * (1 - distance / 5 km), the same formula as py/SISAL in osm2lod.
Run after `python main.py import-osm --offline`; running it twice changes nothing. Windows: `python sisal_link.py`.
"""
from __future__ import annotations

import csv
import difflib
import glob
import json
import math
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEEDS = ROOT / "data" / "seeds"
CSV = ROOT / "data" / "csv"
SITE_IRI = "http://w3id.org/geo-lod/Cave_site_{:04d}"
SOURCE = "https://research-squirrel-engineers.github.io/GeoScience-FAIRification-LOD/"
RADIUS_KM = 5.0
STOP = set("""cave caves cavern caverns grotte grotta grotto gruta caverna caverne hohle hoehle hole cueva pestera pecina jaskinia jeskyne
barlang barlangja magara mağara cova sistema system entrance eingang bejarat de la el del di da do of the gua goa ngalau jama ledenica
grot gouffre aven resurgence spring""".split())
PROPS = [  # id, datatype, label_en, label_de, description_en, description_de
    ("P114", "url", "SISAL site", "SISAL-Standort",
     "The SISAL speleothem site (palaeoclimate record) that this cave belongs to, as its IRI in the geo-lod graph of the EPICA-SISAL-FAIRification project.",
     "Der SISAL-Standort (Speleothem-Paläoklima), zu dem diese Höhle gehört, als IRI im geo-lod-Graphen des Projekts EPICA-SISAL-FAIRification."),
    ("P115", "string", "SISAL site name", "SISAL-Standortname", "Name of the SISAL site (qualifier).", "Name des SISAL-Standorts (Qualifier)."),
    ("P116", "quantity", "d18O samples", "δ18O-Proben", "Number of δ18O samples of the SISAL site (qualifier).", "Zahl der δ18O-Proben des SISAL-Standorts (Qualifier)."),
    ("P117", "quantity", "d13C samples", "δ13C-Proben", "Number of δ13C samples of the SISAL site (qualifier).", "Zahl der δ13C-Proben des SISAL-Standorts (Qualifier)."),
    ("P118", "quantity", "match distance (km)", "Abstand der Zuordnung (km)", "Distance in kilometres between the SISAL site and the OSM element (qualifier).",
     "Abstand in Kilometern zwischen SISAL-Standort und OSM-Element (Qualifier)."),
    ("P119", "quantity", "match score", "Zuordnungs-Score", "Score of the assignment, 0 to 1: 0.7 times name similarity plus 0.3 times closeness (qualifier).",
     "Score der Zuordnung, 0 bis 1: 0,7 mal Namensähnlichkeit plus 0,3 mal Nähe (Qualifier)."),
    ("P120", "string", "match status", "Status der Zuordnung", "sure (names or position agree) or accepted (confirmed by hand) (qualifier).",
     "sure (Namen oder Lage stimmen überein) oder accepted (von Hand bestätigt) (Qualifier)."),
]


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    tokens = [t for t in re.findall(r"[^\W_]+", text) if t not in STOP]
    return " ".join(tokens) or text


def km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p = math.pi / 180
    return 6371.0 * math.hypot((lon2 - lon1) * p * math.cos((lat1 + lat2) * p / 2), (lat2 - lat1) * p)


def status(distance: float, similarity: float) -> str:
    if similarity >= 0.8 or distance <= 0.05 or (distance <= 0.25 and similarity >= 0.65):
        return "sure"
    return "check" if similarity >= 0.5 or distance <= 1.0 else "weak"


def read(path: Path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write(path: Path, rows: list[dict], fields: list[str]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    sites = []
    for r in read(SEEDS / "sisal-sites.csv"):
        m = re.match(r"POINT\(([-\d.]+) ([-\d.]+)\)", r["wkt"])
        sites.append({**r, "lon": float(m[1]), "lat": float(m[2])})
    files = sorted(glob.glob(str(ROOT / "data/raw/osm/overpass/*.json")))
    elements = [e for f in files for e in json.load(open(f, encoding="utf-8"))["elements"] if e["type"] == "node"]
    overrides = {(r["site_id"], r["osm_id"]): r["decision"] for r in read(SEEDS / "sisal-overrides.csv")}
    idmap = {r["key"]: r["id"] for r in read(CSV / "idmap.csv") if r["source"] == "osm"}
    pairs = []
    for e in sorted(elements, key=lambda e: e["id"]):
        tags = e.get("tags", {})
        names = [tags[k] for k in ("name", "name:en", "alt_name", "official_name", "int_name", "loc_name", "old_name") if tags.get(k)]
        for s in sites:
            d = km(e["lat"], e["lon"], s["lat"], s["lon"])
            if d > RADIUS_KM:
                continue
            sim = max((difflib.SequenceMatcher(None, norm(s["site_name"]), norm(n)).ratio() for n in names), default=0.0)
            score = 0.7 * sim + 0.3 * (1 - d / RADIUS_KM)
            st = status(d, sim)
            dec = overrides.get((s["site_id"], str(e["id"])), "")
            use = "accepted" if dec == "accept" else ("" if dec == "reject" else ("sure" if st == "sure" else ""))
            pairs.append({"site_id": s["site_id"], "site_name": s["site_name"], "osm_id": e["id"], "osm_name": names[0] if names else "",
                          "distance_km": f"{d:.3f}", "name_similarity": f"{sim:.3f}", "score": f"{score:.3f}", "status": st, "decision": dec, "used": use,
                          "n_d18o": s["n_d18o_samples"], "n_d13c": s["n_d13c_samples"]})
    pairs.sort(key=lambda p: (-float(p["score"]), p["site_id"], p["osm_id"]))
    write(SEEDS / "sisal-matches.csv", pairs, list(pairs[0]))

    ents = read(CSV / "entities.csv")
    stats = read(CSV / "statements.csv")
    quals = read(CSV / "qualifiers.csv")
    refs = read(CSV / "references.csv")
    old = {r["sid"] for r in stats if r["property"] == "P114"}
    stats = [r for r in stats if r["property"] != "P114"]
    quals = [r for r in quals if r["sid"] not in old]
    refs = [r for r in refs if r["sid"] not in old]
    ents = [r for r in ents if r["id"] not in {p[0] for p in PROPS}]
    for pid, dt, len_, lde, den, dde in PROPS:
        ents.append({"id": pid, "kind": "property", "datatype": dt, "origin": "", "label_en": len_, "label_de": lde, "description_en": den, "description_de": dde})
    count: dict[str, int] = {}
    for p in sorted((p for p in pairs if p["used"]), key=lambda p: (int(p["osm_id"]), int(p["site_id"]))):
        qid = idmap.get(f"node/{p['osm_id']}")
        if not qid:
            continue
        count[qid] = count.get(qid, 0) + 1
        sid = f"{qid}-P114-{count[qid]}"
        stats.append({"sid": sid, "subject": qid, "property": "P114", "value": SITE_IRI.format(int(p["site_id"])), "rank": "", "origin": ""})
        for prop, val in (("P115", p["site_name"]), ("P116", p["n_d18o"]), ("P117", p["n_d13c"]), ("P118", p["distance_km"]),
                          ("P119", p["score"]), ("P120", p["used"])):
            quals.append({"sid": sid, "property": prop, "value": val})
        refs.append({"sid": sid, "group": "1", "property": "P6", "value": SOURCE})
    for name, rows in (("entities", ents), ("statements", stats), ("qualifiers", quals), ("references", refs)):
        write(CSV / f"{name}.csv", rows, list(rows[0]))
    used = [p for p in pairs if p["used"]]
    print(f"[sisal-link] {len(sites)} sites, {len(elements)} nodes, {len(pairs)} candidate pairs within {RADIUS_KM:g} km: "
          f"{sum(p['status'] == 'sure' for p in pairs)} sure, {sum(p['status'] == 'check' for p in pairs)} check, {sum(p['status'] == 'weak' for p in pairs)} weak")
    print(f"[sisal-link] {len(used)} statement(s) written on {len({p['osm_id'] for p in used})} item(s), {len({p['site_id'] for p in used})} site(s); "
          f"{sum(1 for p in pairs if p['status'] == 'check' and not p['decision'])} pair(s) to decide in data/seeds/sisal-overrides.csv")


if __name__ == "__main__":
    main()
