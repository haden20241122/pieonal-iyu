"""꽃·풀밭 일러스트(SVG)를 코드로 그립니다 — 이미지 파일 없이도 선명하고 용량이 작아요.

`data_uri(svg)` 로 바꿔서 <img src="..."> 에 넣어 사용합니다. (st.html 은 인라인 SVG 를 걸러내서 꼭 <img> 로 써야 해요.)
움직임(피어남·살랑임)은 SVG 안의 <style> 에 들어 있어서 <img> 로 불러도 움직여요.

그림 종류
  · daisy_svg()          흰 데이지 한 송이 (아이콘용)
  · daisy_bouquet_svg()  데이지 세 송이 + 봉오리 + 잎 (꽃 소개 카드용, 레퍼런스 사진 느낌)
  · meadow_svg()         풀밭에서 데이지가 하나씩 피어나는 움직이는 그림 (홈 히어로 아래쪽)
  · hills_svg()          이끼 낀 초록 언덕 배경 (홈 히어로·페이지 배너 배경)
"""
from __future__ import annotations

import base64
import math
import random
from functools import lru_cache

# 색 — 차분한 초록 + 흰 데이지 + 노란 꽃술
PETAL_TIP = "#FFFFFF"
PETAL_BASE = "#E8ECDC"
PETAL_EDGE = "#C9D1BD"
CENTER_LIGHT = "#F4CF55"
CENTER_DEEP = "#D49A12"
CENTER_DOT = "#B7800E"
LEAF = "#3E6B3A"
LEAF_DARK = "#2D5230"
LEAF_VEIN = "#6C9A5C"
STEM = "#4F7F45"


