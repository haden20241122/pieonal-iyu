"""분석 대시보드 (운영·분석용) — 규칙 기반 vs AI 생성 메시지 비교, 사전/사후 변화, 이유·검진 시기 분포.

지금은 '가상 데이터'로 화면 구조만 보여줍니다. 실제 응답 CSV 를 올리면 같은 화면이 실제 데이터로 바뀌어요.
필터·지표 선택은 차트 위 한 줄에 두고, 아래 모든 숫자·차트가 같은 조건으로 함께 바뀝니다.
"""
import streamlit as st

from components import charts, layout
from utils import analytics as A

layout.page_header(
    "ANALYTICS",
    "캠페인 효과 분석",
    "규칙 기반 메시지와 AI 생성 메시지의 반응을 비교하고, 사전·사후 변화를 살펴봐요.",
    icon="📊",
)

PLOT_CONFIG = {"displayModeBar": False}


@st.cache_data(show_spinner=False)
def _mock():
    return A.make_mock_responses()


# ── 데이터 연결 ──────────────────────────────────────────
data = _mock()
is_mock = True
with st.expander("데이터 연결 — 실제 응답 CSV 올리기 · 양식 내려받기"):
    st.caption("열 구성은 아래 ‘데이터 구조’와 같아야 해요. 개인정보(이름·연락처 등)는 넣지 마세요. 올린 파일은 저장되지 않고 이 화면에서만 쓰여요.")
    st.download_button("CSV 양식 내려받기", A.template_csv(), file_name="pieonal_responses_template.csv", mime="text/csv")
    uploaded = st.file_uploader("응답 CSV 올리기", type="csv")
    if uploaded is not None:
        parsed, problems = A.load_uploaded_csv(uploaded.getvalue())
        for problem in problems:
            st.warning(problem)
        if parsed is not None:
            data, is_mock = parsed, False
            st.success(f"{len(parsed)}건을 불러왔어요.")

if is_mock:
    layout.notice(
        "지금 보이는 숫자는 <b>화면 구성을 보여주기 위한 가상(mock) 데이터</b>예요. 실제 캠페인 결과가 아니며, "
        "어떤 메시지가 더 낫다는 결론을 뒷받침하지 않아요.",
        kind="warn",
        icon="🧪",
    )

# ── 필터 (한 줄, 아래 전체에 적용) ─────────────────────────
filter_age, filter_persona, filter_metric = st.columns([1, 1, 1])
ages = filter_age.multiselect("연령대", A.AGE_GROUPS, default=A.AGE_GROUPS)
persona_options = sorted(data["persona"].unique())
personas = filter_persona.multiselect("페르소나", persona_options, default=persona_options)
metric_label = filter_metric.segmented_control(
    "메시지 비교 지표 (첫 번째 차트)", ["평균 참여 의향(사후)", "실제 참여율"], default="평균 참여 의향(사후)", key="dash_metric"
) or "평균 참여 의향(사후)"
metric = "participated" if metric_label == "실제 참여율" else "intent_post"

view = data[data["age_group"].isin(ages) & data["persona"].isin(personas)]


def _delta(value: float, unit: str, label: str) -> str:
    """증감 표시: 색과 함께 ▲/▼ 기호와 설명 글자를 항상 같이 보여줘요."""
    arrow, klass = ("▲", "up") if value >= 0 else ("▼", "down")
    return f'<div class="pr-stat__delta"><b class="{klass}">{arrow} {abs(value):.2f}{unit}</b> {label}</div>'


def _table_view(table) -> None:
    """모든 차트에 붙는 '표 보기' — 툴팁이나 색을 못 보는 경우에도 값을 확인할 수 있어요."""
    with st.expander("표로 보기"):
        st.dataframe(table, hide_index=True, width="stretch")


def _chart_head(title: str, subtitle: str) -> None:
    st.html(f'<div class="pr-chart__title">{title}</div><div class="pr-chart__sub">{subtitle}</div>')


if view.empty:
    st.info("선택한 조건에 맞는 응답이 없어요. 필터를 넓혀보세요.")
