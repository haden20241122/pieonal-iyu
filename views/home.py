"""홈 — 캠페인 소개 → 핵심 버튼 4개 → 데이지 소개."""
import streamlit as st

from components import flower_card, hero, layout, petals
from config import campaign as C

hero.render_hero()
hero.render_flow_strip()

layout.section_title("지금, 어디부터 시작해볼까요?", "꽃잎을 눌러 원하는 곳으로 이동하세요.")
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
