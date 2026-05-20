from pathlib import Path
from datetime import datetime

import xlwings as xw


EXCEL_PATH = Path(r"D:\funity\Test1\alt-tests\TC_Result.xlsx")


def find_open_workbook():
    for app in xw.apps:
        for book in app.books:
            if Path(book.fullname).resolve() == EXCEL_PATH.resolve():
                return book

    raise RuntimeError(
        "열려 있는 TC_Result.xlsx를 찾을 수 없음. "
        "Excel에서 D:\\funity\\Test1\\alt-tests\\TC_Result.xlsx 파일을 먼저 열어야 함."
    )


def main():
    book = find_open_workbook()
    sheet = book.sheets[0]

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 테스트용으로 I2 셀에 값 입력
    sheet.range("I2").value = f"Excel 실시간 연결 테스트 성공 / {now}"

    # G2/H2에도 테스트 값 입력
    sheet.range("G2").value = "Live-Test"
    sheet.range("H2").value = "연결 확인"

    book.save()

    print("Excel 실시간 쓰기 테스트 완료")
    print(f"파일: {EXCEL_PATH}")
    print("확인 위치: G2, H2, I2")


if __name__ == "__main__":
    main()