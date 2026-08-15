# discwhich — Product Rev 1

**Working name:** discwhich  
**Nickname:** the Whicher  
**One-liner:** Build, fill, or convert a disc golf bag by shot shape — not by vibes alone.

**North star:** Every recommendation answers *what shot is this for?* and *what do I already cover?*

---

## 1. Problem

Golfers either:
1. Switch brands and don’t know equivalents
2. Stay in-brand and bag 4 discs that all fly the same
3. Buy max-speed plastic they can’t control

Existing tools show catalogs and static flight charts. Few run a **bag-aware shot grid** with toggles for stay / convert / hybrid.

---

## 2. Product thesis

**Core object = the bag as a shot-shape grid.**  
Modes (gap fill, brand convert, full build) are views over that grid.

Numbers are the skeleton.  
Sentiment + pro comps are optional muscle (v1.5+).  
Visual flight paths make overlap obvious — classic Innova-chart energy, interactive and bag-aware.

---

## 3. Primary jobs (all supported by toggles)

| Job | User intent | Output |
|---|---|---|
| **Gap fill** | Stay in family; what’s missing? | Empty cells + 1 pick each |
| **Convert** | Defect / try new brand | Same shots in target brand(s) |
| **Full build** | Build from scratch | Ladder putter → max distance |
| **Single swap** | “Mystere → MVP?” | Top 3 + why |
| **Overlap audit** | Too many same-shape discs | Collapse near-dupes |

---

## 4. Controls (clean full-featured panel)

### 4.1 Mode
- `Fill gaps` (default retention mode)
- `Convert bag`
- `Build new bag`
- `Single disc match`

### 4.2 Brand policy
- **Stay in:** Innova | Discraft | MVP family | Discmania  
- **Convert to:** one or more of the above  
- **MVP family** = MVP + Axiom + Streamline (one ecosystem toggle)  
- **Mixed OK** on/off (off for v1 purity)

### 4.3 Thrower profile
- Max controllable speed (slider 3–14) — hard cap on recommendations  
- Dominant hand path: BH / FH / both  
- Power band label (auto from speed): touch / control / distance  
- Stability bias: prefer straighter | balanced | prefer OS safety  
- Optional: lefty mirror (flip turn/fade display)

### 4.4 Bag size
- 6 / 9 / 12 / 18 / custom  
- Drives how many grid cells are “required” vs “nice”

### 4.5 Matching signals (toggles)
- Flight numbers (on, always available)  
- Stability buckets (on)  
- Thrower sentiment (off until data exists)  
- Pro commentary (off until data exists)  
- Collapse duplicates (on by default)

### 4.6 Recommendation style
- Conservative (high confidence only)  
- Standard  
- Exploratory (more US options / newer molds)

---

## 5. Shot-shape grid (v1 schema)

Rows = speed class. Columns = stability role.

### 5.1 Stability columns (left → right = US → OS)

| Col | Code | Meaning | Stab proxy (`turn+fade`) guide |
|---|---|---|---|
| 1 | US | Understable / flip / turnover | ≤ -1 |
| 2 | STR | Straight / neutral | ~ -0.5 to 1.5 |
| 3 | OS | Overstable / reliable fade | ≥ 2 |
| 4 | VOS | Utility beef (optional cell) | ≥ 3.5 + low glide |

### 5.2 Speed rows

| Row | Class | Speed band | Required at bag size |
|---|---|---|---|
| P | Putt | 1–2 | 6+ (1 STR putt) |
| A | Approach | 2–4 | 9+ |
| M | Mid | 4–5 | 6+ |
| F | Fairway | 6–9 | 6+ |
| C | Control / hybrid | 9–11 | 9+ |
| D | Distance | 10–max | only ≤ user max speed |

### 5.3 Default “complete bag” cells (12-bag target)

Required core (9):
1. P-STR — putting putter  
2. A-OS — approach OS (Zone/Pig/Envy class)  
3. M-US — flip mid  
4. M-STR — neutral mid  
5. M-OS — stable mid  
6. F-US — hyzer-flip / turnover fairway  
7. F-STR — workhorse fairway  
8. F-OS — OS fairway  
9. C/D-STR or mild US — controllable distance under max  

