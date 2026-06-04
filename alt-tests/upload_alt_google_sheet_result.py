from pathlib import Path
from datetime import datetime
import json
import re

import gspread
from google.oauth2.service_account import Credentials


ALT_TEST_ROOT = Path(__file__).resolve().parent
SERVICE_ACCOUNT_PATH = ALT_TEST_ROOT / "google-service-account.json"
ALLURE_RESULTS_DIR = ALT_TEST_ROOT / "alt-allure-results"

SPREADSHEET_ID = "1qTELlK_FmKfSeKF85NDK9ZWjKix1qNPP7Y0GXDjYVsw"

TC_LIST_SHEET_NAME = "TC_List"
HISTORY_SHEET_NAME = "History"
SUMMARY_SHEET_NAME = "Summary"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

RESULT_STYLE = {
    "Pass": {
        "status": "자동화 완료",
        "background": {"red": 0.78, "green": 0.94, "blue": 0.80},
    },
    "Fail": {
        "status": "실패 확인 필요",
        "background": {"red": 1.0, "green": 0.78, "blue": 0.80},
    },
    "Broken": {
        "status": "스크립트 확인 필요",
        "background": {"red": 1.0, "green": 0.78, "blue": 0.80},
    },
    "Skipped": {
        "status": "미실행",
        "background": {"red": 1.0, "green": 0.92, "blue": 0.61},
    },
}


def get_run_info():
    now = datetime.now()
    return {
        "run_id": now.strftime("%Y%m%d_%H%M%S"),
        "executed_at": now.strftime("%Y-%m-%d %H:%M:%S"),
    }


def get_spreadsheet():
    if not SERVICE_ACCOUNT_PATH.exists():
        raise FileNotFoundError(f"서비스 계정 JSON 파일을 찾을 수 없음: {SERVICE_ACCOUNT_PATH}")

    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_PATH,
        scopes=SCOPES,
    )

    client = gspread.authorize(credentials)
    return client.open_by_key(SPREADSHEET_ID)


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

    results = {}

    for file_path in result_files:
        data = json.loads(file_path.read_text(encoding="utf-8"))

        test_name = data.get("name", "")
        allure_status = data.get("status", "unknown")
        message = data.get("statusDetails", {}).get("message", "")

        tc_id = extract_tc_id(test_name)

        if tc_id is None:
            continue

        if allure_status == "passed":
            result = "Pass"
        elif allure_status == "failed":
            result = "Fail"
        elif allure_status == "broken":
            result = "Broken"
        elif allure_status == "skipped":
            result = "Skipped"
        else:
            result = "Broken"

        results[tc_id] = {
            "tc_id": tc_id,
            "test_name": test_name,
            "result": result,
            "allure_status": allure_status,
            "message": message,
        }

    return dict(sorted(results.items()))


def get_header_map(sheet):
    headers = sheet.row_values(1)
    header_map = {}

    for index, header in enumerate(headers, start=1):
        header_map[str(header).strip()] = index

    required_headers = ["ID", "실행결과", "상태", "비고"]

    missing = [
        header for header in required_headers
        if header not in header_map
    ]

    if missing:
        raise RuntimeError(f"Google Sheet 필수 컬럼 누락: {', '.join(missing)}")

    return header_map


def find_tc_row(sheet, tc_id, id_col):
    id_values = sheet.col_values(id_col)

    for row_index, value in enumerate(id_values, start=1):
        if str(value).strip() == tc_id:
            return row_index

    return None


def a1_range(row, start_col, end_col):
    start = gspread.utils.rowcol_to_a1(row, start_col)
    end = gspread.utils.rowcol_to_a1(row, end_col)
    return f"{start}:{end}"


def update_tc_list(sheet, results, run_info):
    header_map = get_header_map(sheet)

    id_col = header_map["ID"]
    result_col = header_map["실행결과"]
    status_col = header_map["상태"]
    note_col = header_map["비고"]

    updated_count = 0
    not_found = []

    requests = []

    for tc_id, info in results.items():
        row = find_tc_row(sheet, tc_id, id_col)

        if row is None:
            not_found.append(tc_id)
            continue

        result = info["result"]
        status = RESULT_STYLE.get(result, RESULT_STYLE["Broken"])["status"]
        note = run_info["executed_at"]

        sheet.update(
            values=[[result, status, note]],
            range_name=a1_range(row, result_col, note_col),
        )

        background = RESULT_STYLE.get(result, RESULT_STYLE["Broken"])["background"]

        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet.id,
                    "startRowIndex": row - 1,
                    "endRowIndex": row,
                    "startColumnIndex": result_col - 1,
                    "endColumnIndex": note_col,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": background,
                        "wrapStrategy": "WRAP",
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,wrapStrategy)",
            }
        })

        updated_count += 1

    if requests:
        sheet.spreadsheet.batch_update({"requests": requests})

    return updated_count, not_found


