"""
KY_Fantasy → Fantasy/dashboard.html 생성기
실행: python web/generate_dashboard.py
"""
import json, os, re
from pathlib import Path
from datetime import datetime

BASE   = Path(__file__).parent.parent          # KY_Fantasy/
OUT    = Path("C:/Users/10_17/Desktop/Fantasy/dashboard.html")
IMG    = "../KY_Fantasy/web/static/images"     # dashboard.html 기준 상대경로

CHAR_IMAGES = {
    "seo-yuna":   f"{IMG}/seo-yoona.jpg",
    "haewol":     f"{IMG}/haewol.jpg",
    "kang-doyun": f"{IMG}/kang-doyun.jpg",
    "seo-daebi":  f"{IMG}/seo-daebi.jpg",
    "yeonsangun": f"{IMG}/yeonsangun.jpg",
    "im-sahong":  f"{IMG}/Imsahong.jpg",
}
CHAR_ORDER = ["seo-yuna","kang-doyun","haewol","seo-daebi","yeonsangun","im-sahong","samdori"]

def load_json(path):
    try: return json.loads((BASE / path).read_text(encoding="utf-8"))
    except: return {}

def read_text(path):
    try: return (BASE / path).read_text(encoding="utf-8")
    except: return ""

def esc(s):
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"','&quot;')

def md_to_html(md):
    lines, out, in_ul = md.splitlines(), [], False
    for line in lines:
        if re.match(r'^#{1}\s', line):
            if in_ul: out.append("</ul>"); in_ul=False
            out.append(f"<h2>{esc(line.lstrip('#').strip())}</h2>")
        elif re.match(r'^#{2,}\s', line):
            if in_ul: out.append("</ul>"); in_ul=False
            out.append(f"<h3>{esc(line.lstrip('#').strip())}</h3>")
        elif re.match(r'^- ', line):
            if not in_ul: out.append("<ul>"); in_ul=True
            inner = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', esc(line[2:]))
            out.append(f"<li>{inner}</li>")
        elif re.match(r'^---+$', line):
            if in_ul: out.append("</ul>"); in_ul=False
            out.append("<hr>")
        elif line.strip():
            if in_ul: out.append("</ul>"); in_ul=False
            inner = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', esc(line))
            out.append(f"<p>{inner}</p>")
    if in_ul: out.append("</ul>")
    return "\n".join(out)

def get_chapters():
    chaps = []
    for f in sorted((BASE / "story/chapters").glob("*.md")):
        content = f.read_text(encoding="utf-8")
        num = int(f.stem.replace("chapter-",""))
        lines = [l for l in content.splitlines() if l.strip()]
        title = lines[0].lstrip("#").strip() if lines else f.stem
        preview = " ".join(lines[1:3])[:120] if len(lines)>1 else ""
        mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d")
        chaps.append({"num": num, "title": title, "chars": len(content),
                      "preview": preview, "date": mtime, "content": content})
    return chaps

def get_characters():
    chars_dir = BASE / "bible/characters"
    files = {f.stem: f for f in chars_dir.glob("*.md")}
    result = []
    ordered = [k for k in CHAR_ORDER if k in files] + [k for k in files if k not in CHAR_ORDER]
    for stem in ordered:
        content = files[stem].read_text(encoding="utf-8")
        first = content.splitlines()[0].lstrip("#").strip()
        name, role = (first.split(" — ",1) if " — " in first else (first,""))
        result.append({"stem":stem,"name":name,"role":role,
                       "image": CHAR_IMAGES.get(stem,""),
                       "html": md_to_html(content)})
    return result

def char_cards_html(chars):
    cards = []
    for c in chars:
        img_tag = (f'<img class="cp-img" src="{c["image"]}" alt="{esc(c["name"])}">'
                   if c["image"] else '<div class="cp-placeholder">👤</div>')
        cards.append(f'''
      <div class="char-card" data-name="{esc(c["name"])}" data-role="{esc(c["role"])}"
           data-image="{c["image"]}" onclick="openModal(this)">
        {img_tag}
        <div class="cp-label">
          <div class="cp-name">{esc(c["name"])}</div>
          <div class="cp-role">{esc(c["role"])}</div>
        </div>
        <div class="cp-body" style="display:none">{c["html"]}</div>
      </div>''')
    return "\n".join(cards)

