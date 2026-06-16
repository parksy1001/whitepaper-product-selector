#!/usr/bin/env python3
"""
html_builder.py
---------------
Reads cameras.json + recorders.json (from excel_parser.py) and builds
a complete IDIS Product Selector HTML file.

Output: output/ipcam_selector_v{N}_{YYYYMMDD_HHMMSS}.html

Usage:
    python3 html_builder.py
    python3 html_builder.py --cameras cameras.json --recorders recorders.json --output-dir output
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


# ── BUILD COUNTER ─────────────────────────────────────────────────────────────

def get_next_build_number(output_dir: Path) -> int:
    """Read build_count.txt and return next build number, then increment."""
    count_file = output_dir / 'build_count.txt'
    n = 1
    if count_file.exists():
        try:
            n = int(count_file.read_text().strip()) + 1
        except ValueError:
            n = 1
    count_file.write_text(str(n))
    return n


# ── VQS DATA (VMS questions - static) ────────────────────────────────────────

VQS_JS = """const VQS=[
  {id:1, q:"I need to use 3rd party devices / solutions (Access Control, VA, etc.)", yes:"ISS", no:null, crit:true},
  {id:2, q:"I need an LPR (License Plate Recognition) solution.", yes:"ISS", no:null, crit:true},
  {id:3, q:"For my video analytic needs, IDIS EdgeAI IPC is enough.", yes:"IDIS Center", no:"ISS"},
  {id:4, q:"I might have more than 10 simultaneous LIVE-only users.", yes:"ISS", no:"IDIS Center"},
  {id:5, q:"I need server/client architecture with a dedicated system administrator.", yes:"ISS", no:"IDIS Center"},
  {id:6, q:"I need to have a scheduled backup service for my video.", yes:"ISS", no:"IDIS Center"},
  {id:7, q:"Up to 2 simultaneous PLAYBACK and 5 simultaneous LIVE users is enough.", yes:"IDIS Center", no:"ISS"},
  {id:8, q:"I have a 4-monitor screen and need a video wall feature, but without extra cost.", yes:"IDIS Center", no:"ISS"},
  {id:9, q:"I need backup / failover service for my critical infrastructure.", yes:"ISS", no:"IDIS Center"},
  {id:10,q:"I have specific projects and may request additional functional add-on features, even at extra cost.", yes:"ISS", no:"IDIS Center"},
  {id:11,q:"I have security-sensitive data and need Audit Logs (who is running the system, how and when).", yes:"ISS", no:"IDIS Center"},
  {id:12,q:"I might have multiple users and need to assign them into groups with different clearances.", yes:"ISS", no:"IDIS Center"},
  {id:13,q:"I may need to consistently add new users and channels for expansions.", yes:"ISS", no:"IDIS Center"},
];"""


# ── HTML BUILDER ──────────────────────────────────────────────────────────────

def build_html(cameras: list, recorders: list, build_num: int, build_dt: datetime) -> str:

    build_label   = build_dt.strftime('%Y-%m-%d %H:%M:%S')
    cameras_json  = json.dumps(cameras,   ensure_ascii=False)
    recorders_json = json.dumps(recorders, ensure_ascii=False)

    # Build recorder JS array in same format as original
    rec_items = []
    for r in recorders:
        rec_items.append(
            '{' +
            f'model:{json.dumps(r["model"])},'
            f'series:{json.dumps(r.get("series",""))},'
            f'status:{json.dumps(r.get("status","출시완료"))},'
            f'title:{json.dumps(r.get("title",""))},'
            f'ch_num:{r.get("ch_num",0)},'
            f'channels:{json.dumps(r.get("channels","-"))},'
            f'maxBandwidth:{json.dumps(r.get("maxBandwidth","-"))},'
            f'recBandwidth:{json.dumps(r.get("recBandwidth","-"))},'
            f'recRes:{json.dumps(r.get("recRes","-"))},'
            f'hdd:{json.dumps(r.get("hdd","-"))},'
            f'totalCapacity:{json.dumps(r.get("totalCapacity","-"))},'
            f'supportedCam:{json.dumps(r.get("supportedCam","DirectIP"))},'
            f'videoOut:{json.dumps(r.get("videoOut","-"))},'
            f'dewarping:{str(r.get("dewarping",False)).lower()},'
            f'hasRAID:{str(r.get("hasRAID",False)).lower()},'
            f'hasONVIF:{str(r.get("hasONVIF",True)).lower()},'
            f'is4K:{str(r.get("is4K",False)).lower()}'
            '}'
        )
    recorders_js = 'const RECORDERS=[\n  ' + ',\n  '.join(rec_items) + '\n];'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IDIS Product Selector</title>
<style>
:root{{
  --bg:#f3f5f8;--surface:#fff;--surface2:#f7f8fa;--surface3:#eef0f3;
  --border:#e2e5ea;--border2:#cdd1d8;
  --text:#1a1d23;--text2:#4a5264;--text3:#8a93a8;
  --accent:#1a6ef5;--accent-bg:#eaf1ff;
  --green:#18a058;--green-bg:#e6f6ee;
  --yellow:#c07800;--yellow-bg:#fff8e6;
  --red:#d0312d;--red-bg:#fde8e6;
  --orange:#c45d00;--orange-bg:#fff0e0;
  --nav-h:52px;--sb:256px;
}}
[data-theme=dark]{{
  --bg:#13151c;--surface:#1d1f29;--surface2:#242632;--surface3:#2c2f3c;
  --border:#333648;--border2:#454858;
  --text:#e8eaf0;--text2:#9aa0b8;--text3:#585e78;
  --accent:#4d8ef5;--accent-bg:#1a2848;
  --green:#3dba6e;--green-bg:#0f2a1a;
  --yellow:#e8a020;--yellow-bg:#2a1e08;
  --red:#e85050;--red-bg:#2a0f0f;
  --orange:#e07020;--orange-bg:#2a1500;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font:14px/1.5 "Segoe UI",system-ui,sans-serif;min-height:100vh}}
/* NAV */
.nav{{position:sticky;top:0;z-index:200;height:var(--nav-h);background:var(--surface);
  border-bottom:1px solid var(--border);display:flex;align-items:center;gap:4px;padding:0 12px}}
.nav-btn{{height:32px;padding:0 13px;border:none;border-radius:6px;font-size:12.5px;font-weight:500;
  cursor:pointer;background:transparent;color:var(--text2);transition:all .15s}}
.nav-btn:hover{{background:var(--surface2);color:var(--text)}}
.nav-btn.nav-on{{background:var(--accent-bg);color:var(--accent);font-weight:600}}
.nav-gap{{flex:1}}
.build-info{{font-size:10.5px;color:var(--text3);margin-right:6px;white-space:nowrap}}
.build-info b{{color:var(--accent);font-weight:700}}
.th-btn{{width:30px;height:30px;border:1px solid var(--border);border-radius:6px;cursor:pointer;
  background:var(--surface2);color:var(--text2);display:flex;align-items:center;justify-content:center;
  font-size:13px;transition:all .15s}}
.th-btn.on{{background:var(--accent-bg);color:var(--accent);border-color:var(--accent)}}
.settings-btn{{width:30px;height:30px;border:1px solid var(--border);border-radius:6px;cursor:pointer;
  background:var(--surface2);color:var(--text2);font-size:16px;display:flex;align-items:center;
  justify-content:center;margin-left:4px;transition:all .15s}}
.settings-btn:hover{{background:var(--accent-bg);color:var(--accent);border-color:var(--accent)}}
/* SCREENS */
.screen{{display:none}}.screen.on{{display:block}}
/* CAM SIDEBAR */
.cam-wrap{{display:flex;min-height:calc(100vh - var(--nav-h))}}
.cam-aside{{width:var(--sb);flex-shrink:0;background:var(--surface);border-right:1px solid var(--border);
  padding:14px 12px;overflow-y:auto;height:calc(100vh - var(--nav-h));position:sticky;top:var(--nav-h)}}
.cam-main{{flex:1;overflow-y:auto;padding:16px}}
.sec-lbl{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.7px;
  color:var(--text3);margin:12px 0 6px}}
.sec-lbl:first-child{{margin-top:0}}
.chip-row{{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:4px}}
.chip{{padding:3px 9px;border-radius:5px;border:1px solid var(--border);background:var(--surface2);
  font-size:11.5px;font-weight:500;cursor:pointer;transition:all .12s;color:var(--text2);user-select:none}}
.chip:hover{{border-color:var(--accent);color:var(--accent)}}
.chip.on{{background:var(--accent-bg);border-color:var(--accent);color:var(--accent);font-weight:600}}
.sub-pnl{{overflow:hidden;transition:max-height .2s}}
.sub-pnl.shut{{max-height:0}}.sub-pnl.open{{max-height:600px}}
.sub-inner{{padding:4px 0 4px 8px;display:flex;flex-wrap:wrap;gap:3px}}
.ck-row{{display:flex;flex-direction:column;gap:3px;margin-top:2px}}
.ck-item{{display:flex;align-items:center;gap:6px;cursor:pointer;padding:2px 0}}
.ck-item input{{display:none}}
.ck-box{{width:14px;height:14px;border:1.5px solid var(--border2);border-radius:3px;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;transition:all .12s}}
.ck-item input:checked+.ck-box{{background:var(--accent);border-color:var(--accent)}}
.ck-item input:checked+.ck-box::after{{content:"✓";color:#fff;font-size:9px;font-weight:700}}
.ck-lbl{{font-size:12px;color:var(--text2)}}
.ck-item:hover .ck-box{{border-color:var(--accent)}}
.st-row{{display:flex;gap:4px;margin-top:2px}}
.st-pill{{padding:3px 10px;border-radius:20px;font-size:11px;font-weight:500;cursor:pointer;
  border:1px solid var(--border);background:var(--surface2);color:var(--text2);transition:all .12s}}
.st-pill.on{{background:var(--accent-bg);border-color:var(--accent);color:var(--accent)}}
.rst-btn{{margin-top:14px;width:100%;padding:7px;border:1px solid var(--border);border-radius:6px;
  background:var(--surface2);cursor:pointer;font-size:12px;color:var(--text2);font-weight:500;transition:all .12s}}
.rst-btn:hover{{border-color:var(--red);color:var(--red);background:var(--red-bg)}}
/* CAM CARDS */
.res-bar{{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}}
.res-pill{{padding:3px 10px;background:var(--accent-bg);color:var(--accent);border-radius:20px;font-size:12px;font-weight:700}}
.cam-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px}}
.cam-card{{background:var(--surface);border:1.5px solid var(--border);border-radius:10px;padding:12px;
  cursor:pointer;transition:all .15s;position:relative}}
.cam-card:hover{{border-color:var(--accent);box-shadow:0 2px 12px rgba(26,110,245,.1)}}
.cam-card.in-cmp{{border-color:var(--green)}}
.card-cmp-btn{{position:absolute;top:8px;right:8px;width:22px;height:22px;border-radius:50%;
  border:1.5px solid var(--border);background:var(--surface2);cursor:pointer;font-size:11px;
  display:flex;align-items:center;justify-content:center;color:var(--text3)}}
.card-cmp-btn:hover{{border-color:var(--green);color:var(--green);background:var(--green-bg)}}
.card-cmp-btn.in{{border-color:var(--green);color:var(--green);background:var(--green-bg)}}
.card-model{{font-size:12px;font-weight:700;color:var(--text);margin-bottom:2px;padding-right:22px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.card-title{{font-size:10.5px;color:var(--text2);margin-bottom:7px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.card-tags{{display:flex;flex-wrap:wrap;gap:3px}}
.tag{{font-size:9.5px;font-weight:600;padding:1px 6px;border-radius:3px}}
.t-mp{{background:var(--surface3);color:var(--text2)}}
.t-ir{{background:#e8f4ff;color:#1a6aa0}}[data-theme=dark] .t-ir{{background:#0f2030;color:#4d9fdd}}
.t-ai{{background:var(--accent-bg);color:var(--accent)}}
.t-aip{{background:var(--yellow-bg);color:var(--yellow)}}
.t-mic{{background:var(--green-bg);color:var(--green)}}
.t-lpr-t{{background:var(--red-bg);color:var(--red)}}
.t-act-t{{background:var(--red-bg);color:var(--red)}}
.t-ul{{background:#f0eaff;color:#6a2dce}}[data-theme=dark] .t-ul{{background:#200f2a;color:#a97de8}}
.t-fips{{background:#fff0e0;color:#c45d00}}
.eol-badge{{font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;background:#fde8e6;color:var(--red)}}
.empty-st{{text-align:center;padding:40px;color:var(--text3)}}
.gone{{display:none!important}}
/* DETAIL */
.dtl-ov{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:500;align-items:center;justify-content:center}}
.dtl-ov.open{{display:flex}}
.dtl-box{{background:var(--surface);border-radius:14px;width:min(720px,95vw);max-height:90vh;overflow-y:auto;padding:24px}}
.dtl-hdr{{display:flex;align-items:flex-start;gap:12px;margin-bottom:18px}}
.dtl-title-area{{flex:1}}
.dtl-model{{font-size:18px;font-weight:700}}
.dtl-title{{font-size:13px;color:var(--text2);margin-top:2px}}
.dtl-close{{width:32px;height:32px;border:1px solid var(--border);border-radius:8px;cursor:pointer;
  background:var(--surface2);color:var(--text2);font-size:18px;display:flex;align-items:center;justify-content:center}}
.dtl-grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}
.dtl-row{{display:flex;flex-direction:column;gap:2px;padding:8px;background:var(--surface2);border-radius:7px}}
.dtl-key{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--text3)}}
.dtl-val{{font-size:12px;color:var(--text);white-space:pre-line}}
.dtl-full{{grid-column:1/-1}}
.dtl-tags{{display:flex;flex-wrap:wrap;gap:4px;margin-top:10px}}
.dtl-tag{{font-size:10px;font-weight:600;padding:2px 8px;border-radius:4px;background:var(--accent-bg);color:var(--accent)}}
.dtl-btns{{display:flex;gap:8px;margin-top:16px}}
.mbtn{{padding:7px 16px;border-radius:7px;border:1.5px solid var(--border);cursor:pointer;
  font-size:12px;font-weight:600;background:var(--surface2);color:var(--text2);transition:all .12s}}
.mbtn:hover{{border-color:var(--accent);color:var(--accent)}}
.mbtn-add.in{{background:var(--green-bg);border-color:var(--green);color:var(--green)}}
/* COMPARE */
.cmp-ov{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:600;overflow-y:auto;padding:20px}}
.cmp-ov.open{{display:block}}
.cmp-box{{background:var(--surface);border-radius:14px;max-width:960px;margin:0 auto;padding:22px}}
.cmp-hdr{{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}}
.cmp-hdr h2{{font-size:16px;font-weight:700}}
.cmp-slots{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}}
.cmp-slot{{padding:5px 12px;border-radius:6px;font-size:12px;background:var(--surface2);border:1px solid var(--border);color:var(--text2)}}
.cmp-slot.full{{display:flex;align-items:center;gap:6px;background:var(--accent-bg);border-color:var(--accent);color:var(--accent)}}
.cmp-x{{cursor:pointer;font-size:14px;color:var(--text3)}}.cmp-x:hover{{color:var(--red)}}
.cmp-table{{width:100%;border-collapse:collapse;font-size:12px;overflow-x:auto;display:block}}
.cmp-table th{{padding:8px 10px;background:var(--surface2);border-bottom:2px solid var(--border);font-weight:700;text-align:left;white-space:nowrap;min-width:140px}}
.cmp-table td{{padding:7px 10px;border-bottom:1px solid var(--border);color:var(--text2);vertical-align:top;min-width:140px}}
.cmp-table tr:hover td{{background:var(--surface2)}}
.cmp-table .row-lbl{{font-weight:600;color:var(--text3);font-size:11px;text-transform:uppercase;background:var(--surface2);width:120px;min-width:120px}}
/* VMS */
.vms-wrap{{max-width:960px;margin:0 auto;padding:20px}}
.vms-result{{padding:16px 20px;border-radius:10px;margin-bottom:20px;display:none}}
.vms-result.show{{display:block}}
.vms-result.iss{{background:var(--accent-bg);border:2px solid var(--accent)}}
.vms-result.idc{{background:var(--green-bg);border:2px solid var(--green)}}
.vms-result-title{{font-size:18px;font-weight:700;margin-bottom:6px}}
.vms-result.iss .vms-result-title{{color:var(--accent)}}
.vms-result.idc .vms-result-title{{color:var(--green)}}
.vms-result-desc{{font-size:13px;color:var(--text2);line-height:1.6}}
.vms-q-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px}}
.vms-q{{padding:10px 12px;background:var(--surface);border:1.5px solid var(--border);border-radius:9px;transition:border-color .12s}}
.vms-q.ans-yes{{border-color:var(--green);background:var(--green-bg)}}
.vms-q.ans-no{{border-color:var(--border2);background:var(--surface2)}}
.vms-q.ans-skip{{opacity:.5}}
.vms-q-text{{font-size:12px;color:var(--text);line-height:1.4;margin-bottom:8px;font-weight:500}}
.vms-q-btns{{display:flex;gap:5px;flex-wrap:wrap}}
.vms-btn{{padding:4px 10px;border-radius:5px;border:1px solid var(--border);cursor:pointer;
  font-size:11px;font-weight:600;background:var(--surface2);color:var(--text2);transition:all .12s}}
.vms-btn:hover{{border-color:var(--accent);color:var(--accent)}}
.vms-btn.active-yes{{background:var(--green-bg);border-color:var(--green);color:var(--green)}}
.vms-btn.active-no{{background:var(--surface3);border-color:var(--border2);color:var(--text2)}}
.vms-btn.active-skip{{background:var(--yellow-bg);border-color:var(--yellow);color:var(--yellow)}}
.vms-reset-btn{{margin-top:12px;padding:7px 14px;border:1px solid var(--border);border-radius:6px;
  background:var(--surface2);cursor:pointer;font-size:12px;color:var(--text2);transition:all .12s}}
.vms-reset-btn:hover{{border-color:var(--red);color:var(--red)}}
/* RECORDER */
.rec-wrap{{display:flex;min-height:calc(100vh - var(--nav-h))}}
.rec-aside{{width:var(--sb);flex-shrink:0;background:var(--surface);border-right:1px solid var(--border);
  padding:14px 12px;overflow-y:auto;height:calc(100vh - var(--nav-h));position:sticky;top:var(--nav-h)}}
.rec-main{{flex:1;overflow-y:auto;padding:16px}}
.rec-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px}}
.rec-card{{background:var(--surface);border:1.5px solid var(--border);border-radius:10px;padding:12px;
  cursor:pointer;transition:all .15s;position:relative}}
.rec-card:hover{{border-color:var(--accent);box-shadow:0 2px 12px rgba(26,110,245,.1)}}
.rec-card.in-cmp{{border-color:var(--green)}}
.rec-ser-badge{{display:inline-block;font-size:9.5px;font-weight:700;padding:2px 7px;border-radius:4px;margin-bottom:5px}}
.rec-model{{font-size:12.5px;font-weight:700;color:var(--text);margin-bottom:3px;padding-right:22px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.rec-title{{font-size:11px;color:var(--text2);margin-bottom:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.rec-tags{{display:flex;flex-wrap:wrap;gap:3px}}
.rec-tag{{font-size:9px;font-weight:600;padding:1px 5px;border-radius:3px;background:var(--surface3);color:var(--text2)}}
.rec-tag.t-4k{{background:var(--accent-bg);color:var(--accent)}}
.rec-tag.t-raid{{background:var(--yellow-bg);color:var(--yellow)}}
.rec-tag.t-onvif{{background:var(--green-bg);color:var(--green)}}
/* VA */
.va-wrap{{display:flex;min-height:calc(100vh - var(--nav-h))}}
.va-left{{width:240px;flex-shrink:0;background:var(--surface);border-right:1px solid var(--border);
  padding:14px 10px;overflow-y:auto;height:calc(100vh - var(--nav-h));position:sticky;top:var(--nav-h)}}
.va-right{{flex:1;overflow-y:auto;padding:20px 24px}}
.va-sec-lbl{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.7px;color:var(--text3);margin:12px 0 6px}}
.va-sec-lbl:first-child{{margin-top:0}}
.va-feat-grid{{display:grid;grid-template-columns:1fr 1fr;gap:5px}}
.va-feat-card{{background:var(--surface2);border:1.5px solid var(--border);border-radius:8px;
  padding:9px 7px 7px;cursor:pointer;transition:all .14s;text-align:center;position:relative;user-select:none}}
.va-feat-card:hover{{border-color:var(--accent);background:var(--accent-bg)}}
.va-feat-card.active{{border-color:var(--accent);background:var(--accent-bg);box-shadow:0 0 0 2px var(--accent)}}
.vfc-badge{{position:absolute;top:4px;right:4px;font-size:8px;font-weight:700;padding:1px 4px;
  border-radius:3px;background:var(--accent);color:#fff;letter-spacing:.3px}}
.vfc-badge.plus{{background:var(--yellow)}}
.vfc-badge.lpr-b{{background:var(--red)}}
.vfc-badge.box-b{{background:var(--orange)}}
.vfc-icon{{font-size:18px;line-height:1;margin-bottom:3px}}
.vfc-name{{font-size:10.5px;font-weight:700;color:var(--text);line-height:1.2;margin-bottom:2px}}
.va-feat-card.active .vfc-name{{color:var(--accent)}}
.vfc-tier{{font-size:9px;color:var(--text3);line-height:1.3}}
.va-intro{{text-align:center;padding:60px 20px;color:var(--text2)}}
.va-intro-icon{{font-size:44px;margin-bottom:12px}}
.va-intro h2{{font-size:17px;font-weight:600;color:var(--text);margin-bottom:8px}}
.va-intro p{{font-size:13px;line-height:1.7;max-width:360px;margin:0 auto}}
.va-feat-hdr{{margin-bottom:14px}}
.va-feat-hdr-top{{display:flex;align-items:center;gap:8px;margin-bottom:4px}}
.va-feat-hdr-icon{{font-size:22px}}
.va-feat-hdr-name{{font-size:17px;font-weight:700;color:var(--text)}}
.va-feat-hdr-desc{{font-size:12.5px;color:var(--text2);line-height:1.55}}
.va-global-note{{background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--accent);
  border-radius:8px;padding:9px 13px;font-size:11.5px;color:var(--text2);margin-bottom:14px;line-height:1.6}}
.va-global-note b{{color:var(--text)}}
.va-col-grid{{display:grid;gap:12px;margin-bottom:12px}}
.va-col-grid.two{{grid-template-columns:1fr 1fr}}
.va-col-grid.three{{grid-template-columns:1fr 1fr 1fr}}
.va-panel{{background:var(--surface);border:1px solid var(--border);border-radius:10px;overflow:hidden}}
.va-panel-hdr{{display:flex;align-items:center;gap:7px;padding:9px 13px;background:var(--surface2);border-bottom:1px solid var(--border)}}
.va-panel-icon{{font-size:14px}}
.va-panel-title{{font-size:12px;font-weight:700;color:var(--text);flex:1}}
.va-panel-cnt{{font-size:10px;font-weight:700;color:var(--accent);background:var(--accent-bg);padding:2px 7px;border-radius:10px}}
.va-panel-body{{padding:7px;display:flex;flex-direction:column;gap:4px;max-height:300px;overflow-y:auto}}
.va-cam-row,.va-nvr-row{{background:var(--surface2);border:1px solid var(--border);border-radius:6px;padding:7px 9px}}
.va-cam-model,.va-nvr-model{{font-size:11px;font-weight:700;color:var(--text);margin-bottom:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.va-cam-title{{font-size:10px;color:var(--text2);margin-bottom:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.va-nvr-spec{{font-size:10px;color:var(--text2);margin-bottom:3px}}
.va-cam-tags,.va-nvr-tags{{display:flex;flex-wrap:wrap;gap:2px}}
.va-cam-tag,.va-nvr-tag{{font-size:9px;font-weight:600;padding:1px 5px;border-radius:3px}}
.t-cat,.t-mp{{background:var(--surface3);color:var(--text2)}}
.t-ai{{background:var(--accent-bg);color:var(--accent)}}
.t-aip{{background:var(--yellow-bg);color:var(--yellow)}}
.t-lpr{{background:var(--red-bg);color:var(--red)}}
.t-act{{background:var(--red-bg);color:var(--red)}}
.t-4k{{background:var(--accent-bg);color:var(--accent)}}
.t-raid{{background:var(--yellow-bg);color:var(--yellow)}}
.t-onvif{{background:var(--green-bg);color:var(--green)}}
.va-nvr-series{{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--text3);margin-bottom:1px}}
.va-box-card{{background:linear-gradient(135deg,var(--surface2),var(--surface3));border:1.5px solid var(--border2);border-radius:8px;padding:11px 13px;margin:8px}}
.va-box-badge{{display:inline-block;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--orange);background:var(--orange-bg);padding:2px 6px;border-radius:3px;margin-bottom:5px}}
.va-box-name{{font-size:13px;font-weight:700;color:var(--text);margin-bottom:3px}}
.va-box-desc{{font-size:11px;color:var(--text2);line-height:1.5;margin-bottom:7px}}
.va-box-specs{{display:flex;flex-direction:column;gap:3px;margin-bottom:7px}}
.va-box-spec{{font-size:10.5px;color:var(--text2);display:flex;gap:6px}}
.va-box-spec b{{color:var(--text);min-width:80px;flex-shrink:0}}
.va-box-compat-title{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--text3);margin-bottom:3px}}
.va-compat-row{{font-size:10.5px;display:flex;gap:4px;align-items:flex-start;margin-bottom:2px;line-height:1.4;color:var(--text2)}}
.va-incompat-note{{background:var(--yellow-bg);border:1px solid var(--yellow);border-radius:7px;padding:9px 13px;font-size:11.5px;color:var(--text2);margin-top:12px;line-height:1.6}}
.va-incompat-row{{display:flex;gap:5px;align-items:flex-start;margin-bottom:3px}}
.va-incompat-row:last-child{{margin-bottom:0}}
/* SETTINGS */
.settings-ov{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:700}}
.settings-ov.open{{display:block}}
.settings-panel{{position:fixed;top:0;right:0;bottom:0;width:min(520px,95vw);
  background:var(--surface);border-left:1px solid var(--border);overflow-y:auto;padding:20px;
  transform:translateX(100%);transition:transform .25s ease;z-index:701}}
.settings-ov.open .settings-panel{{transform:translateX(0)}}
.set-hdr{{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}}
.set-hdr h2{{font-size:16px;font-weight:700}}
.set-close{{width:30px;height:30px;border:1px solid var(--border);border-radius:7px;cursor:pointer;
  background:var(--surface2);color:var(--text2);font-size:18px;display:flex;align-items:center;justify-content:center}}
.set-tabs{{display:flex;gap:4px;margin-bottom:16px;border-bottom:1px solid var(--border);padding-bottom:10px}}
.set-tab{{padding:5px 14px;border-radius:6px;font-size:12.5px;font-weight:500;cursor:pointer;
  background:transparent;border:none;color:var(--text2);transition:all .12s}}
.set-tab.on{{background:var(--accent-bg);color:var(--accent);font-weight:600}}
.set-content{{display:none}}.set-content.on{{display:block}}
.set-section-lbl{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:var(--text3);margin:12px 0 6px}}
.model-vis-row{{display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid var(--border)}}
.model-vis-row:last-child{{border-bottom:none}}
.model-vis-name{{font-size:12px;color:var(--text);flex:1}}
.model-vis-cat{{font-size:10px;color:var(--text3);min-width:65px}}
.vis-toggle{{width:36px;height:20px;border-radius:10px;cursor:pointer;position:relative;
  flex-shrink:0;border:none;transition:background .15s;background:var(--border2)}}
.vis-toggle.on{{background:var(--accent)}}
.vis-toggle::after{{content:'';position:absolute;top:2px;left:2px;width:16px;height:16px;
  border-radius:50%;background:#fff;transition:transform .15s;box-shadow:0 1px 3px rgba(0,0,0,.2)}}
.vis-toggle.on::after{{transform:translateX(16px)}}
.cat-assign-row{{display:flex;align-items:center;gap:8px;padding:5px 0;border-bottom:1px solid var(--border)}}
.cat-assign-row:last-child{{border-bottom:none}}
.cat-assign-name{{font-size:12px;color:var(--text);flex:1}}
.cat-select{{font-size:11px;padding:3px 8px;border:1px solid var(--border);border-radius:5px;
  background:var(--surface2);color:var(--text);cursor:pointer}}
.new-cat-row{{display:flex;gap:6px;margin-top:10px}}
.new-cat-input{{flex:1;padding:6px 10px;border:1px solid var(--border);border-radius:6px;
  background:var(--surface2);color:var(--text);font-size:12px}}
.new-cat-btn{{padding:6px 12px;background:var(--accent);color:#fff;border:none;border-radius:6px;
  cursor:pointer;font-size:12px;font-weight:600}}
.set-save-btn{{width:100%;margin-top:16px;padding:10px;background:var(--accent);color:#fff;
  border:none;border-radius:8px;cursor:pointer;font-size:13px;font-weight:600}}
</style>
</head>
<body>

<nav class="nav">
  <button class="nav-btn nav-on" id="navCam" onclick="goScreen('cam')">Camera Selector</button>
  <button class="nav-btn" id="navVms" onclick="goScreen('vms')">VMS Selector</button>
  <button class="nav-btn" id="navRec" onclick="goScreen('rec')">Recorder Selector</button>
  <button class="nav-btn" id="navVa"  onclick="goScreen('va')">VA Selector</button>
  <div class="nav-gap"></div>
  <span class="build-info">Build <b>#{build_num}</b> &nbsp;{build_label}</span>
  <button class="th-btn on" id="btnL" onclick="setTheme('light')" title="Light">☀</button>
  <button class="th-btn" id="btnD" onclick="setTheme('dark')" title="Dark">🌙</button>
  <button class="settings-btn" onclick="openSettings()" title="Settings">⚙</button>
</nav>

<!-- CAMERA SCREEN -->
<div id="scrCam" class="screen on">
<div class="cam-wrap">
  <aside class="cam-aside">
    <div class="sec-lbl">Protocol</div>
    <div class="chip-row">
      <span class="chip" onclick="togSet(aProto,'directip',this)">DirectIP</span>
      <span class="chip" onclick="togSet(aProto,'onvif',this)">ONVIF</span>
    </div>
    <div class="sub-pnl shut" id="sub-onvif">
      <div class="sub-inner">
        <span class="chip" data-onvifp="S" onclick="togSet(aOnvifP,'S',this)">Profile S</span>
        <span class="chip" data-onvifp="T" onclick="togSet(aOnvifP,'T',this)">Profile T</span>
        <span class="chip" data-onvifp="M" onclick="togSet(aOnvifP,'M',this)">Profile M</span>
      </div>
    </div>
    <div class="sec-lbl">Form Factor</div>
    <div class="chip-row" id="catFilters"></div>
    <div class="sec-lbl">Lens Type &amp; Focal Length</div>
    <div class="chip-row">
      <span class="chip" id="lFixed"    onclick="toggleLens('fixed',this)">Fixed Focal</span>
      <span class="chip" id="lMoto"     onclick="toggleLens('motorized',this)">Motorized</span>
    </div>
    <div class="sub-pnl shut" id="sub-fixed">
      <div class="sub-inner">
        <span class="chip" data-lens="fixed" data-fl="≤2.0mm"    onclick="toggleFl(this)">≤ 2.0mm</span>
        <span class="chip" data-lens="fixed" data-fl="2.8mm"     onclick="toggleFl(this)">2.8mm</span>
        <span class="chip" data-lens="fixed" data-fl="3.3mm"     onclick="toggleFl(this)">3.3mm</span>
        <span class="chip" data-lens="fixed" data-fl="4.0–4.3mm" onclick="toggleFl(this)">4.0–4.3mm</span>
        <span class="chip" data-lens="fixed" data-fl="6.0mm+"    onclick="toggleFl(this)">6.0mm+</span>
      </div>
    </div>
    <div class="sub-pnl shut" id="sub-motorized">
      <div class="sub-inner">
        <span class="chip" data-lens="motorized" data-fl="Normal"   onclick="toggleFl(this)">Normal (≤14mm)</span>
        <span class="chip" data-lens="motorized" data-fl="Extended" onclick="toggleFl(this)">Extended (7–22mm)</span>
        <span class="chip" data-lens="motorized" data-fl="PTZ"      onclick="toggleFl(this)">PTZ</span>
      </div>
    </div>
    <div class="sec-lbl">Resolution</div>
    <div class="chip-row">
      <span class="chip" onclick="togSet(aRes,'2',this)">2MP</span>
      <span class="chip" onclick="togSet(aRes,'4',this)">4MP</span>
      <span class="chip" onclick="togSet(aRes,'5',this)">5MP</span>
      <span class="chip" onclick="togSet(aRes,'8',this)">8MP+</span>
    </div>
    <div class="sec-lbl">Video Analytics</div>
    <div class="chip-row">
      <span class="chip" onclick="togSet(aAn,'none',this)">None</span>
      <span class="chip" onclick="togSet(aAn,'edgeai',this)">EdgeAI</span>
      <span class="chip" onclick="togSet(aAn,'edgeai_plus',this)">EdgeAI+</span>
      <span class="chip" onclick="togSet(aAn,'lpr',this)">LPR</span>
      <span class="chip" onclick="togSet(aAn,'active',this)">ActiveDet</span>
    </div>
    <div class="sec-lbl">Features</div>
    <div class="ck-row">
      <label class="ck-item"><input type="checkbox" data-feat="hasIR"><span class="ck-box"></span><span class="ck-lbl">IR Night Vision</span></label>
      <label class="ck-item"><input type="checkbox" data-feat="hasAlarm"><span class="ck-box"></span><span class="ck-lbl">Alarm In/Out</span></label>
      <label class="ck-item"><input type="checkbox" data-feat="hasIDLA"><span class="ck-box"></span><span class="ck-lbl">AI Deep Learning (IDLA)</span></label>
      <label class="ck-item"><input type="checkbox" data-feat="hasVandal"><span class="ck-box"></span><span class="ck-lbl">Vandal / Outdoor</span></label>
      <label class="ck-item"><input type="checkbox" data-feat="hasFIPS"><span class="ck-box"></span><span class="ck-lbl">FIPS 140-3 + UL</span></label>
      <label class="ck-item"><input type="checkbox" data-feat="hasMotorizedZoom"><span class="ck-box"></span><span class="ck-lbl">Motorized Zoom</span></label>
      <label class="ck-item"><input type="checkbox" data-feat="hasBuiltinMic"><span class="ck-box"></span><span class="ck-lbl">Built-in Microphone</span></label>
      <label class="ck-item"><input type="checkbox" data-feat="hasSD"><span class="ck-box"></span><span class="ck-lbl">SD Card Slot</span></label>
      <label class="ck-item"><input type="checkbox" data-feat="hasAudio"><span class="ck-box"></span><span class="ck-lbl">Two-Way Audio</span></label>
    </div>
    <div class="sec-lbl">Status</div>
    <div class="st-row">
      <span class="st-pill on" data-st="출시완료" onclick="togStatus('출시완료',this)">Released</span>
      <span class="st-pill" data-st="개발중"  onclick="togStatus('개발중',this)">In Dev</span>
    </div>
    <button class="rst-btn" onclick="resetAll()">↺ Reset All Filters</button>
  </aside>
  <main class="cam-main">
    <div class="res-bar">
      <span class="res-pill" id="resNum">—</span>
      <button class="mbtn" onclick="openCmpModal()">Compare (<span id="cmpCnt">0</span>)</button>
    </div>
    <div class="cam-grid" id="cardsGrid"></div>
    <div class="empty-st gone" id="emptySt">No cameras match the selected filters.</div>
  </main>
</div>
</div>

<!-- DETAIL MODAL -->
<div class="dtl-ov" id="dtlOv" onclick="if(event.target===this)this.classList.remove('open')">
  <div class="dtl-box" id="dtlBox"></div>
</div>

<!-- COMPARE MODAL -->
<div class="cmp-ov" id="cmpOv" onclick="if(event.target===this)this.classList.remove('open')">
  <div class="cmp-box">
    <div class="cmp-hdr">
      <h2>Compare Cameras</h2>
      <button class="dtl-close" onclick="document.getElementById('cmpOv').classList.remove('open')">✕</button>
    </div>
    <div class="cmp-slots" id="cmpSlots"></div>
    <div id="cmpTableWrap"></div>
  </div>
</div>

<!-- VMS SCREEN (result above questions) -->
<div id="scrVms" class="screen">
  <div class="vms-wrap">
    <div id="vmsResult" class="vms-result">
      <div class="vms-result-title" id="vmsRTitle"></div>
      <div class="vms-result-desc"  id="vmsRDesc"></div>
    </div>
    <div class="vms-q-grid" id="vmsQGrid"></div>
    <button class="vms-reset-btn" onclick="vReset()">↺ Reset</button>
  </div>
</div>

<!-- RECORDER SCREEN -->
<div id="scrRec" class="screen">
<div class="rec-wrap">
  <aside class="rec-aside">
    <div class="sec-lbl">Series</div>
    <div class="chip-row" id="recSerFilters"></div>
    <div class="sec-lbl">Channels</div>
    <div class="chip-row">
      <span class="chip" onclick="togRSet(rChF,'4',this)">4ch</span>
      <span class="chip" onclick="togRSet(rChF,'8',this)">8ch</span>
      <span class="chip" onclick="togRSet(rChF,'16',this)">16ch</span>
      <span class="chip" onclick="togRSet(rChF,'32',this)">32ch</span>
      <span class="chip" onclick="togRSet(rChF,'64',this)">64ch+</span>
    </div>
    <div class="sec-lbl">Features</div>
    <div class="ck-row">
      <label class="ck-item"><input type="checkbox" data-rfeat="is4K"><span class="ck-box"></span><span class="ck-lbl">4K Support</span></label>
      <label class="ck-item"><input type="checkbox" data-rfeat="hasRAID"><span class="ck-box"></span><span class="ck-lbl">RAID</span></label>
      <label class="ck-item"><input type="checkbox" data-rfeat="hasONVIF"><span class="ck-box"></span><span class="ck-lbl">ONVIF</span></label>
    </div>
    <div class="sec-lbl">Status</div>
    <div class="st-row">
      <span class="st-pill on" data-rst="출시완료" onclick="togRStatus('출시완료',this)">Released</span>
      <span class="st-pill"    data-rst="단종"    onclick="togRStatus('단종',this)">EOL</span>
    </div>
    <button class="rst-btn" onclick="resetRec()">↺ Reset</button>
  </aside>
  <main class="rec-main">
    <div class="res-bar">
      <span class="res-pill" id="recNum">—</span>
      <button class="mbtn" onclick="openRCmpModal()">Compare (<span id="rCmpCnt">0</span>)</button>
    </div>
    <div class="rec-grid" id="recGrid"></div>
    <div class="empty-st gone" id="recEmpty">No recorders match the selected filters.</div>
  </main>
</div>
</div>

<!-- RECORDER COMPARE -->
<div class="cmp-ov" id="rCmpOv" onclick="if(event.target===this)this.classList.remove('open')">
  <div class="cmp-box">
    <div class="cmp-hdr">
      <h2>Compare Recorders</h2>
      <button class="dtl-close" onclick="document.getElementById('rCmpOv').classList.remove('open')">✕</button>
    </div>
    <div class="cmp-slots" id="rCmpSlots"></div>
    <div id="rCmpTableWrap"></div>
  </div>
</div>

<!-- VA SCREEN -->
<div id="scrVa" class="screen">
<div class="va-wrap">
  <aside class="va-left">
    <div class="va-sec-lbl">Edge AI (Camera Built-in)</div>
    <div class="va-feat-grid">
      <div class="va-feat-card" data-vaf="edgeai">
        <span class="vfc-badge">AI</span>
        <div class="vfc-icon">🎯</div>
        <div class="vfc-name">EdgeAI</div>
        <div class="vfc-tier">Obj Det · Loitering · Intrusion</div>
      </div>
      <div class="va-feat-card" data-vaf="edgeai_plus">
        <span class="vfc-badge plus">AI+</span>
        <div class="vfc-icon">✨</div>
        <div class="vfc-name">EdgeAI Plus</div>
        <div class="vfc-tier">Attributes · A-Cut · Crowd</div>
      </div>
      <div class="va-feat-card" data-vaf="lpr">
        <span class="vfc-badge lpr-b">LPR</span>
        <div class="vfc-icon">🚗</div>
        <div class="vfc-name">LPR</div>
        <div class="vfc-tier">License Plate Recognition</div>
      </div>
      <div class="va-feat-card" data-vaf="active">
        <span class="vfc-badge lpr-b">ACT</span>
        <div class="vfc-icon">🚨</div>
        <div class="vfc-name">Active Deterrence</div>
        <div class="vfc-tier">Warm Light · Warning</div>
      </div>
    </div>
    <div class="va-sec-lbl">VA Box (Add-on Appliance)</div>
    <div class="va-feat-grid">
      <div class="va-feat-card" data-vaf="dv1304a">
        <span class="vfc-badge box-b">BOX</span>
        <div class="vfc-icon">📦</div>
        <div class="vfc-name">DV-1304A</div>
        <div class="vfc-tier">EdgeAI add-on · 4 Streams</div>
      </div>
      <div class="va-feat-card" data-vaf="dv1304">
        <span class="vfc-badge box-b">BOX</span>
        <div class="vfc-icon">📊</div>
        <div class="vfc-name">DV-1304</div>
        <div class="vfc-tier">BI Analytics · 4 Streams</div>
      </div>
      <div class="va-feat-card" style="grid-column:1/-1" data-vaf="dv3200b">
        <span class="vfc-badge box-b">SVR</span>
        <div class="vfc-icon">🖥️</div>
        <div class="vfc-name">DV-3200-B (Server VA)</div>
        <div class="vfc-tier">Standard cameras only · IDLA Server</div>
      </div>
    </div>
  </aside>
  <main class="va-right">
    <div class="va-intro" id="vaIntro">
      <div class="va-intro-icon">🔍</div>
      <h2>Video Analytics Selector</h2>
      <p>Select a VA feature on the left to see compatible cameras, NVRs, and appliance requirements.</p>
    </div>
    <div class="gone" id="vaResults"></div>
  </main>
</div>
</div>

<!-- SETTINGS PANEL -->
<div class="settings-ov" id="settingsOv">
  <div class="settings-panel" id="settingsPanel">
    <div class="set-hdr">
      <h2>⚙ Settings</h2>
      <button class="set-close" onclick="closeSettings()">✕</button>
    </div>
    <div class="set-tabs">
      <button class="set-tab on" onclick="setTab('vis')">Model Visibility</button>
      <button class="set-tab"    onclick="setTab('cat')">Category Assignment</button>
    </div>
    <div class="set-content on" id="setVis"></div>
    <div class="set-content"    id="setCat"></div>
    <button class="set-save-btn" onclick="saveSettings()">Save &amp; Apply</button>
  </div>
</div>

<script>
const CAMERAS = {cameras_json};
{recorders_js}
{VQS_JS}

// ── SETTINGS STATE ──
let hiddenModels = new Set();
let customCats   = {{}};
function getVisibleCameras() {{ return CAMERAS.filter(c=>!hiddenModels.has(c.model)); }}
function getCameraCategory(c) {{ return customCats[c.model] || c.category; }}

// ── THEME ──
function setTheme(t){{
  document.documentElement.dataset.theme=t;
  document.getElementById('btnL').className='th-btn'+(t==='light'?' on':'');
  document.getElementById('btnD').className='th-btn'+(t==='dark'?' on':'');
  try{{localStorage.setItem('idis_t',t);}}catch(e){{}}
}}
try{{const s=localStorage.getItem('idis_t');if(s)setTheme(s);}}catch(e){{}}

// ── SCREEN SWITCH ──
function goScreen(s){{
  ['cam','vms','rec','va'].forEach(x=>{{
    const cap=x.charAt(0).toUpperCase()+x.slice(1);
    document.getElementById('scr'+cap).className='screen'+(s===x?' on':'');
    document.getElementById('nav'+cap).className='nav-btn'+(s===x?' nav-on':'');
  }});
  if(s==='vms') vRenderQ();
}}

// ── HELPERS ──
function esc(s){{const d=document.createElement('div');d.textContent=s;return d.innerHTML;}}

// ── CAMERA FILTER STATE ──
let aCats=new Set(),aLens=new Set(),aFls=new Set(),aRes=new Set(),aAn=new Set(),aFeat=new Set();
let aSt=new Set(['출시완료']),aProto=new Set(),aOnvifP=new Set(),cmpList=[];

function getMotoGroup(cam){{
  if(cam.category==='PTZ') return 'PTZ';
  const fl=cam.focalLength||'';
  if(fl.startsWith('7 ~')||fl.startsWith('7~')) return 'Extended';
  return 'Normal';
}}

(function(){{
  const cats=[...new Set(getVisibleCameras().map(c=>getCameraCategory(c)))].sort();
  const el=document.getElementById('catFilters');
  cats.forEach(cat=>{{
    const s=document.createElement('span');
    s.className='chip';s.textContent=cat;s.dataset.cat=cat;
    s.onclick=()=>{{togSet(aCats,cat,s);render();}};
    el.appendChild(s);
  }});
}})();

document.querySelectorAll('[data-feat]').forEach(cb=>{{
  cb.onchange=()=>{{if(cb.checked)aFeat.add(cb.dataset.feat);else aFeat.delete(cb.dataset.feat);render();}};
}});
document.querySelectorAll('[data-rfeat]').forEach(cb=>{{
  cb.onchange=()=>{{if(cb.checked)rFeatF.add(cb.dataset.rfeat);else rFeatF.delete(cb.dataset.rfeat);renderRec();}};
}});

function togSet(set,val,el){{
  if(set.has(val)){{set.delete(val);el.classList.remove('on');}}
  else{{set.add(val);el.classList.add('on');}}
  if(set===aProto){{
    document.getElementById('sub-onvif').className='sub-pnl '+(aProto.has('onvif')?'open':'shut');
    if(!aProto.has('onvif')){{aOnvifP.clear();document.querySelectorAll('[data-onvifp]').forEach(c=>c.classList.remove('on'));}}
  }}
  render();
}}
function togStatus(val,el){{
  if(aSt.has(val)){{aSt.delete(val);el.classList.remove('on');}}else{{aSt.add(val);el.classList.add('on');}}
  render();
}}
function toggleLens(lens,el){{
  if(aLens.has(lens)){{
    aLens.delete(lens);el.classList.remove('on');
    document.querySelectorAll('#sub-'+lens+' [data-fl]').forEach(c=>{{aFls.delete(c.dataset.fl);c.classList.remove('on');}});
  }}else{{aLens.add(lens);el.classList.add('on');}}
  document.getElementById('sub-'+lens).className='sub-pnl '+(aLens.has(lens)?'open':'shut');
  render();
}}
function toggleFl(el){{
  const fl=el.dataset.fl;
  if(aFls.has(fl)){{aFls.delete(fl);el.classList.remove('on');}}else{{aFls.add(fl);el.classList.add('on');}}
  render();
}}

function passes(cam){{
  if(hiddenModels.has(cam.model)) return false;
  if(aSt.size&&!aSt.has(cam.status)) return false;
  if(aProto.size){{
    const ok=(aProto.has('directip')&&cam.isDirectIP)||(aProto.has('onvif')&&cam.isONVIF);
    if(!ok) return false;
    if(aProto.has('onvif')&&aOnvifP.size&&![...aOnvifP].some(p=>cam.onvifProfiles&&cam.onvifProfiles.includes(p))) return false;
  }}
  const camCat=getCameraCategory(cam);
  if(aCats.size&&!aCats.has(camCat)) return false;
  if(aLens.size&&!aLens.has(cam.lensTypeTag)) return false;
  if(aFls.size){{
    if(cam.lensTypeTag==='motorized'){{
      const ok=[...aFls].some(fl=>{{
        if(fl==='PTZ') return getCameraCategory(cam)==='PTZ';
        if(fl==='Extended') return getMotoGroup(cam)==='Extended';
        if(fl==='Normal') return getMotoGroup(cam)==='Normal';
        return false;
      }});
      if(!ok) return false;
    }}else{{
      const mySubs=[...aFls].filter(fl=>document.querySelector('#sub-'+cam.lensTypeTag+' [data-fl="'+CSS.escape(fl)+'"]'));
      if(mySubs.length>0&&!mySubs.includes(cam.flSubtag)) return false;
    }}
  }}
  if(aRes.size){{
    const mp=cam.mp;
    if(!((aRes.has('2')&&mp>=2&&mp<4)||(aRes.has('4')&&mp>=4&&mp<5)||(aRes.has('5')&&mp>=5&&mp<8)||(aRes.has('8')&&mp>=8))) return false;
  }}
  if(aAn.size){{
    const t=cam.analyticsTier;
    const ok=(aAn.has('none')&&t==='none')||(aAn.has('edgeai')&&(t==='edgeai'||t==='edgeai_plus'))||(aAn.has('edgeai_plus')&&t==='edgeai_plus')||(aAn.has('lpr')&&cam.isLPR)||(aAn.has('active')&&cam.isActiveDeterrent);
    if(!ok) return false;
  }}
  for(const f of aFeat){{
    if(f==='hasFIPS'){{if(!cam.hasFIPS||!cam.hasUL) return false;}}
    else if(f==='hasVandal'){{if(!cam.hasVandal&&!cam.hasOutdoor) return false;}}
    else{{if(!cam[f]) return false;}}
  }}
  return true;
}}

function render(){{
  const list=CAMERAS.filter(passes);
  document.getElementById('resNum').textContent=list.length+' models';
  const grid=document.getElementById('cardsGrid');
  const empty=document.getElementById('emptySt');
  if(!list.length){{grid.innerHTML='';empty.classList.remove('gone');return;}}
  empty.classList.add('gone');
  grid.innerHTML=list.map(cam=>{{
    const inC=cmpList.includes(cam.model),sm=esc(cam.model),tags=[];
    if(cam.mp>0) tags.push('<span class="tag t-mp">'+(cam.mp>=8?Math.round(cam.mp):cam.mp)+'MP</span>');
    if(cam.hasIR) tags.push('<span class="tag t-ir">IR</span>');
    if(cam.isLPR) tags.push('<span class="tag t-lpr-t">LPR</span>');
    else if(cam.isActiveDeterrent) tags.push('<span class="tag t-act-t">ActiveDet</span>');
    else if(cam.analyticsTier==='edgeai_plus') tags.push('<span class="tag t-aip">AI+</span>');
    else if(cam.analyticsTier==='edgeai') tags.push('<span class="tag t-ai">AI</span>');
    if(cam.hasBuiltinMic) tags.push('<span class="tag t-mic">Mic</span>');
    if(cam.hasUL) tags.push('<span class="tag t-ul">UL</span>');
    if(cam.hasFIPS) tags.push('<span class="tag t-fips">FIPS</span>');
    const eol=cam.status==='단종'?'<span class="eol-badge">EOL</span>':'';
    return '<div class="cam-card'+(inC?' in-cmp':'')+'" onclick="openDtl(\\''+sm+'\\')">'+
      '<div class="card-cmp-btn'+(inC?' in':'')+'" onclick="event.stopPropagation();togCmp(\\''+sm+'\\')">'+
        (inC?'✓':'+')+
      '</div>'+
      '<div class="card-model">'+esc(cam.model)+eol+'</div>'+
      '<div class="card-title">'+esc(cam.title)+'</div>'+
      '<div class="card-tags">'+tags.join('')+'</div>'+
    '</div>';
  }}).join('');
}}

function resetAll(){{
  aCats.clear();aLens.clear();aFls.clear();aRes.clear();aAn.clear();aFeat.clear();
  aProto.clear();aOnvifP.clear();aSt=new Set(['출시완료']);
  document.querySelectorAll('#scrCam .chip.on').forEach(el=>el.classList.remove('on'));
  document.querySelectorAll('[data-feat]').forEach(cb=>cb.checked=false);
  document.querySelectorAll('.st-pill').forEach(p=>{{p.className='st-pill'+(p.dataset.st==='출시완료'?' on':'');}});
  document.getElementById('sub-onvif').className='sub-pnl shut';
  document.getElementById('sub-fixed').className='sub-pnl shut';
  document.getElementById('sub-motorized').className='sub-pnl shut';
  render();
}}

function openDtl(model){{
  const cam=CAMERAS.find(c=>c.model===model);if(!cam)return;
  const inC=cmpList.includes(model),sm=esc(model),ftags=[];
  if(cam.hasIR)ftags.push('IR');if(cam.hasAudio)ftags.push('Two-Way Audio');
  if(cam.hasBuiltinMic)ftags.push('Built-in Mic');if(cam.hasAlarm)ftags.push('Alarm I/O');
  if(cam.hasSD)ftags.push('SD Card');if(cam.hasIDLA)ftags.push('IDLA');
  if(cam.hasVandal)ftags.push('Vandal IK10');if(cam.hasOutdoor)ftags.push('IP67/66');
  if(cam.hasMotorizedZoom)ftags.push('Motorized');if(cam.isDirectIP)ftags.push('DirectIP');
  if(cam.isONVIF)ftags.push('ONVIF');if(cam.isLPR)ftags.push('LPR');
  if(cam.isActiveDeterrent)ftags.push('Active Det');if(cam.hasWDR)ftags.push('WDR');
  if(cam.hasUL)ftags.push('UL Listed');if(cam.hasFIPS)ftags.push('FIPS 140-3');
  document.getElementById('dtlBox').innerHTML=
    '<div class="dtl-hdr"><div class="dtl-title-area"><div class="dtl-model">'+esc(cam.model)+'</div>'+
    '<div class="dtl-title">'+esc(cam.title)+'</div></div>'+
    '<button class="dtl-close" onclick="document.getElementById(\\'dtlOv\\').classList.remove(\\'open\\')">✕</button></div>'+
    '<div class="dtl-grid">'+
    [['Resolution',cam.resolution],['Sensor',cam.imageSensor],['Lens Type',cam.lensType],
     ['Focal Length',cam.focalLength],['Min Illumination',cam.minIllumination],['WDR',cam.wdr],
     ['Compression',cam.compression],['Max Frame Rate',cam.maxFrameRate],
     ['Power',cam.powerSource],['Approval',cam.approval],['Dimensions',cam.dimensions],['Weight',cam.weight]]
    .map(([k,v])=>'<div class="dtl-row"><div class="dtl-key">'+k+'</div><div class="dtl-val">'+esc(v||'-')+'</div></div>').join('')+
    '<div class="dtl-row dtl-full"><div class="dtl-key">Key Features</div><div class="dtl-val">'+esc(cam.keyFeature||'-')+'</div></div>'+
    '<div class="dtl-row dtl-full"><div class="dtl-key">Video Analytics</div><div class="dtl-val">'+esc(cam.videoAnalytics||'-')+'</div></div>'+
    '</div><div class="dtl-tags">'+ftags.map(t=>'<span class="dtl-tag">'+t+'</span>').join('')+'</div>'+
    '<div class="dtl-btns">'+
    '<button class="mbtn mbtn-add'+(inC?' in':'')+'" id="dtlCmpBtn" onclick="togCmpDtl(\\''+sm+'\\')">'+
    (inC?'✓ In Compare':'＋ Add to Compare')+'</button>'+
    '<button class="mbtn" onclick="document.getElementById(\\'dtlOv\\').classList.remove(\\'open\\')">Close</button></div>';
  document.getElementById('dtlOv').classList.add('open');
}}
function togCmp(m){{
  if(cmpList.includes(m))cmpList=cmpList.filter(x=>x!==m);
  else if(cmpList.length<4)cmpList.push(m);
  document.getElementById('cmpCnt').textContent=cmpList.length;render();
}}
function togCmpDtl(m){{
  togCmp(m);const inC=cmpList.includes(m);
  const btn=document.getElementById('dtlCmpBtn');
  if(btn){{btn.className='mbtn mbtn-add'+(inC?' in':'');btn.textContent=inC?'✓ In Compare':'＋ Add to Compare';}}
}}
function openCmpModal(){{
  if(!cmpList.length)return;
  const cams=cmpList.map(m=>CAMERAS.find(c=>c.model===m)).filter(Boolean);
  document.getElementById('cmpSlots').innerHTML=cmpList.map(m=>
    '<div class="cmp-slot full">'+esc(m)+'<span class="cmp-x" onclick="togCmp(\\''+esc(m)+'\\');openCmpModal()">✕</span></div>').join('');
  const fields=[['Resolution','resolution'],['Sensor','imageSensor'],['Lens','lensType'],['FL','focalLength'],
    ['Min Illum','minIllumination'],['WDR','wdr'],['Compression','compression'],['Frame Rate','maxFrameRate'],
    ['Audio I/O','audioInOut'],['Alarm I/O','alarmInOut'],['Edge Storage','edgeStorage'],
    ['Power','powerSource'],['Approval','approval'],['Dimensions','dimensions'],['Weight','weight']];
  document.getElementById('cmpTableWrap').innerHTML='<table class="cmp-table"><thead><tr><th class="row-lbl">Spec</th>'+
    cams.map(c=>'<th>'+esc(c.model)+'</th>').join('')+'</tr></thead><tbody>'+
    fields.map(([l,k])=>'<tr><td class="row-lbl">'+l+'</td>'+cams.map(c=>'<td>'+esc(c[k]||'-')+'</td>').join('')+'</tr>').join('')+
    '</tbody></table>';
  document.getElementById('cmpOv').classList.add('open');
}}

// ── VMS ──
const vAns={{}};
const ISS_DESC="IDIS Solution Suite (ISS) — Enterprise VMS: 3rd-party integration, LPR, server/client architecture, audit logs, scheduled backup, large-scale expansion, advanced analytics.";
const IDC_DESC="IDIS Center — Streamlined VMS for small-to-medium deployments. No server required, easy setup, up to 2 simultaneous playback users, video wall (4 monitors) at no extra cost.";
function vCalc(){{
  let iss=0,idc=0;
  VQS.forEach(q=>{{
    const a=vAns[q.id];if(a===undefined)return;
    if(q.crit){{if(a==='yes'&&q.yes==='ISS')iss+=10;}}
    else{{if(a==='yes'){{if(q.yes==='ISS')iss++;else if(q.yes==='IDIS Center')idc++;}}
          else if(a==='no'){{if(q.no==='ISS')iss++;else if(q.no==='IDIS Center')idc++;}}}}
  }});
  const res=document.getElementById('vmsResult');
  const answered=Object.keys(vAns).filter(k=>vAns[k]!=='skip').length;
  if(!answered){{res.style.display='none';return;}}
  res.style.display='block';
  if(iss>0){{res.className='vms-result iss show';document.getElementById('vmsRTitle').textContent='Recommended: IDIS Solution Suite (ISS)';document.getElementById('vmsRDesc').textContent=ISS_DESC;}}
  else{{res.className='vms-result idc show';document.getElementById('vmsRTitle').textContent='Recommended: IDIS Center';document.getElementById('vmsRDesc').textContent=IDC_DESC;}}
}}
function vRenderQ(){{
  document.getElementById('vmsQGrid').innerHTML=VQS.map(q=>{{
    const a=vAns[q.id],cls=a==='yes'?'ans-yes':a==='no'?'ans-no':a==='skip'?'ans-skip':'';
    return '<div class="vms-q '+cls+'">'+
      '<div class="vms-q-text">'+esc(q.q)+'</div>'+
      '<div class="vms-q-btns">'+
        '<button class="vms-btn'+(a==='yes'?' active-yes':'')+'" onclick="vAns['+q.id+']=(vAns['+q.id+']===\\'yes\\'?undefined:\\'yes\\');vRenderQ();vCalc()">Yes</button>'+
        '<button class="vms-btn'+(a==='no'?' active-no':'')+'" onclick="vAns['+q.id+']=(vAns['+q.id+']===\\'no\\'?undefined:\\'no\\');vRenderQ();vCalc()">No</button>'+
        '<button class="vms-btn'+(a==='skip'?' active-skip':'')+'" onclick="vAns['+q.id+']=(vAns['+q.id+']===\\'skip\\'?undefined:\\'skip\\');vRenderQ();vCalc()">Skip</button>'+
      '</div></div>';
  }}).join('');
}}
function vReset(){{
  Object.keys(vAns).forEach(k=>delete vAns[k]);
  document.getElementById('vmsResult').style.display='none';vRenderQ();
}}

// ── RECORDER ──
let rSerF=new Set(),rChF=new Set(),rFeatF=new Set(),rStF=new Set(['출시완료']),rCmpList=[];
const SERIES_INFO={{DR1:{{label:'DR-1500',color:'#667'}},DR2:{{label:'DR-2500',color:'#1a5fce'}},
  DR6:{{label:'DR-6500',color:'#c45d00'}},DR8:{{label:'DR-8500',color:'#a04000'}},
  'IR-WS':{{label:'IR-310',color:'#4a8020'}},'IR-SVR':{{label:'IR-1200',color:'#b07d00'}}}};
(function(){{
  const el=document.getElementById('recSerFilters');
  [...new Set(RECORDERS.map(r=>r.series))].forEach(key=>{{
    const info=SERIES_INFO[key]||{{label:key,color:'#667'}};
    const sp=document.createElement('span');sp.className='chip';sp.textContent=info.label;
    sp.style.cssText='border-color:'+info.color+';color:'+info.color;
    sp.onclick=function(){{togRSet(rSerF,key,sp);}};el.appendChild(sp);
  }});
}})();
function togRSet(set,val,el){{
  if(set.has(val)){{set.delete(val);el.classList.remove('on');}}else{{set.add(val);el.classList.add('on');}}renderRec();
}}
function togRStatus(val,el){{
  if(rStF.has(val)){{rStF.delete(val);el.classList.remove('on');}}else{{rStF.add(val);el.classList.add('on');}}renderRec();
}}
function renderRec(){{
  const list=RECORDERS.filter(r=>{{
    if(rStF.size&&!rStF.has(r.status)) return false;
    if(rSerF.size&&!rSerF.has(r.series)) return false;
    if(rChF.size&&!rChF.has(String(r.ch_num))) return false;
    for(const f of rFeatF){{if(!r[f]) return false;}}
    return true;
  }});
  document.getElementById('recNum').textContent=list.length+' models';
  const grid=document.getElementById('recGrid'),empty=document.getElementById('recEmpty');
  if(!list.length){{grid.innerHTML='';empty.classList.remove('gone');return;}}
  empty.classList.add('gone');
  grid.innerHTML=list.map(r=>{{
    const inC=rCmpList.includes(r.model),sm=esc(r.model);
    const info=SERIES_INFO[r.series]||{{label:r.series,color:'#667'}};
    const tags=[];
    if(r.is4K)tags.push('<span class="rec-tag t-4k">4K</span>');
    if(r.hasRAID)tags.push('<span class="rec-tag t-raid">RAID</span>');
    if(r.hasONVIF)tags.push('<span class="rec-tag t-onvif">ONVIF</span>');
    return '<div class="rec-card'+(inC?' in-cmp':'')+'" onclick="openRecDetail(\\''+sm+'\\')">'+
      '<div class="card-cmp-btn'+(inC?' in':'')+'" onclick="event.stopPropagation();togRCmp(\\''+sm+'\\')">'+
        (inC?'✓':'+')+
      '</div>'+
      '<div class="rec-ser-badge" style="background:'+info.color+'20;color:'+info.color+'">'+esc(info.label)+'</div>'+
      '<div class="rec-model">'+esc(r.model)+'</div>'+
      '<div class="rec-title">'+esc(r.title)+'</div>'+
      '<div class="rec-tags">'+tags.join('')+'<span class="rec-tag">'+esc(r.channels)+'</span></div>'+
    '</div>';
  }}).join('');
}}
function openRecDetail(model){{
  const r=RECORDERS.find(x=>x.model===model);if(!r)return;
  const inC=rCmpList.includes(model),sm=esc(model);
  document.getElementById('dtlBox').innerHTML=
    '<div class="dtl-hdr"><div class="dtl-title-area"><div class="dtl-model">'+esc(r.model)+'</div>'+
    '<div class="dtl-title">'+esc(r.title)+'</div></div>'+
    '<button class="dtl-close" onclick="document.getElementById(\\'dtlOv\\').classList.remove(\\'open\\')">✕</button></div>'+
    '<div class="dtl-grid">'+
    [['Channels',r.channels],['Max Bandwidth',r.maxBandwidth],['Rec Bandwidth',r.recBandwidth],
     ['Rec Resolution',r.recRes],['HDD',r.hdd],['Max Capacity',r.totalCapacity],['Video Output',r.videoOut]]
    .map(([k,v])=>'<div class="dtl-row"><div class="dtl-key">'+k+'</div><div class="dtl-val">'+esc(v||'-')+'</div></div>').join('')+
    '</div><div class="dtl-btns">'+
    '<button class="mbtn mbtn-add'+(inC?' in':'')+'" onclick="togRCmpDtl(\\''+sm+'\\')">'+
    (inC?'✓ In Compare':'＋ Add to Compare')+'</button>'+
    '<button class="mbtn" onclick="document.getElementById(\\'dtlOv\\').classList.remove(\\'open\\')">Close</button></div>';
  document.getElementById('dtlOv').classList.add('open');
}}
function togRCmp(m){{
  if(rCmpList.includes(m))rCmpList=rCmpList.filter(x=>x!==m);
  else if(rCmpList.length<4)rCmpList.push(m);
  document.getElementById('rCmpCnt').textContent=rCmpList.length;renderRec();
}}
function togRCmpDtl(m){{
  togRCmp(m);const inC=rCmpList.includes(m);
  const btn=document.querySelector('#dtlBox .mbtn-add');
  if(btn){{btn.className='mbtn mbtn-add'+(inC?' in':'');btn.textContent=inC?'✓ In Compare':'＋ Add to Compare';}}
}}
function openRCmpModal(){{
  if(!rCmpList.length)return;
  const recs=rCmpList.map(m=>RECORDERS.find(r=>r.model===m)).filter(Boolean);
  document.getElementById('rCmpSlots').innerHTML=rCmpList.map(m=>
    '<div class="cmp-slot full">'+esc(m)+'<span class="cmp-x" onclick="togRCmp(\\''+esc(m)+'\\');openRCmpModal()">✕</span></div>').join('');
  const fields=[['Series','series'],['Channels','channels'],['Max BW','maxBandwidth'],['Rec BW','recBandwidth'],
    ['Rec Res','recRes'],['HDD','hdd'],['Capacity','totalCapacity'],['Video Out','videoOut']];
  document.getElementById('rCmpTableWrap').innerHTML='<table class="cmp-table"><thead><tr><th class="row-lbl">Spec</th>'+
    recs.map(r=>'<th>'+esc(r.model)+'</th>').join('')+'</tr></thead><tbody>'+
    fields.map(([l,k])=>'<tr><td class="row-lbl">'+l+'</td>'+recs.map(r=>'<td>'+esc(String(r[k]||'-'))+'</td>').join('')+'</tr>').join('')+
    '</tbody></table>';
  document.getElementById('rCmpOv').classList.add('open');
}}
function resetRec(){{
  rSerF.clear();rChF.clear();rFeatF.clear();rStF=new Set(['출시완료']);
  document.querySelectorAll('#scrRec .chip.on').forEach(el=>el.classList.remove('on'));
  document.querySelectorAll('[data-rfeat]').forEach(cb=>cb.checked=false);
  document.querySelectorAll('[data-rst]').forEach(p=>{{p.className='st-pill'+(p.dataset.rst==='출시완료'?' on':'');}});
  renderRec();
}}

// ── VA ──
const VA_CFG={{
  edgeai:{{icon:'🎯',name:'EdgeAI',desc:'Object Detection, Loitering, Line Crossing, Intrusion, Face Detection.',
    camFilter:c=>(c.analyticsTier==='edgeai'||c.analyticsTier==='edgeai_plus')&&c.status==='출시완료',
    nvrFilter:r=>r.series!=='DR1'&&r.status==='출시완료',panelNvrTitle:'Compatible NVR',boxes:[],
    notes:[{{ok:true,t:'VA results visible only in <b>ISS or IDIS Center</b>'}},{{ok:false,t:'EdgeAI + DV-1304A ❌ (Metadata duplication)'}},{{ok:false,t:'EdgeAI + DV-3200-B ❌ (Metadata duplication)'}}]}},
  edgeai_plus:{{icon:'✨',name:'EdgeAI Plus',desc:'All EdgeAI + Object Attributes, A-Cut, Crowd Detection (IDLA Pro).',
    camFilter:c=>c.analyticsTier==='edgeai_plus'&&c.status==='출시완료',
    nvrFilter:r=>r.series!=='DR1'&&r.status==='출시완료',panelNvrTitle:'Compatible NVR',boxes:[],
    notes:[{{ok:true,t:'VA results visible only in <b>ISS or IDIS Center</b>'}},{{ok:false,t:'EdgeAI Plus + DV-1304A ❌'}},{{ok:false,t:'EdgeAI Plus + DV-3200-B ❌'}}]}},
  lpr:{{icon:'🚗',name:'LPR',desc:'License Plate Recognition. Black/White List, Attribute Events. Management only in ISS.',
    camFilter:c=>c.isLPR===true&&c.status==='출시완료',
    nvrFilter:r=>(r.series==='IR-WS'||r.series==='IR-SVR')&&r.status==='출시완료',
    panelNvrTitle:'Compatible NVR (IR-310D / IR-1200)',boxes:[],
    notes:[{{ok:true,t:'LPR management only in <b>ISS</b>'}},{{ok:true,t:'LPR cameras connect via ONVIF → requires IR-310D or IR-1200'}},{{ok:false,t:'DR series NVRs: not compatible'}}]}},
  active:{{icon:'🚨',name:'Active Deterrence',desc:'Warm Light, Red/Blue Warning Light, audible alarm.',
    camFilter:c=>c.isActiveDeterrent===true&&c.status==='출시완료',
    nvrFilter:r=>(r.series==='IR-WS'||r.series==='IR-SVR')&&r.status==='출시완료',
    panelNvrTitle:'Compatible NVR (IR-310D / IR-1200)',boxes:[],
    notes:[{{ok:true,t:'Active Deterrence cameras connect via ONVIF → requires IR-310D or IR-1200'}},{{ok:false,t:'DR series: not compatible'}}]}},
  dv1304a:{{icon:'📦',name:'DV-1304A',desc:'Adds EdgeAI to standard DirectIP cameras. 4 Streams. Must operate with NVR.',
    camFilter:c=>c.isDirectIP&&c.analyticsTier==='none'&&c.status==='출시완료',
    nvrFilter:r=>r.series.startsWith('DR')&&r.status==='출시완료',
    panelNvrTitle:'Must Have NVR (DR series)',boxes:['dv1304a'],
    notes:[{{ok:true,t:'Standard DirectIP + DV-1304A + NVR + ISS/IDIS Center ✅'}},{{ok:false,t:'EdgeAI/EdgeAI+ cameras ❌ (Metadata duplication)'}},{{ok:false,t:'DV-1304A + DV-3200-B ❌'}}]}},
  dv1304:{{icon:'📊',name:'DV-1304',desc:'BI Analytics: People Count, Occupancy, HeatMap, Queue. 4 Streams. Must operate with NVR.',
    camFilter:c=>c.isDirectIP&&c.status==='출시완료',
    nvrFilter:r=>r.series.startsWith('DR')&&r.status==='출시완료',
    panelNvrTitle:'Must Have NVR (DR series)',boxes:['dv1304'],
    notes:[{{ok:true,t:'DirectIP cameras + DV-1304 + NVR + ISS/IDIS Center ✅'}},{{ok:false,t:'DV-3200-B cannot be used simultaneously'}}]}},
  dv3200b:{{icon:'🖥️',name:'DV-3200-B (Server VA)',desc:'Server-based IDLA for standard DirectIP cameras only.',
    camFilter:c=>c.isDirectIP&&c.analyticsTier==='none'&&c.status==='출시완료',
    nvrFilter:r=>r.series!=='DR1'&&r.status==='출시완료',
    panelNvrTitle:'Compatible NVR',boxes:[],
    notes:[{{ok:true,t:'Standard DirectIP cameras only'}},{{ok:false,t:'EdgeAI / EdgeAI+ cameras ❌'}},{{ok:false,t:'DV-1304A or DV-1304 cannot be used simultaneously'}}]}},
}};
const VA_BOX={{
  dv1304a:{{badge:'EdgeAI Add-on Box',name:'DV-1304A',desc:'Adds EdgeAI analytics to standard DirectIP cameras.',
    specs:[['Analytics','Obj Det, Loitering, Line Crossing, Intrusion'],['Capacity','Max 4 Streams'],['Required','DirectIP NVR + ISS or IDIS Center']],
    compat:[{{ok:true,t:'Standard DirectIP + DV-1304A + NVR + ISS/IDIS Center'}},{{ok:false,t:'EdgeAI/EdgeAI+ cameras (Metadata duplication)'}}]}},
  dv1304:{{badge:'BI Analytics Box',name:'DV-1304',desc:'Business Intelligence analytics.',
    specs:[['Analytics','People Count, Occupancy, Queue, HeatMap'],['Capacity','Max 4 Streams'],['Required','DirectIP NVR + ISS or IDIS Center']],
    compat:[{{ok:true,t:'DirectIP cameras (incl. EdgeAI) + NVR + ISS/IDIS Center'}},{{ok:false,t:'Cannot coexist with DV-3200-B'}}]}},
}};
const SERIES_LBL={{DR1:'DR-1500',DR2:'DR-2500',DR6:'DR-6500',DR8:'DR-8500','IR-WS':'IR-310','IR-SVR':'IR-1200'}};
let vaActive=null;
function vaRender(feat){{
  const cfg=VA_CFG[feat];if(!cfg)return;
  const cams=CAMERAS.filter(cfg.camFilter),nvrs=RECORDERS.filter(cfg.nvrFilter);
  const hasBox=cfg.boxes&&cfg.boxes.length>0;
  function aiTag(c){{
    if(c.analyticsTier==='edgeai_plus')return'<span class="va-cam-tag t-aip">AI+</span>';
    if(c.analyticsTier==='edgeai')return'<span class="va-cam-tag t-ai">AI</span>';
    if(c.isLPR)return'<span class="va-cam-tag t-lpr">LPR</span>';
    if(c.isActiveDeterrent)return'<span class="va-cam-tag t-act">ActiveDet</span>';
    return'';
  }}
  const camRows=cams.length?cams.map(c=>'<div class="va-cam-row"><div class="va-cam-model">'+esc(c.model)+'</div>'+
    '<div class="va-cam-title">'+esc(c.title)+'</div>'+
    '<div class="va-cam-tags"><span class="va-cam-tag t-cat">'+c.category+'</span>'+
    '<span class="va-cam-tag t-mp">'+c.mp+'MP</span>'+aiTag(c)+'</div></div>').join('')
    :'<div style="padding:12px;font-size:12px;color:var(--text3)">No models</div>';
  const nvrRows=nvrs.map(r=>'<div class="va-nvr-row">'+
    '<div class="va-nvr-series">'+(SERIES_LBL[r.series]||r.series)+'</div>'+
    '<div class="va-nvr-model">'+esc(r.model)+'</div>'+
    '<div class="va-nvr-spec">'+esc(r.channels)+' · '+esc(r.maxBandwidth)+'</div>'+
    '<div class="va-nvr-tags">'+(r.is4K?'<span class="va-nvr-tag t-4k">4K</span>':'')+
    (r.hasRAID?'<span class="va-nvr-tag t-raid">RAID</span>':'')+
    (r.hasONVIF?'<span class="va-nvr-tag t-onvif">ONVIF</span>':'')+'</div></div>').join('');
  const boxHtml=hasBox?cfg.boxes.map(bk=>{{
    const b=VA_BOX[bk];if(!b)return'';
    return'<div style="padding:10px"><div class="va-box-card">'+
      '<div class="va-box-badge">'+b.badge+'</div>'+
      '<div class="va-box-name">'+b.name+'</div>'+
      '<div class="va-box-desc">'+b.desc+'</div>'+
      '<div class="va-box-specs">'+b.specs.map(s=>'<div class="va-box-spec"><b>'+s[0]+'</b>'+s[1]+'</div>').join('')+'</div>'+
      '<div class="va-box-compat-title">Compatibility</div>'+
      b.compat.map(c=>'<div class="va-compat-row">'+(c.ok?'✅':'❌')+' '+c.t+'</div>').join('')+
      '</div></div>';
  }}).join(''):'';
  const grid=hasBox?'three':'two';
  document.getElementById('vaResults').innerHTML=
    '<div class="va-feat-hdr"><div class="va-feat-hdr-top">'+
    '<span class="va-feat-hdr-icon">'+cfg.icon+'</span>'+
    '<span class="va-feat-hdr-name">'+cfg.name+'</span></div>'+
    '<div class="va-feat-hdr-desc">'+cfg.desc+'</div></div>'+
    '<div class="va-global-note">ℹ️ <b>Important:</b> All VA results visible only in <b>ISS or IDIS Center</b>. '+
    'NVR Local Display does NOT show VA overlays.</div>'+
    '<div class="va-col-grid '+grid+'">'+
    '<div class="va-panel"><div class="va-panel-hdr"><span class="va-panel-icon">📷</span>'+
    '<span class="va-panel-title">Compatible Cameras</span><span class="va-panel-cnt">'+cams.length+'</span></div>'+
    '<div class="va-panel-body">'+camRows+'</div></div>'+
    '<div class="va-panel"><div class="va-panel-hdr"><span class="va-panel-icon">🖥️</span>'+
    '<span class="va-panel-title">'+esc(cfg.panelNvrTitle)+'</span><span class="va-panel-cnt">'+nvrs.length+'</span></div>'+
    '<div class="va-panel-body">'+nvrRows+'</div></div>'+
    (hasBox?'<div class="va-panel"><div class="va-panel-hdr"><span class="va-panel-icon">📦</span>'+
    '<span class="va-panel-title">VA Box</span></div>'+
    '<div class="va-panel-body" style="padding:0">'+boxHtml+'</div></div>':'')+
    '</div><div class="va-incompat-note">'+
    cfg.notes.map(n=>'<div class="va-incompat-row">'+(n.ok?'ℹ️':'⚠️')+'<span>'+n.t+'</span></div>').join('')+
    '</div>';
  document.getElementById('vaResults').classList.remove('gone');
}}
document.getElementById('scrVa').addEventListener('click',function(e){{
  const card=e.target.closest('.va-feat-card');if(!card)return;
  const feat=card.dataset.vaf;if(!feat)return;
  if(vaActive===feat){{
    vaActive=null;
    document.querySelectorAll('.va-feat-card').forEach(c=>c.classList.remove('active'));
    document.getElementById('vaResults').classList.add('gone');
    document.getElementById('vaIntro').style.display='';return;
  }}
  vaActive=feat;
  document.querySelectorAll('.va-feat-card').forEach(c=>c.classList.remove('active'));
  card.classList.add('active');
  document.getElementById('vaIntro').style.display='none';
  vaRender(feat);
}});

// ── SETTINGS ──
let extraCats=[...new Set(CAMERAS.map(c=>c.category))].sort();
function openSettings(){{renderSettingsVis();renderSettingsCat();document.getElementById('settingsOv').classList.add('open');}}
function closeSettings(){{document.getElementById('settingsOv').classList.remove('open');}}
document.getElementById('settingsOv').addEventListener('click',function(e){{if(e.target===this)closeSettings();}});
function setTab(tab){{
  document.querySelectorAll('.set-tab').forEach((t,i)=>t.classList.toggle('on',['vis','cat'][i]===tab));
  document.getElementById('setVis').classList.toggle('on',tab==='vis');
  document.getElementById('setCat').classList.toggle('on',tab==='cat');
}}
function renderSettingsVis(){{
  document.getElementById('setVis').innerHTML='<div class="set-section-lbl">Toggle models on/off</div>'+
    CAMERAS.map(c=>'<div class="model-vis-row"><span class="model-vis-name">'+esc(c.model)+'</span>'+
    '<span class="model-vis-cat">'+esc(c.category)+'</span>'+
    '<button class="vis-toggle'+(hiddenModels.has(c.model)?'':' on')+'" data-model="'+esc(c.model)+'"></button></div>').join('');
  document.querySelectorAll('#setVis .vis-toggle').forEach(btn=>btn.onclick=function(){{this.classList.toggle('on');}});
}}
function renderSettingsCat(){{
  document.getElementById('setCat').innerHTML='<div class="set-section-lbl">Assign each model to a category</div>'+
    CAMERAS.map(c=>{{
      const cur=customCats[c.model]||c.category;
      return'<div class="cat-assign-row"><span class="cat-assign-name">'+esc(c.model)+'</span>'+
        '<select class="cat-select" data-model="'+esc(c.model)+'">'+
        extraCats.map(cat=>'<option value="'+esc(cat)+'"'+(cat===cur?' selected':'')+'>'+esc(cat)+'</option>').join('')+
        '</select></div>';
    }}).join('')+
    '<div class="new-cat-row"><input class="new-cat-input" id="newCatInput" placeholder="New category name...">'+
    '<button class="new-cat-btn" onclick="addCategory()">+ Add</button></div>';
}}
function addCategory(){{
  const inp=document.getElementById('newCatInput'),val=(inp.value||'').trim();
  if(!val)return;
  if(!extraCats.includes(val)){{extraCats.push(val);extraCats.sort();}}
  inp.value='';renderSettingsCat();
}}
function saveSettings(){{
  hiddenModels.clear();
  document.querySelectorAll('#setVis .vis-toggle').forEach(btn=>{{if(!btn.classList.contains('on'))hiddenModels.add(btn.dataset.model);}});
  Object.keys(customCats).forEach(k=>delete customCats[k]);
  document.querySelectorAll('#setCat .cat-select').forEach(sel=>{{
    const orig=(CAMERAS.find(c=>c.model===sel.dataset.model)||{{}}).category;
    if(sel.value!==orig)customCats[sel.dataset.model]=sel.value;
  }});
  const el=document.getElementById('catFilters');el.innerHTML='';
  const activeCats=new Set(aCats);aCats.clear();
  const cats=[...new Set(CAMERAS.filter(c=>!hiddenModels.has(c.model)).map(c=>getCameraCategory(c)))].sort();
  cats.forEach(cat=>{{
    const s=document.createElement('span');s.className='chip';s.textContent=cat;s.dataset.cat=cat;
    if(activeCats.has(cat)){{s.classList.add('on');aCats.add(cat);}}
    s.onclick=()=>{{togSet(aCats,cat,s);render();}};el.appendChild(s);
  }});
  render();closeSettings();
}}

// ── INIT ──
vRenderQ();
render();
renderRec();
</script>
</body>
</html>"""


