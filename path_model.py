"""discwhich schematic flight-path model.

Chart convention (LOCKED):
  - Tee at BOTTOM, flight runs UP (away from viewer)
  - Model space: +y = farther from tee
  - +x = right (RHBH turn / flip)
  - -x = left  (RHBH fade)

Innova number mapping (calibrated to official characteristic plates):
  - turn more negative → stronger right push through mid-flight
  - fade more positive → stronger left hook at the finish
  - speed + glide → carry (how far up the plate)
  - high fade / low turn → whole line sits left (Firebird family)
  - high turn / low fade → S-curve bulge right (Leopard / Mamba / Roadrunner)

Innova prints tee-at-top; we flip orientation only. Curve *families* match their plates.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Sequence, Tuple

Point = Tuple[float, float]


@dataclass(frozen=True)
class Disc:
    name: str
    speed: float
    glide: float
    turn: float
    fade: float
    brand: str = "Innova"
    plastic: str = ""
    note: str = ""

    @property
    def stab(self) -> float:
        return self.turn + self.fade

    @property
    def numbers(self) -> str:
        def fmt(v: float) -> str:
            if float(v).is_integer():
                return str(int(v))
            return f"{v:g}"

        return f"{fmt(self.speed)}/{fmt(self.glide)}/{fmt(self.turn)}/{fmt(self.fade)}"


def _smoothstep(edge0: float, edge1: float, x: float) -> float:
    if edge0 == edge1:
        return 0.0
    t = (x - edge0) / (edge1 - edge0)
    t = min(1.0, max(0.0, t))
    return t * t * (3.0 - 2.0 * t)


def _logistic(t: float, mid: float, k: float) -> float:
    return 1.0 / (1.0 + math.exp(-k * (t - mid)))


class PathModel:
    """Innova-plate-tuned path generator.

    Visual targets (fairway / distance plates):
    - Firebird / Banshee: little/no right; hard left finish; line lives left of tee
    - TeeBird: nearly straight; mild left finish
    - Leopard / Leopard3: clear right mid bulge; soft finish
    - Roadrunner / Sidewinder / Mamba: big right S; finish still right-biased
    - Destroyer / Wraith: mild early right then authoritative left dump
    - Mystere / Archon: more right + longer carry than Wraith; softer finish than Destroyer
    - Mamba: longest right travel in the distance class
    """

    def __init__(
        self,
        *,
        length_base: float = 52.0,
        length_speed: float = 6.4,
        length_glide: float = 7.8,
        turn_gain: float = 14.0,
        fade_gain: float = 16.5,
        os_rail_gain: float = 5.5,
        max_abs_x: float = 52.0,
    ) -> None:
        self.length_base = length_base
        self.length_speed = length_speed
        self.length_glide = length_glide
        self.turn_gain = turn_gain
        self.fade_gain = fade_gain
        self.os_rail_gain = os_rail_gain
        self.max_abs_x = max_abs_x

    def length(self, d: Disc) -> float:
        # Match plate proportions: putters short, distance long; glide matters.
        sp = d.speed
        sp_eff = sp if sp <= 12 else 12 + 0.45 * (sp - 12)
        # understable high-glide gets a little extra "flies farther with less effort"
        us_bonus = 0.0
        if d.turn <= -2 and d.glide >= 5:
            us_bonus = 4.0 + 1.5 * min(3.0, -d.turn - 1)
        return (
            self.length_base
            + self.length_speed * sp_eff
            + self.length_glide * d.glide
            + us_bonus
        )

    def _turn_weight(self, t: float, d: Disc) -> float:
        """How much turn has expressed by progress t.

        Innova paths: turn builds through the first half, peaks mid-flight,
        then stops adding as speed bleeds (fade takes over).
        """
        # Peak earlier for slower discs; faster discs hold turn longer.
        peak = 0.42 + 0.015 * max(0.0, d.speed - 6.0)
        peak = min(0.55, peak)
        # accumulate to ~1 by peak, slight ease after
        acc = _logistic(t, mid=peak * 0.55, k=14.0)
        hold = 1.0 - 0.12 * _smoothstep(peak, min(1.0, peak + 0.35), t)
        return acc * hold

    def _fade_weight(self, t: float, d: Disc) -> float:
        """Fade is quiet early, then a decisive late hook — Innova J/S finishes."""
        # Higher fade starts biting a hair earlier (Firebird vs Leopard finish).
        mid = 0.70 - 0.03 * min(4.0, max(0.0, d.fade))
        k = 16.0 + 1.2 * min(4.0, max(0.0, d.fade))
        return _logistic(t, mid=mid, k=k)

    def _os_rail(self, t: float, d: Disc) -> float:
        """Whole-path left rail for OS molds (Firebird family lives left of tee)."""
        # Strong when fade high and turn not very negative.
        os_amt = max(0.0, d.fade - max(0.0, -d.turn) * 0.65)
        if os_amt <= 0.15:
            return 0.0
        # builds quickly after release, then steady
        rail = _smoothstep(0.0, 0.28, t) * (0.55 + 0.45 * t)
        return -self.os_rail_gain * os_amt * rail

    def point(self, d: Disc, t: float) -> Point:
        t = min(1.0, max(0.0, t))

        # Innova: turn number negative => right on RHBH plate
        turn_x = (-d.turn) * self.turn_gain * self._turn_weight(t, d)
        # fade positive => left
        fade_x = (-d.fade) * self.fade_gain * self._fade_weight(t, d)
        rail_x = self._os_rail(t, d)

        # Very understable (Mamba/Roadrunner): exaggerate mid bulge slightly
        if d.turn <= -3:
            bulge = math.sin(math.pi * t) ** 1.05
            turn_x *= 0.92 + 0.20 * bulge

        # Slight hyzer-flip delay on high-speed mild turn (Destroyer -1):
        # keep early line tighter before late dump — matches Destroyer/Wraith plates.
        if d.speed >= 11 and -1.25 <= d.turn <= 0 and d.fade >= 2.5:
            early = 1.0 - _smoothstep(0.0, 0.35, t)
            turn_x *= 1.0 - 0.35 * early

        x = turn_x + fade_x + rail_x
        if abs(x) > self.max_abs_x:
            x = math.copysign(self.max_abs_x + (abs(x) - self.max_abs_x) * 0.2, x)

        y = t * self.length(d)
        return (x, y)

    def path(self, d: Disc, n: int = 64) -> List[Point]:
        if n < 2:
            n = 2
        return [self.point(d, i / (n - 1)) for i in range(n)]

    def stability_color(self, d: Disc) -> str:
        """Innova plate language: red OS, orange/yellow straight, green US."""
        s = d.stab
        # also respect fade-heavy OS even if sum is moderate
        if d.fade >= 3.5 and d.turn >= -0.5:
            return "#c1121f"
        if s >= 3.0 or (d.fade >= 3.0 and s >= 1.5):
            return "#e85d04"
        if s >= 1.5:
            return "#f4a261"
        if s >= 0.0:
            return "#e9c46a"
        if s >= -1.5:
            return "#8ac926"
        return "#2a9d8f"


def svg_path_d(
    points: Sequence[Point],
    *,
    sx: float,
    sy: float,
    ox: float,
    oy: float,
    y_up: bool = True,
) -> str:
    """Map model coords to SVG.

    y_up=True (discwhich default): tee at oy, +model y goes UP the page.
    """
    if not points:
        return ""
    parts: list[str] = []
    for i, (x, y) in enumerate(points):
        px = ox + x * sx
        py = oy - y * sy if y_up else oy + y * sy
        parts.append(("M" if i == 0 else "L") + f"{px:.2f} {py:.2f}")
    return " ".join(parts)


def category_for(d: Disc) -> str:
    if d.speed <= 3:
        return "putt"
    if d.speed <= 5:
        return "mid"
    if d.speed <= 9:
        return "fairway"
    return "distance"
