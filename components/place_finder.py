"""지역 검색 + 지도 + 목록 — 검진기관 찾기와 인증 꽃집 찾기에서 함께 씁니다.

흐름:  검색어 입력(또는 '현재 위치' 버튼) → 위치 확인(utils.geo) → 가까운 장소(utils.places) → 지도 + 카드 목록
지금은 모든 단계가 mock(샘플 데이터·간이 위치 사전)이에요. 실제 API 를 붙이는 방법은 README 를 보세요.
"""
from __future__ import annotations

import streamlit as st

from components.layout import badge, h
from components.map_view import hours_label, link_html, render_place_map
from utils import geo, places as places_util
from utils.places import Place

_TEXT = {
    "clinic": {"label": "지역 또는 장소 검색", "unit": "검진기관", "noun": "검진기관"},
    "flower": {"label": "지역 또는 장소 검색", "unit": "인증 꽃집", "noun": "꽃집"},
}


def _card(place: Place, kind: str) -> str:
    tags = [badge("샘플", "sample")] if place.is_sample else []
    if kind == "flower":
        tags.append(badge("꽃 수령 가능", "ok") if place.campaign_active else badge("참여 준비 중", "draft"))
    distance = f' · 약 {place.distance_km:.1f}km' if place.distance_km is not None else ""
    extra = ""
    if place.hours:
        extra += f"<p>🕘 {hours_label(kind)} {h(place.hours)}</p>"
    if kind == "clinic" and place.info:
        extra += f"<p>🩺 {h(place.info)}</p>"
    return f"""
    <div class="pr-card">
      <div class="pr-card__title">{h(place.name)}</div>
      <div style="margin-bottom:.3rem">{" ".join(tags)}<span style="color:var(--muted);font-size:.85rem">{h(place.district)}{distance}</span></div>
      <p>📍 {h(place.address)}</p>
      <p>☎ {h(place.phone)}</p>
      {extra}
      <p style="margin-top:.6rem">{link_html(place, kind, " · ")}</p>
    </div>
    """


def render_place_finder(kind: str, key: str, example_hint: str, limit: int = 8) -> None:
    text = _TEXT[kind]
    loc_key = f"{key}_location"
    if loc_key not in st.session_state:
        st.session_state[loc_key] = geo.default_location()

    # ── 검색 ─────────────────────────────────────────────
    with st.form(f"{key}-search", border=False):
        input_col, button_col = st.columns([4, 1.2], vertical_alignment="bottom")
        query = input_col.text_input(text["label"], placeholder=example_hint, key=f"{key}_query")
        submitted = button_col.form_submit_button("🔍 검색", type="primary", use_container_width=True)
    if st.button("📍 현재 위치로 찾기 (모의 위치)", key=f"{key}_gps", help="실제 GPS 는 사용하지 않고 서울시청 부근을 현재 위치로 가정해요."):
        st.session_state[loc_key] = geo.mock_current_location()
        submitted = False
    elif submitted:
        if not query.strip():
            st.info(f"검색어를 입력해주세요. 예: {geo.KNOWN_EXAMPLES}")
        else:
            found = geo.search_location(query)
            if found is None:
                st.warning(f"‘{query.strip()}’ 지역을 찾지 못했어요. 이 샘플 버전은 서울 자치구와 주요 지역만 알아요. (예: {geo.KNOWN_EXAMPLES})")
            else:
                st.session_state[loc_key] = found

    # ── 결과 ─────────────────────────────────────────────
    location: geo.GeoResult = st.session_state[loc_key]
    if location.kind == "default":
        st.caption("검색어를 입력하지 않으면 서울시청 부근을 기준으로 보여드려요.")
    nearby = places_util.find_nearby(kind, location.lat, location.lon, limit=limit)  # type: ignore[arg-type]
    if not nearby:
        st.info(f"표시할 {text['noun']} 정보가 아직 없어요.")
        return

    st.html(f'<p style="margin:.6rem 0 .3rem"><b>📍 {h(location.label)}</b> 주변 {text["unit"]} <b>{len(nearby)}곳</b></p>')
    if places_util.has_sample_data(nearby):
        st.html(
            '<div class="pr-notice pr-notice--warn" style="margin:.2rem 0 .6rem"><span aria-hidden="true">🧪</span>'
            f"<div>표시된 {text['noun']}은 <b>화면 구성을 보여주기 위한 샘플 데이터</b>이며 실제 {text['noun']}이 아닙니다. "
            "실제 API를 연결하면 진짜 정보로 바뀌어요.</div></div>"
        )
    render_place_map(nearby, location, kind)
    st.html('<div class="pr-grid" style="margin-top:1rem">' + "".join(_card(p, kind) for p in nearby) + "</div>")
