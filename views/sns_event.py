"""SNS 이벤트 — 기간 · 대상 · 참여 방법 · 해시태그(복사 버튼) · 혜택."""
import streamlit as st

from components import layout
from components.copy_button import copy_button
from config import campaign as C
from config import pages as P

event = C.SNS_EVENT

layout.page_header(event["eyebrow"], event["title"], "검진을 마쳤다면, 나의 ‘피어날 이유’를 한 줄만 남겨주세요.", icon="📣")

layout.notice("SNS 이벤트는 <b>나이와 상관없이</b> 건강검진을 받은 누구나 참여할 수 있어요.", kind="ok", icon="🙌")


def _card(card: dict) -> str:
    body = "".join(f"<p>{layout.h(line)}</p>" for line in card["body"])
    return f'<div class="pr-card"><div class="pr-card__title">{card["icon"]} {layout.h(card["title"])}</div>{body}</div>'


st.html('<div class="pr-grid">' + "".join(_card(card) for card in event["cards"]) + "</div>")

# ── 해시태그 ─────────────────────────────────────────────
layout.section_title("해시태그", "버튼을 누르면 복사돼요. 게시물에 그대로 붙여넣으세요.")
with st.container(key="card-hashtags-current"):
    for index, tag in enumerate(C.SNS_HASHTAGS):
        tag_col, button_col = st.columns([2, 1], vertical_alignment="center")
        tag_col.html(f'<span class="pr-hashtag">{layout.h(tag)}</span>')
        with button_col:
            copy_button(tag, "복사")
    st.divider()
    copy_button(" ".join(C.SNS_HASHTAGS), "해시태그 전체 복사")

# ── 공식 계정 / 다음 행동 ─────────────────────────────────
st.write("")
if C.SNS_ACCOUNT_URL:
    st.link_button("공식 SNS 계정 바로가기 →", C.SNS_ACCOUNT_URL, type="primary")
else:
    st.caption("해시태그를 검색하면 다른 분들의 ‘피어날 이유’도 볼 수 있어요.")
layout.cta_link(P.FLOWER_SHOPS, "💐 꽃 받으러 가기 (꽃집 찾기) →", "sns-flowers")
