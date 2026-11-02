"""캠페인 효과 분석용 데이터 구조 + 가상(mock) 데이터 + 집계 함수.

★ 이 파일이 만들어내는 숫자는 전부 '가상 데이터'입니다. 실제 캠페인 결과가 아니에요.
   실제 응답이 생기면 같은 열 구성(SCHEMA)의 CSV 를 대시보드에서 올리거나,
   `load_responses()` 를 Google Sheets·DB 읽기로 바꾸면 화면 코드는 그대로 쓸 수 있습니다.
"""
from __future__ import annotations

import io

import numpy as np
import pandas as pd

MESSAGE_TYPES = {"rule": "규칙 기반", "ai": "AI 생성"}
# 캠페인 대상은 만 19~29세. 공공데이터(5세 단위: 20~24세, 25~29세)와 비교하기 쉽도록 두 구간으로 나눠요.
AGE_GROUPS = ["19~24세", "25~29세"]
LAST_CHECKUP = ["1년 이내", "1~2년 전", "2년보다 더 오래전", "받아본 적 없어요"]
SKIP_REASONS = ["시간이 없어서", "건강하다고 생각해서", "결과가 걱정돼서", "비용이 부담돼서", "어디서 받는지 몰라서", "특별한 이유는 없어요"]
UNKNOWN_PERSONA = "미상"

# (열 이름, 형식, 설명, 필수 여부)
SCHEMA = [
    ("response_id", "문자", "익명 응답 ID (개인정보 넣지 않기)", False),
    ("week", "정수", "응답 주차 (1부터)", False),
    ("persona", "문자", "페르소나 (예: 바쁜 사회초년생)", False),
    ("age_group", "문자", " / ".join(AGE_GROUPS) + " (캠페인 대상: 만 19~29세)", True),
    ("last_checkup", "문자", "마지막 검진 시기 (" + " / ".join(LAST_CHECKUP) + ")", True),
    ("skip_reason", "문자", "검진을 미룬 주된 이유", True),
    ("sns_reaction", "숫자", "SNS 반응도 (1~5)", False),
    ("message_type", "문자", "rule(규칙 기반) 또는 ai(AI 생성)", True),
    ("message_text", "문자", "응답자에게 보여준 메시지", False),
    ("intent_pre", "숫자", "사전 참여 의향 (1~5)", True),
    ("intent_post", "숫자", "사후 참여 의향 (1~5)", True),
    ("participated", "TRUE/FALSE", "실제 캠페인 참여(꽃 수령) 여부", True),
]
REQUIRED = [name for name, _, _, required in SCHEMA if required]

_PERSONAS = {
    "19~24세": ["건강 자신 있는 대학생", "바쁜 취업 준비생"],
    "25~29세": ["바쁜 사회초년생", "이직·자격증을 준비하는 청년"],
}
_RULE_MESSAGES = [
    "올해 건강검진 대상이에요. 검진 받고 데이지 받아가세요.",
    "건강검진 받고 설문에 참여하면 데이지를 드려요.",
]
_AI_MESSAGES = [
    "바쁜 하루 중 잠깐, 나를 위한 검진 어때요? 다녀오면 데이지가 기다려요.",
    "결과가 걱정될 땐 확인부터 — 작은 용기에 꽃 한 송이를 드려요.",
    "가족을 챙기던 마음, 오늘은 나에게도. 검진 후 데이지를 받아가세요.",
]


def make_mock_responses(n: int = 320, seed: int = 2026) -> pd.DataFrame:
    """화면 시연용 가상 응답. 메시지 효과는 일부러 작고 엇갈리게 설정 — 어떤 결론도 뒷받침하지 않아요."""
    rng = np.random.default_rng(seed)
    age = rng.choice(AGE_GROUPS, size=n, p=[0.5, 0.5])
    message = rng.choice(["rule", "ai"], size=n)
    week = rng.integers(1, 9, size=n)

    age_shift = np.array([{"19~24세": -0.2, "25~29세": 0.1}[a] for a in age])
    ai_shift = np.array([{"19~24세": 0.25, "25~29세": 0.05}[a] for a in age])
    effect = np.where(message == "ai", ai_shift, 0.0)

    pre = np.clip(np.rint(rng.normal(3.0 + age_shift, 0.95)), 1, 5)
    post = np.clip(np.rint(pre + 0.35 + effect + 0.03 * week + rng.normal(0, 0.8, n)), 1, 5)
    participated = rng.random(n) < 1 / (1 + np.exp(-(-0.9 + 0.55 * (post - 3) + 0.3 * effect)))
    sns = np.clip(np.rint(rng.normal(2.8 + 0.2 * (pre - 3), 1.1)), 1, 5)

    last_p = {"19~24세": [.20, .20, .20, .40], "25~29세": [.30, .25, .20, .25]}
    reason_p = {
        "19~24세": [.22, .30, .10, .10, .12, .16],
        "25~29세": [.38, .14, .12, .12, .10, .14],
    }
    persona = [rng.choice(_PERSONAS[a]) for a in age]
    last = [rng.choice(LAST_CHECKUP, p=last_p[a]) for a in age]
    reason = [rng.choice(SKIP_REASONS, p=reason_p[a]) for a in age]
    text = [rng.choice(_RULE_MESSAGES) if m == "rule" else rng.choice(_AI_MESSAGES) for m in message]

    return pd.DataFrame(
        {
            "response_id": [f"M{i:04d}" for i in range(1, n + 1)],
            "week": week,
            "persona": persona,
            "age_group": age,
            "last_checkup": last,
            "skip_reason": reason,
            "sns_reaction": sns.astype(int),
            "message_type": message,
            "message_text": text,
            "intent_pre": pre.astype(int),
            "intent_post": post.astype(int),
            "participated": participated,
        }
    )


