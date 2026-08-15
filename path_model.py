"""discwhich schematic flight-path model.

Chart convention (LOCKED):
  - Tee at BOTTOM, flight runs UP (away from viewer)
  - Model +y = farther from tee
  - +x = right (RHBH turn/flip) · −x = left (RHBH fade)

Innova plate truth (researched against official characteristic charts):
  - Almost EVERY mold finishes with a LEFT hook at the tip (fade).
  - Even Mamba / Roadrunner / Leopard / Wolf: big right mid, then tip curls left.
  - OS (Firebird/Banshee/Gator/Pig): whole line lives left; finish is a sharp left crook.
  - Straight (TeeBird/Mako/Aviar): near-vertical, gentle left finish only.
  - US finish position may still sit right of the tee line — but final tangent is leftward.
  - Labels on Innova sit at path ends; we put tee at bottom with names under tee.

We match curve *grammar* (families + finishes), not pixel-traced art.
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


def _clamp01(x: float) -> float:
    return min(1.0, max(0.0, x))


def _smoothstep(edge0: float, edge1: float, x: float) -> float:
    if edge1 == edge0:
        return 0.0
    t = _clamp01((x - edge0) / (edge1 - edge0))
    return t * t * (3.0 - 2.0 * t)


def _logistic(t: float, mid: float, k: float) -> float:
    return 1.0 / (1.0 + math.exp(-k * (t - mid)))


class PathModel:
    """Innova-finish-faithful path generator.

    Finish law (non-negotiable):
      d(x)/dt < 0 near t→1 for essentially all molds (left hook).
      Rated fade scales hook sharpness; fade 0 still gets a small natural finish.
    """

    def __init__(
        self,
        *,
        length_base: float = 50.0,
        length_speed: float = 6.2,
        length_glide: float = 7.6,
        turn_gain: float = 13.2,
        fade_gain: float = 15.0,
        # minimum end-hook so even 0-fade lines curl left like Innova putt/US tips
        natural_finish: float = 3.8,
        os_bow_gain: float = 4.8,
        max_abs_x: float = 50.0,
    ) -> None:
        self.length_base = length_base
        self.length_speed = length_speed
        self.length_glide = length_glide
        self.turn_gain = turn_gain
        self.fade_gain = fade_gain
        self.natural_finish = natural_finish
        self.os_bow_gain = os_bow_gain
        self.max_abs_x = max_abs_x

    def length(self, d: Disc) -> float:
        sp = d.speed
        sp_eff = sp if sp <= 12 else 12 + 0.45 * (sp - 12)
        us_bonus = 0.0
        if d.turn <= -2 and d.glide >= 5:
            us_bonus = 3.5 + 1.2 * min(3.0, -d.turn - 1)
        return (
            self.length_base
            + self.length_speed * sp_eff
            + self.length_glide * d.glide
            + us_bonus
        )

    def _turn_build(self, t: float, d: Disc) -> float:
        """Turn displacement builds mid-flight, then STOPS (does not keep pushing at tip).

        Innova US paths: max right is before the tip; tip is the fade crook.
        """
        # Faster discs hold high-speed turn a bit longer.
        peak = 0.40 + 0.012 * max(0.0, min(6.0, d.speed - 5.0))
        # Build to full by ~peak
        build = _logistic(t, mid=peak * 0.5, k=13.0)
        # After peak, freeze turn contribution (plateau) so fade can win the tip
        # Slight decay so S-curves come back cleaner
        freeze = 1.0 - 0.18 * _smoothstep(peak, min(0.95, peak + 0.40), t)
        return build * freeze

    def _fade_build(self, t: float, d: Disc) -> float:
        """Fade is a late shepherd's crook — last ~25% of flight on Innova plates."""
        # Higher rated fade bites slightly earlier and harder
        fade_n = max(0.0, d.fade)
        mid = 0.78 - 0.025 * min(4.0, fade_n)
        k = 20.0 + 2.0 * min(4.0, fade_n)
        return _logistic(t, mid=mid, k=k)

    def _os_bow(self, t: float, d: Disc) -> float:
        """OS molds bow left for most of the flight (Firebird/Banshee/Gator), not only at tip."""
        # Amount of "always left" character
        os = max(0.0, d.fade - max(0.0, -d.turn) * 0.7)
        if os < 0.2:
            return 0.0
        # Smooth left bow from early on
        bow = _smoothstep(0.02, 0.45, t) * (0.65 + 0.35 * t)
        return -self.os_bow_gain * os * bow

    def point(self, d: Disc, t: float) -> Point:
        t = _clamp01(t)

        turn_n = float(d.turn)  # negative = US
        fade_n = max(0.0, float(d.fade))

        # --- lateral components ---
        # Turn → right when turn_n negative
        turn_x = (-turn_n) * self.turn_gain * self._turn_build(t, d)

        # Extra mid bulge for very US (Mamba/Roadrunner) — still finishes left via fade
        if turn_n <= -3.0:
            mid_bulge = math.sin(math.pi * _clamp01(t / 0.92)) ** 1.08
            turn_x *= 0.88 + 0.28 * mid_bulge

        # Rated fade → left crook at tip
        fade_x = -fade_n * self.fade_gain * self._fade_build(t, d)

        # Natural finish: nearly all Innova lines curl left at the tip,
        # even Classic Aviar (0 fade) and extreme US (still a left tip).
        # Scale down a bit for already high-fade molds (already crooking hard).
        nat_scale = 1.0 - 0.15 * min(4.0, fade_n)
        # US discs still get full natural tip curl (critical for Leopard/Mamba tips)
        natural_x = -self.natural_finish * nat_scale * self._fade_build(t, d)

        # OS continuous left bow
        bow_x = self._os_bow(t, d)

        # High-speed beef (Destroyer/Wraith): keep early line tighter, dump late
        if d.speed >= 11 and -1.3 <= turn_n <= 0.0 and fade_n >= 2.5:
            early = 1.0 - _smoothstep(0.0, 0.32, t)
            turn_x *= 1.0 - 0.45 * early

        x = turn_x + fade_x + natural_x + bow_x

        if abs(x) > self.max_abs_x:
            x = math.copysign(self.max_abs_x + (abs(x) - self.max_abs_x) * 0.18, x)

        y = t * self.length(d)
        return (x, y)

    def path(self, d: Disc, n: int = 72) -> List[Point]:
        if n < 2:
            n = 2
        return [self.point(d, i / (n - 1)) for i in range(n)]

    def finish_dx(self, d: Disc, eps: float = 0.02) -> float:
        """Lateral delta near tip; should be negative (left) for nearly all molds."""
        x0 = self.point(d, 1.0 - eps)[0]
        x1 = self.point(d, 1.0)[0]
        return x1 - x0

    def stability_color(self, d: Disc) -> str:
        s = d.stab
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
