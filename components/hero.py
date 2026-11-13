"""메인 화면 상단: 이끼 낀 초록 언덕 히어로 + '건강검진 → 설문 → 꽃' 흐름 띠.

구성(레퍼런스 'blume*' 처럼 말수를 줄이고 큰 글씨 하나로):
  · 가운데: 크림색 둥근 글씨 '피어날 이유*', 한 줄 안내, 두 개의 알약 버튼
  · 왼쪽 아래: 얇고 넓은 자간의 문구
  · 오른쪽 아래: 풀밭에서 흰 데이지가 하나씩 피어나는 움직이는 그림 (그림 안에 애니메이션이 들어 있어요)
  · 마우스를 따라 꽃잎이 떨어지는 효과는 components/petal_cursor.py
움직임은 모두 작고 느리며, '동작 줄이기' 설정을 켠 사람에게는 멈춘 그림만 보여줘요.
"""
import streamlit as st

from components.layout import h
from components.petal_cursor import render_petal_cursor
from config import campaign as C
from config import pages as P
from utils import illustrations as art


def render_hero() -> None:
    """캠페인 이름과 핵심 메시지를 한 장면으로 보여줍니다. (배경 언덕은 styles.py 가 --hills 로 심어둬요)"""
    with st.container(key="hero"):
        st.html(f'<img class="pr-hero__meadow" alt="" aria-hidden="true" src="{art.data_uri(art.meadow_svg())}">')
        st.html(
            f"""
            <div class="pr-hero__center">
              <span class="pr-hero__kicker">{h(C.CAMPAIGN_KICKER)}</span>
              <h1 class="pr-hero__title" aria-label="{h(C.CAMPAIGN_NAME)}">{h(C.CAMPAIGN_NAME)}<span class="star" aria-hidden="true">*</span></h1>
              <p class="pr-hero__lead">건강검진하고 <b>꽃 받아가세요</b></p>
            </div>
            """
        )
        with st.container(key="hero-cta"):
            primary, secondary = st.columns(2, gap="small")
            with primary:
                st.page_link(P.SURVEY, label="나의 피어남 시작하기")
            with secondary:
                st.page_link(P.HEALTH, label="검진 알아보기")
        st.html(
            f'<p class="pr-hero__tag">{h(C.CAMPAIGN_TAGLINE[0])}<br>{h(C.CAMPAIGN_TAGLINE[1])}</p>'
        )
    render_petal_cursor()

    # 꽃 받기 안내는 히어로 아래에 차분한 칩으로
    st.html(
        f"""
        <div class="pr-hero__meta">
          <span class="pr-meta-chip"><b>{h(C.FLOWER_EDITION)}</b> {h(C.FLOWER_NAME)} {C.FLOWER_EMOJI}</span>
          <span class="pr-meta-chip">{h(C.TARGET_MESSAGE)}</span>
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
          <div class="pr-flow__item" role="listitem"><div class="pr-flow__icon">📝</div><b>설문</b><span>두 번 하면</span></div>
          <div class="pr-flow__arrow" aria-hidden="true">→</div>
          <div class="pr-flow__item" role="listitem"><div class="pr-flow__icon">🌼</div><b>꽃</b><span>받아가요</span></div>
        </div>
        <p class="pr-flow__caption">설문은 검진 전후로 한 번씩, 각각 2분쯤 걸려요. 끝나면 서울 인증 꽃집에서 데이지를 받아가세요.</p>
        """
    )
