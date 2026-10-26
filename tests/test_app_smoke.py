"""모든 화면이 오류 없이 열리는지 확인하는 간단한 시험.

실행:  python -m pytest -q      (pytest 가 없으면  pip install -r requirements-dev.txt)
"""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent
PAGES = [
    "views/home.py",
    "views/health_info.py",
    "views/survey.py",
    "views/sns_event.py",
    "views/flower_shops.py",
    "views/shop_verify.py",
    "views/dashboard.py",
]


@pytest.mark.parametrize("page", PAGES)
def test_page_runs_without_exception(page):
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
    at.run()
    if page != "views/home.py":
        at.switch_page(page)
        at.run()
    assert not at.exception, [e.value for e in at.exception]


def test_unexpected_error_shows_friendly_message(monkeypatch):
    """화면 코드에서 예상 못한 오류가 나도 방문자에게는 친절한 안내가 보여야 합니다."""
    from utils import places

    def boom(*_args, **_kwargs):
        raise RuntimeError("일부러 낸 오류")

    monkeypatch.setattr(places, "load_places", boom)
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
    at.run()
    at.switch_page("views/flower_shops.py")
    at.run()

    friendly = [e.value for e in at.get("html") if "잠시 문제가 생겼어요" in str(e.value)]
    assert friendly, "친절한 오류 안내가 보이지 않아요"
    # 방문자에게 파이썬 오류 내용이 그대로 노출되지 않는지: DEMO_MODE 일 때만 '개발자용' 확장 영역에 있어야 함
    assert any("개발자용" in str(e.label) for e in at.expander)
