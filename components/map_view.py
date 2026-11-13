"""지도 컴포넌트.

★ 지도 공급자를 바꾸려면 이 파일만 고치면 됩니다.
   - 지금: folium(Leaflet) + 지도 타일. API 키가 필요 없어서 바로 실행돼요.
   - Kakao Map / Naver Map 으로 바꾸려면 `_render_kakao()` 같은 함수를 만들어 `_PROVIDERS` 에 등록하고
     .env 의 MAP_PROVIDER 를 kakao 로 바꾸세요. (README '지도 API 연결' 참고)

화면 코드는 `render_place_map()` 하나만 호출하므로, 공급자가 바뀌어도 다른 파일은 수정하지 않아도 됩니다.
"""
from __future__ import annotations

import json
from typing import Callable
from urllib.parse import quote

import folium
import streamlit as st

from components.embed import embed_html
from components.layout import h
from config import settings
from config.campaign import NHIS_FACILITY_SEARCH_URL
from utils.geo import GeoResult
from utils.places import Place

_PIN_CSS = """
<style>
  .pin { width: 38px; height: 38px; display: grid; place-items: center; font-size: 20px; border-radius: 50%;
         background: #fff; box-shadow: 0 0 0 3px #FFC93C, 0 3px 10px rgba(0,0,0,.25); }
  .pin--clinic { box-shadow: 0 0 0 3px #3E9B6E, 0 3px 10px rgba(0,0,0,.25); }
  .pin--off { filter: grayscale(.9); opacity: .8; box-shadow: 0 0 0 3px #BBB, 0 3px 10px rgba(0,0,0,.2); }
  .pin--me { background: #2F6DA8; color: #fff; box-shadow: 0 0 0 4px rgba(47,109,168,.3); font-size: 18px; }
  .leaflet-popup-content { font-family: 'Noto Sans KR','Malgun Gothic',sans-serif; font-size: 13px; line-height: 1.55; margin: 12px 14px; }
  .pp .t { font-weight: 700; font-size: 15px; margin-bottom: 4px; }
  .pp .r { color: #33443c; }
  .pp .b { display: inline-block; font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 99px; margin-left: 4px;
           background: #FDEEEB; color: #B0523F; border: 1px dashed #E7A79B; vertical-align: middle; }
  .pp .ok { color: #2A7A55; font-weight: 700; } .pp .off { color: #8a7a3a; font-weight: 700; }
  .pp .l { margin-top: 6px; } .pp .l a { color: #2A7A55; font-weight: 700; margin-right: 10px; text-decoration: none; }
</style>
"""


def hours_label(kind: str) -> str:
    return "영업시간" if kind == "flower" else "진료시간"


def route_url(place: Place) -> str:
    """길찾기 링크 (Kakao 지도 '도착지' 링크 — 별도 API 키 없이 동작)."""
    return f"https://map.kakao.com/link/to/{quote(place.name)},{place.lat},{place.lon}"


def detail_link(place: Place, kind: str) -> tuple[str, str] | None:
    """(주소, 표시 문구) 홈페이지/상세정보 링크. 보여줄 링크가 없으면 None.

    · 등록된 주소가 있으면 그대로 연결
    · 검진기관인데 주소가 없으면 공단의 '검진기관 찾기'로 연결
    · 꽃집은 공식 상세 페이지가 없으면 링크를 만들지 않아요 (엉뚱한 곳으로 보내지 않기 위해)
    """
    if place.url:
        return place.url, "상세정보"
    if kind == "clinic":
        return NHIS_FACILITY_SEARCH_URL, "공단 검진기관 찾기"
    return None


def link_html(place: Place, kind: str, separator: str) -> str:
    """길찾기 + (있으면) 상세정보 링크 묶음."""
    links = [f'<a href="{h(route_url(place))}" target="_blank" rel="noopener noreferrer">길찾기</a>']
    detail = detail_link(place, kind)
    if detail:
        links.append(f'<a href="{h(detail[0])}" target="_blank" rel="noopener noreferrer">{h(detail[1])}</a>')
    return separator.join(links)


