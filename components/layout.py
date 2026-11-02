"""여러 화면에서 함께 쓰는 작은 HTML 조각들 (제목·배지·안내 박스·푸터 등)."""
from __future__ import annotations

from html import escape

import streamlit as st

from config import campaign as C
from config.settings import DEMO_MODE
from data.health_content import SOURCES


def h(text: object) -> str:
    """HTML 에 안전하게 넣기 위한 이스케이프."""
    return escape(str(text), quote=True)


def badge(text: str, kind: str = "sample") -> str:
    """작은 배지. kind: sample(샘플) | draft(예시) | ok | info"""
    return f'<span class="pr-badge pr-badge--{kind}">{h(text)}</span>'


def page_header(kicker: str, title: str, desc: str = "", icon: str = "🌼") -> None:
    desc_html = f'<p class="pr-pagehead__desc">{desc}</p>' if desc else ""
    st.html(
        f"""
        <section class="pr-pagehead">
          <div class="pr-pagehead__icon" aria-hidden="true">{icon}</div>
          <div>
            <div class="pr-eyebrow">{h(kicker)}</div>
            <h1 class="pr-pagehead__title">{h(title)}</h1>
            {desc_html}
          </div>
        </section>
        """
    )


def section_title(title: str, sub: str = "") -> None:
    sub_html = f'<p class="pr-section__sub">{h(sub)}</p>' if sub else ""
    st.html(f'<div class="pr-section"><h2 class="pr-section__title">{h(title)}</h2>{sub_html}</div>')


def notice(text: str, kind: str = "info", icon: str = "ℹ️") -> None:
    """안내 박스. kind: info | warn | ok"""
    st.html(f'<div class="pr-notice pr-notice--{kind}"><span aria-hidden="true">{icon}</span><div>{text}</div></div>')


def cta_link(page: str, label: str, key: str) -> None:
    """눌러야 하는 '다음 행동' 버튼 (노란 큰 버튼). key 는 화면 안에서 겹치지 않게 지어주세요."""
    with st.container(key=f"cta-{key}"):
        st.page_link(page, label=label)


def source_line(source_key: str, verified: bool) -> str:
    """콘텐츠 출처 표시. 공식 자료로 확인되지 않은 내용에는 '예시' 배지가 붙습니다."""
    src = SOURCES.get(source_key, {"name": source_key, "url": ""})
    name = h(src["name"])
    link = f'<a href="{h(src["url"])}" target="_blank" rel="noopener noreferrer">{name}</a>' if src["url"] else name
    tag = "" if verified else " " + badge("예시 · 공식 자료 확인 전", "draft")
    return f'<div class="pr-source">출처: {link}{tag}</div>'


def chips(items: list[str], kind: str = "leaf") -> str:
    return '<div class="pr-chips">' + "".join(f'<span class="pr-chip pr-chip--{kind}">{h(i)}</span>' for i in items) + "</div>"


def footer() -> None:
    demo = (
        '<p class="pr-footer__demo">현재 <b>프로토타입(데모) 모드</b>입니다. '
        "지도의 꽃집·검진기관은 샘플 데이터입니다.</p>"
        if DEMO_MODE
        else ""
    )
    st.html(
        f"""
        <footer class="pr-footer">
          <div class="pr-footer__brand">🌼 {h(C.CAMPAIGN_NAME)} <span>{h(C.CAMPAIGN_KICKER)}</span></div>
          <p>{h(C.CAMPAIGN_TAGLINE[0])} {h(C.CAMPAIGN_TAGLINE[1])}</p>
          <p class="pr-footer__small">이 사이트는 건강 정보를 안내할 뿐, 진단이나 치료를 대신하지 않아요.
          검진 결과 같은 개인 건강정보는 저장하지 않아요.</p>
          {demo}
        </footer>
        """
    )


def friendly_error(error: Exception) -> None:
    """예상하지 못한 오류가 나도 방문자에게는 부드러운 안내를, 개발자에게는 원인을 보여줍니다."""
    st.html(
        """
        <div class="pr-notice pr-notice--warn"><span aria-hidden="true">🌧️</span>
        <div><b>잠시 문제가 생겼어요.</b><br>페이지를 새로고침하거나 잠시 뒤 다시 시도해주세요.
        계속되면 운영팀에 알려주세요.</div></div>
        """
    )
    if DEMO_MODE:
        with st.expander("개발자용 오류 내용 (데모 모드에서만 보여요)"):
            st.exception(error)
