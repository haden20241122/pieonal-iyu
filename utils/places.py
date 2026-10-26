"""꽃집·검진기관 데이터 로더.

지금은 data/ 폴더의 '샘플 CSV'(is_sample=TRUE)를 읽습니다.
실제 API(공공데이터포털 건강검진기관 조회, 서울시 인증 꽃집 목록 등)를 연결할 때는
`load_places()` 안에서 API 결과를 같은 `Place` 형태로 돌려주면 화면 코드는 바꾸지 않아도 됩니다.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, replace
from functools import lru_cache
from typing import Literal

from config.settings import BASE_DIR
from utils.geo import haversine_km

Kind = Literal["clinic", "flower"]

_SAMPLE_FILES = {
    "clinic": BASE_DIR / "data" / "sample_health_facilities.csv",
    "flower": BASE_DIR / "data" / "sample_flower_shops.csv",
}


@dataclass(frozen=True)
class Place:
    id: str
    kind: str  # clinic | flower
    name: str
    district: str
    address: str
    phone: str
    lat: float
    lon: float
    hours: str = ""  # 운영/영업시간
    info: str = ""  # 검진 관련 정보(검진기관)
    url: str = ""  # 홈페이지/상세정보 (없으면 빈 문자열 — 검진기관은 공단 검진기관 찾기로, 꽃집은 링크 없음)
    campaign_active: bool = True  # 꽃집: 캠페인 꽃 수령 가능 여부
    is_sample: bool = True  # ★ 샘플(가짜) 데이터 여부 — 화면에 '샘플' 배지로 표시
    distance_km: float | None = None  # 검색 위치로부터 거리 (검색 후 채워짐)


def _truthy(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "y", "yes"}


def _read_sample(kind: Kind) -> list[Place]:
    path = _SAMPLE_FILES[kind]
    if not path.exists():
        return []
    places: list[Place] = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            try:
                places.append(
                    Place(
                        id=row["id"],
                        kind=kind,
                        name=row["name"],
                        district=row.get("district", ""),
                        address=row.get("address", ""),
                        phone=row.get("phone", ""),
                        lat=float(row["lat"]),
                        lon=float(row["lon"]),
                        hours=row.get("hours", ""),
                        info=row.get("screening_info", ""),
                        url=row.get("url", ""),
                        campaign_active=_truthy(row.get("campaign_active", "TRUE")),
                        is_sample=_truthy(row.get("is_sample", "TRUE")),
                    )
                )
            except (KeyError, ValueError):
                continue  # 잘못된 줄은 건너뜀 (앱이 멈추지 않도록)
    return places


@lru_cache(maxsize=4)
def load_places(kind: Kind) -> tuple[Place, ...]:
    """★ 데이터 소스를 고르는 지점 — 실제 API 연결 시 여기만 수정하세요."""
    # 예) if kind == "clinic" and settings.PUBLIC_DATA_API_KEY: return tuple(_from_public_api())
    return tuple(_read_sample(kind))


def find_nearby(
    kind: Kind,
    lat: float,
    lon: float,
    limit: int = 8,
    only_active: bool = False,
) -> list[Place]:
    """검색 위치에서 가까운 순으로 정렬해 돌려줍니다."""
    places = [p for p in load_places(kind) if (p.campaign_active or not only_active)]
    ranked = [replace(p, distance_km=haversine_km(lat, lon, p.lat, p.lon)) for p in places]
    ranked.sort(key=lambda p: p.distance_km or 0.0)
    return ranked[:limit]


def has_sample_data(places: list[Place]) -> bool:
    return any(p.is_sample for p in places)
