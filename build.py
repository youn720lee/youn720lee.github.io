#!/usr/bin/env python3
"""Build the static homepage from the YAML files in ./data.

    python build.py            # writes index.html, assets/publications.bib, tiles

Edit data/*.yml, run this script, commit the result.  No build step runs on
GitHub Pages; the generated index.html is what gets served.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import html
import pathlib
import re

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "data"
TEMPLATES = ROOT / "templates"
TILES = ROOT / "assets" / "pubs" / "tiles"

TYPE_LABEL = {
    "journal": "Journal",
    "conference": "Conference",
    "workshop": "Workshop",
    "preprint": "Preprint",
    "domestic": "Domestic",
}

# Consistent tile colours for frequently used venues; anything else is hashed
# onto the palette below.
VENUE_COLORS = {
    "CVPR": ("#1e3a8a", "#3b82f6"),
    "ICCV": ("#3730a3", "#6366f1"),
    "ECCV": ("#4c1d95", "#8b5cf6"),
    "WACV": ("#0f766e", "#14b8a6"),
    "ICRA": ("#9a3412", "#f97316"),
    "RA-L": ("#b45309", "#f59e0b"),
    "T-ITS": ("#065f46", "#10b981"),
    "T-NNLS": ("#155e75", "#06b6d4"),
    "PRL": ("#831843", "#ec4899"),
    "ICIP": ("#1e40af", "#60a5fa"),
    "AVSS": ("#7c2d12", "#fb923c"),
    "IV": ("#365314", "#84cc16"),
    "arXiv": ("#7f1d1d", "#ef4444"),
    "IEEE Access": ("#1f2937", "#6b7280"),
    "Inf. Sci.": ("#312e81", "#818cf8"),
}
PALETTE = [
    ("#1e3a8a", "#3b82f6"), ("#0f766e", "#14b8a6"), ("#7c2d12", "#fb923c"),
    ("#4c1d95", "#8b5cf6"), ("#065f46", "#10b981"), ("#831843", "#ec4899"),
    ("#155e75", "#06b6d4"), ("#365314", "#84cc16"), ("#1f2937", "#6b7280"),
]


def load(name: str):
    with open(DATA / name, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def venue_colors(venue_short: str):
    if venue_short in VENUE_COLORS:
        return VENUE_COLORS[venue_short]
    idx = int(hashlib.md5(venue_short.encode()).hexdigest(), 16) % len(PALETTE)
    return PALETTE[idx]


def make_tile(pub: dict) -> str:
    """Write an SVG venue tile for a publication and return its relative path."""
    TILES.mkdir(parents=True, exist_ok=True)
    short = str(pub.get("venue_short") or TYPE_LABEL.get(pub["type"], "Paper"))
    c1, c2 = venue_colors(short)
    year = pub.get("year", "")
    # Scale the label so long venue names still fit on the tile.
    size = 44 if len(short) <= 5 else 34 if len(short) <= 8 else 26
    gid = re.sub(r"[^a-z0-9]", "", short.lower()) or "g"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 160" width="240" height="160" role="img" aria-label="{html.escape(short)} {year}">
  <defs>
    <linearGradient id="g-{gid}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{c1}"/>
      <stop offset="1" stop-color="{c2}"/>
    </linearGradient>
    <pattern id="p-{gid}" width="18" height="18" patternUnits="userSpaceOnUse" patternTransform="rotate(35)">
      <rect width="18" height="18" fill="none"/>
      <line x1="0" y1="0" x2="0" y2="18" stroke="#ffffff" stroke-opacity="0.10" stroke-width="6"/>
    </pattern>
  </defs>
  <rect width="240" height="160" rx="14" fill="url(#g-{gid})"/>
  <rect width="240" height="160" rx="14" fill="url(#p-{gid})"/>
  <circle cx="206" cy="-10" r="70" fill="#ffffff" fill-opacity="0.10"/>
  <text x="22" y="94" font-family="Inter, 'Segoe UI', Helvetica, Arial, sans-serif" font-weight="800" font-size="{size}" fill="#ffffff" letter-spacing="-0.5">{html.escape(short)}</text>
  <text x="22" y="128" font-family="Inter, 'Segoe UI', Helvetica, Arial, sans-serif" font-weight="600" font-size="18" fill="#ffffff" fill-opacity="0.85">{year}</text>
</svg>
"""
    path = TILES / f"{pub['key']}.svg"
    path.write_text(svg, encoding="utf-8")
    return path.relative_to(ROOT).as_posix()


