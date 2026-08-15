#!/usr/bin/env python3
"""Build WhichDisc prototype HTML: bag paths + gaps + Innova-style plate."""

from __future__ import annotations

import base64
import json
import math
from pathlib import Path

from path_model import Disc, PathModel, category_for, svg_path_d

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
REFS = ROOT / "refs"


def load_innova() -> dict[str, dict]:
    raw = json.loads((ROOT / "innova.json").read_text())
    by: dict[str, dict] = {}
    for d in raw:
        by.setdefault(d["name"], d)
    return by


def disc_from_db(by: dict[str, dict], name: str, aliases: list[str] | None = None) -> Disc:
    aliases = aliases or []
    for key in [name, *aliases]:
        if key in by:
            d = by[key]
            return Disc(
                name=d["name"],
                speed=float(d["speed"]),
                glide=float(d["glide"]),
                turn=float(d["turn"]),
                fade=float(d["fade"]),
                brand=d.get("brand") or "Innova",
            )
    # case-insensitive
    lower = {k.lower(): v for k, v in by.items()}
    for key in [name, *aliases]:
        if key.lower() in lower:
            d = lower[key.lower()]
            return Disc(
                name=d["name"],
                speed=float(d["speed"]),
                glide=float(d["glide"]),
                turn=float(d["turn"]),
                fade=float(d["fade"]),
                brand=d.get("brand") or "Innova",
            )
    raise KeyError(name)


def stab_col(d: Disc) -> str:
    """Bucket stability for bag grid.

    Stab sum alone lies: TeeBird (0/2) and Orc (-1/3) both sum to 2.
    Fade-heavy molds tip OS/VOS even when the sum looks "straight."
    """
    s = d.stab
    if s <= -1.0:
        return "US"
    # True beef: high fade, little turn
    if d.fade >= 3.5 and d.turn >= -0.5:
        return "VOS"
    if d.fade >= 3.0 and s >= 1.5:
        return "OS"
    if s <= 2.0:
        return "STR"
    if s < 3.5:
        return "OS"
    return "VOS"


def speed_row(d: Disc) -> str:
    if d.speed <= 3:
        return "Putt/Approach"
    if d.speed <= 5:
        return "Mid"
    if d.speed <= 9:
        return "Fairway"
    if d.speed <= 11:
        return "Control/Hybrid"
    return "Distance"


# Required shot cells for a solid ~12 bag
REQUIRED = [
    ("Putt/Approach", "STR", "Straight putter"),
    ("Putt/Approach", "OS", "OS approach"),
    ("Mid", "US", "Flip / turnover mid"),
    ("Mid", "STR", "Neutral mid"),
    ("Mid", "OS", "Stable mid"),
    ("Fairway", "US", "US fairway"),
    ("Fairway", "STR", "Workhorse fairway"),
    ("Fairway", "OS", "OS fairway"),
    ("Control/Hybrid", "STR", "Controllable distance"),
    ("Control/Hybrid", "OS", "OS hybrid / wind"),
    ("Distance", "US", "Flip distance"),
    ("Distance", "OS", "OS distance"),
]


def cell_for(d: Disc) -> tuple[str, str]:
    return speed_row(d), stab_col(d)


