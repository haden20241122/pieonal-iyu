# 🌼 피어날 이유 — 서울시 건강검진 캠페인 웹사이트

> **건강검진하고 꽃 받아가세요!**
> 건강을 확인하는 작은 실천이 나의 일상을 피어나게 합니다.

건강검진 참여자가 **사전 설문 → 건강검진 → 사후 설문**을 마치고 **인증 QR**을 발급받아,
서울시 인증 꽃집에서 제1회 캠페인 꽃 **데이지**를 받아가는 전체 경험을 담은 Streamlit 웹서비스(프로토타입)입니다.

```
캠페인 소개 → 건강검진 정보 → 사전 설문 → 건강검진 → 사후 설문 → 인증 QR 발급 → 꽃집 방문 → 꽃 수령
```

- PC · 태블릿 · 모바일을 **하나의 코드**로 지원합니다 (별도 모바일 사이트 없음).
- 외부 API 없이도 **끝까지 실행**됩니다. 아직 연결되지 않은 부분은 mock(샘플) 데이터로 동작하고, 화면에 **‘샘플’·‘예시’ 배지**가 표시됩니다.

---

## 1. 화면 구성

| 화면 | 주소 | 하는 일 |
|---|---|---|
| 홈 | `/` | 캠페인 소개, 꽃잎 모양 핵심 버튼 4개, 데이지 소개, 참여 대상 안내 |
| 건강검진 알아보기 | `/health` | 검사항목(무료·유료·연령별·기타) · 연령별 건강정보 · 주변 검진기관 지도 · 결과 확인 링크 |
| 설문·꽃 인증 | `/survey` | 진행 단계(나의 피어남) · 사전/사후 설문 · **인증 QR 발급** |
| SNS 이벤트 | `/sns` | 이벤트 안내 카드 · 해시태그 복사 버튼 |
| 인증 꽃집 | `/flowers` | 꽃집 지도 검색 · 꽃 받는 방법 · 데이지 소개 |
| 꽃집 QR 인증 | `/shop` | (꽃집 직원용) 인증번호/QR 확인 → 꽃 전달 완료 → 재사용 차단 |
| 분석 대시보드 | `/dashboard` | (운영용) 규칙 기반 vs AI 생성 메시지 비교, 사전·사후 변화 등 — 가상 데이터로 구조 시연 |

`/shop`, `/dashboard` 는 상단 메뉴의 **‘운영’** 묶음에 있습니다.

---

## 2. 실행 방법

### Windows (PowerShell)

```powershell
cd C:\Users\user\Desktop\pieonal-iyu

py -3.12 -m venv .venv                       # 처음 한 번: 가상환경 만들기
.\.venv\Scripts\python.exe -m pip install -r requirements.txt   # 처음 한 번: 패키지 설치

.\.venv\Scripts\python.exe -m streamlit run app.py              # 실행 → http://localhost:8501
```

> `python` 명령이 Microsoft Store 로 연결되는 PC 에서는 `py -3.12` 를 쓰면 됩니다.
> 가상환경을 활성화(`.\.venv\Scripts\Activate.ps1`)해서 `streamlit run app.py` 만 입력해도 같아요.

### Mac / Linux

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### 체험해 보는 순서

1. **설문·꽃 인증** 에서 사전 설문 → 건강검진(‘받았어요’ 버튼) → 사후 설문을 차례로 진행 → **QR 발급**
2. 다른 브라우저(또는 휴대폰)에서 **`/shop`** 을 열고 인증번호를 입력 → **꽃 전달 완료**
3. 같은 QR 을 다시 확인하면 ‘이미 사용된 QR’ 로 막히는지 확인

데모 모드(`DEMO_MODE=true`, 기본값)에서는 **‘프로토타입 도우미’** 가 보여요. (설문 한 번에 완료 처리, 처음부터 다시 체험, 만료 시험 등)

---

## 3. 프로젝트 구조

