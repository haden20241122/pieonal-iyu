"""마우스(손가락)를 따라 꽃잎이 한 장씩 떨어지는 연출 — 홈 화면에서만 동작해요.

· 가만히 있으면 아무것도 떨어지지 않아요. 움직인 만큼만, 천천히 흔들리며 내려와요 (눈이 피로하지 않게).
· 꽃잎은 화면 위 투명한 캔버스에 그려서 클릭·스크롤을 방해하지 않아요.
· '동작 줄이기' 설정을 켠 사람에게는 아예 켜지지 않아요.

동작 방식: st.html 은 스크립트를 막아서, 눈에 보이지 않는 작은 st.iframe 이 부모 화면에 스크립트를 심어요
(Streamlit 이 이 iframe 에 same-origin 을 허용해서 가능해요). 홈의 히어로(.st-key-hero)가 사라지면 스스로 정리돼요.
"""
import json

import streamlit as st

from components.embed import embed_html

# 부모 화면에서 실행되는 코드 (그래서 window/document 는 Streamlit 화면 쪽이에요)
_SCRIPT = r"""
(function () {
  if (window.__prPetals && window.__prPetals.alive) return;
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var state = window.__prPetals = { alive: true };
  var cv = document.createElement('canvas');
  cv.id = 'pr-petal-canvas';
  cv.setAttribute('aria-hidden', 'true');
  cv.style.cssText = 'position:fixed;left:0;top:0;width:100%;height:100%;pointer-events:none;z-index:30';
  document.body.appendChild(cv);
  var ctx = cv.getContext('2d'), dpr = Math.min(window.devicePixelRatio || 1, 2), w = 0, h = 0;
  function resize() { w = window.innerWidth; h = window.innerHeight; cv.width = w * dpr; cv.height = h * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); }
  resize();
  window.addEventListener('resize', resize);

  var petals = [], last = null, acc = 0, lastT = performance.now(), missing = 0;
  function spawn(x, y) {
    if (petals.length >= 56) petals.shift();
    petals.push({
      x: x + (Math.random() - .5) * 16, y: y + (Math.random() - .5) * 10,
      vx: (Math.random() - .5) * .025, vy: .012 + Math.random() * .02,
      size: 12 + Math.random() * 9, rot: Math.random() * 6.28, spin: (Math.random() - .5) * .003,
      flip: Math.random() * 6.28, flipSpd: .0018 + Math.random() * .0026,
      phase: Math.random() * 6.28, sway: .010 + Math.random() * .016,
      t: 0, life: 3400 + Math.random() * 1800, tone: Math.random() < .25 ? 1 : 0
    });
  }
  function onMove(x, y) {
    if (last) {
      var dx = x - last.x, dy = y - last.y;
      acc += Math.sqrt(dx * dx + dy * dy);
      var n = 0;
      while (acc > 36 && n < 2) { acc -= 36; n++; spawn(x, y); }   // 36px 움직일 때마다 한 장 (한 번에 최대 2장)
      if (acc > 200) acc = 0;
    }
    last = { x: x, y: y };
  }
  function pm(e) { onMove(e.clientX, e.clientY); }
  function tm(e) { var t = e.touches && e.touches[0]; if (t) onMove(t.clientX, t.clientY); }
  function leave() { last = null; acc = 0; }
  document.addEventListener('pointermove', pm, { passive: true });
  document.addEventListener('touchmove', tm, { passive: true });
  document.documentElement.addEventListener('mouseleave', leave);

  function draw(p, a) {
    var s = p.size;
    ctx.save();
    ctx.translate(p.x, p.y);
    ctx.rotate(p.rot);
    ctx.scale(1, .3 + .7 * Math.abs(Math.cos(p.flip)));   // 팔랑이며 뒤집히는 느낌
    ctx.globalAlpha = a;
    ctx.shadowColor = 'rgba(30,60,35,.30)'; ctx.shadowBlur = 7; ctx.shadowOffsetY = 2;
    var g = ctx.createLinearGradient(0, s * .5, 0, -s * .5);
    if (p.tone) { g.addColorStop(0, '#F2C9D2'); g.addColorStop(1, '#FFF3F4'); }
    else { g.addColorStop(0, '#EFE6C6'); g.addColorStop(1, '#FFFFFF'); }
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.moveTo(0, s * .5);
    ctx.bezierCurveTo(s * .44, s * .3, s * .34, -s * .38, 0, -s * .5);
    ctx.bezierCurveTo(-s * .34, -s * .38, -s * .44, s * .3, 0, s * .5);
    ctx.fill();
    ctx.restore();
  }
  function destroy() {
    state.alive = false;
    document.removeEventListener('pointermove', pm);
    document.removeEventListener('touchmove', tm);
    document.documentElement.removeEventListener('mouseleave', leave);
    window.removeEventListener('resize', resize);
    if (cv.parentNode) cv.parentNode.removeChild(cv);
    window.__prPetals = null;
  }
  function frame(now) {
    if (!state.alive) return;
    var dt = Math.min(now - lastT, 50); lastT = now;
    // 홈을 떠나면 정리 (잠깐 사라졌다 다시 그려지는 순간은 1.5초 기다려줘요)
    if (!document.querySelector('.st-key-hero')) { missing += dt; if (missing > 1500) { destroy(); return; } } else { missing = 0; }
    ctx.clearRect(0, 0, w, h);
    for (var i = petals.length - 1; i >= 0; i--) {
      var p = petals[i];
      p.t += dt;
      if (p.t > p.life || p.y > h + 40) { petals.splice(i, 1); continue; }
      p.vy = Math.min(p.vy + .00004 * dt, .07);                  // 점점 빨라지지만 천천히 (최대 초속 70px)
      p.x += (p.vx + Math.sin(p.t * .002 + p.phase) * p.sway) * dt;   // 좌우로 살랑
      p.y += p.vy * dt; p.rot += p.spin * dt; p.flip += p.flipSpd * dt;
      draw(p, Math.min(p.t / 240, 1) * Math.min((p.life - p.t) / 1200, 1) * .96);
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
"""

_LOADER = (
    "<!doctype html><html><body><script>"
    "try{var P=window.parent,D=P.document;"
    "if(!(P.__prPetals&&P.__prPetals.alive)){var s=D.createElement('script');s.textContent=%s;D.head.appendChild(s);}"
    "}catch(e){}"
    "</script></body></html>"
)


def render_petal_cursor() -> None:
    """눈에 보이지 않는 1px 짜리 iframe 으로 스크립트를 심어요. (스타일: .st-key-petal-script)"""
    with st.container(key="petal-script"):
        embed_html(_LOADER % json.dumps(_SCRIPT), height=1)
