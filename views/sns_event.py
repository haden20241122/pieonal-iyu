"""SNS 이벤트 — 기간 · 대상 · 참여 방법 · 해시태그(복사 버튼) · 혜택."""
import streamlit as st

from components import layout
from components.copy_button import copy_button
from config import campaign as C
from config import pages as P

event = C.SNS_EVENT

layout.page_header(event["eyebrow"], event["title"], "건강검진 후, 나의 ‘피어날 이유’를 SNS에 남겨주세요.", icon="📣")

if not event["verified"]:
    layout.notice(
        "이벤트 세부 내용(기간·인증 방법·혜택)은 <b>예시</b>예요. 운영팀에서 확정하면 "
        "<code>config/campaign.py</code> 의 <code>SNS_EVENT</code> 를 수정해주세요.",
        kind="warn",
        icon="🧪",
    )


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
    st.caption("공식 SNS 계정은 곧 공개돼요. 공개되면 이곳에 바로가기 버튼이 나타나요.")
st.page_link(P.FLOWER_SHOPS, label="💐 꽃 받으러 가기 (인증 꽃집 찾기)")
