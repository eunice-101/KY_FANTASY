"""
KY_Fantasy 판타지 소설 작성 현황 대시보드
Flask 기반 실시간 모니터링 웹 앱 (포트 8765)
"""
import json
import os
import glob
import sqlite3
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify

app = Flask(__name__)

BASE_DIR = Path(__file__).parent.parent
DB_PATH = Path(__file__).parent / "novels.db"
FALLBACK_COVER = "/static/images/default-cover.jpg"


# ──────────────────────────────────────────
# DB 초기화
# ──────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS novels (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            title               TEXT    NOT NULL,
            subtitle            TEXT,
            genre               TEXT,
            synopsis            TEXT,
            cover_image_url     TEXT,
            cover_prompt        TEXT,
            total_chapters      INTEGER DEFAULT 25,
            completed_chapters  INTEGER DEFAULT 0,
            progress_percent    REAL    DEFAULT 0.0,
            current_chapter     INTEGER DEFAULT 1,
            current_arc_title   TEXT,
            quality_score       INTEGER DEFAULT 0,
            health_score        INTEGER DEFAULT 100,
            status              TEXT    DEFAULT 'draft',
            created_at          TEXT    DEFAULT CURRENT_TIMESTAMP,
            updated_at          TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 샘플 데이터 — 중복 방지 (title 기준)
    conn.execute("""
        INSERT OR IGNORE INTO novels (
            title, subtitle, genre, synopsis,
            cover_image_url, cover_prompt,
            total_chapters, completed_chapters, progress_percent,
            current_chapter, current_arc_title,
            quality_score, health_score, status
        ) VALUES (
            '천서의 아이',
            '고구려의 잊힌 문자 마법',
            '역사 판타지',
            '고구려의 잊힌 문자 마법 천서력을 둘러싼 혈통과 금기의 이야기',
            '/static/images/cheonseo-cover.jpg',
            'dark korean historical fantasy cover, ancient goguryeo-inspired ruins, mystical rune magic, epic female protagonist, vertical novel cover',
            25, 7, 28.0,
            8, '3막 - 문자의 시험',
            0, 100, 'writing'
        )
    """)
    conn.commit()
    conn.close()


init_db()


