"""서울시 인증 꽃집 — 지도 검색 · 꽃 받는 방법 · 캠페인 꽃(데이지) 소개."""
import streamlit as st

from components import flower_card, layout
from components.place_finder import render_place_finder
from config import campaign as C
from config import pages as P

layout.page_header(
    "FLOWER SHOPS",
    "서울시 인증 꽃집 🌼",
    "건강검진과 설문조사를 완료했다면<br>가까운 인증 꽃집에서 캠페인 꽃을 받아가세요.",
    icon="💐",
)

layout.notice(
    f"꽃 받기 이벤트는 <b>{C.TARGET_LABEL} 청년</b>이 대상이에요. 꽃집 위치와 지도는 나이와 상관없이 누구나 볼 수 있어요.",
    kind="info",
    icon="🌼",
)

# ── 꽃 받는 방법 ─────────────────────────────────────────
st.html(
    """
    <div class="pr-grid">
      <div class="pr-card"><div class="pr-card__title">1️⃣ 설문 마치고 QR 발급</div>
        <p>사전·사후 설문을 모두 마치면 ‘꽃 수령 인증 QR’을 받을 수 있어요.</p></div>
      <div class="pr-card"><div class="pr-card__title">2️⃣ 인증 꽃집 방문</div>
        <p>아래 지도에서 가까운 인증 꽃집을 찾아 방문해요.</p></div>
      <div class="pr-card"><div class="pr-card__title">3️⃣ QR 보여주고 꽃 받기</div>
        <p>직원에게 QR을 보여주면 확인 후 데이지를 건네드려요. (QR은 1회만 사용돼요)</p></div>
    </div>
    """
)
st.write("")
layout.cta_link(P.SURVEY, "📝 설문하고 꽃 받을 QR 만들기 →", "flowers-survey")

# ── 지도 검색 ────────────────────────────────────────────
layout.section_title("가까운 인증 꽃집 찾기", "지역이나 장소를 검색하면 주변 꽃집을 지도에 표시해요. 마커를 누르면 자세한 정보가 나와요.")
render_place_finder("flower", key="flower", example_hint="예: 강남구, 홍대입구, 서울시청")

# ── 캠페인 꽃 ────────────────────────────────────────────
layout.section_title("제1회 캠페인 꽃")
flower_card.render_flower_card()
