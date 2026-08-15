"""discwhich flight paths — grounded in disc flight dynamics + Innova plate grammar.

Convention (LOCKED):
  Tee at BOTTOM, flight UP. +x = RHBH right (turn). −x = RHBH left (fade).

Physics grammar (RHBH):
  1. High-speed phase: understable turn can push RIGHT (flip).
  2. Low-speed phase: fade ALWAYS pulls LEFT.
  3. Once fade owns the line, it does NOT straighten out — tip keeps hooking left.
  4. OS molds: little/no right; continuous left bow into a left finish.
  5. Straight molds: nearly vertical, small left finish only.
  6. US molds: right mid, then left crook; tip still leftward.

Innova plates: paths are mostly VERTICAL. Lateral motion is modest
(roughly ~8–20% of path length), smooth, no wild swings.
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


def _clamp(x: float, a: float = 0.0, b: float = 1.0) -> float:
    return min(b, max(a, x))


class PathModel:
    """Integrate lateral rate: turn early, fade late, fade never reverses or flattens to straight.

    x'(t) = turn_rate(t) + fade_rate(t)
      turn_rate ≥ 0 pushes right when mold turn is negative (US)
      fade_rate ≤ 0 always pulls left, and |fade_rate| grows through the finish
    """

    def __init__(
        self,
        *,
        length_base: float = 100.0,
        length_per_speed: float = 8.0,
        length_per_glide: float = 6.0,
        # modest lateral — Innova lines stay mostly vertical
        turn_gain: float = 0.38,
        fade_gain: float = 0.48,
        natural_fade: float = 0.06,
        os_bias_gain: float = 0.16,
        integrate_scale: float = 72.0,
    ) -> None:
        self.length_base = length_base
        self.length_per_speed = length_per_speed
        self.length_per_glide = length_per_glide
        self.turn_gain = turn_gain
        self.fade_gain = fade_gain
        self.natural_fade = natural_fade
        self.os_bias_gain = os_bias_gain
        self.integrate_scale = integrate_scale

    def length(self, d: Disc) -> float:
        sp = d.speed if d.speed <= 12 else 12 + 0.4 * (d.speed - 12)
        bonus = 0.0
        if d.turn <= -2 and d.glide >= 5:
            bonus = 4.0 + (-d.turn - 2) * 1.5
        return self.length_base + self.length_per_speed * sp + self.length_per_glide * d.glide + bonus

    def _turn_rate_weight(self, t: float, d: Disc) -> float:
        """High-speed turn: rises after release, peaks mid-early, dies before finish.

        Must be ~0 at t→1 so we never get rightward motion in the fade phase.
        """
        # bell peaking ~0.35–0.45 depending on speed
        peak = 0.34 + 0.012 * max(0.0, min(5.0, d.speed - 6.0))
        # gaussian-like
        width = 0.22
        w = math.exp(-0.5 * ((t - peak) / width) ** 2)
        # hard kill in last 25% — fade owns the end
        kill = 1.0 - _clamp((t - 0.72) / 0.20)
        return max(0.0, w * kill)

    def _fade_rate_weight(self, t: float, d: Disc) -> float:
        """Low-speed fade: near 0 early, ramps up, STAYS ON through the tip.

        Critical: weight is still increasing or high at t=1 — never drops back
        (that was the bug: left hook then straight vertical tip).
        """
        # smooth ramp starting mid-late
        # use t^n so derivative stays positive at end
        fade_n = max(0.0, d.fade)
        # higher fade starts a hair earlier
        start = 0.45 - 0.03 * min(3.0, fade_n)
        u = _clamp((t - start) / max(0.05, 1.0 - start))
        # ease-in then keep climbing (no plateau-to-zero)
        # u^2 early, mix with u so end still has slope
        return 0.35 * u * u + 0.65 * (u ** 1.35)

    def lateral_rate(self, d: Disc, t: float) -> float:
        """dx/dt in model units. Right positive, left negative."""
        t = _clamp(t)
        turn_n = float(d.turn)  # negative = US
        fade_n = max(0.0, float(d.fade))

        # Turn contributes RIGHT when turn_n is negative: rate = (-turn_n) * weight >= 0
        turn_rate = (-turn_n) * self.turn_gain * self._turn_rate_weight(t, d)

        # Fade always LEFT — stays on through tip (never straighten-out)
        fade_strength = fade_n * self.fade_gain + self.natural_fade
        if turn_n <= -1:
            # US still shows a left tip crook after flip
            fade_strength += 0.10 * min(3.0, -turn_n)
        if fade_n >= 3 and turn_n >= -0.5:
            fade_strength *= 1.12
        fade_rate = -fade_strength * self._fade_rate_weight(t, d)

        # OS bias: continuous gentle left during flight (Firebird family never flips right)
        os = max(0.0, fade_n - max(0.0, -turn_n) * 0.8)
        os_rate = 0.0
        if os > 0.25:
            # gentle left through middle of flight
            mid = math.sin(math.pi * t)  # 0 at ends, 1 mid — but we want some at end too
            # prefer steady left pressure after t>0.15
            press = _clamp((t - 0.12) / 0.5)
            os_rate = -self.os_bias_gain * os * (0.5 * press + 0.5 * press * press)

        # Destroyer-class: suppress early turn so line stays tight then dumps left
        if d.speed >= 11 and -1.25 <= turn_n <= 0 and fade_n >= 2.5:
            turn_rate *= 0.45

        return turn_rate + fade_rate + os_rate

    def path(self, d: Disc, n: int = 80) -> List[Point]:
        if n < 2:
            n = 2
        L = self.length(d)
        xs = [0.0]
        # integrate rate with simple RK-ish steps along t
        for i in range(1, n):
            t0 = (i - 1) / (n - 1)
            t1 = i / (n - 1)
            dt = t1 - t0
            # midpoint rule
            r_mid = self.lateral_rate(d, 0.5 * (t0 + t1))
            xs.append(xs[-1] + r_mid * dt * self.integrate_scale)

        # light end clamp only if absurd
        pts: List[Point] = []
        for i, x in enumerate(xs):
            t = i / (n - 1)
            if abs(x) > 36:
                x = math.copysign(36 + (abs(x) - 36) * 0.15, x)
            pts.append((x, t * L))
        return pts

    def shape_metrics(self, d: Disc) -> dict:
        pts = self.path(d, 100)
        xs = [p[0] for p in pts]
        max_r = max(xs)
        min_x = min(xs)
        # tip: last 15% must be leftward (dx < 0)
        i0 = int(0.85 * (len(xs) - 1))
        tip_dx = xs[-1] - xs[i0]
        # check no "straighten after fade": last segment rates should stay <= 0
        last_rates = []
        for i in range(max(1, len(xs) - 10), len(xs)):
            last_rates.append(xs[i] - xs[i - 1])
        return {
            "flip_right": round(max(0.0, max_r), 2),
            "finish_x": round(xs[-1], 2),
            "min_x": round(min_x, 2),
            "tip_dx": round(tip_dx, 2),
            "last_rates_max": round(max(last_rates), 4),
            "flips": max_r > 1.2,
            "lat_span": round(max(xs) - min(xs), 2),
            "lat_over_len": round((max(xs) - min(xs)) / max(1e-6, pts[-1][1]), 3),
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
