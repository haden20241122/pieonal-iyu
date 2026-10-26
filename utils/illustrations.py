"""꽃 일러스트(SVG)를 코드로 그립니다 — 이미지 파일 없이도 선명하고 용량이 작아요.

`data_uri(svg)` 로 바꿔서 <img src="..."> 에 넣어 사용합니다.
색을 바꾸고 싶다면 아래 상수만 고치세요.
"""
from __future__ import annotations

import base64
from functools import lru_cache

PETAL = "#FFFFFF"
PETAL_EDGE = "#EBDDB0"
PETAL_BLUSH = "#FBE3DF"
CENTER = "#FFC93C"
CENTER_DEEP = "#EBA300"
LEAF = "#3E9B6E"
LEAF_DARK = "#2A7A55"
STEM = "#4FAE7F"


def data_uri(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


def _daisy_head(cx: float, cy: float, r: float, rotate: float = 0.0, petals: int = 14) -> str:
    """데이지 꽃송이 하나 (r = 꽃송이 반지름)."""
    parts = [f'<g transform="translate({cx} {cy}) rotate({rotate})">']
    step = 360 / petals
    length, width = r * 0.62, r * 0.17
    # 뒤쪽 꽃잎(살짝 분홍빛) → 앞쪽 꽃잎(흰색) 순서로 겹쳐 깊이감을 줌
    for layer, (offset, scale, fill) in enumerate([(step / 2, 0.92, PETAL_BLUSH), (0, 1.0, PETAL)]):
        for i in range(petals):
            angle = i * step + offset
            parts.append(
                f'<ellipse cx="0" cy="{-r * 0.56 * scale:.2f}" rx="{width:.2f}" ry="{length * scale:.2f}" '
                f'fill="{fill}" stroke="{PETAL_EDGE}" stroke-width="{max(r * 0.012, 0.6):.2f}" '
                f'transform="rotate({angle:.2f})"/>'
            )
    parts.append(f'<circle r="{r * 0.27:.2f}" fill="{CENTER}"/>')
    parts.append(f'<circle r="{r * 0.27:.2f}" fill="none" stroke="{CENTER_DEEP}" stroke-width="{r * 0.03:.2f}"/>')
    for dx, dy in [(-0.09, -0.07), (0.08, -0.09), (0.02, 0.08), (-0.07, 0.06), (0.1, 0.03)]:
        parts.append(f'<circle cx="{dx * r:.2f}" cy="{dy * r:.2f}" r="{r * 0.028:.2f}" fill="{CENTER_DEEP}" opacity=".55"/>')
    parts.append("</g>")
    return "".join(parts)


@lru_cache(maxsize=None)
def daisy_svg(size: int = 200) -> str:
    """데이지 한 송이."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="{size}" height="{size}">'
        f"{_daisy_head(100, 100, 92, 4)}</svg>"
    )


@lru_cache(maxsize=None)
def hero_bouquet_svg() -> str:
    """히어로 영역용 — 줄기와 잎이 있는 데이지 세 송이."""
    leaf = lambda d, fill: f'<path d="{d}" fill="{fill}"/>'  # noqa: E731
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 420" width="400" height="420">'
        # 줄기
        f'<path d="M200 400 C 196 330, 200 270, 196 210" stroke="{STEM}" stroke-width="7" fill="none" stroke-linecap="round"/>'
        f'<path d="M198 380 C 160 330, 118 290, 100 240" stroke="{STEM}" stroke-width="6" fill="none" stroke-linecap="round"/>'
        f'<path d="M202 370 C 250 320, 292 280, 306 214" stroke="{STEM}" stroke-width="6" fill="none" stroke-linecap="round"/>'
        # 잎
        + leaf("M197 340 C 150 350, 118 330, 108 300 C 150 296, 184 310, 197 340 Z", LEAF)
        + leaf("M203 330 C 250 342, 288 322, 300 290 C 256 286, 216 298, 203 330 Z", LEAF_DARK)
        + leaf("M200 395 C 172 372, 150 372, 130 386 C 156 402, 184 404, 200 395 Z", LEAF_DARK)
        # 꽃송이 (뒤 → 앞)
        + _daisy_head(100, 214, 62, -10)
        + _daisy_head(306, 190, 70, 12)
        + _daisy_head(196, 130, 96, 4)
        + "</svg>"
    )


@lru_cache(maxsize=None)
def scatter_daisy_svg(size: int = 64) -> str:
    """장식용 작은 데이지."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="{size}" height="{size}">'
        f"{_daisy_head(50, 50, 46, 8, petals=12)}</svg>"
    )


@lru_cache(maxsize=None)
def logo_svg() -> str:
    """상단 로고용 아이콘."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="96" height="96">'
        f"{_daisy_head(50, 50, 47, 0, petals=12)}</svg>"
    )
