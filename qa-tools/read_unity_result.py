from pathlib import Path
import xml.etree.ElementTree as ET


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = PROJECT_ROOT / "TestResults" / "playmode-result.xml"


def main():
    if not RESULT_PATH.exists():
        raise FileNotFoundError(f"테스트 결과 파일을 찾을 수 없음: {RESULT_PATH}")

    root = ET.parse(RESULT_PATH).getroot()

    total = int(root.attrib.get("total", 0))
    passed = int(root.attrib.get("passed", 0))
    failed = int(root.attrib.get("failed", 0))
    skipped = int(root.attrib.get("skipped", 0))
    result = root.attrib.get("result", "Unknown")
    duration = root.attrib.get("duration", "0")

    print("Unity PlayMode Test Result")
    print(f"Result: {result}")
    print(f"Total: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print(f"Duration: {duration} seconds")
    print()

    print("Test Cases")
    for test_case in root.iter("test-case"):
        name = test_case.attrib.get("name", "Unknown")
        case_result = test_case.attrib.get("result", "Unknown")
        case_duration = test_case.attrib.get("duration", "0")
        print(f"- {name}: {case_result} ({case_duration}s)")


if __name__ == "__main__":
    main()