def data_uri(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


# ── 데이지 ───────────────────────────────────────────────
def _daisy_defs(uid: str) -> str:
    """꽃잎: 안쪽은 연한 연둣빛 흰색 → 끝은 순백. 꽃술: 금빛 방사형."""
    return (
        f'<linearGradient id="{uid}p" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{PETAL_BASE}"/>'
        f'<stop offset=".55" stop-color="#F8FAF2"/><stop offset="1" stop-color="{PETAL_TIP}"/></linearGradient>'
        f'<radialGradient id="{uid}c" cx=".42" cy=".4" r=".7"><stop offset="0" stop-color="{CENTER_LIGHT}"/>'
        f'<stop offset="1" stop-color="{CENTER_DEEP}"/></radialGradient>'
    )


def _daisy_head(cx: float, cy: float, r: float, rotate: float, uid: str, petals: int = 21, tilt: float = 1.0, seed: int = 1) -> str:
    """흰 데이지 한 송이. 꽃잎 길이·각도를 조금씩 다르게 해서 손으로 그린 듯한 자연스러움을 줘요."""
    rng = random.Random(seed)
    step = 360 / petals
    parts = [f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({rotate}) scale(1 {tilt})">']
    # 꽃술 아래의 옅은 그림자(깊이감)
    parts.append(f'<circle r="{r * 0.3:.1f}" fill="#8A7A3A" opacity=".16"/>')
    for layer in (0, 1):  # 0: 뒤쪽 꽃잎(살짝 회색빛) · 1: 앞쪽 꽃잎
        for i in range(petals):
            a = i * step + (step / 2 if layer == 0 else 0) + rng.uniform(-3.5, 3.5)
            length = r * rng.uniform(0.86, 1.0) * (0.93 if layer == 0 else 1.0)
            w = r * 0.12
            b = r * 0.16
            d = (
                f"M0 {-b:.1f} C {-w * 1.1:.1f} {-b - (length - b) * .25:.1f}, {-w * 1.3:.1f} {-length * .78:.1f}, {-w * .6:.1f} {-length:.1f} "
                f"Q 0 {-length - r * .05:.1f}, {w * .6:.1f} {-length:.1f} "
                f"C {w * 1.3:.1f} {-length * .78:.1f}, {w * 1.1:.1f} {-b - (length - b) * .25:.1f}, 0 {-b:.1f} Z"
            )
            fill = "#E3E8D8" if layer == 0 else f"url(#{uid}p)"
            parts.append(
                f'<g transform="rotate({a:.1f})"><path d="{d}" fill="{fill}" stroke="{PETAL_EDGE}" stroke-width="{max(r * .008, .4):.2f}" stroke-opacity=".7"/>'
                + (
                    f'<path d="M0 {-b - r * .05:.1f} L0 {-length * .86:.1f}" stroke="{PETAL_EDGE}" stroke-width="{max(r * .006, .35):.2f}" opacity=".55"/>'
                    f'<path d="M{-w * .45:.1f} {-b - r * .1:.1f} L{-w * .5:.1f} {-length * .8:.1f} M{w * .45:.1f} {-b - r * .1:.1f} L{w * .5:.1f} {-length * .8:.1f}" '
                    f'stroke="{PETAL_EDGE}" stroke-width="{max(r * .005, .3):.2f}" opacity=".4"/>'
                    if layer == 1
                    else ""
                )
                + "</g>"
            )
    parts.append(f'<circle r="{r * 0.215:.1f}" fill="url(#{uid}c)"/>')
    parts.append(f'<circle r="{r * 0.215:.1f}" fill="none" stroke="{CENTER_DOT}" stroke-width="{r * .02:.2f}" opacity=".5"/>')
    for k in range(34):  # 꽃술의 알갱이
        ang = k * 137.5
        rad = r * 0.17 * math.sqrt((k + 1) / 34)
        parts.append(
            f'<circle cx="{rad * math.cos(math.radians(ang)):.1f}" cy="{rad * math.sin(math.radians(ang)):.1f}" r="{r * .018:.2f}" fill="{CENTER_DOT}" opacity=".5"/>'
        )
    parts.append("</g>")
    return "".join(parts)


@lru_cache(maxsize=None)
def daisy_svg(size: int = 200) -> str:
    """흰 데이지 한 송이."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="{size}" height="{size}">'
        f"<defs>{_daisy_defs('d1')}</defs>{_daisy_head(100, 100, 92, 6, 'd1')}</svg>"
    )


@lru_cache(maxsize=None)
def gerbera_svg(size: int = 200) -> str:
    """(이전 이름 호환) 같은 흰 데이지를 돌려줘요."""
    return daisy_svg(size)


# ── 잎 ───────────────────────────────────────────────────
def _lobed_leaf(x: float, y: float, length: float, angle: float, fill: str = LEAF, vein: str = LEAF_VEIN) -> str:
    """가장자리가 깊게 갈라진 데이지 잎. (x, y)가 잎자루, angle 은 위쪽(0°) 기준 기울기."""
    lobes = 5
    right, left = [], []
    for k in range(lobes):
        t = (k + 0.7) / (lobes + 0.5)
        wide = length * 0.3 * math.sin(math.pi * min(t * 1.05, 1)) ** 0.75
        tip = (wide, -length * t)
        notch = (wide * 0.28, -length * (t + 0.5 / (lobes + 0.5)))
        right += [tip, notch]
        left += [(-tip[0], tip[1]), (-notch[0], notch[1])]
    pts = [(0, 0)] + right + [(0, -length)] + list(reversed(left))
    d = "M" + " L".join(f"{px:.1f} {py:.1f}" for px, py in pts) + " Z"
    return (
        f'<g transform="translate({x:.1f} {y:.1f}) rotate({angle})">'
        f'<path d="{d}" fill="{fill}" stroke="{LEAF_DARK}" stroke-width="1.2" stroke-linejoin="round"/>'
        f'<path d="M0 0 L0 {-length * .94:.1f}" stroke="{vein}" stroke-width="1.6" stroke-linecap="round" opacity=".8"/></g>'
    )


def _frond(x: float, y: float, length: float, angle: float, color: str = "#6B9A5A") -> str:
    """깃털처럼 가는 잎(쑥갓처럼 보이는 가는 잎)."""
    parts = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({angle})" stroke="{color}" stroke-linecap="round" fill="none">']
    parts.append(f'<path d="M0 0 L0 {-length:.1f}" stroke-width="1.3"/>')
    n = 11
    for i in range(1, n + 1):
        t = i / (n + 1)
        py = -length * t
        ln = length * 0.2 * (1 - t * 0.75)
        parts.append(f'<path d="M0 {py:.1f} L{-ln:.1f} {py - ln * .7:.1f} M0 {py:.1f} L{ln:.1f} {py - ln * .7:.1f}" stroke-width="1"/>')
    parts.append("</g>")
    return "".join(parts)


def _bud(cx: float, cy: float, r: float, rotate: float) -> str:
    """아직 피지 않은 봉오리."""
    return (
        f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({rotate})">'
        f'<ellipse cx="0" cy="{-r * .1:.1f}" rx="{r * .62:.1f}" ry="{r * .9:.1f}" fill="#FBFCF6" stroke="{PETAL_EDGE}" stroke-width=".8"/>'
        f'<path d="M{-r * .2:.1f} {-r * .85:.1f} Q0 {-r * .3:.1f} {r * .22:.1f} {-r * .85:.1f}" stroke="{PETAL_EDGE}" fill="none" stroke-width=".8"/>'
        f'<path d="M{-r * .58:.1f} {r * .1:.1f} Q0 {r * 1.2:.1f} {r * .58:.1f} {r * .1:.1f} L{r * .4:.1f} {r * .62:.1f} Q0 {r * .85:.1f} {-r * .4:.1f} {r * .62:.1f} Z" '
        f'fill="#6E8F4E" stroke="{LEAF_DARK}" stroke-width=".9"/></g>'
    )


@lru_cache(maxsize=None)
def daisy_bouquet_svg() -> str:
    """꽃 소개 카드용 — 흰 데이지 세 송이와 봉오리, 갈라진 잎, 가는 잎 (레퍼런스 사진 느낌)."""
    stems = (
        ("M205 540 C 200 440, 196 360, 190 300", 5.5),   # 중앙 아래 꽃
        ("M215 540 C 240 420, 280 300, 318 196", 5.5),   # 오른쪽 위 꽃
        ("M200 540 C 190 420, 150 300, 118 150", 5),     # 봉오리
        ("M222 540 C 262 480, 318 430, 338 350", 5),     # 오른쪽 아래 꽃
    )
    stem_html = "".join(f'<path d="{d}" stroke="{STEM}" stroke-width="{w}" fill="none" stroke-linecap="round"/>' for d, w in stems)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 560">'
        f"<defs>{_daisy_defs('b')}</defs>"
        + _frond(180, 470, 150, -38) + _frond(240, 470, 160, 34) + _frond(206, 420, 120, 6)
        + stem_html
        + _lobed_leaf(196, 520, 150, -58) + _lobed_leaf(218, 526, 160, 62)
        + _bud(118, 142, 24, -14)
        + _daisy_head(318, 188, 74, 8, "b", seed=3, tilt=.92)
        + _daisy_head(188, 292, 86, -10, "b", seed=5, tilt=.95)
        + _daisy_head(338, 340, 56, 12, "b", seed=9, tilt=.82)
        + "</svg>"
    )


# ── 풀밭에서 피어나는 데이지 (움직이는 그림) ───────────────────
def meadow_svg() -> str:
    """홈 히어로 아래쪽 — 풀잎이 바람에 살랑이고, 데이지가 줄기를 올리며 차례로 피어나요.

    움직임은 모두 이 그림 안의 <style> 에 있어요. '동작 줄이기' 설정을 켜면 활짝 핀 모습으로 멈춰요.
    """
    rng = random.Random(11)
    ground = 380
    css = (
        ".tuft{animation:wave 5.5s ease-in-out infinite;animation-delay:var(--d,0s)}"
        ".plant{animation:sway 6.5s ease-in-out 2.4s infinite;animation-delay:calc(var(--d,0s) + 2.4s)}"
        ".stem{stroke-dasharray:420;stroke-dashoffset:420;animation:grow 1.5s cubic-bezier(.3,.7,.3,1) forwards;animation-delay:var(--d,0s)}"
        ".leaf{opacity:0;animation:fade .9s ease forwards;animation-delay:calc(var(--d,0s) + .7s)}"
        ".bl{transform-box:fill-box;transform-origin:center;transform:scale(0) rotate(-40deg);"
        "animation:bloom 1.4s cubic-bezier(.2,1.25,.4,1) forwards;animation-delay:calc(var(--d,0s) + .9s)}"
        "@keyframes grow{to{stroke-dashoffset:0}}"
        "@keyframes fade{to{opacity:1}}"
        "@keyframes bloom{to{transform:scale(1) rotate(0)}}"
        "@keyframes wave{0%,100%{transform:rotate(-1.8deg)}50%{transform:rotate(2.2deg)}}"
        "@keyframes sway{0%,100%{transform:rotate(-1.2deg)}50%{transform:rotate(1.4deg)}}"
        "@media (prefers-reduced-motion:reduce){.tuft,.plant{animation:none}.stem{animation:none;stroke-dashoffset:0}"
        ".leaf{animation:none;opacity:1}.bl{animation:none;transform:none}}"
    )
    greens = ["#3F7A40", "#4E8C47", "#5E9B4D", "#2F5E34", "#6FA856"]
    tufts = []
    for k in range(26):  # 풀 다발: 가까운 풀잎 여러 개를 한 묶음으로 같이 흔들어요
        cx = rng.uniform(-10, 1210)
        d = rng.uniform(0, 3)
        blades = []
        for _ in range(rng.randint(5, 8)):
            bx = cx + rng.uniform(-22, 22)
            h = rng.uniform(40, 120)
            lean = rng.uniform(-26, 26)
            blades.append(
                f'<path d="M{bx:.0f} {ground + 4} Q{bx + lean * .3:.0f} {ground - h * .55:.0f}, {bx + lean:.0f} {ground - h:.0f}" '
                f'stroke="{rng.choice(greens)}" stroke-width="{rng.uniform(1.6, 3.2):.1f}" fill="none" stroke-linecap="round" opacity="{rng.uniform(.72, .96):.2f}"/>'
            )
        tufts.append(f'<g class="tuft" style="--d:-{d:.1f}s;transform-origin:{cx:.0f}px {ground}px">{"".join(blades)}</g>')

    # 데이지: (x, 머리 높이 y, 머리 반지름, 지연)
    plants = [(838, 232, 32, .35), (936, 160, 42, .6), (1042, 244, 34, .85), (1120, 186, 38, 1.1), (1182, 290, 24, 1.35)]   # 왼쪽 아래는 안내 문구 자리라 비워둬요
    plant_html = []
    for i, (x, hy, r, d) in enumerate(plants):
        lean = rng.uniform(-24, 24)
        stem = f"M{x} {ground + 8} C {x + lean * .2:.0f} {ground - (ground - hy) * .35:.0f}, {x - lean * .5:.0f} {ground - (ground - hy) * .7:.0f}, {x + lean * .3:.0f} {hy + r * .6:.0f}"
        plant_html.append(
            f'<g class="plant" style="--d:{d}s;transform-origin:{x}px {ground}px">'
            f'<path class="stem" d="{stem}" stroke="{STEM}" stroke-width="{3.2 + r * .04:.1f}" fill="none" stroke-linecap="round"/>'
            f'<g class="leaf">{_lobed_leaf(x, ground - 6, r * 2.1, -52 + i * 6, LEAF, LEAF_VEIN)}{_lobed_leaf(x, ground - 4, r * 1.8, 58 - i * 5, LEAF_DARK, LEAF_VEIN)}</g>'
            f'<g class="bl">{_daisy_head(x + lean * .3, hy, r, rng.uniform(-14, 14), "m", seed=20 + i, tilt=rng.uniform(.86, 1.0))}</g></g>'
        )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 380" preserveAspectRatio="xMidYMax slice">'
        f"<style>{css}</style><defs>{_daisy_defs('m')}</defs>"
        + "".join(tufts[:11]) + "".join(plant_html) + "".join(tufts[11:])
        + "</svg>"
    )


# ── 이끼 낀 초록 언덕 배경 ──────────────────────────────────
@lru_cache(maxsize=None)
def hills_svg() -> str:
    """깊은 초록 언덕 + 풀잎 질감 + 민들레 솜털 + 작은 데이지. 빛이 능선을 따라 흘러요."""
    rng = random.Random(7)
    W, H = 1200, 700
    # 능선 (x, y) — 풀잎을 능선 아래에 배치하는 데 써요
    ridges = {
        "back": [(0, 330), (300, 270), (560, 232), (860, 196), (1200, 150)],
        "mid": [(0, 450), (320, 372), (640, 300), (900, 270), (1200, 238)],
        "front": [(0, 560), (340, 500), (700, 450), (960, 424), (1200, 400)],
    }

    def ridge_y(name: str, x: float) -> float:
        pts = ridges[name]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if x0 <= x <= x1:
                return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        return pts[-1][1]

    strokes = []
    palette = {
        "back": ["#2D5A33", "#376B3B", "#244A2B", "#43793F"],
        "mid": ["#3F7A40", "#4E8C47", "#5C9A4C", "#366B38", "#7AAE58"],
        "front": ["#4E8C47", "#62A150", "#79B25A", "#8FC264", "#3D7A3F"],
    }
    counts = {"back": 140, "mid": 200, "front": 220}
    for name in ("back", "mid", "front"):
        for _ in range(counts[name]):
            x = rng.uniform(0, W)
            y = ridge_y(name, x) + rng.uniform(4, 230) ** 1.0
            if y > H:
                continue
            ln = rng.uniform(7, 20) * (0.8 if name == "back" else 1.0 if name == "mid" else 1.3)
            lean = math.radians(rng.uniform(-24, 24))
            strokes.append(
                f'<path d="M{x:.0f} {y:.0f} l{ln * math.sin(lean):.1f} {-ln * math.cos(lean):.1f}" stroke="{rng.choice(palette[name])}" '
                f'stroke-width="{rng.uniform(1.1, 2.2):.1f}" stroke-linecap="round" opacity="{rng.uniform(.5, .92):.2f}"/>'
            )

    fluff = []  # 민들레 솜털(참고 이미지처럼 풀 위로 솟은 둥근 점들)
    for _ in range(26):
        x = rng.uniform(30, W - 30)
        name = rng.choice(("mid", "front", "front"))
        y = ridge_y(name, x) + rng.uniform(20, 180)
        r = rng.uniform(4, 11)
        top = y - rng.uniform(26, 60)
        fluff.append(
            f'<path d="M{x:.0f} {y:.0f} Q{x + rng.uniform(-6, 6):.0f} {(y + top) / 2:.0f}, {x + rng.uniform(-4, 4):.0f} {top:.0f}" '
            f'stroke="#A9C27E" stroke-width="1" fill="none" opacity=".6"/>'
            f'<circle cx="{x:.0f}" cy="{top:.0f}" r="{r:.1f}" fill="url(#puff)"/>'
        )
    for _ in range(12):  # 풀밭의 작은 흰 데이지
        x = rng.uniform(40, W - 40)
        y = ridge_y("front", x) + rng.uniform(30, 140)
        r = rng.uniform(5, 9)
        fluff.append(
            f'<g transform="translate({x:.0f} {y - 28:.0f})"><path d="M0 28 L0 0" stroke="#A9C27E" stroke-width="1" opacity=".6"/>'
            + "".join(f'<ellipse cx="0" cy="{-r * .7:.1f}" rx="{r * .28:.1f}" ry="{r * .7:.1f}" fill="#F8F6EC" transform="rotate({a})"/>' for a in range(0, 360, 45))
            + f'<circle r="{r * .32:.1f}" fill="#E5B92E"/></g>'
        )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">'
        "<defs>"
        '<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#13291A"/><stop offset="1" stop-color="#21452B"/></linearGradient>'
        '<linearGradient id="gb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2E6036"/><stop offset="1" stop-color="#173621"/></linearGradient>'
        '<linearGradient id="gm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4B8A45"/><stop offset=".55" stop-color="#2F6A38"/><stop offset="1" stop-color="#1D4A2B"/></linearGradient>'
        '<linearGradient id="gf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5FA14E"/><stop offset=".5" stop-color="#3C7C3E"/><stop offset="1" stop-color="#255A31"/></linearGradient>'
        '<radialGradient id="puff"><stop offset="0" stop-color="#FBF7E6"/><stop offset=".65" stop-color="#EFEAD2"/><stop offset="1" stop-color="#EFEAD2" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="sun" cx=".8" cy=".3" r=".6"><stop offset="0" stop-color="#D6EC9A" stop-opacity=".2"/><stop offset="1" stop-color="#D6EC9A" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="vig" cx=".5" cy=".45" r=".78"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".42"/></radialGradient>'
        '<filter id="soft" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="7"/></filter>'
        "</defs>"
        f'<rect width="{W}" height="{H}" fill="url(#bg)"/>'
        '<path d="M0 330 C 200 250, 380 290, 560 232 C 760 168, 960 224, 1200 150 L1200 700 L0 700 Z" fill="url(#gb)"/>'
        '<path d="M0 330 C 200 250, 380 290, 560 232 C 760 168, 960 224, 1200 150" stroke="#A8D070" stroke-opacity=".28" stroke-width="12" fill="none" filter="url(#soft)"/>'
        '<path d="M0 450 C 180 350, 420 390, 640 300 C 840 224, 1020 300, 1200 238 L1200 700 L0 700 Z" fill="url(#gm)"/>'
        '<path d="M0 450 C 180 350, 420 390, 640 300 C 840 224, 1020 300, 1200 238" stroke="#C4E37E" stroke-opacity=".4" stroke-width="14" fill="none" filter="url(#soft)"/>'
        '<path d="M0 560 C 220 472, 460 524, 700 450 C 900 390, 1060 440, 1200 400 L1200 700 L0 700 Z" fill="url(#gf)"/>'
        '<path d="M0 560 C 220 472, 460 524, 700 450 C 900 390, 1060 440, 1200 400" stroke="#D7F08C" stroke-opacity=".32" stroke-width="14" fill="none" filter="url(#soft)"/>'
        + "".join(strokes)
        + "".join(fluff)
        + f'<rect width="{W}" height="{H}" fill="url(#sun)"/><rect width="{W}" height="{H}" fill="url(#vig)"/>'
        "</svg>"
    )
