from pathlib import Path
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials


SERVICE_ACCOUNT_PATH = Path(r"D:\funity\Test1\alt-tests\google-service-account.json")

SPREADSHEET_ID = "1qTELlK_FmKfSeKF85NDK9ZWjKix1qNPP7Y0GXDjYVsw"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]


def get_spreadsheet():
    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_PATH,
        scopes=SCOPES,
    )

    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    return spreadsheet


def main():
    spreadsheet = get_spreadsheet()
    sheet = spreadsheet.worksheet("TC_List")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sheet.update(
        "G2:I2",
        [[
            "Live-Test",
            "Google Sheet 연결 확인",
            now,
        ]]
    )

    print("Google Sheets 연결 테스트 완료")
    print("업데이트 위치: TC_List!G2:I2")


if __name__ == "__main__":
    main()