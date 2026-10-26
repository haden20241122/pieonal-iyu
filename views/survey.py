"""사전·사후 설문조사 + 꽃 수령 인증 QR 발급.

  ① 사전 설문 → ② 건강검진 → ③ 사후 설문 → ④ 꽃 받기
사전·사후 설문을 모두 마친 경우에만 QR 발급이 열립니다. 설문 URL(.env)이 비어 있으면 앱 안의 샘플 설문(mock)이 열려요.
"""
import streamlit as st

from components import layout
from components.stepper import render_stepper
from components.survey_form import render_survey_form
from config import campaign as C
from config import pages as P
from config import settings
from data.survey_questions import POST_QUESTIONS, PRE_QUESTIONS
from utils import qr, state, voucher_store

layout.page_header(
    "SURVEY",
    "사전·사후 설문조사",
    "설문 두 번과 건강검진 한 번이면 데이지를 받을 준비가 끝나요.",
    icon="📝",
)

progress = state.get_progress()
statuses = progress.statuses()
render_stepper(progress)
st.write("")


def _step_head(number: int, title: str, status: str) -> None:
    chip = {"done": layout.badge("완료", "ok"), "current": layout.badge("진행 중", "info"), "locked": layout.badge("잠김", "draft")}[status]
    st.html(
        f'<div class="pr-stephead"><span class="pr-stephead__num">{number}</span>'
        f'<h3 class="pr-stephead__title">{title}</h3>{chip}</div>'
    )


def _survey_block(kind: str, intro: tuple[str, str], url: str, questions: list[dict], status: str) -> None:
    """사전/사후 설문 카드의 공통 본문. kind: 'pre' | 'post'"""
    done_key = f"{kind}_done"
    label = "사전" if kind == "pre" else "사후"
    st.html(f'<p class="pr-quote">{layout.h(intro[0])}<br>{layout.h(intro[1])}</p><p class="pr-time">⏱ {C.SURVEY_TIME_TEXT}</p>')

    if status == "done":
        st.success(f"{label} 설문을 완료했어요. 고마워요! 🌱")
        return

    locked = status == "locked"
    if url:  # 실제 Google Forms 등 외부 설문
        st.link_button(f"{label} 설문 시작하기", url, type="primary", disabled=locked)
        st.caption("설문을 제출한 뒤 이 페이지로 돌아와 아래 버튼을 눌러주세요.")
        if st.button("설문을 마쳤어요 (완료 처리)", key=f"{kind}_confirm", disabled=locked):
            st.session_state[done_key] = True
            st.rerun()
        return

    # 앱 안 샘플 설문 (mock)
    if st.button(f"{label} 설문 시작하기", type="primary", key=f"{kind}_start", disabled=locked):
        st.session_state.survey_open = kind
    if st.session_state.get("survey_open") == kind and not locked:
        st.caption("🧪 샘플 설문이에요. 실제 문항은 Google Forms로 교체할 수 있어요. 응답은 저장되지 않아요.")
        answers = render_survey_form(f"{kind}_form", questions)
        if answers is not None:
            st.session_state[f"{kind}_answers"] = answers
            st.session_state[done_key] = True
            st.session_state.survey_open = None
            st.rerun()


# ── ① 사전 설문 ──────────────────────────────────────────
with st.container(key=f"card-pre-{statuses[0]}"):
    _step_head(1, "사전 설문", statuses[0])
    _survey_block("pre", C.SURVEY_PRE_INTRO, settings.SURVEY_PRE_URL, PRE_QUESTIONS, statuses[0])

st.write("")

# ── ② 건강검진 ───────────────────────────────────────────
with st.container(key=f"card-checkup-{statuses[1]}"):
    _step_head(2, "건강검진 받기", statuses[1])
    st.html('<p class="pr-quote">가까운 검진기관에서 건강검진을 받아보세요.<br>검진을 마쳤다면 아래 버튼으로 알려주세요.</p>')
    if statuses[1] == "done":
        st.success("건강검진을 받았어요. 수고했어요! 🩺")
        st.link_button("내 건강검진 결과 확인하기 →", C.NHIS_RESULT_URL)
    else:
        st.page_link(P.HEALTH, label="🔎 가까운 검진기관 찾아보기")
        if st.button("건강검진을 받았어요", type="primary", key="checkup_confirm", disabled=statuses[1] == "locked"):
            st.session_state.checkup_done = True
            st.rerun()
        if statuses[1] == "locked":
            st.caption("사전 설문을 마치면 열려요.")

st.write("")

