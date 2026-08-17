#!/usr/bin/env python3
"""discwhich bag field grid — deterministic 14×9 placement + mobile field visual.

Grid (LOCKED):
  Rows: 14  → speed 1 (nearest tee / bottom) … speed 14 (farthest / top)
  Cols:  9  → -4 -3 -2 -1  0  1  2  3  4
              left=OS/fade …… center …… right=flip/US   (RHBH, behind thrower)

  row = clamp(round(speed), 1, 14)
  col = clamp(round((-turn) * 2 - fade), -4, +4)

Glide = carry tag only. Path engine separate.
"""

from __future__ import annotations

import html
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Disc:
    label: str
    mold: str
    speed: float
    glide: float
    turn: float
    fade: float
    note: str = ""

    @property
    def numbers(self) -> str:
        def fmt(v: float) -> str:
            return str(int(v)) if float(v).is_integer() else f"{v:g}"

        return f"{fmt(self.speed)}/{fmt(self.glide)}/{fmt(self.turn)}/{fmt(self.fade)}"


def clamp_int(v: float, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(round(v))))


def row_for(speed: float) -> int:
    return clamp_int(speed, 1, 14)


def col_for(turn: float, fade: float) -> int:
    # Flight numbers: neg turn (US) → neg col → RIGHT; pos fade (OS) → pos col → LEFT
    raw = turn * 2 + fade
    return clamp_int(raw, -4, 4)


def carry_tag(glide: float) -> str:
    if glide <= 2:
        return "short"
    if glide <= 4:
        return "normal"
    return "long"


def stab_class(col: int) -> str:
    # col+ = OS/left, col- = US/right
    if col >= 3:
        return "vos"
    if col >= 1:
        return "os"
    if col == 0:
        return "str"
    if col >= -2:
        return "soft-us"
    return "us"


BAG: list[Disc] = [
    Disc("Aviar", "Aviar P&A", 2, 3, 0, 1, "putter proxy"),
    Disc("Aviar X3", "AviarX3", 3, 2, 0, 3),
    Disc("Atlas", "Atlas", 5, 4, 0, 1),
    Disc("Mako3", "Mako3", 5, 5, 0, 0),
    Disc("TB3", "Teebird3", 8, 4, 0, 2),
    Disc("Banshee", "Banshee", 7, 3, 0, 3),
    Disc("Firebird", "Firebird", 9, 3, 0, 4),
    Disc("Orc", "Orc", 10, 4, -1, 3),
    Disc("Archon", "Archon", 11, 5, -2, 2),
    Disc("Mystere", "Mystere", 11, 6, -2, 2),
]


def place(d: Disc) -> dict:
    r = row_for(d.speed)
    c = col_for(d.turn, d.fade)
    return {
        "label": d.label,
        "mold": d.mold,
        "numbers": d.numbers,
        "speed": d.speed,
        "glide": d.glide,
        "turn": d.turn,
        "fade": d.fade,
        "row": r,
        "col": c,
        "carry": carry_tag(d.glide),
        "raw_col": d.turn * 2 + d.fade,
        "stab": stab_class(c),
        "note": d.note,
    }