Optional (unlock with bag size / bias):
10. A-STR — straight approach  
11. C-OS — OS hybrid  
12. D-US — max flip distance  
13. D-OS — distance OS  
14. F/C-VOS — wind/utility beef  

**Rule:** never fill D cells above max controllable speed.  
**Rule:** one primary disc per cell; second disc only if plastics differ and user opts “depth.”

---

## 6. Engine (v1 logic)

### 6.1 Place existing discs on grid
For each bagged mold:
- Map speed → row  
- Map `turn+fade` (+ category hints) → column  
- If two discs map same cell → mark **overlap**

### 6.2 Score candidate molds
```
score = w_stab * |stab_src - stab_cand|
      + w_speed * |speed_src - speed_cand|
      + w_fade * |fade_src - fade_cand|
      + w_turn * |turn_src - turn_cand|
      + w_glide * |glide_src - glide_cand|
      + band_penalty (hard if row mismatch)
```
Default weights: stab 3.0, speed 2.0, fade 1.5, turn 1.2, glide 0.5

### 6.3 Mode behaviors
- **Gap fill:** empty required cells → best in-brand picks  
- **Convert:** each occupied cell → best target-brand pick; preserve shot labels  
- **Build new:** fill required cells from profile only (no source bag)  
- **Single match:** ignore grid completeness; return top 3 + alts  

### 6.4 Duplicate collapse
If two recommendations have:
- same row, and  
- |Δstab| < 0.75 and |Δspeed| < 1  
→ keep higher confidence / more popular; show the other as “same job.”

### 6.5 Explainability (always on)
Each pick shows:
- Shot label (“OS fairway / reliable hyzer”)  
- Numbers  
- Why (gap | convert | overlap replace)  
- Confidence: high / med / low  

---

## 7. Visual system (critical)

Inspired by classic **Innova flight characteristic charts** (paths from tee, US left / OS right fade finish for RHBH) and modern interactive guides — but **bag-aware**.

### 7.0 Brand chart sources (research log)

