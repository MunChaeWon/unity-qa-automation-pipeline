@echo off
chcp 65001 > nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

cd /d D:\funity\Test1\alt-tests

echo [INFO] Unity QA Google Sheets + Slack Pipeline Start
echo [INFO] Unity AltTester Play in Editor 상태를 먼저 확인해야 합니다.
echo.

echo [START] AltTester pytest 실행
python -m pytest tests\test_player_bridge_movement.py -v -s --alluredir=alt-allure-results --clean-alluredir
set TEST_EXIT_CODE=%ERRORLEVEL%
echo pytest exit code: %TEST_EXIT_CODE%
echo.

echo [START] Allure HTML 리포트 생성
call allure generate alt-allure-results -o alt-allure-report --clean
set ALLURE_GENERATE_EXIT_CODE=%ERRORLEVEL%
echo allure generate exit code: %ALLURE_GENERATE_EXIT_CODE%
echo.

if not "%ALLURE_GENERATE_EXIT_CODE%"=="0" (
    echo [ERROR] Allure 리포트 생성 실패
    exit /b %ALLURE_GENERATE_EXIT_CODE%
)

echo [START] Jira 이슈 생성
python upload_alt_jira_result.py
set JIRA_EXIT_CODE=%ERRORLEVEL%
echo jira upload exit code: %JIRA_EXIT_CODE%
echo.

if not "%JIRA_EXIT_CODE%"=="0" (
    echo [WARNING] Jira 업로드 실패 (프로세스는 계속 진행됩니다)
)

echo [START] Slack 알림 전송
python send_slack_notification.py
set SLACK_EXIT_CODE=%ERRORLEVEL%
echo slack notification exit code: %SLACK_EXIT_CODE%
echo.

if not "%SLACK_EXIT_CODE%"=="0" (
    echo [WARNING] Slack 알림 전송 실패
)

echo [END] Unity QA Google Sheets + Slack Pipeline Complete
echo [INFO] 최종 pytest 종료 코드: %TEST_EXIT_CODE%

exit /b %TEST_EXIT_CODE%