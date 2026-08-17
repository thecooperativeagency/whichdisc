#!/usr/bin/env python3
"""discwhich bag field grid — deterministic 14×9 placement.

Grid (LOCKED trial):
  Rows: 14  → speed 1 (nearest tee / bottom) … speed 14 (farthest / top)
  Cols:  9  → -4 -3 -2 -1  0  1  2  3  4
              left=OS/fade …… center …… right=flip/US   (RHBH, behind thrower)

Column formula (foolproof, no hand placement):
  col = clamp(round((-turn) * 2 - fade), -4, +4)

  Why:
    - negative turn (US) → positive col (right / flip)
    - high fade (OS)     → negative col (left / fade)
    - Aviar 0/1 → -1; Aviar X3 0/3 → -3  (X3 left of Aviar) ✓

Row formula:
  row_speed = clamp(round(speed), 1, 14)
  (half-speeds round to nearest int)

Glide does NOT move the cell in v1 — only a carry tag for labels.
Path engine stays separate.
"""

from __future__ import annotations

import html
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
    """Speed 1..14. One row per speed number."""
    return clamp_int(speed, 1, 14)


def col_for(turn: float, fade: float) -> int:
    """Stability column -4..+4. Deterministic from turn + fade only."""
    # US (neg turn) pushes RIGHT (+); fade pushes LEFT (−)
    raw = (-turn) * 2 - fade
    return clamp_int(raw, -4, 4)


def carry_tag(glide: float) -> str:
    if glide <= 2:
        return "short"
    if glide <= 4:
        return "normal"
    return "long"


# Lance bag — stock numbers (Aviar = Aviar P&A proxy)
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
        "disc": d,
        "row": r,
        "col": c,
        "carry": carry_tag(d.glide),
        "raw_col": (-d.turn) * 2 - d.fade,
    }


def build_html(placed: list[dict]) -> str:
    cols = list(range(-4, 5))  # -4..4
    rows = list(range(14, 0, -1))  # top=14 far, bottom=1 near

    # cell → discs
    cells: dict[tuple[int, int], list[dict]] = {}
    for p in placed:
        cells.setdefault((p["row"], p["col"]), []).append(p)

    # debug table rows
    dbg_rows = []
    for p in sorted(placed, key=lambda x: (-x["row"], x["col"], x["disc"].label)):
        d = p["disc"]
        dbg_rows.append(
            "<tr>"
            f"<td>{html.escape(d.label)}</td>"
            f"<td class='mono'>{html.escape(d.numbers)}</td>"
            f"<td class='mono'>{p['row']}</td>"
            f"<td class='mono'>{p['col']:+d}</td>"
            f"<td class='mono'>{p['raw_col']:g}</td>"
            f"<td>{p['carry']}</td>"
            f"<td class='mute'>{html.escape(d.note)}</td>"
            "</tr>"
        )

    # grid body
    body_rows = []
    for r in rows:
        tds = [f"<th class='rowh'><span>{r}</span></th>"]
        for c in cols:
            items = cells.get((r, c), [])
            if not items:
                tds.append(f"<td class='cell empty' data-r='{r}' data-c='{c}'></td>")
                continue
            overlap = " overlap" if len(items) > 1 else ""
            chips = []
            for p in items:
                d = p["disc"]
                chips.append(
                    "<div class='disc'>"
                    f"<div class='name'>{html.escape(d.label)}</div>"
                    f"<div class='nums'>{html.escape(d.numbers)}</div>"
                    "</div>"
                )
            tds.append(
                f"<td class='cell filled{overlap}' data-r='{r}' data-c='{c}'>"
                + "".join(chips)
                + "</td>"
            )
        # thrower marker on row 1 center feels wrong in table — separate under grid
        body_rows.append("<tr>" + "".join(tds) + "</tr>")

    col_headers = "".join(
        f"<th class='colh{' zero' if c == 0 else ''}'>{c:+d}</th>" if c != 0 else "<th class='colh zero'>0</th>"
        for c in cols
    )

    tb3 = next(p for p in placed if p["disc"].label == "TB3")
    x3 = next(p for p in placed if p["disc"].label == "Aviar X3")
    av = next(p for p in placed if p["disc"].label == "Aviar")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>discwhich — 14×9 bag grid</title>
