from pyrogram import Client, filters
from pyrogram.types import Message

from TelegramBot.database import database
from TelegramBot.helpers.filters import sudo_cmd
from TelegramBot import redis
import json
from TelegramBot.plugins.users.game import a_text_, a_button_


r_key = "FSCBOT:GAME"


@Client.on_message(sudo_cmd & filters.command("admin"))
async def game_admin(bot: Client, m: Message):
    await database.update_all_is_jiesuan()

    game_data = await redis.get(r_key)
    if game_data:
        game_data = json.loads(game_data)
        a_text = await a_text_(game_data)
        a_button = await a_button_(game_data.get("qihao"))
        await m.reply_text(a_text, reply_markup=a_button)
    else:
        return await m.reply_text("游戏数据不存在，请在群组内输入 `开群` 开启游戏")