def get_or_create_worksheet(spreadsheet, sheet_name, rows=1000, cols=20):
    try:
        return spreadsheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=sheet_name, rows=rows, cols=cols)


def setup_history_header(sheet):
    headers = [
        "Run ID",
        "실행일시",
        "TC ID",
        "테스트명",
        "실행결과",
        "상태",
        "Allure 상태",
        "비고",
    ]

    current_headers = sheet.row_values(1)

    if current_headers:
        return

    sheet.update(values=[headers], range_name="A1:H1")

    sheet.format("A1:H1", {
        "textFormat": {"bold": True},
        "backgroundColor": {"red": 0.85, "green": 0.85, "blue": 0.85},
        "horizontalAlignment": "CENTER",
    })


def append_history(sheet, results, run_info):
    setup_history_header(sheet)

    rows = []

    for tc_id, info in results.items():
        result = info["result"]
        status = RESULT_STYLE.get(result, RESULT_STYLE["Broken"])["status"]

        rows.append([
            run_info["run_id"],
            run_info["executed_at"],
            tc_id,
            info["test_name"],
            result,
            status,
            info["allure_status"],
            run_info["executed_at"],
        ])

    if not rows:
        return 0

    sheet.append_rows(rows, value_input_option="USER_ENTERED")
    return len(rows)


def update_summary(sheet, results, run_info):
    total = len(results)
    passed = sum(1 for item in results.values() if item["result"] == "Pass")
    failed = sum(1 for item in results.values() if item["result"] == "Fail")
    broken = sum(1 for item in results.values() if item["result"] == "Broken")
    skipped = sum(1 for item in results.values() if item["result"] == "Skipped")

    pass_rate = 0 if total == 0 else round((passed / total) * 100, 2)
    final_result = "Passed" if total > 0 and failed == 0 and broken == 0 else "Failed"

    data = [
        ["항목", "값"],
        ["최근 Run ID", run_info["run_id"]],
        ["최근 실행일시", run_info["executed_at"]],
        ["전체 TC 수", total],
        ["Pass 수", passed],
        ["Fail 수", failed],
        ["Broken 수", broken],
        ["Skipped 수", skipped],
        ["Pass Rate", f"{pass_rate}%"],
        ["최근 실행 결과", final_result],
    ]

    sheet.clear()
    sheet.update(values=data, range_name="A1:B10")

    sheet.format("A1:B1", {
        "textFormat": {"bold": True},
        "backgroundColor": {"red": 0.85, "green": 0.85, "blue": 0.85},
        "horizontalAlignment": "CENTER",
    })

    result_color = (
        {"red": 0.78, "green": 0.94, "blue": 0.80}
        if final_result == "Passed"
        else {"red": 1.0, "green": 0.78, "blue": 0.80}
    )

    sheet.format("B10", {
        "backgroundColor": result_color,
        "textFormat": {"bold": True},
    })


def main():
    run_info = get_run_info()
    results = read_allure_results()

    if not results:
        raise RuntimeError("Allure 결과에서 TC-MJ 형식의 테스트를 찾지 못함")

    spreadsheet = get_spreadsheet()

    tc_list_sheet = spreadsheet.worksheet(TC_LIST_SHEET_NAME)
    history_sheet = get_or_create_worksheet(spreadsheet, HISTORY_SHEET_NAME)
    summary_sheet = get_or_create_worksheet(spreadsheet, SUMMARY_SHEET_NAME)

    updated_count, not_found = update_tc_list(tc_list_sheet, results, run_info)
    history_count = append_history(history_sheet, results, run_info)
    update_summary(summary_sheet, results, run_info)

    print("Google Sheets 업데이트 완료")
    print(f"Run ID: {run_info['run_id']}")
    print(f"실행일시: {run_info['executed_at']}")
    print(f"TC_List 업데이트 수: {updated_count}")
    print(f"History 추가 수: {history_count}")
    print(f"Summary 갱신 완료")

    if not_found:
        print(f"TC_List에서 찾지 못한 TC ID: {', '.join(not_found)}")


if __name__ == "__main__":
    main()