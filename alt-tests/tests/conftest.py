import pytest

from live_excel_reporter import extract_tc_id, mark_running, mark_finished


_started_tests = set()
_finished_tests = set()


def pytest_runtest_setup(item):
    tc_id = extract_tc_id(item.name)

    if tc_id is None:
        return

    if item.nodeid in _started_tests:
        return

    _started_tests.add(item.nodeid)
    mark_running(tc_id, item.name)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    tc_id = extract_tc_id(item.name)

    if tc_id is None:
        return

    if item.nodeid in _finished_tests:
        return

    # setup 단계에서 실패한 경우:
    # 예: AltDriver 연결 실패, fixture 오류, 환경 오류
    if report.when == "setup" and report.failed:
        message = str(report.longrepr)
        mark_finished(tc_id, item.name, "Broken", message[:500])
        _finished_tests.add(item.nodeid)
        return

    # 실제 테스트 본문 단계 결과
    if report.when == "call":
        if report.passed:
            mark_finished(tc_id, item.name, "Pass")
        elif report.failed:
            message = str(report.longrepr)
            mark_finished(tc_id, item.name, "Fail", message[:500])
        elif report.skipped:
            mark_finished(tc_id, item.name, "Skipped", "pytest skipped")

        _finished_tests.add(item.nodeid)