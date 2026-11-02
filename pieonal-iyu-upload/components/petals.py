"""메인 화면의 핵심 버튼 4개 — 꽃잎 모양으로 배치.

PC 에서는 2×2 로 모여 가운데 데이지가 있는 '꽃'이 되고, 모바일에서는 한 열로 쌓입니다.
카드 전체가 눌리지만, 실제 이동은 st.page_link 가 처리해서 (새로고침 없이) 진행 상태가 유지돼요.
"""
import streamlit as st

from components.layout import h
from config import pages as P
from utils import illustrations as art

# (아이콘, 제목, 설명, 이동할 페이지, 버튼 문구)
PETALS = [
    ("🩺", "내 검진 알아보기", "나에게 해당하는 검진과 가까운 검진기관을 찾아봐요.", P.HEALTH, "검진 확인하기 →"),
    ("📝", "설문하고 꽃 받기", "설문 두 번이면 꽃 받을 QR이 나와요.", P.SURVEY, "시작하기 →"),
    ("📣", "SNS 이벤트", "나의 ‘피어날 이유’를 남기고 이벤트에 참여해요.", P.SNS, "구경하기 →"),
    ("💐", "꽃집 찾기", "가까운 서울시 인증 꽃집에서 데이지를 받아가요.", P.FLOWER_SHOPS, "꽃집 찾기 →"),
]


def render_petal_menu() -> None:
    # 가운데 데이지 이미지는 CSS 배경으로 넣기 위해 여기서 스타일을 한 줄 더합니다.
    st.html(f'<style>.st-key-petals::after {{ background-image: url("{art.data_uri(art.daisy_svg())}"); }}</style>')

    with st.container(key="petals"):
        for index, (icon, title, desc, page, button_label) in enumerate(PETALS):
            with st.container(key=f"petal-{index}"):
                st.html(
                    f"""
                    <div class="pr-petal__icon" aria-hidden="true">{icon}</div>
                    <div class="pr-petal__title">{h(title)}</div>
                    <div class="pr-petal__desc">{h(desc)}</div>
                    """
                )
                st.page_link(page, label=button_label)
