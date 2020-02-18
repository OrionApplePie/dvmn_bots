import telegram
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("TELEGRAM_API_TOKEN")
SOCKS5_PROXY = "socks5://94.182.189.29:443"

PROXY_KWARGS = {
    'assert_hostname': 'False',
    'cert_reqs': 'CERT_NONE'
}
pp = telegram.utils.request.Request(
    proxy_url=SOCKS5_PROXY,
    urllib3_proxy_kwargs=PROXY_KWARGS
)

bot = telegram.Bot(token=token, request=pp)

print(bot.get_me())
bot.send_message(chat_id=472955649, text="wazzup")
