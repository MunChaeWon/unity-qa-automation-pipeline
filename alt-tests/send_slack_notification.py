from pathlib import Path
from datetime import datetime
import json
import os
import re

import requests
from dotenv import load_dotenv


ALT_TEST_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ALT_TEST_ROOT.parent
ALLURE_RESULTS_DIR = ALT_TEST_ROOT / "alt-allure-results"

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(ALT_TEST_ROOT / ".env")

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def extract_tc_id(test_name: str):
    match = re.search(r"TC[_-]MJ[_-](\d{3})", test_name, re.IGNORECASE)

    if not match:
        return None

    return f"TC-MJ-{match.group(1)}"


def read_allure_results():
    if not ALLURE_RESULTS_DIR.exists():
        raise FileNotFoundError(f"Allure 결과 폴더를 찾을 수 없음: {ALLURE_RESULTS_DIR}")

    result_files = list(ALLURE_RESULTS_DIR.glob("*-result.json"))

    if not result_files:
        raise FileNotFoundError(f"Allure result json 파일이 없음: {ALLURE_RESULTS_DIR}")

    results = []

    for file_path in result_files:
        data = json.loads(file_path.read_text(encoding="utf-8"))

        test_name = data.get("name", "")
        status = data.get("status", "unknown")
        message = data.get("statusDetails", {}).get("message", "")

        tc_id = extract_tc_id(test_name)

        if tc_id is None:
            continue

        results.append({
            "tc_id": tc_id,
            "test_name": test_name,
            "status": status,
            "message": message,
        })

    return sorted(results, key=lambda item: item["tc_id"])


def summarize_results(results):
    total = len(results)
    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")
    broken = sum(1 for item in results if item["status"] == "broken")
    skipped = sum(1 for item in results if item["status"] == "skipped")

    final_result = "Passed" if total > 0 and failed == 0 and broken == 0 else "Failed"

    failed_items = [
        item for item in results
        if item["status"] in ("failed", "broken")
    ]

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "broken": broken,
        "skipped": skipped,
        "final_result": final_result,
        "failed_items": failed_items,
    }


def build_slack_message(summary):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if summary["final_result"] == "Passed":
        title = "[Unity QA 자동화 테스트 결과] Passed"
    else:
        title = "[Unity QA 자동화 테스트 결과] Failed"

    lines = [
        title,
        f"실행일시: {now}",
        f"전체 TC: {summary['total']}",
        f"Pass: {summary['passed']}",
        f"Fail: {summary['failed']}",
        f"Broken: {summary['broken']}",
        f"Skipped: {summary['skipped']}",
        f"최종 결과: {summary['final_result']}",
        "Google Sheets 업데이트: 완료",
    ]

    if summary["failed_items"]:
        lines.append("")
        lines.append("실패/오류 TC:")

        for item in summary["failed_items"]:
            lines.append(f"- {item['tc_id']} / {item['status']}")

    return "\n".join(lines)


def send_slack_message(message):
    if not SLACK_WEBHOOK_URL:
        raise RuntimeError(".env에서 SLACK_WEBHOOK_URL을 찾을 수 없음")

    response = requests.post(
        SLACK_WEBHOOK_URL,
        json={"text": message},
        timeout=10,
    )

    print(f"Slack status code: {response.status_code}")
    print(f"Slack response: {response.text}")

    response.raise_for_status()


def main():
    results = read_allure_results()

    if not results:
        raise RuntimeError("Allure 결과에서 TC-MJ 형식의 테스트를 찾지 못함")

    summary = summarize_results(results)
    message = build_slack_message(summary)

    send_slack_message(message)

    print("Slack 테스트 결과 알림 전송 완료")


if __name__ == "__main__":
    main()