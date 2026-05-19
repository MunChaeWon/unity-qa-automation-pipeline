from pathlib import Path
import json
import uuid
import time
import xml.etree.ElementTree as ET


PROJECT_ROOT = Path(__file__).resolve().parents[1]
UNITY_RESULT_PATH = PROJECT_ROOT / "TestResults" / "playmode-result.xml"
ALLURE_RESULTS_DIR = PROJECT_ROOT / "allure-results"


def parse_unity_result():
    if not UNITY_RESULT_PATH.exists():
        raise FileNotFoundError(f"Unity 테스트 결과 파일을 찾을 수 없음: {UNITY_RESULT_PATH}")

    root = ET.parse(UNITY_RESULT_PATH).getroot()
    test_cases = []

    for test_case in root.iter("test-case"):
        name = test_case.attrib.get("name", "Unknown")
        fullname = test_case.attrib.get("fullname", name)
        result = test_case.attrib.get("result", "Unknown")
        duration = float(test_case.attrib.get("duration", "0") or 0)

        message = ""
        stack_trace = ""

        failure = test_case.find("failure")
        if failure is not None:
            message_node = failure.find("message")
            stack_node = failure.find("stack-trace")

            if message_node is not None and message_node.text:
                message = message_node.text.strip()

            if stack_node is not None and stack_node.text:
                stack_trace = stack_node.text.strip()

        status = "passed" if result == "Passed" else "failed"

        test_cases.append({
            "name": name,
            "fullname": fullname,
            "status": status,
            "duration": duration,
            "message": message,
            "stack_trace": stack_trace,
        })

    return test_cases


def clear_old_allure_results():
    ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    for file_path in ALLURE_RESULTS_DIR.glob("*-result.json"):
        file_path.unlink()


def create_allure_result_files(test_cases):
    clear_old_allure_results()

    base_time = int(time.time() * 1000)

    for index, case in enumerate(test_cases):
        start_time = base_time + index
        stop_time = start_time + int(case["duration"] * 1000)

        result_data = {
            "uuid": str(uuid.uuid4()),
            "historyId": case["fullname"],
            "testCaseId": case["fullname"],
            "name": case["name"],
            "fullName": case["fullname"],
            "status": case["status"],
            "stage": "finished",
            "start": start_time,
            "stop": stop_time,
            "labels": [
                {
                    "name": "framework",
                    "value": "Unity Test Framework"
                },
                {
                    "name": "language",
                    "value": "C#"
                },
                {
                    "name": "suite",
                    "value": "Unity PlayMode"
                },
                {
                    "name": "feature",
                    "value": "2D Platformer Microgame"
                },
                {
                    "name": "story",
                    "value": "Player Function PlayMode Test"
                }
            ],
            "parameters": [
                {
                    "name": "Scene",
                    "value": "SampleScene"
                },
                {
                    "name": "TestPlatform",
                    "value": "PlayMode"
                }
            ]
        }

        if case["status"] == "failed":
            result_data["statusDetails"] = {
                "message": case["message"] or "테스트 실패",
                "trace": case["stack_trace"]
            }

        output_path = ALLURE_RESULTS_DIR / f"{result_data['uuid']}-result.json"
        output_path.write_text(
            json.dumps(result_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )


def main():
    test_cases = parse_unity_result()
    create_allure_result_files(test_cases)

    passed = sum(1 for case in test_cases if case["status"] == "passed")
    failed = sum(1 for case in test_cases if case["status"] == "failed")

    print("Allure 결과 파일 생성 완료")
    print(f"Total: {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Output: {ALLURE_RESULTS_DIR}")


if __name__ == "__main__":
    main()