"""화면 파일 경로를 한곳에서 관리합니다.

app.py(메뉴 등록)와 각 화면의 버튼(st.page_link)이 같은 경로를 쓰도록 모아 둔 파일입니다.
화면을 추가/삭제할 때는 여기와 app.py 만 고치면 됩니다.

※ 화면 파일은 'pages/' 가 아니라 'views/' 폴더에 둡니다.
   Streamlit 은 'pages/' 폴더를 자동으로 화면 목록으로 인식하는데, 그러면 서버가 막 켜진 상태에서
   /shop 같은 주소로 바로 들어왔을 때 app.py(공통 스타일·메뉴)를 건너뛰고 화면 파일만 단독 실행돼요.
   (꽃집에서 QR 을 스캔해 들어오는 경로가 바로 이 경우예요.)
"""

HOME = "views/home.py"
HEALTH = "views/health_info.py"
SURVEY = "views/survey.py"
SNS = "views/sns_event.py"
FLOWER_SHOPS = "views/flower_shops.py"
FAQ = "views/faq.py"
SHOP_VERIFY ="views/shop_verify.py"  # 꽃집 직원용 (/shop)
DASHBOARD = "views/dashboard.py"  # 운영·분석용
