"""건강검진 안내 콘텐츠 (검사항목 · 연령별 건강정보).

★ 이 파일의 내용은 2026-11-02 에 국민건강보험공단(nhis.or.kr) 공식 페이지를 직접 확인해 작성했어요.
   - 일반건강검진 실시안내: https://www.nhis.or.kr/nhis/healthin/wbhaca04500m01.do
   - 암검진 실시안내:       https://www.nhis.or.kr/nhis/healthin/wbhaca04600m01.do
   - 건강검진 로드맵:       https://www.nhis.or.kr/nhis/healthin/retrieveHltExmdLoadMap.do
   공단 페이지 사이에 표기가 다른 곳은 '일반건강검진 실시안내' 페이지를 기준으로 했어요.
   (예: 골밀도 검사 — 실시안내 '54·60·66세 여성' / 제도소개 '54·66세 여성')
   공단에서 확인되지 않는 내용(민간 종합검진·질환 설명 등)은 넣지 않았어요.
   검진 기준은 해마다 바뀔 수 있으니 배포 전·연 1회 공단 페이지와 다시 대조하세요.

항목 형식(모든 항목 공통):
    name      검사명
    target    대상
    desc      간단한 설명
    cost      비용 관련 안내
    source    SOURCES 의 키 (출처 표시용)
    verified  공식 자료 확인 여부
"""
from dataclasses import dataclass

from config.campaign import NHIS_CANCER_URL, NHIS_RESULT_URL, NHIS_ROADMAP_URL, TARGET_AGE_MAX, TARGET_AGE_MIN, TARGET_LABEL

# ── 출처 목록 ─────────────────────────────────────────────
SOURCES = {
    "nhis_general": {"name": "국민건강보험공단 — 일반건강검진 실시안내", "url": NHIS_RESULT_URL},
    "nhis_cancer": {"name": "국민건강보험공단 — 암검진 실시안내", "url": NHIS_CANCER_URL},
    "nhis_roadmap": {"name": "국민건강보험공단 — 건강검진 로드맵", "url": NHIS_ROADMAP_URL},
}

DISCLAIMER = (
    "국민건강보험공단 공개 자료를 바탕으로 정리한 안내예요. 진단이나 건강 상태 판단을 대신하지는 않아요. "
    "실제로 검진 대상인지는 공단에서 확인하고, 불편한 증상이 있으면 의료진과 상담하세요."
)

# ── 검사항목 (탭 4개) ─────────────────────────────────────
SCREENING_CATEGORIES = [
    ("general", "일반건강검진"),
    ("extra", "성·연령별 추가 항목"),
    ("cancer", "국가암검진"),
    ("cost", "비용 안내"),
]

_EXTRA_COST = "일반건강검진의 성·연령별 항목이에요."
_CANCER_COST_90 = "공단 90%, 수검자 10% 부담이에요. 건강보험료 하위 50%(전년도 11월 기준)와 의료급여수급권자는 본인부담이 없어요."

