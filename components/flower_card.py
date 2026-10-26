"""제1회 캠페인 꽃(데이지) 소개 카드 — 홈과 인증 꽃집 페이지에서 함께 씁니다."""
import streamlit as st

from components.layout import badge, h
from config import campaign as C
from utils import illustrations as art


def render_flower_card() -> None:
    info = C.FLOWER_INFO
    draft = "" if info["verified"] else " " + badge("문구 예시 · 확정 문구로 교체", "draft")
    st.html(
        f"""
        <section class="pr-flowercard">
          <div class="pr-flowercard__art" aria-hidden="true"><img alt="" src="{art.data_uri(art.daisy_svg())}"></div>
          <div>
            <div class="pr-eyebrow">{h(info["kicker"])}</div>
            <h2>{h(info["name"])}</h2>
            <p>{h(info["intro"])}</p>
            <dl>
              <div><dt>{h(info["meaning_title"])}</dt><dd>{h(info["meaning"])}</dd></div>
              <div><dt>{h(info["why_title"])}</dt><dd>{h(info["why"])}</dd></div>
            </dl>
            <div style="margin-top:.7rem">{draft}</div>
          </div>
        </section>
        """
    )
