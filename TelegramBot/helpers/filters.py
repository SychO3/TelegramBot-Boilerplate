"""
Creating custom filters
https://docs.pyrogram.org/topics/create-filters
"""

from pyrogram import filters, enums
from pyrogram.types import Message
from TelegramBot.config import SUDO_USERID, OWNER_USERID
from TelegramBot import config


def dev_users(_, __, message: Message) -> bool:
    return message.from_user.id in OWNER_USERID if message.from_user else False


def sudo_users(_, __, message: Message) -> bool:
    return message.from_user.id in SUDO_USERID if message.from_user else False


async def shangfen_group_filter(_, __, m: Message):
    if m.chat and m.chat.type in {enums.ChatType.GROUP, enums.ChatType.SUPERGROUP}:
        return bool(m.chat.id == config.SHANGFEN_GROUP_ID)


async def game_group_filter(_, __, m: Message):
    if m.chat and m.chat.type in {enums.ChatType.GROUP, enums.ChatType.SUPERGROUP}:
        return bool(m.chat.id == config.GAME_GROUP_ID)


dev_cmd = filters.create(dev_users)
sudo_cmd = filters.create(sudo_users)
shangfen_group = filters.create(shangfen_group_filter)
game_group = filters.create(game_group_filter)
