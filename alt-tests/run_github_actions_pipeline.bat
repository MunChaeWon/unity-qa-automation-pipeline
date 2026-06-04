@echo off
chcp 65001 >nul
echo ========================================================
echo [주군의 무인 일꾼] GitHub Actions 전용 완전 무인 파이프라인 가동
echo ========================================================

:: 1. 혹시 메모리에 좀비처럼 남아있을지 모르는 이전 유니티 게임 프로세스를 완벽히 처단합니다
taskkill /f /im "YourGameName.exe" 2>nul
timeout /t 2

:: 2. AltTester 소켓이 심어진 유니티 빌드 파일(.exe)을 화면 없이 백그라운드로 강제 실행합니다
:: ※ 주군, 아래 경로와 "YourGameName.exe" 부분을 실제 빌드 파일 경로와 이름으로 꼭 수정해 주소서!
start "" "D:\funity\Build\YourGameName.exe" -screen-width 640 -screen-height 480 -screen-fullscreen 0
echo 유니티 게임 기상 완료. 소켓 포트 대기를 위해 10초간 대기합니다...
timeout /t 10

:: 3. 유니티가 깨어났으니, 주군이 기존에 완벽하게 짜두셨던 구글/슬랙 마스터 배치 파일을 호출합니다
echo 기존 구글/슬랙 마스터 파이프라인 연동 가동...
call D:\funity\Test1\alt-tests\run_alt_google_slack_pipeline.bat

:: 4. 모든 테스트와 슬랙 전송이 끝났으므로, 켜두었던 유니티 게임을 스스로 끄고 퇴근하게 만듭니다
echo ========================================================
echo [주군의 무인 일꾼] 테스트 종료. 가동했던 유니티 게임을 안전하게 폐점합니다.
echo ========================================================
taskkill /f /im "YourGameName.exe" 2>nul