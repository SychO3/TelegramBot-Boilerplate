import sys
import time
from asyncio import get_event_loop, new_event_loop, set_event_loop

from pyrogram import Client

from TelegramBot import config
from TelegramBot.database.MysqlDb import check_mysql_url, mysql_database
from TelegramBot.logging import log

if sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
    import uvloop

    uvloop.install()
    log(__name__).info("uvloop is installed.")

log(__name__).info("Starting TelegramBot....")
BotStartTime = time.time()


if sys.version_info[0] < 3 or sys.version_info[1] < 11:
    log(__name__).critical(
        "You MUST need to be on python 3.11 or above, shutting down the bot..."
    )
    sys.exit(1)


log(__name__).info("setting up event loop....")
try:
    loop = get_event_loop()
except RuntimeError:
    set_event_loop(new_event_loop())
    loop = get_event_loop()


log(__name__).info("initiating the client....")
log(__name__).info("checking MongoDb URI....")
loop.run_until_complete(check_mysql_url(config.MYSQL_URI))
loop.run_until_complete(mysql_database.ensure_pool())


# https://docs.pyrogram.org/topics/smart-plugins
plugins = dict(root="TelegramBot/plugins")
bot = Client(
    "TelegramBot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    plugins=plugins,
)