def plate_svg(
    discs: list[Disc],
    model: PathModel,
    *,
    title: str,
    width: int = 920,
    height: int = 520,
    ghost: list[Disc] | None = None,
) -> str:
    """Innova-style plate: tee top, flight down, one column path per disc."""
    ghost = ghost or []
    all_d = discs + ghost
    if not all_d:
        return f'<svg width="{width}" height="{height}"></svg>'

    pad_l, pad_r, pad_t, pad_b = 36, 36, 48, 78
    n = len(all_d)
    col_w = (width - pad_l - pad_r) / max(n, 1)
    max_len = max(model.length(d) for d in all_d)
    # fit y
    usable_h = height - pad_t - pad_b
    sy = usable_h / max_len
    sx = 0.85  # lateral scale

    # grid lines
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="100%" height="100%" fill="#0f1419"/>',
        f'<text x="{pad_l}" y="28" fill="#f2f4f8" font-family="ui-sans-serif,system-ui,sans-serif" font-size="16" font-weight="700">{title}</text>',
        f'<text x="{width-pad_r}" y="28" fill="#8b95a8" font-family="ui-sans-serif,system-ui,sans-serif" font-size="11" text-anchor="end">RHBH schematic · tee at top</text>',
    ]

    # horizontal guides
    for frac, label in [(0.0, "TEE"), (0.33, ""), (0.66, ""), (1.0, "END")]:
        y = pad_t + frac * usable_h
        parts.append(
            f'<line x1="{pad_l-8}" y1="{y:.1f}" x2="{width-pad_r+8}" y2="{y:.1f}" stroke="#243041" stroke-width="1"/>'
        )
        if label:
            parts.append(
                f'<text x="{pad_l-10}" y="{y+4:.1f}" fill="#6b7689" font-size="9" font-family="ui-sans-serif,system-ui,sans-serif" text-anchor="end">{label}</text>'
            )

    # US/OS legend strip
    parts.append(
        f'<text x="{pad_l}" y="{height-18}" fill="#6b7689" font-size="10" font-family="ui-sans-serif,system-ui,sans-serif">← fade (OS left)　　turn / flip (US right) →</text>'
    )

    def draw_one(d: Disc, idx: int, *, is_ghost: bool = False) -> None:
        ox = pad_l + col_w * idx + col_w / 2
        oy = pad_t
        pts = model.path(d, 56)
        dattr = svg_path_d(pts, sx=sx, sy=sy, ox=ox, oy=oy)
        color = model.stability_color(d)
        opacity = 0.35 if is_ghost else 1.0
        dash = ' stroke-dasharray="5 4"' if is_ghost else ""
        sw = 2.2 if is_ghost else 3.0
        # end dot
        ex = ox + pts[-1][0] * sx
        ey = oy + pts[-1][1] * sy
        # start tee tick
        parts.append(
            f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="3.2" fill="{color}" opacity="{opacity}"/>'
        )
        parts.append(
            f'<path d="{dattr}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" opacity="{opacity}"{dash}/>'
        )
        parts.append(
            f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="{color}" opacity="{opacity}"/>'
        )
        # relative distance tick on the right of each path end (shows speed/glide stretch)
        rel = model.length(d) / max_len
        parts.append(
            f'<text x="{ex+8:.1f}" y="{ey+3:.1f}" fill="#6b7689" opacity="{opacity}" font-size="8" font-family="ui-monospace,monospace">{rel:.0%}</text>'
        )
        # label
        label = d.name.upper()
        if is_ghost:
            label = f"+ {label}"
        parts.append(
            f'<text x="{ox:.1f}" y="{height-44}" fill="{color}" opacity="{min(1.0, opacity+0.25)}" font-size="10" font-weight="700" font-family="ui-sans-serif,system-ui,sans-serif" text-anchor="middle">{label}</text>'
        )
        parts.append(
            f'<text x="{ox:.1f}" y="{height-30}" fill="#8b95a8" opacity="{opacity}" font-size="9" font-family="ui-monospace,monospace" text-anchor="middle">{d.numbers}</text>'
        )

    for i, d in enumerate(discs):
        draw_one(d, i, is_ghost=False)
    for j, d in enumerate(ghost):
        draw_one(d, len(discs) + j, is_ghost=True)

    parts.append("</svg>")
    return "\n".join(parts)


def analyze_bag(bag: list[Disc], catalog: list[Disc], model: PathModel):
    occupied: dict[tuple[str, str], list[Disc]] = {}
    for d in bag:
        occupied.setdefault(cell_for(d), []).append(d)

    gaps = []
    for row, col, label in REQUIRED:
        key = (row, col)
        if key not in occupied:
            # find best in-catalog fill for a synthetic target in that cell
            target = _synthetic_target(row, col)
            ranked = sorted(catalog, key=lambda c: _match_score(target, c))
            # prefer same speed row
            pick = None
            for c in ranked:
                if speed_row(c) == row and stab_col(c) == col and c.name not in {b.name for b in bag}:
                    pick = c
                    break
            if pick is None:
                for c in ranked:
                    if c.name not in {b.name for b in bag}:
                        pick = c
                        break
            gaps.append({"row": row, "col": col, "label": label, "pick": pick})

    overlaps = {k: v for k, v in occupied.items() if len(v) > 1}
    return occupied, gaps, overlaps