def bib_author(name: str) -> str:
    name = name.strip()
    if "," in name:
        return name
    parts = name.split()
    if len(parts) == 1:
        return name
    return f"{parts[-1]}, {' '.join(parts[:-1])}"


def bibtex(pub: dict) -> str:
    kind = "article" if pub["type"] in ("journal", "preprint") else "inproceedings"
    fields = [("title", pub["title"]), ("author", " and ".join(bib_author(a) for a in pub["authors"]))]
    venue = pub["venue"]
    if kind == "article":
        fields.append(("journal", venue))
        if pub.get("volume"):
            fields.append(("volume", str(pub["volume"])))
        if pub.get("number"):
            fields.append(("number", str(pub["number"])))
    else:
        fields.append(("booktitle", venue))
    if pub.get("pages"):
        fields.append(("pages", str(pub["pages"]).replace("–", "--").replace("—", "--")))
    fields.append(("year", str(pub["year"])))
    if pub.get("note"):
        fields.append(("note", pub["note"]))
    body = ",\n".join(f"  {k}={{{v}}}" for k, v in fields)
    return f"@{kind}{{{pub['key']},\n{body}\n}}"


def main() -> None:
    profile = load("profile.yml")
    pubs = load("publications.yml")
    projects = load("projects.yml") or []

    self_name = profile["name"]
    for p in pubs:
        p.setdefault("links", {})
        p["links"] = {k: v for k, v in (p["links"] or {}).items() if v}
        p.setdefault("tags", [])
        p["type_label"] = TYPE_LABEL.get(p["type"], p["type"].title())
        p["is_first_author"] = bool(p["authors"]) and p["authors"][0] == self_name
        p["bibtex"] = bibtex(p)
        if not p.get("image"):
            # Use assets/pubs/<key>.(jpg|png|webp|gif) when present, otherwise a venue tile.
            for ext in ("jpg", "jpeg", "png", "webp", "gif"):
                cand = ROOT / "assets" / "pubs" / f"{p['key']}.{ext}"
                if cand.exists():
                    p["image"] = cand.relative_to(ROOT).as_posix()
                    break
            else:
                p["image"] = make_tile(p)
        # Search index text for the client-side filter.
        p["search"] = " ".join([p["title"], " ".join(p["authors"]), p["venue"], str(p["year"]), p.get("venue_short", "")]).lower()

    pubs.sort(key=lambda p: -int(p["year"]))  # stable: keeps file order within a year
    international = [p for p in pubs if p["type"] != "domestic"]
    domestic = [p for p in pubs if p["type"] == "domestic"]

    years = []
    for p in international:
        if not years or years[-1]["year"] != p["year"]:
            years.append({"year": p["year"], "pubs": []})
        years[-1]["pubs"].append(p)

    counts = {t: sum(1 for p in pubs if p["type"] == t) for t in TYPE_LABEL}
    counts["selected"] = sum(1 for p in pubs if p.get("selected"))
    counts["all"] = len(international)

    (ROOT / "assets").mkdir(exist_ok=True)
    (ROOT / "assets" / "publications.bib").write_text("\n\n".join(p["bibtex"] for p in pubs) + "\n", encoding="utf-8")

    # Content hashes for cache-busting the stylesheet and script (GitHub Pages caches assets).
    def _v(rel: str) -> str:
        return hashlib.md5((ROOT / rel).read_bytes()).hexdigest()[:8]
    asset_v = {"css": _v("assets/css/style.css"), "js": _v("assets/js/main.js")}

    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(["html", "j2"]), trim_blocks=True, lstrip_blocks=True)
    env.filters["venue_year"] = lambda p: f"{p.get('venue_short') or p['venue']} {p['year']}"
    tpl = env.get_template("index.html.j2")
    out = tpl.render(
        profile=profile,
        years=years,
        domestic=domestic,
        projects=projects,
        counts=counts,
        self_name=self_name,
        asset_v=asset_v,
        updated=_dt.date.today().strftime("%B %Y"),
        year_now=_dt.date.today().year,
    )
    (ROOT / "index.html").write_text(out, encoding="utf-8")
    print(f"index.html written — {len(international)} international + {len(domestic)} domestic publications, {len(projects)} projects")


if __name__ == "__main__":
    main()
