"""인증번호 생성·형식 검사와 QR 이미지 만들기.

인증번호 형식:  PR-2026-XXXXXX   (PR = 피어날 이유, 연도, 6자리 무작위)
헷갈리기 쉬운 문자(0/O, 1/I)는 뺐어요 — 꽃집에서 직접 입력할 때 실수를 줄이기 위해서입니다.
"""
from __future__ import annotations

import io
import re
import secrets

import qrcode
from qrcode.constants import ERROR_CORRECT_M

from config.campaign import CAMPAIGN_YEAR
from config.settings import APP_BASE_URL

_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
CODE_PATTERN = re.compile(r"PR-\d{4}-[A-Z0-9]{6}")
CODE_EXAMPLE = f"PR-{CAMPAIGN_YEAR}-A1B2C3"


def new_code() -> str:
    suffix = "".join(secrets.choice(_ALPHABET) for _ in range(6))
    return f"PR-{CAMPAIGN_YEAR}-{suffix}"


def extract_code(text: str | None) -> str | None:
    """입력값(인증번호 또는 QR 주소)에서 인증번호만 뽑아냅니다. 형식이 다르면 None."""
    if not text:
        return None
    match = CODE_PATTERN.search(text.strip().upper())
    return match.group(0) if match else None


def qr_payload(code: str) -> str:
    """QR 에 담을 내용. 사이트 주소가 설정돼 있으면 '주소/shop?code=…' 로 만들어,
    꽃집에서 휴대폰 카메라로 스캔하면 바로 인증 화면이 열립니다."""
    if APP_BASE_URL:
        return f"{APP_BASE_URL}/shop?code={code}"
    return code


def make_qr_png(payload: str) -> bytes:
    qr = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_M, box_size=10, border=2)
    qr.add_data(payload)
    qr.make(fit=True)
    image = qr.make_image(fill_color="#22332C", back_color="white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