# ── ③ 사후 설문 ──────────────────────────────────────────
with st.container(key=f"card-post-{statuses[2]}"):
    _step_head(3, "사후 설문", statuses[2])
    _survey_block("post", C.SURVEY_POST_INTRO, settings.SURVEY_POST_URL, POST_QUESTIONS, statuses[2])
    if statuses[2] == "locked":
        st.caption("건강검진을 받았다고 알려주면 열려요.")

st.write("")

# ── ④ 꽃 수령 인증 QR ────────────────────────────────────
with st.container(key=f"card-qr-{statuses[3]}"):
    _step_head(4, "꽃 수령 인증 QR", statuses[3])
    voucher = progress.voucher

    if not progress.surveys_done:
        st.html('<p class="pr-quote">사전·사후 설문을 모두 마치면<br>꽃 수령 인증 QR을 발급받을 수 있어요.</p>')
        st.button("꽃 수령 인증 QR 발급하기", key="qr_issue_locked", disabled=True)

    elif voucher is None or (voucher.is_expired):
        if voucher is not None:
            st.warning("QR 유효기간이 지났어요. 설문은 이미 완료했으니 새 QR을 발급받을 수 있어요.")
        else:
            st.html(
                f'<div class="pr-celebrate">🎉 캠페인 참여가 완료되었습니다!</div>'
                f'<p class="pr-quote">이제 가까운 서울시 인증 꽃집에서<br>{C.FLOWER_NAME}를 받아가세요.</p>'
            )
        if st.button("꽃 수령 인증 QR 발급하기", type="primary", key="qr_issue"):
            new_voucher = voucher_store.issue(progress.pre, progress.post)
            st.session_state.voucher_code = new_voucher.code
            st.rerun()

    elif voucher.is_used:
        st.html(
            f'<div class="pr-celebrate">🌼 꽃 수령이 완료되었어요!</div>'
            f'<p class="pr-quote">이 QR은 이미 사용됐어요. (인증번호 <span class="pr-code" style="font-size:1rem">{layout.h(voucher.code)}</span>)</p>'
            f'<p class="pr-time">수령 시각 {voucher_store.fmt_kst(voucher.used_at)} · {layout.h(voucher.used_shop or "꽃집 정보 없음")}</p>'
        )
        st.page_link(P.SNS, label="📣 SNS에 피어날 이유 공유하러 가기")

    else:  # 발급됨 · 사용 전 · 유효
        st.html(
            f'<div class="pr-celebrate">🎉 QR이 발급되었어요!</div>'
            f'<p class="pr-quote">꽃집에서 이 QR을 보여주면 {C.FLOWER_NAME}를 받을 수 있어요.</p>'
        )
        with st.container(key="qr-card"):
            st.image(qr.make_qr_png(qr.qr_payload(voucher.code)), width=230)
            st.html(f'<div class="pr-code">{layout.h(voucher.code)}</div>')
            st.html(
                f'<p class="pr-time" style="margin-top:.6rem">1회만 사용할 수 있어요 · 유효기간 {voucher_store.fmt_kst(voucher.expires_at)}까지</p>'
            )
        st.page_link(P.FLOWER_SHOPS, label="💐 가까운 인증 꽃집 찾기")

st.write("")

# ── 이어하기 / 데모 도우미 ────────────────────────────────
with st.expander("이미 QR을 발급받았나요? 인증번호로 이어하기"):
    st.caption("브라우저를 새로고침하면 진행 상태가 사라져요. 발급받은 인증번호를 넣으면 QR 화면을 다시 불러올 수 있어요.")
    with st.form("restore-form", border=False):
        raw = st.text_input("인증번호", placeholder=qr.CODE_EXAMPLE, key="restore_code")
        if st.form_submit_button("불러오기"):
            code = qr.extract_code(raw)
            found = voucher_store.get(code) if code else None
            if found is None:
                st.warning("인증번호를 찾지 못했어요. 다시 확인해주세요.")
            else:
                state.restore_from_voucher(found)
                st.rerun()

if settings.DEMO_MODE:
    with st.expander("🧪 프로토타입 도우미 (데모 모드에서만 보여요)"):
        st.caption("발표·테스트용 버튼이에요. 실제 운영에서는 DEMO_MODE=false 로 숨겨집니다.")
        c1, c2 = st.columns(2)
        if c1.button("⏩ 설문·검진 모두 완료 처리", key="demo_fill", use_container_width=True):
            st.session_state.update(pre_done=True, checkup_done=True, post_done=True)
            st.rerun()
        if c2.button("↩️ 처음부터 다시 체험", key="demo_reset", use_container_width=True):
            state.reset_progress()
            st.rerun()
