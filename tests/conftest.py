"""시험 공통 설정 — 실제 QR 발급 기록(data/runtime)을 건드리지 않도록 임시 DB 를 쓰게 합니다."""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
# config.settings 를 불러오기 '전에' 지정해야 해서 여기(가장 먼저 읽히는 파일)에서 설정합니다.
os.environ["VOUCHER_DB_PATH"] = str(Path(tempfile.mkdtemp()) / "test_vouchers.sqlite3")
