from pathlib import Path
from datetime import datetime
import json
import os
import requests
from dotenv import load_dotenv


ALT_TEST_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ALT_TEST_ROOT.parent

ENV_PATH = PROJECT_ROOT / ".env"
ALLURE_RESULTS_DIR = ALT_TEST_ROOT / "alt-allure-results"


def load_config():
    load_dotenv(ENV_PATH)

    config = {
        "server": os.getenv("JIRA_SERVER"),
        "email": os.getenv("JIRA_EMAIL"),
        "token": os.getenv("JIRA_API_TOKEN"),
        "project_key": os.getenv("JIRA_PROJECT_KEY", "FF12"),
        "success_issue_type": os.getenv("JIRA_SUCCESS_ISSUE_TYPE", "Task"),
        "fail_issue_type": os.getenv("JIRA_FAIL_ISSUE_TYPE", "Bug"),
    }

    missing = [key for key, value in config.items() if not value]
    if missing:
        raise RuntimeError(f".env 값 누락: {', '.join(missing)}")

    return config


def read_allure_results():
    if not ALLURE_RESULTS_DIR.exists():
        raise FileNotFoundError(f"Allure 결과 폴더를 찾을 수 없음: {ALLURE_RESULTS_DIR}")

    result_files = list(ALLURE_RESULTS_DIR.glob("*-result.json"))

    if not result_files:
        raise FileNotFoundError(f"Allure result json 파일이 없음: {ALLURE_RESULTS_DIR}")

    cases = []

    for file_path in result_files:
        data = json.loads(file_path.read_text(encoding="utf-8"))

        cases.append({
            "name": data.get("name", "Unknown"),
            "full_name": data.get("fullName", ""),
            "status": data.get("status", "unknown"),
            "message": data.get("statusDetails", {}).get("message", ""),
            "trace": data.get("statusDetails", {}).get("trace", ""),
        })

    total = len(cases)
    passed = sum(1 for case in cases if case["status"] == "passed")
    failed = sum(1 for case in cases if case["status"] == "failed")
    skipped = sum(1 for case in cases if case["status"] == "skipped")
    broken = sum(1 for case in cases if case["status"] == "broken")

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "broken": broken,
        "cases": sorted(cases, key=lambda item: item["name"]),
    }


def build_description(summary):
    lines = [
        "AltTester 자동화 테스트 결과",
        "",
        f"- 실행 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "- 프로젝트: Unity 2D Platformer Microgame",
        "- 테스트 방식: AltTester + pytest + TestInputBridge",
        "- 테스트 대상: Player 이동/점프 기능",
        "- 테스트 범위: TC-MJ-001 ~ TC-MJ-008",
        f"- 전체 테스트 수: {summary['total']}",
        f"- 성공: {summary['passed']}",
        f"- 실패: {summary['failed']}",
        f"- Broken: {summary['broken']}",
        f"- Skipped: {summary['skipped']}",
        "",
        "테스트 케이스 목록",
    ]

    for case in summary["cases"]:
        lines.append(f"- {case['name']}: {case['status']}")

    failed_cases = [
        case for case in summary["cases"]
        if case["status"] in ("failed", "broken")
    ]

    if failed_cases:
        lines.append("")
        lines.append("실패 상세")
        for case in failed_cases:
            lines.append(f"- 테스트명: {case['name']}")
            lines.append(f"  상태: {case['status']}")
            lines.append(f"  메시지: {case['message'][:500]}")
            lines.append(f"  Trace: {case['trace'][:700]}")

    lines.append("")
    lines.append("비고")
    lines.append("- AltTester press_key 입력은 Editor PlayMode 환경에서 안정적으로 반영되지 않아 TestInputBridge 입력값 주입 방식으로 자동화함")
    lines.append("- 실제 A/D/Space 키 입력 가능 여부는 수동 테스트로 별도 확인함")
    lines.append("- 플랫폼 가장자리 점프와 장애물 충돌 테스트는 환경 의존성이 높아 11주차 자동화 범위에서 제외함")

    return "\n".join(lines)


def to_adf_text_document(text):
    content = []

    for line in text.splitlines():
        if line.strip() == "":
            content.append({"type": "paragraph"})
        else:
            content.append({
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": line
                    }
                ]
            })

    return {
        "type": "doc",
        "version": 1,
        "content": content
    }


def create_jira_issue(config, summary):
    has_failure = summary["failed"] > 0 or summary["broken"] > 0
    issue_type = config["fail_issue_type"] if has_failure else config["success_issue_type"]

    if has_failure:
        title = f"[Unity][AltTester] 자동화 테스트 실패 - 실패 {summary['failed']}건 / Broken {summary['broken']}건"
    else:
        title = "[Unity][AltTester] 자동화 테스트 성공 - 8개 TC 통과"

    payload = {
        "fields": {
            "project": {
                "key": config["project_key"]
            },
            "summary": title,
            "description": to_adf_text_document(build_description(summary)),
            "issuetype": {
                "name": issue_type
            },
            "labels": [
                "unity",
                "alttester",
                "pytest",
                "qa-automation",
                "week11"
            ]
        }
    }

    url = f"{config['server'].rstrip('/')}/rest/api/3/issue"

    response = requests.post(
        url,
        auth=(config["email"], config["token"]),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=30
    )

    if response.status_code not in (200, 201):
        raise RuntimeError(
            f"Jira 이슈 생성 실패\n"
            f"Status Code: {response.status_code}\n"
            f"Response: {response.text}"
        )

    return response.json()


def main():
    config = load_config()
    summary = read_allure_results()
    issue = create_jira_issue(config, summary)

    print("Jira 업로드 완료")
    print(f"Issue Key: {issue.get('key')}")
    print(f"Total: {summary['total']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Broken: {summary['broken']}")
    print(f"Skipped: {summary['skipped']}")


if __name__ == "__main__":
    main()