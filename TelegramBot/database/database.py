from datetime import datetime

from pyrogram.types import User

from TelegramBot.database import MongoDb as db


async def save_user(user: User):
    """
    Save the new user id in the database if it is not already there.
    """

    insert_format = {
        "name": user.full_name,
        "username": user.username,
        "date": datetime.now(),
    }
    await db.users.update_document(user.id, insert_format)


async def save_chat(chat_id: int):
    """
    Save the new chat id in the database if it is not already there.
    """

    insert_format = {"date": datetime.now()}
    await db.chats.update_document(chat_id, insert_format)
