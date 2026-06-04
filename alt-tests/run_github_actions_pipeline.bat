@echo off
chcp 65001 >nul
echo ========================================================
echo [주군의 무인 일꾼] GitHub Actions 전용 완전 무인 파이프라인 가동
echo ========================================================

:: [1단계] 혹시 메모리에 좀비처럼 남아있을지 모르는 이전 게임과 웹 서버 프로세스를 완벽히 처단합니다
taskkill /f /im "Test1.exe" 2>nul
taskkill /f /im "allure.exe" 2>nul
timeout /t 2

:: [2단계] 주군께서 명시하신 진짜 경로의 유니티 빌드 파일(Test1.exe)을 백그라운드로 강제 실행합니다
start "" "D:\funity\Test1\Build\Test1.exe" -screen-width 640 -screen-height 480 -screen-fullscreen 0 -force-d3d11
echo 유니티 게임(Test1.exe) 기상 완료. 소켓 포트 대기를 위해 10초간 대기합니다...
timeout /t 10

:: [3단계] 주군이 기존에 짜두셨던 구글/슬랙 마스터 배치 파일을 호출합니다
echo 기존 구글/슬랙 마스터 파이프라인 연동 가동...
call D:\funity\Test1\alt-tests\run_alt_google_slack_pipeline.bat

:: [4단계] ★Ctrl+C 박멸 구역★ 모든 일이 끝났으므로 켜두었던 게임과 웹 서버의 목을 베어 퇴근시킵니다
echo ========================================================
echo [주군의 무인 일꾼] 테스트 종료. 가동했던 유니티 게임 및 무한 대기 웹 서버를 강제 종료합니다.
echo ========================================================
taskkill /f /im "Test1.exe" 2>nul
taskkill /f /im "allure.exe" 2>nul
echo 파이프라인이 깔끔하게 정리되었습니다. 일꾼 퇴근 승인!