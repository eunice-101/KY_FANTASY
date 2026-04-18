"""
판타지 소설 AI 생성 시스템
Claude API를 사용하여 세계관, 캐릭터, 플롯, 챕터를 자동 생성합니다.
"""

import anthropic
import json
import os
import re
from pathlib import Path


def _parse_json(text: str) -> dict:
    """LLM 응답에서 JSON 객체를 추출합니다."""
    match = re.search(r'\{[\s\S]*\}', text)
    if not match:
        raise ValueError(f"JSON 객체를 찾을 수 없습니다: {text[:200]}")
    return json.loads(match.group())

MODEL = "claude-opus-4-6"


def _get_client() -> anthropic.Anthropic:
    """API 키를 확인하고 클라이언트를 반환합니다."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        # .env 파일에서 읽기
        env_file = Path(".env")
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("ANTHROPIC_API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not api_key:
        print("\n🔑 ANTHROPIC_API_KEY가 설정되지 않았습니다.")
        print("   https://console.anthropic.com 에서 API 키를 발급받으세요.")
        api_key = input("   API 키를 입력하세요: ").strip()
        if api_key:
            # .env 파일에 저장
            Path(".env").write_text(f'ANTHROPIC_API_KEY="{api_key}"\n', encoding="utf-8")
            print("   ✅ .env 파일에 저장했습니다.")
    return anthropic.Anthropic(api_key=api_key)


client = _get_client()

SYSTEM_PROMPT = """당신은 세계적인 수준의 판타지 소설 작가입니다.
독창적이고 생생한 판타지 세계를 구축하고, 입체적인 캐릭터와
흡입력 있는 이야기를 창조하는 전문가입니다.

작성 원칙:
- 풍부하고 구체적인 묘사
- 감정이 살아있는 대화
- 긴장감과 흥미를 유지
- 일관된 세계관과 설정
- 독자를 몰입시키는 문체

항상 한국어로 작성하세요."""


# ─────────────────────────────────────────────
# 1. 세계관 생성
# ─────────────────────────────────────────────

def generate_world(theme: str = "") -> dict:
    """판타지 세계관을 생성합니다."""
    print("\n🌍 세계관을 생성 중입니다...")

    prompt = f"""판타지 소설의 세계관을 창조해주세요.
{'테마: ' + theme if theme else '독창적인 테마로 자유롭게 생성해주세요.'}

다음 JSON 형식으로 반환해주세요:
{{
  "world_name": "세계 이름",
  "theme": "핵심 테마",
  "description": "세계관 전반적인 설명 (200자 이상)",
  "geography": "주요 지형과 지역 설명",
  "magic_system": "마법/능력 체계 설명",
  "history": "주요 역사적 사건과 배경",
  "races": ["종족1", "종족2", "종족3"],
  "conflicts": "현재 세계의 주요 갈등과 위기",
  "atmosphere": "세계의 분위기와 톤"
}}

JSON만 반환하세요."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        thinking={"type": "adaptive"},
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": prompt}],
    )

    text = next(b.text for b in response.content if b.type == "text")
    world = _parse_json(text)
    print(f"✅ '{world['world_name']}' 세계관 생성 완료!")
    return world


# ─────────────────────────────────────────────
# 2. 캐릭터 생성
# ─────────────────────────────────────────────

