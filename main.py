import os

from dotenv import load_dotenv, find_dotenv
import requests
from requests.compat import urljoin

DEVMAN_API_BASE_URL = "https://dvmn.org/api/"
DEVMAN_REVIEWS_URL = "user_reviews"
DEVMAN_LONG_POLLING_URL = "long_polling"


def main():
    token = os.getenv("DEVMAN_TOKEN")
    headers = {
        "Authorization": f"Token {token}",
    }
    params = {}
    url = urljoin(DEVMAN_API_BASE_URL, DEVMAN_LONG_POLLING_URL)

    while True:
        response = requests.get(
            url=url,
            headers=headers,
            params=params,
            timeout=90,
        )
        resp_data = response.json()
        if resp_data["status"] == "timeout":
            params["timestamp"] = resp_data["timestamp_to_request"]

        if resp_data["status"] == "found":
            print("got answer!!!")
            break

    print(response.text)


if __name__ == "__main__":
    load_dotenv()
    main()