| Brand | Classic path-wall chart? | Best known sources | Notes for discwhich |
|---|---|---|---|
| **Innova** | Yes — the gold standard | [Disc Golf Shopping Innova charts](https://discgolfshopping.com/pages/innova-flight-chart); Innova disc comparison | Distance / fairway / mid / putt separate path plates |
| **Discraft** | Partial / different system | [team.discraft.com/flight-chart](https://www.team.discraft.com/flight-chart); BuildMyBag.Discraft.com; stability -2…+3 legacy | Has flight chart + disc finder; not always Innova-style multi-path plate |
| **Discmania** | Yes (PDF lineage) | [discmania.net/pages/flight-chart](https://www.discmania.net/pages/flight-chart); retail mirrors | Printable flight chart exists — closest “other brand Innova-like” asset |
| **MVP / Axiom / Streamline** | Weak as official wall art | Per-mold pages + numbers; community interactive charts; Marshall Street | No strong official multi-disc path poster; we generate paths from numbers |
| **Cross-brand** | Interactive, not brand-official | [Marshall Street Flight Guide](https://www.marshallstreetdiscgolf.com/flightguide); [DG Puttheads flightcharts](https://flightcharts.dgputtheads.com/); TryDiscs matrix | Use as UX refs, not scrape targets for product visuals |

**Implication:** Don’t wait on MVP/Discraft to publish Innova-quality posters. **discwhich owns a unified schematic path renderer** driven by S/G/T/F (+ optional brand underlays when assets are clean/licensed). Classic Innova/Discmania charts inform art direction only.

### 7.1 Views
1. **Path chart** — each bagged disc as a flight curve; gaps shown as ghost paths  
2. **Grid heatmap** — cells covered / overlapping / empty  
3. **Ladder list** — putter → distance, mobile default  
4. **Compare strip** — source disc path vs recommended path overlay  

### 7.2 Path rendering (v1 simple model)
Generate a stylized 2D path from S/G/T/F (not physics sim):
- Early turn from Turn + Speed  
- Late hook from Fade  
- Length from Speed + Glide  
- HFB / RHBH mirror toggle  

Curves should be **readable and relative**, not claim laboratory truth. Label: “schematic flight shape.”

### 7.3 Visual states
- Solid path = in bag  
- Dashed ghost = recommended fill  
- Red double-stroke = overlap cluster  
- Dim above speed cap = “not for your arm yet”

### 7.4 Brand chart mode
Toggle brand catalog underlay (Innova-only, MVP family, etc.) like the old wall-chart feel, with **your discs highlighted** so overlap vs lineup is obvious.

---

## 8. IA / screens

```
Home
 ├─ My Bag (add molds, size, profile)
 ├─ Analyze (grid + paths + gaps)
 ├─ Build / Convert (wizard with toggles)
 ├─ Match (single disc)
 └─ Chart Explore (brand underlay + filters)
```

Mobile-first. Desktop gets full chart + control rail.

---

## 9. Data (v1 brands)

**Families:**
1. Innova  
2. Discraft  
3. MVP family (MVP + Axiom + Streamline)  
4. Discmania  

**Source spine:** DiscIt / Marshall-derived mold list (mirror locally; nightly refresh later)  
**Fields:** id, name, brand, family, category, speed, glide, turn, fade, stability slug, optional image  

**Later layers (off by default):**
- `comparables[]` {source, target, weight, origin: sentiment|pro|editorial}  
- plastic class modifiers (premium vs baseline)

---

## 10. Example — Lance bag stress test

**In bag:** Aviar, Atlas, Mako3, Orc, Mystere, Banshee, (Archon sometimes)

| Cell | Status | Note |
|---|---|---|
| P-STR | covered | Aviar |
| A-OS | gap | no true approach beef |
| M-US | gap | |
| M-STR | covered | Mako3 |
| M-OS | covered | Atlas |
| F-US | gap | |
| F-STR | gap | |
| F-OS | covered | Banshee |
| C-OS | covered | Orc |
| D-US | covered | Mystere / Archon overlap |

**Fill gaps (Innova):** e.g. Leopard3 (F-US), TeeBird/TL3 (F-STR), Pig or AviarX3 (A-OS); skip second Mystere-class.  
**Convert (MVP family):** Atom, Hex, Reactor, Terra, Defy, Wave (+ Envy for A-OS).

---

## 11. V1 cut (ship)

**In**
- 4 brand families  
- Profile: max speed, BH/FH, bag size, brand policy  
- Modes: gap fill, convert, single match  
- Grid + ladder + simple path chart  
- Number matcher + duplicate collapse  
- Shareable results (link/image later OK as plain URL)

**Out (v1)**
- Accounts (optional local save only)  
- Sentiment/pro model live weights  
- Retail checkout  
- Full physics / arm-speed video  
- Every brand on earth  
- Plastic-level SKU inventory  

---

## 12. V1.5 / V2

- Sentiment + pro edges  
- Build-new wizard polish  
- Bag depth (beat-in / backup plastics)  
- Export image story card (“my discwhich bag”)  
- Affiliate links  
- Lefty + FH-optimized path art  

---

## 13. Success metrics

- User completes analyze with ≥3 discs  
- Gap mode produces ≤4 adds (not a dump)  
- Convert preserves slot count ±1  
- Qualitative: “that’s actually my missing shot”

---

## 14. Open questions for Lance

1. Default bag size on first run: 9 or 12?  
2. Putters: separate “putting only” vs “approach putter” always?  
3. Brand voice: utility-clean (Coop) vs disc-culture playful (“the Whicher”)?  
4. Ship order: **Analyze+Gaps** first, or **Single Match** viral hook first?  
5. Domain: whichdisc.com / .app availability TBD  

---

## 15. Recommendation

Build **Analyze (grid + paths + gaps)** and **Convert/Match** on the same engine.  
Visual shot shapes are not decoration — they’re how non-nerds trust the tool.

**Next build step after approval:**  
data mirror (4 families) → grid classifier → path SVG component → one working Analyze page on Lance’s bag.
