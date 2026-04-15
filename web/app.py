"""
KY_Fantasy 판타지 소설 작성 현황 대시보드
Flask 기반 실시간 모니터링 웹 앱 (포트 8765)
"""
import json
import os
import glob
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify

app = Flask(__name__)

BASE_DIR = Path(__file__).parent.parent


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
        chapters.append({
            "filename": f.name,
            "number": f.stem.replace("chapter-", ""),
            "char_count": len(content),
            "preview": content[:200].replace("\n", " "),
            "word_count": len(content.split()),
        })
    return chapters


def get_characters():
    chars_dir = BASE_DIR / "bible" / "characters"
    chars = []
    for f in sorted(chars_dir.glob("*.md")):
        content = f.read_text(encoding="utf-8")
        chars.append({
            "name": f.stem,
            "preview": content[:300].replace("\n", " "),
        })
    return chars


@app.route("/")
def index():
    progress = load_json("planning/plot-progress.json")
    quality = load_json("planning/quality-metrics.json")
    health = load_json("planning/system-health.json")
    chapters = get_chapters()
    characters = get_characters()

    completion_pct = 0
    total = progress.get("total_chapters", 30)
    completed = progress.get("completed_chapters", 0)
    if total > 0:
        completion_pct = round(completed / total * 100, 1)

    return render_template(
        "index.html",
        progress=progress,
        quality=quality,
        health=health,
        chapters=chapters,
        characters=characters,
        completion_pct=completion_pct,
        now=datetime.now().strftime("%Y-%m-%d %H:%M"),
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


@app.route("/api/timeline")
def api_timeline():
    history = read_file("timeline/history.md")
    current = read_file("timeline/current-chapter.md")
    return jsonify({"history": history, "current": current})


if __name__ == "__main__":
    print("KY_Fantasy 대시보드 시작: http://127.0.0.1:8765")
    app.run(host="127.0.0.1", port=8765, debug=True)
