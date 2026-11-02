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
    raw = "age_group,message_type\n19~24세,ai\n".encode("utf-8")
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


def test_location_from_place_is_used_as_search_center():
    location = geo.location_from_place("샘플병원", 37.5, 127.0)
    assert location.label == "샘플병원 근처" and location.kind == "clinic" and location.matched
    nearby = places.find_nearby("flower", location.lat, location.lon, limit=3)
    assert nearby and nearby == sorted(nearby, key=lambda p: p.distance_km)


@pytest.mark.parametrize("age,expected", [(None, False), (18, False), (19, True), (24, True), (29, True), (30, False)])
def test_target_age_is_19_to_29(age, expected):
    from data import health_content as D

    assert D.is_target_age(age) is expected


def _texts(age):
    from data import health_content as D

    guide = D.my_age_guide(age)
    return " ".join(guide["screenings"]), " ".join(guide["extras"]), guide


@pytest.mark.parametrize("age", [0, 3, 10, 18, 19, 20, 24, 29, 35, 40, 54, 56, 66, 70, 80, 95, 120])
def test_every_age_gets_a_guide(age):
    """어느 나이든 오류 없이 안내가 나와요 (꽃 받기만 19~29세로 한정)."""
    screenings, extras, guide = _texts(age)
    assert guide["eyebrow"] == f"만 {age}세" and guide["screenings"], f"만 {age}세에 해당하는 검진이 하나도 없어요"


def test_age_rules_follow_nhis_standards():
    # 만 19세: 직장가입자·세대주만 대상일 수 있고 20세부터 정신건강·자궁경부암이 해당
    s19, e19, g19 = _texts(19)
    assert "세대원" in s19 and "자궁경부암" not in s19 and not g19["extras"]
    # 20대: 이상지질혈증은 남성 24세부터
    _, e23, _ = _texts(23)
    _, e24, _ = _texts(24)
    assert "이상지질혈증" not in e23 and "이상지질혈증" in e24 and "정신건강검사" in e23
    # 40세: 암검진 시작 + 40세 한정 항목(B형간염 등)
    s40, e40, _ = _texts(40)
    assert "위암" in s40 and "유방암" in s40 and "B형간염" in e40 and "생활습관평가" in e40
    s41, e41, _ = _texts(41)
    assert "B형간염" not in e41  # 40세에만 받는 항목
    # 50세: 대장암, 54~74세: 폐암 고위험군
    assert "대장암" in _texts(50)[0] and "폐암" not in _texts(50)[0] and "폐암" in _texts(54)[0] and "폐암" not in _texts(75)[0]
    # 66세 이상: 인지기능장애 검사 · 의료급여 생애전환기검진
    s66, e66, _ = _texts(66)
    assert "인지기능장애" in e66 and "생애전환기" in s66 and "폐기능" in e66
    # 어린이·학생
    assert "영유아" in _texts(2)[0] and "학생" in _texts(12)[0]


def test_next_change_points_to_the_next_milestone():
    from data import health_content as D

    assert D.next_change(19)[0] == 20
    age, names = D.next_change(30)
    assert age == 35 and any("정신건강검사" in n for n in names)
    assert D.next_change(120) is None
    assert "다음 변화: 만 40세부터" in D.my_age_guide(36)["tip"]


@pytest.mark.parametrize("age,band", [(None, None), (5, "만 18세 이하"), (19, "만 19세"), (25, "20대"), (39, "30대"), (49, "40대"), (59, "50대"), (65, "60대"), (70, "70세 이상"), (101, "70세 이상")])
def test_band_for_age(age, band):
    from data import health_content as D

    assert D.band_for_age(age) == band


def test_every_band_has_a_guide():
    from data import health_content as D

    for name in D.AGE_BANDS:
        guide = D.band_guide(name)
        assert guide["eyebrow"] == name and guide["screenings"]
