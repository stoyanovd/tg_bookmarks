import os

from utils.local_env import try_initialize_local_env


class TgConf:
    TOKEN = ""
    PORT = 0
    WEBHOOK_URL_PREFIX = ""


DEFAULT_PORT = '5000'

TOKEN_NAME = 'TELEGRAM_BOT_TOKEN'
PORT_NAME = 'PORT'
WEBHOOK_URL_PREFIX_NAME = "WEBHOOK_URL_PREFIX"


def init_conf():
    try_initialize_local_env()

    assert TOKEN_NAME in os.environ.keys()

    conf = TgConf()
    conf.TOKEN = os.environ.get(TOKEN_NAME)
    conf.PORT = int(os.environ.get(PORT_NAME, DEFAULT_PORT))
    conf.WEBHOOK_URL_PREFIX = os.environ.get(WEBHOOK_URL_PREFIX_NAME)
    return conf