def build_html(placed: list[dict]) -> str:
    # stack offsets when multiple discs share a cell
    cell_counts: dict[tuple[int, int], int] = defaultdict(int)
    marks = []
    for p in sorted(placed, key=lambda x: (x["row"], x["col"], x["label"])):
        key = (p["row"], p["col"])
        stack_i = cell_counts[key]
        cell_counts[key] += 1
        # CSS grid: col 1..9 = -4..+4; row 1..14 = speed 14..1 (top=far)
        css_col = 5 - p["col"]  # +4→1 (left) … -4→9 (right)
        css_row = 15 - p["row"]  # speed 14→1, speed 1→14
        marks.append({**p, "css_col": css_col, "css_row": css_row, "stack": stack_i})

    marks_json = json.dumps(marks)
    log_rows = []
    for p in sorted(placed, key=lambda x: (-x["row"], x["col"], x["label"])):
        log_rows.append(
            "<tr>"
            f"<td>{html.escape(p['label'])}</td>"
            f"<td class='mono'>{html.escape(p['numbers'])}</td>"
            f"<td class='mono'>{p['row']}</td>"
            f"<td class='mono'>{p['col']:+d}</td>"
            f"<td class='mono'>{p['raw_col']:g}</td>"
            "</tr>"
        )

    tb3 = next(p for p in placed if p["label"] == "TB3")
    x3 = next(p for p in placed if p["label"] == "Aviar X3")
    av = next(p for p in placed if p["label"] == "Aviar")

    mark_html = []
    for m in marks:
        # slight stack nudge inside shared cells
        nudge = f" style='--stack:{m['stack']}'" if m["stack"] else ""
        mark_html.append(
            f"<button type='button' class='mark {html.escape(m['stab'])}' "
            f"data-row='{m['row']}' data-col='{m['col']}' "
            f"style='grid-column:{m['css_col']};grid-row:{m['css_row']};--stack:{m['stack']}' "
            f"aria-label='{html.escape(m['label'])} {html.escape(m['numbers'])} row {m['row']} col {m['col']:+d}'>"
            f"<span class='dot'></span>"
            f"<span class='label'>"
            f"<span class='name'>{html.escape(m['label'])}</span>"
            f"<span class='nums'>{html.escape(m['numbers'])}</span>"
            f"</span>"
            f"</button>"
        )

    # speed rail labels (right side) — only a few for phone clarity
    speed_labels = []
    for spd in (14, 12, 10, 8, 6, 4, 2, 1):
        css_row = 15 - spd
        speed_labels.append(
            f"<div class='spd' style='grid-row:{css_row}'>{spd}</div>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"/>
<meta name="theme-color" content="#0b0f14"/>
<meta name="apple-mobile-web-app-capable" content="yes"/>
<title>discwhich — bag field</title>
<style>
  :root {{
    --bg: #0b0f14;
    --text: #f2f5f8;
    --muted: #9aa3b2;
    --faint: #6a7382;
    --accent: #5eead4;
    --line: rgba(255,255,255,.08);
    --safe-t: env(safe-area-inset-top, 0px);
    --safe-b: env(safe-area-inset-bottom, 0px);
    --safe-l: env(safe-area-inset-left, 0px);
    --safe-r: env(safe-area-inset-right, 0px);
  }}
  * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
  html, body {{ margin: 0; padding: 0; background: var(--bg); color: var(--text); }}
  body {{
    font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
    min-height: 100dvh;
    padding: calc(12px + var(--safe-t)) calc(12px + var(--safe-r)) calc(16px + var(--safe-b)) calc(12px + var(--safe-l));
  }}
  a {{ color: var(--accent); text-decoration: none; }}

  .top {{
    max-width: 480px;
    margin: 0 auto 10px;
  }}
  .eyebrow {{
    color: var(--accent);
    font-size: 10px;
    font-weight: 800;
    letter-spacing: .12em;
    text-transform: uppercase;
  }}
  h1 {{
    margin: 4px 0 4px;
    font-size: 1.35rem;
    letter-spacing: -.02em;
    line-height: 1.15;
  }}
  .sub {{
    margin: 0;
    color: var(--muted);
    font-size: 13px;
    line-height: 1.4;
  }}
  .chips {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 10px;
  }}
  .chip {{
    font-size: 11px;
    color: var(--muted);
    border: 1px solid #243041;
    background: #121820;
    border-radius: 999px;
    padding: 5px 9px;
  }}
  .chip b {{ color: var(--text); font-weight: 700; }}

  /* ===== PHONE FIELD ===== */
  .stage {{
    max-width: 480px;
    margin: 0 auto;
  }}
  .axis-x {{
    display: grid;
    grid-template-columns: 18px 1fr 18px;
    gap: 0;
    align-items: center;
    margin-bottom: 4px;
    padding: 0 2px;
  }}
  .axis-x .mid {{
    display: grid;
    grid-template-columns: repeat(9, 1fr);
    text-align: center;
    font-size: 10px;
    font-weight: 750;
    color: var(--faint);
    font-variant-numeric: tabular-nums;
  }}
  .axis-x .mid span.z {{ color: #f0d78c; }}
  .axis-x .end {{
    font-size: 9px;
    font-weight: 800;
    letter-spacing: .04em;
    text-transform: uppercase;
    color: rgba(242,245,248,.28);
    writing-mode: vertical-rl;
    transform: rotate(180deg);
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  .axis-x .end.r {{ transform: none; }}

  .field-wrap {{
    position: relative;
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid #1c3a27;
    box-shadow: 0 16px 40px rgba(0,0,0,.45);
    background:
      radial-gradient(ellipse 90% 40% at 50% 100%, rgba(0,0,0,.4), transparent 70%),
      radial-gradient(ellipse 80% 30% at 50% 0%, rgba(255,255,255,.04), transparent 60%),
      repeating-linear-gradient(90deg, #14351f 0 28px, #12311c 28px 56px),
      #12301c;
  }}

  /* 9 cols × 14 speed rows + tee band */
  .field {{
    display: grid;
    grid-template-columns: repeat(9, minmax(0, 1fr));
    grid-template-rows: repeat(14, minmax(0, 1fr));
    /* phone-first height: tall enough to separate speeds, still one screen-ish */
    height: min(72dvh, 640px);
    min-height: 520px;
    width: 100%;
    position: relative;
    padding: 8px 4px 0;
  }}

  /* center corridor */
  .field::before {{
    content: "";
    position: absolute;
    left: calc(50% - 0.5px);
    top: 6px;
    bottom: 52px;
    width: 1px;
    background: linear-gradient(180deg, transparent, rgba(240,215,140,.22), transparent);
    pointer-events: none;
    z-index: 0;
  }}

  /* faint row lines every speed */
  .gridlines {{
    position: absolute;
    inset: 8px 0 52px 0;
    display: grid;
    grid-template-rows: repeat(14, 1fr);
    pointer-events: none;
    z-index: 0;
  }}
  .gridlines i {{
    border-bottom: 1px solid rgba(255,255,255,.04);
  }}

  .spd-rail {{
    position: absolute;
    right: 4px;
    top: 8px;
    bottom: 52px;
    width: 16px;
    display: grid;
    grid-template-rows: repeat(14, 1fr);
    pointer-events: none;
    z-index: 1;
  }}
  .spd {{
    font-size: 9px;
    font-weight: 700;
    color: rgba(242,245,248,.28);
    display: flex;
    align-items: center;
    justify-content: flex-end;
    font-variant-numeric: tabular-nums;
  }}

  .far-tag {{
    position: absolute;
    top: 8px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 9px;
    font-weight: 800;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: rgba(242,245,248,.22);
    z-index: 1;
    pointer-events: none;
  }}

  /* disc marks */
  .mark {{
    appearance: none;
    -webkit-appearance: none;
    border: 0;
    background: transparent;
    padding: 0;
    margin: 0;
    position: relative;
    z-index: 2;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-width: 0;
    min-height: 0;
    /* stack shared cells */
    transform: translateY(calc(var(--stack, 0) * -10px)) translateX(calc(var(--stack, 0) * 6px));
    cursor: pointer;
  }}
  .mark .dot {{
    width: clamp(22px, 7.2vw, 30px);
    height: clamp(22px, 7.2vw, 30px);
    border-radius: 50%;
    border: 2px solid rgba(255,255,255,.28);
    box-shadow:
      0 6px 14px rgba(0,0,0,.4),
      inset 0 1px 0 rgba(255,255,255,.2);
  }}
  .mark .label {{
    margin-top: 3px;
    text-align: center;
    line-height: 1.05;
    max-width: 100%;
    padding: 0 1px;
  }}
  .mark .name {{
    display: block;
    font-size: clamp(9px, 2.7vw, 11px);
    font-weight: 800;
    letter-spacing: -.01em;
    color: var(--text);
    text-shadow: 0 1px 3px rgba(0,0,0,.75);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 4.8rem;
  }}
  .mark .nums {{
    display: block;
    font-size: clamp(8px, 2.3vw, 10px);
    font-weight: 700;
    color: var(--accent);
    font-variant-numeric: tabular-nums;
    text-shadow: 0 1px 2px rgba(0,0,0,.7);
  }}

  .mark.vos .dot {{ background: radial-gradient(circle at 35% 30%, #c45a5a, #6b1d1d); border-color: rgba(248,113,113,.65); }}
  .mark.os .dot {{ background: radial-gradient(circle at 35% 30%, #d4894a, #6b3a14); border-color: rgba(251,146,60,.6); }}
  .mark.str .dot {{ background: radial-gradient(circle at 35% 30%, #c6b56a, #5c5224); border-color: rgba(240,215,140,.55); }}
  .mark.soft-us .dot {{ background: radial-gradient(circle at 35% 30%, #4fae9e, #1a5c52); border-color: rgba(45,212,191,.5); }}
  .mark.us .dot {{ background: radial-gradient(circle at 35% 30%, #3dcfb8, #0f5c50); border-color: rgba(94,234,212,.65); }}

  .mark:active .dot, .mark:focus-visible .dot {{
    transform: scale(1.08);
    outline: none;
  }}
  .mark:focus-visible {{ outline: none; }}
  .mark.is-active {{ z-index: 5; }}
  .mark.is-active .dot {{
    box-shadow: 0 0 0 3px rgba(94,234,212,.35), 0 8px 18px rgba(0,0,0,.45);
  }}

  /* tee band */
  .tee {{
    position: absolute;
    left: 0; right: 0; bottom: 0;
    height: 52px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    padding-bottom: 8px;
    background: linear-gradient(180deg, transparent, rgba(0,0,0,.35));
    border-top: 1px solid rgba(255,255,255,.06);
    z-index: 3;
    pointer-events: none;
  }}
  .tee .pad {{
    width: 52px;
    height: 14px;
    border-radius: 6px;
    background: rgba(255,255,255,.1);
    border: 1px solid rgba(255,255,255,.16);
    margin-bottom: 4px;
  }}
  .tee .you {{
    font-size: 9px;
    font-weight: 800;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: rgba(242,245,248,.45);
  }}

  /* selected sheet */
  .sheet {{
    max-width: 480px;
    margin: 12px auto 0;
    border: 1px solid #243041;
    background: #121820;
    border-radius: 14px;
    padding: 12px 14px;
    min-height: 72px;
  }}
  .sheet .hint {{
    color: var(--faint);
    font-size: 12px;
  }}
  .sheet .title {{
    font-size: 16px;
    font-weight: 800;
    letter-spacing: -.01em;
  }}
  .sheet .meta {{
    margin-top: 4px;
    color: var(--muted);
    font-size: 13px;
    line-height: 1.4;
  }}
  .sheet .meta b {{ color: var(--text); }}
  .sheet .nums {{
    color: var(--accent);
    font-weight: 750;
    font-variant-numeric: tabular-nums;
  }}

  details.log {{
    max-width: 480px;
    margin: 14px auto 0;
    border: 1px solid #243041;
    background: #10161d;
    border-radius: 14px;
    padding: 10px 12px;
  }}
  details.log summary {{
    cursor: pointer;
    font-size: 12px;
    font-weight: 750;
    color: var(--muted);
    letter-spacing: .04em;
    text-transform: uppercase;
    list-style: none;
  }}
  details.log summary::-webkit-details-marker {{ display: none; }}
  table.dbg {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
    font-size: 12px;
  }}
  table.dbg th, table.dbg td {{
    text-align: left;
    padding: 6px 4px;
    border-bottom: 1px solid #243041;
  }}
  table.dbg th {{
    color: var(--faint);
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: .06em;
  }}
  .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 11px; }}

  .foot {{
    max-width: 480px;
    margin: 14px auto 0;
    color: var(--faint);
    font-size: 11px;
    line-height: 1.4;
  }}

  /* wider phones / desktop: roomier field */
  @media (min-width: 520px) {{
    .top, .stage, .sheet, details.log, .foot {{ max-width: 560px; }}
    .field {{ height: min(75dvh, 720px); min-height: 600px; }}
    .mark .name {{ max-width: 5.5rem; font-size: 12px; }}
    .mark .nums {{ font-size: 11px; }}
    .mark .dot {{ width: 32px; height: 32px; }}
  }}
</style>
</head>
<body>
  <div class="top">
    <div class="eyebrow">discwhich · 14×9 field</div>
    <h1>Your bag on the fairway</h1>
    <p class="sub">Phone layout. Tee at bottom. Farther = higher. Left = + OS/fade. Right = − flip/US. Flight-number axis. Same math every disc.</p>
    <div class="chips">
      <div class="chip">TB3 <b>{tb3['row']},{tb3['col']:+d}</b></div>
      <div class="chip">X3 <b>{x3['col']:+d}</b> · Aviar <b>{av['col']:+d}</b></div>
      <div class="chip"><a href="./">main</a></div>
    </div>
  </div>

  <div class="stage">
    <div class="axis-x" aria-hidden="true">
      <div class="end">OS +</div>
      <div class="mid">
        <span>+4</span><span>+3</span><span>+2</span><span>+1</span><span class="z">0</span><span>−1</span><span>−2</span><span>−3</span><span>−4</span>
      </div>
      <div class="end r">US −</div>
    </div>

    <div class="field-wrap">
      <div class="far-tag">farther</div>
      <div class="field" id="field" aria-label="Bag field grid, 14 speeds by 9 stability columns">
        <div class="gridlines" aria-hidden="true">{''.join('<i></i>' for _ in range(14))}</div>
        <div class="spd-rail" aria-hidden="true">{''.join(speed_labels)}</div>
        {''.join(mark_html)}
        <div class="tee"><div class="pad"></div><div class="you">you · tee</div></div>
      </div>
    </div>
  </div>

  <div class="sheet" id="sheet" aria-live="polite">
    <div class="hint">Tap a disc</div>
  </div>

  <details class="log">
    <summary>Placement log · formula</summary>
    <p class="sub" style="margin:8px 0 0">
      <span class="mono">row = clamp(round(speed),1,14)</span><br/>
      <span class="mono">col = clamp(round(turn*2 + fade),-4,+4)</span><br/>
      <span class="mono">chart: + left (OS) · − right (US)</span>
    </p>
    <table class="dbg">
      <thead><tr><th>Disc</th><th>Numbers</th><th>Row</th><th>Col</th><th>Raw</th></tr></thead>
      <tbody>{''.join(log_rows)}</tbody>
    </table>
  </details>

  <p class="foot">Generated by build_bag_grid.py · not hand-placed · discwhich</p>

<script>
const DISCS = {marks_json};
const sheet = document.getElementById('sheet');
const marks = [...document.querySelectorAll('.mark')];

function show(p) {{
  marks.forEach(m => m.classList.toggle('is-active',
    m.dataset.row === String(p.row) && m.dataset.col === String(p.col) && m.querySelector('.name')?.textContent === p.label
  ));
  sheet.innerHTML = `
    <div class="title">${{p.label}}</div>
    <div class="meta">
      <span class="nums">${{p.numbers}}</span><br/>
      cell <b>${{p.row}}, ${{p.col >= 0 ? '+' : ''}}${{p.col}}</b>
      · speed row ${{p.row}}
      · ${{p.carry}} carry
      ${{p.note ? ' · ' + p.note : ''}}
    </div>`;
}}

marks.forEach(btn => {{
  btn.addEventListener('click', () => {{
    const label = btn.querySelector('.name').textContent;
    const p = DISCS.find(d => d.label === label);
    if (p) show(p);
  }});
}});

// default select nearest putter
const aviar = DISCS.find(d => d.label === 'Aviar');
if (aviar) show(aviar);
</script>
</body>
</html>
"""


def main() -> None:
    placed = [place(d) for d in BAG]
    out = Path(__file__).resolve().parent / "bag-grid.html"
    out.write_text(build_html(placed), encoding="utf-8")
    print("wrote", out)
    for p in sorted(placed, key=lambda x: (-x["row"], x["col"])):
        print(f"{p['label']:12} {p['numbers']:12} -> ({p['row']}, {p['col']:+d})")


if __name__ == "__main__":
    main()
