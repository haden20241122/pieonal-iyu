"""HTML 문서를 iframe 으로 끼워 넣는 작은 도구 (지도·복사 버튼에서 사용).

최신 Streamlit 은 st.iframe, 오래된 버전은 st.components.v1.html 을 씁니다.
"""
import streamlit as st
import streamlit.components.v1 as components


def embed_html(html: str, height: int) -> None:
    html = html.strip()
    if hasattr(st, "iframe"):
        st.iframe(html, height=height)
    else:  # pragma: no cover - 구버전 호환
        components.html(html, height=height)