SCREENINGS = {
    "general": [
        {
            "name": "일반건강검진",
            "target": "지역가입자 세대주와 20세 이상 세대원, 직장가입자, 20세 이상 직장 피부양자, 20~64세 의료급여수급권자",
            "desc": "2년마다 1회 받아요(비사무직 직장가입자는 매년). 검진 기간은 매년 1월 1일~12월 31일이에요.",
            "cost": "정해진 검진 항목 외의 검사를 추가로 하면 비용이 발생해요.",
            "source": "nhis_general",
            "verified": True,
        },
        {
            "name": "공통 검사항목",
            "target": "일반건강검진 대상자 모두",
            "desc": "진찰 및 상담, 신체계측(신장·체중·허리둘레·비만도), 시력·청력검사, 혈압측정, 흉부방사선 검사, "
            "혈액검사(혈색소·공복혈당·AST·ALT·γ-GTP·혈청크레아티닌·e-GFR), 요검사, 구강검진을 해요.",
            "cost": "일반건강검진에 포함돼요.",
            "source": "nhis_general",
            "verified": True,
        },
        {
            "name": "검진 받을 때 준비물",
            "target": "일반건강검진 대상자",
            "desc": "일반건강검진결과 통보서와 신분증을 지참해서 검진기관을 방문해야 해요. "
            "의료급여수급권자는 의료전달체계에 따라 가까운 의원에서 받아요.",
            "cost": "그 외 검사를 하면 비용이 발생해요.",
            "source": "nhis_general",
            "verified": True,
        },
        {
            "name": "의료급여 생애전환기검진",
            "target": "66세 이상 의료급여수급권자(65세 이상 의료급여수급권자는 일반건강검진 대상에서 제외돼요)",
            "desc": "2년마다 받는 검진이에요. 진찰·신체계측·시력·청력 등 공통항목과 성·연령별 항목(골다공증, 인지기능장애, "
            "정신건강(우울증), 생활습관평가, 노인신체기능 등)으로 구성돼요.",
            "cost": "본인부담이 없어요.",
            "source": "nhis_roadmap",
            "verified": True,
        },
    ],
    "extra": [
        {
            "name": "이상지질혈증 검사",
            "target": "남성 24세 이상, 여성 40세 이상 — 4년마다(남성 24·28·32…세, 여성 40·44·48…세)",
            "desc": "총콜레스테롤, HDL, 중성지방, LDL 수치를 확인해요.",
            "cost": _EXTRA_COST,
            "source": "nhis_general",
            "verified": True,
        },
        {
            "name": "정신건강검사(우울증)",
            "target": "20~34세는 2년마다, 35~39세·40대·50대·60대·70대는 각 연령대에서 1회",
            "desc": "마음 건강 상태를 살펴보는 우울증 선별검사예요.",
            "cost": _EXTRA_COST,
            "source": "nhis_general",
            "verified": True,
        },
        {
            "name": "조기정신증 검사",
            "target": "20~34세 — 2년마다",
            "desc": "조기정신증 선별검사예요.",
            "cost": _EXTRA_COST,
            "source": "nhis_general",
            "verified": True,
        },
        {
            "name": "B형간염 · C형간염 검사",
            "target": "B형간염 40세(보균자·면역자 제외), C형간염 56세",
            "desc": "해당 나이에 한 번 받는 간염 검사예요.",
            "cost": "C형간염 확진검사에서는 본인부담금이 발생하고, 정부24 또는 보건소에 별도 정산 신청이 필요해요.",
            "source": "nhis_general",
            "verified": True,
        },
        {
            "name": "폐기능 검사",
            "target": "56세, 66세",
            "desc": "해당 나이에 받는 검사예요.",
            "cost": _EXTRA_COST,
            "source": "nhis_general",
            "verified": True,
        },
        {
            "name": "골밀도 검사",
            "target": "여성 54세, 60세, 66세",
            "desc": "해당 나이의 여성에게 실시하는 검사예요.",
            "cost": _EXTRA_COST,
            "source": "nhis_general",
            "verified": True,
        },
        {
            "name": "생활습관평가",
            "target": "40세, 50세, 60세, 70세",
            "desc": "해당 나이에 생활습관을 평가해요.",
            "cost": _EXTRA_COST,
            "source": "nhis_general",
            "verified": True,
        },
        {
            "name": "치면세균막 검사",
            "target": "40세",
            "desc": "구강검진의 하나로, 해당 나이에 받아요.",
            "cost": _EXTRA_COST,
            "source": "nhis_general",
            "verified": True,
        },
        {
            "name": "인지기능장애 검사",
            "target": "66세 이상 — 2년마다(66·68·70…세)",
            "desc": "인지기능 상태를 확인하는 검사예요.",
            "cost": _EXTRA_COST,
            "source": "nhis_general",
            "verified": True,
        },
        {
            "name": "노인신체기능 검사",
            "target": "66세, 70세, 80세",
            "desc": "해당 나이에 신체기능 상태를 확인해요.",
            "cost": _EXTRA_COST,
            "source": "nhis_general",
            "verified": True,
        },
    ],
    "cancer": [
        {
            "name": "위암 검진",
            "target": "40세 이상 남녀 — 2년마다",
            "desc": "위내시경검사를 해요. 어려운 경우 위장조영검사를 선택할 수 있어요.",
            "cost": _CANCER_COST_90,
            "source": "nhis_cancer",
            "verified": True,
        },
        {
            "name": "대장암 검진",
            "target": "50세 이상 남녀 — 1년마다",
            "desc": "1단계로 분변잠혈검사를 하고, 결과가 양성이면 2단계로 대장내시경검사를 해요.",
            "cost": "검진 비용은 전액 공단이 부담해요. 분변잠혈검사 없이 대장내시경을 받으면 검사비 전액이 본인부담이에요.",
            "source": "nhis_cancer",
            "verified": True,
        },
        {
            "name": "유방암 검진",
            "target": "40세 이상 여성 — 2년마다",
            "desc": "유방 촬영검사를 해요.",
            "cost": _CANCER_COST_90,
            "source": "nhis_cancer",
            "verified": True,
        },
        {
            "name": "자궁경부암 검진",
            "target": "20세 이상 여성 — 2년마다",
            "desc": "자궁경부세포검사를 해요.",
            "cost": "검진 비용은 전액 공단이 부담해요.",
            "source": "nhis_cancer",
            "verified": True,
        },
        {
            "name": "간암 검진 (고위험군)",
            "target": "40세 이상 중 간암 발생 고위험군 — 6개월마다(상·하반기 각 1회). "
            "고위험군: ① 최근 2개년도 보험급여 내역에 간경변증·B형간염·C형간염·B형 또는 C형 간염 바이러스에 의한 만성 간질환이 있는 경우, "
            "② 과거 일반건강검진에서 B형간염 표면항원 또는 C형간염 항체가 양성인 경우",
            "desc": "간 초음파검사와 혈액검사(혈청알파태아단백검사)를 해요.",
            "cost": _CANCER_COST_90,
            "source": "nhis_cancer",
            "verified": True,
        },
        {
            "name": "폐암 검진 (고위험군)",
            "target": "54~74세 남녀 중 폐암 발생 고위험군 — 2년마다. 고위험군은 ① 최근 2년 내 국가건강검진 문진표로 30갑년 이상 흡연력이 확인되고 현재 흡연 중인 경우, "
            "② 건강보험 금연치료 사업 문진표로 30갑년 이상이 확인되는 경우, ③ 국가폐암검진을 받았고 검진 후 금연 15년 이내인 경우(74세까지)예요. "
            "(1갑년 = 하루 1갑(20개비) × 흡연 1년)",
            "desc": "저선량 흉부 CT검사를 하고, 결과 상담을 받아요.",
            "cost": _CANCER_COST_90,
            "source": "nhis_cancer",
            "verified": True,
        },
    ],
    "cost": [
        {
            "name": "국가암검진 본인부담",
            "target": "국가암검진 대상자",
            "desc": "위암·유방암·간암·폐암은 공단 90%, 수검자 10%를 부담해요. 대장암과 자궁경부암은 검진 비용을 전액 공단이 부담해요.",
            "cost": "국가암검진사업 대상자(전년도 11월 건강보험료 기준 하위 50%)와 의료급여수급권자는 수검자 부담이 없어요.",
            "source": "nhis_cancer",
            "verified": True,
        },
        {
            "name": "대장내시경 비용",
            "target": "대장암 검진 대상자",
            "desc": "분변잠혈검사 없이 바로 대장내시경을 받으면 검사비 전액을 본인이 부담해요. "
            "분변잠혈검사에서 양성이 나온 뒤의 대장내시경은 수면검사·용종 제거 등으로 별도 비용이 생길 수 있어요.",
            "cost": "자세한 비용은 검진기관에 확인하세요.",
            "source": "nhis_cancer",
            "verified": True,
        },
        {
            "name": "검진 항목 외 검사",
            "target": "일반건강검진 대상자",
            "desc": "정해진 검진 항목 외의 검사를 추가로 하면 비용이 발생해요.",
            "cost": "받기 전에 검진기관에 비용을 확인하세요.",
            "source": "nhis_general",
            "verified": True,
        },
    ],
}