def build(cameras_path: str, recorders_path: str, output_dir: str):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Load data
    print(f"Loading {cameras_path} ...")
    with open(cameras_path, encoding='utf-8') as f:
        cameras = json.load(f)
    print(f"  {len(cameras)} cameras")

    print(f"Loading {recorders_path} ...")
    with open(recorders_path, encoding='utf-8') as f:
        recorders = json.load(f)
    print(f"  {len(recorders)} recorders")

    # Build number + timestamp
    build_num = get_next_build_number(output_path)
    build_dt  = datetime.now()
    filename  = f"ipcam_selector_v{build_num}_{build_dt.strftime('%Y%m%d_%H%M%S')}.html"
    out_file  = output_path / filename

    # Generate HTML
    print(f"\nBuilding HTML ...")
    html = build_html(cameras, recorders, build_num, build_dt)

    out_file.write_text(html, encoding='utf-8')
    print(f"Output: {out_file}")
    print(f"Size:   {len(html):,} bytes")
    print(f"\nBuild #{build_num} complete → {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='Build IDIS Product Selector HTML from JSON data'
    )
    parser.add_argument('--cameras',    default='cameras.json',    help='cameras.json path')
    parser.add_argument('--recorders',  default='recorders.json',  help='recorders.json path')
    parser.add_argument('--output-dir', default='output',          help='Output folder (default: output)')
    args = parser.parse_args()

    build(args.cameras, args.recorders, args.output_dir)


if __name__ == '__main__':
    main()
