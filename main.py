import os
from time import sleep

import requests
import telegram
from dotenv import find_dotenv, load_dotenv
from requests.compat import urljoin
from requests.exceptions import ConnectionError, ReadTimeout

DEVMAN_API_BASE_URL = "https://dvmn.org/api/"
DEVMAN_REVIEWS_URL = "user_reviews"
DEVMAN_LONG_POLLING_URL = "long_polling"
DEVMAN_TIMEOUT = 120
CHAT_ID = 472955649

def main():
    devman_token = os.getenv("DEVMAN_API_TOKEN")
    telegram_token = os.getenv("TELEGRAM_API_TOKEN")

    headers = {
        "Authorization": f"Token {devman_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    params = {}
    url = urljoin(DEVMAN_API_BASE_URL, DEVMAN_LONG_POLLING_URL)

    # настройки прокси берет из переменной окружения 
    req = telegram.utils.request.Request()
    bot = telegram.Bot(token=telegram_token, request=req)

    while True:
        try:
            response = requests.get(
                url=url,
                headers=headers,
                params=params,
                timeout=DEVMAN_TIMEOUT,
            )
        except ReadTimeout as error:
            print(f"Timeout error, try again:\n{error}\n")
            continue

        except ConnectionError as error:
            print(f"Connection error, try again:\n{error}\n")
            continue

        resp_data = response.json()

        if resp_data["status"] == "timeout":
            params["timestamp"] = resp_data["timestamp_to_request"]
            print(resp_data)

        if resp_data["status"] == "found":
            bot.send_message(
                chat_id=CHAT_ID,
                text="Преподаватель проверил работу!"
            )
            params["timestamp"] = resp_data["last_attempt_timestamp"]
            print(resp_data)


if __name__ == "__main__":
    load_dotenv()
    main()
