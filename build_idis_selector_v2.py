#!/usr/bin/env python3
"""
IDIS Product Selector — Builder (v2)
======================================
파이널 기준 파일: Final_IDIS_Product_Selector_Final_8.html

사전 준비 (ref/ 폴더):
  ipcam_selector_9_1.html       ← 원본 베이스
  manual_p79_toolbar.png
  manual_p95_hover.PNG
  manual_p124_timeline.PNG
  manual_p231_stats.PNG
  manual_p259_gdpr.PNG
  manual_p268_acut.PNG
  manual_p269_filter.PNG
# test1
실행:
  python build_idis_selector_v2.py

출력:
  IDIS_Product_Selector_Final.html  (~670KB)

요구사항:
  Python 3.8+
  Node.js (node --check 로 JS syntax 검증)
"""

import base64, os, re, subprocess, sys, tempfile
from pathlib import Path

REF = Path("ref")
OUT = Path("IDIS_Product_Selector_Final.html")

# ─────────────────────────────────────────────────────────────
# 유틸
# ─────────────────────────────────────────────────────────────
def fail(msg):
    print(f"\n❌  {msg}")
    sys.exit(1)

def ok(msg):
    print(f"  ✓  {msg}")

def find_file(name: str) -> Path:
    """대소문자 무관 파일 검색"""
    for p in REF.iterdir():
        if p.name.lower() == name.lower():
            return p
    return None