def chapter_content_html(content):
    """마크다운 챕터 내용을 읽기 좋은 HTML로 변환"""
    lines, out = content.splitlines(), []
    for line in lines:
        if line.startswith("# "):
            out.append(f'<h2 class="chap-modal-title">{esc(line[2:].strip())}</h2>')
        elif line.strip() == "---":
            out.append('<hr class="chap-sep">')
        elif line.strip() == "":
            out.append('<p class="chap-blank"></p>')
        else:
            inner = re.sub(r'\*(.+?)\*', r'<em>\1</em>', esc(line))
            out.append(f'<p class="chap-line">{inner}</p>')
    return "\n".join(out)

def chapter_rows_html(chaps):
    if not chaps: return '<tr><td colspan="4" class="td-empty">아직 작성된 장이 없습니다</td></tr>'
    rows = []
    for c in sorted(chaps, key=lambda x: x["num"], reverse=True):
        content_html = chapter_content_html(c["content"])
        rows.append(f'''
    <tr class="chap-row" onclick="openChapModal({c['num']})">
      <td class="td-n"><span class="num-badge">제 {c["num"]} 장</span></td>
      <td class="td-p">{esc(c["preview"])}</td>
      <td class="td-w">{c["chars"]:,}자</td>
      <td class="td-d">{c["date"]}</td>
    </tr>
    <script type="application/json" id="chap-data-{c['num']}">{json.dumps({"title": esc(c["title"]), "chars": c["chars"], "date": c["date"], "html": content_html})}</script>''')
    return "\n".join(rows)

def recent_entries_html(chaps):
    if not chaps: return '<p class="empty-note">아직 작성된 장이 없습니다</p>'
    rows = []
    for c in sorted(chaps, key=lambda x: x["num"], reverse=True)[:8]:
        rows.append(f'''
    <div class="scroll-entry">
      <span class="scroll-n">제 {c["num"]} 장</span>
      <span class="scroll-p">{esc(c["preview"][:80])}</span>
      <span class="scroll-w">{c["chars"]:,}자</span>
      <span class="scroll-d">{c["date"]}</span>
    </div>''')
    return "\n".join(rows)

def chart_data(chaps):
    s = sorted(chaps, key=lambda x: x["num"])
    labels = json.dumps([f"{c['num']}장" for c in s])
    data   = json.dumps([c["chars"] for c in s])
    return labels, data

