# discwhich — Working notes (saved)

Last updated: 2026-08-15 (evening pass)  
Prototype: https://thecooperativeagency.github.io/whichdisc/  
Repo: https://github.com/thecooperativeagency/whichdisc  
Local: `~/whichdisc/` (NOTES.md, REV1.md, path_model.py, build_prototype.py, out/, site/)

### Domain
- **Buy: discwhich.com** — was AVAILABLE (no WHOIS match, DNS NXDOMAIN). Lance planned morning purchase.
- **whichdisc.com** — TAKEN since 2003, Cloudflare, expires 2027-06-09; dead "no longer trading" page. Not ours.
- Also looked free-ish: discwhich.io, whichdisc.io, .golf variants (confirm at registrar).
- Live prototype stays on github.io until domain points.

---

## Name
- Product: **discwhich**
- Nickname: **the Whicher** (secondary / badge only)
- Do not lead with abstract "arm band" language — say **arm speed**

---

## Core thesis
- Core object = **the bag as coverage of shot shapes / landing zones**, not a mold catalog
- Numbers = skeleton
- Plastic + arm speed + release + (later) sentiment/pro = muscle
- We **draw our own** schematic paths + field map from S/G/T/F (+ throw conditions)
- Innova official charts = calibration reference only
- Puttheads etc. = UX/category proof, **not** a high bar and not commonly known

---

## Chart orientation (LOCKED)
- **Tee at BOTTOM** of every graphic (paths + field map)
- Flight / fairway runs **UP** the page (away from viewer)
- RHBH: +x = right (turn/flip), −x = left (fade)
- Shape ≠ distance: turn/fade = curve; speed/glide = how far upfield
- Lateral motion should stay **subtle** (Innova / Puttheads scale) — over-dramatic curves look fake
- Fade once started **keeps hooking left through the tip** — never "fade then straighten"
- Same-ish shape can still be different discs (Orc vs Mystere)

### Path law — two lateral questions
1. **Does it flip / go right before the finish?** → turn  
2. **How far left does it fade at the very end?** → fade  

### Throw conditions — spin × speed
| More… | Effect |
|---|---|
| **Speed** (arm speed) | Farther; more flip if mold can; fade **later** if disc is flying |
| **Spin** | More flip-up, more glide; fade **later** |
| **Both** | Chart flight |
| **Low both** | Early dump, little flip, short ("too much disc") |

Copy: "Faster & more spin = more flip, more glide, fade waits until the end."

---

## Bag field map (drone / top-down) — PREFERRED bag viz

**Lance concept:** drone view behind thrower.

### Layout (LOCKED)
- Thrower **silhouette at BOTTOM**
- Field extends **UP** = farther
- L/R = fade / turn sides (RHBH default)
- Each disc = **landing zone blob** (distance + left/right), not only a thin line
- **Empty grass** = missing shots (spatial gap story)
- Ghost blobs = recommended fills

### Why primary
- "Banshee lands here, Archon deep, Aviar short" in one glance
- Gaps obvious without reading a matrix
- Shareable bag card

### Views
| View | Job |
|---|---|
| **Field map** | bag coverage on the ground — primary bag story |
| Path plate | flight shape (flip → fade) |
| Shot grid | taxonomy / completeness checklist |

v1: simple silhouette OK; schematic zones not GPS; arm speed scales depth; label missing **shots** first.

---

## Competitive landscape (honest)