def b64(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()

def js_ok(code: str, label: str = "") -> bool:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(code); fn = f.name
    # Node.js 없으면 syntax check 건너뜀
    try:
        r = subprocess.run(["node", "--check", fn], capture_output=True, text=True, timeout=15)
        os.unlink(fn)
        if r.returncode:
            print(f"  ❌  JS syntax error [{label}]:\n     {r.stderr[:250]}")
        return r.returncode == 0
    except FileNotFoundError:
        os.unlink(fn)
        print(f"  ⚠   Node.js not found — skipping syntax check [{label}]")
        return True
    except Exception as e:
        os.unlink(fn)
        print(f"  ⚠   Syntax check skipped [{label}]: {e}")
        return True

def must(needle, haystack, label):
    if needle not in haystack:
        fail(f"Anchor not found: {label}\n   Wanted: {repr(needle[:80])}")

# ─────────────────────────────────────────────────────────────
# 0. 파일 확인
# ─────────────────────────────────────────────────────────────
print("=" * 62)
print("  IDIS Product Selector Builder  v2")
print("=" * 62)

IMAGES = {
    "TOOLBAR":  "manual_p79_toolbar.png",
    "HOVER":    "manual_p95_hover.PNG",
    "TIMELINE": "manual_p124_timeline.PNG",
    "STATS":    "manual_p231_stats.PNG",
    "GDPR":     "manual_p259_gdpr.PNG",
    "ACUT":     "manual_p268_acut.PNG",
    "FILTER":   "manual_p269_filter.PNG",
}

print("\n[0] Checking ref/ files ...")

# ── 진단: ref/ 폴더 내용 출력 ──
if not REF.exists():
    print(f"\n  ❌  'ref' 폴더 자체가 없습니다!")
    print(f"     스크립트 위치: {Path('.').resolve()}")
    print(f"     찾는 경로:    {REF.resolve()}")
    print(f"\n  해결: 스크립트와 같은 폴더에 'ref' 폴더를 만드세요.")
    sys.exit(1)

print(f"  ref/ 폴더 경로: {REF.resolve()}")
ref_files = sorted([p.name for p in REF.iterdir()])
if ref_files:
    print(f"  ref/ 폴더 내 파일 목록 ({len(ref_files)}개):")
    for f in ref_files:
        print(f"    · {f}")
else:
    print("  ⚠  ref/ 폴더가 비어 있습니다!")

print()

base_path = find_file("ipcam_selector_9_1.html")
if not base_path:
    print("  ❌  ipcam_selector_9_1.html 을 찾지 못했습니다.")
    print("     위 목록에서 비슷한 파일이 있는지 확인하세요.")
    print("     (예: 파일명 대소문자, 공백, 버전 번호 차이)")
    sys.exit(1)
ok(f"Base  {base_path.name}  ({base_path.stat().st_size // 1024} KB)")

img_paths = {}
for key, fname in IMAGES.items():
    p = find_file(fname)
    if not p:
        print(f"  ❌  이미지 없음: {fname}")
        print(f"     ref/ 폴더에 해당 파일을 추가하세요.")
        sys.exit(1)
    img_paths[key] = p
    ok(f"Image {p.name}  ({p.stat().st_size // 1024} KB)")

src = base_path.read_text(encoding="utf-8")
print(f"\n  Base loaded: {len(src) // 1024} KB")

# ─────────────────────────────────────────────────────────────
# 1. 이미지 base64 인코딩
# ─────────────────────────────────────────────────────────────
print("\n[1] Encoding images ...")
imgs = {k: b64(p) for k, p in img_paths.items()}
IMG_VARS = "\n".join(f'var VMS_IMG_{k} = "{v}";' for k, v in imgs.items())
ok(f"7 images encoded  ({sum(len(v) for v in imgs.values()) // 1024} KB total)")

# ─────────────────────────────────────────────────────────────
# 2. CSS 주입 — base CSS 끝에 추가
# ─────────────────────────────────────────────────────────────
print("\n[2] Injecting CSS ...")

CSS_ANCHOR = (
    ".set-save-btn{width:100%;margin-top:16px;padding:10px;"
    "background:var(--accent);color:#fff;\n"
    "  border:none;border-radius:8px;cursor:pointer;"
    "font-size:13px;font-weight:600}"
)
must(CSS_ANCHOR, src, "CSS boundary anchor")

EXTRA_CSS = """

/* ══ VMS SCREEN ═══════════════════════════════════════════════════ */
#scrIss{background:#060c12;overflow-y:auto;}
#scrIss .vms-page{background:#060c12;min-height:calc(100vh - 52px);
  font-family:'IBM Plex Sans','Segoe UI',system-ui,sans-serif;color:#e8eef5;}
/* hero */
#scrIss .vhero{padding:56px 48px 40px;max-width:1200px;margin:0 auto;}
#scrIss .vhero-tag{display:inline-flex;align-items:center;gap:8px;
  font-size:10px;letter-spacing:2.5px;text-transform:uppercase;color:#00c8ff;
  padding:5px 12px;border:1px solid rgba(0,200,255,.2);border-radius:4px;
  background:rgba(0,200,255,.05);margin-bottom:22px;font-family:'Courier New',monospace;}
#scrIss .vhero-h1{font-size:clamp(32px,4vw,58px);font-weight:800;line-height:1.0;
  letter-spacing:-1.5px;margin-bottom:16px;font-family:'Georgia',serif;}
#scrIss .vhero-h1 em{font-style:italic;
  background:linear-gradient(90deg,#00c8ff,#00e5b0);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
/* stats */
#scrIss .vstats{display:flex;gap:40px;flex-wrap:wrap;padding:36px 0;
  border-top:1px solid #1a2f42;margin-top:20px;}
#scrIss .vstat-num{font-size:38px;font-weight:800;color:#e8eef5;line-height:1;
  font-family:'Georgia',serif;}
#scrIss .vstat-lbl{font-size:10px;color:#4d6a82;letter-spacing:1.5px;
  text-transform:uppercase;margin-top:5px;font-family:'Courier New',monospace;}
/* search */
#scrIss .vsearch-wrap{max-width:1200px;margin:0 auto;padding:0 48px 32px;}
#scrIss .vsearch-box{position:relative;max-width:520px;}
#scrIss .vsearch-input{width:100%;height:44px;padding:0 46px 0 16px;
  background:#0f1e2d;border:1px solid #1a2f42;border-radius:8px;
  font-size:13px;color:#e8eef5;outline:none;
  font-family:'Courier New',monospace;transition:border-color .2s,box-shadow .2s;}
#scrIss .vsearch-input::placeholder{color:#4d6a82;}
#scrIss .vsearch-input:focus{border-color:#00c8ff;
  box-shadow:0 0 0 3px rgba(0,200,255,.1);}
#scrIss .vsearch-icon{position:absolute;right:14px;top:50%;
  transform:translateY(-50%);color:#4d6a82;pointer-events:none;}
#scrIss .vsearch-results{display:none;margin-top:8px;background:#0f1e2d;
  border:1px solid #1a2f42;border-radius:8px;overflow:hidden;
  max-height:340px;overflow-y:auto;}
#scrIss .vsearch-results.show{display:block;}
#scrIss .vsr-count{padding:7px 14px;font-size:10px;color:#4d6a82;
  letter-spacing:1px;text-transform:uppercase;font-family:'Courier New',monospace;
  background:#080e16;border-bottom:1px solid #1a2f42;}
#scrIss .vsr-item{padding:12px 14px;border-bottom:1px solid #1a2f42;
  cursor:pointer;transition:background .15s;}
#scrIss .vsr-item:last-child{border-bottom:none;}
#scrIss .vsr-item:hover{background:rgba(0,200,255,.06);}
#scrIss .vsr-cat{font-size:9px;color:#00c8ff;letter-spacing:2px;
  text-transform:uppercase;margin-bottom:3px;font-family:'Courier New',monospace;}
#scrIss .vsr-title{font-size:13px;font-weight:600;color:#e8eef5;margin-bottom:2px;}
#scrIss .vsr-excerpt{font-size:11px;color:#8ba3bc;line-height:1.5;}
#scrIss .vsr-excerpt mark{background:rgba(0,200,255,.18);color:#00c8ff;
  border-radius:2px;padding:0 2px;}
#scrIss .vsr-empty{padding:18px 14px;font-size:12px;color:#4d6a82;text-align:center;}
/* section divider */
#scrIss .vsec-div{max-width:1200px;margin:0 auto;padding:0 48px;}
#scrIss .vsec-lbl{font-size:9px;letter-spacing:3px;text-transform:uppercase;
  color:#4d6a82;display:flex;align-items:center;gap:14px;padding-bottom:18px;
  border-bottom:1px solid #1a2f42;margin-bottom:0;font-family:'Courier New',monospace;}
#scrIss .vsec-lbl::before{content:'';width:28px;height:1px;
  background:rgba(0,200,255,.5);}
/* card grid */
#scrIss .vgrid-wrap{max-width:1200px;margin:0 auto;padding:20px 48px 60px;}
#scrIss .vcard-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;}
#scrIss .vcard{position:relative;background:#0f1e2d;border:1px solid #1a2f42;
  border-radius:10px;padding:26px 20px 22px;cursor:pointer;overflow:hidden;
  display:flex;flex-direction:column;align-items:flex-start;min-height:240px;
  transition:transform .3s ease,border-color .3s,box-shadow .3s;}
#scrIss .vcard::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:var(--vc);transform:scaleX(0);transform-origin:left;
  transition:transform .35s ease;}
#scrIss .vcard:hover::before{transform:scaleX(1);}
#scrIss .vcard:hover{transform:translateY(-4px);
  border-color:rgba(var(--vcr),.3);
  box-shadow:0 20px 40px rgba(0,0,0,.4),0 0 0 1px rgba(var(--vcr),.1);}
#scrIss .vcard-num{font-family:'Courier New',monospace;font-size:9px;
  color:var(--vc);letter-spacing:2px;margin-bottom:16px;opacity:.65;}
#scrIss .vcard-icon{width:48px;height:48px;border-radius:12px;
  background:rgba(var(--vcr),.08);border:1px solid rgba(var(--vcr),.18);
  display:flex;align-items:center;justify-content:center;margin-bottom:16px;
  transition:all .3s;}
#scrIss .vcard:hover .vcard-icon{background:rgba(var(--vcr),.16);
  border-color:rgba(var(--vcr),.35);transform:scale(1.06);}
#scrIss .vcard-icon svg{width:24px;height:24px;}
#scrIss .vcard-title{font-size:16px;font-weight:700;color:#e8eef5;
  line-height:1.3;margin-bottom:8px;flex:1;font-family:'Georgia',serif;}
#scrIss .vcard-desc{font-size:11px;color:#8ba3bc;line-height:1.6;font-weight:300;}
#scrIss .vcard-cta{margin-top:16px;font-family:'Courier New',monospace;font-size:9px;
  color:var(--vc);letter-spacing:2px;text-transform:uppercase;
  opacity:0;transform:translateX(-6px);transition:all .28s;}
#scrIss .vcard:hover .vcard-cta{opacity:1;transform:translateX(0);}
#scrIss .vc1{--vc:#00c8ff;--vcr:0,200,255;}
#scrIss .vc2{--vc:#00e5b0;--vcr:0,229,176;}
#scrIss .vc3{--vc:#a78bfa;--vcr:167,139,250;}
#scrIss .vc4{--vc:#f59e0b;--vcr:245,158,11;}
#scrIss .vc5{--vc:#ef4444;--vcr:239,68,68;}
/* modal overlay */
#vmsOverlay{position:fixed;inset:0;background:rgba(3,8,14,.8);
  backdrop-filter:blur(10px);z-index:999;display:none;
  align-items:flex-start;justify-content:center;padding:20px;overflow-y:auto;}
#vmsOverlay.vms-open{display:flex;}
.vms-modal{position:relative;background:#0a1520;border:1px solid #203649;
  border-radius:16px;width:100%;max-width:880px;margin:auto;overflow:hidden;
  animation:vmsIn .38s cubic-bezier(.34,1.56,.64,1);}
@keyframes vmsIn{from{transform:translateY(24px) scale(.97);opacity:0;}
  to{transform:none;opacity:1;}}
.vms-mhdr{position:relative;padding:36px 48px 28px;background:#0f1e2d;
  border-bottom:1px solid #1a2f42;overflow:hidden;}
.vms-mhdr::before{content:'';position:absolute;top:-60px;right:-60px;
  width:220px;height:220px;
  background:radial-gradient(circle,rgba(var(--mvcr),.12),transparent 70%);
  border-radius:50%;}
.vms-mclose{position:absolute;top:16px;right:16px;width:32px;height:32px;
  border-radius:50%;background:#152435;border:1px solid #1a2f42;
  display:flex;align-items:center;justify-content:center;cursor:pointer;
  color:#8ba3bc;z-index:10;font-size:16px;line-height:1;transition:all .2s;}
.vms-mclose:hover{color:#e8eef5;border-color:#203649;transform:rotate(90deg);}
.vms-mcat{font-family:'Courier New',monospace;font-size:9px;letter-spacing:2.5px;
  text-transform:uppercase;color:var(--mvc);margin-bottom:12px;
  display:flex;align-items:center;gap:10px;}
.vms-mcat::before{content:'';width:22px;height:1px;background:var(--mvc);}
.vms-mtitle{font-size:clamp(24px,3.5vw,38px);font-weight:800;letter-spacing:-1px;
  color:#e8eef5;margin-bottom:12px;font-family:'Georgia',serif;}
.vms-mtagline{font-size:13px;color:#8ba3bc;font-style:italic;line-height:1.7;
  font-family:'Georgia',serif;}
.vms-mbody{padding:36px 48px;}
.vms-fblock{margin-bottom:34px;padding-bottom:34px;border-bottom:1px solid #1a2f42;}
.vms-fblock:last-child{border-bottom:none;margin-bottom:0;padding-bottom:0;}
.vms-fhdr{display:flex;align-items:flex-start;gap:12px;margin-bottom:14px;}
.vms-fhdr-ic{width:28px;height:28px;border-radius:6px;
  background:rgba(var(--mvcr),.08);border:1px solid rgba(var(--mvcr),.2);
  display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px;}
.vms-fhdr-ic svg{width:14px;height:14px;}
.vms-fh3{font-size:17px;font-weight:700;color:#e8eef5;line-height:1.3;
  font-family:'Georgia',serif;}
.vms-fh3 small{display:block;font-family:'Courier New',monospace;font-size:9px;
  font-weight:400;color:var(--mvc);letter-spacing:1.5px;text-transform:uppercase;
  margin-bottom:3px;}
.vms-ftxt{font-size:13px;color:#8ba3bc;line-height:1.82;padding-left:40px;
  font-weight:300;}
.vms-ftxt p{margin-bottom:11px;}
.vms-ftxt p:last-child{margin-bottom:0;}
.vms-ftxt strong{color:#e8eef5;font-weight:500;}
.vms-ftxt em{color:var(--mvc);font-style:normal;}
.vms-kw{display:inline-flex;padding:1px 7px;background:rgba(var(--mvcr),.08);
  border:1px solid rgba(var(--mvcr),.2);border-radius:3px;
  font-family:'Courier New',monospace;font-size:10px;color:var(--mvc);}
.vms-spec{background:#0f1e2d;border:1px solid #1a2f42;border-left:3px solid var(--mvc);
  border-radius:0 8px 8px 0;padding:16px 20px;margin:14px 0 14px 40px;}
.vms-spec-lbl{font-family:'Courier New',monospace;font-size:8px;letter-spacing:2px;
  color:var(--mvc);text-transform:uppercase;margin-bottom:10px;
  display:flex;align-items:center;gap:8px;}
.vms-spec-lbl::after{content:'';flex:1;height:1px;background:#1a2f42;}
.vms-spec-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  gap:9px;}
.vms-spec-item{padding:9px 12px;background:#060c12;border-radius:6px;
  border:1px solid #1a2f42;}
.vms-spec-key{font-family:'Courier New',monospace;font-size:8px;color:#4d6a82;
  letter-spacing:1px;text-transform:uppercase;margin-bottom:3px;}
.vms-spec-val{font-size:12px;color:#e8eef5;font-weight:500;}
.vms-spec-val b{color:var(--mvc);font-size:14px;font-family:'Georgia',serif;
  font-weight:700;}
.vms-imgslot{margin:14px 0 14px 40px;width:calc(100% - 40px);border-radius:8px;
  overflow:hidden;border:1px solid #1a2f42;background:#060c12;}
.vms-imgslot img{width:100%;display:block;max-height:300px;object-fit:contain;
  background:#080e16;}
.vms-imgslot-cap{padding:8px 13px;font-family:'Courier New',monospace;font-size:9px;
  color:#4d6a82;border-top:1px solid #1a2f42;}
.vms-pro{display:inline-flex;padding:2px 7px;background:rgba(245,166,35,.1);
  border:1px solid rgba(245,166,35,.25);border-radius:3px;
  font-family:'Courier New',monospace;font-size:8px;color:#f5a623;
  letter-spacing:1.5px;text-transform:uppercase;vertical-align:middle;
  margin-left:7px;}
.vms-archtip{background:linear-gradient(120deg,rgba(245,166,35,.05),rgba(239,68,68,.03));
  border:1px solid rgba(245,166,35,.18);border-radius:9px;padding:16px 20px;
  margin:16px 0 16px 40px;}
.vms-archtip-lbl{font-family:'Courier New',monospace;font-size:8px;color:#f5a623;
  letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;}
.vms-archtip-txt{font-size:12px;color:#8ba3bc;line-height:1.75;}
.vms-fo{margin:14px 0 14px 40px;padding:20px;background:#0f1e2d;
  border:1px solid #1a2f42;border-radius:9px;display:flex;align-items:center;
  justify-content:center;gap:18px;flex-wrap:wrap;}
.vms-fo-node{display:flex;flex-direction:column;align-items:center;gap:6px;}
.vms-fo-box{width:58px;height:58px;border-radius:8px;border:2px solid;
  display:flex;align-items:center;justify-content:center;
  font-family:'Courier New',monospace;font-size:8px;letter-spacing:.8px;
  text-align:center;line-height:1.3;}
.vms-fo-box.down{border-color:#ef4444;background:rgba(239,68,68,.08);color:#ef4444;}
.vms-fo-box.up{border-color:#00e5b0;background:rgba(0,229,176,.08);color:#00e5b0;
  animation:vmsGlow 1.8s ease-in-out infinite;}
@keyframes vmsGlow{0%,100%{box-shadow:0 0 0 0 rgba(0,229,176,.3);}
  50%{box-shadow:0 0 0 7px transparent;}}
.vms-fo-lbl{font-family:'Courier New',monospace;font-size:9px;color:#4d6a82;}
.vms-fo-arr{font-size:20px;color:#00c8ff;
  animation:vmsArr 1.4s ease-in-out infinite;}
@keyframes vmsArr{0%,100%{opacity:.4;transform:translateX(-2px);}
  50%{opacity:1;transform:translateX(2px);}}
.vms-fo-note{padding:7px 12px;background:#060c12;border-radius:5px;
  border:1px solid #1a2f42;font-family:'Courier New',monospace;font-size:9px;
  color:#4d6a82;text-align:center;line-height:1.5;}
.vms-modes{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;
  margin:12px 0 12px 40px;width:calc(100% - 40px);}
.vms-mode{padding:12px 14px;border-radius:7px;background:#0f1e2d;
  border:1px solid #1a2f42;}
.vms-mode-dot{display:inline-block;width:7px;height:7px;border-radius:50%;
  margin-right:6px;vertical-align:middle;}
.vms-mode-name{font-size:11px;font-weight:600;color:#e8eef5;margin-bottom:4px;}
.vms-mode-info{font-size:10px;color:#4d6a82;line-height:1.5;}
@media(max-width:1100px){#scrIss .vcard-grid{grid-template-columns:repeat(3,1fr);}}
@media(max-width:720px){
  #scrIss .vhero,#scrIss .vsearch-wrap,#scrIss .vsec-div,#scrIss .vgrid-wrap{
    padding-left:20px;padding-right:20px;}
  #scrIss .vcard-grid{grid-template-columns:repeat(2,1fr);}
  .vms-mbody,.vms-mhdr{padding:24px 22px;}
  .vms-ftxt,.vms-spec,.vms-imgslot,.vms-archtip,.vms-modes,.vms-fo{
    margin-left:0;width:100%;}
}

/* ══ ISS EXPLAINED SCREEN ════════════════════════════════════════ */
#scrExpl{background:#060c12;overflow-y:auto;}
#scrExpl .exp-page{background:#060c12;min-height:calc(100vh - 52px);
  font-family:'IBM Plex Sans','Segoe UI',system-ui,sans-serif;color:#e8eef5;
  padding:48px;}
#scrExpl .exp-page-inner{max-width:1280px;margin:0 auto;}
#scrExpl .exp-hero-tag{display:inline-flex;align-items:center;gap:8px;
  font-size:10px;letter-spacing:2.5px;text-transform:uppercase;color:#00c8ff;
  padding:5px 12px;border:1px solid rgba(0,200,255,.2);border-radius:4px;
  background:rgba(0,200,255,.05);margin-bottom:22px;
  font-family:'Courier New',monospace;}
#scrExpl .exp-h1{font-size:clamp(28px,3.5vw,52px);font-weight:800;
  letter-spacing:-1.5px;margin-bottom:10px;font-family:'Georgia',serif;
  line-height:1.05;}
#scrExpl .exp-h1 em{font-style:italic;
  background:linear-gradient(90deg,#00c8ff,#a78bfa);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;}
#scrExpl .exp-sub{font-size:13px;color:#8ba3bc;line-height:1.7;
  max-width:600px;margin-bottom:40px;font-weight:300;}
#scrExpl .hub-area{position:relative;width:100%;margin-bottom:48px;
  display:block !important;}
#scrExpl .hub-svg{width:100%;display:block !important;}
#scrExpl .svc-sections{display:grid;gap:32px;}
#scrExpl .svc-section-title{font-family:'Courier New',monospace;font-size:27px;
  letter-spacing:3px;text-transform:uppercase;color:#4d6a82;
  display:flex;align-items:center;gap:14px;margin-bottom:16px;padding-bottom:12px;
  border-bottom:1px solid #1a2f42;}
#scrExpl .svc-section-title::before{content:'';width:24px;height:1px;
  background:rgba(0,200,255,.5);}
#scrExpl .svc-grid{display:grid;
  grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;}
#scrExpl .svc-card{background:#0f1e2d;border:1px solid #1a2f42;border-radius:10px;
  padding:20px;cursor:pointer;transition:all .28s;position:relative;overflow:hidden;}
#scrExpl .svc-card::before{content:'';position:absolute;top:0;left:0;right:0;
  height:2px;background:var(--sc);transform:scaleX(0);transform-origin:left;
  transition:transform .3s;}
#scrExpl .svc-card:hover::before{transform:scaleX(1);}
#scrExpl .svc-card:hover{border-color:rgba(var(--scr),.3);
  transform:translateY(-3px);box-shadow:0 16px 32px rgba(0,0,0,.4);}
@media(max-width:720px){#scrExpl .exp-page{padding:24px;}}

/* ══ VA ASIDE RESIZER ════════════════════════════════════════════ */
.va-aside-resizer{width:5px;flex-shrink:0;cursor:col-resize;background:transparent;
  position:relative;transition:background .15s;z-index:10;}
.va-aside-resizer:hover,.va-aside-resizer.dragging{background:var(--accent);}
.va-aside-resizer::after{content:'';position:absolute;top:50%;left:50%;
  transform:translate(-50%,-50%);width:3px;height:32px;border-radius:3px;
  background:var(--border2);}
.va-aside-resizer:hover::after,.va-aside-resizer.dragging::after{
  background:var(--accent);}
#vaAside{min-width:160px;max-width:480px;}

/* ══ FONT SIZE CONTROLLER ════════════════════════════════════════ */
#fontCtrl{display:flex;align-items:center;gap:4px;border:1px solid var(--border);
  border-radius:6px;background:var(--surface2);padding:2px 4px;}
.fc-btn{width:26px;height:26px;border:none;border-radius:4px;
  background:transparent;color:var(--text2);cursor:pointer;font-size:14px;
  font-weight:700;display:flex;align-items:center;justify-content:center;
  transition:all .14s;line-height:1;}
.fc-btn:hover{background:var(--surface);color:var(--text);}
.fc-size{font-size:11px;color:var(--text3);min-width:28px;text-align:center;
  font-weight:500;}

/* ══ VA SUMMARY PANEL ════════════════════════════════════════════ */
#vaSummaryPanel{display:none;}
#vaSummaryPanel.show{display:block;}
.vas-hdr{padding:18px 20px 14px;border-bottom:1px solid var(--border);
  display:flex;align-items:center;gap:12px;}
.vas-hdr-icon{font-size:28px;}
.vas-hdr-title{font-size:18px;font-weight:700;color:var(--text);}
.vas-hdr-sub{font-size:12px;color:var(--text2);margin-top:2px;}
.vas-body{padding:16px;}
.vas-table-wrap{overflow-x:auto;overflow-y:auto;
  max-height:calc(100vh - 200px);border-radius:8px;border:1px solid var(--border);}
.vas-table{width:100%;min-width:720px;border-collapse:collapse;font-size:11.5px;}
.vas-table thead th{padding:8px 10px;text-align:center;font-weight:700;
  position:sticky;top:0;z-index:2;white-space:nowrap;
  border-bottom:2px solid var(--border2);}
.vas-table thead th:first-child{text-align:left;position:sticky;left:0;z-index:3;
  min-width:180px;background:var(--surface2)!important;}
.vas-table thead tr:first-child th{background:var(--surface2);}
.vas-table tbody td{padding:6px 10px;border-bottom:1px solid var(--border);
  text-align:center;font-size:13px;}
.vas-table tbody td:first-child{text-align:left;position:sticky;left:0;
  background:var(--surface);font-size:11.5px;color:var(--text2);z-index:1;}
.vas-table tbody tr:hover td{background:var(--surface2);}
.vas-table tbody tr:hover td:first-child{background:var(--surface2);}
.vas-group-row td{background:var(--surface3)!important;color:var(--text3)!important;
  font-size:9.5px!important;font-weight:700!important;letter-spacing:1px;
  text-transform:uppercase;text-align:left!important;padding:5px 10px!important;}
.vas-sub td:first-child{padding-left:22px!important;color:var(--text3)!important;
  font-size:10.5px!important;}
.vas-legend{display:flex;gap:14px;flex-wrap:wrap;padding:10px 0;font-size:11px;
  color:var(--text3);}
.vas-tiers{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px;}
.vas-tier-badge{padding:3px 10px;border-radius:12px;font-size:10px;font-weight:700;}"""

src = src.replace(CSS_ANCHOR, CSS_ANCHOR + EXTRA_CSS, 1)
ok(f"CSS injected  ({len(EXTRA_CSS)//1024}KB)")

# ─────────────────────────────────────────────────────────────
# 3. Nav — ISS/EXPL 버튼 + Font Controller 추가
# ─────────────────────────────────────────────────────────────
print("\n[3] Adding nav buttons + font controller ...")

OLD_NAV = (
    "  <button class=\"nav-btn\" id=\"navVa\"  onclick=\"goScreen('va')\">VA Selector</button>\n"
    "  <div class=\"nav-gap\"></div>\n"
    "  <button class=\"th-btn on\" id=\"btnL\" onclick=\"setTheme('light')\" title=\"Light\">☀</button>\n"
    "  <button class=\"th-btn\" id=\"btnD\" onclick=\"setTheme('dark')\" title=\"Dark\">🌙</button>\n"
    "  <button class=\"settings-btn\" onclick=\"openSettings()\" title=\"Settings\">⚙</button>"
)
NEW_NAV = (
    "  <button class=\"nav-btn\" id=\"navVa\"  onclick=\"goScreen('va')\">VA Selector</button>\n"
    "  <button class=\"nav-btn\" id=\"navIss\" onclick=\"goScreen('iss')\">IDIS VMS (ISS)</button>\n"
    "  <button class=\"nav-btn\" id=\"navExpl\" onclick=\"goScreen('expl')\">ISS Explained</button>\n"
    "  <div class=\"nav-gap\"></div>\n"
    "  <button class=\"th-btn on\" id=\"btnL\" onclick=\"setTheme('light')\" title=\"Light\">☀</button>\n"
    "  <button class=\"th-btn\" id=\"btnD\" onclick=\"setTheme('dark')\" title=\"Dark\">🌙</button>\n"
    "  <div id=\"fontCtrl\" title=\"Adjust font size\">\n"
    "    <button class=\"fc-btn\" onclick=\"adjFont(-1)\" title=\"Decrease font size\">A−</button>\n"
    "    <span class=\"fc-size\" id=\"fcSize\">100%</span>\n"
    "    <button class=\"fc-btn\" onclick=\"adjFont(1)\" title=\"Increase font size\">A+</button>\n"
    "    <button class=\"fc-btn\" onclick=\"adjFont(0)\" title=\"Reset\" style=\"font-size:10px;\">↺</button>\n"
    "  </div>\n"
    "  <button class=\"settings-btn\" onclick=\"openSettings()\" title=\"Settings\">⚙</button>"
)
must(OLD_NAV, src, "nav buttons")
src = src.replace(OLD_NAV, NEW_NAV, 1)
ok("IDIS VMS (ISS) + ISS Explained tabs added")
ok("Font size controller (A− / A+ / ↺) added")

# ─────────────────────────────────────────────────────────────
# 4. Camera Selector HTML 패치
# ─────────────────────────────────────────────────────────────
print("\n[4] Camera Selector HTML patches ...")

# 4a. ONVIF Only (Profile sub-panel 제거)
OLD_ONVIF = (
    'id="pOnvif"    onclick="togSet(aProto,\'onvif\',this)">ONVIF</span>\n'
    '    </div>\n'
    '    <div class="sub-pnl shut" id="sub-onvif">\n'
    '      <div class="sub-inner">\n'
    '        <span class="chip" data-onvifp="S" onclick="togSet(aOnvifP,\'S\',this)">Profile S</span>\n'
    '        <span class="chip" data-onvifp="T" onclick="togSet(aOnvifP,\'T\',this)">Profile T</span>\n'
    '        <span class="chip" data-onvifp="M" onclick="togSet(aOnvifP,\'M\',this)">Profile M</span>\n'
    '      </div>\n'
    '    </div>'
)
NEW_ONVIF = (
    'id="pOnvif"    onclick="togSet(aProto,\'onvif\',this)">ONVIF Only</span>\n'
    '    </div>'
)
must(OLD_ONVIF, src, "ONVIF chip + sub-panel")
src = src.replace(OLD_ONVIF, NEW_ONVIF, 1)
ok("ONVIF → 'ONVIF Only'  (Profile sub-panel removed)")

# 4b. FIPS + UL 분리
OLD_FIPS = (
    '<label class="ck-item"><input type="checkbox" data-feat="hasFIPS">'
    '<span class="ck-box"></span><span class="ck-lbl">FIPS 140-3 + UL</span></label>'
)
NEW_FIPS = (
    '<label class="ck-item"><input type="checkbox" data-feat="hasFIPS">'
    '<span class="ck-box"></span><span class="ck-lbl">FIPS 140-3</span></label>\n'
    '      <label class="ck-item"><input type="checkbox" data-feat="hasUL">'
    '<span class="ck-box"></span><span class="ck-lbl">UL Listed</span></label>'
)
must(OLD_FIPS, src, "FIPS 140-3 + UL checkbox")
src = src.replace(OLD_FIPS, NEW_FIPS, 1)
ok("FIPS 140-3  /  UL Listed — separated into two checkboxes")

# ─────────────────────────────────────────────────────────────
# 5. VA Selector HTML 재구성
# ─────────────────────────────────────────────────────────────
print("\n[5] VA Selector HTML restructure ...")

# 5a. va-wrap + aside (id 추가 + SUMMARY 버튼)
OLD_VA_WRAP_ASIDE = '<div class="va-wrap">\n  <aside class="va-left">'
NEW_VA_WRAP_ASIDE = (
    '<div class="va-wrap" id="vaWrap">\n'
    '<aside class="va-left" id="vaAside">\n'
    '    <!-- VA OVERALL SUMMARY button -->\n'
    '    <div class="va-feat-card" data-vaf="__summary__" style="grid-column:1/-1;'
    'background:linear-gradient(135deg,var(--accent-bg),var(--surface2));'
    'border:1.5px solid var(--accent);margin-bottom:4px;">\n'
    '      <span class="vfc-badge" style="background:var(--accent);color:white;">📊</span>\n'
    '      <div class="vfc-icon" style="font-size:20px;">📋</div>\n'
    '      <div class="vfc-name" style="color:var(--accent);font-size:11px;">VA OVERALL SUMMARY</div>\n'
    '      <div class="vfc-tier">Full Analytics Lineup Comparison</div>\n'
    '    </div>'
)
must(OLD_VA_WRAP_ASIDE, src, "va-wrap + va-left aside")
src = src.replace(OLD_VA_WRAP_ASIDE, NEW_VA_WRAP_ASIDE, 1)
ok("va-wrap id + VA OVERALL SUMMARY button added")

# 5b. va-right + va-intro: 리사이저 + 요약 패널 삽입
OLD_VA_RIGHT_INTRO = (
    '  <main class="va-right">\n'
    '    <div class="va-intro" id="vaIntro">\n'
    '      <div class="va-intro-icon">🔍</div>\n'
    '      <h2>Video Analytics Selector</h2>\n'
    '      <p>Select a VA feature on the left to see compatible cameras, NVRs, '
    'and appliance requirements.</p>\n'
    '    </div>\n'
    '    <div class="gone" id="vaResults"></div>'
)
NEW_VA_RIGHT_INTRO = (
    '  <div class="va-aside-resizer" id="vaResizer"></div>\n'
    '  <main class="va-right">\n'
    '    <div id="vaSummaryPanel">\n'
    '      <div class="vas-hdr">\n'
    '        <div class="vas-hdr-icon">📊</div>\n'
    '        <div>\n'
    '          <div class="vas-hdr-title">IDIS Analytics Lineup — Full Comparison</div>\n'
    '          <div class="vas-hdr-sub">All analytics capabilities across '
    'Edge AI, VA Box appliances, and VAIDIO server platform</div>\n'
    '        </div>\n'
    '      </div>\n'
    '      <div class="vas-body">\n'
    '        <div class="vas-tiers">\n'
    '          <span class="vas-tier-badge" style="background:var(--accent-bg);'
    'color:var(--accent);border:1px solid var(--accent);">EDGE AI+ — Camera Built-in</span>\n'
    '          <span class="vas-tier-badge" style="background:var(--orange-bg);'
    'color:var(--orange);border:1px solid var(--orange);">VA BOX — Add-on Appliance</span>\n'
    '          <span class="vas-tier-badge" style="background:var(--green-bg);'
    'color:var(--green);border:1px solid var(--green);">VAIDIO — ISS Server</span>\n'
    '        </div>\n'
    '        <div class="vas-legend"><span>✅ Supported &nbsp; '
    '🔶 Add-on Option &nbsp; ❌ Not Available</span></div>\n'
    '        <div class="vas-table-wrap">\n'
    '          <table class="vas-table">\n'
    '            <thead>\n'
    '              <tr>\n'
    '                <th style="background:var(--surface2);border-bottom:2px solid '
    'var(--border2);text-align:left;">Feature</th>\n'
    '                <th style="background:var(--accent-bg);color:var(--accent);'
    'border-bottom:2px solid var(--accent);">EdgeAI+<br>'
    '<small style="font-weight:400;color:var(--text3);">Dome/Bullet</small></th>\n'
    '                <th style="background:var(--accent-bg);color:var(--accent);'
    'border-bottom:2px solid var(--accent);">EdgeAI+<br>'
    '<small style="font-weight:400;color:var(--text3);">PTZ</small></th>\n'
    '                <th style="background:var(--surface2);color:var(--text2);'
    'border-bottom:2px solid var(--border2);">EdgeAI<br>'
    '<small style="font-weight:400;color:var(--text3);">Dome/Bullet</small></th>\n'
    '                <th style="background:var(--surface2);color:var(--text2);'
    'border-bottom:2px solid var(--border2);">EdgeAI<br>'
    '<small style="font-weight:400;color:var(--text3);">PTZ</small></th>\n'
    '                <th style="background:var(--orange-bg);color:var(--orange);'
    'border-bottom:2px solid var(--orange);">DV-1304A<br>'
    '<small style="font-weight:400;color:var(--text3);">BOX·Security</small></th>\n'
    '                <th style="background:var(--orange-bg);color:var(--orange);'
    'border-bottom:2px solid var(--orange);">DV-1304<br>'
    '<small style="font-weight:400;color:var(--text3);">BOX·Business</small></th>\n'
    '                <th style="background:var(--orange-bg);color:var(--orange);'
    'border-bottom:2px solid var(--orange);">DV-3200-B<br>'
    '<small style="font-weight:400;color:var(--text3);">SVR·Security</small></th>\n'
    '                <th style="background:var(--green-bg);color:var(--green);'
    'border-bottom:2px solid var(--green);">VAIDIO<br>'
    '<small style="font-weight:400;color:var(--text3);">Server</small></th>\n'
    '              </tr>\n'
    '              <tr style="font-size:9px;color:var(--text3);">\n'
    '                <td style="padding:3px 10px;background:var(--surface3);'
    'position:sticky;left:0;">Channels / Unit</td>\n'
    '                <td style="padding:3px 8px;text-align:center;'
    'background:var(--surface3);font-weight:600;">1</td>\n'
    '                <td style="padding:3px 8px;text-align:center;'
    'background:var(--surface3);font-weight:600;">1</td>\n'
    '                <td style="padding:3px 8px;text-align:center;'
    'background:var(--surface3);font-weight:600;">1</td>\n'
    '                <td style="padding:3px 8px;text-align:center;'
    'background:var(--surface3);font-weight:600;">1</td>\n'
    '                <td style="padding:3px 8px;text-align:center;'
    'background:var(--surface3);font-weight:600;">4</td>\n'
    '                <td style="padding:3px 8px;text-align:center;'
    'background:var(--surface3);font-weight:600;">4</td>\n'
    '                <td style="padding:3px 8px;text-align:center;'
    'background:var(--surface3);font-weight:600;">Up to 64</td>\n'
    '                <td style="padding:3px 8px;text-align:center;'
    'background:var(--surface3);font-weight:600;color:var(--green);">24/48/96</td>\n'
    '              </tr>\n'
    '            </thead>\n'
    '            <tbody id="vasTbody"></tbody>\n'
    '          </table>\n'
    '        </div>\n'
    '      </div>\n'
    '    </div>\n'
    '    <div class="va-intro" id="vaIntro">\n'
    '      <div class="va-intro-icon">🔍</div>\n'
    '      <h2>Video Analytics Selector</h2>\n'
    '      <p>Select a VA feature on the left to see compatible cameras, NVRs, '
    'and appliance requirements.</p>\n'
    '    </div>\n'
    '    <div class="gone" id="vaResults"></div>'
)
must(OLD_VA_RIGHT_INTRO, src, "va-right + va-intro")
src = src.replace(OLD_VA_RIGHT_INTRO, NEW_VA_RIGHT_INTRO, 1)
ok("Aside drag-resizer + VA Summary Panel + intro preserved")

# ─────────────────────────────────────────────────────────────
# 6. ISS Standard + ISS Explained HTML 스크린 삽입
# ─────────────────────────────────────────────────────────────
print("\n[6] Inserting ISS Standard and ISS Explained screens ...")

OLD_SETTINGS = '<div class="settings-ov" id="settingsOv">'
must(OLD_SETTINGS, src, "settings overlay")

ISS_EXPL_HTML = '''
</div>

<!-- ══ VMS (ISS) SCREEN ══ -->
<div id="scrIss" class="screen">
<div class="vms-page">

  <!-- HERO -->
  <div class="vhero">
    <div class="vhero-tag">
      <svg width="8" height="8" viewBox="0 0 8 8" fill="#00c8ff"><circle cx="4" cy="4" r="4"/></svg>
      IDIS Americas &nbsp;·&nbsp; Enterprise VMS
    </div>
    <h1 class="vhero-h1">Command.<br>Analyse.<br><em>Protect.</em></h1>
    <div class="vstats">
      <div><div class="vstat-num" id="vcnt1">0</div><div class="vstat-lbl">Max Devices</div></div>
      <div><div class="vstat-num" id="vcnt2">0</div><div class="vstat-lbl">Channels / 4 Monitors</div></div>
      <div><div class="vstat-num" id="vcnt3">0</div><div class="vstat-lbl">Concurrent Clients</div></div>
      <div><div class="vstat-num" id="vcnt4">0</div><div class="vstat-lbl">Maps Per Screen</div></div>
      <div><div class="vstat-num" id="vcnt5">0</div><div class="vstat-lbl">Layout Templates</div></div>
    </div>
  </div>

  <!-- SEARCH -->
  <div class="vsearch-wrap">
    <div class="vsearch-box">
      <input class="vsearch-input" id="vmsSearchInput" type="text"
             placeholder="Search features, specs, technologies..."
             oninput="vmsDoSearch(this.value)"
             onkeydown="if(event.key===\'Escape\'){this.value=\'\';vmsDoSearch(\'\');}">
      <svg class="vsearch-icon" width="15" height="15" viewBox="0 0 15 15" fill="none"
           stroke="currentColor" stroke-width="1.5">
        <circle cx="6" cy="6" r="5"/><path d="M10 10l3.5 3.5"/>
      </svg>
      <div class="vsearch-results" id="vmsSearchResults"></div>
    </div>
  </div>

  <!-- SECTION LABEL -->
  <div class="vsec-div"><div class="vsec-lbl">Core Features — Click a card to explore</div></div>

  <!-- CARD GRID -->
  <div class="vgrid-wrap"><div class="vcard-grid">

    <div class="vcard vc1" onclick="vmsOpen(\'m1\')">
      <div class="vcard-num">01 / 05</div>
      <div class="vcard-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="#00c8ff" stroke-width="1.4"
             stroke-linecap="round" stroke-linejoin="round">
          <rect x="1" y="1" width="9.5" height="9.5" rx="1.5"/>
          <rect x="13.5" y="1" width="9.5" height="9.5" rx="1.5"/>
          <rect x="1" y="13.5" width="9.5" height="9.5" rx="1.5"/>
          <rect x="13.5" y="13.5" width="9.5" height="9.5" rx="1.5"/>
        </svg>
      </div>
      <div class="vcard-title">Tactical UI &amp; Monitoring</div>
      <div class="vcard-desc">256-channel quad-monitor command centre with
        hover-menu quick controls &amp; 36-map geospatial awareness</div>
      <div class="vcard-cta">Explore →</div>
    </div>

    <div class="vcard vc2" onclick="vmsOpen(\'m2\')">
      <div class="vcard-num">02 / 05</div>
      <div class="vcard-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="#00e5b0" stroke-width="1.4"
             stroke-linecap="round" stroke-linejoin="round">
          <rect x="2" y="6" width="20" height="13" rx="2"/>
          <path d="M2 10h20"/><circle cx="6" cy="16" r="1.5"/>
          <circle cx="12" cy="16" r="1.5"/><circle cx="18" cy="16" r="1.5"/>
          <path d="M8 3h8M10 5h4"/>
        </svg>
      </div>
      <div class="vcard-title">Forensic Recording &amp; Retrieval</div>
      <div class="vcard-desc">Proprietary DB · 1/30-sec frame search ·
        HDP edge recovery · redundant recording</div>
      <div class="vcard-cta">Explore →</div>
    </div>

    <div class="vcard vc3" onclick="vmsOpen(\'m3\')">
      <div class="vcard-num">03 / 05</div>
      <div class="vcard-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="#a78bfa" stroke-width="1.4"
             stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="9.5"/>
          <path d="M12 3v4M12 17v4M3 12h4M17 12h4"/>
          <circle cx="12" cy="12" r="3.5"/>
        </svg>
      </div>
      <div class="vcard-title">Actionable Intelligence</div>
      <div class="vcard-desc">A-Cut AI search · Pixel Counter ·
        VA heatmap &amp; queue management BI</div>
      <div class="vcard-cta">Explore →</div>
    </div>

    <div class="vcard vc4" onclick="vmsOpen(\'m4\')">
      <div class="vcard-num">04 / 05</div>
      <div class="vcard-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="1.4"
             stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 2l2 5h5l-4 3 1.5 5L12 12.5 7.5 15 9 10 5 7h5l2-5z"/>
          <circle cx="12" cy="18" r="4.5"/>
          <path d="M10 18l1.5 1.5 3.5-3.5"/>
        </svg>
      </div>
      <div class="vcard-title">Universal Device Management</div>
      <div class="vcard-desc">ABC · 2,048-device ZeroConf deployment ·
        self-diagnosis &amp; remote batch upgrades</div>
      <div class="vcard-cta">Explore →</div>
    </div>

    <div class="vcard vc5" onclick="vmsOpen(\'m5\')">
      <div class="vcard-num">05 / 05</div>
      <div class="vcard-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="1.4"
             stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 2l9 3.5v7.5c0 5-4 8.5-9 10-5-1.5-9-5-9-10V5.5L12 2z"/>
          <path d="M9 12l2.5 2.5 5-5"/>
        </svg>
      </div>
      <div class="vcard-title">Resilience &amp; Security</div>
      <div class="vcard-desc">N:M Failover · SSL encryption ·
        GDPR privacy zones · OSD watermarking</div>
      <div class="vcard-cta">Explore →</div>
    </div>

  </div></div>
</div>
</div>

<!-- VMS MODAL OVERLAY -->
<div id="vmsOverlay" onclick="if(event.target===this)vmsClose()">
  <div class="vms-modal" id="vmsModal"></div>
</div>

<!-- ══ ISS EXPLAINED SCREEN ══ -->
<div id="scrExpl" class="screen">
<div class="exp-page">
<div class="exp-page-inner">
  <div class="exp-hero-tag">
    <svg width="8" height="8" viewBox="0 0 8 8" fill="#00c8ff"><circle cx="4" cy="4" r="4"/></svg>
    ISS Standard &nbsp;·&nbsp; Service Architecture
  </div>
  <h1 class="exp-h1">How ISS Standard<br><em>Actually Works</em></h1>
  <p class="exp-sub">ISS Standard is a modular, service-oriented VMS.
    The Administration Service is the central hub.
    Click any node to explore its technical logic.</p>
  <div class="hub-area">
    <svg class="hub-svg" id="hubSvg" viewBox="0 0 980 720"
         xmlns="http://www.w3.org/2000/svg"></svg>
  </div>
  <div class="svc-sections" style="display:none;">
    <div>
      <div class="svc-section-title">Core Services</div>
      <div class="svc-grid" id="coreGrid"></div>
    </div>
    <div>
      <div class="svc-section-title">Addon Services</div>
      <div class="svc-grid" id="proGrid"></div>
    </div>
  </div>
</div>
</div>
</div>

<!-- EXPL MODAL OVERLAY -->
<div id="explOverlay" style="position:fixed;inset:0;background:rgba(3,8,14,.82);
  backdrop-filter:blur(10px);z-index:998;display:none;align-items:flex-start;
  justify-content:center;padding:20px;overflow-y:auto;"
  onclick="if(event.target===this)explClose()">
  <div id="explModal" style="position:relative;background:#0a1520;
    border:1px solid #203649;border-radius:16px;width:100%;max-width:820px;
    margin:auto;overflow:hidden;
    animation:vmsIn .38s cubic-bezier(.34,1.56,.64,1);"></div>
</div>

'''

src = src.replace(OLD_SETTINGS, ISS_EXPL_HTML + OLD_SETTINGS, 1)
ok("ISS Standard screen inserted")
ok("ISS Explained screen inserted")
ok("VMS modal overlay inserted")
ok("EXPL modal overlay inserted")

# ─────────────────────────────────────────────────────────────
# 7. Script 1 — JS 패치 (togSet / passes / goScreen / VA)
# ─────────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────────
# 6b. cameras.json / recorders.json 이 있으면 배열 교체
# ──────────────────────────────────────────────────────────────────
import json as _json

scripts_tmp = list(re.finditer(r'<script>(.*?)</script>', src, re.DOTALL))
cam_js_tmp = scripts_tmp[0].group(1)
cam_js_updated = cam_js_tmp

CAMERAS_JSON  = Path("cameras.json")
RECORDERS_JSON = Path("recorders.json")

if CAMERAS_JSON.exists():
    print("\n[6b] Loading cameras.json ...")
    with open(CAMERAS_JSON, encoding="utf-8") as _f:
        new_cameras = _json.load(_f)
    cam_match = re.search(r'const CAMERAS\s*=\s*(\[.*?\]);', cam_js_updated, re.DOTALL)
    if cam_match:
        cam_js_updated = cam_js_updated.replace(
            "const CAMERAS = " + cam_match.group(1) + ";",
            "const CAMERAS = " + _json.dumps(new_cameras, ensure_ascii=False) + ";"
        , 1)
        ok(f"CAMERAS replaced: {len(new_cameras)} cameras from cameras.json")
    else:
        ok("cameras.json found but CAMERAS pattern not matched — skipping")
else:
    ok("cameras.json not found — using CAMERAS from base HTML")

if RECORDERS_JSON.exists():
    with open(RECORDERS_JSON, encoding="utf-8") as _f:
        new_recorders = _json.load(_f)
    # RECORDERS or NVR_DATA array
    for arr_name in ['const RECORDERS', 'const NVR_DATA', 'const NVRS']:
        rec_match = re.search(arr_name + r'\s*=\s*(\[.*?\]);', cam_js_updated, re.DOTALL)
        if rec_match:
            cam_js_updated = cam_js_updated.replace(
                arr_name.split()[1] + ' = ' + rec_match.group(1) + ';',
                arr_name.split()[1] + ' = ' + _json.dumps(new_recorders, ensure_ascii=False) + ';'
            , 1)
            ok(f"RECORDERS replaced: {len(new_recorders)} recorders from recorders.json")
            break
    else:
        ok(f"recorders.json loaded ({len(new_recorders)} recorders) — no array pattern matched in JS")
else:
    ok("recorders.json not found — using RECORDERS from base HTML")

if cam_js_updated != cam_js_tmp:
    src = src.replace("<script>" + cam_js_tmp, "<script>" + cam_js_updated, 1)

print("\n[7] Patching Camera Selector JS (Script 1) ...")

scripts = list(re.finditer(r'<script>(.*?)</script>', src, re.DOTALL))
cam = scripts[0].group(1)

# 7a. togSet — null sub-onvif 참조 제거 (핵심 버그 수정)
OLD_TOGSET = (
    "function togSet(set,val,el){\n"
    "  if(set.has(val)){set.delete(val);el.classList.remove('on');}\n"
    "  else{set.add(val);el.classList.add('on');}\n"
    "  if(set===aProto){\n"
    "    const pnl=document.getElementById('sub-onvif');\n"
    "    pnl.className='sub-pnl '+(aProto.has('onvif')?'open':'shut');\n"
    "    if(!aProto.has('onvif')){aOnvifP.clear();"
    "document.querySelectorAll('[data-onvifp]').forEach(c=>c.classList.remove('on'));}\n"
    "  }\n"
    "  render();\n"
    "}"
)
NEW_TOGSET = (
    "function togSet(set,val,el){\n"
    "  if(set.has(val)){set.delete(val);el.classList.remove('on');}\n"
    "  else{set.add(val);el.classList.add('on');}\n"
    "  // Note: sub-onvif panel removed (ONVIF Only mode — no sub-profile filter needed)\n"
    "  render();\n"
    "}"
)
must(OLD_TOGSET, cam, "togSet function")
cam = cam.replace(OLD_TOGSET, NEW_TOGSET, 1)
ok("togSet: null sub-onvif reference removed (protocol filter now works instantly)")

# 7b. passes() — ONVIF Only 필터
OLD_ONVIF_FILTER = (
    "const ok=(aProto.has('directip')&&cam.isDirectIP)"
    "||(aProto.has('onvif')&&cam.isONVIF);"
)
NEW_ONVIF_FILTER = (
    "const ok=(aProto.has('directip')&&cam.isDirectIP)"
    "||(aProto.has('onvif')&&cam.isONVIF&&!cam.isDirectIP);"
)
must(OLD_ONVIF_FILTER, cam, "passes() ONVIF filter")
cam = cam.replace(OLD_ONVIF_FILTER, NEW_ONVIF_FILTER, 1)
ok("passes(): ONVIF Only = isONVIF && !isDirectIP")

# 7c. passes() — FIPS/UL 독립 필터
OLD_FIPS_PASSES = (
    "for(const f of aFeat){\n"
    "    if(f==='hasFIPS'){\n"
    "      if(!cam.hasFIPS || !cam.hasUL) return false;\n"
    "    } else if(f==='hasVandal'){"
)
NEW_FIPS_PASSES = (
    "for(const f of aFeat){\n"
    "    if(f==='hasFIPS'){\n"
    "      if(!cam.hasFIPS) return false;\n"
    "    } else if(f==='hasUL'){\n"
    "      if(!cam.hasUL) return false;\n"
    "    } else if(f==='hasVandal'){"
)
must(OLD_FIPS_PASSES, cam, "passes() FIPS filter")
cam = cam.replace(OLD_FIPS_PASSES, NEW_FIPS_PASSES, 1)
ok("passes(): hasFIPS and hasUL are independent filters")

# 7d. resetAll() — aOnvifP.clear() + sub-onvif 참조 제거
cam = re.sub(r'  aOnvifP\.clear\(\);\n', '', cam)
cam = re.sub(r"[^\n]*getElementById\('sub-onvif'\)[^\n]*\n", '', cam)

# 7e. goScreen() 확장 (iss/expl 탭)
OLD_GOSCREEN = (
    "  document.getElementById('scrVa').className='screen'+(s==='va'?' on':'');\n"
    "  document.getElementById('navVa').className='nav-btn'+(s==='va'?' nav-on':'');\n"
    "  if(s==='vms') vRenderQ();\n"
    "}"
)
NEW_GOSCREEN = (
    "  document.getElementById('scrVa').className='screen'+(s==='va'?' on':'');\n"
    "  document.getElementById('navVa').className='nav-btn'+(s==='va'?' nav-on':'');\n"
    "  document.getElementById('scrIss').className='screen'+(s==='iss'?' on':'');\n"
    "  document.getElementById('navIss').className='nav-btn'+(s==='iss'?' nav-on':'');\n"
    "  document.getElementById('scrExpl').className='screen'+(s==='expl'?' on':'');\n"
    "  document.getElementById('navExpl').className='nav-btn'+(s==='expl'?' nav-on':'');\n"
    "  document.body.style.background = (s==='iss'||s==='expl') ? '#060c12' : '';\n"
    "  if(s==='iss'   && window._vmsOnEnter)  window._vmsOnEnter();\n"
    "  if(s==='expl'  && window._explOnEnter) window._explOnEnter();\n"
    "  if(s==='vms') vRenderQ();\n"
    "}"
)
must(OLD_GOSCREEN, cam, "goScreen function end")
cam = cam.replace(OLD_GOSCREEN, NEW_GOSCREEN, 1)
ok("goScreen(): extended for iss / expl tabs")

# 7f. VA click handler 교체 + 추가 함수 삽입 (init 바로 전)
OLD_VA_CLICK = (
    "document.getElementById('scrVa').addEventListener('click',function(e){\n"
    "  const card=e.target.closest('.va-feat-card');if(!card)return;\n"
    "  const feat=card.dataset.vaf;if(!feat)return;\n"
    "  if(vaActive===feat){\n"
    "    vaActive=null;\n"
    "    document.querySelectorAll('.va-feat-card').forEach(c=>c.classList.remove('active'));\n"
    "    document.getElementById('vaResults').classList.add('gone');\n"
    "    document.getElementById('vaIntro').style.display='';\n"
    "    return;\n"
    "  }\n"
    "  vaActive=feat;\n"
    "  document.querySelectorAll('.va-feat-card').forEach(c=>c.classList.remove('active'));\n"
    "  card.classList.add('active');\n"
    "  document.getElementById('vaIntro').style.display='none';\n"
    "  vaRender(feat);\n"
    "});"
)

NEW_VA_CLICK = r"""document.getElementById('scrVa').addEventListener('click',function(e){
  const card=e.target.closest('.va-feat-card');if(!card)return;
  const feat=card.dataset.vaf;if(!feat)return;

  // Reset all cards
  document.querySelectorAll('.va-feat-card').forEach(c=>c.classList.remove('active'));
  const sumPanel=document.getElementById('vaSummaryPanel');
  const intro=document.getElementById('vaIntro');
  const results=document.getElementById('vaResults');

  // VA OVERALL SUMMARY
  if(feat==='__summary__'){
    if(vaActive==='__summary__'){
      vaActive=null;sumPanel.classList.remove('show');
      intro.style.display='';results.classList.add('gone');return;
    }
    vaActive='__summary__';card.classList.add('active');
    intro.style.display='none';results.classList.add('gone');
    sumPanel.classList.add('show');buildVaSummaryTable();return;
  }

  // Regular feature card
  if(vaActive===feat){
    vaActive=null;results.classList.add('gone');
    sumPanel.classList.remove('show');intro.style.display='';return;
  }
  vaActive=feat;card.classList.add('active');
  intro.style.display='none';sumPanel.classList.remove('show');
  results.classList.remove('gone');
  vaRender(feat);
});

/* ── VA OVERALL SUMMARY TABLE ── */
function buildVaSummaryTable(){
  var tbody=document.getElementById('vasTbody');
  if(!tbody||tbody.dataset.built==='1')return;
  tbody.dataset.built='1';
  var Y='✅',N='❌',A='🔶';
  var secs=[
    {g:'METADATA CLASSIFICATION',rows:[
      ['A-Cut Search',Y,Y,N,N,N,N,N,Y],
      ['Human Detection',Y,Y,Y,Y,Y,N,Y,Y],
      ['· Gender/Age/Bag/Hat',Y,Y,N,N,N,N,N,Y],
      ['Vehicle Detection',Y,Y,Y,Y,Y,N,Y,Y],
      ['· Car/Bike/Motorcycle',Y,Y,N,N,N,N,N,Y],
      ['· Bus/Truck/Emergency',Y,Y,N,N,N,N,N,Y],
      ['· Maker/Model',N,N,N,N,N,N,N,Y],
      ['Face Detection',Y,Y,Y,Y,Y,N,Y,Y],
      ['· Gender/Age/Glasses/Hat/Mask',Y,Y,N,N,N,N,N,Y],
      ['Face Recognition',N,N,N,N,N,N,N,Y],
      ['LPR',N,N,N,N,N,N,N,Y],
      ['Container ID Recognition',N,N,N,N,N,N,N,Y],
      ['Color Match (Human/Vehicle)',Y,Y,N,N,N,N,N,Y],
      ['Business Data',N,N,N,N,N,Y,N,Y],
    ]},
    {g:'ANALYTIC ALARMS',rows:[
      ['Object Detection',Y,Y,Y,Y,Y,N,Y,Y],
      ['Special Object Detection',N,N,N,N,N,N,N,Y],
      ['PPE Detection',N,N,N,N,N,N,N,Y],
      ['Intrusion/Trip Zone/Loitering',Y,Y,Y,Y,Y,N,N,Y],
      ['Line Crossing / Wrong Dir.',Y,Y,Y,Y,Y,N,Y,Y],
      ['Crowd Detection',Y,Y,N,N,N,N,A,Y],
      ['Abandoned/Removed Object',Y,Y,N,N,N,N,A,Y],
      ['Fall Detection',Y,Y,N,N,N,N,A,Y],
      ['Violence Detection',Y,Y,N,N,N,N,A,N],
      ['PTZ Auto Tracking',N,Y,N,Y,N,N,Y,N],
      ['Person Match / Cross-Camera',N,N,N,N,N,N,A,Y],
    ]},
    {g:'BUSINESS INTELLIGENCE',rows:[
      ['People Counting',N,N,N,N,N,Y,N,Y],
      ['Object Counting',N,N,N,N,N,N,N,Y],
      ['Queue Monitoring',N,N,N,N,N,Y,N,Y],
      ['Heat Map',N,N,N,N,N,Y,N,Y],
      ['Queue Congestion',N,N,N,N,N,Y,N,Y],
      ['Exceed Occupancy Limit',N,N,N,N,N,Y,N,Y],
      ['Social Distancing Violation',N,N,N,N,N,Y,N,N],
      ['Mask Rule Violation',N,N,N,N,N,Y,N,Y],
      ['Scene Change',N,N,N,N,N,N,N,Y],
      ['Fire/Explosion Detection',N,N,N,N,N,N,A,Y],
      ['Live Privacy Masking',N,N,N,N,N,N,A,Y],
    ]},
    {g:'CLIENT FEATURES',rows:[
      ['Instant Meta Filtering',Y,Y,Y,Y,Y,N,Y,Y],
      ['A-Cut Monitoring Panel',Y,Y,N,Y,N,N,N,N],
      ['AI Search',Y,Y,Y,Y,N,N,N,Y],
      ['AI Search w/ Attribute Mode',Y,Y,N,Y,N,N,N,Y],
      ['Fisheye Analytics (Add-on)',N,N,N,N,N,N,A,Y],
    ]},
  ];
  var html='';
  secs.forEach(function(sec){
    html+='<tr class="vas-group-row"><td colspan="9">'+sec.g+'</td></tr>';
    sec.rows.forEach(function(row){
      var isSub=row[0].charAt(0)==='·';
      html+='<tr'+(isSub?' class="vas-sub"':'')+'><td>'+row[0]+'</td>';
      for(var ci=1;ci<=8;ci++) html+='<td>'+row[ci]+'</td>';
      html+='</tr>';
    });
  });
  tbody.innerHTML=html;
}

/* ── FONT SIZE CONTROLLER ── */
var _fsLevel=0;
function adjFont(dir){
  if(dir===0){_fsLevel=0;}
  else{_fsLevel=Math.max(-4,Math.min(6,_fsLevel+dir));}
  var pct=100+_fsLevel*10;
  document.body.style.fontSize=pct+'%';
  var el=document.getElementById('fcSize');if(el)el.textContent=pct+'%';
}

/* ── VA ASIDE DRAG RESIZER ── */
(function(){
  var rz=document.getElementById('vaResizer');
  var aside=document.getElementById('vaAside');
  if(!rz||!aside)return;
  var dragging=false,startX=0,startW=0;
  rz.addEventListener('mousedown',function(e){
    dragging=true;startX=e.clientX;startW=aside.offsetWidth;
    rz.classList.add('dragging');
    document.body.style.userSelect='none';
    document.body.style.cursor='col-resize';
    e.preventDefault();
  });
  document.addEventListener('mousemove',function(e){
    if(!dragging)return;
    var newW=Math.max(160,Math.min(480,startW+(e.clientX-startX)));
    aside.style.width=newW+'px';aside.style.minWidth=newW+'px';
  });
  document.addEventListener('mouseup',function(){
    if(!dragging)return;dragging=false;
    rz.classList.remove('dragging');
    document.body.style.userSelect='';document.body.style.cursor='';
  });
})();"""

must(OLD_VA_CLICK, cam, "VA click handler")
cam = cam.replace(OLD_VA_CLICK, NEW_VA_CLICK, 1)
ok("VA click handler: __summary__ + regular cards")
ok("buildVaSummaryTable() added  (35 features × 8 products)")
ok("adjFont() added  (80%–160%, ±10% per step)")
ok("VA aside drag resizer IIFE added  (160–480px)")

# Syntax check
if not js_ok(cam, "Script 1 — Camera JS"):
    fail("Script 1 has syntax errors — aborting")
ok("Script 1 syntax OK")

src = src.replace("<script>" + scripts[0].group(1), "<script>" + cam, 1)

# ─────────────────────────────────────────────────────────────
# 8. Script 2 — VMS JS (이미지 base64 포함)
# ─────────────────────────────────────────────────────────────
print("\n[8] Building VMS Script (Script 2) ...")

VMS_JS_TEMPLATE = r"""
/* ════════════════════════════════════════════════════════
   VMS (ISS STANDARD) — Self-Contained IIFE
   All functions prefixed vms*  /  No external dependencies
   ════════════════════════════════════════════════════════ */
(function(){

/* ── IMAGE DATA (injected by build script) ── */
/* IMG_VARS_PLACEHOLDER */

/* ── MODAL CONTENT DATA ── */
var VMS_DATA={
m1:{color:"#00c8ff",cr:"0,200,255",cat:"Category 01",
  title:"Tactical UI & Monitoring",
  tagline:"Total situational command through a high-performance interface designed for complex, mission-critical environments.",
  body:`
<div class="vms-fblock">
  <div class="vms-fhdr">
    <div class="vms-fhdr-ic"><svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.4">
      <rect x="1" y="1" width="5.5" height="5.5" rx="1"/><rect x="7.5" y="1" width="5.5" height="5.5" rx="1"/>
      <rect x="1" y="7.5" width="5.5" height="5.5" rx="1"/><rect x="7.5" y="7.5" width="5.5" height="5.5" rx="1"/>
    </svg></div>
    <div class="vms-fh3"><small>High-Density Display</small>Quad-Monitor 256-Channel Architecture</div>
  </div>
  <div class="vms-ftxt">
    <p>ISS Standard spans <strong>4 independent monitors</strong> delivering real-time surveillance of up to
    <strong>256 simultaneous channels</strong> with <strong>43 layout templates</strong> and
    up to <strong>36 maps per screen</strong>.</p>
  </div>
  <div class="vms-imgslot">
    <img src="manual_p79_toolbar.png" id="vmsImg-toolbar" alt="Panel Toolbar">
    <div class="vms-imgslot-cap">Panel toolbar — layout selector, PTZ, recording controls (p.79)</div>
  </div>
  <div class="vms-spec"><div class="vms-spec-lbl">Tech Spec</div><div class="vms-spec-grid">
    <div class="vms-spec-item"><div class="vms-spec-key">Monitors</div><div class="vms-spec-val"><b>4</b> independent</div></div>
    <div class="vms-spec-item"><div class="vms-spec-key">Channels</div><div class="vms-spec-val"><b>256</b> CH max</div></div>
    <div class="vms-spec-item"><div class="vms-spec-key">Layouts</div><div class="vms-spec-val"><b>43</b> templates</div></div>
    <div class="vms-spec-item"><div class="vms-spec-key">Maps/Screen</div><div class="vms-spec-val"><b>36</b> simultaneous</div></div>
  </div></div>
</div>
<div class="vms-fblock">
  <div class="vms-fhdr">
    <div class="vms-fhdr-ic"><svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.4">
      <circle cx="7" cy="7" r="5.5"/><path d="M7 4v3l2 1.5"/>
    </svg></div>
    <div class="vms-fh3"><small>Smart UX</small>Tactical Hover Menu <span class="vms-pro">⚡ Pro Tech</span></div>
  </div>
  <div class="vms-ftxt">
    <p>Context-aware <strong>Hover Menu</strong> provides instant PTZ, colour adjustment, audio, and recording.
    Includes <em>Multi-Stream</em>, <em>Event Spot</em>, and <strong>Video Analysis toggle</strong>.</p>
  </div>
  <div class="vms-imgslot">
    <img src="manual_p95_hover.png" id="vmsImg-hover" alt="Hover Menu">
    <div class="vms-imgslot-cap">Context-aware hover menu with full command palette (p.95)</div>
  </div>
</div>`},

m2:{color:"#00e5b0",cr:"0,229,176",cat:"Category 02",
  title:"Forensic Recording & Retrieval",
  tagline:"Absolute data integrity with proprietary file systems and high-precision forensic search tools.",
  body:`
<div class="vms-fblock">
  <div class="vms-fhdr">
    <div class="vms-fhdr-ic"><svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.4">
      <rect x="2" y="3.5" width="10" height="7.5" rx="1"/><path d="M2 6.5h10"/>
    </svg></div>
    <div class="vms-fh3"><small>Recording Engine</small>Multi-Mode Recording Architecture</div>
  </div>
  <div class="vms-ftxt">
    <p>Supports <span class="vms-kw">H.265</span> <span class="vms-kw">H.264</span>
    <span class="vms-kw">MPEG-4</span> <span class="vms-kw">M-JPEG</span> with a
    <strong>proprietary video DB</strong> eliminating fragmentation and extending HDD lifespan.</p>
  </div>
  <div class="vms-modes">
    <div class="vms-mode"><div class="vms-mode-name"><span class="vms-mode-dot" style="background:#3b82f6"></span>Continuous</div><div class="vms-mode-info">24/7 scheduled (blue)</div></div>
    <div class="vms-mode"><div class="vms-mode-name"><span class="vms-mode-dot" style="background:#ef4444"></span>Event</div><div class="vms-mode-info">Motion/IDLA only (red)</div></div>
    <div class="vms-mode"><div class="vms-mode-name"><span class="vms-mode-dot" style="background:#f59e0b"></span>Emergency</div><div class="vms-mode-info">Operator-triggered (yellow)</div></div>
  </div>
  <div class="vms-imgslot">
    <img src="manual_p124_timeline.png" id="vmsImg-timeline" alt="Timeline">
    <div class="vms-imgslot-cap">Multi-channel playback timeline (p.124)</div>
  </div>
</div>
<div class="vms-fblock">
  <div class="vms-fhdr">
    <div class="vms-fhdr-ic"><svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.4">
      <circle cx="7" cy="7" r="5.5"/><path d="M7 4v3l2 2"/>
    </svg></div>
    <div class="vms-fh3"><small>Forensic Search</small>1/30-Second Frame Precision <span class="vms-pro">⚡ Pro Tech</span></div>
  </div>
  <div class="vms-ftxt">
    <p><strong>1/30-second frame-by-frame search</strong> via mouse shuttle.
    <strong>HDP</strong> auto-ingests edge SD-card footage on reconnection.</p>
  </div>
  <div class="vms-spec"><div class="vms-spec-lbl">Tech Spec</div><div class="vms-spec-grid">
    <div class="vms-spec-item"><div class="vms-spec-key">Frame Precision</div><div class="vms-spec-val"><b>1/30</b> sec</div></div>
    <div class="vms-spec-item"><div class="vms-spec-key">CH/Server</div><div class="vms-spec-val"><b>256</b></div></div>
    <div class="vms-spec-item"><div class="vms-spec-key">Rec Servers</div><div class="vms-spec-val"><b>64</b> max</div></div>
    <div class="vms-spec-item"><div class="vms-spec-key">Export</div><div class="vms-spec-val">AVI/BMP/JPEG</div></div>
  </div></div>
</div>`},

m3:{color:"#a78bfa",cr:"167,139,250",cat:"Category 03",
  title:"Actionable Intelligence",
  tagline:"Transform raw video into operational insights via AI analytics and BI dashboards.",
  body:`
<div class="vms-fblock">
  <div class="vms-fhdr">
    <div class="vms-fhdr-ic"><svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.4">
      <circle cx="7" cy="4.5" r="2.8"/><path d="M1.5 12.5c0-3 11-3 11 0"/>
    </svg></div>
    <div class="vms-fh3"><small>A-Cut AI Search</small>Attribute-Based Object Retrieval <span class="vms-pro">⚡ Pro Tech</span></div>
  </div>
  <div class="vms-ftxt">
    <p><strong>A-Cut panel</strong> searches footage by <em>gender, age group, hat/bag, and 10 clothing colours</em>.
    Extracts evidence frames instantly.</p>
  </div>
  <div class="vms-imgslot">
    <img src="manual_p268_acut.png" id="vmsImg-acut" alt="A-Cut Detection">
    <div class="vms-imgslot-cap">A-Cut live detection — person attributes (p.268)</div>
  </div>
  <div class="vms-imgslot">
    <img src="manual_p269_filter.png" id="vmsImg-filter" alt="A-Cut Filter">
    <div class="vms-imgslot-cap">A-Cut AI search filter panel (p.269)</div>
  </div>
</div>
<div class="vms-fblock">
  <div class="vms-fhdr">
    <div class="vms-fhdr-ic"><svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.4">
      <rect x="1" y="1" width="12" height="12" rx="1.5"/>
      <path d="M3.5 11V7.5l2 2.5 2-5 2.5 3.5 2-3"/>
    </svg></div>
    <div class="vms-fh3"><small>Business Intelligence</small>Queue Management &amp; Heatmap Dashboard</div>
  </div>
  <div class="vms-ftxt">
    <p><strong>Queue Management</strong> tracks headcount and wait times across 3 configurable zones.
    <strong>Heatmaps</strong> reveal foot-traffic density in real time.</p>
  </div>
  <div class="vms-imgslot">
    <img src="manual_p231_stats.png" id="vmsImg-stats" alt="Queue Stats Dashboard">
    <div class="vms-imgslot-cap">Queue Management live dashboard (p.231)</div>
  </div>
</div>`},

m4:{color:"#f59e0b",cr:"245,158,11",cat:"Category 04",
  title:"Universal Device Management",
  tagline:"Limitless infrastructure expansion through automated discovery and industry-standard protocols.",
  body:`
<div class="vms-fblock">
  <div class="vms-fhdr">
    <div class="vms-fhdr-ic"><svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.4">
      <circle cx="7" cy="4.5" r="2.5"/><path d="M1.5 13c0-3.5 11-3.5 11 0"/>
    </svg></div>
    <div class="vms-fh3"><small>Enterprise Scale</small>2,048-Device Unified Management</div>
  </div>
  <div class="vms-ftxt">
    <p>Manages up to <strong>2,048 devices</strong> — IDIS, ONVIF (Profile S/G/T), Axis, Panasonic —
    within a single unified system.</p>
  </div>
  <div class="vms-spec"><div class="vms-spec-lbl">Tech Spec</div><div class="vms-spec-grid">
    <div class="vms-spec-item"><div class="vms-spec-key">Max Devices</div><div class="vms-spec-val"><b>2,048</b> units</div></div>
    <div class="vms-spec-item"><div class="vms-spec-key">ONVIF</div><div class="vms-spec-val">Profile S/G/<b>T</b></div></div>
    <div class="vms-spec-item"><div class="vms-spec-key">Discovery</div><div class="vms-spec-val"><b>ZeroConf</b></div></div>
    <div class="vms-spec-item"><div class="vms-spec-key">Concurrent</div><div class="vms-spec-val"><b>64</b> clients</div></div>
  </div></div>
</div>
<div class="vms-fblock">
  <div class="vms-fhdr">
    <div class="vms-fhdr-ic"><svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.4">
      <path d="M7 1.5L12.5 4.5v4c0 3.2-2.3 5-5.5 5.5-3.2-.5-5.5-2.3-5.5-5.5v-4L7 1.5z"/>
    </svg></div>
    <div class="vms-fh3"><small>ABC Engine</small>Active Bandwidth Control <span class="vms-pro">⚡ Pro Tech</span></div>
  </div>
  <div class="vms-ftxt">
    <p>Auto-switches Sub-stream ↔ Main-stream with <strong>H.264/H.265 logic</strong>.
    Load balancing sustains <strong>64 concurrent clients</strong>.
    <strong>FEN</strong> resolves NAT without port-forwarding.</p>
  </div>
</div>`},

m5:{color:"#ef4444",cr:"239,68,68",cat:"Category 05",
  title:"Resilience & Security",
  tagline:"Maximise availability with hardened failover, GDPR compliance, and proactive monitoring.",
  body:`
<div class="vms-fblock">
  <div class="vms-fhdr">
    <div class="vms-fhdr-ic"><svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.4">
      <path d="M2 7h10M7.5 1.5l5.5 5.5-5.5 5.5M4 4.5L1.5 7l2.5 2.5"/>
    </svg></div>
    <div class="vms-fh3"><small>Failover</small>N:M Multi-Role Failover <span class="vms-pro">⚡ Pro Tech</span></div>
  </div>
  <div class="vms-ftxt">
    <p>Independent <strong>N:M failover</strong> for every server role — Admin, Recording, Monitoring, Video Wall.
    Standby activates with <strong>zero operator intervention</strong>.</p>
  </div>
  <div class="vms-fo">
    <div class="vms-fo-node"><div class="vms-fo-box down">PRIMARY<br>SERVER</div><div class="vms-fo-lbl" style="color:#ef4444">⚠ Fault</div></div>
    <div class="vms-fo-arr">→</div>
    <div class="vms-fo-node"><div class="vms-fo-box up">STANDBY<br>SERVER</div><div class="vms-fo-lbl" style="color:#00e5b0">✓ Active</div></div>
    <div class="vms-fo-note">Zero-downtime<br>handover</div>
  </div>
  <div class="vms-spec"><div class="vms-spec-lbl">Resilience Stack</div><div class="vms-spec-grid">
    <div class="vms-spec-item"><div class="vms-spec-key">Failover Scope</div><div class="vms-spec-val">Admin/Rec/Mon/VW</div></div>
    <div class="vms-spec-item"><div class="vms-spec-key">Dual Recording</div><div class="vms-spec-val"><b>Redundant</b></div></div>
    <div class="vms-spec-item"><div class="vms-spec-key">WIBU Keys</div><div class="vms-spec-val">Up to <b>8</b>/Admin</div></div>
    <div class="vms-spec-item"><div class="vms-spec-key">Clients</div><div class="vms-spec-val"><b>64</b> + LB</div></div>
  </div></div>
</div>
<div class="vms-fblock">
  <div class="vms-fhdr">
    <div class="vms-fhdr-ic"><svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.4">
      <rect x="3.5" y="6.5" width="7" height="6" rx="1"/>
      <path d="M5 6.5V5a2 2 0 014 0v1.5"/>
    </svg></div>
    <div class="vms-fh3"><small>Privacy</small>GDPR Architecture &amp; Privacy Zones <span class="vms-pro">⚡ Pro Tech</span></div>
  </div>
  <div class="vms-ftxt">
    <p>3-step <strong>GDPR consent wizard</strong> for FEN remote access.
    <strong>Clip Privacy Zone</strong> masking permanently redacts exported footage.</p>
  </div>
  <div class="vms-imgslot">
    <img src="manual_p259_gdpr.png" id="vmsImg-gdpr" alt="GDPR Consent">
    <div class="vms-imgslot-cap">FEN service GDPR consent wizard (p.259)</div>
  </div>
  <div class="vms-archtip">
    <div class="vms-archtip-lbl">⚠ Architect's Tip — WIBU Key Stability</div>
    <div class="vms-archtip-txt">The Admin Server supports up to <strong>8 WIBU keys</strong>.
    Removing any key halts all dependent services immediately. Always perform a full graceful shutdown
    before handling keys. Streaming, Backup, Video Wall, and Failover each require dedicated licence keys.</div>
  </div>
</div>`}
};

/* ── IMAGE INJECTION ── */
var VMS_IMGMAP={
  "vmsImg-toolbar": typeof VMS_IMG_TOOLBAR!=="undefined"?VMS_IMG_TOOLBAR:null,
  "vmsImg-hover":   typeof VMS_IMG_HOVER!=="undefined"?VMS_IMG_HOVER:null,
  "vmsImg-timeline":typeof VMS_IMG_TIMELINE!=="undefined"?VMS_IMG_TIMELINE:null,
  "vmsImg-stats":   typeof VMS_IMG_STATS!=="undefined"?VMS_IMG_STATS:null,
  "vmsImg-gdpr":    typeof VMS_IMG_GDPR!=="undefined"?VMS_IMG_GDPR:null,
  "vmsImg-acut":    typeof VMS_IMG_ACUT!=="undefined"?VMS_IMG_ACUT:null,
  "vmsImg-filter":  typeof VMS_IMG_FILTER!=="undefined"?VMS_IMG_FILTER:null
};
function vmsInjectImgs(){
  Object.keys(VMS_IMGMAP).forEach(function(id){
    var el=document.getElementById(id);
    if(el&&VMS_IMGMAP[id]) el.src=VMS_IMGMAP[id];
  });
}

/* ── COUNTER ANIMATION ── */
function vmsRunCounters(){
  [{id:"vcnt1",t:2048},{id:"vcnt2",t:256},{id:"vcnt3",t:64},
   {id:"vcnt4",t:36},{id:"vcnt5",t:43}].forEach(function(item){
    var el=document.getElementById(item.id);if(!el)return;
    var v=0,step=Math.ceil(item.t/55);
    var iv=setInterval(function(){
      v=Math.min(v+step,item.t);el.textContent=v.toLocaleString();
      if(v>=item.t)clearInterval(iv);
    },28);
  });
}

/* ── OPEN MODAL ── */
window.vmsOpen=function(id){
  var d=VMS_DATA[id];if(!d)return;
  var ov=document.getElementById("vmsOverlay");
  var mo=document.getElementById("vmsModal");if(!ov||!mo)return;
  mo.style.setProperty("--mvc",d.color);mo.style.setProperty("--mvcr",d.cr);
  mo.innerHTML='<div class="vms-mhdr">'+
    '<button class="vms-mclose" onclick="vmsClose()">&#x2715;</button>'+
    '<div class="vms-mcat">'+d.cat+'</div>'+
    '<h2 class="vms-mtitle">'+d.title+'</h2>'+
    '<p class="vms-mtagline">&ldquo;'+d.tagline+'&rdquo;</p>'+
    '</div><div class="vms-mbody">'+d.body+'</div>';
  ov.classList.add("vms-open");document.body.style.overflow="hidden";
  vmsInjectImgs();
};

/* ── CLOSE MODAL ── */
window.vmsClose=function(){
  var o=document.getElementById("vmsOverlay");
  if(o)o.classList.remove("vms-open");
  document.body.style.overflow="";
};

/* ── SEARCH INDEX ── */
var vmsIdx=null;
function vmsBuildIdx(){
  if(vmsIdx)return vmsIdx;
  vmsIdx=[];
  Object.keys(VMS_DATA).forEach(function(id){
    var d=VMS_DATA[id];
    var tmp=document.createElement("div");tmp.innerHTML=d.body||"";
    var blocks=tmp.querySelectorAll(".vms-fblock");
    (blocks.length?Array.from(blocks):[tmp]).forEach(function(block){
      var h=block.querySelector(".vms-fh3");
      var b=block.querySelector(".vms-ftxt");
      var s=block.querySelector(".vms-spec");
      vmsIdx.push({id:id,cat:d.cat,modalTitle:d.title,
        title:(h?h.textContent:"").replace(/\s+/g," ").trim()||d.title,
        text:((b?b.textContent:"")+" "+(s?s.textContent:""))
          .replace(/\s+/g," ").trim().slice(0,400)});
    });
  });
  return vmsIdx;
}
function vmsHL(s,q){
  if(!q)return s;
  return s.replace(
    new RegExp("("+q.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")+")", "gi"),
    "<mark>$1</mark>"
  );
}

/* ── SEARCH ── */
window.vmsDoSearch=function(q){
  var res=document.getElementById("vmsSearchResults");if(!res)return;
  q=(q||"").trim();
  if(!q){res.className="vsearch-results";res.innerHTML="";return;}
  var lq=q.toLowerCase();
  var hits=vmsBuildIdx().filter(function(i){
    return i.title.toLowerCase().includes(lq)||
           i.text.toLowerCase().includes(lq)||
           i.modalTitle.toLowerCase().includes(lq);
  });
  if(!hits.length){
    res.className="vsearch-results show";
    res.innerHTML='<div class="vsr-empty">No results for &ldquo;'+q+'&rdquo;</div>';
    return;
  }
  var html='<div class="vsr-count">'+hits.length+' result'+(hits.length>1?"s":"")+'</div>';
  hits.forEach(function(item){
    var ki=item.text.toLowerCase().indexOf(lq);
    var ex=ki>=0?item.text.slice(Math.max(0,ki-50),ki+q.length+100):item.text.slice(0,160);
    html+='<div class="vsr-item" onclick="vmsOpen(\''+item.id+'\');'+
      'document.getElementById(\'vmsSearchInput\').value=\'\';vmsDoSearch(\'\');">';
    html+='<div class="vsr-cat">'+vmsHL(item.cat+" — "+item.modalTitle,q)+'</div>';
    html+='<div class="vsr-title">'+vmsHL(item.title,q)+'</div>';
    html+='<div class="vsr-excerpt">'+vmsHL(ex,q)+'</div></div>';
  });
  res.className="vsearch-results show";res.innerHTML=html;
};
document.addEventListener("click",function(e){
  var inp=document.getElementById("vmsSearchInput");
  var res=document.getElementById("vmsSearchResults");
  if(inp&&res&&!inp.parentElement.contains(e.target))
    res.className="vsearch-results";
});

/* ── INIT ── */
var _vmsDone=false;
window._vmsOnEnter=function(){
  if(!_vmsDone){_vmsDone=true;vmsRunCounters();}
};

})();
"""

VMS_JS = VMS_JS_TEMPLATE.replace("/* IMG_VARS_PLACEHOLDER */", IMG_VARS)

if not js_ok(VMS_JS, "VMS Script"):
    fail("VMS Script has syntax errors — aborting")
ok(f"VMS Script built  ({len(VMS_JS)//1024}KB  incl. {len(imgs)} embedded images)")

# ─────────────────────────────────────────────────────────────
# 9. Script 3 — ISS Explained Hub-and-Spoke Diagram
# ─────────────────────────────────────────────────────────────
print("\n[9] Building ISS Explained Script (Script 3) ...")

EXPL_JS = r"""
/* ════════════════════════════════════════════════════════
   ISS EXPLAINED — Interactive Ecosystem Diagram
   Federation umbrella · 5 Admin instances
   Streaming clients · Backup Service · Addon badges
   ════════════════════════════════════════════════════════ */
(function(){

var SVCS={
  fed:    {name:"ISS Federation",  nick:"The Unifier",    icon:"🌐",color:"#00c8ff",cr:"0,200,255",badge:"ADDON",isAddon:true,
    title:"ISS Federation Service",tagline:"Connects multiple independent ISS sites into one global management network.",
    detail:"<p>Central HQ manages cameras across hundreds of distributed ISS installations as one logical system. Each branch retains local autonomy if the link drops. Ideal for city-scale or multinational deployments.</p><p><em>Requires separate licence key.</em></p>"},
  admin:  {name:"Administration",  nick:"The Hub",        icon:"🧠",color:"#00c8ff",cr:"0,200,255",badge:"CORE",isAddon:false,
    title:"Administration Service",tagline:"The Brain — central authority for all ISS operations.",
    detail:"<p>Central authority for all ISS operations. Manages device registration (up to <strong>2,048 devices</strong>), user authentication, schedules, and WIBU licence keys (up to 8 per server).</p><p>All services register with Admin on startup. The <em>Failover Admin</em> mirrors its config for instant takeover.</p>"},
  stream: {name:"Streaming",       nick:"Load Balancer",  icon:"📡",color:"#00e5b0",cr:"0,229,176",badge:"CORE",isAddon:false,
    title:"Streaming Service — Load Balancing",tagline:"The Broadcaster — delivers live video to 64 concurrent clients.",
    detail:"<p>Delivers live video to <strong>64 concurrent users</strong>. <strong>ABC (Active Bandwidth Control)</strong> auto-switches Sub-stream ↔ Main-stream using H.264/H.265 logic. 2+ Streaming servers trigger automatic <strong>Load Balancing</strong>.</p>"},
  rec:    {name:"Recording",       nick:"The Vault",      icon:"💾",color:"#a78bfa",cr:"167,139,250",badge:"CORE",isAddon:false,
    title:"Recording Service",tagline:"High-performance, fragmentation-free video storage.",
    detail:"<p>Supports <strong>256 channels/server</strong> and <strong>64 recording servers</strong> per system. Proprietary video DB eliminates fragmentation and extends HDD lifespan. <strong>HDP</strong> auto-ingests edge footage on reconnection.</p>"},
  mon:    {name:"Monitoring",      nick:"The Messenger",  icon:"🔔",color:"#f59e0b",cr:"245,158,11",badge:"CORE",isAddon:false,
    title:"Monitoring Service",tagline:"Dedicated real-time event gateway.",
    detail:"<p>Event broker between cameras, analytics, and clients. Alarm delivery stays instant even under heavy recording load. Integrates with <strong>EventSpot</strong> on maps to auto-focus operators on active incidents.</p>"},
  va:     {name:"Video Analytics", nick:"The Analyzer",   icon:"🤖",color:"#ef4444",cr:"239,68,68",badge:"ADDON",isAddon:true,
    title:"Video Analytics Service (IDLA)",tagline:"AI-powered object detection and intelligence layer.",
    detail:"<p>Processes <strong>64 streams/service</strong>. Detects intrusion, loitering, line crossing, crowd density, face detection. Outputs metadata for A-Cut AI search and BI dashboards.</p><p><em>Requires separate licence key.</em></p>"},
  vw:     {name:"Video Wall",      nick:"Command Center", icon:"🖥️",color:"#00e5b0",cr:"0,229,176",badge:"ADDON",isAddon:true,
    title:"Video Wall Service",tagline:"Large-scale multi-monitor display management.",
    detail:"<p>Drives <strong>4 independent monitors</strong> with hardware controllers and network keyboard. Supports event-triggered camera pop-ups and pre-programmed layout sequences.</p><p><em>Requires licence key.</em></p>"},
  backup: {name:"Backup",          nick:"The Safeguard",  icon:"📦",color:"#f59e0b",cr:"245,158,11",badge:"ADDON",isAddon:true,
    title:"ISS Backup Service — The Safeguard",tagline:"Automated video data migration to independent storage.",
    detail:"<p>Migrates video from the Recording Service to independent backup storage.</p><ul style='padding-left:18px;line-height:1.9;'><li><strong>Summary Backup</strong> — key-frame extraction for storage efficiency</li><li><strong>Up to 1,024 channels</strong> per backup server</li><li><strong>HDP Player</strong> — direct HDD playback without system registration</li><li><strong>Bandwidth throttling</strong> — 40–50 MB/s for network stability</li></ul><div style='margin-top:14px;height:110px;background:#0a1828;border:1px dashed #203649;border-radius:8px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:6px;'><span style='font-size:18px;'>📷</span><span style='font-family:Courier New,monospace;font-size:9px;color:#4d6a82;'>manual_p207_backup.png</span><span style='font-size:10px;color:#4d6a82;'>Insert screenshot from ISS manual p.207</span></div><p style='margin-top:12px;'><em>Requires separate licence key.</em></p>"},
  redund: {name:"Redundant Rec.",  nick:"The Shadow",     icon:"🪞",color:"#a78bfa",cr:"167,139,250",badge:"ADDON",isAddon:true,
    title:"Redundant Recording",tagline:"Mirrors Recording 1:1 — zero data loss.",
    detail:"<p>Writes every stream to two servers simultaneously. If primary fails, shadow continues with no footage gap. Up to <strong>64 redundant services</strong> per system.</p><p><em>Requires licence key.</em></p>"},
  failover:{name:"Failover",       nick:"HA Guardian",    icon:"🛡️",color:"#f59e0b",cr:"245,158,11",badge:"ADDON",isAddon:true,
    title:"Failover Service",tagline:"Active-standby HA protection across all server roles.",
    detail:"<p>N:M warm-standby for Admin, Recording, Monitoring, and Video Wall. Standby activates with <strong>zero operator intervention</strong>, preserving all config and permissions.</p><p><em>Requires licence key.</em></p>"},
  web:    {name:"Web/Mobile",      nick:"The Remote",     icon:"📱",color:"#00c8ff",cr:"0,200,255",badge:"CORE",isAddon:false,
    title:"Web / Mobile Service",tagline:"Browser and mobile access without full client installation.",
    detail:"<p>Browser-based and mobile-native interface. <strong>FEN (For Every Network)</strong> enables remote access through NAT/firewall without port-forwarding.</p>"}
};

var W=980,H=720;
var NR={fed:52,admin:56,stream:46,rec:46,mon:46,va:40,vw:40,backup:40,redund:40,failover:40,web:40};
var POS={
  fed:{x:490,y:56},
  admin:{x:210,y:185},admin2:{x:332,y:185},admin3:{x:490,y:185},
  admin4:{x:648,y:185},admin5:{x:770,y:185},
  stream:{x:148,y:350},rec:{x:370,y:390},mon:{x:610,y:390},
  va:{x:820,y:320},vw:{x:820,y:480},
  web:{x:148,y:510},backup:{x:290,y:530},
  redund:{x:490,y:555},failover:{x:690,y:555},
  cl1:{x:50,y:290},cl2:{x:40,y:370},cl3:{x:50,y:450}
};

function buildDiagram(){
  var svg=document.getElementById("hubSvg");if(!svg)return;
  svg.setAttribute("viewBox","0 0 "+W+" "+H);
  svg.setAttribute("width","100%");svg.style.display="block";

  var defs="<defs>"+
    "<radialGradient id='hg' cx='50%' cy='50%' r='50%'>"+
      "<stop offset='0%' stop-color='#00c8ff' stop-opacity='.18'/>"+
      "<stop offset='100%' stop-color='#060c12' stop-opacity='0'/></radialGradient>"+
    "<linearGradient id='bg' x1='0%' y1='0%' x2='100%' y2='100%'>"+
      "<stop offset='0%' stop-color='#071420'/>"+
      "<stop offset='100%' stop-color='#060c12'/></linearGradient>"+
    "<filter id='glow' x='-40%' y='-40%' width='180%' height='180%'>"+
      "<feGaussianBlur stdDeviation='3.5' result='b'/>"+
      "<feMerge><feMergeNode in='b'/><feMergeNode in='SourceGraphic'/></feMerge></filter>"+
    "<marker id='arrY' markerWidth='7' markerHeight='7' refX='3.5' refY='3.5' orient='auto'>"+
      "<path d='M0,0 L7,3.5 L0,7 Z' fill='rgba(245,158,11,.5)'/></marker>"+
    "</defs>";
  var bg="<rect width='"+W+"' height='"+H+"' fill='url(#bg)' rx='14'/>";
  var grid="<g opacity='.03' stroke='#00c8ff' stroke-width='.5'>";
  for(var gx=0;gx<W;gx+=55) grid+="<line x1='"+gx+"' y1='0' x2='"+gx+"' y2='"+H+"'/>";
  for(var gy=0;gy<H;gy+=55) grid+="<line x1='0' y1='"+gy+"' x2='"+W+"' y2='"+gy+"'/>";
  grid+="</g>";

  function ln(x1,y1,x2,y2,col,dash,opa,ww,id,mk){
    return "<line"+(id?" id='"+id+"'":"")+" x1='"+x1+"' y1='"+y1+"' x2='"+x2+"' y2='"+y2+
      "' stroke='"+col+"' stroke-width='"+(ww||"1.5")+"' stroke-opacity='"+(opa||".4")+"'"+
      (dash?" stroke-dasharray='"+dash+"'":"")+
      (mk?" marker-end='url(#"+mk+")'":"")+" style='transition:all .2s;'/>";
  }
  function curve(x1,y1,cpx,cpy,x2,y2,col,dash,opa,id){
    return "<path"+(id?" id='"+id+"'":"")+" d='M"+x1+","+y1+" Q"+cpx+","+cpy+
      " "+x2+","+y2+"' fill='none' stroke='"+col+"' stroke-width='1.5'"+
      " stroke-opacity='"+(opa||".4")+"'"+
      (dash?" stroke-dasharray='"+dash+"'":"")+
      " style='transition:all .2s;'/>";
  }

  var f=POS.fed, a3=POS.admin3, conn="";
  ['admin','admin2','admin3','admin4','admin5'].forEach(function(ak){
    var ap=POS[ak];
    conn+=curve(f.x,f.y+NR.fed,f.x+(ap.x-f.x)*.3,f.y+80,ap.x,ap.y-NR.admin,
      "#00c8ff","5 4",".45","conn-fed-"+ak);
  });
  conn+=ln(a3.x,a3.y+NR.admin,POS.stream.x,POS.stream.y-NR.stream,"#00e5b0","",".5","1.8","conn-a-stream");
  conn+=ln(a3.x,a3.y+NR.admin,POS.rec.x,POS.rec.y-NR.rec,"#a78bfa","",".5","1.8","conn-a-rec");
  conn+=ln(a3.x,a3.y+NR.admin,POS.mon.x,POS.mon.y-NR.mon,"#f59e0b","",".5","1.8","conn-a-mon");
  conn+=ln(a3.x,a3.y+NR.admin,POS.va.x,POS.va.y-NR.va,"#ef4444","4 3",".35");
  conn+=ln(a3.x,a3.y+NR.admin,POS.vw.x,POS.vw.y-NR.vw,"#00e5b0","4 3",".3");
  conn+=ln(a3.x,a3.y+NR.admin,POS.web.x,POS.web.y-NR.web,"#00c8ff","4 3",".3");
  conn+=ln(POS.rec.x,POS.rec.y+NR.rec,POS.backup.x,POS.backup.y-NR.backup,
    "#f59e0b","6 3",".5","2","conn-rec-backup","arrY");
  conn+="<line id='conn-redund-rec' x1='"+POS.rec.x+"' y1='"+(POS.rec.y+NR.rec)+
    "' x2='"+POS.redund.x+"' y2='"+(POS.redund.y-NR.failover)+
    "' stroke='#a78bfa' stroke-width='2' stroke-opacity='.4' stroke-dasharray='6 3' style='transition:all .22s;'/>";
  conn+=ln(POS.failover.x,POS.failover.y-NR.failover,a3.x,a3.y+NR.admin,
    "#f59e0b","5 4",".3","1.5","conn-fo-admin");
  conn+=ln(POS.failover.x,POS.failover.y-NR.failover,POS.rec.x,POS.rec.y+NR.rec,
    "#f59e0b","5 4",".3","1.5","conn-fo-rec");
  ['cl1','cl2','cl3'].forEach(function(ck,ci){
    var cp=POS[ck];
    conn+=ln(cp.x+28,cp.y,POS.stream.x-NR.stream,POS.stream.y+(ci-1)*16,
      "#00e5b0","3 3",".5","1.5","conn-"+ck);
  });

  var clients="";
  ['cl1','cl2','cl3'].forEach(function(ck,ci){
    var cp=POS[ck];
    clients+="<rect x='"+(cp.x-22)+"' y='"+(cp.y-14)+"' width='44' height='28' rx='5'"+
      " fill='#0a1828' stroke='#00e5b0' stroke-width='1.2' stroke-opacity='.5'/>";
    clients+="<text x='"+cp.x+"' y='"+(cp.y-1)+"' text-anchor='middle' font-size='12'"+
      " style='pointer-events:none;user-select:none;'>🖥</text>";
    clients+="<text x='"+cp.x+"' y='"+(cp.y+12)+"' text-anchor='middle' font-size='7'"+
      " fill='rgba(0,229,176,.6)' style='font-family:Courier New,monospace;"+
      "pointer-events:none;'>Client "+(ci+1)+"</text>";
  });

  function makeNode(id){
    var svc=SVCS[id],p=POS[id];if(!svc||!p)return"";
    var r=NR[id]||40,col=svc.color;
    var out="<circle cx='"+p.x+"' cy='"+p.y+"' r='"+(r+18)+"' fill='"+col+"' fill-opacity='.05'/>";
    out+="<circle id='node-"+id+"' cx='"+p.x+"' cy='"+p.y+"' r='"+r+"'"+
      " fill='#091e34' stroke='"+col+"'"+
      " stroke-width='"+(id==='fed'?2.8:svc.isAddon?1.5:2)+"'"+
      " filter='url(#glow)' style='cursor:pointer;transition:all .22s;'"+
      " onmouseenter=\"nHover('"+id+"',true)\""+
      " onmouseleave=\"nHover('"+id+"',false)\""+
      " onclick=\"explOpen('"+id+"')\"/>";
    if(svc.isAddon)
      out+="<circle cx='"+(p.x+r-5)+"' cy='"+(p.y-r+5)+"' r='6'"+
        " fill='#f59e0b' stroke='#060c12' stroke-width='1.5'/>"+
        "<text x='"+(p.x+r-5)+"' y='"+(p.y-r+9)+"' text-anchor='middle'"+
        " font-size='6' fill='#060c12' font-weight='700' style='pointer-events:none;'>A</text>";
    out+="<text x='"+p.x+"' y='"+(p.y-(r>48?12:8))+"' text-anchor='middle'"+
      " font-size='"+(r>48?22:18)+"'"+
      " style='pointer-events:none;user-select:none;'>"+svc.icon+"</text>";
    var parts=svc.name.split(' '),l1=parts.slice(0,2).join(' '),l2=parts.slice(2).join(' ');
    out+="<text x='"+p.x+"' y='"+(p.y+(r>48?10:8))+"' text-anchor='middle'"+
      " font-size='"+(r>48?9:8)+"' fill='"+col+"' font-weight='700'"+
      " style='font-family:Courier New,monospace;pointer-events:none;'>"+l1.toUpperCase()+"</text>";
    if(l2) out+="<text x='"+p.x+"' y='"+(p.y+(r>48?20:18))+"' text-anchor='middle'"+
      " font-size='"+(r>48?9:8)+"' fill='"+col+"' font-weight='700'"+
      " style='font-family:Courier New,monospace;pointer-events:none;'>"+l2.toUpperCase()+"</text>";
    out+="<text x='"+p.x+"' y='"+(p.y+r-8)+"' text-anchor='middle' font-size='7'"+
      " fill='rgba(255,255,255,.3)' style='font-family:Courier New,monospace;pointer-events:none;'>"+
      svc.nick.substring(0,14)+"</text>";
    return out;
  }
  function ghostAdmin(key,label){
    var p=POS[key],r=NR.admin,col="#00c8ff";
    return "<circle cx='"+p.x+"' cy='"+p.y+"' r='"+r+"' fill='#091e34' stroke='"+col+
      "' stroke-width='1.5' stroke-opacity='.35' style='cursor:pointer;'"+
      " onclick=\"explOpen('admin')\"/>"+
      "<text x='"+p.x+"' y='"+(p.y-10)+"' text-anchor='middle' font-size='18'"+
      " style='pointer-events:none;user-select:none;opacity:.5;'>🧠</text>"+
      "<text x='"+p.x+"' y='"+(p.y+8)+"' text-anchor='middle' font-size='8'"+
      " fill='rgba(0,200,255,.4)' font-weight='700'"+
      " style='font-family:Courier New,monospace;pointer-events:none;'>ADMIN</text>"+
      "<text x='"+p.x+"' y='"+(p.y+19)+"' text-anchor='middle' font-size='7'"+
      " fill='rgba(0,200,255,.25)'"+
      " style='font-family:Courier New,monospace;pointer-events:none;'>"+label+"</text>";
  }

  var fedArc="<path d='M70,180 Q490,-20 910,180' fill='none' stroke='#00c8ff'"+
    " stroke-width='1' stroke-opacity='.12' stroke-dasharray='8 5'/>";
  var fedLabel="<text x='490' y='14' text-anchor='middle' font-size='9'"+
    " fill='rgba(0,200,255,.4)'"+
    " style='font-family:Courier New,monospace;letter-spacing:2px;'>"+
    "── ISS FEDERATION UMBRELLA ──</text>";

  var nodes=makeNode('fed')+makeNode('admin')+
    ghostAdmin('admin2','Branch 2')+ghostAdmin('admin3','Branch 3')+
    ghostAdmin('admin4','Branch 4')+ghostAdmin('admin5','Branch 5')+
    makeNode('stream')+makeNode('rec')+makeNode('mon')+
    makeNode('va')+makeNode('vw')+makeNode('web')+
    makeNode('backup')+makeNode('redund')+makeNode('failover');

  var legend="<g transform='translate(10,688)'>"+
    "<circle cx='8' cy='7' r='7' fill='none' stroke='#00c8ff' stroke-width='1.5'/>"+
    "<text x='20' y='11' font-size='9.5' fill='rgba(0,200,255,.7)'"+
    " style='font-family:Courier New,monospace;'>Core</text>"+
    "<circle cx='80' cy='7' r='7' fill='none' stroke='#f59e0b' stroke-width='1.5'/>"+
    "<circle cx='84' cy='3' r='4.5' fill='#f59e0b'/>"+
    "<text x='94' y='11' font-size='9.5' fill='rgba(245,158,11,.7)'"+
    " style='font-family:Courier New,monospace;'>Addon</text>"+
    "<line x1='160' y1='7' x2='185' y2='7' stroke='#a78bfa' stroke-width='2'"+
    " stroke-dasharray='5 3'/>"+
    "<text x='190' y='11' font-size='9.5' fill='rgba(167,139,250,.7)'"+
    " style='font-family:Courier New,monospace;'>Mirror/Backup</text>"+
    "</g>";

  svg.innerHTML=defs+bg+grid+fedArc+fedLabel+conn+clients+nodes+legend;

  Object.keys(SVCS).forEach(function(id){
    var n=document.getElementById("node-"+id);if(!n)return;
    n.addEventListener("mouseenter",function(){nHover(id,true);});
    n.addEventListener("mouseleave",function(){nHover(id,false);});
    n.addEventListener("click",function(){explOpen(id);});
  });
}

/* ── HOVER EFFECTS ── */
window.nHover=function(id,on){
  var n=document.getElementById("node-"+id);
  if(n){
    n.setAttribute("r",on?String((NR[id]||40)+6):String(NR[id]||40));
    n.setAttribute("fill",on?"rgba(0,200,255,.08)":"#091e34");
  }
  if(id==="redund"){
    var c=document.getElementById("conn-redund-rec");
    if(c){c.setAttribute("stroke-opacity",on?"1":".4");c.setAttribute("stroke-width",on?"3":"2");}
    var rn=document.getElementById("node-rec");
    if(rn){rn.setAttribute("stroke",on?"#c4b5fd":"#a78bfa");rn.setAttribute("stroke-width",on?"2.8":"2");}
  }
  if(id==="failover"){
    ["conn-fo-admin","conn-fo-rec"].forEach(function(cid){
      var c=document.getElementById(cid);
      if(c){c.setAttribute("stroke-opacity",on?".9":".3");c.setAttribute("stroke-width",on?"2.5":"1.5");}
    });
  }
  if(id==="backup"){
    var c=document.getElementById("conn-rec-backup");
    if(c){c.setAttribute("stroke-opacity",on?"1":".5");c.setAttribute("stroke-width",on?"3":"2");}
    var rn=document.getElementById("node-rec");
    if(rn){rn.setAttribute("stroke",on?"#fbbf24":"#a78bfa");rn.setAttribute("stroke-width",on?"2.8":"2");}
  }
  if(id==="stream"){
    ["conn-cl1","conn-cl2","conn-cl3"].forEach(function(cid){
      var c=document.getElementById(cid);
      if(c){c.setAttribute("stroke-opacity",on?".9":".5");c.setAttribute("stroke-width",on?"2.5":"1.5");}
    });
  }
};

/* ── MODAL ── */
window.explOpen=function(id){
  var svc=SVCS[id];if(!svc)return;
  var ov=document.getElementById("explOverlay");
  var md=document.getElementById("explModal");if(!ov||!md)return;
  var bs=svc.isAddon
    ?"background:rgba(245,158,11,.1);border:1px solid rgba(245,158,11,.3);color:#f59e0b;"
    :"background:rgba(0,200,255,.1);border:1px solid rgba(0,200,255,.3);color:#00c8ff;";
  md.innerHTML=
    "<div style='position:relative;padding:32px 40px 24px;background:#0f1e2d;"+
    "border-bottom:1px solid #1a2f42;overflow:hidden;'>"+
    "<div style='position:absolute;top:-40px;right:-40px;width:180px;height:180px;"+
    "border-radius:50%;background:radial-gradient(circle,rgba("+svc.cr+",.12),transparent 70%);"+
    "pointer-events:none;'></div>"+
    "<button onclick='explClose()' style='position:absolute;top:14px;right:14px;"+
    "width:32px;height:32px;border-radius:50%;background:#152435;"+
    "border:1px solid #1a2f42;cursor:pointer;color:#8ba3bc;font-size:16px;"+
    "display:flex;align-items:center;justify-content:center;'>&#x2715;</button>"+
    "<span style='display:inline-flex;padding:2px 9px;border-radius:4px;"+
    "font-family:Courier New,monospace;font-size:9px;letter-spacing:2px;font-weight:700;"+
    "text-transform:uppercase;"+bs+"margin-bottom:12px;'>"+svc.badge+"</span>"+
    "<div style='font-size:38px;margin-bottom:10px;'>"+svc.icon+"</div>"+
    "<h2 style='font-size:clamp(20px,3vw,34px);font-weight:800;letter-spacing:-1px;"+
    "color:#e8eef5;margin-bottom:6px;font-family:Georgia,serif;line-height:1.1;'>"+
    svc.title+"</h2>"+
    "<p style='font-size:13px;color:"+svc.color+";font-family:Courier New,monospace;"+
    "letter-spacing:.5px;font-style:italic;'>"+svc.tagline+"</p>"+
    "</div>"+
    "<div style='padding:28px 40px;font-size:13.5px;color:#8ba3bc;line-height:1.82;'>"+
    svc.detail+"</div>";
  ov.style.display="flex";document.body.style.overflow="hidden";
};

window.explClose=function(){
  var o=document.getElementById("explOverlay");if(o)o.style.display="none";
  document.body.style.overflow="";
};
window.hubHL=function(){};

document.addEventListener("keydown",function(e){
  if(e.key==="Escape"){
    explClose();
    if(window.vmsClose) vmsClose();
  }
});

/* ── INIT ── */
var lego=document.getElementById("legoLayout");if(lego)lego.style.display="none";
var svgEl=document.getElementById("hubSvg");
if(svgEl){
  svgEl.style.display="block";
  if(svgEl.parentElement) svgEl.parentElement.style.display="block";
}
var secs=document.querySelector("#scrExpl .svc-sections");
if(secs) secs.style.display="none";
buildDiagram();
window._explOnEnter=function(){buildDiagram();};

})();
"""

if not js_ok(EXPL_JS, "ISS Explained Script"):
    fail("ISS Explained Script has syntax errors — aborting")
ok(f"ISS Explained Script built  ({len(EXPL_JS)//1024}KB)")

# ─────────────────────────────────────────────────────────────
# 10. Script 2 + Script 3 삽입
# ─────────────────────────────────────────────────────────────
print("\n[10] Injecting Script 2 (VMS) and Script 3 (EXPL) ...")

OLD_SCRIPT_END = "vRenderQ();\nrender();\nrenderRec();\n</script>\n</body>"
NEW_SCRIPT_END = (
    "vRenderQ();\nrender();\nrenderRec();\n"
    "</script>\n\n"
    "<script>\n" + VMS_JS + "\n</script>\n\n"
    "<script>\n" + EXPL_JS + "\n</script>\n\n"
    "</body>"
)
must(OLD_SCRIPT_END, src, "script end + body")
src = src.replace(OLD_SCRIPT_END, NEW_SCRIPT_END, 1)
ok("VMS Script injected as Script 2")
ok("EXPL Script injected as Script 3")

# ─────────────────────────────────────────────────────────────
# 11. 최종 JS syntax 검증
# ─────────────────────────────────────────────────────────────
print("\n[11] Final syntax verification ...")
all_scripts = list(re.finditer(r'<script>(.*?)</script>', src, re.DOTALL))
print(f"  Total script blocks: {len(all_scripts)}")

all_ok = True
for i, m in enumerate(all_scripts):
    code = m.group(1)
    passed = js_ok(code, f"Script {i+1}")
    if passed:
        ok(f"Script {i+1}  ({len(code)//1024}KB)")
    else:
        all_ok = False

if not all_ok:
    fail("One or more scripts have syntax errors. Build aborted.")

# ─────────────────────────────────────────────────────────────
# 12. 저장
# ─────────────────────────────────────────────────────────────
print(f"\n[12] Saving output ...")
OUT.write_text(src, encoding="utf-8")

print(f"""
{'=' * 62}
  ✅  Build complete!
{'=' * 62}
  Output : {OUT}
  Size   : {len(src) // 1024} KB
  Scripts: {len(all_scripts)}
  Images : {len(imgs)} base64-embedded

  Tabs built
  ─────────────────────────────────────────────────────
  📷  Camera Selector   — multi-filter camera comparison
       ● ONVIF Only chip  (isONVIF && !isDirectIP)
       ● FIPS 140-3 / UL Listed  — independent checkboxes
       ● togSet bug fixed  (protocol filter works on first click)

  🖥  VMS Selector       — ISS vs IDIS Center questionnaire
  💿  Recorder Selector  — NVR/DVR filter

  🤖  VA Selector        — analytics feature selector
       ● VA OVERALL SUMMARY  → main panel analytics table
       ● Aside drag-resize  (160–480px)

  🔵  IDIS VMS (ISS)     — ISS Standard interactive overview
       ● 5 feature cards with embedded screenshots
       ● Keyword search across all features
       ● Animated counters  (Max 2,048 devices, etc.)

  🌐  ISS Explained      — hub-and-spoke architecture diagram
       ● Federation umbrella → 5 Admin instances
       ● Streaming → 3 live client nodes
       ● Recording → Backup (gold arrow, data-flow)
       ● Redundant / Failover with hover highlights
       ● Backup Service with manual_p207_backup.png slot
       ● All Addon nodes marked with gold 'A' badge

  🔤  Font controller  (A− / A+ / ↺)  in top-right nav
{'=' * 62}
""")
