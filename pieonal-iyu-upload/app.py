"""피어날 이유 — 서울시 건강검진 캠페인 웹사이트

실행:  streamlit run app.py

이 파일은 '사이트의 뼈대'입니다.
  1) 페이지 기본 설정  2) 공통 스타일  3) 상단 메뉴(페이지 등록)  4) 오류 안내  5) 공통 푸터
각 화면의 실제 내용은 views/ 폴더의 파일에 있어요. (폴더 이름이 pages 가 아닌 이유는 config/pages.py 참고)
"""
import streamlit as st

from components import layout, styles
from config import pages as P
from utils.state import init_state

st.set_page_config(
    page_title="피어날 이유 | 서울시 건강검진 캠페인",
    page_icon="🌼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

styles.inject_global_css()
init_state()

# ── 상단 메뉴 ─────────────────────────────────────────────
# 딕셔너리의 키는 메뉴 묶음 이름입니다. '운영' 묶음은 참가자용이 아니라 꽃집 직원·운영팀용이에요.
navigation = st.navigation(
    {
        "": [
            st.Page(P.HOME, title="홈", icon="🌼", default=True),
            st.Page(P.HEALTH, title="검진 알아보기", icon="🩺", url_path="health"),
            st.Page(P.SURVEY, title="설문하고 꽃 받기", icon="📝", url_path="survey"),
            st.Page(P.SNS, title="SNS 이벤트", icon="📣", url_path="sns"),
            st.Page(P.FLOWER_SHOPS, title="꽃집 찾기", icon="💐", url_path="flowers"),
            st.Page(P.FAQ, title="FAQ", icon="❓", url_path="faq"),
        ],
        "운영": [
            st.Page(P.SHOP_VERIFY, title="꽃집 QR 인증", icon="✅", url_path="shop"),
            st.Page(P.DASHBOARD, title="분석 대시보드", icon="📊", url_path="dashboard"),
        ],
    },
    position="top",
)

# ── 화면 실행 (오류가 나도 방문자에게는 친절한 안내만 보여줍니다) ─
try:
    navigation.run()
except Exception as error:  # st.rerun / st.stop 같은 제어 흐름은 여기로 오지 않습니다.
    layout.friendly_error(error)

layout.footer()
