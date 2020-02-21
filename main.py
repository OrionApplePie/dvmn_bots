import os

import requests
import telegram
from dotenv import find_dotenv, load_dotenv
from requests.compat import urljoin
from requests.exceptions import ConnectionError, ReadTimeout

DEVMAN_BASE_URL = "https://dvmn.org/"

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
            messages = []
            new_attempts = resp_data["new_attempts"]
            for attempt in new_attempts:
                attempt_result = (
                    "К сожалению, в работе нашлись ошибки."
                    if attempt["is_negative"]
                    else "Преподавателю все понравилось, можно приступать к следующему уроку!"
                )
                lesson_title = attempt["lesson_title"]
                lesson_url = attempt["lesson_url"]
                message = "".join([
                    "У Вас проверили работу",
                    " ",
                    f"\u00AB{lesson_title}\u00BB",
                    "\n\n",
                    attempt_result,
                    "\n\n",
                    urljoin(DEVMAN_BASE_URL, lesson_url)
                ])
                messages.append(message)
            for message in messages:
                bot.send_message(
                    chat_id=CHAT_ID,
                    text=message
                )
            params["timestamp"] = resp_data["last_attempt_timestamp"]
            print(resp_data)


if __name__ == "__main__":
    load_dotenv()
    main()
