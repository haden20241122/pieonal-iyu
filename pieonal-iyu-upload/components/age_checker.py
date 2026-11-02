"""홈 화면의 '내 나이로 검진 확인' — 나이를 입력하면 그 나이에 해당하는 검진을 바로 보여줘요.

어느 나이든 이용할 수 있어요. 꽃 받기 이벤트만 만 19~29세 청년 대상이고, 그 여부는 결과 아래에 따로 알려줘요.
입력한 나이는 이 브라우저 세션에서만 쓰여요. 건강검진 알아보기 화면은 이 값을 읽어서 '내 나이대'를 먼저 보여주기만 하고,
나이를 입력받는 곳은 홈 한 곳뿐이에요.
"""
from __future__ import annotations

import streamlit as st

from components import layout
from config import campaign as C
from config import pages as P
from data import health_content as D

MY_AGE_KEY = "my_age"  # 입력 위젯의 key 가 아닌 별도 값 (화면을 옮겨도 사라지지 않게)


def get_my_age() -> int | None:
    value = st.session_state.get(MY_AGE_KEY)
    return int(value) if value is not None else None


def render_age_card(guide: dict, label: str) -> None:
    """나이(구간)별 검진 안내 카드."""
    h = layout.h
    extras = (
        layout.chips(guide["extras"], "leaf")
        if guide["extras"]
        else '<span style="color:var(--muted)">이 나이에는 따로 받는 추가 항목이 없어요.</span>'
    )
    st.html(
        f"""
        <div class="pr-card" style="margin-top:.6rem">
          <div class="pr-eyebrow">{h(label)}</div>
          <div class="pr-card__title" style="font-size:1.5rem">{h(guide["headline"])}</div>
          <dl>
            <dt>🩺 해당하는 검진</dt><dd>{layout.chips(guide["screenings"], "daisy")}</dd>
            <dt>📅 나이에 따라 받는 추가 항목</dt><dd>{extras}</dd>
          </dl>
          <p style="margin-top:.9rem">💡 {h(guide["tip"])}</p>
          {layout.source_line(guide["source"], guide["verified"])}
        </div>
        """
    )


def _go_health(section: str) -> None:
    """건강검진 알아보기의 특정 탭으로 바로 이동."""
    st.session_state["health_goto"] = section
    st.switch_page(P.HEALTH)


def render_age_checker() -> None:
    with st.container(key="age-checker"):
        st.html(
            '<div class="pr-eyebrow">🔎 나에게 맞는 검진 찾기</div>'
            '<h2 class="pr-agecheck__title">몇 살이에요? 나이만 알려주세요</h2>'
            '<p class="pr-agecheck__desc">나이를 알려주면 지금 받을 수 있는 검진을 바로 보여드려요. 몇 살이든 괜찮아요.</p>'
        )
        with st.form("age-form", border=False):
            input_col, button_col = st.columns([3, 1.5], vertical_alignment="bottom")
            typed = input_col.number_input(
                "내 나이 (만 나이)",
                min_value=0,
                max_value=120,
                value=get_my_age(),
                step=1,
                placeholder=f"예: {C.TARGET_AGE_MIN + 5}",
            )
            submitted = button_col.form_submit_button("🔎 내 검진 확인하기", type="primary", use_container_width=True)
        if submitted:
            st.session_state[MY_AGE_KEY] = int(typed) if typed is not None else None
            if typed is None:
                st.info("나이를 입력하고 버튼을 눌러주세요 🙂")

        age = get_my_age()
        if age is None:
            return

        render_age_card(D.my_age_guide(age), f"만 {age}세")

        # 꽃 받기 이벤트만 대상이 정해져 있어요
        if D.is_target_age(age):
            layout.notice(f"🌼 만 {age}세는 <b>꽃 받기 이벤트 대상</b>이에요. 검진을 받고 데이지를 받아가세요!", kind="ok", icon="🎉")
        else:
            layout.notice(
                f"꽃 받기 이벤트는 {C.TARGET_LABEL} 청년이 대상이에요. 검진 정보와 SNS 이벤트는 만 {age}세도 이용할 수 있어요.",
                kind="info",
                icon="💬",
            )
        go_info, go_clinic = st.columns(2)
        if go_info.button("🩺 내 검진 더 자세히 보기", type="primary", key="age_to_info", use_container_width=True):
            _go_health("연령별 건강정보")
        if go_clinic.button("📍 가까운 검진기관 찾기", key="age_to_clinic", use_container_width=True):
            _go_health("검진기관 찾기")
