"""홈 — 캠페인 소개 → 핵심 버튼 4개 → 데이지 소개."""
import streamlit as st

from components import age_checker, flower_card, hero, layout, next_step, petals, story
from config import campaign as C

hero.render_hero()
story.render_name_story()  # 왜 '피어날 이유'인지
age_checker.render_age_checker()  # 나이를 입력하면 바로 내 검진 안내
hero.render_flow_strip()
next_step.render_next_step()  # 캠페인을 시작한 사람에게만: 다음에 할 일

layout.section_title("어디부터 볼까요?", "궁금한 곳부터 눌러보세요.")
petals.render_petal_menu()

layout.section_title("건강검진하고 받는 꽃")
flower_card.render_flower_card()

verified_tag = "" if C.ELIGIBILITY["verified"] else " " + layout.badge("안내 문구 예시 · 공식 기준 확인 전", "draft")
st.html(
    f"""
    <div class="pr-eligibility" style="margin-top:1.4rem">
      <div class="pr-eligibility__icon" aria-hidden="true">📋</div>
      <div>
        <h3>{layout.h(C.ELIGIBILITY["title"])}{verified_tag}</h3>
        <p>{layout.h(C.ELIGIBILITY["text"])}</p>
        <p>{layout.h(C.ELIGIBILITY["note"])}
           <a href="{layout.h(C.ELIGIBILITY["source_url"])}" target="_blank" rel="noopener noreferrer">{layout.h(C.ELIGIBILITY["source_name"])} 바로가기</a></p>
        <p style="color:var(--muted);font-size:.9rem">📅 {layout.h(C.CAMPAIGN_PERIOD)}</p>
      </div>
    </div>
    """
)
