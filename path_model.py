"""WhichDisc schematic flight-path model.

RHBH chart convention (Innova-style plates):
  - Tee at TOP, flight runs DOWN the page ( +y = farther )
  - +x = right (turn / hyzer-flip side for RHBH)
  - -x = left  (fade finish for RHBH)

Innova numbers:
  - turn: more negative => more right push early
  - fade: more positive => more left hook late
  - speed/glide => path length
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple


Point = Tuple[float, float]


@dataclass(frozen=True)
class Disc:
    name: str
    speed: float
    glide: float
    turn: float
    fade: float
    brand: str = "Innova"
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


# Tuned against Innova fairway/distance/mid/putt characteristic plates.
# Goal: family relationships and curve grammar, not pixel clones.
class PathModel:
    def __init__(
        self,
        *,
        length_base: float = 38.0,
        length_speed: float = 7.0,
        # Glide must read on the plate: Mystere (G6) outruns Orc (G4)
        # even when stability neighborhoods look related.
        length_glide: float = 8.5,
        turn_gain: float = 11.5,
        fade_gain: float = 13.5,
        # OS discs also "lean" left earlier on Innova plates
        os_early_lean: float = 3.6,
        # keep extreme US from leaving the frame
        max_abs_x: float = 48.0,
    ) -> None:
        self.length_base = length_base
        self.length_speed = length_speed
        self.length_glide = length_glide
        self.turn_gain = turn_gain
        self.fade_gain = fade_gain
        self.os_early_lean = os_early_lean
        self.max_abs_x = max_abs_x

    def length(self, d: Disc) -> float:
        # Putters short, distance long — match plate proportions.
        # Soft diminishing returns above speed 12.
        sp = d.speed
        sp_eff = sp if sp <= 12 else 12 + 0.55 * (sp - 12)
        return self.length_base + self.length_speed * sp_eff + self.length_glide * d.glide

    def _turn_envelope(self, t: float) -> float:
        """Early/mid right-push envelope (0..1). Peaks ~0.35-0.45 of flight."""
        # smooth rise then hold/decay so fade can win late
        rise = 1.0 - math.exp(-3.4 * t)
        decay = 1.0 - 1.0 / (1.0 + math.exp(-14.0 * (t - 0.72)))
        return max(0.0, rise * (0.35 + 0.65 * decay))

    def _fade_envelope(self, t: float) -> float:
        """Late left-hook envelope (0..1). Quiet early, strong finish."""
        # logistic late ramp
        return 1.0 / (1.0 + math.exp(-16.0 * (t - 0.58)))

    def _os_lean_envelope(self, t: float) -> float:
        """Gentle early left lean for high-fade / positive-stability discs."""
        return 1.0 - math.exp(-2.2 * t)

    def point(self, d: Disc, t: float) -> Point:
        t = min(1.0, max(0.0, t))
        # Innova turn is negative when understable. Chart +x is right.
        turn_x = (-d.turn) * self.turn_gain * self._turn_envelope(t)
        fade_x = (-d.fade) * self.fade_gain * self._fade_envelope(t)

        # Stability-driven early lean (Firebird/Banshee family sit left on plates)
        stab = d.stab
        lean = 0.0
        if stab > 0.75:
            lean = -self.os_early_lean * (stab - 0.75) * self._os_lean_envelope(t)

        # Slight speed stretch: faster discs show turn a hair longer before fade
        if d.speed >= 10 and d.turn <= -1:
            turn_x *= 1.0 + 0.04 * (d.speed - 9)

        x = turn_x + fade_x + lean
        # soft clamp
        if abs(x) > self.max_abs_x:
            x = math.copysign(self.max_abs_x + (abs(x) - self.max_abs_x) * 0.25, x)

        y = t * self.length(d)
        return (x, y)

    def path(self, d: Disc, n: int = 48) -> List[Point]:
        if n < 2:
            n = 2
        return [self.point(d, i / (n - 1)) for i in range(n)]

    def stability_color(self, d: Disc) -> str:
        """Innova plate language: red OS, orange/yellow straight, green US."""
        s = d.stab
        if s >= 3.0:
            return "#d62828"  # deep red — very OS
        if s >= 2.0:
            return "#e85d04"  # red-orange OS
        if s >= 1.0:
            return "#f4a261"  # orange stable
        if s >= 0.0:
            return "#e9c46a"  # yellow straight
        if s >= -1.5:
            return "#8ac926"  # light green mild US
        return "#2a9d8f"  # teal/green very US


def svg_path_d(points: Sequence[Point], sx: float, sy: float, ox: float, oy: float) -> str:
    """Map model coords to SVG: x right, y down already."""
    if not points:
        return ""
    parts = []
    for i, (x, y) in enumerate(points):
        px = ox + x * sx
        py = oy + y * sy
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
