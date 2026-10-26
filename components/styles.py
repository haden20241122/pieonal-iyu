"""공통 스타일 주입. 디자인 수정은 assets/styles.css 에서 하세요."""
import streamlit as st

from config.settings import BASE_DIR

CSS_PATH = BASE_DIR / "assets" / "styles.css"


def inject_global_css() -> None:
    # st.html 에 CSS 파일 경로를 주면 <style> 로 감싸서 적용해 줍니다.
    st.html(CSS_PATH)
