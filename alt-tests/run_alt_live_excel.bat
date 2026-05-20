@echo off
chcp 65001 > nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

cd /d D:\funity\Test1\alt-tests

echo [INFO] AltTester Live Excel Regression Test Start
echo [INFO] TC_Result.xlsx 파일이 Excel에서 열려 있어야 합니다.
echo.

echo [START] AltTester pytest 실행 - 정상 8개 TC
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
    echo Allure 리포트 생성 실패
    pause
    exit /b %ALLURE_GENERATE_EXIT_CODE%
)

echo [START] Jira 이슈 생성
python upload_alt_jira_result.py
set JIRA_EXIT_CODE=%ERRORLEVEL%
echo jira upload exit code: %JIRA_EXIT_CODE%
echo.

if not "%JIRA_EXIT_CODE%"=="0" (
    echo Jira 업로드 실패
    pause
    exit /b %JIRA_EXIT_CODE%
)

echo [START] Allure HTML 리포트 열기
call allure open alt-allure-report
set ALLURE_OPEN_EXIT_CODE=%ERRORLEVEL%
echo allure open exit code: %ALLURE_OPEN_EXIT_CODE%
echo.

echo [END] AltTester Live Excel Regression Test Complete
pause
exit /b %TEST_EXIT_CODE%