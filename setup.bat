@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ========================================
echo   KY_FANTASY 설치 마법사
echo ========================================
echo.

cd /d "%~dp0"

:: Python 확인
python --version > nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo        https://python.org 에서 Python 3.11 이상을 설치하세요.
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo Python !PY_VER! 확인됨.
echo.

:: 가상환경 생성 여부 선택
echo  1. 가상환경(venv) 생성 후 설치 (권장)
echo  2. 전역 환경에 바로 설치
echo.
set /p VENV_CHOICE="선택 (1/2, 엔터=1): "
if "!VENV_CHOICE!"=="" set VENV_CHOICE=1

if "!VENV_CHOICE!"=="1" (
    if not exist "venv\" (
        echo 가상환경 생성 중...
        python -m venv venv
    )
    call venv\Scripts\activate.bat
    echo 가상환경 활성화됨: venv\
    echo.
)

:: pip 업그레이드
echo [1/3] pip 업그레이드...
python -m pip install --upgrade pip -q

:: 루트 의존성 설치 (anthropic)
echo [2/3] 기본 의존성 설치 (anthropic)...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [오류] 기본 의존성 설치 실패
    pause
    exit /b 1
)
echo        완료.

:: AI_NovelGenerator 의존성 설치 여부
echo.
echo [3/3] AI_NovelGenerator GUI 의존성 설치 여부
echo       (chromadb, transformers 등 대용량 — 약 2~5분 소요)
set /p GUI_CHOICE="설치할까요? (y/n, 엔터=y): "
if "!GUI_CHOICE!"=="" set GUI_CHOICE=y

if /i "!GUI_CHOICE!"=="y" (
    pip install -r AI_NovelGenerator\requirements.txt -q
    if errorlevel 1 (
        echo [경고] AI_NovelGenerator 의존성 일부 설치 실패. 계속 진행합니다.
    ) else (
        echo        완료.
    )
)

:: API 키 설정
echo.
echo ========================================
echo   API 키 설정
echo ========================================
if exist ".env" (
    echo .env 파일이 이미 존재합니다. 건너뜁니다.
) else (
    echo Anthropic API 키가 필요합니다.
    echo https://console.anthropic.com 에서 발급받으세요.
    echo.
    set /p API_KEY="API 키 입력 (엔터로 건너뜀): "
    if not "!API_KEY!"=="" (
        echo ANTHROPIC_API_KEY="!API_KEY!" > .env
        echo .env 파일에 저장했습니다.
    )
)

:: 완료
echo.
echo ========================================
echo   설치 완료!
echo ========================================
echo.
echo 사용 방법:
echo   소설 생성:   run_fantasy_generator.bat
echo   대시보드:    run_dashboard.bat
echo   GUI 생성기:  run_novel_generator.bat
echo.
echo CLI (빠른 시작):
echo   python fantasy_generator.py quick "테마" -y
echo.

if "!VENV_CHOICE!"=="1" (
    echo 주의: bat 파일 실행 시 venv가 자동으로 활성화됩니다.
    echo.
)

endlocal
pause
