import os
from datetime import datetime

import requests
from dotenv import load_dotenv


load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def main():
    if not SLACK_WEBHOOK_URL:
        raise RuntimeError(".env에서 SLACK_WEBHOOK_URL을 찾을 수 없음")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    message = (
        "[Unity QA 자동화 알림 테스트]\n"
        "Slack Webhook 연결 테스트 메시지\n"
        f"전송 시간: {now}"
    )

    response = requests.post(
        SLACK_WEBHOOK_URL,
        json={"text": message},
        timeout=10,
    )

    print(f"status code: {response.status_code}")
    print(f"response text: {response.text}")

    response.raise_for_status()

    print("Slack 알림 테스트 완료")


if __name__ == "__main__":
    main()