def main():
    progress = load_json("planning/plot-progress.json")
    chaps    = get_chapters()
    chars    = get_characters()

    title   = progress.get("novel_title","천서의 아이")
    total   = progress.get("total_chapters", 25)
    done    = progress.get("completed_chapters", len(chaps))
    phase   = progress.get("story_phase","—")
    pct     = round(done / total * 100, 1)
    total_chars = sum(c["chars"] for c in chaps)
    avg_chars   = round(total_chars / len(chaps)) if chaps else 0
    labels, chart_data_val = chart_data(chaps)
    now_str = datetime.now().strftime("%Y년 %m월 %d일  %H:%M")

    status_seals = {
        "세계관 · 架構":  ("완 료","seal-on") if (BASE/"bible/structure.md").exists() else ("미 완","seal-off"),
        "캐릭터 상태":    ("완 료","seal-on") if chars else ("없 음","seal-off"),
        "챕터 목차":      ("완 료","seal-on") if chaps else ("미 완","seal-off"),
        "글로벌 요약":    ("완 료","seal-on") if (BASE/"timeline/history.md").exists() else ("없 음","seal-off"),
    }
    seals_html = "\n".join(
        f'<div class="status-row"><span class="status-row-label">{k}</span>'
        f'<span class="seal {v}">{l}</span></div>'
        for k,(l,v) in status_seals.items()
    )

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>작업현황 · {esc(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root {{
  --bg:#07060a; --s1:#0e0c10; --s2:#141118; --s3:#1c1822; --s4:#241f2c;
  --gold:#c49a3c; --gold2:#9a7628; --gold3:#4a3812; --gold4:#2a2008;
  --crimson:#b83028; --crim2:#7a1e18; --crim3:#3a0e0c;
  --jade:#4a8a68; --jade2:#2e5a44;
  --t1:#ddd0b8; --t2:#a09070; --t3:#5a4e38; --t4:#302820;
  --serif:'Noto Serif KR','Batang','바탕',Georgia,serif;
  --sans:'Malgun Gothic','Apple SD Gothic Neo',sans-serif;
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
html{{scrollbar-width:thin;scrollbar-color:var(--gold3) var(--bg);}}
::-webkit-scrollbar{{width:5px;height:5px;}}
::-webkit-scrollbar-track{{background:var(--bg);}}
::-webkit-scrollbar-thumb{{background:var(--gold3);border-radius:2px;}}
body{{font-family:var(--sans);background:var(--bg);color:var(--t1);min-height:100vh;
  background-image:
    repeating-linear-gradient(0deg,transparent,transparent 47px,rgba(74,56,18,.06) 48px),
    repeating-linear-gradient(90deg,transparent,transparent 47px,rgba(74,56,18,.04) 48px);}}

/* 헤더 */
.header{{position:relative;overflow:hidden;padding:52px 56px 44px;
  background:radial-gradient(ellipse 70% 100% at 80% 50%,rgba(42,28,8,.6) 0%,transparent 70%),
    radial-gradient(ellipse 50% 80% at 10% 30%,rgba(30,14,30,.5) 0%,transparent 60%),var(--s1);
  border-bottom:1px solid var(--gold3);}}
.header-deco{{position:absolute;right:40px;top:50%;transform:translateY(-50%);
  font-family:var(--serif);font-size:260px;font-weight:700;color:transparent;
  -webkit-text-stroke:1px rgba(196,154,60,.07);line-height:1;pointer-events:none;}}
.header-eyebrow{{font-family:var(--serif);font-size:10px;letter-spacing:5px;color:var(--gold2);
  text-transform:uppercase;margin-bottom:16px;}}
.header h1{{font-family:var(--serif);font-size:38px;font-weight:600;letter-spacing:.04em;
  color:var(--t1);text-shadow:0 2px 20px rgba(196,154,60,.15);margin-bottom:14px;line-height:1.3;}}
.header-genre{{display:inline-block;font-family:var(--serif);font-size:11px;letter-spacing:3px;
  color:var(--gold);border:1px solid var(--gold2);padding:4px 16px;margin-bottom:22px;}}
.header-rule{{width:100%;height:1px;
  background:linear-gradient(90deg,transparent,var(--gold3) 20%,var(--gold3) 80%,transparent);
  margin:20px 0 16px;}}
.header-meta{{display:flex;flex-wrap:wrap;gap:28px;font-size:11px;color:var(--t3);letter-spacing:.5px;}}
.header-meta span{{display:flex;align-items:center;gap:6px;}}
.meta-label{{color:var(--t3);}} .meta-val{{color:var(--t2);}}

/* 레이아웃 */
.wrap{{max-width:1360px;margin:0 auto;padding:40px 40px 80px;}}
.row-4{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px;}}
.row-2{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px;}}
.row-1{{margin-bottom:20px;}}

/* 카드 */
.card{{position:relative;background:var(--s2);border:1px solid var(--gold3);padding:22px 24px;
  box-shadow:inset 0 0 0 3px var(--s2),inset 0 0 0 4px var(--gold4);}}
.card::before,.card::after{{content:'';position:absolute;width:14px;height:14px;
  border-color:var(--gold2);border-style:solid;opacity:.6;}}
.card::before{{top:5px;left:5px;border-width:1px 0 0 1px;}}
.card::after{{bottom:5px;right:5px;border-width:0 1px 1px 0;}}
.card-corner-tr,.card-corner-bl{{position:absolute;width:14px;height:14px;
  border-color:var(--gold2);border-style:solid;opacity:.6;pointer-events:none;}}
.card-corner-tr{{top:5px;right:5px;border-width:1px 1px 0 0;}}
.card-corner-bl{{bottom:5px;left:5px;border-width:0 0 1px 1px;}}

/* 섹션 제목 */
.sec-title{{font-family:var(--serif);font-size:13px;font-weight:500;letter-spacing:3px;
  color:var(--t2);margin-bottom:18px;display:flex;align-items:center;gap:10px;}}
.sec-title::before{{content:'◆';color:var(--gold2);font-size:8px;}}
.sec-title::after{{content:'';flex:1;height:1px;background:linear-gradient(90deg,var(--gold3),transparent);}}

/* 통계 */
.stat-eyebrow{{font-size:10px;letter-spacing:3px;color:var(--t3);text-transform:uppercase;
  margin-bottom:10px;font-family:var(--serif);}}
.stat-val{{font-family:var(--serif);font-size:44px;font-weight:300;line-height:1;
  color:var(--gold);margin-bottom:8px;letter-spacing:-.02em;}}
.stat-val.jade{{color:var(--jade);}} .stat-val.crimson{{color:var(--crimson);}} .stat-val.pearl{{color:var(--t1);}}
.stat-sub{{font-size:11px;color:var(--t3);letter-spacing:.5px;}}
.prog-row{{display:flex;align-items:center;gap:10px;margin-top:12px;}}
.prog-track{{flex:1;height:3px;background:var(--gold4);position:relative;overflow:hidden;}}
.prog-fill{{height:100%;background:linear-gradient(90deg,var(--crim2),var(--gold));
  transition:width .8s cubic-bezier(.4,0,.2,1);position:relative;}}
.prog-fill::after{{content:'';position:absolute;right:0;top:-2px;width:5px;height:7px;
  background:var(--gold);clip-path:polygon(0 0,100% 50%,0 100%);}}
.prog-pct{{font-size:10px;color:var(--gold2);font-family:var(--serif);letter-spacing:1px;min-width:36px;text-align:right;}}

/* 도장 */
.seal{{display:inline-flex;align-items:center;justify-content:center;
  font-family:var(--serif);font-size:11px;letter-spacing:2px;
  padding:4px 12px;min-width:64px;border:1.5px solid;}}
.seal-on{{color:var(--crimson);border-color:var(--crimson);background:var(--crim3);
  text-shadow:0 0 8px rgba(184,48,40,.3);}}
.seal-off{{color:var(--t3);border-color:var(--t4);background:transparent;}}

/* 작업 현황 */
.status-grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px;}}
.status-row{{display:flex;align-items:center;justify-content:space-between;
  padding:12px 14px;background:var(--s3);border:1px solid var(--t4);}}
