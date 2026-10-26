"""꽃 수령 인증 QR 저장소 (SQLite · 프로토타입 수준).

왜 DB 파일이 필요한가요?
    참가자 휴대폰(세션 A)에서 발급한 QR 을 꽃집 직원 기기(세션 B)에서 확인해야 하는데,
    st.session_state 는 접속자마다 따로라 서로 볼 수 없습니다. 그래서 발급·사용 상태만 파일 DB 에 둡니다.

저장하는 것:  인증번호, 발급/만료/사용 시각, 사용한 꽃집 이름, 설문 완료 여부(두 개 모두 True 인 경우만 발급)
저장하지 않는 것: 이름·연락처·건강정보 등 개인정보 전부

한계(프로토타입):  Streamlit Cloud 는 재시작하면 파일이 초기화됩니다.
    실제 운영에서는 이 파일의 함수들(issue / verify / redeem …)을 유지한 채 Supabase·Firestore 등으로 바꾸세요.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterator, Literal

from config.settings import QR_VALID_HOURS, VOUCHER_DB_PATH
from utils.qr import extract_code, new_code

KST = timezone(timedelta(hours=9))  # 한국은 서머타임이 없어 고정 오프셋으로 충분
VerifyState = Literal["valid", "used", "expired", "not_found", "bad_format"]


class NotEligibleError(Exception):
    """사전·사후 설문을 모두 마치지 않았는데 QR 발급을 요청한 경우."""


@dataclass(frozen=True)
class Voucher:
    code: str
    issued_at: datetime
    expires_at: datetime
    status: str  # issued | used
    used_at: datetime | None
    used_shop: str
    pre_done: bool
    post_done: bool

    @property
    def is_used(self) -> bool:
        return self.status == "used"

    @property
    def is_expired(self) -> bool:
        return not self.is_used and _now() >= self.expires_at


@dataclass(frozen=True)
class VerifyResult:
    state: VerifyState
    voucher: Voucher | None = None


# ── 내부 도구 ─────────────────────────────────────────────
def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def _parse(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def fmt_kst(dt: datetime | None) -> str:
    return dt.astimezone(KST).strftime("%Y-%m-%d %H:%M") if dt else "-"


@contextmanager
def _db() -> Iterator[sqlite3.Connection]:
    VOUCHER_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(VOUCHER_DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute(
        """CREATE TABLE IF NOT EXISTS vouchers (
            code TEXT PRIMARY KEY,
            issued_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'issued',
            used_at TEXT,
            used_shop TEXT NOT NULL DEFAULT '',
            pre_done INTEGER NOT NULL,
            post_done INTEGER NOT NULL
        )"""
    )
    try:
        yield con
        con.commit()
    finally:
        con.close()


def _to_voucher(row: sqlite3.Row) -> Voucher:
    return Voucher(
        code=row["code"],
        issued_at=_parse(row["issued_at"]),
        expires_at=_parse(row["expires_at"]),
        status=row["status"],
        used_at=_parse(row["used_at"]),
        used_shop=row["used_shop"],
        pre_done=bool(row["pre_done"]),
        post_done=bool(row["post_done"]),
    )


# ── 공개 함수 ─────────────────────────────────────────────
def issue(pre_done: bool, post_done: bool, valid_hours: int = QR_VALID_HOURS) -> Voucher:
    """QR 발급. 사전·사후 설문을 모두 마친 경우에만 가능합니다."""
    if not (pre_done and post_done):
        raise NotEligibleError("사전·사후 설문을 모두 완료해야 QR 을 발급할 수 있어요.")
    now = _now()
    with _db() as con:
        for _ in range(10):  # 인증번호가 우연히 겹치면 다시 뽑기
            code = new_code()
            try:
                con.execute(
                    "INSERT INTO vouchers (code, issued_at, expires_at, pre_done, post_done) VALUES (?,?,?,?,?)",
                    (code, _iso(now), _iso(now + timedelta(hours=valid_hours)), 1, 1),
                )
                break
            except sqlite3.IntegrityError:
                continue
        else:
            raise RuntimeError("인증번호를 만들지 못했어요. 잠시 후 다시 시도해주세요.")
    return get(code)  # type: ignore[return-value]


def get(code: str) -> Voucher | None:
    with _db() as con:
        row = con.execute("SELECT * FROM vouchers WHERE code = ?", (code,)).fetchone()
    return _to_voucher(row) if row else None


def verify(raw_input: str) -> VerifyResult:
    """꽃집 직원이 입력한 값(인증번호 또는 QR 주소)을 확인합니다."""
    code = extract_code(raw_input)
    if code is None:
        return VerifyResult("bad_format")
    voucher = get(code)
    if voucher is None:
        return VerifyResult("not_found")
    if voucher.is_used:
        return VerifyResult("used", voucher)
    if voucher.is_expired:
        return VerifyResult("expired", voucher)
    return VerifyResult("valid", voucher)


def redeem(code: str, shop_name: str = "") -> tuple[bool, VerifyResult]:
    """'꽃 전달 완료' 처리 → (이번 호출로 처리됐는지, 처리 후 확인 결과).
    한 번만 성공합니다. 두 기기에서 동시에 눌러도 먼저 도착한 한쪽만 True 예요."""
    now = _iso(_now())
    with _db() as con:
        cursor = con.execute(
            "UPDATE vouchers SET status='used', used_at=?, used_shop=? "
            "WHERE code=? AND status='issued' AND expires_at > ?",
            (now, shop_name, code, now),
        )
        success = cursor.rowcount == 1
    return success, verify(code)


def recent(limit: int = 8) -> list[Voucher]:
    """최근 발급 목록 (데모 모드 도우미용)."""
    with _db() as con:
        rows = con.execute("SELECT * FROM vouchers ORDER BY issued_at DESC LIMIT ?", (limit,)).fetchall()
    return [_to_voucher(r) for r in rows]


def force_expire(code: str) -> None:
    """(테스트용) 만료 상태를 만들어 봅니다."""
    past = _iso(_now() - timedelta(minutes=1))
    with _db() as con:
        con.execute("UPDATE vouchers SET expires_at=? WHERE code=? AND status='issued'", (past, code))