```
pieonal-iyu/
├─ app.py                  # 진입점: 페이지 기본 설정 · 공통 스타일 · 상단 메뉴 · 오류 안내 · 푸터
├─ views/                  # 화면(페이지) 파일 — 메뉴 하나당 파일 하나
│   ├─ home.py  health_info.py  survey.py  sns_event.py
│   └─ flower_shops.py  shop_verify.py  dashboard.py
├─ components/             # 여러 화면이 함께 쓰는 UI 조각
│   ├─ hero.py  petals.py  flower_card.py  stepper.py   # 홈·진행 단계 표시
│   ├─ place_finder.py  map_view.py                     # 지역 검색 + 지도 (지도 공급자는 map_view.py 안에 분리)
│   ├─ survey_form.py  copy_button.py  charts.py        # 샘플 설문 · 복사 버튼 · 대시보드 차트
│   └─ layout.py  styles.py  embed.py                   # 배지·안내 박스·푸터 / CSS 주입 / iframe 삽입
├─ config/
│   ├─ settings.py         # .env · Streamlit secrets 읽기 (API key · 설문 URL · 모드 스위치)
│   ├─ campaign.py         # 캠페인 문구 · 공식 링크 · 참여 대상 기준 · SNS 이벤트 · 꽃 소개
│   └─ pages.py            # 화면 파일 경로 모음
├─ data/
│   ├─ health_content.py   # 검사항목 · 연령별 건강정보 (출처·검증 여부 필드 포함)
│   ├─ survey_questions.py # 앱 안 샘플 설문 문항
│   ├─ sample_flower_shops.csv / sample_health_facilities.csv   # ★ 샘플 데이터 (실제 아님)
│   └─ runtime/            # QR 발급 기록(SQLite)이 자동 생성되는 곳 (Git 제외)
├─ utils/
│   ├─ geo.py places.py    # 위치 검색(mock) · 장소 데이터 로더
│   ├─ qr.py voucher_store.py   # 인증번호/QR 이미지 · 발급·사용·만료 관리
│   ├─ state.py            # 진행 상태(session_state)
│   ├─ analytics.py        # 분석 데이터 구조 · 가상 데이터 · 집계
│   └─ illustrations.py    # 코드로 그린 데이지 일러스트(SVG)
├─ assets/styles.css       # 전체 디자인(색·글꼴·반응형)
├─ tests/                  # pytest (화면 7개 + 핵심 규칙)
├─ .streamlit/config.toml  # 테마 · 서버 설정  /  secrets.toml.example
├─ requirements.txt  requirements-dev.txt  .env.example  .gitignore
```

**요청하신 구조에서 달라진 점 — 화면 폴더 이름이 `pages/` 가 아니라 `views/` 입니다.**
Streamlit 은 `pages/` 폴더를 옛 방식으로 자동 인식해서, 서버가 막 켜진 상태에서 `/shop` 처럼 **주소로 바로 들어오면**
`app.py`(공통 스타일·메뉴)를 건너뛰고 화면 파일만 단독 실행되는 문제가 있었어요.
꽃집 직원이 QR 을 스캔해 `/shop?code=…` 로 들어오는 경로가 바로 이 경우라서 폴더 이름을 바꿨습니다.

---

## 4. 사용 기술

