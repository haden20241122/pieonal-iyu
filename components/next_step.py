"""홈 화면의 '지금 이어서 할 일' — 캠페인을 시작한 사람에게만 보여주는 다음 행동 안내.

처음 방문한 사람에게는 보이지 않아요(히어로의 '나의 피어남 시작하기' 버튼이 그 역할을 해요).
"""
import streamlit as st

from components import layout
from components.stepper import render_stepper
from config import pages as P
from utils import state


def render_next_step() -> None:
    progress = state.get_progress()
    if progress.done_count == 0:
        return

    layout.section_title("여기까지 왔어요", "다음 단계만 눌러서 이어가세요.")
    render_stepper(progress)

    if progress.flower_received:
        st.success("꽃까지 받았어요. 수고했어요! 🌼")
        layout.cta_link(P.SNS, "📣 나의 ‘피어날 이유’ 남기러 가기 →", "next-sns")
        return

    current = progress.statuses().index("current")
    if current == 0:
        layout.cta_link(P.SURVEY, "📝 사전 설문 이어서 하기 →", "next-pre")
    elif current == 1:
        layout.cta_link(P.HEALTH, "📍 건강검진 받으러 가기 →", "next-checkup")
        st.page_link(P.SURVEY, label="이미 검진을 받았어요")
    elif current == 2:
        layout.cta_link(P.SURVEY, "📝 사후 설문 하러 가기 →", "next-post")
    elif progress.voucher is None or progress.voucher.is_expired:
        layout.cta_link(P.SURVEY, "🎁 꽃 받을 QR 만들기 →", "next-qr")
    else:
        layout.cta_link(P.FLOWER_SHOPS, "💐 꽃 받으러 가기 →", "next-flower")
