"""'클릭하면 복사되는' 버튼. Streamlit 기본 위젯에는 클립보드 복사가 없어서 작은 HTML 버튼을 씁니다."""
import json

from components.embed import embed_html
from components.layout import h


def copy_button(text: str, label: str = "복사하기", height: int = 52) -> None:
    payload = json.dumps(text).replace("</", "<\\/")  # <script> 안에 안전하게 넣기
    label_js = json.dumps(f"📋 {label}")
    embed_html(
        f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
        html, body {{ margin: 0; background: transparent; }}
        button {{ width: 100%; height: 44px; border: 0; border-radius: 999px; background: #FFC93C; color: #22332C;
                 font: 700 15px 'Noto Sans KR','Malgun Gothic',sans-serif; cursor: pointer; box-shadow: 0 4px 0 #E9A400; }}
        button:hover {{ background: #FFD25E; }} button:active {{ transform: translateY(2px); box-shadow: 0 2px 0 #E9A400; }}
        </style></head><body>
        <button id="b" type="button" aria-label="{h(label)}"></button>
        <script>
          const text = {payload}, label = {label_js}, btn = document.getElementById('b');
          btn.textContent = label;
          btn.addEventListener('click', async () => {{
            try {{ await navigator.clipboard.writeText(text); }}
            catch (e) {{
              const t = document.createElement('textarea'); t.value = text; document.body.appendChild(t);
              t.select(); document.execCommand('copy'); t.remove();
            }}
            btn.textContent = '✅ 복사됐어요!';
            setTimeout(() => btn.textContent = label, 1800);
          }});
        </script></body></html>""",
        height=height,
    )
