# discwhich — Working notes (saved)

Last updated: 2026-08-15  
Prototype: https://thecooperativeagency.github.io/whichdisc/  
Repo: https://github.com/thecooperativeagency/whichdisc  
Domain intent: buy **discwhich.com** (available). **discwhich.com** taken (dead site thru 2027).

---

## Name
- Product: **discwhich**
- Nickname: the Whicher (secondary)
- Public URL candidate: discwhich.com (Lance buying morning-of)

---

## Core thesis
- Core object = **bag as shot-shape grid**, not a mold catalog
- Numbers = skeleton
- Plastic mannerisms + sentiment + pro comps = muscle
- We **draw our own** schematic flight paths from S/G/T/F
- Innova official charts = **calibration / proof only**, not assets we ship as ours
- After Innova-proofed: chart molds brands never plated

---

## Chart orientation (LOCKED)
- **Tee at BOTTOM** of graphic
- Flight runs **UP** the page (away from viewer)
- RHBH: +x = right (turn/flip), −x = left (fade)
- Shape ≠ distance: **turn/fade = curve**, **speed/glide = how far up the chart**
- Same-ish shape can still be different discs (Orc vs Mystere)

---

## V1 brand families
1. Innova  
2. Discraft  
3. MVP family = MVP + Axiom + Streamline  
4. Discmania  

---

## Modes
- Gap fill (stay / mixed)
- Convert bag
- Build new bag
- Single disc match
- Overlap audit

---

## Brand / fill policy
- **Stay in family**
- **Convert to** target brand(s)
- **Mixed bag default:** if bag already has 2–3 brands, **fill from brands already present** first
- Toggles: bag-brands-only | prefer-bag-brands | single-lock | any
- Son’s bag example → fill from Innova + MVP/Axiom first

---

## Plastic mannerisms (required layer)
Same mold ≠ same flight. Store `mold + plastic` when known.

### Innova-style ladder (general)
- DX / baseline → less stable, beats in fast  
- Pro / GStar → often flippier than premium  
- Star → premium, holds longer  
- Champion / C-line class → usually most stable OOTB  

### MVP-family analog
- Soft / Electron / some Fission → often less stable  
- Neutron / Proton / Plasma → closer to chart premium  
- Stiffer OS blends → hold OS longer  

**Engine:** effective_stability = numbers ± plastic_offset ± beat-in (later)

Examples in son’s bag:
- DX Invader = flippier end of mold  
- Champion Sidewinder ≠ DX Sidewinder  
- Star Destroyer = premium OS distance  
- Neutron Soft Hex = can play a hair less stable than stiff Neutron  
- Glitch Glow = own class (catch / touch, not standard putter)

---

## Shot grid
Rows: Putt/Approach · Mid · Fairway · Control/Hybrid · Distance  
Cols: US · STR · OS · VOS  

Stability bucketing note:
- stab sum alone lies (TeeBird 0/2 and Orc −1/3 both sum ~2)
- fade-heavy molds tip OS/VOS even when sum looks straight

---

## Matching
- Stability (turn+fade) heaviest  
- Speed band hard filter  
- Fade / turn / glide  
- Plastic offset  
- Optional sentiment + pro edges later  
- Always show why  
- Collapse near-duplicates by **shot**, not logo  
- Cap recommendations at max controllable speed  

Shape vs carry:
- Orc 10/4/−1/3 → shorter, harder fade  
- Mystere 11/6/−2/2 → longer, more flip  
- Related neighborhood ≠ same line  

---

## Data
- Spine: DiscIt / Marshall-derived mold list (mirror locally)
- Fields: mold, brand, family, category, S/G/T/F, plastic, stability slug
- Later: comparables[] from sentiment/pro/editorial

---

## Lance bag (adult) — test set
Aviar P&A, AviarX3, Atlas, Mako3, TeeBird3, Banshee, Firebird, Orc, Mystere, Archon  

Observed:
- Overlaps: Mako3+Atlas (mid STR); Mystere+Archon (flip hybrid)
- Gaps: US mid, OS mid, US fairway, flip distance, OS distance
- Suggested Innova fills (number pass): Panther, Roc3, Leopard3, Tern, Destroyer

---

## Son bag — discuss before build
1. Innova Star Destroyer  
2. Axiom Neutron Soft Hex  
3. MVP Glitch Glow  
4. Innova Champion Sidewinder  
5. Innova DX Invader  

