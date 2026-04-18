@echo off
chcp 65001 > nul
cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat

echo ========================================
echo   판타지 소설 AI 생성기 (Claude)
echo ========================================
echo.

if not "%ANTHROPIC_API_KEY%"=="" goto run
if exist ".env" goto run

set /p ANTHROPIC_API_KEY="Anthropic API 키를 입력하세요: "

:run
echo.
python fantasy_generator.py
pause
