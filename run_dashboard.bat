@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================
echo   판타지 소설 작업현황 대시보드
echo ========================================
echo.
echo  1. 한 번 생성 후 종료
echo  2. 자동 갱신 모드 (30초마다 새로고침)
echo.
set /p MODE="선택 (1/2): "

if "%MODE%"=="2" (
    echo.
    echo [watch] 자동 갱신 모드로 실행합니다. 종료: Ctrl+C
    python dashboard.py --watch
) else (
    python dashboard.py
)

pause