Read: fun mixed starter pile, not a ladder.  
Tension: Sidewinder → Destroyer is a huge jump; Glitch ≠ putting putter.  
Missing: real putter, OS/stable mid, straight fairway, OS fairway, controllable 9–11.  
Fill policy when run: **Innova + MVP/Axiom only** unless opened.  
Plastic-aware. Discuss fill list before regenerating page.

Open questions (son):
- Age / arm speed  
- Does Destroyer actually fly for him?  
- What does he putt with?  
- Bag size target 6–8 vs 9–12  

---

## Visual system
- Own path renderer from S/G/T/F  
- Innova plates = side-by-side proof only  
- Brand chart availability:
  - Innova: classic multi-path plates (gold standard)
  - Discmania: official flight chart/PDF
  - Discraft: flight chart + different stability language
  - MVP family: weak official wall art → we generate
- Views: path chart, grid heatmap, ladder, compare overlay
- Ghost dashed = recommended gap fills
- Length % marks optional so carry differences read

---

## Prototype status
- Local engine: `~/whichdisc/`
- Live Pages: github.io/whichdisc
- Needs: tee-at-bottom fix (code pass may still be pending), plastic field, mixed-brand fill, son bag run after discuss

---

## Brand marks / logo directions (topic for tomorrow)
Tone: utility tool golfers trust — clean, sport, a little sharp. Not cartoon mascot unless we choose playful lane on purpose.

### Strong directions
1. **Flight-path wordmark** — “Which” in solid type, “Disc” with a single RHBH schematic curve through/under the letters (tee-bottom grammar). Instantly on-product.
2. **W / path monogram** — letter W whose right leg becomes a turn→fade flight line. App icon gold.
3. **Bag grid mark** — tiny 3×3 shot grid with one cell lit (the “missing” shot). Owns gap-fill story.
4. **Disc + chevron** — top-down disc silhouette, small nose chevron / path leaving the rim. More generic DG; only if path mark feels too nerdy.
5. **The Whicher badge** — secondary stamp only (“asked the Whicher”); not the primary corporate mark.

### System to build (when we do it)
- Primary wordmark
- App / favicon monogram
- One-color + dark-mode + stamped-on-photo versions
- Optional path-curve as UI motif (charts, loading, share cards)

### Avoid
- Clip-art basket chains as the whole logo
- Innova-clone flight-plate wallpaper as brand
- Over-literal “?” + disc mashup unless very tight

### Tomorrow decision
Pick 1–2 directions → generate mark board → lock primary before public discwhich.com.

---

## Feature development backlog (ideas parked)

### Tier A — near-core (after bag grid + paths work)
- Plastic mannerisms / effective stability
- Mixed-bag fill from brands already in bag
- Max controllable speed hard cap
- Overlap collapse by shot shape
- Convert / single-match / gap fill modes

### Tier B — pro + power model (big differentiator)
**Pro bags**
- Featured tour/am bags: what’s in the bag by slot + shot shape plate
- Compare *your* bag ↔ pro bag (same grid language)
- Source: in-the-bag posts, team pages, coverage — cited, dated (bags change)
- Not just mold lists — **their shot map** (US mid, OS fairway, etc.)

### Arm speed scale (discwhich) — worked example

**Idea:** user-facing **arm speed 1–12** (not raw mph first).  
Mph optional advanced; the 1–12 arm speed drives recommendations.

| Band | Who it feels like | Controllable speed (approx) | What the bag should emphasize |
|---|---|---|---|
| **1–2** | New / kid arm | ≤ 6–7 | Putters, mids, understable fairways; almost no 10+ |
| **3–4** | Rec / developing | ≤ 8–9 | Straight fairways enter; light US distance only |
| **5–6** | Solid am | ≤ 10–11 | Full fairway suite; controllable drivers |
| **7–8** | Hot am / low pro | ≤ 12 | Distance OS/US both useful |
| **9–10** | Tour power (Ricky-class) | ≤ 13 | High-speed molds actually flip/hold as numbered |
| **11–12** | Elite distance (Wiggins-class) | 14+ viable | Max D molds “work”; still need utility OS |