def _synthetic_target(row: str, col: str) -> Disc:
    speed = {
        "Putt/Approach": 2.5,
        "Mid": 5.0,
        "Fairway": 7.5,
        "Control/Hybrid": 10.0,
        "Distance": 12.0,
    }[row]
    turn, fade = {
        "US": (-2.5, 1.0),
        "STR": (-0.5, 1.5),
        "OS": (0.0, 3.0),
        "VOS": (0.5, 4.0),
    }[col]
    return Disc(name="target", speed=speed, glide=4.0, turn=turn, fade=fade)


def _match_score(src: Disc, cand: Disc) -> float:
    ds = abs(src.speed - cand.speed)
    dg = abs(src.glide - cand.glide)
    dt = abs(src.turn - cand.turn)
    df = abs(src.fade - cand.fade)
    dst = abs(src.stab - cand.stab)
    band = 0.0 if speed_row(src) == speed_row(cand) else 4.0
    # soft preference for common molds; bury odd retail-only names
    name = cand.name.lower()
    junk = 0.0
    if any(x in name for x in ("power disc", "dx", "blizard", "blizzard", "#")):
        junk += 1.5
    popular = {
        "leopard3",
        "teebird",
        "teebird3",
        "roc3",
        "mako3",
        "wraith",
        "destroyer",
        "firebird",
        "valkyrie",
        "sidewinder",
        "roadrunner",
        "mamba",
        "tern",
        "pig",
        "rhyno",
        "aviarx3",
        "panther",
        "lion",
        "thunderbird",
        "eagle",
        "invictus",
        "xcaliber",
    }
    if name in popular:
        junk -= 0.8
    return 3.0 * dst + 2.0 * ds + 1.5 * df + 1.2 * dt + 0.5 * dg + band + junk


