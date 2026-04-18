# KY_FANTASY — 판타지 소설 AI 생성 시스템

## 프로젝트 개요

Claude API와 AI_NovelGenerator를 결합한 판타지 소설 자동 집필 시스템.

- **GitHub**: https://github.com/eunice-101/KY_FANTASY
- **작업 디렉터리**: `C:\Users\10_17\Desktop\Fantasy`

---

## 파일 구조

```
Fantasy/
├── fantasy_generator.py        # Claude API 독립 CLI 소설 생성기 (주력)
├── dashboard.py                # 작업현황 HTML 대시보드 생성기
├── run_fantasy_generator.bat   # 독립 생성기 실행
├── run_dashboard.bat           # 대시보드 실행 (1회 / --watch 모드)
├── run_novel_generator.bat     # AI_NovelGenerator GUI 실행
├── requirements.txt            # anthropic>=0.40.0
├── fantasyfiles/               # 판타지 소설 Claude Code 스킬 소스
├── writing-skills-package/     # 글쓰기 워크플로우 스킬 소스
└── AI_NovelGenerator/          # 멀티 LLM GUI 소설 생성기 (git submodule)
    ├── config.json             # API 키 포함 — gitignore됨, 절대 커밋 금지
    ├── consistency_checker.py
    └── novel_generator/
        ├── blueprint.py
        ├── chapter.py
        └── common.py
```

---

## 핵심 파일 설명

### `fantasy_generator.py`
- **모델**: `claude-sonnet-4-6`
- **지연 초기화**: `get_client()` — import 시 API 키 불요
- **저장**: `save_project()` 호출 시 `AI_NovelGenerator` 파일 구조 자동 동기화
- **로그**: `fantasy_generator.log` 파일에 세계관·캐릭터·플롯·챕터 생성 이력 기록
- **대화형 메뉴** (`python fantasy_generator.py`):
  - 1~4: 세계관·캐릭터·플롯·단일 챕터 생성
  - 5: 전체 챕터 순차 자동 작성
  - 6: 대화형 이야기 모드 (슬라이딩 윈도우 10메시지)
  - 7: 소설 내보내기 `.txt`
  - 8: 저장/불러오기
  - 9: **원클릭 자동 생성** (테마 → 세계관 → 캐릭터 → 플롯 → 전체 챕터)
- **CLI 서브커맨드** (`python fantasy_generator.py <cmd>`):
  - `status` — 현재 프로젝트 현황 출력
  - `quick [theme] [--roles 주인공,악당] [--no-chapters]` — 원클릭 자동 생성
  - `chapter N` — 특정 챕터 작성
  - `all-chapters` — 전체 챕터 순차 작성
  - `export` — `.txt` 내보내기
- **오류 처리**: `_with_retry()` — 429/529/연결 오류 시 지수 백오프 3회
- **스트리밍**: 실패 시 비스트리밍 폴백

### `dashboard.py`
- `python dashboard.py` — 1회 생성 후 브라우저 오픈
- `python dashboard.py --watch` — 30초마다 자동 갱신
- AI_NovelGenerator `config.json`의 `filepath`에서 데이터 읽음
- 표시 항목: 통계 카드 5개, 작업 파일 현황, 최근 장, 차트, 세계관/캐릭터/목차/글로벌 요약 미리보기, 전체 장 목록

### AI_NovelGenerator 데이터 파일 (filepath 기준)
| 파일 | 용도 |
|------|------|
| `novel_architecture.txt` | 세계관 |
| `Novel_directory.txt` | 챕터 목차 (대문자 N 주의) |
| `character_state.txt` | 캐릭터 상태 |
| `global_summary.txt` | 글로벌 요약 |
| `chapters/chapter_N.txt` | 챕터 본문 |

---

## 완료된 버그 수정

| 파일 | 수정 내용 |
|------|---------|
| `dashboard.py` | 블루프린트 파일명 오탈자 (`chapter_blueprint.txt` → `Novel_directory.txt`) |
| `consistency_checker.py` | `interface_format` 기본값 `"OpenAI"` → `"openai"` |
| `blueprint.py` | `tokens_per_chapter` 300→600, 한국어 장번호(`제N장`) 파싱 추가 |
| `common.py` | `debug_log` INFO→DEBUG (터미널 과출력 억제) |
| `fantasy_generator.py` | `_parse_json()` 헬퍼로 취약한 JSON 파싱 교체 |

---

## 설치된 Claude Code 스킬 (`~/.claude/skills/`)

| 스킬 | 설명 |
|------|------|
| `/fantasy-novel-writer` | 베스트셀러급 판타지 소설 10단계 워크플로우 |
| `/prose-style-engine` | 산문 품질 분석·설정·개선 |
| `/dialogue-voice-engine` | 캐릭터별 고유 화법(음성 DNA) 설계 |
| `/beta-reader-simulator` | 5종 독자 페르소나 원고 피드백 |
| `/writing-workflow` | 일반 글쓰기 워크플로우 |
| `/blog-writing-workflow` | 블로그 SEO 최적화 |
| `/brunch-writing-workflow` | 브런치 플랫폼 최적화 |

---

## Git 구조

- **루트 레포**: https://github.com/eunice-101/KY_FANTASY
- **서브모듈**: https://github.com/eunice-101/AI_NovelGenerator (원본 YILING0013에서 fork)
  - 버그 수정 커밋이 fork에 반영됨
  - 원본에 push 권한 없으므로 서브모듈 변경은 항상 fork로 push

## 보안 주의사항

- `AI_NovelGenerator/config.json` — API 키 포함, `.gitignore`에 등록됨. **절대 커밋 금지**
- `.env` — API 키 저장 파일, `.gitignore`에 등록됨. **절대 커밋 금지**
- `my_fantasy_novel.json` — 생성된 소설 데이터, `.gitignore`에 등록됨
- `fantasy_generator.log` — 작업 로그, `.gitignore`에 등록됨

---

## 개발 가이드라인

- AI_NovelGenerator는 git submodule — 변경 시 submodule 디렉터리에서 별도 커밋
- `fantasy_generator.py` 수정 후 반드시 `python -c "import fantasy_generator"` 로 import 테스트
- 대시보드 수정 후 `python dashboard.py` 로 생성 확인
- 챕터 표기는 한국어 통일: `제N장` (중국어 `第N章` 사용 금지)
