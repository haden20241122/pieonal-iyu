"""간이 위치 검색 (mock).

실제 지도 API(Kakao Local / Naver Geocoding 등)를 연결하기 전까지,
서울 25개 자치구와 주요 지역의 '근사 좌표'만 알고 있는 작은 사전으로 검색을 흉내 냅니다.
API 를 붙일 때는 `search_location()` 안쪽만 API 호출로 바꾸면 화면 코드는 그대로 쓸 수 있어요.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass

SEOUL_CITY_HALL = (37.5663, 126.9779)


@dataclass(frozen=True)
class GeoResult:
    label: str  # 화면에 보여줄 이름
    lat: float
    lon: float
    matched: bool  # False → 검색어를 알아보지 못해 기본 위치를 쓴 경우
    kind: str  # district | landmark | default | mock_gps


# 자치구 중심 (근사 좌표)
_DISTRICTS = {
    "종로구": (37.5735, 126.9788), "중구": (37.5638, 126.9975), "용산구": (37.5326, 126.9906),
    "성동구": (37.5634, 127.0369), "광진구": (37.5385, 127.0823), "동대문구": (37.5744, 127.0396),
    "중랑구": (37.6066, 127.0927), "성북구": (37.5894, 127.0167), "강북구": (37.6397, 127.0257),
    "도봉구": (37.6688, 127.0471), "노원구": (37.6542, 127.0568), "은평구": (37.6027, 126.9291),
    "서대문구": (37.5791, 126.9368), "마포구": (37.5663, 126.9019), "양천구": (37.5169, 126.8664),
    "강서구": (37.5510, 126.8495), "구로구": (37.4954, 126.8874), "금천구": (37.4569, 126.8955),
    "영등포구": (37.5264, 126.8963), "동작구": (37.5124, 126.9393), "관악구": (37.4784, 126.9516),
    "서초구": (37.4837, 127.0324), "강남구": (37.5172, 127.0473), "송파구": (37.5145, 127.1059),
    "강동구": (37.5301, 127.1238),
}

# 주요 지역·역 (이름, 별칭, 위도, 경도)
_LANDMARKS = [
    ("서울시청", ("시청",), 37.5663, 126.9779),
    ("서울역", (), 37.5547, 126.9707),
    ("광화문", (), 37.5759, 126.9769),
    ("명동", (), 37.5636, 126.9869),
    ("종로3가", ("종로삼가",), 37.5704, 126.9922),
    ("동대문", ("동대문역사문화공원",), 37.5711, 127.0095),
    ("혜화", ("대학로",), 37.5822, 127.0018),
    ("이태원", (), 37.5345, 126.9946),
    ("왕십리", (), 37.5612, 127.0371),
    ("성수", ("성수동",), 37.5446, 127.0557),
    ("건대입구", ("건대",), 37.5404, 127.0692),
    ("잠실", (), 37.5133, 127.1002),
    ("천호", (), 37.5386, 127.1237),
    ("강남역", (), 37.4979, 127.0276),
    ("압구정", (), 37.5271, 127.0284),
    ("선릉", (), 37.5045, 127.0490),
    ("삼성", ("코엑스",), 37.5119, 127.0590),
    ("양재", (), 37.4845, 127.0342),
    ("교대", (), 37.4934, 127.0146),
    ("사당", (), 37.4765, 126.9816),
    ("노량진", (), 37.5133, 126.9426),
    ("신림", (), 37.4843, 126.9297),
    ("여의도", (), 37.5219, 126.9245),
    ("홍대입구", ("홍대", "홍익대"), 37.5572, 126.9245),
    ("신촌", ("이대",), 37.5551, 126.9366),
    ("합정", (), 37.5496, 126.9139),
    ("상암", (), 37.5779, 126.8896),
    ("마곡", (), 37.5601, 126.8256),
    ("목동", (), 37.5264, 126.8642),
    ("구로디지털단지", ("구디",), 37.4853, 126.9015),
    ("가산디지털단지", ("가디",), 37.4816, 126.8827),
    ("노원역", ("노원",), 37.6551, 127.0619),
    ("수유", (), 37.6386, 127.0256),
    ("불광", (), 37.6106, 126.9301),
]


def _norm(text: str) -> str:
    # '서울 마포구' 같은 입력은 아래 2단계(검색어 안에 지역명 포함)에서 처리되므로 접두어는 지우지 않아요.
    return re.sub(r"\s+", "", text or "").lower()


_WHOLE_CITY = {"서울", "서울시", "서울특별시"}


def _build_index() -> list[tuple[str, str, float, float, str]]:
    """(검색 키, 화면 이름, 위도, 경도, 종류) 목록."""
    index: list[tuple[str, str, float, float, str]] = []
    for name, (lat, lon) in _DISTRICTS.items():
        index.append((name, name, lat, lon, "district"))
        short = name[:-1]  # '강남구' → '강남'
        if len(short) >= 2:  # '중구' → '중' 처럼 한 글자가 되는 경우는 제외
            index.append((short, name, lat, lon, "district"))
    for name, aliases, lat, lon in _LANDMARKS:
        for key in (name, *aliases):
            index.append((key, name, lat, lon, "landmark"))
    return index


_INDEX = _build_index()
KNOWN_EXAMPLES = "강남구, 홍대입구, 서울시청, 잠실, 성수"


def search_location(query: str) -> GeoResult | None:
    """검색어 → 위치. 알아보지 못하면 None."""
    q = _norm(query)
    if not q:
        return None
    if q in _WHOLE_CITY:
        lat, lon = SEOUL_CITY_HALL
        return GeoResult("서울 전체", lat, lon, True, "default")

    # 1) 완전히 같은 이름
    for key, label, lat, lon, kind in _INDEX:
        if q == key:
            return GeoResult(label, lat, lon, True, kind)
    # 2) 검색어 안에 지역명이 들어 있는 경우 (예: '강남역 근처') — 긴 이름 우선
    contained = [item for item in _INDEX if item[0] in q]
    if contained:
        key, label, lat, lon, kind = max(contained, key=lambda item: len(item[0]))
        return GeoResult(label, lat, lon, True, kind)
    # 3) 지역명이 검색어를 포함하는 경우 (예: '홍대' → '홍대입구') — 짧은 이름 우선
    if len(q) >= 2:
        partial = [item for item in _INDEX if q in item[0]]
        if partial:
            key, label, lat, lon, kind = min(partial, key=lambda item: len(item[0]))
            return GeoResult(label, lat, lon, True, kind)
    return None


def default_location() -> GeoResult:
    lat, lon = SEOUL_CITY_HALL
    return GeoResult("서울시청 부근", lat, lon, False, "default")


def location_from_place(name: str, lat: float, lon: float) -> GeoResult:
    """특정 장소(예: 검진 받은 병원)를 검색 위치로 쓰기 위한 변환."""
    return GeoResult(f"{name} 근처", lat, lon, True, "clinic")


def mock_current_location() -> GeoResult:
    """'현재 위치' 버튼용 모의 위치 (실제 GPS 아님)."""
    lat, lon = SEOUL_CITY_HALL
    return GeoResult("현재 위치 (모의: 서울시청 부근)", lat, lon, True, "mock_gps")


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))
