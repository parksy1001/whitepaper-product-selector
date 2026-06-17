#!/usr/bin/env python3
"""
html_builder_va_only.py
----------------------
Reads cameras.json + recorders.json and builds a dedicated IDIS VA Selector HTML file.

Output: output/idis_va_selector_v{N}_{YYYYMMDD_HHMMSS}.html
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
            f'videoOut:{json.dumps(r.get("videoOut","-"))},'
            f'is4K:{str(r.get("is4K",False)).lower()},'
            f'hasRAID:{str(r.get("hasRAID",False)).lower()},'
            f'hasONVIF:{str(r.get("hasONVIF",True)).lower()}'
            '}'
        )
    recorders_js = 'const RECORDERS=[\n  ' + ',\n  '.join(rec_items) + '\n];'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IDIS VA Selector</title>
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
  --nav-h:52px;--sb:260px;
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
.nav-title{{font-size:15px;font-weight:700;color:var(--text);margin-left:4px}}
.nav-gap{{flex:1}}
.build-info{{font-size:10.5px;color:var(--text3);margin-right:6px;white-space:nowrap}}
.build-info b{{color:var(--accent);font-weight:700}}
.th-btn{{width:30px;height:30px;border:1px solid var(--border);border-radius:6px;cursor:pointer;
  background:var(--surface2);color:var(--text2);display:flex;align-items:center;justify-content:center;
  font-size:13px;transition:all .15s}}
.th-btn.on{{background:var(--accent-bg);color:var(--accent);border-color:var(--accent)}}

/* MAIN WRAPPER */
.va-wrap{{display:flex;min-height:calc(100vh - var(--nav-h))}}
.va-left{{width:var(--sb);flex-shrink:0;background:var(--surface);border-right:1px solid var(--border);
  padding:14px 12px;overflow-y:auto;height:calc(100vh - var(--nav-h));position:sticky;top:var(--nav-h)}}
.va-right{{flex:1;overflow-y:auto;padding:20px 24px}}

/* SIDEBAR COMPONENTS */
.va-sec-lbl{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.7px;color:var(--text3);margin:16px 0 8px}}
.va-sec-lbl:first-child{{margin-top:0}}
.va-feat-grid{{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:6px}}
.va-feat-card{{background:var(--surface2);border:1.5px solid var(--border);border-radius:8px;
  padding:9px 6px 7px;cursor:pointer;transition:all .14s;text-align:center;position:relative;user-select:none}}
.va-feat-card:hover{{border-color:var(--accent);background:var(--accent-bg)}}
.va-feat-card.active{{border-color:var(--accent);background:var(--accent-bg);box-shadow:0 0 0 2px var(--accent)}}

.vfc-badge{{position:absolute;top:4px;right:4px;font-size:8px;font-weight:700;padding:1px 4px;
  border-radius:3px;background:var(--accent);color:#fff;letter-spacing:.3px}}
.vfc-badge.plus{{background:var(--yellow)}}
.vfc-badge.box-b{{background:var(--orange)}}
.vfc-badge.svr-b{{background:var(--text)}}
.vfc-icon{{font-size:18px;line-height:1;margin-bottom:4px}}
.vfc-name{{font-size:11px;font-weight:700;color:var(--text);line-height:1.2;margin-bottom:2px}}
.va-feat-card.active .vfc-name{{color:var(--accent)}}
.vfc-tier{{font-size:9px;color:var(--text3);line-height:1.3}}

/* CHECKBOX FILTERS */
.ck-row{{display:flex;flex-direction:column;gap:4px;margin-top:2px}}
.ck-item{{display:flex;align-items:center;gap:6px;cursor:pointer;padding:3px 0}}
.ck-item input{{display:none}}
.ck-box{{width:14px;height:14px;border:1.5px solid var(--border2);border-radius:3px;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;transition:all .12s}}
.ck-item input:checked+.ck-box{{background:var(--accent);border-color:var(--accent)}}
.ck-item input:checked+.ck-box::after{{content:"✓";color:#fff;font-size:9px;font-weight:700}}
.ck-lbl{{font-size:12px;color:var(--text2)}}
.ck-item:hover .ck-box{{border-color:var(--accent)}}

.rst-btn{{margin-top:14px;width:100%;padding:8px;border:1px solid var(--border);border-radius:6px;
  background:var(--surface2);cursor:pointer;font-size:12px;color:var(--text2);font-weight:500;transition:all .12s}}
.rst-btn:hover{{border-color:var(--red);color:var(--red);background:var(--red-bg)}}

/* CONTENT PANELS */
.va-intro{{text-align:center;padding:80px 20px;color:var(--text2)}}
.va-intro-icon{{font-size:48px;margin-bottom:12px}}
.va-intro h2{{font-size:18px;font-weight:600;color:var(--text);margin-bottom:8px}}
.va-intro p{{font-size:13px;line-height:1.7;max-width:380px;margin:0 auto}}

.va-feat-hdr{{margin-bottom:16px}}
.va-feat-hdr-top{{display:flex;align-items:center;gap:8px;margin-bottom:4px}}
.va-feat-hdr-icon{{font-size:24px}}
.va-feat-hdr-name{{font-size:18px;font-weight:700;color:var(--text)}}
.va-feat-hdr-desc{{font-size:13px;color:var(--text2);line-height:1.55}}

.va-global-note{{background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--accent);
  border-radius:8px;padding:10px 14px;font-size:12px;color:var(--text2);margin-bottom:16px;line-height:1.6}}
.va-global-note b{{color:var(--text)}}

.va-col-grid{{display:grid;gap:14px;margin-bottom:14px}}
.va-col-grid.two{{grid-template-columns:1fr 1fr}}
.va-col-grid.three{{grid-template-columns:1fr 1fr 1fr}}

.va-panel{{background:var(--surface);border:1px solid var(--border);border-radius:10px;overflow:hidden}}
.va-panel-hdr{{display:flex;align-items:center;gap:7px;padding:10px 14px;background:var(--surface2);border-bottom:1px solid var(--border)}}
.va-panel-icon{{font-size:14px}}
.va-panel-title{{font-size:12.5px;font-weight:700;color:var(--text);flex:1}}
.va-panel-cnt{{font-size:10.5px;font-weight:700;color:var(--accent);background:var(--accent-bg);padding:2px 8px;border-radius:10px}}
.va-panel-body{{padding:8px;display:flex;flex-direction:column;gap:6px;max-height:550px;overflow-y:auto}}

/* MATCHED ROWS */
.va-cam-row, .va-nvr-row{{background:var(--surface2);border:1px solid var(--border);border-radius:6px;padding:8px 10px}}
.va-cam-model, .va-nvr-model{{font-size:12px;font-weight:700;color:var(--text);margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.va-cam-title{{font-size:11px;color:var(--text2);margin-bottom:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.va-nvr-spec{{font-size:11px;color:var(--text2);margin-bottom:4px}}
.va-nvr-series{{font-size:9.5px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--text3);margin-bottom:2px}}

.va-cam-tags, .va-nvr-tags{{display:flex;flex-wrap:wrap;gap:3px}}
.va-cam-tag, .va-nvr-tag{{font-size:9px;font-weight:600;padding:1px 5px;border-radius:3px}}

.t-cat, .t-mp{{background:var(--surface3);color:var(--text2)}}
.t-ai{{background:var(--accent-bg);color:var(--accent)}}
.t-aip{{background:var(--yellow-bg);color:var(--yellow)}}
.t-lpr{{background:var(--red-bg);color:var(--red)}}
.t-act{{background:var(--red-bg);color:var(--red)}}
.t-4k{{background:var(--accent-bg);color:var(--accent)}}
.t-raid{{background:var(--yellow-bg);color:var(--yellow)}}
.t-onvif{{background:var(--green-bg);color:var(--green)}}

/* APPLIANCE BOX CARD */
.va-box-card{{background:linear-gradient(135deg,var(--surface2),var(--surface3));border:1.5px solid var(--border2);border-radius:8px;padding:12px 14px;margin:8px}}
.va-box-badge{{display:inline-block;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--orange);background:var(--orange-bg);padding:2px 6px;border-radius:3px;margin-bottom:6px}}
.va-box-name{{font-size:13.5px;font-weight:700;color:var(--text);margin-bottom:4px}}
.va-box-desc{{font-size:11.5px;color:var(--text2);line-height:1.5;margin-bottom:8px}}
.va-box-specs{{display:flex;flex-direction:column;gap:4px;margin-bottom:8px}}
.va-box-spec{{font-size:11px;color:var(--text2);display:flex;gap:6px}}
.va-box-spec b{{color:var(--text);min-width:85px;flex-shrink:0}}
.va-box-compat-title{{font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--text3);margin-bottom:4px}}
.va-compat-row{{font-size:11px;display:flex;gap:4px;align-items:flex-start;margin-bottom:3px;line-height:1.4;color:var(--text2)}}

.va-incompat-note{{background:var(--yellow-bg);border:1px solid var(--yellow);border-radius:7px;padding:10px 14px;font-size:12px;color:var(--text2);margin-top:14px;line-height:1.6}}
.va-incompat-row{{display:flex;gap:6px;align-items:flex-start;margin-bottom:4px}}
.va-incompat-row:last-child{{margin-bottom:0}}
.gone{{display:none!important}}
</style>
</head>
<body>

<nav class="nav">
  <span class="nav-title">IDIS Video Analytics Selector</span>
  <div class="nav-gap"></div>
  <span class="build-info">Build <b>#{build_num}</b> &nbsp;{build_label}</span>
  <button class="th-btn on" id="btnL" onclick="setTheme('light')" title="Light">☀</button>
  <button class="th-btn" id="btnD" onclick="setTheme('dark')" title="Dark">🌙</button>
</nav>

<div class="va-wrap">
  <!-- SIDEBAR FILTERS -->
  <aside class="va-left">
    <div class="va-sec-lbl">Edge AI (Camera Built-in)</div>
    <div class="va-feat-grid">
      <div class="va-feat-card" data-vaf="edgeai">
        <span class="vfc-badge">AI</span>
        <div class="vfc-icon">🎯</div>
        <div class="vfc-name">EdgeAI</div>
        <div class="vfc-tier">IDLA</div>
      </div>
      <div class="va-feat-card" data-vaf="edgeai_plus">
        <span class="vfc-badge plus">AI+</span>
        <div class="vfc-icon">✨</div>
        <div class="vfc-name">EdgeAI Plus</div>
        <div class="vfc-tier">A-cut · IDLA PRO</div>
      </div>
    </div>

    <div class="va-sec-lbl">Camera Built-in VA Features</div>
    <div class="ck-row">
      <label class="ck-item"><input type="checkbox" data-vsel="A-Cut"><span class="ck-box"></span><span class="ck-lbl">A-Cut (Attributes)</span></label>
      <label class="ck-item"><input type="checkbox" data-vsel="Object Detection"><span class="ck-box"></span><span class="ck-lbl">Object Detection</span></label>
      <label class="ck-item"><input type="checkbox" data-vsel="Intrusion"><span class="ck-box"></span><span class="ck-lbl">Intrusion</span></label>
      <label class="ck-item"><input type="checkbox" data-vsel="Loitering"><span class="ck-box"></span><span class="ck-lbl">Loitering</span></label>
      <label class="ck-item"><input type="checkbox" data-vsel="Line Crossing"><span class="ck-box"></span><span class="ck-lbl">Line Crossing</span></label>
      <label class="ck-item"><input type="checkbox" data-vsel="Face Detection"><span class="ck-box"></span><span class="ck-lbl">Face Detection</span></label>
      <label class="ck-item"><input type="checkbox" data-vsel="Crowd Detection"><span class="ck-box"></span><span class="ck-lbl">Crowd Detection</span></label>
      <label class="ck-item"><input type="checkbox" data-vsel="Abandoned Object Detection"><span class="ck-box"></span><span class="ck-lbl">Abandoned Object</span></label>
      <label class="ck-item"><input type="checkbox" data-vsel="Removed Object Detection"><span class="ck-box"></span><span class="ck-lbl">Removed Object</span></label>
      <label class="ck-item"><input type="checkbox" data-vsel="Fall Detection"><span class="ck-box"></span><span class="ck-lbl">Fall Detection</span></label>
    </div>
    
    <button class="rst-btn" onclick="resetVaFeatureSelector()">↺ Reset Features</button>

    <div class="va-sec-lbl">VA Box (Add-on Appliance)</div>
    <div class="va-feat-grid">
      <div class="va-feat-card" data-vaf="dv1304a">
        <span class="vfc-badge box-b">BOX</span>
        <div class="vfc-icon">📦</div>
        <div class="vfc-name">DV-1304-A</div>
        <div class="vfc-tier">EdgeAI · 4 Streams</div>
      </div>
      <div class="va-feat-card" data-vaf="dv1304">
        <span class="vfc-badge box-b">BOX</span>
        <div class="vfc-icon">📊</div>
        <div class="vfc-name">DV-1304</div>
        <div class="vfc-tier">BI · 4 Streams</div>
      </div>
      <div class="va-feat-card" style="grid-column:1/-1" data-vaf="dv3200b">
        <span class="vfc-badge svr-b">SVR</span>
        <div class="vfc-icon">🖥️</div>
        <div class="vfc-name">DV-3200-B (Server)</div>
        <div class="vfc-tier">Standard Cam · IDLA Server</div>
      </div>
    </div>
  </aside>

  <!-- DYNAMIC DISPLAY MAIN AREA -->
  <main class="va-right">
    <div class="va-intro" id="vaIntro">
      <div class="va-intro-icon">🔍</div>
      <h2>Video Analytics Selector</h2>
      <p>Select an Edge AI type, distinct feature checkboxes, or an add-on VA Box on the left to instantly query matching hardware combinations.</p>
    </div>
    <div class="gone" id="vaResults"></div>
  </main>
</div>

<script>
const CAMERAS = {cameras_json};
{recorders_js}

let vaActive = null;
let vaSelectedFeatures = new Set();

// ── THEME CONTROL ──
function setTheme(t){{
  document.documentElement.dataset.theme=t;
  document.getElementById('btnL').className='th-btn'+(t==='light'?' on':'');
  document.getElementById('btnD').className='th-btn'+(t==='dark'?' on':'');
  try{{localStorage.setItem('idis_va_t',t);}}catch(e){{}}
}}
try{{const s=localStorage.getItem('idis_va_t');if(s)setTheme(s);}}catch(e){{}}

function esc(s){{const d=document.createElement('div');d.textContent=s;return d.innerHTML;}}

// ── VA SPECIFIC CONFIG DATA ──
const VA_CFG={{
  edgeai:{{icon:'🎯',name:'EdgeAI',desc:'Object Detection, Loitering, Line Crossing, Intrusion, Face Detection.',
    camFilter:c=>(c.analyticsTier==='edgeai'||c.analyticsTier==='edgeai_plus')&&c.status==='출시완료',
    nvrFilter:r=>r.status==='출시완료' && !['DR1','IR-WS'].includes(r.series),panelNvrTitle:'Compatible NVR',boxes:[],
    notes:[{{ok:true,t:'VA results visible only in <b>ISS or IDIS Center</b>'}},{{ok:false,t:'EdgeAI + DV-1304-A ❌ (Metadata duplication)'}},{{ok:false,t:'EdgeAI + DV-3200-B ❌ (Metadata duplication)'}}]}},
  edgeai_plus:{{icon:'✨',name:'EdgeAI Plus',desc:'All EdgeAI + Object Attributes, A-Cut, Crowd Detection (IDLA Pro).',
    camFilter:c=>c.analyticsTier==='edgeai_plus'&&c.status==='출시완료',
    nvrFilter:r=>r.status==='출시완료' && !['DR1','IR-WS'].includes(r.series),panelNvrTitle:'Compatible NVR',boxes:[],
    notes:[{{ok:true,t:'VA results visible only in <b>ISS or IDIS Center</b>'}},{{ok:false,t:'EdgeAI Plus + DV-1304-A ❌'}},{{ok:false,t:'EdgeAI Plus + DV-3200-B ❌'}}]}},
  dv1304a:{{icon:'📦',name:'DV-1304-A',desc:'Adds EdgeAI to standard DirectIP cameras. 4 Streams. Must operate with NVR.',
    camFilter:c=>c.isDirectIP&&c.analyticsTier==='none'&&c.status==='출시완료',
    nvrFilter:r=>r.status==='출시완료' && !['DR1','IR-WS','IR-SVR'].includes(r.series),
    panelNvrTitle:'Must Have NVR (DR series)',boxes:['dv1304a'],
    notes:[]}},
  dv1304:{{icon:'📊',name:'DV-1304',desc:'BI Analytics: People Counting, Occupancy, HeatMap, Queue Management. 4 Streams. Must operate with NVR.',
    camFilter:c=>c.isDirectIP&&c.status==='출시완료',
    nvrFilter:r=>r.status==='출시완료' && !['DR1','IR-WS','IR-SVR'].includes(r.series),
    panelNvrTitle:'Must Have NVR (DR series)',boxes:['dv1304'],
    notes:[]}},
  dv3200b:{{icon:'🖥️',name:'DV-3200-B (Server VA)',desc:'Server-based IDLA appliance for IDIS Solution Suite.',
    camFilter:c=>c.isDirectIP&&c.analyticsTier==='none'&&c.status==='출시완료',
    nvrFilter:r=>r.status==='출시완료' && !['DR1','DR2','DR6','DR8','IR-WS'].includes(r.series),
    panelNvrTitle:'Compatible NVR',boxes:['dv3200b'],
    notes:[]}}
}};

const VA_BOX={{
  dv1304a:{{badge:'EdgeAI Box',name:'DV-1304-A',desc:'Adds EdgeAI analytics to standard DirectIP cameras.',
    specs:[['Analytics','Object Detection, Loitering, Line Crossing, Intrusion, Face Detection'],['Capacity','Max 4 Streams'],['Required','DirectIP NVR + ISS or IDIS Center']],
    compat:[{{ok:true,t:'Standard DirectIP + DV-1304-A + NVR + ISS/IDIS Center'}},{{ok:false,t:'EdgeAI/EdgeAI+ cameras (Metadata duplication)'}}]}},
  dv1304:{{badge:'BI Analytics Box',name:'DV-1304',desc:'Business Intelligence analytics.',
    specs:[['Analytics','People Counting, Occupancy, Queue Management, HeatMap'],['Capacity','Max 4 Streams'],['Required','DirectIP NVR + ISS or IDIS Center']],
    compat:[{{ok:true,t:'DirectIP cameras (incl. EdgeAI/EdgeAI Plus) + NVR + ISS/IDIS Center'}},{{ok:false,t:'Cannot coexist with DV-3200-B'}}]}},
  dv3200b:{{badge:'Server VA',name:'DV-3200-B',desc:'Server-based IDLA appliance for IDIS Solution Suite.',
    specs:[['Included Analytics','Intrusion, Loitering, Line Crossing, PTZ Auto Tracking'],['Optional Analytics','Face Detection, Abandoned Object Detection, Fall Detection, <br>Violence Detection, Fire Detection, Explosion Detection, <br>Crowd Detection,  Privacy Masking, Rockfall Detection, <br>Fisheye Camera Object Detection, Fisheye PI Tracking '],['Requirement','Add-on Service installation is required when using an NVR or Edge AI IP camera, or when enabling optional Analytics features. <br>Please contact your sales representative.'],['Client','ISS Client for VA result display/playback']],
    compat:[{{ok:true,t:'Standard IP cameras + ISS + ISS Client'}},{{ok:false,t:'EdgeAI/EdgeAI Plus cameras require Add-on Service'}},{{ok:false,t:'NVRs/DVRs require Add-on Service'}}]}},
}};

const SERIES_LBL={{DR1:'DR-1500',DR2:'DR-2500',DR6:'DR-6500',DR8:'DR-8500',IR:'IR-SVR'}};

// ── CORE LOGIC FOR CHECKBOX SELECTION ──
function normVaFeature(s){{
  return String(s || '').toLowerCase().replace(/[-_\s]+/g, '').trim();
}}

function camHasVaFeature(cam, feature){{
  const features = (cam.analyticsFeatures || []).map(normVaFeature);
  return features.includes(normVaFeature(feature));
}}

document.querySelectorAll('[data-vsel]').forEach(cb=>{{
  cb.onchange = () => {{
    if(cb.checked) vaSelectedFeatures.add(cb.dataset.vsel);
    else vaSelectedFeatures.delete(cb.dataset.vsel);

    // Turn off active card state if a distinct checkbox is touched
    document.querySelectorAll('.va-feat-card.active').forEach(c=>c.classList.remove('active'));
    vaActive = null;

    renderVaFeatureSelector();
  }};
}});

function resetVaFeatureSelector(){{
  vaSelectedFeatures.clear();
  vaActive = null;
  document.querySelectorAll('[data-vsel]').forEach(cb=>cb.checked=false);
  document.querySelectorAll('.va-feat-card.active').forEach(c=>c.classList.remove('active'));

  document.getElementById('vaIntro').classList.remove('gone');
  document.getElementById('vaResults').classList.add('gone');
  document.getElementById('vaResults').innerHTML = '';
}}

function renderVaFeatureSelector(){{
  const selected = [...vaSelectedFeatures];
  if(!selected.length){{
    resetVaFeatureSelector();
    return;
  }}

  const cams = CAMERAS.filter(c =>
    c.status === '출시완료' && selected.every(feature => camHasVaFeature(c, feature))
  );
  const nvrs = RECORDERS.filter(VA_CFG.edgeai.nvrFilter);

  const camRows = cams.length ? cams.map(c => {{
    const featureTags = (c.analyticsFeatures || []).map(f => `<span class="va-cam-tag t-ai">${{esc(f)}}</span>`).join('');
    return `<div class="va-cam-row">
      <div class="va-cam-model">${{esc(c.model)}}</div>
      <div class="va-cam-title">${{esc(c.title || '-')}}</div>
      <div class="va-cam-tags">
        <span class="va-cam-tag t-cat">${{esc(c.category || '-')}}</span>
        <span class="va-cam-tag t-mp">${{esc(String(c.mp || '-'))}}MP</span>
        ${{featureTags}}
      </div>
    </div>`;
  }}).join('') : '<div style="padding:12px;font-size:12px;color:var(--text3)">No cameras match all selected features.</div>';
  
  const nvrRows = nvrs.map(r => `
    <div class="va-nvr-row">
      <div class="va-nvr-series">${{esc(r.series || '-')}}</div>
      <div class="va-nvr-model">${{esc(r.model)}}</div>
      <div class="va-nvr-spec">${{esc(r.channels)}}ch · ${{esc(r.recBandwidth || '-')}} · ${{esc(r.recRes || '-')}}</div>
      <div class="va-nvr-tags">
        ${{r.is4K?'<span class="va-nvr-tag t-4k">4K</span>':''}}
        ${{r.hasRAID?'<span class="va-nvr-tag t-raid">RAID</span>':''}}
        ${{r.hasONVIF?'<span class="va-nvr-tag t-onvif">ONVIF</span>':''}}
      </div>
    </div>`).join('');

  document.getElementById('vaIntro').classList.add('gone');
  document.getElementById('vaResults').innerHTML = `
    <div class="va-feat-hdr">
      <div class="va-feat-hdr-top">
        <span class="va-feat-hdr-icon">🔍</span>
        <span class="va-feat-hdr-name">Camera Built-in VA Features</span>
      </div>
      <div class="va-feat-hdr-desc">Selected Constraints: <b>${{esc(selected.join(', '))}}</b></div>
    </div>
    <div class="va-global-note">ℹ️ <b>Important:</b> All VA results visible only in <b>ISS or IDIS Center</b>. NVR Local Display does NOT show VA overlays.</div>
    <div class="va-col-grid two">
      <div class="va-panel">
        <div class="va-panel-hdr">
          <span class="va-panel-icon">📷</span>
          <span class="va-panel-title">Matched Cameras</span>
          <span class="va-panel-cnt">${{cams.length}}</span>
        </div>
        <div class="va-panel-body">${{camRows}}</div>
      </div>
      <div class="va-panel">
        <div class="va-panel-hdr">
          <span class="va-panel-icon">🖥️</span>
          <span class="va-panel-title">Compatible NVRs</span>
          <span class="va-panel-cnt">${{nvrs.length}}</span>
        </div>
        <div class="va-panel-body">${{nvrRows}}</div>
      </div>
    </div>`;
  document.getElementById('vaResults').classList.remove('gone');
}}

// ── CORE LOGIC FOR PRESET CARD CLICK ──
function vaRenderPreset(feat){{
  const cfg=VA_CFG[feat]; if(!cfg)return;
  const cams=CAMERAS.filter(cfg.camFilter), nvrs=RECORDERS.filter(cfg.nvrFilter);
  const hasBox=cfg.boxes && cfg.boxes.length>0;

  const globalNote = feat === 'dv3200b'
    ? 'ℹ️ <b>Important:</b> The ISS IDLA Service and Admin Service must be installed on separate PCs.'
    : 'ℹ️ <b>Important:</b> All VA results visible only in <b>ISS or IDIS Center</b>. NVR Local Display does NOT show VA overlays.';

  const camRows = cams.length ? cams.map(c=>{{
    let aiTagStr = '';
    if(c.analyticsTier==='edgeai_plus') aiTagStr='<span class="va-cam-tag t-aip">AI+</span>';
    else if(c.analyticsTier==='edgeai') aiTagStr='<span class="va-cam-tag t-ai">AI</span>';
    else if(c.isLPR) aiTagStr='<span class="va-cam-tag t-lpr">LPR</span>';
    else if(c.isActiveDeterrent) aiTagStr='<span class="va-cam-tag t-act">ActiveDet</span>';

    return `<div class="va-cam-row">
      <div class="va-cam-model">${{esc(c.model)}}</div>
      <div class="va-cam-title">${{esc(c.title || '-')}}</div>
      <div class="va-cam-tags">
        <span class="va-cam-tag t-cat">${{esc(c.category)}}</span>
        <span class="va-cam-tag t-mp">${{esc(String(c.mp))}}MP</span>
        ${{aiTagStr}}
      </div>
    </div>`;
  }}).join('') : '<div style="padding:12px;font-size:12px;color:var(--text3)">No standard models applicable.</div>';

  const nvrRows = nvrs.map(r=>`<div class="va-nvr-row">
    <div class="va-nvr-series">${{esc(SERIES_LBL[r.series]||r.series)}}</div>
    <div class="va-nvr-model">${{esc(r.model)}}</div>
    <div class="va-nvr-spec">${{esc(r.channels)}}ch · ${{esc(r.maxBandwidth || '-')}}</div>
    <div class="va-nvr-tags">
      ${{r.is4K?'<span class="va-nvr-tag t-4k">4K</span>':''}}
      ${{r.hasRAID?'<span class="va-nvr-tag t-raid">RAID</span>':''}}
      ${{r.hasONVIF?'<span class="va-nvr-tag t-onvif">ONVIF</span>':''}}
    </div>
  </div>`).join('');

  let boxHtml = '';
  if(hasBox){{
    cfg.boxes.forEach(bk=>{{
      const b=VA_BOX[bk]; if(!b) return;
      boxHtml += `<div style="padding:2px"><div class="va-box-card">
        <div class="va-box-badge">${{esc(b.badge)}}</div>
        <div class="va-box-name">${{esc(b.name)}}</div>
        <div class="va-box-desc">${{esc(b.desc)}}</div>
        <div class="va-box-specs">
          ${{b.specs.map(s=>`<div class="va-box-spec"><b>${{esc(s[0])}}</b>${{s[1]}}</div>`).join('')}}
        </div>
        <div class="va-box-compat-title">Architecture Topology</div>
        ${{b.compat.map(c=>`<div class="va-compat-row">${{c.ok?'✅':'❌'}} ${{esc(c.t)}}</div>`).join('')}}
      </div></div>`;
    }});
  }}

  // notes 데이터가 없거나 비어있는 경우 화면 하단 컨테이너 블록을 생성하지 않도록 예외 처리
  const notesHtml = (cfg.notes && cfg.notes.length > 0) 
    ? `<div class="va-incompat-note">
        ${{cfg.notes.map(n=>`<div class="va-incompat-row">${{n.ok?'ℹ️':'⚠️'}}<span>${{n.t}}</span></div>`).join('')}}
       </div>`
    : '';

  const gridClass = hasBox ? 'three' : 'two';
  document.getElementById('vaResults').innerHTML = `
    <div class="va-feat-hdr">
      <div class="va-feat-hdr-top">
        <span class="va-feat-hdr-icon">${{cfg.icon}}</span>
        <span class="va-feat-hdr-name">${{cfg.name}}</span>
      </div>
      <div class="va-feat-hdr-desc">${{cfg.desc}}</div>
    </div>
    <div class="va-global-note">${{globalNote}}</div>
    <div class="va-col-grid ${{gridClass}}">
      <div class="va-panel">
        <div class="va-panel-hdr">
          <span class="va-panel-icon">📷</span>
          <span class="va-panel-title">Target Cameras</span>
          <span class="va-panel-cnt">${{cams.length}}</span>
        </div>
        <div class="va-panel-body">${{camRows}}</div>
      </div>
      <div class="va-panel">
        <div class="va-panel-hdr">
          <span class="va-panel-icon">🖥️</span>
          <span class="va-panel-title">${{esc(cfg.panelNvrTitle)}}</span>
          <span class="va-panel-cnt">${{nvrs.length}}</span>
        </div>
        <div class="va-panel-body">${{nvrRows}}</div>
      </div>
      ${{hasBox ? `<div class="va-panel">
        <div class="va-panel-hdr">
          <span class="va-panel-icon">📦</span>
          <span class="va-panel-title">Appliance Dimension</span>
        </div>
        <div class="va-panel-body" style="padding:0">${{boxHtml}}</div>
      </div>` : ''}}
    </div>
    ${{notesHtml}}`; // 동적으로 가공된 노출 영역 매핑
  document.getElementById('vaResults').classList.remove('gone');
}}

// Click Event Interceptor for the Preset Cards
document.querySelector('.va-left').addEventListener('click', function(e){{
  const card = e.target.closest('.va-feat-card'); if(!card) return;
  const feat = card.dataset.vaf; if(!feat) return;

  // Clear checkbox state when preset cards are triggered
  vaSelectedFeatures.clear();
  document.querySelectorAll('[data-vsel]').forEach(cb=>cb.checked=false);

  if(vaActive === feat){{
    resetVaFeatureSelector();
    return;
  }}

  vaActive = feat;
  document.querySelectorAll('.va-feat-card').forEach(c=>c.classList.remove('active'));
  card.classList.add('active');
  document.getElementById('vaIntro').classList.add('gone');
  vaRenderPreset(feat);
}});
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
    filename  = f"idis_va_selector_v{build_num}_{build_dt.strftime('%Y%m%d_%H%M%S')}.html"
    out_file  = output_path / filename

    # Generate HTML
    print(f"\nBuilding Dedicated VA Selector HTML ...")
    html = build_html(cameras, recorders, build_num, build_dt)

    out_file.write_text(html, encoding='utf-8')
    print(f"Output: {out_file}")
    print(f"Size:   {len(html):,} bytes")
    print(f"\nBuild #{build_num} complete → {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='Build IDIS Dedicated VA Selector HTML from JSON data'
    )
    parser.add_argument('--cameras',    default='cameras.json',    help='cameras.json path')
    parser.add_argument('--recorders',  default='recorders.json',  help='recorders.json path')
    parser.add_argument('--output-dir', default='output',          help='Output folder (default: output)')
    args = parser.parse_args()

    build(args.cameras, args.recorders, args.output_dir)


if __name__ == '__main__':
    main()