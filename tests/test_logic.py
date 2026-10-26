"""화면 없이 확인할 수 있는 핵심 규칙 시험: 위치 검색 · 인증번호 · QR 발급/1회 사용/만료 · 분석 데이터."""
import io

import pandas as pd
import pytest

from utils import analytics, geo, places, qr
from utils import voucher_store as vs


# ── 위치 검색 (mock) ──────────────────────────────────────
@pytest.mark.parametrize(
    "query, label",
    [
        ("강남구", "강남구"),
        ("강남", "강남구"),
        ("강남역 근처", "강남역"),  # 검색어 안에 지역명이 들어 있어도 인식
        ("홍대", "홍대입구"),  # 별칭
        ("서울 마포구", "마포구"),
        ("서울시청", "서울시청"),  # '서울시' 접두어를 지우다 망가지지 않아야 함
    ],
)
def test_search_location_known(query, label):
    result = geo.search_location(query)
    assert result is not None and result.label == label


@pytest.mark.parametrize("query", ["", "   ", "없는곳", "중"])
def test_search_location_unknown_returns_none(query):
    assert geo.search_location(query) is None


def test_nearby_places_sorted_by_distance():
    nearby = places.find_nearby("flower", *geo.SEOUL_CITY_HALL, limit=5)
    distances = [p.distance_km for p in nearby]
    assert distances == sorted(distances) and len(nearby) == 5
    assert all(p.is_sample for p in nearby)  # 샘플 데이터는 항상 샘플로 표시되어야 함


# ── 인증번호 ──────────────────────────────────────────────
def test_code_format_and_extraction():
    code = qr.new_code()
    assert qr.CODE_PATTERN.fullmatch(code)
    assert qr.extract_code(f"  {code.lower()} ") == code
    assert qr.extract_code(f"https://example.app/shop?code={code}") == code
    assert qr.extract_code("hello") is None and qr.extract_code(None) is None


def test_qr_png_is_generated():
    assert qr.make_qr_png(qr.new_code()).startswith(b"\x89PNG")


# ── QR 발급·인증 ──────────────────────────────────────────
def test_cannot_issue_without_both_surveys():
    with pytest.raises(vs.NotEligibleError):
        vs.issue(pre_done=True, post_done=False)
    with pytest.raises(vs.NotEligibleError):
        vs.issue(pre_done=False, post_done=True)


def test_voucher_can_be_used_only_once():
    voucher = vs.issue(True, True)
    assert vs.verify(voucher.code).state == "valid"

    ok, result = vs.redeem(voucher.code, "테스트 꽃집")
    assert ok and result.state == "used"

    ok_again, result_again = vs.redeem(voucher.code, "다른 꽃집")
    assert not ok_again and result_again.state == "used"
    assert vs.get(voucher.code).used_shop == "테스트 꽃집"  # 처음 사용한 꽃집 기록이 유지됨


def test_expired_voucher_cannot_be_redeemed():
    voucher = vs.issue(True, True)
    vs.force_expire(voucher.code)
    assert vs.verify(voucher.code).state == "expired"
    ok, result = vs.redeem(voucher.code, "테스트 꽃집")
    assert not ok and result.state == "expired"


def test_unknown_and_malformed_codes():
    assert vs.verify("PR-2026-ZZZZZZ").state == "not_found"
    assert vs.verify("hello").state == "bad_format"


# ── 분석 데이터 ───────────────────────────────────────────
def test_mock_data_has_all_schema_columns():
    frame = analytics.make_mock_responses(n=50)
    assert {name for name, *_ in analytics.SCHEMA} <= set(frame.columns)
    assert frame["intent_pre"].between(1, 5).all() and frame["intent_post"].between(1, 5).all()


def test_template_csv_roundtrips_through_loader():
    loaded, problems = analytics.load_uploaded_csv(analytics.template_csv())
    assert loaded is not None and not problems and len(loaded) == 1


def test_upload_missing_required_columns_is_rejected():
    raw = "age_group,message_type\n20대,ai\n".encode("utf-8")
    loaded, problems = analytics.load_uploaded_csv(raw)
    assert loaded is None and "필수 열" in problems[0]


def test_upload_accepts_korean_message_labels_and_drops_bad_rows():
    frame = analytics.make_mock_responses(n=20)
    frame["message_type"] = frame["message_type"].map(analytics.MESSAGE_TYPES)  # '규칙 기반' / 'AI 생성'
    frame.loc[0, "message_type"] = "???"
    buffer = io.StringIO()
    frame.to_csv(buffer, index=False)
    loaded, problems = analytics.load_uploaded_csv(buffer.getvalue().encode("utf-8"))
    assert loaded is not None and len(loaded) == 19 and problems
    assert set(loaded["message_type"]) <= {"rule", "ai"}


def test_aggregations_have_expected_shape():
    frame = analytics.make_mock_responses(n=200)
    assert set(analytics.pre_post(frame)["message_type"]) == {"rule", "ai"}
    assert analytics.reason_share(frame)["비율(%)"].sum() == pytest.approx(100)
    assert list(analytics.last_checkup_share(frame)["마지막 검진"]) == analytics.LAST_CHECKUP
    assert isinstance(analytics.kpis(frame)["rate"], float)