def generate_character(world: dict, role: str = "주인공") -> dict:
    """캐릭터를 생성합니다."""
    print(f"\n👤 {role} 캐릭터를 생성 중입니다...")

    prompt = f"""다음 세계관에 맞는 {role} 캐릭터를 만들어주세요.

세계관: {world['world_name']}
설명: {world['description']}
마법 체계: {world['magic_system']}
갈등: {world['conflicts']}

다음 JSON 형식으로 반환해주세요:
{{
  "name": "이름",
  "role": "{role}",
  "age": 나이(숫자),
  "race": "종족",
  "appearance": "외모 묘사",
  "personality": "성격과 특징",
  "background": "과거 배경과 성장 이야기",
  "motivation": "주요 동기와 목표",
  "abilities": "능력과 기술",
  "weakness": "약점과 내면의 갈등",
  "secret": "숨겨진 비밀 또는 과거"
}}

JSON만 반환하세요."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": prompt}],
    )

    text = next(b.text for b in response.content if b.type == "text")
    character = _parse_json(text)
    print(f"✅ 캐릭터 '{character['name']}' 생성 완료!")
    return character


# ─────────────────────────────────────────────
# 3. 플롯 생성
# ─────────────────────────────────────────────

def generate_plot(world: dict, characters: list[dict]) -> dict:
    """스토리 플롯을 생성합니다. 복잡한 작업이므로 adaptive thinking 사용."""
    print("\n📖 플롯을 구성 중입니다... (깊이 있는 사고 중)")

    char_summary = "\n".join(
        f"- {c['name']} ({c['role']}): {c['motivation']}" for c in characters
    )

    prompt = f"""다음 세계관과 캐릭터들을 바탕으로 판타지 소설의 전체 플롯을 구성해주세요.

=== 세계관 ===
이름: {world['world_name']}
테마: {world['theme']}
갈등: {world['conflicts']}

=== 캐릭터 ===
{char_summary}

복잡하고 흥미로운 플롯을 설계하세요. 다음 JSON 형식으로 반환해주세요:
{{
  "title": "소설 제목",
  "logline": "한 문장 요약",
  "genre_tags": ["장르태그1", "장르태그2"],
  "total_chapters": 총챕터수(숫자),
  "acts": [
    {{
      "act": 1,
      "name": "막 이름",
      "summary": "이 막의 요약",
      "key_events": ["사건1", "사건2", "사건3"],
      "chapters": [1, 2, 3]
    }}
  ],
  "chapter_outlines": [
    {{
      "chapter": 1,
      "title": "챕터 제목",
      "summary": "챕터 내용 요약",
      "key_scene": "핵심 장면",
      "emotional_beat": "감정적 흐름"
    }}
  ],
  "climax": "클라이맥스 설명",
  "resolution": "결말 설명",
  "themes": ["주제1", "주제2"]
}}

최소 3개의 막(act), 12개 이상의 챕터를 포함하세요. JSON만 반환하세요."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        thinking={"type": "adaptive"},
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": prompt}],
    )

    text = next(b.text for b in response.content if b.type == "text")
    plot = _parse_json(text)
    print(f"✅ 플롯 '{plot['title']}' 생성 완료! (총 {plot['total_chapters']}챕터)")
    return plot


# ─────────────────────────────────────────────
# 4. 챕터 작성 (스트리밍)
# ─────────────────────────────────────────────

def write_chapter(world: dict, characters: list[dict], plot: dict, chapter_num: int) -> str:
    """챕터를 스트리밍으로 작성합니다."""
    # 챕터 정보 찾기
    outline = next(
        (c for c in plot["chapter_outlines"] if c["chapter"] == chapter_num),
        None
    )
    if not outline:
        print(f"⚠️ {chapter_num}챕터 정보를 찾을 수 없습니다.")
        return ""

    print(f"\n✍️ {chapter_num}챕터: '{outline['title']}' 작성 중...")
    print("─" * 50)

    char_context = "\n".join(
        f"- {c['name']}: {c['personality']} / 능력: {c['abilities']}" for c in characters
    )

    prompt = f"""다음 정보를 바탕으로 판타지 소설의 {chapter_num}챕터를 완성된 소설 문체로 작성해주세요.

=== 세계관 ===
{world['world_name']}: {world['description'][:300]}

=== 등장인물 ===
{char_context}

=== 소설 정보 ===
제목: {plot['title']}
전체 테마: {', '.join(plot['themes'])}

=== {chapter_num}챕터 정보 ===
제목: {outline['title']}
내용: {outline['summary']}
핵심 장면: {outline['key_scene']}
감정 흐름: {outline['emotional_beat']}

요구사항:
- 최소 1500자 이상의 풍부한 서술
- 생생한 장면 묘사와 대화
- 감정과 긴장감이 살아있는 문체
- 챕터 제목을 맨 위에 표시
- 소설 본문만 작성 (설명 없이)"""

    full_text = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=3000,
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_text += text

    print("\n" + "─" * 50)
    print(f"✅ {chapter_num}챕터 작성 완료! ({len(full_text)}자)")
    return full_text


