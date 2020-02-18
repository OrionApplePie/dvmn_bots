import requests

proxies = {
    "http": "http://151.253.165.70:8080",
    "https": "http://151.253.165.70:8080",
}

r = requests.get("http://api.telegram.org", proxies=proxies)
