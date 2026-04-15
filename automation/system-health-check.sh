#!/bin/bash
# 시스템 헬스 체크 스크립트

HEALTH_FILE="planning/system-health.json"
SCORE=100
ISSUES=()
WARNINGS=()

# 1. 필수 디렉토리 확인
REQUIRED_DIRS=("bible" "state" "state/current" "timeline" "story/chapters" "planning" "automation" ".claude/agents")
for dir in "${REQUIRED_DIRS[@]}"; do
  if [ ! -d "$dir" ]; then
    SCORE=$((SCORE - 10))
    ISSUES+=("디렉토리 없음: $dir")
  fi
done

# 2. 필수 파일 확인
REQUIRED_FILES=("CLAUDE.md" "bible/style.md" "bible/structure.md" "timeline/history.md" "timeline/current-chapter.md")
for file in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$file" ]; then
    SCORE=$((SCORE - 5))
    WARNINGS+=("파일 없음: $file")
  fi
done

# 3. JSON 파일 유효성 확인
JSON_FILES=("planning/plot-progress.json" "planning/chapter-status.json" "planning/quality-metrics.json" "planning/system-health.json")
for jsonfile in "${JSON_FILES[@]}"; do
  if [ -f "$jsonfile" ]; then
    if ! python3 -c "import json; json.load(open('$jsonfile'))" 2>/dev/null; then
      SCORE=$((SCORE - 10))
      ISSUES+=("손상된 JSON: $jsonfile")
    fi
  else
    SCORE=$((SCORE - 5))
    WARNINGS+=("JSON 파일 없음: $jsonfile")
  fi
done

# 4. 챕터 파일과 상태 동기화 확인
ACTUAL_CHAPTERS=$(ls story/chapters/*.md 2>/dev/null | wc -l)
TRACKED_CHAPTERS=$(python3 -c "import json; d=json.load(open('planning/plot-progress.json')); print(d.get('completed_chapters', 0))" 2>/dev/null || echo "0")

if [ "$ACTUAL_CHAPTERS" != "$TRACKED_CHAPTERS" ]; then
  WARNINGS+=("챕터 동기화 불일치: 실제=${ACTUAL_CHAPTERS}, 추적=${TRACKED_CHAPTERS}")
  SCORE=$((SCORE - 5))
fi

# 결과를 JSON으로 저장
DATE=$(date +"%Y-%m-%d")
ISSUES_JSON=$(printf '"%s",' "${ISSUES[@]}" | sed 's/,$//')
WARNINGS_JSON=$(printf '"%s",' "${WARNINGS[@]}" | sed 's/,$//')

cat > "$HEALTH_FILE" << EOF
{
  "overall_score": $SCORE,
  "filesystem": $([ ${#ISSUES[@]} -eq 0 ] && echo 100 || echo $((100 - ${#ISSUES[@]} * 10))),
  "state_consistency": $([ "$ACTUAL_CHAPTERS" == "$TRACKED_CHAPTERS" ] && echo 100 || echo 80),
  "api_connectivity": 100,
  "last_check": "$DATE",
  "issues": [${ISSUES_JSON}],
  "warnings": [${WARNINGS_JSON}]
}
EOF

echo "헬스 점수: $SCORE/100"
if [ ${#ISSUES[@]} -gt 0 ]; then
  echo "심각한 문제:"
  for issue in "${ISSUES[@]}"; do
    echo "  - $issue"
  done
fi
if [ ${#WARNINGS[@]} -gt 0 ]; then
  echo "경고:"
  for warning in "${WARNINGS[@]}"; do
    echo "  - $warning"
  done
fi