# ─────────────────────────────────────────────
# 5. 저장 / 불러오기
# ─────────────────────────────────────────────

def save_project(project: dict, filename: str = "my_fantasy_novel.json"):
    """프로젝트를 JSON 파일로 저장합니다."""
    path = Path(filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(project, f, ensure_ascii=False, indent=2)
    print(f"\n💾 '{path}' 에 저장되었습니다.")


def load_project(filename: str = "my_fantasy_novel.json") -> dict | None:
    """저장된 프로젝트를 불러옵니다."""
    path = Path(filename)
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def export_novel(project: dict):
    """소설을 텍스트 파일로 출력합니다."""
    title = project.get("plot", {}).get("title", "나의_판타지_소설")
    filename = f"{title}.txt"
    lines = []

    if "plot" in project:
        lines.append(f"{'=' * 60}")
        lines.append(f"  {project['plot']['title']}")
        lines.append(f"{'=' * 60}\n")
        lines.append(f"장르: {', '.join(project['plot'].get('genre_tags', []))}")
        lines.append(f"한줄 요약: {project['plot'].get('logline', '')}\n")

    for num, content in sorted(project.get("chapters", {}).items(), key=lambda x: int(x[0])):
        lines.append(f"\n{'─' * 60}")
        lines.append(content)

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n📄 '{filename}' 로 출력되었습니다.")


# ─────────────────────────────────────────────
# 6. 대화형 이야기 계속하기
# ─────────────────────────────────────────────

def interactive_story(project: dict):
    """사용자와 함께 이야기를 이어나갑니다."""
    world = project.get("world", {})
    characters = project.get("characters", [])
    plot = project.get("plot", {})

    context = f"""세계관: {world.get('world_name', '')} - {world.get('description', '')[:200]}
주인공: {', '.join(c['name'] for c in characters)}
소설: {plot.get('title', '')}"""

    print("\n🎭 대화형 이야기 모드")
    print("이야기를 이어나가거나 방향을 제시하세요. ('종료' 입력 시 메뉴로)")
    print("─" * 50)

    messages = [
        {"role": "user", "content": f"다음 설정으로 대화형 판타지 소설을 진행합니다:\n{context}\n\n이야기를 시작해주세요."}
    ]

    # 첫 이야기 시작
    with client.messages.stream(
        model=MODEL,
        max_tokens=800,
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=messages,
    ) as stream:
        response_text = ""
        for text in stream.text_stream:
            print(text, end="", flush=True)
            response_text += text
    print()

    messages.append({"role": "assistant", "content": response_text})

    while True:
        user_input = input("\n🖊️ 당신: ").strip()
        if user_input in ("종료", "exit", "quit"):
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        print("\n📖 ", end="")
        with client.messages.stream(
            model=MODEL,
            max_tokens=600,
            system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
            messages=messages,
        ) as stream:
            response_text = ""
            for text in stream.text_stream:
                print(text, end="", flush=True)
                response_text += text
        print()

        messages.append({"role": "assistant", "content": response_text})


# ─────────────────────────────────────────────
# 메인 메뉴
# ─────────────────────────────────────────────

def print_menu(project: dict):
    title = project.get("plot", {}).get("title", "없음")
    has_world = "✅" if "world" in project else "❌"
    has_chars = f"✅ ({len(project.get('characters', []))}명)" if "characters" in project else "❌"
    has_plot = "✅" if "plot" in project else "❌"
    chapter_count = len(project.get("chapters", {}))

    print(f"""
╔══════════════════════════════════════╗
║    🏰 판타지 소설 AI 생성 시스템      ║
╠══════════════════════════════════════╣
║  현재 소설: {title[:20]:<20} ║
║  세계관: {has_world}  캐릭터: {has_chars}      ║
║  플롯: {has_plot}  작성된 챕터: {chapter_count}개           ║
╠══════════════════════════════════════╣
║  1. 세계관 생성                      ║
║  2. 캐릭터 추가                      ║
║  3. 플롯 생성                        ║
║  4. 챕터 작성                        ║
║  5. 대화형 이야기 모드               ║
║  6. 소설 내보내기 (.txt)             ║
║  7. 저장 / 불러오기                  ║
║  0. 종료                            ║
╚══════════════════════════════════════╝""")


def main():
    project = {}

    # 저장 파일 자동 로드
    saved = load_project()
    if saved:
        ans = input("\n💾 저장된 프로젝트를 발견했습니다. 불러올까요? (y/n): ").strip().lower()
        if ans == "y":
            project = saved
            print(f"✅ '{project.get('plot', {}).get('title', '프로젝트')}' 불러왔습니다.")

    while True:
        print_menu(project)
        choice = input("\n선택: ").strip()

        if choice == "1":
            theme = input("테마를 입력하세요 (엔터 = 자동): ").strip()
            project["world"] = generate_world(theme)
            save_project(project)

        elif choice == "2":
            if "world" not in project:
                print("⚠️ 먼저 세계관을 생성해주세요.")
                continue
            role = input("역할 (주인공/악당/조력자 등): ").strip() or "주인공"
            char = generate_character(project["world"], role)
            project.setdefault("characters", []).append(char)
            save_project(project)

        elif choice == "3":
            if "world" not in project or not project.get("characters"):
                print("⚠️ 세계관과 최소 1명의 캐릭터가 필요합니다.")
                continue
            project["plot"] = generate_plot(project["world"], project["characters"])
            save_project(project)

        elif choice == "4":
            if "plot" not in project:
                print("⚠️ 먼저 플롯을 생성해주세요.")
                continue
            total = project["plot"]["total_chapters"]
            written = list(project.get("chapters", {}).keys())
            print(f"\n총 {total}챕터 | 작성됨: {written or '없음'}")

            try:
                num = int(input(f"작성할 챕터 번호 (1~{total}): ").strip())
            except ValueError:
                print("⚠️ 올바른 번호를 입력하세요.")
                continue

            content = write_chapter(
                project["world"],
                project["characters"],
                project["plot"],
                num
            )
            if content:
                project.setdefault("chapters", {})[str(num)] = content
                save_project(project)

        elif choice == "5":
            if not project:
                print("⚠️ 먼저 세계관과 캐릭터를 만들어주세요.")
                continue
            interactive_story(project)

        elif choice == "6":
            if not project.get("chapters"):
                print("⚠️ 작성된 챕터가 없습니다.")
                continue
            export_novel(project)

        elif choice == "7":
            sub = input("저장(s) / 불러오기(l): ").strip().lower()
            if sub == "s":
                fname = input("파일명 (엔터=기본값): ").strip() or "my_fantasy_novel.json"
                save_project(project, fname)
            elif sub == "l":
                fname = input("파일명 (엔터=기본값): ").strip() or "my_fantasy_novel.json"
                loaded = load_project(fname)
                if loaded:
                    project = loaded
                    print("✅ 불러왔습니다.")
                else:
                    print(f"⚠️ '{fname}' 파일을 찾을 수 없습니다.")

        elif choice == "0":
            print("\n👋 소설 생성을 종료합니다. 좋은 작품 되세요!")
            break

        else:
            print("⚠️ 올바른 번호를 입력하세요.")


if __name__ == "__main__":
    main()