# ── 연령별 건강정보 (모든 나이) ────────────────────────────
# 건강검진 정보는 나이와 상관없이 누구나 볼 수 있어요. 나이를 알려주면 그 나이에 해당하는 검진을 계산해서 보여주고,
# 꽃 받기 이벤트만 캠페인 대상(만 19~29세)으로 한정돼요 (is_target_age).
# 규칙은 국민건강보험공단 '일반건강검진 실시안내'·'암검진 실시안내'·'건강검진 로드맵'(2026-11-02 확인)을 따라요.
CHECKUP_NOTE = "해당 연도의 정확한 대상 여부는 국민건강보험공단 대상자 조회에서 확인해주세요."


def is_target_age(age) -> bool:
    """꽃 받기 이벤트 대상(만 19~29세)인지."""
    return age is not None and TARGET_AGE_MIN <= age <= TARGET_AGE_MAX


@dataclass(frozen=True)
class Rule:
    text: str  # 화면에 보이는 문구 (조건이 문구 안에 들어 있어요)
    kind: str  # "screening"(해당하는 검진) | "extra"(나이에 따라 받는 추가 항목)
    name: str  # '다음 변화' 안내에 쓰는 짧은 이름
    min_age: int = 0
    max_age: int = 200
    exact: tuple[int, ...] = ()  # 이 나이에만 받는 항목이면 해당 나이들 (비어 있으면 min~max 전체)

    def applies(self, age: int) -> bool:
        return age in self.exact if self.exact else self.min_age <= age <= self.max_age

    @property
    def starts(self) -> tuple[int, ...]:
        """새로 해당되기 시작하는 나이."""
        return self.exact if self.exact else (self.min_age,)


