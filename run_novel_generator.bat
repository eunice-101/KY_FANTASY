@echo off
chcp 65001 > nul
echo ========================================
echo   AI 판타지 소설 생성기 (AI_NovelGenerator)
echo ========================================
echo.

cd /d "%~dp0"

:: .env 파일에서 API 키 읽기
if exist ".env" (
    for /f "tokens=1,* delims==" %%A in (.env) do (
        if "%%A"=="ANTHROPIC_API_KEY" set ANTHROPIC_API_KEY=%%B
    )
)

:: 환경 변수도 없으면 직접 입력
if "%ANTHROPIC_API_KEY%"=="" (
    set /p ANTHROPIC_API_KEY="Anthropic API 키를 입력하세요: "
)

echo.
echo GUI 실행 중...
cd /d "%~dp0AI_NovelGenerator"
python main.py

pause