else:
    # ── 핵심 숫자 ────────────────────────────────────────
    summary = A.kpis(view)
    rule_rate = summary["rate_by_type"].get("rule")
    ai_rate = summary["rate_by_type"].get("ai")
    if rule_rate is not None and ai_rate is not None:
        gap_html = _delta(ai_rate - rule_rate, "%p", "AI 생성 − 규칙 기반")
    else:
        gap_html = '<div class="pr-stat__delta">두 메시지 유형이 모두 있어야 비교할 수 있어요</div>'
    st.html(
        f"""
        <div class="pr-stats">
          <div class="pr-stat"><div class="pr-stat__label">응답 수</div><div class="pr-stat__value">{summary["n"]:,}</div>
            <div class="pr-stat__delta">선택한 조건 기준</div></div>
          <div class="pr-stat"><div class="pr-stat__label">평균 참여 의향 (사후, 5점 만점)</div><div class="pr-stat__value">{summary["post"]:.2f}</div>
            {_delta(summary["post"] - summary["pre"], "점", "사전 대비")}</div>
          <div class="pr-stat"><div class="pr-stat__label">실제 캠페인 참여율</div><div class="pr-stat__value">{summary["rate"]:.1f}%</div>
            {gap_html}</div>
        </div>
        """
    )

    # ── 1행: 메시지 비교 · 사전/사후 변화 ─────────────────────
    left, right = st.columns(2)
    with left, st.container(key="card-chart-compare"):
        _chart_head("메시지 유형별 반응 비교", "연령대별로 규칙 기반과 AI 생성 메시지를 나란히 봐요.")
        compare = A.by_age_and_message(view, metric)
        st.plotly_chart(charts.message_compare_bar(compare, metric), width="stretch", theme=None, config=PLOT_CONFIG, key="chart_compare")
        _table_view(compare.rename(columns={"값": "참여율(%)" if metric == "participated" else "평균 의향(점)"}))
    with right, st.container(key="card-chart-prepost"):
        _chart_head("사전 → 사후 변화", "빈 원은 사전, 채운 원은 사후 평균 의향이에요. 오른쪽 숫자는 변화량이에요.")
        prepost = A.pre_post(view)
        st.plotly_chart(charts.pre_post_dumbbell(prepost), width="stretch", theme=None, config=PLOT_CONFIG, key="chart_prepost")
        _table_view(prepost.drop(columns=["message_type"]))

    # ── 2행: 주차별 추이 ─────────────────────────────────────
    with st.container(key="card-chart-weekly"):
        _chart_head("주차별 평균 참여 의향 (사후)", "응답이 들어온 주차별 흐름이에요. 주차마다 응답 수가 적을 수 있어 참고용으로 봐주세요.")
        weekly = A.weekly(view)
        st.plotly_chart(charts.weekly_line(weekly), width="stretch", theme=None, config=PLOT_CONFIG, key="chart_weekly")
        _table_view(weekly.drop(columns=["message_type"]))

    # ── 3행: 미검진 이유 · 마지막 검진 시기 ───────────────────
    left, right = st.columns(2)
    with left, st.container(key="card-chart-reason"):
        _chart_head("건강검진을 미룬 이유", "응답자가 고른 주된 이유의 비율이에요.")
        reasons = A.reason_share(view)
        st.plotly_chart(charts.reason_donut(reasons), width="stretch", theme=None, config=PLOT_CONFIG, key="chart_reason")
        _table_view(reasons)
    with right, st.container(key="card-chart-last"):
        _chart_head("마지막 검진 시기", "색이 진할수록 검진을 받은 지 오래된 응답이에요.")
        last = A.last_checkup_share(view)
        st.plotly_chart(charts.last_checkup_bar(last), width="stretch", theme=None, config=PLOT_CONFIG, key="chart_last")
        _table_view(last)

# ── 데이터 구조 안내 (앞으로 어떤 데이터가 들어오는지) ─────────
layout.section_title("데이터 구조", "이 열 구성으로 응답을 모으면 위 차트가 그대로 실제 데이터로 채워져요.")
with st.expander("열 설명 보기"):
    st.dataframe(
        [{"열 이름": n, "형식": t, "설명": d, "필수": "✓" if r else ""} for n, t, d, r in A.SCHEMA],
        hide_index=True,
        width="stretch",
    )
    st.caption("확장 아이디어: 메시지 문구별 비교(message_text), SNS 반응도(sns_reaction)와 참여 여부의 관계, 페르소나별 메시지 반응 등을 같은 방식으로 추가할 수 있어요.")