<style>
  :root {{
    --bg: #0b0f14;
    --panel: #121a22;
    --line: #243041;
    --text: #eef2f7;
    --muted: #8b95a8;
    --faint: #5c677a;
    --accent: #5eead4;
    --os: #fb923c;
    --us: #2dd4bf;
    --zero: #f0d78c;
    --fill: #1a2733;
    --overlap: #3a1d24;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
  }}
  a {{ color: var(--accent); text-decoration: none; }}
  header, main, footer {{ max-width: 1100px; margin: 0 auto; padding: 0 16px; }}
  header {{ padding-top: 20px; }}
  .eyebrow {{ color: var(--accent); font-size: 11px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; }}
  h1 {{ margin: 6px 0; font-size: 24px; letter-spacing: -.02em; }}
  .sub {{ color: var(--muted); font-size: 14px; line-height: 1.5; max-width: 70ch; }}
  .sub code {{ color: #d9e2ec; font-size: 12.5px; }}
  .meta {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0 8px; }}
  .chip {{ border: 1px solid var(--line); background: var(--panel); color: var(--muted); font-size: 12px; padding: 5px 10px; border-radius: 999px; }}
  .chip strong {{ color: var(--text); }}
  .ok {{ color: #6ee7b7; }}
  .warn {{ color: #fbbf24; }}

  .field-shell {{
    margin: 14px 0 8px;
    border: 1px solid #1e3a28;
    border-radius: 16px;
    overflow: auto;
    background:
      linear-gradient(180deg, rgba(12,28,18,.55), rgba(10,16,12,.92)),
      repeating-linear-gradient(90deg, #12301c 0 36px, #102b19 36px 72px);
    box-shadow: 0 18px 50px rgba(0,0,0,.4);
  }}
  table.g {{
    width: 100%;
    min-width: 860px;
    border-collapse: collapse;
    table-layout: fixed;
  }}
  .corner {{
    width: 44px;
    background: rgba(0,0,0,.35);
    border-bottom: 1px solid rgba(255,255,255,.08);
    border-right: 1px solid rgba(255,255,255,.08);
  }}
  th.colh {{
    position: sticky; top: 0;
    z-index: 2;
    background: rgba(8,14,12,.92);
    color: var(--muted);
    font-size: 11px;
    font-weight: 750;
    padding: 10px 4px;
    border-bottom: 1px solid rgba(255,255,255,.1);
    text-align: center;
  }}
  th.colh.zero {{ color: var(--zero); }}
  th.rowh {{
    width: 44px;
    background: rgba(8,14,12,.75);
    color: var(--faint);
    font-size: 11px;
    font-weight: 700;
    text-align: center;
    border-right: 1px solid rgba(255,255,255,.08);
    border-bottom: 1px solid rgba(255,255,255,.05);
  }}
  th.rowh span {{
    display: inline-block;
    min-width: 1.2em;
  }}
  td.cell {{
    height: 52px;
    border-right: 1px solid rgba(255,255,255,.045);
    border-bottom: 1px solid rgba(255,255,255,.045);
    vertical-align: middle;
    padding: 3px;
    text-align: center;
  }}
  /* center column emphasis */
  td.cell[data-c="0"], th.colh.zero {{
    box-shadow: inset 0 0 0 1px rgba(240,215,140,.08);
  }}
  td.cell.empty {{ background: transparent; }}
  td.cell.filled {{
    background: rgba(20, 36, 28, .88);
  }}
  td.cell.overlap {{
    background: var(--overlap);
  }}
  .disc {{
    display: inline-block;
    min-width: 72px;
    margin: 1px;
    padding: 4px 6px 3px;
    border-radius: 8px;
    background: rgba(0,0,0,.35);
    border: 1px solid rgba(255,255,255,.12);
  }}
  .disc .name {{
    font-size: 11px;
    font-weight: 750;
    line-height: 1.15;
  }}
  .disc .nums {{
    font-size: 10px;
    font-weight: 650;
    color: var(--accent);
    font-variant-numeric: tabular-nums;
  }}

  .axis {{
    display: flex;
    justify-content: space-between;
    padding: 8px 48px 0 52px;
    color: rgba(238,242,247,.35);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .12em;
    text-transform: uppercase;
  }}
  .thrower {{
    text-align: center;
    padding: 10px 0 14px;
    color: rgba(238,242,247,.5);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .14em;
    text-transform: uppercase;
  }}
  .thrower .pad {{
    width: 56px; height: 16px; margin: 0 auto 6px;
    border-radius: 6px;
    background: rgba(255,255,255,.08);
    border: 1px solid rgba(255,255,255,.14);
  }}

  section.card {{
    margin: 18px 0;
    padding: 14px 16px;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 14px;
  }}
  section.card h2 {{
    margin: 0 0 8px;
    font-size: 12px;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--muted);
  }}
  section.card p, section.card li {{
    color: var(--text);
    font-size: 13.5px;
    line-height: 1.5;
  }}
  section.card ul {{ margin: 0; padding-left: 18px; }}
  .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; }}
  .mute {{ color: var(--muted); }}
  table.dbg {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
  }}
  table.dbg th, table.dbg td {{
    text-align: left;
    padding: 7px 8px;
    border-bottom: 1px solid var(--line);
  }}
  table.dbg th {{ color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: .06em; }}
  footer {{ padding: 8px 16px 32px; color: var(--faint); font-size: 12px; }}
</style>
</head>
<body>
<header>
  <div class="eyebrow">discwhich · deterministic grid</div>
  <h1>14 × 9 bag grid</h1>
  <p class="sub">
    Not hand-placed. Every disc goes through the same functions.<br/>
    <code>row = clamp(round(speed), 1, 14)</code><br/>
    <code>col = clamp(round((-turn) * 2 - fade), -4, +4)</code><br/>
    Top of page = farther (speed 14). Bottom = tee / speed 1.
    Left = OS/fade (−). Right = flip/US (+). Center column = 0.
  </p>
  <div class="meta">
    <div class="chip"><strong>logic</strong> not guesses</div>
    <div class="chip">TB3 → row <strong>{tb3['row']}</strong>, col <strong>{tb3['col']:+d}</strong></div>
    <div class="chip">X3 col <strong>{x3['col']:+d}</strong> · Aviar col <strong>{av['col']:+d}</strong> <span class="ok">X3 left ✓</span></div>
    <div class="chip"><a href="./">main prototype</a></div>
  </div>
</header>

<main>
  <div class="axis">
    <span>← OS / fade (−4)</span>
    <span>0 straight</span>
    <span>flip / US (+4) →</span>
  </div>
  <div class="field-shell">
    <table class="g" aria-label="14 by 9 disc bag grid">
      <thead>
        <tr>
          <th class="corner" title="speed"></th>
          {col_headers}
        </tr>
      </thead>
      <tbody>
        {''.join(body_rows)}
      </tbody>
    </table>
    <div class="thrower">
      <div class="pad"></div>
      you · tee · speed rises away from you
    </div>
  </div>

  <section class="card">
    <h2>Is TB3 correct?</h2>
    <p>
      <strong>TB3 8/4/0/2</strong> →
      row <strong class="mono">{tb3['row']}</strong>,
      col <strong class="mono">{tb3['col']:+d}</strong>
      (raw <span class="mono">{tb3['raw_col']:g}</span>).
    </p>
    <p class="mute" style="margin-top:8px">
      Speed 8 fairway row — correct class. Turn 0 / fade 2 is a mild OS workhorse, so it sits
      one step left of center (−2), not on 0. That is what the formula says; if you want TeeBird-class
      on 0, we change the formula (e.g. fade weight), not the TB3 coordinates by hand.
    </p>
  </section>

  <section class="card">
    <h2>Plug-in contract for discwhich</h2>
    <ul>
      <li><strong>Input:</strong> speed, glide, turn, fade (glide unused for cell id v1)</li>
      <li><strong>Output:</strong> <span class="mono">{{ row: 1..14, col: -4..+4 }}</span></li>
      <li><strong>No</strong> mold-name special cases in placement</li>
      <li>Path drawing = separate algorithm; does not assign cells</li>
      <li>Source: <span class="mono">build_bag_grid.py</span> → regenerate this page</li>
    </ul>
  </section>

  <section class="card">
    <h2>Placement log (all discs)</h2>
    <table class="dbg">
      <thead>
        <tr>
          <th>Disc</th><th>Numbers</th><th>Row</th><th>Col</th><th>Raw col</th><th>Carry</th><th>Note</th>
        </tr>
      </thead>
      <tbody>
        {''.join(dbg_rows)}
      </tbody>
    </table>
  </section>
</main>

<footer>
  Generated by build_bag_grid.py · discwhich · not hand-placed
</footer>
</body>
</html>
"""


def main() -> None:
    placed = [place(d) for d in BAG]
    out = Path(__file__).resolve().parent / "bag-grid.html"
    out.write_text(build_html(placed), encoding="utf-8")

    print("wrote", out)
    print("row = speed | col = clamp(round((-turn)*2 - fade), -4, 4)")
    print(f"{'disc':12} {'nums':14} {'row':>4} {'col':>4} {'raw':>6}")
    for p in sorted(placed, key=lambda x: (-x["row"], x["col"])):
        d = p["disc"]
        print(f"{d.label:12} {d.numbers:14} {p['row']:4d} {p['col']:+4d} {p['raw_col']:6g}")


if __name__ == "__main__":
    main()