.status-row-label{{font-size:12px;color:var(--t2);letter-spacing:.5px;}}

/* 최근 장 */
.scroll-entry{{display:flex;align-items:baseline;gap:12px;padding:11px 0;border-bottom:1px solid var(--t4);}}
.scroll-entry:last-child{{border-bottom:none;}}
.scroll-n{{font-family:var(--serif);font-size:12px;color:var(--gold2);min-width:64px;letter-spacing:1px;}}
.scroll-p{{flex:1;font-size:12px;color:var(--t2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}
.scroll-w{{font-size:11px;color:var(--t3);min-width:70px;text-align:right;letter-spacing:.5px;}}
.scroll-d{{font-size:10px;color:var(--t3);min-width:72px;text-align:right;}}

/* 차트 */
.chart-wrap{{position:relative;height:160px;}}

/* 전체 장 표 */
.chap-table{{width:100%;border-collapse:collapse;}}
.chap-table thead th{{font-family:var(--serif);font-size:10px;letter-spacing:3px;color:var(--t3);
  text-align:left;padding:0 12px 12px;border-bottom:1px solid var(--gold3);}}
.chap-table tbody td{{padding:10px 12px;border-bottom:1px solid var(--t4);vertical-align:middle;}}
.chap-table tbody tr:hover td{{background:rgba(196,154,60,.04);}}
.num-badge{{display:inline-block;font-family:var(--serif);font-size:11px;color:var(--gold2);
  border:1px solid var(--gold3);padding:2px 8px;letter-spacing:1px;white-space:nowrap;}}
.td-n{{width:90px;}} .td-p{{color:var(--t2);font-size:12px;max-width:320px;overflow:hidden;
  text-overflow:ellipsis;white-space:nowrap;}}
.td-w{{text-align:right;font-family:var(--serif);font-size:12px;color:var(--t2);width:100px;letter-spacing:.5px;}}
.td-d{{text-align:right;font-size:11px;color:var(--t3);width:90px;}}
.td-empty{{text-align:center;color:var(--t3);padding:36px;font-family:var(--serif);font-size:13px;letter-spacing:2px;}}

/* 캐릭터 그리드 */
.char-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:.75rem;padding:.5rem 0;}}
.char-card{{display:flex;flex-direction:column;align-items:center;text-align:center;
  border:1px solid var(--gold3);border-radius:8px;background:var(--s3);
  overflow:hidden;cursor:pointer;transition:box-shadow .2s,transform .15s;}}
