"""앱 안 샘플 설문 폼. 응답은 세션에만 잠시 보관하고 어디에도 저장하지 않습니다."""
from __future__ import annotations

import streamlit as st

from components.layout import h


def render_survey_form(form_key: str, questions: list[dict]) -> dict | None:
    """폼을 그리고, 모든 문항에 답해 제출하면 응답 dict, 아니면 None 을 돌려줍니다."""
    answers: dict = {}
    with st.form(form_key, border=False):
        for q in questions:
            widget_key = f"{form_key}_{q['id']}"
            if q["type"] == "select":
                answers[q["id"]] = st.radio(q["label"], q["options"], index=None, key=widget_key)
            elif q["type"] == "multiselect":
                answers[q["id"]] = st.multiselect(q["label"], q["options"], key=widget_key, placeholder="선택해주세요")
            elif q["type"] == "scale":
                st.html(f'<div style="color:var(--muted);font-size:.85rem;margin-top:.4rem">1 = {h(q["low"])} · 5 = {h(q["high"])}</div>')
                answers[q["id"]] = st.radio(q["label"], [1, 2, 3, 4, 5], index=None, horizontal=True, key=widget_key)
        submitted = st.form_submit_button("제출하기", type="primary")

    if not submitted:
        return None
    missing = [q["label"] for q in questions if q["type"] != "multiselect" and answers.get(q["id"]) is None]
    if missing:
        st.warning("모든 질문에 답해주세요. (빠진 문항이 있어요)")
        return None
    return answers