def _popup_html(place: Place, kind: str) -> str:
    rows = [f'<div class="t">{h(place.name)}{"<span class=b>샘플</span>" if place.is_sample else ""}</div>']
    rows.append(f'<div class="r">📍 {h(place.address)}</div>')
    rows.append(f'<div class="r">☎ {h(place.phone)}</div>')
    if place.hours:
        rows.append(f'<div class="r">🕘 {hours_label(kind)} {h(place.hours)}</div>')
    if kind == "clinic" and place.info:
        rows.append(f'<div class="r">🩺 {h(place.info)}</div>')
    if kind == "flower":
        status = '<span class="ok">참여 중 (꽃 수령 가능)</span>' if place.campaign_active else '<span class="off">참여 준비 중</span>'
        rows.append(f'<div class="r">🌼 캠페인 참여: {status}</div>')
    rows.append(f'<div class="l">{link_html(place, kind, " ")}</div>')
    return '<div class="pp">' + "".join(rows) + "</div>"


def _render_folium(places: list[Place], center: GeoResult, kind: str, height: int) -> None:
    fmap = folium.Map(
        location=[center.lat, center.lon],
        zoom_start=14,
        # API 키 없이 쓸 수 있는 OpenStreetMap 타일. 프로토타입·소규모용이에요.
        # 실제 서비스 트래픽에는 Kakao/Naver 등 정식 지도 API 를 쓰세요. (README 참고)
        tiles="OpenStreetMap",
        scrollWheelZoom=False,  # 페이지를 스크롤할 때 지도가 확대/축소되지 않게
        control_scale=True,
    )
    fmap.get_root().header.add_child(folium.Element(_PIN_CSS))

    bounds = [[center.lat, center.lon]]
    folium.Marker(
        [center.lat, center.lon],
        tooltip=f"검색 위치: {center.label}",
        icon=folium.DivIcon(html='<div class="pin pin--me">●</div>', icon_size=(38, 38), icon_anchor=(19, 19)),
    ).add_to(fmap)

    for place in places:
        emoji = "🩺" if kind == "clinic" else "🌼"
        css = "pin pin--clinic" if kind == "clinic" else ("pin" if place.campaign_active else "pin pin--off")
        folium.Marker(
            [place.lat, place.lon],
            tooltip=place.name,
            popup=folium.Popup(_popup_html(place, kind), max_width=300),
            icon=folium.DivIcon(html=f'<div class="{css}">{emoji}</div>', icon_size=(38, 38), icon_anchor=(19, 19)),
        ).add_to(fmap)
        bounds.append([place.lat, place.lon])

    if len(bounds) > 1:
        fmap.fit_bounds(bounds, padding=(36, 36), max_zoom=16)
    embed_html(fmap.get_root().render(), height=height)


