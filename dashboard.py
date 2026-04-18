#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
판타지 소설 작업현황 대시보드 — 동양 수묵 감성
AI_NovelGenerator의 데이터를 읽어 HTML 대시보드를 생성합니다.
"""

import os
import sys
import json
import re
import time
import webbrowser
from pathlib import Path
from datetime import datetime


CONFIG_PATH  = Path(__file__).parent / "AI_NovelGenerator" / "config.json"
JSON_PATH    = Path(__file__).parent / "my_fantasy_novel.json"


def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def read_file_safe(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def _empty_data(title="제목 미설정", genre="판타지", target=0, wpch=0,
                arch_model="", final_model="", filepath=""):
    return {
        "title": title, "genre": genre,
        "target_chapters": target, "word_per_chapter": wpch,
        "arch_model": arch_model, "final_model": final_model,
        "filepath": filepath,
        "chapters": [], "total_words": 0,
        "has_architecture": False, "has_blueprint": False,
        "has_characters": False, "has_summary": False,
        "architecture_preview": "", "blueprint_preview": "",
        "character_preview": "", "summary_preview": "",
        "source": "none",
        "generated_at": datetime.now().strftime("%Y년 %m월 %d일  %H:%M"),
    }


def _collect_from_filepath(data: dict, filepath: str) -> bool:
    """filepath 디렉터리에서 파일을 읽어 data를 채웁니다. 데이터 있으면 True."""
    if not filepath or not os.path.isdir(filepath):
        return False

    found = False
    for key, fname, preview_key in [
        ("has_architecture", "novel_architecture.txt", "architecture_preview"),
        ("has_blueprint",    "Novel_directory.txt",    "blueprint_preview"),
        ("has_characters",   "character_state.txt",    "character_preview"),
    ]:
        fpath = os.path.join(filepath, fname)
        if os.path.exists(fpath):
            content = read_file_safe(fpath)
            if content.strip():
                data[key] = True
                data[preview_key] = content[:600].strip()
                found = True

    summary_file = os.path.join(filepath, "global_summary.txt")
    summary_content = read_file_safe(summary_file).strip() if os.path.exists(summary_file) else ""
    if summary_content:
        data["has_summary"] = True
        data["summary_preview"] = summary_content[:600]
        found = True

    chapters_dir = os.path.join(filepath, "chapters")
    if os.path.isdir(chapters_dir):
        chapter_files = sorted(
            [(int(m.group(1)), f)
             for f in os.listdir(chapters_dir)
             if (m := re.match(r"chapter_(\d+)\.txt", f))],
            key=lambda x: x[0],
        )
        for num, fname in chapter_files:
            path = os.path.join(chapters_dir, fname)
            content = read_file_safe(path)
            word_count = len(content.strip())
            mtime = os.path.getmtime(path)
            modified = datetime.fromtimestamp(mtime).strftime("%Y.%m.%d")
            first_line = content.strip().split("\n")[0][:60] if content.strip() else ""
            data["chapters"].append({
                "num": num, "word_count": word_count,
                "modified": modified, "preview": first_line,
            })
            data["total_words"] += word_count
            found = True

    return found


def _collect_from_json(data: dict) -> bool:
    """my_fantasy_novel.json에서 데이터를 읽어 data를 채웁니다. 데이터 있으면 True."""
    if not JSON_PATH.exists():
        return False
    try:
        proj = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    except Exception:
        return False

    world = proj.get("world", {})
    characters = proj.get("characters", [])
    plot = proj.get("plot", {})
    chapters_raw = proj.get("chapters", {})

    if not (world or plot or chapters_raw):
        return False

    # 기본 메타
    if plot:
        data["title"] = plot.get("title", data["title"])
        tags = plot.get("genre_tags", [])
        data["genre"] = ", ".join(tags) if tags else data["genre"]
        data["target_chapters"] = int(plot.get("total_chapters", 0)) or data["target_chapters"]

    # 세계관 미리보기
    if world:
        lines = [
            f"# {world.get('world_name','')}",
            f"\n테마: {world.get('theme','')}",
            f"\n{world.get('description','')[:400]}",
        ]
        data["has_architecture"] = True
        data["architecture_preview"] = "\n".join(lines)[:600]

    # 캐릭터 미리보기
    if characters:
        parts = [
            f"{c.get('name','')} ({c.get('role','')}): {c.get('personality','')[:80]}"
            for c in characters
        ]
        data["has_characters"] = True
        data["character_preview"] = "\n".join(parts)[:600]

    # 목차 미리보기
    if plot and plot.get("chapter_outlines"):
        lines = [f"# {plot.get('title','')}"]
        for co in plot["chapter_outlines"]:
            lines.append(f"제{co['chapter']}장 {co.get('title','')} — {co.get('summary','')[:60]}")
        data["has_blueprint"] = True
        data["blueprint_preview"] = "\n".join(lines)[:600]

    # 요약 미리보기
    if plot:
        acts = "\n".join(
            f"[{a.get('name','')}] {a.get('summary','')}"
            for a in plot.get("acts", [])
        )
        summary = f"{plot.get('title','')}\n{plot.get('logline','')}\n\n{acts}"
        if summary.strip():
            data["has_summary"] = True
            data["summary_preview"] = summary[:600]

    # 챕터 목록
    mtime_str = datetime.fromtimestamp(JSON_PATH.stat().st_mtime).strftime("%Y.%m.%d")
    for num_str, content in sorted(chapters_raw.items(), key=lambda x: int(x[0])):
        word_count = len(content.strip())
        first_line = content.strip().split("\n")[0][:60] if content.strip() else ""
        data["chapters"].append({
            "num": int(num_str), "word_count": word_count,
            "modified": mtime_str, "preview": first_line,
        })
        data["total_words"] += word_count

    data["source"] = "json"
    return True


def collect_novel_data(config):
    other = config.get("other_params", {})
    filepath = other.get("filepath", "").strip()
    topic    = other.get("topic", "").strip()
    genre    = other.get("genre", "판타지").strip()
    target_chapters = int(other.get("chapter_num") or other.get("num_chapters") or 0)
    word_number     = int(other.get("word_number") or 0)

    choose     = config.get("choose_configs", {})
    arch_model = choose.get("architecture_llm", "")
    final_model = choose.get("final_chapter_llm", "")

    data = _empty_data(
        title=topic or "제목 미설정", genre=genre,
        target=target_chapters, wpch=word_number,
        arch_model=arch_model, final_model=final_model,
        filepath=filepath,
    )

    # 1순위: AI_NovelGenerator filepath 디렉터리
    if _collect_from_filepath(data, filepath):
        data["source"] = "filepath"
        return data

    # 2순위: my_fantasy_novel.json (fantasy_generator.py 네이티브 포맷)
    _collect_from_json(data)
    return data


# ── 렌더 헬퍼 ──────────────────────────────────────────────────────────────────

def seal_badge(ok, label_on, label_off):
    if ok:
        return f'<span class="seal seal-on">{label_on}</span>'
    return f'<span class="seal seal-off">{label_off}</span>'


def preview_box(content, empty_msg):
    if content:
        safe = (content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        return f'<div class="parchment"><pre>{safe}</pre></div>'
    return f'<p class="empty-note">{empty_msg}</p>'


def progress_bar(val, total):
    pct = min(100.0, round(val / total * 100, 1)) if total > 0 else 0.0
    return pct, f"""
    <div class="prog-row">
      <div class="prog-track"><div class="prog-fill" style="width:{pct}%"></div></div>
      <span class="prog-pct">{pct}%</span>
    </div>"""


# ── HTML 생성 ──────────────────────────────────────────────────────────────────

def generate_html(data, watch: bool = False):
    chapters = data["chapters"]
    written  = len(chapters)
    target   = data["target_chapters"]
    total_w  = data["total_words"]
    avg_w    = total_w // written if written else 0
    est_tot  = avg_w * target if avg_w and target else 0

    ch_pct, ch_prog_html = progress_bar(written, target)
    wpch_cfg = data["word_per_chapter"]
    # config에 미설정 시 실제 평균으로 추정
    wpch_est = avg_w if (not wpch_cfg and avg_w) else wpch_cfg
    word_target = wpch_est * target if wpch_est and target else est_tot
    w_pct,  w_prog_html  = progress_bar(total_w, word_target)

    # 챕터 표
    ch_rows = ""
    for ch in chapters:
        ch_rows += f"""
          <tr>
            <td class="td-n"><span class="num-badge">제{ch['num']}장</span></td>
            <td class="td-p">{ch['preview'] or '—'}</td>
            <td class="td-w">{ch['word_count']:,}자</td>
            <td class="td-d">{ch['modified']}</td>
          </tr>"""
    if not ch_rows:
        ch_rows = '<tr><td colspan="4" class="td-empty">아직 작성된 장이 없습니다</td></tr>'

    # 최근 5장
    recent_html = ""
    for ch in reversed(chapters[-5:]):
        recent_html += f"""
        <div class="scroll-entry">
          <span class="scroll-n">제{ch['num']}장</span>
          <span class="scroll-p">{ch['preview'] or '—'}</span>
          <span class="scroll-w">{ch['word_count']:,}자</span>
          <span class="scroll-d">{ch['modified']}</span>
        </div>"""
    if not recent_html:
        recent_html = '<p class="empty-note">아직 작성된 장이 없습니다</p>'

    # 세계관·캐릭터·목차 미리보기
    arch_html    = preview_box(data["architecture_preview"], "세계관이 아직 생성되지 않았습니다")
    char_html    = preview_box(data["character_preview"],    "캐릭터 정보가 없습니다")
    bp_html      = preview_box(data["blueprint_preview"],    "챕터 목차가 아직 생성되지 않았습니다")
    summary_html = preview_box(data["summary_preview"],      "글로벌 요약이 없습니다")

    # 시작 가이드 (데이터 없을 때만 표시)
    no_data = not data["filepath"] or (
        not data["has_architecture"] and not data["chapters"]
    )
    guide_html = f"""
  <div class="row-1" id="guide-section">
    <div class="card">
      <div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="sec-title">시작 가이드 · 使用方法</p>
      <div style="padding:8px 0; line-height:2.2; font-size:13px; color:var(--t2);">
        <p style="margin-bottom:12px; color:var(--gold);">소설 데이터가 아직 없습니다. 아래 순서로 시작하세요.</p>
        <ol style="padding-left:20px; color:var(--t2);">
          <li><code style="color:var(--gold2);">run_fantasy_generator.bat</code> 실행 → 저장 경로 설정</li>
          <li>메뉴 <strong>9</strong> (원클릭 자동 생성) 선택 → 테마 입력</li>
          <li>세계관·캐릭터·플롯·챕터가 자동 생성됩니다</li>
          <li><code style="color:var(--gold2);">run_dashboard.bat</code> 재실행 → 결과 확인</li>
        </ol>
        <p style="margin-top:16px; color:var(--t3); font-size:11px;">
          CLI: <code>python fantasy_generator.py quick "테마" -y</code>
        </p>
      </div>
    </div>
  </div>""" if no_data else ""

    # 차트 데이터
    c_labels = json.dumps([f"제{ch['num']}장" for ch in chapters], ensure_ascii=False)
    c_data   = json.dumps([ch["word_count"] for ch in chapters])

    # 챕터당 목표 달성 상태
    wpch = wpch_est
    if wpch and avg_w:
        wpch_status = "달성" if avg_w >= wpch else "미달"
        wpch_cls    = "jade" if avg_w >= wpch else "crimson"
    else:
        wpch_status, wpch_cls = "—", "pearl"

    # 예상 완료일
    if written >= 2 and target > written:
        dates = sorted({ch["modified"] for ch in chapters})
        if len(dates) >= 2:
            first = datetime.strptime(dates[0], "%Y.%m.%d")
            last  = datetime.strptime(dates[-1], "%Y.%m.%d")
            days_elapsed = max((last - first).days, 1)
            pace = written / days_elapsed  # 장/일
            days_left = (target - written) / pace
            est_done = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            from datetime import timedelta
            est_done = est_done + timedelta(days=days_left)
            est_done_str = est_done.strftime("%Y.%m.%d")
        else:
            est_done_str = "데이터 부족"
    else:
        est_done_str = "—"

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{('<meta http-equiv="refresh" content="30">') if watch else ''}
<title>작업현황 · {data['title']}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
/* ═══════════════════════════════════════════════
   변수
═══════════════════════════════════════════════ */
:root {{
  --bg:      #07060a;
  --s1:      #0e0c10;
  --s2:      #141118;
  --s3:      #1c1822;
  --s4:      #241f2c;

  --gold:    #c49a3c;
  --gold2:   #9a7628;
  --gold3:   #4a3812;
  --gold4:   #2a2008;

  --crimson: #b83028;
  --crim2:   #7a1e18;
  --crim3:   #3a0e0c;

  --jade:    #4a8a68;
  --jade2:   #2e5a44;

  --t1:      #ddd0b8;
  --t2:      #a09070;
  --t3:      #5a4e38;
  --t4:      #302820;

  --serif: 'Noto Serif KR', 'Batang', '바탕', Georgia, serif;
  --sans:  'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
}}

/* ═══════════════════════════════════════════════
   기반
═══════════════════════════════════════════════ */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html {{ scrollbar-width: thin; scrollbar-color: var(--gold3) var(--bg); }}
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: var(--bg); }}
::-webkit-scrollbar-thumb {{ background: var(--gold3); border-radius: 2px; }}

body {{
  font-family: var(--sans);
  background: var(--bg);
  color: var(--t1);
  min-height: 100vh;
  /* 종이 격자 — 격지(格紙) */
  background-image:
    repeating-linear-gradient(0deg, transparent, transparent 47px, rgba(74,56,18,0.06) 48px),
    repeating-linear-gradient(90deg, transparent, transparent 47px, rgba(74,56,18,0.04) 48px);
}}

/* ═══════════════════════════════════════════════
   헤더
═══════════════════════════════════════════════ */
.header {{
  position: relative;
  overflow: hidden;
  padding: 52px 56px 44px;
  background:
    radial-gradient(ellipse 70% 100% at 80% 50%, rgba(42,28,8,0.6) 0%, transparent 70%),
    radial-gradient(ellipse 50% 80% at 10% 30%, rgba(30,14,30,0.5) 0%, transparent 60%),
    var(--s1);
  border-bottom: 1px solid var(--gold3);
}}

/* 수묵 문자 장식 */
.header-deco {{
  position: absolute; right: 40px; top: 50%; transform: translateY(-50%);
  font-family: var(--serif); font-size: 260px; font-weight: 700;
  color: transparent;
  -webkit-text-stroke: 1px rgba(196,154,60,0.07);
  line-height: 1; pointer-events: none; user-select: none;
  letter-spacing: -0.05em;
}}

.header-eyebrow {{
  font-family: var(--serif);
  font-size: 10px; letter-spacing: 5px; color: var(--gold2);
  text-transform: uppercase; margin-bottom: 16px;
}}

.header h1 {{
  font-family: var(--serif);
  font-size: 38px; font-weight: 600; letter-spacing: 0.04em;
  color: var(--t1);
  text-shadow: 0 2px 20px rgba(196,154,60,0.15);
  margin-bottom: 14px;
  line-height: 1.3;
}}

.header-genre {{
  display: inline-block;
  font-family: var(--serif); font-size: 11px; letter-spacing: 3px;
  color: var(--gold); border: 1px solid var(--gold2);
  padding: 4px 16px; margin-bottom: 22px;
}}

.header-rule {{
  width: 100%; height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold3) 20%, var(--gold3) 80%, transparent);
  margin: 20px 0 16px;
}}

.header-meta {{
  display: flex; flex-wrap: wrap; gap: 28px;
  font-size: 11px; color: var(--t3); letter-spacing: 0.5px;
}}
.header-meta span {{ display: flex; align-items: center; gap: 6px; }}
.header-meta .meta-label {{ color: var(--t3); }}
.header-meta .meta-val {{ color: var(--t2); }}

/* ═══════════════════════════════════════════════
   레이아웃
═══════════════════════════════════════════════ */
.wrap {{ max-width: 1360px; margin: 0 auto; padding: 40px 40px 80px; }}

.row-4 {{ display: grid; grid-template-columns: repeat(4,1fr); gap: 16px; margin-bottom: 20px; }}
.row-2 {{ display: grid; grid-template-columns: 1fr 1fr;      gap: 20px; margin-bottom: 20px; }}
.row-1 {{ margin-bottom: 20px; }}

/* ═══════════════════════════════════════════════
   카드 (창호지 격자 테두리)
═══════════════════════════════════════════════ */
.card {{
  position: relative;
  background: var(--s2);
  border: 1px solid var(--gold3);
  padding: 22px 24px;
  /* 안쪽 얇은 선 */
  box-shadow: inset 0 0 0 3px var(--s2), inset 0 0 0 4px var(--gold4);
}}

/* 네 모서리 꺾쇠 장식 */
.card::before, .card::after {{
  content: '';
  position: absolute;
  width: 14px; height: 14px;
  border-color: var(--gold2);
  border-style: solid;
  opacity: 0.6;
}}
.card::before {{ top: 5px; left: 5px; border-width: 1px 0 0 1px; }}
.card::after  {{ bottom: 5px; right: 5px; border-width: 0 1px 1px 0; }}

.card-corner-tr, .card-corner-bl {{
  position: absolute;
  width: 14px; height: 14px;
  border-color: var(--gold2);
  border-style: solid;
  opacity: 0.6;
  pointer-events: none;
}}
.card-corner-tr {{ top: 5px; right: 5px; border-width: 1px 1px 0 0; }}
.card-corner-bl {{ bottom: 5px; left: 5px; border-width: 0 0 1px 1px; }}

/* ═══════════════════════════════════════════════
   섹션 제목
═══════════════════════════════════════════════ */
.sec-title {{
  font-family: var(--serif);
  font-size: 13px; font-weight: 500; letter-spacing: 3px;
  color: var(--t2); margin-bottom: 18px;
  display: flex; align-items: center; gap: 10px;
}}
.sec-title::before {{
  content: '◆';
  color: var(--gold2); font-size: 8px;
}}
.sec-title::after {{
  content: '';
  flex: 1; height: 1px;
  background: linear-gradient(90deg, var(--gold3), transparent);
}}

/* ═══════════════════════════════════════════════
   통계 카드
═══════════════════════════════════════════════ */
.stat-eyebrow {{
  font-size: 10px; letter-spacing: 3px; color: var(--t3);
  text-transform: uppercase; margin-bottom: 10px;
  font-family: var(--serif);
}}
.stat-val {{
  font-family: var(--serif);
  font-size: 44px; font-weight: 300; line-height: 1;
  color: var(--gold); margin-bottom: 8px;
  letter-spacing: -0.02em;
}}
.stat-val.jade   {{ color: var(--jade); }}
.stat-val.crimson {{ color: var(--crimson); }}
.stat-val.pearl  {{ color: var(--t1); }}

.stat-sub {{
  font-size: 11px; color: var(--t3); letter-spacing: 0.5px;
}}

/* 진행률 바 */
.prog-row {{
  display: flex; align-items: center; gap: 10px;
  margin-top: 12px;
}}
.prog-track {{
  flex: 1; height: 3px;
  background: var(--gold4); position: relative; overflow: hidden;
}}
.prog-fill {{
  height: 100%;
  background: linear-gradient(90deg, var(--crim2), var(--gold));
  transition: width .8s cubic-bezier(.4,0,.2,1);
  position: relative;
}}
.prog-fill::after {{
  content: '';
  position: absolute; right: 0; top: -2px;
  width: 5px; height: 7px;
  background: var(--gold);
  clip-path: polygon(0 0, 100% 50%, 0 100%);
}}
.prog-pct {{
  font-size: 10px; color: var(--gold2);
  font-family: var(--serif); letter-spacing: 1px; min-width: 36px; text-align: right;
}}

/* ═══════════════════════════════════════════════
   도장 배지 (印章)
═══════════════════════════════════════════════ */
.seal {{
  display: inline-flex; align-items: center; justify-content: center;
  font-family: var(--serif);
  font-size: 11px; letter-spacing: 2px;
  padding: 4px 12px; min-width: 64px;
  border: 1.5px solid;
}}
.seal-on {{
  color: var(--crimson); border-color: var(--crimson);
  background: var(--crim3);
  text-shadow: 0 0 8px rgba(184,48,40,0.3);
}}
.seal-off {{
  color: var(--t3); border-color: var(--t4);
  background: transparent;
}}

/* ═══════════════════════════════════════════════
   작업 현황 (상태 격자)
═══════════════════════════════════════════════ */
.status-grid {{
  display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
}}
.status-row {{
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 14px;
  background: var(--s3); border: 1px solid var(--t4);
}}
.status-row-label {{
  font-size: 12px; color: var(--t2); letter-spacing: 0.5px;
}}

/* ═══════════════════════════════════════════════
   최근 장 스크롤
═══════════════════════════════════════════════ */
.scroll-entry {{
  display: flex; align-items: baseline; gap: 12px;
  padding: 11px 0;
  border-bottom: 1px solid var(--t4);
}}
.scroll-entry:last-child {{ border-bottom: none; }}
.scroll-n  {{ font-family: var(--serif); font-size: 12px; color: var(--gold2); min-width: 64px; letter-spacing: 1px; }}
.scroll-p  {{ flex: 1; font-size: 12px; color: var(--t2); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.scroll-w  {{ font-size: 11px; color: var(--t3); min-width: 70px; text-align: right; letter-spacing: 0.5px; }}
.scroll-d  {{ font-size: 10px; color: var(--t3); min-width: 72px; text-align: right; }}

/* ═══════════════════════════════════════════════
   창호지 미리보기 박스
═══════════════════════════════════════════════ */
.parchment {{
  background: var(--s3); border: 1px solid var(--t4);
  padding: 16px; max-height: 200px; overflow-y: auto;
}}
.parchment pre {{
  font-family: var(--serif);
  font-size: 12px; color: var(--t2);
  white-space: pre-wrap; word-break: break-word;
  line-height: 1.9; letter-spacing: 0.3px;
}}
.empty-note {{
  font-family: var(--serif);
  font-size: 12px; color: var(--t3);
  padding: 18px 0; letter-spacing: 1px;
  text-align: center;
}}

/* ═══════════════════════════════════════════════
   챕터 표
═══════════════════════════════════════════════ */
.chap-table {{ width: 100%; border-collapse: collapse; }}
.chap-table thead th {{
  font-family: var(--serif);
  font-size: 10px; letter-spacing: 3px; color: var(--t3);
  text-align: left; padding: 0 12px 12px;
  border-bottom: 1px solid var(--gold3);
}}
.chap-table tbody td {{
  padding: 10px 12px;
  border-bottom: 1px solid var(--t4);
  vertical-align: middle;
}}
.chap-table tbody tr:hover td {{ background: rgba(196,154,60,0.04); }}

.num-badge {{
  display: inline-block;
  font-family: var(--serif); font-size: 11px; color: var(--gold2);
  border: 1px solid var(--gold3); padding: 2px 8px;
  letter-spacing: 1px; white-space: nowrap;
}}

.td-n {{ width: 90px; }}
.td-p {{ color: var(--t2); font-size: 12px; max-width: 320px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.td-w {{ text-align: right; font-family: var(--serif); font-size: 12px; color: var(--t2); width: 100px; letter-spacing: 0.5px; }}
.td-d {{ text-align: right; font-size: 11px; color: var(--t3); width: 90px; }}
.td-empty {{ text-align: center; color: var(--t3); padding: 36px; font-family: var(--serif); font-size: 13px; letter-spacing: 2px; }}

/* ═══════════════════════════════════════════════
   차트
═══════════════════════════════════════════════ */
.chart-wrap {{ position: relative; height: 230px; }}

/* ═══════════════════════════════════════════════
   푸터
═══════════════════════════════════════════════ */
.footer {{
  margin-top: 60px; padding-top: 28px;
  border-top: 1px solid var(--gold3);
  text-align: center;
}}
.footer-inner {{
  display: inline-flex; align-items: center; gap: 20px;
  font-family: var(--serif); font-size: 11px; color: var(--t3);
  letter-spacing: 2px;
}}
.footer-sep {{ color: var(--gold3); }}

/* ═══════════════════════════════════════════════
   반응형
═══════════════════════════════════════════════ */
@media (max-width: 1200px) {{
  .row-4 {{ grid-template-columns: repeat(3,1fr) !important; }}
}}
@media (max-width: 960px) {{
  .row-4 {{ grid-template-columns: 1fr 1fr !important; }}
  .row-2 {{ grid-template-columns: 1fr; }}
  .header {{ padding: 36px 28px 32px; }}
  .wrap {{ padding: 28px 20px 60px; }}
  .header-deco {{ font-size: 160px; right: 10px; }}
  .header h1 {{ font-size: 28px; }}
}}
@media (max-width: 600px) {{
  .row-4 {{ grid-template-columns: 1fr; }}
  .status-grid {{ grid-template-columns: 1fr; }}
  .stat-val {{ font-size: 36px; }}
}}
</style>
</head>
<body>

<!-- ═════════════════════  HEADER  ═════════════════════ -->
<header class="header">
  <div class="header-deco">幻</div>

  <p class="header-eyebrow">Fantasy Novel · 作業現況</p>
  <h1>{data['title']}</h1>
  <span class="header-genre">{data['genre']}</span>

  <div class="header-rule"></div>

  <div class="header-meta">
    <span><span class="meta-label">진행</span><span class="meta-val">{written} / {target if target else '?'} 장 ({ch_pct}%)</span></span>
    <span><span class="meta-label">총 자수</span><span class="meta-val">{total_w:,}자</span></span>
    <span><span class="meta-label">架構 모델</span><span class="meta-val">{data['arch_model'] or '—'}</span></span>
    <span><span class="meta-label">執筆 모델</span><span class="meta-val">{data['final_model'] or '—'}</span></span>
    <span><span class="meta-label">저장 경로</span><span class="meta-val">{data['filepath'] or '미설정'}</span></span>
    <span><span class="meta-label">데이터 소스</span><span class="meta-val">{'파일 디렉터리' if data['source']=='filepath' else 'JSON (fantasy_generator)' if data['source']=='json' else '없음'}</span></span>
    <span><span class="meta-label">생성 일시</span><span class="meta-val">{data['generated_at']}</span></span>
  </div>
</header>

<!-- ═════════════════════  본문  ═════════════════════ -->
<div class="wrap">

  <!-- 통계 카드 5열 -->
  <div class="row-4" style="grid-template-columns:repeat(5,1fr);">

    <div class="card">
      <div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="stat-eyebrow">完成 章</p>
      <p class="stat-val">{written}</p>
      <p class="stat-sub">목표 {target if target else '미설정'} 장</p>
      {ch_prog_html if target else ''}
    </div>

    <div class="card">
      <div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="stat-eyebrow">總 字數</p>
      <p class="stat-val jade">{total_w:,}</p>
      <p class="stat-sub">평균 {avg_w:,} 자 / 장</p>
      {w_prog_html if est_tot else ''}
    </div>

    <div class="card">
      <div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="stat-eyebrow">推定 完成 字數</p>
      <p class="stat-val pearl">{est_tot:,}</p>
      <p class="stat-sub">{'진행률 ' + str(round(total_w/est_tot*100,1)) + '%' if est_tot else '데이터 부족'}</p>
    </div>

    <div class="card">
      <div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="stat-eyebrow">章當 目標 字數</p>
      <p class="stat-val {wpch_cls}">{wpch:,}</p>
      <p class="stat-sub">{wpch_status}</p>
    </div>

    <div class="card">
      <div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="stat-eyebrow">예상 완료일</p>
      <p class="stat-val pearl" style="font-size:26px;letter-spacing:0;">{est_done_str}</p>
      <p class="stat-sub">{'잔여 ' + str(target - written) + '장' if target > written else '완료' if written >= target and target else '—'}</p>
    </div>

  </div>

  {guide_html}

  <!-- 작업 현황 + 최근 장 -->
  <div class="row-2">

    <div class="card">
      <div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="sec-title">작업 파일 현황</p>
      <div class="status-grid">
        <div class="status-row">
          <span class="status-row-label">세계관 · 架構</span>
          {seal_badge(data['has_architecture'], '완 성', '미 완')}
        </div>
        <div class="status-row">
          <span class="status-row-label">챕터 목차</span>
          {seal_badge(data['has_blueprint'], '완 성', '미 완')}
        </div>
        <div class="status-row">
          <span class="status-row-label">캐릭터 상태</span>
          {seal_badge(data['has_characters'], '기록 있음', '없 음')}
        </div>
        <div class="status-row">
          <span class="status-row-label">글로벌 요약</span>
          {seal_badge(data['has_summary'], '기록 있음', '없 음')}
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="sec-title">최근 작성 장</p>
      {recent_html}
    </div>

  </div>

  <!-- 차트 + 세계관 -->
  <div class="row-2">

    <div class="card">
      <div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="sec-title">장별 자수</p>
      <div class="chart-wrap">
        <canvas id="chapterChart"></canvas>
      </div>
    </div>

    <div class="card">
      <div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="sec-title">세계관 · 世界觀</p>
      {arch_html}
    </div>

  </div>

  <!-- 캐릭터 + 목차 -->
  <div class="row-2">

    <div class="card">
      <div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="sec-title">캐릭터 상태 · 人物</p>
      {char_html}
    </div>

    <div class="card">
      <div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="sec-title">챕터 목차 · 目次</p>
      {bp_html}
    </div>

  </div>

  <!-- 글로벌 요약 -->
  <div class="row-1">
    <div class="card">
      <div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="sec-title">글로벌 요약 · 全體要約</p>
      {summary_html}
    </div>
  </div>

  <!-- 전체 장 목록 -->
  <div class="row-1">
    <div class="card">
      <div class="card-corner-tr"></div><div class="card-corner-bl"></div>
      <p class="sec-title">전체 장 목록 · 章目錄</p>
      <div style="overflow-x:auto;">
        <table class="chap-table">
          <thead>
            <tr>
              <th>장 번호</th>
              <th>내용 미리보기</th>
              <th style="text-align:right;">자수</th>
              <th style="text-align:right;">수정일</th>
            </tr>
          </thead>
          <tbody>{ch_rows}</tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- 푸터 -->
  <div class="footer">
    <div class="footer-inner">
      <span>作業現況</span>
      <span class="footer-sep">◆</span>
      <span>AI_NovelGenerator</span>
      <span class="footer-sep">◆</span>
      <span>{data['generated_at']}</span>
    </div>
  </div>

</div><!-- /wrap -->

<script>
(function() {{
  const labels  = {c_labels};
  const dataArr = {c_data};

  if (!labels.length) {{
    const wrap = document.getElementById('chapterChart').parentElement;
    wrap.innerHTML = '<p class="empty-note">아직 장 데이터가 없습니다</p>';
    return;
  }}

  Chart.defaults.color = '#5a4e38';
  Chart.defaults.font.family = "'Noto Serif KR', serif";

  const ctx = document.getElementById('chapterChart').getContext('2d');

  const gradient = ctx.createLinearGradient(0, 0, 0, 230);
  gradient.addColorStop(0,   'rgba(184, 48, 40, 0.85)');
  gradient.addColorStop(0.5, 'rgba(154, 118, 40, 0.70)');
  gradient.addColorStop(1,   'rgba(196,154, 60, 0.40)');

  new Chart(ctx, {{
    type: 'bar',
    data: {{
      labels,
      datasets: [{{
        data: dataArr,
        backgroundColor: gradient,
        borderColor: 'rgba(196,154,60,0.5)',
        borderWidth: 1,
        borderRadius: 0,
        borderSkipped: false,
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{
          backgroundColor: '#1c1822',
          borderColor: '#4a3812',
          borderWidth: 1,
          titleColor: '#c49a3c',
          bodyColor: '#a09070',
          titleFont: {{ family: "'Noto Serif KR', serif", size: 11 }},
          bodyFont:  {{ family: "'Noto Serif KR', serif", size: 11 }},
          callbacks: {{
            label: ctx => '  ' + ctx.parsed.y.toLocaleString() + ' 字',
          }}
        }}
      }},
      scales: {{
        x: {{
          ticks: {{ color: '#5a4e38', font: {{ size: 10 }}, maxRotation: 45 }},
          grid: {{ color: 'rgba(74,56,18,0.2)', drawBorder: false }},
          border: {{ color: 'rgba(74,56,18,0.3)' }}
        }},
        y: {{
          ticks: {{ color: '#5a4e38', font: {{ size: 10 }},
            callback: v => v.toLocaleString() }},
          grid: {{ color: 'rgba(74,56,18,0.2)', drawBorder: false }},
          border: {{ color: 'rgba(74,56,18,0.3)', dash: [4, 4] }}
        }}
      }}
    }}
  }});
}})();
</script>

</body>
</html>"""


# ── 메인 ──────────────────────────────────────────────────────────────────────

WATCH_INTERVAL = 30  # 초


def _build(watch: bool = False) -> Path:
    config = load_config()
    data   = collect_novel_data(config)
    html   = generate_html(data, watch=watch)
    out_path = Path(__file__).parent / "dashboard.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def main():
    watch = "--watch" in sys.argv

    out_path = _build(watch=watch)
    print(f"{'[watch]' if watch else ''} 완료 → {out_path}")
    webbrowser.open(out_path.as_uri())

    if watch:
        print(f"[watch] {WATCH_INTERVAL}초마다 자동 갱신합니다. 종료: Ctrl+C")
        try:
            while True:
                time.sleep(WATCH_INTERVAL)
                _build(watch=True)
                print(f"[watch] 갱신 완료 {datetime.now().strftime('%H:%M:%S')}")
        except KeyboardInterrupt:
            print("\n[watch] 종료.")


if __name__ == "__main__":
    main()
