import logging
import os
from textwrap import dedent
from time import sleep

import requests
import telegram
from dotenv import find_dotenv, load_dotenv
from requests.compat import urljoin
from requests.exceptions import ConnectionError, HTTPError, ReadTimeout

DEVMAN_BASE_URL = "https://dvmn.org/"

DEVMAN_API_BASE_URL = "https://dvmn.org/api/"
DEVMAN_REVIEWS_URL = "user_reviews"
DEVMAN_LONG_POLLING_URL = "long_polling"
DEVMAN_TIMEOUT = 120

FAIL_ATTEMPTS_COUNT = 10
SLEEP_TIME = 60 * 2


class MyLogsHandler(logging.Handler):

    def __init__(self, bot, chat_id):
        super(MyLogsHandler, self).__init__()

        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)

        self.bot.send_message(
            chat_id=self.chat_id,
            text=log_entry
        )


def main():
    devman_token = os.getenv("DEVMAN_API_TOKEN")
    telegram_token = os.getenv("TELEGRAM_API_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    headers = {
        "Authorization": f"Token {devman_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    params = {}
    url = urljoin(DEVMAN_API_BASE_URL, DEVMAN_LONG_POLLING_URL)

    # настройки прокси берутся из переменной окружения
    req = telegram.utils.request.Request()
    bot = telegram.Bot(token=telegram_token, request=req)

    logger = logging.getLogger("Логер бота")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(MyLogsHandler(bot=bot, chat_id=telegram_chat_id))

    logger.info("Бот запущен.")
    fail_count = 0

    while True:
        try:
            response = requests.get(
                url=url,
                headers=headers,
                params=params,
                timeout=DEVMAN_TIMEOUT,
            )
            response.raise_for_status()

        except HTTPError as err:
            logger.error("Бот упал с ошибкой:")
            logger.error(err, exc_info=True)
            continue

        except ReadTimeout as err:
            logger.error("Бот упал с ошибкой:")
            logger.error(err, exc_info=True)
            continue

        except ConnectionError as err:
            fail_count += 1
            if fail_count >= FAIL_ATTEMPTS_COUNT:
                logger.error(
                    f"Too much connection attempts fail, waiting {SLEEP_TIME} secs.\n"
                )
                logger.error(err, exc_info=True)
                sleep(SLEEP_TIME)
            else:
                logger.error("Бот упал с ошибкой:")
                logger.error(err, exc_info=True)
                continue

        fail_count = 0
        resp_data = response.json()

        if resp_data["status"] == "timeout":
            params["timestamp"] = resp_data["timestamp_to_request"]

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

                message = f"""
                У Вас проверили работу \u00AB{lesson_title}\u00BB

                {attempt_result}

                {urljoin(DEVMAN_BASE_URL, lesson_url)}
                """

                messages.append(dedent(message))
            for message in messages:
                bot.send_message(
                    chat_id=telegram_chat_id,
                    text=message
                )
            params["timestamp"] = resp_data["last_attempt_timestamp"]


if __name__ == "__main__":
    load_dotenv()
    main()
