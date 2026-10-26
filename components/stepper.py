"""'나의 피어남 🌱' 진행 단계 표시:  ① 사전 설문 → ② 건강검진 → ③ 사후 설문 → ④ 꽃 받기"""
import streamlit as st

from components.layout import h
from config import campaign as C
from utils.state import Progress

_STATUS_TEXT = {"done": "완료", "current": "진행 중", "locked": "대기"}


def render_stepper(progress: Progress) -> None:
    statuses = progress.statuses()
    items = []
    for index, ((icon, name, _desc), status) in enumerate(zip(C.STEPS, statuses), start=1):
        dot = "✓" if status == "done" else icon
        sub = "수령 완료" if (index == 4 and status == "done") else _STATUS_TEXT[status]
        items.append(
            f'<li class="pr-step pr-step--{status}"><div class="pr-step__dot">{dot}</div>'
            f"<b>{h(name)}</b><small>{sub}</small></li>"
        )
    percent = max(3, round(progress.done_count / len(C.STEPS) * 100))
    st.html(
        f"""
        <section class="pr-stepper" aria-label="캠페인 진행 단계">
          <div class="pr-stepper__head">
            <h2>나의 피어남 🌱</h2>
            <span class="pr-stepper__count">{progress.done_count} / {len(C.STEPS)} 단계 완료</span>
          </div>
          <ol class="pr-stepper__list">{"".join(items)}</ol>
          <div class="pr-stepper__bar" role="progressbar" aria-valuenow="{percent}" aria-valuemin="0" aria-valuemax="100"><i style="width:{percent}%"></i></div>
        </section>
        """
    )