.char-card:hover{{box-shadow:0 6px 20px rgba(0,0,0,.5);transform:translateY(-2px);}}
.cp-img{{width:100%;aspect-ratio:2/3;object-fit:cover;object-position:top center;display:block;}}
.cp-placeholder{{width:100%;aspect-ratio:2/3;background:var(--s4);
  display:flex;align-items:center;justify-content:center;font-size:2.5rem;}}
.cp-label{{padding:.4rem .3rem .5rem;border-top:2px solid var(--gold3);width:100%;}}
.cp-name{{font-weight:bold;color:var(--gold);font-size:.8rem;line-height:1.3;font-family:var(--serif);}}
.cp-role{{font-size:.68rem;color:var(--jade);margin-top:.15rem;}}

/* 모달 */
.modal-backdrop{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:100;
  align-items:center;justify-content:center;}}
.modal-backdrop.open{{display:flex;}}
.modal{{background:var(--s1);border:1px solid var(--gold3);border-radius:4px;
  width:min(780px,95vw);max-height:90vh;
  display:flex;flex-direction:row;overflow:hidden;
  box-shadow:0 16px 64px rgba(0,0,0,.6);}}
.modal-face{{width:260px;flex-shrink:0;background:var(--s2);
  display:flex;align-items:stretch;
  border-right:1px solid var(--gold3);overflow:hidden;}}
.modal-face-img{{width:100%;height:100%;object-fit:cover;object-position:top center;display:block;}}
.modal-face-placeholder{{width:100%;display:flex;align-items:center;justify-content:center;
  font-size:5rem;color:var(--t3);}}
.modal-right{{flex:1;display:flex;flex-direction:column;overflow:hidden;}}
.modal-header{{display:flex;align-items:center;gap:.8rem;padding:1.1rem 1.3rem .8rem;
  border-bottom:1px solid var(--gold3);background:var(--s1);}}
.modal-name{{font-family:var(--serif);font-size:1.1rem;font-weight:600;color:var(--gold);flex:1;}}
.modal-role{{font-size:.78rem;color:var(--jade);margin-top:.2rem;}}
.modal-close{{background:none;border:none;font-size:1.3rem;cursor:pointer;
  color:var(--t3);padding:.25rem .5rem;border-radius:4px;}}
.modal-close:hover{{background:var(--s3);color:var(--t1);}}
.modal-body{{padding:1rem 1.3rem 1.4rem;overflow-y:auto;flex:1;
  font-size:.88rem;color:var(--t2);line-height:1.8;}}
