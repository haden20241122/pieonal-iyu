"""환경 설정 — API key·설문 URL 같은 '바뀌는 값'과 '비밀값'은 전부 여기서만 읽습니다.

읽는 순서: ① 환경변수(.env 파일 포함) → ② Streamlit secrets → ③ 아래 기본값
코드에 키를 직접 쓰지 마세요. 로컬은 .env, Streamlit Cloud 는 Secrets 에 넣습니다.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _get(name: str, default: str = "") -> str:
    """환경변수 → Streamlit secrets 순으로 값을 찾고, 없으면 default."""
    value = os.getenv(name)
    if value not in (None, ""):
        return value.strip()
    try:  # secrets.toml 이 없는 로컬 환경에서도 오류 없이 넘어가도록
        import streamlit as st

        if name in st.secrets:
            return str(st.secrets[name]).strip()
    except Exception:
        pass
    return default


def _flag(name: str, default: bool) -> bool:
    raw = _get(name, "")
    if raw == "":
        return default
    return raw.lower() in {"1", "true", "yes", "y", "on"}


def _int(name: str, default: int) -> int:
    try:
        return int(_get(name, str(default)))
    except ValueError:
        return default


# ── 동작 모드 ─────────────────────────────────────────────
DEMO_MODE = _flag("DEMO_MODE", True)  # True: '프로토타입 도우미' 표시
APP_BASE_URL = _get("APP_BASE_URL").rstrip("/")  # QR 에 넣을 사이트 주소(선택)

# ── 설문 (비어 있으면 앱 안의 샘플 설문 사용) ─────────────
SURVEY_PRE_URL = _get("SURVEY_PRE_URL")
SURVEY_POST_URL = _get("SURVEY_POST_URL")

# ── QR / 꽃집 인증 ────────────────────────────────────────
QR_VALID_HOURS = _int("QR_VALID_HOURS", 72)
SHOP_STAFF_PIN = _get("SHOP_STAFF_PIN")  # 비어 있으면 PIN 없이 접근
VOUCHER_DB_PATH = Path(_get("VOUCHER_DB_PATH", str(BASE_DIR / "data" / "runtime" / "vouchers.sqlite3")))

# ── 지도 / 외부 API (연결 전에는 비워 둠 → mock 데이터로 동작) ─
MAP_PROVIDER = _get("MAP_PROVIDER", "folium").lower()  # folium | kakao | naver
KAKAO_JS_KEY = _get("KAKAO_JS_KEY")
KAKAO_REST_API_KEY = _get("KAKAO_REST_API_KEY")
NAVER_MAP_CLIENT_ID = _get("NAVER_MAP_CLIENT_ID")
PUBLIC_DATA_API_KEY = _get("PUBLIC_DATA_API_KEY")
