"""건강검진 알아보기 — 검사항목 · 연령별 건강정보 · 검진기관 찾기 · 결과 확인.

나이는 이 화면에서 입력받지 않아요. 홈 화면에서 입력한 나이(세션)가 있으면 '내 나이'를 먼저 보여주기만 합니다.
"""
import streamlit as st

from components import layout
from components.age_checker import get_my_age, render_age_card
from components.place_finder import render_place_finder
from config import campaign as C
from config import pages as P
from data import health_content as D

layout.page_header(
    "HEALTH CHECK",
    "건강검진 알아보기",
    "어떤 검진이 있는지, 내 나이에는 뭐가 해당되는지, 어디서 받는지 여기서 한 번에 볼 수 있어요.",
    icon="🩺",
)

# 4개 화면을 pills 로 전환합니다. (탭 대신 쓰는 이유: 지도는 화면에 보일 때만 그려야 정확하고 빨라요)
SECTIONS = ["검사항목", "연령별 건강정보", "검진기관 찾기", "결과 확인"]
# 홈의 버튼에서 특정 탭으로 바로 들어온 경우 (위젯을 만들기 전에 값을 정해야 해요)
st.session_state.setdefault("health_section", SECTIONS[0])
_goto = st.session_state.pop("health_goto", None)
if _goto in SECTIONS:
    st.session_state["health_section"] = _goto
section = st.pills("보기 선택", SECTIONS, key="health_section", label_visibility="collapsed") or SECTIONS[0]


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
        "검진 종류", list(labels), default="general", format_func=lambda key: labels[key], key="health_category"
    ) or "general"
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
    my_age = get_my_age()
    my_band = D.band_for_age(my_age)

    # 건강검진 정보는 나이와 상관없이 누구나 볼 수 있어요 (꽃 받기만 만 19~29세 대상)
    if my_age is None:
        layout.notice(
            "건강검진 정보는 <b>나이와 상관없이 누구나</b> 볼 수 있어요. 홈에서 나이를 알려주면 내 나이대가 먼저 보여요.",
            kind="info",
            icon="🌱",
        )
        layout.cta_link(P.HOME, "🔎 홈에서 내 나이로 확인하기 →", "age-from-home")
    else:
        layout.notice(f"홈에서 알려준 <b>만 {my_age}세</b>는 ‘{my_band}’ 안내에 해당해요.", kind="ok", icon="✅")

    # 나이대를 눌러서 둘러봐요 (나이를 입력하지 않아도 볼 수 있어요)
    st.session_state.setdefault("health_band", my_band or D.DEFAULT_BAND)
    band = st.pills(
        "나이대 보기",
        list(D.AGE_BANDS),
        key="health_band",
        format_func=lambda b: f"{b} · 내 나이" if b == my_band else b,
    ) or (my_band or D.DEFAULT_BAND)
    render_age_card(D.band_guide(band), band)
    if my_age is not None:
        st.caption("정확히 내 나이에 해당하는 검진은 홈 화면의 ‘내 검진 확인하기’에서 볼 수 있어요.")
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
    st.link_button("📄 내 건강검진 결과 확인하기 →", C.NHIS_RESULT_URL, type="primary")
    st.caption("국민건강보험공단 ‘건강검진 실시안내’ 페이지로 이동해요. 사이드 메뉴의 ‘건강검진 결과조회’에서 로그인하면 확인할 수 있어요.")

# ── 다음 행동 ──────────────────────────────────────────────
if section == "결과 확인":
    layout.cta_link(P.SURVEY, "📝 결과를 확인했다면, 사후 설문 하러 가기 →", "health-next")
else:
    layout.cta_link(P.SURVEY, "🌱 검진 받기 전, 사전 설문 시작하기 →", "health-next")