.modal-body h2,.modal-body h3{{color:var(--gold2);margin:1rem 0 .4rem;font-size:.95rem;
  font-family:var(--serif);letter-spacing:1px;}}
.modal-body h2:first-child{{display:none;}}
.modal-body p{{margin:.3rem 0;}}
.modal-body ul{{padding-left:1.2rem;margin:.3rem 0;}}
.modal-body li{{line-height:1.8;}}
.modal-body strong{{color:var(--t1);}}
.modal-body hr{{border:none;border-top:1px solid var(--t4);margin:.7rem 0;}}

/* 챕터 행 클릭 */
.chap-row{{cursor:pointer;}}
.chap-row:hover td{{background:rgba(196,154,60,.08)!important;}}

/* 챕터 모달 */
.chap-modal-backdrop{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:200;
  align-items:center;justify-content:center;}}
.chap-modal-backdrop.open{{display:flex;}}
.chap-modal{{background:var(--s1);border:1px solid var(--gold3);border-radius:4px;
  width:min(720px,94vw);max-height:90vh;display:flex;flex-direction:column;
  box-shadow:0 16px 64px rgba(0,0,0,.7);overflow:hidden;}}
.chap-modal-head{{display:flex;align-items:center;gap:1rem;
  padding:1.1rem 1.4rem;border-bottom:1px solid var(--gold3);flex-shrink:0;}}
.chap-modal-num{{font-family:var(--serif);font-size:.75rem;color:var(--gold2);
  letter-spacing:2px;border:1px solid var(--gold3);padding:3px 10px;white-space:nowrap;}}
.chap-modal-info{{flex:1;}}
.chap-modal-htitle{{font-family:var(--serif);font-size:1.05rem;color:var(--t1);font-weight:500;}}
.chap-modal-meta{{font-size:.75rem;color:var(--t3);margin-top:.2rem;letter-spacing:.5px;}}
.chap-modal-close{{background:none;border:none;font-size:1.3rem;cursor:pointer;
  color:var(--t3);padding:.25rem .5rem;border-radius:4px;}}
