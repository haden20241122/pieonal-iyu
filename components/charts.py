"""분석 대시보드용 차트 (Plotly). 데이터 → Figure 만 만들고, 화면 배치는 views/dashboard.py 가 맡습니다.

색 규칙 (스킬 'dataviz' 의 검증된 팔레트를 그대로 사용, 흰 카드 위에서 검증 완료)
  · 같은 대상은 어느 차트에서나 같은 색  →  규칙 기반 = 파랑, AI 생성 = 주황
  · 도넛(미검진 이유 6개)은 슬롯 3~8 색 (조각마다 % 라벨 + 표 보기를 함께 제공 — 3:1 미만 색의 보완 장치)
  · 순서가 있는 값(마지막 검진 시기)은 파랑 한 가지 색의 밝기 단계
  · 글자에는 데이터 색을 쓰지 않음 (글자는 항상 잉크색)
  · 이중 축 없음, 막대는 얇게, 격자는 흐린 실선, 모든 차트에 '표 보기' 제공
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from utils.analytics import LAST_CHECKUP, MESSAGE_TYPES, SKIP_REASONS

TYPES_IN_ORDER = list(MESSAGE_TYPES.values())  # ['규칙 기반', 'AI 생성']

SURFACE = "#FFFFFF"
INK = "#22332C"
INK_SECOND = "#52514E"
GRID = "#ECEAE2"
AXIS = "#C3C2B7"
FONT = '"Noto Sans KR", "Malgun Gothic", "Apple SD Gothic Neo", sans-serif'

# 메시지 유형 → 색 (카테고리 슬롯 1·2)
TYPE_COLOR = {"규칙 기반": "#2A78D6", "AI 생성": "#EB6834"}
# 미검진 이유 → 색 (카테고리 슬롯 3~8, 고정 순서)
REASON_COLOR = dict(zip(SKIP_REASONS, ["#1BAF7A", "#EDA100", "#E87BA4", "#008300", "#4A3AA7", "#E34948"]))
# 마지막 검진 시기 → 파랑 밝기 단계 (밝음 = 최근, 어두움 = 오래됨)
ORDINAL_BLUE = dict(zip(LAST_CHECKUP, ["#86B6EF", "#5598E7", "#2A78D6", "#1C5CAB"]))


def _frame(fig: go.Figure, height: int = 340, legend: bool = True) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=4, r=8, t=8 if not legend else 44, b=8),
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(family=FONT, size=13, color=INK_SECOND),
        hoverlabel=dict(bgcolor="white", bordercolor=AXIS, font=dict(family=FONT, size=13, color=INK)),
        showlegend=legend,
        legend=dict(orientation="h", x=0, y=1.0, yanchor="bottom", font=dict(size=13, color=INK_SECOND)),
        dragmode=False,  # 손가락으로 페이지를 스크롤할 때 차트가 끌려 다니지 않게
    )
    # automargin: 눈금 글자가 잘리지 않게 여백을 자동으로 늘려요 (x축 밴드까지 높이에 포함)
    tick_font = dict(size=12, color=INK_SECOND)
    fig.update_xaxes(showgrid=False, linecolor=AXIS, linewidth=1, ticks="", fixedrange=True, automargin=True, tickfont=tick_font)
    fig.update_yaxes(gridcolor=GRID, gridwidth=1, zeroline=False, ticks="", fixedrange=True, linecolor="rgba(0,0,0,0)", automargin=True, tickfont=tick_font)
    return fig


def message_compare_bar(table: pd.DataFrame, metric: str) -> go.Figure:
    """연령대별 · 메시지 유형별 막대 (막대는 0 에서 시작)."""
    percent = metric == "participated"
    fig = go.Figure()
    for message_type, color in TYPE_COLOR.items():
        part = table[table["메시지 유형"] == message_type]
        fig.add_bar(
            x=part["연령대"].astype(str),
            y=part["값"],
            name=message_type,
            marker=dict(color=color, cornerradius=4),
            customdata=part[["응답 수"]],
            hovertemplate=("<b>%{y:.1f}%</b>" if percent else "<b>%{y:.2f}점</b>")
            + " · %{fullData.name}<br>%{x} · 응답 %{customdata[0]}건<extra></extra>",
        )
    fig.update_layout(barmode="group", bargap=0.6, bargroupgap=0.1, hovermode="closest")
    _frame(fig)
    if percent:
        fig.update_yaxes(range=[0, 100], ticksuffix="%", tick0=0, dtick=25)
    else:
        fig.update_yaxes(range=[0, 5], dtick=1)
    return fig


def pre_post_dumbbell(table: pd.DataFrame) -> go.Figure:
    """메시지 유형별 사전 → 사후 평균 의향. 빈 원 = 사전, 채운 원 = 사후 (색은 메시지 유형 색 그대로)."""
    fig = go.Figure()
    for _, row in table.iterrows():
        color = TYPE_COLOR[row["메시지 유형"]]
        label = row["메시지 유형"]
        fig.add_trace(go.Scatter(x=[row["사전"], row["사후"]], y=[label, label], mode="lines", line=dict(color=AXIS, width=2), hoverinfo="skip", showlegend=False))
        fig.add_trace(
            go.Scatter(
                x=[row["사전"]], y=[label], mode="markers", showlegend=False,
                marker=dict(size=14, color=SURFACE, line=dict(color=color, width=3)),
                hovertemplate="사전 <b>%{x:.2f}점</b> · " + label + "<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[row["사후"]], y=[label], mode="markers+text", showlegend=False,
                marker=dict(size=14, color=color, line=dict(color=SURFACE, width=2)),
                text=[f"{row['변화']:+.2f}"], textposition="middle right", textfont=dict(color=INK, size=14),
                hovertemplate="사후 <b>%{x:.2f}점</b> · " + label + "<extra></extra>",
            )
        )
    # 범례용 (회색): 사전=빈 원, 사후=채운 원
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name="사전", marker=dict(size=12, color=SURFACE, line=dict(color=INK_SECOND, width=3))))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name="사후", marker=dict(size=12, color=INK_SECOND, line=dict(color=SURFACE, width=2))))
    _frame(fig)
    fig.update_xaxes(range=[1, 5.4], dtick=1, showgrid=True, gridcolor=GRID, linecolor="rgba(0,0,0,0)")
    # 위에서부터 '규칙 기반 → AI 생성' 순서 (다른 차트의 범례 순서와 같게)
    # range 를 좁혀 두 줄이 위아래 끝으로 벌어지지 않게 모아줘요.
    fig.update_yaxes(showgrid=False, categoryorder="array", categoryarray=TYPES_IN_ORDER, range=[1.8, -0.8], tickfont=dict(size=14, color=INK))
    return fig


def weekly_line(table: pd.DataFrame) -> go.Figure:
    """주차별 평균 사후 의향 추이 (선 2px, 끝점에 이름 표시)."""
    fig = go.Figure()
    ends = []
    for message_type, color in TYPE_COLOR.items():
        part = table[table["메시지 유형"] == message_type].sort_values("주차")
        if part.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=part["주차"], y=part["평균 사후 의향"], mode="lines+markers", name=message_type,
                line=dict(color=color, width=2),
                marker=dict(size=8, color=color, line=dict(color=SURFACE, width=2)),
                customdata=part[["응답 수"]],
                hovertemplate="<b>%{y:.2f}점</b> (응답 %{customdata[0]}건)<extra>" + message_type + "</extra>",
            )
        )
        ends.append((message_type, part.iloc[-1]["주차"], part.iloc[-1]["평균 사후 의향"]))
    # 끝점 라벨이 겹치면 위/아래로 살짝 벌림 (선에서 너무 멀어지지 않게 ±10px)
    ends.sort(key=lambda e: e[2])
    close = len(ends) == 2 and abs(ends[0][2] - ends[1][2]) < 0.25
    for index, (name, week, value) in enumerate(ends):
        shift = (10 if index == len(ends) - 1 else -10) if close else 0
        fig.add_annotation(x=week, y=value, text=name, showarrow=False, xanchor="left", xshift=10, yshift=shift, font=dict(color=INK, size=13))
    _frame(fig)
    weeks = sorted(table["주차"].unique())
    fig.update_layout(hovermode="x unified", margin=dict(l=4, r=64, t=44, b=8))
    fig.update_xaxes(tickvals=weeks, ticktext=[f"{w}주" for w in weeks])
    low, high = table["평균 사후 의향"].min(), table["평균 사후 의향"].max()
    fig.update_yaxes(range=[max(1, low - 0.3), min(5, high + 0.3)], tickformat=".1f")
    return fig


def reason_donut(table: pd.DataFrame) -> go.Figure:
    """미검진 이유 비율 (도넛, 6조각 이하). 조각 사이 2px 간격 + 조각마다 % 라벨."""
    fig = go.Figure(
        go.Pie(
            labels=table["이유"], values=table["응답 수"], hole=0.6, sort=False, direction="clockwise",
            marker=dict(colors=[REASON_COLOR.get(r, AXIS) for r in table["이유"]], line=dict(color=SURFACE, width=2)),
            textinfo="percent", textposition="outside", textfont=dict(color=INK, size=13), insidetextorientation="horizontal",
            automargin=True,  # 바깥 % 라벨이 좌우 끝에서 잘리지 않게
            hovertemplate="%{label}<br><b>%{value}건</b> (%{percent})<extra></extra>",
        )
    )
    _frame(fig, height=380)
    total = int(table["응답 수"].sum())
    fig.update_layout(
        margin=dict(l=8, r=8, t=16, b=8),
        legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.02, yanchor="top"),
        annotations=[dict(text=f"<b>{total}</b><br>응답", showarrow=False, font=dict(size=16, color=INK))],
    )
    return fig


def last_checkup_bar(table: pd.DataFrame) -> go.Figure:
    """마지막 검진 시기 분포 (순서가 있는 값 → 파랑 밝기 단계, 막대 위에 % 표시)."""
    fig = go.Figure(
        go.Bar(
            x=table["마지막 검진"], y=table["비율(%)"],
            marker=dict(color=[ORDINAL_BLUE[v] for v in table["마지막 검진"]], cornerradius=4),
            width=0.32, text=[f"{v:.0f}%" for v in table["비율(%)"]], textposition="outside", textfont=dict(color=INK, size=14),
            customdata=table[["응답 수"]], hovertemplate="%{x}<br><b>%{y:.1f}%</b> · 응답 %{customdata[0]}건<extra></extra>", cliponaxis=False,
        )
    )
    _frame(fig, height=380, legend=False)
    fig.update_layout(margin=dict(l=4, r=8, t=28, b=8))
    fig.update_yaxes(range=[0, max(table["비율(%)"].max() * 1.25, 10)], ticksuffix="%", showticklabels=False, showgrid=False)
    return fig
