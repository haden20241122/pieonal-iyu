"""꽃집 직원용 QR 인증 화면 (/shop).

    인증번호(또는 QR 주소) 입력 → 유효성 확인 → [꽃 전달 완료] → 같은 QR 재사용 불가
QR 발급 때 APP_BASE_URL 이 설정돼 있으면 QR 이 '주소/shop?code=…' 라서,
휴대폰 카메라로 스캔하면 이 화면이 열리면서 인증번호가 자동으로 확인됩니다.
"""
import streamlit as st

from components import layout
from config import settings
from utils import places as places_util
from utils import voucher_store as vs
from utils.qr import CODE_EXAMPLE


def _next_customer() -> None:
    """다음 참가자를 확인하기 위해 화면을 비웁니다. (콜백이라서 입력칸 값도 바꿀 수 있어요)"""
    st.session_state.shop_checked = None
    st.session_state.shop_just_redeemed = None
    st.session_state.shop_code_input = ""
    st.query_params.clear()


def _fill_code(code: str) -> None:
    st.session_state.shop_code_input = code
    st.session_state.shop_checked = code
    st.session_state.shop_just_redeemed = None


def _result_card(kind: str, title: str, body_html: str) -> None:
    st.html(f'<div class="pr-result pr-result--{kind}"><div class="pr-result__title">{title}</div>{body_html}</div>')


def _render_result(checked: str, shop_name: str) -> None:
    result = vs.verify(checked)
    voucher = result.voucher
    just = st.session_state.get("shop_just_redeemed")

    # 방금 이 화면에서 '꽃 전달 완료'를 누른 경우
    if just and voucher and voucher.code == just:
        st.html(
            f"""
            <div class="pr-result pr-result--ok pr-done">
              <div class="pr-done__icon" aria-hidden="true">🌼</div>
              <div class="pr-result__title">🌼 꽃 수령이 완료되었습니다!</div>
              <p>인증번호 <span class="pr-code" style="font-size:1rem">{layout.h(voucher.code)}</span> 는 이제 다시 사용할 수 없어요.</p>
            </div>
            """
        )
        st.button("다음 참가자 확인하기", type="primary", on_click=_next_customer, key="next_after_done")
        return

    if result.state == "valid" and voucher:
        _result_card(
            "ok",
            "✅ 인증 가능",
            """<ul class="pr-checklist">
                 <li><span class="ck">✓</span>사전 설문 완료</li>
                 <li><span class="ck">✓</span>사후 설문 완료</li>
                 <li><span class="ck">✓</span>QR 유효</li>
                 <li><span class="ck">✓</span>미사용</li>
               </ul>"""
            f'<div class="pr-meta">인증번호 {layout.h(voucher.code)} · 발급 {vs.fmt_kst(voucher.issued_at)} · 만료 {vs.fmt_kst(voucher.expires_at)}</div>',
        )
        if st.button("🌼 꽃 전달 완료", type="primary", key="redeem"):
            success, _ = vs.redeem(voucher.code, shop_name)
            if success:
                st.session_state.shop_just_redeemed = voucher.code
            else:
                st.warning("방금 다른 기기에서 먼저 처리된 QR이에요. 다시 확인해볼게요.")
            st.rerun()
        return

    if result.state == "used" and voucher:
        _result_card(
            "bad",
            "⛔ 이미 사용된 QR이에요",
            f'<p>꽃을 건네기 전에 확인해주세요. 이 QR은 다시 사용할 수 없어요.</p>'
            f'<div class="pr-meta">인증번호 {layout.h(voucher.code)} · 사용 {vs.fmt_kst(voucher.used_at)} · {layout.h(voucher.used_shop or "꽃집 정보 없음")}</div>',
        )
    elif result.state == "expired" and voucher:
        _result_card(
            "warn",
            "⏰ 유효기간이 지난 QR이에요",
            f'<p>참가자에게 설문 페이지에서 새 QR을 발급받도록 안내해주세요.</p>'
            f'<div class="pr-meta">인증번호 {layout.h(voucher.code)} · 만료 {vs.fmt_kst(voucher.expires_at)}</div>',
        )
    elif result.state == "not_found":
        _result_card("bad", "❓ 등록되지 않은 인증번호예요", "<p>입력한 번호를 다시 확인해주세요. 대소문자·하이픈(-)을 확인해보세요.</p>")
    else:  # bad_format
        _result_card("bad", "✍️ 인증번호 형식이 달라요", f"<p>인증번호는 <b>{CODE_EXAMPLE}</b> 처럼 생겼어요.</p>")
    st.button("다시 확인하기", on_click=_next_customer, key="retry")