_KAKAO_TEMPLATE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  html,body{margin:0;height:100%;font-family:'Noto Sans KR','Malgun Gothic',sans-serif}
  #map{width:100%;height:100%;border-radius:12px}
  .pin{width:36px;height:36px;display:grid;place-items:center;font-size:19px;border-radius:50%;background:#fff;
       box-shadow:0 0 0 3px #3E9B6E,0 3px 10px rgba(0,0,0,.25);cursor:pointer}
  .pin--flower{box-shadow:0 0 0 3px #FFC93C,0 3px 10px rgba(0,0,0,.25)}
  .pin--off{filter:grayscale(.9);opacity:.8}
  .pin--me{background:#2F6DA8;color:#fff;box-shadow:0 0 0 4px rgba(47,109,168,.3);font-size:16px;cursor:default}
  .iw{padding:10px 12px;font-size:13px;line-height:1.55;min-width:210px;max-width:260px}
  .iw .t{font-weight:700;font-size:14px;margin-bottom:3px}
  .iw a{color:#2A7A55;font-weight:700;margin-right:10px;text-decoration:none}
  .iw .b{font-size:10px;padding:1px 6px;border-radius:99px;background:#FDEEEB;color:#B0523F;border:1px dashed #E7A79B;margin-left:4px}
  #err{display:none;padding:24px;color:#8a4b3a;font-size:14px;line-height:1.6}
</style></head><body>
<div id="map"></div><div id="err"></div>
<script>
const DATA = __DATA__;
function fail(msg){document.getElementById('map').style.display='none';const e=document.getElementById('err');e.style.display='block';e.innerHTML=msg;}
function start(){
  const map = new kakao.maps.Map(document.getElementById('map'),{center:new kakao.maps.LatLng(DATA.center.lat,DATA.center.lon),level:5});
  map.addControl(new kakao.maps.ZoomControl(), kakao.maps.ControlPosition.RIGHT);
  const bounds = new kakao.maps.LatLngBounds();
  const me = new kakao.maps.LatLng(DATA.center.lat,DATA.center.lon);
  new kakao.maps.CustomOverlay({position:me,content:'<div class="pin pin--me" title="검색 위치">●</div>',yAnchor:.5,xAnchor:.5}).setMap(map);
  bounds.extend(me);
  let open = null;
  DATA.places.forEach(p=>{
    const pos = new kakao.maps.LatLng(p.lat,p.lon);
    bounds.extend(pos);
    const el = document.createElement('div');
    el.className = 'pin' + (DATA.kind==='flower' ? ' pin--flower' : '') + (p.off ? ' pin--off' : '');
    el.textContent = DATA.kind==='flower' ? '🌼' : '🩺'; el.title = p.name;
    const iw = new kakao.maps.InfoWindow({content:p.html,removable:true});
    el.onclick = ()=>{ if(open) open.close(); iw.setPosition(pos); iw.open(map); open=iw; };
    new kakao.maps.CustomOverlay({position:pos,content:el,yAnchor:.5,xAnchor:.5}).setMap(map);
  });
  if (DATA.places.length) map.setBounds(bounds,36,36,36,36);
}
const s = document.createElement('script');
s.src = 'https://dapi.kakao.com/v2/maps/sdk.js?appkey=__KEY__&autoload=false';
s.onload = ()=>{ try{ kakao.maps.load(start); }catch(e){ fail('카카오맵을 시작하지 못했어요.'); } };
s.onerror = ()=>fail('카카오맵 SDK를 불러오지 못했어요.<br>JavaScript 키와 <b>등록한 사이트 도메인</b>(Kakao Developers → 플랫폼 → Web)을 확인해주세요.');
document.head.appendChild(s);
</script></body></html>"""


def _render_kakao(places: list[Place], center: GeoResult, kind: str, height: int) -> None:
    if not settings.KAKAO_JS_KEY:
        raise RuntimeError("KAKAO_JS_KEY 가 설정되지 않았어요.")
    payload = {
        "kind": kind,
        "center": {"lat": center.lat, "lon": center.lon},
        "places": [
            {
                "name": p.name,
                "lat": p.lat,
                "lon": p.lon,
                "off": kind == "flower" and not p.campaign_active,
                "html": '<div class="iw">' + _popup_html(p, kind).replace('class="pp"', "") + "</div>",
            }
            for p in places
        ],
    }
    # </script> 로 HTML 이 끊기지 않도록 '<' 를 이스케이프
    data = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")
    html = _KAKAO_TEMPLATE.replace("__DATA__", data).replace("__KEY__", quote(settings.KAKAO_JS_KEY, safe=""))
    embed_html(html, height=height)


# 공급자 이름 → 그리기 함수.
_PROVIDERS: dict[str, Callable[[list[Place], GeoResult, str, int], None]] = {
    "folium": _render_folium,
    "kakao": _render_kakao,
}


def render_place_map(places: list[Place], center: GeoResult, kind: str, height: int = 440) -> None:
    """검색 위치(center)와 장소들을 지도에 marker 로 표시합니다. kind: 'clinic' | 'flower'"""
    provider = settings.MAP_PROVIDER
    if provider == "folium" and settings.KAKAO_JS_KEY:
        provider = "kakao"  # 키가 있으면 별도 설정 없이 카카오맵 사용
    renderer = _PROVIDERS.get(provider)
    if renderer is None:
        st.caption(f"‘{provider}’ 지도는 아직 연결되지 않아 기본 지도로 보여드려요.")
        renderer = _render_folium
    elif renderer is _render_kakao and not settings.KAKAO_JS_KEY:
        st.caption("KAKAO_JS_KEY 가 없어 기본 지도(OpenStreetMap)로 보여드려요.")
        renderer = _render_folium
    try:
        renderer(places, center, kind, height)
    except Exception:  # 지도 로딩에 실패해도 아래 목록은 계속 보이도록
        st.warning("지도를 불러오지 못했어요. 아래 목록에서 장소를 확인해주세요.")
