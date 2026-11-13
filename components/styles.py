"""공통 스타일 주입. 디자인 수정은 assets/styles.css 에서 하세요."""
import streamlit as st

from config.settings import BASE_DIR
from utils import illustrations as art

CSS_PATH = BASE_DIR / "assets" / "styles.css"


def inject_global_css() -> None:
    # st.html 에 CSS 파일 경로를 주면 <style> 로 감싸서 적용해 줍니다.
    st.html(CSS_PATH)
    # 긴 그림 데이터는 CSS 파일 밖에서 변수로 한 번만 넘겨요: 히어로와 각 페이지 배너가 같은 언덕 배경을 써요
    st.html(f'<style>:root {{ --hills: url("{art.data_uri(art.hills_svg())}"); }}</style>')