| 영역 | 기술 |
|---|---|
| 프레임워크 | [Streamlit](https://streamlit.io) ≥ 1.64 (`st.navigation` 상단 메뉴, `st.html`, `st.pills`) |
| 지도 | folium(Leaflet) + OpenStreetMap 타일 — API 키 없이 동작 |
| 차트 | Plotly (막대 · 도넛 · 선 · 덤벨) |
| QR | `qrcode` + Pillow |
| 데이터 | pandas / numpy, QR 상태는 SQLite(표준 라이브러리) |
| 디자인 | 직접 작성한 CSS(반응형) · Google Fonts(Gowun Batang / Noto Sans KR) · 코드로 그린 SVG 데이지 |
| 시험 | pytest + Streamlit `AppTest` |

개발 때 시험한 환경: Python 3.12 · Streamlit 1.64.0 · pandas 3.0 · plotly 7.1 · folium 0.20.

---

## 5. 환경변수 · API key 설정

**비밀값은 코드에 쓰지 않습니다.** 로컬은 `.env`, Streamlit Cloud 는 **Secrets** 에 넣어요. (`.env` 는 `.gitignore` 로 Git 에서 제외됩니다.)

```powershell
copy .env.example .env      # 복사 후 값을 채우세요
```

읽는 순서: **환경변수(.env 포함) → Streamlit secrets → 기본값**. 값이 비어 있으면 mock(샘플) 모드로 동작합니다.

| 이름 | 설명 | 비어 있으면 |
|---|---|---|
| `DEMO_MODE` | `true` 면 ‘프로토타입 도우미’ 표시 (운영 시 `false`) | `true` |
| `APP_BASE_URL` | 배포 주소. 넣으면 QR 이 `주소/shop?code=…` 가 되어 **휴대폰 카메라로 스캔하면 바로 인증 화면**이 열려요 | QR 에 인증번호만 담김 |
| `SURVEY_PRE_URL` `SURVEY_POST_URL` | Google Forms 등 설문 주소 | 앱 안의 **샘플 설문**이 열림 |
| `SHOP_STAFF_PIN` | `/shop` 접근 PIN | PIN 없이 열림 |
| `QR_VALID_HOURS` | QR 유효 시간(시간) | `72` |
| `MAP_PROVIDER` | `folium`(기본) · `kakao` · `naver` | `folium` |
| `KAKAO_JS_KEY` `KAKAO_REST_API_KEY` `NAVER_MAP_CLIENT_ID` | 지도 API 키 (연결 전) | 사용 안 함 |
| `PUBLIC_DATA_API_KEY` | 공공데이터포털 검진기관 API 키 (연결 전) | 샘플 CSV 사용 |

---

## 6. mock(샘플) 데이터와 실제 데이터 구분

“존재하지 않는 데이터를 실제인 것처럼 보이지 않게” 하기 위해 다음 규칙을 둡니다.

- **장소 데이터**: `Place.is_sample` 플래그. 샘플이면 목록·지도 팝업에 **‘샘플’ 배지**와 안내 문구가 항상 붙어요.
  샘플 꽃집·검진기관은 가상의 도로명(‘샘플로’)과 `02-000-…` 전화번호를 써서 실제 장소와 혼동되지 않게 했습니다.
- **건강정보·캠페인 문구**: `verified: False` 항목은 **‘예시 · 공식 자료 확인 전’ 배지**가 붙어요.
  공식 자료로 확인한 뒤 내용을 고치고 `verified: True` 로 바꾸면 배지가 사라집니다. 항목마다 **출처(`source`)** 를 표시합니다.
- **분석 대시보드**: 가상 데이터일 때 상단에 경고 박스가 표시되고, 실제 CSV 를 올리면 사라져요.
- **개인 건강정보는 저장하지 않습니다.** 샘플 설문 응답은 세션에만 잠시 있다가 사라지고, QR 기록에는 이름·연락처·건강정보가 없습니다.

---

## 7. 자주 하는 수정

| 바꾸고 싶은 것 | 고칠 곳 |
|---|---|
| 캠페인 문구 · 참여 대상 기준 · 운영 기간 · SNS 이벤트 · 꽃 소개 | `config/campaign.py` |
| 검사항목 · 연령별 건강정보 · 출처 | `data/health_content.py` |
| 샘플 설문 문항 | `data/survey_questions.py` (실제 운영은 Google Forms → `SURVEY_*_URL`) |
| 색상 · 글꼴 · 여백 · 모바일 배치 | `assets/styles.css` 맨 위 `:root` 변수 |
| 샘플 꽃집 · 검진기관 목록 | `data/sample_*.csv` (엑셀에서 열어 수정 가능) |
| 메뉴 추가/삭제 | `views/` 에 파일 추가 → `config/pages.py` 와 `app.py` 에 한 줄씩 |
| 외부 링크(공단 등) | `config/campaign.py` 상단 — **2026-09-20 에 응답을 확인**했어요. 배포 전에 한 번씩 눌러보세요 |

---

## 8. 실제 API 연결 방법

### 지도 (Kakao Map / Naver Map)
화면 코드는 `components/map_view.py` 의 `render_place_map()` 하나만 부릅니다.
`_render_kakao()` 같은 함수를 만들어 `_PROVIDERS` 에 등록하고 `MAP_PROVIDER=kakao` 로 바꾸면 다른 파일은 그대로예요.
- ⚠️ Kakao/Naver 지도 JS 는 **등록한 도메인에서만** 동작합니다. iframe 안에서 도메인 검사에 걸릴 수 있으니 **배포 주소에서 꼭 시험**하세요.
  (대안: 지도는 folium 을 그대로 두고, 장소 검색·좌표 변환만 Kakao Local REST API 로 교체)
- 지금 쓰는 OpenStreetMap 타일은 **프로토타입·소규모용**입니다. 실제 서비스 트래픽에는 정식 지도 API 를 쓰세요.

### 장소 검색 · 현재 위치
`utils/geo.py` 의 `search_location()` 안쪽만 API 호출로 바꾸면 됩니다. (지금은 서울 25개 자치구와 주요 지역의 근사 좌표 사전)
‘현재 위치’ 버튼은 지금 서울시청을 가정한 **모의 위치**예요. 실제 GPS 는 브라우저 위치 권한을 받는 컴포넌트가 필요합니다.

### 검진기관 · 인증 꽃집 목록
`utils/places.py` 의 `load_places()` 가 데이터 소스를 고르는 지점입니다. API 결과를 `Place` 형태로 돌려주면 화면은 그대로 동작해요.
(공공데이터포털에서 건강검진기관 관련 API 를 찾아 키를 신청한 뒤 `PUBLIC_DATA_API_KEY` 에 넣으세요.)

### 설문 (Google Forms)
`SURVEY_PRE_URL` / `SURVEY_POST_URL` 을 넣으면 ‘설문 시작하기’ 가 새 탭으로 열립니다.
- ⚠️ 이 모드에서는 참가자가 돌아와서 **‘설문을 마쳤어요’ 를 눌러 스스로 완료 처리**해요. 제출 여부를 자동 확인하려면
  Forms 응답 시트(Google Sheets API)나 웹훅으로 확인하는 로직이 필요합니다. (향후 개발)

---

## 9. QR 인증은 어떻게 동작하나요

- 인증번호 형식 `PR-2026-XXXXXX` (혼동되는 0/O, 1/I 제외). 사전·사후 설문을 **모두 마친 경우에만** 발급됩니다.
- 발급·만료·사용 기록은 `data/runtime/vouchers.sqlite3` 에 저장돼요. 참가자 휴대폰과 꽃집 직원 기기는 서로 다른 세션이라 `session_state` 로는 인증할 수 없기 때문입니다.
- **1회 사용**: ‘꽃 전달 완료’ 는 DB 에서 한 번만 성공합니다(동시에 눌러도 한 명만). 만료(`QR_VALID_HOURS`) 후에는 사용할 수 없어요.
- 브라우저를 새로고침하면 진행 상태가 초기화되므로, 설문 화면의 **‘인증번호로 이어하기’** 로 QR 화면을 다시 불러올 수 있어요.
- ⚠️ **프로토타입 수준입니다.** Streamlit Cloud 는 앱이 재시작되면 파일이 초기화돼 발급 기록이 사라져요.
  실제 운영 전에는 `utils/voucher_store.py` 의 함수(`issue / verify / redeem …`)를 유지한 채 Supabase · Firestore 같은 외부 DB 로 바꾸세요.

---

## 10. 분석 대시보드 (`/dashboard`)

캠페인 효과 분석을 위한 **데이터 구조**와 **차트 골격**입니다. (지금 숫자는 전부 가상 데이터)

- 열 구성은 `utils/analytics.py` 의 `SCHEMA`: 페르소나 · 연령대 · 마지막 검진 시기 · 미검진 이유 · SNS 반응도 · 메시지 유형(규칙 기반/AI 생성) · 메시지 문구 · 사전/사후 참여 의향 · 실제 참여 여부
- 대시보드에서 **‘CSV 양식 내려받기’ → 실제 응답을 채워 올리면** 같은 화면이 실제 데이터로 바뀝니다.
- 차트: 메시지 유형별 비교(막대) · 사전→사후(덤벨) · 주차별 추이(선) · 미검진 이유(도넛) · 마지막 검진 시기(막대). 모든 차트에 **‘표로 보기’** 가 있어요.
- 같은 대상은 어느 차트에서나 같은 색(규칙 기반=파랑, AI 생성=주황)입니다. 팔레트는 색각 이상 시뮬레이션 검증을 통과한 값을 썼어요.

---

## 11. 시험

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

화면 7개가 오류 없이 열리는지, 위치 검색 · 인증번호 · QR 발급/1회 사용/만료 · 분석 데이터 규칙을 확인합니다. (시험은 임시 DB 를 써서 실제 발급 기록을 건드리지 않아요.)
`watchdog` 이 설치돼 있으면 코드를 고칠 때 화면이 자동 새로고침됩니다.

---

## 12. GitHub 에 올리기

```powershell
cd C:\Users\user\Desktop\pieonal-iyu
git init
git add .
git status            # ← .env, .venv, data/runtime 이 목록에 없는지 꼭 확인!
git commit -m "피어날 이유: 캠페인 웹사이트 프로토타입"
git branch -M main
git remote add origin https://github.com/<내-계정>/<저장소-이름>.git
git push -u origin main
```

GitHub 에서 먼저 빈 저장소(README 없이)를 만들어 주소를 복사하세요. `.gitignore` 가 `.env`, `.streamlit/secrets.toml`, `.venv/`, QR 기록을 제외합니다.
**API key 를 실수로 올렸다면 키를 즉시 폐기하고 새로 발급**하세요 (Git 기록에서 지워도 이미 노출된 것으로 봐야 해요).

---

## 13. Streamlit Community Cloud 배포

1. GitHub 에 코드를 올립니다 (위 12번).
2. <https://share.streamlit.io> 에 GitHub 계정으로 로그인 → **Create app**
3. 저장소 · 브랜치(`main`) 선택, **Main file path** 에 `app.py`
4. **Advanced settings** → Python 버전 `3.12`, **Secrets** 에 `.streamlit/secrets.toml.example` 내용을 붙여넣고 값 채우기
5. **Deploy** → `https://<앱이름>.streamlit.app` 주소가 생겨요
6. 그 주소를 Secrets 의 **`APP_BASE_URL`** 에 넣고 저장 → 이후 발급되는 QR 이 `주소/shop?code=…` 형태가 됩니다
7. 실제 운영 시 `DEMO_MODE = "false"`

배포 후 확인: 휴대폰에서 QR 발급 → 다른 기기로 `/shop` 인증이 되는지, 모바일에서 화면이 깨지지 않는지 봐주세요.

---

## 14. 알려진 한계 · 확인이 필요한 것

- **샘플 데이터**: 꽃집·검진기관·좌표는 가상입니다. 위치 검색은 서울 자치구와 주요 지역만 알아요.
- **건강정보는 ‘작성 예시’**: 검진 대상·주기·비용은 공식 자료(국민건강보험공단, 질병관리청)로 확인해서 고쳐야 합니다. 참여 대상 기준은 `config/campaign.py` 의 `ELIGIBILITY`.
- **QR 저장소는 프로토타입**: 위 9번 참고 (재시작 시 초기화).
- **설문 완료 자동 확인 없음**: Google Forms 모드는 자가 확인 방식입니다.
- **‘내 검진 결과 확인’ 링크**는 공단 ‘건강검진 실시안내’ 페이지로 연결돼요. 결과조회 메뉴는 로그인이 필요하고, 공단 사이트 개편 시 주소가 바뀔 수 있어요.
- **라이트 테마 고정**: 캠페인 분위기를 위해 다크 모드는 지원하지 않습니다(`.streamlit/config.toml`).
- **접근성**: 모든 차트에 표 보기 · 색 외 보조 표시(범례·라벨)가 있지만, 스크린리더 전체 점검은 아직 하지 않았어요.

---

## 15. 향후 개발 예정 기능

- [ ] 공식 자료 기반 건강정보 교체 (`verified=True`) · 참여 대상 기준 확정
- [ ] 실제 검진기관 API · 인증 꽃집 목록 연동, Kakao/Naver 지도 연결
- [ ] Google Forms 제출 자동 확인 (Sheets API/웹훅)
- [ ] QR 저장소를 외부 DB 로 교체, 꽃집별 재고·수령 현황
- [ ] 꽃집 직원 화면에서 카메라로 QR 스캔
- [ ] 브라우저 위치 권한을 이용한 ‘현재 위치’
- [ ] 분석 대시보드: 메시지 문구별 비교, SNS 반응도–참여 관계, 페르소나별 반응, 실제 응답 자동 수집
- [ ] 다국어(영어 · 중국어 · 일본어) 안내
