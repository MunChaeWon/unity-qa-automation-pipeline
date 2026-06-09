@echo off
chcp 65001 >nul
echo ========================================================
echo  GitHub Actions CI/CD Pipeline - Automated Testing
echo ========================================================

:: [1단계] 안정적인 테스트 환경 확보를 위해 기존 잔여 프로세스 강제 종료
taskkill /f /im "Test1.exe" 2>nul
taskkill /f /im "allure.exe" 2>nul
ping 127.0.0.1 -n 3 >nul

:: [2단계] 타깃 유니티 빌드 파일(Test1.exe) 가동 및 소켓 대기
start "" "D:\funity\Test1\Build\Test1.exe" -screen-width 640 -screen-height 480 -screen-fullscreen 0 -force-d3d11
echo [INFO] Unity 게임 프로세스 기동 완료. 소켓 포트 활성화를 위해 10초간 대기합니다.
ping 127.0.0.1 -n 11 >nul

:: [3단계] 통합 테스트 및 마스터 파이프라인(Google Sheets / Slack) 배치 파일 호출
echo [INFO] 마스터 자동화 파이프라인 연동 공정 가동 시작.
call "D:\funity\Test1\alt-tests\run_alt_google_slack_pipeline.bat"

:: [4단계] 테스트 완료에 따른 시스템 자원 회수 및 프로세스 강제 종료
echo ========================================================
echo [INFO] 테스트 시나리오 종료. 가동 프로세스 및 웹 서버를 종료합니다.
echo ========================================================
taskkill /f /im "Test1.exe" 2>nul
taskkill /f /im "allure.exe" 2>nul