def b64_img(path: Path) -> str:
    if not path.exists():
        return ""
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{data}"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    by = load_innova()
    model = PathModel()

    # Lance bag (stated + remembered)
    bag_spec = [
        ("Aviar P&A", ["Aviar"]),
        ("AviarX3", ["Aviar X3"]),
        ("Atlas", []),
        ("Mako3", ["Mako"]),
        ("TeeBird3", ["Teebird3", "TeeBird3"]),
        ("Banshee", []),
        ("Firebird", []),
        ("Orc", []),
        ("Mystere", []),
        ("Archon", []),
    ]
    bag: list[Disc] = []
    for name, aliases in bag_spec:
        try:
            bag.append(disc_from_db(by, name, aliases))
        except KeyError:
            print("missing", name)

    # sort bag roughly putter -> distance, OS left-ish within class
    bag.sort(key=lambda d: (d.speed, d.stab))

    # catalog for gap fills (innova only)
    catalog = []
    for d in by.values():
        try:
            catalog.append(
                Disc(
                    name=d["name"],
                    speed=float(d["speed"]),
                    glide=float(d["glide"]),
                    turn=float(d["turn"]),
                    fade=float(d["fade"]),
                )
            )
        except (TypeError, ValueError):
            pass

    occupied, gaps, overlaps = analyze_bag(bag, catalog, model)
    ghost_picks = [g["pick"] for g in gaps if g["pick"] is not None]

    # Proof plates — discs clearly on classic Innova PNGs
    fairway_proof = []
    for n in ["Teebird", "TL3", "Banshee", "Eagle", "Leopard3", "Firebird", "Valkyrie", "Roadrunner", "Cheetah", "Leopard"]:
        try:
            fairway_proof.append(disc_from_db(by, n, ["TeeBird", "Teebird3"]))
        except KeyError:
            pass
    # clean fairway proof list manually preferred order matching chart left→right-ish OS→US
    fairway_names = [
        ("Teebird3", ["Teebird3"]),
        ("TL3", []),
        ("Banshee", []),
        ("Eagle", []),
        ("Teebird", ["TeeBird"]),
        ("Leopard3", []),
        ("Firebird", []),
        ("Valkyrie", []),
        ("Roadrunner", []),
        ("Leopard", []),
    ]
    fairway_proof = []
    for n, a in fairway_names:
        try:
            fairway_proof.append(disc_from_db(by, n, a))
        except KeyError:
            print("skip fairway", n)

    distance_names = [
        ("Destroyer", []),
        ("Wraith", []),
        ("Archon", []),
        ("Mystere", []),
        ("Mamba", []),
        ("Orc", []),
        ("Beast", []),
        ("Firebird", []),  # sometimes on distance plate edge
        ("Valkyrie", []),
        ("Sidewinder", []),
        ("Roadrunner", []),
    ]
    distance_proof = []
    for n, a in distance_names:
        try:
            distance_proof.append(disc_from_db(by, n, a))
        except KeyError:
            print("skip distance", n)

    mid_names = [
        ("Gator", []),
        ("Roc3", []),
        ("Atlas", []),
        ("Mako3", []),
        ("Manta", []),
        ("Wombat3", ["Wombat"]),
        ("Roc", []),
        ("Shark", []),
        ("Cobra", []),
        ("Wolf", []),
    ]
    mid_proof = []
    for n, a in mid_names:
        try:
            mid_proof.append(disc_from_db(by, n, a))
        except KeyError:
            print("skip mid", n)

    putt_names = [
        ("Pig", []),
        ("AviarX3", []),
        ("Rhyno", []),
        ("KC Pro Aviar", []),
        ("Aviar P&A", []),
        ("Classic Aviar", ["Aviar Classic"]),
        ("Birdie", []),
        ("Polecat", []),
    ]
    putt_proof = []
    for n, a in putt_names:
        try:
            putt_proof.append(disc_from_db(by, n, a))
        except KeyError:
            print("skip putt", n)

    bag_svg = plate_svg(bag, model, title="Your bag — shot shapes", width=980, height=540)
    bag_gaps_svg = plate_svg(
        bag,
        model,
        title="Your bag + missing shot shapes (dashed)",
        width=1100,
        height=560,
        ghost=ghost_picks,
    )
    fairway_svg = plate_svg(fairway_proof, model, title="WhichDisc fairway plate (proof set)", width=980, height=520)
    distance_svg = plate_svg(distance_proof, model, title="WhichDisc distance plate (proof set)", width=980, height=520)
    mid_svg = plate_svg(mid_proof, model, title="WhichDisc mid plate (proof set)", width=920, height=500)
    putt_svg = plate_svg(putt_proof, model, title="WhichDisc putt/approach plate (proof set)", width=900, height=480)

    # grid HTML
    rows_order = ["Putt/Approach", "Mid", "Fairway", "Control/Hybrid", "Distance"]
    cols_order = ["US", "STR", "OS", "VOS"]
    grid_cells = []
    for r in rows_order:
        for c in cols_order:
            key = (r, c)
            discs_here = occupied.get(key, [])
            gap = next((g for g in gaps if g["row"] == r and g["col"] == c), None)
            if discs_here:
                names = ", ".join(d.name for d in discs_here)
                cls = "filled overlap" if len(discs_here) > 1 else "filled"
                extra = f"<div class='mini'>{names}</div>"
            elif gap:
                pick = gap["pick"].name if gap["pick"] else "?"
                names = gap["label"]
                cls = "gap"
                extra = f"<div class='mini'>+ {pick}</div>"
            else:
                names = "—"
                cls = "empty"
                extra = ""
            grid_cells.append(
                f"<div class='cell {cls}'><div class='rc'>{r} · {c}</div><div class='lab'>{names}</div>{extra}</div>"
            )

    gap_rows = []
    for g in gaps:
        p = g["pick"]
        if not p:
            continue
        gap_rows.append(
            f"<tr><td>{g['label']}</td><td>{g['row']} / {g['col']}</td><td><strong>{p.name}</strong> <span class='mono'>{p.numbers}</span></td><td class='muted'>Innova fill</td></tr>"
        )

    bag_rows = []
    for d in bag:
        r, c = cell_for(d)
        bag_rows.append(
            f"<tr><td><strong>{d.name}</strong></td><td class='mono'>{d.numbers}</td><td>{r}</td><td>{c}</td><td>stab {d.stab:+.1f}</td></tr>"
        )

    ref_fairway = b64_img(REFS / "innova-fairway.png")
    ref_distance = b64_img(REFS / "innova-distance.png")
    ref_mid = b64_img(REFS / "innova-mid.png")
    ref_putt = b64_img(REFS / "innova-putt.png")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>WhichDisc — Prototype</title>
