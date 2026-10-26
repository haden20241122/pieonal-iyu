"""사용자의 캠페인 진행 상태 (st.session_state).

  사전 설문 → 건강검진 → 사후 설문 → 꽃 받기   (4단계)

개인의 건강정보는 저장하지 않습니다. 여기에는 '어느 단계까지 했는지'만 있어요.
브라우저를 새로고침하면 세션이 초기화되므로, 이미 발급한 QR 은 인증번호로 다시 불러올 수 있게 했습니다.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Literal

import streamlit as st

from utils import voucher_store

StepStatus = Literal["done", "current", "locked"]

_DEFAULTS = {
    "pre_done": False,
    "checkup_done": False,  # '건강검진을 받았어요' 자가 확인
    "post_done": False,
    "pre_answers": None,  # 샘플 설문 응답 (세션에만 보관, 저장하지 않음)
    "post_answers": None,
    "survey_open": None,  # 앱 안 샘플 설문을 펼친 상태: 'pre' | 'post' | None
    "voucher_code": None,
}


def init_state() -> None:
    for key, value in _DEFAULTS.items():
        st.session_state.setdefault(key, copy.deepcopy(value))


def reset_progress() -> None:
    """처음부터 다시 체험 (데모용)."""
    for key, value in _DEFAULTS.items():
        st.session_state[key] = copy.deepcopy(value)


@dataclass(frozen=True)
class Progress:
    pre: bool
    checkup: bool
    post: bool
    voucher: voucher_store.Voucher | None

    @property
    def flower_received(self) -> bool:
        return bool(self.voucher and self.voucher.is_used)

    @property
    def surveys_done(self) -> bool:
        return self.pre and self.post

    def flags(self) -> list[bool]:
        return [self.pre, self.checkup, self.post, self.flower_received]

    def statuses(self) -> list[StepStatus]:
        """단계별 상태 — 완료된 것은 done, 처음 미완료 단계는 current, 나머지는 locked."""
        result: list[StepStatus] = []
        current_found = False
        for done in self.flags():
            if done:
                result.append("done")
            elif not current_found:
                result.append("current")
                current_found = True
            else:
                result.append("locked")
        return result

    @property
    def done_count(self) -> int:
        return sum(self.flags())


def get_progress() -> Progress:
    code = st.session_state.get("voucher_code")
    voucher = voucher_store.get(code) if code else None
    return Progress(
        pre=bool(st.session_state.get("pre_done")),
        checkup=bool(st.session_state.get("checkup_done")),
        post=bool(st.session_state.get("post_done")),
        voucher=voucher,
    )


def restore_from_voucher(voucher: voucher_store.Voucher) -> None:
    """인증번호로 진행 상태 복원 (새로고침 후 이어하기)."""
    st.session_state.update(
        pre_done=voucher.pre_done,
        checkup_done=True,
        post_done=voucher.post_done,
        voucher_code=voucher.code,
        survey_open=None,
    )
