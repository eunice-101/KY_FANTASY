#!/bin/bash
# 최신 챕터 품질 체크 스크립트

LATEST_CHAPTER=$(ls -t story/chapters/*.md 2>/dev/null | head -1)

if [ -z "$LATEST_CHAPTER" ]; then
  echo "아직 생성된 챕터가 없습니다."
  exit 0
fi

echo "=== 품질 분석: $LATEST_CHAPTER ==="

# 1. 글자 수
CHAR_COUNT=$(wc -m < "$LATEST_CHAPTER")
echo "글자 수: $CHAR_COUNT자"

if [ "$CHAR_COUNT" -lt 5000 ]; then
  echo "경고: 목표 분량 미달 (5000자 이상 필요)"
elif [ "$CHAR_COUNT" -gt 8000 ]; then
  echo "경고: 분량 초과 (8000자 이하 권장)"
else
  echo "분량: 적정"
fi

# 2. 대화 비율 추정 (따옴표 포함 라인)
TOTAL_LINES=$(wc -l < "$LATEST_CHAPTER")
DIALOG_LINES=$(grep -c '"' "$LATEST_CHAPTER" 2>/dev/null || echo 0)
if [ "$TOTAL_LINES" -gt 0 ]; then
  DIALOG_RATIO=$((DIALOG_LINES * 100 / TOTAL_LINES))
  echo "대화 비율: 약 ${DIALOG_RATIO}% (목표: 30-40%)"
fi

# 3. 품질 점수 계산
SCORE=70  # 기본 점수

if [ "$CHAR_COUNT" -ge 5000 ] && [ "$CHAR_COUNT" -le 8000 ]; then
  SCORE=$((SCORE + 15))
fi

if [ "$DIALOG_RATIO" -ge 25 ] && [ "$DIALOG_RATIO" -le 45 ]; then
  SCORE=$((SCORE + 15))
fi

echo "품질 점수: $SCORE/100"

# 4. quality-metrics.json 업데이트
DATE=$(date +"%Y-%m-%d")
CHAPTER_NAME=$(basename "$LATEST_CHAPTER")

python3 << PYEOF
import json
import os

metrics_file = "planning/quality-metrics.json"
if os.path.exists(metrics_file):
    with open(metrics_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
else:
    data = {"metrics_history": [], "chapters_analyzed": 0}

data["metrics_history"].append({
    "chapter": "$CHAPTER_NAME",
    "date": "$DATE",
    "char_count": $CHAR_COUNT,
    "score": $SCORE
})
data["chapters_analyzed"] = len(data["metrics_history"])
data["overall_score"] = sum(m["score"] for m in data["metrics_history"]) // len(data["metrics_history"])
data["current_mode"] = "최고 품질 모드" if $SCORE >= 90 else ("고성능 모드" if $SCORE >= 80 else ("표준 모드" if $SCORE >= 60 else "품질 집중 모드"))

with open(metrics_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"품질 모드: {data['current_mode']}")
PYEOF