.chap-modal-close:hover{{background:var(--s3);color:var(--t1);}}
.chap-modal-body{{overflow-y:auto;padding:2rem 2.4rem 2.4rem;flex:1;color:#e8e0d0;}}
.chap-modal-title{{font-family:var(--serif);font-size:1.3rem;color:var(--gold);
  margin-bottom:1.4rem;letter-spacing:.05em;}}
.chap-sep{{border:none;border-top:1px solid var(--t4);margin:1rem 0;}}
.chap-blank{{height:.6rem;}}
.chap-line{{font-family:var(--serif);font-size:.95rem;color:#e8e0d0;
  line-height:2.1;letter-spacing:.03em;margin:0;}}
.chap-line em{{color:#fff;font-style:italic;}}

/* 빈 상태 */
.empty-note{{font-family:var(--serif);font-size:12px;color:var(--t3);
  padding:18px 0;letter-spacing:1px;text-align:center;}}

/* 푸터 */
.footer{{margin-top:60px;padding-top:28px;border-top:1px solid var(--gold3);text-align:center;}}
.footer-inner{{display:inline-flex;align-items:center;gap:20px;
  font-family:var(--serif);font-size:11px;color:var(--t3);letter-spacing:2px;}}
.footer-sep{{color:var(--gold3);}}

/* 반응형 */
@media(max-width:1200px){{.row-4{{grid-template-columns:repeat(3,1fr)!important;}}}}
@media(max-width:960px){{
  .row-4{{grid-template-columns:1fr 1fr!important;}} .row-2{{grid-template-columns:1fr;}}
  .header{{padding:36px 28px 32px;}} .wrap{{padding:28px 20px 60px;}}
  .header-deco{{font-size:160px;right:10px;}} .header h1{{font-size:28px;}}
}}
@media(max-width:600px){{.row-4{{grid-template-columns:1fr;}} .stat-val{{font-size:36px;}}}}
</style>
</head>
<body>

<header class="header">
  <div class="header-deco">天</div>
  <p class="header-eyebrow">Fantasy Novel · 作業現況</p>
  <h1>{esc(title)}</h1>
  <span class="header-genre">역사 판타지</span>
  <div class="header-rule"></div>
  <div class="header-meta">
    <span><span class="meta-label">진행</span><span class="meta-val">{done} / {total} 장 ({pct}%)</span></span>
    <span><span class="meta-label">총 자수</span><span class="meta-val">{total_chars:,}자</span></span>
    <span><span class="meta-label">현재 막</span><span class="meta-val">{esc(phase)}</span></span>
    <span><span class="meta-label">集筆 모델</span><span class="meta-val">Claude Sonnet 4.6</span></span>
    <span><span class="meta-label">생성 일시</span><span class="meta-val">{now_str}</span></span>
  </div>
</header>

<div class="wrap">

  <div class="row-4" style="grid-template-columns:repeat(5,1fr);">
    <div class="card"><div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="stat-eyebrow">完成 章</p>
      <p class="stat-val">{done}</p>
      <p class="stat-sub">목표 {total} 장</p>
      <div class="prog-row"><div class="prog-track"><div class="prog-fill" style="width:{pct}%"></div></div>
      <span class="prog-pct">{pct}%</span></div>
    </div>
    <div class="card"><div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="stat-eyebrow">總 字數</p>
      <p class="stat-val jade">{total_chars:,}</p>
      <p class="stat-sub">평균 {avg_chars:,}자 / 장</p>
    </div>
    <div class="card"><div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="stat-eyebrow">推定 完成 字數</p>
      <p class="stat-val pearl">{avg_chars * total:,}</p>
      <p class="stat-sub">평균 자수 기준</p>
    </div>
    <div class="card"><div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="stat-eyebrow">章當 目標 字數</p>
      <p class="stat-val pearl">6,500</p>
      <p class="stat-sub">5,000 – 8,000자</p>
    </div>
    <div class="card"><div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="stat-eyebrow">잔여 章</p>
      <p class="stat-val crimson">{total - done}</p>
      <p class="stat-sub">현재: {esc(phase[:8])}</p>
    </div>
  </div>

  <div class="row-1">
    <div class="card"><div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="sec-title">작업 파일 현황</p>
      <div class="status-grid">
        {seals_html}
      </div>
    </div>
  </div>

  <div class="row-1">
    <div class="card"><div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="sec-title">장별 자수</p>
      <div class="chart-wrap"><canvas id="chapterChart"></canvas></div>
    </div>
  </div>

  <div class="row-1">
    <div class="card"><div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="sec-title">캐릭터 · 人物</p>
      <div class="char-grid">
        {char_cards_html(chars)}
      </div>
    </div>
  </div>

  <div class="row-1">
    <div class="card"><div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="sec-title">전체 장 목록 · 章目錄</p>
      <div style="overflow-x:auto;">
        <table class="chap-table">
          <thead><tr><th>장 번호</th><th>내용 미리보기</th>
          <th style="text-align:right;">자수</th><th style="text-align:right;">수정일</th></tr></thead>
          <tbody>{chapter_rows_html(chaps)}</tbody>
        </table>
      </div>
    </div>
  </div>

</div>

<div class="footer">
  <div class="footer-inner">
    <span>天書의 아이</span><span class="footer-sep">·</span>
    <span>Claude Sonnet 4.6</span><span class="footer-sep">·</span>
    <span>{now_str} 생성</span>
  </div>
</div>

<!-- 챕터 모달 -->
<div class="chap-modal-backdrop" id="chapModal" onclick="closeChapOnBackdrop(event)">
  <div class="chap-modal">
    <div class="chap-modal-head">
      <span class="chap-modal-num" id="chapNum"></span>
      <div class="chap-modal-info">
        <div class="chap-modal-htitle" id="chapTitle"></div>
        <div class="chap-modal-meta" id="chapMeta"></div>
      </div>
      <button class="chap-modal-close" onclick="closeChapModal()">✕</button>
    </div>
    <div class="chap-modal-body" id="chapBody"></div>
  </div>
</div>

<!-- 캐릭터 모달 -->
<div class="modal-backdrop" id="charModal" onclick="closeOnBackdrop(event)">
  <div class="modal">
    <div class="modal-face" id="modalFace"></div>
    <div class="modal-right">
      <div class="modal-header">
        <div style="flex:1">
          <div class="modal-name" id="modalName"></div>
          <div class="modal-role" id="modalRole"></div>
        </div>
        <button class="modal-close" onclick="closeModal()">✕</button>
      </div>
      <div class="modal-body" id="modalBody"></div>
    </div>
  </div>
</div>

<script>
const chartLabels = {labels};
const chartData   = {chart_data_val};

const ctx = document.getElementById('chapterChart').getContext('2d');
new Chart(ctx, {{
  type: 'bar',
  data: {{
    labels: chartLabels,
    datasets: [{{
      label: '자수',
      data: chartData,
      backgroundColor: 'rgba(196,154,60,.25)',
      borderColor: 'rgba(196,154,60,.8)',
      borderWidth: 1,
    }}]
  }},
  options: {{
    responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ ticks: {{ color:'#5a4e38', font:{{size:10}} }}, grid:{{ color:'rgba(74,56,18,.2)' }} }},
      y: {{ ticks: {{ color:'#5a4e38', font:{{size:10}} }}, grid:{{ color:'rgba(74,56,18,.2)' }} }}
    }}
  }}
}});