### DiscIt
- **What:** REST API of mold list scraped from Marshall Street Flight Guide (nightly)
- **Gives:** name, brand, S/G/T/F, stability slug, optional pic/link
- **Does not:** paths, physics, arm speed, hyzer, bag logic
- **Use for us:** catalog spine only (mirror locally; don't depend on live scrape forever)

### Marshall Street Flight Guide
- Best-known **catalog UI** (speed vertical, stability horizontal)
- Static flight chart images per disc; not a throw simulator
- Not a bag-gap/convert product

### DG Puttheads Flight Charts — deep dive (2026-08-15)
**Site:** https://flightcharts.dgputtheads.com/  
**Who:** Chris & Rodney, dgputtheads.com blog  
**Market reality:** **Not great UX, not commonly known, looks very 1990s.** Low brand threat. Category prototype, not category owner.

**What it is:** interactive multi-brand grid + path chart + light throw dials + compare + my-bag matrix.

**How paths really work (inspected code/API):**
- Browser does **not** compute paths live from S/G/T/F
- API: `https://flightcharts.dgputtheads.com/discdata/{id}`
- Each disc stores **six prebaked polylines** (~17–18 points):
  - `bh1/bh2/bh3` = backhand arm speed slow/normal/fast
  - `fh1/fh2/fh3` = forehand (separate sets, not just mirrored BH)
- UI swaps which array to plot (AmCharts)
- Also stores manufacturer numbers + PDGA-ish dims (diameter, rim, max weight, approval date) + buy/review links

**Their stated method (about page):**
- "Complex math formula" from inputs
- **Plus human adjustment** from throwing experience
- Fast to add molds
- Extra data mostly **PDGA public**
- They admit charts can be wrong

**Geometry lesson:** their paths are nearly vertical; lateral x is tiny vs distance y. Matches Innova subtlety. Our early lines were overcooked laterally.

**Dials they have:** L/R hand, FH toggle, 3 arm speeds.  
**Dials they lack:** hyzer degrees, spin, nose, wind, plastic-in-path.

**Steal:** grid → select → path → arm-speed/hand → compare → bag  
**Don't steal:** dated UI, opaque editorial black box as long-term data dependency, scrape of their path arrays  
**Beat them on:** modern UI, field map, bag gaps/convert, plastic, better arm-speed onboarding, release angle, trust copy

### Shotshaper (kegiljarhus) — honest
- Clean academic repo (UiS fluid dynamics prof), GPL-3, not shady
- **Physics throw sim** for a **few** CFD-modeled discs
- Inputs: speed, spin, nose/roll — **not** S/G/T/F
- Use: calibrate our physics intuition / optional research  
- **Not** the product path engine for all molds

### FrisPy / flying-discs
- Python frisbee ODEs; same class as Shotshaper (physics, not flight-number catalog)

### TechDisc
- Paid launch monitor + sim; measures real throws; different job

### TryDiscs
- Speed×stability matrix; no path sim

### Hard truth
There is **no** finished open product that is: all molds + flight numbers in + continuous arm speed/hyzer/spin + trusted physics + modern bag tool.  
That gap **is** discwhich.

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
- Stay in family / convert to / mixed
- **Mixed default:** fill from brands already in bag first
- Son bag → Innova + MVP/Axiom first

---

## Plastic mannerisms (required)
Same mold ≠ same flight. Store mold + plastic.

Innova-ish: DX less stable → Star holds → Champion often most OS OOTB  
MVP-ish: Soft/Electron flippier → Neutron/Proton premium → stiff OS holds  

effective_stability = numbers ± plastic_offset ± beat-in (later)

---

## Shot grid
Rows: Putt/Approach · Mid · Fairway · Control/Hybrid · Distance  
Cols: US · STR · OS · VOS  
Fade-heavy molds tip OS even when turn+fade sum looks "straight."

---

## Matching
- Stab / speed band / fade / turn / glide / plastic
- Show why; collapse by shot not logo
- Cap at controllable speed for arm speed
- Shape vs carry both matter (Orc ≠ Mystere)

---

## Arm speed (not "band")
- UX lead with **max reliable distance + which disc + how it flies**
- Internal scale can be 1–12 or speed-ceiling; don't marry 1–12 publicly
- Lance calibration hint: max D from Archon / beat-in Orc / Mystere → ~controllable **speed 11** class
- Kid/son: if arm low, Sidewinder = distance; Destroyer often utility/future

---

## Data spine
- Mirror DiscIt/MS mold list locally
- PDGA for dims when useful
- Own path/field generator
- Later: comparables from sentiment/pro

---

## Test bags
**Lance:** Aviar P&A, AviarX3, Atlas, Mako3, TeeBird3, Banshee, Firebird, Orc, Mystere, Archon  
- Overlaps: Mako3+Atlas; Mystere+Archon  
- Gaps: US mid, OS mid, US fairway, flip distance, OS distance  

**Son (discuss before build):** Star Destroyer, Neutron Soft Hex, Glitch Glow, Champion Sidewinder, DX Invader  
- Mixed starter; Glitch ≠ putter; Sidewinder→Destroyer jump  

---

## Brand / logo directions
1. Flight-path wordmark (tee-bottom grammar)  
2. W monogram → path (app icon)  
3. Gap-grid missing cell  
4. Disc + chevron  
5. "the Whicher" badge only  
Lean: #2 icon + #1 wordmark. Modern utility — not Puttheads-era UI.

---

## Feature backlog
**A:** plastic, mixed fill, speed cap, overlap, convert/match/gaps, **field map**  
**B:** pro bags on same map, arm-speed distances, release-angle dial  
**C:** beat-in, FH grid, wind, sentiment, share cards, affiliate  

Build order: path+field+grid → arm speed → release → pro bags  

---

## Prototype status
- Live Pages + repo exist (branding discwhich on page)
- Path model iterated; tee-bottom + finish law in code; still needs visual QA vs Innova
- Field map **not built yet** (notes only)
- Puttheads reverse-engineering done (prebaked bh/fh paths)

---

## Next when Lance says go
1. discwhich.com DNS when purchased  
2. Field map v0 (tee bottom, landing blobs, empty zones)  
3. Path visual QA (subtle lateral, no straighten-after-fade)  
4. Logo board  
5. Son bag discuss/fill  
6. Plastic + bag-brands fill  
