from pathlib import Path
from datetime import datetime
import re

import xlwings as xw


EXCEL_PATH = Path(r"D:\funity\Test1\alt-tests\TC_Result.xlsx")

HEADER_ROW = 1
HISTORY_SHEET_NAME = "History"
SUMMARY_SHEET_NAME = "Summary"


RESULT_STYLE = {
    "Running": {"color": (189, 215, 238), "status": "실행 중"},
    "Pass": {"color": (198, 239, 206), "status": "자동화 완료"},
    "Fail": {"color": (255, 199, 206), "status": "실패 확인 필요"},
    "Broken": {"color": (255, 199, 206), "status": "스크립트 확인 필요"},
    "Skipped": {"color": (255, 235, 156), "status": "미실행"},
}


def get_run_info():
    now = datetime.now()
    return {
        "run_id": now.strftime("%Y%m%d_%H%M%S"),
        "executed_at": now.strftime("%Y-%m-%d %H:%M:%S"),
    }


RUN_INFO = get_run_info()


def extract_tc_id(text: str):
    match = re.search(r"TC[_-]MJ[_-](\d{3})", text, re.IGNORECASE)

    if not match:
        return None

    return f"TC-MJ-{match.group(1)}"


def find_open_workbook():
    for app in xw.apps:
        for book in app.books:
            try:
                if Path(book.fullname).resolve() == EXCEL_PATH.resolve():
                    return book
            except Exception:
                continue

    raise RuntimeError(
        "열려 있는 TC_Result.xlsx를 찾을 수 없음. "
        "Excel에서 D:\\funity\\Test1\\alt-tests\\TC_Result.xlsx 파일을 먼저 열어야 함."
    )


def get_main_sheet(book):
    return book.sheets[0]


def get_header_map(sheet):
    header_map = {}
    last_col = sheet.range((HEADER_ROW, sheet.cells.last_cell.column)).end("left").column

    for col in range(1, last_col + 1):
        value = sheet.range((HEADER_ROW, col)).value

        if value is None:
            continue

        header_map[str(value).strip()] = col

    required_headers = ["ID", "실행결과", "상태", "비고"]

    missing = [
        header for header in required_headers
        if header not in header_map
    ]

    if missing:
        raise RuntimeError(f"Excel 필수 컬럼 누락: {', '.join(missing)}")

    return header_map


def find_tc_row(sheet, header_map, tc_id):
    id_col = header_map["ID"]
    last_row = sheet.range((sheet.cells.last_cell.row, id_col)).end("up").row

    for row in range(2, last_row + 1):
        value = sheet.range((row, id_col)).value

        if value is None:
            continue

        if str(value).strip() == tc_id:
            return row

    return None


def apply_row_style(sheet, row, header_map, result):
    style = RESULT_STYLE.get(result, RESULT_STYLE["Broken"])
    color = style["color"]

    for header in ["실행결과", "상태", "비고"]:
        cell = sheet.range((row, header_map[header]))
        cell.color = color
        cell.api.WrapText = True


def update_tc_result(tc_id, result, note):
    book = find_open_workbook()
    sheet = get_main_sheet(book)
    header_map = get_header_map(sheet)

    row = find_tc_row(sheet, header_map, tc_id)

    if row is None:
        print(f"[Excel] TC ID를 찾을 수 없음: {tc_id}")
        return

    status = RESULT_STYLE.get(result, RESULT_STYLE["Broken"])["status"]

    sheet.range((row, header_map["실행결과"])).value = result
    sheet.range((row, header_map["상태"])).value = status
    sheet.range((row, header_map["비고"])).value = note

    apply_row_style(sheet, row, header_map, result)
    book.save()

    print(f"[Excel] {tc_id} → {result}")


def mark_running(tc_id, test_name):
    note = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    update_tc_result(tc_id, "Running", note)


def mark_finished(tc_id, test_name, result, message=""):
    note = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    update_tc_result(tc_id, result, note)
    append_history(tc_id, test_name, result, note)
    update_summary()

def get_or_create_sheet(book, sheet_name):
    for sheet in book.sheets:
        if sheet.name == sheet_name:
            return sheet

    return book.sheets.add(sheet_name, after=book.sheets[-1])


def append_history(tc_id, test_name, result, note):
    book = find_open_workbook()
    sheet = get_or_create_sheet(book, HISTORY_SHEET_NAME)

    if sheet.range("A1").value is None:
        headers = [
            "Run ID",
            "실행일시",
            "TC ID",
            "테스트명",
            "실행결과",
            "상태",
            "비고",
        ]

        for index, header in enumerate(headers, start=1):
            sheet.range((1, index)).value = header
            sheet.range((1, index)).api.Font.Bold = True
            sheet.range((1, index)).color = (217, 217, 217)

    next_row = sheet.range((sheet.cells.last_cell.row, 1)).end("up").row + 1
    status = RESULT_STYLE.get(result, RESULT_STYLE["Broken"])["status"]

    values = [
        RUN_INFO["run_id"],
        RUN_INFO["executed_at"],
        tc_id,
        test_name,
        result,
        status,
        note,
    ]

    for col, value in enumerate(values, start=1):
        sheet.range((next_row, col)).value = value
        sheet.range((next_row, col)).api.WrapText = True

    color = RESULT_STYLE.get(result, RESULT_STYLE["Broken"])["color"]

    for col in range(1, 8):
        sheet.range((next_row, col)).color = color

    sheet.autofit()
    book.save()


def update_summary():
    book = find_open_workbook()
    history = get_or_create_sheet(book, HISTORY_SHEET_NAME)
    summary = get_or_create_sheet(book, SUMMARY_SHEET_NAME)

    last_row = history.range((history.cells.last_cell.row, 1)).end("up").row

    if last_row < 2:
        return

    rows = history.range((2, 1), (last_row, 7)).value

    if rows is None:
        return

    if not isinstance(rows[0], list):
        rows = [rows]

    current_run_rows = [
        row for row in rows
        if row[0] == RUN_INFO["run_id"]
    ]

    total = len(current_run_rows)
    passed = sum(1 for row in current_run_rows if row[4] == "Pass")
    failed = sum(1 for row in current_run_rows if row[4] == "Fail")
    broken = sum(1 for row in current_run_rows if row[4] == "Broken")
    skipped = sum(1 for row in current_run_rows if row[4] == "Skipped")

    pass_rate = 0 if total == 0 else round((passed / total) * 100, 2)
    final_result = "Passed" if total > 0 and failed == 0 and broken == 0 else "Failed"

    summary.clear()

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

    for row_index, row_values in enumerate(data, start=1):
        for col_index, value in enumerate(row_values, start=1):
            summary.range((row_index, col_index)).value = value

    summary.range("A1:B1").api.Font.Bold = True
    summary.range("A1:B1").color = (217, 217, 217)

    if final_result == "Passed":
        summary.range("B10").color = (198, 239, 206)
    else:
        summary.range("B10").color = (255, 199, 206)

    summary.autofit()
    book.save()