function openModal(card) {{
  const name  = card.dataset.name;
  const role  = card.dataset.role;
  const image = card.dataset.image;
  const html  = card.querySelector('.cp-body').innerHTML;

  document.getElementById('modalName').textContent = name;
  document.getElementById('modalRole').textContent = role;
  document.getElementById('modalBody').innerHTML   = html;

  const face = document.getElementById('modalFace');
  if (image) {{
    face.innerHTML = `<img class="modal-face-img" src="${{image}}" alt="${{name}}">`;
  }} else {{
    face.innerHTML = `<div class="modal-face-placeholder">👤</div>`;
  }}

  document.getElementById('charModal').classList.add('open');
  document.body.style.overflow = 'hidden';
}}

function closeModal() {{
  document.getElementById('charModal').classList.remove('open');
  document.body.style.overflow = '';
}}

function closeOnBackdrop(e) {{
  if (e.target === document.getElementById('charModal')) closeModal();
}}

document.addEventListener('keydown', e => {{
  if (e.key === 'Escape') {{ closeModal(); closeChapModal(); }}
}});

function openChapModal(num) {{
  const raw = document.getElementById('chap-data-' + num);
  if (!raw) return;
  const d = JSON.parse(raw.textContent);
  document.getElementById('chapNum').textContent   = '제 ' + num + ' 장';
  document.getElementById('chapTitle').textContent = d.title;
  document.getElementById('chapMeta').textContent  = d.chars.toLocaleString() + '자  ·  ' + d.date;
  document.getElementById('chapBody').innerHTML    = d.html;
  document.getElementById('chapBody').scrollTop   = 0;
  document.getElementById('chapModal').classList.add('open');
  document.body.style.overflow = 'hidden';
}}

function closeChapModal() {{
  document.getElementById('chapModal').classList.remove('open');
  document.body.style.overflow = '';
}}

function closeChapOnBackdrop(e) {{
  if (e.target === document.getElementById('chapModal')) closeChapModal();
}}
</script>
</body>
</html>"""

    OUT.write_text(html, encoding="utf-8")
    print(f"OK: {OUT}")
    print(f"  chapters={len(chaps)}, chars={len(chars)}, total={total_chars:,}")

if __name__ == "__main__":
    main()
