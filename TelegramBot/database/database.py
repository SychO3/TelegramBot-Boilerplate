from datetime import datetime

from pyrogram.types import User

from TelegramBot.database.MysqlDb import mysql_database as db

from prestool.PresMySql import SqlStr

s = SqlStr()


async def save_user(user: User):
    """
    Save the new user id in the database if it is not already there.
    """

    insert_format = {
        "id": user.id,
        "full_name": user.full_name,
        "username": user.username,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    sql = s.insert_sql_str("users", insert_format)
    await db.execute(sql)


async def save_chat(chat_id: int):
    """
    Save the new chat id in the database if it is not already there.
    """

    insert_format = {"date": datetime.now()}
    sql = s.insert_sql_str("chats", insert_format)
    await db.execute(sql)