def _pin_ok() -> bool:
    if not settings.SHOP_STAFF_PIN or st.session_state.get("shop_authed"):
        return True
    st.info("꽃집 직원 전용 화면이에요. 운영팀이 알려준 PIN을 입력해주세요.")
    with st.form("pin-form", border=False):
        pin = st.text_input("꽃집 직원 PIN", type="password")
        if st.form_submit_button("입장", type="primary"):
            if pin == settings.SHOP_STAFF_PIN:
                st.session_state.shop_authed = True
                st.rerun()
            st.error("PIN이 맞지 않아요.")
    return False


def main() -> None:
    layout.page_header("FOR FLOWER SHOPS", "꽃 수령 인증", "참가자의 QR을 확인해주세요.", icon="✅")
    if not _pin_ok():
        return

    ss = st.session_state
    ss.setdefault("shop_checked", None)
    ss.setdefault("shop_just_redeemed", None)
    ss.setdefault("shop_code_input", "")
    # QR 을 스캔해 '/shop?code=…' 로 들어온 경우 자동으로 확인
    param = st.query_params.get("code")
    if param and ss.get("shop_qp_seen") != param:
        ss.shop_qp_seen = param
        ss.shop_checked = param
        ss.shop_code_input = param

    shop_names = [p.name for p in places_util.load_places("flower")]
    if shop_names:
        shop_name = st.selectbox("우리 꽃집", shop_names, key="shop_name", help="샘플 꽃집 목록이에요. 실제 운영에서는 인증 꽃집 목록으로 바뀝니다.")
    else:
        shop_name = st.text_input("우리 꽃집 이름", key="shop_name_text")

    with st.form("verify-form", border=False):
        raw = st.text_input("인증번호 입력 (또는 QR 주소 붙여넣기)", key="shop_code_input", placeholder=CODE_EXAMPLE)
        submitted = st.form_submit_button("확인하기", type="primary")
    if submitted:
        ss.shop_checked = raw.strip() or None
        ss.shop_just_redeemed = None
        if not raw.strip():
            st.info("인증번호를 입력해주세요.")

    if ss.shop_checked:
        _render_result(ss.shop_checked, shop_name or "")

    if settings.DEMO_MODE:
        with st.expander("🧪 프로토타입 도우미 — 최근 발급된 QR"):
            st.caption("참가자 화면(설문·꽃 인증)에서 발급한 QR이 여기에 나타나요. 상태별 화면을 시험해볼 수 있어요.")
            vouchers = vs.recent(6)
            if not vouchers:
                st.info("아직 발급된 QR이 없어요. ‘설문·꽃 인증’ 페이지에서 먼저 발급해보세요.")
            for v in vouchers:
                status = "사용됨" if v.is_used else ("만료" if v.is_expired else "사용 전")
                code_col, status_col, action_col = st.columns([2.2, 1, 1.6], vertical_alignment="center")
                code_col.code(v.code, language=None)
                status_col.write(status)
                with action_col:
                    st.button("이 코드로 확인", key=f"fill-{v.code}", on_click=_fill_code, args=(v.code,))
                    if status == "사용 전" and st.button("만료 시켜보기", key=f"expire-{v.code}"):
                        vs.force_expire(v.code)
                        st.rerun()


main()
