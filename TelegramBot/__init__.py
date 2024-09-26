import sys
import time
from asyncio import get_event_loop, new_event_loop, set_event_loop

from pyrogram import Client
from redis import asyncio as aioredis

from TelegramBot import config
from TelegramBot.database.MysqlDb import check_mysql_url, mysql_database
from TelegramBot.logging import log

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from TelegramBot.tasks import game as game_task

import logging

logging.basicConfig(level=logging.ERROR)  # 设置为 DEBUG 级别


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

redis = aioredis.from_url(config.REDIS_URI, decode_responses=True)


# https://docs.pyrogram.org/topics/smart-plugins
plugins = dict(root="TelegramBot/plugins")
bot = Client(
    "TelegramBot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    plugins=plugins,
)

scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")

scheduler.add_job(
    game_task.stop_bet, "interval", seconds=1, args=[bot, redis], max_instances=1
)
# scheduler.add_job(game_task.calculate_agent_reward, "cron", hour=23, minute=59, second=59, args=[bot, redis], max_instances=1)
# 代理佣金，10秒执行一次
scheduler.add_job(
    game_task.calculate_agent_reward,
    "interval",
    seconds=10,
    args=[bot, redis],
    max_instances=1,
)
log(__name__).info("Scheduled task started successfully...")
scheduler.start()
