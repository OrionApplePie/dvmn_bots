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
    response = requests.get(
        url=urljoin(DEVMAN_API_BASE_URL, DEVMAN_LONG_POLLING_URL),
        headers=headers,
        timeout=60,
    )
    print(response.text)


if __name__ == "__main__":
    load_dotenv()
    main()
