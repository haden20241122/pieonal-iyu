"""지도 컴포넌트.

★ 지도 공급자를 바꾸려면 이 파일만 고치면 됩니다.
   - 지금: folium(Leaflet) + 지도 타일. API 키가 필요 없어서 바로 실행돼요.
   - Kakao Map / Naver Map 으로 바꾸려면 `_render_kakao()` 같은 함수를 만들어 `_PROVIDERS` 에 등록하고
     .env 의 MAP_PROVIDER 를 kakao 로 바꾸세요. (README '지도 API 연결' 참고)

화면 코드는 `render_place_map()` 하나만 호출하므로, 공급자가 바뀌어도 다른 파일은 수정하지 않아도 됩니다.
"""
from __future__ import annotations

from typing import Callable
from urllib.parse import quote

import folium
import streamlit as st

from components.embed import embed_html
from components.layout import h
from config import settings
from config.campaign import NHIS_FACILITY_SEARCH_URL
from utils.geo import GeoResult
from utils.places import Place

_PIN_CSS = """
<style>
  .pin { width: 38px; height: 38px; display: grid; place-items: center; font-size: 20px; border-radius: 50%;
         background: #fff; box-shadow: 0 0 0 3px #FFC93C, 0 3px 10px rgba(0,0,0,.25); }
  .pin--clinic { box-shadow: 0 0 0 3px #3E9B6E, 0 3px 10px rgba(0,0,0,.25); }
  .pin--off { filter: grayscale(.9); opacity: .8; box-shadow: 0 0 0 3px #BBB, 0 3px 10px rgba(0,0,0,.2); }
  .pin--me { background: #2F6DA8; color: #fff; box-shadow: 0 0 0 4px rgba(47,109,168,.3); font-size: 18px; }
  .leaflet-popup-content { font-family: 'Noto Sans KR','Malgun Gothic',sans-serif; font-size: 13px; line-height: 1.55; margin: 12px 14px; }
  .pp .t { font-weight: 700; font-size: 15px; margin-bottom: 4px; }
  .pp .r { color: #33443c; }
  .pp .b { display: inline-block; font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 99px; margin-left: 4px;
           background: #FDEEEB; color: #B0523F; border: 1px dashed #E7A79B; vertical-align: middle; }
  .pp .ok { color: #2A7A55; font-weight: 700; } .pp .off { color: #8a7a3a; font-weight: 700; }
  .pp .l { margin-top: 6px; } .pp .l a { color: #2A7A55; font-weight: 700; margin-right: 10px; text-decoration: none; }
</style>
"""


def hours_label(kind: str) -> str:
    return "영업시간" if kind == "flower" else "진료시간"


def route_url(place: Place) -> str:
    """길찾기 링크 (Kakao 지도 '도착지' 링크 — 별도 API 키 없이 동작)."""
    return f"https://map.kakao.com/link/to/{quote(place.name)},{place.lat},{place.lon}"


def detail_link(place: Place, kind: str) -> tuple[str, str] | None:
    """(주소, 표시 문구) 홈페이지/상세정보 링크. 보여줄 링크가 없으면 None.

    · 등록된 주소가 있으면 그대로 연결
    · 검진기관인데 주소가 없으면 공단의 '검진기관 찾기'로 연결
    · 꽃집은 공식 상세 페이지가 없으면 링크를 만들지 않아요 (엉뚱한 곳으로 보내지 않기 위해)
    """
    if place.url:
        return place.url, "상세정보"
    if kind == "clinic":
        return NHIS_FACILITY_SEARCH_URL, "공단 검진기관 찾기"
    return None


def link_html(place: Place, kind: str, separator: str) -> str:
    """길찾기 + (있으면) 상세정보 링크 묶음."""
    links = [f'<a href="{h(route_url(place))}" target="_blank" rel="noopener noreferrer">길찾기</a>']
    detail = detail_link(place, kind)
    if detail:
        links.append(f'<a href="{h(detail[0])}" target="_blank" rel="noopener noreferrer">{h(detail[1])}</a>')
    return separator.join(links)


