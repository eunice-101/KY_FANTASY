@echo off
chcp 65001 > nul
echo ========================================
echo   AI 판타지 소설 생성기 (AI_NovelGenerator)
echo ========================================
echo.

cd /d "%~dp0AI_NovelGenerator"

:: API 키 입력
if "%ANTHROPIC_API_KEY%"=="" (
    set /p ANTHROPIC_API_KEY="Anthropic API 키를 입력하세요: "
)

echo.
echo GUI 실행 중...
python main.py

pause