def template_csv() -> bytes:
    """빈 양식(열 이름 + 예시 1줄). 엑셀에서 한글이 깨지지 않도록 BOM 을 붙여요."""
    example = ["R0001", 1, "바쁜 사회초년생", "25~29세",LAST_CHECKUP[1], SKIP_REASONS[0], 3, "ai", "예시 메시지", 3, 4, "TRUE"]
    frame = pd.DataFrame([example], columns=[name for name, *_ in SCHEMA])
    return frame.to_csv(index=False).encode("utf-8-sig")


def _to_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "y", "yes", "참여", "예"})


def load_uploaded_csv(raw: bytes) -> tuple[pd.DataFrame | None, list[str]]:
    """업로드한 CSV 를 검사하고 분석용 형태로 정리합니다. → (표, 문제 목록)"""
    problems: list[str] = []
    try:
        frame = pd.read_csv(io.BytesIO(raw), encoding="utf-8-sig")
    except Exception:
        return None, ["CSV 파일을 읽지 못했어요. UTF-8로 저장된 CSV인지 확인해주세요."]

    frame.columns = [str(c).strip() for c in frame.columns]
    missing = [c for c in REQUIRED if c not in frame.columns]
    if missing:
        return None, [f"필수 열이 없어요: {', '.join(missing)}"]

    frame = frame.copy()
    frame["message_type"] = (
        frame["message_type"].astype(str).str.strip().str.lower().replace({"규칙 기반": "rule", "규칙기반": "rule", "ai 생성": "ai", "ai생성": "ai"})
    )
    bad_type = ~frame["message_type"].isin(MESSAGE_TYPES)
    if bad_type.any():
        problems.append(f"message_type 이 rule/ai 가 아닌 {int(bad_type.sum())}행은 제외했어요.")
        frame = frame[~bad_type]
    for col in ("intent_pre", "intent_post"):
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    frame["participated"] = _to_bool(frame["participated"])
    frame = frame.dropna(subset=["intent_pre", "intent_post"])
    bad_age = ~frame["age_group"].isin(AGE_GROUPS)
    if bad_age.any():
        problems.append(f"age_group 이 {' / '.join(AGE_GROUPS)} 가 아닌 {int(bad_age.sum())}행은 제외했어요. (캠페인 대상은 만 19~29세예요)")
        frame = frame[~bad_age]

    for col, default in (("persona", UNKNOWN_PERSONA), ("week", 1), ("sns_reaction", np.nan), ("message_text", ""), ("response_id", "")):
        if col not in frame.columns:
            frame[col] = default
    frame["persona"] = frame["persona"].fillna(UNKNOWN_PERSONA).astype(str)
    frame["week"] = pd.to_numeric(frame["week"], errors="coerce").fillna(1).astype(int)
    if frame.empty:
        return None, problems + ["분석할 수 있는 행이 없어요. 연령대·의향 점수 값을 확인해주세요."]
    return frame.reset_index(drop=True), problems


# ── 집계 (차트마다 표 보기와 같은 표를 씁니다) ─────────────
def _label(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame["메시지 유형"] = frame["message_type"].map(MESSAGE_TYPES)
    return frame


def kpis(frame: pd.DataFrame) -> dict:
    return {
        "n": len(frame),
        "pre": frame["intent_pre"].mean(),
        "post": frame["intent_post"].mean(),
        "rate": frame["participated"].mean() * 100,
        "rate_by_type": (frame.groupby("message_type")["participated"].mean() * 100).to_dict(),
    }


def by_age_and_message(frame: pd.DataFrame, metric: str) -> pd.DataFrame:
    """연령대 × 메시지 유형별 평균 사후 의향(metric='intent_post') 또는 실제 참여율(%)(metric='participated')."""
    scale = 100 if metric == "participated" else 1
    grouped = _label(frame).groupby(["age_group", "메시지 유형"], observed=True)[metric].agg(["mean", "size"]).reset_index()
    grouped["값"] = grouped["mean"] * scale
    grouped["응답 수"] = grouped["size"]
    grouped["연령대"] = pd.Categorical(grouped["age_group"], AGE_GROUPS, ordered=True)
    return grouped.sort_values(["연령대", "메시지 유형"])[["연령대", "메시지 유형", "값", "응답 수"]].reset_index(drop=True)


def pre_post(frame: pd.DataFrame) -> pd.DataFrame:
    grouped = _label(frame).groupby(["message_type", "메시지 유형"], observed=True).agg(사전=("intent_pre", "mean"), 사후=("intent_post", "mean"), **{"응답 수": ("intent_pre", "size")}).reset_index()
    grouped["변화"] = grouped["사후"] - grouped["사전"]
    return grouped


def weekly(frame: pd.DataFrame) -> pd.DataFrame:
    grouped = _label(frame).groupby(["week", "message_type", "메시지 유형"], observed=True).agg(평균_사후_의향=("intent_post", "mean"), **{"응답 수": ("intent_post", "size")}).reset_index()
    return grouped.sort_values(["week", "message_type"]).rename(columns={"week": "주차", "평균_사후_의향": "평균 사후 의향"})


def reason_share(frame: pd.DataFrame) -> pd.DataFrame:
    counts = frame["skip_reason"].value_counts().rename_axis("이유").reset_index(name="응답 수")
    counts["비율(%)"] = counts["응답 수"] / counts["응답 수"].sum() * 100
    return counts


def last_checkup_share(frame: pd.DataFrame) -> pd.DataFrame:
    counts = frame["last_checkup"].value_counts().reindex(LAST_CHECKUP, fill_value=0).rename_axis("마지막 검진").reset_index(name="응답 수")
    counts["비율(%)"] = counts["응답 수"] / max(counts["응답 수"].sum(), 1) * 100
    return counts