RULES = [
    # ── 해당하는 검진 ──
    Rule("영유아 건강검진(생후 14일~71개월, 총 8차)", "screening", "영유아 건강검진", 0, 5),
    Rule("학생 건강검진(초1·초4·중1·고1 일반검진, 구강검진은 초등 전학년·중1·고1)", "screening", "학생 건강검진", 6, 18),
    Rule("일반건강검진: 직장가입자·지역가입자 세대주라면 대상일 수 있어요(세대원·피부양자는 만 20세부터)", "screening", "일반건강검진", exact=(19,)),
    Rule("일반건강검진(2년마다, 비사무직 직장가입자는 매년)", "screening", "일반건강검진", 20),
    Rule("자궁경부암 검진(20세 이상 여성, 2년마다)", "screening", "자궁경부암 검진(여성)", 20),
    Rule("위암 검진(40세 이상, 2년마다)", "screening", "위암 검진", 40),
    Rule("유방암 검진(40세 이상 여성, 2년마다)", "screening", "유방암 검진(여성)", 40),
    Rule("간암 검진(40세 이상 고위험군, 6개월마다)", "screening", "간암 검진(고위험군)", 40),
    Rule("대장암 검진(50세 이상, 1년마다)", "screening", "대장암 검진", 50),
    Rule("폐암 검진(54~74세 고위험군, 2년마다)", "screening", "폐암 검진(고위험군)", 54, 74),
    Rule("의료급여 생애전환기검진(66세 이상 의료급여수급권자, 2년마다)", "screening", "의료급여 생애전환기검진", 66),
    # ── 나이에 따라 받는 추가 항목 ──
    Rule("정신건강검사(우울증): 20~34세 2년마다", "extra", "정신건강검사(우울증)", 20, 34),
    Rule("정신건강검사(우울증): 35~39세·40대·50대·60대·70대 각 1회", "extra", "정신건강검사(우울증)", 35, 79),
    Rule("조기정신증 검사: 20~34세 2년마다", "extra", "조기정신증 검사", 20, 34),
    Rule("이상지질혈증 검사(남성 24세 이상, 4년마다)", "extra", "이상지질혈증 검사(남성)", 24),
    Rule("이상지질혈증 검사(여성 40세 이상, 4년마다)", "extra", "이상지질혈증 검사(여성)", 40),
    Rule("B형간염 검사(40세, 보균자·면역자 제외)", "extra", "B형간염 검사", exact=(40,)),
    Rule("생활습관평가(40·50·60·70세)", "extra", "생활습관평가", exact=(40, 50, 60, 70)),
    Rule("치면세균막 검사(40세)", "extra", "치면세균막 검사", exact=(40,)),
    Rule("C형간염 검사(56세)", "extra", "C형간염 검사", exact=(56,)),
    Rule("폐기능 검사(56·66세)", "extra", "폐기능 검사", exact=(56, 66)),
    Rule("골밀도 검사(여성 54·60·66세)", "extra", "골밀도 검사(여성)", exact=(54, 60, 66)),
    Rule("인지기능장애 검사(66세 이상, 2년마다)", "extra", "인지기능장애 검사", 66),
    Rule("노인신체기능 검사(66·70·80세)", "extra", "노인신체기능 검사", exact=(66, 70, 80)),
]


