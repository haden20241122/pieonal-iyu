"""건강검진 알아보기 — 검사항목 · 연령별 건강정보 · 검진기관 찾기 · 결과 확인."""
import streamlit as st

from components import layout
from components.place_finder import render_place_finder
from config import campaign as C
from config import pages as P
from data import health_content as D

layout.page_header(
    "HEALTH CHECK",
    "건강검진 알아보기",
    "어떤 검진이 있는지, 내 연령대에는 무엇을 살펴보면 좋은지, 어디서 받을 수 있는지 한곳에서 확인해요.",
    icon="🩺",
)

# 4개 화면을 pills 로 전환합니다. (탭 대신 쓰는 이유: 지도는 화면에 보일 때만 그려야 정확하고 빨라요)
SECTIONS = ["검사항목", "연령별 건강정보", "검진기관 찾기", "결과 확인"]
section = st.pills("보기 선택", SECTIONS, default=SECTIONS[0], key="health_section", label_visibility="collapsed") or SECTIONS[0]


def _screening_card(item: dict) -> str:
    h = layout.h
    return f"""
    <div class="pr-card">
      <div class="pr-card__title">{h(item["name"])}</div>
      <dl>
        <dt>대상</dt><dd>{h(item["target"])}</dd>
        <dt>설명</dt><dd>{h(item["desc"])}</dd>
        <dt>비용 안내</dt><dd>{h(item["cost"])}</dd>
      </dl>
      {layout.source_line(item["source"], item["verified"])}
    </div>
    """


# ── 1. 검사항목 ────────────────────────────────────────────
if section == "검사항목":
    labels = dict(D.SCREENING_CATEGORIES)
    category = st.pills(
        "검진 종류", list(labels), default="free", format_func=lambda key: labels[key], key="health_category"
    ) or "free"
    items = D.SCREENINGS[category]
    if any(not item["verified"] for item in items):
        layout.notice(
            "검진 대상·주기·비용은 해마다 달라질 수 있어요. 아래 내용은 <b>안내용 예시</b>이니, "
            f'정확한 기준은 <a href="{C.NHIS_URL}" target="_blank" rel="noopener noreferrer">국민건강보험공단</a> 공식 안내에서 꼭 확인해주세요.',
            kind="warn",
            icon="⚠️",
        )
    st.html('<div class="pr-grid">' + "".join(_screening_card(item) for item in items) + "</div>")

# ── 2. 연령별 건강정보 ─────────────────────────────────────
elif section == "연령별 건강정보":
    age = st.pills("연령대", D.AGE_GROUPS, default=D.AGE_GROUPS[0], key="health_age") or D.AGE_GROUPS[0]
    guide = D.AGE_GUIDES[age]
    h = layout.h
    st.html(
        f"""
        <div class="pr-card" style="margin-top:.6rem">
          <div class="pr-eyebrow">{h(age)}</div>
          <div class="pr-card__title" style="font-size:1.5rem">{h(guide["headline"])}</div>
          <dl>
            <dt>🫀 함께 살펴보면 좋은 부위·주제</dt><dd>{layout.chips(guide["parts"], "leaf")}</dd>
            <dt>👀 자주 확인하는 신호</dt><dd>{layout.chips(guide["signals"], "blush")}</dd>
            <dt>📚 알아두면 좋은 질환</dt><dd>{layout.chips(guide["conditions"], "sky")}</dd>
            <dt>🩺 참고할 만한 검진</dt><dd>{layout.chips(guide["screenings"], "daisy")}</dd>
          </dl>
          <p style="margin-top:.9rem">💡 {h(guide["tip"])}</p>
          {layout.source_line(guide["source"], guide["verified"])}
        </div>
        """
    )
    layout.notice(D.DISCLAIMER, kind="info", icon="💬")

# ── 3. 검진기관 찾기 ───────────────────────────────────────
elif section == "검진기관 찾기":
    layout.section_title("주변 건강검진기관 찾기", "지역이나 장소를 검색하면 가까운 검진기관을 지도에 표시해요.")
    render_place_finder("clinic", key="clinic", example_hint="예: 강남구, 홍대입구, 서울시청")

# ── 4. 결과 확인 ───────────────────────────────────────────
else:
    st.html(
        """
        <div class="pr-card">
          <div class="pr-card__title" style="font-size:1.4rem">검진을 받은 뒤에는 결과를 확인해보세요 📄</div>
          <p>건강검진 결과는 국민건강보험공단 등 공식 서비스에서 확인할 수 있어요.
             이 사이트는 개인의 검진 결과를 <b>저장하거나 전달받지 않아요.</b></p>
        </div>
        """
    )
    st.link_button("내 건강검진 결과 확인하기 →", C.NHIS_RESULT_URL, type="primary")
    st.caption("국민건강보험공단 ‘건강검진 실시안내’ 페이지로 이동해요. 사이드 메뉴의 ‘건강검진 결과조회’에서 로그인하면 확인할 수 있어요.")
    st.page_link(P.SURVEY, label="결과를 확인했다면, 사후 설문 참여하기 →")