def _popup_html(place: Place, kind: str) -> str:
    rows = [f'<div class="t">{h(place.name)}{"<span class=b>샘플</span>" if place.is_sample else ""}</div>']
    rows.append(f'<div class="r">📍 {h(place.address)}</div>')
    rows.append(f'<div class="r">☎ {h(place.phone)}</div>')
    if place.hours:
        rows.append(f'<div class="r">🕘 {hours_label(kind)} {h(place.hours)}</div>')
    if kind == "clinic" and place.info:
        rows.append(f'<div class="r">🩺 {h(place.info)}</div>')
    if kind == "flower":
        status = '<span class="ok">참여 중 (꽃 수령 가능)</span>' if place.campaign_active else '<span class="off">참여 준비 중</span>'
        rows.append(f'<div class="r">🌼 캠페인 참여: {status}</div>')
    rows.append(f'<div class="l">{link_html(place, kind, " ")}</div>')
    return '<div class="pp">' + "".join(rows) + "</div>"


def _render_folium(places: list[Place], center: GeoResult, kind: str, height: int) -> None:
    fmap = folium.Map(
        location=[center.lat, center.lon],
        zoom_start=14,
        # API 키 없이 쓸 수 있는 OpenStreetMap 타일. 프로토타입·소규모용이에요.
        # 실제 서비스 트래픽에는 Kakao/Naver 등 정식 지도 API 를 쓰세요. (README 참고)
        tiles="OpenStreetMap",
        scrollWheelZoom=False,  # 페이지를 스크롤할 때 지도가 확대/축소되지 않게
        control_scale=True,
    )
    fmap.get_root().header.add_child(folium.Element(_PIN_CSS))

    bounds = [[center.lat, center.lon]]
    folium.Marker(
        [center.lat, center.lon],
        tooltip=f"검색 위치: {center.label}",
        icon=folium.DivIcon(html='<div class="pin pin--me">●</div>', icon_size=(38, 38), icon_anchor=(19, 19)),
    ).add_to(fmap)

    for place in places:
        emoji = "🩺" if kind == "clinic" else "🌼"
        css = "pin pin--clinic" if kind == "clinic" else ("pin" if place.campaign_active else "pin pin--off")
        folium.Marker(
            [place.lat, place.lon],
            tooltip=place.name,
            popup=folium.Popup(_popup_html(place, kind), max_width=300),
            icon=folium.DivIcon(html=f'<div class="{css}">{emoji}</div>', icon_size=(38, 38), icon_anchor=(19, 19)),
        ).add_to(fmap)
        bounds.append([place.lat, place.lon])

    if len(bounds) > 1:
        fmap.fit_bounds(bounds, padding=(36, 36), max_zoom=16)
    embed_html(fmap.get_root().render(), height=height)


# 공급자 이름 → 그리기 함수. Kakao/Naver 를 연결하면 여기에 등록하세요.
_PROVIDERS: dict[str, Callable[[list[Place], GeoResult, str, int], None]] = {
    "folium": _render_folium,
}


def render_place_map(places: list[Place], center: GeoResult, kind: str, height: int = 440) -> None:
    """검색 위치(center)와 장소들을 지도에 marker 로 표시합니다. kind: 'clinic' | 'flower'"""
    renderer = _PROVIDERS.get(settings.MAP_PROVIDER)
    if renderer is None:
        st.caption(f"‘{settings.MAP_PROVIDER}’ 지도는 아직 연결되지 않아 기본 지도로 보여드려요.")
        renderer = _render_folium
    try:
        renderer(places, center, kind, height)
    except Exception:  # 지도 로딩에 실패해도 아래 목록은 계속 보이도록
        st.warning("지도를 불러오지 못했어요. 아래 목록에서 장소를 확인해주세요.")