def rules_for(ages) -> tuple[list[str], list[str]]:
    """주어진 나이(들) 중 하나라도 해당하는 검진·추가 항목 문구."""
    screenings: list[str] = []
    extras: list[str] = []
    for rule in RULES:
        if any(rule.applies(a) for a in ages):
            (screenings if rule.kind == "screening" else extras).append(rule.text)
    return screenings, extras


def next_change(age: int) -> tuple[int, list[str]] | None:
    """앞으로 처음 새로 해당되는 검진이 생기는 나이와 그 이름들. 더 없으면 None."""
    upcoming = sorted({s for rule in RULES for s in rule.starts if s > age})
    if not upcoming:
        return None
    nxt = upcoming[0]
    names: list[str] = []
    for rule in RULES:
        if nxt in rule.starts and rule.name not in names:
            names.append(rule.name)
    return nxt, names


def _source_for(age: int) -> str:
    return "nhis_general" if age >= 19 else "nhis_roadmap"


def my_age_guide(age: int) -> dict:
    """한 사람의 나이(만 나이)에 해당하는 검진 안내."""
    screenings, extras = rules_for([age])
    tip = []
    if age >= 19:
        tip.append("검진 때는 일반건강검진결과 통보서와 신분증을 챙겨가세요.")
    change = next_change(age)
    if change:
        tip.append(f"다음 변화: 만 {change[0]}세부터 {', '.join(change[1])}.")
    tip.append(CHECKUP_NOTE)
    return {
        "eyebrow": f"만 {age}세",
        "headline": f"만 {age}세, 지금 받을 수 있는 검진",
        "screenings": screenings,
        "extras": extras,
        "tip": " ".join(tip),
        "source": _source_for(age),
        "verified": True,
    }


# 나이대(구간) 둘러보기 — 나이를 입력하지 않아도 볼 수 있어요
AGE_BANDS = {
    "만 18세 이하": range(0, 19),
    "만 19세": range(19, 20),
    "20대": range(20, 30),
    "30대": range(30, 40),
    "40대": range(40, 50),
    "50대": range(50, 60),
    "60대": range(60, 70),
    "70세 이상": range(70, 121),
}
DEFAULT_BAND = "20대"  # 나이를 입력하지 않았을 때 먼저 보여줄 구간


def band_for_age(age) -> str | None:
    if age is None:
        return None
    return next((name for name, ages in AGE_BANDS.items() if age in ages), None)


def band_guide(name: str) -> dict:
    ages = AGE_BANDS[name]
    screenings, extras = rules_for(ages)
    tip = []
    if ages.stop > 19:
        tip.append("검진 때는 일반건강검진결과 통보서와 신분증을 챙겨가세요.")
    tip.append(CHECKUP_NOTE)
    return {
        "eyebrow": name,
        "headline": f"{name}에 해당하는 검진",
        "screenings": screenings,
        "extras": extras,
        "tip": " ".join(tip),
        "source": _source_for(ages.start),
        "verified": True,
    }
