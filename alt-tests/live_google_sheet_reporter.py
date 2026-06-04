from pathlib import Path
from datetime import datetime
import re

import gspread
from google.oauth2.service_account import Credentials


ALT_TEST_ROOT = Path(__file__).resolve().parent
SERVICE_ACCOUNT_PATH = ALT_TEST_ROOT / "google-service-account.json"

SPREADSHEET_ID = "1qTELlK_FmKfSeKF85NDK9ZWjKix1qNPP7Y0GXDjYVsw"

TC_LIST_SHEET_NAME = "TC_List"
HISTORY_SHEET_NAME = "History"
SUMMARY_SHEET_NAME = "Summary"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

RESULT_STYLE = {
    "Running": {
        "status": "실행 중",
        "background": {"red": 0.74, "green": 0.84, "blue": 0.93},
    },
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


RUN_INFO = get_run_info()
_SPREADSHEET = None
_RUN_RESULTS = {}


def extract_tc_id(test_name: str):
    match = re.search(r"TC[_-]MJ[_-](\d{3})", test_name, re.IGNORECASE)

    if not match:
        return None

    return f"TC-MJ-{match.group(1)}"


def get_spreadsheet():
    if not SERVICE_ACCOUNT_PATH.exists():
        raise FileNotFoundError(f"서비스 계정 JSON 파일을 찾을 수 없음: {SERVICE_ACCOUNT_PATH}")

    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_PATH,
        scopes=SCOPES,
    )

    client = gspread.authorize(credentials)
    return client.open_by_key(SPREADSHEET_ID)


def spreadsheet():
    global _SPREADSHEET

    if _SPREADSHEET is None:
        _SPREADSHEET = get_spreadsheet()

    return _SPREADSHEET


def get_or_create_worksheet(sheet_name, rows=1000, cols=20):
    book = spreadsheet()

    try:
        return book.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        return book.add_worksheet(title=sheet_name, rows=rows, cols=cols)


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


def update_tc_list(tc_id, result):
    sheet = get_or_create_worksheet(TC_LIST_SHEET_NAME)
    header_map = get_header_map(sheet)

    id_col = header_map["ID"]
    result_col = header_map["실행결과"]
    status_col = header_map["상태"]
    note_col = header_map["비고"]

    row = find_tc_row(sheet, tc_id, id_col)

    if row is None:
        print(f"[Google Sheets] TC ID를 찾을 수 없음: {tc_id}")
        return

    status = RESULT_STYLE.get(result, RESULT_STYLE["Broken"])["status"]
    note = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sheet.update(
        values=[[result, status, note]],
        range_name=a1_range(row, result_col, note_col),
    )

    background = RESULT_STYLE.get(result, RESULT_STYLE["Broken"])["background"]

    sheet.spreadsheet.batch_update({
        "requests": [
            {
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
            }
        ]
    })

    print(f"[Google Sheets] {tc_id} → {result}")


def setup_history_header(sheet):
    current_headers = sheet.row_values(1)

    if current_headers:
        return

    headers = [
        "Run ID",
        "실행일시",
        "TC ID",
        "테스트명",
        "실행결과",
        "상태",
        "비고",
    ]

    sheet.update(values=[headers], range_name="A1:G1")
    sheet.format("A1:G1", {
        "textFormat": {"bold": True},
        "backgroundColor": {"red": 0.85, "green": 0.85, "blue": 0.85},
        "horizontalAlignment": "CENTER",
    })


def record_result(tc_id, test_name, result):
    executed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = RESULT_STYLE.get(result, RESULT_STYLE["Broken"])["status"]

    _RUN_RESULTS[tc_id] = {
        "run_id": RUN_INFO["run_id"],
        "executed_at": executed_at,
        "tc_id": tc_id,
        "test_name": test_name,
        "result": result,
        "status": status,
        "note": executed_at,
    }


def append_history_once():
    if not _RUN_RESULTS:
        return 0

    sheet = get_or_create_worksheet(HISTORY_SHEET_NAME)
    setup_history_header(sheet)

    rows = []

    for tc_id in sorted(_RUN_RESULTS.keys()):
        info = _RUN_RESULTS[tc_id]

        rows.append([
            info["run_id"],
            info["executed_at"],
            info["tc_id"],
            info["test_name"],
            info["result"],
            info["status"],
            info["note"],
        ])

    sheet.append_rows(rows, value_input_option="USER_ENTERED")
    print(f"[Google Sheets] History {len(rows)}건 추가")

    return len(rows)


def update_summary_once():
    summary = get_or_create_worksheet(SUMMARY_SHEET_NAME)

    total = len(_RUN_RESULTS)
    passed = sum(1 for item in _RUN_RESULTS.values() if item["result"] == "Pass")
    failed = sum(1 for item in _RUN_RESULTS.values() if item["result"] == "Fail")
    broken = sum(1 for item in _RUN_RESULTS.values() if item["result"] == "Broken")
    skipped = sum(1 for item in _RUN_RESULTS.values() if item["result"] == "Skipped")

    pass_rate = 0 if total == 0 else round((passed / total) * 100, 2)
    final_result = "Passed" if total > 0 and failed == 0 and broken == 0 else "Failed"

    data = [
        ["항목", "값"],
        ["최근 Run ID", RUN_INFO["run_id"]],
        ["최근 실행일시", RUN_INFO["executed_at"]],
        ["전체 TC 수", total],
        ["Pass 수", passed],
        ["Fail 수", failed],
        ["Broken 수", broken],
        ["Skipped 수", skipped],
        ["Pass Rate", f"{pass_rate}%"],
        ["최근 실행 결과", final_result],
    ]

    summary.clear()
    summary.update(values=data, range_name="A1:B10")

    summary.format("A1:B1", {
        "textFormat": {"bold": True},
        "backgroundColor": {"red": 0.85, "green": 0.85, "blue": 0.85},
        "horizontalAlignment": "CENTER",
    })

    result_color = (
        {"red": 0.78, "green": 0.94, "blue": 0.80}
        if final_result == "Passed"
        else {"red": 1.0, "green": 0.78, "blue": 0.80}
    )

    summary.format("B10", {
        "backgroundColor": result_color,
        "textFormat": {"bold": True},
    })

    print("[Google Sheets] Summary 갱신 완료")


def mark_running(tc_id, test_name):
    update_tc_list(tc_id, "Running")


def mark_finished(tc_id, test_name, result):
    update_tc_list(tc_id, result)
    record_result(tc_id, test_name, result)


def finalize_run():
    append_history_once()
    update_summary_once()