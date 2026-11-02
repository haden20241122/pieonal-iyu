"""자주 묻는 질문 (FAQ) — 분류별로 보거나 검색해서 찾아봐요."""
import streamlit as st

from components import layout
from config import campaign as C
from config import pages as P
from data import faq as D

layout.page_header(
    "FAQ",
    "자주 묻는 질문",
    "많이 물어보시는 것들만 모았어요. 없는 질문은 아래 안내를 참고해주세요.",
    icon="❓",
)

ALL = "전체"
categories = [name for name, _ in D.FAQ]
category = st.pills("분류", [ALL] + categories, default=ALL, key="faq_category", label_visibility="collapsed") or ALL
query = st.text_input("질문 검색", placeholder="궁금한 단어를 입력해보세요 (예: QR, 검진, 개인정보)", key="faq_query").strip()


def _matches(question: str, answer: str) -> bool:
    return not query or query.lower() in (question + " " + answer).lower()


shown = 0
for name, items in D.FAQ:
    if category not in (ALL, name):
        continue
    visible = [(q, a) for q, a in items if _matches(q, a)]
    if not visible:
        continue
    layout.section_title(name)
    for question, answer in visible:
        with st.expander(question):
            st.markdown(answer)
        shown += 1

if shown == 0:
    st.info("찾는 질문이 없어요. 검색어를 바꾸거나 분류를 ‘전체’로 바꿔보세요.")

layout.notice(
    f"찾는 답이 없나요? 건강검진 대상·비용은 <a href=\"{C.NHIS_URL}\" target=\"_blank\" rel=\"noopener noreferrer\">국민건강보험공단</a> "
    f"고객센터({D.NHIS_PHONE})에 문의해주세요.",
    kind="info",
    icon="💬",
)
layout.cta_link(P.SURVEY, "🌱 나도 시작해볼래요 →", "faq-start")
