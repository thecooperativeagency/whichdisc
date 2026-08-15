"""discwhich schematic flight-path model.

Chart convention (LOCKED):
  - Tee at BOTTOM, flight runs UP (away from viewer)
  - Model +y = farther from tee
  - +x = right (RHBH turn/flip) · −x = left (RHBH fade)

THE TWO QUESTIONS (product law):
  1) Does it flip / push RIGHT before the finish?  (turn)
  2) How far LEFT does it fade at the very end?   (fade)

Innova plate truth:
  - Almost every mold finishes with a left tip hook.
  - US: right mid (flip), then left crook — end may still sit right of tee.
  - Straight: little/no right, gentle left finish.
  - OS: little/no right, hard left finish (whole line often lives left).
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
    """Path = (1) right flip amount + (2) left finish amount + carry.

    Q1 flip right  ← turn (and a little speed)
    Q2 fade left   ← fade (plus small natural tip curl)
    """

    def __init__(
        self,
        *,
        length_base: float = 50.0,
        length_speed: float = 6.2,
        length_glide: float = 7.6,
        turn_gain: float = 14.5,
        fade_gain: float = 18.5,
        natural_finish: float = 7.0,
        os_bow_gain: float = 5.5,
        max_abs_x: float = 52.0,
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
        """Q1: flip/right push builds early-mid, freezes before tip."""
        peak = 0.38 + 0.014 * max(0.0, min(6.0, d.speed - 5.0))
        build = _logistic(t, mid=peak * 0.48, k=12.5)
        freeze = 1.0 - 0.22 * _smoothstep(peak, min(0.96, peak + 0.42), t)
        return build * freeze

    def _fade_build(self, t: float, d: Disc) -> float:
        """Q2: quiet early, decisive left crook at the end."""
        fade_n = max(0.0, d.fade)
        mid = 0.70 - 0.02 * min(4.0, fade_n)
        k = 16.0 + 1.3 * min(4.0, fade_n)
        body = _logistic(t, mid=mid, k=k)
        crook = t ** (4.0 - 0.12 * min(3.0, fade_n))
        return 0.58 * body + 0.62 * crook

    def _os_bow(self, t: float, d: Disc) -> float:
        """OS skips the right flip — line lives left (Firebird family)."""
        os = max(0.0, d.fade - max(0.0, -d.turn) * 0.75)
        if os < 0.2:
            return 0.0
        bow = _smoothstep(0.02, 0.40, t) * (0.6 + 0.4 * t)
        return -self.os_bow_gain * os * bow

    def point(self, d: Disc, t: float) -> Point:
        t = _clamp01(t)
        turn_n = float(d.turn)
        fade_n = max(0.0, float(d.fade))

        # Q1 — flip right
        flip_x = (-turn_n) * self.turn_gain * self._turn_build(t, d)
        if turn_n <= -3.0:
            mid_bulge = math.sin(math.pi * _clamp01(t / 0.90)) ** 1.05
            flip_x *= 0.86 + 0.32 * mid_bulge

        if d.speed >= 11 and -1.3 <= turn_n <= 0.0 and fade_n >= 2.5:
            early = 1.0 - _smoothstep(0.0, 0.30, t)
            flip_x *= 1.0 - 0.50 * early

        # Q2 — finish left
        finish_w = self._fade_build(t, d)
        fade_x = -fade_n * self.fade_gain * finish_w
        natural_x = -self.natural_finish * (1.0 - 0.12 * min(4.0, fade_n)) * finish_w
        bow_x = self._os_bow(t, d)

        x = flip_x + fade_x + natural_x + bow_x
        if abs(x) > self.max_abs_x:
            x = math.copysign(self.max_abs_x + (abs(x) - self.max_abs_x) * 0.18, x)

        return (x, t * self.length(d))

    def path(self, d: Disc, n: int = 72) -> List[Point]:
        if n < 2:
            n = 2
        return [self.point(d, i / (n - 1)) for i in range(n)]

    def shape_metrics(self, d: Disc) -> dict:
        """The two questions, quantified."""
        pts = self.path(d, 80)
        xs = [p[0] for p in pts]
        max_right = max(xs)
        flip = max(0.0, max_right)
        i0 = int(0.85 * (len(xs) - 1))
        tip_dx = xs[-1] - xs[i0]
        return {
            "flip_right": round(flip, 2),
            "finish_x": round(xs[-1], 2),
            "tip_dx": round(tip_dx, 2),
            "flips": flip > 1.5,
        }

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
