#!/bin/bash
# 상태 동기화 스크립트 — 실제 파일 기반으로 JSON 상태 재동기화

echo "=== 상태 동기화 시작 ==="

# 실제 챕터 파일 수 카운트
ACTUAL_CHAPTERS=$(ls story/chapters/*.md 2>/dev/null | wc -l)
echo "실제 챕터 파일: ${ACTUAL_CHAPTERS}개"

# plot-progress.json 업데이트
python3 << PYEOF
import json
import os
import glob

# 실제 챕터 파일 스캔
chapters = sorted(glob.glob("story/chapters/*.md"))
actual_count = len(chapters)

# plot-progress.json 읽기
progress_file = "planning/plot-progress.json"
if os.path.exists(progress_file):
    with open(progress_file, 'r', encoding='utf-8') as f:
        progress = json.load(f)
else:
    progress = {"total_chapters": 25, "novel_title": "미설정"}

# 동기화
progress["completed_chapters"] = actual_count
progress["current_chapter"] = actual_count + 1
progress["last_updated"] = "$(date +%Y-%m-%d)"

# 진행 단계 업데이트
if actual_count == 0:
    progress["story_phase"] = "초기화"
elif actual_count <= 5:
    progress["story_phase"] = "도입부"
elif actual_count <= 10:
    progress["story_phase"] = "전개 1"
elif actual_count <= 15:
    progress["story_phase"] = "전개 2"
elif actual_count <= 25:
    progress["story_phase"] = "위기와 반전"
else:
    progress["story_phase"] = "결말"

with open(progress_file, 'w', encoding='utf-8') as f:
    json.dump(progress, f, ensure_ascii=False, indent=2)

# chapter-status.json 업데이트
status_file = "planning/chapter-status.json"
if os.path.exists(status_file):
    with open(status_file, 'r', encoding='utf-8') as f:
        status_data = json.load(f)
else:
    status_data = {"chapters": {}}

for chapter_file in chapters:
    chapter_name = os.path.basename(chapter_file)
    chapter_num = chapter_name.replace("chapter-", "").replace(".md", "")
    if chapter_num not in status_data["chapters"]:
        char_count = len(open(chapter_file, encoding='utf-8').read())
        status_data["chapters"][chapter_num] = {
            "status": "완료",
            "char_count": char_count,
            "file": chapter_name
        }

with open(status_file, 'w', encoding='utf-8') as f:
    json.dump(status_data, f, ensure_ascii=False, indent=2)

print(f"동기화 완료: {actual_count}챕터")
PYEOF

echo "=== 동기화 완료 ==="
