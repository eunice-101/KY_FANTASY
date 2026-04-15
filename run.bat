@echo off
chcp 65001 >nul
echo ============================================
echo   KY Fantasy 소설 자동화 시스템 대시보드
echo ============================================
echo.

cd /d "%~dp0"

REM .env 파일 확인
if not exist ".env" (
    echo [경고] .env 파일이 없습니다.
    echo .env.example을 복사해서 API 키를 설정하세요.
    echo copy .env.example .env
    echo.
)

REM 의존성 설치 확인
python -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo Flask 설치 중...
    pip install -r requirements.txt
)

echo 대시보드 시작: http://127.0.0.1:8765
echo 종료하려면 Ctrl+C 를 누르세요.
echo.

python web/app.py
pause
