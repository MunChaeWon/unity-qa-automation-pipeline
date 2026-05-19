from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]

UNITY_EXE = Path(r"D:\funity\Hub\Editor\2022.3.62f3\Editor\Unity.exe")
UNITY_PROJECT = PROJECT_ROOT

RUN_TIME = datetime.now()
RUN_DATE = RUN_TIME.strftime("%Y-%m-%d")
RUN_ID = RUN_TIME.strftime("%H%M%S")

RUN_RESULT_DIR = PROJECT_ROOT / "TestResults" / RUN_DATE
UNITY_RESULT_XML = RUN_RESULT_DIR / f"{RUN_ID}-playmode-result.xml"
UNITY_LOG_FILE = RUN_RESULT_DIR / f"{RUN_ID}-unity-test-log.txt"

LATEST_RESULT_XML = PROJECT_ROOT / "TestResults" / "playmode-result.xml"
LATEST_LOG_FILE = PROJECT_ROOT / "TestResults" / "unity-test-log.txt"

JIRA_SCRIPT = PROJECT_ROOT / "qa-tools" / "upload_jira_result.py"
ALLURE_RESULT_SCRIPT = PROJECT_ROOT / "qa-tools" / "create_allure_result.py"

ALLURE_RESULTS_DIR = PROJECT_ROOT / "allure-results"
ALLURE_REPORT_DIR = PROJECT_ROOT / "allure-report"


def find_allure_command():
    allure_command = shutil.which("allure") or shutil.which("allure.bat")

    if allure_command:
        return allure_command

    raise FileNotFoundError(
        "Allure 실행 파일을 찾을 수 없음. CMD에서 'where allure' 명령어로 설치 경로 확인 필요"
    )


def run_command(command, title, allow_failure=False):
    print()
    print(f"[START] {title}")
    print(" ".join(str(part) for part in command))

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        shell=False
    )

    if result.returncode != 0:
        if allow_failure:
            print(f"[DONE WITH TEST FAILURE] {title}. Exit Code: {result.returncode}")
            return result.returncode

        raise RuntimeError(f"{title} 실패. 종료 코드: {result.returncode}")

    print(f"[DONE] {title}")
    return result.returncode


def run_unity_playmode_tests():
    RUN_RESULT_DIR.mkdir(parents=True, exist_ok=True)

    command = [
        str(UNITY_EXE),
        "-batchmode",
        "-projectPath",
        str(UNITY_PROJECT),
        "-runTests",
        "-testPlatform",
        "PlayMode",
        "-testResults",
        str(UNITY_RESULT_XML),
        "-logFile",
        str(UNITY_LOG_FILE)
    ]

    run_command(command, "Unity PlayMode 테스트 실행", allow_failure=True)

    if not UNITY_RESULT_XML.exists():
        raise FileNotFoundError(f"Unity 테스트 결과 XML 생성 실패: {UNITY_RESULT_XML}")

    shutil.copy2(UNITY_RESULT_XML, LATEST_RESULT_XML)
    shutil.copy2(UNITY_LOG_FILE, LATEST_LOG_FILE)


def upload_result_to_jira():
    command = [
        sys.executable,
        str(JIRA_SCRIPT)
    ]

    run_command(command, "Jira 이슈 생성")


def create_allure_results():
    command = [
        sys.executable,
        str(ALLURE_RESULT_SCRIPT)
    ]

    run_command(command, "Allure 결과 JSON 생성")


def generate_allure_report():
    allure_command = find_allure_command()

    command = [
        allure_command,
        "generate",
        str(ALLURE_RESULTS_DIR),
        "-o",
        str(ALLURE_REPORT_DIR),
        "--clean"
    ]

    run_command(command, "Allure HTML 리포트 생성")


def open_allure_report():
    allure_command = find_allure_command()

    command = [
        allure_command,
        "open",
        str(ALLURE_REPORT_DIR)
    ]

    run_command(command, "Allure HTML 리포트 열기")


def main():
    print("QA Pipeline Start")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Run Result Directory: {RUN_RESULT_DIR}")

    run_unity_playmode_tests()
    upload_result_to_jira()
    create_allure_results()
    generate_allure_report()
    open_allure_report()

    print()
    print("QA Pipeline Done")
    print(f"Run Result XML: {UNITY_RESULT_XML}")
    print(f"Run Log: {UNITY_LOG_FILE}")
    print(f"Latest Result XML: {LATEST_RESULT_XML}")
    print(f"Latest Log: {LATEST_LOG_FILE}")
    print(f"Allure Results: {ALLURE_RESULTS_DIR}")
    print(f"Allure Report: {ALLURE_REPORT_DIR}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print()
        print(f"QA Pipeline Failed: {error}")
        sys.exit(1)