"""검진기관 찾기 — 서울 25개 구의 일반건강검진 기관을 지도와 목록으로 찾아요."""
import streamlit as st

from components import layout
from components.place_finder import render_place_finder
from config import campaign as C
from config import pages as P
from utils.places import load_places

layout.page_header(
    "FIND A CLINIC",
    "검진기관 찾기",
    "구를 고르면 서울 안의 가까운 일반건강검진 기관을 지도에 표시해요.",
    icon="📍",
)

layout.notice(
    f"서울 25개 구의 일반건강검진 기관 <b>{len(load_places('clinic')):,}곳</b>을 지도에서 볼 수 있어요. "
    "서울 밖 지역은 아래 ‘공단 검진기관 찾기’에서 확인해주세요.",
    kind="info",
    icon="📍",
)
render_place_finder("clinic", key="clinic", example_hint="예: 성신여대입구, 강남역, 홍대입구", limit=10, region="서울")
st.html(
    f'<p style="margin:.4rem 0"><a href="{C.NHIS_FACILITY_SEARCH_URL}" target="_blank" rel="noopener noreferrer">'
    "🔎 서울 밖 지역은 국민건강보험공단 검진기관 찾기에서 확인하기</a></p>"
)
st.caption(
    "출처: 국민건강보험공단 검진기관별 검진유형내역(2025-10-31 기준, 일반건강검진 가능 기관) · "
    "주소·전화·위치는 카카오 지도 검색 결과예요. 방문 전 기관에 검진 가능 여부와 진료시간을 확인해주세요."
)

layout.cta_link(P.SURVEY, "🌱 검진 받기 전, 사전 설문 시작하기 →", "clinics-next")
