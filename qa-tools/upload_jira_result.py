from pathlib import Path
from datetime import datetime
import os
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = PROJECT_ROOT / "TestResults" / "playmode-result.xml"
ENV_PATH = PROJECT_ROOT / ".env"


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


def parse_unity_result():
    if not RESULT_PATH.exists():
        raise FileNotFoundError(f"테스트 결과 파일을 찾을 수 없음: {RESULT_PATH}")

    root = ET.parse(RESULT_PATH).getroot()

    summary = {
        "result": root.attrib.get("result", "Unknown"),
        "total": int(root.attrib.get("total", 0)),
        "passed": int(root.attrib.get("passed", 0)),
        "failed": int(root.attrib.get("failed", 0)),
        "skipped": int(root.attrib.get("skipped", 0)),
        "duration": root.attrib.get("duration", "0"),
        "cases": [],
    }

    for test_case in root.iter("test-case"):
        case = {
            "name": test_case.attrib.get("name", "Unknown"),
            "fullname": test_case.attrib.get("fullname", ""),
            "result": test_case.attrib.get("result", "Unknown"),
            "duration": test_case.attrib.get("duration", "0"),
            "message": "",
            "stack_trace": "",
        }

        failure = test_case.find("failure")
        if failure is not None:
            message = failure.find("message")
            stack_trace = failure.find("stack-trace")

            if message is not None and message.text:
                case["message"] = message.text.strip()

            if stack_trace is not None and stack_trace.text:
                case["stack_trace"] = stack_trace.text.strip()

        summary["cases"].append(case)

    return summary


def build_jira_description(summary):
    lines = [
        "Unity PlayMode 테스트 결과",
        "",
        f"- 실행 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "- 프로젝트: 2D Platformer Microgame",
        "- 테스트 씬: SampleScene",
        "- 테스트 플랫폼: PlayMode",
        f"- 전체 테스트 수: {summary['total']}",
        f"- 성공: {summary['passed']}",
        f"- 실패: {summary['failed']}",
        f"- 스킵: {summary['skipped']}",
        f"- 실행 시간: {summary['duration']}초",
        "",
        "테스트 케이스 목록",
    ]

    for case in summary["cases"]:
        lines.append(f"- {case['name']}: {case['result']} ({case['duration']}초)")

    failed_cases = [case for case in summary["cases"] if case["result"] != "Passed"]

    if failed_cases:
        lines.append("")
        lines.append("실패 상세")
        for case in failed_cases:
            lines.append(f"- 테스트명: {case['name']}")
            lines.append(f"  메시지: {case['message']}")
            lines.append(f"  스택: {case['stack_trace'][:500]}")

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
    has_failure = summary["failed"] > 0
    issue_type = config["fail_issue_type"] if has_failure else config["success_issue_type"]

    if has_failure:
        title = f"[Unity][PlayMode] 테스트 실패 - {summary['failed']}건 실패"
    else:
        title = "[Unity][PlayMode] 테스트 성공 - 전체 테스트 통과"

    description_text = build_jira_description(summary)

    url = f"{config['server'].rstrip('/')}/rest/api/3/issue"

    payload = {
        "fields": {
            "project": {
                "key": config["project_key"]
            },
            "summary": title,
            "description": to_adf_text_document(description_text),
            "issuetype": {
                "name": issue_type
            },
            "labels": [
                "unity",
                "playmode",
                "qa-automation",
                "week10"
            ]
        }
    }

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
    summary = parse_unity_result()
    issue = create_jira_issue(config, summary)

    print("Jira 업로드 완료")
    print(f"Issue Key: {issue.get('key')}")
    print(f"Result: {summary['result']}")
    print(f"Total: {summary['total']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")


if __name__ == "__main__":
    main()