def load_json(path):
    try:
        with open(BASE_DIR / path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def read_file(path):
    try:
        with open(BASE_DIR / path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def get_chapters():
    chapters_dir = BASE_DIR / "story" / "chapters"
    chapters = []
    for f in sorted(chapters_dir.glob("*.md")):
        content = f.read_text(encoding="utf-8")
        num = int(f.stem.replace("chapter-", ""))
        lines = [l for l in content.splitlines() if l.strip()]
        title = lines[0].lstrip("#").strip() if lines else f.stem
        mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d")
        chapters.append({
            "filename": f.name,
            "number": num,
            "num_str": f.stem.replace("chapter-", ""),
            "title": title,
            "char_count": len(content),
            "preview": " ".join(lines[1:3])[:120] if len(lines) > 1 else "",
            "date": mtime,
            "content": content,
        })
    return chapters


def get_novel():
    """novels DB에서 첫 번째 소설 정보를 반환. 없으면 기본값."""
    conn = get_db()
    row = conn.execute("SELECT * FROM novels ORDER BY id LIMIT 1").fetchone()
    conn.close()
    if row:
        novel = dict(row)
        if not novel.get("cover_image_url"):
            novel["cover_image_url"] = FALLBACK_COVER
        return novel
    return {
        "title": "소설 제목 미설정",
        "subtitle": "",
        "genre": "",
        "synopsis": "",
        "cover_image_url": FALLBACK_COVER,
        "total_chapters": 25,
        "completed_chapters": 0,
        "progress_percent": 0.0,
        "current_chapter": 1,
        "current_arc_title": "초기화",
        "quality_score": 0,
        "health_score": 100,
        "status": "draft",
    }


CHAR_IMAGES = {
    "seo-yuna":    "/static/images/seo-yoona.jpg",
    "haewol":      "/static/images/haewol.jpg",
    "kang-doyun":  "/static/images/kang-doyun.jpg",
    "seo-daebi":   "/static/images/seo-daebi.jpg",
    "yeonsangun":  "/static/images/yeonsangun.jpg",
    "im-sahong":   "/static/images/Imsahong.jpg",
}

def get_characters():
    chars_dir = BASE_DIR / "bible" / "characters"
    chars = []
    order = ["seo-yuna", "kang-doyun", "haewol", "seo-daebi", "yeonsangun", "im-sahong", "samdori"]
    files = {f.stem: f for f in chars_dir.glob("*.md")}
    sorted_keys = [k for k in order if k in files] + [k for k in files if k not in order]
    for stem in sorted_keys:
        f = files[stem]
        content = f.read_text(encoding="utf-8")
        first_line = content.splitlines()[0].lstrip("#").strip()
        # "서윤아(徐潤雅) — 주인공" → name="서윤아(徐潤雅)", role="주인공"
        if " — " in first_line:
            display_name, role = first_line.split(" — ", 1)
        else:
            display_name, role = first_line, ""
        # 두 번째 비어있지 않은 줄부터 외모 등 미리보기
        lines = [l.strip() for l in content.splitlines() if l.strip() and not l.startswith("#")]
        preview = " ".join(lines[:3])[:120]
        chars.append({
            "stem": stem,
            "display_name": display_name,
            "role": role,
            "preview": preview,
            "image_url": CHAR_IMAGES.get(stem, ""),
            "content": content,
        })
    return chars


@app.route("/")
def index():
    import json as _json
    progress   = load_json("planning/plot-progress.json")
    chapters   = get_chapters()
    characters = get_characters()

    total_chars = sum(c["char_count"] for c in chapters)
    avg_chars   = round(total_chars / len(chapters)) if chapters else 0
    total_ch    = progress.get("total_chapters", 25)
    done_ch     = progress.get("completed_chapters", len(chapters))
    pct         = round(done_ch / total_ch * 100, 1) if total_ch else 0
    sorted_ch   = sorted(chapters, key=lambda x: x["number"])
    chart_labels = _json.dumps([f"{c['number']}장" for c in sorted_ch])
    chart_data   = _json.dumps([c["char_count"] for c in sorted_ch])

    return render_template(
        "index.html",
        progress=progress,
        chapters=sorted(chapters, key=lambda x: x["number"], reverse=True),
        characters=characters,
        total_chars=total_chars,
        avg_chars=avg_chars,
        total_ch=total_ch,
        done_ch=done_ch,
        pct=pct,
        chart_labels=chart_labels,
        chart_data=chart_data,
        now=datetime.now().strftime("%Y년 %m월 %d일 %H:%M"),
    )


@app.route("/chapter/<number>")
def chapter_detail(number):
    chapter_file = BASE_DIR / "story" / "chapters" / f"chapter-{number}.md"
    if not chapter_file.exists():
        return "챕터를 찾을 수 없습니다.", 404
    content = chapter_file.read_text(encoding="utf-8")
    return render_template("chapter_detail.html", number=number, content=content)


@app.route("/api/status")
def api_status():
    progress = load_json("planning/plot-progress.json")
    quality = load_json("planning/quality-metrics.json")
    health = load_json("planning/system-health.json")
    chapters = get_chapters()

    return jsonify({
        "novel_title": progress.get("novel_title", "미설정"),
        "completed_chapters": progress.get("completed_chapters", 0),
        "total_chapters": progress.get("total_chapters", 30),
        "current_chapter": progress.get("current_chapter", 1),
        "story_phase": progress.get("story_phase", "초기화"),
        "quality_score": quality.get("overall_score", 0),
        "quality_mode": quality.get("current_mode", "표준 모드"),
        "health_score": health.get("overall_score", 100),
        "chapter_count": len(chapters),
        "last_updated": progress.get("last_updated", "-"),
    })


@app.route("/api/chapters")
def api_chapters():
    return jsonify(get_chapters())


@app.route("/api/novels")
def api_novels():
    conn = get_db()
    rows = conn.execute("SELECT * FROM novels ORDER BY id").fetchall()
    conn.close()
    novels = []
    for row in rows:
        novel = dict(row)
        # cover_image_url 없으면 fallback 경로 주입
        if not novel.get("cover_image_url"):
            novel["cover_image_url"] = FALLBACK_COVER
        novels.append(novel)
    return jsonify(novels)


@app.route("/api/novels/<int:novel_id>")
def api_novel_detail(novel_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM novels WHERE id = ?", (novel_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "not found"}), 404
    novel = dict(row)
    if not novel.get("cover_image_url"):
        novel["cover_image_url"] = FALLBACK_COVER
    return jsonify(novel)


@app.route("/api/timeline")
def api_timeline():
    history = read_file("timeline/history.md")
    current = read_file("timeline/current-chapter.md")
    return jsonify({"history": history, "current": current})


if __name__ == "__main__":
    print("KY_Fantasy 대시보드 시작: http://127.0.0.1:8765")
    app.run(host="127.0.0.1", port=8765, debug=True)
