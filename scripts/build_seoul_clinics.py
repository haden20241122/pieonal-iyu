"""서울 일반건강검진 기관 데이터 만들기 (1회 실행용).

입력 : 공공데이터포털 '국민건강보험공단_검진기관별 검진유형내역' CSV (cp949)
       → 서울특별시 + '일반' 칸이 채워진(내원/출장) 기관만 사용 (= 일반건강검진을 받을 수 있는 기관)
처리 : 이 파일에는 주소·전화·좌표가 없어서, 카카오 로컬 API(키워드 검색)로 채움
       · 같은 구 안에서 상호가 같은 곳만 자동 채택 (엉뚱한 병원이 섞이지 않게)
       · 상호가 조금 다른 곳은 '같은 구에서 후보가 딱 1곳'일 때만 채택, 그 외는 제외하고 후보를 기록
출력 : data/seoul_health_facilities.csv  (is_sample=FALSE)
       data/runtime/seoul_unmatched.txt   (제외한 기관 + 카카오 후보 → 확인 후 MANUAL_IDS 에 추가)

실행:  .\\.venv\\Scripts\\python.exe -I scripts\\build_seoul_clinics.py "<검진유형내역.csv 경로>"
"""
from __future__ import annotations

import csv
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from config import settings  # noqa: E402

OUT = ROOT / "data" / "seoul_health_facilities.csv"
REPORT = ROOT / "data" / "runtime" / "seoul_unmatched.txt"
CHECKS = ["영유아", "구강", "위암", "대장암", "간암", "유방암", "자궁경부암", "폐암"]
LABEL = {"영유아": "영유아검진", "구강": "구강검진", "위암": "위암검진", "대장암": "대장암검진",
         "간암": "간암검진", "유방암": "유방암검진", "자궁경부암": "자궁경부암검진", "폐암": "폐암검진"}

# 공단 기관명 → 카카오 장소 id (수동 확인한 것). 같은 구 안에서 후보가 1곳뿐이고 업종이 일치하는 경우만 등록.
MANUAL_IDS = {
    ("성북구", "연세속편한의원"): "14671306",
    ("성북구", "김동일내과의원"): "17110585",
    ("성북구", "SKY서울가정의학과의원"): "26826211",
    ("성북구", "국민건강내과의원"): "2006631714",
    ("성북구", "속편한내과의원"): "621801014",
}

_MEDICAL = re.compile(r"의료|병원|의원|건강")


def norm(s: str) -> str:
    return re.sub(r"[\s()·\-,.]", "", s).lower()


def core(s: str) -> str:
    """공단 기관명에서 '(MB)' 같은 괄호 병기와 '의료법인○○재단' 같은 법인 접두어를 걷어낸 이름."""
    s = re.sub(r"\([^)]*\)", "", s)  # 서울엠비(MB)내과의원 → 서울엠비내과의원
    s = re.sub(r"^(의료법인|재단법인|학교법인|사회복지법인)", "", s)
    s = re.sub(r"^.{1,12}?(재단|학원)(?=.{3,})", "", s)  # 동신의료재단동신병원 → 동신병원
    return norm(s)


def kakao_search(query: str) -> list[dict]:
    url = "https://dapi.kakao.com/v2/local/search/keyword.json?" + urllib.parse.urlencode({"query": query, "size": 10})
    req = urllib.request.Request(url, headers={"Authorization": f"KakaoAK {settings.KAKAO_REST_API_KEY}"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read().decode("utf-8")).get("documents", [])
        except Exception:
            time.sleep(1 + attempt)
    return []


def in_gu(d: dict, gu: str) -> bool:
    addr = d.get("road_address_name") or d.get("address_name", "")
    return addr.startswith("서울") and f" {gu} " in f" {addr} "


def pick(gu: str, name: str, docs: list[dict]) -> tuple[dict | None, list[dict]]:
    """(채택한 문서, 후보 목록). 채택 못 하면 (None, 같은 구 의료기관 후보)."""
    target = norm(name)
    base = core(name)
    local = [d for d in docs if in_gu(d, gu)]
    manual = MANUAL_IDS.get((gu, name))
    for d in local:
        if (manual and d["id"] == manual) or norm(d["place_name"]) in (target, base):
            return d, local
    # 상호가 조금 다른 경우: 같은 구에서 이름이 서로 포함되는 의료기관이 정확히 1곳일 때만
    loose = [d for d in local if _MEDICAL.search(d.get("category_name", ""))
             and len(base) >= 4 and (base in norm(d["place_name"]) or norm(d["place_name"]) in base)]
    if len({d["id"] for d in loose}) > 1:  # 본관·신관·응급실 등으로 갈리면 '본관'만 인정
        loose = [d for d in loose if "본관" in d["place_name"]]
    if len({d["id"] for d in loose}) == 1:
        return loose[0], local
    return None, local


def main(csv_path: str) -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows 콘솔(cp949)에서도 멈추지 않게
    if not settings.KAKAO_REST_API_KEY:
        sys.exit("KAKAO_REST_API_KEY 가 .env 에 없어요.")
    with open(csv_path, encoding="cp949", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["시도명"].startswith("서울") and r["일반"].strip()]
    print(f"서울 일반건강검진 기관: {len(rows)}곳", flush=True)

    out, missed, seen_ids = [], [], set()
    for i, r in enumerate(rows, 1):
        name, gu = r["검진기관명"].strip(), r["시군구명"].strip()
        doc, cands = pick(gu, name, kakao_search(f"{gu} {name}"))
        if doc is None:  # 구 이름 없이 한 번 더 (상호만으로 검색)
            time.sleep(0.1)
            doc, cands2 = pick(gu, name, kakao_search(f"서울 {name}"))
            cands = cands or cands2
        if doc is None or doc["id"] in seen_ids:
            reason = "중복" if doc is not None else "미매칭"
            hint = " / ".join(f"{d['place_name']}({d.get('road_address_name') or d['address_name']})" for d in cands[:3])
            missed.append(f"{gu}\t{name}\t{reason}\t{hint}")
        else:
            seen_ids.add(doc["id"])
            extra = [LABEL[c] for c in CHECKS if r[c].strip()]
            out.append({
                "id": f"SE{len(out) + 1:04d}",
                "name": name,
                "district": gu,
                "address": doc.get("road_address_name") or doc["address_name"],
                "phone": doc.get("phone", ""),
                "lat": doc["y"],
                "lon": doc["x"],
                "screening_info": " · ".join(["일반건강검진", *extra]),
                "hours": "",
                "url": doc.get("place_url", ""),
                "is_sample": "FALSE",
            })
        if i % 50 == 0:
            print(f"  {i}/{len(rows)} (채움 {len(out)}, 제외 {len(missed)})", flush=True)
        time.sleep(0.12)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("구\t기관명\t사유\t카카오 후보\n" + "\n".join(missed), encoding="utf-8")
    print(f"\n저장: {OUT} ({len(out)}곳) / 제외 {len(missed)}곳 → {REPORT}", flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