<style>
  :root {{
    --bg: #0b0f14;
    --panel: #141b24;
    --line: #243041;
    --text: #eef2f7;
    --muted: #8b95a8;
    --accent: #5eead4;
    --gap: #fbbf24;
    --fill: #34d399;
    --overlap: #f87171;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
    background: var(--bg); color: var(--text); line-height: 1.45;
  }}
  header {{
    padding: 28px 22px 10px; max-width: 1180px; margin: 0 auto;
  }}
  header h1 {{ margin: 0 0 6px; font-size: 28px; letter-spacing: -0.03em; }}
  header p {{ margin: 0; color: var(--muted); max-width: 70ch; }}
  nav {{
    display: flex; gap: 10px; flex-wrap: wrap; max-width: 1180px; margin: 14px auto 0; padding: 0 22px;
  }}
  nav a {{
    color: var(--accent); text-decoration: none; font-size: 13px; border: 1px solid #1f3340;
    padding: 6px 10px; border-radius: 999px; background: #0f1a20;
  }}
  main {{ max-width: 1180px; margin: 0 auto; padding: 18px 22px 60px; display: grid; gap: 22px; }}
  section {{
    background: var(--panel); border: 1px solid var(--line); border-radius: 16px; padding: 16px;
  }}
  section h2 {{ margin: 0 0 8px; font-size: 18px; }}
  section .sub {{ color: var(--muted); font-size: 13px; margin-bottom: 12px; }}
  .svgwrap {{ overflow-x: auto; border-radius: 12px; border: 1px solid var(--line); background: #0f1419; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
  th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); }}
  th {{ color: var(--muted); font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }}
  .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; color: #cbd5e1; }}
  .muted {{ color: var(--muted); }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 8px;
  }}
  .cell {{
    border: 1px solid var(--line); border-radius: 12px; padding: 10px; min-height: 78px;
    background: #0f1419;
  }}
  .cell .rc {{ font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }}
  .cell .lab {{ font-size: 13px; font-weight: 650; margin-top: 4px; }}
  .cell .mini {{ font-size: 11px; color: var(--muted); margin-top: 4px; }}
  .cell.filled {{ border-color: #14532d; box-shadow: inset 0 0 0 1px rgba(52,211,153,.15); }}
  .cell.filled .lab {{ color: var(--fill); }}
  .cell.overlap {{ border-color: #7f1d1d; }}
  .cell.overlap .lab {{ color: var(--overlap); }}
  .cell.gap {{ border-color: #78350f; border-style: dashed; }}
  .cell.gap .lab {{ color: var(--gap); }}
  .compare {{
    display: grid; grid-template-columns: 1fr; gap: 12px;
  }}
  @media (min-width: 960px) {{
    .compare.two {{ grid-template-columns: 1.1fr 0.9fr; align-items: start; }}
  }}
  .compare img {{ width: 100%; border-radius: 12px; border: 1px solid var(--line); background: #fff; }}
  .pillrow {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0 0; }}
  .pill {{
    font-size: 12px; padding: 5px 9px; border-radius: 999px; border: 1px solid var(--line); color: var(--muted);
  }}
  .pill strong {{ color: var(--text); font-weight: 650; }}
  footer {{ color: var(--muted); font-size: 12px; max-width: 1180px; margin: 0 auto; padding: 0 22px 40px; }}
</style>
</head>
<body>
<header>
  <h1>WhichDisc <span style="color:var(--muted);font-weight:600">prototype</span></h1>
  <p>Schematic shot shapes from flight numbers (Innova-calibrated grammar). Your bag plotted, gaps dashed, proof plates beside classic Innova charts.</p>
  <div class="pillrow">
    <div class="pill"><strong>{len(bag)}</strong> discs in bag</div>
    <div class="pill"><strong>{len(gaps)}</strong> shot gaps</div>
    <div class="pill"><strong>{len(overlaps)}</strong> overlap cells</div>
    <div class="pill">RHBH · tee at top</div>
  </div>
</header>
<nav>
  <a href="#bag">Your bag</a>
  <a href="#gaps">Gaps</a>
  <a href="#grid">Shot grid</a>
  <a href="#proof">Innova proof</a>
</nav>
<main>
  <section id="bag">
    <h2>Your bag flight chart</h2>
    <div class="sub">Aviar P&amp;A, AviarX3, Atlas, Mako3, TeeBird3, Banshee, Firebird, Orc, Mystere, Archon — solid lines = what you bag.</div>
    <div class="svgwrap">{bag_svg}</div>
    <div style="overflow-x:auto;margin-top:14px">
      <table>
        <thead><tr><th>Disc</th><th>Numbers</th><th>Row</th><th>Stability</th><th>Stab Σ</th></tr></thead>
        <tbody>
          {''.join(bag_rows)}
        </tbody>
      </table>
    </div>
  </section>

  <section id="gaps">
    <h2>Bag + missing shot shapes</h2>
    <div class="sub">Dashed paths = recommended Innova fills for empty shot cells (not random hot molds). Same chart grammar.</div>
    <div class="svgwrap">{bag_gaps_svg}</div>
    <div style="overflow-x:auto;margin-top:14px">
      <table>
        <thead><tr><th>Missing shot</th><th>Cell</th><th>Suggested disc</th><th></th></tr></thead>
        <tbody>
          {''.join(gap_rows) if gap_rows else '<tr><td colspan="4">No gaps on required grid.</td></tr>'}
        </tbody>
      </table>
    </div>
  </section>

  <section id="grid">
    <h2>Shot-shape grid</h2>
    <div class="sub">Green = covered · Red = overlap (two discs, one job) · Amber dashed = gap</div>
    <div class="grid">
      {''.join(grid_cells)}
    </div>
  </section>

  <section id="proof">
    <h2>Innova proof (frame of mind)</h2>
    <div class="sub">Left/top: WhichDisc generated plate. Right/bottom: classic Innova characteristic chart. Tune target = family relationships, not pixel clone.</div>

    <h3 style="margin:18px 0 8px;font-size:15px;color:var(--muted)">Fairway</h3>
    <div class="compare two">
      <div class="svgwrap">{fairway_svg}</div>
      <div>{'<img alt="Innova fairway chart" src="'+ref_fairway+'"/>' if ref_fairway else '<p class="muted">ref missing</p>'}</div>
    </div>

    <h3 style="margin:18px 0 8px;font-size:15px;color:var(--muted)">Distance</h3>
    <div class="compare two">
      <div class="svgwrap">{distance_svg}</div>
      <div>{'<img alt="Innova distance chart" src="'+ref_distance+'"/>' if ref_distance else '<p class="muted">ref missing</p>'}</div>
    </div>

    <h3 style="margin:18px 0 8px;font-size:15px;color:var(--muted)">Mid</h3>
    <div class="compare two">
      <div class="svgwrap">{mid_svg}</div>
      <div>{'<img alt="Innova mid chart" src="'+ref_mid+'"/>' if ref_mid else '<p class="muted">ref missing</p>'}</div>
    </div>

    <h3 style="margin:18px 0 8px;font-size:15px;color:var(--muted)">Putt / approach</h3>
    <div class="compare two">
      <div class="svgwrap">{putt_svg}</div>
      <div>{'<img alt="Innova putt chart" src="'+ref_putt+'"/>' if ref_putt else '<p class="muted">ref missing</p>'}</div>
    </div>
  </section>
</main>
<footer>
  WhichDisc prototype · local schematic paths from S/G/T/F · Innova refs used only for calibration / side-by-side proof · not affiliated with Innova.
</footer>
</body>
</html>
"""
    out_path = OUT / "index.html"
    out_path.write_text(html)
    print(f"wrote {out_path}")
    print("BAG:")
    for d in bag:
        print(f"  {d.name:12} {d.numbers:12} {speed_row(d):16} {stab_col(d)}")
    print("GAPS:")
    for g in gaps:
        p = g["pick"]
        print(f"  {g['label']:28} -> {p.name if p else '?'} {p.numbers if p else ''}")
    print("OVERLAPS:")
    for k, v in overlaps.items():
        print(f"  {k}: {[d.name for d in v]}")


if __name__ == "__main__":
    main()
