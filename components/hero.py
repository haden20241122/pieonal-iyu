"""메인 화면 상단: 히어로 + '건강검진 → 설문 → 꽃' 흐름 띠."""
import streamlit as st

from components.layout import h
from config import campaign as C
from config import pages as P
from utils import illustrations as art


def render_hero() -> None:
    """캠페인 이름·핵심 메시지·제1회 캠페인 꽃을 한눈에 보여줍니다."""
    text_col, art_col = st.columns([1.15, 0.85], vertical_alignment="center", gap="large")

    with text_col:
        st.html(
            f"""
            <div class="pr-hero__text">
              <span class="pr-eyebrow pr-eyebrow--pill">{h(C.CAMPAIGN_KICKER)}</span>
              <h1 class="pr-hero__title">피어날 <em>이유</em></h1>
              <p class="pr-hero__lead">건강검진하고 <b>꽃 받아가세요!</b></p>
              <p class="pr-hero__tag">{h(C.CAMPAIGN_TAGLINE[0])}<br>{h(C.CAMPAIGN_TAGLINE[1])}</p>
              <div class="pr-hero__edition"><span>{h(C.FLOWER_EDITION)}</span><b>{h(C.FLOWER_NAME)} {C.FLOWER_EMOJI}</b></div>
            </div>
            """
        )
        with st.container(key="hero-cta"):
            st.page_link(P.SURVEY, label="🌱 나의 피어남 시작하기")

    with art_col:
        st.html(
            f"""
            <div class="pr-hero__art" aria-hidden="true">
              <div class="pr-hero__blob"></div>
              <img class="pr-hero__bouquet" alt="" src="{art.data_uri(art.hero_bouquet_svg())}">
              <img class="pr-hero__spark s1" alt="" src="{art.data_uri(art.scatter_daisy_svg())}">
              <img class="pr-hero__spark s2" alt="" src="{art.data_uri(art.scatter_daisy_svg())}">
              <img class="pr-hero__spark s3" alt="" src="{art.data_uri(art.scatter_daisy_svg())}">
            </div>
            """
        )


def render_flow_strip() -> None:
    """5초 안에 '무엇을 하면 무엇을 받는지' 이해시키는 3단 요약."""
    st.html(
        """
        <div class="pr-flow" role="list">
          <div class="pr-flow__item" role="listitem"><div class="pr-flow__icon">🩺</div><b>건강검진</b><span>받고</span></div>
          <div class="pr-flow__arrow" aria-hidden="true">→</div>
          <div class="pr-flow__item" role="listitem"><div class="pr-flow__icon">📝</div><b>설문</b><span>참여하면</span></div>
          <div class="pr-flow__arrow" aria-hidden="true">→</div>
          <div class="pr-flow__item" role="listitem"><div class="pr-flow__icon">🌼</div><b>꽃</b><span>받아가요</span></div>
        </div>
        <p class="pr-flow__caption">사전·사후 설문(각 약 2분)을 마치면, 서울시 인증 꽃집에서 데이지를 받을 수 있어요.</p>
        """
    )
