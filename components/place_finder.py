"""지역 검색 + 지도 + 목록 — 검진기관 찾기와 인증 꽃집 찾기에서 함께 씁니다.

흐름:  검색어 입력(또는 '현재 위치' 버튼) → 위치 확인(utils.geo) → 가까운 장소(utils.places) → 지도 + 카드 목록
지금은 모든 단계가 mock(샘플 데이터·간이 위치 사전)이에요. 실제 API 를 붙이는 방법은 README 를 보세요.
"""
from __future__ import annotations

import streamlit as st

from components.layout import badge, h
from components.map_view import hours_label, link_html, render_place_map
from config import pages as P
from utils import geo, places as places_util
from utils.places import Place

_TEXT = {
    "clinic": {"label": "지역 또는 장소 검색", "unit": "검진기관", "noun": "검진기관"},
    "flower": {"label": "지역 또는 장소 검색", "unit": "인증 꽃집", "noun": "꽃집"},
}


_SEOUL_GUIDE = """
<div class="pr-card" style="margin:.2rem 0 1rem">
  <div class="pr-card__title" style="font-size:1.05rem">🧭 이렇게 이용해보세요</div>
  <p><b>① 구 고르기</b> — 아래에서 사는 곳(또는 일하는 곳)의 <b>구</b>를 눌러요. 더 가까운 병원을 보고 싶다면 동네·역 이름으로 검색해도 돼요.</p>
  <p><b>② 지도에서 병원 확인</b> — 🩺 표시가 일반건강검진을 받을 수 있는 병원이에요. 🔵 파란 점은 내가 고른 위치예요. 🩺를 누르면 이름·전화번호가 나와요.</p>
  <p><b>③ 병원 선택하기</b> — 아래 목록에서 가까운 순서로 볼 수 있어요. ‘길찾기’로 가는 방법도 확인해요.</p>
  <p style="color:var(--muted);font-size:.88rem;margin-top:.5rem">
     ※ <b>일반건강검진</b>은 건강보험공단이 지정한 병원에서 받는 기본 검진이에요. 병원 방문 전 <b>전화로 예약과 진료시간</b>을 꼭 확인해주세요.</p>
</div>
"""


def _card(place: Place, kind: str) -> str:
    tags = [badge("샘플", "sample")] if place.is_sample else []
    if kind == "clinic" and not place.is_sample:
        tags.append(badge("일반건강검진 가능", "ok"))
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


def _render_flower_shortcut(clinics: list[Place], key: str) -> None:
    """검진 받은 병원을 고르면, 그 병원 위치를 기준으로 인증 꽃집 화면을 열어줘요."""
    by_id = {p.id: p for p in clinics}
    with st.container(key=f"{key}-flower-shortcut"):
        st.html('<p style="margin:1rem 0 .2rem"><b>💐 검진을 받았나요? 그 병원 근처에서 꽃집을 찾아보세요</b></p>')
        picked_col, button_col = st.columns([3, 1.6], vertical_alignment="bottom")
        picked_id = picked_col.selectbox(
            "검진 받은 병원",
            list(by_id),
            format_func=lambda pid: f"{by_id[pid].name} ({by_id[pid].district})",
            key=f"{key}_picked_clinic",
        )
        if button_col.button("💐 근처 꽃집 찾기", type="primary", key=f"{key}_to_flowers", use_container_width=True):
            clinic = by_id[picked_id]
            st.session_state["flower_location"] = geo.location_from_place(clinic.name, clinic.lat, clinic.lon)
            st.switch_page(P.FLOWER_SHOPS)


def render_place_finder(kind: str, key: str, example_hint: str, limit: int = 8, region: str | None = None) -> None:
    """region='서울' 이면 '구 선택 → 동네 검색' 방식으로 서울 안에서만 찾습니다."""
    text = _TEXT[kind]
    loc_key = f"{key}_location"
    seoul = region == "서울"
    gu_key = f"{key}_gu"
    if loc_key not in st.session_state:
        st.session_state[loc_key] = geo.default_location()

    # ── 서울 안내: 사용 방법 + 구 바로 선택 ──────────────────────
    if seoul:
        st.html(_SEOUL_GUIDE)
        picked = st.pills("📍 ① 어느 구에서 찾을까요?", list(geo.SEOUL_DISTRICTS), key=gu_key)
        applied_key = f"{key}_gu_applied"
        if picked != st.session_state.get(applied_key):
            st.session_state[applied_key] = picked
            if picked:
                st.session_state[loc_key] = geo.district_location(picked)
                st.session_state[f"{key}_query"] = ""  # 구를 바꾸면 이전 검색어는 지워요

    # ── 검색 ─────────────────────────────────────────────
    with st.form(f"{key}-search", border=False):
        input_col, button_col = st.columns([4, 1.2], vertical_alignment="bottom")
        label = (
            f"② {st.session_state.get(gu_key)} 안의 동네·역·건물 이름으로 더 가까운 곳 찾기 (선택)"
            if seoul and st.session_state.get(gu_key)
            else ("② 서울 안의 동네·역·건물 이름으로 직접 찾기" if seoul else text["label"])
        )
        query = input_col.text_input(label, placeholder=example_hint, key=f"{key}_query")
        submitted = button_col.form_submit_button("🔍 검색", type="primary", use_container_width=True)
    if not seoul and st.button("📍 현재 위치로 찾기 (모의 위치)", key=f"{key}_gps", help="실제 GPS 는 사용하지 않고 서울시청 부근을 현재 위치로 가정해요."):
        st.session_state[loc_key] = geo.mock_current_location()
        submitted = False
    elif submitted:
        if not query.strip():
            st.info(f"검색어를 입력해주세요. 예: {example_hint.removeprefix('예: ')}")
        elif seoul:
            gu = st.session_state.get(gu_key)
            found = geo.search_in_seoul(query, gu)
            if found is None:
                where = gu or "서울"
                st.warning(f"‘{query.strip()}’ 을(를) {where}에서 찾지 못했어요. {where} 안의 동네·역·건물 이름으로 검색하거나, 위에서 다른 구를 눌러보세요.")
            else:
                st.session_state[loc_key] = found
        else:
            found = geo.search_location(query)
            if found is None:
                st.warning(f"‘{query.strip()}’ 지역을 찾지 못했어요. 이 샘플 버전은 서울 자치구와 주요 지역만 알아요. (예: {geo.KNOWN_EXAMPLES})")
            else:
                st.session_state[loc_key] = found

    # ── 결과 ─────────────────────────────────────────────
    location: geo.GeoResult = st.session_state[loc_key]
    if location.kind == "default" and seoul:
        st.caption("지금은 서울시청 근처를 기준으로 보여드려요. 위에서 내가 사는 구를 눌러보세요.")
    elif location.kind == "default":
        st.caption("검색어를 입력하지 않으면 서울시청 부근을 기준으로 보여드려요.")
    elif location.kind == "clinic" and kind == "flower":
        st.caption("검진 받은 병원을 기준으로 보여드려요. 다른 곳을 보려면 위에서 지역을 검색해보세요.")
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
    if kind == "clinic":
        _render_flower_shortcut(nearby, key)
    st.html('<div class="pr-grid" style="margin-top:1rem">' + "".join(_card(p, kind) for p in nearby) + "</div>")