**Worked example**
- Kid **arm 1** → Sidewinder = main driver; Destroyer = often just a heavy OS dump / future disc  
- Lance *(placeholder until measured)* likely **5–7** if he bags Mystere/Orc/Firebird with intent — full fairway + hybrid ladder, selective distance  
- **Ricky ~9** → Destroyer/Wraith class are real workhorses, not toys  
- **Wiggins ~11** → 14-speed understable actually goes where numbers promise  

**How picks change (same mold, different arm)**
- Arm 1 + Star Destroyer → label as *utility beef / do not max-D*; prefer Sidewinder, Hex, putter  
- Arm 6 + Star Destroyer → *OS distance / wind / hyzer button*  
- Arm 9 + Star Destroyer → *primary OS distance slot*  
- Arm 11 + understable 14-speed → *max D flipper*; arm 3 → *don’t bag it*

**Rules for Discwhich**
1. Every profile has an **arm speed (1–12)** (default ask; don’t assume tour).  
2. Recommendations **hard-cap mold speed** near band (with small stretch if stability bias = OS utility).  
3. Distance shown as **range for that band**, not one fantasy number.  
4. Pro bags tagged with **pro arm speed** so compare is fair (“Ricky’s bag at your arm 4 ≠ his flight”).  
5. Release angle is a second dial on top of arm speed.

**Arm-speed calibration wizard (no launch monitor required)**  
Ask 3–5 plain questions → map to 1–12:

1. **Max reliable drive distance** (not one lucky roller) — bands in feet/meters  
2. **Which disc** they use for that max (mold + plastic if known)  
3. **How it flies at that power** — holds straight / flips some / turns and burns / never turns (always fades early)  
4. Optional: comfortable **fairway** distance with a TeeBird/Hex-class  
5. Optional: age / years playing (soft prior only)

**Mapping logic (sketch)**
- Distance alone → rough arm speed  
- Disc used for max → refine (max on Sidewinder ≠ max on Destroyer)  
- Shape at max → refine further:
  - Destroyer that never turns + short distance → lower arm speed, disc too fast  
  - Sidewinder that goes far and flips to flat → mid arm speed  
  - High-speed US that still finishes predictably at long distance → high arm speed  
- Output: **arm speed + confidence** + one sentence (“Arm ~3: Sidewinder is your distance disc; 12-speeds are utility/future”)

**Informing son’s bag specifically**
- If arm ≈ 1–2: keep Hex + Sidewinder + real putter; bench or reframe Destroyer; skip stacking more high-speed OS.  
- Fill: putter, stable mid, straight fairway — not another 12-speed.
- Calibrate his arm speed via max distance + “is max on Sidewinder or Destroyer?” before final fills.


**Release angle dial**
- Flat / hyzer / anhyzer (and degrees later)
- Re-draw schematic path for same disc under different release
- Teach shot shaping: “Hex on hyzer vs flat vs anhyzer”
- Pair with arm speed: high-speed OS on hyzer vs understable on anhyzer

### Tier C — later depth
- Beat-in / seasons of plastic
- FH vs BH separate grids
- Lefty mirror
- Wind presets
- Sentiment + pro commentary edges on matches
- Share cards: “my bag plate” / “my arm speed map”
- Affiliate buy links once trust is real

### Product principle for all of the above
Still one engine: **shot shape + conditions → recommendation**.  
Arm speed and release angle are **modifiers on the same path model**, not a separate app.
Pros are **reference bags on the same grid**, not celebrity merch pages.

### Build order suggestion
1. Solid path model + bag grid + plastic + mixed fill  
2. Arm speed (1–12) → distance ranges + speed cap enforcement  
3. Release-angle dial on path renderer  
4. Pro bag library on same grid + compare  

---

## Tomorrow agenda (~9am reminder)
1. Buy **discwhich.com** (if not done)
2. Finish **tee-at-bottom** charts + push Pages
3. **Logo / brand mark** directions → pick + optional generate board
4. Son bag: chart + fill discuss (Innova + MVP/Axiom, plastic-aware)
5. Plastic offsets v0 + bag-brands-only fill mode notes → build if time
6. Skim **feature backlog** (pro bags, arm speed distance, release angle) — park or promote, don’t build all tomorrow

---

## Next when Lance says go
1. Tee-bottom charts + git/pages  
2. Logo exploration board  
3. Son bag chart + gap discuss  
4. Plastic offsets v0  
5. Bag-brands-only fill mode  
6. discwhich.com → point Pages/CNAME  
